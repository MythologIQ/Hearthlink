# LLM Implementation Guide - Hearthlink

**Module:** `feature/llm-client`  
**Implementation:** `src/llm/local_llm_client.py`  
**Status:** ✅ Complete Implementation  
**Documentation Status:** ✅ Complete  

---

## Overview

The Hearthlink LLM Client provides a unified interface for interacting with local Large Language Models. This module enables Hearthlink's personas (Alden, Alice, Mimic) to leverage local LLM capabilities while maintaining privacy and ethical standards. The client supports multiple LLM backends and provides consistent APIs for text generation, conversation management, and model interaction.

## Architecture

### Core Components

1. **Local LLM Client** (`src/llm/local_llm_client.py`)
   - Unified LLM interface
   - Model management and switching
   - Conversation context handling
   - Response processing and validation

2. **Supported Backends**
   - Ollama (primary)
   - LM Studio
   - LocalAI
   - Custom model endpoints

3. **Integration Points**
   - Alden Persona (`src/personas/alden.py`)
   - Mimic Persona (`src/personas/mimic.py`)
   - Core Orchestration (`src/core/core.py`)

## Implementation Details

### Client Configuration

```python
from src.llm.local_llm_client import LocalLLMClient

# Basic configuration
config = {
    "backend": "ollama",
    "model": "llama2:7b",
    "endpoint": "http://localhost:11434",
    "timeout": 30,
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

client = LocalLLMClient(config)
```

### Model Management

```python
# List available models
models = client.list_models()
print(models)
# Output: ['llama2:7b', 'llama2:13b', 'mistral:7b', 'codellama:7b']

# Switch models
client.switch_model("mistral:7b")

# Get model info
model_info = client.get_model_info("llama2:7b")
print(model_info)
# Output: {
#     "name": "llama2:7b",
#     "size": "7B",
#     "context_length": 4096,
#     "supported_tasks": ["text-generation", "chat"]
# }
```

## API Reference

### Core Methods

#### 1. Text Generation

```python
# Simple text generation
response = client.generate(
    prompt="Explain quantum computing in simple terms",
    max_tokens=500,
    temperature=0.7
)

print(response.text)
# Output: "Quantum computing is a revolutionary approach to processing information..."

# With streaming
for chunk in client.generate_stream(
    prompt="Write a short story about AI",
    max_tokens=1000
):
    print(chunk.text, end="", flush=True)
```

#### 2. Chat Completion

```python
# Chat conversation
messages = [
    {"role": "system", "content": "You are Alden, an evolutionary AI companion."},
    {"role": "user", "content": "Hello Alden, how are you today?"},
    {"role": "assistant", "content": "Hello! I'm doing well, thank you for asking."},
    {"role": "user", "content": "Can you help me with my project?"}
]

response = client.chat_complete(
    messages=messages,
    max_tokens=300,
    temperature=0.8
)

print(response.message)
# Output: "Of course! I'd be happy to help you with your project. What kind of project are you working on?"
```

#### 3. Context Management

```python
# Create conversation context
context = client.create_context(
    system_prompt="You are a helpful AI assistant.",
    conversation_history=[],
    max_history_length=10
)

# Add messages to context
context.add_message("user", "What is machine learning?")
context.add_message("assistant", "Machine learning is a subset of AI...")

# Generate response with context
response = client.generate_with_context(
    context=context,
    user_message="Can you give me an example?",
    max_tokens=400
)
```

### Advanced Features

#### 1. Function Calling

```python
# Define functions
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
]

# Function calling
response = client.chat_complete_with_functions(
    messages=[{"role": "user", "content": "What's the weather in New York?"}],
    functions=functions,
    function_call="auto"
)

if response.function_call:
    print(f"Function: {response.function_call.name}")
    print(f"Arguments: {response.function_call.arguments}")
```

#### 2. Structured Output

```python
# JSON output
response = client.generate_structured(
    prompt="List the top 3 programming languages for AI development",
    output_format={
        "type": "object",
        "properties": {
            "languages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "popularity_score": {"type": "number"}
                    }
                }
            }
        }
    }
)

print(response.structured_output)
# Output: {
#     "languages": [
#         {"name": "Python", "description": "Most popular for AI/ML", "popularity_score": 9.5},
#         {"name": "R", "description": "Statistical computing", "popularity_score": 7.2},
#         {"name": "Julia", "description": "High-performance scientific computing", "popularity_score": 6.8}
#     ]
# }
```

## Backend Support

### Ollama Backend

```python
# Ollama configuration
ollama_config = {
    "backend": "ollama",
    "endpoint": "http://localhost:11434",
    "model": "llama2:7b",
    "options": {
        "num_ctx": 4096,
        "num_gpu": 1,
        "num_thread": 8
    }
}

client = LocalLLMClient(ollama_config)
```

### LM Studio Backend

