# Hearthlink API Specification Document
## Source of Truth - v1.1.0

**Document Version:** 1.0.0  
**Last Updated:** July 13, 2025  
**Status:** Living Document  
**API Version:** v1.1.0  
**Base URL:** `http://localhost:8888`  
**Maintained By:** Backend Team  

---

## 1. API Overview

### 1.1 Introduction
The Hearthlink API provides programmatic access to all AI agents, memory management, configuration, and system operations. The API follows RESTful principles with JSON request/response format and comprehensive error handling.

### 1.2 Base Information
- **Protocol**: HTTP/1.1
- **Content-Type**: `application/json`
- **Encoding**: UTF-8
- **Authentication**: Local session tokens
- **Rate Limiting**: 100 requests per minute per client

### 1.3 API Categories
- **Agents API**: Interact with AI agents (Alden, Alice, Mimic, Sentry)
- **Memory API**: Manage memory slices and retrieval
- **Sessions API**: Manage conversation sessions
- **System API**: System status, configuration, and health checks
- **Security API**: Authentication, permissions, and audit logs

### 1.4 Response Format
All API responses follow a consistent format:
```json
{
  "success": true,
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2025-07-13T10:30:00Z",
    "request_id": "req_123456",
    "api_version": "1.1.0"
  },
  "errors": [] // Only present when success is false
}
```

---

## 2. Authentication & Security

### 2.1 Authentication Scheme
Hearthlink uses local session-based authentication for API access.

#### Session Token Format
```http
Authorization: Bearer <session_token>
```

#### Authentication Flow
```http
POST /api/auth/session
Content-Type: application/json

{
  "user_id": "default-user-001",
  "device_id": "device_123"
}

Response:
{
  "success": true,
  "data": {
    "session_token": "sess_eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_at": "2025-07-13T18:30:00Z",
    "user_id": "default-user-001"
  }
}
```

### 2.2 Error Responses
All errors follow RFC 7807 Problem Details format:
```json
{
  "success": false,
  "errors": [
    {
      "type": "validation_error",
      "title": "Invalid Request Parameters",
      "status": 400,
      "detail": "The 'query' field is required and cannot be empty",
      "instance": "/api/agents/alden/query"
    }
  ]
}
```

### 2.3 Rate Limiting
- **Default Limit**: 100 requests per minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit per window
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

---

## 3. Agents API

### 3.1 Query Agent

Send a natural language query to a specific AI agent.

#### Endpoint
```http
POST /api/agents/{agent_id}/query
```

#### Parameters
- **agent_id** (path, required): Agent identifier (`alden`, `alice`, `mimic`, `sentry`)

#### Request Body
```json
{
  "query": "What's on my schedule today?",
  "session_id": "sess_123456",
  "user_id": "user_123",
  "include_memory": true,
  "max_memories": 10,
  "context": {
    "previous_queries": ["How was my meeting yesterday?"],
    "user_mood": "focused",
    "time_of_day": "morning"
  }
}
```

#### Request Schema
```typescript
interface QueryRequest {
  query: string;                    // User query text (1-10000 chars)
  session_id: string;               // Session identifier
  user_id: string;                  // User identifier  
  include_memory?: boolean;         // Include relevant memories (default: true)
  max_memories?: number;            // Max memories to include (1-50, default: 10)
  context?: {                       // Optional context information
    previous_queries?: string[];    // Recent queries in conversation
    user_mood?: string;             // Current user mood/state
    time_of_day?: string;           // Time context (morning/afternoon/evening)
    location?: string;              // User location context
    urgency?: 'low' | 'medium' | 'high'; // Query urgency level
  };
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "response": "Based on your calendar, you have a team meeting at 10 AM and a client call at 2 PM today.",
    "confidence": 0.95,
    "agent_id": "alden",
    "session_id": "sess_123456",
    "timestamp": "2025-07-13T10:30:00Z",
    "relevant_memories": [
      {
        "id": "mem_789",
        "content": "User prefers 15-minute prep time before meetings",
        "slice_type": "procedural",
        "importance": 0.8,
        "created_at": "2025-07-12T14:22:00Z"
      }
    ],
    "personality_context": {
      "adaptability": 0.75,
      "conscientiousness": 0.85,
      "empathy": 0.80
    },
    "metadata": {
      "processing_time_ms": 342,
      "memory_search_time_ms": 45,
      "llm_generation_time_ms": 287,
      "memories_searched": 150,
      "memories_used": 3
    }
  }
}
```

