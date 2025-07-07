# Alden Persona Integration

This document describes the integration of Alden, the primary local agent/persona for Hearthlink, with local LLM engines and the implementation of baseline reflective capabilities.

## Overview

Alden is designed as an evolutionary companion AI that provides:
- Executive function and productivity support
- Cognitive/developmental scaffolding
- Dynamic emotional and motivational feedback
- Habit- and relationship-aware memory and reasoning
- Progressive autonomy with user-controlled trust/delegation

All learning is local, transparent, and user-editable—no hidden memory or external training.

## Architecture

### Components

1. **Local LLM Client** (`src/llm/local_llm_client.py`)
   - Unified interface for Ollama, LM Studio, and custom LLM endpoints
   - Platinum-standard error handling and logging
   - Connection testing and health monitoring

2. **Alden Persona** (`src/personas/alden.py`)
   - Core persona implementation with memory schema
   - Baseline reflective prompts and response generation
   - Trait management and learning capabilities
   - Audit logging and memory export

3. **API Interface** (`src/api/alden_api.py`)
   - FastAPI-based REST API for Alden interactions
   - Message exchange, memory management, and configuration
   - Comprehensive error handling and logging

4. **CLI Interface** (`src/cli/alden_cli.py`)
   - Interactive command-line interface
   - Real-time chat with Alden
   - Memory management and configuration commands

5. **Configuration** (`config/alden_config.json`)
   - Default settings for different LLM engines
   - API and CLI configuration options
   - Logging and behavior settings

## Setup Instructions

### Prerequisites

1. **Python 3.8+** with pip
2. **Local LLM Engine** (Ollama, LM Studio, or compatible)
3. **Required Python packages** (see `requirements.txt`)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up local LLM engine:**

   **Option A: Ollama**
   ```bash
   # Install Ollama (https://ollama.ai/)
   # Pull a model
   ollama pull llama2
   # Start Ollama service
   ollama serve
   ```

   **Option B: LM Studio**
   ```bash
   # Download and install LM Studio
   # Load a model and start local server
   # Configure to run on http://localhost:1234
   ```

3. **Verify configuration:**
   ```bash
   # Test with default settings
   python src/run_alden.py cli --engine ollama --model llama2
   ```

## Usage

### Command Line Interface

**Basic CLI usage:**
```bash
# Start interactive CLI with Ollama
python src/run_alden.py cli --engine ollama --model llama2

# Use LM Studio
python src/run_alden.py cli --engine lmstudio --url http://localhost:1234 --model local-model

# Custom configuration
python src/run_alden.py cli --config my_config.json --engine custom
```

**CLI Commands:**
- Type messages to chat with Alden
- `/help` - Show available commands
- `/status` - Show Alden's current status
- `/traits` - View or modify personality traits
- `/correction <type> <description>` - Add learning feedback
- `/mood <mood> <score>` - Record current mood
- `/export [filename]` - Export memory data
- `/quit` - Exit CLI

### API Interface

**Start API server:**
```bash
# Start API with default settings
python src/run_alden.py api --engine ollama --model llama2

# Custom host and port
python src/run_alden.py api --host 0.0.0.0 --port 8080
```

**API Endpoints:**

1. **Send Message**
   ```bash
   POST /api/v1/alden/message
   {
     "message": "Hello Alden, how are you today?",
     "session_id": "optional-session-id",
     "context": {"source": "web"}
   }
   ```

2. **Update Traits**
   ```bash
   PATCH /api/v1/alden/traits/openness
   {
     "trait_name": "openness",
     "new_value": 85,
     "reason": "user_update"
   }
   ```

3. **Add Correction**
   ```bash
   POST /api/v1/alden/corrections
   {
     "event_type": "positive",
     "description": "Great response to my question",
     "impact_score": 0.5
   }
   ```

4. **Record Mood**
   ```bash
   POST /api/v1/alden/mood
   {
     "session_id": "session-123",
     "mood": "positive",
     "score": 85
   }
   ```

5. **Get Status**
   ```bash
   GET /api/v1/alden/status
   ```

6. **Export Memory**
   ```bash
   GET /api/v1/alden/memory/export
   ```

7. **Health Check**
   ```bash
   GET /api/v1/alden/health
   ```

## Configuration

### Configuration File

The default configuration is in `config/alden_config.json`:

