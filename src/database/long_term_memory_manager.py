#!/usr/bin/env python3
"""
Long-Term Memory Manager - Phase 3 Integration
Manages long-term memory storage, archival, consolidation, and optimization
"""

import os
import sys
import json
import uuid
import asyncio
import asyncpg
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.alden_memory_manager import AldenMemoryManager, AldenMemory
from database.pgvector_client import PGVectorClient

logger = logging.getLogger(__name__)

class ArchivePriority(Enum):
    """Archive priority levels"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    CRITICAL = "critical"

class PreservationLevel(Enum):
    """Memory preservation levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PERMANENT = "permanent"

class HierarchyType(Enum):
    """Memory hierarchy types"""
    TEMPORAL = "temporal"
    CONCEPTUAL = "conceptual"
    CAUSAL = "causal"
    PROCEDURAL = "procedural"

@dataclass
class ArchivedMemory:
    """Archived memory record"""
    archive_id: str
    original_memory_id: str
    session_id: str
    user_id: str
    agent_id: str
    archived_content: str
    content_hash: str
    memory_type: str
    memory_category: str
    archive_reason: str
    archive_priority: str
    original_created_at: str
    archived_at: str
    preservation_level: str
    retention_years: int
    importance_score: float
    keywords_summary: List[str]
    checksum: str

@dataclass
class SessionCache:
    """Session-specific memory cache"""
    cache_id: str
    session_id: str
    user_id: str
    agent_id: str
    cached_memory_ids: List[str]
    hot_memory_ids: List[str]
    recent_memory_ids: List[str]
    contextual_memory_ids: List[str]
    cache_hit_count: int
    cache_miss_count: int
    last_optimization: str
    expires_at: str

@dataclass
class MemoryConsolidation:
    """Memory consolidation cluster"""
    consolidation_id: str
    user_id: str
    agent_id: str
    cluster_hash: str
    representative_memory_id: str
    consolidated_memory_ids: List[str]
    consolidation_type: str
    similarity_threshold: float
    cluster_size: int
    storage_saved_bytes: int

@dataclass
class MemoryHierarchy:
    """Memory hierarchy relationship"""
    hierarchy_id: str
    user_id: str
    agent_id: str
    root_memory_id: str
    parent_memory_id: Optional[str]
    child_memory_ids: List[str]
    hierarchy_depth: int
    hierarchy_type: str
    relationship_strength: float
    context_summary: Optional[str]

@dataclass
class SessionPattern:
    """Analyzed session pattern"""
    pattern_id: str
    user_id: str
    agent_id: str
    pattern_type: str
    pattern_signature: str
    session_ids: List[str]
    memory_access_sequence: List[str]
    common_memory_types: List[str]
    common_categories: List[str]
    occurrence_count: int
    confidence_score: float
    efficiency_score: float

