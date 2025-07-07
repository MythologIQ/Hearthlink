# ![Hearthlink](https://github.com/user-attachments/assets/a4ef30dd-d0f0-4150-8eb1-f7945c2f6897)




# Hearthlink Global Container

## Overview

Hearthlink is a local-first, persona-aware AI companion system with ethical safety rails and zero-trust architecture. This repository contains the initial scaffold for the global container.

## System Architecture

Hearthlink consists of seven core modules:
- **Alden** - Evolutionary Companion AI
- **Alice** - Behavioral Analysis & Context-Awareness  
- **Mimic** - Dynamic Persona & Adaptive Agent
- **Vault** - Persona-Aware Secure Memory Store
- **Core** - Communication Switch & Context Moderator
- **Synapse** - Secure External Gateway & Protocol Boundary
- **Sentry** - Security, Compliance & Oversight Persona

## Current Implementation

This scaffold implements:
- Cross-platform background process (Windows 10+ compatible)
- Platinum-standard logging with timestamps
- Ethical safety rails compliance
- Silent startup with audit trail
- Local-first architecture (no external dependencies)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10+ (primary target), macOS, or Linux

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Hearthlink
```

2. Run the container:
```bash
python src/main.py
```

### Expected Output

The container will start silently and log to:
- **Windows**: `%LOCALAPPDATA%\Hearthlink\logs\hearthlink.log`
- **Unix-like**: `~/.hearthlink/logs/hearthlink.log`

**Log Rotation**: Files rotate at 10MB, retaining up to 5 backup files.

Sample structured JSON log output:
```json
{"timestamp": "2025-01-27T10:30:15.123456", "level": "INFO", "logger": "Hearthlink", "message": "Hearthlink container started", "module": "main", "function": "log_startup", "line": 123, "event_type": "container_startup", "platform": {"system": "Windows", "release": "10", "version": "10.0.19045", "machine": "AMD64", "processor": "Intel64 Family 6"}, "python": {"version": "3.11.0", "implementation": "CPython", "compiler": "MSC v.1935 64 bit (AMD64)"}, "log_directory": "C:\\Users\\username\\AppData\\Local\\Hearthlink\\logs", "log_config": {"max_size_mb": 10, "backup_count": 5, "format": "structured_json"}}
{"timestamp": "2025-01-27T10:30:15.124567", "level": "INFO", "logger": "Hearthlink", "message": "Initializing ethical safety rails", "module": "main", "function": "_setup_safety_rails", "line": 234, "event_type": "safety_rails_initialization", "rails": ["dependency_mitigation", "human_origin_clause", "audit_trail", "ethical_boundaries"]}
{"timestamp": "2025-01-27T10:30:15.125678", "level": "INFO", "logger": "Hearthlink", "message": "Hearthlink container started successfully", "module": "main", "function": "start", "line": 345, "event_type": "container_start", "start_time": "2025-01-27T10:30:15.125678"}
```

### Stopping the Container

Press `Ctrl+C` to stop the container gracefully.

### Testing

Run the logging test suite to verify functionality:

```bash
python tests/test_logging.py
```

This will test:
- Structured JSON logging format
- Log rotation functionality
- Error handling and fallback mechanisms
- Container integration
- JSON format validation

## Development

### Project Structure
```
Hearthlink/
├── src/
│   └── main.py              # Main container entry point
├── docs/                    # System documentation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Key Features

1. **Cross-Platform Compatibility**
   - Windows: Uses `%LOCALAPPDATA%\Hearthlink\logs`
   - Unix-like: Uses `~/.hearthlink/logs`
   - Automatic directory creation

2. **Platinum-Standard Structured JSON Logging**
   - Structured JSON format with explicit timestamps and log levels
   - 10MB log rotation with 5 backup files
   - Platform and architecture detection
   - UTF-8 encoding support
   - Exception traceback capture
   - Audit trail compliance

