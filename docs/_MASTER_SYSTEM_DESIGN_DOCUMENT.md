# Hearthlink System Design Document
## Source of Truth - v1.1.0

**Document Version:** 1.0.0  
**Last Updated:** July 13, 2025  
**Status:** Living Document  
**Authors:** Development Team  
**Reviewers:** Product, Engineering, Security  

---

## 1. Executive Summary

### 1.1 System Overview
Hearthlink is an AI-powered desktop productivity system designed to provide intelligent, adaptive assistance through multiple specialized AI agents. The system enables natural language interaction, persistent memory, and contextual learning to support executive function, productivity enhancement, and personal development.

### 1.2 Core Value Proposition
- **Adaptive AI Companions**: Multiple specialized agents that learn and adapt to user preferences
- **Local-First Architecture**: All data and learning remains on the user's device
- **Executive Function Support**: Specialized tools for ADHD, productivity, and cognitive assistance
- **Voice-First Interaction**: Natural voice commands with intelligent routing
- **Extensible Framework**: Plugin architecture for custom functionality

### 1.3 Key Success Metrics
- User engagement retention >80% after 30 days
- Task completion rate improvement >40% for users with executive function challenges
- Voice command accuracy >95% for core functions
- System response time <500ms for all interactions

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Hearthlink Desktop                       │
├─────────────────────────────────────────────────────────────┤
│  Electron Shell + React Frontend                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Alden Agent   │   Alice Agent   │   Additional Agents     │
│ (Primary AI)    │ (Behavioral)    │  (Mimic, Sentry)       │
├─────────────────┼─────────────────┼─────────────────────────┤
│           Core Orchestration Engine                         │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Vault Storage  │   Memory Sys    │   Voice Processing      │
│  (SQLite)       │   (RAG/Vector)  │   (Speech/NLP)          │
├─────────────────┼─────────────────┼─────────────────────────┤
│           Synapse Security Gateway                          │
├─────────────────────────────────────────────────────────────┤
│  OS Integration Layer (Windows/macOS/Linux)                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Presentation Layer
- **Electron Shell**: Cross-platform desktop framework
- **React Frontend**: Component-based UI with TypeScript
- **Radial Interface**: Primary navigation paradigm
- **Voice Interface**: Speech recognition and synthesis

#### 2.2.2 Agent Layer
- **Alden**: Primary conversational AI and task coordinator
- **Alice**: Behavioral analysis and context awareness
- **Mimic**: Adaptive persona and role-playing capability
- **Sentry**: Security monitoring and compliance oversight

#### 2.2.3 Core Services
- **Core Orchestration**: Agent communication and session management
- **Memory Management**: Persistent storage and retrieval
- **Voice Processing**: Speech-to-text and natural language understanding
- **Project Command**: Task and project management workflows

#### 2.2.4 Data Layer
- **Vault**: Encrypted local storage (SQLite-based)
- **Memory Slices**: Persona-specific memory storage
- **Session Logs**: Conversation and interaction history
- **Configuration**: User preferences and system settings

#### 2.2.5 Security Layer
- **Synapse Gateway**: External API security and sandboxing
- **Audit Logger**: Security event tracking
- **Credential Manager**: Encrypted credential storage
- **Permission System**: Role-based access control

### 2.3 Technology Stack

#### Frontend
- **React 18.2.0**: Primary UI framework
- **TypeScript 4.9.5**: Type safety and development experience
- **Electron 28.0.0**: Desktop application framework
- **Tailwind CSS**: Utility-first styling framework
- **Lucide React**: Icon library

#### Backend
- **Python 3.10+**: Primary backend language
- **FastAPI**: REST API framework
- **SQLite**: Local database storage
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization

#### AI/ML Stack
- **Local LLM Integration**: Ollama, llama.cpp support
- **Vector Search**: FAISS/Chroma for semantic search
- **Speech Processing**: Web Speech API, SpeechRecognition
- **Natural Language**: spaCy, NLTK for text processing

#### Development Tools
- **Node.js 18+**: JavaScript runtime
- **npm/yarn**: Package management
- **ESLint/Prettier**: Code quality tools
- **Jest/React Testing Library**: Testing frameworks
- **Electron Builder**: Application packaging

---

## 3. Agent Specifications

### 3.1 Alden - Primary AI Companion

#### 3.1.1 Purpose
Evolutionary companion AI focused on executive function, cognitive partnership, and adaptive growth support.

#### 3.1.2 Core Capabilities
- **Executive Function Support**: Task breakdown, prioritization, scheduling
- **Learning & Adaptation**: Personality trait evolution based on interaction patterns
- **Memory Integration**: Access to all conversation history and learned preferences
- **Natural Language Processing**: Advanced understanding of context and intent
- **Project Coordination**: Integration with Project Command for complex task management

