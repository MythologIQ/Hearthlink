# Alden Memory Phase 2 - API Reference

## AldenMemoryManager

Main class for managing Alden's enhanced memory system.

### Initialization

```python
manager = AldenMemoryManager(database_url, embedding_service, logger)
await manager.initialize()
```

### Session Management

#### create_session()
Create a new conversation session.

**Parameters:**
- `user_id` (str): User identifier
- `agent_id` (str): Agent identifier (default: "alden") 
- `session_name` (str, optional): Session name
- `session_type` (str): Session type ("conversation", "task", "learning")
- `session_settings` (dict): Optional session configuration

**Returns:** `AldenSession` object

#### get_session_memories()
Get all memories for a specific session.

**Parameters:**
- `session_id` (str): Session identifier
- `user_id` (str): User identifier
- `agent_id` (str): Agent identifier
- `memory_types` (list, optional): Filter by memory types
- `limit` (int): Maximum results (default: 50)

**Returns:** List of `AldenMemory` objects

### Memory Storage

#### store_memory()
Store a new memory with enhanced features.

**Parameters:**
- `session_id` (str): Session identifier
- `user_id` (str): User identifier
- `content` (str): Memory content
- `memory_type` (str): Memory type ("episodic", "semantic", "procedural", "working", "contextual")
- `memory_category` (str): Memory category ("conversation", "task", "knowledge", "preference")
- `agent_id` (str): Agent identifier (default: "alden")
- `keywords` (list): Extracted keywords
- `custom_tags` (list): User-defined tags
- `relevance_score` (float): Relevance score (0.0-1.0)
- `importance_score` (float): Importance score (0.0-1.0)
- `confidence_score` (float): Confidence score (0.0-1.0)
- `expires_after_hours` (int, optional): Hours until expiration
- `metadata` (dict): Additional metadata
- `conversation_turn` (int, optional): Turn number in conversation
- `context_window` (str, optional): Context when created
- `parent_memory_id` (str, optional): Parent memory reference

**Returns:** `AldenMemory` object

### Memory Search

#### semantic_search()
Perform semantic similarity search.

**Parameters:**
- `query` (str): Search query
- `user_id` (str): User identifier  
- `agent_id` (str): Agent identifier (default: "alden")
- `session_id` (str, optional): Session filter
- `memory_types` (list, optional): Memory type filters
- `memory_categories` (list, optional): Category filters
- `custom_tags` (list, optional): Tag filters
- `limit` (int): Maximum results (default: 10)
- `min_similarity` (float): Minimum similarity threshold (default: 0.3)
- `include_expired` (bool): Include expired memories (default: False)

**Returns:** List of `SearchResult` objects

#### hybrid_search()
Perform hybrid search combining keywords and semantic similarity.

**Parameters:**
- `query` (str): Search query
- `user_id` (str): User identifier
- `agent_id` (str): Agent identifier (default: "alden")
- `session_id` (str, optional): Session filter (gets boost)
- `memory_types` (list, optional): Memory type filters
- `limit` (int): Maximum results (default: 10)
- `keyword_weight` (float): Weight for keyword matching (default: 0.3)
- `semantic_weight` (float): Weight for semantic similarity (default: 0.7)
- `session_boost` (float): Boost for same-session memories (default: 0.1)

**Returns:** List of `SearchResult` objects

### Statistics and Monitoring

#### get_memory_statistics()
Get comprehensive memory statistics.

**Parameters:**
- `user_id` (str, optional): User filter
- `agent_id` (str, optional): Agent filter
- `session_id` (str, optional): Session filter

**Returns:** Dictionary with comprehensive statistics

#### health_check()
Perform comprehensive health check.

**Returns:** Dictionary with health status and component details

#### cleanup_expired_memories()
Clean up expired working memories.

**Returns:** Number of memories cleaned up

### Utility Methods

#### cleanup()
Cleanup resources and connections.

#### generate_memory_id()
Generate unique memory ID.

#### generate_session_id()
Generate unique session ID.

## Data Models

### AldenMemory
Complete memory record with all Phase 2 features.

### AldenSession  
Session tracking record.

### MemoryTag
Memory tag definition.

### SearchResult
Enhanced search result with scoring metadata.

## Database Schema

The Phase 2 schema includes these main tables:

- `alden_memory`: Enhanced memory storage with sessions and tags
- `alden_sessions`: Session tracking and management
- `alden_memory_tags`: Tag definitions and hierarchy
- `alden_memory_tag_relations`: Memory-tag relationships

## Error Handling

All methods include comprehensive error handling and logging. Check the logs for detailed error information.

## Performance Optimization

- Connection pooling for database efficiency
- Caching for frequently accessed tags and sessions
- Optimized indexes for fast retrieval
- Batch operations where possible

For implementation details, see the source code in `alden_memory_manager.py`.