3. **Ethical Safety Rails**
   - Dependency mitigation logging
   - Human origin clause preparation
   - Audit trail initialization
   - Crisis handling readiness

4. **Silent Background Operation**
   - Minimal resource usage
   - Graceful shutdown handling
   - Error recovery and logging

## Compliance

This implementation follows:
- **PLATINUM_BLOCKERS.md**: Ethical safety rails and dependency mitigation
- **System Documentation**: Architecture constraints and requirements
- **Zero-Trust Principles**: Local-first, no external dependencies
- **User Sovereignty**: User always has final authority

## Next Steps

This scaffold provides the foundation for implementing:
1. Vault (secure memory store)
2. Core (agent orchestration)
3. Individual persona modules (Alden, Alice, Mimic)
4. Synapse (external gateway)
5. Sentry (security and audit)

## License

[License information to be added]

## Contributing

[Contribution guidelines to be added]

# Hearthlink

> **Open, honest, transparent… Real.**

---

## Features

- **Global Orchestration**: Run agents in the background across all processes (desktop, terminal, system tray)
- **Alice**: Neurodivergent-aware AI support with empathic, non-clinical protocol
- **Alden**: Reflection, feedback, and LLM integration
- **Vault**: Secure, encrypted memory—per persona and communal
- **Mimic**: Extensible persona and plugin system with sandboxing and audit
- **Sentry**: Comprehensive system logging, audit export, anomaly detection (local only, privacy-first)
- **Synapse**: Plugin management, manifest enforcement, secure extension

See [`/docs/PLATINUM_BLOCKERS.md`](./docs/PLATINUM_BLOCKERS.md) for full details on platinum barrier features.

---

## Quick Start

1. **Clone the repo**
    ```sh
    git clone https://github.com/WulfForge/Hearthlink.git
    ```
2. **Open in Codespaces or your local development environment**
3. **See `/docs/` for all architecture, system, and implementation details**
4. **Launch via your preferred entry point (e.g., `main.py`, desktop launcher, etc.)**
5. **Consult `/docs/PLATINUM_BLOCKERS.md` for neurodivergent support, compliance mapping, and advanced features**

---

## Documentation

- **System Overview:** [`/docs/hearthlink_system_documentation_master.md`](./docs/hearthlink_system_documentation_master.md)
- **Platinum Blockers:** [`/docs/PLATINUM_BLOCKERS.md`](./docs/PLATINUM_BLOCKERS.md)
- **Model Context Protocol:** [`/docs/appendix_e_model_context_protocol_mcp_full_specification.md`](./docs/appendix_e_model_context_protocol_mcp_full_specification.md)
- **Developer & QA Checklists:** [`/docs/appendix_h_developer_qa_platinum_checklists.md`](./docs/appendix_h_developer_qa_platinum_checklists.md)
- **Full documentation index:** See `/docs/`

---

## Contribution & Development

- This repository is **private**.  
- Access is by invitation only.
- All development and QA are managed internally by the authorized team (Cursor, Product Owner, select beta participants).
- For requests or to join the beta, please contact the maintainer directly.

---

## Licensing

Hearthlink is open source under the **MIT License**.  
See [`LICENSE`](./LICENSE) for full legal terms.

## Download & Usage

- Hearthlink is available for download via the official website for a minimal fee to support ongoing development and maintenance.
- Each download includes the MIT License and all required documentation.
- Users may use, modify, or redistribute Hearthlink per the MIT License.  
  Note: redistribution may occur, as permitted by the license.

---

## Status

- **Closed Beta**: Actively under development
- **Contact**: For questions or access, open an Issue or contact the maintainer

---

## Disclaimer

Hearthlink and Alice are support tools for productivity and personal development—**not clinical or therapeutic software**.  
Crisis support features are informational only. Users are always urged to seek professional help if needed.

---

**Welcome to the next generation of collaborative AI.**

