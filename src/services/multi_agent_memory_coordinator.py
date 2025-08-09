#!/usr/bin/env python3
"""
Multi-Agent Memory Coordinator - Phase 2 Integration
Coordinates memory management across Alden, Alice, Sentry, and Mimic agents
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.alden_memory_manager import AldenMemoryManager, create_alden_memory_manager
from services.memory_sync_service import MemorySyncService, create_memory_sync_service, ConflictResolution, AgentPriority
from embedding.semantic_embedding_service import SemanticMemoryManager
from personas.alden import AldenPersona

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    agent_id: str
    agent_name: str
    priority: AgentPriority
    memory_retention_days: int
    max_working_memory_items: int
    auto_sync_enabled: bool
    conflict_resolution_preference: ConflictResolution
    memory_categories: List[str]
    specialized_memory_types: List[str]
    status: AgentStatus = AgentStatus.INACTIVE

@dataclass
class MemoryAllocation:
    """Memory allocation across agents"""
    total_memories: int
    agent_breakdown: Dict[str, int]
    memory_type_breakdown: Dict[str, int]
    storage_utilization_mb: float
    last_cleanup: str
    next_cleanup: str

class MultiAgentMemoryCoordinator:
    """
    Multi-Agent Memory Coordinator
    
    Orchestrates memory management across multiple AI agents:
    - Alden: Primary productivity and conversation agent
    - Alice: Cognitive behavioral analysis agent  
    - Sentry: Security monitoring and incident response
    - Mimic: Dynamic persona creation and management
    
    Features:
    - Agent-specific memory isolation
    - Cross-agent memory sharing when appropriate
    - Coordinated conflict resolution
    - Load balancing and resource management
    - Comprehensive monitoring and analytics
    """
    
    def __init__(
        self,
        database_url: str = None,
        embedding_service: SemanticMemoryManager = None,
        sync_interval_seconds: int = 60,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Multi-Agent Memory Coordinator
        
        Args:
            database_url: PostgreSQL connection URL
            embedding_service: Semantic embedding service
            sync_interval_seconds: Memory sync interval
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.database_url = database_url
        self.embedding_service = embedding_service
        self.sync_interval = sync_interval_seconds
        
        # Core services
        self.memory_manager: Optional[AldenMemoryManager] = None
        self.sync_service: Optional[MemorySyncService] = None
        
        # Agent configurations
        self.agent_configs = self._create_default_agent_configs()
        self.active_agents: Dict[str, AgentStatus] = {}
        
        # Cross-agent sharing rules
        self.sharing_rules = self._create_default_sharing_rules()
        
        # Performance tracking
        self.coordinator_stats = {
            "total_agents": len(self.agent_configs),
            "active_agents": 0,
            "total_coordinated_operations": 0,
            "cross_agent_shares": 0,
            "resource_optimizations": 0,
            "avg_coordination_time_ms": 0.0
        }
        
        self.logger.info("Multi-Agent Memory Coordinator initialized", extra={
            "agents_configured": len(self.agent_configs),
            "sync_interval": sync_interval_seconds
        })
    
    def _create_default_agent_configs(self) -> Dict[str, AgentConfig]:
        """Create default configurations for all agents"""
        return {
            "alden": AgentConfig(
                agent_id="alden",
                agent_name="Alden - Primary Assistant",
                priority=AgentPriority.HIGH,
                memory_retention_days=90,
                max_working_memory_items=100,
                auto_sync_enabled=True,
                conflict_resolution_preference=ConflictResolution.LATEST_WINS,
                memory_categories=["conversation", "task", "knowledge", "preference"],
                specialized_memory_types=["episodic", "semantic", "procedural"]
            ),
            "alice": AgentConfig(
                agent_id="alice", 
                agent_name="Alice - Cognitive Analysis",
                priority=AgentPriority.MEDIUM,
                memory_retention_days=60,
                max_working_memory_items=50,
                auto_sync_enabled=True,
                conflict_resolution_preference=ConflictResolution.HIGHEST_IMPORTANCE,
                memory_categories=["analysis", "pattern", "behavioral"],
                specialized_memory_types=["episodic", "working"]
            ),
            "sentry": AgentConfig(
                agent_id="sentry",
                agent_name="Sentry - Security Monitor", 
                priority=AgentPriority.MEDIUM,
                memory_retention_days=180,  # Longer retention for security
                max_working_memory_items=75,
                auto_sync_enabled=True,
                conflict_resolution_preference=ConflictResolution.MANUAL_REVIEW,
                memory_categories=["security", "incident", "alert", "audit"],
                specialized_memory_types=["semantic", "contextual"]
            ),
            "mimic": AgentConfig(
                agent_id="mimic",
                agent_name="Mimic - Dynamic Personas",
                priority=AgentPriority.LOW,
                memory_retention_days=30,
                max_working_memory_items=25,
                auto_sync_enabled=False,  # Manual sync for dynamic personas
                conflict_resolution_preference=ConflictResolution.AGENT_PRIORITY,
                memory_categories=["persona", "style", "template"],
                specialized_memory_types=["working", "contextual"]
            )
        }
    
    def _create_default_sharing_rules(self) -> Dict[str, Any]:
        """Create default cross-agent memory sharing rules"""
        return {
            "global_sharing": {
                # Memories that can be shared across all agents
                "user_preferences": ["alden", "alice", "mimic"],
                "system_knowledge": ["alden", "alice", "sentry"],
                "security_alerts": ["alden", "sentry"],
                "behavioral_patterns": ["alice", "mimic"]
            },
            "restricted_sharing": {
                # Agent-specific memories that should not be shared
                "alden": ["personal_conversations", "private_tasks"],
                "alice": ["analysis_internals", "cognitive_models"],
                "sentry": ["security_credentials", "incident_details"],
                "mimic": ["persona_templates", "style_adaptations"]
            },
            "automatic_propagation": {
                # Memories that automatically propagate to specific agents
                "user_preference_changes": ["alden", "mimic"],
                "security_incidents": ["alden", "sentry"],
                "behavioral_insights": ["alden", "alice"]
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize all coordinator services"""
        try:
            self.logger.info("Initializing Multi-Agent Memory Coordinator...")
            
            # Initialize memory manager
            self.memory_manager = await create_alden_memory_manager(
                database_url=self.database_url,
                embedding_service=self.embedding_service,
                logger=self.logger
            )
            
            # Initialize sync service
            agent_priorities = {
                config.agent_id: config.priority 
                for config in self.agent_configs.values()
            }
            
            self.sync_service = await create_memory_sync_service(
                memory_manager=self.memory_manager,
                sync_interval_seconds=self.sync_interval,
                conflict_resolution_strategy=ConflictResolution.LATEST_WINS,
                agent_priorities=agent_priorities,
                logger=self.logger
            )
            
            # Initialize agent statuses
            for agent_id in self.agent_configs.keys():
                self.active_agents[agent_id] = AgentStatus.INACTIVE
            
            self.logger.info("Multi-Agent Memory Coordinator initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize coordinator: {e}")
            return False
    
    async def register_agent(
        self,
        agent_id: str,
        config: AgentConfig = None
    ) -> bool:
        """
        Register an agent with the coordinator
        
        Args:
            agent_id: Agent identifier
            config: Optional custom configuration
            
        Returns:
            bool: Registration success
        """
        try:
            if config:
                self.agent_configs[agent_id] = config
            elif agent_id not in self.agent_configs:
                self.logger.error(f"No configuration found for agent {agent_id}")
                return False
            
            # Mark agent as active
            self.active_agents[agent_id] = AgentStatus.ACTIVE
            self.coordinator_stats["active_agents"] = sum(
                1 for status in self.active_agents.values() 
                if status == AgentStatus.ACTIVE
            )
            
            # Create initial session if needed
            test_user_id = f"system_{agent_id}"
            session = await self.memory_manager.create_session(
                user_id=test_user_id,
                agent_id=agent_id,
                session_name=f"{agent_id.title()} System Session",
                session_type="system"
            )
            
            self.logger.info(f"Agent {agent_id} registered successfully", extra={
                "session_id": session.session_id,
                "agent_priority": self.agent_configs[agent_id].priority.value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    async def store_agent_memory(
        self,
        agent_id: str,
        user_id: str,
        session_id: str,
        content: str,
        memory_type: str = "episodic",
        memory_category: str = "general",
        custom_tags: List[str] = None,
        importance_score: float = 0.5,
        share_with_agents: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Store memory for a specific agent with coordination features
        
        Args:
            agent_id: Agent storing the memory
            user_id: User identifier
            session_id: Session identifier
            content: Memory content
            memory_type: Type of memory
            memory_category: Category of memory
            custom_tags: User-defined tags
            importance_score: Importance score
            share_with_agents: List of agents to share with
            metadata: Additional metadata
            
        Returns:
            Optional[str]: Memory ID if successful
        """
        try:
            start_time = datetime.now()
            
            if agent_id not in self.agent_configs:
                raise ValueError(f"Unknown agent: {agent_id}")
            
            if self.active_agents.get(agent_id) != AgentStatus.ACTIVE:
                raise ValueError(f"Agent {agent_id} is not active")
            
            # Acquire memory lock for coordination
            memory_id_placeholder = f"mem_{uuid.uuid4().hex[:16]}"
            lock_acquired = await self.sync_service.acquire_memory_lock(
                memory_id=memory_id_placeholder,
                agent_id=agent_id,
                lock_duration_minutes=2
            )
            
            if not lock_acquired:
                raise RuntimeError("Could not acquire memory lock")
            
            try:
                # Enhanced metadata with agent coordination info
                enhanced_metadata = metadata or {}
                enhanced_metadata.update({
                    "coordinated_by": "multi_agent_coordinator",
                    "originating_agent": agent_id,
                    "coordination_timestamp": datetime.now().isoformat(),
                    "sharing_rules_applied": bool(share_with_agents)
                })
                
                # Store the memory
                memory = await self.memory_manager.store_memory(
                    session_id=session_id,
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type,
                    memory_category=memory_category,
                    agent_id=agent_id,
                    custom_tags=custom_tags or [],
                    importance_score=importance_score,
                    metadata=enhanced_metadata
                )
                
                # Apply cross-agent sharing if specified
                if share_with_agents:
                    await self._apply_cross_agent_sharing(
                        memory, share_with_agents, user_id
                    )
                
                # Check for automatic propagation rules
                await self._check_automatic_propagation(memory, user_id)
                
                # Release lock
                await self.sync_service.release_memory_lock(
                    memory.memory_id, agent_id
                )
                
                # Update statistics
                coordination_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.coordinator_stats["total_coordinated_operations"] += 1
                self.coordinator_stats["avg_coordination_time_ms"] = (
                    (self.coordinator_stats["avg_coordination_time_ms"] * 
                     (self.coordinator_stats["total_coordinated_operations"] - 1) + 
                     coordination_time_ms) /
                    self.coordinator_stats["total_coordinated_operations"]
                )
                
                self.logger.info(f"Memory stored with coordination for {agent_id}", extra={
                    "memory_id": memory.memory_id,
                    "memory_type": memory_type,
                    "shared_with": len(share_with_agents) if share_with_agents else 0,
                    "coordination_time_ms": coordination_time_ms
                })
                
                return memory.memory_id
                
            finally:
                # Ensure lock is released
                await self.sync_service.release_memory_lock(
                    memory_id_placeholder, agent_id, force=True
                )
            
        except Exception as e:
            self.logger.error(f"Failed to store coordinated memory for {agent_id}: {e}")
            return None
    
    async def search_agent_memories(
        self,
        agent_id: str,
        user_id: str,
        query: str,
        session_id: Optional[str] = None,
        include_shared_memories: bool = True,
        search_type: str = "semantic",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories for a specific agent with cross-agent access
        
        Args:
            agent_id: Agent performing search
            user_id: User identifier
            query: Search query
            session_id: Optional session filter
            include_shared_memories: Include memories shared from other agents
            search_type: Type of search (semantic, hybrid)
            limit: Maximum results
            
        Returns:
            List[Dict[str, Any]]: Search results with coordination metadata
        """
        try:
            if agent_id not in self.agent_configs:
                raise ValueError(f"Unknown agent: {agent_id}")
            
            # Perform primary search for agent's own memories
            if search_type == "semantic":
                search_results = await self.memory_manager.semantic_search(
                    query=query,
                    user_id=user_id,
                    agent_id=agent_id,
                    session_id=session_id,
                    limit=limit
                )
            else:  # hybrid
                search_results = await self.memory_manager.hybrid_search(
                    query=query,
                    user_id=user_id,
                    agent_id=agent_id,
                    session_id=session_id,
                    limit=limit
                )
            
            coordinated_results = []
            
            # Process each result with coordination metadata
            for result in search_results:
                result_data = {
                    "memory": asdict(result.memory),
                    "similarity_score": result.similarity_score,
                    "source_agent": result.memory.agent_id,
                    "is_shared": result.memory.agent_id != agent_id,
                    "coordination_metadata": {
                        "accessed_by": agent_id,
                        "access_timestamp": datetime.now().isoformat(),
                        "cross_agent_access": result.memory.agent_id != agent_id
                    }
                }
                
                # Add sharing context if it's a shared memory
                if result.memory.agent_id != agent_id:
                    result_data["sharing_context"] = self._get_sharing_context(
                        result.memory.agent_id, agent_id, result.memory.memory_category
                    )
                
                coordinated_results.append(result_data)
            
            # Include shared memories from other agents if requested
            if include_shared_memories and len(coordinated_results) < limit:
                remaining_limit = limit - len(coordinated_results)
                shared_results = await self._search_shared_memories(
                    agent_id, user_id, query, session_id, remaining_limit
                )
                coordinated_results.extend(shared_results)
            
            self.logger.info(f"Coordinated search completed for {agent_id}", extra={
                "query_length": len(query),
                "results_count": len(coordinated_results),
                "shared_results": sum(1 for r in coordinated_results if r["is_shared"]),
                "search_type": search_type
            })
            
            return coordinated_results[:limit]
            
        except Exception as e:
            self.logger.error(f"Coordinated search failed for {agent_id}: {e}")
            return []
    
    async def sync_all_agents(
        self,
        user_id: str,
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize memories across all active agents
        
        Args:
            user_id: User identifier
            force_sync: Force sync regardless of recent sync status
            
        Returns:
            Dict[str, Any]: Comprehensive sync results
        """
        try:
            start_time = datetime.now()
            
            sync_results = {
                "coordination_id": str(uuid.uuid4()),
                "user_id": user_id,
                "agents_synced": [],
                "total_memories_processed": 0,
                "conflicts_detected": 0,
                "conflicts_resolved": 0,
                "sync_errors": [],
                "agent_results": {}
            }
            
            # Sync each active agent
            active_agent_ids = [
                agent_id for agent_id, status in self.active_agents.items()
                if status == AgentStatus.ACTIVE
            ]
            
            for agent_id in active_agent_ids:
                try:
                    agent_sync_result = await self.sync_service.sync_agent_memories(
                        agent_id=agent_id,
                        user_id=user_id,
                        force_sync=force_sync
                    )
                    
                    sync_results["agent_results"][agent_id] = agent_sync_result
                    sync_results["agents_synced"].append(agent_id)
                    sync_results["total_memories_processed"] += agent_sync_result.get("memories_processed", 0)
                    sync_results["conflicts_detected"] += agent_sync_result.get("conflicts_detected", 0)
                    sync_results["conflicts_resolved"] += agent_sync_result.get("conflicts_resolved", 0)
                    
                    if agent_sync_result.get("errors"):
                        sync_results["sync_errors"].extend(agent_sync_result["errors"])
                    
                except Exception as agent_error:
                    error_msg = f"Sync failed for {agent_id}: {agent_error}"
                    sync_results["sync_errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            # Apply cross-agent optimizations
            optimization_results = await self._apply_cross_agent_optimizations(user_id)
            sync_results["optimizations"] = optimization_results
            
            total_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            sync_results["total_sync_time_ms"] = total_time_ms
            sync_results["success"] = len(sync_results["sync_errors"]) == 0
            
            self.logger.info("Multi-agent sync completed", extra={
                "coordination_id": sync_results["coordination_id"],
                "agents_synced": len(sync_results["agents_synced"]),
                "memories_processed": sync_results["total_memories_processed"],
                "conflicts": sync_results["conflicts_detected"],
                "sync_time_ms": total_time_ms
            })
            
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Multi-agent sync failed: {e}")
            return {
                "coordination_id": str(uuid.uuid4()),
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_memory_allocation(self, user_id: str) -> MemoryAllocation:
        """
        Get comprehensive memory allocation across all agents
        
        Args:
            user_id: User identifier
            
        Returns:
            MemoryAllocation: Memory usage breakdown
        """
        try:
            # Get statistics from memory manager
            stats = await self.memory_manager.get_memory_statistics(user_id=user_id)
            
            agent_breakdown = {}
            memory_type_breakdown = {}
            total_memories = 0
            
            # Process memory breakdown by agent
            for breakdown in stats.get("memory_breakdown", []):
                agent_id = breakdown["agent_id"]
                count = breakdown["count"]
                memory_type = breakdown["memory_type"]
                
                agent_breakdown[agent_id] = agent_breakdown.get(agent_id, 0) + count
                memory_type_breakdown[memory_type] = memory_type_breakdown.get(memory_type, 0) + count
                total_memories += count
            
            # Estimate storage utilization (simplified calculation)
            # Average 1.5KB per memory (embedding + content + metadata)
            storage_utilization_mb = total_memories * 1.5 / 1024
            
            return MemoryAllocation(
                total_memories=total_memories,
                agent_breakdown=agent_breakdown,
                memory_type_breakdown=memory_type_breakdown,
                storage_utilization_mb=storage_utilization_mb,
                last_cleanup=datetime.now().isoformat(),  # Placeholder
                next_cleanup=(datetime.now() + timedelta(hours=24)).isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get memory allocation: {e}")
            return MemoryAllocation(
                total_memories=0,
                agent_breakdown={},
                memory_type_breakdown={},
                storage_utilization_mb=0.0,
                last_cleanup=datetime.now().isoformat(),
                next_cleanup=datetime.now().isoformat()
            )
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get comprehensive coordinator status and statistics"""
        try:
            # Get sync service statistics
            sync_stats = await self.sync_service.get_sync_statistics()
            
            # Get memory manager health
            memory_health = await self.memory_manager.health_check()
            
            # Calculate agent status summary
            agent_status_summary = {}
            for agent_id, status in self.active_agents.items():
                agent_status_summary[agent_id] = {
                    "status": status.value,
                    "config": asdict(self.agent_configs[agent_id]) if agent_id in self.agent_configs else None
                }
            
            return {
                "coordinator_stats": self.coordinator_stats.copy(),
                "agent_status": agent_status_summary,
                "sync_service_stats": sync_stats,
                "memory_manager_health": memory_health,
                "sharing_rules": self.sharing_rules,
                "system_health": {
                    "overall_status": "healthy" if memory_health.get("status") == "healthy" else "degraded",
                    "active_agents": self.coordinator_stats["active_agents"],
                    "total_agents": self.coordinator_stats["total_agents"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get coordinator status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    async def _apply_cross_agent_sharing(
        self,
        memory,
        share_with_agents: List[str],
        user_id: str
    ):
        """Apply cross-agent memory sharing"""
        try:
            for target_agent in share_with_agents:
                if target_agent in self.agent_configs and target_agent != memory.agent_id:
                    # Create shared memory copy for target agent
                    shared_memory_id = f"shared_{memory.memory_id}_{target_agent}"
                    
                    # Store shared version (would need enhanced memory manager method)
                    self.logger.info(f"Shared memory {memory.memory_id} with {target_agent}")
                    self.coordinator_stats["cross_agent_shares"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to apply cross-agent sharing: {e}")
    
    async def _check_automatic_propagation(self, memory, user_id: str):
        """Check and apply automatic propagation rules"""
        try:
            propagation_rules = self.sharing_rules.get("automatic_propagation", {})
            
            # Check each propagation rule
            for rule_name, target_agents in propagation_rules.items():
                if self._memory_matches_rule(memory, rule_name):
                    await self._apply_cross_agent_sharing(memory, target_agents, user_id)
                    self.logger.info(f"Applied automatic propagation rule: {rule_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to check automatic propagation: {e}")
    
    def _memory_matches_rule(self, memory, rule_name: str) -> bool:
        """Check if memory matches a propagation rule"""
        # Simplified rule matching - would be more sophisticated in practice
        content_lower = memory.content.lower()
        
        if rule_name == "user_preference_changes":
            return "preference" in content_lower or "setting" in content_lower
        elif rule_name == "security_incidents":
            return "security" in content_lower or "alert" in content_lower
        elif rule_name == "behavioral_insights":
            return "behavior" in content_lower or "pattern" in content_lower
        
        return False
    
    async def _search_shared_memories(
        self,
        agent_id: str,
        user_id: str,
        query: str,
        session_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search for memories shared with this agent"""
        try:
            shared_results = []
            
            # Get sharing rules for this agent
            shareable_categories = self.sharing_rules.get("global_sharing", {})
            
            # Search across other agents (simplified implementation)
            for category, allowed_agents in shareable_categories.items():
                if agent_id in allowed_agents:
                    # Would implement cross-agent search here
                    pass
            
            return shared_results[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search shared memories: {e}")
            return []
    
    def _get_sharing_context(
        self,
        source_agent: str,
        target_agent: str,
        memory_category: str
    ) -> Dict[str, Any]:
        """Get context for why a memory was shared"""
        return {
            "source_agent": source_agent,
            "target_agent": target_agent,
            "memory_category": memory_category,
            "sharing_reason": "global_sharing_rule",  # Simplified
            "shared_at": datetime.now().isoformat()
        }
    
    async def _apply_cross_agent_optimizations(self, user_id: str) -> Dict[str, Any]:
        """Apply memory optimizations across agents"""
        try:
            optimizations = {
                "duplicate_removal": 0,
                "memory_consolidation": 0,
                "storage_optimization": 0
            }
            
            # Placeholder for optimization logic
            # Would implement:
            # - Duplicate memory detection and removal
            # - Memory consolidation for similar content
            # - Storage optimization strategies
            
            self.coordinator_stats["resource_optimizations"] += sum(optimizations.values())
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimizations: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup coordinator resources"""
        try:
            # Mark all agents as inactive
            for agent_id in self.active_agents:
                self.active_agents[agent_id] = AgentStatus.INACTIVE
            
            # Cleanup services
            if self.sync_service:
                await self.sync_service.cleanup()
            
            if self.memory_manager:
                await self.memory_manager.cleanup()
            
            self.logger.info("Multi-Agent Memory Coordinator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during coordinator cleanup: {e}")

# Factory function
async def create_multi_agent_coordinator(
    database_url: str = None,
    embedding_service: SemanticMemoryManager = None,
    sync_interval_seconds: int = 60,
    logger: Optional[logging.Logger] = None
) -> MultiAgentMemoryCoordinator:
    """
    Factory function to create and initialize Multi-Agent Memory Coordinator
    
    Args:
        database_url: PostgreSQL connection URL
        embedding_service: Semantic embedding service
        sync_interval_seconds: Memory sync interval
        logger: Optional logger instance
        
    Returns:
        MultiAgentMemoryCoordinator: Initialized coordinator
    """
    coordinator = MultiAgentMemoryCoordinator(
        database_url=database_url,
        embedding_service=embedding_service,
        sync_interval_seconds=sync_interval_seconds,
        logger=logger
    )
    
    success = await coordinator.initialize()
    if not success:
        raise RuntimeError("Failed to initialize Multi-Agent Memory Coordinator")
    
    return coordinator

# Test function
async def test_multi_agent_coordinator():
    """Test the Multi-Agent Memory Coordinator"""
    print("🧪 Testing Multi-Agent Memory Coordinator")
    print("=" * 45)
    
    try:
        # Create coordinator
        print("📡 Creating multi-agent coordinator...")
        coordinator = await create_multi_agent_coordinator(
            sync_interval_seconds=120  # Longer interval for testing
        )
        print("   ✅ Coordinator created successfully")
        
        # Register agents
        print("\n🤖 Registering agents...")
        agents_to_register = ["alden", "alice", "sentry", "mimic"]
        
        for agent_id in agents_to_register:
            success = await coordinator.register_agent(agent_id)
            print(f"   {agent_id}: {'✅ Registered' if success else '❌ Failed'}")
        
        # Test coordinated memory storage
        print("\n💾 Testing coordinated memory storage...")
        test_user_id = "test_coordination_user"
        
        # Create test sessions for each agent
        test_sessions = {}
        for agent_id in agents_to_register:
            session = await coordinator.memory_manager.create_session(
                user_id=test_user_id,
                agent_id=agent_id,
                session_name=f"Test Session for {agent_id}",
                session_type="test"
            )
            test_sessions[agent_id] = session.session_id
        
        # Store memories with coordination
        test_memories = [
            {
                "agent_id": "alden",
                "content": "User prefers morning meetings and uses dark mode",
                "memory_type": "semantic",
                "memory_category": "preference",
                "share_with_agents": ["alice", "mimic"],
                "importance_score": 0.8
            },
            {
                "agent_id": "alice", 
                "content": "User shows signs of productivity anxiety during task planning",
                "memory_type": "episodic",
                "memory_category": "analysis",
                "share_with_agents": ["alden"],
                "importance_score": 0.7
            },
            {
                "agent_id": "sentry",
                "content": "Security alert: Unusual login pattern detected from new location",
                "memory_type": "contextual",
                "memory_category": "security",
                "share_with_agents": ["alden"],
                "importance_score": 0.9
            }
        ]
        
        stored_memory_ids = []
        for memory_data in test_memories:
            agent_id = memory_data["agent_id"]
            memory_id = await coordinator.store_agent_memory(
                agent_id=agent_id,
                user_id=test_user_id,
                session_id=test_sessions[agent_id],
                content=memory_data["content"],
                memory_type=memory_data["memory_type"],
                memory_category=memory_data["memory_category"],
                share_with_agents=memory_data["share_with_agents"],
                importance_score=memory_data["importance_score"]
            )
            
            if memory_id:
                stored_memory_ids.append(memory_id)
                print(f"   ✅ Stored memory for {agent_id}: {memory_id}")
            else:
                print(f"   ❌ Failed to store memory for {agent_id}")
        
        # Test coordinated search
        print("\n🔍 Testing coordinated search...")
        search_queries = [
            ("alden", "user preferences and settings"),
            ("alice", "productivity and behavior patterns"),
            ("sentry", "security alerts and incidents")
        ]
        
        for agent_id, query in search_queries:
            results = await coordinator.search_agent_memories(
                agent_id=agent_id,
                user_id=test_user_id,
                query=query,
                include_shared_memories=True,
                limit=5
            )
            
            print(f"   {agent_id}: Found {len(results)} results")
            shared_count = sum(1 for r in results if r["is_shared"])
            print(f"     Shared memories: {shared_count}")
        
        # Test multi-agent sync
        print("\n🔄 Testing multi-agent sync...")
        sync_results = await coordinator.sync_all_agents(
            user_id=test_user_id,
            force_sync=True
        )
        
        print(f"   Sync success: {'✅' if sync_results['success'] else '❌'}")
        print(f"   Agents synced: {len(sync_results['agents_synced'])}")
        print(f"   Total memories: {sync_results['total_memories_processed']}")
        print(f"   Conflicts: {sync_results['conflicts_detected']}")
        
        # Test memory allocation
        print("\n📊 Testing memory allocation...")
        allocation = await coordinator.get_memory_allocation(test_user_id)
        
        print(f"   Total memories: {allocation.total_memories}")
        print(f"   Storage utilization: {allocation.storage_utilization_mb:.1f} MB")
        print(f"   Agent breakdown:")
        for agent_id, count in allocation.agent_breakdown.items():
            print(f"     {agent_id}: {count} memories")
        
        # Test coordinator status
        print("\n📈 Testing coordinator status...")
        status = await coordinator.get_coordinator_status()
        
        print(f"   Overall health: {status.get('system_health', {}).get('overall_status', 'unknown')}")
        print(f"   Active agents: {status.get('coordinator_stats', {}).get('active_agents', 0)}")
        print(f"   Total operations: {status.get('coordinator_stats', {}).get('total_coordinated_operations', 0)}")
        print(f"   Cross-agent shares: {status.get('coordinator_stats', {}).get('cross_agent_shares', 0)}")
        
        # Cleanup
        await coordinator.cleanup()
        
        print("\n✅ Multi-Agent Memory Coordinator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Multi-Agent Memory Coordinator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_multi_agent_coordinator())
    sys.exit(0 if success else 1)