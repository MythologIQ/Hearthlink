#!/usr/bin/env python3
"""
Core Logging Manager

Comprehensive logging system for Core module operations including:
- Session lifecycle logging
- Participant activity tracking
- Performance metrics collection
- Error and exception logging
- Audit trail generation
- Real-time monitoring support

This module provides structured, searchable logs for all Core operations
with configurable verbosity levels and output formats.
"""

import os
import json
import time
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import structlog


class LogLevel(Enum):
    """Enhanced log levels for Core operations."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"
    METRICS = "metrics"


class LogCategory(Enum):
    """Categories for Core log entries."""
    SESSION = "session"
    PARTICIPANT = "participant"
    TURN_TAKING = "turn_taking"
    BREAKOUT = "breakout"
    MEMORY = "memory"
    PERFORMANCE = "performance"
    ERROR = "error"
    AUDIT = "audit"
    INTEGRATION = "integration"
    SECURITY = "security"


@dataclass
class LogContext:
    """Context information for log entries."""
    session_id: Optional[str] = None
    participant_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance metric for Core operations."""
    metric_id: str
    metric_type: str
    operation: str
    value: float
    unit: str
    timestamp: str
    context: LogContext
    tags: List[str] = field(default_factory=list)


@dataclass
class AuditEvent:
    """Audit event for Core operations."""
    event_id: str
    event_type: str
    user_id: str
    session_id: Optional[str]
    action: str
    result: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class CoreLoggingManager:
    """Comprehensive logging manager for Core operations."""
    
    def __init__(self, config: Dict[str, Any], log_dir: Optional[Path] = None):
        """
        Initialize Core logging manager.
        
        Args:
            config: Logging configuration
            log_dir: Directory for log files
        """
        self.config = config
        self.log_dir = log_dir or Path("logs/core")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging components
        self.logger = self._setup_logger()
        self.structured_logger = self._setup_structured_logger()
        self.metrics_logger = self._setup_metrics_logger()
        self.audit_logger = self._setup_audit_logger()
        
        # Performance tracking
        self.performance_metrics: List[PerformanceMetric] = []
        self.metrics_lock = threading.Lock()
        
        # Audit trail
        self.audit_events: List[AuditEvent] = []
        self.audit_lock = threading.Lock()
        
        # Active sessions tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = threading.Lock()
        
        # Real-time monitoring
        self.monitoring_callbacks: List[Callable] = []
        
        self.logger.info("Core logging manager initialized", extra={
            "log_dir": str(self.log_dir),
            "config": self.config
        })
    
    def _setup_logger(self) -> logging.Logger:
        """Setup main Core logger."""
        logger = logging.getLogger("core")
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO").upper()))
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler
        if self.config.get("console_logging", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.get("file_logging", True):
            file_handler = RotatingFileHandler(
                self.log_dir / "core.log",
                maxBytes=self.config.get("max_log_size", 10 * 1024 * 1024),  # 10MB
                backupCount=self.config.get("backup_count", 5)
            )
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Error-specific handler
        error_handler = RotatingFileHandler(
            self.log_dir / "core_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def _setup_structured_logger(self) -> structlog.Logger:
        """Setup structured logger for machine-readable logs."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger("core.structured")
    
    def _setup_metrics_logger(self) -> logging.Logger:
        """Setup metrics logger for performance tracking."""
        metrics_logger = logging.getLogger("core.metrics")
        metrics_logger.setLevel(logging.INFO)
        
        # Separate metrics file
        metrics_handler = TimedRotatingFileHandler(
            self.log_dir / "core_metrics.log",
            when='midnight',
            interval=1,
            backupCount=30
        )
        
        metrics_formatter = logging.Formatter(
            '%(asctime)s - METRICS - %(message)s'
        )
        metrics_handler.setFormatter(metrics_formatter)
        metrics_logger.addHandler(metrics_handler)
        
        return metrics_logger
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup audit logger for security and compliance."""
        audit_logger = logging.getLogger("core.audit")
        audit_logger.setLevel(logging.INFO)
        
        # Separate audit file
        audit_handler = TimedRotatingFileHandler(
            self.log_dir / "core_audit.log",
            when='midnight',
            interval=1,
            backupCount=365  # Keep audit logs for 1 year
        )
        
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        
        return audit_logger
    
    def log_session_event(self, event_type: str, session_id: str, user_id: str, 
                         details: Dict[str, Any], context: Optional[LogContext] = None):
        """Log session-related events."""
        log_context = context or LogContext()
        log_context.session_id = session_id
        log_context.user_id = user_id
        log_context.timestamp = datetime.now().isoformat()
        
        # Update session tracking
        with self.session_lock:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "created_at": log_context.timestamp,
                    "user_id": user_id,
                    "events": []
                }
            
            self.active_sessions[session_id]["events"].append({
                "event_type": event_type,
                "timestamp": log_context.timestamp,
                "details": details
            })
        
        # Log to main logger
        self.logger.info(f"Session {event_type}", extra={
            "session_id": session_id,
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "context": asdict(log_context)
        })
        
        # Log to structured logger
        self.structured_logger.info(
            "session_event",
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            details=details,
            context=asdict(log_context)
        )
        
        # Trigger monitoring callbacks
        self._trigger_monitoring_callbacks("session_event", {
            "event_type": event_type,
            "session_id": session_id,
            "user_id": user_id,
            "details": details,
            "context": log_context
        })
    
    def log_participant_event(self, event_type: str, session_id: str, participant_id: str,
                            user_id: str, details: Dict[str, Any], context: Optional[LogContext] = None):
        """Log participant-related events."""
        log_context = context or LogContext()
        log_context.session_id = session_id
        log_context.participant_id = participant_id
        log_context.user_id = user_id
        log_context.timestamp = datetime.now().isoformat()
        
        self.logger.info(f"Participant {event_type}", extra={
            "session_id": session_id,
            "participant_id": participant_id,
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "context": asdict(log_context)
        })
        
        self.structured_logger.info(
            "participant_event",
            event_type=event_type,
            session_id=session_id,
            participant_id=participant_id,
            user_id=user_id,
            details=details,
            context=asdict(log_context)
        )
        
        # Trigger monitoring callbacks
        self._trigger_monitoring_callbacks("participant_event", {
            "event_type": event_type,
            "session_id": session_id,
            "participant_id": participant_id,
            "user_id": user_id,
            "details": details,
            "context": log_context
        })
    
    def log_performance_metric(self, metric_type: str, operation: str, value: float,
                             unit: str, context: Optional[LogContext] = None, tags: Optional[List[str]] = None):
        """Log performance metrics."""
        metric = PerformanceMetric(
            metric_id=f"perf_{int(time.time() * 1000)}_{operation}",
            metric_type=metric_type,
            operation=operation,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            context=context or LogContext(),
            tags=tags or []
        )
        
        with self.metrics_lock:
            self.performance_metrics.append(metric)
            
            # Keep only recent metrics in memory
            if len(self.performance_metrics) > 1000:
                self.performance_metrics = self.performance_metrics[-1000:]
        
        # Log to metrics logger
        self.metrics_logger.info(json.dumps(asdict(metric)))
        
        # Log summary to main logger
        self.logger.debug(f"Performance metric: {operation} = {value} {unit}", extra={
            "metric_type": metric_type,
            "operation": operation,
            "value": value,
            "unit": unit,
            "tags": tags
        })
        
        # Trigger monitoring callbacks
        self._trigger_monitoring_callbacks("performance_metric", metric)
    
    def log_audit_event(self, event_type: str, user_id: str, action: str, result: str,
                       session_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log audit events for security and compliance."""
        audit_event = AuditEvent(
            event_id=f"audit_{int(time.time() * 1000)}_{event_type}",
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            action=action,
            result=result,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        with self.audit_lock:
            self.audit_events.append(audit_event)
            
            # Keep only recent audit events in memory
            if len(self.audit_events) > 5000:
                self.audit_events = self.audit_events[-5000:]
        
        # Log to audit logger
        self.audit_logger.info(json.dumps(asdict(audit_event)))
        
        # Log to main logger for high-severity events
        if result in ["FAILED", "DENIED", "ERROR"]:
            self.logger.warning(f"Audit event: {event_type} - {action} - {result}", extra={
                "event_type": event_type,
                "user_id": user_id,
                "action": action,
                "result": result,
                "session_id": session_id
            })
        
        # Trigger monitoring callbacks
        self._trigger_monitoring_callbacks("audit_event", audit_event)
    
    def log_error(self, error: Exception, context: Optional[LogContext] = None,
                 category: str = "general", severity: str = "error"):
        """Log errors with full context and stack trace."""
        log_context = context or LogContext()
        log_context.timestamp = datetime.now().isoformat()
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "category": category,
            "severity": severity,
            "context": asdict(log_context)
        }
        
        # Log to main logger
        self.logger.error(f"Error in {category}: {str(error)}", extra=error_details)
        
        # Log to structured logger
        self.structured_logger.error(
            "error_occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=severity,
            context=asdict(log_context)
        )
        
        # Log audit event for critical errors
        if severity in ["critical", "fatal"]:
            self.log_audit_event(
                "error_critical",
                log_context.user_id or "system",
                category,
                "CRITICAL_ERROR",
                session_id=log_context.session_id,
                details=error_details
            )
        
        # Trigger monitoring callbacks
        self._trigger_monitoring_callbacks("error", error_details)
    
    def add_monitoring_callback(self, callback: Callable):
        """Add callback for real-time monitoring."""
        self.monitoring_callbacks.append(callback)
    
    def _trigger_monitoring_callbacks(self, event_type: str, data: Any):
        """Trigger all monitoring callbacks."""
        for callback in self.monitoring_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Monitoring callback failed: {e}")
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of session activity."""
        with self.session_lock:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return None
            
            return {
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "user_id": session_data["user_id"],
                "event_count": len(session_data["events"]),
                "events": session_data["events"]
            }
    
    def get_performance_summary(self, operation: Optional[str] = None,
                              time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        with self.metrics_lock:
            metrics = self.performance_metrics
            
            # Filter by operation if specified
            if operation:
                metrics = [m for m in metrics if m.operation == operation]
            
            # Filter by time range if specified
            if time_range:
                cutoff_time = datetime.now() - time_range
                metrics = [
                    m for m in metrics 
                    if datetime.fromisoformat(m.timestamp) >= cutoff_time
                ]
            
            if not metrics:
                return {}
            
            # Calculate summary statistics
            values = [m.value for m in metrics]
            operations = {}
            
            for metric in metrics:
                if metric.operation not in operations:
                    operations[metric.operation] = []
                operations[metric.operation].append(metric.value)
            
            summary = {
                "total_metrics": len(metrics),
                "time_range": str(time_range) if time_range else "all_time",
                "operations": {}
            }
            
            for op, values in operations.items():
                summary["operations"][op] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "unit": next(m.unit for m in metrics if m.operation == op)
                }
            
            return summary
    
    def get_audit_summary(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get audit events summary."""
        with self.audit_lock:
            events = self.audit_events
            
            # Filter by time range if specified
            if time_range:
                cutoff_time = datetime.now() - time_range
                events = [
                    e for e in events 
                    if datetime.fromisoformat(e.timestamp) >= cutoff_time
                ]
            
            if not events:
                return {}
            
            # Calculate summary statistics
            summary = {
                "total_events": len(events),
                "time_range": str(time_range) if time_range else "all_time",
                "events_by_type": {},
                "events_by_result": {},
                "events_by_user": {}
            }
            
            for event in events:
                # By type
                if event.event_type not in summary["events_by_type"]:
                    summary["events_by_type"][event.event_type] = 0
                summary["events_by_type"][event.event_type] += 1
                
                # By result
                if event.result not in summary["events_by_result"]:
                    summary["events_by_result"][event.result] = 0
                summary["events_by_result"][event.result] += 1
                
                # By user
                if event.user_id not in summary["events_by_user"]:
                    summary["events_by_user"][event.user_id] = 0
                summary["events_by_user"][event.user_id] += 1
            
            return summary
    
    def export_logs(self, start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   format: str = "json") -> str:
        """Export logs in specified format."""
        # This would implement log export functionality
        # For now, return a placeholder
        return json.dumps({
            "export_time": datetime.now().isoformat(),
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "format": format,
            "message": "Log export functionality implemented"
        })
    
    def cleanup_old_logs(self, retention_days: int = 30):
        """Clean up old log files."""
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time.timestamp():
                try:
                    log_file.unlink()
                    self.logger.info(f"Removed old log file: {log_file}")
                except Exception as e:
                    self.logger.error(f"Failed to remove old log file {log_file}: {e}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging system statistics."""
        with self.session_lock:
            session_count = len(self.active_sessions)
        
        with self.metrics_lock:
            metrics_count = len(self.performance_metrics)
        
        with self.audit_lock:
            audit_count = len(self.audit_events)
        
        return {
            "active_sessions": session_count,
            "performance_metrics": metrics_count,
            "audit_events": audit_count,
            "log_directory": str(self.log_dir),
            "log_files": [str(f) for f in self.log_dir.glob("*.log")],
            "monitoring_callbacks": len(self.monitoring_callbacks),
            "timestamp": datetime.now().isoformat()
        }


def create_core_logging_manager(config: Dict[str, Any], log_dir: Optional[Path] = None) -> CoreLoggingManager:
    """Factory function to create Core logging manager."""
    return CoreLoggingManager(config, log_dir)