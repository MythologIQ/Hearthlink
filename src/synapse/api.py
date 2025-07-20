"""
Synapse API Endpoints

FastAPI endpoints for plugin registration, execution, and management.
Provides RESTful API for Synapse plugin gateway functionality.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json

from .synapse import Synapse, SynapseConfig, ConnectionRequest, ConnectionResult
from .manifest import PluginManifest, RiskTier
from .permissions import PermissionRequest
from .plugin_manager import PluginExecutionResult, PluginStatus

# Pydantic models for API requests/responses

class PluginManifestRequest(BaseModel):
    """Plugin manifest registration request."""
    plugin_id: str = Field(..., description="Unique plugin identifier")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    manifest_version: str = Field(default="1.0.0", description="Manifest version")
    requested_permissions: List[str] = Field(default=[], description="Requested permissions")
    sandbox: bool = Field(default=True, description="Require sandbox execution")
    risk_tier: str = Field(default="moderate", description="Risk tier")

class PluginExecutionRequest(BaseModel):
    """Plugin execution request."""
    payload: Dict[str, Any] = Field(..., description="Execution payload")
    session_id: Optional[str] = Field(None, description="Session ID")
    timeout: Optional[int] = Field(None, description="Execution timeout")

class PluginApprovalRequest(BaseModel):
    """Plugin approval request."""
    reason: Optional[str] = Field(None, description="Approval reason")

class PluginRevocationRequest(BaseModel):
    """Plugin revocation request."""
    reason: str = Field(..., description="Revocation reason")

class PermissionApprovalRequest(BaseModel):
    """Permission approval request."""
    reason: Optional[str] = Field(None, description="Approval reason")

class PermissionDenialRequest(BaseModel):
    """Permission denial request."""
    reason: str = Field(..., description="Denial reason")

class ConnectionRequestModel(BaseModel):
    """Connection request."""
    agent_id: str = Field(..., description="External agent ID")
    intent: str = Field(..., description="Connection intent")
    permissions: List[str] = Field(..., description="Required permissions")

class BenchmarkRequest(BaseModel):
    """Benchmark request."""
    test_params: Optional[Dict[str, Any]] = Field(None, description="Test parameters")

class TrafficLogFilter(BaseModel):
    """Traffic log filter."""
    plugin_id: Optional[str] = Field(None, description="Filter by plugin ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    session_id: Optional[str] = Field(None, description="Filter by session ID")
    traffic_type: Optional[str] = Field(None, description="Filter by traffic type")
    start_time: Optional[str] = Field(None, description="Filter by start time")
    end_time: Optional[str] = Field(None, description="Filter by end time")
    limit: Optional[int] = Field(None, description="Limit results")

class APIResponse(BaseModel):
    """Standard API response."""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

# API setup

app = FastAPI(
    title="Synapse Plugin Gateway API",
    description="Secure external gateway for plugin management and execution",
    version="1.0.0"
)

security = HTTPBearer()

# Global Synapse instance
synapse: Optional[Synapse] = None
logger: Optional[logging.Logger] = None

def get_synapse() -> Synapse:
    """Get Synapse instance."""
    if synapse is None:
        raise HTTPException(status_code=500, detail="Synapse not initialized")
    return synapse

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from JWT token."""
    # This is a simplified implementation
    # In a real system, you'd validate the JWT token and extract user info
    token = credentials.credentials
    # For now, assume the token contains the user ID
    return token

def initialize_synapse(config: Optional[SynapseConfig] = None):
    """Initialize Synapse instance."""
    global synapse, logger
    logger = logging.getLogger(__name__)
    synapse = Synapse(config, logger)
    logger.info("Synapse API initialized")

# Plugin Management Endpoints

