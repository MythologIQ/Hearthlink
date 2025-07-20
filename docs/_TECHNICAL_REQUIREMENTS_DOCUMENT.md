# Hearthlink Technical Requirements Document (TRD)
## Source of Truth - v1.1.0

**Document Version:** 1.0.0  
**Last Updated:** July 13, 2025  
**Status:** Approved  
**Technical Lead:** Engineering Team  
**Stakeholders:** Engineering, DevOps, Security, QA  

---

## 1. Technical Overview

### 1.1 System Requirements Summary
Hearthlink is a cross-platform desktop application built on Electron with React frontend and Python backend services. The system provides AI-powered productivity assistance through a multi-agent architecture with local-first data processing and storage.

### 1.2 Architecture Principles
- **Local-First**: All user data processing and storage occurs locally
- **Privacy by Design**: No personal data transmitted to external services without explicit consent
- **Modularity**: Loosely coupled components with clear interfaces
- **Extensibility**: Plugin architecture for future enhancements
- **Accessibility**: WCAG 2.1 AA compliance for all interfaces
- **Performance**: Sub-500ms response times for core interactions

### 1.3 Technology Stack Overview
```
Frontend:    React 18.2+ / TypeScript 4.9+ / Electron 28.0+
Backend:     Python 3.10+ / FastAPI / SQLite
AI/ML:       Local LLM (Ollama/llama.cpp) / Speech APIs
Build:       Node.js 18+ / npm/yarn / Electron Builder
Testing:     Jest / React Testing Library / pytest
```

---

## 2. System Architecture

### 2.1 Component Architecture

#### 2.1.1 Frontend Architecture
```
src/
├── components/           # React components
│   ├── agents/          # Agent-specific interfaces
│   ├── core/            # Core system components
│   ├── ui/              # Shared UI components
│   └── voice/           # Voice interface components
├── hooks/               # React hooks
├── services/            # Frontend services
├── utils/               # Utility functions
├── types/               # TypeScript definitions
└── assets/              # Static assets
```

**React Component Hierarchy**
```typescript
App
├── RouterProvider
├── AudioProvider
├── AgentProvider
├── ConfigProvider
└── Layout
    ├── Header
    ├── Navigation (Radial)
    ├── MainContent
    │   ├── AgentInterface
    │   ├── ChatInterface
    │   └── MemoryPanel
    └── Footer
```

#### 2.1.2 Backend Architecture
```
backend/
├── api/                 # FastAPI routes
│   ├── agents/         # Agent endpoints
│   ├── memory/         # Memory management
│   ├── config/         # Configuration
│   └── auth/           # Authentication
├── services/           # Business logic
│   ├── agent_service.py
│   ├── memory_service.py
│   └── voice_service.py
├── models/             # Data models
├── database/           # Database layer
├── ai/                 # AI/ML integration
└── utils/              # Utilities
```

#### 2.1.3 Data Architecture
```sql
-- Core database schema
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_slices (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES agents(id),
    user_id TEXT NOT NULL,
    slice_type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    embedding BLOB,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    agent_id TEXT REFERENCES agents(id),
    user_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    context JSON
);
```

### 2.2 Inter-Process Communication

#### 2.2.1 Electron IPC Channels
```typescript
// Main process channels
interface IPCChannels {
  // Agent communication
  'agent:query': (data: QueryRequest) => Promise<QueryResponse>;
  'agent:memory': (data: MemoryRequest) => Promise<MemoryResponse>;
  
  // Configuration
  'config:get': (key: string) => Promise<any>;
  'config:set': (key: string, value: any) => Promise<void>;
  
  // Voice interface
  'voice:start': () => Promise<void>;
  'voice:stop': () => Promise<void>;
  'voice:command': (text: string) => Promise<CommandResponse>;
  
  // Security
  'security:encrypt': (data: string) => Promise<string>;
  'security:decrypt': (data: string) => Promise<string>;
}
```

#### 2.2.2 Frontend-Backend API
```typescript
// REST API endpoints
interface APIEndpoints {
  // Agent management
  GET    /api/agents                    // List agents
  GET    /api/agents/{id}              // Get agent details
  POST   /api/agents/{id}/query        // Send query to agent
  
  // Memory management
  GET    /api/memory/{agent_id}        // Get agent memories
  POST   /api/memory/{agent_id}        // Create memory
  PUT    /api/memory/{agent_id}/{id}   // Update memory
  DELETE /api/memory/{agent_id}/{id}   // Delete memory
  
  // Session management
  GET    /api/sessions                 // List sessions
  POST   /api/sessions                 // Create session
  GET    /api/sessions/{id}            // Get session details
  
  // System
  GET    /api/status                   // System health check
  GET    /api/config                   // Get configuration
  POST   /api/config                   // Update configuration
}
```

---

## 3. Detailed Component Specifications

### 3.1 Frontend Components