#### Response Schema
```typescript
interface QueryResponse {
  response: string;                 // Agent's response to the query
  confidence: number;               // Confidence score (0.0-1.0)
  agent_id: string;                 // Agent that processed the query
  session_id: string;               // Session identifier
  timestamp: string;                // ISO 8601 timestamp
  relevant_memories: MemorySlice[]; // Memories used in response generation
  personality_context: {            // Agent's current personality state
    [trait: string]: number;        // Trait values (0.0-1.0)
  };
  metadata: {                       // Performance and debug information
    processing_time_ms: number;     // Total processing time
    memory_search_time_ms: number;  // Time spent searching memories
    llm_generation_time_ms: number; // Time spent in LLM generation
    memories_searched: number;      // Total memories searched
    memories_used: number;          // Memories included in context
  };
}
```

#### Error Responses
- **400 Bad Request**: Invalid query parameters
- **404 Not Found**: Agent not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server processing error

#### Example Usage
```bash
curl -X POST "http://localhost:8888/api/agents/alden/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sess_eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "query": "Help me plan my morning routine",
    "session_id": "sess_morning_123",
    "user_id": "user_001",
    "include_memory": true,
    "context": {
      "time_of_day": "morning",
      "user_mood": "energetic"
    }
  }'
```

### 3.2 Get Agent Status

Retrieve current status and capabilities of a specific agent.

#### Endpoint
```http
GET /api/agents/{agent_id}/status
```

#### Response
```json
{
  "success": true,
  "data": {
    "agent_id": "alden",
    "name": "Alden",
    "status": "active",
    "capabilities": [
      "conversation",
      "memory_management", 
      "task_planning",
      "personality_adaptation"
    ],
    "personality_traits": {
      "openness": 75,
      "conscientiousness": 86,
      "extraversion": 44,
      "agreeableness": 93,
      "emotional_stability": 77
    },
    "memory_stats": {
      "total_memories": 1247,
      "episodic": 423,
      "semantic": 651,
      "procedural": 173
    },
    "last_interaction": "2025-07-13T09:45:00Z",
    "version": "1.1.0"
  }
}
```

### 3.3 Update Agent Configuration

Update agent-specific configuration and personality settings.

#### Endpoint
```http
PATCH /api/agents/{agent_id}/config
```

#### Request Body
```json
{
  "personality_traits": {
    "conscientiousness": 90,
    "empathy": 85
  },
  "response_style": "supportive",
  "memory_preferences": {
    "importance_threshold": 0.3,
    "max_context_memories": 15
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "agent_id": "alden",
    "updated_fields": ["personality_traits", "memory_preferences"],
    "timestamp": "2025-07-13T10:30:00Z"
  }
}
```

### 3.4 List Available Agents

Get list of all available agents and their current status.

#### Endpoint
```http
GET /api/agents
```

