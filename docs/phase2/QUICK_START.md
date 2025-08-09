# Alden Memory Phase 2 - Quick Start Guide

## Overview

Phase 2 enhances Alden's memory system with session tracking, custom tags, and multi-agent support.

## Key Features

- **Session-aware Memory**: Memories are organized by conversation sessions
- **Custom Tags**: User-defined tags for better organization
- **Multi-agent Support**: Isolated memory spaces for different agents
- **Advanced Search**: Hybrid semantic + keyword search with session boosting
- **Memory Lifecycle**: Automatic expiration for working memory
- **Statistics & Analytics**: Comprehensive memory usage statistics

## Quick Setup

1. **Install Dependencies**:
   ```bash
   python3 setup_alden_memory_phase2.py
   ```

2. **Start Database**:
   ```bash
   docker-compose -f docker-compose.pgvector.yml up -d postgres-pgvector
   ```

3. **Test Installation**:
   ```bash
   python3 src/database/alden_memory_manager.py
   ```

## Basic Usage

```python
from database.alden_memory_manager import create_alden_memory_manager

# Initialize memory manager
manager = await create_alden_memory_manager()

# Create a conversation session
session = await manager.create_session(
    user_id="user_123",
    agent_id="alden",
    session_name="Planning Discussion",
    session_type="conversation"
)

# Store a memory
memory = await manager.store_memory(
    session_id=session.session_id,
    user_id="user_123",
    content="User wants to plan a vacation to Japan next summer",
    memory_type="episodic",
    memory_category="conversation",
    custom_tags=["vacation", "japan", "planning"],
    importance_score=0.8
)

# Search memories
results = await manager.semantic_search(
    query="vacation planning",
    user_id="user_123",
    session_id=session.session_id,
    limit=5
)

# Get session statistics
stats = await manager.get_memory_statistics(user_id="user_123")
```

## Memory Types

- **episodic**: Specific conversations and interactions
- **semantic**: General knowledge and facts
- **procedural**: How-to information and processes
- **working**: Temporary session-specific information
- **contextual**: Context and environmental information

## Memory Categories

- **conversation**: General conversation memories
- **task**: Task-related information
- **knowledge**: Factual knowledge
- **preference**: User preferences and settings

## Custom Tags

Create and use custom tags to organize memories:

```python
# Tags are automatically created when used
memory = await manager.store_memory(
    session_id=session_id,
    user_id=user_id,
    content="Remember to send the report by Friday",
    custom_tags=["deadline", "work", "urgent"]
)

# Search by tags
results = await manager.semantic_search(
    query="report deadline",
    user_id=user_id,
    custom_tags=["urgent", "work"]
)
```

## Advanced Features

### Hybrid Search
Combines semantic similarity with keyword matching:

```python
results = await manager.hybrid_search(
    query="machine learning python",
    user_id=user_id,
    keyword_weight=0.3,    # 30% keyword matching
    semantic_weight=0.7,   # 70% semantic similarity
    session_boost=0.1      # 10% boost for same-session memories
)
```

### Memory Statistics
Get comprehensive statistics:

```python
stats = await manager.get_memory_statistics(user_id=user_id)
print(f"Total memories: {stats['total_memories']}")
print(f"Memory by type: {stats['memory_types']}")
print(f"Average importance: {stats['avg_importance_score']}")
```

### Session Management
Track and manage conversation sessions:

```python
# Get all memories from a session
session_memories = await manager.get_session_memories(
    session_id=session.session_id,
    user_id=user_id
)

# Update session activity (done automatically)
await manager._update_session_activity(session.session_id)
```

For more detailed examples, see the test function in `alden_memory_manager.py`.