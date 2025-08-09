# Memory Slicing and Sync Service - Phase 2 Guide

## Overview

The Memory Slicing and Sync Service provides sophisticated multi-agent memory coordination for Hearthlink's AI system. It manages memory synchronization, conflict resolution, and cross-agent sharing across Alden, Alice, Sentry, and Mimic agents.

## Architecture

### Core Components

1. **MemorySyncService**: Handles memory synchronization and conflict resolution
2. **MultiAgentMemoryCoordinator**: Orchestrates memory management across agents
3. **Agent-Specific Memory Slices**: Isolated memory spaces per agent
4. **Cross-Agent Sharing Rules**: Configurable memory sharing policies

### Agent Configuration

#### Alden (Primary Assistant)
- **Priority**: HIGH
- **Memory Retention**: 90 days
- **Conflict Resolution**: Latest Wins
- **Specialties**: Conversation, tasks, knowledge, preferences
- **Memory Types**: Episodic, semantic, procedural

#### Alice (Cognitive Analysis)
- **Priority**: MEDIUM  
- **Memory Retention**: 60 days
- **Conflict Resolution**: Highest Importance
- **Specialties**: Analysis, patterns, behavioral insights
- **Memory Types**: Episodic, working

#### Sentry (Security Monitor)
- **Priority**: MEDIUM
- **Memory Retention**: 180 days (security requirement)
- **Conflict Resolution**: Manual Review
- **Specialties**: Security, incidents, alerts, audit logs
- **Memory Types**: Semantic, contextual

#### Mimic (Dynamic Personas)
- **Priority**: LOW
- **Memory Retention**: 30 days
- **Conflict Resolution**: Agent Priority
- **Specialties**: Persona templates, style adaptations
- **Memory Types**: Working, contextual

## Key Features

### 1. Memory Synchronization

```python
# Sync memories for a specific agent
sync_results = await sync_service.sync_agent_memories(
    agent_id="alden",
    user_id="user_123",
    session_id="sess_abc",
    force_sync=False
)

# Sync all agents
all_results = await coordinator.sync_all_agents(
    user_id="user_123",
    force_sync=True
)
```

### 2. Memory Locking

```python
# Acquire exclusive lock for modification
lock_acquired = await sync_service.acquire_memory_lock(
    memory_id="mem_123",
    agent_id="alden",
    lock_duration_minutes=5,
    wait_for_lock=True
)

# Release lock
await sync_service.release_memory_lock(
    memory_id="mem_123",
    agent_id="alden"
)
```

### 3. Conflict Resolution

#### Available Strategies

- **LATEST_WINS**: Keep the most recently modified version
- **HIGHEST_IMPORTANCE**: Choose version with highest importance score
- **AGENT_PRIORITY**: Use agent priority levels for resolution
- **MANUAL_REVIEW**: Require manual intervention
- **MERGE_CONTENT**: Intelligently merge conflicting content

```python
# Resolve specific conflict
resolved = await sync_service.resolve_conflict(
    conflict_id="conflict_123",
    resolution_strategy=ConflictResolution.AGENT_PRIORITY
)
```

### 4. Cross-Agent Memory Sharing

```python
# Store memory with cross-agent sharing
memory_id = await coordinator.store_agent_memory(
    agent_id="alden",
    user_id="user_123",
    session_id="sess_abc",
    content="User prefers dark mode interface",
    memory_category="preference",
    share_with_agents=["alice", "mimic"],
    importance_score=0.8
)
```

### 5. Agent Memory Slices

```python
# Get complete memory slice for an agent
memory_slice = await sync_service.get_agent_memory_slice(
    agent_id="alden",
    user_id="user_123",
    include_sync_metadata=True
)

# Access slice data
total_memories = memory_slice["statistics"]["total_memories"]
locked_memories = memory_slice["statistics"]["locked_memories"]
```

## Sharing Rules

### Global Sharing Categories

- **user_preferences**: Shared with Alden, Alice, Mimic
- **system_knowledge**: Shared with Alden, Alice, Sentry  
- **security_alerts**: Shared with Alden, Sentry
- **behavioral_patterns**: Shared with Alice, Mimic

### Restricted Categories (Agent-Specific)

- **Alden**: Personal conversations, private tasks
- **Alice**: Analysis internals, cognitive models
- **Sentry**: Security credentials, incident details
- **Mimic**: Persona templates, style adaptations

### Automatic Propagation Rules

- **User preference changes** → Auto-share with Alden, Mimic
- **Security incidents** → Auto-share with Alden, Sentry  
- **Behavioral insights** → Auto-share with Alden, Alice

## Integration with Existing System

### 1. Initialize Multi-Agent Coordinator

```python
from services.multi_agent_memory_coordinator import create_multi_agent_coordinator

# Create coordinator
coordinator = await create_multi_agent_coordinator(
    database_url="postgresql://user:pass@localhost:5432/hearthlink_vectors",
    sync_interval_seconds=60
)

# Register agents
await coordinator.register_agent("alden")
await coordinator.register_agent("alice") 
await coordinator.register_agent("sentry")
await coordinator.register_agent("mimic")
```

### 2. Integration with Alden Persona

```python
# In your existing Alden persona code
class AldenPersona:
    def __init__(self, llm_client, coordinator=None):
        self.llm_client = llm_client
        self.coordinator = coordinator  # Add coordinator
    
    async def generate_response(self, user_message, session_id, user_id):
        # Store response in coordinated memory
        if self.coordinator:
            await self.coordinator.store_agent_memory(
                agent_id="alden",
                user_id=user_id,
                session_id=session_id,
                content=f"User: {user_message}\nAlden: {response}",
                memory_type="episodic",
                memory_category="conversation"
            )
```