#### Response
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "alden",
        "name": "Alden",
        "description": "Primary AI companion for productivity and executive function",
        "status": "active",
        "capabilities": ["conversation", "memory_management", "task_planning"]
      },
      {
        "id": "alice", 
        "name": "Alice",
        "description": "Behavioral analysis and communication coaching",
        "status": "active",
        "capabilities": ["behavioral_analysis", "communication_coaching"]
      }
    ],
    "total_agents": 2
  }
}
```

---

## 4. Memory API

### 4.1 Search Memories

Search for relevant memories using semantic similarity or filters.

#### Endpoint
```http
POST /api/memory/{agent_id}/search
```

#### Request Body
```json
{
  "query": "morning routine tasks",
  "user_id": "user_123",
  "filters": {
    "slice_types": ["procedural", "episodic"],
    "importance_min": 0.5,
    "date_range": {
      "start": "2025-07-01T00:00:00Z",
      "end": "2025-07-13T23:59:59Z"
    }
  },
  "limit": 10,
  "include_embeddings": false
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "memories": [
      {
        "id": "mem_456",
        "agent_id": "alden",
        "user_id": "user_123",
        "slice_type": "procedural",
        "content": "User prefers to start with coffee and 10 minutes of planning",
        "importance": 0.8,
        "created_at": "2025-07-10T08:15:00Z",
        "accessed_at": "2025-07-13T10:30:00Z",
        "access_count": 5,
        "tags": ["morning", "routine", "planning"],
        "similarity_score": 0.89
      }
    ],
    "total_found": 15,
    "search_time_ms": 45
  }
}
```

### 4.2 Create Memory

Create a new memory slice for an agent.

#### Endpoint
```http
POST /api/memory/{agent_id}
```

#### Request Body
```json
{
  "user_id": "user_123",
  "slice_type": "episodic",
  "content": "User completed project presentation successfully and received positive feedback",
  "importance": 0.9,
  "tags": ["achievement", "presentation", "positive"],
  "metadata": {
    "project_name": "Q3 Marketing Campaign",
    "feedback_score": 4.5,
    "audience_size": 25
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "memory": {
      "id": "mem_789",
      "agent_id": "alden",
      "user_id": "user_123",
      "slice_type": "episodic",
      "content": "User completed project presentation successfully and received positive feedback",
      "importance": 0.9,
      "tags": ["achievement", "presentation", "positive"],
      "created_at": "2025-07-13T10:30:00Z",
      "accessed_at": "2025-07-13T10:30:00Z",
      "access_count": 0
    }
  }
}
```

### 4.3 Update Memory

Update an existing memory slice.

#### Endpoint
```http
PUT /api/memory/{agent_id}/{memory_id}
```

#### Request Body
```json
{
  "importance": 0.95,
  "tags": ["achievement", "presentation", "positive", "milestone"],
  "metadata": {
    "follow_up_needed": true,
    "team_celebration": "planned"
  }
}
```

### 4.4 Delete Memory

Delete a memory slice.

#### Endpoint
```http
DELETE /api/memory/{agent_id}/{memory_id}
```

#### Response
```json
{
  "success": true,
  "data": {
    "deleted_memory_id": "mem_789",
    "timestamp": "2025-07-13T10:30:00Z"
  }
}
```

### 4.5 Memory Statistics

Get memory usage statistics for an agent.

#### Endpoint
```http
GET /api/memory/{agent_id}/stats
```

#### Response
```json
{
  "success": true,
  "data": {
    "total_memories": 1247,
    "by_type": {
      "episodic": 423,
      "semantic": 651, 
      "procedural": 173
    },
    "by_importance": {
      "high": 312,      // importance >= 0.8
      "medium": 623,    // importance 0.4-0.8
      "low": 312        // importance < 0.4
    },
    "storage_stats": {
      "total_size_mb": 15.7,
      "avg_memory_size_bytes": 1024,
      "oldest_memory": "2025-06-01T10:00:00Z",
      "newest_memory": "2025-07-13T10:29:00Z"
    },
    "usage_stats": {
      "most_accessed_count": 45,
      "avg_access_count": 3.2,
      "last_cleanup": "2025-07-12T02:00:00Z"
    }
  }
}
```

---

## 5. Sessions API

### 5.1 Create Session

Start a new conversation session.

#### Endpoint
```http
POST /api/sessions
```

#### Request Body
```json
{
  "user_id": "user_123",
  "context": {
    "session_type": "morning_planning",
    "location": "home_office",
    "mood": "focused"
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "sess_456",
      "user_id": "user_123", 
      "started_at": "2025-07-13T10:30:00Z",
      "context": {
        "session_type": "morning_planning",
        "location": "home_office",
        "mood": "focused"
      },
      "agents_participating": [],
      "message_count": 0
    }
  }
}
```

### 5.2 Get Session

Retrieve session details and conversation history.

#### Endpoint
```http
GET /api/sessions/{session_id}
```

#### Query Parameters
- **include_messages** (optional): Include conversation messages (default: true)
- **message_limit** (optional): Limit number of messages returned (default: 100)
- **message_offset** (optional): Offset for message pagination (default: 0)

#### Response
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "sess_456",
      "user_id": "user_123",
      "started_at": "2025-07-13T10:30:00Z", 
      "ended_at": null,
      "context": {
        "session_type": "morning_planning",
        "location": "home_office"
      },
      "agents_participating": ["alden"],
      "message_count": 5,
      "messages": [
        {
          "id": "msg_789",
          "session_id": "sess_456",
          "agent_id": "alden",
          "user_id": "user_123",
          "message_type": "user",
          "content": "Good morning Alden, help me plan my day",
          "metadata": {},
          "created_at": "2025-07-13T10:30:00Z"
        }
      ]
    },
    "pagination": {
      "total_messages": 5,
      "returned_messages": 5,
      "offset": 0,
      "has_more": false
    }
  }
}
```

