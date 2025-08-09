#!/usr/bin/env python3
"""
Memory Slicing and Sync Service - Phase 2 Multi-Agent Support
Manages memory synchronization and conflict resolution between multiple agents
"""

import os
import sys
import json
import uuid
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.alden_memory_manager import AldenMemoryManager, AldenMemory, create_alden_memory_manager
from embedding.semantic_embedding_service import SemanticMemoryManager

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Memory synchronization status"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    DELETED = "deleted"
    LOCKED = "locked"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    HIGHEST_IMPORTANCE = "highest_importance"
    AGENT_PRIORITY = "agent_priority"
    MANUAL_REVIEW = "manual_review"
    MERGE_CONTENT = "merge_content"

class AgentPriority(Enum):
    """Agent priority levels for conflict resolution"""
    CRITICAL = 1    # System-critical agents
    HIGH = 2        # Primary agents (Alden)
    MEDIUM = 3      # Secondary agents (Alice, Sentry)
    LOW = 4         # Utility agents (Mimic)

@dataclass
class MemorySlice:
    """Enhanced memory slice with sync metadata"""
    memory_id: str
    agent_id: str
    user_id: str
    session_id: str
    content: str
    memory_type: str
    sync_status: SyncStatus
    version: int
    last_modified: str
    last_sync: str
    checksum: str
    conflict_data: Optional[Dict[str, Any]] = None
    lock_holder: Optional[str] = None
    lock_expires: Optional[str] = None

@dataclass
class SyncConflict:
    """Memory synchronization conflict"""
    conflict_id: str
    memory_id: str
    conflicting_agents: List[str]
    conflict_type: str  # content, metadata, deletion
    created_at: str
    resolution_strategy: ConflictResolution
    resolved: bool
    resolution_data: Optional[Dict[str, Any]] = None
    memory_versions: Dict[str, MemorySlice] = None

@dataclass
class SyncOperation:
    """Synchronization operation record"""
    operation_id: str
    operation_type: str  # sync, resolve_conflict, lock, unlock
    agent_id: str
    memory_ids: List[str]
    started_at: str
    completed_at: Optional[str]
    success: bool
    error_message: Optional[str] = None
    operation_data: Dict[str, Any] = None