```python
# LM Studio configuration
lmstudio_config = {
    "backend": "lmstudio",
    "endpoint": "http://localhost:1234/v1",
    "model": "local-model",
    "api_key": "not-needed"
}

client = LocalLLMClient(lmstudio_config)
```

### LocalAI Backend

```python
# LocalAI configuration
localai_config = {
    "backend": "localai",
    "endpoint": "http://localhost:8080",
    "model": "gpt-3.5-turbo",
    "api_key": "not-needed"
}

client = LocalLLMClient(localai_config)
```

### Custom Backend

```python
# Custom backend configuration
custom_config = {
    "backend": "custom",
    "endpoint": "http://localhost:5000",
    "model": "custom-model",
    "headers": {"Authorization": "Bearer token"},
    "request_format": "openai",  # or "anthropic", "custom"
    "response_format": "openai"
}

client = LocalLLMClient(custom_config)
```

## Error Handling

### Error Types

```python
from src.llm.local_llm_client import LLMError, ModelNotFoundError, ConnectionError

try:
    response = client.generate("Hello world")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    # Handle model not found
except ConnectionError as e:
    print(f"Connection failed: {e}")
    # Handle connection issues
except LLMError as e:
    print(f"LLM error: {e}")
    # Handle general LLM errors
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

# Apply retry decorator
@retry_on_error(max_retries=3, delay=1)
def generate_with_retry(client, prompt):
    return client.generate(prompt)
```

## Performance Optimization

### Caching

```python
import hashlib
import json
from functools import lru_cache

class LLMCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
    
    def get_cache_key(self, prompt, model, params):
        key_data = {
            "prompt": prompt,
            "model": model,
            "params": params
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value

# Usage
cache = LLMCache()
key = cache.get_cache_key(prompt, model, params)
cached_response = cache.get(key)

if cached_response is None:
    response = client.generate(prompt, **params)
    cache.set(key, response)
else:
    response = cached_response
```

### Batch Processing

```python
def batch_generate(client, prompts, batch_size=5):
    """Generate responses for multiple prompts in batches"""
    results = []
    
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        batch_results = []
        
        # Process batch in parallel
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [
                executor.submit(client.generate, prompt)
                for prompt in batch
            ]
            batch_results = [future.result() for future in futures]
        
        results.extend(batch_results)
    
    return results

# Usage
prompts = [
    "Explain AI in one sentence",
    "What is machine learning?",
    "Describe neural networks",
    "How does deep learning work?",
    "What are transformers?"
]

responses = batch_generate(client, prompts, batch_size=3)
```

## Integration with Personas

### Alden Integration

```python
from src.personas.alden import Alden
from src.llm.local_llm_client import LocalLLMClient

class AldenWithLLM(Alden):
    def __init__(self, llm_config):
        super().__init__()
        self.llm_client = LocalLLMClient(llm_config)
    
    def process_message(self, message, context=None):
        # Prepare system prompt for Alden
        system_prompt = """You are Alden, an evolutionary AI companion. 
        You help users grow and develop through thoughtful conversation and insights."""
        
        # Create conversation context
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Generate response
        response = self.llm_client.chat_complete(
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        
        return response.message

# Usage
llm_config = {"backend": "ollama", "model": "llama2:7b"}
alden = AldenWithLLM(llm_config)
response = alden.process_message("Hello Alden, how can you help me grow?")
```

### Mimic Integration

```python
from src.personas.mimic import Mimic
from src.llm.local_llm_client import LocalLLMClient

class MimicWithLLM(Mimic):
    def __init__(self, llm_config):
        super().__init__()
        self.llm_client = LocalLLMClient(llm_config)
    
    def generate_persona_response(self, persona_config, message):
        # Create persona-specific system prompt
        system_prompt = f"""You are {persona_config['name']}, {persona_config['description']}.
        Traits: {persona_config['traits']}
        Communication style: {persona_config['communication_style']}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = self.llm_client.chat_complete(
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        
        return response.message

# Usage
llm_config = {"backend": "ollama", "model": "mistral:7b"}
mimic = MimicWithLLM(llm_config)

persona_config = {
    "name": "Technical Advisor",
    "description": "Expert software architect",
    "traits": ["analytical", "detail-oriented", "practical"],
    "communication_style": "clear and structured"
}

response = mimic.generate_persona_response(
    persona_config,
    "How should I design a microservices architecture?"
)
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from src.llm.local_llm_client import LocalLLMClient

class TestLocalLLMClient:
    def setup_method(self):
        self.config = {
            "backend": "ollama",
            "model": "test-model",
            "endpoint": "http://localhost:11434"
        }
        self.client = LocalLLMClient(self.config)
    
    def test_generate_text(self):
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "response": "Test response",
                "done": True
            }
            mock_post.return_value = mock_response
            
            response = self.client.generate("Test prompt")
            assert response.text == "Test response"
    
    def test_model_switching(self):
        self.client.switch_model("new-model")
        assert self.client.current_model == "new-model"
    
    def test_error_handling(self):
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            
            with pytest.raises(ConnectionError):
                self.client.generate("Test prompt")
```