### 3. Search with Cross-Agent Access

```python
# Enhanced search across agents
async def enhanced_search(query, user_id, agent_id):
    results = await coordinator.search_agent_memories(
        agent_id=agent_id,
        user_id=user_id, 
        query=query,
        include_shared_memories=True,
        search_type="hybrid"
    )
    
    # Process results with sharing context
    for result in results:
        if result["is_shared"]:
            print(f"Shared from {result['source_agent']}: {result['memory']['content']}")
        else:
            print(f"Own memory: {result['memory']['content']}")
```

## Monitoring and Statistics

### 1. Sync Service Statistics

```python
stats = await sync_service.get_sync_statistics()

print(f"Total syncs: {stats['service_stats']['total_syncs']}")
print(f"Active locks: {stats['active_locks']['count']}")
print(f"Pending conflicts: {stats['pending_conflicts']['count']}")
```

### 2. Coordinator Status

```python
status = await coordinator.get_coordinator_status()

print(f"Active agents: {status['coordinator_stats']['active_agents']}")
print(f"Cross-agent shares: {status['coordinator_stats']['cross_agent_shares']}")
print(f"Total operations: {status['coordinator_stats']['total_coordinated_operations']}")
```

### 3. Memory Allocation

```python
allocation = await coordinator.get_memory_allocation(user_id)

print(f"Total memories: {allocation.total_memories}")
print(f"Storage: {allocation.storage_utilization_mb:.1f} MB")

for agent_id, count in allocation.agent_breakdown.items():
    print(f"{agent_id}: {count} memories")
```

## Performance Optimization

### 1. Background Synchronization

- Automatic sync every 60 seconds (configurable)
- Background thread handles sync operations
- Non-blocking agent operations during sync

### 2. Memory Locking

- Prevents concurrent modification conflicts
- Automatic lock expiration (5 minutes default)
- Lock queue for waiting operations

### 3. Conflict Detection

- Real-time conflict detection during sync
- Automatic resolution based on configured strategies
- Manual review queue for complex conflicts

### 4. Resource Management

- Memory cleanup for expired working memories
- Cross-agent duplicate detection and removal
- Storage optimization through memory consolidation

## Error Handling and Recovery

### 1. Sync Failures

```python
# Automatic retry with exponential backoff
# Fallback to individual agent sync if batch fails
# Error logging and alerting for persistent failures
```

### 2. Lock Timeouts

```python
# Automatic lock expiration prevents deadlocks
# Force release capability for maintenance
# Lock health monitoring and cleanup
```

### 3. Conflict Resolution Failures

```python
# Escalation to manual review queue
# Rollback to known good state
# Administrator notification for critical conflicts
```

## Security Considerations

### 1. Agent Isolation

- Memory spaces isolated by agent_id
- Sharing only through explicit rules
- Access control based on agent priorities

### 2. Data Privacy

- User-specific memory isolation
- Encrypted storage for sensitive memories
- Audit logging for all cross-agent access

### 3. Conflict Prevention

- Proactive conflict detection
- Lock-based serialization for critical operations
- Version control for memory modifications

## Deployment Configuration

### 1. Environment Variables

```bash
# Memory Sync Configuration
MEMORY_SYNC_INTERVAL=60
MEMORY_LOCK_TIMEOUT=300
CONFLICT_RESOLUTION_STRATEGY=latest_wins

# Agent Configuration
ALDEN_MEMORY_RETENTION_DAYS=90
ALICE_MEMORY_RETENTION_DAYS=60
SENTRY_MEMORY_RETENTION_DAYS=180
MIMIC_MEMORY_RETENTION_DAYS=30
```

### 2. Database Schema

- Extends existing alden_memory schema
- Additional sync metadata columns
- Indexes optimized for multi-agent queries

### 3. Monitoring Setup

- Prometheus metrics for sync operations
- Grafana dashboards for memory allocation
- Alerting for conflict resolution failures

## Troubleshooting

### Common Issues

1. **Sync Failures**
   - Check database connectivity
   - Verify agent registrations
   - Review conflict resolution logs

2. **Lock Contention**
   - Monitor lock timeout settings
   - Check for deadlock conditions
   - Review concurrent operation patterns

3. **Memory Growth**
   - Verify cleanup schedules
   - Check retention policy configuration
   - Monitor cross-agent sharing rules

### Debug Commands

```python
# Health check
health = await coordinator.get_coordinator_status()

# Force sync single agent
await sync_service.sync_agent_memories("alden", user_id, force_sync=True)

# Release all locks (maintenance)
for memory_id in sync_service.active_locks:
    await sync_service.release_memory_lock(memory_id, "system", force=True)
```

## Future Enhancements

1. **Machine Learning Integration**
   - AI-powered conflict resolution
   - Predictive memory sharing
   - Automatic importance scoring

2. **Advanced Analytics**
   - Memory usage patterns
   - Agent interaction insights
   - Performance optimization recommendations

3. **Distributed Deployment**
   - Multi-node memory coordination
   - Geographic memory distribution
   - High-availability configurations

---

This memory slicing and sync system provides robust multi-agent coordination while maintaining security, performance, and reliability for the Hearthlink AI platform.