#!/usr/bin/env python3
"""
PGVector Database Client for Hearthlink Semantic Memory
Provides connection and operations for PostgreSQL with PGVector extension
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

try:
    import asyncpg
    import numpy as np
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install asyncpg numpy")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class SemanticMemorySlice:
    """Enhanced memory slice with vector embedding support"""
    slice_id: str
    persona_id: str
    user_id: str
    content: str
    memory_type: str
    keywords: List[str]
    embedding: Optional[List[float]]
    relevance_score: float
    created_at: str
    last_accessed: str
    retrieval_count: int
    metadata: Dict[str, Any]

@dataclass
class SemanticSearchResult:
    """Result from semantic similarity search"""
    memories: List[SemanticMemorySlice]
    similarity_scores: List[float]
    total_results: int
    query_time_ms: int
    search_type: str  # 'semantic', 'hybrid', 'keyword'

@dataclass
class ReasoningChain:
    """Enhanced reasoning chain for CAG functionality"""
    chain_id: str
    persona_id: str
    user_id: str
    initial_query: str
    reasoning_steps: List[Dict[str, Any]]
    final_conclusion: str
    confidence_score: float
    supporting_memories: List[str]
    created_at: str

class PGVectorClient:
    """PostgreSQL + PGVector client for semantic memory operations"""
    
    def __init__(self, connection_string: str = None, logger: logging.Logger = None):
        """
        Initialize PGVector client
        
        Args:
            connection_string: PostgreSQL connection string
            logger: Optional logger instance
        """
        self.connection_string = connection_string or self._get_connection_string()
        self.logger = logger or logging.getLogger(__name__)
        self.pool: Optional[asyncpg.Pool] = None
        
    def _get_connection_string(self) -> str:
        """Build connection string from environment variables"""
        # Try environment variables first
        if os.getenv('PGVECTOR_URL'):
            return os.getenv('PGVECTOR_URL')
        
        # Build from individual components
        host = os.getenv('PGVECTOR_HOST', 'localhost')
        port = os.getenv('PGVECTOR_PORT', '5432')
        database = os.getenv('PGVECTOR_DATABASE', 'hearthlink_vectors')
        user = os.getenv('PGVECTOR_USER', 'hearthlink_user')
        password = os.getenv('PGVECTOR_PASSWORD', 'hearthlink_secure_pass_2025')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def connect(self) -> bool:
        """Establish connection pool to PGVector database"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'search_path': 'semantic_memory,public'
                }
            )
            
            # Test connection and verify PGVector extension
            async with self.pool.acquire() as conn:
                # Check if vector extension is available
                result = await conn.fetchrow(
                    "SELECT * FROM pg_extension WHERE extname = 'vector'"
                )
                if not result:
                    raise Exception("PGVector extension not found in database")
                
                # Verify our schema exists
                schema_exists = await conn.fetchrow(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'semantic_memory'"
                )
                if not schema_exists:
                    raise Exception("semantic_memory schema not found")
                
                # Test our main table
                table_exists = await conn.fetchrow(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'semantic_memory' AND table_name = 'memory_slices'"
                )
                if not table_exists:
                    raise Exception("memory_slices table not found in semantic_memory schema")
            
            self.logger.info("Successfully connected to PGVector database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to PGVector database: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.logger.info("Disconnected from PGVector database")
    
    async def store_memory_slice(self, memory_slice: SemanticMemorySlice) -> bool:
        """
        Store a memory slice with vector embedding
        
        Args:
            memory_slice: Memory slice to store
            
        Returns:
            bool: Success status
        """
        if not self.pool:
            raise Exception("Database not connected")
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO memory_slices (
                        slice_id, persona_id, user_id, content, memory_type,
                        keywords, embedding, relevance_score, created_at,
                        last_accessed, retrieval_count, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (slice_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        keywords = EXCLUDED.keywords,
                        embedding = EXCLUDED.embedding,
                        relevance_score = EXCLUDED.relevance_score,
                        last_accessed = EXCLUDED.last_accessed,
                        metadata = EXCLUDED.metadata
                    """,
                    memory_slice.slice_id,
                    memory_slice.persona_id,
                    uuid.UUID(memory_slice.user_id) if isinstance(memory_slice.user_id, str) else memory_slice.user_id,
                    memory_slice.content,
                    memory_slice.memory_type,
                    memory_slice.keywords,
                    memory_slice.embedding,
                    memory_slice.relevance_score,
                    datetime.fromisoformat(memory_slice.created_at.replace('Z', '+00:00')),
                    datetime.fromisoformat(memory_slice.last_accessed.replace('Z', '+00:00')),
                    memory_slice.retrieval_count,
                    json.dumps(memory_slice.metadata)
                )
            
            self.logger.info(f"Stored memory slice: {memory_slice.slice_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store memory slice {memory_slice.slice_id}: {e}")
            return False
    
    async def semantic_search(
        self,
        query_embedding: List[float],
        persona_id: str,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> SemanticSearchResult:
        """
        Perform semantic similarity search using vector embeddings
        
        Args:
            query_embedding: Query vector embedding
            persona_id: Persona identifier
            user_id: User identifier
            memory_types: Optional memory type filter
            limit: Maximum results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            SemanticSearchResult: Search results with similarities
        """
        if not self.pool:
            raise Exception("Database not connected")
        
        start_time = datetime.now()
        
        try:
            async with self.pool.acquire() as conn:
                # Call the semantic_search function
                rows = await conn.fetch(
                    """
                    SELECT * FROM semantic_search(
                        $1::vector(384), $2, $3::uuid, $4, $5, $6
                    )
                    """,
                    query_embedding,
                    persona_id,
                    uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                    memory_types,
                    limit,
                    min_similarity
                )
                
                # Process results
                memories = []
                similarity_scores = []
                
                for row in rows:
                    memory = SemanticMemorySlice(
                        slice_id=row['slice_id'],
                        persona_id=persona_id,
                        user_id=str(user_id),
                        content=row['content'],
                        memory_type=row['memory_type'],
                        keywords=row['keywords'] or [],
                        embedding=None,  # Don't return embedding in search results
                        relevance_score=row['relevance_score'],
                        created_at=row['created_at'].isoformat(),
                        last_accessed=row['last_accessed'].isoformat(),
                        retrieval_count=row['retrieval_count'],
                        metadata=row['metadata'] or {}
                    )
                    memories.append(memory)
                    similarity_scores.append(float(row['similarity_score']))
                
                # Update retrieval statistics
                if memories:
                    slice_ids = [m.slice_id for m in memories]
                    await conn.execute(
                        "SELECT update_retrieval_stats($1)",
                        slice_ids
                    )
                
                query_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                result = SemanticSearchResult(
                    memories=memories,
                    similarity_scores=similarity_scores,
                    total_results=len(memories),
                    query_time_ms=query_time,
                    search_type='semantic'
                )
                
                self.logger.info(
                    f"Semantic search completed: {len(memories)} results in {query_time}ms"
                )
                
                return result
                
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return SemanticSearchResult(
                memories=[],
                similarity_scores=[],
                total_results=0,
                query_time_ms=0,
                search_type='semantic'
            )
    
    async def hybrid_search(
        self,
        query_text: str,
        query_embedding: List[float],
        query_keywords: List[str],
        persona_id: str,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> SemanticSearchResult:
        """
        Perform hybrid search combining keyword matching and semantic similarity
        
        Args:
            query_text: Original query text
            query_embedding: Query vector embedding
            query_keywords: Extracted query keywords
            persona_id: Persona identifier
            user_id: User identifier
            memory_types: Optional memory type filter
            limit: Maximum results to return
            keyword_weight: Weight for keyword matching
            semantic_weight: Weight for semantic similarity
            
        Returns:
            SemanticSearchResult: Hybrid search results
        """
        if not self.pool:
            raise Exception("Database not connected")
        
        start_time = datetime.now()
        
        try:
            async with self.pool.acquire() as conn:
                # Call the hybrid_search function
                rows = await conn.fetch(
                    """
                    SELECT * FROM hybrid_search(
                        $1, $2::vector(384), $3, $4, $5::uuid, $6, $7, $8, $9
                    )
                    """,
                    query_text,
                    query_embedding,
                    query_keywords,
                    persona_id,
                    uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                    memory_types,
                    limit,
                    keyword_weight,
                    semantic_weight
                )
                
                # Process results
                memories = []
                similarity_scores = []
                
                for row in rows:
                    memory = SemanticMemorySlice(
                        slice_id=row['slice_id'],
                        persona_id=persona_id,
                        user_id=str(user_id),
                        content=row['content'],
                        memory_type=row['memory_type'],
                        keywords=row['keywords'] or [],
                        embedding=None,
                        relevance_score=row['relevance_score'],
                        created_at=row['created_at'].isoformat(),
                        last_accessed=row['last_accessed'].isoformat(),
                        retrieval_count=row['retrieval_count'],
                        metadata=row['metadata'] or {}
                    )
                    memories.append(memory)
                    similarity_scores.append(float(row['combined_score']))
                
                # Update retrieval statistics
                if memories:
                    slice_ids = [m.slice_id for m in memories]
                    await conn.execute(
                        "SELECT update_retrieval_stats($1)",
                        slice_ids
                    )
                
                query_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                result = SemanticSearchResult(
                    memories=memories,
                    similarity_scores=similarity_scores,
                    total_results=len(memories),
                    query_time_ms=query_time,
                    search_type='hybrid'
                )
                
                self.logger.info(
                    f"Hybrid search completed: {len(memories)} results in {query_time}ms"
                )
                
                return result
                
        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}")
            return SemanticSearchResult(
                memories=[],
                similarity_scores=[],
                total_results=0,
                query_time_ms=0,
                search_type='hybrid'
            )
    
    async def store_reasoning_chain(self, reasoning_chain: ReasoningChain) -> bool:
        """
        Store a reasoning chain in the database
        
        Args:
            reasoning_chain: Reasoning chain to store
            
        Returns:
            bool: Success status
        """
        if not self.pool:
            raise Exception("Database not connected")
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO reasoning_chains (
                        chain_id, persona_id, user_id, initial_query,
                        reasoning_steps, final_conclusion, confidence_score,
                        supporting_memories, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (chain_id) DO UPDATE SET
                        reasoning_steps = EXCLUDED.reasoning_steps,
                        final_conclusion = EXCLUDED.final_conclusion,
                        confidence_score = EXCLUDED.confidence_score,
                        supporting_memories = EXCLUDED.supporting_memories
                    """,
                    reasoning_chain.chain_id,
                    reasoning_chain.persona_id,
                    uuid.UUID(reasoning_chain.user_id) if isinstance(reasoning_chain.user_id, str) else reasoning_chain.user_id,
                    reasoning_chain.initial_query,
                    json.dumps(reasoning_chain.reasoning_steps),
                    reasoning_chain.final_conclusion,
                    reasoning_chain.confidence_score,
                    reasoning_chain.supporting_memories,
                    datetime.fromisoformat(reasoning_chain.created_at.replace('Z', '+00:00'))
                )
            
            self.logger.info(f"Stored reasoning chain: {reasoning_chain.chain_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store reasoning chain {reasoning_chain.chain_id}: {e}")
            return False
    
    async def get_memory_statistics(self, persona_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics for a persona
        
        Args:
            persona_id: Persona identifier
            user_id: User identifier
            
        Returns:
            Dict containing memory statistics
        """
        if not self.pool:
            raise Exception("Database not connected")
        
        try:
            async with self.pool.acquire() as conn:
                # Get memory slice statistics
                memory_stats = await conn.fetch(
                    """
                    SELECT * FROM memory_statistics 
                    WHERE persona_id = $1 AND user_id = $2
                    """,
                    persona_id,
                    uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                )
                
                # Get reasoning chain statistics
                chain_stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_chains,
                        AVG(confidence_score) as avg_confidence_score
                    FROM reasoning_chains 
                    WHERE persona_id = $1 AND user_id = $2
                    """,
                    persona_id,
                    uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                )
                
                # Format results
                stats = {
                    "memory_by_type": {},
                    "totals": {
                        "total_slices": 0,
                        "avg_relevance": 0.0,
                        "total_retrievals": 0
                    },
                    "reasoning_chains": {
                        "total_chains": chain_stats['total_chains'] if chain_stats else 0,
                        "avg_confidence": float(chain_stats['avg_confidence_score']) if chain_stats and chain_stats['avg_confidence_score'] else 0.0
                    },
                    "timestamp": datetime.now().isoformat(),
                    "database_type": "pgvector"
                }
                
                # Process memory statistics
                for row in memory_stats:
                    memory_type = row['memory_type']
                    stats["memory_by_type"][memory_type] = {
                        "count": row['slice_count'],
                        "avg_relevance": float(row['avg_relevance_score']),
                        "avg_retrieval_count": float(row['avg_retrieval_count']),
                        "last_accessed": row['last_accessed'].isoformat() if row['last_accessed'] else None,
                        "first_created": row['first_created'].isoformat() if row['first_created'] else None,
                        "last_created": row['last_created'].isoformat() if row['last_created'] else None
                    }
                    
                    # Update totals
                    stats["totals"]["total_slices"] += row['slice_count']
                    stats["totals"]["total_retrievals"] += int(row['avg_retrieval_count'] * row['slice_count'])
                
                # Calculate overall average relevance
                if stats["totals"]["total_slices"] > 0:
                    total_relevance = sum(
                        info["avg_relevance"] * info["count"] 
                        for info in stats["memory_by_type"].values()
                    )
                    stats["totals"]["avg_relevance"] = total_relevance / stats["totals"]["total_slices"]
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the database connection
        
        Returns:
            Dict containing health status
        """
        try:
            if not self.pool:
                return {"status": "disconnected", "error": "No connection pool"}
            
            async with self.pool.acquire() as conn:
                # Test basic query
                result = await conn.fetchrow("SELECT version(), current_timestamp")
                
                # Test vector extension
                vector_result = await conn.fetchrow(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                )
                
                # Test our schema
                table_count = await conn.fetchrow(
                    """
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'semantic_memory'
                    """
                )
                
                return {
                    "status": "healthy",
                    "database_version": result[0],
                    "current_time": result[1].isoformat(),
                    "pgvector_version": vector_result[0] if vector_result else "not_found",
                    "schema_tables": table_count[0],
                    "connection_pool_size": len(self.pool._holders) if hasattr(self.pool, '_holders') else "unknown"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Test functions and CLI interface
async def test_connection():
    """Test PGVector database connection"""
    print("🔧 Testing PGVector Database Connection")
    print("=" * 40)
    
    client = PGVectorClient()
    
    # Test connection
    print("📡 Connecting to database...")
    connected = await client.connect()
    
    if not connected:
        print("❌ Connection failed")
        return False
    
    print("✅ Connected successfully")
    
    # Health check
    print("\n🏥 Performing health check...")
    health = await client.health_check()
    
    if health["status"] == "healthy":
        print("✅ Database is healthy")
        print(f"   Database: {health['database_version']}")
        print(f"   PGVector: {health['pgvector_version']}")
        print(f"   Tables: {health['schema_tables']}")
    else:
        print(f"❌ Database unhealthy: {health.get('error', 'Unknown error')}")
    
    # Cleanup
    await client.disconnect()
    return health["status"] == "healthy"

if __name__ == "__main__":
    import asyncio
    
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env.pgvector"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run connection test
    asyncio.run(test_connection())