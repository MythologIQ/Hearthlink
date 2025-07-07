# ![Hearthlink](https://github.com/user-attachments/assets/a4ef30dd-d0f0-4150-8eb1-f7945c2f6897)




# Hearthlink Global Container

## Overview

Hearthlink is a local-first, persona-aware AI companion system with ethical safety rails and zero-trust architecture. This repository contains the initial scaffold for the global container with advanced multimodal persona capabilities and enterprise-grade features.

## System Architecture

Hearthlink consists of seven core modules plus enterprise features:
- **Alden** - Evolutionary Companion AI with Advanced Multimodal Persona
- **Alice** - Behavioral Analysis & Context-Awareness  
- **Mimic** - Dynamic Persona & Adaptive Agent
- **Vault** - Persona-Aware Secure Memory Store
- **Core** - Communication Switch & Context Moderator
- **Synapse** - Secure External Gateway & Protocol Boundary
- **Sentry** - Security, Compliance & Oversight Persona

### Enterprise Features (Phase 5 Complete)

- **Advanced Monitoring System**: Real-time metrics, health checks, performance monitoring
- **Multi-User Collaboration**: Session management, real-time collaboration, access controls
- **RBAC/ABAC Security**: Role-based and attribute-based access control
- **SIEM Monitoring**: Security event collection, threat detection, incident management

### Advanced Features

- **Multimodal Input Processing**: Text, audio, visual, environmental, behavioral, and sensory inputs
- **Dynamic User Adaptation**: Real-time persona adjustment based on behavioral patterns
- **Learning Feedback Loops**: Integrated learning from behavioral analysis and user corrections
- **Behavioral Analysis Integration**: Comprehensive understanding of user behavior patterns

## Current Implementation

This scaffold implements:
- Cross-platform background process (Windows 10+ compatible)
- Platinum-standard logging with timestamps
- Ethical safety rails compliance
- Silent startup with audit trail
- Local-first architecture (no external dependencies)
- Advanced multimodal persona system with dynamic adaptation
- **Enterprise-grade features with comprehensive error handling**

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

Run the comprehensive test suite to verify functionality:

```bash
# Core functionality tests
python tests/test_logging.py

# Enterprise features tests
python tests/test_enterprise_features.py
```

This will test:
- Structured JSON logging format
- Log rotation functionality
- Error handling and fallback mechanisms
- Container integration
- JSON format validation
- **Enterprise features integration**
- **Security and monitoring systems**

## Enterprise Features

### Advanced Monitoring

Real-time system monitoring with health checks and performance metrics:

```python
from src.enterprise.advanced_monitoring import AdvancedMonitoring

monitoring = AdvancedMonitoring()
health_status = monitoring.get_health_status()
performance = monitoring.get_performance_metrics()
```

### Multi-User Collaboration

Session-based collaboration with real-time features:

```python
from src.enterprise.multi_user_collaboration import MultiUserCollaboration

collaboration = MultiUserCollaboration()
session_id = collaboration.create_session("user1", "project-session")
collaboration.join_session(session_id, "user2")
```

### RBAC/ABAC Security

Role-based and attribute-based access control:

```python
from src.enterprise.rbac_abac_security import RBACABACSecurity

security = RBACABACSecurity()
decision = security.evaluate_access("user1", "resource1", "read")
```

### SIEM Monitoring

Security information and event management:

```python
from src.enterprise.siem_monitoring import SIEMMonitoring

siem = SIEMMonitoring()
event_id = siem.collect_event("system", EventCategory.AUTHENTICATION, EventSeverity.HIGH)
alerts = siem.get_active_alerts()
```

For detailed enterprise documentation, see [`/docs/PHASE_5_ENTERPRISE_FEATURES_SUMMARY.md`](./docs/PHASE_5_ENTERPRISE_FEATURES_SUMMARY.md).

## Advanced Multimodal Persona

### Features

The advanced multimodal persona system provides:

- **Multi-modal Input Processing**: Process text, audio, visual, environmental, behavioral, and sensory inputs
- **Dynamic User Adaptation**: Real-time persona adjustment based on behavioral triggers
- **Learning Feedback Loops**: Continuous learning from behavioral analysis and user corrections
- **State Management**: Comprehensive persona state tracking and persistence
- **Privacy-First**: Local processing with user-controlled data sharing

### Usage Example