@app.post("/api/synapse/plugin/register", response_model=APIResponse)
async def register_plugin(
    manifest: PluginManifestRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Register a new plugin."""
    try:
        manifest_data = manifest.dict()
        plugin_id = synapse_instance.register_plugin(manifest_data, current_user)
        
        return APIResponse(
            status="success",
            message="Plugin registered successfully",
            data={"plugin_id": plugin_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Plugin registration failed: {e}")
        raise HTTPException(status_code=500, detail="Plugin registration failed")

@app.post("/api/synapse/plugin/{plugin_id}/approve", response_model=APIResponse)
async def approve_plugin(
    plugin_id: str,
    approval: PluginApprovalRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Approve a plugin for execution."""
    try:
        success = synapse_instance.approve_plugin(plugin_id, current_user, approval.reason)
        
        if success:
            return APIResponse(
                status="success",
                message="Plugin approved successfully",
                data={"plugin_id": plugin_id}
            )
        else:
            raise HTTPException(status_code=400, detail="Plugin approval failed")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Plugin approval failed: {e}")
        raise HTTPException(status_code=500, detail="Plugin approval failed")

@app.post("/api/synapse/plugin/{plugin_id}/revoke", response_model=APIResponse)
async def revoke_plugin(
    plugin_id: str,
    revocation: PluginRevocationRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Revoke a plugin."""
    try:
        success = synapse_instance.revoke_plugin(plugin_id, current_user, revocation.reason)
        
        if success:
            return APIResponse(
                status="success",
                message="Plugin revoked successfully",
                data={"plugin_id": plugin_id}
            )
        else:
            raise HTTPException(status_code=400, detail="Plugin revocation failed")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Plugin revocation failed: {e}")
        raise HTTPException(status_code=500, detail="Plugin revocation failed")

@app.post("/api/synapse/plugin/{plugin_id}/execute", response_model=APIResponse)
async def execute_plugin(
    plugin_id: str,
    execution: PluginExecutionRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Execute a plugin."""
    try:
        result = synapse_instance.execute_plugin(
            plugin_id, current_user, execution.payload,
            execution.session_id, execution.timeout
        )
        
        return APIResponse(
            status="success",
            message="Plugin executed successfully",
            data={
                "request_id": result.request_id,
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}")
        raise HTTPException(status_code=500, detail="Plugin execution failed")

@app.get("/api/synapse/plugin/{plugin_id}/status", response_model=APIResponse)
async def get_plugin_status(
    plugin_id: str,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get plugin status."""
    try:
        status = synapse_instance.get_plugin_status(plugin_id)
        
        if status:
            return APIResponse(
                status="success",
                message="Plugin status retrieved",
                data=status.__dict__
            )
        else:
            raise HTTPException(status_code=404, detail="Plugin not found")
    except Exception as e:
        logger.error(f"Failed to get plugin status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plugin status")

@app.get("/api/synapse/plugins", response_model=APIResponse)
async def list_plugins(
    status_filter: Optional[str] = None,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """List plugins."""
    try:
        plugins = synapse_instance.list_plugins(status_filter)
        
        return APIResponse(
            status="success",
            message="Plugins retrieved successfully",
            data={"plugins": [plugin.__dict__ for plugin in plugins]}
        )
    except Exception as e:
        logger.error(f"Failed to list plugins: {e}")
        raise HTTPException(status_code=500, detail="Failed to list plugins")

# Permission Management Endpoints

@app.post("/api/synapse/plugin/{plugin_id}/permissions/request", response_model=APIResponse)
async def request_permissions(
    plugin_id: str,
    permissions: List[str],
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Request permissions for a plugin."""
    try:
        request_id = synapse_instance.request_permissions(plugin_id, current_user, permissions)
        
        return APIResponse(
            status="success",
            message="Permission request created",
            data={"request_id": request_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Permission request failed: {e}")
        raise HTTPException(status_code=500, detail="Permission request failed")

@app.post("/api/synapse/permissions/{request_id}/approve", response_model=APIResponse)
async def approve_permissions(
    request_id: str,
    approval: PermissionApprovalRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Approve a permission request."""
    try:
        success = synapse_instance.approve_permissions(request_id, current_user, approval.reason)
        
        if success:
            return APIResponse(
                status="success",
                message="Permissions approved",
                data={"request_id": request_id}
            )
        else:
            raise HTTPException(status_code=400, detail="Permission approval failed")
    except Exception as e:
        logger.error(f"Permission approval failed: {e}")
        raise HTTPException(status_code=500, detail="Permission approval failed")

@app.post("/api/synapse/permissions/{request_id}/deny", response_model=APIResponse)
async def deny_permissions(
    request_id: str,
    denial: PermissionDenialRequest,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Deny a permission request."""
    try:
        success = synapse_instance.deny_permissions(request_id, current_user, denial.reason)
        
        if success:
            return APIResponse(
                status="success",
                message="Permissions denied",
                data={"request_id": request_id}
            )
        else:
            raise HTTPException(status_code=400, detail="Permission denial failed")
    except Exception as e:
        logger.error(f"Permission denial failed: {e}")
        raise HTTPException(status_code=500, detail="Permission denial failed")

@app.get("/api/synapse/permissions/pending", response_model=APIResponse)
async def get_pending_permissions(
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get pending permission requests."""
    try:
        requests = synapse_instance.get_pending_permission_requests()
        
        return APIResponse(
            status="success",
            message="Pending permissions retrieved",
            data={"requests": [request.__dict__ for request in requests]}
        )
    except Exception as e:
        logger.error(f"Failed to get pending permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending permissions")

# Connection Management Endpoints

@app.post("/api/synapse/connection/request", response_model=APIResponse)
async def request_connection(
    connection: ConnectionRequestModel,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Request a connection to an external agent."""
    try:
        connection_id = synapse_instance.request_connection(
            connection.agent_id, connection.intent, connection.permissions, current_user
        )
        
        return APIResponse(
            status="success",
            message="Connection request created",
            data={"connection_id": connection_id}
        )
    except Exception as e:
        logger.error(f"Connection request failed: {e}")
        raise HTTPException(status_code=500, detail="Connection request failed")

@app.post("/api/synapse/connection/{connection_id}/approve", response_model=APIResponse)
async def approve_connection(
    connection_id: str,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Approve a connection request."""
    try:
        result = synapse_instance.approve_connection(connection_id, current_user)
        
        return APIResponse(
            status="success",
            message="Connection approved",
            data=result.__dict__
        )
    except Exception as e:
        logger.error(f"Connection approval failed: {e}")
        raise HTTPException(status_code=500, detail="Connection approval failed")

@app.post("/api/synapse/connection/{connection_id}/close", response_model=APIResponse)
async def close_connection(
    connection_id: str,
    current_user: str = Depends(get_current_user),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Close a connection."""
    try:
        success = synapse_instance.close_connection(connection_id, current_user)
        
        if success:
            return APIResponse(
                status="success",
                message="Connection closed",
                data={"connection_id": connection_id}
            )
        else:
            raise HTTPException(status_code=400, detail="Connection close failed")
    except Exception as e:
        logger.error(f"Connection close failed: {e}")
        raise HTTPException(status_code=500, detail="Connection close failed")

# Benchmarking Endpoints

@app.post("/api/synapse/plugin/{plugin_id}/benchmark", response_model=APIResponse)
async def run_benchmark(
    plugin_id: str,
    benchmark: BenchmarkRequest,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Run a benchmark test for a plugin."""
    try:
        # This is a simplified implementation
        # In a real system, you'd have actual test functions
        def test_function(**params):
            import time
            time.sleep(0.1)
            return {"result": "benchmark_test"}
        
        result = synapse_instance.run_benchmark(
            plugin_id, test_function, benchmark.test_params
        )
        
        return APIResponse(
            status="success",
            message="Benchmark completed",
            data=result
        )
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        raise HTTPException(status_code=500, detail="Benchmark failed")

@app.get("/api/synapse/plugin/{plugin_id}/benchmark", response_model=APIResponse)
async def get_benchmark_summary(
    plugin_id: str,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get benchmark summary for a plugin."""
    try:
        summary = synapse_instance.get_benchmark_summary(plugin_id)
        
        if summary:
            return APIResponse(
                status="success",
                message="Benchmark summary retrieved",
                data=summary
            )
        else:
            return APIResponse(
                status="success",
                message="No benchmark data available",
                data=None
            )
    except Exception as e:
        logger.error(f"Failed to get benchmark summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get benchmark summary")

# Traffic Monitoring Endpoints

@app.get("/api/synapse/traffic/logs", response_model=APIResponse)
async def get_traffic_logs(
    filter_params: TrafficLogFilter = Depends(),
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get traffic logs."""
    try:
        logs = synapse_instance.get_traffic_logs(**filter_params.dict(exclude_none=True))
        
        return APIResponse(
            status="success",
            message="Traffic logs retrieved",
            data={"logs": logs}
        )
    except Exception as e:
        logger.error(f"Failed to get traffic logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get traffic logs")

@app.get("/api/synapse/traffic/summary", response_model=APIResponse)
async def get_traffic_summary(
    hours: int = 24,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get traffic summary."""
    try:
        summary = synapse_instance.get_traffic_summary(hours)
        
        return APIResponse(
            status="success",
            message="Traffic summary retrieved",
            data=summary
        )
    except Exception as e:
        logger.error(f"Failed to get traffic summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get traffic summary")

@app.get("/api/synapse/traffic/export", response_model=APIResponse)
async def export_traffic_logs(
    format: str = "json",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Export traffic logs."""
    try:
        exported_data = synapse_instance.export_traffic_logs(
            format=format, start_time=start_time, end_time=end_time
        )
        
        return APIResponse(
            status="success",
            message="Traffic logs exported",
            data={"export": exported_data}
        )
    except Exception as e:
        logger.error(f"Failed to export traffic logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to export traffic logs")

# System Management Endpoints

@app.get("/api/synapse/system/status", response_model=APIResponse)
async def get_system_status(
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Get system status."""
    try:
        status = synapse_instance.get_system_status()
        
        return APIResponse(
            status="success",
            message="System status retrieved",
            data=status
        )
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@app.get("/api/synapse/system/export", response_model=APIResponse)
async def export_system_data(
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Export all system data."""
    try:
        data = synapse_instance.export_system_data()
        
        return APIResponse(
            status="success",
            message="System data exported",
            data=data
        )
    except Exception as e:
        logger.error(f"Failed to export system data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export system data")

@app.post("/api/synapse/system/cleanup", response_model=APIResponse)
async def cleanup_system(
    synapse_instance: Synapse = Depends(get_synapse)
):
    """Clean up system resources."""
    try:
        synapse_instance.cleanup_system()
        
        return APIResponse(
            status="success",
            message="System cleanup completed",
            data=None
        )
    except Exception as e:
        logger.error(f"System cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="System cleanup failed")

# Settings management endpoints

class SettingsUpdateRequest(BaseModel):
    """Settings update request."""
    settings: Dict[str, Any] = Field(..., description="Settings data")

@app.post("/api/settings", response_model=APIResponse)
async def save_settings(request: SettingsUpdateRequest):
    """Save Hearthlink settings."""
    try:
        import os
        import json
        from pathlib import Path
        
        # Create settings directory if it doesn't exist
        settings_dir = Path("hearthlink_data/settings")
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save settings to file
        settings_file = settings_dir / "hearthlink_settings.json"
        with open(settings_file, 'w') as f:
            json.dump(request.settings, f, indent=2)
        
        return APIResponse(
            status="success",
            message="Settings saved successfully",
            data={"settings_file": str(settings_file)}
        )
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")

@app.get("/api/settings", response_model=APIResponse)
async def get_settings():
    """Get Hearthlink settings."""
    try:
        import os
        import json
        from pathlib import Path
        
        settings_file = Path("hearthlink_data/settings/hearthlink_settings.json")
        
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            # Return default settings
            settings = {
                "llm": {"model": "llama3.2", "temperature": 0.7},
                "vault": {"encryption": True},
                "synapse": {"sandbox": True},
                "sentry": {"monitoring": True}
            }
        
        return APIResponse(
            status="success",
            message="Settings retrieved successfully",
            data=settings
        )
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

# Health check endpoint

@app.get("/api/synapse/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint."""
    return APIResponse(
        status="success",
        message="Synapse API is healthy",
        data={"version": "1.0.0"}
    ) 