### 5.3 End Session

End an active conversation session.

#### Endpoint
```http
POST /api/sessions/{session_id}/end
```

#### Response
```json
{
  "success": true,
  "data": {
    "session_id": "sess_456",
    "ended_at": "2025-07-13T11:45:00Z",
    "duration_minutes": 75,
    "total_messages": 23,
    "agents_used": ["alden", "alice"]
  }
}
```

### 5.4 List Sessions

Get list of user's conversation sessions.

#### Endpoint
```http
GET /api/sessions
```

#### Query Parameters
- **user_id** (required): User identifier
- **limit** (optional): Number of sessions to return (default: 50)
- **offset** (optional): Offset for pagination (default: 0)
- **status** (optional): Filter by session status (active, ended)

#### Response
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "sess_456",
        "user_id": "user_123",
        "started_at": "2025-07-13T10:30:00Z",
        "ended_at": "2025-07-13T11:45:00Z",
        "message_count": 23,
        "agents_participating": ["alden", "alice"],
        "context": {
          "session_type": "morning_planning"
        }
      }
    ],
    "total_sessions": 47,
    "pagination": {
      "limit": 50,
      "offset": 0,
      "has_more": false
    }
  }
}
```

---

## 6. System API

### 6.1 System Status

Get overall system health and status information.

#### Endpoint
```http
GET /api/status
```

#### Response
```json
{
  "success": true,
  "data": {
    "service": "hearthlink",
    "status": "healthy",
    "version": "1.1.0",
    "timestamp": "2025-07-13T10:30:00Z",
    "uptime_seconds": 86400,
    "components": {
      "database": {
        "status": "healthy",
        "type": "sqlite",
        "path": "./hearthlink_data/hearthlink.db",
        "size_mb": 125.7,
        "connections": 5
      },
      "llm_backend": {
        "status": "healthy", 
        "type": "ollama",
        "model": "llama2:7b-chat",
        "available_models": ["llama2:7b-chat", "codellama:7b"],
        "memory_usage_mb": 3072
      },
      "memory_service": {
        "status": "healthy",
        "total_memories": 1247,
        "search_avg_time_ms": 45
      },
      "voice_service": {
        "status": "available",
        "engines": ["web_speech_api", "python_speech"],
        "primary_engine": "web_speech_api"
      }
    },
    "performance": {
      "avg_response_time_ms": 342,
      "requests_per_minute": 23,
      "memory_usage_mb": 1024,
      "cpu_usage_percent": 15.2
    }
  }
}
```

### 6.2 System Configuration

Get or update system configuration.

#### Get Configuration
```http
GET /api/config
```

#### Update Configuration
```http
PATCH /api/config
```

#### Request Body (Update)
```json
{
  "llm": {
    "default_model": "llama2:7b-chat",
    "temperature": 0.7,
    "max_tokens": 512
  },
  "memory": {
    "importance_threshold": 0.3,
    "max_memories_per_search": 15
  },
  "voice": {
    "primary_engine": "web_speech_api",
    "language": "en-US"
  }
}
```

### 6.3 System Metrics

Get detailed system performance metrics.

#### Endpoint
```http
GET /api/metrics
```

#### Response
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-07-13T10:30:00Z",
    "uptime_seconds": 86400,
    "requests": {
      "total": 15247,
      "per_minute": 23,
      "by_endpoint": {
        "/api/agents/alden/query": 8934,
        "/api/memory/alden/search": 3421,
        "/api/sessions": 1892
      }
    },
    "performance": {
      "avg_response_time_ms": 342,
      "p95_response_time_ms": 1250,
      "p99_response_time_ms": 2100,
      "error_rate_percent": 0.15
    },
    "resources": {
      "memory_usage_mb": 1024,
      "memory_limit_mb": 2048,
      "cpu_usage_percent": 15.2,
      "disk_usage_gb": 2.1,
      "disk_available_gb": 47.9
    },
    "agents": {
      "alden": {
        "queries_processed": 8934,
        "avg_response_time_ms": 398,
        "memory_searches": 6742
      }
    }
  }
}
```

