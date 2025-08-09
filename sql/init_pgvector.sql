-- Initialize PGVector database for Hearthlink semantic memory storage
-- This script sets up the vector extension and creates the required schema

-- Enable PGVector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for semantic memory storage
CREATE SCHEMA IF NOT EXISTS semantic_memory;

-- Set search path to include semantic_memory schema
SET search_path TO semantic_memory, public;

-- Memory slices table with vector embeddings
CREATE TABLE IF NOT EXISTS memory_slices (
    slice_id VARCHAR(64) PRIMARY KEY,
    persona_id VARCHAR(64) NOT NULL,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    memory_type VARCHAR(32) NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'working')),
    keywords TEXT[], -- Array of extracted keywords for hybrid search
    embedding vector(384), -- 384-dimensional embeddings (sentence-transformers/all-MiniLM-L6-v2)
    relevance_score REAL DEFAULT 0.5 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    retrieval_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT check_content_length CHECK (char_length(content) > 0),
    CONSTRAINT check_slice_id_format CHECK (slice_id ~ '^slice_[a-f0-9]{12}$')
);

-- Reasoning chains table for CAG functionality
CREATE TABLE IF NOT EXISTS reasoning_chains (
    chain_id VARCHAR(64) PRIMARY KEY,
    persona_id VARCHAR(64) NOT NULL,
    user_id UUID NOT NULL,
    initial_query TEXT NOT NULL,
    reasoning_steps JSONB NOT NULL,
    final_conclusion TEXT NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    supporting_memories TEXT[], -- Array of memory slice IDs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_chain_id_format CHECK (chain_id ~ '^chain_[a-f0-9]{12}$')
);

-- Vector similarity search index using HNSW (Hierarchical Navigable Small World)
-- This is the most efficient index for high-dimensional vector similarity search
CREATE INDEX IF NOT EXISTS idx_memory_slices_embedding_hnsw 
ON memory_slices USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Traditional indexes for hybrid search and filtering
CREATE INDEX IF NOT EXISTS idx_memory_slices_persona_user 
ON memory_slices (persona_id, user_id);

CREATE INDEX IF NOT EXISTS idx_memory_slices_memory_type 
ON memory_slices (memory_type);