#### 3.1.1 Core Components

**AldenEnhancedInterface Component**
```typescript
interface AldenEnhancedInterfaceProps {
  accessibilitySettings: AccessibilitySettings;
  onVoiceCommand: (command: string) => void;
}

interface AldenState {
  messages: Message[];
  isConnected: boolean;
  systemStatus: SystemStatus;
  activeScreen: string;
  isRadialOpen: boolean;
  activeSubmenu: string | null;
  relevantMemories: MemorySlice[];
}

// Key methods:
- checkBackendStatus(): Promise<SystemStatus>
- handleSendMessage(content: string): Promise<void>
- renderRadialMenu(): React.ReactElement
- renderScreen(): React.ReactElement
```

**Radial Navigation Component**
```typescript
interface RadialMenuProps {
  isOpen: boolean;
  onToggle: () => void;
  items: MenuItem[];
  onItemSelect: (itemId: string) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: string;
  angle: number;
  submenu?: MenuItem[];
}

// Features:
- Animated menu appearance/disappearance
- Nested submenu support
- Keyboard navigation
- Voice command integration
```

**Voice Interface Component**
```typescript
interface VoiceInterfaceProps {
  isEnabled: boolean;
  onTranscript: (text: string) => void;
  onCommand: (command: string) => void;
  language: string;
}

// Features:
- Continuous speech recognition
- Command keyword detection
- Multiple language support
- Visual feedback for listening state
```

#### 3.1.2 Agent-Specific Components

**Agent Chat Interface**
```typescript
interface AgentChatProps {
  agentId: string;
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  isTyping: boolean;
  relevantMemories: MemorySlice[];
}

// Features:
- Agent-specific styling and personality
- Memory context display
- Typing indicators
- Message threading
```

### 3.2 Backend Services

#### 3.2.1 Agent Service Architecture

**Base Agent Interface**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.memory_service = MemoryService(agent_id)
    
    @abstractmethod
    async def process_query(self, query: QueryRequest) -> QueryResponse:
        """Process user query and return response"""
        pass
    
    @abstractmethod
    async def update_memory(self, interaction: Interaction) -> None:
        """Update agent memory with interaction"""
        pass
    
    @abstractmethod
    def get_personality_context(self) -> Dict[str, Any]:
        """Return current personality context"""
        pass
```

**Alden Agent Implementation**
```python
class AldenAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.llm_client = LocalLLMClient(config.get('llm_config'))
        self.personality = PersonalityManager(agent_id)
    
    async def process_query(self, query: QueryRequest) -> QueryResponse:
        # Retrieve relevant memories
        memories = await self.memory_service.search_memories(
            query.user_id, query.query
        )
        
        # Get personality context
        personality_context = self.personality.get_context()
        
        # Generate response using LLM
        response = await self.llm_client.generate_response(
            query=query.query,
            memories=memories,
            personality=personality_context,
            user_context=query.user_context
        )
        
        # Update memory with interaction
        await self.update_memory(Interaction(
            query=query.query,
            response=response,
            memories_used=memories
        ))
        
        return QueryResponse(
            response=response,
            confidence=0.95,
            relevant_memories=memories,
            personality_context=personality_context
        )
```

#### 3.2.2 Memory Management Service

**Memory Service Implementation**
```python
class MemoryService:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.database = DatabaseManager()
        self.vector_store = VectorStore()
    
    async def create_memory(self, memory: MemorySliceCreate) -> MemorySlice:
        """Create new memory slice"""
        # Generate embedding for semantic search
        embedding = await self.vector_store.embed_text(memory.content)
        
        # Store in database
        memory_slice = await self.database.create_memory_slice(
            agent_id=self.agent_id,
            user_id=memory.user_id,
            slice_type=memory.slice_type,
            content=memory.content,
            importance=memory.importance,
            embedding=embedding
        )
        
        return memory_slice
    
    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 10
    ) -> List[MemorySlice]:
        """Search memories using semantic similarity"""
        # Generate query embedding
        query_embedding = await self.vector_store.embed_text(query)
        
        # Perform similarity search
        similar_memories = await self.database.search_memories_by_embedding(
            agent_id=self.agent_id,
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit
        )
        
        return similar_memories
