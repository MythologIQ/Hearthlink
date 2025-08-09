# Hearthlink Cloudflare Workers API

A secure, globally distributed REST API for the Hearthlink AI orchestration platform, built on Cloudflare Workers for edge computing capabilities.

## 🚀 **Features**

- **🌍 Global Distribution**: Deploy to 300+ Cloudflare edge locations worldwide
- **🔒 Security First**: JWT authentication, rate limiting, and comprehensive security headers
- **⚡ High Performance**: Sub-100ms response times with intelligent caching
- **🔄 Auto-scaling**: Serverless architecture that scales from 0 to millions of requests
- **📊 Real-time Monitoring**: Built-in analytics and observability
- **🛡️ DDoS Protection**: Cloudflare's enterprise-grade protection included

## 📋 **API Endpoints**

### **Authentication**
```
POST /api/v1/auth/login      - User login
POST /api/v1/auth/logout     - User logout  
POST /api/v1/auth/refresh    - Refresh access token
GET  /api/v1/auth/validate   - Validate current token
```

### **Agent Management**
```
GET    /api/v1/agents                  - List all agents
GET    /api/v1/agents/{id}             - Get agent details
POST   /api/v1/agents/{id}/query       - Query specific agent
PATCH  /api/v1/agents/{id}/config      - Update agent config
GET    /api/v1/agents/{id}/status      - Get agent status
POST   /api/v1/agents/{id}/reset       - Reset agent state
```

### **Memory Management**
```
POST   /api/v1/memory/{agentId}/search    - Search memories
POST   /api/v1/memory/{agentId}           - Create memory
GET    /api/v1/memory/{agentId}/{id}      - Get specific memory
PUT    /api/v1/memory/{agentId}/{id}      - Update memory
DELETE /api/v1/memory/{agentId}/{id}      - Delete memory
GET    /api/v1/memory/{agentId}/stats     - Memory statistics
```

### **Session Management**
```
POST   /api/v1/sessions           - Create new session
GET    /api/v1/sessions           - List sessions
GET    /api/v1/sessions/{id}      - Get session details
PATCH  /api/v1/sessions/{id}      - Update session
DELETE /api/v1/sessions/{id}      - Delete session
```

### **System Operations**
```
GET    /api/v1/health             - Health check (no auth)
GET    /api/v1/status             - System status (no auth)
GET    /api/v1/system/metrics     - System metrics (admin)
GET    /api/v1/system/config      - System configuration (admin)
PATCH  /api/v1/system/config      - Update configuration (admin)
```

## 🔧 **Local Development**

### **Prerequisites**
- Node.js 18+ 
- npm or yarn
- Cloudflare account
- Wrangler CLI

### **Setup**
```bash
# Navigate to workers directory
cd workers

# Install dependencies
npm install

# Install Wrangler CLI globally
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create KV namespaces
npm run kv:create

# Set environment secrets
wrangler secret put JWT_SECRET
# Enter a secure random string (32+ characters)

# Start development server
npm run dev
```

### **Environment Variables**
```bash
# Required secrets (set via wrangler secret put)
JWT_SECRET=your-super-secure-jwt-secret-key-here

# Environment-specific variables (in wrangler.toml)
ENVIRONMENT=development
API_VERSION=v1
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=*
DEBUG_MODE=true
```

## 🚀 **Deployment**

### **Development Environment**
```bash
npm run deploy
```

### **Staging Environment**  
```bash
npm run deploy:staging
```

### **Production Environment**
```bash
npm run deploy:production
```

## 🔒 **Authentication & Security**

### **JWT Authentication**
The API uses JWT tokens for authentication:

```javascript
// Login to get tokens
POST /api/v1/auth/login
{
  "email": "user@hearthlink.ai",
  "password": "your-password"
}

// Use access token in subsequent requests
Authorization: Bearer <access_token>
```

### **Rate Limiting**
- **Default**: 100 requests per minute per client
- **Login**: 10 requests per minute (stricter)
- **File Upload**: 10 requests per minute
- **Health Checks**: 1000 requests per minute

### **Security Headers**
All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 📊 **Monitoring & Observability**

### **Built-in Analytics**
- Request volume and response times
- Error rates and status codes
- Geographic distribution of requests
- Rate limiting metrics

### **Custom Metrics**
```bash
# View real-time logs
npm run tail

# Get deployment info
wrangler deployments list

# View KV storage usage
npm run kv:list
```

