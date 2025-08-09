"""
Enhanced Core API with Kimi K2 Integration

This module provides API endpoints for the enhanced Core system,
including agentic workflow management and intelligent agent delegation.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.enhanced_core import EnhancedCore
from ..core.kimi_k2_orchestration import WorkflowStatus, AgentCapabilityType
from ..utils.errors import CoreError, ErrorHandler
from ..vault.vault import Vault

# Initialize router
router = APIRouter(prefix="/api/enhanced-core", tags=["enhanced-core"])

# Enhanced Core instance (will be initialized on startup)
enhanced_core = None

# Request/Response models
class AgenticTaskRequest(BaseModel):
    task_description: str = Field(..., description="Description of the task to execute")
    agent_id: str = Field(default="kimi-k2", description="Agent to execute the task")
    tools: Optional[List[str]] = Field(None, description="Available tools for the task")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class AgenticTaskResponse(BaseModel):
    workflow_id: Optional[str] = Field(None, description="Workflow ID if created")
    result: Dict[str, Any] = Field(..., description="Task execution result")
    agent_id: str = Field(..., description="Agent that executed the task")
    task_description: str = Field(..., description="Original task description")
    execution_time: float = Field(..., description="Execution time in seconds")
    tokens_used: int = Field(..., description="Tokens used for the task")
    cost_estimate: float = Field(..., description="Estimated cost")

class TaskDelegationRequest(BaseModel):
    task_description: str = Field(..., description="Task to be delegated")
    task_type: str = Field(default="general", description="Type of task")
    
class TaskDelegationResponse(BaseModel):
    selected_agent: str = Field(..., description="Agent selected for the task")
    delegation_reason: str = Field(..., description="Reason for agent selection")
    result: Dict[str, Any] = Field(..., description="Task execution result")

class AgenticSessionRequest(BaseModel):
    topic: str = Field(..., description="Session topic")
    primary_agent: str = Field(default="kimi-k2", description="Primary agent for the session")
    tools: Optional[List[str]] = Field(None, description="Available tools")

class WorkflowControlRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID to control")
    action: str = Field(..., description="Action to perform (pause, resume, cancel)")

class AgentCapabilitiesResponse(BaseModel):
    agents: Dict[str, Dict[str, Any]] = Field(..., description="Agent capabilities summary")

class WorkflowStatusResponse(BaseModel):
    total_workflows: int = Field(..., description="Total number of workflows")
    active: int = Field(..., description="Active workflows")
    completed: int = Field(..., description="Completed workflows")
    failed: int = Field(..., description="Failed workflows")
    by_agent: Dict[str, Dict[str, int]] = Field(..., description="Statistics by agent")

# Dependencies
async def get_enhanced_core():
    """Get the enhanced core instance."""
    global enhanced_core
    if enhanced_core is None:
        raise HTTPException(status_code=500, detail="Enhanced Core not initialized")
    return enhanced_core

async def authenticate_request(request: Request):
    """Authenticate the request."""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")
    return user_id

# Endpoints
@router.post("/session/agentic", response_model=Dict[str, str])
async def create_agentic_session(
    request: AgenticSessionRequest,
    user_id: str = Depends(authenticate_request),
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Create a new agentic session optimized for complex workflows.
    """
    try:
        session_id = await core.create_agentic_session(
            user_id=user_id,
            topic=request.topic,
            primary_agent=request.primary_agent,
            tools=request.tools
        )
        
        return {"session_id": session_id}
        
    except CoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/task/agentic", response_model=AgenticTaskResponse)
