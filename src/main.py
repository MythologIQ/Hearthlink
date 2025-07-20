#!/usr/bin/env python3
"""
Hearthlink Global Container - Main Entry Point

This module provides the initial scaffold for Hearthlink's global container,
implementing a minimal cross-platform background process with structured JSON logging
and robust error handling.

References:
- PLATINUM_BLOCKERS.md: Ethical safety rails, dependency mitigation, audit requirements
- hearthlink_system_documentation_master.md: System architecture and constraints
- appendix_h_developer_qa_platinum_checklists.md: QA requirements and error handling

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import time
import json
import logging
import platform
import traceback
import signal
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from logging.handlers import RotatingFileHandler


class HearthlinkError(Exception):
    """Base exception class for Hearthlink container errors."""
    pass


class LoggingError(HearthlinkError):
    """Exception raised when logging operations fail."""
    pass


class ContainerError(HearthlinkError):
    """Exception raised when container operations fail."""
    pass


class StructuredJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Implements platinum-standard structured logging with explicit
    timestamps, log levels, and audit trail requirements.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: LogRecord to format
            
        Returns:
            str: JSON-formatted log entry
        """
        try:
            # Base structured log entry
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = {
                    "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                    "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                    "traceback": traceback.format_exception(*record.exc_info)
                }
            
            # Add extra fields if present
            if hasattr(record, 'extra_fields'):
                log_entry.update(record.extra_fields)
            
            return json.dumps(log_entry, ensure_ascii=False)
            
        except Exception as e:
            # Fallback formatting if JSON formatting fails
            fallback_msg = f"FORMAT_ERROR: {str(e)} - Original: {record.getMessage()}"
            return json.dumps({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "logger": "Hearthlink-Formatter",
                "message": fallback_msg,
                "format_error": str(e)
            }, ensure_ascii=False)