### **Health Monitoring**
```bash
# Health check endpoint
curl https://your-worker.your-domain.workers.dev/api/v1/health

# Detailed status
curl https://your-worker.your-domain.workers.dev/api/v1/status
```

## 🗄️ **Data Storage**

### **KV Namespaces**
- **SESSIONS**: User session data
- **CACHE**: Response caching
- **RATE_LIMITS**: Rate limiting counters

### **R2 Storage** (Optional)
- **FILES**: File upload storage
- Automatically configured if enabled

### **Durable Objects**
- **SessionManager**: Stateful session management
- **WebSocketHandler**: Real-time connections

## 🔧 **Configuration**

### **Custom Domain Setup**
1. Add domain to Cloudflare
2. Update `wrangler.toml`:
```toml
routes = [
  "api.hearthlink.ai/*",
  "api-staging.hearthlink.ai/*"
]
```

### **Environment-Specific Config**
```toml
[env.production.vars]
ENVIRONMENT = "production"
RATE_LIMIT_PER_MINUTE = 500
CORS_ORIGINS = "https://hearthlink.ai,https://app.hearthlink.ai"
DEBUG_MODE = false
```

## 🧪 **Testing**

### **Unit Tests**
```bash
npm test
```

### **Integration Tests**
```bash
# Test against local development server
npm run dev &
npm run test:integration
```

### **Load Testing**
```bash
# Use your preferred load testing tool
# Example with curl:
for i in {1..100}; do
  curl -X POST https://your-api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}' &
done
```

## 📚 **API Documentation**

### **Response Format**
All API responses follow a consistent format:

```javascript
// Success Response
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-07-14T12:00:00.000Z"
}

// Error Response  
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Validation failed",
    "timestamp": "2024-07-14T12:00:00.000Z",
    "details": { ... }
  }
}
```

### **Rate Limit Headers**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642608000000
```

## 🛠️ **Development Tools**

### **Useful Commands**
```bash
# View logs in real-time
wrangler tail --format=pretty

# Manage secrets
wrangler secret put SECRET_NAME
wrangler secret list
wrangler secret delete SECRET_NAME

# KV operations
wrangler kv:namespace create NAMESPACE_NAME
wrangler kv:key put --binding=SESSIONS "key" "value"
wrangler kv:key get --binding=SESSIONS "key"

# Deployment management
wrangler deployments list
wrangler deployments view DEPLOYMENT_ID
```

### **Debugging**
Enable debug mode for detailed error responses:
```toml
[env.development.vars]
DEBUG_MODE = true
```

## 🔄 **Integration with Hearthlink**

### **Backend Integration**
The Workers API acts as a proxy/gateway to the main Hearthlink backend:

```javascript
// Example agent query flow:
1. Client → Workers API
2. Workers API validates auth & rate limits
3. Workers API → Hearthlink Backend
4. Hearthlink Backend processes query  
5. Workers API ← Response from backend
6. Client ← Cached/processed response
```

### **Real-time Features**
WebSocket connections for real-time updates:
```javascript
const ws = new WebSocket('wss://api.hearthlink.ai/api/v1/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

## 📈 **Performance Optimization**

### **Caching Strategy**
- **Static responses**: 1 hour cache
- **Agent data**: 5 minute cache  
- **User sessions**: No cache
- **Health checks**: 30 second cache

### **Geographic Distribution**
Responses served from the nearest edge location:
- **North America**: Multiple data centers
- **Europe**: Frankfurt, London, Amsterdam
- **Asia-Pacific**: Singapore, Tokyo, Sydney
- **Global**: 300+ locations worldwide

## 🚨 **Troubleshooting**

### **Common Issues**

**Rate Limiting Errors**
```bash
# Check rate limit status
curl -H "Authorization: Bearer <token>" \
  https://your-api/api/v1/status
```

**Authentication Failures**
```bash
# Verify JWT secret is set
wrangler secret list

# Test token validation
curl -H "Authorization: Bearer <token>" \
  https://your-api/api/v1/auth/validate
```

**CORS Issues**
```bash
# Check CORS configuration in wrangler.toml
# Ensure origins are properly configured
```

### **Support**
- **Documentation**: [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- **Community**: [Cloudflare Discord](https://discord.cloudflare.com)
- **Issues**: Report bugs in the main Hearthlink repository

---

**🎉 Your secure, globally distributed Hearthlink API is ready to serve millions of requests worldwide!**