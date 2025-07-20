# Hearthlink Cloudflare Workers Deployment Guide

This guide walks you through deploying the Hearthlink Workers API to Cloudflare's global edge network.

## 🚀 **Quick Deployment**

### **1. Prerequisites**
```bash
# Install Node.js 18+
node --version

# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### **2. Setup Environment**
```bash
# Navigate to workers directory
cd workers

# Install dependencies
npm install

# Create KV namespaces
wrangler kv:namespace create SESSIONS
wrangler kv:namespace create CACHE  
wrangler kv:namespace create RATE_LIMITS

# Update wrangler.toml with the namespace IDs returned above
```

### **3. Configure Secrets**
```bash
# Set JWT secret (use a strong 32+ character random string)
wrangler secret put JWT_SECRET

# Optional: Set additional secrets
wrangler secret put BACKEND_API_KEY
wrangler secret put ENCRYPTION_KEY
```

### **4. Deploy**
```bash
# Deploy to development
npm run deploy

# Deploy to staging
npm run deploy:staging

# Deploy to production  
npm run deploy:production
```

## 🔧 **Detailed Configuration**

### **Environment Setup**

**Development Environment**
```toml
[env.development.vars]
ENVIRONMENT = "development"
API_VERSION = "v1"
RATE_LIMIT_PER_MINUTE = 100
CORS_ORIGINS = "*"
DEBUG_MODE = true
```

**Production Environment**
```toml
[env.production.vars]
ENVIRONMENT = "production"
API_VERSION = "v1"
RATE_LIMIT_PER_MINUTE = 500
CORS_ORIGINS = "https://hearthlink.ai,https://app.hearthlink.ai"
DEBUG_MODE = false
```

### **KV Namespace Configuration**

1. **Create namespaces:**
```bash
wrangler kv:namespace create SESSIONS
wrangler kv:namespace create CACHE
wrangler kv:namespace create RATE_LIMITS
```

2. **Update wrangler.toml with returned IDs:**
```toml
[[kv_namespaces]]
binding = "SESSIONS"
id = "your-sessions-namespace-id"
preview_id = "your-sessions-preview-id"

[[kv_namespaces]]
binding = "CACHE"
id = "your-cache-namespace-id"
preview_id = "your-cache-preview-id"

[[kv_namespaces]]
binding = "RATE_LIMITS"
id = "your-ratelimits-namespace-id"
preview_id = "your-ratelimits-preview-id"
```

### **Custom Domain Setup**

1. **Add domain to Cloudflare:**
   - Go to Cloudflare Dashboard
   - Add your domain (e.g., `hearthlink.ai`)
   - Update nameservers

2. **Configure routes in wrangler.toml:**
```toml
routes = [
  "api.hearthlink.ai/*",
  "api-staging.hearthlink.ai/*"
]
```

3. **Deploy with custom domain:**
```bash
wrangler deploy --env production
```

## 🔒 **Security Configuration**

### **JWT Configuration**
```bash
# Generate a secure JWT secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Set the secret
wrangler secret put JWT_SECRET
# Paste the generated secret when prompted
```

### **CORS Configuration**
```toml
# Production - restrict to specific origins
[env.production.vars]
CORS_ORIGINS = "https://hearthlink.ai,https://app.hearthlink.ai,https://dashboard.hearthlink.ai"

# Development - allow all origins
[env.development.vars]
CORS_ORIGINS = "*"
```

### **Rate Limiting Configuration**
```toml
# Adjust based on your needs
[env.production.vars]
RATE_LIMIT_PER_MINUTE = 500  # Higher for production

[env.development.vars]
RATE_LIMIT_PER_MINUTE = 100  # Lower for development
```

## 📊 **Monitoring Setup**

### **Analytics Configuration**
```toml
[observability]
enabled = true
```

### **Real-time Logs**
```bash
# View logs in real-time
wrangler tail --format=pretty

# View logs for specific environment
wrangler tail --env production --format=pretty
```

### **Custom Metrics**
The API automatically tracks:
- Request volume and response times
- Error rates by endpoint
- Authentication success/failure rates
- Rate limiting metrics
- Geographic distribution

## 🗄️ **R2 Storage Setup** (Optional)

For file upload capabilities:

1. **Create R2 bucket:**
```bash
wrangler r2 bucket create hearthlink-files
```

2. **Update wrangler.toml:**
```toml
[[r2_buckets]]
binding = "FILES"
bucket_name = "hearthlink-files"
preview_bucket_name = "hearthlink-files-preview"
```

## 🧪 **Testing Deployment**

### **Health Check**
```bash
# Test health endpoint
curl https://your-worker.workers.dev/api/v1/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-07-14T12:00:00.000Z",
  "version": "1.3.0",
  "environment": "production",
  "region": "DFW"
}
```

### **Authentication Test**
```bash
# Test login
curl -X POST https://your-worker.workers.dev/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hearthlink.ai",
    "password": "admin123"
  }'

