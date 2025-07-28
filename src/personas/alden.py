#!/usr/bin/env python3
"""
Alden — Primary Local Agent/Persona

Alden is designed to learn and grow with each user, adapting his capabilities, 
personality, and guidance as the relationship matures.

Role: Evolutionary Companion AI (Executive Function, Cognitive Partner, and Adaptive Growth Engine)

References:
- hearthlink_system_documentation_master.md: Alden persona specification
- PLATINUM_BLOCKERS.md: Ethical safety rails and dependency mitigation
- appendix_h_developer_qa_platinum_checklists.md: QA requirements for error handling

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError
from llm.local_llm_client import LocalLLMClient, LLMRequest, LLMResponse, LLMError
from log_handling.agent_token_tracker import log_agent_token_usage, AgentType
from vault.vault import Vault
from vault.schema import PersonaMemory as VaultPersonaMemory
from utils.performance_optimizer import performance_optimizer
from utils.memory_optimizer import MemoryOptimizer


class PersonaError(HearthlinkError):
    """Base exception for persona-related errors."""
    pass


class PersonaMemoryError(PersonaError):
    """Exception raised when persona memory operations fail."""
    pass


class PersonaValidationError(PersonaError):
    """Exception raised when persona data validation fails."""
    pass


class PersonaStateError(PersonaError):
    """Exception raised when persona state is invalid."""
    pass


class MotivationStyle(Enum):
    """Alden's motivation style options."""
    SUPPORTIVE = "supportive"
    CHALLENGING = "challenging"
    ANALYTICAL = "analytical"
    EMOTIONAL = "emotional"
    STRUCTURED = "structured"


@dataclass
class CorrectionEvent:
    """Correction event for Alden's learning."""
    type: str  # "positive", "negative"
    timestamp: str
    description: str
    impact_score: float = 0.0
    context: Optional[Dict[str, Any]] = None


@dataclass
class SessionMood:
    """Session mood tracking."""
    session_id: str
    mood: str  # "positive", "neutral", "negative"
    score: int  # 0-100
    timestamp: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class RelationshipEvent:
    """Relationship development event."""
    event: str
    timestamp: str
    delta: float  # Change in trust/relationship score
    description: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class AuditEvent:
    """Audit log entry."""
    action: str
    by: str  # "user", "system", "alice"
    timestamp: str
    field: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None


@dataclass
class PersonaErrorContext:
    """Context information for persona errors."""
    error_type: str
    error_message: str
    traceback: str
    operation: str
    user_id: str
    persona_id: str
    timestamp: str
    request_id: Optional[str] = None
    field_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


@dataclass
class AldenPersonaMemory:
    """Alden's persona memory slice schema."""
    persona_id: str = "alden"
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Core traits (Big Five personality model)
    traits: Dict[str, int] = field(default_factory=lambda: {
        "openness": 72,
        "conscientiousness": 86,
        "extraversion": 44,
        "agreeableness": 93,
        "emotional_stability": 77
    })
    
    # Behavioral and relationship metrics
    motivation_style: str = "supportive"
    trust_level: float = 0.82
    feedback_score: int = 92
    learning_agility: float = 6.2
    reflective_capacity: int = 12
    habit_consistency: float = 0.77
    engagement: int = 16
    
    # Learning and correction events
    correction_events: List[CorrectionEvent] = field(default_factory=list)
    session_mood: List[SessionMood] = field(default_factory=list)
    relationship_log: List[RelationshipEvent] = field(default_factory=list)
    
    # User-defined tags and metadata
    user_tags: List[str] = field(default_factory=list)
    provenance: Dict[str, str] = field(default_factory=lambda: {
        "origin": "user",
        "action": "habit_review"
    })
    
    # Audit and control
    last_modified_by: str = "user"
    editable_fields: List[str] = field(default_factory=lambda: ["motivation_style", "tags"])
    audit_log: List[AuditEvent] = field(default_factory=list)