```python
from personas.advanced_multimodal_persona import (
    AdvancedMultimodalPersona, MultimodalInput, InputModality
)

# Create advanced persona
persona = AdvancedMultimodalPersona(
    persona_id="alden-advanced",
    llm_client=llm_client,
    behavioral_analysis=behavioral_analysis,
    logger=logger
)

# Process multimodal inputs
text_input = MultimodalInput(
    modality=InputModality.TEXT,
    data={"text": "I need help with my project"},
    confidence=0.95,
    source="user_message"
)

env_input = MultimodalInput(
    modality=InputModality.ENVIRONMENTAL,
    data={"environmental": {"location": "home", "time_of_day": "evening"}},
    confidence=0.9,
    source="system_context"
)

# Process inputs and get adaptive response
result = persona.process_multimodal_input([text_input, env_input], user_id="user-123")
print(f"Response: {result['response']}")
```

For detailed documentation, see [`/docs/PERSONA_GUIDE.md`](./docs/PERSONA_GUIDE.md).

## Development

### Project Structure
```
Hearthlink/
├── src/
│   ├── main.py              # Main container entry point
│   ├── personas/
│   │   ├── alden.py         # Alden persona implementation
│   │   └── advanced_multimodal_persona.py  # Advanced multimodal persona
│   ├── core/
│   │   ├── core.py          # Core orchestration
│   │   └── behavioral_analysis.py  # Behavioral analysis
│   ├── vault/
│   │   └── vault.py         # Secure memory store
│   └── enterprise/          # Enterprise features (Phase 5)
│       ├── advanced_monitoring.py
│       ├── multi_user_collaboration.py
│       ├── rbac_abac_security.py
│       └── siem_monitoring.py
├── docs/                    # System documentation
├── tests/                   # Test suites
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

5. **Advanced Multimodal Persona**
   - Multi-modal input processing
   - Dynamic user adaptation
   - Learning feedback loops
   - Behavioral analysis integration

6. **Enterprise-Grade Features**
   - Advanced monitoring and health checks
   - Multi-user collaboration capabilities
   - RBAC/ABAC security framework
   - SIEM monitoring and threat detection
   - Comprehensive error handling

## Phase Status

- **Phase 1-4**: ✅ Complete - Core system, Vault, Synapse, and Alden integration
- **Phase 5**: ✅ Complete - Enterprise features implementation (63% test success rate)
- **Phase 6**: 📋 Planned - Test refinement, security hardening, performance optimization

## Compliance

This implementation follows:
- **PLATINUM_BLOCKERS.md**: Ethical safety rails and dependency mitigation
- **System Documentation**: Architecture constraints and requirements
- **Zero-Trust Principles**: Local-first, no external dependencies
- **User Sovereignty**: User always has final authority
- **Enterprise Standards**: Security, monitoring, and collaboration requirements

## Next Steps

This scaffold provides the foundation for implementing:
1. Vault (secure memory store)
2. Core (agent orchestration)
3. Individual persona modules (Alden, Alice, Mimic)
4. Synapse (external gateway)
5. Sentry (security and audit)
6. Advanced multimodal persona features

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
- **Alden**: Reflection, feedback, and LLM integration with advanced multimodal capabilities
- **Vault**: Secure, encrypted memory—per persona and communal
- **Mimic**: Extensible persona and plugin system with sandboxing and audit
- **Sentry**: Comprehensive system logging, audit export, anomaly detection (local only, privacy-first)
- **Synapse**: Plugin management, manifest enforcement, secure extension
- **Advanced Multimodal Persona**: Multi-modal input processing, dynamic adaptation, and learning feedback loops

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
- **Persona Guide:** [`/docs/PERSONA_GUIDE.md`](./docs/PERSONA_GUIDE.md)
- **Platinum Blockers:** [`/docs/PLATINUM_BLOCKERS.md`](./docs/PLATINUM_BLOCKERS.md)
- **Model Context Protocol:** [`/docs/appendix_e_model_context_protocol_mcp_full_specification.md`](./docs/appendix_e_model_context_protocol_mcp_full_specification.md)
- **Developer & QA Checklists:** [`/docs/appendix_h_developer_qa_platinum_checklists.md`](./docs/appendix_h_developer_qa_platinum_checklists.md)
- **Full documentation index:** See `/docs/`

---

## Extending Synapse: Adding New Agent/Plugin Connections

All Synapse connections (external agents, plugins, APIs) are integrated via a standardized process:
- **Draft a PRD/Blueprint**: Use the template in /docs/SYNAPSE_INTEGRATION_TEMPLATE.md.
- **Document in /docs/**: Each integration has a dedicated supplement, e.g., /docs/SYNAPSE_<AGENT/PLUGIN>_SUPPLEMENT.md.
- **Register the Connection**: Update config/connection_registry.json or equivalent.
- **Implementation**: Use a feature branch: feature/synapse-<agent/connection>.
- **Review & Merge**: Full code, docs, and process review before merge.
- **Setup**: Use Synapse's connections wizard or custom setup config for dynamic registration (if implemented).

For details, see:

 Synapse Integration Template
 All Synapse Agent Supplements

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

