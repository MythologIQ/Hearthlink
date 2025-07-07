#!/usr/bin/env python3
"""
Mimic Persona API - FastAPI endpoints for Mimic persona ecosystem

Provides RESTful API endpoints for:
- Dynamic persona generation
- Performance analytics and tracking
- Persona forking and merging
- Plugin extension management
- Knowledge indexing and retrieval

References:
- hearthlink_system_documentation_master.md: API contract specifications
- PLATINUM_BLOCKERS.md: Security and compliance requirements

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from pydantic.types import UUID4

from personas.mimic import (
    MimicPersona, MimicError, PersonaGenerationError, PerformanceAnalyticsError,
    PersonaForkError, KnowledgeIndexError, PluginExtensionError,
    CoreTraits, PerformanceTier, PersonaStatus
)
from main import HearthlinkLogger

# Initialize FastAPI app
app = FastAPI(
    title="Mimic Persona API",
    description="Dynamic persona generation and management API for Hearthlink",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Global instances
mimic_personas: Dict[str, MimicPersona] = {}
logger = HearthlinkLogger()

# Pydantic models for API requests/responses

class CoreTraitsRequest(BaseModel):
    """Core traits request model."""
    focus: int = Field(50, ge=0, le=100, description="Concentration and task focus")
    creativity: int = Field(50, ge=0, le=100, description="Creative problem solving")
    precision: int = Field(50, ge=0, le=100, description="Attention to detail")
    humor: int = Field(25, ge=0, le=100, description="Humor and levity")
    empathy: int = Field(50, ge=0, le=100, description="Emotional intelligence")
    assertiveness: int = Field(50, ge=0, le=100, description="Confidence and directness")
    adaptability: int = Field(50, ge=0, le=100, description="Flexibility and learning speed")
    collaboration: int = Field(50, ge=0, le=100, description="Teamwork and cooperation")

class PersonaGenerationRequest(BaseModel):
    """Persona generation request model."""
    role: str = Field(..., description="The role/purpose of the persona")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context and requirements")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional user preferences")
    base_traits: Optional[CoreTraitsRequest] = Field(None, description="Optional base trait values")
    persona_name: Optional[str] = Field(None, description="Optional custom persona name")
    description: Optional[str] = Field(None, description="Optional custom description")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")

class PerformanceRecordRequest(BaseModel):
    """Performance record request model."""
    session_id: str = Field(..., description="Unique session identifier")
    task: str = Field(..., description="Task description")
    score: int = Field(..., ge=0, le=100, description="Performance score (0-100)")
    user_feedback: str = Field(..., description="User feedback text")
    success: bool = Field(..., description="Whether task was successful")
    duration: float = Field(..., ge=0, description="Task duration in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context information")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Optional performance metrics")

class PersonaForkRequest(BaseModel):
    """Persona fork request model."""
    source_persona_id: str = Field(..., description="ID of source persona to fork")
    new_role: str = Field(..., description="New role for forked persona")
    modifications: Dict[str, Any] = Field(default_factory=dict, description="Modifications to apply")
    name: Optional[str] = Field(None, description="Name for forked persona")
    description: Optional[str] = Field(None, description="Description for forked persona")
    tags: List[str] = Field(default_factory=list, description="Tags for forked persona")

class PersonaMergeRequest(BaseModel):
    """Persona merge request model."""
    primary_persona_id: str = Field(..., description="ID of primary persona (base)")
    secondary_persona_id: str = Field(..., description="ID of secondary persona (to be merged)")
    merge_strategy: str = Field("selective", description="Strategy for merging")
    name: Optional[str] = Field(None, description="Name for merged persona")
    description: Optional[str] = Field(None, description="Description for merged persona")

class PluginExtensionRequest(BaseModel):
    """Plugin extension request model."""
    plugin_id: str = Field(..., description="Unique plugin identifier")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    performance_impact: float = Field(0.0, ge=-1.0, le=1.0, description="Impact on performance")

class KnowledgeIndexRequest(BaseModel):
    """Knowledge indexing request model."""
    content: str = Field(..., description="Content to index")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    relevance_score: float = Field(0.5, ge=0.0, le=1.0, description="Initial relevance score")

class PersonaResponse(BaseModel):
    """Persona response model."""
    persona_id: str
    persona_name: str
    role: str
    description: str
    status: str
    performance_tier: str
    sessions_completed: int
    average_score: float
    active_plugins: int
    knowledge_items: int
    created_at: str
    last_updated: str

class PerformanceAnalyticsResponse(BaseModel):
    """Performance analytics response model."""
    persona_id: str
    persona_name: str
    role: str
    status: str
    growth_stats: Dict[str, Any]
    total_sessions: int
    average_score: float
    success_rate: float
    performance_trend: List[int]
    top_topics: List[Dict[str, Any]]
    knowledge_coverage: float
    active_plugins: int
    plugin_performance_impact: float
    recommendations: List[str]
    growth_opportunities: List[str]

class PluginExtensionResponse(BaseModel):
    """Plugin extension response model."""
    plugin_id: str
    name: str
    version: str
    enabled: bool
    permissions: List[str]
    performance_impact: float
    last_used: Optional[str]
    usage_count: int

class KnowledgeSummaryResponse(BaseModel):
    """Knowledge summary response model."""
    doc_id: str
    summary: str
    relevance_score: float
    tags: List[str]
    created_at: str
    last_accessed: Optional[str]
    access_count: int

# Dependency functions

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from authentication token."""
    # In a real implementation, this would validate the JWT token
    # For now, we'll use a simple user ID extraction
    try:
        # Extract user ID from token (simplified)
        user_id = credentials.credentials.split(":")[0] if ":" in credentials.credentials else "default_user"
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def get_mimic_persona(persona_id: str) -> MimicPersona:
    """Get Mimic persona instance by ID."""
    if persona_id not in mimic_personas:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return mimic_personas[persona_id]