```

#### 3.2.3 LLM Integration Service

**Local LLM Client**
```python
class LocalLLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.model_path = config.get('model_path')
        self.backend_type = config.get('backend_type', 'ollama')
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on backend type"""
        if self.backend_type == 'ollama':
            return OllamaClient(self.model_path)
        elif self.backend_type == 'llama_cpp':
            return LlamaCppClient(self.model_path)
        else:
            raise ValueError(f"Unsupported backend: {self.backend_type}")
    
    async def generate_response(
        self,
        query: str,
        memories: List[MemorySlice],
        personality: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """Generate response using local LLM"""
        prompt = self._build_prompt(query, memories, personality, user_context)
        
        response = await self.client.generate(
            prompt=prompt,
            max_tokens=512,
            temperature=0.7,
            stop_sequences=["Human:", "User:"]
        )
        
        return response.strip()
    
    def _build_prompt(
        self,
        query: str,
        memories: List[MemorySlice],
        personality: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """Build context-aware prompt for LLM"""
        prompt_parts = [
            "You are Alden, an AI assistant with the following personality:",
            f"Traits: {personality.get('traits', {})}",
            f"Style: {personality.get('motivation_style', 'supportive')}",
            "",
            "Relevant memories from past conversations:",
        ]
        
        for memory in memories[:5]:  # Limit context length
            prompt_parts.append(f"- {memory.content}")
        
        prompt_parts.extend([
            "",
            f"User: {query}",
            "Alden:"
        ])
        
        return "\n".join(prompt_parts)
```

### 3.3 Voice Processing System

#### 3.3.1 Speech Recognition
```typescript
interface SpeechRecognitionService {
  start(): Promise<void>;
  stop(): Promise<void>;
  onResult: (transcript: string) => void;
  onError: (error: Error) => void;
  onEnd: () => void;
}

class WebSpeechRecognition implements SpeechRecognitionService {
  private recognition: SpeechRecognition;
  
  constructor(config: VoiceConfig) {
    this.recognition = new (window as any).webkitSpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = config.language || 'en-US';
  }
  
  async start(): Promise<void> {
    this.recognition.start();
  }
  
  async stop(): Promise<void> {
    this.recognition.stop();
  }
}
```

#### 3.3.2 Natural Language Understanding
```python
class NLUService:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
    
    async def process_transcript(self, transcript: str) -> NLUResult:
        """Process speech transcript for intent and entities"""
        # Clean and normalize transcript
        normalized_text = self._normalize_text(transcript)
        
        # Extract intent
        intent = await self.intent_classifier.classify(normalized_text)
        
        # Extract entities
        entities = await self.entity_extractor.extract(normalized_text)
        
        return NLUResult(
            transcript=transcript,
            normalized_text=normalized_text,
            intent=intent,
            entities=entities,
            confidence=intent.confidence
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize speech transcript"""
        # Remove filler words, normalize punctuation, etc.
        return text.lower().strip()
```

---

## 4. Database Design

### 4.1 Schema Design

#### 4.1.1 Complete Database Schema
```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Agents table
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('alden', 'alice', 'mimic', 'sentry')),
    config JSON DEFAULT '{}',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for multi-user support)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    display_name TEXT,
    preferences JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory slices
CREATE TABLE memory_slices (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slice_type TEXT NOT NULL CHECK (slice_type IN ('episodic', 'semantic', 'procedural')),
    content TEXT NOT NULL,
    importance REAL DEFAULT 0.5 CHECK (importance >= 0.0 AND importance <= 1.0),
    embedding BLOB,
    metadata JSON DEFAULT '{}',
    tags TEXT, -- Comma-separated tags for filtering
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- Sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    context JSON DEFAULT '{}',
    total_messages INTEGER DEFAULT 0,
    total_agents_used INTEGER DEFAULT 0
);

-- Conversations
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personality traits (for Alden and other adaptive agents)
CREATE TABLE personality_traits (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trait_name TEXT NOT NULL,
    trait_value REAL NOT NULL CHECK (trait_value >= 0.0 AND trait_value <= 100.0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, user_id, trait_name)
);