```json
{
  "alden": {
    "persona_id": "alden",
    "schema_version": "1.0.0",
    "default_traits": {
      "openness": 72,
      "conscientiousness": 86,
      "extraversion": 44,
      "agreeableness": 93,
      "emotional_stability": 77
    }
  },
  "llm_engines": {
    "ollama": {
      "engine": "ollama",
      "base_url": "http://localhost:11434",
      "default_model": "llama2"
    }
  },
  "api": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": false
  }
}
```

### Environment Variables

You can override configuration with environment variables:

```bash
export ALDEN_LLM_ENGINE=ollama
export ALDEN_LLM_URL=http://localhost:11434
export ALDEN_LLM_MODEL=llama2
export ALDEN_API_HOST=0.0.0.0
export ALDEN_API_PORT=8080
```

## Memory Schema

Alden's memory follows the schema defined in the system documentation:

```json
{
  "persona_id": "alden",
  "user_id": "user-123",
  "schema_version": "1.0.0",
  "timestamp": "2025-01-06T12:00:00Z",
  "traits": {
    "openness": 72,
    "conscientiousness": 86,
    "extraversion": 44,
    "agreeableness": 93,
    "emotional_stability": 77
  },
  "motivation_style": "supportive",
  "trust_level": 0.82,
  "feedback_score": 92,
  "learning_agility": 6.2,
  "reflective_capacity": 12,
  "habit_consistency": 0.77,
  "engagement": 16,
  "correction_events": [],
  "session_mood": [],
  "relationship_log": [],
  "user_tags": [],
  "audit_log": []
}
```

## Logging

All interactions are logged using the HearthlinkLogger system:

- **Event Types:**
  - `llm_client_init` - LLM client initialization
  - `llm_generation_request` - LLM request
  - `llm_generation_success` - Successful LLM response
  - `alden_persona_init` - Persona initialization
  - `alden_interaction_request` - User interaction
  - `alden_response_success` - Successful response
  - `api_message_request` - API message request
  - `cli_input_processing` - CLI input processing

- **Log Files:**
  - Default: `logs/alden.log`
  - Configurable in `alden_config.json`

## Error Handling

The system implements platinum-standard error handling:

- **LLM Errors:** Connection failures, invalid responses, timeouts
- **Persona Errors:** Memory operations, trait updates, learning events
- **API Errors:** Invalid requests, authentication, rate limiting
- **CLI Errors:** Input validation, command parsing, user errors

All errors are logged with context and handled gracefully.

## Security Considerations

1. **Local Only:** All processing happens locally
2. **No External Calls:** No data leaves the local environment
3. **User Control:** All memory is user-editable and exportable
4. **Audit Trail:** All changes are logged with timestamps
5. **Input Validation:** All inputs are validated and sanitized

## Troubleshooting

### Common Issues

1. **LLM Connection Failed**
   - Verify LLM engine is running
   - Check URL and port configuration
   - Test with curl: `curl http://localhost:11434/api/tags`

2. **Model Not Found**
   - Ensure model is downloaded/loaded
   - Check model name spelling
   - Verify model compatibility

3. **API Not Starting**
   - Check port availability
   - Verify host configuration
   - Check firewall settings

4. **CLI Not Responding**
   - Verify LLM connection
   - Check input format
   - Review error logs

### Debug Mode

Enable debug mode for detailed logging:

```bash
# API debug mode
python src/run_alden.py api --engine ollama --model llama2

# CLI with verbose logging
export ALDEN_LOG_LEVEL=DEBUG
python src/run_alden.py cli --engine ollama --model llama2
```

## Development

### Adding New LLM Engines

1. Extend `LocalLLMClient` in `src/llm/local_llm_client.py`
2. Add engine-specific generation method
3. Update configuration schema
4. Add tests and documentation

### Extending Alden's Capabilities

1. Modify `AldenPersona` class in `src/personas/alden.py`
2. Update memory schema as needed
3. Add new API endpoints
4. Extend CLI commands

### Testing

```bash
# Run basic functionality test
python -c "
from src.personas.alden import create_alden_persona
config = {'engine': 'ollama', 'base_url': 'http://localhost:11434', 'model': 'llama2'}
alden = create_alden_persona(config)
response = alden.generate_response('Hello')
print(response)
"
```

## References

- [Hearthlink System Documentation](../docs/hearthlink_system_documentation_master.md)
- [Platinum Blockers](../docs/PLATINUM_BLOCKERS.md)
- [Open Items](../docs/appendix_a_combined_open_items.md)
- [API Documentation](http://localhost:8000/docs) (when API is running)

## License

This implementation follows the Hearthlink project license and ethical guidelines. 