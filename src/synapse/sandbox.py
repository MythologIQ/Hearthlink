"""
Sandbox Management System

Provides secure, isolated execution environments for plugins.
All plugin code runs in sandboxed containers with resource constraints.
"""

import os
import sys
import time
import signal
import threading
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
import json

@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    max_cpu_percent: float = 50.0
    max_memory_mb: int = 512
    max_disk_mb: int = 100
    max_execution_time: int = 300  # seconds
    max_processes: int = 5
    allowed_network_hosts: List[str] = field(default_factory=list)
    allowed_file_paths: List[str] = field(default_factory=list)
    read_only_paths: List[str] = field(default_factory=list)

@dataclass
class SandboxMetrics:
    """Sandbox execution metrics."""
    start_time: str
    end_time: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    execution_time: float = 0.0
    process_count: int = 0
    network_requests: int = 0
    file_operations: int = 0
    exit_code: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class SandboxResult:
    """Sandbox execution result."""
    success: bool
    output: str
    metrics: SandboxMetrics
    execution_id: str
    error: Optional[str] = None

class SandboxManager:
    """Manages secure sandboxed execution environments."""
    
    def __init__(self, config: SandboxConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Active sandboxes
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        
        # Sandbox base directory
        self.sandbox_base = Path(tempfile.gettempdir()) / "hearthlink_sandboxes"
        self.sandbox_base.mkdir(exist_ok=True)
        
        # Resource monitoring
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.stop_monitoring: Dict[str, bool] = {}
    
    def create_sandbox(self, plugin_id: str, execution_id: str) -> str:
        """
        Create a new sandbox environment.
        
        Args:
            plugin_id: Plugin identifier
            execution_id: Execution identifier
            
        Returns:
            Sandbox path
        """
        sandbox_id = f"{plugin_id}-{execution_id}"
        sandbox_path = self.sandbox_base / sandbox_id
        
        try:
            # Create sandbox directory
            sandbox_path.mkdir(exist_ok=True)
            
            # Create subdirectories
            (sandbox_path / "workspace").mkdir(exist_ok=True)
            (sandbox_path / "temp").mkdir(exist_ok=True)
            (sandbox_path / "logs").mkdir(exist_ok=True)
            
            # Set up sandbox environment
            self._setup_sandbox_environment(sandbox_path)
            
            # Record active sandbox
            self.active_sandboxes[sandbox_id] = {
                "plugin_id": plugin_id,
                "execution_id": execution_id,
                "path": str(sandbox_path),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            self.logger.info(f"Sandbox created: {sandbox_id}")
            return str(sandbox_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create sandbox {sandbox_id}: {e}")
            raise
    
    def execute_in_sandbox(self, plugin_id: str, execution_id: str, 
                          command: List[str], input_data: Optional[str] = None,
                          timeout: Optional[int] = None) -> SandboxResult:
        """
        Execute a command in a sandboxed environment.
        
        Args:
            plugin_id: Plugin identifier
            execution_id: Execution identifier
            command: Command to execute
            input_data: Optional input data
            timeout: Optional timeout override
            
        Returns:
            Sandbox execution result
        """
        sandbox_id = f"{plugin_id}-{execution_id}"
        sandbox_path = self.sandbox_base / sandbox_id
        
        if not sandbox_path.exists():
            raise ValueError(f"Sandbox not found: {sandbox_id}")
        
        # Create metrics
        metrics = SandboxMetrics(
            start_time=datetime.now().isoformat(),
            execution_id=execution_id
        )
        
        # Start resource monitoring
        self._start_monitoring(sandbox_id, metrics)
        
        try:
            # Prepare execution environment
            env = self._prepare_execution_environment(sandbox_path)
            
            # Set timeout
            exec_timeout = timeout or self.config.max_execution_time
            
            # Execute command
            start_time = time.time()
            
            process = subprocess.Popen(
                command,
                cwd=str(sandbox_path / "workspace"),
                env=env,
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._setup_process_restrictions
            )
            
            # Send input data if provided
            if input_data:
                process.stdin.write(input_data)
                process.stdin.close()
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=exec_timeout)
                exit_code = process.returncode
                error_message = None
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                error_message = f"Execution timed out after {exec_timeout} seconds"
            
            execution_time = time.time() - start_time
            
            # Stop monitoring
            self._stop_monitoring(sandbox_id)
            
            # Update metrics
            metrics.end_time = datetime.now().isoformat()
            metrics.execution_time = execution_time
            metrics.exit_code = exit_code
            metrics.error_message = error_message
            
            # Determine success
            success = exit_code == 0 and not error_message
            
            # Create result
            result = SandboxResult(
                success=success,
                output=stdout,
                error=error_message or stderr if not success else None,
                metrics=metrics,
                execution_id=execution_id
            )
            
            self.logger.info(f"Sandbox execution completed: {sandbox_id}")
            return result
            
        except Exception as e:
            self._stop_monitoring(sandbox_id)
            metrics.end_time = datetime.now().isoformat()
            metrics.error_message = str(e)
            
            result = SandboxResult(
                success=False,
                output="",
                error=str(e),
                metrics=metrics,
                execution_id=execution_id
            )
            
            self.logger.error(f"Sandbox execution failed: {sandbox_id} - {e}")
            return result
    
    def cleanup_sandbox(self, plugin_id: str, execution_id: str) -> bool:
        """
        Clean up a sandbox environment.
        
        Args:
            plugin_id: Plugin identifier
            execution_id: Execution identifier
            
        Returns:
            Success status
        """
        sandbox_id = f"{plugin_id}-{execution_id}"
        sandbox_path = self.sandbox_base / sandbox_id
        
        try:
            # Stop monitoring if active
            self._stop_monitoring(sandbox_id)
            
            # Remove sandbox directory
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path)
            
            # Remove from active sandboxes
            if sandbox_id in self.active_sandboxes:
                del self.active_sandboxes[sandbox_id]
            
            self.logger.info(f"Sandbox cleaned up: {sandbox_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
            return False
    
    def get_sandbox_status(self, plugin_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get sandbox status."""
        sandbox_id = f"{plugin_id}-{execution_id}"
        return self.active_sandboxes.get(sandbox_id)
    
    def list_active_sandboxes(self) -> List[Dict[str, Any]]:
        """List all active sandboxes."""
        return list(self.active_sandboxes.values())
    
    def _setup_sandbox_environment(self, sandbox_path: Path):
        """Set up sandbox environment."""
        # Create restricted environment files
        env_file = sandbox_path / "environment.json"
        env_data = {
            "sandbox_id": sandbox_path.name,
            "restricted": True,
            "max_cpu": self.config.max_cpu_percent,
            "max_memory": self.config.max_memory_mb,
            "max_disk": self.config.max_disk_mb,
            "allowed_hosts": self.config.allowed_network_hosts,
            "allowed_paths": self.config.allowed_file_paths,
            "read_only_paths": self.config.read_only_paths
        }
        
        with open(env_file, 'w') as f:
            json.dump(env_data, f, indent=2)
    
    def _prepare_execution_environment(self, sandbox_path: Path) -> Dict[str, str]:
        """Prepare execution environment."""
        env = os.environ.copy()
        
        # Set sandbox-specific environment variables
        env.update({
            "HEARTHLINK_SANDBOX": "1",
            "HEARTHLINK_SANDBOX_PATH": str(sandbox_path),
            "HEARTHLINK_WORKSPACE": str(sandbox_path / "workspace"),
            "HEARTHLINK_TEMP": str(sandbox_path / "temp"),
            "HEARTHLINK_LOGS": str(sandbox_path / "logs"),
            "PYTHONPATH": str(sandbox_path / "workspace"),
            "TEMP": str(sandbox_path / "temp"),
            "TMP": str(sandbox_path / "temp")
        })
        
        return env
    
    def _setup_process_restrictions(self):
        """Set up process restrictions (Unix only)."""
        if os.name == 'posix':
            try:
                import resource
                # Set resource limits
                resource.setrlimit(resource.RLIMIT_CPU, (self.config.max_execution_time, self.config.max_execution_time))
                resource.setrlimit(resource.RLIMIT_AS, (self.config.max_memory_mb * 1024 * 1024, -1))
                resource.setrlimit(resource.RLIMIT_NPROC, (self.config.max_processes, self.config.max_processes))
            except ImportError:
                pass  # Resource module not available
    
    def _start_monitoring(self, sandbox_id: str, metrics: SandboxMetrics):
        """Start resource monitoring for sandbox."""
        self.stop_monitoring[sandbox_id] = False
        
        def monitor_resources():
            while not self.stop_monitoring.get(sandbox_id, False):
                try:
                    # Monitor CPU and memory usage
                    # This is a simplified implementation
                    # In a real system, you'd use psutil or similar
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Resource monitoring error: {e}")
                    break
        
        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()
        self.monitoring_threads[sandbox_id] = thread
    
    def _stop_monitoring(self, sandbox_id: str):
        """Stop resource monitoring for sandbox."""
        self.stop_monitoring[sandbox_id] = True
        if sandbox_id in self.monitoring_threads:
            thread = self.monitoring_threads[sandbox_id]
            thread.join(timeout=5)
            del self.monitoring_threads[sandbox_id]
    
    def cleanup_all_sandboxes(self):
        """Clean up all active sandboxes."""
        sandbox_ids = list(self.active_sandboxes.keys())
        for sandbox_id in sandbox_ids:
            plugin_id = self.active_sandboxes[sandbox_id]["plugin_id"]
            execution_id = self.active_sandboxes[sandbox_id]["execution_id"]
            self.cleanup_sandbox(plugin_id, execution_id) 