CREATE INDEX IF NOT EXISTS idx_memory_slices_created_at 
ON memory_slices (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_memory_slices_relevance_score 
ON memory_slices (relevance_score DESC);

-- GIN index for keyword array search (hybrid retrieval)
CREATE INDEX IF NOT EXISTS idx_memory_slices_keywords_gin 
ON memory_slices USING gin (keywords);

-- Full-text search index for content
CREATE INDEX IF NOT EXISTS idx_memory_slices_content_fts 
ON memory_slices USING gin (to_tsvector('english', content));

-- Reasoning chains indexes
CREATE INDEX IF NOT EXISTS idx_reasoning_chains_persona_user 
ON reasoning_chains (persona_id, user_id);

CREATE INDEX IF NOT EXISTS idx_reasoning_chains_created_at 
ON reasoning_chains (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reasoning_chains_confidence 
ON reasoning_chains (confidence_score DESC);

-- Function to update last_accessed timestamp
CREATE OR REPLACE FUNCTION update_last_accessed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_accessed = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update last_accessed when retrieval_count changes
CREATE TRIGGER trigger_update_last_accessed
    BEFORE UPDATE OF retrieval_count ON memory_slices
    FOR EACH ROW
    EXECUTE FUNCTION update_last_accessed();

-- Function for semantic similarity search with hybrid filtering
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding vector(384),
    p_persona_id VARCHAR(64),
    p_user_id UUID,
    p_memory_types VARCHAR(32)[] DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_min_similarity REAL DEFAULT 0.0
)
RETURNS TABLE (
    slice_id VARCHAR(64),
    content TEXT,
    memory_type VARCHAR(32),
    keywords TEXT[],
    similarity_score REAL,
    relevance_score REAL,
    created_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE,
    retrieval_count INTEGER,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ms.slice_id,
        ms.content,
        ms.memory_type,
        ms.keywords,
        (1 - (ms.embedding <=> query_embedding))::REAL as similarity_score,
        ms.relevance_score,
        ms.created_at,
        ms.last_accessed,
        ms.retrieval_count,
        ms.metadata
    FROM memory_slices ms
    WHERE 
        ms.persona_id = p_persona_id 
        AND ms.user_id = p_user_id
        AND ms.embedding IS NOT NULL
        AND (p_memory_types IS NULL OR ms.memory_type = ANY(p_memory_types))
        AND (1 - (ms.embedding <=> query_embedding)) >= p_min_similarity
    ORDER BY 
        (1 - (ms.embedding <=> query_embedding)) DESC,
        ms.relevance_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function for hybrid search (keywords + semantic)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(384),
    query_keywords TEXT[],
    p_persona_id VARCHAR(64),
    p_user_id UUID,
    p_memory_types VARCHAR(32)[] DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_keyword_weight REAL DEFAULT 0.3,
    p_semantic_weight REAL DEFAULT 0.7
)
RETURNS TABLE (
    slice_id VARCHAR(64),
    content TEXT,
    memory_type VARCHAR(32),
    keywords TEXT[],
    combined_score REAL,
    semantic_score REAL,
    keyword_score REAL,
    relevance_score REAL,
    created_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE,
    retrieval_count INTEGER,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ms.slice_id,
        ms.content,
        ms.memory_type,
        ms.keywords,
        (
            p_semantic_weight * (1 - (ms.embedding <=> query_embedding)) +
            p_keyword_weight * (
                CASE 
                    WHEN query_keywords IS NULL OR array_length(query_keywords, 1) = 0 THEN 0.0
                    ELSE (
                        array_length(
                            (SELECT array_agg(kw) FROM unnest(ms.keywords) kw WHERE kw = ANY(query_keywords)), 
                            1
                        )::REAL / 
                        GREATEST(array_length(query_keywords, 1), 1)::REAL
                    )
                END
            )
        )::REAL as combined_score,
        (1 - (ms.embedding <=> query_embedding))::REAL as semantic_score,
        (
            CASE 
                WHEN query_keywords IS NULL OR array_length(query_keywords, 1) = 0 THEN 0.0
                ELSE (
                    array_length(
                        (SELECT array_agg(kw) FROM unnest(ms.keywords) kw WHERE kw = ANY(query_keywords)), 
                        1
                    )::REAL / 
                    GREATEST(array_length(query_keywords, 1), 1)::REAL
                )
            END
        )::REAL as keyword_score,
        ms.relevance_score,
        ms.created_at,
        ms.last_accessed,
        ms.retrieval_count,
        ms.metadata
    FROM memory_slices ms
    WHERE 
        ms.persona_id = p_persona_id 
        AND ms.user_id = p_user_id
        AND ms.embedding IS NOT NULL
        AND (p_memory_types IS NULL OR ms.memory_type = ANY(p_memory_types))
    ORDER BY 
        combined_score DESC,
        ms.relevance_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to update retrieval statistics
CREATE OR REPLACE FUNCTION update_retrieval_stats(slice_ids VARCHAR(64)[])
RETURNS VOID AS $$
BEGIN
    UPDATE memory_slices 
    SET 
        retrieval_count = retrieval_count + 1,
        last_accessed = CURRENT_TIMESTAMP
    WHERE slice_id = ANY(slice_ids);
END;
$$ LANGUAGE plpgsql;

-- Create a view for memory statistics
CREATE OR REPLACE VIEW memory_statistics AS
SELECT 
    persona_id,
    user_id,
    memory_type,
    COUNT(*) as slice_count,
    AVG(relevance_score) as avg_relevance_score,
    AVG(retrieval_count) as avg_retrieval_count,
    MAX(last_accessed) as last_accessed,
    MIN(created_at) as first_created,
    MAX(created_at) as last_created
FROM memory_slices
GROUP BY persona_id, user_id, memory_type;

-- Grant permissions to hearthlink_user
GRANT ALL PRIVILEGES ON SCHEMA semantic_memory TO hearthlink_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA semantic_memory TO hearthlink_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA semantic_memory TO hearthlink_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA semantic_memory TO hearthlink_user;

-- Insert a test record to verify the setup
INSERT INTO memory_slices (
    slice_id, persona_id, user_id, content, memory_type, keywords, embedding, relevance_score
) VALUES (
    'slice_test_setup', 'test_persona', gen_random_uuid(), 
    'This is a test memory slice to verify PGVector setup is working correctly.',
    'semantic', 
    ARRAY['test', 'setup', 'verification', 'pgvector'],
    array_fill(0.1, ARRAY[384])::vector(384), -- Test embedding with all 0.1 values
    0.8
) ON CONFLICT (slice_id) DO NOTHING;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PGVector database initialized successfully for Hearthlink semantic memory';
    RAISE NOTICE 'Schema: semantic_memory';
    RAISE NOTICE 'Tables: memory_slices, reasoning_chains';
    RAISE NOTICE 'Functions: semantic_search, hybrid_search, update_retrieval_stats';
    RAISE NOTICE 'Test record inserted with slice_id: slice_test_setup';
END $$;