async def execute_agentic_task(
    session_id: str,
    request: AgenticTaskRequest,
    user_id: str = Depends(authenticate_request),
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Execute an agentic task within a session.
    """
    try:
        result = await core.execute_agentic_task(
            session_id=session_id,
            user_id=user_id,
            task_description=request.task_description,
            agent_id=request.agent_id,
            tools=request.tools
        )
        
        return AgenticTaskResponse(
            workflow_id=result.get("workflow_id"),
            result=result["result"],
            agent_id=result["agent_id"],
            task_description=result["task_description"],
            execution_time=result["result"].get("execution_time", 0),
            tokens_used=result["result"].get("tokens_used", 0),
            cost_estimate=result["result"].get("cost_estimate", 0.0)
        )
        
    except CoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/task/delegate", response_model=TaskDelegationResponse)
async def delegate_task(
    session_id: str,
    request: TaskDelegationRequest,
    user_id: str = Depends(authenticate_request),
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Delegate a task to the optimal agent based on capabilities.
    """
    try:
        result = await core.delegate_to_optimal_agent(
            session_id=session_id,
            user_id=user_id,
            task_description=request.task_description,
            task_type=request.task_type
        )
        
        return TaskDelegationResponse(
            selected_agent=result["agent_id"],
            delegation_reason=f"Selected for {request.task_type} task",
            result=result["result"]
        )
        
    except CoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/agents/capabilities", response_model=AgentCapabilitiesResponse)
async def get_agent_capabilities(
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Get capabilities summary for all available agents.
    """
    try:
        capabilities = core.get_agent_capabilities_summary()
        return AgentCapabilitiesResponse(agents=capabilities)
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/workflows/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Get workflow execution status and statistics.
    """
    try:
        status = core.get_workflow_status_summary()
        
        if "error" in status:
            raise HTTPException(status_code=503, detail=status["error"])
        
        return WorkflowStatusResponse(
            total_workflows=status["total_workflows"],
            active=status["active"],
            completed=status["completed"],
            failed=status["failed"],
            by_agent=status["by_agent"]
        )
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/workflow/control")
async def control_workflow(
    request: WorkflowControlRequest,
    user_id: str = Depends(authenticate_request),
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Control workflow execution (pause, resume, cancel).
    """
    try:
        if not core.kimi_k2_orchestrator:
            raise HTTPException(status_code=503, detail="Kimi K2 orchestrator not available")
        
        if request.action == "pause":
            await core.kimi_k2_orchestrator.pause_workflow(request.workflow_id)
        elif request.action == "resume":
            await core.kimi_k2_orchestrator.resume_workflow(request.workflow_id)
        elif request.action == "cancel":
            await core.kimi_k2_orchestrator.cancel_workflow(request.workflow_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {"message": f"Workflow {request.workflow_id} {request.action}d successfully"}
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/session/{session_id}/enhanced")
async def get_enhanced_session_info(
    session_id: str,
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Get enhanced session information including agentic capabilities.
    """
    try:
        session_info = core.get_enhanced_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_info
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/session/{session_id}/workflows")
async def get_session_workflows(
    session_id: str,
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Get active workflows for a specific session.
    """
    try:
        if not core.kimi_k2_orchestrator:
            raise HTTPException(status_code=503, detail="Kimi K2 orchestrator not available")
        
        workflows = core.kimi_k2_orchestrator.get_active_workflows(session_id)
        
        return {
            "session_id": session_id,
            "active_workflows": len(workflows),
            "workflows": [
                {
                    "workflow_id": w.workflow_id,
                    "agent_id": w.agent_id,
                    "status": w.status.value,
                    "task_description": w.task_description,
                    "created_at": w.created_at,
                    "current_step": w.current_step,
                    "total_steps": len(w.steps),
                    "tools_used": w.tools_used
                }
                for w in workflows
            ]
        }
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/agents/{agent_id}/delegations")
async def get_agent_delegations(
    agent_id: str,
    limit: int = 10,
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Get recent delegations for a specific agent.
    """
    try:
        delegations = core.agent_delegations.get(agent_id, [])
        
        # Sort by timestamp and limit
        recent_delegations = sorted(
            delegations,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
        
        return {
            "agent_id": agent_id,
            "total_delegations": len(delegations),
            "recent_delegations": recent_delegations
        }
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/agents/suggest")
async def suggest_agent(
    task_description: str,
    task_type: str = "general",
    core: EnhancedCore = Depends(get_enhanced_core)
):
    """
    Suggest the optimal agent for a task.
    """
    try:
        optimal_agent = core._select_optimal_agent(task_type, task_description)
        
        if not optimal_agent:
            raise HTTPException(status_code=404, detail="No suitable agent found")
        
        agent_info = core.agent_registry[optimal_agent]
        reason = core._get_delegation_reason(optimal_agent, task_type)
        
        return {
            "suggested_agent": optimal_agent,
            "agent_name": agent_info["name"],
            "agent_role": agent_info["role"],
            "reason": reason,
            "capabilities": [cap.value for cap in agent_info["capabilities"]],
            "specializations": agent_info["specializations"]
        }
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/health")
async def health_check():
    """
    Health check for the enhanced core system.
    """
    try:
        global enhanced_core
        
        if enhanced_core is None:
            return {"status": "unhealthy", "reason": "Enhanced Core not initialized"}
        
        # Check Kimi K2 orchestrator
        kimi_k2_available = enhanced_core.kimi_k2_orchestrator is not None
        
        # Check LLM backend manager
        llm_backends = enhanced_core.llm_backend_manager.getAvailableBackends() if enhanced_core.llm_backend_manager else []
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "enhanced_core": True,
                "kimi_k2_orchestrator": kimi_k2_available,
                "llm_backend_manager": bool(enhanced_core.llm_backend_manager),
                "available_backends": llm_backends,
                "registered_agents": list(enhanced_core.agent_registry.keys())
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Startup event
@router.on_event("startup")
async def startup_event():
    """
    Initialize the enhanced core system on startup.
    """
    global enhanced_core
    
    try:
        # Load configuration
        config = {
            "session": {
                "max_participants": 10,
                "max_breakouts_per_session": 5,
                "session_timeout_minutes": 480
            },
            "llm_backends": {
                # This would be loaded from configuration files
            }
        }
        
        # Initialize vault
        vault = Vault()
        
        # Initialize enhanced core
        enhanced_core = EnhancedCore(config, vault)
        
        print("Enhanced Core API service started successfully")
        
    except Exception as e:
        print(f"Failed to start Enhanced Core API service: {e}")

# Shutdown event
@router.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown.
    """
    global enhanced_core
    
    if enhanced_core and enhanced_core.kimi_k2_orchestrator:
        # Clean up old workflows
        enhanced_core.kimi_k2_orchestrator.cleanup_old_workflows()
        
    print("Enhanced Core API service shut down successfully")