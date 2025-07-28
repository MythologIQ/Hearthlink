#!/usr/bin/env python3
"""
Enhanced Core Session Manager with Deep Vault Integration
Provides advanced session management with communal memory mediation
"""

import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from contextlib import asynccontextmanager

# Import existing session manager
from core.session_manager import SessionManager, SessionInfo, ConversationMessage, MessageRole, SessionStatus

# Import Vault for persistent storage
from vault.vault import Vault
from vault.schema import CommunalMemory, PersonaMemory

# Import database manager
from database.database_manager import DatabaseManager

class SessionType(Enum):
    """Types of Core sessions"""
    SOLO = "solo"  # Single agent session
    COLLABORATIVE = "collaborative"  # Multi-agent collaboration
    ROUNDTABLE = "roundtable"  # Structured discussion
    BREAKOUT = "breakout"  # Focused breakout session
    PERFORMANCE_CHALLENGE = "performance_challenge"  # Agent evaluation

class AgentRole(Enum):
    """Roles agents can take in sessions"""
    FACILITATOR = "facilitator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"
    EVALUATOR = "evaluator"

@dataclass
class SessionParticipant:
    """Enhanced participant information"""
    id: str
    name: str
    type: str  # "persona", "external", "user"
    role: AgentRole
    capabilities: List[str]
    memory_access_level: str  # "read", "write", "full"
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    context_memory: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

@dataclass
class EnhancedSessionInfo(SessionInfo):
    """Enhanced session information with Core-specific data"""
    session_type: SessionType = SessionType.SOLO
    participants: List[SessionParticipant] = field(default_factory=list)
    communal_memory_id: Optional[str] = None
    vault_sync_enabled: bool = True
    performance_tracking: bool = True
    context_switching_count: int = 0
    breakout_rooms: List[str] = field(default_factory=list)
    shared_insights: List[Dict[str, Any]] = field(default_factory=list)
    session_objectives: List[str] = field(default_factory=list)

