# Hearthlink Memory Sync Service

## Overview

The Memory Sync Service provides multi-agent conflict resolution for concurrent memory operations in the Hearthlink ecosystem. It handles memory synchronization between Alden, Alice, Sentry, and Mimic agents with sophisticated conflict resolution strategies.

## Features

- **Multi-Agent Support**: Handles concurrent writes from all Hearthlink agents
- **Conflict Resolution**: Multiple strategies including agent priority, timestamp-based, and importance-based resolution
- **Distributed Locking**: Redis-based memory locking to prevent race conditions
- **Real-time Metrics**: Comprehensive metrics collection and monitoring
- **Health Monitoring**: Built-in health checks and status monitoring
- **Rate Limiting**: Protection against abuse with configurable rate limits
- **Graceful Shutdown**: Proper cleanup of active operations

## Architecture

### Agent Priority Hierarchy
1. **Sentry** (Priority 1) - Security operations have highest priority
2. **Alden** (Priority 2) - Primary agent with high priority  
3. **Alice** (Priority 3) - Analysis agent with medium priority
4. **Mimic** (Priority 4) - Persona agent with lower priority

### Conflict Resolution Strategies
- **AGENT_PRIORITY**: Resolves based on agent hierarchy
- **TIMESTAMP_LATEST**: Most recent operation wins
- **CONTENT_MERGE**: Attempts to merge conflicting content
- **MANUAL_REVIEW**: Queues for human review
- **IMPORTANCE_HIGHEST**: Resolves based on operation importance score

## API Endpoints

### Health & Monitoring
- `GET /health` - Service health check
- `GET /api/metrics` - Service metrics and statistics
- `GET /api/conflicts` - List active conflicts

### Memory Operations
- `POST /api/sync-memory` - Synchronize memory operation
- `GET /api/sync-status/:syncId` - Get sync operation status
- `POST /api/force-sync` - Force immediate synchronization

### Conflict Management
- `POST /api/resolve-conflict/:conflictId` - Manually resolve conflict

## Configuration

### Environment Variables
```bash
# Service Configuration
MEMORY_SYNC_PORT=8003
LOG_LEVEL=info

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=2

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=1000
```

### Agent Configuration
```json
{
  "agents": {
    "priorities": {
      "sentry": 1,
      "alden": 2, 
      "alice": 3,
      "mimic": 4
    },
    "conflictResolution": {
      "timeout": 5000,
      "maxRetries": 3,
      "backoffMs": 1000
    }
  }
}
```

## Usage

### Starting the Service
```bash
# Development
npm run dev

# Production
npm start

# Docker
docker-compose up -d
```

### Memory Sync Request
```javascript
const syncData = {
  agentId: 'alden',
  memoryId: 'user-session-123',
  operation: 'create',
  content: 'User preferences updated',
  importance: 0.8,
  metadata: {
    sessionId: 'sess_123',
    userId: 'user_456'
  }
};

const response = await fetch('/api/sync-memory', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(syncData)
});
```

### Handling Conflicts
```javascript
// Check for conflicts
const conflicts = await fetch('/api/conflicts').then(r => r.json());

// Manually resolve conflict
const resolution = await fetch(`/api/resolve-conflict/${conflictId}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    strategy: 'AGENT_PRIORITY',
    resolution: 'approve'
  })
});
```

## Monitoring

### Metrics Collected
- Total sync operations
- Conflicts resolved/pending
- Agent operation counts
- Average resolution time
- System health status

### Health Checks
The service provides comprehensive health monitoring:
- Redis connectivity
- Active operation counts
- Conflict queue status
- System uptime and performance

### Logging
Structured JSON logging with configurable levels:
- Error logs: `/var/log/hearthlink/memory-sync-error.log`
- General logs: `/var/log/hearthlink/memory-sync.log`
- Console output for development

## Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Integration tests
npm run test:integration
```

## Deployment

### Docker Deployment
```bash
# Build and start
docker-compose up -d

# Scale service
docker-compose up -d --scale memory-sync=3

# Monitor logs
docker-compose logs -f memory-sync
```

### Production Considerations
- Configure Redis persistence for reliability
- Set up monitoring and alerting
- Use load balancer for high availability
- Configure log rotation
- Set appropriate resource limits

## Security

- Rate limiting to prevent abuse
- Input validation on all endpoints
- Secure Redis connection
- Non-root container execution
- Memory operation auditing

## Performance

- Redis-based distributed locking
- Connection pooling
- Graceful degradation under load
- Configurable timeout and retry logic
- Memory usage optimization

## Troubleshooting

### Common Issues
1. **Redis Connection Failed**: Check Redis server status and credentials
2. **High Conflict Rate**: Review agent operation patterns and timing
3. **Memory Locks Stuck**: Monitor lock TTL and cleanup procedures
4. **Performance Issues**: Check Redis memory usage and network latency

### Debug Mode
```bash
LOG_LEVEL=debug npm start
```

## Contributing

1. Follow the existing code style
2. Add tests for new features  
3. Update documentation
4. Test with all agent types
5. Monitor performance impact