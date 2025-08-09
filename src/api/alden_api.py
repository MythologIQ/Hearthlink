#!/usr/bin/env python3
"""
Alden API Endpoint

FastAPI-based REST API for Alden persona interactions.
Provides endpoints for message exchange, memory management, and persona configuration.

References:
- hearthlink_system_documentation_master.md: API contracts and RBAC requirements
- PLATINUM_BLOCKERS.md: Security and compliance requirements

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError
from personas.alden import AldenPersona, PersonaError, create_alden_persona
from llm.local_llm_client import LLMError

try:
    from fastapi import FastAPI, HTTPException, Depends, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, validator
    import uvicorn
except ImportError as e:
    print(f"FastAPI dependencies not installed: {e}")
    print("Install with: pip install fastapi uvicorn")
    sys.exit(1)


# Pydantic models for API requests/responses
class MessageRequest(BaseModel):
    """Request model for sending messages to Alden."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class MessageResponse(BaseModel):
    """Response model for Alden's messages."""
    response: str = Field(..., description="Alden's response")
    session_id: str = Field(..., description="Session identifier")
    timestamp: str = Field(..., description="Response timestamp")
    model: str = Field(..., description="LLM model used")
    response_time: float = Field(..., description="Response time in seconds")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")


class TraitUpdateRequest(BaseModel):
    """Request model for updating Alden's traits."""
    trait_name: str = Field(..., description="Name of trait to update")
    new_value: int = Field(..., ge=0, le=100, description="New trait value (0-100)")
    reason: str = Field("user_update", description="Reason for update")