---

## 7. Security API

### 7.1 Create Authentication Session

Create a new authenticated session.

#### Endpoint
```http
POST /api/auth/session
```

#### Request Body
```json
{
  "user_id": "user_123",
  "device_id": "device_456",
  "client_info": {
    "user_agent": "Hearthlink/1.1.0 (Windows 10)",
    "ip_address": "127.0.0.1"
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "session_token": "sess_eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_at": "2025-07-13T18:30:00Z",
    "user_id": "user_123",
    "permissions": [
      "agents:query",
      "memory:read",
      "memory:write",
      "sessions:create"
    ]
  }
}
```

### 7.2 Validate Session

Validate an existing session token.

#### Endpoint
```http
GET /api/auth/session/validate
```

#### Headers
```http
Authorization: Bearer sess_eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Response
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": "user_123",
    "expires_at": "2025-07-13T18:30:00Z",
    "time_remaining_seconds": 28800
  }
}
```

### 7.3 Audit Logs

Retrieve security audit logs.

#### Endpoint
```http
GET /api/security/audit
```

#### Query Parameters
- **start_date** (optional): Start date for log entries (ISO 8601)
- **end_date** (optional): End date for log entries (ISO 8601)
- **action** (optional): Filter by action type
- **user_id** (optional): Filter by user
- **limit** (optional): Number of entries to return (default: 100)

#### Response
```json
{
  "success": true,
  "data": {
    "audit_entries": [
      {
        "id": "audit_789",
        "timestamp": "2025-07-13T10:30:00Z",
        "user_id": "user_123",
        "action": "memory_access",
        "resource_type": "memory_slice",
        "resource_id": "mem_456",
        "ip_address": "127.0.0.1",
        "user_agent": "Hearthlink/1.1.0",
        "success": true,
        "metadata": {
          "agent_id": "alden",
          "access_type": "read"
        }
      }
    ],
    "total_entries": 1247,
    "pagination": {
      "limit": 100,
      "offset": 0,
      "has_more": true
    }
  }
}
```

---

## 8. WebSocket API

### 8.1 Real-time Communication

Hearthlink supports WebSocket connections for real-time updates and voice processing.

#### Connection Endpoint
```
ws://localhost:8888/ws
```

