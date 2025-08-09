#!/usr/bin/env python3
"""
Database Setup Script for Hearthlink
Sets up PostgreSQL, Neo4j, Redis, and Qdrant for Alden backend
"""

import asyncio
import asyncpg
import neo4j
import redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load database configuration"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'database_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

async def setup_postgresql(config):
    """Set up PostgreSQL database and tables"""
    try:
        pg_config = config.get('postgresql', {})
        
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host=pg_config['host'],
            port=pg_config['port'],
            database=pg_config['database'],
            user=pg_config['user'],
            password=pg_config['password']
        )
        
        # Create schema
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {pg_config['schema']}")
        
        # Create tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alden_memory.conversation_contexts (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                conversation_history JSONB NOT NULL DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alden_memory.memory_slices (
                id VARCHAR(255) PRIMARY KEY,
                content TEXT NOT NULL,
                slice_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                importance REAL NOT NULL,
                context JSONB NOT NULL DEFAULT '{}',
                user_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alden_memory.knowledge_entities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                metadata JSONB NOT NULL DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, entity_type)
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alden_memory.user_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_data JSONB NOT NULL DEFAULT '{}',
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_slices_user_id ON alden_memory.memory_slices(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_slices_timestamp ON alden_memory.memory_slices(timestamp)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_slices_importance ON alden_memory.memory_slices(importance)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conversation_contexts_user_id ON alden_memory.conversation_contexts(user_id)")
        
        await conn.close()
        logger.info("PostgreSQL setup completed successfully")
        
    except Exception as e:
        logger.error(f"PostgreSQL setup failed: {e}")
        raise

async def setup_neo4j(config):
    """Set up Neo4j database and constraints"""
    try:
        neo4j_config = config.get('neo4j', {})
        
        # Connect to Neo4j
        driver = neo4j.AsyncGraphDatabase.driver(
            neo4j_config['uri'],
            auth=(neo4j_config['user'], neo4j_config['password'])
        )
        
        async with driver.session() as session:
            # Create constraints
            await session.run("CREATE CONSTRAINT memory_slice_id IF NOT EXISTS FOR (m:MemorySlice) REQUIRE m.id IS UNIQUE")
            await session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            await session.run("CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE")
            await session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            
            # Create indexes
            await session.run("CREATE INDEX memory_importance IF NOT EXISTS FOR (m:MemorySlice) ON (m.importance)")
            await session.run("CREATE INDEX memory_timestamp IF NOT EXISTS FOR (m:MemorySlice) ON (m.timestamp)")
            await session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)")
            
            # Create initial knowledge structure
            await session.run("""
                MERGE (alden:Agent {name: 'Alden', type: 'AI_Assistant'})
                MERGE (hearthlink:System {name: 'Hearthlink', type: 'AI_Orchestration'})
                MERGE (alden)-[:PART_OF]->(hearthlink)
            """)
            
        await driver.close()
        logger.info("Neo4j setup completed successfully")
        
    except Exception as e:
        logger.error(f"Neo4j setup failed: {e}")
        raise

def setup_redis(config):
    """Set up Redis for caching and sessions"""
    try:
        redis_config = config.get('redis', {})
        
        # Connect to Redis
        r = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            password=redis_config.get('password'),
            db=redis_config['db']
        )
        
        # Test connection
        r.ping()
        
        # Set up basic configuration
        r.set('hearthlink:system:initialized', datetime.now().isoformat())
        r.set('hearthlink:system:version', '1.0.0')
        
        logger.info("Redis setup completed successfully")
        
    except Exception as e:
        logger.error(f"Redis setup failed: {e}")
        raise

def setup_qdrant(config):
    """Set up Qdrant vector database"""
    try:
        vector_config = config.get('vector_database', {})
        
        # Connect to Qdrant
        client = QdrantClient(
            host=vector_config['host'],
            port=vector_config['port'],
            api_key=vector_config.get('api_key')
        )
        
        # Create collection
        collection_name = vector_config['collection_name']
        vector_size = vector_config['vector_size']
        
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Qdrant collection {collection_name} already exists")
            else:
                raise
        
        # Create index for better performance
        client.create_payload_index(
            collection_name=collection_name,
            field_name="slice_type",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=collection_name,
            field_name="timestamp",
            field_schema="datetime"
        )
        
        logger.info("Qdrant setup completed successfully")
        
    except Exception as e:
        logger.error(f"Qdrant setup failed: {e}")
        raise

async def main():
    """Main setup function"""
    logger.info("Starting Hearthlink database setup...")
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
    
    try:
        # Setup databases
        await setup_postgresql(config)
        await setup_neo4j(config)
        setup_redis(config)
        setup_qdrant(config)
        
        logger.info("🎉 All databases set up successfully!")
        logger.info("Next steps:")
        logger.info("1. Start the Alden backend: python src/backend/alden_backend.py")
        logger.info("2. Install Ollama and download models: ollama pull llama3.2:latest")
        logger.info("3. Download spaCy model: python -m spacy download en_core_web_sm")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())