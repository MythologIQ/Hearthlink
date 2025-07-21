"""
MCP Server Management API Endpoints
Provides REST API for managing Model Context Protocol servers
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ..mcp_plugin_manager import get_mcp_plugin_manager, MCPPluginManager
from ..auth import require_auth, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/synapse/mcp", tags=["MCP Servers"])

# Request/Response Models
class MCPToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class MCPServerResponse(BaseModel):
    server_id: str
    plugin_id: str
    name: str
    version: str
    status: str
    description: str
    connection_type: str
    security_level: str
    auto_start: bool
    oauth_required: bool
    tools_available: List[str]

class MCPToolResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    server_id: str
    status: str
    healthy: bool
    last_check: str
    details: Optional[Dict[str, Any]] = None

# Dependency to get MCP plugin manager
async def get_mcp_manager() -> MCPPluginManager:
    manager = get_mcp_plugin_manager()
    if not manager:
        raise HTTPException(status_code=503, detail="MCP Plugin Manager not initialized")
    return manager

@router.get("/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """List all available MCP servers"""
    try:
        servers = mcp_manager.list_active_servers()
        
        return [
            MCPServerResponse(
                server_id=server.server_id,
                plugin_id=server.plugin_id,
                name=server.name,
                version=server.version,
                status=server.status,
                description=server.description,
                connection_type=server.connection_type,
                security_level=server.security_level,
                auto_start=server.auto_start,
                oauth_required=server.oauth_required,
                tools_available=mcp_manager.get_available_tools(server.server_id)
            )
            for server in servers
        ]
        
    except Exception as e:
        logger.error(f"Failed to list MCP servers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP servers")

@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: str,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Get information about a specific MCP server"""
    try:
        server = mcp_manager.get_server_info(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
        
        return MCPServerResponse(
            server_id=server.server_id,
            plugin_id=server.plugin_id,
            name=server.name,
            version=server.version,
            status=server.status,
            description=server.description,
            connection_type=server.connection_type,
            security_level=server.security_level,
            auto_start=server.auto_start,
            oauth_required=server.oauth_required,
            tools_available=mcp_manager.get_available_tools(server_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP server")

@router.post("/servers/{server_id}/start")
async def start_mcp_server(
    server_id: str,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Start an MCP server"""
    try:
        success = await mcp_manager.start_mcp_server(server_id)
        
        if success:
            return {"message": f"MCP server {server_id} started successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to start MCP server {server_id}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start MCP server")

@router.post("/servers/{server_id}/stop")
async def stop_mcp_server(
    server_id: str,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Stop an MCP server"""
    try:
        success = await mcp_manager.stop_mcp_server(server_id)
        
        if success:
            return {"message": f"MCP server {server_id} stopped successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to stop MCP server {server_id}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop MCP server")

@router.get("/servers/{server_id}/tools")
async def get_mcp_server_tools(
    server_id: str,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Get available tools for an MCP server"""
    try:
        server = mcp_manager.get_server_info(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
        
        tools = mcp_manager.get_available_tools(server_id)
        
        return {
            "server_id": server_id,
            "tools": tools,
            "count": len(tools)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tools for MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP server tools")

@router.post("/servers/{server_id}/execute", response_model=MCPToolResponse)
async def execute_mcp_tool(
    server_id: str,
    request: MCPToolRequest,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Execute a tool on an MCP server"""
    try:
        result = await mcp_manager.execute_mcp_tool(
            server_id=server_id,
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        
        return MCPToolResponse(
            success=result.get('success', False),
            result=result.get('result'),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Failed to execute MCP tool {request.tool_name} on server {server_id}: {e}")
        return MCPToolResponse(
            success=False,
            error=f"Execution failed: {str(e)}"
        )

@router.get("/servers/{server_id}/health", response_model=HealthCheckResponse)
async def get_mcp_server_health(
    server_id: str,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Get health status of an MCP server"""
    try:
        server = mcp_manager.get_server_info(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
        
        health_results = await mcp_manager.health_check_all_servers()
        health_info = health_results.get(server_id, {})
        
        return HealthCheckResponse(
            server_id=server_id,
            status=health_info.get('status', 'unknown'),
            healthy=health_info.get('status') == 'healthy',
            last_check=health_info.get('timestamp', ''),
            details=health_info.get('details')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get health for MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP server health")

@router.get("/health", response_model=List[HealthCheckResponse])
async def get_all_mcp_health(
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Get health status of all MCP servers"""
    try:
        health_results = await mcp_manager.health_check_all_servers()
        
        return [
            HealthCheckResponse(
                server_id=server_id,
                status=health_info.get('status', 'unknown'),
                healthy=health_info.get('status') == 'healthy',
                last_check=health_info.get('timestamp', ''),
                details=health_info.get('details')
            )
            for server_id, health_info in health_results.items()
        ]
        
    except Exception as e:
        logger.error(f"Failed to get health for all MCP servers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP server health")

# Gmail/Calendar specific endpoints
@router.post("/gmail/send")
async def send_gmail(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Send email via Gmail MCP server"""
    try:
        result = await mcp_manager.execute_mcp_tool(
            server_id="gmail-calendar",
            tool_name="send_email",
            parameters={
                "to": to,
                "subject": subject,
                "body": body,
                "attachments": attachments or []
            }
        )
        
        if result.get('success'):
            return {"message": "Email sent successfully", "result": result.get('result')}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to send email: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.get("/gmail/emails")
async def list_gmail_emails(
    query: Optional[str] = None,
    max_results: int = 50,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """List emails from Gmail"""
    try:
        result = await mcp_manager.execute_mcp_tool(
            server_id="gmail-calendar",
            tool_name="list_emails",
            parameters={
                "query": query,
                "max_results": max_results
            }
        )
        
        if result.get('success'):
            return result.get('result')
        else:
            raise HTTPException(status_code=400, detail=f"Failed to list emails: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list emails: {e}")
        raise HTTPException(status_code=500, detail="Failed to list emails")

@router.get("/calendar/events")
async def list_calendar_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 250,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """List calendar events"""
    try:
        result = await mcp_manager.execute_mcp_tool(
            server_id="gmail-calendar",
            tool_name="list_calendar_events",
            parameters={
                "calendar_id": calendar_id,
                "time_min": time_min,
                "time_max": time_max,
                "max_results": max_results
            }
        )
        
        if result.get('success'):
            return result.get('result')
        else:
            raise HTTPException(status_code=400, detail=f"Failed to list calendar events: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list calendar events: {e}")
        raise HTTPException(status_code=500, detail="Failed to list calendar events")

@router.post("/calendar/events")
async def create_calendar_event(
    calendar_id: str,
    summary: str,
    start: str,
    end: str,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user),
    mcp_manager: MCPPluginManager = Depends(get_mcp_manager)
):
    """Create a calendar event"""
    try:
        result = await mcp_manager.execute_mcp_tool(
            server_id="gmail-calendar",
            tool_name="create_calendar_event",
            parameters={
                "calendar_id": calendar_id,
                "summary": summary,
                "start": start,
                "end": end,
                "description": description,
                "attendees": attendees or []
            }
        )
        
        if result.get('success'):
            return {"message": "Calendar event created successfully", "result": result.get('result')}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create calendar event: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create calendar event")