#### Authentication
Send authentication message immediately after connection:
```json
{
  "type": "auth",
  "token": "sess_eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Message Types

##### Voice Data Streaming
```json
{
  "type": "voice_data",
  "data": {
    "audio_chunk": "base64_encoded_audio_data",
    "sample_rate": 16000,
    "format": "wav"
  }
}
```

##### Real-time Agent Response
```json
{
  "type": "agent_response_stream",
  "data": {
    "session_id": "sess_123",
    "agent_id": "alden",
    "partial_response": "I'm currently analyzing your request...",
    "is_complete": false
  }
}
```

##### System Notifications
```json
{
  "type": "system_notification",
  "data": {
    "level": "info",
    "title": "New Memory Created",
    "message": "Alden has created a new memory about your preferences",
    "timestamp": "2025-07-13T10:30:00Z"
  }
}
```

---

## 9. Error Handling

### 9.1 HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|--------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful request with no response body |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | Service temporarily unavailable |

### 9.2 Error Response Format

All error responses follow RFC 7807 Problem Details format:

```json
{
  "success": false,
  "errors": [
    {
      "type": "validation_error",
      "title": "Invalid Request Parameters", 
      "status": 400,
      "detail": "The 'query' field is required and cannot be empty",
      "instance": "/api/agents/alden/query",
      "validation_errors": [
        {
          "field": "query",
          "code": "required",
          "message": "This field is required"
        }
      ]
    }
  ],
  "meta": {
    "timestamp": "2025-07-13T10:30:00Z",
    "request_id": "req_123456",
    "api_version": "1.1.0"
  }
}
```

### 9.3 Common Error Types

#### Validation Errors
```json
{
  "type": "validation_error",
  "title": "Request Validation Failed",
  "status": 422,
  "detail": "One or more fields failed validation",
  "validation_errors": [
    {
      "field": "importance",
      "code": "range",
      "message": "Value must be between 0.0 and 1.0"
    }
  ]
}
```

#### Authentication Errors
```json
{
  "type": "authentication_error",
  "title": "Authentication Required",
  "status": 401,
  "detail": "Valid session token required for this operation"
}
```

#### Rate Limiting Errors
```json
{
  "type": "rate_limit_error",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "Too many requests. Try again in 60 seconds",
  "retry_after": 60
}
```

#### Agent Processing Errors
```json
{
  "type": "agent_processing_error",
  "title": "Agent Processing Failed",
  "status": 500,
  "detail": "The AI agent encountered an error while processing your request",
  "agent_id": "alden",
  "error_code": "llm_timeout"
}
```

---

## 10. Data Models

### 10.1 Core Models

#### User Model
```typescript
interface User {
  id: string;
  username?: string;
  display_name?: string;
  preferences: {
    theme: 'dark' | 'light';
    language: string;
    voice_settings: {
      enabled: boolean;
      primary_engine: string;
      language: string;
    };
  };
  created_at: string;
  last_active: string;
}
```

#### Agent Model
```typescript
interface Agent {
  id: string;
  name: string;
  type: 'alden' | 'alice' | 'mimic' | 'sentry';
  description: string;
  status: 'active' | 'inactive' | 'maintenance';
  capabilities: string[];
  personality_traits?: {
    [trait: string]: number; // 0-100
  };
  config: {
    llm_model?: string;
    temperature?: number;
    max_tokens?: number;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}
```

#### Memory Slice Model
```typescript
interface MemorySlice {
  id: string;
  agent_id: string;
  user_id: string;
  slice_type: 'episodic' | 'semantic' | 'procedural';
  content: string;
  importance: number; // 0.0-1.0
  tags?: string[];
  metadata?: {
    [key: string]: any;
  };
  created_at: string;
  accessed_at: string;
  access_count: number;
}
```

#### Session Model
```typescript
interface Session {
  id: string;
  user_id: string;
  started_at: string;
  ended_at?: string;
  context: {
    session_type?: string;
    location?: string;
    mood?: string;
    [key: string]: any;
  };
  agents_participating: string[];
  message_count: number;
}
```

#### Message Model
```typescript
interface Message {
  id: string;
  session_id: string;
  agent_id: string;
  user_id: string;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  metadata: {
    memories_referenced?: string[];
    processing_time_ms?: number;
    confidence?: number;
    [key: string]: any;
  };
  created_at: string;
}
```

### 10.2 Request/Response Models

#### Query Models
```typescript
interface QueryRequest {
  query: string;
  session_id: string;
  user_id: string;
  include_memory?: boolean;
  max_memories?: number;
  context?: {
    previous_queries?: string[];
    user_mood?: string;
    time_of_day?: string;
    location?: string;
    urgency?: 'low' | 'medium' | 'high';
  };
}

interface QueryResponse {
  response: string;
  confidence: number;
  agent_id: string;
  session_id: string;
  timestamp: string;
  relevant_memories: MemorySlice[];
  personality_context: {
    [trait: string]: number;
  };
  metadata: {
    processing_time_ms: number;
    memory_search_time_ms: number;
    llm_generation_time_ms: number;
    memories_searched: number;
    memories_used: number;
  };
}
```

#### Memory Models
```typescript
interface MemorySearchRequest {
  query: string;
  user_id: string;
  filters?: {
    slice_types?: string[];
    importance_min?: number;
    importance_max?: number;
    date_range?: {
      start: string;
      end: string;
    };
    tags?: string[];
  };
  limit?: number;
  include_embeddings?: boolean;
}

interface MemorySearchResponse {
  memories: MemorySlice[];
  total_found: number;
  search_time_ms: number;
}

interface MemoryCreateRequest {
  user_id: string;
  slice_type: 'episodic' | 'semantic' | 'procedural';
  content: string;
  importance?: number;
  tags?: string[];
  metadata?: {
    [key: string]: any;
  };
}
```

---

## 11. SDK Examples

### 11.1 JavaScript/TypeScript SDK

#### Basic Usage
```typescript
import { HearthlinkAPI } from '@hearthlink/api-client';

const api = new HearthlinkAPI({
  baseURL: 'http://localhost:8888',
  apiKey: 'your-session-token'
});

// Query an agent
const response = await api.agents.query('alden', {
  query: 'Help me plan my morning routine',
  session_id: 'sess_123',
  user_id: 'user_456'
});

console.log(response.data.response);

// Search memories
const memories = await api.memory.search('alden', {
  query: 'morning routine',
  user_id: 'user_456',
  limit: 5
});

// Create a new session
const session = await api.sessions.create({
  user_id: 'user_456',
  context: { session_type: 'daily_planning' }
});
```

#### WebSocket Integration
```typescript
import { HearthlinkWebSocket } from '@hearthlink/api-client';

const ws = new HearthlinkWebSocket('ws://localhost:8888/ws');

await ws.authenticate('your-session-token');

// Listen for real-time agent responses
ws.on('agent_response_stream', (data) => {
  console.log('Partial response:', data.partial_response);
  if (data.is_complete) {
    console.log('Response complete');
  }
});

// Send voice data
ws.sendVoiceData(audioBuffer);
```

### 11.2 Python SDK

#### Basic Usage
```python
from hearthlink_api import HearthlinkAPI

api = HearthlinkAPI(
    base_url='http://localhost:8888',
    session_token='your-session-token'
)

# Query an agent
response = api.agents.query(
    agent_id='alden',
    query='Help me organize my tasks for today',
    session_id='sess_123',
    user_id='user_456'
)

print(response.response)

# Search memories
memories = api.memory.search(
    agent_id='alden',
    query='task organization',
    user_id='user_456',
    filters={'slice_types': ['procedural']},
    limit=10
)

for memory in memories:
    print(f"Memory: {memory.content} (importance: {memory.importance})")

# Create memory
new_memory = api.memory.create(
    agent_id='alden',
    user_id='user_456',
    slice_type='episodic',
    content='User successfully completed quarterly review',
    importance=0.8,
    tags=['achievement', 'quarterly', 'review']
)
```

#### Async Usage
```python
import asyncio
from hearthlink_api import AsyncHearthlinkAPI

async def main():
    api = AsyncHearthlinkAPI(
        base_url='http://localhost:8888',
        session_token='your-session-token'
    )
    
