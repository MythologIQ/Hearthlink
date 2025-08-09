#!/usr/bin/env python3
"""
Alden Memory Manager - Phase 2 Enhanced Memory System
Manages session-aware memory storage with custom tags and multi-agent support
"""

import os
import sys
import json
import uuid
import asyncio
import asyncpg
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.pgvector_client import PGVectorClient
from embedding.semantic_embedding_service import SemanticMemoryManager

logger = logging.getLogger(__name__)

@dataclass
class AldenMemory:
    """Enhanced memory record with Phase 2 features"""
    memory_id: str
    session_id: str
    user_id: str
    agent_id: str
    content: str
    memory_type: str
    memory_category: str
    keywords: List[str]
    custom_tags: List[str]
    embedding: Optional[List[float]]
    relevance_score: float
    importance_score: float
    confidence_score: float
    created_at: str
    updated_at: str
    last_accessed: str
    expires_at: Optional[str]
    access_count: int
    retrieval_count: int
    modification_count: int
    metadata: Dict[str, Any]
    parent_memory_id: Optional[str]
    related_memory_ids: List[str]
    conversation_turn: Optional[int]
    context_window: Optional[str]
    version: int
    sync_status: str
    last_sync_at: str

@dataclass
class AldenSession:
    """Session tracking record"""
    session_id: str
    user_id: str
    agent_id: str
    session_name: Optional[str]
    session_type: str
    session_status: str
    started_at: str
    last_activity_at: str
    ended_at: Optional[str]
    total_turns: int
    total_memories_created: int
    total_tokens_used: int
    context_summary: Optional[str]
    session_settings: Dict[str, Any]
    memory_retention_policy: str
    auto_archive_after_days: int

@dataclass
class MemoryTag:
    """Memory tag definition"""
    tag_id: int
    tag_name: str
    tag_category: str
    tag_color: str
    description: Optional[str]
    created_by: Optional[str]
    created_at: str
    usage_count: int
    is_hierarchical: bool
    parent_tag_id: Optional[int]
    auto_apply_rules: Dict[str, Any]

@dataclass
class SearchResult:
    """Enhanced search result with additional metadata"""
    memory: AldenMemory
    similarity_score: float
    combined_score: Optional[float] = None
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None
    session_boost: Optional[float] = None