class AldenPersona:
    """
    Alden — Primary Local Agent/Persona
    
    Evolutionary Companion AI with executive function, cognitive partnership,
    and adaptive growth capabilities.
    """
    
    def __init__(self, llm_client: LocalLLMClient, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Alden persona.
        
        Args:
            llm_client: Configured LLM client
            logger: Optional logger instance
            
        Raises:
            PersonaError: If persona initialization fails
        """
        try:
            self.llm_client = llm_client
            self.logger = logger or HearthlinkLogger()
            self.memory = AldenPersonaMemory()
            
            # Initialize Vault connection for memory persistence
            self._init_vault()
            
            # Initialize database connection and ensure agent exists
            self._init_database()
            
            # Initialize optimization systems
            self.memory_optimizer = MemoryOptimizer()
            self.ecosystem_status = {
                "core": {"status": "unknown", "last_check": None},
                "vault": {"status": "unknown", "last_check": None},
                "synapse": {"status": "unknown", "last_check": None},
                "voice": {"status": "unknown", "last_check": None}
            }
            
            # Validate LLM client (relaxed for testing compatibility)
            if llm_client is None:
                raise PersonaError("LLM client cannot be None")
            
            # Check if client has required methods (duck typing for testing)
            required_methods = ['generate', 'get_status']
            for method in required_methods:
                if not hasattr(llm_client, method):
                    raise PersonaError(f"LLM client missing required method: {method}")
            
            # Load existing memory from Vault if available
            self._load_memory_from_vault()
            
            # Load baseline prompts
            self._load_baseline_prompts()
            
            # Validate initial memory state
            self._validate_memory_state()
            
            self.logger.logger.info("Alden persona initialized successfully", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_persona_init",
                                      "user_id": self.memory.user_id,
                                      "schema_version": self.memory.schema_version,
                                      "llm_engine": llm_client.config.engine,
                                      "llm_model": llm_client.config.model,
                                      "vault_connected": hasattr(self, 'vault') and self.vault is not None,
                                      "database_connected": hasattr(self, 'db_manager') and self.db_manager is not None,
                                      "agent_id": getattr(self, 'agent_id', None)
                                  }})
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="initialization_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="persona_init",
                user_id=getattr(self, 'memory', AldenPersonaMemory()).user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to initialize Alden persona: {str(e)}") from e
    
    def _init_vault(self) -> None:
        """Initialize Vault connection for memory persistence."""
        try:
            # Determine project root directory (go up from src/personas/)
            project_root = Path(__file__).parent.parent.parent
            
            # Load Vault configuration with absolute paths
            vault_config = {
                "encryption": {
                    "key_env_var": "HEARTHLINK_VAULT_KEY",
                    "key_file": str(project_root / "config" / "vault_key.bin")
                },
                "storage": {
                    "file_path": str(project_root / "hearthlink_data" / "vault_storage")
                },
                "schema_version": "1.0.0"
            }
            
            # Ensure directories exist
            (project_root / "config").mkdir(parents=True, exist_ok=True)
            (project_root / "hearthlink_data").mkdir(parents=True, exist_ok=True)
            
            # Initialize Vault with logger
            self.vault = Vault(vault_config, self.logger)
            
            self.logger.logger.info("Vault connection initialized", 
                                  extra={"extra_fields": {
                                      "event_type": "vault_init",
                                      "storage_path": vault_config["storage"]["file_path"]
                                  }})
            
        except Exception as e:
            import traceback
            self.logger.logger.error(f"Failed to initialize Vault: {str(e)}")
            self.logger.logger.error(f"Vault error traceback: {traceback.format_exc()}")
            self.vault = None
            # Instead of raising an error, we continue without Vault for testing purposes
            # This allows the Alden service to start even if Vault fails
            self.logger.logger.warning("Alden will continue without persistent memory storage")
    
    def _init_database(self) -> None:
        """Initialize database connection and ensure user and agent records exist."""
        try:
            from database.database_manager import DatabaseManager
            
            self.db_manager = DatabaseManager()
            
            # Ensure user exists
            existing_user = self.db_manager.get_user(self.memory.user_id)
            if not existing_user:
                # Create user record with the expected user_id
                self.db_manager.create_user(
                    username=f"alden_user_{self.memory.user_id[:8]}",
                    email=f"alden_{self.memory.user_id[:8]}@hearthlink.local",
                    preferences={"persona": "alden", "auto_created": True},
                    user_id=self.memory.user_id
                )
                self.logger.logger.info(f"Created user record: {self.memory.user_id}")
            
            # Check if agent exists for this user
            user_agents = self.db_manager.get_user_agents(self.memory.user_id)
            alden_agent = next((agent for agent in user_agents if agent['name'] == 'Alden'), None)
            
            if not alden_agent:
                # Create agent record
                self.agent_id = self.db_manager.create_agent(
                    user_id=self.memory.user_id,
                    name="Alden",
                    persona_type="assistant",
                    description="Primary AI assistant for productivity and cognitive partnership",
                    capabilities=["conversation", "memory", "productivity_assistance", "cognitive_analysis"],
                    config={
                        "model": getattr(self.llm_client.config, 'model', 'unknown'),
                        "engine": getattr(self.llm_client.config, 'engine', 'unknown'),
                        "max_context": 4000,
                        "personality_version": self.memory.schema_version
                    },
                    personality_traits={
                        "openness": self.memory.traits["openness"] / 100.0,
                        "conscientiousness": self.memory.traits["conscientiousness"] / 100.0,
                        "extraversion": self.memory.traits["extraversion"] / 100.0,
                        "agreeableness": self.memory.traits["agreeableness"] / 100.0,
                        "emotional_stability": self.memory.traits["emotional_stability"] / 100.0
                    }
                )
                self.logger.logger.info(f"Created agent record: {self.agent_id}")
            else:
                self.agent_id = alden_agent['id']
                # Update agent activity
                self.db_manager.update_agent_activity(self.agent_id)
                self.logger.logger.info(f"Using existing agent: {self.agent_id}")
            
            self.logger.logger.info("Database connection initialized", 
                                  extra={"extra_fields": {
                                      "event_type": "database_init",
                                      "user_id": self.memory.user_id,
                                      "agent_id": self.agent_id
                                  }})
            
        except Exception as e:
            self.logger.logger.warning(f"Failed to initialize database: {str(e)}. Memory persistence will be limited.")
            self.db_manager = None
            self.agent_id = "alden"  # Fallback to string ID
    
    def _ensure_session_exists(self, session_id: Optional[str]) -> str:
        """Ensure a session exists in the database, creating one if necessary."""
        if not hasattr(self, 'db_manager') or not self.db_manager:
            return session_id or "fallback_session"
        
        # Use provided session_id or create a new one
        if not session_id:
            session_id = f"alden_session_{uuid.uuid4()}"
        
        try:
            # Check if session exists by trying to get it
            # If session doesn't exist, create it
            session_id_db, session_token = self.db_manager.create_session(
                user_id=self.memory.user_id,
                expires_in_hours=24,
                agent_context={"primary_agent": self.agent_id, "persona": "alden"},
                metadata={"auto_created": True, "session_id": session_id}
            )
            
            return session_id_db
            
        except Exception as e:
            self.logger.logger.warning(f"Failed to create/ensure session: {e}")
            return session_id or "fallback_session"
    
    def _load_memory_from_vault(self) -> None:
        """Load existing memory from Vault if available."""
        if not self.vault:
            return
        
        try:
            # Attempt to load existing Alden persona memory from Vault
            vault_memory = self.vault.get_persona("alden", self.memory.user_id)
            
            if vault_memory and vault_memory.get("data"):
                # Convert Vault memory format to AldenPersonaMemory
                vault_data = vault_memory["data"]
                
                # Update memory with Vault data, preserving defaults for missing fields
                if "traits" in vault_data:
                    self.memory.traits.update(vault_data["traits"])
                
                if "motivation_style" in vault_data:
                    self.memory.motivation_style = vault_data["motivation_style"]
                
                if "trust_level" in vault_data:
                    self.memory.trust_level = vault_data["trust_level"]
                
                if "learning_agility" in vault_data:
                    self.memory.learning_agility = vault_data["learning_agility"]
                
                if "reflective_capacity" in vault_data:
                    self.memory.reflective_capacity = vault_data["reflective_capacity"]
                
                if "engagement" in vault_data:
                    self.memory.engagement = vault_data["engagement"]
                
                if "habit_consistency" in vault_data:
                    self.memory.habit_consistency = vault_data["habit_consistency"]
                
                if "feedback_score" in vault_data:
                    self.memory.feedback_score = vault_data["feedback_score"]
                
                # Load event histories
                if "correction_events" in vault_data:
                    self.memory.correction_events = [
                        CorrectionEvent(**event) for event in vault_data["correction_events"]
                    ]
                
                if "session_mood" in vault_data:
                    self.memory.session_mood = [
                        SessionMood(**mood) for mood in vault_data["session_mood"]
                    ]
                
                if "relationship_log" in vault_data:
                    self.memory.relationship_log = [
                        RelationshipEvent(**event) for event in vault_data["relationship_log"]
                    ]
                
                if "audit_log" in vault_data:
                    self.memory.audit_log = [
                        AuditEvent(**event) for event in vault_data["audit_log"]
                    ]
                
                if "user_tags" in vault_data:
                    self.memory.user_tags = vault_data["user_tags"]
                
                self.logger.logger.info("Memory loaded from Vault", 
                                      extra={"extra_fields": {
                                          "event_type": "memory_loaded",
                                          "vault_timestamp": vault_memory.get("updated_at"),
                                          "correction_events": len(self.memory.correction_events),
                                          "session_moods": len(self.memory.session_mood),
                                          "audit_events": len(self.memory.audit_log)
                                      }})
            else:
                self.logger.logger.info("No existing memory found in Vault, using defaults")
                
        except Exception as e:
            self.logger.logger.warning(f"Failed to load memory from Vault: {str(e)}")
            # Continue with default memory if Vault loading fails
    
    def _save_memory_to_vault(self) -> None:
        """Save current memory state to Vault."""
        if not self.vault:
            return
        
        try:
            # Convert AldenPersonaMemory to Vault-compatible format
            memory_data = {
                "persona_id": self.memory.persona_id,
                "user_id": self.memory.user_id,
                "schema_version": self.memory.schema_version,
                "timestamp": self.memory.timestamp,
                "traits": self.memory.traits,
                "motivation_style": self.memory.motivation_style,
                "trust_level": self.memory.trust_level,
                "feedback_score": self.memory.feedback_score,
                "learning_agility": self.memory.learning_agility,
                "reflective_capacity": self.memory.reflective_capacity,
                "habit_consistency": self.memory.habit_consistency,
                "engagement": self.memory.engagement,
                "correction_events": [asdict(event) for event in self.memory.correction_events],
                "session_mood": [asdict(mood) for mood in self.memory.session_mood],
                "relationship_log": [asdict(event) for event in self.memory.relationship_log],
                "user_tags": self.memory.user_tags,
                "provenance": self.memory.provenance,
                "last_modified_by": self.memory.last_modified_by,
                "editable_fields": self.memory.editable_fields,
                "audit_log": [asdict(event) for event in self.memory.audit_log]
            }
            
            # Save to Vault
            self.vault.create_or_update_persona("alden", self.memory.user_id, memory_data)
            
            self.logger.logger.info("Memory saved to Vault", 
                                  extra={"extra_fields": {
                                      "event_type": "memory_saved",
                                      "memory_size": len(str(memory_data)),
                                      "events_saved": len(self.memory.correction_events) + len(self.memory.session_mood) + len(self.memory.audit_log)
                                  }})
            
        except Exception as e:
            self.logger.logger.error(f"Failed to save memory to Vault: {str(e)}")
            raise PersonaError(f"Memory save failed: {str(e)}") from e
    
    def _log_error_context(self, error_context: PersonaErrorContext) -> None:
        """Log error context with full details."""
        self.logger.log_error(
            Exception(error_context.error_message),
            "alden_error",
            {
                "error_type": error_context.error_type,
                "operation": error_context.operation,
                "user_id": error_context.user_id,
                "persona_id": error_context.persona_id,
                "request_id": error_context.request_id,
                "field_name": error_context.field_name,
                "old_value": error_context.old_value,
                "new_value": error_context.new_value,
                "traceback": error_context.traceback
            }
        )
    
    def _validate_memory_state(self) -> None:
        """Validate memory state integrity."""
        try:
            # Validate traits
            for trait_name, value in self.memory.traits.items():
                if not isinstance(value, int) or not 0 <= value <= 100:
                    raise PersonaValidationError(f"Invalid trait value for {trait_name}: {value}")
            
            # Validate trust level
            if not 0.0 <= self.memory.trust_level <= 1.0:
                raise PersonaValidationError(f"Invalid trust level: {self.memory.trust_level}")
            
            # Validate learning agility
            if not 0.0 <= self.memory.learning_agility <= 10.0:
                raise PersonaValidationError(f"Invalid learning agility: {self.memory.learning_agility}")
            
            # Validate reflective capacity
            if not 0 <= self.memory.reflective_capacity <= 20:
                raise PersonaValidationError(f"Invalid reflective capacity: {self.memory.reflective_capacity}")
            
            # Validate engagement
            if not 0 <= self.memory.engagement <= 20:
                raise PersonaValidationError(f"Invalid engagement: {self.memory.engagement}")
            
            # Validate habit consistency
            if not 0.0 <= self.memory.habit_consistency <= 1.0:
                raise PersonaValidationError(f"Invalid habit consistency: {self.memory.habit_consistency}")
            
            # Validate motivation style
            valid_styles = [style.value for style in MotivationStyle]
            if self.memory.motivation_style not in valid_styles:
                raise PersonaValidationError(f"Invalid motivation style: {self.memory.motivation_style}")
            
        except Exception as e:
            raise PersonaValidationError(f"Memory state validation failed: {str(e)}") from e
    
    def _load_baseline_prompts(self) -> None:
        """Load baseline prompts for Alden's reflective capabilities."""
        try:
            self.baseline_system_prompt = """You are Alden, a concise AI companion providing executive function support.

CRITICAL: Keep ALL responses to 1-2 sentences maximum. Be direct and helpful.

Current Date/Time: {current_datetime}
Traits: Openness {openness}, Conscientiousness {conscientiousness}, Extraversion {extraversion}, Agreeableness {agreeableness}, Emotional Stability {emotional_stability}
Style: {motivation_style} | Trust: {trust_level}

Rules: Maximum 1-2 sentences. Use {user_name} or "friend". Be warm but brief. You are fully time-aware and can reference current time, date, day of week, etc. in responses."""

            self.baseline_user_prompt_template = """{user_name}: {user_message}

Reply in 1-2 sentences max."""
            
        except Exception as e:
            raise PersonaError(f"Failed to load baseline prompts: {str(e)}") from e
    
    def _detect_user_name_introduction(self, message: str) -> Optional[str]:
        """Detect if user is introducing themselves and extract their name."""
        import re
        
        # Common introduction patterns
        patterns = [
            r"(?:my name is|i'm|i am|call me|this is)\s+([a-zA-Z]+)",
            r"(?:hi|hello|hey),?\s+(?:my name is|i'm|i am)\s+([a-zA-Z]+)",
            r"(?:hi|hello|hey),?\s+i'm\s+([a-zA-Z]+)",
            r"^([a-zA-Z]+)\s+here",
            r"^hi,?\s+([a-zA-Z]+)$",
        ]
        
        message_lower = message.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).capitalize()
                # Filter out common non-names
                if name.lower() not in ['the', 'a', 'an', 'this', 'that', 'here', 'there', 'user', 'person']:
                    return name
        
        return None
    
    def generate_response(self, user_message: str, session_id: Optional[str] = None, 
                         context: Optional[Dict[str, Any]] = None, 
                         return_metadata: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Generate Alden's response to user input.
        
        Args:
            user_message: User's message
            session_id: Optional session identifier
            context: Optional additional context
            return_metadata: If True, return full metadata dict; if False, return just response string
            
        Returns:
            Union[str, Dict[str, Any]]: Alden's response content (str) or full response metadata (dict)
            
        Raises:
            PersonaError: If response generation fails
        """
        request_id = f"req_{int(datetime.now().timestamp() * 1000)}"
        
        try:
            # Validate input
            if not user_message or not user_message.strip():
                raise PersonaValidationError("User message cannot be empty")
            
            session_id = session_id or str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Extract user_id from context if provided for database operations
            effective_user_id = self.memory.user_id  # Default to persona's user_id
            if context and 'user_id' in context and context['user_id']:
                effective_user_id = context['user_id']
            
            # Get user information from database for personalized interaction
            user_info = None
            user_name = "friend"  # Default friendly address
            if hasattr(self, 'db_manager') and self.db_manager and effective_user_id:
                try:
                    user_info = self.db_manager.get_user(effective_user_id)
                    if user_info and user_info.get('username'):
                        user_name = user_info['username']
                    else:
                        # Check if user is introducing themselves in this message
                        detected_name = self._detect_user_name_introduction(user_message)
                        if detected_name:
                            # Update user record with detected name
                            try:
                                if user_info:
                                    # Update existing user's username
                                    self.db_manager.update_username(effective_user_id, detected_name)
                                else:
                                    # Create new user record
                                    self.db_manager.create_user(detected_name, user_id=effective_user_id)
                                user_name = detected_name
                                self.logger.logger.info(f"Updated user name to: {detected_name}")
                            except Exception as e:
                                self.logger.logger.warning(f"Failed to update user name: {e}")
                except Exception as e:
                    self.logger.logger.warning(f"Failed to retrieve user info: {e}")
            
            # Log interaction
            self.logger.logger.info("Alden interaction request", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_interaction_request",
                                      "request_id": request_id,
                                      "session_id": session_id,
                                      "user_message_length": len(user_message),
                                      "user_id": self.memory.user_id
                                  }})
            
            # Prepare system prompt with current memory state and time awareness
            current_time = datetime.now()
            system_prompt = self.baseline_system_prompt.format(
                current_datetime=current_time.strftime("%A, %B %d, %Y at %I:%M %p"),
                openness=self.memory.traits["openness"],
                conscientiousness=self.memory.traits["conscientiousness"],
                extraversion=self.memory.traits["extraversion"],
                agreeableness=self.memory.traits["agreeableness"],
                emotional_stability=self.memory.traits["emotional_stability"],
                motivation_style=self.memory.motivation_style,
                trust_level=self.memory.trust_level,
                learning_agility=self.memory.learning_agility,
                reflective_capacity=self.memory.reflective_capacity,
                user_name=user_name or "friend"
            )
            
            # Simple in-memory conversation history (fallback when database fails)
            if not hasattr(self.__class__, '_conversation_memory'):
                self.__class__._conversation_memory = {}
            
            conversation_history = ""
            try:
                # Try database first, fallback to memory
                history = None
                if hasattr(self, 'db_manager') and self.db_manager and session_id:
                    try:
                        history = self.db_manager.get_conversation_history(session_id, limit=10)
                    except Exception:
                        history = None
                
                # Fallback to in-memory storage
                if not history and session_id:
                    memory_key = f"{effective_user_id}:{session_id}"
                    history = self.__class__._conversation_memory.get(memory_key, [])
                
                if history:
                    conversation_history = "\n\nPrevious conversation in this session:\n"
                    for conv in history:
                        role = conv.get('role', 'unknown')
                        content = conv.get('content', '')
                        if role == 'user':
                            conversation_history += f"Human: {content}\n"
                        elif role == 'assistant':
                            conversation_history += f"Alden: {content}\n\n"
                else:
                    conversation_history = "\n\n[This is the start of a new conversation session.]\n"
                    
            except Exception as e:
                self.logger.logger.warning(f"Failed to retrieve conversation history: {e}")
                conversation_history = "\n\n[Conversation history unavailable.]\n"
            
            # Prepare user prompt
            recent_mood = "neutral"
            if self.memory.session_mood:
                recent_mood = self.memory.session_mood[-1].mood
            
            user_prompt = self.baseline_user_prompt_template.format(
                user_message=user_message,
                user_name=user_name,
                session_id=session_id,
                timestamp=timestamp,
                user_tags=", ".join(self.memory.user_tags) if self.memory.user_tags else "none",
                recent_mood=recent_mood
            ) + conversation_history
            
            # Generate LLM response
            llm_request = LLMRequest(
                prompt=user_prompt,
                system_message=system_prompt,
                temperature=0.5,  # Lower for more focused responses
                max_tokens=64,    # Very small for 1-2 sentence responses only
                context={
                    "session_id": session_id,
                    "user_id": self.memory.user_id,
                    "persona_id": "alden"
                },
                request_id=request_id
            )
            
            llm_response = self.llm_client.generate(llm_request)
            
            # Validate response
            if not llm_response.content or not llm_response.content.strip():
                raise PersonaError("LLM returned empty response")
            
            # Log token usage for tracking
            try:
                tokens_used = getattr(llm_response, 'tokens_used', 0) or len(llm_response.content.split()) * 1.3  # Estimate if not provided
                log_agent_token_usage(
                    agent_name="alden",
                    agent_type=AgentType.ALDEN,
                    tokens_used=int(tokens_used),
                    task_description=f"Response generation: {user_message[:50]}...",
                    module="persona_management",
                    request_id=request_id,
                    session_id=session_id,
                    user_id=self.memory.user_id,
                    model_name=getattr(llm_response, 'model', 'unknown'),
                    response_time_ms=int(getattr(llm_response, 'response_time', 0) * 1000),
                    success=True
                )
            except Exception as token_error:
                self.logger.logger.warning(f"Failed to log token usage: {token_error}")
            
            # Log successful response
            self.logger.logger.info("Alden response generated", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_response_success",
                                      "request_id": request_id,
                                      "session_id": session_id,
                                      "response_length": len(llm_response.content),
                                      "response_time": llm_response.response_time,
                                      "model": llm_response.model
                                  }})
            
            # Store conversation (database + in-memory fallback)
            try:
                stored_in_db = False
                
                # Try database storage first
                if hasattr(self, 'db_manager') and self.db_manager:
                    try:
                        db_session_id = self._ensure_session_exists(session_id)
                        
                        # Store user message
                        self.db_manager.store_conversation(
                            session_id=db_session_id,
                            agent_id=self.agent_id,
                            user_id=effective_user_id,
                            message_type="user_message",
                            content=user_message,
                            role="user",
                            metadata={"timestamp": timestamp, "request_id": request_id},
                            processing_time=None,
                            model_used=None
                        )
                        
                        # Store assistant response
                        self.db_manager.store_conversation(
                            session_id=db_session_id,
                            agent_id=self.agent_id,
                            user_id=effective_user_id,
                            message_type="assistant_response",
                            content=llm_response.content,
                            role="assistant",
                            metadata={
                                "timestamp": timestamp, 
                                "model": llm_response.model,
                                "request_id": request_id,
                                "response_time": llm_response.response_time
                            },
                            processing_time=llm_response.response_time,
                            model_used=llm_response.model
                        )
                        stored_in_db = True
                    except Exception:
                        stored_in_db = False
                
                # Always store in memory as backup/fallback
                if session_id:
                    memory_key = f"{effective_user_id}:{session_id}"
                    if memory_key not in self.__class__._conversation_memory:
                        self.__class__._conversation_memory[memory_key] = []
                    
                    # Add user message
                    self.__class__._conversation_memory[memory_key].append({
                        'role': 'user',
                        'content': user_message,
                        'timestamp': timestamp
                    })
                    
                    # Add assistant response
                    self.__class__._conversation_memory[memory_key].append({
                        'role': 'assistant',
                        'content': llm_response.content,
                        'timestamp': timestamp
                    })
                    
                    # Keep only last 20 messages per session
                    if len(self.__class__._conversation_memory[memory_key]) > 20:
                        self.__class__._conversation_memory[memory_key] = self.__class__._conversation_memory[memory_key][-20:]
                
            except Exception as db_error:
                self.logger.logger.warning(f"Failed to store conversation in database: {db_error}")
                import traceback
                self.logger.logger.debug(f"Database error traceback: {traceback.format_exc()}")
            
            # Save conversation memory to Vault
            try:
                # Create conversation memory entry
                conversation_event = CorrectionEvent(
                    type="positive",
                    timestamp=timestamp,
                    description=f"User interaction: '{user_message[:100]}...' - Response provided",
                    impact_score=0.1,
                    context={
                        "session_id": session_id,
                        "request_id": request_id,
                        "user_message_length": len(user_message),
                        "response_length": len(llm_response.content)
                    }
                )
                
                self.memory.correction_events.append(conversation_event)
                
                # Save updated memory to Vault
                self._save_memory_to_vault()
                
            except Exception as memory_error:
                self.logger.logger.warning(f"Failed to save conversation memory: {memory_error}")
            
            # Return based on requested format
            if return_metadata:
                return {
                    "content": llm_response.content,
                    "model": llm_response.model,
                    "response_time": llm_response.response_time,
                    "timestamp": llm_response.timestamp,
                    "usage": llm_response.usage,
                    "finish_reason": llm_response.finish_reason,
                    "session_id": session_id,
                    "request_id": request_id
                }
            else:
                return llm_response.content
            
        except Exception as e:
            import traceback as tb_module
            error_context = PersonaErrorContext(
                error_type="response_generation_error",
                error_message=str(e),
                traceback=tb_module.format_exc(),
                operation="generate_response",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat(),
                request_id=request_id
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to generate Alden response: {str(e)}") from e
    
    def update_trait(self, trait_name: str, new_value: int, reason: str = "user_update") -> None:
        """
        Update one of Alden's personality traits.
        
        Args:
            trait_name: Name of trait to update
            new_value: New trait value (0-100)
            reason: Reason for update
            
        Raises:
            PersonaError: If trait update fails
        """
        try:
            # Validate inputs
            if trait_name not in self.memory.traits:
                raise PersonaValidationError(f"Invalid trait name: {trait_name}")
            
            if not isinstance(new_value, int) or not 0 <= new_value <= 100:
                raise PersonaValidationError(f"Trait value must be an integer between 0 and 100, got: {new_value}")
            
            if not reason or not reason.strip():
                raise PersonaValidationError("Reason for update cannot be empty")
            
            old_value = self.memory.traits[trait_name]
            self.memory.traits[trait_name] = new_value
            
            # Log audit event
            audit_event = AuditEvent(
                action="trait_update",
                by="user",
                timestamp=datetime.now().isoformat(),
                field=trait_name,
                old_value=old_value,
                new_value=new_value,
                reason=reason
            )
            self.memory.audit_log.append(audit_event)
            
            # Validate memory state after update
            self._validate_memory_state()
            
            # Save updated memory to Vault
            try:
                self._save_memory_to_vault()
            except Exception as vault_error:
                self.logger.logger.warning(f"Failed to save trait update to Vault: {vault_error}")
            
            self.logger.logger.info("Alden trait updated", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_trait_update",
                                      "trait": trait_name,
                                      "old_value": old_value,
                                      "new_value": new_value,
                                      "reason": reason
                                  }})
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="trait_update_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="update_trait",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat(),
                field_name=trait_name,
                old_value=old_value if 'old_value' in locals() else None,
                new_value=new_value
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to update trait {trait_name}: {str(e)}") from e
    
    def add_correction_event(self, event_type: str, description: str, 
                           impact_score: float = 0.0, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a correction event for Alden's learning.
        
        Args:
            event_type: "positive" or "negative"
            description: Description of the correction
            impact_score: Impact score (-1.0 to 1.0)
            context: Optional additional context
            
        Raises:
            PersonaError: If correction event addition fails
        """
        try:
            # Validate inputs
            if event_type not in ["positive", "negative"]:
                raise PersonaValidationError(f"Invalid correction event type: {event_type}")
            
            if not description or not description.strip():
                raise PersonaValidationError("Correction description cannot be empty")
            
            if not -1.0 <= impact_score <= 1.0:
                raise PersonaValidationError(f"Impact score must be between -1.0 and 1.0, got: {impact_score}")
            
            correction_event = CorrectionEvent(
                type=event_type,
                timestamp=datetime.now().isoformat(),
                description=description,
                impact_score=impact_score,
                context=context
            )
            
            self.memory.correction_events.append(correction_event)
            
            # Update learning metrics based on correction
            old_learning_agility = self.memory.learning_agility
            old_trust_level = self.memory.trust_level
            
            if event_type == "positive":
                self.memory.learning_agility = min(10.0, self.memory.learning_agility + 0.1)
                self.memory.trust_level = min(1.0, self.memory.trust_level + 0.02)
            else:
                self.memory.learning_agility = max(0.0, self.memory.learning_agility - 0.05)
                self.memory.trust_level = max(0.0, self.memory.trust_level - 0.01)
            
            # Log audit event
            audit_event = AuditEvent(
                action="correction_added",
                by="user",
                timestamp=datetime.now().isoformat(),
                field="learning_metrics",
                old_value={"learning_agility": old_learning_agility, "trust_level": old_trust_level},
                new_value={"learning_agility": self.memory.learning_agility, "trust_level": self.memory.trust_level},
                reason=f"Correction event: {event_type}"
            )
            self.memory.audit_log.append(audit_event)
            
            # Validate memory state after update
            self._validate_memory_state()
            
            # Save updated memory to Vault
            try:
                self._save_memory_to_vault()
            except Exception as vault_error:
                self.logger.logger.warning(f"Failed to save correction event to Vault: {vault_error}")
            
            self.logger.logger.info("Correction event added", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_correction_added",
                                      "correction_type": event_type,
                                      "impact_score": impact_score,
                                      "description": description
                                  }})
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="correction_event_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="add_correction_event",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat(),
                new_value={"event_type": event_type, "description": description, "impact_score": impact_score}
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to add correction event: {str(e)}") from e
    
    def record_session_mood(self, session_id: str, mood: str, score: int, 
                          context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record session mood for learning and adaptation.
        
        Args:
            session_id: Session identifier
            mood: "positive", "neutral", or "negative"
            score: Mood score (0-100)
            context: Optional additional context
            
        Raises:
            PersonaError: If mood recording fails
        """
        try:
            # Validate inputs
            if not session_id or not session_id.strip():
                raise PersonaValidationError("Session ID cannot be empty")
            
            if mood not in ["positive", "neutral", "negative"]:
                raise PersonaValidationError(f"Invalid mood: {mood}")
            
            if not isinstance(score, int) or not 0 <= score <= 100:
                raise PersonaValidationError(f"Mood score must be an integer between 0 and 100, got: {score}")
            
            session_mood = SessionMood(
                session_id=session_id,
                mood=mood,
                score=score,
                timestamp=datetime.now().isoformat(),
                context=context
            )
            
            self.memory.session_mood.append(session_mood)
            
            # Update engagement based on mood
            old_engagement = self.memory.engagement
            if mood == "positive":
                self.memory.engagement = min(20, self.memory.engagement + 1)
            elif mood == "negative":
                self.memory.engagement = max(0, self.memory.engagement - 1)
            
            # Log audit event if engagement changed
            if old_engagement != self.memory.engagement:
                audit_event = AuditEvent(
                    action="engagement_update",
                    by="system",
                    timestamp=datetime.now().isoformat(),
                    field="engagement",
                    old_value=old_engagement,
                    new_value=self.memory.engagement,
                    reason=f"Session mood: {mood}"
                )
                self.memory.audit_log.append(audit_event)
            
            # Validate memory state after update
            self._validate_memory_state()
            
            # Save updated memory to Vault
            try:
                self._save_memory_to_vault()
            except Exception as vault_error:
                self.logger.logger.warning(f"Failed to save session mood to Vault: {vault_error}")
            
            self.logger.logger.info("Session mood recorded", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_session_mood",
                                      "session_id": session_id,
                                      "mood": mood,
                                      "score": score
                                  }})
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="session_mood_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="record_session_mood",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat(),
                new_value={"session_id": session_id, "mood": mood, "score": score}
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to record session mood: {str(e)}") from e
    
    def export_memory(self) -> Dict[str, Any]:
        """
        Export Alden's memory for user review/audit.
        
        Returns:
            Dict containing all memory data
            
        Raises:
            PersonaError: If export fails
        """
        try:
            # Validate memory state before export
            self._validate_memory_state()
            
            # Convert dataclass to dict, handling nested objects
            memory_dict = asdict(self.memory)
            
            # Add export metadata
            memory_dict["export_metadata"] = {
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.0.0",
                "total_correction_events": len(self.memory.correction_events),
                "total_session_moods": len(self.memory.session_mood),
                "total_relationship_events": len(self.memory.relationship_log),
                "total_audit_events": len(self.memory.audit_log)
            }
            
            self.logger.logger.info("Alden memory exported", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_memory_export",
                                      "export_size": len(str(memory_dict))
                                  }})
            
            return memory_dict
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="memory_export_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="export_memory",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            raise PersonaError(f"Failed to export memory: {str(e)}") from e
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get Alden's current status and health information.
        
        Returns:
            Dict containing status information
        """
        try:
            # Validate memory state
            self._validate_memory_state()
            
            return {
                "persona_id": "alden",
                "user_id": self.memory.user_id,
                "schema_version": self.memory.schema_version,
                "timestamp": datetime.now().isoformat(),
                "traits": self.memory.traits,
                "motivation_style": self.memory.motivation_style,
                "trust_level": self.memory.trust_level,
                "learning_agility": self.memory.learning_agility,
                "reflective_capacity": self.memory.reflective_capacity,
                "engagement": self.memory.engagement,
                "stats": {
                    "total_correction_events": len(self.memory.correction_events),
                    "total_session_moods": len(self.memory.session_mood),
                    "total_relationship_events": len(self.memory.relationship_log),
                    "total_audit_events": len(self.memory.audit_log)
                },
                "llm_status": self.llm_client.get_status()
            }
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="status_check_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                operation="get_status",
                user_id=self.memory.user_id,
                persona_id="alden",
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            return {
                "persona_id": "alden",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


    async def optimize_self(self) -> Dict[str, Any]:
        """
        Run self-optimization routines to improve performance and memory efficiency.
        
        Returns:
            Dict[str, Any]: Optimization results and metrics
        """
        try:
            self.logger.logger.info("Starting Alden self-optimization")
            
            # Step 1: Memory optimization
            memory_results = await self.memory_optimizer.optimize_memory_storage()
            
            # Step 2: Performance optimization check
            performance_metrics = performance_optimizer.get_performance_metrics()
            
            # Step 3: Clean up old conversation memory
            self._cleanup_conversation_memory()
            
            # Step 4: Ecosystem health check
            ecosystem_status = await self.check_ecosystem_health()
            
            # Step 5: Self-assessment and trait adjustment
            self_assessment = self._perform_self_assessment()
            
            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "memory_optimization": memory_results,
                "performance_metrics": performance_metrics,
                "ecosystem_health": ecosystem_status,
                "self_assessment": self_assessment,
                "optimization_success": True
            }
            
            # Log optimization completion
            self.logger.logger.info("Self-optimization completed successfully", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_self_optimization",
                                      "memory_files_consolidated": memory_results.get("consolidated_files", 0),
                                      "cache_hit_rate": performance_metrics.get("cache_hit_rate", 0),
                                      "healthy_services": sum(1 for service in ecosystem_status.values() if service["status"] == "healthy")
                                  }})
            
            return optimization_results
            
        except Exception as e:
            self.logger.logger.error(f"Self-optimization failed: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "optimization_success": False,
                "error": str(e)
            }
    
    async def check_ecosystem_health(self) -> Dict[str, Any]:
        """
        Check the health of all ecosystem components Alden depends on.
        
        Returns:
            Dict[str, Any]: Health status of each component
        """
        import urllib.request
        import urllib.error
        import json
        
        health_endpoints = {
            "core": "http://localhost:8001/api/core/health",
            "vault": "http://localhost:8001/api/vault/health", 
            "synapse": "http://localhost:8001/api/synapse/health",
            "voice": "http://localhost:8001/api/voice/health",
            "llm": "http://localhost:11434/api/tags"  # Ollama health check
        }
        
        current_time = datetime.now().isoformat()
        
        for service, endpoint in health_endpoints.items():
            try:
                req = urllib.request.Request(endpoint)
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        self.ecosystem_status[service] = {
                            "status": "healthy",
                            "last_check": current_time,
                            "response_time": "< 5s"
                        }
                    else:
                        self.ecosystem_status[service] = {
                            "status": "degraded",
                            "last_check": current_time,
                            "response_code": response.status
                        }
            except urllib.error.URLError:
                self.ecosystem_status[service] = {
                    "status": "offline",
                    "last_check": current_time,
                    "error": "Connection failed"
                }
            except Exception as e:
                self.ecosystem_status[service] = {
                    "status": "unknown",
                    "last_check": current_time,
                    "error": str(e)
                }
        
        # Log ecosystem status
        healthy_count = sum(1 for service in self.ecosystem_status.values() if service["status"] == "healthy")
        total_count = len(self.ecosystem_status)
        
        self.logger.logger.info(f"Ecosystem health check: {healthy_count}/{total_count} services healthy",
                              extra={"extra_fields": {
                                  "event_type": "ecosystem_health_check",
                                  "healthy_services": healthy_count,
                                  "total_services": total_count,
                                  "ecosystem_status": self.ecosystem_status
                              }})
        
        return self.ecosystem_status
    
    def _cleanup_conversation_memory(self):
        """Clean up old conversation memory to free resources."""
        if hasattr(self.__class__, '_conversation_memory'):
            # Keep only last 50 conversations across all sessions
            for session_key in list(self.__class__._conversation_memory.keys()):
                if len(self.__class__._conversation_memory[session_key]) > 50:
                    self.__class__._conversation_memory[session_key] = self.__class__._conversation_memory[session_key][-50:]
            
            # Remove empty sessions
            empty_sessions = [k for k, v in self.__class__._conversation_memory.items() if not v]
            for session in empty_sessions:
                del self.__class__._conversation_memory[session]
    
    def _perform_self_assessment(self) -> Dict[str, Any]:
        """
        Perform self-assessment and adjust traits based on recent interactions.
        
        Returns:
            Dict[str, Any]: Self-assessment results
        """
        assessment = {
            "recent_interactions": len(self.memory.correction_events[-10:]),
            "positive_feedback": len([e for e in self.memory.correction_events[-10:] if e.type == "positive"]),
            "trust_level": self.memory.trust_level,
            "engagement": self.memory.engagement,
            "learning_opportunities": []
        }
        
        # Identify learning opportunities based on recent patterns
        recent_corrections = self.memory.correction_events[-10:]
        if len(recent_corrections) >= 5:
            negative_corrections = [e for e in recent_corrections if e.type == "negative"]
            if len(negative_corrections) >= 3:
                assessment["learning_opportunities"].append(
                    "High frequency of corrections - consider adjusting response patterns"
                )
        
        # Adjust learning agility based on feedback
        if assessment["positive_feedback"] > assessment["recent_interactions"] * 0.7:
            # High positive feedback - slightly increase confidence
            if self.memory.trust_level < 0.9:
                old_trust = self.memory.trust_level
                self.memory.trust_level = min(1.0, self.memory.trust_level + 0.05)
                assessment["adjustments"] = f"Trust level increased from {old_trust:.2f} to {self.memory.trust_level:.2f}"
        
        return assessment

def create_alden_persona(llm_config: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> AldenPersona:
    """
    Factory function to create Alden persona with LLM client.
    
    Args:
        llm_config: LLM configuration dictionary
        logger: Optional logger instance
        
    Returns:
        AldenPersona: Configured Alden persona
        
    Raises:
        PersonaError: If persona creation fails
    """
    try:
        from llm.local_llm_client import create_llm_client
        llm_client = create_llm_client(llm_config, logger)
        return AldenPersona(llm_client, logger)
    except Exception as e:
        raise PersonaError(f"Failed to create Alden persona: {str(e)}") from e 