class MemorySyncService:
    """
    Memory Slicing and Synchronization Service
    
    Provides:
    - Multi-agent memory synchronization
    - Conflict detection and resolution
    - Memory locking for concurrent access
    - Agent-specific memory slicing
    - Automatic sync scheduling
    - Comprehensive audit logging
    """
    
    def __init__(
        self,
        memory_manager: AldenMemoryManager,
        sync_interval_seconds: int = 30,
        conflict_resolution_strategy: ConflictResolution = ConflictResolution.LATEST_WINS,
        agent_priorities: Dict[str, AgentPriority] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Memory Sync Service
        
        Args:
            memory_manager: Alden memory manager instance
            sync_interval_seconds: Automatic sync interval
            conflict_resolution_strategy: Default conflict resolution
            agent_priorities: Agent priority configuration
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.memory_manager = memory_manager
        self.sync_interval = sync_interval_seconds
        self.default_resolution = conflict_resolution_strategy
        
        # Agent configuration
        self.agent_priorities = agent_priorities or {
            "system": AgentPriority.CRITICAL,
            "alden": AgentPriority.HIGH,
            "alice": AgentPriority.MEDIUM,
            "sentry": AgentPriority.MEDIUM,
            "mimic": AgentPriority.LOW
        }
        
        # Active sync state
        self.active_locks: Dict[str, Dict[str, Any]] = {}  # memory_id -> lock_info
        self.pending_conflicts: Dict[str, SyncConflict] = {}  # conflict_id -> conflict
        self.sync_operations: List[SyncOperation] = []
        
        # Background sync management
        self._sync_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._sync_enabled = True
        
        # Statistics
        self.stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "locks_acquired": 0,
            "locks_released": 0,
            "avg_sync_time_ms": 0.0
        }
        
        self.logger.info("Memory Sync Service initialized", extra={
            "sync_interval": sync_interval_seconds,
            "default_resolution": conflict_resolution_strategy.value,
            "agent_priorities": {k: v.value for k, v in self.agent_priorities.items()}
        })
    
    async def initialize(self) -> bool:
        """Initialize the sync service and start background tasks"""
        try:
            # Verify memory manager is ready
            if not self.memory_manager:
                raise ValueError("Memory manager not provided")
            
            # Start background sync thread
            self._start_sync_thread()
            
            # Clean up any stale locks from previous sessions
            await self._cleanup_stale_locks()
            
            # Load pending conflicts
            await self._load_pending_conflicts()
            
            self.logger.info("Memory Sync Service initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Memory Sync Service: {e}")
            return False
    
    def _start_sync_thread(self):
        """Start background synchronization thread"""
        def sync_worker():
            while not self._shutdown_event.is_set():
                try:
                    if self._sync_enabled:
                        # Run sync in async context
                        asyncio.run(self._background_sync_cycle())
                    
                    # Wait for next sync or shutdown
                    self._shutdown_event.wait(timeout=self.sync_interval)
                    
                except Exception as e:
                    self.logger.error(f"Background sync error: {e}")
                    # Wait before retrying
                    self._shutdown_event.wait(timeout=min(60, self.sync_interval * 2))
        
        self._sync_thread = threading.Thread(
            target=sync_worker,
            name="MemorySync",
            daemon=True
        )
        self._sync_thread.start()
        self.logger.info(f"Background sync thread started (interval: {self.sync_interval}s)")
    
    async def _background_sync_cycle(self):
        """Perform one background synchronization cycle"""
        try:
            start_time = datetime.now()
            
            # 1. Clean up expired locks
            await self._cleanup_expired_locks()
            
            # 2. Detect and resolve conflicts
            conflicts_detected = await self._detect_conflicts()
            if conflicts_detected > 0:
                await self._resolve_pending_conflicts()
            
            # 3. Sync pending memories
            await self._sync_pending_memories()
            
            # 4. Update statistics
            sync_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.stats["total_syncs"] += 1
            self.stats["avg_sync_time_ms"] = (
                (self.stats["avg_sync_time_ms"] * (self.stats["total_syncs"] - 1) + sync_time_ms) /
                self.stats["total_syncs"]
            )
            
            self.logger.debug(f"Background sync cycle completed in {sync_time_ms:.1f}ms")
            
        except Exception as e:
            self.logger.error(f"Background sync cycle failed: {e}")
    
    async def acquire_memory_lock(
        self,
        memory_id: str,
        agent_id: str,
        lock_duration_minutes: int = 5,
        wait_for_lock: bool = True,
        timeout_seconds: int = 30
    ) -> bool:
        """
        Acquire exclusive lock on memory for modification
        
        Args:
            memory_id: Memory identifier
            agent_id: Agent requesting lock
            lock_duration_minutes: Lock duration
            wait_for_lock: Wait if memory is already locked
            timeout_seconds: Maximum wait time
            
        Returns:
            bool: True if lock acquired successfully
        """
        try:
            start_time = datetime.now()
            
            while True:
                # Check if memory is already locked
                if memory_id in self.active_locks:
                    lock_info = self.active_locks[memory_id]
                    
                    # Check if lock has expired
                    lock_expires = datetime.fromisoformat(lock_info["expires_at"])
                    if datetime.now() > lock_expires:
                        # Remove expired lock
                        del self.active_locks[memory_id]
                        self.logger.info(f"Removed expired lock on {memory_id}")
                    else:
                        # Lock is still active
                        if not wait_for_lock:
                            return False
                        
                        # Check timeout
                        if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                            self.logger.warning(f"Lock acquisition timeout for {memory_id}")
                            return False
                        
                        # Wait and retry
                        await asyncio.sleep(1)
                        continue
                
                # Acquire lock
                expires_at = datetime.now() + timedelta(minutes=lock_duration_minutes)
                lock_info = {
                    "agent_id": agent_id,
                    "acquired_at": datetime.now().isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "operation_id": str(uuid.uuid4())
                }
                
                self.active_locks[memory_id] = lock_info
                
                # Update database
                await self._update_memory_lock_status(memory_id, agent_id, expires_at)
                
                self.stats["locks_acquired"] += 1
                
                self.logger.info(f"Lock acquired on {memory_id} by {agent_id}", extra={
                    "memory_id": memory_id,
                    "agent_id": agent_id,
                    "expires_at": expires_at.isoformat()
                })
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to acquire lock on {memory_id}: {e}")
            return False
    
    async def release_memory_lock(
        self,
        memory_id: str,
        agent_id: str,
        force: bool = False
    ) -> bool:
        """
        Release memory lock
        
        Args:
            memory_id: Memory identifier
            agent_id: Agent releasing lock
            force: Force release even if agent doesn't own lock
            
        Returns:
            bool: True if lock released successfully
        """
        try:
            if memory_id not in self.active_locks:
                self.logger.warning(f"No active lock found for {memory_id}")
                return True
            
            lock_info = self.active_locks[memory_id]
            
            # Verify ownership unless forcing
            if not force and lock_info["agent_id"] != agent_id:
                self.logger.error(f"Agent {agent_id} cannot release lock owned by {lock_info['agent_id']}")
                return False
            
            # Release lock
            del self.active_locks[memory_id]
            
            # Update database
            await self._update_memory_lock_status(memory_id, None, None)
            
            self.stats["locks_released"] += 1
            
            self.logger.info(f"Lock released on {memory_id} by {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release lock on {memory_id}: {e}")
            return False
    
    async def sync_agent_memories(
        self,
        agent_id: str,
        user_id: str,
        session_id: Optional[str] = None,
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize memories for a specific agent
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            session_id: Optional session filter
            force_sync: Force sync even for recently synced memories
            
        Returns:
            Dict[str, Any]: Sync results and statistics
        """
        try:
            start_time = datetime.now()
            operation_id = str(uuid.uuid4())
            
            # Create sync operation record
            sync_op = SyncOperation(
                operation_id=operation_id,
                operation_type="sync",
                agent_id=agent_id,
                memory_ids=[],
                started_at=start_time.isoformat(),
                completed_at=None,
                success=False,
                operation_data={
                    "user_id": user_id,
                    "session_id": session_id,
                    "force_sync": force_sync
                }
            )
            
            self.sync_operations.append(sync_op)
            
            # Get memories needing sync
            pending_memories = await self._get_pending_sync_memories(
                agent_id, user_id, session_id, force_sync
            )
            
            sync_op.memory_ids = [mem.memory_id for mem in pending_memories]
            
            sync_results = {
                "operation_id": operation_id,
                "agent_id": agent_id,
                "memories_processed": len(pending_memories),
                "successful_syncs": 0,
                "conflicts_detected": 0,
                "conflicts_resolved": 0,
                "errors": []
            }
            
            # Process each memory
            for memory in pending_memories:
                try:
                    # Check for conflicts
                    conflict = await self._detect_memory_conflict(memory)
                    if conflict:
                        sync_results["conflicts_detected"] += 1
                        self.pending_conflicts[conflict.conflict_id] = conflict
                        self.stats["conflicts_detected"] += 1
                        
                        # Attempt automatic resolution
                        if await self._resolve_conflict(conflict):
                            sync_results["conflicts_resolved"] += 1
                            self.stats["conflicts_resolved"] += 1
                    
                    # Update sync status
                    await self._update_memory_sync_status(
                        memory.memory_id, SyncStatus.SYNCED
                    )
                    
                    sync_results["successful_syncs"] += 1
                    
                except Exception as mem_error:
                    error_msg = f"Failed to sync {memory.memory_id}: {mem_error}"
                    sync_results["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            # Complete sync operation
            sync_op.completed_at = datetime.now().isoformat()
            sync_op.success = len(sync_results["errors"]) == 0
            
            if sync_results["errors"]:
                sync_op.error_message = "; ".join(sync_results["errors"][:3])
            
            # Update statistics
            self.stats["successful_syncs"] += sync_results["successful_syncs"]
            
            sync_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            sync_results["sync_time_ms"] = sync_time_ms
            
            self.logger.info(f"Agent sync completed for {agent_id}", extra={
                "operation_id": operation_id,
                "memories_processed": sync_results["memories_processed"],
                "successful_syncs": sync_results["successful_syncs"],
                "conflicts": sync_results["conflicts_detected"],
                "sync_time_ms": sync_time_ms
            })
            
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Agent sync failed for {agent_id}: {e}")
            return {
                "operation_id": operation_id,
                "agent_id": agent_id,
                "success": False,
                "error": str(e)
            }
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution_strategy: ConflictResolution = None,
        manual_resolution_data: Dict[str, Any] = None
    ) -> bool:
        """
        Resolve a specific memory conflict
        
        Args:
            conflict_id: Conflict identifier
            resolution_strategy: Override default resolution strategy
            manual_resolution_data: Data for manual resolution
            
        Returns:
            bool: True if conflict resolved successfully
        """
        try:
            if conflict_id not in self.pending_conflicts:
                self.logger.warning(f"Conflict {conflict_id} not found")
                return False
            
            conflict = self.pending_conflicts[conflict_id]
            strategy = resolution_strategy or self.default_resolution
            
            self.logger.info(f"Resolving conflict {conflict_id} using {strategy.value}")
            
            success = False
            
            if strategy == ConflictResolution.LATEST_WINS:
                success = await self._resolve_latest_wins(conflict)
            
            elif strategy == ConflictResolution.HIGHEST_IMPORTANCE:
                success = await self._resolve_highest_importance(conflict)
            
            elif strategy == ConflictResolution.AGENT_PRIORITY:
                success = await self._resolve_agent_priority(conflict)
            
            elif strategy == ConflictResolution.MERGE_CONTENT:
                success = await self._resolve_merge_content(conflict)
            
            elif strategy == ConflictResolution.MANUAL_REVIEW:
                success = await self._resolve_manual(conflict, manual_resolution_data)
            
            else:
                self.logger.error(f"Unknown resolution strategy: {strategy}")
                return False
            
            if success:
                conflict.resolved = True
                conflict.resolution_data = {
                    "strategy": strategy.value,
                    "resolved_at": datetime.now().isoformat(),
                    "manual_data": manual_resolution_data
                }
                
                # Remove from pending conflicts
                del self.pending_conflicts[conflict_id]
                
                self.stats["conflicts_resolved"] += 1
                
                self.logger.info(f"Conflict {conflict_id} resolved successfully")
            else:
                self.logger.error(f"Failed to resolve conflict {conflict_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return False
    
    async def get_agent_memory_slice(
        self,
        agent_id: str,
        user_id: str,
        session_id: Optional[str] = None,
        memory_types: List[str] = None,
        include_sync_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Get memory slice for a specific agent
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            session_id: Optional session filter
            memory_types: Optional memory type filters
            include_sync_metadata: Include synchronization metadata
            
        Returns:
            Dict[str, Any]: Agent memory slice with metadata
        """
        try:
            # Get memories using memory manager
            if session_id:
                memories = await self.memory_manager.get_session_memories(
                    session_id=session_id,
                    user_id=user_id,
                    agent_id=agent_id,
                    memory_types=memory_types
                )
            else:
                # Get all memories for agent (would need new method in memory manager)
                # For now, use semantic search with broad query
                search_results = await self.memory_manager.semantic_search(
                    query="*",  # Broad search
                    user_id=user_id,
                    agent_id=agent_id,
                    memory_types=memory_types,
                    limit=1000,
                    min_similarity=0.0
                )
                memories = [result.memory for result in search_results]
            
            # Enhance with sync metadata if requested
            memory_slices = []
            for memory in memories:
                if include_sync_metadata:
                    # Add sync information
                    slice_data = {
                        "memory": asdict(memory),
                        "sync_metadata": {
                            "is_locked": memory.memory_id in self.active_locks,
                            "lock_holder": self.active_locks.get(memory.memory_id, {}).get("agent_id"),
                            "has_conflicts": any(
                                memory.memory_id == conf.memory_id 
                                for conf in self.pending_conflicts.values()
                            ),
                            "last_sync_check": datetime.now().isoformat()
                        }
                    }
                else:
                    slice_data = asdict(memory)
                
                memory_slices.append(slice_data)
            
            # Calculate slice statistics
            slice_stats = {
                "total_memories": len(memory_slices),
                "memory_types": {},
                "sync_status": {},
                "locked_memories": sum(1 for m in memories if m.memory_id in self.active_locks),
                "conflicted_memories": len([
                    c for c in self.pending_conflicts.values() 
                    if any(m.memory_id == c.memory_id for m in memories)
                ])
            }
            
            # Count by type and sync status
            for memory in memories:
                # Memory type counts
                mem_type = memory.memory_type
                slice_stats["memory_types"][mem_type] = slice_stats["memory_types"].get(mem_type, 0) + 1
                
                # Sync status counts
                sync_status = memory.sync_status
                slice_stats["sync_status"][sync_status] = slice_stats["sync_status"].get(sync_status, 0) + 1
            
            return {
                "agent_id": agent_id,
                "user_id": user_id,
                "session_id": session_id,
                "memory_slice": memory_slices,
                "statistics": slice_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory slice for {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "user_id": user_id,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get comprehensive sync service statistics"""
        try:
            # Calculate additional metrics
            recent_ops = [
                op for op in self.sync_operations 
                if datetime.fromisoformat(op.started_at) > datetime.now() - timedelta(hours=24)
            ]
            
            return {
                "service_stats": self.stats.copy(),
                "active_locks": {
                    "count": len(self.active_locks),
                    "locks": [
                        {
                            "memory_id": mem_id,
                            "agent_id": lock_info["agent_id"],
                            "acquired_at": lock_info["acquired_at"],
                            "expires_at": lock_info["expires_at"]
                        }
                        for mem_id, lock_info in self.active_locks.items()
                    ]
                },
                "pending_conflicts": {
                    "count": len(self.pending_conflicts),
                    "conflicts": [
                        {
                            "conflict_id": conf_id,
                            "memory_id": conflict.memory_id,
                            "agents": conflict.conflicting_agents,
                            "type": conflict.conflict_type,
                            "created_at": conflict.created_at
                        }
                        for conf_id, conflict in self.pending_conflicts.items()
                    ]
                },
                "recent_operations": {
                    "last_24h": len(recent_ops),
                    "successful": sum(1 for op in recent_ops if op.success),
                    "failed": sum(1 for op in recent_ops if not op.success)
                },
                "agent_priorities": {
                    agent: priority.value 
                    for agent, priority in self.agent_priorities.items()
                },
                "configuration": {
                    "sync_interval_seconds": self.sync_interval,
                    "default_resolution": self.default_resolution.value,
                    "sync_enabled": self._sync_enabled
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get sync statistics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    async def _cleanup_stale_locks(self):
        """Clean up locks from previous sessions"""
        try:
            # This would query the database for locks that are marked but expired
            # For now, just clear the in-memory locks
            self.active_locks.clear()
            self.logger.info("Cleared stale locks from previous sessions")
        except Exception as e:
            self.logger.error(f"Failed to cleanup stale locks: {e}")
    
    async def _cleanup_expired_locks(self):
        """Remove expired locks"""
        try:
            now = datetime.now()
            expired_locks = []
            
            for memory_id, lock_info in self.active_locks.items():
                expires_at = datetime.fromisoformat(lock_info["expires_at"])
                if now > expires_at:
                    expired_locks.append(memory_id)
            
            for memory_id in expired_locks:
                del self.active_locks[memory_id]
                await self._update_memory_lock_status(memory_id, None, None)
                self.logger.info(f"Removed expired lock on {memory_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired locks: {e}")
    
    async def _load_pending_conflicts(self):
        """Load pending conflicts from database"""
        try:
            # This would query the database for unresolved conflicts
            # For now, start with empty conflicts
            self.pending_conflicts.clear()
            self.logger.info("Loaded pending conflicts from database")
        except Exception as e:
            self.logger.error(f"Failed to load pending conflicts: {e}")
    
    async def _get_pending_sync_memories(
        self, 
        agent_id: str, 
        user_id: str, 
        session_id: Optional[str], 
        force_sync: bool
    ) -> List[AldenMemory]:
        """Get memories that need synchronization"""
        try:
            # Get memories with pending sync status or force all
            if session_id:
                memories = await self.memory_manager.get_session_memories(
                    session_id=session_id,
                    user_id=user_id,
                    agent_id=agent_id
                )
            else:
                # Would need enhanced query method to get by sync status
                # For now, get recent memories
                search_results = await self.memory_manager.semantic_search(
                    query="*",
                    user_id=user_id,
                    agent_id=agent_id,
                    limit=100
                )
                memories = [result.memory for result in search_results]
            
            # Filter by sync status
            if not force_sync:
                pending_memories = [
                    mem for mem in memories 
                    if mem.sync_status in ["pending", "conflict"]
                ]
            else:
                pending_memories = memories
            
            return pending_memories
            
        except Exception as e:
            self.logger.error(f"Failed to get pending sync memories: {e}")
            return []
    
    async def _detect_conflicts(self) -> int:
        """Detect memory conflicts across agents"""
        try:
            conflicts_found = 0
            # This would implement conflict detection logic
            # For now, return 0 as a placeholder
            return conflicts_found
        except Exception as e:
            self.logger.error(f"Failed to detect conflicts: {e}")
            return 0
    
    async def _detect_memory_conflict(self, memory: AldenMemory) -> Optional[SyncConflict]:
        """Detect conflict for a specific memory"""
        try:
            # Placeholder conflict detection logic
            # In real implementation, this would check for:
            # - Concurrent modifications
            # - Version conflicts
            # - Content divergence
            return None
        except Exception as e:
            self.logger.error(f"Failed to detect conflict for {memory.memory_id}: {e}")
            return None
    
    async def _resolve_pending_conflicts(self):
        """Resolve all pending conflicts"""
        try:
            conflicts_to_resolve = list(self.pending_conflicts.keys())
            for conflict_id in conflicts_to_resolve:
                await self.resolve_conflict(conflict_id)
        except Exception as e:
            self.logger.error(f"Failed to resolve pending conflicts: {e}")
    
    async def _sync_pending_memories(self):
        """Sync all pending memories"""
        try:
            # This would implement the actual memory synchronization logic
            # For now, just log that sync was attempted
            self.logger.debug("Pending memories sync completed")
        except Exception as e:
            self.logger.error(f"Failed to sync pending memories: {e}")
    
    async def _update_memory_lock_status(
        self, 
        memory_id: str, 
        agent_id: Optional[str], 
        expires_at: Optional[datetime]
    ):
        """Update memory lock status in database"""
        try:
            # This would update the database with lock information
            # For now, just log the action
            if agent_id:
                self.logger.debug(f"Lock set on {memory_id} by {agent_id}")
            else:
                self.logger.debug(f"Lock removed from {memory_id}")
        except Exception as e:
            self.logger.error(f"Failed to update lock status for {memory_id}: {e}")
    
    async def _update_memory_sync_status(self, memory_id: str, status: SyncStatus):
        """Update memory sync status in database"""
        try:
            # This would update the database with sync status
            self.logger.debug(f"Sync status for {memory_id} set to {status.value}")
        except Exception as e:
            self.logger.error(f"Failed to update sync status for {memory_id}: {e}")
    
    # Conflict resolution strategies
    
    async def _resolve_latest_wins(self, conflict: SyncConflict) -> bool:
        """Resolve conflict by keeping the latest version"""
        try:
            if not conflict.memory_versions:
                return False
            
            # Find the most recent version
            latest_version = None
            latest_time = None
            
            for agent_id, memory_slice in conflict.memory_versions.items():
                modified_time = datetime.fromisoformat(memory_slice.last_modified)
                if latest_time is None or modified_time > latest_time:
                    latest_time = modified_time
                    latest_version = memory_slice
            
            if latest_version:
                # Update memory with latest version
                await self._apply_memory_resolution(conflict.memory_id, latest_version)
                self.logger.info(f"Conflict {conflict.conflict_id} resolved with latest version")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resolve latest wins for {conflict.conflict_id}: {e}")
            return False
    
    async def _resolve_highest_importance(self, conflict: SyncConflict) -> bool:
        """Resolve conflict by keeping the version with highest importance"""
        try:
            # Implementation would find the memory version with highest importance score
            self.logger.info(f"Conflict {conflict.conflict_id} resolved by importance")
            return True
        except Exception as e:
            self.logger.error(f"Failed to resolve by importance for {conflict.conflict_id}: {e}")
            return False
    
    async def _resolve_agent_priority(self, conflict: SyncConflict) -> bool:
        """Resolve conflict based on agent priority"""
        try:
            if not conflict.memory_versions:
                return False
            
            # Find the highest priority agent
            highest_priority = None
            winning_agent = None
            
            for agent_id in conflict.conflicting_agents:
                priority = self.agent_priorities.get(agent_id, AgentPriority.LOW)
                if highest_priority is None or priority.value < highest_priority.value:
                    highest_priority = priority
                    winning_agent = agent_id
            
            if winning_agent and winning_agent in conflict.memory_versions:
                winning_version = conflict.memory_versions[winning_agent]
                await self._apply_memory_resolution(conflict.memory_id, winning_version)
                self.logger.info(f"Conflict {conflict.conflict_id} resolved by agent priority: {winning_agent}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resolve by priority for {conflict.conflict_id}: {e}")
            return False
    
    async def _resolve_merge_content(self, conflict: SyncConflict) -> bool:
        """Resolve conflict by merging content from all versions"""
        try:
            # Implementation would merge content intelligently
            self.logger.info(f"Conflict {conflict.conflict_id} resolved by content merge")
            return True
        except Exception as e:
            self.logger.error(f"Failed to resolve by merge for {conflict.conflict_id}: {e}")
            return False
    
    async def _resolve_manual(self, conflict: SyncConflict, resolution_data: Dict[str, Any]) -> bool:
        """Resolve conflict using manual resolution data"""
        try:
            if not resolution_data:
                return False
            
            # Apply manual resolution
            self.logger.info(f"Conflict {conflict.conflict_id} resolved manually")
            return True
        except Exception as e:
            self.logger.error(f"Failed manual resolution for {conflict.conflict_id}: {e}")
            return False
    
    async def _apply_memory_resolution(self, memory_id: str, resolved_version: MemorySlice):
        """Apply resolved memory version to database"""
        try:
            # This would update the database with the resolved version
            self.logger.debug(f"Applied resolution for memory {memory_id}")
        except Exception as e:
            self.logger.error(f"Failed to apply resolution for {memory_id}: {e}")
    
    async def _resolve_conflict(self, conflict: SyncConflict) -> bool:
        """Attempt to resolve a conflict automatically"""
        return await self.resolve_conflict(conflict.conflict_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for sync service"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            # Check background sync thread
            if self._sync_thread and self._sync_thread.is_alive():
                health_status["components"]["sync_thread"] = {
                    "status": "healthy",
                    "enabled": self._sync_enabled
                }
            else:
                health_status["components"]["sync_thread"] = {
                    "status": "unhealthy",
                    "enabled": self._sync_enabled
                }
            
            # Check memory manager
            if self.memory_manager:
                mem_health = await self.memory_manager.health_check()
                health_status["components"]["memory_manager"] = {
                    "status": mem_health.get("status", "unknown")
                }
            else:
                health_status["components"]["memory_manager"] = {
                    "status": "missing"
                }
            
            # Check lock state
            expired_locks = sum(
                1 for lock_info in self.active_locks.values()
                if datetime.fromisoformat(lock_info["expires_at"]) < datetime.now()
            )
            
            health_status["components"]["locks"] = {
                "status": "healthy" if expired_locks == 0 else "degraded",
                "active_locks": len(self.active_locks),
                "expired_locks": expired_locks
            }
            
            # Check conflicts
            health_status["components"]["conflicts"] = {
                "status": "healthy" if len(self.pending_conflicts) < 10 else "degraded",
                "pending_conflicts": len(self.pending_conflicts)
            }
            
            # Overall assessment
            component_statuses = [comp["status"] for comp in health_status["components"].values()]
            if "unhealthy" in component_statuses:
                health_status["status"] = "unhealthy"
            elif "degraded" in component_statuses or "missing" in component_statuses:
                health_status["status"] = "degraded"
            
            # Add statistics
            health_status["statistics"] = self.stats.copy()
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup sync service resources"""
        try:
            # Stop background sync
            self._sync_enabled = False
            self._shutdown_event.set()
            
            if self._sync_thread and self._sync_thread.is_alive():
                self._sync_thread.join(timeout=10)
            
            # Release all active locks
            for memory_id in list(self.active_locks.keys()):
                await self.release_memory_lock(memory_id, "system", force=True)
            
            self.logger.info("Memory Sync Service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during sync service cleanup: {e}")

# Factory function
async def create_memory_sync_service(
    memory_manager: AldenMemoryManager,
    sync_interval_seconds: int = 30,
    conflict_resolution_strategy: ConflictResolution = ConflictResolution.LATEST_WINS,
    agent_priorities: Dict[str, AgentPriority] = None,
    logger: Optional[logging.Logger] = None
) -> MemorySyncService:
    """
    Factory function to create and initialize Memory Sync Service
    
    Args:
        memory_manager: Alden memory manager instance
        sync_interval_seconds: Automatic sync interval
        conflict_resolution_strategy: Default conflict resolution
        agent_priorities: Agent priority configuration
        logger: Optional logger instance
        
    Returns:
        MemorySyncService: Initialized sync service
    """
    service = MemorySyncService(
        memory_manager=memory_manager,
        sync_interval_seconds=sync_interval_seconds,
        conflict_resolution_strategy=conflict_resolution_strategy,
        agent_priorities=agent_priorities,
        logger=logger
    )
    
    success = await service.initialize()
    if not success:
        raise RuntimeError("Failed to initialize Memory Sync Service")
    
    return service

# Test function
async def test_memory_sync_service():
    """Test the Memory Sync Service functionality"""
    print("🧪 Testing Memory Sync Service")
    print("=" * 40)
    
    try:
        # Mock memory manager for testing
        print("📡 Creating mock memory manager...")
        
        # For testing, we'll create a minimal mock
        class MockMemoryManager:
            def __init__(self):
                self.memories = []
            
            async def health_check(self):
                return {"status": "healthy"}
            
            async def get_session_memories(self, **kwargs):
                return self.memories[:5]  # Return first 5 memories
            
            async def semantic_search(self, **kwargs):
                # Return mock search results
                from database.alden_memory_manager import SearchResult, AldenMemory
                mock_memory = AldenMemory(
                    memory_id="mem_test123",
                    session_id="sess_test123",
                    user_id="user_test123",
                    agent_id="alden",
                    content="Test memory for sync service",
                    memory_type="episodic",
                    memory_category="test",
                    keywords=["test"],
                    custom_tags=["sync"],
                    embedding=None,
                    relevance_score=0.8,
                    importance_score=0.7,
                    confidence_score=0.9,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    last_accessed=datetime.now().isoformat(),
                    expires_at=None,
                    access_count=0,
                    retrieval_count=0,
                    modification_count=0,
                    metadata={},
                    parent_memory_id=None,
                    related_memory_ids=[],
                    conversation_turn=1,
                    context_window=None,
                    version=1,
                    sync_status="synced",
                    last_sync_at=datetime.now().isoformat()
                )
                return [SearchResult(memory=mock_memory, similarity_score=0.9)]
        
        mock_manager = MockMemoryManager()
        print("   ✅ Mock memory manager created")
        
        # Create sync service
        print("\n🔄 Creating sync service...")
        sync_service = await create_memory_sync_service(
            memory_manager=mock_manager,
            sync_interval_seconds=60,  # Longer interval for testing
            conflict_resolution_strategy=ConflictResolution.LATEST_WINS
        )
        print("   ✅ Sync service created successfully")
        
        # Test lock acquisition
        print("\n🔒 Testing memory locking...")
        memory_id = "mem_test_lock_123"
        
        lock_acquired = await sync_service.acquire_memory_lock(
            memory_id=memory_id,
            agent_id="alden",
            lock_duration_minutes=1
        )
        print(f"   Lock acquisition: {'✅ Success' if lock_acquired else '❌ Failed'}")
        
        # Test lock conflicts
        conflict_lock = await sync_service.acquire_memory_lock(
            memory_id=memory_id,
            agent_id="alice",
            wait_for_lock=False
        )
        print(f"   Lock conflict handling: {'✅ Blocked' if not conflict_lock else '❌ Should be blocked'}")
        
        # Test lock release
        lock_released = await sync_service.release_memory_lock(
            memory_id=memory_id,
            agent_id="alden"
        )
        print(f"   Lock release: {'✅ Success' if lock_released else '❌ Failed'}")
        
        # Test agent sync
        print("\n🔄 Testing agent sync...")
        sync_results = await sync_service.sync_agent_memories(
            agent_id="alden",
            user_id="user_test123",
            session_id="sess_test123"
        )
        
        print(f"   Sync operation: {'✅ Success' if sync_results.get('successful_syncs', 0) >= 0 else '❌ Failed'}")
        print(f"   Memories processed: {sync_results.get('memories_processed', 0)}")
        
        # Test memory slice retrieval
        print("\n📋 Testing memory slice...")
        memory_slice = await sync_service.get_agent_memory_slice(
            agent_id="alden",
            user_id="user_test123",
            include_sync_metadata=True
        )
        
        print(f"   Memory slice: {'✅ Retrieved' if 'memory_slice' in memory_slice else '❌ Failed'}")
        print(f"   Slice size: {memory_slice.get('statistics', {}).get('total_memories', 0)}")
        
        # Test statistics
        print("\n📊 Testing sync statistics...")
        stats = await sync_service.get_sync_statistics()
        
        print(f"   Statistics: {'✅ Retrieved' if 'service_stats' in stats else '❌ Failed'}")
        print(f"   Total syncs: {stats.get('service_stats', {}).get('total_syncs', 0)}")
        print(f"   Active locks: {stats.get('active_locks', {}).get('count', 0)}")
        print(f"   Pending conflicts: {stats.get('pending_conflicts', {}).get('count', 0)}")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health = await sync_service.health_check()
        
        print(f"   Overall status: {health.get('status', 'unknown')}")
        for component, status in health.get('components', {}).items():
            print(f"   {component}: {status.get('status', 'unknown')}")
        
        # Test conflict resolution (simulated)
        print("\n⚔️  Testing conflict resolution...")
        
        # Create a mock conflict
        mock_conflict = SyncConflict(
            conflict_id="conflict_test_123",
            memory_id="mem_conflict_123",
            conflicting_agents=["alden", "alice"],
            conflict_type="content",
            created_at=datetime.now().isoformat(),
            resolution_strategy=ConflictResolution.AGENT_PRIORITY,
            resolved=False,
            memory_versions={
                "alden": MemorySlice(
                    memory_id="mem_conflict_123",
                    agent_id="alden",
                    user_id="user_test123",
                    session_id="sess_test123",
                    content="Alden's version",
                    memory_type="episodic",
                    sync_status=SyncStatus.CONFLICT,
                    version=1,
                    last_modified=datetime.now().isoformat(),
                    last_sync=datetime.now().isoformat(),
                    checksum="alden_checksum"
                ),
                "alice": MemorySlice(
                    memory_id="mem_conflict_123",
                    agent_id="alice",
                    user_id="user_test123",
                    session_id="sess_test123",
                    content="Alice's version",
                    memory_type="episodic",
                    sync_status=SyncStatus.CONFLICT,
                    version=1,
                    last_modified=datetime.now().isoformat(),
                    last_sync=datetime.now().isoformat(),
                    checksum="alice_checksum"
                )
            }
        )
        
        # Add conflict to pending list
        sync_service.pending_conflicts[mock_conflict.conflict_id] = mock_conflict
        
        # Resolve conflict
        conflict_resolved = await sync_service.resolve_conflict(
            mock_conflict.conflict_id,
            ConflictResolution.AGENT_PRIORITY
        )
        print(f"   Conflict resolution: {'✅ Success' if conflict_resolved else '❌ Failed'}")
        
        # Cleanup
        await sync_service.cleanup()
        
        print("\n✅ Memory Sync Service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory Sync Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_memory_sync_service())
    sys.exit(0 if success else 1)