-- System configuration
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT DEFAULT 'string' CHECK (type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for security and debugging
CREATE TABLE audit_log (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    agent_id TEXT REFERENCES agents(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    old_values JSON,
    new_values JSON,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_memory_slices_agent_user ON memory_slices(agent_id, user_id);
CREATE INDEX idx_memory_slices_type ON memory_slices(slice_type);
CREATE INDEX idx_memory_slices_importance ON memory_slices(importance DESC);
CREATE INDEX idx_memory_slices_accessed ON memory_slices(accessed_at DESC);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_agent ON conversations(agent_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_audit_log_user_action ON audit_log(user_id, action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
```

#### 4.1.2 Data Access Layer
```python
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """Initialize SQLite connection pool"""
        self.pool = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        self.pool.row_factory = sqlite3.Row
        
        # Enable foreign keys and other pragmas
        self.pool.execute("PRAGMA foreign_keys = ON")
        self.pool.execute("PRAGMA journal_mode = WAL")
        self.pool.execute("PRAGMA synchronous = NORMAL")
    
    async def create_memory_slice(
        self,
        agent_id: str,
        user_id: str,
        slice_type: str,
        content: str,
        importance: float = 0.5,
        embedding: bytes = None,
        metadata: Dict[str, Any] = None
    ) -> MemorySlice:
        """Create a new memory slice"""
        memory_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO memory_slices 
        (id, agent_id, user_id, slice_type, content, importance, embedding, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.pool.execute(query, (
            memory_id, agent_id, user_id, slice_type, content,
            importance, embedding, json.dumps(metadata or {})
        ))
        
        return await self.get_memory_slice(memory_id)
    
    async def search_memories_by_embedding(
        self,
        agent_id: str,
        user_id: str,
        query_embedding: np.ndarray,
        limit: int = 10,
        min_importance: float = 0.1
    ) -> List[MemorySlice]:
        """Search memories using vector similarity"""
        query = """
        SELECT id, agent_id, user_id, slice_type, content, importance, 
               metadata, created_at, accessed_at, access_count
        FROM memory_slices 
        WHERE agent_id = ? AND user_id = ? AND importance >= ?
        ORDER BY importance DESC, accessed_at DESC
        LIMIT ?
        """
        
        rows = self.pool.execute(query, (agent_id, user_id, min_importance, limit * 2))
        
        memories = []
        for row in rows:
            # Calculate similarity if embedding exists
            if row['embedding']:
                stored_embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                if similarity > 0.7:  # Similarity threshold
                    memories.append(MemorySlice.from_row(row))
        
        # Update access timestamps
        memory_ids = [m.id for m in memories[:limit]]
        if memory_ids:
            placeholders = ",".join("?" * len(memory_ids))
            self.pool.execute(
                f"UPDATE memory_slices SET accessed_at = CURRENT_TIMESTAMP, "
                f"access_count = access_count + 1 WHERE id IN ({placeholders})",
                memory_ids
            )
        
        return memories[:limit]
```

### 4.2 Data Models

#### 4.2.1 Pydantic Data Models
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    ALDEN = "alden"
    ALICE = "alice"
    MIMIC = "mimic"
    SENTRY = "sentry"

class MemorySliceType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Core data models
class MemorySlice(BaseModel):
    id: str
    agent_id: str
    user_id: str
    slice_type: MemorySliceType
    content: str
    importance: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Optional[str] = None
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0

class Agent(BaseModel):
    id: str
    name: str
    type: AgentType
    config: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"
    created_at: datetime
    updated_at: datetime

class Session(BaseModel):
    id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    total_messages: int = 0
    total_agents_used: int = 0

class Conversation(BaseModel):
    id: str
    session_id: str
    agent_id: str
    user_id: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class PersonalityTrait(BaseModel):
    id: str
    agent_id: str
    user_id: str
    trait_name: str
    trait_value: float = Field(ge=0.0, le=100.0)
    updated_at: datetime

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    session_id: str
    user_id: str
    include_memory: bool = True
    max_memories: int = 10

class QueryResponse(BaseModel):
    response: str
    confidence: float
    relevant_memories: List[MemorySlice]
    personality_context: Dict[str, Any]
    session_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SystemStatus(BaseModel):
    service: str = "hearthlink"
    status: str = "healthy"
    timestamp: datetime
    llm_available: bool = True
    database_available: bool = True
    vector_db_available: bool = False
    knowledge_graph_available: bool = False
    backend_healthy: bool = True
    memory_count: int = 0
    database_type: str = "sqlite"
    database_path: str
```

---

## 5. Security Requirements

### 5.1 Data Security

#### 5.1.1 Encryption Requirements
```python
class EncryptionManager:
    def __init__(self, encryption_key: bytes):
        self.cipher_suite = Fernet(encryption_key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive user data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate new encryption key"""
        return Fernet.generate_key()

# Database encryption for sensitive fields
class SecureMemorySlice(MemorySlice):
    @classmethod
    def from_db_row(cls, row: sqlite3.Row, encryption_manager: EncryptionManager):
        """Create memory slice from database row with decryption"""
        data = dict(row)
        
        # Decrypt sensitive content
        if data.get('content'):
            data['content'] = encryption_manager.decrypt_sensitive_data(data['content'])
        
        return cls(**data)
    
    def to_db_dict(self, encryption_manager: EncryptionManager) -> Dict[str, Any]:
        """Convert to database dict with encryption"""
        data = self.dict()
        
        # Encrypt sensitive content
        data['content'] = encryption_manager.encrypt_sensitive_data(self.content)
        
        return data
```

#### 5.1.2 Access Control System
```python
from enum import Enum
from typing import Set

class Permission(str, Enum):
    READ_MEMORY = "memory:read"
    WRITE_MEMORY = "memory:write"
    DELETE_MEMORY = "memory:delete"
    AGENT_QUERY = "agent:query"
    AGENT_CONFIG = "agent:config"
    SYSTEM_CONFIG = "system:config"
    USER_ADMIN = "user:admin"

class Role(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    ADMIN = "admin"

class AccessControlManager:
    def __init__(self):
        self.role_permissions = {
            Role.USER: {
                Permission.READ_MEMORY,
                Permission.WRITE_MEMORY,
                Permission.DELETE_MEMORY,
                Permission.AGENT_QUERY
            },
            Role.AGENT: {
                Permission.READ_MEMORY,
                Permission.WRITE_MEMORY,
                Permission.AGENT_QUERY
            },
            Role.SYSTEM: {
                Permission.READ_MEMORY,
                Permission.WRITE_MEMORY,
                Permission.AGENT_QUERY,
                Permission.SYSTEM_CONFIG
            },
            Role.ADMIN: set(Permission)  # All permissions
        }
    
    def check_permission(
        self, 
        user_role: Role, 
        required_permission: Permission,
        resource_owner: str = None,
        requesting_user: str = None
    ) -> bool:
        """Check if role has required permission"""
        # Check basic role permissions
        if required_permission not in self.role_permissions.get(user_role, set()):
            return False
        
        # Additional checks for resource ownership
        if resource_owner and requesting_user:
            if resource_owner != requesting_user and user_role != Role.ADMIN:
                return False
        
        return True
    
    def require_permission(self, permission: Permission):
        """Decorator for API endpoints requiring specific permissions"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract user context from request
                user_role = kwargs.get('user_role', Role.USER)
                user_id = kwargs.get('user_id')
                resource_owner = kwargs.get('resource_owner')
                
                if not self.check_permission(user_role, permission, resource_owner, user_id):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient permissions: {permission}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

### 5.2 Network Security

#### 5.2.1 API Security Middleware
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
from collections import defaultdict

class SecurityMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app
        self.rate_limits = defaultdict(list)
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup security middleware"""
        # CORS configuration
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["electron://localhost", "http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # Rate limiting middleware
        @self.app.middleware("http")
        async def rate_limiting_middleware(request: Request, call_next):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old requests (older than 1 minute)
            self.rate_limits[client_ip] = [
                req_time for req_time in self.rate_limits[client_ip]
                if current_time - req_time < 60
            ]
            
            # Check rate limit (max 100 requests per minute)
            if len(self.rate_limits[client_ip]) >= 100:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
            
            # Add current request
            self.rate_limits[client_ip].append(current_time)
            
            response = await call_next(request)
            return response
        
        # Request validation middleware
        @self.app.middleware("http")
        async def request_validation_middleware(request: Request, call_next):
            # Validate content length
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 10_000_000:  # 10MB limit
                raise HTTPException(
                    status_code=413,
                    detail="Request too large"
                )
            
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            return response
```

#### 5.2.2 Audit Logging System
```python
class AuditLogger:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def log_action(
        self,
        user_id: Optional[str],
        agent_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log security-relevant action"""
        audit_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO audit_log 
        (id, user_id, agent_id, action, resource_type, resource_id, 
         old_values, new_values, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        await self.db_manager.execute(query, (
            audit_id, user_id, agent_id, action, resource_type, resource_id,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None,
            ip_address, user_agent
        ))
    
    async def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail with filters"""
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        
        if start_date:
            conditions.append("created_at >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            conditions.append("created_at <= ?")
            params.append(end_date.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM audit_log 
        WHERE {where_clause}
        ORDER BY created_at DESC 
        LIMIT ?
        """
        
        params.append(limit)
        
        rows = await self.db_manager.fetch_all(query, params)
        return [dict(row) for row in rows]
```

---

## 6. Performance Requirements

### 6.1 Response Time Requirements

#### 6.1.1 Performance Targets
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.targets = {
            'voice_recognition': 200,      # ms
            'simple_query': 500,           # ms
            'complex_query': 2000,         # ms
            'memory_search': 100,          # ms
            'ui_interaction': 16,          # ms (60fps)
            'database_query': 50,          # ms
            'agent_response': 500,         # ms
        }
    
    def measure_performance(self, operation_name: str):
        """Decorator to measure operation performance"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    self.record_metric(operation_name, duration_ms)
                    
                    # Alert if performance target exceeded
                    target = self.targets.get(operation_name)
                    if target and duration_ms > target:
                        logger.warning(
                            f"Performance target exceeded for {operation_name}: "
                            f"{duration_ms:.2f}ms > {target}ms"
                        )
            
            return wrapper
        return decorator
    
    def record_metric(self, operation: str, duration_ms: float):
        """Record performance metric"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append({
            'duration_ms': duration_ms,
            'timestamp': datetime.now()
        })
        
        # Keep only last 1000 measurements
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]
    
    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for operation"""
        if operation not in self.metrics:
            return {}
        
        durations = [m['duration_ms'] for m in self.metrics[operation]]
        
        return {
            'count': len(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'p95': numpy.percentile(durations, 95),
            'p99': numpy.percentile(durations, 99),
            'min': min(durations),
            'max': max(durations),
            'target': self.targets.get(operation, 0)
        }
```

#### 6.1.2 Memory Management
```python
class MemoryManager:
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.cache = {}
        self.cache_stats = defaultdict(int)
    
    def check_memory_usage(self):
        """Monitor memory usage and clean up if necessary"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.max_memory_mb:
            logger.warning(f"Memory usage high: {memory_mb:.1f}MB")
            self.cleanup_memory()
    
    def cleanup_memory(self):
        """Clean up memory caches and temporary data"""
        # Clear LRU cache entries
        cache_size_before = len(self.cache)
        
        # Remove least recently used items
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1].get('last_access', 0)
        )
        
        # Remove oldest 25% of items
        items_to_remove = len(sorted_items) // 4
        for key, _ in sorted_items[:items_to_remove]:
            del self.cache[key]
        
        logger.info(
            f"Memory cleanup: removed {cache_size_before - len(self.cache)} cache entries"
        )
        
        # Force garbage collection
        import gc
        gc.collect()
```

### 6.2 Scalability Considerations

#### 6.2.1 Database Optimization
```sql
-- Partitioning strategy for large tables
CREATE TABLE memory_slices_partition_template (
    LIKE memory_slices INCLUDING ALL
);

-- Indexes for query optimization
CREATE INDEX CONCURRENTLY idx_memory_slices_user_importance 
ON memory_slices(user_id, importance DESC, created_at DESC);

CREATE INDEX CONCURRENTLY idx_memory_slices_agent_type 
ON memory_slices(agent_id, slice_type, accessed_at DESC);

CREATE INDEX CONCURRENTLY idx_conversations_session_time 
ON conversations(session_id, created_at DESC);

-- Query optimization views
CREATE VIEW recent_memories AS
SELECT * FROM memory_slices 
WHERE created_at > datetime('now', '-30 days')
ORDER BY importance DESC, accessed_at DESC;

-- Database maintenance procedures
CREATE TRIGGER update_memory_access_time
AFTER SELECT ON memory_slices
BEGIN
    UPDATE memory_slices 
    SET accessed_at = CURRENT_TIMESTAMP,
        access_count = access_count + 1
    WHERE id = NEW.id;
END;
```

---

## 7. Testing Requirements

### 7.1 Testing Strategy

#### 7.1.1 Test Pyramid Structure
```
                    E2E Tests (5%)
                 ┌─────────────────┐
                 │  User Journeys  │
                 │  Integration    │
                 └─────────────────┘
                   
               Integration Tests (25%)
            ┌─────────────────────────┐
            │    API Tests           │
            │    Component Tests     │
            │    Database Tests      │
            └─────────────────────────┘
            
          Unit Tests (70%)
     ┌───────────────────────────────┐
     │     Service Logic Tests       │
     │     Utility Function Tests    │
     │     Component Unit Tests      │
     └───────────────────────────────┘
```

#### 7.1.2 Frontend Testing Requirements
```typescript
// Component testing with React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AldenEnhancedInterface from '../AldenEnhancedInterface';

describe('AldenEnhancedInterface', () => {
  const mockProps = {
    accessibilitySettings: {
      voiceFeedback: true,
      highContrast: false,
      fontSize: 'medium'
    },
    onVoiceCommand: jest.fn()
  };

  beforeEach(() => {
    // Mock backend connection
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        service: 'test',
        status: 'healthy',
        llm_available: true,
        database_available: true
      })
    });
  });

  test('renders main interface elements', async () => {
    render(<AldenEnhancedInterface {...mockProps} />);
    
    expect(screen.getByText(/ALDEN ENHANCED CONSTRUCT/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /radial menu/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ask me anything/i)).toBeInTheDocument();
  });

  test('opens and closes radial menu', async () => {
    const user = userEvent.setup();
    render(<AldenEnhancedInterface {...mockProps} />);
    
    const menuButton = screen.getByRole('button', { name: /radial menu/i });
    
    // Open menu
    await user.click(menuButton);
    expect(screen.getByText('Core Ops')).toBeInTheDocument();
    
    // Close menu
    await user.click(menuButton);
    await waitFor(() => {
      expect(screen.queryByText('Core Ops')).not.toBeInTheDocument();
    });
  });

  test('sends message and receives response', async () => {
    const user = userEvent.setup();
    
    // Mock successful API response
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          response: 'Hello! How can I help you today?',
          confidence: 0.95,
          relevant_memories: [],
          personality_context: {}
        })
      })
    );

    render(<AldenEnhancedInterface {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ask me anything/i);
    const sendButton = screen.getByRole('button', { name: /transmit/i });
    
    await user.type(input, 'Hello Alden');
    await user.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
    });
  });

  test('handles voice commands', async () => {
    const user = userEvent.setup();
    render(<AldenEnhancedInterface {...mockProps} />);
    
    // Simulate voice command
    fireEvent(window, new CustomEvent('voicecommand', {
      detail: { transcript: 'open dashboard' }
    }));
    
    expect(mockProps.onVoiceCommand).toHaveBeenCalledWith('open dashboard');
  });
});
```

#### 7.1.3 Backend Testing Requirements
```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api import app
from src.services.agent_service import AldenAgent
from src.database.database_manager import DatabaseManager

