"""
Core API - FastAPI endpoints for Core orchestration module.

Provides REST API endpoints for session management, turn-taking,
breakout rooms, and communal memory mediation.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import json
import logging

from .core import Core, Session, Participant, ParticipantType, SessionStatus, CoreError

# Pydantic models for API requests/responses
class ParticipantRequest(BaseModel):
    id: str = Field(..., description="Participant ID")
    type: str = Field(..., description="Participant type (persona, external, user)")
    name: str = Field(..., description="Participant name")
    role: Optional[str] = Field(None, description="Participant role")

class SessionCreateRequest(BaseModel):
    topic: str = Field(..., description="Session topic")
    initial_participants: Optional[List[ParticipantRequest]] = Field(None, description="Initial participants")

class SessionResponse(BaseModel):
    session_id: str
    topic: str
    created_by: str
    created_at: str
    status: str
    participant_count: int
    current_turn: Optional[str]
    breakout_count: int
    event_count: int

class ParticipantResponse(BaseModel):
    id: str
    type: str
    name: str
    role: Optional[str]
    joined_at: str
    left_at: Optional[str]
    is_active: bool

class SessionEventResponse(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    participant_id: Optional[str]
    content: Optional[str]
    metadata: Dict[str, Any]

class BreakoutCreateRequest(BaseModel):
    topic: str = Field(..., description="Breakout topic")
    participant_ids: List[str] = Field(..., description="Participant IDs to include")

class BreakoutResponse(BaseModel):
    breakout_id: str
    topic: str
    parent_session_id: str
    participants: List[str]
    created_at: str
    ended_at: Optional[str]

class InsightShareRequest(BaseModel):
    insight: str = Field(..., description="Insight content")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")

class TurnAdvanceRequest(BaseModel):
    manual_participant_id: Optional[str] = Field(None, description="Manual participant ID for turn")

class LiveFeedSettingsRequest(BaseModel):
    verbosity: Optional[str] = Field(None, description="Feed verbosity (default, verbose, minimal)")
    auto_include_external: Optional[bool] = Field(None, description="Auto-include external participants")
    show_metadata: Optional[bool] = Field(None, description="Show metadata in feed")

class CoreAPI:
    """FastAPI application for Core module."""
    
    def __init__(self, core: Core):
        """
        Initialize Core API.
        
        Args:
            core: Core module instance
        """
        self.core = core
        self.app = FastAPI(
            title="Hearthlink Core API",
            description="API for Core orchestration module",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.post("/api/core/session", response_model=Dict[str, str])
        async def create_session(
            request: SessionCreateRequest,
            user_id: str = Depends(self._get_user_id)
        ):
            """Create new session/room."""
            try:
                initial_participants = None
                if request.initial_participants:
                    initial_participants = [p.dict() for p in request.initial_participants]
                
                session_id = self.core.create_session(
                    user_id, request.topic, initial_participants
                )
                
                return {"session_id": session_id, "status": "created"}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Session creation error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/api/core/session/{session_id}", response_model=SessionResponse)
        async def get_session(session_id: str):
            """Get session information."""
            try:
                session = self.core.get_session(session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                summary = self.core.get_session_summary(session_id)
                if not summary:
                    raise HTTPException(status_code=404, detail="Session summary not found")
                
                return SessionResponse(**summary)
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Session retrieval error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/api/core/sessions", response_model=List[SessionResponse])
        async def get_active_sessions():
            """Get all active sessions."""
            try:
                sessions = self.core.get_active_sessions()
                summaries = []
                
                for session in sessions:
                    summary = self.core.get_session_summary(session.session_id)
                    if summary:
                        summaries.append(SessionResponse(**summary))
                
                return summaries
                
            except Exception as e:
                logging.error(f"Active sessions retrieval error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/participants")
        async def add_participant(
            session_id: str,
            participant: ParticipantRequest,
            user_id: str = Depends(self._get_user_id)
        ):
            """Add participant to session."""
            try:
                success = self.core.add_participant(session_id, user_id, participant.dict())
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to add participant")
                
                return {"status": "participant_added", "participant_id": participant.id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Add participant error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.delete("/api/core/session/{session_id}/participants/{participant_id}")
        async def remove_participant(
            session_id: str,
            participant_id: str,
            user_id: str = Depends(self._get_user_id)
        ):
            """Remove participant from session."""
            try:
                success = self.core.remove_participant(session_id, user_id, participant_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to remove participant")
                
                return {"status": "participant_removed", "participant_id": participant_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Remove participant error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/api/core/session/{session_id}/participants", response_model=List[ParticipantResponse])
        async def get_session_participants(session_id: str):
            """Get session participants."""
            try:
                session = self.core.get_session(session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                participants = []
                for p in session.participants:
                    participants.append(ParticipantResponse(
                        id=p.id,
                        type=p.type.value,
                        name=p.name,
                        role=p.role,
                        joined_at=p.joined_at,
                        left_at=p.left_at,
                        is_active=p.is_active
                    ))
                
                return participants
                
            except Exception as e:
                logging.error(f"Get participants error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/turn-taking/start")
        async def start_turn_taking(
            session_id: str,
            turn_order: Optional[List[str]] = None,
            user_id: str = Depends(self._get_user_id)
        ):
            """Start turn-taking in session."""
            try:
                success = self.core.start_turn_taking(session_id, user_id, turn_order)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to start turn-taking")
                
                return {"status": "turn_taking_started", "session_id": session_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Start turn-taking error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/turn-taking/advance")
        async def advance_turn(
            session_id: str,
            request: TurnAdvanceRequest,
            user_id: str = Depends(self._get_user_id)
        ):
            """Advance turn in session."""
            try:
                if request.manual_participant_id:
                    # Set specific participant as current turn
                    success = self.core.set_current_turn(session_id, user_id, request.manual_participant_id)
                    if not success:
                        raise HTTPException(status_code=400, detail="Failed to set current turn")
                    next_turn = request.manual_participant_id
                else:
                    # Advance to next turn
                    next_turn = self.core.advance_turn(session_id, user_id)
                
                return {
                    "status": "turn_advanced" if next_turn else "turn_taking_complete",
                    "current_turn": next_turn
                }
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Advance turn error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/breakout")
        async def create_breakout(
            session_id: str,
            request: BreakoutCreateRequest,
            user_id: str = Depends(self._get_user_id)
        ):
            """Create breakout room."""
            try:
                breakout_id = self.core.create_breakout(
                    session_id, user_id, request.topic, request.participant_ids
                )
                
                return {"status": "breakout_created", "breakout_id": breakout_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Create breakout error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.delete("/api/core/session/{session_id}/breakout/{breakout_id}")
        async def end_breakout(
            session_id: str,
            breakout_id: str,
            user_id: str = Depends(self._get_user_id)
        ):
            """End breakout room."""
            try:
                success = self.core.end_breakout(session_id, user_id, breakout_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to end breakout")
                
                return {"status": "breakout_ended", "breakout_id": breakout_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"End breakout error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/insights")
        async def share_insight(
            session_id: str,
            request: InsightShareRequest,
            participant_id: str = Depends(self._get_participant_id)
        ):
            """Share insight to communal memory."""
            try:
                success = self.core.share_insight(
                    session_id, participant_id, request.insight, request.context
                )
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to share insight")
                
                return {"status": "insight_shared", "participant_id": participant_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Share insight error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/api/core/session/{session_id}/log")
        async def export_session_log(
            session_id: str,
            include_hidden: bool = False,
            user_id: str = Depends(self._get_user_id)
        ):
            """Export session log."""
            try:
                export_data = self.core.export_session_log(session_id, user_id, include_hidden)
                if not export_data:
                    raise HTTPException(status_code=404, detail="Session log not found")
                
                return {"status": "log_exported", "data": json.loads(export_data)}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Export log error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.patch("/api/core/session/{session_id}/settings")
        async def update_live_feed_settings(
            session_id: str,
            request: LiveFeedSettingsRequest,
            user_id: str = Depends(self._get_user_id)
        ):
            """Update live feed settings."""
            try:
                session = self.core.get_session(session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                # Update settings
                if request.verbosity is not None:
                    session.live_feed_settings.verbosity = request.verbosity
                if request.auto_include_external is not None:
                    session.live_feed_settings.auto_include_external = request.auto_include_external
                if request.show_metadata is not None:
                    session.live_feed_settings.show_metadata = request.show_metadata
                
                return {"status": "settings_updated", "session_id": session_id}
                
            except Exception as e:
                logging.error(f"Update settings error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/pause")
        async def pause_session(
            session_id: str,
            user_id: str = Depends(self._get_user_id)
        ):
            """Pause session."""
            try:
                success = self.core.pause_session(session_id, user_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to pause session")
                
                return {"status": "session_paused", "session_id": session_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Pause session error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/core/session/{session_id}/resume")
        async def resume_session(
            session_id: str,
            user_id: str = Depends(self._get_user_id)
        ):
            """Resume session."""
            try:
                success = self.core.resume_session(session_id, user_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to resume session")
                
                return {"status": "session_resumed", "session_id": session_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Resume session error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.delete("/api/core/session/{session_id}")
        async def end_session(
            session_id: str,
            user_id: str = Depends(self._get_user_id)
        ):
            """End session."""
            try:
                success = self.core.end_session(session_id, user_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to end session")
                
                return {"status": "session_ended", "session_id": session_id}
                
            except CoreError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"End session error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _get_user_id(self) -> str:
        """Get user ID from request context."""
        # TODO: Implement proper authentication/authorization
        # For now, return a default user ID
        return "default-user"
    
    def _get_participant_id(self) -> str:
        """Get participant ID from request context."""
        # TODO: Implement proper participant identification
        # For now, return a default participant ID
        return "default-participant"
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application instance."""
        return self.app 