class AldenMemoryManager:
    """
    Enhanced Alden Memory Manager with Phase 2 capabilities
    
    Features:
    - Session-aware memory storage and retrieval
    - Custom tagging system with hierarchical support
    - Multi-agent memory isolation
    - Advanced search with hybrid scoring
    - Memory lifecycle management (expiration, archiving)
    - Comprehensive statistics and analytics
    """
    
    def __init__(
        self, 
        database_url: str = None,
        embedding_service: SemanticMemoryManager = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Alden Memory Manager
        
        Args:
            database_url: PostgreSQL connection URL
            embedding_service: Semantic embedding service
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.database_url = database_url or os.getenv(
            'PGVECTOR_URL', 
            'postgresql://hearthlink_user:hearthlink_secure_pass_2025@localhost:5432/hearthlink_vectors'
        )
        
        # Initialize components
        self.pgvector_client = PGVectorClient(self.database_url, logger)
        self.embedding_service = embedding_service
        
        # Cache for frequent operations
        self.tag_cache: Dict[str, MemoryTag] = {}
        self.session_cache: Dict[str, AldenSession] = {}
        
        # Statistics tracking
        self.stats = {
            "total_memories": 0,
            "total_sessions": 0,
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time_ms": 0.0
        }
        
        self.logger.info("Alden Memory Manager initialized", extra={
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "configured",
            "embedding_service": embedding_service is not None
        })
    
    async def initialize(self) -> bool:
        """Initialize database connection and run migrations if needed"""
        try:
            # Initialize PGVector client
            success = await self.pgvector_client.initialize()
            if not success:
                self.logger.error("Failed to initialize PGVector client")
                return False
            
            # Check if Phase 2 schema exists
            schema_exists = await self._check_phase2_schema()
            if not schema_exists:
                self.logger.info("Phase 2 schema not found, running migration...")
                migration_success = await self._run_phase2_migration()
                if not migration_success:
                    self.logger.error("Phase 2 migration failed")
                    return False
            
            # Initialize embedding service if provided
            if self.embedding_service:
                await self.embedding_service.initialize()
            
            # Load initial caches
            await self._load_tag_cache()
            
            self.logger.info("Alden Memory Manager initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Alden Memory Manager: {e}")
            return False
    
    async def _check_phase2_schema(self) -> bool:
        """Check if Phase 2 schema tables exist"""
        try:
            query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'semantic_memory' 
                AND table_name = 'alden_memory'
            );
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                result = await conn.fetchval(query)
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to check Phase 2 schema: {e}")
            return False
    
    async def _run_phase2_migration(self) -> bool:
        """Run Phase 2 database migration"""
        try:
            migration_file = Path(__file__).parent.parent.parent / "sql" / "migrate_alden_memory_phase2.sql"
            
            if not migration_file.exists():
                self.logger.error(f"Migration file not found: {migration_file}")
                return False
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            async with self.pgvector_client.pool.acquire() as conn:
                await conn.execute(migration_sql)
            
            self.logger.info("Phase 2 migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run Phase 2 migration: {e}")
            return False
    
    async def _load_tag_cache(self):
        """Load frequently used tags into cache"""
        try:
            query = """
            SELECT tag_id, tag_name, tag_category, tag_color, description, 
                   created_by, created_at, usage_count, is_hierarchical, 
                   parent_tag_id, auto_apply_rules
            FROM semantic_memory.alden_memory_tags
            ORDER BY usage_count DESC
            LIMIT 100;
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                rows = await conn.fetch(query)
                
                for row in rows:
                    tag = MemoryTag(
                        tag_id=row['tag_id'],
                        tag_name=row['tag_name'],
                        tag_category=row['tag_category'],
                        tag_color=row['tag_color'],
                        description=row['description'],
                        created_by=row['created_by'],
                        created_at=row['created_at'].isoformat(),
                        usage_count=row['usage_count'],
                        is_hierarchical=row['is_hierarchical'],
                        parent_tag_id=row['parent_tag_id'],
                        auto_apply_rules=row['auto_apply_rules'] or {}
                    )
                    self.tag_cache[tag.tag_name] = tag
            
            self.logger.info(f"Loaded {len(self.tag_cache)} tags into cache")
            
        except Exception as e:
            self.logger.error(f"Failed to load tag cache: {e}")
    
    def generate_memory_id(self) -> str:
        """Generate unique memory ID"""
        return f"mem_{uuid.uuid4().hex[:16]}"
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"sess_{uuid.uuid4().hex[:16]}"
    
    async def create_session(
        self,
        user_id: str,
        agent_id: str = "alden",
        session_name: Optional[str] = None,
        session_type: str = "conversation",
        session_settings: Dict[str, Any] = None
    ) -> AldenSession:
        """
        Create a new conversation session
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier (default: alden)
            session_name: Optional session name
            session_type: Type of session (conversation, task, learning)
            session_settings: Optional session configuration
            
        Returns:
            AldenSession: Created session record
        """
        try:
            session_id = self.generate_session_id()
            session_settings = session_settings or {}
            
            query = """
            INSERT INTO semantic_memory.alden_sessions (
                session_id, user_id, agent_id, session_name, session_type, session_settings
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING session_id, user_id, agent_id, session_name, session_type, 
                      session_status, started_at, last_activity_at, ended_at,
                      total_turns, total_memories_created, total_tokens_used,
                      context_summary, session_settings, memory_retention_policy,
                      auto_archive_after_days;
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                row = await conn.fetchrow(
                    query, session_id, user_id, agent_id, session_name, 
                    session_type, json.dumps(session_settings)
                )
                
                session = AldenSession(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    agent_id=row['agent_id'],
                    session_name=row['session_name'],
                    session_type=row['session_type'],
                    session_status=row['session_status'],
                    started_at=row['started_at'].isoformat(),
                    last_activity_at=row['last_activity_at'].isoformat(),
                    ended_at=row['ended_at'].isoformat() if row['ended_at'] else None,
                    total_turns=row['total_turns'],
                    total_memories_created=row['total_memories_created'],
                    total_tokens_used=row['total_tokens_used'],
                    context_summary=row['context_summary'],
                    session_settings=row['session_settings'] or {},
                    memory_retention_policy=row['memory_retention_policy'],
                    auto_archive_after_days=row['auto_archive_after_days']
                )
            
            # Cache the session
            self.session_cache[session_id] = session
            self.stats["total_sessions"] += 1
            
            self.logger.info(f"Created new session: {session_id}", extra={
                "user_id": user_id,
                "agent_id": agent_id,
                "session_type": session_type
            })
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    async def store_memory(
        self,
        session_id: str,
        user_id: str,
        content: str,
        memory_type: str = "episodic",
        memory_category: str = "conversation",
        agent_id: str = "alden",
        keywords: List[str] = None,
        custom_tags: List[str] = None,
        relevance_score: float = 0.8,
        importance_score: float = 0.5,
        confidence_score: float = 0.8,
        expires_after_hours: Optional[int] = None,
        metadata: Dict[str, Any] = None,
        conversation_turn: Optional[int] = None,
        context_window: Optional[str] = None,
        parent_memory_id: Optional[str] = None
    ) -> AldenMemory:
        """
        Store a new memory with enhanced Phase 2 features
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            content: Memory content
            memory_type: Type of memory (episodic, semantic, procedural, working, contextual)
            memory_category: Category (conversation, task, knowledge, preference)
            agent_id: Agent identifier
            keywords: Extracted keywords
            custom_tags: User-defined tags
            relevance_score: Relevance score (0.0-1.0)
            importance_score: Importance score (0.0-1.0)
            confidence_score: Confidence score (0.0-1.0)
            expires_after_hours: Hours until expiration (for working memory)
            metadata: Additional metadata
            conversation_turn: Turn number in conversation
            context_window: Context when memory was created
            parent_memory_id: Parent memory reference
            
        Returns:
            AldenMemory: Stored memory record
        """
        try:
            memory_id = self.generate_memory_id()
            keywords = keywords or []
            custom_tags = custom_tags or []
            metadata = metadata or {}
            
            # Generate embedding if embedding service is available
            embedding = None
            if self.embedding_service:
                embedding_result = await self.embedding_service.generate_embedding(content)
                if embedding_result:
                    embedding = embedding_result.tolist()
            
            # Calculate expiration time for working memory
            expires_at = None
            if memory_type == "working" and expires_after_hours:
                expires_at = datetime.now() + timedelta(hours=expires_after_hours)
            
            query = """
            INSERT INTO semantic_memory.alden_memory (
                memory_id, session_id, user_id, agent_id, content, memory_type, 
                memory_category, keywords, custom_tags, embedding, relevance_score,
                importance_score, confidence_score, expires_at, metadata,
                conversation_turn, context_window, parent_memory_id
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
            )
            RETURNING memory_id, session_id, user_id, agent_id, content, memory_type,
                      memory_category, keywords, custom_tags, relevance_score,
                      importance_score, confidence_score, created_at, updated_at,
                      last_accessed, expires_at, access_count, retrieval_count,
                      modification_count, metadata, parent_memory_id, related_memory_ids,
                      conversation_turn, context_window, version, sync_status, last_sync_at;
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                row = await conn.fetchrow(
                    query, memory_id, session_id, user_id, agent_id, content,
                    memory_type, memory_category, keywords, custom_tags,
                    embedding, relevance_score, importance_score, confidence_score,
                    expires_at, json.dumps(metadata), conversation_turn, 
                    context_window, parent_memory_id
                )
                
                memory = AldenMemory(
                    memory_id=row['memory_id'],
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    agent_id=row['agent_id'],
                    content=row['content'],
                    memory_type=row['memory_type'],
                    memory_category=row['memory_category'],
                    keywords=row['keywords'] or [],
                    custom_tags=row['custom_tags'] or [],
                    embedding=embedding,
                    relevance_score=row['relevance_score'],
                    importance_score=row['importance_score'],
                    confidence_score=row['confidence_score'],
                    created_at=row['created_at'].isoformat(),
                    updated_at=row['updated_at'].isoformat(),
                    last_accessed=row['last_accessed'].isoformat(),
                    expires_at=row['expires_at'].isoformat() if row['expires_at'] else None,
                    access_count=row['access_count'],
                    retrieval_count=row['retrieval_count'],
                    modification_count=row['modification_count'],
                    metadata=row['metadata'] or {},
                    parent_memory_id=row['parent_memory_id'],
                    related_memory_ids=row['related_memory_ids'] or [],
                    conversation_turn=row['conversation_turn'],
                    context_window=row['context_window'],
                    version=row['version'],
                    sync_status=row['sync_status'],
                    last_sync_at=row['last_sync_at'].isoformat()
                )
            
            # Update session activity
            await self._update_session_activity(session_id)
            
            # Apply auto-tags based on content
            await self._apply_auto_tags(memory_id, content, keywords, custom_tags)
            
            self.stats["total_memories"] += 1
            
            self.logger.info(f"Stored memory: {memory_id}", extra={
                "session_id": session_id,
                "memory_type": memory_type,
                "memory_category": memory_category,
                "has_embedding": embedding is not None,
                "custom_tags_count": len(custom_tags)
            })
            
            return memory
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            raise
    
    async def semantic_search(
        self,
        query: str,
        user_id: str,
        agent_id: str = "alden",
        session_id: Optional[str] = None,
        memory_types: List[str] = None,
        memory_categories: List[str] = None,
        custom_tags: List[str] = None,
        limit: int = 10,
        min_similarity: float = 0.3,
        include_expired: bool = False
    ) -> List[SearchResult]:
        """
        Perform semantic search on Alden memories
        
        Args:
            query: Search query
            user_id: User identifier
            agent_id: Agent identifier
            session_id: Optional session filter
            memory_types: Optional memory type filters
            memory_categories: Optional category filters
            custom_tags: Optional tag filters
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            include_expired: Include expired memories
            
        Returns:
            List[SearchResult]: Search results with similarity scores
        """
        try:
            start_time = datetime.now()
            
            # Generate query embedding
            if not self.embedding_service:
                raise ValueError("Embedding service not available for semantic search")
            
            query_embedding = await self.embedding_service.generate_embedding(query)
            if query_embedding is None:
                raise ValueError("Failed to generate query embedding")
            
            query_embedding_list = query_embedding.tolist()
            
            query = """
            SELECT * FROM semantic_memory.alden_semantic_search(
                $1::vector(384), $2::uuid, $3, $4, $5, $6, $7, $8, $9, $10
            );
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                rows = await conn.fetch(
                    query, query_embedding_list, user_id, agent_id, session_id,
                    memory_types, memory_categories, custom_tags, limit,
                    min_similarity, include_expired
                )
                
                results = []
                memory_ids = []
                
                for row in rows:
                    memory = AldenMemory(
                        memory_id=row['memory_id'],
                        session_id=row['session_id'],
                        user_id=user_id,
                        agent_id=agent_id,
                        content=row['content'],
                        memory_type=row['memory_type'],
                        memory_category=row['memory_category'],
                        keywords=row['keywords'] or [],
                        custom_tags=row['custom_tags'] or [],
                        embedding=None,  # Don't return full embedding
                        relevance_score=row['relevance_score'],
                        importance_score=row['importance_score'],
                        confidence_score=row['confidence_score'],
                        created_at=row['created_at'].isoformat(),
                        updated_at=row['created_at'].isoformat(),  # Placeholder
                        last_accessed=row['last_accessed'].isoformat(),
                        expires_at=None,  # Placeholder
                        access_count=0,  # Placeholder
                        retrieval_count=row['retrieval_count'],
                        modification_count=0,  # Placeholder
                        metadata=row['metadata'] or {},
                        parent_memory_id=None,  # Placeholder
                        related_memory_ids=[],  # Placeholder
                        conversation_turn=None,  # Placeholder
                        context_window=None,  # Placeholder
                        version=1,  # Placeholder
                        sync_status="synced",  # Placeholder
                        last_sync_at=row['created_at'].isoformat()  # Placeholder
                    )
                    
                    result = SearchResult(
                        memory=memory,
                        similarity_score=row['similarity_score']
                    )
                    
                    results.append(result)
                    memory_ids.append(row['memory_id'])
                
                # Update access statistics
                if memory_ids:
                    await self._update_memory_access_stats(memory_ids)
            
            # Update search statistics
            search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.stats["total_searches"] += 1
            self.stats["avg_search_time_ms"] = (
                (self.stats["avg_search_time_ms"] * (self.stats["total_searches"] - 1) + search_time_ms) /
                self.stats["total_searches"]
            )
            
            self.logger.info(f"Semantic search completed", extra={
                "query_length": len(query),
                "results_count": len(results),
                "search_time_ms": search_time_ms,
                "user_id": user_id,
                "session_id": session_id
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            raise
    
    async def hybrid_search(
        self,
        query: str,
        user_id: str,
        agent_id: str = "alden",
        session_id: Optional[str] = None,
        memory_types: List[str] = None,
        limit: int = 10,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
        session_boost: float = 0.1
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining keywords and semantic similarity
        
        Args:
            query: Search query
            user_id: User identifier
            agent_id: Agent identifier
            session_id: Optional session filter (gets boost)
            memory_types: Optional memory type filters
            limit: Maximum results
            keyword_weight: Weight for keyword matching (0.0-1.0)
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            session_boost: Boost for same-session memories
            
        Returns:
            List[SearchResult]: Search results with combined scores
        """
        try:
            start_time = datetime.now()
            
            # Generate query embedding and extract keywords
            if not self.embedding_service:
                raise ValueError("Embedding service not available for hybrid search")
            
            query_embedding = await self.embedding_service.generate_embedding(query)
            if query_embedding is None:
                raise ValueError("Failed to generate query embedding")
            
            # Simple keyword extraction (could be enhanced)
            keywords = await self._extract_keywords(query)
            
            query_sql = """
            SELECT * FROM semantic_memory.alden_hybrid_search(
                $1, $2::vector(384), $3, $4::uuid, $5, $6, $7, $8, $9, $10, $11
            );
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                rows = await conn.fetch(
                    query_sql, query, query_embedding.tolist(), keywords, user_id,
                    agent_id, session_id, memory_types, limit, keyword_weight,
                    semantic_weight, session_boost
                )
                
                results = []
                memory_ids = []
                
                for row in rows:
                    memory = AldenMemory(
                        memory_id=row['memory_id'],
                        session_id=row['session_id'],
                        user_id=user_id,
                        agent_id=agent_id,
                        content=row['content'],
                        memory_type=row['memory_type'],
                        memory_category="general",  # Placeholder
                        keywords=[],  # Placeholder
                        custom_tags=[],  # Placeholder
                        embedding=None,
                        relevance_score=row['relevance_score'],
                        importance_score=row['importance_score'],
                        confidence_score=0.8,  # Placeholder
                        created_at=row['created_at'].isoformat(),
                        updated_at=row['created_at'].isoformat(),
                        last_accessed=row['created_at'].isoformat(),
                        expires_at=None,
                        access_count=0,
                        retrieval_count=0,
                        modification_count=0,
                        metadata=row['metadata'] or {},
                        parent_memory_id=None,
                        related_memory_ids=[],
                        conversation_turn=None,
                        context_window=None,
                        version=1,
                        sync_status="synced",
                        last_sync_at=row['created_at'].isoformat()
                    )
                    
                    result = SearchResult(
                        memory=memory,
                        similarity_score=row['semantic_score'],
                        combined_score=row['combined_score'],
                        semantic_score=row['semantic_score'],
                        keyword_score=row['keyword_score'],
                        session_boost=row['session_boost']
                    )
                    
                    results.append(result)
                    memory_ids.append(row['memory_id'])
                
                # Update access statistics
                if memory_ids:
                    await self._update_memory_access_stats(memory_ids)
            
            # Update search statistics
            search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.stats["total_searches"] += 1
            self.stats["avg_search_time_ms"] = (
                (self.stats["avg_search_time_ms"] * (self.stats["total_searches"] - 1) + search_time_ms) /
                self.stats["total_searches"]
            )
            
            self.logger.info(f"Hybrid search completed", extra={
                "query_length": len(query),
                "results_count": len(results),
                "search_time_ms": search_time_ms,
                "keyword_weight": keyword_weight,
                "semantic_weight": semantic_weight
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}")
            raise
    
    async def get_session_memories(
        self,
        session_id: str,
        user_id: str,
        agent_id: str = "alden",
        memory_types: List[str] = None,
        limit: int = 50
    ) -> List[AldenMemory]:
        """
        Get all memories for a specific session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            agent_id: Agent identifier
            memory_types: Optional memory type filters
            limit: Maximum results
            
        Returns:
            List[AldenMemory]: Session memories
        """
        try:
            query = """
            SELECT memory_id, session_id, user_id, agent_id, content, memory_type,
                   memory_category, keywords, custom_tags, relevance_score,
                   importance_score, confidence_score, created_at, updated_at,
                   last_accessed, expires_at, access_count, retrieval_count,
                   modification_count, metadata, parent_memory_id, related_memory_ids,
                   conversation_turn, context_window, version, sync_status, last_sync_at
            FROM semantic_memory.alden_memory
            WHERE session_id = $1 AND user_id = $2 AND agent_id = $3
                  AND sync_status != 'deleted'
                  AND ($4::varchar(32)[] IS NULL OR memory_type = ANY($4))
            ORDER BY created_at ASC
            LIMIT $5;
            """
            
            async with self.pgvector_client.pool.acquire() as conn:
                rows = await conn.fetch(query, session_id, user_id, agent_id, memory_types, limit)
                
                memories = []
                for row in rows:
                    memory = AldenMemory(
                        memory_id=row['memory_id'],
                        session_id=row['session_id'],
                        user_id=row['user_id'],
                        agent_id=row['agent_id'],
                        content=row['content'],
                        memory_type=row['memory_type'],
                        memory_category=row['memory_category'],
                        keywords=row['keywords'] or [],
                        custom_tags=row['custom_tags'] or [],
                        embedding=None,  # Don't return full embedding
                        relevance_score=row['relevance_score'],
                        importance_score=row['importance_score'],
                        confidence_score=row['confidence_score'],
                        created_at=row['created_at'].isoformat(),
                        updated_at=row['updated_at'].isoformat(),
                        last_accessed=row['last_accessed'].isoformat(),
                        expires_at=row['expires_at'].isoformat() if row['expires_at'] else None,
                        access_count=row['access_count'],
                        retrieval_count=row['retrieval_count'],
                        modification_count=row['modification_count'],
                        metadata=row['metadata'] or {},
                        parent_memory_id=row['parent_memory_id'],
                        related_memory_ids=row['related_memory_ids'] or [],
                        conversation_turn=row['conversation_turn'],
                        context_window=row['context_window'],
                        version=row['version'],
                        sync_status=row['sync_status'],
                        last_sync_at=row['last_sync_at'].isoformat()
                    )
                    memories.append(memory)
            
            self.logger.info(f"Retrieved {len(memories)} memories for session {session_id}")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to get session memories: {e}")
            raise
    
    async def cleanup_expired_memories(self) -> int:
        """
        Clean up expired working memories
        
        Returns:
            int: Number of memories cleaned up
        """
        try:
            query = "SELECT semantic_memory.cleanup_expired_memories();"
            
            async with self.pgvector_client.pool.acquire() as conn:
                cleanup_count = await conn.fetchval(query)
            
            self.logger.info(f"Cleaned up {cleanup_count} expired memories")
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            return 0
    
    async def get_memory_statistics(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics
        
        Args:
            user_id: Optional user filter
            agent_id: Optional agent filter
            session_id: Optional session filter
            
        Returns:
            Dict[str, Any]: Comprehensive statistics
        """
        try:
            base_query = """
            SELECT user_id, agent_id, session_id, memory_type, memory_category,
                   memory_count, avg_relevance_score, avg_importance_score,
                   avg_confidence_score, avg_retrieval_count, last_accessed,
                   first_created, last_created, pending_sync_count, conflict_count
            FROM semantic_memory.alden_memory_statistics
            WHERE 1=1
            """
            
            params = []
            param_count = 0
            
            if user_id:
                param_count += 1
                base_query += f" AND user_id = ${param_count}"
                params.append(user_id)
            
            if agent_id:
                param_count += 1
                base_query += f" AND agent_id = ${param_count}"
                params.append(agent_id)
            
            if session_id:
                param_count += 1
                base_query += f" AND session_id = ${param_count}"
                params.append(session_id)
            
            async with self.pgvector_client.pool.acquire() as conn:
                rows = await conn.fetch(base_query, *params)
                
                statistics = {
                    "memory_breakdown": [],
                    "total_memories": 0,
                    "total_sessions": 0,
                    "avg_memories_per_session": 0.0,
                    "memory_types": {},
                    "memory_categories": {},
                    "avg_relevance_score": 0.0,
                    "avg_importance_score": 0.0,
                    "avg_confidence_score": 0.0,
                    "sync_stats": {
                        "pending_sync": 0,
                        "conflicts": 0
                    }
                }
                
                sessions = set()
                total_relevance = 0.0
                total_importance = 0.0
                total_confidence = 0.0
                
                for row in rows:
                    sessions.add(row['session_id'])
                    statistics["total_memories"] += row['memory_count']
                    
                    # Memory type breakdown
                    memory_type = row['memory_type']
                    if memory_type not in statistics["memory_types"]:
                        statistics["memory_types"][memory_type] = 0
                    statistics["memory_types"][memory_type] += row['memory_count']
                    
                    # Memory category breakdown
                    memory_category = row['memory_category']
                    if memory_category not in statistics["memory_categories"]:
                        statistics["memory_categories"][memory_category] = 0
                    statistics["memory_categories"][memory_category] += row['memory_count']
                    
                    # Accumulate scores
                    total_relevance += row['avg_relevance_score'] * row['memory_count']
                    total_importance += row['avg_importance_score'] * row['memory_count']
                    total_confidence += row['avg_confidence_score'] * row['memory_count']
                    
                    # Sync statistics
                    statistics["sync_stats"]["pending_sync"] += row['pending_sync_count']
                    statistics["sync_stats"]["conflicts"] += row['conflict_count']
                    
                    statistics["memory_breakdown"].append({
                        "user_id": row['user_id'],
                        "agent_id": row['agent_id'],
                        "session_id": row['session_id'],
                        "memory_type": row['memory_type'],
                        "memory_category": row['memory_category'],
                        "count": row['memory_count'],
                        "avg_relevance": row['avg_relevance_score'],
                        "avg_importance": row['avg_importance_score'],
                        "avg_confidence": row['avg_confidence_score'],
                        "avg_retrievals": row['avg_retrieval_count'],
                        "last_accessed": row['last_accessed'].isoformat() if row['last_accessed'] else None,
                        "first_created": row['first_created'].isoformat() if row['first_created'] else None,
                        "last_created": row['last_created'].isoformat() if row['last_created'] else None
                    })
                
                statistics["total_sessions"] = len(sessions)
                
                if statistics["total_memories"] > 0:
                    statistics["avg_memories_per_session"] = statistics["total_memories"] / max(1, statistics["total_sessions"])
                    statistics["avg_relevance_score"] = total_relevance / statistics["total_memories"]
                    statistics["avg_importance_score"] = total_importance / statistics["total_memories"]
                    statistics["avg_confidence_score"] = total_confidence / statistics["total_memories"]
                
                # Add system statistics
                statistics["system_stats"] = self.stats.copy()
                statistics["timestamp"] = datetime.now().isoformat()
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _update_session_activity(self, session_id: str):
        """Update session activity timestamp"""
        try:
            query = "SELECT semantic_memory.update_session_activity($1);"
            async with self.pgvector_client.pool.acquire() as conn:
                await conn.execute(query, session_id)
        
        except Exception as e:
            self.logger.warning(f"Failed to update session activity: {e}")
    
    async def _update_memory_access_stats(self, memory_ids: List[str]):
        """Update memory access statistics"""
        try:
            query = "SELECT semantic_memory.update_alden_memory_access_stats($1);"
            async with self.pgvector_client.pool.acquire() as conn:
                await conn.execute(query, memory_ids)
        
        except Exception as e:
            self.logger.warning(f"Failed to update memory access stats: {e}")
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction"""
        import re
        from collections import Counter
        
        # Simple keyword extraction (could be enhanced with NLP)
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with'
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Return top 10 most frequent keywords
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    async def _apply_auto_tags(self, memory_id: str, content: str, keywords: List[str], custom_tags: List[str]):
        """Apply automatic tags based on content analysis"""
        try:
            # Simple auto-tagging logic (could be enhanced with ML)
            auto_tags = []
            
            content_lower = content.lower()
            
            # Task-related detection
            if any(word in content_lower for word in ['task', 'todo', 'complete', 'finish', 'do']):
                auto_tags.append('task')
            
            # Error/Problem detection
            if any(word in content_lower for word in ['error', 'problem', 'issue', 'bug', 'failed']):
                auto_tags.append('error')
            
            # Success detection
            if any(word in content_lower for word in ['completed', 'success', 'finished', 'done', 'accomplished']):
                auto_tags.append('success')
            
            # Important detection
            if any(word in content_lower for word in ['important', 'critical', 'urgent', 'priority']):
                auto_tags.append('important')
            
            # Apply auto tags
            for tag_name in auto_tags:
                if tag_name in self.tag_cache:
                    tag = self.tag_cache[tag_name]
                    try:
                        insert_query = """
                        INSERT INTO semantic_memory.alden_memory_tag_relations (memory_id, tag_id, tagged_by)
                        VALUES ($1, $2, 'auto')
                        ON CONFLICT (memory_id, tag_id) DO NOTHING;
                        """
                        
                        async with self.pgvector_client.pool.acquire() as conn:
                            await conn.execute(insert_query, memory_id, tag.tag_id)
                        
                        # Update tag usage count
                        update_query = """
                        UPDATE semantic_memory.alden_memory_tags 
                        SET usage_count = usage_count + 1 
                        WHERE tag_id = $1;
                        """
                        
                        async with self.pgvector_client.pool.acquire() as conn:
                            await conn.execute(update_query, tag.tag_id)
                    
                    except Exception as tag_error:
                        self.logger.warning(f"Failed to apply auto tag {tag_name}: {tag_error}")
        
        except Exception as e:
            self.logger.warning(f"Failed to apply auto tags: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for the memory system
        
        Returns:
            Dict[str, Any]: Health status and metrics
        """
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            # Check database connection
            try:
                async with self.pgvector_client.pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1;")
                    health_status["components"]["database"] = {
                        "status": "healthy" if result == 1 else "unhealthy",
                        "response_time_ms": 0  # Could add timing
                    }
            except Exception as db_error:
                health_status["components"]["database"] = {
                    "status": "unhealthy",
                    "error": str(db_error)
                }
            
            # Check Phase 2 schema
            try:
                schema_exists = await self._check_phase2_schema()
                health_status["components"]["phase2_schema"] = {
                    "status": "healthy" if schema_exists else "missing",
                    "exists": schema_exists
                }
            except Exception as schema_error:
                health_status["components"]["phase2_schema"] = {
                    "status": "error",
                    "error": str(schema_error)
                }
            
            # Check embedding service
            if self.embedding_service:
                try:
                    # Simple test embedding
                    test_embedding = await self.embedding_service.generate_embedding("test")
                    health_status["components"]["embedding_service"] = {
                        "status": "healthy" if test_embedding is not None else "unhealthy",
                        "embedding_dimension": len(test_embedding) if test_embedding is not None else None
                    }
                except Exception as embed_error:
                    health_status["components"]["embedding_service"] = {
                        "status": "unhealthy",
                        "error": str(embed_error)
                    }
            else:
                health_status["components"]["embedding_service"] = {
                    "status": "not_configured",
                    "message": "Embedding service not initialized"
                }
            
            # Overall health assessment
            component_statuses = [comp["status"] for comp in health_status["components"].values()]
            if "unhealthy" in component_statuses or "error" in component_statuses:
                health_status["status"] = "unhealthy"
            elif "missing" in component_statuses or "not_configured" in component_statuses:
                health_status["status"] = "degraded"
            
            # Add system statistics
            health_status["statistics"] = self.stats.copy()
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.pgvector_client:
                await self.pgvector_client.cleanup()
            
            if self.embedding_service:
                await self.embedding_service.cleanup()
            
            # Clear caches
            self.tag_cache.clear()
            self.session_cache.clear()
            
            self.logger.info("Alden Memory Manager cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Factory function
async def create_alden_memory_manager(
    database_url: str = None,
    embedding_service: SemanticMemoryManager = None,
    logger: Optional[logging.Logger] = None
) -> AldenMemoryManager:
    """
    Factory function to create and initialize Alden Memory Manager
    
    Args:
        database_url: PostgreSQL connection URL
        embedding_service: Semantic embedding service
        logger: Optional logger instance
        
    Returns:
        AldenMemoryManager: Initialized memory manager
    """
    manager = AldenMemoryManager(database_url, embedding_service, logger)
    
    success = await manager.initialize()
    if not success:
        raise RuntimeError("Failed to initialize Alden Memory Manager")
    
    return manager

# Test function
async def test_alden_memory_manager():
    """Test the Alden Memory Manager functionality"""
    print("🧪 Testing Alden Memory Manager - Phase 2")
    print("=" * 50)
    
    try:
        # Create memory manager
        print("📡 Creating memory manager...")
        manager = await create_alden_memory_manager()
        print("   ✅ Memory manager created successfully")
        
        # Health check
        print("\n🏥 Running health check...")
        health = await manager.health_check()
        print(f"   Status: {health['status']}")
        
        for component, status in health['components'].items():
            print(f"   {component}: {status['status']}")
        
        # Create test session
        print("\n📝 Creating test session...")
        test_user_id = str(uuid.uuid4())
        session = await manager.create_session(
            user_id=test_user_id,
            agent_id="alden",
            session_name="Phase 2 Test Session",
            session_type="conversation"
        )
        print(f"   ✅ Session created: {session.session_id}")
        
        # Store test memories
        print("\n💾 Storing test memories...")
        test_memories = [
            "I learned about machine learning algorithms today, especially neural networks and decision trees.",
            "The user prefers dark mode and wants notifications disabled after 9 PM.",
            "We discussed the upcoming project deadline which is next Friday at 5 PM.",
            "The user mentioned they are working on a Python application for data analysis."
        ]
        
        stored_memories = []
        for i, content in enumerate(test_memories):
            memory = await manager.store_memory(
                session_id=session.session_id,
                user_id=test_user_id,
                content=content,
                memory_type="episodic",
                memory_category="conversation",
                custom_tags=["test", f"memory_{i+1}"],
                conversation_turn=i+1,
                importance_score=0.7 + (i * 0.05)
            )
            stored_memories.append(memory)
            print(f"   ✅ Memory {i+1} stored: {memory.memory_id}")
        
        # Test semantic search
        print("\n🔍 Testing semantic search...")
        search_results = await manager.semantic_search(
            query="machine learning and algorithms",
            user_id=test_user_id,
            agent_id="alden",
            limit=3
        )
        
        print(f"   Found {len(search_results)} results:")
        for i, result in enumerate(search_results):
            print(f"   {i+1}. Similarity: {result.similarity_score:.3f}")
            print(f"      Content: {result.memory.content[:80]}...")
        
        # Test hybrid search
        print("\n🔍 Testing hybrid search...")
        hybrid_results = await manager.hybrid_search(
            query="project deadline Python",
            user_id=test_user_id,
            agent_id="alden",
            session_id=session.session_id,
            limit=3
        )
        
        print(f"   Found {len(hybrid_results)} results:")
        for i, result in enumerate(hybrid_results):
            print(f"   {i+1}. Combined Score: {result.combined_score:.3f}")
            print(f"      Semantic: {result.semantic_score:.3f}, Keyword: {result.keyword_score:.3f}")
            print(f"      Content: {result.memory.content[:80]}...")
        
        # Test session memories
        print("\n📋 Testing session memory retrieval...")
        session_memories = await manager.get_session_memories(
            session_id=session.session_id,
            user_id=test_user_id,
            agent_id="alden"
        )
        
        print(f"   Retrieved {len(session_memories)} session memories:")
        for memory in session_memories:
            print(f"   - {memory.memory_type}: {memory.content[:60]}...")
        
        # Get statistics
        print("\n📊 Testing memory statistics...")
        stats = await manager.get_memory_statistics(user_id=test_user_id)
        
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Total sessions: {stats['total_sessions']}")
        print(f"   Memory types: {stats['memory_types']}")
        print(f"   Avg relevance: {stats['avg_relevance_score']:.3f}")
        print(f"   Avg importance: {stats['avg_importance_score']:.3f}")
        
        # Cleanup
        await manager.cleanup()
        
        print("\n✅ Alden Memory Manager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Alden Memory Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_alden_memory_manager())
    sys.exit(0 if success else 1)