    # Concurrent operations
    tasks = [
        api.agents.query('alden', query='What are my priorities?', 
                        session_id='sess_123', user_id='user_456'),
        api.memory.search('alden', query='priorities', user_id='user_456'),
        api.sessions.get('sess_123')
    ]
    
    response, memories, session = await asyncio.gather(*tasks)
    
    print(f"Agent response: {response.response}")
    print(f"Found {len(memories)} relevant memories")
    print(f"Session has {session.message_count} messages")

asyncio.run(main())
```

---

## 12. Testing

### 12.1 API Testing Examples

#### Unit Testing with pytest
```python
import pytest
from hearthlink_api.tests import HearthlinkAPITestClient

@pytest.fixture
def api_client():
    return HearthlinkAPITestClient()

def test_agent_query(api_client):
    response = api_client.post('/api/agents/alden/query', json={
        'query': 'Test query',
        'session_id': 'test_session',
        'user_id': 'test_user'
    })
    
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert 'response' in response.json()['data']

def test_memory_creation(api_client):
    response = api_client.post('/api/memory/alden', json={
        'user_id': 'test_user',
        'slice_type': 'episodic',
        'content': 'Test memory content',
        'importance': 0.7
    })
    
    assert response.status_code == 201
    memory_data = response.json()['data']['memory']
    assert memory_data['content'] == 'Test memory content'
    assert memory_data['importance'] == 0.7

def test_error_handling(api_client):
    response = api_client.post('/api/agents/alden/query', json={
        'query': '',  # Empty query should fail
        'session_id': 'test_session'
    })
    
