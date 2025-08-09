-- Hearthlink Database Initialization
-- Creates core tables for Alden, Vault, and memory management

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- User management table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    security_settings JSONB DEFAULT '{}'
);

-- AI Agents/Personas table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    persona_type VARCHAR(50) NOT NULL, -- alden, alice, mimic, sentry, vault, core, synapse
    description TEXT,
    capabilities JSONB DEFAULT '[]',
    config JSONB DEFAULT '{}',
    personality_traits JSONB DEFAULT '{}',
    trust_level DECIMAL(3,2) DEFAULT 0.82,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    api_key_encrypted TEXT, -- Encrypted API key storage
    last_activity TIMESTAMP WITH TIME ZONE
);

-- Memory system - Core memory slices
CREATE TABLE IF NOT EXISTS memory_slices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    slice_type VARCHAR(50) NOT NULL, -- episodic, semantic, procedural, emotional
    content TEXT NOT NULL,
    content_encrypted TEXT, -- Encrypted version of content
    embedding_id UUID, -- Reference to vector embedding in Qdrant
    importance DECIMAL(3,2) DEFAULT 0.5,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    parent_slice_id UUID REFERENCES memory_slices(id),
    version INTEGER DEFAULT 1
);

-- Session management
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    agent_context JSONB DEFAULT '{}',
    conversation_history JSONB DEFAULT '[]',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    metadata JSONB DEFAULT '{}'
);

-- Conversations table for persistent chat history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- user, assistant, system, tool
    content TEXT NOT NULL,
    content_encrypted TEXT,
    role VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    memory_references JSONB DEFAULT '[]', -- References to relevant memory slices
    feedback_score DECIMAL(3,2),
    correction_flag BOOLEAN DEFAULT false
);

-- Agent authentication tokens
CREATE TABLE IF NOT EXISTS agent_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    token_hash TEXT NOT NULL,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'
);

-- Alden-specific personality and learning tables
CREATE TABLE IF NOT EXISTS alden_personality (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    trait_name VARCHAR(100) NOT NULL,
    trait_value DECIMAL(5,2) NOT NULL,
    trait_confidence DECIMAL(3,2) DEFAULT 1.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_reason TEXT,
    validation_score DECIMAL(3,2),
    UNIQUE(agent_id, trait_name)
);

CREATE TABLE IF NOT EXISTS alden_learning_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- correction, feedback, preference_update, habit_tracking
    event_data JSONB NOT NULL,
    user_feedback TEXT,
    confidence_impact DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT false,
    memory_slice_id UUID REFERENCES memory_slices(id)
);

-- Cognitive analytics for Alden's Observatory
CREATE TABLE IF NOT EXISTS cognitive_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(50),
    measurement_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    context JSONB DEFAULT '{}',
    aggregation_period VARCHAR(20) DEFAULT 'instant' -- instant, hourly, daily, weekly
);

-- Knowledge graph relationships (for Neo4j integration preparation)
CREATE TABLE IF NOT EXISTS knowledge_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_memory_id UUID REFERENCES memory_slices(id) ON DELETE CASCADE,
    target_memory_id UUID REFERENCES memory_slices(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    strength DECIMAL(3,2) DEFAULT 0.5,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_memory_slices_agent_id ON memory_slices(agent_id);
CREATE INDEX IF NOT EXISTS idx_memory_slices_type ON memory_slices(slice_type);
CREATE INDEX IF NOT EXISTS idx_memory_slices_importance ON memory_slices(importance);
CREATE INDEX IF NOT EXISTS idx_memory_slices_created_at ON memory_slices(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_agents_persona_type ON agents(persona_type);
CREATE INDEX IF NOT EXISTS idx_cognitive_analytics_agent_timestamp ON cognitive_analytics(agent_id, measurement_timestamp);

-- Create default Alden agent
INSERT INTO users (id, username, email) 
VALUES ('00000000-0000-0000-0000-000000000001', 'default_user', 'user@hearthlink.local')
ON CONFLICT (username) DO NOTHING;

INSERT INTO agents (
    id, 
    user_id, 
    name, 
    persona_type, 
    description, 
    capabilities, 
    config,
    personality_traits
) VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Alden',
    'alden',
    'Primary AI companion focused on productivity, learning, and cognitive scaffolding',
    '["memory_management", "personality_adaptation", "productivity_coaching", "learning_support", "habit_tracking"]',
    '{"version": "1.0.0", "memory_encryption": true, "learning_enabled": true, "voice_enabled": true}',
    '{"openness": 0.75, "conscientiousness": 0.85, "extraversion": 0.65, "agreeableness": 0.80, "neuroticism": 0.25}'
) ON CONFLICT (id) DO NOTHING;

-- Initialize Alden's personality traits
INSERT INTO alden_personality (agent_id, trait_name, trait_value, trait_confidence)
SELECT 
    '00000000-0000-0000-0000-000000000002',
    trait,
    value::DECIMAL,
    1.0
FROM (
    VALUES 
        ('openness', 0.75),
        ('conscientiousness', 0.85),
        ('extraversion', 0.65),
        ('agreeableness', 0.80),
        ('neuroticism', 0.25),
        ('curiosity', 0.90),
        ('patience', 0.85),
        ('empathy', 0.80),
        ('precision', 0.88),
        ('adaptability', 0.75)
) AS traits(trait, value)
ON CONFLICT (agent_id, trait_name) DO NOTHING;

-- Functions for encrypted storage
CREATE OR REPLACE FUNCTION encrypt_content(content TEXT, key_id TEXT DEFAULT 'hearthlink_master_key')
RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        pgp_sym_encrypt(content, key_id),
        'base64'
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_content(encrypted_content TEXT, key_id TEXT DEFAULT 'hearthlink_master_key')
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(
        decode(encrypted_content, 'base64'),
        key_id
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Commit the transaction
COMMIT;