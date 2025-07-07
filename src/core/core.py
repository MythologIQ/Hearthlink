"""
Core - Communication Switch & Context Moderator

Orchestrator for multi-agent conversational interaction, roundtables, 
agent performance challenges, and context switching. Always user-controlled—
no agent or external participant is assigned without explicit user command.

Core's prime function is to facilitate the most effective collaboration 
between AI personas, including external agents, in live or breakout sessions.
"""

import os
import json
import uuid
import asyncio
import traceback
import time
from typing import Dict, Any, Optional, List, Tuple, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Import Vault for communal memory mediation
from ..vault.vault import Vault
from ..vault.schema import CommunalMemory

# Import error handling
from .error_handling import (
    CoreErrorHandler, CoreErrorRecovery, CoreErrorValidator, CoreErrorMetrics,
    SessionNotFoundError, ParticipantNotFoundError, InvalidOperationError,
    TurnTakingError, BreakoutRoomError, CommunalMemoryError, VaultIntegrationError,
    CoreErrorContext, ErrorCategory, ErrorSeverity
)

class ParticipantType(Enum):
    """Types of session participants."""
    PERSONA = "persona"
    EXTERNAL = "external"
    USER = "user"

class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"

class TurnStatus(Enum):
    """Turn-taking status."""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class Participant:
    """Session participant information."""
    id: str
    type: ParticipantType
    name: str
    role: Optional[str] = None
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    left_at: Optional[str] = None
    turn_order: Optional[int] = None
    is_active: bool = True

@dataclass
class SessionEvent:
    """Session event log entry."""
    event_id: str
    timestamp: str
    event_type: str  # join, leave, response, breakout_create, etc.
    participant_id: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BreakoutRoom:
    """Breakout room information."""
    breakout_id: str
    topic: str
    parent_session_id: str
    participants: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    session_log: List[SessionEvent] = field(default_factory=list)

@dataclass
class LiveFeedSettings:
    """Live feed configuration."""
    verbosity: str = "default"  # default, verbose, minimal
    hidden_responses: List[str] = field(default_factory=list)
    auto_include_external: bool = True
    show_metadata: bool = False

@dataclass
class Session:
    """Session/room information."""
    session_id: str
    created_by: str
    created_at: str
    topic: str
    participants: List[Participant] = field(default_factory=list)
    session_log: List[SessionEvent] = field(default_factory=list)
    breakouts: List[BreakoutRoom] = field(default_factory=list)
    live_feed_settings: LiveFeedSettings = field(default_factory=LiveFeedSettings)
    status: SessionStatus = SessionStatus.ACTIVE
    current_turn: Optional[str] = None
    turn_order: List[str] = field(default_factory=list)
    communal_memory_id: Optional[str] = None
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

class CoreError(Exception):
    """Core module specific exceptions."""
    pass

