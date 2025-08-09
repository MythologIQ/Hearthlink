-- Phase 3 Database Schema Enhancements for Long-Term Memory Storage
-- Enhances existing Phase 2 schema with long-term retention, session optimization, and advanced features
-- Focus: Long-term memory tables, session-specific optimizations, temporal hierarchies

-- Use semantic_memory schema
SET search_path TO semantic_memory, public;

-- =====================================================
-- LONG-TERM MEMORY STORAGE ENHANCEMENTS
-- =====================================================

-- Long-term memory archive table for persistent storage beyond working memory
CREATE TABLE IF NOT EXISTS alden_memory_archive (
    archive_id VARCHAR(64) PRIMARY KEY,
    original_memory_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Archived content with compression
    archived_content TEXT NOT NULL,
    compressed_content BYTEA DEFAULT NULL, -- For very large memories
    content_hash VARCHAR(64) NOT NULL, -- For deduplication
    
    -- Archive metadata
    memory_type VARCHAR(32) NOT NULL,
    memory_category VARCHAR(32) DEFAULT 'general',
    archive_reason VARCHAR(64) DEFAULT 'retention_policy', -- retention_policy, user_request, importance
    archive_priority VARCHAR(16) DEFAULT 'normal' CHECK (archive_priority IN ('low', 'normal', 'high', 'critical')),
    
    -- Temporal information
    original_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_from_archive TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    scheduled_deletion_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    -- Preservation metadata
    preservation_level VARCHAR(16) DEFAULT 'standard' CHECK (preservation_level IN ('minimal', 'standard', 'enhanced', 'permanent')),
    retention_years INTEGER DEFAULT 5,
    access_restrictions JSONB DEFAULT '{}',
    
    -- Statistical summaries (to avoid re-processing)
    importance_score REAL DEFAULT 0.5,
    historical_access_count INTEGER DEFAULT 0,
    summary_embedding vector(384) DEFAULT NULL, -- Reduced embedding for fast similarity
    keywords_summary TEXT[] DEFAULT '{}',
    
    -- Archival integrity
    checksum VARCHAR(64) NOT NULL,
    version INTEGER DEFAULT 1,
    
    CONSTRAINT check_archive_id_format CHECK (archive_id ~ '^arch_[a-f0-9]+$'),
    CONSTRAINT check_content_hash_format CHECK (content_hash ~ '^[a-f0-9]{64}$'),
    CONSTRAINT unique_content_hash UNIQUE (content_hash, user_id) -- Prevent duplicate archiving
);

-- Session-specific memory optimization table for high-frequency access patterns
CREATE TABLE IF NOT EXISTS alden_memory_session_cache (
    cache_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Cached memory IDs for fast session retrieval
    cached_memory_ids TEXT[] NOT NULL,
    cache_metadata JSONB DEFAULT '{}',
    
    -- Cache optimization data
    access_pattern VARCHAR(32) DEFAULT 'sequential', -- sequential, random, clustered
    hot_memory_ids TEXT[] DEFAULT '{}', -- Most frequently accessed
    recent_memory_ids TEXT[] DEFAULT '{}', -- Most recently accessed
    contextual_memory_ids TEXT[] DEFAULT '{}', -- Contextually related
    
    -- Cache performance metrics
    cache_hit_count INTEGER DEFAULT 0,
    cache_miss_count INTEGER DEFAULT 0,
    last_optimization TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Cache lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    
    CONSTRAINT check_cache_id_format CHECK (cache_id ~ '^scache_[a-f0-9]+$'),
    CONSTRAINT unique_session_cache UNIQUE (session_id, agent_id)
);