class LongTermMemoryManager:
    """
    Long-Term Memory Manager
    
    Extends AldenMemoryManager with long-term storage capabilities:
    - Automated memory archival based on retention policies
    - Session-specific memory caching and optimization
    - Memory consolidation and deduplication
    - Hierarchical memory relationships
    - Session pattern analysis and optimization
    - Maintenance job scheduling
    """
    
    def __init__(
        self,
        base_memory_manager: AldenMemoryManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Long-Term Memory Manager
        
        Args:
            base_memory_manager: Base memory manager instance
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.base_manager = base_memory_manager
        self.db_client = base_memory_manager.db_client if hasattr(base_memory_manager, 'db_client') else None
        
        # Configuration
        self.default_retention_days = 90
        self.default_consolidation_threshold = 0.85
        self.cache_expiry_hours = 24
        
        # Statistics tracking
        self.long_term_stats = {
            "memories_archived": 0,
            "consolidations_created": 0,
            "cache_optimizations": 0,
            "hierarchies_built": 0,
            "patterns_analyzed": 0,
            "bytes_saved": 0
        }
        
        self.logger.info("Long-Term Memory Manager initialized", extra={
            "retention_days": self.default_retention_days,
            "consolidation_threshold": self.default_consolidation_threshold
        })
    
    # =====================================================
    # MEMORY ARCHIVAL METHODS
    # =====================================================
    
    async def archive_memories_by_policy(
        self,
        user_id: str = None,
        agent_id: str = "alden",
        retention_days: int = None,
        min_importance_score: float = 0.3,
        preserve_high_importance: bool = True
    ) -> Dict[str, Any]:
        """
        Archive memories based on retention policy
        
        Args:
            user_id: User identifier (None for all users)
            agent_id: Agent identifier
            retention_days: Days to retain memories
            min_importance_score: Minimum importance to preserve
            preserve_high_importance: Keep high importance memories
            
        Returns:
            Dict containing archival statistics
        """
        try:
            retention_days = retention_days or self.default_retention_days
            
            # Call database function for archival
            async with self.db_client.connection_pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT * FROM archive_memories_by_retention_policy($1, $2, $3)",
                    retention_days, min_importance_score, preserve_high_importance
                )
                
                archival_stats = {
                    "archived_count": result["archived_count"],
                    "skipped_count": result["skipped_count"], 
                    "bytes_saved": result["bytes_saved"],
                    "retention_days": retention_days,
                    "min_importance_score": min_importance_score,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Update local statistics
                self.long_term_stats["memories_archived"] += result["archived_count"]
                self.long_term_stats["bytes_saved"] += result["bytes_saved"]
                
                self.logger.info("Memory archival completed", extra=archival_stats)
                return archival_stats
                
        except Exception as e:
            self.logger.error(f"Memory archival failed: {e}")
            return {
                "error": str(e),
                "archived_count": 0,
                "bytes_saved": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_manual_archive(
        self,
        memory_id: str,
        archive_reason: str = "user_request",
        preservation_level: PreservationLevel = PreservationLevel.STANDARD,
        retention_years: int = 5
    ) -> Optional[str]:
        """
        Manually archive a specific memory
        
        Args:
            memory_id: Memory to archive
            archive_reason: Reason for archival
            preservation_level: Level of preservation
            retention_years: Years to retain
            
        Returns:
            Archive ID if successful
        """
        try:
            # Get memory details
            memory = await self.base_manager.get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory not found: {memory_id}")
            
            # Generate archive record
            archive_id = f"arch_{uuid.uuid4().hex[:16]}"
            content_hash = hashlib.sha256(memory.content.encode()).hexdigest()
            checksum = hashlib.sha256(f"{memory_id}{memory.content}".encode()).hexdigest()
            
            async with self.db_client.connection_pool.acquire() as conn:
                # Insert archive record
                await conn.execute("""
                    INSERT INTO alden_memory_archive (
                        archive_id, original_memory_id, session_id, user_id, agent_id,
                        archived_content, content_hash, memory_type, memory_category,
                        original_created_at, archive_reason, archive_priority,
                        preservation_level, retention_years, importance_score,
                        keywords_summary, checksum
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                """, 
                    archive_id, memory_id, memory.session_id, memory.user_id, memory.agent_id,
                    memory.content, content_hash, memory.memory_type, memory.memory_category,
                    memory.created_at, archive_reason, ArchivePriority.NORMAL.value,
                    preservation_level.value, retention_years, memory.importance_score,
                    memory.keywords, checksum
                )
                
                # Mark original memory as archived
                await conn.execute("""
                    UPDATE alden_memory 
                    SET sync_status = 'deleted',
                        metadata = metadata || $2
                    WHERE memory_id = $1
                """, memory_id, json.dumps({"archived": True, "archive_id": archive_id}))
            
            self.long_term_stats["memories_archived"] += 1
            
            self.logger.info(f"Memory manually archived: {memory_id} -> {archive_id}")
            return archive_id
            
        except Exception as e:
            self.logger.error(f"Manual archive failed for {memory_id}: {e}")
            return None
    
    async def retrieve_from_archive(
        self,
        archive_id: str = None,
        original_memory_id: str = None,
        restore: bool = False
    ) -> Optional[ArchivedMemory]:
        """
        Retrieve memory from archive
        
        Args:
            archive_id: Archive identifier
            original_memory_id: Original memory identifier
            restore: Whether to restore to active memory
            
        Returns:
            ArchivedMemory if found
        """
        try:
            if not archive_id and not original_memory_id:
                raise ValueError("Either archive_id or original_memory_id required")
            
            async with self.db_client.connection_pool.acquire() as conn:
                if archive_id:
                    query = "SELECT * FROM alden_memory_archive WHERE archive_id = $1"
                    result = await conn.fetchrow(query, archive_id)
                else:
                    query = "SELECT * FROM alden_memory_archive WHERE original_memory_id = $1"
                    result = await conn.fetchrow(query, original_memory_id)
                
                if not result:
                    return None
                
                # Update access statistics
                await conn.execute("""
                    UPDATE alden_memory_archive 
                    SET last_accessed_from_archive = CURRENT_TIMESTAMP
                    WHERE archive_id = $1
                """, result["archive_id"])
                
                archived_memory = ArchivedMemory(
                    archive_id=result["archive_id"],
                    original_memory_id=result["original_memory_id"],
                    session_id=result["session_id"],
                    user_id=str(result["user_id"]),
                    agent_id=result["agent_id"],
                    archived_content=result["archived_content"],
                    content_hash=result["content_hash"],
                    memory_type=result["memory_type"],
                    memory_category=result["memory_category"],
                    archive_reason=result["archive_reason"],
                    archive_priority=result["archive_priority"],
                    original_created_at=result["original_created_at"].isoformat(),
                    archived_at=result["archived_at"].isoformat(),
                    preservation_level=result["preservation_level"],
                    retention_years=result["retention_years"],
                    importance_score=result["importance_score"],
                    keywords_summary=result["keywords_summary"] or [],
                    checksum=result["checksum"]
                )
                
                # Restore to active memory if requested
                if restore:
                    await self._restore_from_archive(archived_memory)
                
                return archived_memory
                
        except Exception as e:
            self.logger.error(f"Archive retrieval failed: {e}")
            return None
    
    # =====================================================
    # SESSION OPTIMIZATION METHODS
    # =====================================================
    
    async def optimize_session_cache(
        self,
        session_id: str,
        optimization_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Optimize session-specific memory cache
        
        Args:
            session_id: Session identifier
            optimization_type: Type of optimization
            
        Returns:
            Optimization results
        """
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT * FROM optimize_session_cache($1, $2)",
                    session_id, optimization_type
                )
                
                optimization_results = {
                    "cache_id": result["cache_id"],
                    "optimization_applied": result["optimization_applied"],
                    "performance_improvement": result["performance_improvement"],
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.long_term_stats["cache_optimizations"] += 1
                
                self.logger.info(f"Session cache optimized: {session_id}", extra=optimization_results)
                return optimization_results
                
        except Exception as e:
            self.logger.error(f"Session cache optimization failed: {e}")
            return {
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_session_cache(self, session_id: str) -> Optional[SessionCache]:
        """Get session cache information"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM alden_memory_session_cache WHERE session_id = $1
                """, session_id)
                
                if not result:
                    return None
                
                return SessionCache(
                    cache_id=result["cache_id"],
                    session_id=result["session_id"],
                    user_id=str(result["user_id"]),
                    agent_id=result["agent_id"],
                    cached_memory_ids=result["cached_memory_ids"] or [],
                    hot_memory_ids=result["hot_memory_ids"] or [],
                    recent_memory_ids=result["recent_memory_ids"] or [],
                    contextual_memory_ids=result["contextual_memory_ids"] or [],
                    cache_hit_count=result["cache_hit_count"],
                    cache_miss_count=result["cache_miss_count"],
                    last_optimization=result["last_optimization"].isoformat(),
                    expires_at=result["expires_at"].isoformat()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get session cache: {e}")
            return None
    
    # =====================================================
    # MEMORY CONSOLIDATION METHODS
    # =====================================================
    
    async def consolidate_similar_memories(
        self,
        user_id: str,
        agent_id: str = "alden",
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Consolidate similar memories for deduplication
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            similarity_threshold: Similarity threshold for consolidation
            
        Returns:
            List of consolidation results
        """
        try:
            threshold = similarity_threshold or self.default_consolidation_threshold
            
            async with self.db_client.connection_pool.acquire() as conn:
                results = await conn.fetch(
                    "SELECT * FROM consolidate_similar_memories($1, $2, $3)",
                    user_id, agent_id, threshold
                )
                
                consolidation_results = []
                total_bytes_saved = 0
                
                for result in results:
                    consolidation_data = {
                        "consolidation_id": result["consolidation_id"],
                        "cluster_size": result["cluster_size"],
                        "bytes_saved": result["bytes_saved"],
                        "similarity_threshold": threshold,
                        "timestamp": datetime.now().isoformat()
                    }
                    consolidation_results.append(consolidation_data)
                    total_bytes_saved += result["bytes_saved"]
                
                # Update statistics
                self.long_term_stats["consolidations_created"] += len(results)
                self.long_term_stats["bytes_saved"] += total_bytes_saved
                
                self.logger.info(f"Memory consolidation completed for {user_id}", extra={
                    "consolidations": len(results),
                    "bytes_saved": total_bytes_saved,
                    "threshold": threshold
                })
                
                return consolidation_results
                
        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")
            return []
    
    async def get_consolidation_clusters(
        self,
        user_id: str,
        agent_id: str = "alden"
    ) -> List[MemoryConsolidation]:
        """Get all consolidation clusters for a user/agent"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM alden_memory_consolidation 
                    WHERE user_id = $1 AND agent_id = $2
                    ORDER BY created_at DESC
                """, user_id, agent_id)
                
                consolidations = []
                for result in results:
                    consolidations.append(MemoryConsolidation(
                        consolidation_id=result["consolidation_id"],
                        user_id=str(result["user_id"]),
                        agent_id=result["agent_id"],
                        cluster_hash=result["cluster_hash"],
                        representative_memory_id=result["representative_memory_id"],
                        consolidated_memory_ids=result["consolidated_memory_ids"] or [],
                        consolidation_type=result["consolidation_type"],
                        similarity_threshold=result["similarity_threshold"],
                        cluster_size=result["cluster_size"],
                        storage_saved_bytes=result["storage_saved_bytes"]
                    ))
                
                return consolidations
                
        except Exception as e:
            self.logger.error(f"Failed to get consolidation clusters: {e}")
            return []
    
    # =====================================================
    # MEMORY HIERARCHY METHODS
    # =====================================================
    
    async def build_memory_hierarchy(
        self,
        user_id: str,
        agent_id: str = "alden", 
        hierarchy_type: HierarchyType = HierarchyType.TEMPORAL
    ) -> int:
        """
        Build memory hierarchy relationships
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            hierarchy_type: Type of hierarchy to build
            
        Returns:
            Number of hierarchy relationships created
        """
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                count = await conn.fetchval(
                    "SELECT build_memory_hierarchy($1, $2, $3)",
                    user_id, agent_id, hierarchy_type.value
                )
                
                self.long_term_stats["hierarchies_built"] += count
                
                self.logger.info(f"Memory hierarchy built: {hierarchy_type.value}", extra={
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "relationships_created": count
                })
                
                return count
                
        except Exception as e:
            self.logger.error(f"Memory hierarchy building failed: {e}")
            return 0
    
    async def get_memory_hierarchy(
        self,
        user_id: str,
        agent_id: str = "alden",
        root_memory_id: str = None
    ) -> List[MemoryHierarchy]:
        """Get memory hierarchy relationships"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                if root_memory_id:
                    query = """
                        SELECT * FROM alden_memory_hierarchy 
                        WHERE user_id = $1 AND agent_id = $2 AND root_memory_id = $3
                        ORDER BY hierarchy_depth
                    """
                    results = await conn.fetch(query, user_id, agent_id, root_memory_id)
                else:
                    query = """
                        SELECT * FROM alden_memory_hierarchy 
                        WHERE user_id = $1 AND agent_id = $2
                        ORDER BY hierarchy_depth
                    """
                    results = await conn.fetch(query, user_id, agent_id)
                
                hierarchies = []
                for result in results:
                    hierarchies.append(MemoryHierarchy(
                        hierarchy_id=result["hierarchy_id"],
                        user_id=str(result["user_id"]),
                        agent_id=result["agent_id"],
                        root_memory_id=result["root_memory_id"],
                        parent_memory_id=result["parent_memory_id"],
                        child_memory_ids=result["child_memory_ids"] or [],
                        hierarchy_depth=result["hierarchy_depth"],
                        hierarchy_type=result["hierarchy_type"],
                        relationship_strength=result["relationship_strength"],
                        context_summary=result["context_summary"]
                    ))
                
                return hierarchies
                
        except Exception as e:
            self.logger.error(f"Failed to get memory hierarchy: {e}")
            return []
    
    # =====================================================
    # PATTERN ANALYSIS METHODS
    # =====================================================
    
    async def analyze_session_patterns(
        self,
        user_id: str,
        agent_id: str = "alden",
        min_pattern_length: int = 3
    ) -> int:
        """
        Analyze and record session patterns
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            min_pattern_length: Minimum pattern length
            
        Returns:
            Number of patterns analyzed
        """
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                count = await conn.fetchval(
                    "SELECT analyze_session_patterns($1, $2, $3)",
                    user_id, agent_id, min_pattern_length
                )
                
                self.long_term_stats["patterns_analyzed"] += count
                
                self.logger.info(f"Session patterns analyzed: {count}", extra={
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "min_length": min_pattern_length
                })
                
                return count
                
        except Exception as e:
            self.logger.error(f"Session pattern analysis failed: {e}")
            return 0
    
    async def get_session_patterns(
        self,
        user_id: str,
        agent_id: str = "alden"
    ) -> List[SessionPattern]:
        """Get analyzed session patterns"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM alden_session_patterns 
                    WHERE user_id = $1 AND agent_id = $2
                    ORDER BY confidence_score DESC, occurrence_count DESC
                """, user_id, agent_id)
                
                patterns = []
                for result in results:
                    patterns.append(SessionPattern(
                        pattern_id=result["pattern_id"],
                        user_id=str(result["user_id"]),
                        agent_id=result["agent_id"],
                        pattern_type=result["pattern_type"],
                        pattern_signature=result["pattern_signature"],
                        session_ids=result["session_ids"] or [],
                        memory_access_sequence=result["memory_access_sequence"] or [],
                        common_memory_types=result["common_memory_types"] or [],
                        common_categories=result["common_categories"] or [],
                        occurrence_count=result["occurrence_count"],
                        confidence_score=result["confidence_score"],
                        efficiency_score=result["efficiency_score"]
                    ))
                
                return patterns
                
        except Exception as e:
            self.logger.error(f"Failed to get session patterns: {e}")
            return []
    
    # =====================================================
    # ANALYTICS AND REPORTING
    # =====================================================
    
    async def get_long_term_utilization(
        self,
        user_id: str = None,
        agent_id: str = None
    ) -> Dict[str, Any]:
        """Get long-term memory utilization analytics"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                query = "SELECT * FROM alden_long_term_memory_utilization"
                params = []
                
                if user_id and agent_id:
                    query += " WHERE user_id = $1 AND agent_id = $2"
                    params = [user_id, agent_id]
                elif user_id:
                    query += " WHERE user_id = $1"
                    params = [user_id]
                elif agent_id:
                    query += " WHERE agent_id = $1"
                    params = [agent_id]
                
                results = await conn.fetch(query, *params)
                
                utilization_data = []
                for result in results:
                    utilization_data.append({
                        "user_id": str(result["user_id"]) if result["user_id"] else None,
                        "agent_id": result["agent_id"],
                        "active_memories": result["active_memories"],
                        "archived_memories": result["archived_memories"],
                        "avg_active_importance": float(result["avg_active_importance"]) if result["avg_active_importance"] else 0.0,
                        "avg_archived_importance": float(result["avg_archived_importance"]) if result["avg_archived_importance"] else 0.0,
                        "active_storage_bytes": result["active_storage_bytes"] or 0,
                        "archived_storage_bytes": result["archived_storage_bytes"] or 0,
                        "consolidation_clusters": result["consolidation_clusters"] or 0,
                        "bytes_saved_by_consolidation": result["bytes_saved_by_consolidation"] or 0,
                        "latest_active_memory": result["latest_active_memory"].isoformat() if result["latest_active_memory"] else None,
                        "latest_archive_date": result["latest_archive_date"].isoformat() if result["latest_archive_date"] else None
                    })
                
                return {
                    "utilization_data": utilization_data,
                    "summary": {
                        "total_users": len(set(d["user_id"] for d in utilization_data if d["user_id"])),
                        "total_active_memories": sum(d["active_memories"] for d in utilization_data),
                        "total_archived_memories": sum(d["archived_memories"] for d in utilization_data),
                        "total_storage_bytes": sum(d["active_storage_bytes"] + d["archived_storage_bytes"] for d in utilization_data),
                        "total_bytes_saved": sum(d["bytes_saved_by_consolidation"] for d in utilization_data)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get long-term utilization: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def get_optimization_insights(
        self,
        user_id: str = None,
        agent_id: str = None
    ) -> Dict[str, Any]:
        """Get session optimization insights"""
        try:
            async with self.db_client.connection_pool.acquire() as conn:
                query = "SELECT * FROM alden_session_optimization_insights"
                params = []
                
                if user_id and agent_id:
                    query += " WHERE user_id = $1 AND agent_id = $2"
                    params = [user_id, agent_id]
                elif user_id:
                    query += " WHERE user_id = $1"
                    params = [user_id]
                elif agent_id:
                    query += " WHERE agent_id = $1"
                    params = [agent_id]
                
                results = await conn.fetch(query, *params)
                
                insights = []
                for result in results:
                    insights.append({
                        "session_id": result["session_id"],
                        "user_id": str(result["user_id"]),
                        "agent_id": result["agent_id"],
                        "session_type": result["session_type"],
                        "memory_count": result["memory_count"],
                        "cache_hit_ratio": float(result["cache_hit_ratio"]) if result["cache_hit_ratio"] else 0.0,
                        "hot_memories_count": result["hot_memories_count"] or 0,
                        "pattern_confidence": float(result["pattern_confidence"]) if result["pattern_confidence"] else 0.0,
                        "pattern_efficiency": float(result["pattern_efficiency"]) if result["pattern_efficiency"] else 0.0,
                        "session_duration_minutes": float(result["session_duration_minutes"]) if result["session_duration_minutes"] else 0.0
                    })
                
                return {
                    "optimization_insights": insights,
                    "summary": {
                        "total_sessions": len(insights),
                        "avg_cache_hit_ratio": sum(i["cache_hit_ratio"] for i in insights) / len(insights) if insights else 0.0,
                        "avg_pattern_confidence": sum(i["pattern_confidence"] for i in insights) / len(insights) if insights else 0.0,
                        "avg_session_duration": sum(i["session_duration_minutes"] for i in insights) / len(insights) if insights else 0.0
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization insights: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def get_long_term_statistics(self) -> Dict[str, Any]:
        """Get comprehensive long-term memory statistics"""
        return {
            "long_term_stats": self.long_term_stats.copy(),
            "configuration": {
                "default_retention_days": self.default_retention_days,
                "default_consolidation_threshold": self.default_consolidation_threshold,
                "cache_expiry_hours": self.cache_expiry_hours
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # =====================================================
    # PRIVATE HELPER METHODS
    # =====================================================
    
    async def _restore_from_archive(self, archived_memory: ArchivedMemory):
        """Restore an archived memory to active storage"""
        try:
            # Create restored memory
            restored_memory = await self.base_manager.store_memory(
                session_id=archived_memory.session_id,
                user_id=archived_memory.user_id,
                content=archived_memory.archived_content,
                memory_type=archived_memory.memory_type,
                memory_category=archived_memory.memory_category,
                agent_id=archived_memory.agent_id,
                keywords=archived_memory.keywords_summary,
                importance_score=archived_memory.importance_score,
                metadata={"restored_from_archive": archived_memory.archive_id}
            )
            
            self.logger.info(f"Memory restored from archive: {archived_memory.archive_id} -> {restored_memory.memory_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore from archive: {e}")
    
    async def cleanup(self):
        """Cleanup long-term memory manager resources"""
        try:
            self.logger.info("Long-Term Memory Manager cleanup completed", extra={
                "final_stats": self.long_term_stats
            })
        except Exception as e:
            self.logger.error(f"Error during long-term memory cleanup: {e}")

# Factory function
async def create_long_term_memory_manager(
    base_memory_manager: AldenMemoryManager,
    logger: Optional[logging.Logger] = None
) -> LongTermMemoryManager:
    """
    Factory function to create Long-Term Memory Manager
    
    Args:
        base_memory_manager: Base memory manager instance
        logger: Optional logger instance
        
    Returns:
        LongTermMemoryManager: Initialized manager
    """
    return LongTermMemoryManager(
        base_memory_manager=base_memory_manager,
        logger=logger
    )

# Test function
async def test_long_term_memory_manager():
    """Test the Long-Term Memory Manager"""
    print("🧪 Testing Long-Term Memory Manager")
    print("=" * 45)
    
    try:
        from database.alden_memory_manager import create_alden_memory_manager
        
        # Create base memory manager
        print("📡 Creating base memory manager...")
        base_manager = await create_alden_memory_manager()
        print("   ✅ Base manager created")
        
        # Create long-term manager
        print("🏗️  Creating long-term memory manager...")
        lt_manager = await create_long_term_memory_manager(base_manager)
        print("   ✅ Long-term manager created")
        
        # Test memory archival
        print("\n📦 Testing memory archival...")
        test_user_id = str(uuid.uuid4())
        
        archival_results = await lt_manager.archive_memories_by_policy(
            user_id=test_user_id,
            retention_days=30,
            min_importance_score=0.2
        )
        print(f"   ✅ Archival completed: {archival_results['archived_count']} memories")
        
        # Test session optimization
        print("\n⚡ Testing session optimization...")
        test_session_id = f"sess_{uuid.uuid4().hex[:16]}"
        
        optimization_results = await lt_manager.optimize_session_cache(
            session_id=test_session_id,
            optimization_type="auto"
        )
        print(f"   ✅ Optimization completed: {optimization_results['optimization_applied']}")
        
        # Test memory consolidation
        print("\n🔗 Testing memory consolidation...")
        consolidation_results = await lt_manager.consolidate_similar_memories(
            user_id=test_user_id,
            similarity_threshold=0.8
        )
        print(f"   ✅ Consolidation completed: {len(consolidation_results)} clusters")
        
        # Test hierarchy building
        print("\n🌳 Testing memory hierarchy...")
        hierarchy_count = await lt_manager.build_memory_hierarchy(
            user_id=test_user_id,
            hierarchy_type=HierarchyType.TEMPORAL
        )
        print(f"   ✅ Hierarchy built: {hierarchy_count} relationships")
        
        # Test pattern analysis
        print("\n📊 Testing pattern analysis...")
        pattern_count = await lt_manager.analyze_session_patterns(
            user_id=test_user_id,
            min_pattern_length=2
        )
        print(f"   ✅ Patterns analyzed: {pattern_count}")
        
        # Test analytics
        print("\n📈 Testing analytics...")
        utilization = await lt_manager.get_long_term_utilization()
        print(f"   ✅ Utilization data: {len(utilization['utilization_data'])} records")
        
        insights = await lt_manager.get_optimization_insights()
        print(f"   ✅ Optimization insights: {len(insights['optimization_insights'])} sessions")
        
        stats = await lt_manager.get_long_term_statistics()
        print(f"   ✅ Statistics: {stats['long_term_stats']}")
        
        # Cleanup
        await lt_manager.cleanup()
        await base_manager.cleanup()
        
        print("\n✅ Long-Term Memory Manager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Long-Term Memory Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_long_term_memory_manager())
    sys.exit(0 if success else 1)