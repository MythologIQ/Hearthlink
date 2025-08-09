-- Phase 2 Database Schema Enhancements for Alden Memory
-- Extends existing PGVector schema with session_id, user_id, and custom tags
-- Supports multi-agent memory slicing and advanced metadata features

-- Use semantic_memory schema
SET search_path TO semantic_memory, public;

-- Create alden_memory table for persona-specific memory management
CREATE TABLE IF NOT EXISTS alden_memory (
    memory_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL, -- Explicit session tracking
    user_id UUID NOT NULL, -- User identifier for multi-user support
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden', -- Support for multiple agents
    
    -- Core content
    content TEXT NOT NULL,
    memory_type VARCHAR(32) NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'working', 'contextual')),
    memory_category VARCHAR(32) DEFAULT 'general', -- conversation, task, knowledge, preference
    
    -- Semantic embedding and search
    embedding vector(384), -- 384-dimensional embeddings
    keywords TEXT[], -- Extracted keywords for hybrid search
    custom_tags TEXT[] DEFAULT '{}', -- User-defined custom tags
    
    -- Relevance and importance
    relevance_score REAL DEFAULT 0.5 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    importance_score REAL DEFAULT 0.5 CHECK (importance_score >= 0.0 AND importance_score <= 1.0),
    confidence_score REAL DEFAULT 0.8 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Temporal information
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- For working memory expiration
    
    -- Usage statistics
    access_count INTEGER DEFAULT 0,
    retrieval_count INTEGER DEFAULT 0,
    modification_count INTEGER DEFAULT 0,
    
    -- Advanced metadata with JSONB for flexibility
    metadata JSONB DEFAULT '{}',
    
    -- Memory relationships
    parent_memory_id VARCHAR(64) DEFAULT NULL, -- Reference to parent memory
    related_memory_ids TEXT[] DEFAULT '{}', -- Array of related memory IDs
    
    -- Session and context information
    conversation_turn INTEGER DEFAULT NULL, -- Turn number in conversation
    context_window TEXT DEFAULT NULL, -- Context window when memory was created
    
    -- Version control and sync
    version INTEGER DEFAULT 1,
    sync_status VARCHAR(16) DEFAULT 'synced' CHECK (sync_status IN ('synced', 'pending', 'conflict', 'deleted')),
    last_sync_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_content_length CHECK (char_length(content) > 0),
    CONSTRAINT check_memory_id_format CHECK (memory_id ~ '^mem_[a-f0-9]+$'),
    CONSTRAINT check_session_id_format CHECK (session_id ~ '^sess_[a-f0-9]+$'),
    CONSTRAINT fk_parent_memory FOREIGN KEY (parent_memory_id) REFERENCES alden_memory(memory_id) ON DELETE SET NULL
);

-- Session tracking table for comprehensive session management
CREATE TABLE IF NOT EXISTS alden_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Session metadata
    session_name VARCHAR(128) DEFAULT NULL,
    session_type VARCHAR(32) DEFAULT 'conversation', -- conversation, task, learning
    session_status VARCHAR(16) DEFAULT 'active' CHECK (session_status IN ('active', 'paused', 'completed', 'archived')),
    
    -- Temporal information
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    -- Session statistics
    total_turns INTEGER DEFAULT 0,
    total_memories_created INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    
    -- Session context and settings
    context_summary TEXT DEFAULT NULL,
    session_settings JSONB DEFAULT '{}',
    
    -- Memory management
    memory_retention_policy VARCHAR(32) DEFAULT 'standard', -- standard, extended, minimal
    auto_archive_after_days INTEGER DEFAULT 30,
    
    CONSTRAINT check_session_id_format CHECK (session_id ~ '^sess_[a-f0-9]+$')
);