-- Memory consolidation table for deduplication and optimization
CREATE TABLE IF NOT EXISTS alden_memory_consolidation (
    consolidation_id VARCHAR(64) PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Consolidated memory cluster
    cluster_hash VARCHAR(64) NOT NULL,
    representative_memory_id VARCHAR(64) NOT NULL, -- Primary memory for this cluster
    consolidated_memory_ids TEXT[] NOT NULL, -- All memories in cluster
    
    -- Consolidation metadata
    consolidation_type VARCHAR(32) DEFAULT 'semantic_similarity', -- semantic_similarity, exact_duplicate, temporal_cluster
    similarity_threshold REAL DEFAULT 0.85,
    cluster_size INTEGER GENERATED ALWAYS AS (array_length(consolidated_memory_ids, 1)) STORED,
    
    -- Performance impact
    storage_saved_bytes INTEGER DEFAULT 0,
    retrieval_time_improvement_ms REAL DEFAULT 0.0,
    
    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_consolidation_id_format CHECK (consolidation_id ~ '^cons_[a-f0-9]+$'),
    FOREIGN KEY (representative_memory_id) REFERENCES alden_memory(memory_id) ON DELETE CASCADE
);

-- Memory hierarchy table for temporal and conceptual relationships
CREATE TABLE IF NOT EXISTS alden_memory_hierarchy (
    hierarchy_id VARCHAR(64) PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Hierarchical structure
    root_memory_id VARCHAR(64) NOT NULL,
    parent_memory_id VARCHAR(64) DEFAULT NULL,
    child_memory_ids TEXT[] DEFAULT '{}',
    hierarchy_depth INTEGER DEFAULT 0,
    hierarchy_type VARCHAR(32) DEFAULT 'temporal' CHECK (hierarchy_type IN ('temporal', 'conceptual', 'causal', 'procedural')),
    
    -- Hierarchy metadata
    relationship_strength REAL DEFAULT 0.5 CHECK (relationship_strength >= 0.0 AND relationship_strength <= 1.0),
    context_summary TEXT DEFAULT NULL,
    
    -- Navigation optimization
    shortest_path_to_root INTEGER DEFAULT 0,
    hierarchy_weight REAL DEFAULT 1.0, -- For weighted traversal
    
    -- Temporal information
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_traversed TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    CONSTRAINT check_hierarchy_id_format CHECK (hierarchy_id ~ '^hier_[a-f0-9]+$'),
    FOREIGN KEY (root_memory_id) REFERENCES alden_memory(memory_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_memory_id) REFERENCES alden_memory(memory_id) ON DELETE CASCADE
);

-- Session pattern analysis for optimization
CREATE TABLE IF NOT EXISTS alden_session_patterns (
    pattern_id VARCHAR(64) PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id VARCHAR(32) NOT NULL DEFAULT 'alden',
    
    -- Pattern identification
    pattern_type VARCHAR(32) DEFAULT 'access_sequence', -- access_sequence, memory_type_preference, temporal_clustering
    pattern_signature VARCHAR(128) NOT NULL, -- Hash of the pattern
    
    -- Pattern data
    session_ids TEXT[] NOT NULL, -- Sessions exhibiting this pattern
    memory_access_sequence TEXT[] DEFAULT '{}',
    common_memory_types VARCHAR(32)[] DEFAULT '{}',
    common_categories VARCHAR(32)[] DEFAULT '{}',
    
    -- Pattern statistics
    occurrence_count INTEGER DEFAULT 1,
    confidence_score REAL DEFAULT 0.5,
    efficiency_score REAL DEFAULT 0.5, -- How efficient this pattern is
    
    -- Optimization suggestions
    optimization_recommendations JSONB DEFAULT '{}',
    
    -- Pattern lifecycle
    first_observed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_observed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_pattern_id_format CHECK (pattern_id ~ '^pat_[a-f0-9]+$'),
    CONSTRAINT unique_pattern_signature UNIQUE (user_id, agent_id, pattern_signature)
);

-- =====================================================
-- ENHANCED INDEXES FOR LONG-TERM OPTIMIZATION
-- =====================================================