class EnhancedSessionManager(SessionManager):
    """Enhanced session manager with Core orchestration features"""
    
    def __init__(self, db_manager: DatabaseManager = None, vault: Vault = None, config: Dict[str, Any] = None):
        super().__init__(db_manager, config)
        self.vault = vault
        self.logger = logging.getLogger(__name__)
        
        # Core-specific tracking
        self.active_breakouts: Dict[str, List[str]] = {}  # session_id -> breakout_room_ids
        self.session_performance: Dict[str, Dict[str, Any]] = {}
        self.communal_memories: Dict[str, str] = {}  # session_id -> communal_memory_id
        
        # Agent coordination
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.turn_taking_state: Dict[str, Dict[str, Any]] = {}
        
    async def create_core_session(
        self, 
        user_id: str, 
        session_type: SessionType = SessionType.COLLABORATIVE,
        objectives: List[str] = None,
        initial_participants: List[SessionParticipant] = None
    ) -> EnhancedSessionInfo:
        """
        Create a new Core session with enhanced features.
        
        Args:
            user_id: User creating the session
            session_type: Type of session to create
            objectives: Session objectives/goals
            initial_participants: Initial participants to add
            
        Returns:
            EnhancedSessionInfo: Created session information
        """
        try:
            # Create base session
            session_id = f"core-{uuid.uuid4().hex[:12]}"
            session_token = f"token-{uuid.uuid4().hex}"
            
            # Create communal memory if vault is available
            communal_memory_id = None
            if self.vault:
                communal_memory_id = f"communal-{session_id}"
                communal_data = {
                    "session_id": session_id,
                    "session_type": session_type.value,
                    "created_at": datetime.now().isoformat(),
                    "objectives": objectives or [],
                    "participants": [],
                    "shared_context": {},
                    "insights": [],
                    "performance_data": {}
                }
                
                await asyncio.to_thread(
                    self.vault.create_or_update_communal,
                    communal_memory_id,
                    communal_data,
                    user_id
                )
                
                self.communal_memories[session_id] = communal_memory_id
            
            # Create enhanced session info
            enhanced_session = EnhancedSessionInfo(
                id=session_id,
                user_id=user_id,
                session_token=session_token,
                status=SessionStatus.ACTIVE,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=self.config.default_expiry_hours),
                agent_context={},
                metadata={
                    "session_type": session_type.value,
                    "created_by": "core_enhanced_session_manager"
                },
                session_type=session_type,
                participants=initial_participants or [],
                communal_memory_id=communal_memory_id,
                session_objectives=objectives or []
            )
            
            # Store in memory and database
            self._active_sessions[session_id] = enhanced_session
            
            # Initialize performance tracking
            if enhanced_session.performance_tracking:
                self.session_performance[session_id] = {
                    "start_time": datetime.now().isoformat(),
                    "messages_processed": 0,
                    "agent_switches": 0,
                    "memory_operations": 0,
                    "response_times": [],
                    "error_count": 0
                }
            
            # Initialize turn-taking for multi-agent sessions
            if session_type in [SessionType.COLLABORATIVE, SessionType.ROUNDTABLE]:
                self.turn_taking_state[session_id] = {
                    "current_turn": None,
                    "turn_queue": [],
                    "turn_history": [],
                    "turn_timeout": 300  # 5 minutes
                }
            
            self.logger.info(f"Created Core session {session_id} of type {session_type.value}")
            return enhanced_session
            
        except Exception as e:
            self.logger.error(f"Failed to create Core session: {e}")
            raise
    
    async def add_participant(
        self,
        session_id: str,
        participant: SessionParticipant,
        auto_sync_memory: bool = True
    ) -> bool:
        """
        Add a participant to an active session.
        
        Args:
            session_id: Target session ID
            participant: Participant to add
            auto_sync_memory: Whether to sync participant memory to communal
            
        Returns:
            bool: Success status
        """
        try:
            session = self._active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Add to session participants
            session.participants.append(participant)
            
            # Update communal memory if available
            if self.vault and session.communal_memory_id:
                communal_mem = await asyncio.to_thread(
                    self.vault.get_communal,
                    session.communal_memory_id,
                    session.user_id
                )
                
                if communal_mem:
                    communal_data = communal_mem.get("data", {})
                    if "participants" not in communal_data:
                        communal_data["participants"] = []
                    
                    communal_data["participants"].append({
                        "id": participant.id,
                        "name": participant.name,
                        "type": participant.type,
                        "role": participant.role.value,
                        "capabilities": participant.capabilities,
                        "joined_at": datetime.now().isoformat()
                    })
                    
                    await asyncio.to_thread(
                        self.vault.create_or_update_communal,
                        session.communal_memory_id,
                        communal_data,
                        session.user_id
                    )
            
            # Add to turn-taking queue for collaborative sessions
            if (session.session_type in [SessionType.COLLABORATIVE, SessionType.ROUNDTABLE] 
                and participant.role == AgentRole.PARTICIPANT):
                turn_state = self.turn_taking_state.get(session_id, {})
                if "turn_queue" in turn_state:
                    turn_state["turn_queue"].append(participant.id)
            
            # Update performance tracking
            if session_id in self.session_performance:
                self.session_performance[session_id]["agent_switches"] += 1
            
            self.logger.info(f"Added participant {participant.name} to session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add participant to session {session_id}: {e}")
            return False
    
    async def sync_agent_memory_to_communal(
        self,
        session_id: str,
        agent_id: str,
        memory_data: Dict[str, Any]
    ) -> bool:
        """
        Sync agent's relevant memory to communal session memory.
        
        Args:
            session_id: Target session ID
            agent_id: Agent whose memory to sync
            memory_data: Memory data to sync
            
        Returns:
            bool: Success status
        """
        try:
            session = self._active_sessions.get(session_id)
            if not session or not session.communal_memory_id or not self.vault:
                return False
            
            # Get current communal memory
            communal_mem = await asyncio.to_thread(
                self.vault.get_communal,
                session.communal_memory_id,
                session.user_id
            )
            
            if not communal_mem:
                return False
            
            communal_data = communal_mem.get("data", {})
            
            # Update shared context with agent memory
            if "shared_context" not in communal_data:
                communal_data["shared_context"] = {}
            
            communal_data["shared_context"][agent_id] = {
                "last_updated": datetime.now().isoformat(),
                "memory_excerpt": memory_data,
                "sync_type": "agent_memory_sync"
            }
            
            # Update memory operation count
            if "memory_operations" not in communal_data:
                communal_data["memory_operations"] = 0
            communal_data["memory_operations"] += 1
            
            # Save updated communal memory
            await asyncio.to_thread(
                self.vault.create_or_update_communal,
                session.communal_memory_id,
                communal_data,
                session.user_id
            )
            
            # Update performance tracking
            if session_id in self.session_performance:
                self.session_performance[session_id]["memory_operations"] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync agent memory to communal: {e}")
            return False
    
    async def create_breakout_room(
        self,
        parent_session_id: str,
        participants: List[str],
        objectives: List[str] = None
    ) -> Optional[str]:
        """
        Create a breakout room from main session.
        
        Args:
            parent_session_id: Parent session ID
            participants: List of participant IDs for breakout
            objectives: Specific objectives for breakout
            
        Returns:
            Optional[str]: Breakout room session ID if successful
        """
        try:
            parent_session = self._active_sessions.get(parent_session_id)
            if not parent_session:
                raise ValueError(f"Parent session {parent_session_id} not found")
            
            # Create breakout session
            breakout_participants = []
            for participant_id in participants:
                # Find participant in parent session
                participant = next(
                    (p for p in parent_session.participants if p.id == participant_id),
                    None
                )
                if participant:
                    breakout_participants.append(participant)
            
            breakout_session = await self.create_core_session(
                user_id=parent_session.user_id,
                session_type=SessionType.BREAKOUT,
                objectives=objectives,
                initial_participants=breakout_participants
            )
            
            # Link to parent session
            breakout_session.metadata["parent_session_id"] = parent_session_id
            parent_session.breakout_rooms.append(breakout_session.id)
            
            # Track breakout
            if parent_session_id not in self.active_breakouts:
                self.active_breakouts[parent_session_id] = []
            self.active_breakouts[parent_session_id].append(breakout_session.id)
            
            self.logger.info(f"Created breakout room {breakout_session.id} from {parent_session_id}")
            return breakout_session.id
            
        except Exception as e:
            self.logger.error(f"Failed to create breakout room: {e}")
            return None
    
    async def manage_turn_taking(
        self,
        session_id: str,
        action: str,
        participant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manage turn-taking in collaborative sessions.
        
        Args:
            session_id: Target session ID
            action: Action to take ("next", "assign", "skip", "status")
            participant_id: Optional participant ID for "assign" action
            
        Returns:
            Dict[str, Any]: Turn-taking status and result
        """
        try:
            session = self._active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            turn_state = self.turn_taking_state.get(session_id, {})
            if not turn_state:
                return {"error": "Turn-taking not enabled for this session"}
            
            result = {"action": action, "timestamp": datetime.now().isoformat()}
            
            if action == "next":
                # Move to next participant in queue
                if turn_state["turn_queue"]:
                    current_turn = turn_state["turn_queue"].pop(0)
                    turn_state["current_turn"] = current_turn
                    turn_state["turn_history"].append({
                        "participant_id": current_turn,
                        "started_at": datetime.now().isoformat()
                    })
                    # Add back to end of queue for round-robin
                    turn_state["turn_queue"].append(current_turn)
                    result["current_turn"] = current_turn
                else:
                    result["error"] = "No participants in turn queue"
            
            elif action == "assign" and participant_id:
                # Assign turn to specific participant
                turn_state["current_turn"] = participant_id
                turn_state["turn_history"].append({
                    "participant_id": participant_id,
                    "started_at": datetime.now().isoformat(),
                    "assigned": True
                })
                result["current_turn"] = participant_id
            
            elif action == "skip":
                # Skip current turn
                if turn_state["current_turn"]:
                    # Update history with skip
                    if turn_state["turn_history"]:
                        turn_state["turn_history"][-1]["skipped"] = True
                        turn_state["turn_history"][-1]["ended_at"] = datetime.now().isoformat()
                    
                    # Move to next
                    return await self.manage_turn_taking(session_id, "next")
            
            elif action == "status":
                # Return current status
                result.update({
                    "current_turn": turn_state.get("current_turn"),
                    "queue_length": len(turn_state.get("turn_queue", [])),
                    "turn_history_count": len(turn_state.get("turn_history", []))
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Turn-taking management failed: {e}")
            return {"error": str(e)}
    
    async def get_session_performance_metrics(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for a session.
        
        Args:
            session_id: Target session ID
            
        Returns:
            Dict[str, Any]: Performance metrics and statistics
        """
        try:
            session = self._active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            performance_data = self.session_performance.get(session_id, {})
            
            # Calculate derived metrics
            current_time = datetime.now()
            session_duration = (current_time - session.created_at).total_seconds()
            
            avg_response_time = 0
            if performance_data.get("response_times"):
                avg_response_time = sum(performance_data["response_times"]) / len(performance_data["response_times"])
            
            metrics = {
                "session_id": session_id,
                "session_type": session.session_type.value,
                "duration_seconds": session_duration,
                "participant_count": len(session.participants),
                "messages_processed": performance_data.get("messages_processed", 0),
                "agent_switches": performance_data.get("agent_switches", 0),
                "memory_operations": performance_data.get("memory_operations", 0),
                "error_count": performance_data.get("error_count", 0),
                "average_response_time": avg_response_time,
                "breakout_rooms_created": len(session.breakout_rooms),
                "context_switches": session.context_switching_count,
                "performance_score": 0  # Will be calculated
            }
            
            # Calculate performance score (0-100)
            score_factors = {
                "uptime": min(100, (session_duration / 3600) * 10),  # Points for session duration
                "activity": min(30, performance_data.get("messages_processed", 0) * 2),  # Activity points
                "efficiency": max(0, 20 - performance_data.get("error_count", 0) * 5),  # Efficiency points
                "collaboration": min(25, len(session.participants) * 5)  # Collaboration points
            }
            
            metrics["performance_score"] = sum(score_factors.values())
            metrics["score_breakdown"] = score_factors
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions and associated resources.
        
        Returns:
            int: Number of sessions cleaned up
        """
        cleaned_count = 0
        current_time = datetime.now()
        
        expired_sessions = []
        for session_id, session in self._active_sessions.items():
            if current_time > session.expires_at or session.status == SessionStatus.ENDED:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            try:
                session = self._active_sessions[session_id]
                
                # Archive communal memory if exists
                if session.communal_memory_id and self.vault:
                    # Mark as archived in vault
                    communal_mem = await asyncio.to_thread(
                        self.vault.get_communal,
                        session.communal_memory_id,
                        session.user_id
                    )
                    
                    if communal_mem:
                        communal_data = communal_mem.get("data", {})
                        communal_data["archived_at"] = current_time.isoformat()
                        communal_data["final_metrics"] = await self.get_session_performance_metrics(session_id)
                        
                        await asyncio.to_thread(
                            self.vault.create_or_update_communal,
                            session.communal_memory_id,
                            communal_data,
                            session.user_id
                        )
                
                # Clean up tracking data
                self._active_sessions.pop(session_id, None)
                self.session_performance.pop(session_id, None)
                self.turn_taking_state.pop(session_id, None)
                self.active_breakouts.pop(session_id, None)
                self.communal_memories.pop(session_id, None)
                
                cleaned_count += 1
                self.logger.info(f"Cleaned up expired session {session_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to cleanup session {session_id}: {e}")
        
        return cleaned_count