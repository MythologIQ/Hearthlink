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
from vault.vault import Vault
from vault.schema import CommunalMemory

# Import error handling
from core.error_handling import (
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

class PerformanceMetricType(Enum):
    """Types of performance metrics tracked by Core."""
    SESSION_DURATION = "session_duration"
    TURN_DURATION = "turn_duration"
    PARTICIPANT_RESPONSE_TIME = "participant_response_time"
    MEMORY_OPERATIONS = "memory_operations"
    BREAKOUT_EFFICIENCY = "breakout_efficiency"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"
    THROUGHPUT = "throughput"
    CONTEXT_SWITCH_LATENCY = "context_switch_latency"

@dataclass
class PerformanceMetric:
    """Individual performance metric measurement."""
    metric_id: str
    metric_type: PerformanceMetricType
    session_id: str
    participant_id: Optional[str]
    timestamp: str
    value: float
    unit: str
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class SessionPerformanceStats:
    """Aggregated performance statistics for a session."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    total_duration: float = 0.0
    participant_count: int = 0
    total_turns: int = 0
    total_messages: int = 0
    breakout_rooms_created: int = 0
    error_count: int = 0
    memory_operations: int = 0
    average_turn_duration: float = 0.0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    context_switches: int = 0
    performance_score: float = 0.0

@dataclass
class ParticipantPerformanceStats:
    """Performance statistics for individual participants."""
    participant_id: str
    participant_type: ParticipantType
    session_id: str
    join_time: str
    leave_time: Optional[str]
    total_turns: int = 0
    total_messages: int = 0
    average_response_time: float = 0.0
    longest_turn_duration: float = 0.0
    shortest_turn_duration: float = 0.0
    contribution_score: float = 0.0
    engagement_score: float = 0.0
    accuracy_score: float = 0.0

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
        
        # Initialize performance tracking
        self.performance_metrics: List[PerformanceMetric] = []
        self.session_performance: Dict[str, SessionPerformanceStats] = {}
        self.participant_performance: Dict[str, ParticipantPerformanceStats] = {}
        self.performance_enabled = config.get('performance_tracking', True)
        self.metrics_retention_days = config.get('metrics_retention_days', 30)
        
        # Performance timing tracking
        self.operation_timings: Dict[str, float] = {}
        
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
            # Start performance tracking
            self.start_operation_timer("create_session")
            
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
            
            # Add session to registry first
            self.sessions[session_id] = session
            
            # Add initial participants
            if initial_participants:
                for participant_data in initial_participants:
                    self.add_participant(session_id, user_id, participant_data)
            
            # Log session creation
            self._log("create_session", user_id, session_id, "session", {
                "topic": topic,
                "participant_count": len(initial_participants or [])
            })
            
            # End performance tracking and record metrics
            duration = self.end_operation_timer("create_session", session_id)
            self.record_metric(
                PerformanceMetricType.CONTEXT_SWITCH_LATENCY,
                session_id, duration, "seconds", None, 
                {"operation": "create_session", "participant_count": len(initial_participants or [])}
            )
            
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
            
            # Log current turn completion and record turn duration
            if session.current_turn:
                # Calculate turn duration if we have start time
                turn_duration = 0.0
                if turn_manager.get("turn_start_time"):
                    try:
                        start_time = datetime.fromisoformat(turn_manager["turn_start_time"])
                        turn_duration = (datetime.now() - start_time).total_seconds()
                        
                        # Record turn duration metric
                        self.record_metric(
                            PerformanceMetricType.TURN_DURATION,
                            session_id, turn_duration, "seconds",
                            session.current_turn,
                            {"turn_index": turn_manager.get("current_index", 0)}
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to calculate turn duration: {e}")
                
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
            # Start timing memory operation
            start_time = time.time()
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
            
            # Record memory operation performance
            duration = time.time() - start_time
            self.record_metric(
                PerformanceMetricType.MEMORY_OPERATIONS,
                session_id, 1, "operations", None,
                {"event_type": event_type, "duration": duration}
            )
            
        except Exception as e:
            # Record error metric
            self.record_metric(
                PerformanceMetricType.ERROR_RATE,
                session_id, 1, "errors", None,
                {"operation": "update_communal_memory", "error_type": type(e).__name__}
            )
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

    # ==============================
    # Performance Metrics Tracking
    # ==============================
    
    def record_metric(self, metric_type: PerformanceMetricType, session_id: str, 
                     value: float, unit: str, participant_id: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None, 
                     tags: Optional[List[str]] = None) -> str:
        """
        Record a performance metric for analysis.
        
        Args:
            metric_type: Type of metric being recorded
            session_id: Session identifier
            value: Numeric value of the metric
            unit: Unit of measurement
            participant_id: Optional participant identifier
            context: Optional context information
            tags: Optional tags for categorization
            
        Returns:
            Metric ID for reference
        """
        if not self.performance_enabled:
            return ""
            
        try:
            metric_id = f"metric_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now().isoformat()
            
            metric = PerformanceMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                session_id=session_id,
                participant_id=participant_id,
                timestamp=timestamp,
                value=value,
                unit=unit,
                context=context or {},
                tags=tags or []
            )
            
            self.performance_metrics.append(metric)
            self._update_performance_stats(metric)
            
            self.logger.debug(f"Recorded performance metric: {metric_type.value} = {value} {unit}")
            return metric_id
            
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
            return ""
    
    def _update_performance_stats(self, metric: PerformanceMetric):
        """Update aggregated performance statistics."""
        try:
            session_id = metric.session_id
            
            # Update session performance stats
            if session_id not in self.session_performance:
                session = self.sessions.get(session_id)
                if session:
                    self.session_performance[session_id] = SessionPerformanceStats(
                        session_id=session_id,
                        start_time=session.created_at,
                        end_time=None
                    )
            
            if session_id in self.session_performance:
                stats = self.session_performance[session_id]
                
                # Update stats based on metric type
                if metric.metric_type == PerformanceMetricType.SESSION_DURATION:
                    stats.total_duration = metric.value
                elif metric.metric_type == PerformanceMetricType.TURN_DURATION:
                    stats.total_turns += 1
                    if stats.total_turns > 0:
                        stats.average_turn_duration = (
                            (stats.average_turn_duration * (stats.total_turns - 1) + metric.value) / 
                            stats.total_turns
                        )
                elif metric.metric_type == PerformanceMetricType.PARTICIPANT_RESPONSE_TIME:
                    current_avg = stats.average_response_time
                    count = stats.total_messages + 1
                    stats.average_response_time = ((current_avg * (count - 1)) + metric.value) / count
                    stats.total_messages += 1
                elif metric.metric_type == PerformanceMetricType.MEMORY_OPERATIONS:
                    stats.memory_operations += int(metric.value)
                elif metric.metric_type == PerformanceMetricType.ERROR_RATE:
                    stats.error_count += int(metric.value)
                elif metric.metric_type == PerformanceMetricType.CONTEXT_SWITCH_LATENCY:
                    stats.context_switches += 1
                
                # Calculate overall performance score
                stats.performance_score = self._calculate_performance_score(stats)
            
            # Update participant performance stats
            if metric.participant_id:
                self._update_participant_stats(metric)
                
        except Exception as e:
            self.logger.error(f"Failed to update performance stats: {e}")
    
    def _update_participant_stats(self, metric: PerformanceMetric):
        """Update participant-specific performance statistics."""
        try:
            participant_key = f"{metric.session_id}:{metric.participant_id}"
            
            if participant_key not in self.participant_performance:
                session = self.sessions.get(metric.session_id)
                participant = None
                if session:
                    participant = next((p for p in session.participants 
                                     if p.participant_id == metric.participant_id), None)
                
                if participant:
                    self.participant_performance[participant_key] = ParticipantPerformanceStats(
                        participant_id=metric.participant_id,
                        participant_type=participant.participant_type,
                        session_id=metric.session_id,
                        join_time=participant.joined_at
                    )
            
            if participant_key in self.participant_performance:
                stats = self.participant_performance[participant_key]
                
                if metric.metric_type == PerformanceMetricType.TURN_DURATION:
                    stats.total_turns += 1
                    if stats.longest_turn_duration == 0 or metric.value > stats.longest_turn_duration:
                        stats.longest_turn_duration = metric.value
                    if stats.shortest_turn_duration == 0 or metric.value < stats.shortest_turn_duration:
                        stats.shortest_turn_duration = metric.value
                
                elif metric.metric_type == PerformanceMetricType.PARTICIPANT_RESPONSE_TIME:
                    current_avg = stats.average_response_time
                    count = stats.total_messages + 1
                    stats.average_response_time = ((current_avg * (count - 1)) + metric.value) / count
                    stats.total_messages += 1
                
                # Calculate derived scores
                stats.contribution_score = self._calculate_contribution_score(stats)
                stats.engagement_score = self._calculate_engagement_score(stats)
                
        except Exception as e:
            self.logger.error(f"Failed to update participant stats: {e}")
    
    def _calculate_performance_score(self, stats: SessionPerformanceStats) -> float:
        """Calculate overall performance score for a session."""
        try:
            score = 100.0
            
            # Deduct points for errors
            if stats.total_turns > 0:
                error_rate = stats.error_count / stats.total_turns
                score -= error_rate * 30  # Max 30 point deduction for errors
            
            # Deduct points for slow response times
            if stats.average_response_time > 10.0:  # 10 seconds threshold
                score -= min(20, (stats.average_response_time - 10) * 2)
            
            # Bonus for high engagement
            if stats.total_messages > 50:  # High activity threshold
                score += min(10, stats.total_messages / 10)
            
            # Ensure score is between 0 and 100
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance score: {e}")
            return 50.0
    
    def _calculate_contribution_score(self, stats: ParticipantPerformanceStats) -> float:
        """Calculate contribution score for a participant."""
        try:
            # Base score on turn count and message count
            base_score = min(100.0, (stats.total_turns * 10) + (stats.total_messages * 2))
            
            # Adjust for response time quality
            if stats.average_response_time > 0:
                if stats.average_response_time < 5.0:
                    base_score *= 1.1  # Bonus for quick responses
                elif stats.average_response_time > 15.0:
                    base_score *= 0.9  # Penalty for slow responses
            
            return min(100.0, base_score)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate contribution score: {e}")
            return 50.0
    
    def _calculate_engagement_score(self, stats: ParticipantPerformanceStats) -> float:
        """Calculate engagement score for a participant."""
        try:
            # Base engagement on activity consistency
            if stats.total_turns == 0:
                return 0.0
            
            avg_turn_length = (stats.longest_turn_duration + stats.shortest_turn_duration) / 2
            consistency_score = 100.0 - min(50.0, abs(stats.longest_turn_duration - stats.shortest_turn_duration))
            
            # Factor in total participation
            participation_score = min(100.0, stats.total_turns * 5)
            
            # Weighted average
            return (consistency_score * 0.3) + (participation_score * 0.7)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate engagement score: {e}")
            return 50.0
    
    def start_operation_timer(self, operation_name: str):
        """Start timing an operation for performance measurement."""
        if self.performance_enabled:
            self.operation_timings[operation_name] = time.time()
    
    def end_operation_timer(self, operation_name: str, session_id: str, 
                          participant_id: Optional[str] = None) -> float:
        """End timing an operation and record the metric."""
        if not self.performance_enabled or operation_name not in self.operation_timings:
            return 0.0
        
        start_time = self.operation_timings.pop(operation_name, time.time())
        duration = time.time() - start_time
        
        # Record appropriate metric based on operation type
        if "turn" in operation_name.lower():
            self.record_metric(
                PerformanceMetricType.TURN_DURATION,
                session_id, duration, "seconds", 
                participant_id, {"operation": operation_name}
            )
        elif "response" in operation_name.lower():
            self.record_metric(
                PerformanceMetricType.PARTICIPANT_RESPONSE_TIME,
                session_id, duration, "seconds", 
                participant_id, {"operation": operation_name}
            )
        elif "context" in operation_name.lower():
            self.record_metric(
                PerformanceMetricType.CONTEXT_SWITCH_LATENCY,
                session_id, duration, "seconds", 
                None, {"operation": operation_name}
            )
        
        return duration
    
    def get_performance_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get performance summary for a session."""
        try:
            if session_id not in self.session_performance:
                return None
            
            stats = self.session_performance[session_id]
            
            # Get participant summaries
            participant_summaries = []
            for key, p_stats in self.participant_performance.items():
                if p_stats.session_id == session_id:
                    participant_summaries.append({
                        "participant_id": p_stats.participant_id,
                        "participant_type": p_stats.participant_type.value,
                        "total_turns": p_stats.total_turns,
                        "total_messages": p_stats.total_messages,
                        "average_response_time": p_stats.average_response_time,
                        "contribution_score": p_stats.contribution_score,
                        "engagement_score": p_stats.engagement_score
                    })
            
            # Get recent metrics
            recent_metrics = [
                {
                    "type": m.metric_type.value,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp,
                    "participant_id": m.participant_id
                }
                for m in self.performance_metrics[-50:]  # Last 50 metrics
                if m.session_id == session_id
            ]
            
            return {
                "session_stats": asdict(stats),
                "participant_stats": participant_summaries,
                "recent_metrics": recent_metrics,
                "performance_enabled": self.performance_enabled,
                "metrics_count": len([m for m in self.performance_metrics if m.session_id == session_id])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return None
    
    def export_performance_data(self, session_id: Optional[str] = None, 
                              format_type: str = "json") -> Optional[Dict[str, Any]]:
        """Export performance data for analysis."""
        try:
            # Filter metrics by session if specified
            if session_id:
                metrics = [m for m in self.performance_metrics if m.session_id == session_id]
                session_stats = {session_id: self.session_performance.get(session_id)}
                participant_stats = {k: v for k, v in self.participant_performance.items() 
                                   if v.session_id == session_id}
            else:
                metrics = self.performance_metrics
                session_stats = self.session_performance
                participant_stats = self.participant_performance
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics_count": len(metrics),
                "sessions_count": len(session_stats),
                "participants_count": len(participant_stats),
                "metrics": [asdict(m) for m in metrics],
                "session_stats": {k: asdict(v) for k, v in session_stats.items() if v},
                "participant_stats": {k: asdict(v) for k, v in participant_stats.items()},
                "format": format_type
            }
            
            self.logger.info(f"Exported performance data: {len(metrics)} metrics, {len(session_stats)} sessions")
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to export performance data: {e}")
            return None
    
    def cleanup_old_metrics(self):
        """Clean up old performance metrics based on retention policy."""
        try:
            if not self.performance_enabled:
                return
            
            cutoff_date = datetime.now().timestamp() - (self.metrics_retention_days * 24 * 3600)
            
            initial_count = len(self.performance_metrics)
            self.performance_metrics = [
                m for m in self.performance_metrics 
                if datetime.fromisoformat(m.timestamp).timestamp() > cutoff_date
            ]
            
            cleaned_count = initial_count - len(self.performance_metrics)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old performance metrics")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {e}")
    
    def get_performance_trends(self, session_id: str, 
                             metric_type: PerformanceMetricType,
                             time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance trends for analysis."""
        try:
            cutoff_time = datetime.now().timestamp() - (time_window_hours * 3600)
            
            relevant_metrics = [
                m for m in self.performance_metrics
                if (m.session_id == session_id and 
                    m.metric_type == metric_type and
                    datetime.fromisoformat(m.timestamp).timestamp() > cutoff_time)
            ]
            
            # Sort by timestamp
            relevant_metrics.sort(key=lambda x: x.timestamp)
            
            trends = []
            for metric in relevant_metrics:
                trends.append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "unit": metric.unit,
                    "participant_id": metric.participant_id,
                    "context": metric.context
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get performance trends: {e}")
            return [] 