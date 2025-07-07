# API Implementation Guide - Hearthlink

**Module:** `feature/api-layer`  
**Implementation:** `src/api/alden_api.py`, `src/api/mimic_api.py`  
**Status:** ✅ Complete Implementation  
**Documentation Status:** ✅ Complete  

---

## Overview

The Hearthlink API layer provides RESTful endpoints for programmatic access to Alden and Mimic persona functionality. This module implements a secure, scalable API that enables external applications to interact with Hearthlink's AI companions while maintaining the system's privacy-first and ethical design principles.

## Architecture

### Core Components

1. **Alden API** (`src/api/alden_api.py`)
   - Alden persona endpoints
   - Evolutionary companion interactions
   - Context-aware responses

2. **Mimic API** (`src/api/mimic_api.py`)
   - Mimic persona endpoints
   - Dynamic persona interactions
   - Plugin system integration

3. **API Gateway**
   - Request routing and validation
   - Authentication and authorization
   - Rate limiting and throttling
   - Error handling and logging

## API Endpoints

### Alden API Endpoints

#### 1. Chat Endpoints

```http
POST /api/v1/alden/chat
Content-Type: application/json

{
  "message": "Hello Alden, how are you today?",
  "context": {
    "session_id": "session_123",
    "user_id": "user_456",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "options": {
    "include_memory": true,
    "response_format": "text"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "response": "Hello! I'm doing well, thank you for asking. I've been analyzing our recent conversations and I notice you've been working on some interesting projects. How can I help you today?",
    "context": {
      "session_id": "session_123",
      "conversation_id": "conv_789",
      "timestamp": "2024-01-01T00:00:01Z"
    },
    "insights": [
      {
        "type": "behavioral",
        "content": "User shows consistent analytical thinking patterns",
        "confidence": 0.85
      }
    ]
  }
}
```

#### 2. Session Management

```http
POST /api/v1/alden/sessions
{
  "name": "Project Planning Session",
  "description": "Planning phase for new project",
  "participants": ["user_456"],
  "settings": {
    "memory_sharing": true,
    "insight_generation": true
  }
}
```

```http
GET /api/v1/alden/sessions/{session_id}
```

```http
PUT /api/v1/alden/sessions/{session_id}
{
  "name": "Updated Session Name",
  "settings": {
    "memory_sharing": false
  }
}
```

```http
DELETE /api/v1/alden/sessions/{session_id}
```

#### 3. Memory Operations

```http
GET /api/v1/alden/memory/personal
{
  "query": "project insights",
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "categories": ["technical", "planning"]
  }
}
```

```http
GET /api/v1/alden/memory/communal
{
  "query": "team discussions",
  "participants": ["user_456", "user_789"]
}
```

```http
POST /api/v1/alden/memory/store
{
  "content": "Important project milestone achieved",
  "category": "milestone",
  "tags": ["project", "success"],
  "visibility": "personal"
}
```

### Mimic API Endpoints

#### 1. Persona Management

```http
POST /api/v1/mimic/personas
{
  "name": "Technical Advisor",
  "description": "Expert technical consultant",
  "traits": {
    "expertise": ["software_architecture", "system_design"],
    "communication_style": "analytical",
    "personality": "detail_oriented"
  },
  "capabilities": ["code_review", "architecture_analysis", "best_practices"]
}
```

```http
GET /api/v1/mimic/personas/{persona_id}
```

```http
PUT /api/v1/mimic/personas/{persona_id}
{
  "traits": {
    "expertise": ["software_architecture", "system_design", "security"]
  }
}
```

```http
DELETE /api/v1/mimic/personas/{persona_id}
```

#### 2. Plugin Management

```http
POST /api/v1/mimic/plugins/install
{
  "plugin_id": "code_analyzer",
  "version": "1.2.0",
  "configuration": {
    "analysis_depth": "detailed",
    "security_scan": true
  }
}
```

```http
GET /api/v1/mimic/plugins/{plugin_id}/status
```

```http
POST /api/v1/mimic/plugins/{plugin_id}/execute
{
  "action": "analyze_code",
  "parameters": {
    "code": "function example() { return true; }",
    "language": "javascript"
  }
}
```

## Authentication & Security

### API Key Authentication

```http
GET /api/v1/alden/chat
Authorization: Bearer api_key_123456789
Content-Type: application/json
```

### Request Signing

```python
import hmac
import hashlib
import time

def sign_request(api_key, api_secret, method, path, body, timestamp):
    message = f"{method}{path}{body}{timestamp}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "message",
      "issue": "Message cannot be empty"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Request/Response Validation

### Request Validation

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

class SessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    settings: Optional[Dict[str, Any]] = None
```

