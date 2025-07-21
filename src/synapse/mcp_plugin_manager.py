"""
MCP Plugin Manager for Synapse
Manages Model Context Protocol servers as Synapse plugins
"""

import json
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from .plugin_manager import PluginManager
from .api import SynapseAPI

logger = logging.getLogger(__name__)

@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    server_id: str
    plugin_id: str
    name: str
    version: str
    status: str
    description: str
    package: str
    tools_provided: List[str]
    connection_type: str
    security_level: str
    auto_start: bool
    oauth_required: bool = False
    sandbox_required: bool = False

class MCPPluginManager:
    """
    Manages MCP servers as Synapse plugins
    Handles registration, lifecycle, and integration
    """
    
    def __init__(self, synapse_api: SynapseAPI, plugin_manager: PluginManager):
        self.synapse_api = synapse_api
        self.plugin_manager = plugin_manager
        self.config_dir = Path(__file__).parent / "config"
        self.plugins_dir = Path(__file__).parent / "plugins"
        self.registry_file = self.config_dir / "mcp_server_registry.json"
        
        self.active_servers: Dict[str, MCPServerInfo] = {}
        self.server_registry: Dict[str, Any] = {}
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.plugins_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Initialize MCP plugin manager"""
        logger.info("Initializing MCP Plugin Manager")
        
        try:
            # Load server registry
            await self.load_server_registry()
            
            # Discover existing plugins
            await self.discover_mcp_plugins()
            
            # Auto-start enabled servers
            await self.auto_start_servers()
            
            logger.info(f"MCP Plugin Manager initialized with {len(self.active_servers)} servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Plugin Manager: {e}")
            raise
    
    async def load_server_registry(self):
        """Load MCP server registry configuration"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    self.server_registry = json.load(f)
                logger.info(f"Loaded MCP server registry: {self.server_registry.get('registry_version', 'unknown')}")
            else:
                logger.warning("MCP server registry not found, creating default")
                await self.create_default_registry()
                
        except Exception as e:
            logger.error(f"Failed to load server registry: {e}")
            await self.create_default_registry()
    
    async def create_default_registry(self):
        """Create default server registry"""
        default_registry = {
            "registry_version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "active_servers": [],
            "pending_servers": [],
            "configuration": {
                "default_security_level": "medium",
                "auto_discovery": True,
                "max_concurrent_servers": 20
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(default_registry, f, indent=2)
        
        self.server_registry = default_registry
        logger.info("Created default MCP server registry")
    
    async def discover_mcp_plugins(self):
        """Discover MCP plugins from manifests"""
        logger.info("Discovering MCP plugins...")
        
        discovered_count = 0
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_file = plugin_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        await self.register_plugin_from_manifest(manifest_file)
                        discovered_count += 1
                    except Exception as e:
                        logger.error(f"Failed to register plugin from {manifest_file}: {e}")
        
        logger.info(f"Discovered {discovered_count} MCP plugins")
    
    async def register_plugin_from_manifest(self, manifest_file: Path):
        """Register MCP plugin from manifest file"""
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Validate manifest
            if not self.validate_mcp_manifest(manifest):
                raise ValueError("Invalid MCP manifest")
            
            # Create server info
            server_info = MCPServerInfo(
                server_id=manifest.get('plugin_id', '').replace('-mcp', ''),
                plugin_id=manifest['plugin_id'],
                name=manifest['name'],
                version=manifest['version'],
                status='registered',
                description=manifest['description'],
                package=manifest.get('mcp_config', {}).get('server_package', manifest['plugin_id']),
                tools_provided=manifest.get('api_endpoints', []),
                connection_type=manifest.get('mcp_config', {}).get('transport', 'direct'),
                security_level=manifest.get('security_profile', {}).get('risk_level', 50),
                auto_start=manifest.get('core_integration', {}).get('startup_priority') == 'critical',
                oauth_required=bool(manifest.get('oauth_config')),
                sandbox_required=manifest.get('sandbox_config', {}).get('network_policy') == 'restricted'
            )
            
            # Register with Synapse plugin manager
            registration_result = await self.plugin_manager.register_plugin(
                manifest_data=manifest,
                user_id='system'
            )
            
            if registration_result['success']:
                self.active_servers[server_info.server_id] = server_info
                logger.info(f"Registered MCP plugin: {server_info.name} ({server_info.plugin_id})")
            else:
                logger.error(f"Failed to register MCP plugin {server_info.name}: {registration_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to register plugin from manifest {manifest_file}: {e}")
            raise
    
    def validate_mcp_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validate MCP plugin manifest"""
        required_fields = ['plugin_id', 'name', 'version', 'type', 'description']
        
        for field in required_fields:
            if field not in manifest:
                logger.error(f"Missing required field in manifest: {field}")
                return False
        
        if manifest['type'] != 'mcp_server':
            logger.error(f"Invalid plugin type: {manifest['type']} (expected: mcp_server)")
            return False
        
        return True
    
    async def auto_start_servers(self):
        """Auto-start enabled MCP servers"""
        logger.info("Auto-starting MCP servers...")
        
        started_count = 0
        
        for server_id, server_info in self.active_servers.items():
            if server_info.auto_start:
                try:
                    await self.start_mcp_server(server_id)
                    started_count += 1
                except Exception as e:
                    logger.error(f"Failed to auto-start MCP server {server_id}: {e}")
        
        logger.info(f"Auto-started {started_count} MCP servers")
    
    async def start_mcp_server(self, server_id: str) -> bool:
        """Start an MCP server"""
        if server_id not in self.active_servers:
            logger.error(f"Unknown MCP server: {server_id}")
            return False
        
        server_info = self.active_servers[server_id]
        
        try:
            logger.info(f"Starting MCP server: {server_info.name}")
            
            # Approve plugin if not already approved
            approval_result = await self.plugin_manager.approve_plugin(
                plugin_id=server_info.plugin_id,
                user_id='system',
                reason='Auto-approval for MCP server'
            )
            
            if not approval_result['success']:
                logger.error(f"Failed to approve MCP plugin {server_info.plugin_id}: {approval_result.get('error')}")
                return False
            
            # Update server status
            server_info.status = 'active'
            
            logger.info(f"Successfully started MCP server: {server_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_id}: {e}")
            server_info.status = 'error'
            return False
    
    async def stop_mcp_server(self, server_id: str) -> bool:
        """Stop an MCP server"""
        if server_id not in self.active_servers:
            logger.error(f"Unknown MCP server: {server_id}")
            return False
        
        server_info = self.active_servers[server_id]
        
        try:
            logger.info(f"Stopping MCP server: {server_info.name}")
            
            # Revoke plugin
            revoke_result = await self.plugin_manager.revoke_plugin(
                plugin_id=server_info.plugin_id,
                user_id='system',
                reason='Manual stop request'
            )
            
            if revoke_result['success']:
                server_info.status = 'stopped'
                logger.info(f"Successfully stopped MCP server: {server_info.name}")
                return True
            else:
                logger.error(f"Failed to revoke MCP plugin {server_info.plugin_id}: {revoke_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop MCP server {server_id}: {e}")
            return False
    
    async def execute_mcp_tool(self, server_id: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on an MCP server"""
        if server_id not in self.active_servers:
            return {'success': False, 'error': f'Unknown MCP server: {server_id}'}
        
        server_info = self.active_servers[server_id]
        
        if server_info.status != 'active':
            return {'success': False, 'error': f'MCP server {server_id} is not active (status: {server_info.status})'}
        
        try:
            # Execute plugin with MCP tool request
            execution_result = await self.plugin_manager.execute_plugin(
                plugin_id=server_info.plugin_id,
                user_id='system',
                execution_data={
                    'tool': tool_name,
                    'parameters': parameters
                }
            )
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Failed to execute MCP tool {tool_name} on server {server_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_server_info(self, server_id: str) -> Optional[MCPServerInfo]:
        """Get information about an MCP server"""
        return self.active_servers.get(server_id)
    
    def list_active_servers(self) -> List[MCPServerInfo]:
        """List all active MCP servers"""
        return list(self.active_servers.values())
    
    def get_available_tools(self, server_id: str) -> List[str]:
        """Get list of available tools for an MCP server"""
        server_info = self.get_server_info(server_id)
        if server_info:
            return [tool.get('name', '') for tool in server_info.tools_provided if isinstance(tool, dict)]
        return []
    
    async def health_check_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all active MCP servers"""
        health_results = {}
        
        for server_id, server_info in self.active_servers.items():
            if server_info.status == 'active':
                try:
                    # Perform health check via plugin manager
                    health_result = await self.plugin_manager.get_plugin_health(server_info.plugin_id)
                    health_results[server_id] = health_result
                except Exception as e:
                    health_results[server_id] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            else:
                health_results[server_id] = {
                    'status': server_info.status,
                    'message': f'Server is {server_info.status}'
                }
        
        return health_results
    
    async def update_server_registry(self):
        """Update the server registry file with current state"""
        try:
            self.server_registry['last_updated'] = datetime.utcnow().isoformat() + "Z"
            self.server_registry['active_servers'] = [
                {
                    'server_id': info.server_id,
                    'plugin_id': info.plugin_id,
                    'name': info.name,
                    'version': info.version,
                    'status': info.status,
                    'description': info.description,
                    'package': info.package,
                    'tools_provided': info.tools_provided,
                    'connection_type': info.connection_type,
                    'security_level': info.security_level,
                    'auto_start': info.auto_start,
                    'oauth_required': info.oauth_required,
                    'sandbox_required': info.sandbox_required
                }
                for info in self.active_servers.values()
            ]
            
            with open(self.registry_file, 'w') as f:
                json.dump(self.server_registry, f, indent=2)
                
            logger.info("Updated MCP server registry")
            
        except Exception as e:
            logger.error(f"Failed to update server registry: {e}")

# Global MCP Plugin Manager instance
mcp_plugin_manager: Optional[MCPPluginManager] = None

async def initialize_mcp_plugin_manager(synapse_api: SynapseAPI, plugin_manager: PluginManager):
    """Initialize the global MCP plugin manager"""
    global mcp_plugin_manager
    mcp_plugin_manager = MCPPluginManager(synapse_api, plugin_manager)
    await mcp_plugin_manager.initialize()
    return mcp_plugin_manager

def get_mcp_plugin_manager() -> Optional[MCPPluginManager]:
    """Get the global MCP plugin manager instance"""
    return mcp_plugin_manager