# API Endpoints

@app.post("/api/mimic/persona/generate", response_model=Dict[str, str])
async def generate_persona(
    request: PersonaGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a new dynamic persona based on task context.
    
    Args:
        request: Persona generation parameters
        current_user: Current authenticated user
        
    Returns:
        Dict containing generated persona ID
    """
    try:
        # Create LLM config (simplified)
        llm_config = {
            "endpoint": "http://localhost:8000",
            "model": "default",
            "timeout": 30
        }
        
        # Create Mimic persona instance
        mimic_persona = MimicPersona(None, logger)  # Simplified for API
        
        # Generate persona
        persona_id = mimic_persona.generate_persona(
            role=request.role,
            context=request.context,
            user_preferences=request.user_preferences,
            base_traits=asdict(request.base_traits) if request.base_traits else None
        )
        
        # Store persona instance
        mimic_personas[persona_id] = mimic_persona
        
        logger.logger.info(f"Generated persona {persona_id} for user {current_user}")
        
        return {"persona_id": persona_id, "status": "created"}
        
    except PersonaGenerationError as e:
        logger.logger.error(f"Persona generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in persona generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/{persona_id}/performance")
async def record_performance(
    persona_id: str,
    request: PerformanceRecordRequest,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Record performance for a persona session/task.
    
    Args:
        persona_id: Persona identifier
        request: Performance record data
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Success confirmation
    """
    try:
        mimic_persona.record_performance(
            session_id=request.session_id,
            task=request.task,
            score=request.score,
            user_feedback=request.user_feedback,
            success=request.success,
            duration=request.duration,
            context=request.context
        )
        
        logger.logger.info(f"Recorded performance for persona {persona_id}, session {request.session_id}")
        
        return {"status": "success", "message": "Performance recorded successfully"}
        
    except PerformanceAnalyticsError as e:
        logger.logger.error(f"Performance recording failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in performance recording: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/persona/{persona_id}/analytics", response_model=PerformanceAnalyticsResponse)
async def get_performance_analytics(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Get comprehensive performance analytics for a persona.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Performance analytics data
    """
    try:
        analytics = mimic_persona.get_performance_analytics()
        
        return PerformanceAnalyticsResponse(**analytics)
        
    except PerformanceAnalyticsError as e:
        logger.logger.error(f"Analytics generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in analytics generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/fork", response_model=Dict[str, str])
async def fork_persona(
    request: PersonaForkRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Fork an existing persona with modifications.
    
    Args:
        request: Fork request parameters
        current_user: Current authenticated user
        
    Returns:
        Dict containing new forked persona ID
    """
    try:
        # Get source persona
        source_persona = get_mimic_persona(request.source_persona_id)
        
        # Prepare modifications
        modifications = request.modifications.copy()
        if request.name:
            modifications["name"] = request.name
        if request.description:
            modifications["description"] = request.description
        if request.tags:
            modifications["tags"] = request.tags
        
        # Fork persona
        forked_persona_id = source_persona.fork_persona(
            source_persona_id=request.source_persona_id,
            new_role=request.new_role,
            modifications=modifications
        )
        
        # Create new persona instance (simplified)
        forked_persona = MimicPersona(None, logger)
        mimic_personas[forked_persona_id] = forked_persona
        
        logger.logger.info(f"Forked persona {request.source_persona_id} to {forked_persona_id}")
        
        return {"forked_persona_id": forked_persona_id, "status": "forked"}
        
    except PersonaForkError as e:
        logger.logger.error(f"Persona forking failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in persona forking: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/merge", response_model=Dict[str, str])
async def merge_personas(
    request: PersonaMergeRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Merge two personas using specified strategy.
    
    Args:
        request: Merge request parameters
        current_user: Current authenticated user
        
    Returns:
        Dict containing merged persona ID
    """
    try:
        # Get primary persona
        primary_persona = get_mimic_persona(request.primary_persona_id)
        
        # Merge personas
        merged_persona_id = primary_persona.merge_personas(
            primary_persona_id=request.primary_persona_id,
            secondary_persona_id=request.secondary_persona_id,
            merge_strategy=request.merge_strategy
        )
        
        # Create merged persona instance (simplified)
        merged_persona = MimicPersona(None, logger)
        mimic_personas[merged_persona_id] = merged_persona
        
        logger.logger.info(f"Merged personas {request.primary_persona_id} + {request.secondary_persona_id} -> {merged_persona_id}")
        
        return {"merged_persona_id": merged_persona_id, "status": "merged"}
        
    except PersonaForkError as e:
        logger.logger.error(f"Persona merging failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in persona merging: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/{persona_id}/plugin")
async def add_plugin_extension(
    persona_id: str,
    request: PluginExtensionRequest,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Add plugin extension to persona capabilities.
    
    Args:
        persona_id: Persona identifier
        request: Plugin extension data
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Success confirmation
    """
    try:
        mimic_persona.add_plugin_extension(
            plugin_id=request.plugin_id,
            name=request.name,
            version=request.version,
            permissions=request.permissions,
            performance_impact=request.performance_impact
        )
        
        logger.logger.info(f"Added plugin {request.name} to persona {persona_id}")
        
        return {"status": "success", "message": "Plugin extension added successfully"}
        
    except PluginExtensionError as e:
        logger.logger.error(f"Plugin addition failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in plugin addition: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/persona/{persona_id}/plugins", response_model=List[PluginExtensionResponse])
async def get_plugin_extensions(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Get plugin extensions for a persona.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        List of plugin extensions
    """
    try:
        plugins = mimic_persona.memory.plugin_extensions
        return [PluginExtensionResponse(**asdict(plugin)) for plugin in plugins]
        
    except Exception as e:
        logger.logger.error(f"Failed to get plugin extensions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/{persona_id}/knowledge")
async def add_knowledge(
    persona_id: str,
    request: KnowledgeIndexRequest,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Add knowledge to persona's custom knowledge base.
    
    Args:
        persona_id: Persona identifier
        request: Knowledge data
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Success confirmation
    """
    try:
        from personas.mimic import KnowledgeSummary
        
        knowledge = KnowledgeSummary(
            doc_id=f"doc-{uuid.uuid4().hex[:8]}",
            summary=request.content,
            relevance_score=request.relevance_score,
            tags=request.tags,
            created_at=datetime.now().isoformat()
        )
        
        mimic_persona.memory.custom_knowledge.append(knowledge)
        
        logger.logger.info(f"Added knowledge to persona {persona_id}")
        
        return {"status": "success", "message": "Knowledge added successfully"}
        
    except Exception as e:
        logger.logger.error(f"Failed to add knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/persona/{persona_id}/knowledge", response_model=List[KnowledgeSummaryResponse])
async def get_knowledge(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Get persona's custom knowledge base.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        List of knowledge summaries
    """
    try:
        knowledge = mimic_persona.memory.custom_knowledge
        return [KnowledgeSummaryResponse(**asdict(k)) for k in knowledge]
        
    except Exception as e:
        logger.logger.error(f"Failed to get knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/persona/{persona_id}/status", response_model=PersonaResponse)
async def get_persona_status(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Get current persona status.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Persona status information
    """
    try:
        status = mimic_persona.get_status()
        return PersonaResponse(**status)
        
    except Exception as e:
        logger.logger.error(f"Failed to get persona status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/persona/{persona_id}/tier")
async def get_performance_tier(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Get current performance tier for persona.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Performance tier information
    """
    try:
        tier = mimic_persona.get_performance_tier()
        return {"persona_id": persona_id, "performance_tier": tier.value}
        
    except Exception as e:
        logger.logger.error(f"Failed to get performance tier: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/{persona_id}/export")
async def export_persona_memory(
    persona_id: str,
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Export complete persona memory for backup/transfer.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Exported memory data
    """
    try:
        export_data = mimic_persona.export_memory()
        return export_data
        
    except Exception as e:
        logger.logger.error(f"Failed to export persona memory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/mimic/persona/{persona_id}/import")
async def import_persona_memory(
    persona_id: str,
    import_data: Dict[str, Any],
    current_user: str = Depends(get_current_user),
    mimic_persona: MimicPersona = Depends(get_mimic_persona)
):
    """
    Import persona memory from backup/transfer.
    
    Args:
        persona_id: Persona identifier
        import_data: Memory data to import
        current_user: Current authenticated user
        mimic_persona: Mimic persona instance
        
    Returns:
        Success confirmation
    """
    try:
        mimic_persona.import_memory(import_data)
        return {"status": "success", "message": "Memory imported successfully"}
        
    except Exception as e:
        logger.logger.error(f"Failed to import persona memory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/mimic/personas", response_model=List[PersonaResponse])
async def list_personas(
    current_user: str = Depends(get_current_user)
):
    """
    List all personas for current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of persona status information
    """
    try:
        personas = []
        for persona_id, mimic_persona in mimic_personas.items():
            try:
                status = mimic_persona.get_status()
                personas.append(PersonaResponse(**status))
            except Exception as e:
                logger.logger.warning(f"Failed to get status for persona {persona_id}: {str(e)}")
                continue
        
        return personas
        
    except Exception as e:
        logger.logger.error(f"Failed to list personas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/mimic/persona/{persona_id}")
async def delete_persona(
    persona_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a persona.
    
    Args:
        persona_id: Persona identifier
        current_user: Current authenticated user
        
    Returns:
        Success confirmation
    """
    try:
        if persona_id not in mimic_personas:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        del mimic_personas[persona_id]
        
        logger.logger.info(f"Deleted persona {persona_id}")
        
        return {"status": "success", "message": "Persona deleted successfully"}
        
    except Exception as e:
        logger.logger.error(f"Failed to delete persona: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@app.get("/api/mimic/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_personas": len(mimic_personas),
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(MimicError)
async def mimic_error_handler(request, exc):
    """Handle Mimic-specific errors."""
    logger.logger.error(f"Mimic error: {str(exc)}")
    return {"error": str(exc), "type": "mimic_error"}

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    """Handle HTTP errors."""
    logger.logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 