    assert response.status_code == 400
    assert response.json()['success'] is False
    assert 'validation_error' in response.json()['errors'][0]['type']
```

#### Integration Testing
```python
import pytest
from hearthlink_api import HearthlinkAPI

@pytest.mark.integration
def test_full_conversation_flow():
    api = HearthlinkAPI(base_url='http://localhost:8888')
    
    # Create session
    session = api.sessions.create(
        user_id='test_user',
        context={'test': True}
    )
    
    # Query agent
    response = api.agents.query(
        'alden',
        query='Remember that I like coffee in the morning',
        session_id=session.id,
        user_id='test_user'
    )
    
    assert response.confidence > 0.5
    
    # Search for created memory
    memories = api.memory.search(
        'alden',
        query='coffee morning',
        user_id='test_user'
    )
    
    assert len(memories) > 0
    assert 'coffee' in memories[0].content.lower()
    
    # End session
    api.sessions.end(session.id)
```

### 12.2 Performance Testing

#### Load Testing with Locust
```python
from locust import HttpUser, task, between

class HearthlinkAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Create session for testing
        response = self.client.post('/api/sessions', json={
            'user_id': f'test_user_{self.environment.runner.user_count}',
            'context': {'test': True}
        })
        self.session_id = response.json()['data']['session']['id']
    
    @task(3)
    def query_alden(self):
        self.client.post('/api/agents/alden/query', json={
            'query': 'What should I focus on today?',
            'session_id': self.session_id,
            'user_id': f'test_user_{self.environment.runner.user_count}'
        })
    
    @task(1)
    def search_memories(self):
        self.client.post('/api/memory/alden/search', json={
            'query': 'focus priorities',
            'user_id': f'test_user_{self.environment.runner.user_count}',
            'limit': 5
        })
    
    @task(1)
    def check_status(self):
        self.client.get('/api/status')
```

---

## 13. Appendices

### Appendix A: OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- **Development**: `http://localhost:8888/docs`
- **JSON Schema**: `http://localhost:8888/openapi.json`

### Appendix B: Rate Limiting Details

#### Default Limits
- **Agent Queries**: 60 per minute per user
- **Memory Operations**: 120 per minute per user  
- **Search Operations**: 100 per minute per user
- **Session Operations**: 30 per minute per user
- **System Operations**: 10 per minute per user

#### Custom Rate Limits
Rate limits can be customized per user or API key through configuration.

### Appendix C: Webhook Integration

Hearthlink supports webhook notifications for external integrations:

```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/hearthlink-webhook",
  "events": ["memory_created", "session_ended"],
  "secret": "webhook_signing_secret"
}
```

### Appendix D: API Versioning

Hearthlink API uses semantic versioning with backward compatibility:
- **Major versions**: Breaking changes (v1.x.x → v2.x.x)
- **Minor versions**: New features, backward compatible (v1.1.x → v1.2.x)
- **Patch versions**: Bug fixes, backward compatible (v1.1.1 → v1.1.2)

Version can be specified in headers:
```http
API-Version: 1.1.0
```

---

**Document Control**
- **Version**: 1.0.0
- **Classification**: Internal Use
- **Review Cycle**: Monthly during active development
- **Next Review**: August 13, 2025
- **Owner**: Backend Team
- **Approvers**: Engineering Leadership, API Working Group

---

*This API Specification Document serves as the comprehensive reference for all Hearthlink API interfaces. All client integrations should conform to the specifications defined herein.*