-- Memory tags table for advanced tagging system
CREATE TABLE IF NOT EXISTS alden_memory_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(64) NOT NULL,
    tag_category VARCHAR(32) DEFAULT 'user', -- user, system, auto, semantic
    tag_color VARCHAR(7) DEFAULT '#808080', -- Hex color for UI
    
    -- Tag metadata
    description TEXT DEFAULT NULL,
    created_by UUID DEFAULT NULL, -- User who created the tag
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    
    -- Tag behavior
    is_hierarchical BOOLEAN DEFAULT FALSE,
    parent_tag_id INTEGER DEFAULT NULL,
    auto_apply_rules JSONB DEFAULT '{}',
    
    CONSTRAINT unique_tag_name UNIQUE (tag_name),
    CONSTRAINT fk_parent_tag FOREIGN KEY (parent_tag_id) REFERENCES alden_memory_tags(tag_id) ON DELETE SET NULL
);

-- Junction table for memory-tag relationships (many-to-many)
CREATE TABLE IF NOT EXISTS alden_memory_tag_relations (
    memory_id VARCHAR(64) NOT NULL,
    tag_id INTEGER NOT NULL,
    tagged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tagged_by VARCHAR(32) DEFAULT 'system', -- system, user, auto
    confidence REAL DEFAULT 1.0,
    
    PRIMARY KEY (memory_id, tag_id),
    FOREIGN KEY (memory_id) REFERENCES alden_memory(memory_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES alden_memory_tags(tag_id) ON DELETE CASCADE
);

-- Enhanced indexes for optimal performance

-- Primary indexes for alden_memory
CREATE INDEX IF NOT EXISTS idx_alden_memory_session_user 
ON alden_memory (session_id, user_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_agent_user 
ON alden_memory (agent_id, user_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_type_category 
ON alden_memory (memory_type, memory_category);

CREATE INDEX IF NOT EXISTS idx_alden_memory_created_at 
ON alden_memory (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_updated_at 
ON alden_memory (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_last_accessed 
ON alden_memory (last_accessed DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_expires_at 
ON alden_memory (expires_at) WHERE expires_at IS NOT NULL;

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_alden_memory_embedding_hnsw 
ON alden_memory USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Relevance and importance indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_relevance_score 
ON alden_memory (relevance_score DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_importance_score 
ON alden_memory (importance_score DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_confidence_score 
ON alden_memory (confidence_score DESC);

-- GIN indexes for array fields
CREATE INDEX IF NOT EXISTS idx_alden_memory_keywords_gin 
ON alden_memory USING gin (keywords);

CREATE INDEX IF NOT EXISTS idx_alden_memory_custom_tags_gin 
ON alden_memory USING gin (custom_tags);

CREATE INDEX IF NOT EXISTS idx_alden_memory_related_ids_gin 
ON alden_memory USING gin (related_memory_ids);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_alden_memory_content_fts 
ON alden_memory USING gin (to_tsvector('english', content));

-- JSONB metadata index
CREATE INDEX IF NOT EXISTS idx_alden_memory_metadata_gin 
ON alden_memory USING gin (metadata);

-- Sync status index
CREATE INDEX IF NOT EXISTS idx_alden_memory_sync_status 
ON alden_memory (sync_status) WHERE sync_status != 'synced';

-- Session indexes
CREATE INDEX IF NOT EXISTS idx_alden_sessions_user_agent 
ON alden_sessions (user_id, agent_id);

CREATE INDEX IF NOT EXISTS idx_alden_sessions_status 
ON alden_sessions (session_status);

CREATE INDEX IF NOT EXISTS idx_alden_sessions_last_activity 
ON alden_sessions (last_activity_at DESC);

-- Tag indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_tags_category 
ON alden_memory_tags (tag_category);

CREATE INDEX IF NOT EXISTS idx_alden_memory_tags_usage_count 
ON alden_memory_tags (usage_count DESC);

-- Tag relations indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_tag_relations_memory 
ON alden_memory_tag_relations (memory_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_tag_relations_tag 
ON alden_memory_tag_relations (tag_id);

-- Functions for enhanced memory operations

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_alden_memory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.modification_count = OLD.modification_count + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updating timestamps
CREATE TRIGGER trigger_alden_memory_updated_at
    BEFORE UPDATE ON alden_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_alden_memory_updated_at();

-- Function to update access statistics
CREATE OR REPLACE FUNCTION update_alden_memory_access_stats(memory_ids VARCHAR(64)[])
RETURNS VOID AS $$
BEGIN
    UPDATE alden_memory 
    SET 
        access_count = access_count + 1,
        retrieval_count = retrieval_count + 1,
        last_accessed = CURRENT_TIMESTAMP
    WHERE memory_id = ANY(memory_ids);
END;
$$ LANGUAGE plpgsql;

-- Enhanced semantic search function for Alden memory
CREATE OR REPLACE FUNCTION alden_semantic_search(
    query_embedding vector(384),
    p_user_id UUID,
    p_agent_id VARCHAR(32) DEFAULT 'alden',
    p_session_id VARCHAR(64) DEFAULT NULL,
    p_memory_types VARCHAR(32)[] DEFAULT NULL,
    p_memory_categories VARCHAR(32)[] DEFAULT NULL,
    p_custom_tags TEXT[] DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_min_similarity REAL DEFAULT 0.3,
    p_include_expired BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    memory_id VARCHAR(64),
    session_id VARCHAR(64),
    content TEXT,
    memory_type VARCHAR(32),
    memory_category VARCHAR(32),
    keywords TEXT[],
    custom_tags TEXT[],
    similarity_score REAL,
    relevance_score REAL,
    importance_score REAL,
    confidence_score REAL,
    created_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE,
    retrieval_count INTEGER,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        am.memory_id,
        am.session_id,
        am.content,
        am.memory_type,
        am.memory_category,
        am.keywords,
        am.custom_tags,
        (1 - (am.embedding <=> query_embedding))::REAL as similarity_score,
        am.relevance_score,
        am.importance_score,
        am.confidence_score,
        am.created_at,
        am.last_accessed,
        am.retrieval_count,
        am.metadata
    FROM alden_memory am
    WHERE 
        am.user_id = p_user_id
        AND am.agent_id = p_agent_id
        AND am.embedding IS NOT NULL
        AND (p_session_id IS NULL OR am.session_id = p_session_id)
        AND (p_memory_types IS NULL OR am.memory_type = ANY(p_memory_types))
        AND (p_memory_categories IS NULL OR am.memory_category = ANY(p_memory_categories))
        AND (p_custom_tags IS NULL OR am.custom_tags && p_custom_tags) -- Array overlap operator
        AND (p_include_expired OR am.expires_at IS NULL OR am.expires_at > CURRENT_TIMESTAMP)
        AND (1 - (am.embedding <=> query_embedding)) >= p_min_similarity
        AND am.sync_status != 'deleted'
    ORDER BY 
        (1 - (am.embedding <=> query_embedding)) DESC,
        am.importance_score DESC,
        am.relevance_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function for session-aware hybrid search
CREATE OR REPLACE FUNCTION alden_hybrid_search(
    query_text TEXT,
    query_embedding vector(384),
    query_keywords TEXT[],
    p_user_id UUID,
    p_agent_id VARCHAR(32) DEFAULT 'alden',
    p_session_id VARCHAR(64) DEFAULT NULL,
    p_memory_types VARCHAR(32)[] DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_keyword_weight REAL DEFAULT 0.3,
    p_semantic_weight REAL DEFAULT 0.7,
    p_session_boost REAL DEFAULT 0.1 -- Boost for same-session memories
)
RETURNS TABLE (
    memory_id VARCHAR(64),
    session_id VARCHAR(64),
    content TEXT,
    memory_type VARCHAR(32),
    combined_score REAL,
    semantic_score REAL,
    keyword_score REAL,
    session_boost REAL,
    relevance_score REAL,
    importance_score REAL,
    created_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        am.memory_id,
        am.session_id,
        am.content,
        am.memory_type,
        (
            p_semantic_weight * (1 - (am.embedding <=> query_embedding)) +
            p_keyword_weight * (
                CASE 
                    WHEN query_keywords IS NULL OR array_length(query_keywords, 1) = 0 THEN 0.0
                    ELSE (
                        array_length(
                            (SELECT array_agg(kw) FROM unnest(am.keywords) kw WHERE kw = ANY(query_keywords)), 
                            1
                        )::REAL / 
                        GREATEST(array_length(query_keywords, 1), 1)::REAL
                    )
                END
            ) +
            (CASE WHEN p_session_id IS NOT NULL AND am.session_id = p_session_id THEN p_session_boost ELSE 0.0 END)
        )::REAL as combined_score,
        (1 - (am.embedding <=> query_embedding))::REAL as semantic_score,
        (
            CASE 
                WHEN query_keywords IS NULL OR array_length(query_keywords, 1) = 0 THEN 0.0
                ELSE (
                    array_length(
                        (SELECT array_agg(kw) FROM unnest(am.keywords) kw WHERE kw = ANY(query_keywords)), 
                        1
                    )::REAL / 
                    GREATEST(array_length(query_keywords, 1), 1)::REAL
                )
            END
        )::REAL as keyword_score,
        (CASE WHEN p_session_id IS NOT NULL AND am.session_id = p_session_id THEN p_session_boost ELSE 0.0 END)::REAL as session_boost,
        am.relevance_score,
        am.importance_score,
        am.created_at,
        am.metadata
    FROM alden_memory am
    WHERE 
        am.user_id = p_user_id
        AND am.agent_id = p_agent_id
        AND am.embedding IS NOT NULL
        AND (p_memory_types IS NULL OR am.memory_type = ANY(p_memory_types))
        AND (am.expires_at IS NULL OR am.expires_at > CURRENT_TIMESTAMP)
        AND am.sync_status != 'deleted'
    ORDER BY 
        combined_score DESC,
        am.importance_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired working memory
CREATE OR REPLACE FUNCTION cleanup_expired_memories()
RETURNS INTEGER AS $$
DECLARE
    cleanup_count INTEGER;
BEGIN
    UPDATE alden_memory 
    SET sync_status = 'deleted'
    WHERE 
        expires_at IS NOT NULL 
        AND expires_at < CURRENT_TIMESTAMP
        AND memory_type = 'working'
        AND sync_status != 'deleted';
    
    GET DIAGNOSTICS cleanup_count = ROW_COUNT;
    
    RETURN cleanup_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update session activity
CREATE OR REPLACE FUNCTION update_session_activity(p_session_id VARCHAR(64))
RETURNS VOID AS $$
BEGIN
    UPDATE alden_sessions 
    SET 
        last_activity_at = CURRENT_TIMESTAMP,
        total_turns = total_turns + 1
    WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Views for comprehensive memory statistics

-- Enhanced memory statistics view
CREATE OR REPLACE VIEW alden_memory_statistics AS
SELECT 
    am.user_id,
    am.agent_id,
    am.session_id,
    am.memory_type,
    am.memory_category,
    COUNT(*) as memory_count,
    AVG(am.relevance_score) as avg_relevance_score,
    AVG(am.importance_score) as avg_importance_score,
    AVG(am.confidence_score) as avg_confidence_score,
    AVG(am.retrieval_count) as avg_retrieval_count,
    MAX(am.last_accessed) as last_accessed,
    MIN(am.created_at) as first_created,
    MAX(am.created_at) as last_created,
    COUNT(CASE WHEN am.sync_status = 'pending' THEN 1 END) as pending_sync_count,
    COUNT(CASE WHEN am.sync_status = 'conflict' THEN 1 END) as conflict_count
FROM alden_memory am
WHERE am.sync_status != 'deleted'
GROUP BY am.user_id, am.agent_id, am.session_id, am.memory_type, am.memory_category;

-- Session summary view
CREATE OR REPLACE VIEW alden_session_summary AS
SELECT 
    s.session_id,
    s.user_id,
    s.agent_id,
    s.session_name,
    s.session_type,
    s.session_status,
    s.started_at,
    s.last_activity_at,
    s.ended_at,
    s.total_turns,
    COUNT(am.memory_id) as actual_memories_created,
    AVG(am.importance_score) as avg_memory_importance,
    MAX(am.created_at) as last_memory_created
FROM alden_sessions s
LEFT JOIN alden_memory am ON s.session_id = am.session_id AND am.sync_status != 'deleted'
GROUP BY s.session_id, s.user_id, s.agent_id, s.session_name, s.session_type, 
         s.session_status, s.started_at, s.last_activity_at, s.ended_at, s.total_turns;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE alden_memory TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_sessions TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_memory_tags TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_memory_tag_relations TO hearthlink_user;
GRANT ALL PRIVILEGES ON SEQUENCE alden_memory_tags_tag_id_seq TO hearthlink_user;

-- Insert initial system tags
INSERT INTO alden_memory_tags (tag_name, tag_category, description, tag_color) VALUES
    ('important', 'system', 'High importance memories', '#ff4444'),
    ('task', 'system', 'Task-related memories', '#4444ff'),
    ('preference', 'system', 'User preference memories', '#44ff44'),
    ('context', 'system', 'Contextual information', '#ffaa44'),
    ('error', 'system', 'Error or problem memories', '#ff8844'),
    ('success', 'system', 'Successful outcome memories', '#44ff88'),
    ('learning', 'system', 'Learning and knowledge memories', '#8844ff'),
    ('conversation', 'system', 'Conversational memories', '#44aaff')
ON CONFLICT (tag_name) DO NOTHING;

-- Insert test data for validation
DO $$
DECLARE
    test_session_id VARCHAR(64) := 'sess_' || encode(gen_random_bytes(16), 'hex');
    test_user_id UUID := gen_random_uuid();
    test_memory_id VARCHAR(64) := 'mem_' || encode(gen_random_bytes(16), 'hex');
BEGIN
    -- Insert test session
    INSERT INTO alden_sessions (
        session_id, user_id, agent_id, session_name, session_type
    ) VALUES (
        test_session_id, test_user_id, 'alden', 'Phase 2 Test Session', 'conversation'
    );
    
    -- Insert test memory
    INSERT INTO alden_memory (
        memory_id, session_id, user_id, agent_id, content, memory_type, memory_category,
        keywords, custom_tags, embedding, relevance_score, importance_score
    ) VALUES (
        test_memory_id, test_session_id, test_user_id, 'alden',
        'This is a Phase 2 test memory with enhanced schema featuring session tracking, custom tags, and improved metadata.',
        'episodic', 'conversation',
        ARRAY['phase2', 'test', 'schema', 'enhancement'],
        ARRAY['test', 'validation'],
        array_fill(0.2, ARRAY[384])::vector(384),
        0.9, 0.8
    );
    
    RAISE NOTICE 'Phase 2 test data inserted successfully';
    RAISE NOTICE 'Test session ID: %', test_session_id;
    RAISE NOTICE 'Test memory ID: %', test_memory_id;
END $$;

-- Log successful migration
DO $$
BEGIN
    RAISE NOTICE 'Phase 2 Alden memory schema migration completed successfully';
    RAISE NOTICE 'New tables: alden_memory, alden_sessions, alden_memory_tags, alden_memory_tag_relations';
    RAISE NOTICE 'Enhanced features: session tracking, custom tags, advanced metadata, multi-agent support';
    RAISE NOTICE 'New functions: alden_semantic_search, alden_hybrid_search, cleanup_expired_memories';
    RAISE NOTICE 'New views: alden_memory_statistics, alden_session_summary';
END $$;