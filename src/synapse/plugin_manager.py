"""
Plugin Manager

Main orchestrator for plugin registration, execution, and lifecycle management.
Integrates manifest validation, permission management, sandboxing, and benchmarking.
"""

import json
import uuid
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

from .manifest import PluginManifest, ManifestValidator, RiskTier
from .permissions import PermissionManager, PermissionStatus
from .sandbox import SandboxManager, SandboxConfig, SandboxResult
from .benchmark import BenchmarkManager, BenchmarkConfig, PerformanceTier
from .traffic_logger import TrafficLogger, TrafficType, TrafficSeverity

@dataclass
class PluginExecutionRequest:
    """Plugin execution request."""
    request_id: str
    plugin_id: str
    user_id: str
    payload: Dict[str, Any]
    session_id: Optional[str] = None
    timeout: Optional[int] = None
    priority: str = "normal"

@dataclass
class PluginExecutionResult:
    """Plugin execution result."""
    request_id: str
    plugin_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float
    sandbox_result: Optional[SandboxResult] = None
    benchmark_summary: Optional[Dict[str, Any]] = None

@dataclass
class PluginStatus:
    """Plugin status information."""
    plugin_id: str
    name: str
    version: str
    status: str  # registered, approved, active, suspended, revoked
    approved_by_user: bool
    risk_tier: RiskTier
    performance_tier: PerformanceTier
    last_execution: Optional[str] = None
    execution_count: int = 0
    error_count: int = 0
    avg_execution_time: float = 0.0