class Core:
    """
    Core orchestration module for multi-agent sessions.
    
    Manages session state, turn-taking, communal memory mediation,
    and context switching between personas and external agents.
    """
    
    def __init__(self, config: Dict[str, Any], vault: Vault, logger=None):
        """
        Initialize Core module.
        
        Args:
            config: Configuration dictionary
            vault: Vault instance for communal memory
            logger: Optional logger instance
        """
        self.config = config
        self.vault = vault
        self.logger = logger or logging.getLogger(__name__)
        
        # Session registry
        self.sessions: Dict[str, Session] = {}
        
        # Agent suggestion registry
        self.agent_suggestions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Turn-taking state
        self.turn_managers: Dict[str, Dict[str, Any]] = {}
        
        # Event callbacks for UI updates
        self.event_callbacks: List[Callable] = []
        
        # Initialize error handling
        self.error_handler = CoreErrorHandler(self.logger)
        self.error_metrics = CoreErrorMetrics()
        self.error_validator = CoreErrorValidator()
        
        # Setup error recovery strategies
        self._setup_error_recovery()
        
        self._log("core_initialized", "system", None, "system", None, {})

    def _setup_error_recovery(self):
        """Setup error recovery strategies for Core operations."""
        self.error_handler.register_recovery_strategy(
            ErrorCategory.SESSION_MANAGEMENT,
            CoreErrorRecovery.session_management_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.PARTICIPANT_MANAGEMENT,
            CoreErrorRecovery.participant_management_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.TURN_TAKING,
            CoreErrorRecovery.turn_taking_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.VAULT_INTEGRATION,
            CoreErrorRecovery.vault_integration_recovery
        )

    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log Core events with audit trail and error handling."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        if error:
            # Handle error through error handler
            error_context = CoreErrorContext(
                session_id=session_id,
                user_id=user_id,
                operation=action,
                metadata=details
            )
            
            # Create appropriate error type based on action
            if "session" in action.lower():
                core_error = SessionNotFoundError(session_id or "unknown", error_context)
            elif "participant" in action.lower():
                core_error = ParticipantNotFoundError("unknown", session_id or "unknown", error_context)
            elif "turn" in action.lower():
                core_error = TurnTakingError(str(error), error_context)
            elif "breakout" in action.lower():
                core_error = BreakoutRoomError(str(error), error_context)
            elif "memory" in action.lower() or "insight" in action.lower():
                core_error = CommunalMemoryError(str(error), error_context)
            else:
                core_error = InvalidOperationError(action, "unknown", error_context)
            
            # Handle error and record metrics
            recovery_start = time.time()
            recovered = self.error_handler.handle_error(core_error, details)
            recovery_time = time.time() - recovery_start
            
            self.error_metrics.record_error(core_error, recovery_time)
            
            self.logger.error(f"Core error: {action} - {error}", 
                             extra={"traceback": traceback.format_exc(), "details": details})
        else:
            self.logger.info(f"Core action: {action}", extra={"details": details})
        
        # Add to session audit log if session_id provided
        if session_id and session_id in self.sessions:
            self.sessions[session_id].audit_log.append(log_entry)
        
        # Trigger event callbacks for UI updates
        self._trigger_event_callbacks(log_entry)

    def _trigger_event_callbacks(self, event: Dict[str, Any]):
        """Trigger registered event callbacks for UI updates."""
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Event callback error: {e}")

    def register_event_callback(self, callback: Callable):
        """Register callback for Core events."""
        self.event_callbacks.append(callback)

    # Session Management
    def create_session(self, user_id: str, topic: str, 
                      initial_participants: List[Dict[str, Any]] = None) -> str:
        """
        Create a new session/room.
        
        Args:
            user_id: User creating the session
            topic: Session topic/description
            initial_participants: List of participant dictionaries
            
        Returns:
            Session ID
        """
        # Validate inputs
        if not user_id or not topic:
            error_context = CoreErrorContext(user_id=user_id, operation="create_session")
            raise InvalidOperationError("create_session", "invalid_input", error_context)
        
        try:
            session_id = f"core-{uuid.uuid4().hex[:8]}"
            
            # Create communal memory for session
            communal_memory_id = f"session-{session_id}"
            communal_data = {
                "session_id": session_id,
                "topic": topic,
                "created_at": datetime.now().isoformat(),
                "participants": [],
                "context": {},
                "shared_insights": []
            }
            self.vault.create_or_update_communal(communal_memory_id, communal_data, user_id)
            
            # Create session
            session = Session(
                session_id=session_id,
                created_by=user_id,
                created_at=datetime.now().isoformat(),
                topic=topic,
                communal_memory_id=communal_memory_id
            )
            
            # Add initial participants
            if initial_participants:
                for participant_data in initial_participants:
                    self.add_participant(session_id, user_id, participant_data)
            
            self.sessions[session_id] = session
            
            # Log session creation
            self._log("create_session", user_id, session_id, "session", {
                "topic": topic,
                "participant_count": len(initial_participants or [])
            })
            
            return session_id
            
        except Exception as e:
            self._log("create_session", user_id, None, "session", {"topic": topic}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to create session: {e}")

    def add_participant(self, session_id: str, user_id: str, 
                       participant_data: Dict[str, Any]) -> bool:
        """
        Add participant to session.
        
        Args:
            session_id: Session to add participant to
            user_id: User adding the participant
            participant_data: Participant information
            
        Returns:
            Success status
        """
        # Validate inputs
        if not self.error_validator.validate_session_id(session_id):
            error_context = CoreErrorContext(session_id=session_id, user_id=user_id, operation="add_participant")
            raise SessionNotFoundError(session_id, error_context)
        
        if not self.error_validator.validate_participant_data(participant_data):
            error_context = CoreErrorContext(session_id=session_id, user_id=user_id, operation="add_participant")
            raise InvalidOperationError("add_participant", "invalid_participant_data", error_context)
        
        try:
            if session_id not in self.sessions:
                error_context = CoreErrorContext(session_id=session_id, user_id=user_id, operation="add_participant")
                raise SessionNotFoundError(session_id, error_context)
            
            session = self.sessions[session_id]
            
            # Validate participant data
            required_fields = ["id", "type", "name"]
            if not all(field in participant_data for field in required_fields):
                raise CoreError("Missing required participant fields")
            
            # Create participant
            participant = Participant(
                id=participant_data["id"],
                type=ParticipantType(participant_data["type"]),
                name=participant_data["name"],
                role=participant_data.get("role"),
                turn_order=len(session.participants)
            )
            
            session.participants.append(participant)
            
            # Add to turn order if not already present
            if participant.id not in session.turn_order:
                session.turn_order.append(participant.id)
            
            # Log participant addition
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="join",
                participant_id=participant.id,
                metadata={"role": participant.role}
            )
            session.session_log.append(event)
            
            # Update communal memory
            self._update_communal_memory(session_id, "participant_added", {
                "participant_id": participant.id,
                "participant_name": participant.name,
                "role": participant.role
            })
            
            self._log("add_participant", user_id, session_id, "participant", {
                "participant_id": participant.id,
                "participant_name": participant.name,
                "role": participant.role
            })
            
            return True
            
        except Exception as e:
            self._log("add_participant", user_id, session_id, "participant", 
                     participant_data, result="failure", error=e)
            raise CoreError(f"Failed to add participant: {e}")

    def remove_participant(self, session_id: str, user_id: str, 
                          participant_id: str) -> bool:
        """
        Remove participant from session.
        
        Args:
            session_id: Session to remove participant from
            user_id: User removing the participant
            participant_id: ID of participant to remove
            
        Returns:
            Success status
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Find and remove participant
            participant = None
            for p in session.participants:
                if p.id == participant_id:
                    participant = p
                    p.left_at = datetime.now().isoformat()
                    p.is_active = False
                    break
            
            if not participant:
                raise CoreError(f"Participant {participant_id} not found in session")
            
            # Remove from turn order
            if participant_id in session.turn_order:
                session.turn_order.remove(participant_id)
            
            # Log participant removal
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="leave",
                participant_id=participant_id
            )
            session.session_log.append(event)
            
            # Update communal memory
            self._update_communal_memory(session_id, "participant_removed", {
                "participant_id": participant_id,
                "participant_name": participant.name
            })
            
            self._log("remove_participant", user_id, session_id, "participant", {
                "participant_id": participant_id,
                "participant_name": participant.name
            })
            
            return True
            
        except Exception as e:
            self._log("remove_participant", user_id, session_id, "participant", 
                     {"participant_id": participant_id}, result="failure", error=e)
            raise CoreError(f"Failed to remove participant: {e}")

    # Turn-taking Management
    def start_turn_taking(self, session_id: str, user_id: str, 
                         turn_order: Optional[List[str]] = None) -> bool:
        """
        Start turn-taking in session.
        
        Args:
            session_id: Session to start turn-taking in
            user_id: User starting turn-taking
            turn_order: Optional custom turn order
            
        Returns:
            Success status
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Set turn order
            if turn_order:
                # Validate all participants exist
                participant_ids = [p.id for p in session.participants if p.is_active]
                if not all(pid in participant_ids for pid in turn_order):
                    raise CoreError("Invalid participant in turn order")
                session.turn_order = turn_order
            else:
                # Use default order (order of joining)
                session.turn_order = [p.id for p in session.participants if p.is_active]
            
            # Set first turn
            if session.turn_order:
                session.current_turn = session.turn_order[0]
            
            # Initialize turn manager
            self.turn_managers[session_id] = {
                "current_index": 0,
                "turn_start_time": datetime.now().isoformat(),
                "turn_timeout": self.config.get("turn_timeout", 300),  # 5 minutes default
                "auto_advance": self.config.get("auto_advance", True)
            }
            
            self._log("start_turn_taking", user_id, session_id, "turn_taking", {
                "turn_order": session.turn_order,
                "current_turn": session.current_turn
            })
            
            return True
            
        except Exception as e:
            self._log("start_turn_taking", user_id, session_id, "turn_taking", 
                     {"turn_order": turn_order}, result="failure", error=e)
            raise CoreError(f"Failed to start turn-taking: {e}")

    def advance_turn(self, session_id: str, user_id: str) -> Optional[str]:
        """
        Advance to next turn in session.
        
        Args:
            session_id: Session to advance turn in
            user_id: User advancing turn
            
        Returns:
            ID of next participant, or None if turn-taking complete
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            turn_manager = self.turn_managers.get(session_id)
            
            if not turn_manager:
                raise CoreError("Turn-taking not started in session")
            
            # Log current turn completion
            if session.current_turn:
                event = SessionEvent(
                    event_id=f"event-{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now().isoformat(),
                    event_type="turn_complete",
                    participant_id=session.current_turn
                )
                session.session_log.append(event)
            
            # Advance to next turn
            current_index = turn_manager["current_index"]
            next_index = current_index + 1
            
            if next_index < len(session.turn_order):
                turn_manager["current_index"] = next_index
                session.current_turn = session.turn_order[next_index]
                turn_manager["turn_start_time"] = datetime.now().isoformat()
                
                # Log turn start
                event = SessionEvent(
                    event_id=f"event-{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now().isoformat(),
                    event_type="turn_start",
                    participant_id=session.current_turn
                )
                session.session_log.append(event)
                
                self._log("advance_turn", user_id, session_id, "turn_taking", {
                    "previous_turn": session.turn_order[current_index],
                    "current_turn": session.current_turn,
                    "turn_index": next_index
                })
                
                return session.current_turn
            else:
                # Turn-taking complete
                session.current_turn = None
                self._log("turn_taking_complete", user_id, session_id, "turn_taking", {
                    "total_turns": len(session.turn_order)
                })
                return None
                
        except Exception as e:
            self._log("advance_turn", user_id, session_id, "turn_taking", {}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to advance turn: {e}")

    def set_current_turn(self, session_id: str, user_id: str, 
                        participant_id: str) -> bool:
        """
        Manually set current turn to specific participant.
        
        Args:
            session_id: Session to modify
            user_id: User setting turn
            participant_id: ID of participant to set as current turn
            
        Returns:
            Success status
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Validate participant exists and is active
            participant = None
            for p in session.participants:
                if p.id == participant_id and p.is_active:
                    participant = p
                    break
            
            if not participant:
                raise CoreError(f"Active participant {participant_id} not found")
            
            # Update turn manager
            if session_id in self.turn_managers:
                turn_manager = self.turn_managers[session_id]
                if participant_id in session.turn_order:
                    turn_manager["current_index"] = session.turn_order.index(participant_id)
                    turn_manager["turn_start_time"] = datetime.now().isoformat()
            
            # Set current turn
            previous_turn = session.current_turn
            session.current_turn = participant_id
            
            # Log turn change
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="turn_set",
                participant_id=participant_id,
                metadata={"previous_turn": previous_turn}
            )
            session.session_log.append(event)
            
            self._log("set_current_turn", user_id, session_id, "turn_taking", {
                "previous_turn": previous_turn,
                "current_turn": participant_id
            })
            
            return True
            
        except Exception as e:
            self._log("set_current_turn", user_id, session_id, "turn_taking", 
                     {"participant_id": participant_id}, result="failure", error=e)
            raise CoreError(f"Failed to set current turn: {e}")

    # Breakout Room Management
    def create_breakout(self, session_id: str, user_id: str, topic: str, 
                       participant_ids: List[str]) -> str:
        """
        Create breakout room within session.
        
        Args:
            session_id: Parent session ID
            user_id: User creating breakout
            topic: Breakout topic
            participant_ids: List of participant IDs to include
            
        Returns:
            Breakout room ID
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Validate participants exist in parent session
            session_participant_ids = [p.id for p in session.participants if p.is_active]
            if not all(pid in session_participant_ids for pid in participant_ids):
                raise CoreError("Invalid participant in breakout")
            
            # Create breakout room
            breakout_id = f"{session_id}-breakout-{uuid.uuid4().hex[:8]}"
            breakout = BreakoutRoom(
                breakout_id=breakout_id,
                topic=topic,
                parent_session_id=session_id,
                participants=participant_ids
            )
            
            session.breakouts.append(breakout)
            
            # Log breakout creation
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="breakout_create",
                metadata={
                    "breakout_id": breakout_id,
                    "topic": topic,
                    "participants": participant_ids
                }
            )
            session.session_log.append(event)
            
            self._log("create_breakout", user_id, session_id, "breakout", {
                "breakout_id": breakout_id,
                "topic": topic,
                "participant_count": len(participant_ids)
            })
            
            return breakout_id
            
        except Exception as e:
            self._log("create_breakout", user_id, session_id, "breakout", 
                     {"topic": topic, "participants": participant_ids}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to create breakout: {e}")

    def end_breakout(self, session_id: str, user_id: str, 
                    breakout_id: str) -> bool:
        """
        End breakout room.
        
        Args:
            session_id: Parent session ID
            user_id: User ending breakout
            breakout_id: Breakout room ID to end
            
        Returns:
            Success status
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Find and end breakout
            breakout = None
            for b in session.breakouts:
                if b.breakout_id == breakout_id and not b.ended_at:
                    breakout = b
                    b.ended_at = datetime.now().isoformat()
                    break
            
            if not breakout:
                raise CoreError(f"Active breakout {breakout_id} not found")
            
            # Log breakout end
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="breakout_end",
                metadata={
                    "breakout_id": breakout_id,
                    "topic": breakout.topic,
                    "duration": "calculated"
                }
            )
            session.session_log.append(event)
            
            self._log("end_breakout", user_id, session_id, "breakout", {
                "breakout_id": breakout_id,
                "topic": breakout.topic
            })
            
            return True
            
        except Exception as e:
            self._log("end_breakout", user_id, session_id, "breakout", 
                     {"breakout_id": breakout_id}, result="failure", error=e)
            raise CoreError(f"Failed to end breakout: {e}")

    # Communal Memory Mediation
    def _update_communal_memory(self, session_id: str, event_type: str, 
                               data: Dict[str, Any]):
        """Update communal memory for session."""
        try:
            session = self.sessions[session_id]
            if not session.communal_memory_id:
                return
            
            # Get current communal memory
            communal_mem = self.vault.get_communal(session.communal_memory_id, session.created_by)
            if not communal_mem:
                return
            
            communal_data = communal_mem["data"]
            
            # Update based on event type
            if event_type == "participant_added":
                communal_data["participants"].append({
                    "id": data["participant_id"],
                    "name": data["participant_name"],
                    "role": data.get("role"),
                    "joined_at": datetime.now().isoformat()
                })
            elif event_type == "participant_removed":
                # Mark participant as left
                for p in communal_data["participants"]:
                    if p["id"] == data["participant_id"]:
                        p["left_at"] = datetime.now().isoformat()
                        break
            elif event_type == "context_update":
                communal_data["context"].update(data)
            elif event_type == "insight_shared":
                communal_data["shared_insights"].append({
                    "timestamp": datetime.now().isoformat(),
                    "participant_id": data["participant_id"],
                    "insight": data["insight"],
                    "context": data.get("context", {})
                })
            
            # Update communal memory
            self.vault.create_or_update_communal(
                session.communal_memory_id, communal_data, session.created_by
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update communal memory: {e}")

    def share_insight(self, session_id: str, participant_id: str, 
                     insight: str, context: Dict[str, Any] = None) -> bool:
        """
        Share insight to communal memory.
        
        Args:
            session_id: Session to share insight in
            participant_id: ID of participant sharing insight
            insight: Insight content
            context: Optional context information
            
        Returns:
            Success status
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Validate participant exists and is active
            participant = None
            for p in session.participants:
                if p.id == participant_id and p.is_active:
                    participant = p
                    break
            
            if not participant:
                raise CoreError(f"Active participant {participant_id} not found")
            
            # Update communal memory
            self._update_communal_memory(session_id, "insight_shared", {
                "participant_id": participant_id,
                "insight": insight,
                "context": context or {}
            })
            
            # Log insight sharing
            event = SessionEvent(
                event_id=f"event-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                event_type="insight_shared",
                participant_id=participant_id,
                content=insight,
                metadata={"context": context}
            )
            session.session_log.append(event)
            
            self._log("share_insight", session.created_by, session_id, "communal", {
                "participant_id": participant_id,
                "insight_length": len(insight)
            })
            
            return True
            
        except Exception as e:
            self._log("share_insight", session.created_by if session_id in self.sessions else "unknown", 
                     session_id, "communal", {"participant_id": participant_id}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to share insight: {e}")

    # Session State Management
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        # Validate session ID
        if not self.error_validator.validate_session_id(session_id):
            error_context = CoreErrorContext(session_id=session_id, operation="get_session")
            raise SessionNotFoundError(session_id, error_context)
        
        session = self.sessions.get(session_id)
        if not session:
            error_context = CoreErrorContext(session_id=session_id, operation="get_session")
            raise SessionNotFoundError(session_id, error_context)
        
        return session

    def get_active_sessions(self) -> List[Session]:
        """Get all active sessions."""
        return [s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE]

    def pause_session(self, session_id: str, user_id: str) -> bool:
        """Pause session."""
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            session.status = SessionStatus.PAUSED
            
            self._log("pause_session", user_id, session_id, "session", {})
            return True
            
        except Exception as e:
            self._log("pause_session", user_id, session_id, "session", {}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to pause session: {e}")

    def resume_session(self, session_id: str, user_id: str) -> bool:
        """Resume paused session."""
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            session.status = SessionStatus.ACTIVE
            
            self._log("resume_session", user_id, session_id, "session", {})
            return True
            
        except Exception as e:
            self._log("resume_session", user_id, session_id, "session", {}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to resume session: {e}")

    def end_session(self, session_id: str, user_id: str) -> bool:
        """End session."""
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            session.status = SessionStatus.ENDED
            
            # End any active breakouts
            for breakout in session.breakouts:
                if not breakout.ended_at:
                    breakout.ended_at = datetime.now().isoformat()
            
            # Clear turn manager
            if session_id in self.turn_managers:
                del self.turn_managers[session_id]
            
            self._log("end_session", user_id, session_id, "session", {})
            return True
            
        except Exception as e:
            self._log("end_session", user_id, session_id, "session", {}, 
                     result="failure", error=e)
            raise CoreError(f"Failed to end session: {e}")

    # Export and Logging
    def export_session_log(self, session_id: str, user_id: str, 
                          include_hidden: bool = False) -> Optional[str]:
        """
        Export session log.
        
        Args:
            session_id: Session to export
            user_id: User requesting export
            include_hidden: Whether to include hidden responses
            
        Returns:
            JSON string of session log
        """
        try:
            if session_id not in self.sessions:
                raise CoreError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Filter events based on settings
            events = session.session_log
            if not include_hidden:
                hidden_responses = session.live_feed_settings.hidden_responses
                events = [e for e in events if e.event_id not in hidden_responses]
            
            export_data = {
                "session_id": session.session_id,
                "topic": session.topic,
                "created_at": session.created_at,
                "status": session.status.value,
                "participants": [asdict(p) for p in session.participants],
                "events": [asdict(e) for e in events],
                "breakouts": [asdict(b) for b in session.breakouts],
                "audit_log": session.audit_log,
                "exported_at": datetime.now().isoformat(),
                "exported_by": user_id
            }
            
            self._log("export_session_log", user_id, session_id, "export", {
                "include_hidden": include_hidden,
                "event_count": len(events)
            })
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            self._log("export_session_log", user_id, session_id, "export", 
                     {"include_hidden": include_hidden}, result="failure", error=e)
            raise CoreError(f"Failed to export session log: {e}")

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary for UI display."""
        try:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            active_participants = [p for p in session.participants if p.is_active]
            
            return {
                "session_id": session.session_id,
                "topic": session.topic,
                "status": session.status.value,
                "participant_count": len(active_participants),
                "current_turn": session.current_turn,
                "breakout_count": len([b for b in session.breakouts if not b.ended_at]),
                "event_count": len(session.session_log),
                "created_at": session.created_at
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session summary: {e}")
            return None 