### Response Validation

```python
class ChatResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: str
    request_id: str

class ErrorResponse(BaseModel):
    status: str
    error: Dict[str, Any]
```

## Integration Examples

### Python Client

```python
import requests
import json

class HearthlinkAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def chat_with_alden(self, message, context=None):
        url = f"{self.base_url}/api/v1/alden/chat"
        data = {
            "message": message,
            "context": context or {}
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def create_session(self, name, description=None):
        url = f"{self.base_url}/api/v1/alden/sessions"
        data = {
            "name": name,
            "description": description
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Usage
api = HearthlinkAPI("http://localhost:8000", "your_api_key")
response = api.chat_with_alden("Hello Alden!")
print(response['data']['response'])
```

### JavaScript Client

```javascript
class HearthlinkAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async chatWithAlden(message, context = {}) {
        const url = `${this.baseUrl}/api/v1/alden/chat`;
        const data = {
            message,
            context
        };
        
        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return response.json();
    }
    
    async createSession(name, description = null) {
        const url = `${this.baseUrl}/api/v1/alden/sessions`;
        const data = {
            name,
            description
        };
        
        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return response.json();
    }
}

// Usage
const api = new HearthlinkAPI('http://localhost:8000', 'your_api_key');
const response = await api.chatWithAlden('Hello Alden!');
console.log(response.data.response);
```

## Performance & Scalability

### Caching Strategy

```python
from functools import lru_cache
import redis

class APICache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def cache_response(self, key, response, ttl=300):
        self.redis_client.setex(key, ttl, json.dumps(response))
    
    def get_cached_response(self, key):
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
```

### Load Balancing

```python
# Multiple API instances behind load balancer
api_instances = [
    "http://api1.hearthlink.local:8000",
    "http://api2.hearthlink.local:8000",
    "http://api3.hearthlink.local:8000"
]

def get_api_instance():
    # Round-robin or health-check based selection
    return random.choice(api_instances)
```

## Monitoring & Logging

### Request Logging

```python
import logging
import time

def log_request(request, response, duration):
    log_entry = {
        "timestamp": time.time(),
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "duration": duration,
        "user_id": request.headers.get("X-User-ID"),
        "request_id": request.headers.get("X-Request-ID")
    }
    
    logging.info(f"API Request: {json.dumps(log_entry)}")
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Metrics
request_count = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])

def track_metrics(endpoint, method, duration):
    request_count.labels(endpoint=endpoint, method=method).inc()
    request_duration.labels(endpoint=endpoint).observe(duration)
```

## Testing

### API Testing

```python
import pytest
from fastapi.testclient import TestClient
from src.api.alden_api import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/api/v1/alden/chat", json={
        "message": "Hello Alden!"
    })
    
    assert response.status_code == 200
    assert "response" in response.json()["data"]

def test_session_creation():
    response = client.post("/api/v1/alden/sessions", json={
        "name": "Test Session"
    })
    
    assert response.status_code == 201
    assert "session_id" in response.json()["data"]
```

### Load Testing

```python
import locust

class HearthlinkAPILoadTest(locust.HttpUser):
    @locust.task
    def chat_with_alden(self):
        self.client.post("/api/v1/alden/chat", json={
            "message": "Test message"
        })
    
    @locust.task
    def create_session(self):
        self.client.post("/api/v1/alden/sessions", json={
            "name": "Load Test Session"
        })
```

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000

CMD ["uvicorn", "src.api.alden_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

```bash
# API Configuration
HEARTHLINK_API_HOST=0.0.0.0
HEARTHLINK_API_PORT=8000
HEARTHLINK_API_WORKERS=4

# Security Configuration
HEARTHLINK_API_SECRET_KEY=your_secret_key
HEARTHLINK_API_CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
HEARTHLINK_API_RATE_LIMIT=100
HEARTHLINK_API_RATE_LIMIT_WINDOW=3600

# Logging
HEARTHLINK_API_LOG_LEVEL=INFO
HEARTHLINK_API_LOG_FORMAT=json
```

## Future Enhancements

### Planned Features

1. **GraphQL Support**
   - GraphQL endpoint for flexible queries
   - Schema introspection
   - Real-time subscriptions

2. **WebSocket Support**
   - Real-time chat functionality
   - Live session updates
   - Streaming responses

3. **API Versioning**
   - Semantic versioning
   - Backward compatibility
   - Migration tools

4. **Advanced Analytics**
   - Usage analytics
   - Performance metrics
   - User behavior insights

---

**Documentation Version:** 1.0  
**Last Updated:** 2025-07-07  
**Next Review:** Phase 5 completion 