class PluginManager:
    """Main plugin management system."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize subsystems
        self.manifest_validator = ManifestValidator(self.logger)
        self.permission_manager = PermissionManager(self.logger)
        
        # Initialize sandbox manager
        sandbox_config = SandboxConfig(
            max_cpu_percent=config.get("sandbox", {}).get("max_cpu_percent", 50.0),
            max_memory_mb=config.get("sandbox", {}).get("max_memory_mb", 512),
            max_disk_mb=config.get("sandbox", {}).get("max_disk_mb", 100),
            max_execution_time=config.get("sandbox", {}).get("max_execution_time", 300)
        )
        self.sandbox_manager = SandboxManager(sandbox_config, self.logger)
        
        # Initialize benchmark manager
        benchmark_config = BenchmarkConfig(
            test_duration=config.get("benchmark", {}).get("test_duration", 30),
            response_time_threshold=config.get("benchmark", {}).get("response_time_threshold", 1000.0)
        )
        self.benchmark_manager = BenchmarkManager(benchmark_config, self.logger)
        
        # Initialize traffic logger
        self.traffic_logger = TrafficLogger(
            max_entries=config.get("traffic", {}).get("max_entries", 10000),
            retention_days=config.get("traffic", {}).get("retention_days", 30),
            logger=self.logger
        )
        
        # Plugin registry
        self.plugins: Dict[str, PluginManifest] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        
        # Active executions
        self.active_executions: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, manifest_data: Dict[str, Any], user_id: str) -> str:
        """
        Register a new plugin.
        
        Args:
            manifest_data: Plugin manifest data
            user_id: User registering the plugin
            
        Returns:
            Plugin ID
        """
        # Validate manifest
        manifest = self.manifest_validator.create_manifest(manifest_data)
        if not manifest:
            raise ValueError("Invalid plugin manifest")
        
        plugin_id = manifest.plugin_id
        
        # Check if plugin already exists
        if plugin_id in self.plugins:
            raise ValueError(f"Plugin {plugin_id} already registered")
        
        # Store plugin
        self.plugins[plugin_id] = manifest
        
        # Create plugin status
        status = PluginStatus(
            plugin_id=plugin_id,
            name=manifest.name,
            version=manifest.version,
            status="registered",
            approved_by_user=False,
            risk_tier=manifest.risk_tier,
            performance_tier=PerformanceTier.UNSTABLE
        )
        self.plugin_status[plugin_id] = status
        
        # Log traffic
        self.traffic_logger.log_traffic(
            traffic_type=TrafficType.PLUGIN_REGISTER,
            source="user",
            target=plugin_id,
            user_id=user_id,
            plugin_id=plugin_id,
            payload=manifest_data,
            severity=TrafficSeverity.LOW
        )
        
        self.logger.info(f"Plugin registered: {plugin_id} by {user_id}")
        return plugin_id
    
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
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        manifest = self.plugins[plugin_id]
        
        # Update manifest
        manifest.approved_by_user = True
        manifest.updated_at = datetime.now().isoformat()
        
        # Add audit event
        audit_event = {
            "event_id": f"audit-{uuid.uuid4().hex[:8]}",
            "event_type": "plugin_approved",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "plugin_id": plugin_id,
            "details": {"reason": reason},
            "risk_score": None,
            "resolution": "approved"
        }
        manifest.audit_log.append(audit_event)
        
        # Update status
        if plugin_id in self.plugin_status:
            self.plugin_status[plugin_id].status = "approved"
            self.plugin_status[plugin_id].approved_by_user = True
        
        # Request permissions
        if manifest.requested_permissions:
            self.permission_manager.request_permissions(
                plugin_id, user_id, manifest.requested_permissions
            )
        
        # Log traffic
        self.traffic_logger.log_traffic(
            traffic_type=TrafficType.PLUGIN_APPROVE,
            source="user",
            target=plugin_id,
            user_id=user_id,
            plugin_id=plugin_id,
            payload={"reason": reason},
            severity=TrafficSeverity.MEDIUM
        )
        
        self.logger.info(f"Plugin approved: {plugin_id} by {user_id}")
        return True
    
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
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        manifest = self.plugins[plugin_id]
        
        # Update manifest
        manifest.approved_by_user = False
        manifest.updated_at = datetime.now().isoformat()
        
        # Add audit event
        audit_event = {
            "event_id": f"audit-{uuid.uuid4().hex[:8]}",
            "event_type": "plugin_revoked",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "plugin_id": plugin_id,
            "details": {"reason": reason},
            "risk_score": None,
            "resolution": "revoked"
        }
        manifest.audit_log.append(audit_event)
        
        # Update status
        if plugin_id in self.plugin_status:
            self.plugin_status[plugin_id].status = "revoked"
            self.plugin_status[plugin_id].approved_by_user = False
        
        # Revoke permissions
        self.permission_manager.revoke_permissions(plugin_id, user_id, reason)
        
        # Clean up active executions
        self._cleanup_plugin_executions(plugin_id)
        
        # Log traffic
        self.traffic_logger.log_traffic(
            traffic_type=TrafficType.PLUGIN_REVOKE,
            source="user",
            target=plugin_id,
            user_id=user_id,
            plugin_id=plugin_id,
            payload={"reason": reason},
            severity=TrafficSeverity.HIGH
        )
        
        self.logger.info(f"Plugin revoked: {plugin_id} by {user_id}")
        return True
    
    def execute_plugin(self, plugin_id: str, user_id: str, payload: Dict[str, Any],
                      session_id: Optional[str] = None, timeout: Optional[int] = None) -> PluginExecutionResult:
        """
        Execute a plugin.
        
        Args:
            plugin_id: Plugin to execute
            user_id: User executing the plugin
            payload: Execution payload
            session_id: Optional session ID
            timeout: Optional timeout override
            
        Returns:
            Execution result
        """
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        manifest = self.plugins[plugin_id]
        
        # Check if plugin is approved
        if not manifest.approved_by_user:
            raise ValueError(f"Plugin {plugin_id} is not approved")
        
        # Check permissions
        if not self._check_execution_permissions(plugin_id, payload):
            raise ValueError(f"Plugin {plugin_id} lacks required permissions")
        
        # Create execution request
        request_id = f"exec-{uuid.uuid4().hex[:8]}"
        request = PluginExecutionRequest(
            request_id=request_id,
            plugin_id=plugin_id,
            user_id=user_id,
            payload=payload,
            session_id=session_id,
            timeout=timeout
        )
        
        # Record active execution
        self.active_executions[request_id] = {
            "request": request,
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
        
        # Log execution start
        self.traffic_logger.log_traffic(
            traffic_type=TrafficType.PLUGIN_EXECUTE,
            source="user",
            target=plugin_id,
            user_id=user_id,
            plugin_id=plugin_id,
            session_id=session_id,
            request_id=request_id,
            payload=payload,
            severity=TrafficSeverity.MEDIUM
        )
        
        start_time = time.time()
        sandbox_result = None
        error = None
        
        try:
            # Create sandbox
            sandbox_path = self.sandbox_manager.create_sandbox(plugin_id, request_id)
            
            # Execute in sandbox
            command = self._build_execution_command(manifest, payload)
            sandbox_result = self.sandbox_manager.execute_in_sandbox(
                plugin_id, request_id, command, 
                input_data=json.dumps(payload),
                timeout=timeout
            )
            
            # Process result
            if sandbox_result.success:
                output = self._parse_plugin_output(sandbox_result.output)
            else:
                output = None
                error = sandbox_result.error
            
            execution_time = time.time() - start_time
            
            # Update plugin status
            self._update_plugin_execution_stats(plugin_id, execution_time, error is None)
            
            # Run benchmark if needed
            benchmark_summary = None
            if self._should_run_benchmark(plugin_id):
                benchmark_summary = self.benchmark_manager.run_benchmark(
                    plugin_id, self._benchmark_test_function, {"payload": payload}
                )
            
            # Create result
            result = PluginExecutionResult(
                request_id=request_id,
                plugin_id=plugin_id,
                success=error is None,
                output=output,
                error=error,
                execution_time=execution_time,
                sandbox_result=sandbox_result,
                benchmark_summary=asdict(benchmark_summary) if benchmark_summary else None
            )
            
            # Log execution completion
            self.traffic_logger.log_traffic(
                traffic_type=TrafficType.PLUGIN_EXECUTE,
                source=plugin_id,
                target="user",
                user_id=user_id,
                plugin_id=plugin_id,
                session_id=session_id,
                request_id=request_id,
                response={"success": result.success, "execution_time": execution_time},
                duration=execution_time,
                status="success" if error is None else "error",
                error_message=error,
                severity=TrafficSeverity.MEDIUM
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error = str(e)
            
            # Log execution error
            self.traffic_logger.log_traffic(
                traffic_type=TrafficType.PLUGIN_EXECUTE,
                source=plugin_id,
                target="user",
                user_id=user_id,
                plugin_id=plugin_id,
                session_id=session_id,
                request_id=request_id,
                duration=execution_time,
                status="error",
                error_message=error,
                severity=TrafficSeverity.HIGH
            )
            
            # Update plugin status
            self._update_plugin_execution_stats(plugin_id, execution_time, False)
            
            return PluginExecutionResult(
                request_id=request_id,
                plugin_id=plugin_id,
                success=False,
                output=None,
                error=error,
                execution_time=execution_time
            )
        
        finally:
            # Clean up
            if request_id in self.active_executions:
                del self.active_executions[request_id]
            
            # Clean up sandbox
            if sandbox_result:
                self.sandbox_manager.cleanup_sandbox(plugin_id, request_id)
    
    def get_plugin_status(self, plugin_id: str) -> Optional[PluginStatus]:
        """Get plugin status."""
        return self.plugin_status.get(plugin_id)
    
    def list_plugins(self, status_filter: Optional[str] = None) -> List[PluginStatus]:
        """List plugins with optional status filter."""
        plugins = list(self.plugin_status.values())
        
        if status_filter:
            plugins = [p for p in plugins if p.status == status_filter]
        
        return plugins
    
    def get_plugin_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest."""
        return self.plugins.get(plugin_id)
    
    def export_plugin_data(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Export plugin data."""
        if plugin_id not in self.plugins:
            return None
        
        manifest = self.plugins[plugin_id]
        status = self.plugin_status.get(plugin_id)
        
        return {
            "manifest": manifest.to_dict(),
            "status": asdict(status) if status else None,
            "permissions": self.permission_manager.get_plugin_permissions(plugin_id),
            "benchmark_summary": self.benchmark_manager.get_benchmark_summary(plugin_id),
            "traffic_summary": self.traffic_logger.get_traffic_summary(24),
            "exported_at": datetime.now().isoformat()
        }
    
    def _check_execution_permissions(self, plugin_id: str, payload: Dict[str, Any]) -> bool:
        """Check if plugin has required permissions for execution."""
        # This is a simplified implementation
        # In a real system, you'd analyze the payload and check specific permissions
        return True
    
    def _build_execution_command(self, manifest: PluginManifest, payload: Dict[str, Any]) -> List[str]:
        """Build execution command for plugin."""
        # This is a simplified implementation
        # In a real system, you'd build the actual command based on the plugin type
        return ["python", "-c", "print('Plugin execution')"]
    
    def _parse_plugin_output(self, output: str) -> Any:
        """Parse plugin output."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output
    
    def _update_plugin_execution_stats(self, plugin_id: str, execution_time: float, success: bool):
        """Update plugin execution statistics."""
        if plugin_id not in self.plugin_status:
            return
        
        status = self.plugin_status[plugin_id]
        status.last_execution = datetime.now().isoformat()
        status.execution_count += 1
        
        if not success:
            status.error_count += 1
        
        # Update average execution time
        if status.execution_count == 1:
            status.avg_execution_time = execution_time
        else:
            status.avg_execution_time = (
                (status.avg_execution_time * (status.execution_count - 1) + execution_time) 
                / status.execution_count
            )
    
    def _should_run_benchmark(self, plugin_id: str) -> bool:
        """Determine if benchmark should be run."""
        # Run benchmark every 10 executions
        status = self.plugin_status.get(plugin_id)
        if not status:
            return False
        
        return status.execution_count % 10 == 0
    
    def _benchmark_test_function(self, payload: Dict[str, Any]) -> Any:
        """Test function for benchmarking."""
        # This would be the actual plugin execution for benchmarking
        time.sleep(0.1)  # Simulate work
        return {"result": "benchmark_test"}
    
    def _cleanup_plugin_executions(self, plugin_id: str):
        """Clean up active executions for a plugin."""
        executions_to_remove = []
        
        for request_id, execution in self.active_executions.items():
            if execution["request"].plugin_id == plugin_id:
                executions_to_remove.append(request_id)
        
        for request_id in executions_to_remove:
            del self.active_executions[request_id] 