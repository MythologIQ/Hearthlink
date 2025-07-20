"""
Kimi K2 API Integration for Hearthlink

This module provides API endpoints for Kimi K2 LLM integration,
including request handling, response processing, and error management.
"""

import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime

from ..llm.KimiK2Backend import KimiK2Backend
from ..monitoring.TokenTracker import TokenTracker
from ..monitoring.MetricsCollector import MetricsCollector
from ..utils.errors import (
    APIError, SecurityError, RateLimitError, 
    ValidationError, TimeoutError, ErrorHandler
)
from ..synapse.security_manager import SecurityManager
from ..vault.vault import Vault

# Initialize router
router = APIRouter(prefix="/api/kimi-k2", tags=["kimi-k2"])

# Initialize components
kimi_k2_backend = None
token_tracker = TokenTracker("kimi-k2")
metrics_collector = MetricsCollector("kimi-k2")
security_manager = SecurityManager()
vault = Vault()

# Request/Response models
class KimiK2Request(BaseModel):
    prompt: str = Field(..., description="The prompt to send to Kimi K2")
    system_message: Optional[str] = Field(None, description="System message for the conversation")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(8192, ge=1, le=8192, description="Maximum tokens in response")
    agent_id: str = Field(..., description="ID of the requesting agent")
    module: str = Field(..., description="Module making the request")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the request")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tools available for the request")
    tool_choice: Optional[str] = Field("auto", description="Tool choice strategy")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")