#### 3.1.3 Personality Framework
```typescript
interface AldenPersonality {
  traits: {
    openness: number;           // 0-100
    conscientiousness: number;  // 0-100
    extraversion: number;       // 0-100
    agreeableness: number;      // 0-100
    emotional_stability: number; // 0-100
  };
  motivation_style: 'supportive' | 'challenging' | 'collaborative' | 'directive';
  trust_level: number;          // 0.0-1.0
  adaptation_rate: number;      // How quickly personality adjusts
}
```

#### 3.1.4 Memory Schema
- **Episodic Memory**: Specific conversation events and context
- **Semantic Memory**: General knowledge and learned facts
- **Procedural Memory**: Task patterns and workflow preferences
- **Relationship Memory**: Trust levels, correction events, user preferences

### 3.2 Alice - Behavioral Analysis Agent

#### 3.2.1 Purpose
Behavioral profile builder and context awareness engine that enhances communication effectiveness.

#### 3.2.2 Core Capabilities
- **Communication Pattern Analysis**: Cadence, tone, formality detection
- **Emotional State Recognition**: Mood and sentiment tracking
- **Behavioral Coaching**: Communication strategy recommendations
- **Meta-Pattern Detection**: Long-term behavioral trend analysis

#### 3.2.3 Analysis Framework
```typescript
interface BehavioralProfile {
  communication: {
    cadence: number;           // Words per minute average
    formality_level: number;   // 1-5 scale
    sentiment_baseline: number; // -1 to 1
    preferred_interaction_style: string;
  };
  patterns: {
    peak_productivity_hours: string[];
    common_cognitive_distortions: string[];
    stress_indicators: string[];
    motivation_triggers: string[];
  };
}
```

### 3.3 Additional Agents

#### Mimic - Adaptive Persona Agent
- **Purpose**: Dynamic role-playing and perspective-taking
- **Capabilities**: Persona switching, scenario simulation, creative problem-solving
- **Use Cases**: Brainstorming, perspective-taking, role-based assistance

#### Sentry - Security & Compliance Agent
- **Purpose**: Security monitoring and compliance oversight
- **Capabilities**: Threat detection, audit logging, permission management
- **Use Cases**: Security alerts, compliance reporting, access control

---

## 4. Data Architecture

### 4.1 Database Design

#### 4.1.1 SQLite Schema
```sql
-- Core agent table
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory slices for persona-specific storage
CREATE TABLE memory_slices (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES agents(id),
    user_id TEXT NOT NULL,
    slice_type TEXT NOT NULL, -- episodic, semantic, procedural
    content TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    embedding BLOB, -- Vector embeddings for similarity search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session management
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_id TEXT REFERENCES agents(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    context JSON
);

-- Conversation logs
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    user_id TEXT NOT NULL,
    agent_id TEXT REFERENCES agents(id),
    message_type TEXT NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.2 Memory Management Strategy
- **Hierarchical Importance**: Memory importance scoring (0.0-1.0)
- **Temporal Decay**: Older memories gradually decrease in importance
- **Contextual Relevance**: Vector similarity search for memory retrieval
- **User Control**: All memories are reviewable and editable by users

### 4.2 Configuration Management

#### 4.2.1 Configuration Structure
```
config/
├── core_config.json        # Core system settings
├── agent_config.json       # Agent-specific configurations
├── llm_config.json         # LLM backend settings
├── voice_config.json       # Voice processing settings
├── security_config.json    # Security and permissions
└── user_preferences.json   # User-specific settings
```

#### 4.2.2 Environment Variables
```bash
# Backend Configuration
HEARTHLINK_DB_PATH=./hearthlink_data/hearthlink.db
HEARTHLINK_LOG_LEVEL=INFO
HEARTHLINK_BACKEND_PORT=8888

# LLM Configuration
LLM_BACKEND_TYPE=local  # local, openai, anthropic
LLM_MODEL_PATH=./models/llama-2-7b-chat.gguf
LLM_API_KEY=sk-...