class TestAldenAgent:
    @pytest.fixture
    def agent(self):
        config = {
            'llm_config': {'model_path': 'test_model'},
            'personality_config': {'default_traits': {}}
        }
        return AldenAgent('test_agent', config)
    
    @pytest.fixture
    def mock_llm_client(self):
        with patch('src.services.agent_service.LocalLLMClient') as mock:
            mock_instance = Mock()
            mock_instance.generate_response.return_value = "Test response"
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.asyncio
    async def test_process_query_simple(self, agent, mock_llm_client):
        """Test simple query processing"""
        query_request = QueryRequest(
            query="Hello",
            session_id="test_session",
            user_id="test_user",
            include_memory=True
        )
        
        with patch.object(agent.memory_service, 'search_memories') as mock_search:
            mock_search.return_value = []
            
            response = await agent.process_query(query_request)
            
            assert response.response == "Test response"
            assert response.confidence > 0
            assert isinstance(response.relevant_memories, list)
    
    @pytest.mark.asyncio
    async def test_memory_integration(self, agent):
        """Test memory storage and retrieval"""
        # Create test memory
        memory = await agent.memory_service.create_memory(
            MemorySliceCreate(
                user_id="test_user",
                slice_type="episodic",
                content="User likes coffee in the morning",
                importance=0.8
            )
        )
        
        assert memory.id is not None
        assert memory.content == "User likes coffee in the morning"
        assert memory.importance == 0.8
        
        # Search for memory
        memories = await agent.memory_service.search_memories(
            user_id="test_user",
            query="morning routine",
            limit=5
        )
        
        assert len(memories) > 0
        assert any("coffee" in m.content for m in memories)