class KimiK2Response(BaseModel):
    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    response_time: float = Field(..., description="Response time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    finish_reason: str = Field(..., description="Reason for completion")
    backend: str = Field(..., description="Backend used")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Health check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")

class StatsResponse(BaseModel):
    total_requests: int = Field(..., description="Total requests processed")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    average_response_time: float = Field(..., description="Average response time")
    total_tokens: int = Field(..., description="Total tokens processed")
    total_cost: float = Field(..., description="Total estimated cost")

# Initialize backend
async def get_kimi_k2_backend():
    global kimi_k2_backend
    if kimi_k2_backend is None:
        kimi_k2_backend = KimiK2Backend()
        await kimi_k2_backend.warmUp()
    return kimi_k2_backend

# Dependency for rate limiting
async def check_rate_limit(request: Request):
    client_ip = request.client.host
    agent_id = request.headers.get("X-Agent-ID", "unknown")
    
    # Implement rate limiting logic here
    # For now, we'll use a simple in-memory rate limiter
    
    return True  # Allow all requests for now

# Dependency for authentication
async def authenticate_request(request: Request):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    agent_id = request.headers.get("X-Agent-ID")
    
    if not agent_id:
        raise HTTPException(status_code=400, detail="X-Agent-ID header required")
    
    # Implement authentication logic here
    # For now, we'll allow all authenticated requests
    
    return {"agent_id": agent_id, "api_key": api_key}

@router.post("/chat", response_model=KimiK2Response)
async def chat(
    request: KimiK2Request,
    auth: Dict[str, str] = Depends(authenticate_request),
    rate_limit: bool = Depends(check_rate_limit)
):
    """
    Generate a chat response using Kimi K2
    """
    start_time = time.time()
    request_id = f"kimi-k2-{int(time.time() * 1000)}"
    
    try:
        # Get backend
        backend = await get_kimi_k2_backend()
        
        # Create LLM request
        llm_request = {
            "prompt": request.prompt,
            "systemMessage": request.system_message,
            "temperature": request.temperature,
            "maxTokens": request.max_tokens,
            "agentId": request.agent_id,
            "module": request.module,
            "context": request.context,
            "tools": request.tools,
            "toolChoice": request.tool_choice,
            "stream": request.stream
        }
        
        # Track request
        metrics_collector.increment("requests_total")
        metrics_collector.gauge("active_requests", 1)
        
        # Process request
        response = await backend.process(llm_request)
        
        # Track success
        metrics_collector.increment("requests_success")
        metrics_collector.histogram("response_time", (time.time() - start_time) * 1000)
        
        # Track tokens
        token_tracker.trackUsage(
            response.usage,
            {
                "agentId": request.agent_id,
                "module": request.module,
                "model": response.model,
                "requestId": request_id
            }
        )
        
        return KimiK2Response(
            content=response.content,
            model=response.model,
            usage=response.usage,
            response_time=response.responseTime,
            timestamp=response.timestamp,
            request_id=response.requestId,
            finish_reason=response.finishReason,
            backend=response.backend,
            tool_calls=response.toolCalls,
            metadata=response.metadata
        )
        
    except Exception as e:
        # Track error
        metrics_collector.increment("requests_failed")
        metrics_collector.increment("errors_total", {"error_type": type(e).__name__})
        
        # Handle error
        error = ErrorHandler.handle(e)
        
        # Log error
        error_data = {
            "request_id": request_id,
            "agent_id": request.agent_id,
            "module": request.module,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }
        
        await vault.logError(error_data)
        
        raise HTTPException(
            status_code=error.statusCode,
            detail={
                "error": error.message,
                "code": error.code,
                "request_id": request_id,
                "timestamp": error.timestamp
            }
        )
    
    finally:
        metrics_collector.gauge("active_requests", -1)

@router.post("/agentic", response_model=KimiK2Response)
async def agentic_workflow(
    request: KimiK2Request,
    auth: Dict[str, str] = Depends(authenticate_request),
    rate_limit: bool = Depends(check_rate_limit)
):
    """
    Execute an agentic workflow using Kimi K2
    """
    try:
        backend = await get_kimi_k2_backend()
        
        # Create agentic workflow request
        workflow_request = {
            "prompt": request.prompt,
            "systemMessage": request.system_message or "You are an advanced AI agent capable of autonomous task execution.",
            "agentId": request.agent_id,
            "module": request.module,
            "tools": request.tools,
            "maxTokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # Execute workflow
        response = await backend.executeAgenticWorkflow(workflow_request)
        
        return KimiK2Response(
            content=response.content,
            model=response.model,
            usage=response.usage,
            response_time=response.responseTime,
            timestamp=response.timestamp,
            request_id=response.requestId,
            finish_reason=response.finishReason,
            backend=response.backend,
            tool_calls=response.toolCalls,
            metadata=response.metadata
        )
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/long-context", response_model=KimiK2Response)
async def long_context_processing(
    request: KimiK2Request,
    documents: List[str] = Field(..., description="Documents to process"),
    auth: Dict[str, str] = Depends(authenticate_request),
    rate_limit: bool = Depends(check_rate_limit)
):
    """
    Process long context documents using Kimi K2
    """
    try:
        backend = await get_kimi_k2_backend()
        
        # Create long context request
        long_context_request = {
            "prompt": request.prompt,
            "systemMessage": request.system_message,
            "agentId": request.agent_id,
            "module": request.module,
            "context": request.context,
            "documents": documents,
            "maxTokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # Process long context
        response = await backend.processWithLongContext(long_context_request)
        
        return KimiK2Response(
            content=response.content,
            model=response.model,
            usage=response.usage,
            response_time=response.responseTime,
            timestamp=response.timestamp,
            request_id=response.requestId,
            finish_reason=response.finishReason,
            backend=response.backend,
            tool_calls=response.toolCalls,
            metadata=response.metadata
        )
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the Kimi K2 service
    """
    try:
        backend = await get_kimi_k2_backend()
        health = await backend.healthCheck()
        
        return HealthResponse(
            status=health["status"],
            timestamp=datetime.now().isoformat(),
            details=health.get("details")
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            details={"error": str(e)}
        )

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    auth: Dict[str, str] = Depends(authenticate_request)
):
    """
    Get usage statistics for Kimi K2
    """
    try:
        backend = await get_kimi_k2_backend()
        usage_stats = await backend.getUsageStats()
        
        return StatsResponse(
            total_requests=usage_stats["totalRequests"],
            successful_requests=usage_stats["successfulRequests"],
            failed_requests=usage_stats["failedRequests"],
            average_response_time=usage_stats["averageResponseTime"],
            total_tokens=usage_stats["totalTokensPrompt"] + usage_stats["totalTokensCompletion"],
            total_cost=0.0  # Calculate based on pricing
        )
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/capabilities")
async def get_capabilities():
    """
    Get the capabilities of the Kimi K2 backend
    """
    try:
        backend = await get_kimi_k2_backend()
        capabilities = await backend.getCapabilities()
        model_info = await backend.getModelInfo()
        
        return {
            "capabilities": capabilities,
            "model_info": model_info,
            "features": [
                "128K context window",
                "Native tool calling",
                "Agentic workflows",
                "Code generation",
                "Long context processing",
                "Reasoning and analysis"
            ]
        }
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.post("/estimate-cost")
async def estimate_cost(
    request: KimiK2Request,
    auth: Dict[str, str] = Depends(authenticate_request)
):
    """
    Estimate the cost of a request
    """
    try:
        backend = await get_kimi_k2_backend()
        
        # Create minimal request for cost estimation
        cost_request = {
            "prompt": request.prompt,
            "maxTokens": request.max_tokens,
            "agentId": request.agent_id,
            "module": request.module
        }
        
        estimated_cost = await backend.estimateCost(cost_request)
        
        return {
            "estimated_cost": estimated_cost,
            "currency": "USD",
            "breakdown": {
                "input_tokens": len(request.prompt.split()) * 1.33,  # Rough estimate
                "output_tokens": request.max_tokens,
                "input_cost": len(request.prompt.split()) * 1.33 * 0.00057 / 1000,
                "output_cost": request.max_tokens * 0.0023 / 1000
            }
        }
        
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

@router.get("/metrics")
async def get_metrics(
    format: str = "json",
    auth: Dict[str, str] = Depends(authenticate_request)
):
    """
    Get metrics in JSON or Prometheus format
    """
    try:
        if format == "prometheus":
            metrics_data = metrics_collector.exportPrometheusFormat()
            return Response(content=metrics_data, media_type="text/plain")
        else:
            metrics_data = metrics_collector.exportJSON()
            return JSONResponse(content=metrics_data)
            
    except Exception as e:
        error = ErrorHandler.handle(e)
        raise HTTPException(status_code=error.statusCode, detail=error.message)

# Startup event
@router.on_event("startup")
async def startup_event():
    """
    Initialize the Kimi K2 service on startup
    """
    try:
        await get_kimi_k2_backend()
        print("Kimi K2 API service started successfully")
    except Exception as e:
        print(f"Failed to start Kimi K2 API service: {e}")

# Shutdown event
@router.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown
    """
    global kimi_k2_backend
    if kimi_k2_backend:
        await kimi_k2_backend.shutdown()
        print("Kimi K2 API service shut down successfully")