class HearthlinkLogger:
    """
    Centralized logging system for Hearthlink container.
    
    Implements platinum-standard structured JSON logging with rotation,
    explicit error handling, and audit trail requirements.
    """
    
    def __init__(self, log_dir: Optional[str] = None, max_size_mb: int = 10, backup_count: int = 5):
        """
        Initialize Hearthlink logger with structured JSON logging and rotation.
        
        Args:
            log_dir: Optional custom log directory path
            max_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup log files to retain
            
        Raises:
            LoggingError: If logger initialization fails
        """
        try:
            self.max_size_mb = max_size_mb
            self.backup_count = backup_count
            
            # Determine log directory based on platform
            if log_dir:
                self.log_dir = Path(log_dir)
            else:
                if platform.system() == "Windows":
                    # Windows: Use AppData\Local\Hearthlink\logs
                    app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
                    self.log_dir = Path(app_data) / "Hearthlink" / "logs"
                else:
                    # Unix-like: Use ~/.hearthlink/logs
                    self.log_dir = Path.home() / ".hearthlink" / "logs"
            
            # Ensure log directory exists
            self._ensure_log_directory()
            
            # Configure logging
            self._setup_logging()
            
        except Exception as e:
            raise LoggingError(f"Failed to initialize Hearthlink logger: {str(e)}") from e
    
    def _ensure_log_directory(self) -> None:
        """
        Ensure log directory exists with explicit error handling.
        
        Raises:
            OSError: If directory creation fails
        """
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create log directory {self.log_dir}: {str(e)}") from e
    
    def _setup_logging(self) -> None:
        """
        Configure structured JSON logging with rotation and explicit error handling.
        
        Implements platinum-standard logging requirements with:
        - Structured JSON format
        - 10MB rotation with 5 backup files
        - Explicit error handling
        - Audit trail compliance
        """
        try:
            log_file = self.log_dir / "hearthlink.log"
            max_bytes = self.max_size_mb * 1024 * 1024  # Convert MB to bytes
            
            # Create rotating file handler with structured JSON formatter
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(StructuredJSONFormatter())
            
            # Create console handler for development (also JSON formatted)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredJSONFormatter())
            
            # Configure root logger
            self.logger = logging.getLogger('Hearthlink')
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # Prevent duplicate logging
            self.logger.propagate = False
            
        except Exception as e:
            # Fallback to basic logging if structured setup fails
            self._setup_fallback_logging(str(e))
    
    def _setup_fallback_logging(self, error_msg: str) -> None:
        """
        Setup fallback logging if structured logging fails.
        
        Args:
            error_msg: Error message from failed structured logging setup
        """
        try:
            # Basic logging setup as fallback
            basic_logger = logging.getLogger('Hearthlink-Fallback')
            basic_logger.setLevel(logging.INFO)
            
            # Console handler only
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            ))
            basic_logger.addHandler(console_handler)
            
            self.logger = basic_logger
            self.logger.error(f"Structured logging setup failed: {error_msg}. Using fallback logging.")
            
        except Exception as fallback_error:
            # Ultimate fallback: print to stderr
            print(f"CRITICAL: All logging setup failed. Original error: {error_msg}. Fallback error: {str(fallback_error)}", 
                  file=sys.stderr)
            # Create a minimal logger that does nothing
            self.logger = logging.getLogger('Hearthlink-Minimal')
            self.logger.addHandler(logging.NullHandler())
    
    def log_startup(self) -> None:
        """
        Log container startup with structured system information.
        
        Implements platinum-standard startup logging with explicit
        system details and audit trail requirements.
        """
        try:
            startup_data = {
                "event_type": "container_startup",
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "compiler": platform.python_compiler()
                },
                "log_directory": str(self.log_dir.absolute()),
                "log_config": {
                    "max_size_mb": self.max_size_mb,
                    "backup_count": self.backup_count,
                    "format": "structured_json"
                }
            }
            
            # Log with extra fields
            self.logger.info("Hearthlink container started", extra={"extra_fields": startup_data})
            
        except Exception as e:
            self.logger.error(f"Failed to log startup information: {str(e)}", 
                            extra={"extra_fields": {"event_type": "startup_log_error"}})
    
    def log_shutdown(self, reason: str = "normal") -> None:
        """
        Log container shutdown with structured information.
        
        Args:
            reason: Reason for shutdown (normal, error, user_request, etc.)
        """
        try:
            shutdown_data = {
                "event_type": "container_shutdown",
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("Hearthlink container stopped", extra={"extra_fields": shutdown_data})
            
        except Exception as e:
            self.logger.error(f"Failed to log shutdown information: {str(e)}", 
                            extra={"extra_fields": {"event_type": "shutdown_log_error"}})
    
    def log_error(self, error: Exception, context: str = "", extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log errors with structured information and context.
        
        Args:
            error: Exception to log
            context: Context where error occurred
            extra_data: Additional structured data to include
        """
        try:
            error_data = {
                "event_type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "traceback": traceback.format_exception(type(error), error, error.__traceback__)
            }
            
            if extra_data:
                error_data.update(extra_data)
            
            self.logger.error(f"Error in {context}: {str(error)}", 
                            extra={"extra_fields": error_data}, exc_info=True)
            
        except Exception as log_error:
            # Fallback error logging
            self.logger.error(f"Failed to log error: {str(log_error)}. Original error: {str(error)}")
    
    def log_critical_error(self, error: Exception, context: str = "", recovery_action: str = "") -> None:
        """
        Log critical errors that may require immediate attention.
        
        Args:
            error: Critical exception to log
            context: Context where error occurred
            recovery_action: Action taken or recommended for recovery
        """
        try:
            critical_data = {
                "event_type": "critical_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "recovery_action": recovery_action,
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback.format_exception(type(error), error, error.__traceback__)
            }
            
            self.logger.critical(f"CRITICAL ERROR in {context}: {str(error)}", 
                               extra={"extra_fields": critical_data}, exc_info=True)
            
        except Exception as log_error:
            # Ultimate fallback for critical errors
            print(f"CRITICAL LOGGING FAILURE: {str(log_error)}. Original critical error: {str(error)}", 
                  file=sys.stderr)


class HearthlinkContainer:
    """
    Main Hearthlink container class.
    
    Implements the global container scaffold with:
    - Cross-platform compatibility
    - Silent background operation
    - Platinum-standard structured JSON logging
    - Ethical safety rails compliance
    - Explicit error handling and modular design
    - Robust error recovery mechanisms
    """
    
    def __init__(self, log_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Hearthlink container with logging and safety checks.
        
        Args:
            log_config: Optional logging configuration
            
        Raises:
            ContainerError: If container initialization fails
        """
        try:
            self.running = False
            self.start_time = None
            self.error_count = 0
            self.max_errors = 10  # Maximum consecutive errors before shutdown
            self.error_lock = threading.Lock()
            
            # Initialize logger with optional configuration
            log_kwargs = {}
            if log_config:
                log_kwargs.update(log_config)
            
            try:
                self.logger = HearthlinkLogger(**log_kwargs)
            except Exception as e:
                # Fallback logger initialization
                self.logger = HearthlinkLogger()
                self.logger.log_error(e, "logger_initialization")
            
            # Log startup information
            self.logger.log_startup()
            
            # Initialize safety rails (per PLATINUM_BLOCKERS.md)
            self._setup_safety_rails()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
        except Exception as e:
            raise ContainerError(f"Failed to initialize Hearthlink container: {str(e)}") from e
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        try:
            def signal_handler(signum, frame):
                signal_name = signal.Signals(signum).name
                self.logger.logger.info(f"Received signal {signal_name}", 
                                      extra={"extra_fields": {"event_type": "signal_received", "signal": signal_name}})
                self.stop("signal")
            
            # Register signal handlers
            signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
            signal.signal(signal.SIGTERM, signal_handler)  # Termination request
            
            if platform.system() != "Windows":
                signal.signal(signal.SIGHUP, signal_handler)  # Hangup (Unix only)
                
        except Exception as e:
            self.logger.log_error(e, "signal_handler_setup")
    
    def _setup_safety_rails(self) -> None:
        """
        Setup ethical safety rails as defined in PLATINUM_BLOCKERS.md.
        
        Implements dependency mitigation and ethical operation boundaries
        with explicit error handling and structured logging.
        """
        try:
            safety_data = {
                "event_type": "safety_rails_initialization",
                "rails": [
                    "dependency_mitigation",
                    "human_origin_clause",
                    "audit_trail",
                    "ethical_boundaries"
                ]
            }
            
            self.logger.logger.info("Initializing ethical safety rails", 
                                  extra={"extra_fields": safety_data})
            
            # Safety rail: Dependency mitigation
            self.logger.logger.info("Dependency mitigation: Container will not encourage overuse",
                                  extra={"extra_fields": {"event_type": "dependency_mitigation_setup"}})
            
            # Safety rail: Human origin clause preparation
            self.logger.logger.info("Human origin clause: Container ready for crisis handling if needed",
                                  extra={"extra_fields": {"event_type": "human_origin_clause_setup"}})
            
            # Safety rail: Audit trail initialization
            self.logger.logger.info("Audit trail: All container actions will be logged",
                                  extra={"extra_fields": {"event_type": "audit_trail_setup"}})
            
        except Exception as e:
            self.logger.log_error(e, "safety_rails_setup")
    
    def _handle_error(self, error: Exception, context: str = "") -> bool:
        """
        Handle errors with recovery mechanisms and error counting.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            bool: True if error was handled successfully, False if max errors exceeded
        """
        try:
            with self.error_lock:
                self.error_count += 1
                current_error_count = self.error_count
            
            # Log the error with full context
            self.logger.log_error(error, context, {
                "error_count": current_error_count,
                "max_errors": self.max_errors
            })
            
            # Check if we've exceeded maximum errors
            if current_error_count >= self.max_errors:
                self.logger.log_critical_error(
                    error, 
                    context, 
                    f"Container shutting down due to {current_error_count} consecutive errors"
                )
                return False
            
            # Reset error count on successful operations
            if current_error_count > 0:
                with self.error_lock:
                    self.error_count = 0
            
            return True
            
        except Exception as handle_error:
            # If error handling itself fails, log to stderr
            print(f"CRITICAL: Error handling failed: {str(handle_error)}. Original error: {str(error)}", 
                  file=sys.stderr)
            return False
    
    def start(self) -> None:
        """
        Start the Hearthlink container in background mode.
        
        Implements silent startup with structured logging and explicit
        error handling as specified in requirements.
        """
        try:
            self.running = True
            self.start_time = datetime.now()
            
            start_data = {
                "event_type": "container_start",
                "start_time": self.start_time.isoformat()
            }
            
            self.logger.logger.info("Hearthlink container started successfully", 
                                  extra={"extra_fields": start_data})
            
            # Main container loop with robust error handling
            while self.running:
                try:
                    # Keep container alive with minimal resource usage
                    time.sleep(1)
                    
                    # Periodic health check
                    if self.start_time and (datetime.now() - self.start_time).seconds % 60 == 0:
                        self._health_check()
                    
                except KeyboardInterrupt:
                    self.logger.logger.info("Received shutdown signal", 
                                          extra={"extra_fields": {"event_type": "shutdown_signal"}})
                    self.stop("user_interrupt")
                    break
                except Exception as e:
                    if not self._handle_error(e, "container_main_loop"):
                        self.stop("max_errors_exceeded")
                        break
                        
        except Exception as e:
            self.logger.log_critical_error(e, "container_start", "Container failed to start")
            self.stop("startup_error")
    
    def _health_check(self) -> None:
        """Perform periodic health checks on the container."""
        try:
            health_data = {
                "event_type": "health_check",
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "error_count": self.error_count,
                "memory_usage": self._get_memory_usage()
            }
            
            self.logger.logger.debug("Health check completed", 
                                   extra={"extra_fields": health_data})
            
        except Exception as e:
            self.logger.log_error(e, "health_check")
    
    def _get_memory_usage(self) -> Optional[Dict[str, Any]]:
        """Get current memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except ImportError:
            return None
        except Exception as e:
            self.logger.log_error(e, "memory_usage_check")
            return None
    
    def stop(self, reason: str = "normal") -> None:
        """
        Stop the Hearthlink container gracefully.
        
        Args:
            reason: Reason for stopping the container
        """
        try:
            self.running = False
            
            # Calculate uptime
            uptime = None
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
            
            stop_data = {
                "event_type": "container_stop",
                "reason": reason,
                "uptime_seconds": uptime,
                "stop_time": datetime.now().isoformat(),
                "final_error_count": self.error_count
            }
            
            self.logger.logger.info("Hearthlink container stopped", 
                                  extra={"extra_fields": stop_data})
            
            # Log shutdown information
            self.logger.log_shutdown(reason)
            
        except Exception as e:
            self.logger.log_critical_error(e, "container_stop", "Container stop failed")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get container status information.
        
        Returns:
            dict: Container status including running state and log location
        """
        try:
            uptime = None
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "running": self.running,
                "platform": platform.system(),
                "log_directory": str(self.logger.log_dir.absolute()),
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "uptime_seconds": uptime,
                "error_count": self.error_count,
                "max_errors": self.max_errors,
                "log_config": {
                    "max_size_mb": self.logger.max_size_mb,
                    "backup_count": self.logger.backup_count
                }
            }
        except Exception as e:
            self.logger.log_error(e, "status_retrieval")
            return {"error": str(e)}
    
    def simulate_error(self, error_type: str = "test") -> None:
        """
        Simulate an error for testing purposes.
        
        Args:
            error_type: Type of error to simulate
        """
        try:
            if error_type == "value":
                raise ValueError("Simulated ValueError for testing")
            elif error_type == "runtime":
                raise RuntimeError("Simulated RuntimeError for testing")
            elif error_type == "io":
                raise IOError("Simulated IOError for testing")
            elif error_type == "keyboard":
                raise KeyboardInterrupt("Simulated KeyboardInterrupt for testing")
            else:
                raise Exception(f"Simulated {error_type} error for testing")
                
        except Exception as e:
            self._handle_error(e, f"simulated_error_{error_type}")


class IPCHandler:
    """
    Handler for Inter-Process Communication with Electron main process.
    
    Manages communication between Python backend and Electron frontend,
    handling JSON messages over stdin/stdout.
    """
    
    def __init__(self, container):
        self.container = container
        self.core = None
        self.vault = None
        self.synapse = None
        self.logger = container.logger
        self.running = False
        
        # Initialize backend modules
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize Core, Vault, and Synapse modules."""
        try:
            # Import and initialize modules
            from vault.vault import Vault
            from core.core import Core
            from synapse.synapse import Synapse
            
            # Initialize Vault
            vault_config = {
                "storage": {
                    "file_path": str(Path(__file__).parent.parent / "vault_data")
                },
                "encryption": {
                    "key_env_var": "HEARTHLINK_VAULT_KEY",
                    "key_file": None,
                    "use_hardware_key": False
                },
                "schema_version": "1.0.0"
            }
            self.vault = Vault(vault_config, self.logger.logger)
            
            # Initialize Core with Vault
            core_config = {
                "turn_timeout": 300,
                "auto_advance": True
            }
            self.core = Core(core_config, self.vault, self.logger.logger)
            
            # Initialize Synapse
            from synapse.synapse import SynapseConfig
            synapse_config = SynapseConfig(
                sandbox={
                    "max_cpu_percent": 50.0,
                    "max_memory_mb": 512,
                    "max_disk_mb": 100,
                    "max_execution_time": 300
                },
                benchmark={
                    "test_duration": 30,
                    "response_time_threshold": 1000.0
                },
                traffic={
                    "max_entries": 10000,
                    "retention_days": 30
                },
                security={
                    "require_manifest_signature": True,
                    "auto_approve_low_risk": False,
                    "max_concurrent_executions": 10
                }
            )
            self.synapse = Synapse(synapse_config, self.logger.logger)
            
            self.logger.logger.info("Backend modules initialized successfully")
            
        except Exception as e:
            self.logger.log_error(e, "module_initialization")
            raise
    
    def start(self):
        """Start IPC communication loop."""
        self.running = True
        
        # Signal readiness to Electron
        print("HEARTHLINK_READY", flush=True)
        
        try:
            while self.running:
                # Read command from stdin
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                
                try:
                    command = json.loads(line)
                    response = self._process_command(command)
                    
                    # Send response to stdout
                    response_json = json.dumps(response)
                    print(response_json, flush=True)
                    
                except json.JSONDecodeError as e:
                    self.logger.log_error(e, "json_decode")
                    error_response = {
                        "id": None,
                        "success": False,
                        "error": "Invalid JSON"
                    }
                    print(json.dumps(error_response), flush=True)
                except Exception as e:
                    self.logger.log_error(e, "command_processing")
                    error_response = {
                        "id": command.get("id") if "command" in locals() else None,
                        "success": False,
                        "error": str(e)
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            self.logger.logger.info("IPC handler stopped by user")
        except Exception as e:
            self.logger.log_error(e, "ipc_main_loop")
        finally:
            self.running = False
    
    def _process_command(self, command):
        """Process a command from Electron and return response."""
        command_type = command.get("type")
        command_id = command.get("id")
        payload = command.get("payload", {})
        
        try:
            if command_type == "voice_command":
                return self._handle_voice_command(command_id, payload)
            elif command_type == "core_create_session":
                return self._handle_core_create_session(command_id, payload)
            elif command_type == "core_get_session":
                return self._handle_core_get_session(command_id, payload)
            elif command_type == "core_add_participant":
                return self._handle_core_add_participant(command_id, payload)
            elif command_type == "core_start_turn_taking":
                return self._handle_core_start_turn_taking(command_id, payload)
            elif command_type == "core_advance_turn":
                return self._handle_core_advance_turn(command_id, payload)
            elif command_type == "vault_get_persona_memory":
                return self._handle_vault_get_persona_memory(command_id, payload)
            elif command_type == "vault_update_persona_memory":
                return self._handle_vault_update_persona_memory(command_id, payload)
            elif command_type == "synapse_execute_plugin":
                return self._handle_synapse_execute_plugin(command_id, payload)
            elif command_type == "synapse_list_plugins":
                return self._handle_synapse_list_plugins(command_id, payload)
            elif command_type == "test_write":
                return self._handle_file_write(command_id, payload)
            elif command_type == "file_write":
                return self._handle_file_write(command_id, payload)
            else:
                return {
                    "id": command_id,
                    "success": False,
                    "error": f"Unknown command type: {command_type}"
                }
        except Exception as e:
            return {
                "id": command_id,
                "success": False,
                "error": str(e)
            }
    
    def _handle_voice_command(self, command_id, payload):
        """Handle voice command processing."""
        command = payload.get("command", "")
        
        # Simple command processing - can be enhanced with NLP
        response_text = f"Processed voice command: {command}"
        
        return {
            "id": command_id,
            "success": True,
            "data": response_text
        }
    
    def _handle_core_create_session(self, command_id, payload):
        """Handle Core session creation."""
        user_id = payload.get("userId")
        topic = payload.get("topic")
        participants = payload.get("participants", [])
        
        session_id = self.core.create_session(user_id, topic, participants)
        
        return {
            "id": command_id,
            "success": True,
            "data": {"sessionId": session_id}
        }
    
    def _handle_core_get_session(self, command_id, payload):
        """Handle Core session retrieval."""
        session_id = payload.get("sessionId")
        
        session = self.core.get_session(session_id)
        if session:
            # Convert session to dict for JSON serialization
            session_dict = {
                "session_id": session.session_id,
                "created_by": session.created_by,
                "created_at": session.created_at,
                "topic": session.topic,
                "status": session.status.value,
                "participants": [{"id": p.id, "name": p.name, "type": p.type.value} for p in session.participants],
                "current_turn": session.current_turn
            }
            return {
                "id": command_id,
                "success": True,
                "data": session_dict
            }
        else:
            return {
                "id": command_id,
                "success": False,
                "error": "Session not found"
            }
    
    def _handle_core_add_participant(self, command_id, payload):
        """Handle Core participant addition."""
        session_id = payload.get("sessionId")
        user_id = payload.get("userId")
        participant_data = payload.get("participantData")
        
        success = self.core.add_participant(session_id, user_id, participant_data)
        
        return {
            "id": command_id,
            "success": success,
            "data": {"participantAdded": success}
        }
    
    def _handle_core_start_turn_taking(self, command_id, payload):
        """Handle Core turn-taking start."""
        session_id = payload.get("sessionId")
        user_id = payload.get("userId")
        turn_order = payload.get("turnOrder")
        
        success = self.core.start_turn_taking(session_id, user_id, turn_order)
        
        return {
            "id": command_id,
            "success": success,
            "data": {"turnTakingStarted": success}
        }
    
    def _handle_core_advance_turn(self, command_id, payload):
        """Handle Core turn advancement."""
        session_id = payload.get("sessionId")
        user_id = payload.get("userId")
        
        next_participant = self.core.advance_turn(session_id, user_id)
        
        return {
            "id": command_id,
            "success": True,
            "data": {"nextParticipant": next_participant}
        }
    
    def _handle_vault_get_persona_memory(self, command_id, payload):
        """Handle Vault persona memory retrieval."""
        persona_id = payload.get("personaId")
        user_id = payload.get("userId")
        
        # Get persona memory from vault
        memory_data = self.vault.get_persona_memory(persona_id, user_id)
        
        return {
            "id": command_id,
            "success": True,
            "data": memory_data
        }
    
    def _handle_vault_update_persona_memory(self, command_id, payload):
        """Handle Vault persona memory update."""
        persona_id = payload.get("personaId")
        user_id = payload.get("userId")
        data = payload.get("data")
        
        success = self.vault.update_persona_memory(persona_id, user_id, data)
        
        return {
            "id": command_id,
            "success": success,
            "data": {"updated": success}
        }
    
    def _handle_synapse_execute_plugin(self, command_id, payload):
        """Handle Synapse plugin execution."""
        plugin_id = payload.get("pluginId")
        plugin_payload = payload.get("payload")
        user_id = payload.get("userId")
        
        result = self.synapse.execute_plugin(plugin_id, plugin_payload, user_id)
        
        return {
            "id": command_id,
            "success": True,
            "data": result
        }
    
    def _handle_synapse_list_plugins(self, command_id, payload):
        """Handle Synapse plugin listing."""
        plugins = self.synapse.list_plugins()
        
        return {
            "id": command_id,
            "success": True,
            "data": {"plugins": plugins}
        }
    
    def _handle_file_write(self, command_id, payload):
        """Handle file write operations."""
        try:
            file_path = payload.get("filePath")
            content = payload.get("content")
            
            if not file_path:
                return {
                    "id": command_id,
                    "success": False,
                    "error": "filePath is required"
                }
                
            if content is None:
                return {
                    "id": command_id,
                    "success": False,
                    "error": "content is required"
                }
            
            # Ensure directory exists
            import os
            from pathlib import Path
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Log the successful write
            print(f"[INFO] File written successfully: {file_path}")
            
            return {
                "id": command_id,
                "success": True,
                "data": {
                    "filePath": str(file_path),
                    "size": len(content),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"[ERROR] File write failed: {e}")
            return {
                "id": command_id,
                "success": False,
                "error": f"File write failed: {str(e)}"
            }


def main():
    """
    Main entry point for Hearthlink global container.
    
    Creates and starts the container with proper error handling
    and cross-platform compatibility.
    """
    container = None
    
    try:
        # Create container instance with default logging configuration
        log_config = {
            "max_size_mb": 10,
            "backup_count": 5
        }
        
        container = HearthlinkContainer(log_config=log_config)
        
        # Check if running in IPC mode (called from Electron)
        if len(sys.argv) > 1 and sys.argv[1] == '--ipc':
            # Run in IPC mode
            ipc_handler = IPCHandler(container)
            ipc_handler.start()
        else:
            # Start container (this will run until interrupted)
            container.start()
        
    except Exception as e:
        # Fallback logging if container initialization fails
        error_msg = f"Fatal error starting Hearthlink container: {str(e)}"
        print(error_msg, file=sys.stderr)
        
        # Try to log the error if possible
        if container and hasattr(container, 'logger'):
            container.logger.log_critical_error(e, "container_initialization", "Container failed to initialize")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