class CorrectionRequest(BaseModel):
    """Request model for adding correction events."""
    event_type: str = Field(..., description="Type of correction: 'positive' or 'negative'")
    description: str = Field(..., min_length=1, description="Description of correction")
    impact_score: float = Field(0.0, ge=-1.0, le=1.0, description="Impact score (-1.0 to 1.0)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class MoodRequest(BaseModel):
    """Request model for recording session mood."""
    session_id: str = Field(..., description="Session identifier")
    mood: str = Field(..., description="Mood: 'positive', 'neutral', or 'negative'")
    score: int = Field(..., ge=0, le=100, description="Mood score (0-100)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class StatusResponse(BaseModel):
    """Response model for Alden's status."""
    persona_id: str = Field(..., description="Persona identifier")
    user_id: str = Field(..., description="User identifier")
    schema_version: str = Field(..., description="Schema version")
    timestamp: str = Field(..., description="Status timestamp")
    traits: Dict[str, int] = Field(..., description="Current traits")
    motivation_style: str = Field(..., description="Current motivation style")
    trust_level: float = Field(..., description="Current trust level")
    learning_agility: float = Field(..., description="Learning agility score")
    reflective_capacity: int = Field(..., description="Reflective capacity score")
    engagement: int = Field(..., description="Engagement score")
    stats: Dict[str, int] = Field(..., description="Statistics")
    llm_status: Dict[str, Any] = Field(..., description="LLM client status")


class AldenAPI:
    """
    FastAPI application for Alden persona interactions.
    
    Provides REST endpoints for:
    - Message exchange with Alden
    - Trait and memory management
    - Status and health monitoring
    - Memory export and audit
    """
    
    def __init__(self, alden_persona: AldenPersona, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Alden API.
        
        Args:
            alden_persona: Configured Alden persona instance
            logger: Optional logger instance
        """
        self.alden = alden_persona
        self.logger = logger or HearthlinkLogger()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Alden API",
            description="REST API for Alden persona interactions",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add exception handlers
        self.app.add_exception_handler(PersonaError, self._handle_persona_error)
        self.app.add_exception_handler(LLMError, self._handle_llm_error)
        self.app.add_exception_handler(Exception, self._handle_generic_error)
        
        # Register routes
        self._register_routes()
        
        self.logger.logger.info("Alden API initialized successfully", 
                              extra={"extra_fields": {"event_type": "alden_api_init"}})
    
    def _register_routes(self) -> None:
        """Register API routes."""
        
        @self.app.post("/api/v1/alden/message", response_model=MessageResponse)
        async def send_message(request: MessageRequest, http_request: Request):
            """Send a message to Alden and receive response."""
            try:
                session_id = request.session_id or str(uuid.uuid4())
                
                # Log API request
                self.logger.logger.info("API message request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_message_request",
                                          "session_id": session_id,
                                          "client_ip": http_request.client.host,
                                          "user_agent": http_request.headers.get("user-agent", "")
                                      }})
                
                # Generate Alden's response with metadata
                response_data = self.alden.generate_response(
                    user_message=request.message,
                    session_id=session_id,
                    context=request.context,
                    return_metadata=True
                )
                
                return MessageResponse(
                    response=response_data["content"],
                    session_id=response_data["session_id"],
                    timestamp=response_data["timestamp"],
                    model=response_data["model"],
                    response_time=response_data["response_time"],
                    usage=response_data["usage"]
                )
                
            except Exception as e:
                self.logger.log_error(e, "api_message_error", {
                    "session_id": request.session_id,
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.patch("/api/v1/alden/traits/{trait_name}")
        async def update_trait(trait_name: str, request: TraitUpdateRequest, http_request: Request):
            """Update one of Alden's personality traits."""
            try:
                # Log trait update request
                self.logger.logger.info("API trait update request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_trait_update",
                                          "trait": trait_name,
                                          "new_value": request.new_value,
                                          "reason": request.reason,
                                          "client_ip": http_request.client.host
                                      }})
                
                self.alden.update_trait(
                    trait_name=trait_name,
                    new_value=request.new_value,
                    reason=request.reason
                )
                
                return {"status": "success", "message": f"Trait {trait_name} updated successfully"}
                
            except Exception as e:
                self.logger.log_error(e, "api_trait_update_error", {
                    "trait": trait_name,
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/v1/alden/corrections")
        async def add_correction(request: CorrectionRequest, http_request: Request):
            """Add a correction event for Alden's learning."""
            try:
                # Log correction request
                self.logger.logger.info("API correction request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_correction_add",
                                          "correction_type": request.event_type,
                                          "impact_score": request.impact_score,
                                          "client_ip": http_request.client.host
                                      }})
                
                self.alden.add_correction_event(
                    event_type=request.event_type,
                    description=request.description,
                    impact_score=request.impact_score,
                    context=request.context
                )
                
                return {"status": "success", "message": "Correction event added successfully"}
                
            except Exception as e:
                self.logger.log_error(e, "api_correction_error", {
                    "correction_type": request.event_type,
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/v1/alden/mood")
        async def record_mood(request: MoodRequest, http_request: Request):
            """Record session mood for learning and adaptation."""
            try:
                # Log mood recording request
                self.logger.logger.info("API mood recording request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_mood_record",
                                          "session_id": request.session_id,
                                          "mood": request.mood,
                                          "score": request.score,
                                          "client_ip": http_request.client.host
                                      }})
                
                self.alden.record_session_mood(
                    session_id=request.session_id,
                    mood=request.mood,
                    score=request.score,
                    context=request.context
                )
                
                return {"status": "success", "message": "Session mood recorded successfully"}
                
            except Exception as e:
                self.logger.log_error(e, "api_mood_error", {
                    "session_id": request.session_id,
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/v1/alden/status", response_model=StatusResponse)
        async def get_status(http_request: Request):
            """Get Alden's current status and health information."""
            try:
                # Log status request
                self.logger.logger.info("API status request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_status_request",
                                          "client_ip": http_request.client.host
                                      }})
                
                status = self.alden.get_status()
                return StatusResponse(**status)
                
            except Exception as e:
                self.logger.log_error(e, "api_status_error", {
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/alden/memory/export")
        async def export_memory(http_request: Request):
            """Export Alden's memory for user review/audit."""
            try:
                # Log export request
                self.logger.logger.info("API memory export request", 
                                      extra={"extra_fields": {
                                          "event_type": "api_memory_export",
                                          "client_ip": http_request.client.host
                                      }})
                
                memory_data = self.alden.export_memory()
                return JSONResponse(content=memory_data)
                
            except Exception as e:
                self.logger.log_error(e, "api_memory_export_error", {
                    "client_ip": http_request.client.host
                })
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/alden/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "alden-api",
                "version": "1.0.0"
            }
    
    def _handle_persona_error(self, request: Request, exc: PersonaError) -> JSONResponse:
        """Handle persona-related errors."""
        self.logger.log_error(exc, "api_persona_error", {
            "client_ip": request.client.host,
            "path": request.url.path
        })
        return JSONResponse(
            status_code=400,
            content={"error": "Persona error", "detail": str(exc)}
        )
    
    def _handle_llm_error(self, request: Request, exc: LLMError) -> JSONResponse:
        """Handle LLM-related errors."""
        self.logger.log_error(exc, "api_llm_error", {
            "client_ip": request.client.host,
            "path": request.url.path
        })
        return JSONResponse(
            status_code=503,
            content={"error": "LLM service error", "detail": str(exc)}
        )
    
    def _handle_generic_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle generic errors."""
        self.logger.log_error(exc, "api_generic_error", {
            "client_ip": request.client.host,
            "path": request.url.path
        })
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, debug: bool = False) -> None:
        """
        Run the Alden API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        try:
            self.logger.logger.info("Starting Alden API server", 
                                  extra={"extra_fields": {
                                      "event_type": "alden_api_start",
                                      "host": host,
                                      "port": port,
                                      "debug": debug
                                  }})
            
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="debug" if debug else "info"
            )
            
        except Exception as e:
            self.logger.log_error(e, "alden_api_start_error")
            raise


def create_alden_api(llm_config: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> AldenAPI:
    """
    Factory function to create Alden API with persona.
    
    Args:
        llm_config: LLM configuration dictionary
        logger: Optional logger instance
        
    Returns:
        AldenAPI: Configured Alden API instance
        
    Raises:
        PersonaError: If API creation fails
    """
    try:
        alden_persona = create_alden_persona(llm_config, logger)
        return AldenAPI(alden_persona, logger)
    except Exception as e:
        raise PersonaError(f"Failed to create Alden API: {str(e)}") from e


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Alden API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--llm-engine", default="ollama", help="LLM engine (ollama, lmstudio, custom)")
    parser.add_argument("--llm-url", default="http://localhost:11434", help="LLM base URL")
    parser.add_argument("--llm-model", default="llama2", help="LLM model name")
    
    args = parser.parse_args()
    
    # Create LLM configuration
    llm_config = {
        "engine": args.llm_engine,
        "base_url": args.llm_url,
        "model": args.llm_model,
        "timeout": 30,
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    try:
        # Create and run API
        api = create_alden_api(llm_config)
        api.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        print(f"Failed to start Alden API: {e}")
        sys.exit(1) 