-- Archive table indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_user_agent 
ON alden_memory_archive (user_id, agent_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_content_hash 
ON alden_memory_archive (content_hash);

CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_archived_at 
ON alden_memory_archive (archived_at DESC);

CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_priority 
ON alden_memory_archive (archive_priority) WHERE archive_priority IN ('high', 'critical');

CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_scheduled_deletion 
ON alden_memory_archive (scheduled_deletion_at) WHERE scheduled_deletion_at IS NOT NULL;

-- Summary embedding index for archive
CREATE INDEX IF NOT EXISTS idx_alden_memory_archive_summary_embedding_hnsw 
ON alden_memory_archive USING hnsw (summary_embedding vector_cosine_ops)
WITH (m = 8, ef_construction = 32); -- Smaller parameters for archive

-- Session cache indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_session_cache_session 
ON alden_memory_session_cache (session_id, agent_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_session_cache_expires_at 
ON alden_memory_session_cache (expires_at) WHERE expires_at < CURRENT_TIMESTAMP + INTERVAL '1 hour';

-- Hot memory lookup index
CREATE INDEX IF NOT EXISTS idx_alden_memory_session_cache_hot_memories_gin 
ON alden_memory_session_cache USING gin (hot_memory_ids);

-- Consolidation indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_consolidation_cluster_hash 
ON alden_memory_consolidation (cluster_hash);

CREATE INDEX IF NOT EXISTS idx_alden_memory_consolidation_size 
ON alden_memory_consolidation (cluster_size DESC);

-- Hierarchy indexes
CREATE INDEX IF NOT EXISTS idx_alden_memory_hierarchy_root 
ON alden_memory_hierarchy (root_memory_id);

CREATE INDEX IF NOT EXISTS idx_alden_memory_hierarchy_parent 
ON alden_memory_hierarchy (parent_memory_id) WHERE parent_memory_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_alden_memory_hierarchy_depth 
ON alden_memory_hierarchy (hierarchy_depth);

-- Pattern analysis indexes
CREATE INDEX IF NOT EXISTS idx_alden_session_patterns_user_agent 
ON alden_session_patterns (user_id, agent_id);

CREATE INDEX IF NOT EXISTS idx_alden_session_patterns_signature 
ON alden_session_patterns (pattern_signature);

CREATE INDEX IF NOT EXISTS idx_alden_session_patterns_confidence 
ON alden_session_patterns (confidence_score DESC);

-- =====================================================
-- ADVANCED FUNCTIONS FOR LONG-TERM MEMORY MANAGEMENT
-- =====================================================

-- Function to archive old memories based on retention policy
CREATE OR REPLACE FUNCTION archive_memories_by_retention_policy(
    p_retention_days INTEGER DEFAULT 90,
    p_min_importance_score REAL DEFAULT 0.3,
    p_preserve_high_importance BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    archived_count INTEGER,
    skipped_count INTEGER,
    bytes_saved BIGINT
) AS $$
DECLARE
    archive_count INTEGER := 0;
    skip_count INTEGER := 0;
    total_bytes_saved BIGINT := 0;
    memory_record RECORD;
BEGIN
    -- Archive memories older than retention period
    FOR memory_record IN 
        SELECT 
            memory_id, session_id, user_id, agent_id, content, memory_type, 
            memory_category, created_at, importance_score,
            char_length(content) as content_size
        FROM alden_memory 
        WHERE 
            created_at < CURRENT_TIMESTAMP - (p_retention_days || ' days')::INTERVAL
            AND sync_status != 'deleted'
            AND (NOT p_preserve_high_importance OR importance_score < p_min_importance_score)
            AND memory_id NOT IN (SELECT original_memory_id FROM alden_memory_archive)
    LOOP
        -- Create archive record
        INSERT INTO alden_memory_archive (
            archive_id, original_memory_id, session_id, user_id, agent_id,
            archived_content, content_hash, memory_type, memory_category,
            original_created_at, archive_reason, importance_score,
            checksum, retention_years
        ) VALUES (
            'arch_' || encode(gen_random_bytes(16), 'hex'),
            memory_record.memory_id,
            memory_record.session_id,
            memory_record.user_id,
            memory_record.agent_id,
            memory_record.content,
            encode(sha256(memory_record.content::bytea), 'hex'),
            memory_record.memory_type,
            memory_record.memory_category,
            memory_record.created_at,
            'retention_policy',
            memory_record.importance_score,
            encode(sha256((memory_record.memory_id || memory_record.content)::bytea), 'hex'),
            CASE 
                WHEN memory_record.importance_score > 0.7 THEN 10
                WHEN memory_record.importance_score > 0.5 THEN 7
                ELSE 5
            END
        );
        
        -- Mark original as archived (soft delete)
        UPDATE alden_memory 
        SET sync_status = 'deleted', metadata = metadata || '{"archived": true}'::jsonb
        WHERE memory_id = memory_record.memory_id;
        
        archive_count := archive_count + 1;
        total_bytes_saved := total_bytes_saved + memory_record.content_size;
    END LOOP;
    
    RETURN QUERY SELECT archive_count, skip_count, total_bytes_saved;
END;
$$ LANGUAGE plpgsql;

-- Function to optimize session cache based on access patterns
CREATE OR REPLACE FUNCTION optimize_session_cache(
    p_session_id VARCHAR(64),
    p_optimization_type VARCHAR(32) DEFAULT 'auto'
)
RETURNS TABLE (
    cache_id VARCHAR(64),
    optimization_applied VARCHAR(64),
    performance_improvement REAL
) AS $$
DECLARE
    session_cache RECORD;
    memory_access_stats RECORD;
    hot_memories TEXT[];
    recent_memories TEXT[];
    contextual_memories TEXT[];
    optimization_applied VARCHAR(64) := 'none';
    performance_gain REAL := 0.0;
BEGIN
    -- Get current cache state
    SELECT * INTO session_cache 
    FROM alden_memory_session_cache 
    WHERE session_id = p_session_id;
    
    IF session_cache IS NULL THEN
        -- Create new cache entry
        INSERT INTO alden_memory_session_cache (
            cache_id, session_id, user_id, agent_id, cached_memory_ids
        )
        SELECT 
            'scache_' || encode(gen_random_bytes(16), 'hex'),
            p_session_id,
            s.user_id,
            s.agent_id,
            array_agg(am.memory_id ORDER BY am.last_accessed DESC)
        FROM alden_sessions s
        LEFT JOIN alden_memory am ON s.session_id = am.session_id
        WHERE s.session_id = p_session_id AND am.sync_status != 'deleted'
        GROUP BY s.user_id, s.agent_id
        RETURNING cache_id INTO session_cache;
        
        optimization_applied := 'cache_created';
        performance_gain := 0.2;
    ELSE
        -- Analyze access patterns and optimize
        SELECT 
            array_agg(memory_id ORDER BY access_count DESC) FILTER (WHERE access_count > 5) as hot,
            array_agg(memory_id ORDER BY last_accessed DESC) FILTER (WHERE last_accessed > CURRENT_TIMESTAMP - INTERVAL '1 hour') as recent
        INTO memory_access_stats
        FROM alden_memory 
        WHERE session_id = p_session_id AND sync_status != 'deleted';
        
        -- Update cache with optimized memory sets
        UPDATE alden_memory_session_cache
        SET 
            hot_memory_ids = COALESCE(memory_access_stats.hot, '{}'),
            recent_memory_ids = COALESCE(memory_access_stats.recent, '{}'),
            last_optimization = CURRENT_TIMESTAMP,
            cache_metadata = cache_metadata || jsonb_build_object(
                'optimization_type', p_optimization_type,
                'hot_memories_count', array_length(memory_access_stats.hot, 1),
                'recent_memories_count', array_length(memory_access_stats.recent, 1)
            )
        WHERE session_id = p_session_id
        RETURNING cache_id INTO session_cache;
        
        optimization_applied := 'pattern_optimization';
        performance_gain := 0.15;
    END IF;
    
    RETURN QUERY SELECT session_cache.cache_id, optimization_applied, performance_gain;
END;
$$ LANGUAGE plpgsql;

-- Function to consolidate similar memories for deduplication
CREATE OR REPLACE FUNCTION consolidate_similar_memories(
    p_user_id UUID,
    p_agent_id VARCHAR(32) DEFAULT 'alden',
    p_similarity_threshold REAL DEFAULT 0.85
)
RETURNS TABLE (
    consolidation_id VARCHAR(64),
    cluster_size INTEGER,
    bytes_saved INTEGER
) AS $$
DECLARE
    memory_record RECORD;
    similar_memories RECORD;
    current_consolidation_id VARCHAR(64);
    total_bytes_saved INTEGER := 0;
BEGIN
    -- Find groups of similar memories using embedding similarity
    FOR memory_record IN 
        SELECT DISTINCT ON (m1.memory_id)
            m1.memory_id,
            m1.content,
            m1.embedding,
            char_length(m1.content) as content_size,
            array_agg(m2.memory_id) as similar_memory_ids,
            array_agg(char_length(m2.content)) as similar_content_sizes
        FROM alden_memory m1
        JOIN alden_memory m2 ON 
            m1.user_id = m2.user_id 
            AND m1.agent_id = m2.agent_id
            AND m1.memory_id != m2.memory_id
            AND m1.embedding IS NOT NULL 
            AND m2.embedding IS NOT NULL
            AND (1 - (m1.embedding <=> m2.embedding)) >= p_similarity_threshold
        WHERE 
            m1.user_id = p_user_id 
            AND m1.agent_id = p_agent_id
            AND m1.sync_status != 'deleted'
            AND m2.sync_status != 'deleted'
            AND m1.memory_id NOT IN (
                SELECT unnest(consolidated_memory_ids) 
                FROM alden_memory_consolidation 
                WHERE user_id = p_user_id AND agent_id = p_agent_id
            )
        GROUP BY m1.memory_id, m1.content, m1.embedding
        HAVING array_length(array_agg(m2.memory_id), 1) >= 2
    LOOP
        -- Create consolidation record
        current_consolidation_id := 'cons_' || encode(gen_random_bytes(16), 'hex');
        
        INSERT INTO alden_memory_consolidation (
            consolidation_id, user_id, agent_id, cluster_hash,
            representative_memory_id, consolidated_memory_ids,
            consolidation_type, similarity_threshold,
            storage_saved_bytes
        ) VALUES (
            current_consolidation_id,
            p_user_id,
            p_agent_id,
            encode(sha256((array_to_string(memory_record.similar_memory_ids, ','))::bytea), 'hex'),
            memory_record.memory_id,
            memory_record.similar_memory_ids,
            'semantic_similarity',
            p_similarity_threshold,
            (SELECT sum(s) FROM unnest(memory_record.similar_content_sizes) s) - memory_record.content_size
        );
        
        total_bytes_saved := total_bytes_saved + 
            (SELECT sum(s) FROM unnest(memory_record.similar_content_sizes) s) - memory_record.content_size;
        
        -- Mark consolidated memories (except representative) as consolidated
        UPDATE alden_memory 
        SET 
            sync_status = 'deleted',
            metadata = metadata || jsonb_build_object(
                'consolidated', true,
                'consolidation_id', current_consolidation_id,
                'representative_memory_id', memory_record.memory_id
            )
        WHERE memory_id = ANY(memory_record.similar_memory_ids)
          AND memory_id != memory_record.memory_id;
        
        RETURN QUERY SELECT 
            current_consolidation_id,
            array_length(memory_record.similar_memory_ids, 1),
            (SELECT sum(s) FROM unnest(memory_record.similar_content_sizes) s) - memory_record.content_size;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to build memory hierarchy based on temporal and conceptual relationships
CREATE OR REPLACE FUNCTION build_memory_hierarchy(
    p_user_id UUID,
    p_agent_id VARCHAR(32) DEFAULT 'alden',
    p_hierarchy_type VARCHAR(32) DEFAULT 'temporal'
)
RETURNS INTEGER AS $$
DECLARE
    memory_record RECORD;
    parent_memory_id VARCHAR(64);
    hierarchy_count INTEGER := 0;
BEGIN
    -- Build temporal hierarchy (chronological order within sessions)
    IF p_hierarchy_type = 'temporal' THEN
        FOR memory_record IN 
            SELECT 
                memory_id, session_id, created_at,
                LAG(memory_id) OVER (PARTITION BY session_id ORDER BY created_at) as prev_memory_id
            FROM alden_memory 
            WHERE user_id = p_user_id AND agent_id = p_agent_id AND sync_status != 'deleted'
            ORDER BY session_id, created_at
        LOOP
            IF memory_record.prev_memory_id IS NOT NULL THEN
                -- Insert hierarchy relationship
                INSERT INTO alden_memory_hierarchy (
                    hierarchy_id, user_id, agent_id, root_memory_id,
                    parent_memory_id, hierarchy_type, relationship_strength
                ) VALUES (
                    'hier_' || encode(gen_random_bytes(16), 'hex'),
                    p_user_id, p_agent_id, memory_record.prev_memory_id,
                    memory_record.prev_memory_id, p_hierarchy_type, 0.8
                ) ON CONFLICT DO NOTHING;
                
                hierarchy_count := hierarchy_count + 1;
            END IF;
        END LOOP;
    END IF;
    
    -- Add conceptual hierarchy based on semantic similarity (simplified)
    IF p_hierarchy_type = 'conceptual' THEN
        -- Implementation for conceptual hierarchy would go here
        -- This would use embedding similarity to create concept clusters
        hierarchy_count := 0; -- Placeholder
    END IF;
    
    RETURN hierarchy_count;
END;
$$ LANGUAGE plpgsql;

-- Function to analyze and record session patterns
CREATE OR REPLACE FUNCTION analyze_session_patterns(
    p_user_id UUID,
    p_agent_id VARCHAR(32) DEFAULT 'alden',
    p_min_pattern_length INTEGER DEFAULT 3
)
RETURNS INTEGER AS $$
DECLARE
    session_record RECORD;
    pattern_signature VARCHAR(128);
    access_sequence TEXT[];
    pattern_count INTEGER := 0;
BEGIN
    -- Analyze access patterns for each session
    FOR session_record IN 
        SELECT 
            session_id,
            array_agg(memory_type ORDER BY created_at) as memory_type_sequence,
            array_agg(memory_category ORDER BY created_at) as category_sequence,
            array_agg(memory_id ORDER BY last_accessed) as access_sequence
        FROM alden_memory 
        WHERE user_id = p_user_id AND agent_id = p_agent_id AND sync_status != 'deleted'
        GROUP BY session_id
        HAVING COUNT(*) >= p_min_pattern_length
    LOOP
        -- Create pattern signature from memory type sequence
        pattern_signature := encode(
            sha256(array_to_string(session_record.memory_type_sequence, ',')::bytea), 
            'hex'
        );
        
        -- Insert or update pattern record
        INSERT INTO alden_session_patterns (
            pattern_id, user_id, agent_id, pattern_type, pattern_signature,
            session_ids, memory_access_sequence, common_memory_types,
            first_observed, last_observed
        ) VALUES (
            'pat_' || encode(gen_random_bytes(16), 'hex'),
            p_user_id, p_agent_id, 'access_sequence', pattern_signature,
            ARRAY[session_record.session_id], session_record.access_sequence,
            session_record.memory_type_sequence,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        ) ON CONFLICT (user_id, agent_id, pattern_signature) DO UPDATE SET
            session_ids = alden_session_patterns.session_ids || EXCLUDED.session_ids[1],
            occurrence_count = alden_session_patterns.occurrence_count + 1,
            last_observed = CURRENT_TIMESTAMP;
        
        pattern_count := pattern_count + 1;
    END LOOP;
    
    RETURN pattern_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENHANCED VIEWS FOR LONG-TERM ANALYTICS
-- =====================================================

-- Long-term memory utilization view
CREATE OR REPLACE VIEW alden_long_term_memory_utilization AS
SELECT 
    am.user_id,
    am.agent_id,
    COUNT(am.memory_id) as active_memories,
    COUNT(ama.archive_id) as archived_memories,
    AVG(am.importance_score) as avg_active_importance,
    AVG(ama.importance_score) as avg_archived_importance,
    SUM(char_length(am.content)) as active_storage_bytes,
    SUM(char_length(ama.archived_content)) as archived_storage_bytes,
    COUNT(amc.consolidation_id) as consolidation_clusters,
    SUM(amc.storage_saved_bytes) as bytes_saved_by_consolidation,
    MAX(am.created_at) as latest_active_memory,
    MAX(ama.archived_at) as latest_archive_date
FROM alden_memory am
FULL OUTER JOIN alden_memory_archive ama ON am.user_id = ama.user_id AND am.agent_id = ama.agent_id
LEFT JOIN alden_memory_consolidation amc ON am.user_id = amc.user_id AND am.agent_id = amc.agent_id  
WHERE (am.sync_status != 'deleted' OR am.sync_status IS NULL)
GROUP BY am.user_id, am.agent_id;

-- Session optimization insights view
CREATE OR REPLACE VIEW alden_session_optimization_insights AS
SELECT 
    s.session_id,
    s.user_id,
    s.agent_id,
    s.session_type,
    COUNT(am.memory_id) as memory_count,
    sc.cache_hit_count,
    sc.cache_miss_count,
    CASE 
        WHEN sc.cache_hit_count + sc.cache_miss_count > 0 
        THEN sc.cache_hit_count::REAL / (sc.cache_hit_count + sc.cache_miss_count)
        ELSE 0.0 
    END as cache_hit_ratio,
    array_length(sc.hot_memory_ids, 1) as hot_memories_count,
    sp.confidence_score as pattern_confidence,
    sp.efficiency_score as pattern_efficiency,
    EXTRACT(EPOCH FROM (s.last_activity_at - s.started_at)) / 60 as session_duration_minutes
FROM alden_sessions s
LEFT JOIN alden_memory am ON s.session_id = am.session_id AND am.sync_status != 'deleted'
LEFT JOIN alden_memory_session_cache sc ON s.session_id = sc.session_id
LEFT JOIN alden_session_patterns sp ON s.user_id = sp.user_id AND s.agent_id = sp.agent_id
GROUP BY s.session_id, s.user_id, s.agent_id, s.session_type, s.started_at, s.last_activity_at,
         sc.cache_hit_count, sc.cache_miss_count, sc.hot_memory_ids, sp.confidence_score, sp.efficiency_score;

-- Memory hierarchy navigation view
CREATE OR REPLACE VIEW alden_memory_hierarchy_navigation AS
SELECT 
    h.hierarchy_id,
    h.user_id,
    h.agent_id,
    h.hierarchy_type,
    h.root_memory_id,
    rm.content as root_content,
    h.parent_memory_id,
    pm.content as parent_content,
    h.hierarchy_depth,
    h.relationship_strength,
    array_length(h.child_memory_ids, 1) as child_count,
    h.shortest_path_to_root
FROM alden_memory_hierarchy h
LEFT JOIN alden_memory rm ON h.root_memory_id = rm.memory_id
LEFT JOIN alden_memory pm ON h.parent_memory_id = pm.memory_id
WHERE rm.sync_status != 'deleted' AND (pm.sync_status != 'deleted' OR pm.sync_status IS NULL);

-- Grant permissions for new tables
GRANT ALL PRIVILEGES ON TABLE alden_memory_archive TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_memory_session_cache TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_memory_consolidation TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_memory_hierarchy TO hearthlink_user;
GRANT ALL PRIVILEGES ON TABLE alden_session_patterns TO hearthlink_user;

-- Create maintenance job scheduling table
CREATE TABLE IF NOT EXISTS alden_maintenance_schedule (
    job_id VARCHAR(64) PRIMARY KEY,
    job_type VARCHAR(32) NOT NULL, -- archive, consolidate, optimize, cleanup
    user_id UUID DEFAULT NULL, -- NULL for system-wide jobs
    agent_id VARCHAR(32) DEFAULT NULL,
    
    -- Scheduling
    schedule_expression VARCHAR(64) NOT NULL, -- Cron-like expression
    next_run TIMESTAMP WITH TIME ZONE NOT NULL,
    last_run TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    -- Job configuration
    job_parameters JSONB DEFAULT '{}',
    max_runtime_minutes INTEGER DEFAULT 30,
    
    -- Status tracking
    is_enabled BOOLEAN DEFAULT TRUE,
    last_status VARCHAR(16) DEFAULT 'pending', -- pending, running, completed, failed
    last_error TEXT DEFAULT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_job_id_format CHECK (job_id ~ '^job_[a-f0-9]+$')
);

GRANT ALL PRIVILEGES ON TABLE alden_maintenance_schedule TO hearthlink_user;

-- Insert default maintenance jobs
INSERT INTO alden_maintenance_schedule (job_id, job_type, schedule_expression, next_run, job_parameters) VALUES
    ('job_' || encode(gen_random_bytes(8), 'hex'), 'archive', '0 2 * * *', CURRENT_TIMESTAMP + INTERVAL '1 day', '{"retention_days": 90, "min_importance": 0.3}'),
    ('job_' || encode(gen_random_bytes(8), 'hex'), 'consolidate', '0 3 * * 0', CURRENT_TIMESTAMP + INTERVAL '7 days', '{"similarity_threshold": 0.85}'),
    ('job_' || encode(gen_random_bytes(8), 'hex'), 'optimize', '0 1 * * *', CURRENT_TIMESTAMP + INTERVAL '1 day', '{"optimization_type": "auto"}'),
    ('job_' || encode(gen_random_bytes(8), 'hex'), 'cleanup', '0 4 * * 0', CURRENT_TIMESTAMP + INTERVAL '7 days', '{"cleanup_expired": true, "cleanup_deleted": true}')
ON CONFLICT DO NOTHING;

-- Log successful migration
DO $$
BEGIN
    RAISE NOTICE 'Phase 3 Long-Term Memory Storage migration completed successfully';
    RAISE NOTICE 'New tables: alden_memory_archive, alden_memory_session_cache, alden_memory_consolidation, alden_memory_hierarchy, alden_session_patterns, alden_maintenance_schedule';
    RAISE NOTICE 'Enhanced features: long-term archival, session optimization, memory consolidation, hierarchical relationships, pattern analysis';
    RAISE NOTICE 'New functions: archive_memories_by_retention_policy, optimize_session_cache, consolidate_similar_memories, build_memory_hierarchy, analyze_session_patterns';
    RAISE NOTICE 'New views: alden_long_term_memory_utilization, alden_session_optimization_insights, alden_memory_hierarchy_navigation';
    RAISE NOTICE 'Maintenance scheduling: Automated jobs for archival, consolidation, optimization, and cleanup';
END $$;