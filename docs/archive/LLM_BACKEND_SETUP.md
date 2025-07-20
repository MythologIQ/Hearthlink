# 🔧 LLM Backend Configuration Guide

Hearthlink supports multiple LLM backends for maximum versatility. Choose the one that fits your setup.

---

## 🎯 Quick Setup by User Type

### Current User (Claude Code)
```bash
# No setup needed! Already configured for Claude Code CLI
cd /mnt/g/MythologIQ/Hearthlink/src
python run_services.py
```

### API Users (Future)
```bash
# Claude API
export CLAUDE_API_KEY="sk-ant-api03-..."

# ChatGPT API  
export OPENAI_API_KEY="sk-..."

# Start services
python run_services.py
```

### Local LLM Users
```bash
# Start Ollama
ollama serve
ollama pull llama2

# Configure Hearthlink
# Edit config/llm_backends.json - set local_llm.enabled = true
python run_services.py
```

---

## 🏗️ Backend Options

### 1. **Claude Code CLI** (Current Setup)
- ✅ **No API key needed**
- ✅ **Already authenticated**  
- ✅ **Default backend**
- 📝 Uses your existing Claude Code session

### 2. **Claude API** (For API Users)
- 🔑 Requires Anthropic API key
- 💰 Paid per token usage
- 🚀 Direct API access
- 📊 Full token tracking

### 3. **ChatGPT API** (For OpenAI Users)
- 🔑 Requires OpenAI API key
- 💰 Paid per token usage  
- 🤖 GPT-4 models available
- 🔄 Alternative to Claude

### 4. **Local LLM** (Privacy First)
- 🏠 Runs entirely local
- 🆓 No API costs
- 🔒 Complete privacy
- ⚡ Works with Ollama/LMStudio

### 5. **Hearthlink API** (Reverse Connection)
- 🔗 Connect to external Hearthlink
- 🌐 Distributed processing
- 🔄 Load balancing
- 🏢 Enterprise setups

---

## 📋 Configuration Files

### Main Config: `config/llm_backends.json`
```json
{
  "default_backend": "claude-code",
  "backends": {
    "claude_code": {
      "enabled": true,
      "description": "Claude Code CLI integration"
    }
  }
}
```

### Environment Variables
```bash
# Optional - only if using API backends
export CLAUDE_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-openai-key"  
export HEARTHLINK_API_ENDPOINT="https://api.hearthlink.com"
```

---

## 🔄 Switching Backends

### Runtime Switching (Future Feature)
```typescript
// In React components
const { switchBackend, getAvailableBackends } = useClaudeConnector();

// Switch to different backend
switchBackend('chatgpt-api');

// Check available backends
const backends = getAvailableBackends(); // ['claude-code', 'local_llm']
```

### Configuration Switching
```bash
# Edit config/llm_backends.json
{
  "default_backend": "local_llm",  # Changed from "claude-code"
  "backends": {
    "local_llm": {
      "enabled": true             # Enable desired backend
    }
  }
}
```

---

## 🚀 Backend Implementation Status

| Backend | Status | Current User | Future Users |
|---------|--------|--------------|--------------|
| **Claude Code** | ✅ Ready | ✅ Active | ✅ Supported |
| **Claude API** | ✅ Ready | ❌ N/A | ✅ Supported |
| **ChatGPT API** | ✅ Ready | ❌ N/A | ✅ Supported |
| **Local LLM** | ✅ Ready | ⚠️ Optional | ✅ Supported |
| **Hearthlink API** | ✅ Ready | ❌ N/A | ✅ Supported |

---

## 🛠️ Adding New Backends

### 1. Create Backend Class
```typescript
class MyLLMBackend {
  async generate(request: LLMRequest): Promise<LLMResponse> {
    // Your LLM integration here
  }
  
  async healthCheck() {
    // Health check implementation
  }
}
```

### 2. Register in BackendManager
```typescript
// In LLMBackendManager.ts
this.backends.set('my-llm', new MyLLMBackend(config));
```

### 3. Add Configuration
```json
{
  "backends": {
    "my_llm": {
      "enabled": false,
      "config": { "endpoint": "..." }
    }
  }
}
```

---

## 🔍 Troubleshooting

### Backend Not Available
```bash
# Check backend status
curl http://localhost:8080/api/backends/status

# Check logs
tail -f logs/synapse.log
```

### Claude Code Issues
```bash
# Check Claude Code auth
claude auth status

# Re-authenticate if needed
claude auth login
```

### Local LLM Issues
```bash
# Check Ollama
ollama list
ollama serve

# Check LMStudio
curl http://localhost:1234/v1/models
```

---

## 🎯 Recommendations

### For Current User
- ✅ **Keep Claude Code backend** - already working
- ⚠️ **Optional**: Set up local LLM as backup
- 📚 **Future**: Easy to add API backends later

### For Future Users  
- 🔑 **API backends** for production use
- 🏠 **Local LLM** for privacy/cost concerns
- 🔄 **Multiple backends** for redundancy

### For Enterprise
- 🌐 **Hearthlink API** for distributed processing
- 🔒 **Local LLM** for sensitive data
- 📊 **Full token tracking** across all backends

The versatile architecture ensures Hearthlink works for **every user type and use case**.