# Security Configuration
HEARTHLINK_ENCRYPTION_KEY=base64_encoded_key
HEARTHLINK_AUDIT_ENABLED=true
```

---

## 5. Security Architecture

### 5.1 Security Principles

#### 5.1.1 Core Security Tenets
- **Local-First**: All sensitive data remains on user's device
- **Zero-Trust**: Every component validates permissions and identity
- **Encryption at Rest**: All stored data is encrypted
- **Audit Trail**: Complete logging of all security-relevant events
- **Principle of Least Privilege**: Minimal permissions for all components

#### 5.1.2 Threat Model
- **Data Exfiltration**: Protection against unauthorized data access
- **Code Injection**: Sandboxing and input validation
- **Privilege Escalation**: Role-based access control
- **Social Engineering**: User education and secure defaults

### 5.2 Synapse Security Gateway

#### 5.2.1 Purpose
Secure boundary between Hearthlink and external services, providing controlled access to internet resources.

#### 5.2.2 Security Controls
- **Request Filtering**: URL allowlisting and content type validation
- **Response Sanitization**: XSS and malware scanning
- **Credential Isolation**: Encrypted credential storage and injection
- **Rate Limiting**: API request throttling and abuse prevention
- **Audit Logging**: Complete request/response logging

### 5.3 Authentication & Authorization

#### 5.3.1 User Authentication
- **Local Authentication**: PIN/password for sensitive operations
- **Biometric Support**: Fingerprint/face recognition where available
- **Session Management**: Secure session tokens with timeout

#### 5.3.2 Component Authorization
```typescript
interface PermissionMatrix {
  agent: {
    vault_read: boolean;
    vault_write: boolean;
    cross_agent_communication: boolean;
    external_api_access: boolean;
  };
  user: {
    agent_configuration: boolean;
    memory_export: boolean;
    security_settings: boolean;
  };
}
```

---

## 6. Integration Architecture

### 6.1 Internal Integration

#### 6.1.1 Inter-Agent Communication
- **Message Bus**: Central communication hub for agent coordination
- **Event System**: Asynchronous event publishing and subscription
- **Shared Context**: Common session and user context across agents
- **Permission Mediation**: All cross-agent access requires explicit permission

#### 6.1.2 Core Service Integration
```typescript
interface CoreServices {
  orchestration: OrchestrationEngine;
  memory: MemoryManager;
  voice: VoiceProcessor;
  security: SecurityManager;
  configuration: ConfigurationService;
}
```

### 6.2 External Integration

#### 6.2.1 LLM Backend Integration
- **Local Models**: Ollama, llama.cpp, GPT4All support
- **Cloud APIs**: OpenAI, Anthropic, Cohere integration (optional)
- **Model Switching**: Dynamic model selection based on task requirements
- **Fallback Strategy**: Graceful degradation when preferred models unavailable

#### 6.2.2 Operating System Integration
- **Notifications**: Native OS notification support
- **File System**: Secure file access with user permission
- **Clipboard**: Clipboard integration for productivity features
- **Global Shortcuts**: System-wide hotkey support

---

## 7. Performance & Scalability

### 7.1 Performance Requirements

#### 7.1.1 Response Time Targets
- **Voice Recognition**: <200ms for speech-to-text
- **Agent Response**: <500ms for simple queries
- **Complex Reasoning**: <2s for multi-step tasks
- **Memory Retrieval**: <100ms for similarity search
- **UI Interactions**: <16ms for 60fps rendering

#### 7.1.2 Resource Utilization
- **Memory Usage**: <2GB total system memory
- **CPU Usage**: <10% during idle, <50% during active use
- **Storage**: <500MB for base installation, growing with user data
- **Network**: Minimal for local-only operation

### 7.2 Scalability Considerations

#### 7.2.1 Data Growth Management
- **Memory Compression**: Automatic compression of older memories
- **Selective Retention**: Importance-based memory pruning
- **Export/Archive**: User-controlled data archiving
- **Index Optimization**: Efficient database indexing strategies

#### 7.2.2 Computational Scaling
- **Background Processing**: Non-blocking async operations
- **Resource Pooling**: Shared computational resources across agents
- **Progressive Enhancement**: Feature availability based on system capabilities

---

## 8. Deployment Architecture

### 8.1 Distribution Strategy

#### 8.1.1 Desktop Application
- **Electron Packaging**: Cross-platform desktop application
- **Auto-Updates**: Secure automatic update mechanism
- **Offline Installation**: Complete offline installation package
- **Portable Mode**: USB-installable portable version

#### 8.1.2 Platform Support
- **Windows**: Windows 10/11 (x64)
- **macOS**: macOS 10.15+ (Intel/Apple Silicon)
- **Linux**: Ubuntu 20.04+, Fedora 35+, Arch Linux

### 8.2 Installation & Setup

#### 8.2.1 Installation Process
```
1. Download installer package
2. Run security verification
3. Install application files
4. Initialize local database
5. Configure basic settings
6. Download/configure LLM backend
7. Complete setup wizard
```

#### 8.2.2 First-Run Experience
- **Welcome Tutorial**: Interactive system introduction
- **Agent Introductions**: Meet each AI agent
- **Preference Configuration**: Basic user preferences
- **Voice Calibration**: Speech recognition training
- **Privacy Settings**: Data handling preferences

---

## 9. Monitoring & Observability

### 9.1 Logging Strategy

#### 9.1.1 Log Categories
- **Application Logs**: General application events and errors
- **Agent Logs**: Agent-specific actions and decisions
- **Security Logs**: Security events and audit trail
- **Performance Logs**: Performance metrics and bottlenecks
- **User Interaction Logs**: User behavior and usage patterns (anonymized)

#### 9.1.2 Log Format
```json
{
  "timestamp": "2025-07-13T10:30:00Z",
  "level": "INFO",
  "component": "alden",
  "event": "memory_retrieval",
  "session_id": "sess_123",
  "user_id": "user_456",
  "metadata": {
    "query": "meeting preparation",
    "memories_found": 5,
    "response_time_ms": 45
  }
}
```

### 9.2 Metrics & Analytics

#### 9.2.1 System Metrics
- **Response Times**: Agent response latency percentiles
- **Error Rates**: Error frequency by component
- **Resource Usage**: CPU, memory, storage utilization
- **User Engagement**: Session length, feature usage
- **Agent Effectiveness**: Task completion rates, user satisfaction

#### 9.2.2 Privacy-Preserving Analytics
- **Local Processing**: All analytics computed locally
- **Aggregated Data**: Only anonymized, aggregated insights
- **User Control**: Complete analytics opt-out capability
- **Data Minimization**: Minimal data collection principles

---

## 10. Compliance & Governance

### 10.1 Privacy Compliance

#### 10.1.1 Data Protection Principles
- **GDPR Compliance**: Full GDPR compliance for EU users
- **CCPA Compliance**: California Consumer Privacy Act compliance
- **Local Processing**: No cloud processing of personal data
- **User Rights**: Complete data portability and deletion rights

#### 10.1.2 Data Handling Policies
- **Collection Minimization**: Only collect necessary data
- **Purpose Limitation**: Data used only for stated purposes
- **Retention Limits**: Automatic deletion of old data
- **Transparency**: Clear data usage documentation

### 10.2 Security Compliance

#### 10.2.1 Security Standards
- **Encryption Standards**: AES-256 for data at rest, TLS 1.3 for data in transit
- **Access Controls**: Role-based access control (RBAC)
- **Audit Requirements**: Complete audit trail for all operations
- **Incident Response**: Defined security incident response procedures

---

## 11. Future Roadmap

### 11.1 Planned Enhancements

#### 11.1.1 Phase 2 Features (Q3 2025)
- **Multi-Modal Input**: Vision and document processing
- **Advanced Memory**: Graph-based knowledge representation
- **Plugin Ecosystem**: Third-party plugin development framework
- **Mobile Companion**: Mobile app for limited functionality

#### 11.1.2 Phase 3 Features (Q4 2025)
- **Collaborative AI**: Multi-user shared agents
- **Advanced Analytics**: Deeper insight and trend analysis
- **Enterprise Features**: Team management and deployment
- **API Platform**: External API for third-party integration

### 11.2 Technology Evolution

#### 11.2.1 AI/ML Improvements
- **Model Optimization**: Smaller, faster, more capable models
- **Multimodal Integration**: Vision, audio, and text processing
- **Reasoning Enhancement**: Better logical reasoning capabilities
- **Personalization**: More sophisticated user adaptation

#### 11.2.2 Platform Expansion
- **Web Version**: Browser-based limited functionality
- **Server Version**: Self-hosted multi-user deployment
- **Cloud Sync**: Optional encrypted cloud synchronization
- **Integration APIs**: Deep OS and application integration

---

## 12. Appendices

### Appendix A: Glossary
- **Agent**: Specialized AI entity with specific capabilities and personality
- **Memory Slice**: Discrete unit of stored information associated with an agent
- **Vault**: Encrypted local storage system for sensitive data
- **Core**: Central orchestration system managing agent communication
- **Synapse**: Security gateway for external communications

### Appendix B: Reference Architecture Diagrams
[See accompanying architectural diagrams in docs/diagrams/]

### Appendix C: Configuration Examples
[See accompanying configuration examples in docs/examples/]

### Appendix D: API Documentation
[See accompanying API documentation in docs/api/]

---

**Document Control**
- **Version**: 1.0.0
- **Classification**: Internal Use
- **Review Cycle**: Quarterly
- **Next Review**: October 2025
- **Owner**: Engineering Team
- **Approvers**: Product, Engineering, Security Leadership

---

*This document serves as the authoritative source of truth for Hearthlink system design and architecture. All implementation decisions should reference and align with this document.*