class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test system health endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "hearthlink"
        assert "status" in data
        assert "timestamp" in data
    
    def test_agent_query_endpoint(self, client):
        """Test agent query endpoint"""
        query_data = {
            "query": "What's the weather like?",
            "session_id": "test_session",
            "user_id": "test_user",
            "include_memory": True
        }
        
        with patch('src.api.agents.agent_service') as mock_service:
            mock_response = QueryResponse(
                response="I don't have access to weather data.",
                confidence=0.9,
                relevant_memories=[],
                personality_context={},
                session_id="test_session",
                timestamp=datetime.now()
            )
            mock_service.process_query.return_value = mock_response
            
            response = client.post("/api/agents/alden/query", json=query_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "response" in data
            assert data["confidence"] > 0
    
    def test_memory_crud_operations(self, client):
        """Test memory CRUD operations"""
        # Create memory
        memory_data = {
            "user_id": "test_user",
            "slice_type": "semantic",
            "content": "Python is a programming language",
            "importance": 0.7
        }
        
        response = client.post("/api/memory/alden", json=memory_data)
        assert response.status_code == 201
        
        memory_id = response.json()["id"]
        
        # Read memory
        response = client.get(f"/api/memory/alden/{memory_id}")
        assert response.status_code == 200
        assert response.json()["content"] == memory_data["content"]
        
        # Update memory
        update_data = {"importance": 0.9}
        response = client.put(f"/api/memory/alden/{memory_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["importance"] == 0.9
        
        # Delete memory
        response = client.delete(f"/api/memory/alden/{memory_id}")
        assert response.status_code == 204
```

### 7.2 Quality Assurance

#### 7.2.1 Code Quality Standards
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.35.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
        additional_dependencies:
          - eslint@8.35.0
          - @typescript-eslint/eslint-plugin@5.54.0
          - @typescript-eslint/parser@5.54.0
```

#### 7.2.2 Continuous Integration Pipeline
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run type checking
        run: npm run type-check
      
      - name: Run tests
        run: npm test -- --coverage --watchAll=false
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  backend-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements_dev.txt
      
      - name: Run linting
        run: |
          black --check .
          isort --check-only .
          flake8 .
          mypy .
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
      
      - name: Build frontend
        run: npm run build
      
      - name: Start backend
        run: |
          python simple_alden_backend.py &
          sleep 10
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Run E2E tests
        run: npm run test:e2e

  security-audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Run npm audit
        run: npm audit --audit-level=moderate
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run safety check
        run: |
          pip install safety
          safety check
      
      - name: Run CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: javascript, python
```

---

## 8. Documentation Requirements

### 8.1 Technical Documentation

#### 8.1.1 API Documentation Standards
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Hearthlink API",
    description="AI-powered productivity system API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str = Field(..., description="User query text", example="What's on my schedule today?")
    session_id: str = Field(..., description="Session identifier", example="sess_123")
    user_id: str = Field(..., description="User identifier", example="user_456")
    include_memory: bool = Field(True, description="Include relevant memories in response")
    max_memories: int = Field(10, description="Maximum number of memories to include", ge=1, le=50)

@app.post(
    "/api/agents/{agent_id}/query",
    response_model=QueryResponse,
    summary="Send query to agent",
    description="""
    Send a natural language query to a specific agent and receive an intelligent response.
    
    The agent will:
    1. Process the query using its specialized capabilities
    2. Search for relevant memories if requested
    3. Generate a personalized response based on learned patterns
    4. Update its memory with the interaction
    
    **Rate Limiting**: 100 requests per minute per user
    **Authentication**: Local session token required
    """,
    tags=["agents"],
    responses={
        200: {"description": "Successful response from agent"},
        400: {"description": "Invalid request format"},
        404: {"description": "Agent not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
async def query_agent(
    agent_id: str = Path(..., description="Agent identifier (alden, alice, mimic, sentry)"),
    request: QueryRequest = Body(..., description="Query request data"),
    user_context: Dict[str, Any] = Depends(get_user_context)
) -> QueryResponse:
    """Process user query through specified agent"""
    # Implementation details...
```

#### 8.1.2 Code Documentation Standards
```python
class MemoryService:
    """
    Memory management service for AI agents.
    
    This service provides persistent memory storage and retrieval capabilities
    for AI agents, enabling them to maintain context across sessions and
    learn from user interactions.
    
    Features:
    - Semantic memory search using vector embeddings
    - Importance-based memory ranking and decay
    - User-controlled memory management and privacy
    - Cross-session persistence with encryption
    
    Example:
        >>> memory_service = MemoryService('alden')
        >>> memory = await memory_service.create_memory(
        ...     user_id='user123',
        ...     content='User prefers morning meetings',
        ...     slice_type='procedural',
        ...     importance=0.8
        ... )
        >>> relevant = await memory_service.search_memories(
        ...     user_id='user123',
        ...     query='schedule meeting'
        ... )
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize memory service for specific agent.
        
        Args:
            agent_id: Unique identifier for the agent ('alden', 'alice', etc.)
            
        Raises:
            ValueError: If agent_id is not a valid agent identifier
        """
        if agent_id not in VALID_AGENT_IDS:
            raise ValueError(f"Invalid agent_id: {agent_id}")
            
        self.agent_id = agent_id
        self.database = DatabaseManager()
        self.vector_store = VectorStore()
    
    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 10,
        min_importance: float = 0.1,
        slice_types: Optional[List[str]] = None
    ) -> List[MemorySlice]:
        """
        Search for relevant memories using semantic similarity.
        
        This method uses vector embeddings to find memories that are
        semantically similar to the query text, ranked by relevance
        and importance.
        
        Args:
            user_id: User identifier for privacy isolation
            query: Search query text
            limit: Maximum number of memories to return (1-50)
            min_importance: Minimum importance threshold (0.0-1.0)
            slice_types: Filter by memory types ('episodic', 'semantic', 'procedural')
            
        Returns:
            List of MemorySlice objects sorted by relevance and importance
            
        Raises:
            ValueError: If parameters are outside valid ranges
            DatabaseError: If database operation fails
            
        Example:
            >>> memories = await service.search_memories(
            ...     user_id='user123',
            ...     query='morning routine',
            ...     limit=5,
            ...     slice_types=['procedural']
            ... )
            >>> for memory in memories:
            ...     print(f"{memory.importance}: {memory.content}")
        """
        # Implementation with detailed error handling and logging...
```

### 8.2 User Documentation

#### 8.2.1 User Guide Structure
```markdown
# Hearthlink User Guide

## Table of Contents
1. Getting Started
   - Installation
   - First Setup
   - Meeting Alden
2. Basic Usage
   - Voice Commands
   - Text Interface
   - Navigation
3. Core Features
   - Memory System
   - Agent Personalities
   - Project Management
4. Advanced Features
   - Customization
   - Integrations
   - Plugins
5. Privacy & Security
   - Data Control
   - Export/Import
   - Security Settings
6. Troubleshooting
   - Common Issues
   - Performance
   - Support
```

---

## 9. Appendices

### Appendix A: Configuration Schema
[Complete JSON schemas for all configuration files]

### Appendix B: Database Migration Scripts
[SQL scripts for database schema updates and migrations]

### Appendix C: Development Environment Setup
[Detailed setup instructions for development environment]

### Appendix D: Deployment Guidelines
[Production deployment and maintenance procedures]

### Appendix E: Security Checklist
[Comprehensive security validation checklist]

---

**Document Control**
- **Version**: 1.0.0
- **Classification**: Internal Use
- **Review Cycle**: Quarterly
- **Next Review**: October 2025
- **Owner**: Engineering Team
- **Approvers**: CTO, Security Lead, QA Lead

---

*This Technical Requirements Document provides the comprehensive technical specifications for Hearthlink development. All implementation work should conform to the standards and requirements defined herein.*