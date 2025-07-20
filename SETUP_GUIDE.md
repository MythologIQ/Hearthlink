# Hearthlink Setup Guide
## Complete AI Backend with LLM, RAG, and Knowledge Graph Integration

### 🚀 Overview
This guide sets up Hearthlink with a complete AI backend featuring:
- **Local LLM Integration** with Ollama
- **RAG (Retrieval-Augmented Generation)** with vector databases
- **Knowledge Graph** with Neo4j
- **Memory Systems** with persistent storage
- **Secure Database Infrastructure**

### 📋 Prerequisites

#### System Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux
- **RAM**: 16GB minimum (32GB recommended for LLM)
- **Storage**: 50GB free space
- **Network**: Internet connection for model downloads

#### Software Dependencies
- **Node.js** 18+ and npm
- **Python** 3.10+ with pip
- **Docker** and Docker Compose
- **Git**

### 🔧 Installation Steps

#### 1. Install Database Systems

**Option A: Using Docker (Recommended)**
```bash
# Create docker-compose.yml in Hearthlink root
docker-compose up -d
```

**Option B: Manual Installation**
```bash
# PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql  # macOS

# Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 4.0' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update && sudo apt install neo4j

# Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis  # macOS

# Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

#### 2. Install Ollama and Models
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download required models
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest
```

#### 3. Setup Python Backend
```bash
# Navigate to backend directory
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

#### 4. Configure Databases
```bash
# Run database setup script
cd scripts
python setup_databases.py
```

#### 5. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Example .env:**
```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hearthlink_memory
POSTGRES_USER=alden_user
POSTGRES_PASSWORD=your_secure_password

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your_qdrant_key

# LLM Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
LLM_MODEL=llama3.2:latest
EMBEDDING_MODEL=nomic-embed-text:latest

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
```

#### 6. Install Frontend Dependencies
```bash
# Navigate to project root
cd ../..

# Install Node.js dependencies
npm install

# Install additional dependencies for enhanced features
npm install axios react-markdown react-syntax-highlighter
```

#### 7. Start the System
```bash
# Start databases (if using Docker)
docker-compose up -d

# Start Ollama service
ollama serve

# Start Python backend
cd src/backend
python alden_backend.py

# Start frontend (new terminal)
cd ../..
npm start
```

### 🧪 Testing the Setup

#### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Database Connectivity
```bash
curl http://localhost:8000/status
```

#### 3. LLM Integration Test
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, can you remember this conversation?", "session_id": "test123"}'
```

### 📊 Expected Response Structure

**Successful Query Response:**
```json
{
  "response": "Hello! Yes, I can remember our conversation. This interaction will be stored in my memory systems...",
  "session_id": "test123",
  "relevant_memories": [
    {
      "id": "mem_1234567890",
      "content": "Previous conversation context...",
      "slice_type": "episodic",
      "importance": 0.85,
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z",
  "status": "success"
}
```

### 🔍 Troubleshooting

#### Common Issues

**Backend Won't Start:**
```bash
# Check Python dependencies
pip list | grep -E "(fastapi|ollama|neo4j|asyncpg)"

# Check database connections
python -c "import asyncpg; print('PostgreSQL driver OK')"
python -c "import neo4j; print('Neo4j driver OK')"
```

**LLM Not Responding:**
```bash
# Check Ollama service
ollama list
curl http://localhost:11434/api/tags

# Test direct LLM call
ollama run llama3.2:latest "Hello, are you working?"
```

**Database Connection Errors:**
```bash
# Check PostgreSQL
psql -h localhost -U alden_user -d hearthlink_memory

# Check Neo4j
cypher-shell -u neo4j -p your_password

# Check Redis
redis-cli ping

# Check Qdrant
curl http://localhost:6333/collections
```

**Frontend Connection Issues:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check browser console for CORS errors
# Verify REACT_APP_ALDEN_BACKEND_URL in .env
```

### 🎯 Features Verification

#### 1. Memory Persistence
- Send a message to Alden
- Restart the backend
- Send a related message
- Verify Alden remembers the context

#### 2. Knowledge Graph
- Ask Alden about a topic
- Use Neo4j browser to view created nodes
- Verify relationships are being created

#### 3. RAG Integration
- Upload a document or provide information
- Ask questions about the content
- Verify relevant information is retrieved

#### 4. Multi-Modal Capabilities
- Test various types of queries
- Verify appropriate memory slice types
- Check conversation context maintenance

### 🔐 Security Considerations

1. **Database Security**
   - Use strong passwords
   - Enable SSL/TLS connections
   - Restrict network access
   - Regular security updates

2. **API Security**
   - JWT token authentication
   - Rate limiting
   - Input validation
   - CORS configuration

3. **Data Privacy**
   - Encrypt sensitive data
   - Secure session management
   - Data retention policies
   - User consent mechanisms

### 🚀 Production Deployment

#### Environment Setup
- Use environment variables for secrets
- Configure proper logging
- Set up monitoring and alerting
- Implement backup strategies

#### Scaling Considerations
- Database connection pooling
- Load balancing for multiple instances
- Redis cluster for session management
- Qdrant clustering for vector storage

### 📈 Performance Optimization

#### Database Optimization
- Index frequently queried fields
- Optimize Neo4j queries
- Use Redis for caching
- Monitor query performance

#### LLM Optimization
- Adjust model parameters
- Implement response caching
- Use GPU acceleration
- Optimize prompt engineering

### 🎉 Success Indicators

You'll know everything is working when:
- ✅ Frontend shows "CONNECTED" status
- ✅ All capability indicators show "Active"
- ✅ Alden responds with contextual memory
- ✅ Memory panel shows relevant slices
- ✅ Database logs show proper connections
- ✅ Knowledge graph grows with interactions

### 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure all services are running
4. Check log files for error messages
5. Test individual components separately

### 📚 Next Steps

Once basic setup is complete:
1. Configure Project Command features
2. Set up Core orchestration
3. Implement Dashboard productivity tools
4. Add Conference system integration
5. Enable advanced AI collaboration features

---

**🎯 Your Hearthlink installation with full AI backend is now complete!**