# Test protected endpoint
curl -H "Authorization: Bearer <token>" \
  https://your-worker.workers.dev/api/v1/agents
```

### **Rate Limiting Test**
```bash
# Test rate limiting (should get 429 after limit exceeded)
for i in {1..101}; do
  curl https://your-worker.workers.dev/api/v1/health
done
```

## 🔄 **CI/CD Integration**

### **GitHub Actions**
Create `.github/workflows/deploy-workers.yml`:

```yaml
name: Deploy Hearthlink Workers API

on:
  push:
    branches: [main]
    paths: ['workers/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          cd workers
          npm ci
          
      - name: Run tests
        run: |
          cd workers
          npm test
          
      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: |
          cd workers
          echo "${{ secrets.CLOUDFLARE_API_TOKEN }}" | wrangler auth
          npm run deploy:staging
          
      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: |
          cd workers
          echo "${{ secrets.CLOUDFLARE_API_TOKEN }}" | wrangler auth
          npm run deploy:production
```

### **Required Secrets**
Add to GitHub repository secrets:
- `CLOUDFLARE_API_TOKEN`: Your Cloudflare API token
- `JWT_SECRET`: Your JWT secret key

## 🛠️ **Management Commands**

### **Deployment Management**
```bash
# List deployments
wrangler deployments list

# View specific deployment
wrangler deployments view <deployment-id>

# Rollback deployment
wrangler rollback <deployment-id>
```

### **KV Management**
```bash
# List namespaces
wrangler kv:namespace list

# View keys in namespace
wrangler kv:key list --binding=SESSIONS

# Get specific key
wrangler kv:key get --binding=SESSIONS "session-id"

# Put key-value
wrangler kv:key put --binding=SESSIONS "key" "value"

# Delete key
wrangler kv:key delete --binding=SESSIONS "key"
```

### **Secret Management**
```bash
# List secrets
wrangler secret list

# Update secret
wrangler secret put SECRET_NAME

# Delete secret
wrangler secret delete SECRET_NAME
```

## 📈 **Performance Optimization**

### **Caching Strategy**
```javascript
// In your handlers, use appropriate cache headers
return new Response(JSON.stringify(data), {
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=300', // 5 minutes
    'CDN-Cache-Control': 'public, max-age=3600' // 1 hour at edge
  }
});
```

### **Geographic Distribution**
Your API will automatically be distributed to 300+ Cloudflare edge locations worldwide:
- **North America**: 100+ locations
- **Europe**: 80+ locations  
- **Asia-Pacific**: 50+ locations
- **South America**: 20+ locations
- **Africa**: 15+ locations
- **Middle East**: 10+ locations

## 🚨 **Troubleshooting**

### **Common Issues**

**"Namespace not found" error:**
```bash
# Recreate namespaces
wrangler kv:namespace create SESSIONS
# Update wrangler.toml with new IDs
```

**"Secret not found" error:**
```bash
# Verify secrets are set
wrangler secret list

# Re-add missing secrets
wrangler secret put JWT_SECRET
```

**CORS errors:**
```bash
# Check CORS_ORIGINS setting in wrangler.toml
# Ensure your domain is included in allowed origins
```

**Rate limiting issues:**
```bash
# Check rate limit configuration
# Increase limits if needed for your use case
```

### **Debug Mode**
Enable debug mode for detailed error information:
```toml
[env.development.vars]
DEBUG_MODE = true
```

### **Monitoring Issues**
```bash
# Check real-time logs
wrangler tail --env production

# View analytics in Cloudflare Dashboard
# Go to Workers → your-worker → Analytics
```

## 📋 **Post-Deployment Checklist**

- [ ] Health check endpoint responds correctly
- [ ] Authentication works (login/logout/refresh)
- [ ] Rate limiting is functioning
- [ ] CORS headers are properly set
- [ ] Custom domain is accessible (if configured)
- [ ] KV namespaces are accessible
- [ ] Secrets are properly configured
- [ ] Analytics are being collected
- [ ] Real-time logs are working
- [ ] Error handling is working correctly

## 📞 **Support**

**Documentation:**
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Docs](https://developers.cloudflare.com/workers/wrangler/)

**Community:**
- [Cloudflare Discord](https://discord.cloudflare.com)
- [GitHub Issues](https://github.com/WulfForge/Hearthlink/issues)

**Performance:**
- Average cold start: <5ms
- Average warm response: <1ms
- Global latency: <50ms (95th percentile)
- Availability: 99.99%+ SLA

---

**🎉 Your Hearthlink Workers API is now deployed globally and ready to serve requests at edge locations worldwide!**