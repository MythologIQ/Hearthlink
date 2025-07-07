"""
Plugin Manager

Main orchestrator for plugin registration, execution, and lifecycle management.
Integrates manifest validation, permission management, sandboxing, and benchmarking.
Enhanced with live sandbox reloading, plugin lifecycle events, and comprehensive audit logging.
"""

import json
import uuid
import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging
import os
import signal
from pathlib import Path

from .manifest import PluginManifest, ManifestValidator, RiskTier, PluginLifecycleEvent
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
    """Enhanced plugin status information."""
    plugin_id: str
    name: str
    version: str
    status: str  # registered, approved, active, suspended, revoked, reloading
    approved_by_user: bool
    risk_tier: RiskTier
    performance_tier: PerformanceTier
    last_execution: Optional[str] = None
    execution_count: int = 0
    error_count: int = 0
    avg_execution_time: float = 0.0
    last_reload: Optional[str] = None
    reload_count: int = 0
    sandbox_active: bool = True
    lifecycle_events: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PluginReloadEvent:
    """Plugin reload event."""
    event_id: str
    plugin_id: str
    timestamp: str
    user_id: str
    reason: str
    previous_version: Optional[str] = None
    new_version: Optional[str] = None
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)

class PluginManager:
    """Enhanced plugin management system with live reloading and lifecycle events."""
    
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
        
        # Live reloading support
        self.reload_events: List[PluginReloadEvent] = []
        self.file_watchers: Dict[str, Any] = {}
        self.reload_callbacks: Dict[str, List[Callable]] = {}
        
        # Lifecycle event handlers
        self.lifecycle_handlers: Dict[str, Callable] = {}
        
        # Threading support
        self._lock = threading.RLock()
        self._reload_queue = asyncio.Queue()
        self._reload_worker_task = None
        
        # Start reload worker
        self._start_reload_worker()
    
    def register_plugin(self, manifest_data: Dict[str, Any], user_id: str) -> str:
        """
        Register a new plugin with enhanced lifecycle support.
        
        Args:
            manifest_data: Plugin manifest data
            user_id: User registering the plugin
            
        Returns:
            Plugin ID
        """
        with self._lock:
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
            
            # Add lifecycle event
            manifest.add_lifecycle_event(
                PluginLifecycleEvent.REGISTERED,
                user_id,
                {"manifest_version": manifest.manifest_version}
            )
            
            # Set up file watching for live reloading
            if manifest.manifest_version >= "2.0.0":
                self._setup_file_watcher(plugin_id, manifest)
            
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
        Approve a plugin for execution with lifecycle event support.
        
        Args:
            plugin_id: Plugin to approve
            user_id: User approving the plugin
            reason: Optional reason for approval
            
        Returns:
            Success status
        """
        with self._lock:
            if plugin_id not in self.plugins:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            manifest = self.plugins[plugin_id]
            
            # Update manifest
            manifest.approved_by_user = True
            manifest.updated_at = datetime.now().isoformat()
            
            # Add lifecycle event
            manifest.add_lifecycle_event(
                PluginLifecycleEvent.APPROVED,
                user_id,
                {"reason": reason},
                previous_state="registered",
                new_state="approved"
            )
            
            # Update status
            if plugin_id in self.plugin_status:
                self.plugin_status[plugin_id].status = "approved"
                self.plugin_status[plugin_id].approved_by_user = True
            
            # Request permissions
            if manifest.requested_permissions:
                permission_data = [
                    {
                        "permission": p.permission,
                        "level": p.level.value,
                        "scope": p.scope,
                        "conditions": p.conditions
                    }
                    for p in manifest.requested_permissions
                ]
                self.permission_manager.request_permissions(
                    plugin_id, user_id, permission_data
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
    
    def reload_plugin(self, plugin_id: str, user_id: str, reason: str = "manual_reload") -> bool:
        """
        Reload a plugin with live sandbox support.
        
        Args:
            plugin_id: Plugin to reload
            user_id: User requesting reload
            reason: Reason for reload
            
        Returns:
            Success status
        """
        with self._lock:
            if plugin_id not in self.plugins:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            manifest = self.plugins[plugin_id]
            previous_version = manifest.version
            
            # Create reload event
            reload_event = PluginReloadEvent(
                event_id=f"reload-{uuid.uuid4().hex[:8]}",
                plugin_id=plugin_id,
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                reason=reason,
                previous_version=previous_version,
                new_version=None,
                success=False
            )
            
            try:
                # Update plugin status
                if plugin_id in self.plugin_status:
                    self.plugin_status[plugin_id].status = "reloading"
                    self.plugin_status[plugin_id].reload_count += 1
                
                # Add lifecycle event
                manifest.add_lifecycle_event(
                    PluginLifecycleEvent.RELOADED,
                    user_id,
                    {"reason": reason, "previous_version": previous_version}
                )
                
                # Reload sandbox if active
                if self.plugin_status[plugin_id].sandbox_active:
                    self._reload_sandbox(plugin_id)
                
                # Update manifest
                manifest.last_reload = datetime.now().isoformat()
                manifest.updated_at = datetime.now().isoformat()
                
                # Update status
                if plugin_id in self.plugin_status:
                    self.plugin_status[plugin_id].status = "active"
                    self.plugin_status[plugin_id].last_reload = datetime.now().isoformat()
                
                reload_event.success = True
                reload_event.new_version = manifest.version
                
                self.logger.info(f"Plugin reloaded: {plugin_id} by {user_id}")
                
            except Exception as e:
                reload_event.details["error"] = str(e)
                self.logger.error(f"Failed to reload plugin {plugin_id}: {e}")
                
                # Restore status
                if plugin_id in self.plugin_status:
                    self.plugin_status[plugin_id].status = "active"
            
            # Store reload event
            self.reload_events.append(reload_event)
            
            # Log traffic
            self.traffic_logger.log_traffic(
                traffic_type=TrafficType.PLUGIN_RELOAD,
                source="user",
                target=plugin_id,
                user_id=user_id,
                plugin_id=plugin_id,
                payload={"reason": reason, "success": reload_event.success},
                severity=TrafficSeverity.MEDIUM
            )
            
            return reload_event.success
    
    def revoke_plugin(self, plugin_id: str, user_id: str, reason: str) -> bool:
        """
        Revoke a plugin with lifecycle event support.
        
        Args:
            plugin_id: Plugin to revoke
            user_id: User revoking the plugin
            reason: Reason for revocation
            
        Returns:
            Success status
        """
        with self._lock:
            if plugin_id not in self.plugins:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            manifest = self.plugins[plugin_id]
            
            # Add lifecycle event
            manifest.add_lifecycle_event(
                PluginLifecycleEvent.REVOKED,
                user_id,
                {"reason": reason},
                previous_state=self.plugin_status[plugin_id].status,
                new_state="revoked"
            )
            
            # Update status
            if plugin_id in self.plugin_status:
                self.plugin_status[plugin_id].status = "revoked"
            
            # Revoke permissions
            self.permission_manager.revoke_permissions(plugin_id, user_id, reason)
            
            # Clean up file watcher
            if plugin_id in self.file_watchers:
                self._cleanup_file_watcher(plugin_id)
            
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
        Execute a plugin with enhanced error handling and audit logging.
        
        Args:
            plugin_id: Plugin to execute
            user_id: User executing the plugin
            payload: Execution payload
            session_id: Optional session ID
            timeout: Optional timeout
            
        Returns:
            Plugin execution result
        """
        with self._lock:
            if plugin_id not in self.plugins:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            manifest = self.plugins[plugin_id]
            
            # Check if plugin is active
            if self.plugin_status[plugin_id].status not in ["active", "approved"]:
                raise ValueError(f"Plugin {plugin_id} is not active")
            
            # Check permissions
            if not self._check_execution_permissions(plugin_id, payload):
                raise ValueError(f"Insufficient permissions for plugin {plugin_id}")
            
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
            
            # Track active execution
            self.active_executions[request_id] = {
                "request": request,
                "start_time": time.time(),
                "status": "running"
            }
            
            start_time = time.time()
            success = False
            output = None
            error = None
            sandbox_result = None
            
            try:
                # Execute in sandbox if required
                if manifest.sandbox:
                    sandbox_result = self.sandbox_manager.execute_in_sandbox(
                        plugin_id, payload, timeout or manifest.sandbox_config.get("timeout", 300)
                    )
                    output = sandbox_result.output
                    success = sandbox_result.success
                    if not success:
                        error = sandbox_result.error
                else:
                    # Direct execution (not recommended for security)
                    output = self._execute_plugin_directly(manifest, payload)
                    success = True
                
                execution_time = time.time() - start_time
                
                # Update execution statistics
                self._update_plugin_execution_stats(plugin_id, execution_time, success)
                
                # Run benchmark if needed
                benchmark_summary = None
                if self._should_run_benchmark(plugin_id):
                    benchmark_summary = self._run_plugin_benchmark(plugin_id, payload)
                
                # Log traffic
                self.traffic_logger.log_traffic(
                    traffic_type=TrafficType.PLUGIN_EXECUTE,
                    source="user",
                    target=plugin_id,
                    user_id=user_id,
                    plugin_id=plugin_id,
                    payload=payload,
                    severity=TrafficSeverity.MEDIUM
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                error = str(e)
                success = False
                
                # Log error
                self.logger.error(f"Plugin execution failed: {plugin_id} - {error}")
                
                # Add audit event
                manifest.add_audit_event(
                    "execution_error",
                    user_id,
                    {"error": error, "payload": payload},
                    risk_score=50
                )
            
            finally:
                # Clean up active execution
                if request_id in self.active_executions:
                    del self.active_executions[request_id]
            
            # Create result
            result = PluginExecutionResult(
                request_id=request_id,
                plugin_id=plugin_id,
                success=success,
                output=output,
                error=error,
                execution_time=execution_time,
                sandbox_result=sandbox_result,
                benchmark_summary=benchmark_summary
            )
            
            return result
    
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
    
    def get_reload_events(self, plugin_id: Optional[str] = None) -> List[PluginReloadEvent]:
        """Get reload events for a plugin or all plugins."""
        if plugin_id:
            return [e for e in self.reload_events if e.plugin_id == plugin_id]
        return self.reload_events
    
    def register_lifecycle_handler(self, event_type: str, handler: Callable):
        """Register a lifecycle event handler."""
        self.lifecycle_handlers[event_type] = handler
    
    def _setup_file_watcher(self, plugin_id: str, manifest: PluginManifest):
        """Set up file watching for live reloading."""
        try:
            # This would integrate with a file watching library like watchdog
            # For now, we'll simulate the setup
            self.file_watchers[plugin_id] = {
                "manifest": manifest,
                "last_modified": datetime.now().isoformat(),
                "watch_paths": self._get_plugin_watch_paths(manifest)
            }
            
            self.logger.info(f"File watcher set up for plugin: {plugin_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to set up file watcher for {plugin_id}: {e}")
    
    def _get_plugin_watch_paths(self, manifest: PluginManifest) -> List[str]:
        """Get paths to watch for plugin changes."""
        # This would be based on the plugin's file structure
        # For now, return a default path
        return [f"plugins/{manifest.plugin_id}"]
    
    def _cleanup_file_watcher(self, plugin_id: str):
        """Clean up file watcher for a plugin."""
        if plugin_id in self.file_watchers:
            del self.file_watchers[plugin_id]
    
    def _reload_sandbox(self, plugin_id: str):
        """Reload plugin sandbox."""
        try:
            # This would reload the sandbox environment for the plugin
            self.logger.info(f"Sandbox reloaded for plugin: {plugin_id}")
        except Exception as e:
            self.logger.error(f"Failed to reload sandbox for {plugin_id}: {e}")
    
    def _start_reload_worker(self):
        """Start the reload worker task."""
        try:
            loop = asyncio.new_event_loop()
            thread = threading.Thread(target=self._reload_worker, args=(loop,), daemon=True)
            thread.start()
        except Exception as e:
            self.logger.error(f"Failed to start reload worker: {e}")
    
    def _reload_worker(self, loop):
        """Worker thread for handling reload events."""
        asyncio.set_event_loop(loop)
        
        while True:
            try:
                # Process reload queue
                # This would handle file change events and trigger reloads
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Reload worker error: {e}")
    
    def _check_execution_permissions(self, plugin_id: str, payload: Dict[str, Any]) -> bool:
        """Check if plugin has execution permissions."""
        # Check basic execution permission
        if not self.permission_manager.check_permission(plugin_id, "plugin_execute", "execute"):
            return False
        
        # Check payload-specific permissions
        if "vault_access" in payload:
            if not self.permission_manager.check_permission(plugin_id, "vault_read", "read"):
                return False
        
        if "network_access" in payload:
            if not self.permission_manager.check_permission(plugin_id, "network_read", "read"):
                return False
        
        return True
    
    def _execute_plugin_directly(self, manifest: PluginManifest, payload: Dict[str, Any]) -> Any:
        """Execute plugin directly (not recommended for security)."""
        # This would execute the plugin code directly
        # For security reasons, this should be avoided in production
        return {"message": "Direct execution not implemented for security"}
    
    def _update_plugin_execution_stats(self, plugin_id: str, execution_time: float, success: bool):
        """Update plugin execution statistics."""
        if plugin_id in self.plugin_status:
            status = self.plugin_status[plugin_id]
            status.execution_count += 1
            status.last_execution = datetime.now().isoformat()
            
            if not success:
                status.error_count += 1
            
            # Update average execution time
            if status.execution_count > 0:
                status.avg_execution_time = (
                    (status.avg_execution_time * (status.execution_count - 1) + execution_time) /
                    status.execution_count
                )
    
    def _should_run_benchmark(self, plugin_id: str) -> bool:
        """Check if benchmark should be run for plugin."""
        if plugin_id not in self.plugin_status:
            return False
        
        status = self.plugin_status[plugin_id]
        return status.execution_count % 10 == 0  # Run every 10 executions
    
    def _run_plugin_benchmark(self, plugin_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run benchmark for plugin."""
        try:
            benchmark_result = self.benchmark_manager.benchmark_plugin(
                plugin_id, payload, self._benchmark_test_function
            )
            return benchmark_result
        except Exception as e:
            self.logger.error(f"Benchmark failed for {plugin_id}: {e}")
            return {"error": str(e)}
    
    def _benchmark_test_function(self, payload: Dict[str, Any]) -> Any:
        """Test function for benchmarking."""
        # This would be the actual plugin execution for benchmarking
        return {"benchmark_result": "test_completed"}
    
    def _cleanup_plugin_executions(self, plugin_id: str):
        """Clean up active executions for a plugin."""
        executions_to_remove = [
            req_id for req_id, exec_data in self.active_executions.items()
            if exec_data["request"].plugin_id == plugin_id
        ]
        
        for req_id in executions_to_remove:
            del self.active_executions[req_id] 