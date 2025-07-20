"""
Synapse - Secure External Gateway & Protocol Boundary

Main orchestrator for all external traffic, plugin management, and API integration.
Provides the unified interface for plugin registration, execution, and monitoring.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

from .plugin_manager import PluginManager, PluginExecutionResult, PluginStatus
from .manifest import PluginManifest, RiskTier
from .permissions import PermissionManager, PermissionRequest
from .sandbox import SandboxManager
from .benchmark import BenchmarkManager, PerformanceTier
from .traffic_logger import TrafficLogger, TrafficSummary
from .traffic_manager import SynapseTrafficManager, AgentPriority
from .sentry_siem import SentrySecurityOrchestrator, ThreatLevel

@dataclass
class SynapseConfig:
    """Synapse configuration."""
    sandbox: Dict[str, Any] = field(default_factory=lambda: {
        "max_cpu_percent": 50.0,
        "max_memory_mb": 512,
        "max_disk_mb": 100,
        "max_execution_time": 300
    })
    benchmark: Dict[str, Any] = field(default_factory=lambda: {
        "test_duration": 30,
        "response_time_threshold": 1000.0
    })
    traffic: Dict[str, Any] = field(default_factory=lambda: {
        "max_entries": 10000,
        "retention_days": 30
    })
    security: Dict[str, Any] = field(default_factory=lambda: {
        "require_manifest_signature": True,
        "auto_approve_low_risk": False,
        "max_concurrent_executions": 10,
        "security_threshold": "MEDIUM"
    })
    traffic_manager: Dict[str, Any] = field(default_factory=lambda: {
        "max_workers": 10,
        "enable_rate_limiting": True,
        "enable_security_monitoring": True
    })

@dataclass
class ConnectionRequest:
    """External connection request."""
    connection_id: str
    agent_id: str
    intent: str
    permissions: List[str]
    user_id: str
    status: str = "pending"
    requested_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None

@dataclass
class ConnectionResult:
    """Connection establishment result."""
    connection_id: str
    status: str
    error: Optional[str] = None
    established_at: Optional[str] = None

class Synapse:
    """Main Synapse gateway system."""
    
    def __init__(self, config: Optional[SynapseConfig] = None, logger=None):
        self.config = config or SynapseConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize plugin manager
        config_dict = {
            "sandbox": self.config.sandbox,
            "benchmark": self.config.benchmark,
            "traffic": self.config.traffic
        }
        self.plugin_manager = PluginManager(config_dict, self.logger)
        
        # Direct access to subsystems for advanced operations
        self.permission_manager = self.plugin_manager.permission_manager
        self.sandbox_manager = self.plugin_manager.sandbox_manager
        self.benchmark_manager = self.plugin_manager.benchmark_manager
        self.traffic_logger = self.plugin_manager.traffic_logger
        
        # Connection management
        self.connections: Dict[str, ConnectionRequest] = {}
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        
        # Enhanced traffic management and security
        self.traffic_manager = SynapseTrafficManager(
            config=self.config.traffic_manager,
            logger=self.logger
        )
        self.security_orchestrator = SentrySecurityOrchestrator(
            config=self.config.security,
            logger=self.logger
        )
    
    # Plugin Management API
    
    def register_plugin(self, manifest_data: Dict[str, Any], user_id: str) -> str:
        """
        Register a new plugin.
        
        Args:
            manifest_data: Plugin manifest data
            user_id: User registering the plugin
            
        Returns:
            Plugin ID
        """
        return self.plugin_manager.register_plugin(manifest_data, user_id)
    
    def approve_plugin(self, plugin_id: str, user_id: str, reason: Optional[str] = None) -> bool:
        """
        Approve a plugin for execution.
        
        Args:
            plugin_id: Plugin to approve
            user_id: User approving the plugin
            reason: Optional reason for approval
            
        Returns:
            Success status
        """
        return self.plugin_manager.approve_plugin(plugin_id, user_id, reason)
    
    def revoke_plugin(self, plugin_id: str, user_id: str, reason: str) -> bool:
        """
        Revoke a plugin.
        
        Args:
            plugin_id: Plugin to revoke
            user_id: User revoking the plugin
            reason: Reason for revocation
            
        Returns:
            Success status
        """
        return self.plugin_manager.revoke_plugin(plugin_id, user_id, reason)
    
    def execute_plugin(self, plugin_id: str, user_id: str, payload: Dict[str, Any],
                      session_id: Optional[str] = None, timeout: Optional[int] = None) -> PluginExecutionResult:
        """
        Execute a plugin with enhanced security and rate limiting.
        
        Args:
            plugin_id: Plugin to execute
            user_id: User executing the plugin
            payload: Execution payload
            session_id: Optional session ID
            timeout: Optional timeout override
            
        Returns:
            Execution result
        """
        # Get plugin manifest to determine agent type
        manifest = self.get_plugin_manifest(plugin_id)
        agent_type = "external_agents"  # Default
        
        if manifest:
            # Determine agent type based on manifest
            if manifest.name.lower() == "alden":
                agent_type = "alden"
            elif manifest.name.lower() in ["alice", "mimic", "sentry"]:
                agent_type = "internal_agents"
            elif manifest.name.lower() == "system":
                agent_type = "system"
        
        # Security monitoring
        security_result = self.security_orchestrator.monitor_agent_transaction(
            agent_id=plugin_id,
            transaction_data={
                "user_id": user_id,
                "payload": payload,
                "session_id": session_id,
                "cpu_usage": 0,  # Would be populated by actual monitoring
                "memory_usage": 0,
                "network_activity": 0,
                "request_rate": 1,
                "response_time": 0,
                "data_volume": len(str(payload))
            }
        )
        
        # Check if security blocked the request
        if not security_result.get("allowed", False):
            return PluginExecutionResult(
                plugin_id=plugin_id,
                user_id=user_id,
                success=False,
                error=f"Security blocked: {security_result.get('reason', 'Unknown security violation')}",
                execution_time=0,
                response_data={"security_event_id": security_result.get("security_event_id")}
            )
        
        # Execute through traffic manager for rate limiting
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # Submit to traffic manager (this is async but we'll handle it synchronously for now)
        import asyncio
        
        try:
            # Create new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Submit request for rate limiting
            traffic_result = loop.run_until_complete(
                self.traffic_manager.submit_request(
                    request_id=request_id,
                    agent_type=agent_type,
                    payload=payload,
                    user_id=user_id
                )
            )
            
            # Check if rate limited
            if not traffic_result.get("success", False):
                return PluginExecutionResult(
                    plugin_id=plugin_id,
                    user_id=user_id,
                    success=False,
                    error=f"Rate limited: {traffic_result.get('error', 'Rate limit exceeded')}",
                    execution_time=0,
                    response_data={"retry_after": traffic_result.get("retry_after")}
                )
            
            # Execute the plugin
            execution_result = self.plugin_manager.execute_plugin(plugin_id, user_id, payload, session_id, timeout)
            
            # Log successful execution
            self.logger.info(f"Plugin executed successfully: {plugin_id} by {user_id}")
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing plugin {plugin_id}: {e}")
            return PluginExecutionResult(
                plugin_id=plugin_id,
                user_id=user_id,
                success=False,
                error=str(e),
                execution_time=0
            )
    
    def get_plugin_status(self, plugin_id: str) -> Optional[PluginStatus]:
        """Get plugin status."""
        return self.plugin_manager.get_plugin_status(plugin_id)
    
    def list_plugins(self, status_filter: Optional[str] = None) -> List[PluginStatus]:
        """List plugins with optional status filter."""
        return self.plugin_manager.list_plugins(status_filter)
    
    def get_plugin_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest."""
        return self.plugin_manager.get_plugin_manifest(plugin_id)
    
    # Permission Management API
    
    def request_permissions(self, plugin_id: str, user_id: str, permissions: List[str]) -> str:
        """
        Request permissions for a plugin.
        
        Args:
            plugin_id: Plugin requesting permissions
            user_id: User making the request
            permissions: List of permission types
            
        Returns:
            Request ID
        """
        return self.permission_manager.request_permissions(plugin_id, user_id, permissions)
    
    def approve_permissions(self, request_id: str, user_id: str, reason: Optional[str] = None) -> bool:
        """
        Approve a permission request.
        
        Args:
            request_id: Request to approve
            user_id: User approving the request
            reason: Optional reason for approval
            
        Returns:
            Success status
        """
        return self.permission_manager.approve_permissions(request_id, user_id, reason)
    
    def deny_permissions(self, request_id: str, user_id: str, reason: str) -> bool:
        """
        Deny a permission request.
        
        Args:
            request_id: Request to deny
            user_id: User denying the request
            reason: Reason for denial
            
        Returns:
            Success status
        """
        return self.permission_manager.deny_permissions(request_id, user_id, reason)
    
    def check_permission(self, plugin_id: str, permission: str) -> bool:
        """
        Check if a plugin has a specific permission.
        
        Args:
            plugin_id: Plugin to check
            permission: Permission to check
            
        Returns:
            True if permission is granted
        """
        return self.permission_manager.check_permission(plugin_id, permission)
    
    def get_pending_permission_requests(self) -> List[PermissionRequest]:
        """Get all pending permission requests."""
        return self.permission_manager.get_pending_requests()
    
    # Connection Management API
    
    def request_connection(self, agent_id: str, intent: str, permissions: List[str], user_id: str) -> str:
        """
        Request a connection to an external agent.
        
        Args:
            agent_id: External agent identifier
            intent: Purpose of the connection
            permissions: Required permissions
            user_id: User requesting the connection
            
        Returns:
            Connection ID
        """
        connection_id = f"conn-{uuid.uuid4().hex[:8]}"
        
        connection = ConnectionRequest(
            connection_id=connection_id,
            agent_id=agent_id,
            intent=intent,
            permissions=permissions,
            user_id=user_id
        )
        
        self.connections[connection_id] = connection
        
        # Log connection request
        self.traffic_logger.log_traffic(
            traffic_type=self.traffic_logger.TrafficType.CONNECTION_REQUEST,
            source="user",
            target=agent_id,
            user_id=user_id,
            request_id=connection_id,
            payload={"intent": intent, "permissions": permissions},
            severity=self.traffic_logger.TrafficSeverity.MEDIUM
        )
        
        self.logger.info(f"Connection requested: {connection_id} to {agent_id}")
        return connection_id
    
    def approve_connection(self, connection_id: str, user_id: str) -> ConnectionResult:
        """
        Approve a connection request.
        
        Args:
            connection_id: Connection to approve
            user_id: User approving the connection
            
        Returns:
            Connection result
        """
        if connection_id not in self.connections:
            return ConnectionResult(connection_id=connection_id, status="error", error="Connection not found")
        
        connection = self.connections[connection_id]
        connection.status = "approved"
        connection.approved_at = datetime.now().isoformat()
        connection.approved_by = user_id
        
        # Establish connection
        self.active_connections[connection_id] = {
            "connection": connection,
            "established_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Log connection establishment
        self.traffic_logger.log_traffic(
            traffic_type=self.traffic_logger.TrafficType.CONNECTION_ESTABLISH,
            source="user",
            target=connection.agent_id,
            user_id=user_id,
            request_id=connection_id,
            payload={"intent": connection.intent},
            severity=self.traffic_logger.TrafficSeverity.MEDIUM
        )
        
        self.logger.info(f"Connection approved: {connection_id}")
        
        return ConnectionResult(
            connection_id=connection_id,
            status="established",
            established_at=datetime.now().isoformat()
        )
    
    def close_connection(self, connection_id: str, user_id: str) -> bool:
        """
        Close an active connection.
        
        Args:
            connection_id: Connection to close
            user_id: User closing the connection
            
        Returns:
            Success status
        """
        if connection_id not in self.active_connections:
            return False
        
        connection_data = self.active_connections[connection_id]
        connection = connection_data["connection"]
        
        # Update connection status
        connection.status = "closed"
        
        # Log connection close
        self.traffic_logger.log_traffic(
            traffic_type=self.traffic_logger.TrafficType.CONNECTION_CLOSE,
            source="user",
            target=connection.agent_id,
            user_id=user_id,
            request_id=connection_id,
            severity=self.traffic_logger.TrafficSeverity.LOW
        )
        
        # Remove from active connections
        del self.active_connections[connection_id]
        
        self.logger.info(f"Connection closed: {connection_id}")
        return True
    
    # Benchmarking API
    
    def run_benchmark(self, plugin_id: str, test_function: callable, 
                     test_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a benchmark test for a plugin.
        
        Args:
            plugin_id: Plugin to benchmark
            test_function: Function to execute for testing
            test_params: Optional parameters for test function
            
        Returns:
            Benchmark summary
        """
        summary = self.benchmark_manager.run_benchmark(plugin_id, test_function, test_params)
        return asdict(summary) if summary else {}
    
    def get_benchmark_summary(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get benchmark summary for a plugin."""
        summary = self.benchmark_manager.get_benchmark_summary(plugin_id)
        return asdict(summary) if summary else None
    
    def get_performance_tier(self, plugin_id: str) -> str:
        """Get current performance tier for a plugin."""
        tier = self.benchmark_manager.get_performance_tier(plugin_id)
        return tier.value if tier else "unstable"
    
    def get_risk_score(self, plugin_id: str) -> int:
        """Get current risk score for a plugin."""
        return self.benchmark_manager.get_risk_score(plugin_id)
    
    # Traffic Monitoring API
    
    def get_traffic_logs(self, **kwargs) -> List[Dict[str, Any]]:
        """Get traffic logs with optional filtering."""
        logs = self.traffic_logger.get_traffic_logs(**kwargs)
        return [asdict(log) for log in logs]
    
    def get_traffic_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get traffic summary for a time period."""
        summary = self.traffic_logger.get_traffic_summary(hours)
        return asdict(summary) if summary else {}
    
    def export_traffic_logs(self, format: str = "json", **kwargs) -> Union[str, Dict[str, Any]]:
        """Export traffic logs."""
        return self.traffic_logger.export_traffic_logs(format, **kwargs)
    
    def get_traffic_statistics(self) -> Dict[str, Any]:
        """Get current traffic statistics."""
        return self.traffic_logger.get_traffic_statistics()
    
    # Sandbox Management API
    
    def get_sandbox_status(self, plugin_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get sandbox status."""
        return self.sandbox_manager.get_sandbox_status(plugin_id, execution_id)
    
    def list_active_sandboxes(self) -> List[Dict[str, Any]]:
        """List all active sandboxes."""
        return self.sandbox_manager.list_active_sandboxes()
    
    def cleanup_sandbox(self, plugin_id: str, execution_id: str) -> bool:
        """Clean up a sandbox environment."""
        return self.sandbox_manager.cleanup_sandbox(plugin_id, execution_id)
    
    # System Management API
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status with enhanced monitoring."""
        return {
            "plugins": {
                "total": len(self.plugin_manager.plugins),
                "approved": len([p for p in self.plugin_manager.plugin_status.values() if p.approved_by_user]),
                "active": len([p for p in self.plugin_manager.plugin_status.values() if p.status == "approved"])
            },
            "connections": {
                "total": len(self.connections),
                "active": len(self.active_connections)
            },
            "sandboxes": {
                "active": len(self.sandbox_manager.active_sandboxes)
            },
            "permissions": {
                "pending_requests": len(self.permission_manager.get_pending_requests()),
                "active_grants": len(self.permission_manager.grants)
            },
            "traffic": self.traffic_logger.get_traffic_statistics(),
            "enhanced_traffic": self.traffic_manager.get_system_metrics(),
            "security": self.security_orchestrator.get_security_report(),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_system_data(self) -> Dict[str, Any]:
        """Export all system data."""
        return {
            "plugins": {
                plugin_id: self.plugin_manager.export_plugin_data(plugin_id)
                for plugin_id in self.plugin_manager.plugins.keys()
            },
            "permissions": self.permission_manager.export_permissions(),
            "connections": {
                conn_id: asdict(conn) for conn_id, conn in self.connections.items()
            },
            "traffic": self.traffic_logger.export_traffic_logs(),
            "system_status": self.get_system_status(),
            "exported_at": datetime.now().isoformat()
        }
    
    def cleanup_system(self):
        """Clean up all system resources."""
        # Clean up all sandboxes
        self.sandbox_manager.cleanup_all_sandboxes()
        
        # Close all connections
        for connection_id in list(self.active_connections.keys()):
            self.close_connection(connection_id, "system")
        
        # Shutdown enhanced components
        self.traffic_manager.shutdown()
        self.security_orchestrator.shutdown()
        
        self.logger.info("System cleanup completed")
    
    # Enhanced API methods for traffic management and security
    
    def get_traffic_metrics(self) -> Dict[str, Any]:
        """Get comprehensive traffic metrics."""
        return self.traffic_manager.get_system_metrics()
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get detailed security monitoring report."""
        return self.security_orchestrator.get_security_report()
    
    def update_user_bandwidth(self, user_id: str, agent_type: str, rate: float, burst: int):
        """Update user bandwidth budget."""
        self.traffic_manager.update_user_budget(user_id, agent_type, rate, burst)
    
    def register_agent_process(self, agent_id: str, pid: int):
        """Register agent process for security monitoring."""
        self.security_orchestrator.register_agent_process(agent_id, pid)
    
    def is_agent_quarantined(self, agent_id: str) -> bool:
        """Check if agent is quarantined by security system."""
        return self.security_orchestrator.is_agent_quarantined(agent_id)
    
    def release_agent_quarantine(self, agent_id: str):
        """Release agent from security quarantine."""
        self.security_orchestrator.release_quarantine(agent_id)
    
    # Local Resource Management API
    
    def launch_local_resource(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Launch a local resource/tool as specified in the Claude Integration Protocol.
        
        Args:
            target: The target resource to launch (e.g., 'claude_code', 'dev_container', 'gemini_colab')
            **kwargs: Optional flags (background, monitor, ipc_bridge)
            
        Returns:
            Dict containing launch result and status
        """
        import subprocess
        import uuid
        
        # Generate request ID for tracking
        request_id = f"launch-{uuid.uuid4().hex[:8]}"
        
        # Log the launch request
        from .traffic_logger import TrafficType, TrafficSeverity
        self.traffic_logger.log_traffic(
            traffic_type=TrafficType.SYSTEM_OPERATION,
            source="synapse",
            target=target,
            user_id="system",
            request_id=request_id,
            payload={"target": target, "kwargs": kwargs},
            severity=TrafficSeverity.MEDIUM
        )
        
        try:
            # Handle different target types
            if target == "claude_code":
                return self._launch_claude_code(**kwargs)
            elif target == "dev_container":
                return self._launch_dev_container(**kwargs)
            elif target == "gemini_colab":
                return self._launch_gemini_colab(**kwargs)
            else:
                raise ValueError(f"Unknown target: {target}")
                
        except Exception as e:
            self.logger.error(f"Failed to launch {target}: {e}")
            return {
                "request_id": request_id,
                "target": target,
                "success": False,
                "error": str(e),
                "launched_at": datetime.now().isoformat()
            }
    
    def _launch_claude_code(self, background: bool = False, monitor: bool = False, 
                           ipc_bridge: bool = False) -> Dict[str, Any]:
        """Launch claude-code with specified options."""
        import subprocess
        import uuid
        
        request_id = f"claude-{uuid.uuid4().hex[:8]}"
        
        # Check if claude is available
        try:
            version_result = subprocess.run(['claude', '--version'], 
                                          capture_output=True, text=True, timeout=10)
            if version_result.returncode != 0:
                raise RuntimeError("claude not available or not responding")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"claude not found or not responding: {e}")
        
        # Build command
        cmd = ['claude']
        
        # Add flags based on options
        if background:
            cmd.append('--background')
        if monitor:
            cmd.append('--monitor')
        if ipc_bridge:
            cmd.append('--ipc-bridge')
        
        # Launch the process
        try:
            if background:
                # Launch in background
                process = subprocess.Popen(cmd, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         text=True)
                pid = process.pid
                
                return {
                    "request_id": request_id,
                    "target": "claude_code",
                    "success": True,
                    "pid": pid,
                    "background": True,
                    "launched_at": datetime.now().isoformat()
                }
            else:
                # Launch synchronously
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                return {
                    "request_id": request_id,
                    "target": "claude_code",
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "launched_at": datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                "request_id": request_id,
                "target": "claude_code",
                "success": False,
                "error": "claude-code launch timed out",
                "launched_at": datetime.now().isoformat()
            }
    
    def _launch_dev_container(self, **kwargs) -> Dict[str, Any]:
        """Launch development container."""
        # Placeholder implementation
        return {
            "target": "dev_container",
            "success": False,
            "error": "dev_container not implemented yet",
            "launched_at": datetime.now().isoformat()
        }
    
    def _launch_gemini_colab(self, **kwargs) -> Dict[str, Any]:
        """Launch Gemini Colab integration."""
        # Placeholder implementation
        return {
            "target": "gemini_colab",
            "success": False,
            "error": "gemini_colab not implemented yet",
            "launched_at": datetime.now().isoformat()
        }