### Integration Tests

```python
def test_ollama_integration():
    """Test actual Ollama integration"""
    config = {
        "backend": "ollama",
        "model": "llama2:7b",
        "endpoint": "http://localhost:11434"
    }
    
    client = LocalLLMClient(config)
    
    # Test basic generation
    response = client.generate("Hello", max_tokens=10)
    assert response.text is not None
    assert len(response.text) > 0
    
    # Test chat completion
    messages = [
        {"role": "user", "content": "What is 2+2?"}
    ]
    response = client.chat_complete(messages, max_tokens=20)
    assert response.message is not None
```

## Configuration

### Environment Variables

```bash
# LLM Backend Configuration
HEARTHLINK_LLM_BACKEND=ollama
HEARTHLINK_LLM_MODEL=llama2:7b
HEARTHLINK_LLM_ENDPOINT=http://localhost:11434

# Performance Configuration
HEARTHLINK_LLM_TIMEOUT=30
HEARTHLINK_LLM_MAX_TOKENS=2048
HEARTHLINK_LLM_TEMPERATURE=0.7

# Caching Configuration
HEARTHLINK_LLM_CACHE_ENABLED=true
HEARTHLINK_LLM_CACHE_SIZE=1000
HEARTHLINK_LLM_CACHE_TTL=3600

# Logging Configuration
HEARTHLINK_LLM_LOG_LEVEL=INFO
HEARTHLINK_LLM_LOG_REQUESTS=true
```

### Configuration File

```yaml
# config/llm_config.yaml
llm:
  backend: ollama
  model: llama2:7b
  endpoint: http://localhost:11434
  
  # Performance settings
  timeout: 30
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9
  
  # Caching
  cache:
    enabled: true
    size: 1000
    ttl: 3600
  
  # Logging
  logging:
    level: INFO
    log_requests: true
    log_responses: false
  
  # Backend-specific settings
  ollama:
    num_ctx: 4096
    num_gpu: 1
    num_thread: 8
```

## Monitoring & Logging

### Request Logging

```python
import logging
import time
import json

class LLMLogger:
    def __init__(self):
        self.logger = logging.getLogger("hearthlink.llm")
    
    def log_request(self, prompt, model, params, response, duration):
        log_entry = {
            "timestamp": time.time(),
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response.text),
            "duration": duration,
            "params": params
        }
        
        self.logger.info(f"LLM Request: {json.dumps(log_entry)}")
    
    def log_error(self, error, context):
        log_entry = {
            "timestamp": time.time(),
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context
        }
        
        self.logger.error(f"LLM Error: {json.dumps(log_entry)}")

# Usage
logger = LLMLogger()
start_time = time.time()

try:
    response = client.generate(prompt, **params)
    duration = time.time() - start_time
    logger.log_request(prompt, model, params, response, duration)
except Exception as e:
    logger.log_error(e, {"prompt": prompt, "model": model})
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
llm_requests_total = Counter('llm_requests_total', 'Total LLM requests', ['model', 'backend'])
llm_request_duration = Histogram('llm_request_duration_seconds', 'LLM request duration', ['model'])
llm_tokens_generated = Counter('llm_tokens_generated_total', 'Total tokens generated', ['model'])
llm_errors_total = Counter('llm_errors_total', 'Total LLM errors', ['model', 'error_type'])

def track_metrics(model, backend, duration, tokens, error=None):
    llm_requests_total.labels(model=model, backend=backend).inc()
    llm_request_duration.labels(model=model).observe(duration)
    llm_tokens_generated.labels(model=model).inc(tokens)
    
    if error:
        llm_errors_total.labels(model=model, error_type=type(error).__name__).inc()
```

## Troubleshooting

### Common Issues

1. **Model Not Found**
   ```bash
   # Check available models
   ollama list
   
   # Pull missing model
   ollama pull llama2:7b
   ```

2. **Connection Errors**
   ```bash
   # Check Ollama service
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

3. **Performance Issues**
   ```bash
   # Check GPU usage
   nvidia-smi
   
   # Monitor system resources
   htop
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug client
client = LocalLLMClient(config, debug=True)

# Test connection
client.test_connection()
```

## Future Enhancements

### Planned Features

1. **Model Fine-tuning Support**
   - LoRA fine-tuning
   - QLoRA support
   - Custom training data

2. **Advanced Prompting**
   - Chain-of-thought prompting
   - Few-shot learning
   - Prompt templates

3. **Multi-modal Support**
   - Image generation
   - Audio processing
   - Video analysis

4. **Model Comparison**
   - A/B testing
   - Performance benchmarking
   - Quality assessment

---

**Documentation Version:** 1.0  
**Last Updated:** 2025-07-07  
**Next Review:** Phase 5 completion 