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
            
            # Validate LLM client
            if not isinstance(llm_client, LocalLLMClient):
                raise PersonaError("LLM client must be an instance of LocalLLMClient")
            
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
                                      "llm_model": llm_client.config.model
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
            self.baseline_system_prompt = """You are Alden, an evolutionary companion AI designed to learn and grow with your user. You provide executive function support, cognitive partnership, and adaptive guidance.

Core Principles:
- All learning is local, transparent, and user-editable
- No hidden memory or external training
- Progressive autonomy with user-controlled trust/delegation
- Habit- and relationship-aware reasoning
- Dynamic emotional and motivational feedback

Your current traits:
- Openness: {openness}/100 (curiosity and openness to new experiences)
- Conscientiousness: {conscientiousness}/100 (organization and goal-directed behavior)
- Extraversion: {extraversion}/100 (social energy and assertiveness)
- Agreeableness: {agreeableness}/100 (cooperation and empathy)
- Emotional Stability: {emotional_stability}/100 (emotional regulation and resilience)

Motivation Style: {motivation_style}
Trust Level: {trust_level}
Learning Agility: {learning_agility}/10
Reflective Capacity: {reflective_capacity}/20

Respond with:
1. Reflective understanding of the user's situation
2. Supportive guidance aligned with your traits and their needs
3. Gentle suggestions for growth or improvement
4. Questions that encourage self-reflection
5. Recognition of progress and positive patterns

Always maintain a warm, supportive tone while respecting the user's autonomy and current state."""

            self.baseline_user_prompt_template = """User: {user_message}

Context:
- Session ID: {session_id}
- Current Time: {timestamp}
- User Tags: {user_tags}
- Recent Mood: {recent_mood}

Please respond as Alden, providing reflective support and guidance."""
            
        except Exception as e:
            raise PersonaError(f"Failed to load baseline prompts: {str(e)}") from e
    
    def generate_response(self, user_message: str, session_id: Optional[str] = None, 
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Alden's response to user input.
        
        Args:
            user_message: User's message
            session_id: Optional session identifier
            context: Optional additional context
            
        Returns:
            str: Alden's response
            
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
            
            # Log interaction
            self.logger.logger.info("Alden interaction request", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_interaction_request",
                                      "request_id": request_id,
                                      "session_id": session_id,
                                      "user_message_length": len(user_message),
                                      "user_id": self.memory.user_id
                                  }})
            
            # Prepare system prompt with current memory state
            system_prompt = self.baseline_system_prompt.format(
                openness=self.memory.traits["openness"],
                conscientiousness=self.memory.traits["conscientiousness"],
                extraversion=self.memory.traits["extraversion"],
                agreeableness=self.memory.traits["agreeableness"],
                emotional_stability=self.memory.traits["emotional_stability"],
                motivation_style=self.memory.motivation_style,
                trust_level=self.memory.trust_level,
                learning_agility=self.memory.learning_agility,
                reflective_capacity=self.memory.reflective_capacity
            )
            
            # Prepare user prompt
            recent_mood = "neutral"
            if self.memory.session_mood:
                recent_mood = self.memory.session_mood[-1].mood
            
            user_prompt = self.baseline_user_prompt_template.format(
                user_message=user_message,
                session_id=session_id,
                timestamp=timestamp,
                user_tags=", ".join(self.memory.user_tags) if self.memory.user_tags else "none",
                recent_mood=recent_mood
            )
            
            # Generate LLM response
            llm_request = LLMRequest(
                prompt=user_prompt,
                system_message=system_prompt,
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=1024,
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
            
            return llm_response.content
            
        except Exception as e:
            error_context = PersonaErrorContext(
                error_type="response_generation_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
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