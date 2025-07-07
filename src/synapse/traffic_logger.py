"""
Traffic Logging System

Logs all plugin, API, and browser extension events for audit and monitoring.
Provides traffic summaries and detailed logs for compliance review.
"""

import json
import uuid
import statistics
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

class TrafficType(Enum):
    """Traffic event types."""
    PLUGIN_REGISTER = "plugin_register"
    PLUGIN_EXECUTE = "plugin_execute"
    PLUGIN_APPROVE = "plugin_approve"
    PLUGIN_REVOKE = "plugin_revoke"
    CONNECTION_REQUEST = "connection_request"
    CONNECTION_ESTABLISH = "connection_establish"
    CONNECTION_CLOSE = "connection_close"
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    EXTERNAL_CALL = "external_call"
    ERROR = "error"
    WARNING = "warning"

class TrafficSeverity(Enum):
    """Traffic event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TrafficLogEntry:
    """Traffic log entry."""
    entry_id: str
    timestamp: str
    traffic_type: TrafficType
    source: str
    target: Optional[str] = None
    user_id: Optional[str] = None
    plugin_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None
    status: str = "success"
    error_message: Optional[str] = None
    severity: TrafficSeverity = TrafficSeverity.LOW
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrafficSummary:
    """Traffic summary for a time period."""
    period_start: str
    period_end: str
    total_events: int
    event_types: Dict[str, int]
    sources: Dict[str, int]
    plugins: Dict[str, int]
    error_count: int
    warning_count: int
    avg_duration: float
    top_plugins: List[Dict[str, Any]]
    top_errors: List[Dict[str, Any]]

@dataclass
class ConnectionLog:
    """Connection-specific log."""
    connection_id: str
    plugin_id: str
    user_id: str
    established_at: str
    closed_at: Optional[str] = None
    total_requests: int = 0
    total_errors: int = 0
    total_duration: float = 0.0
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

class TrafficLogger:
    """Logs and manages traffic events for plugins and APIs."""
    
    def __init__(self, max_entries: int = 10000, retention_days: int = 30, logger=None):
        self.max_entries = max_entries
        self.retention_days = retention_days
        self.logger = logger or logging.getLogger(__name__)
        
        # Traffic log storage
        self.traffic_logs: List[TrafficLogEntry] = []
        
        # Connection logs
        self.connection_logs: Dict[str, ConnectionLog] = {}
        
        # Indexes for quick lookups
        self.plugin_index: Dict[str, List[str]] = defaultdict(list)
        self.user_index: Dict[str, List[str]] = defaultdict(list)
        self.session_index: Dict[str, List[str]] = defaultdict(list)
        
        # Traffic counters
        self.traffic_counters = {
            "total_events": 0,
            "events_by_type": defaultdict(int),
            "events_by_source": defaultdict(int),
            "events_by_plugin": defaultdict(int),
            "errors": 0,
            "warnings": 0
        }
    
    def log_traffic(self, traffic_type: TrafficType, source: str, 
                   target: Optional[str] = None, user_id: Optional[str] = None,
                   plugin_id: Optional[str] = None, session_id: Optional[str] = None,
                   request_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None,
                   response: Optional[Dict[str, Any]] = None, duration: Optional[float] = None,
                   status: str = "success", error_message: Optional[str] = None,
                   severity: TrafficSeverity = TrafficSeverity.LOW,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a traffic event.
        
        Args:
            traffic_type: Type of traffic event
            source: Source of the event
            target: Target of the event
            user_id: User ID associated with event
            plugin_id: Plugin ID associated with event
            session_id: Session ID associated with event
            request_id: Request ID associated with event
            payload: Request payload
            response: Response data
            duration: Event duration
            status: Event status
            error_message: Error message if any
            severity: Event severity
            metadata: Additional metadata
            
        Returns:
            Entry ID
        """
        entry_id = f"traffic-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create log entry
        entry = TrafficLogEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            traffic_type=traffic_type,
            source=source,
            target=target,
            user_id=user_id,
            plugin_id=plugin_id,
            session_id=session_id,
            request_id=request_id,
            payload=payload,
            response=response,
            duration=duration,
            status=status,
            error_message=error_message,
            severity=severity,
            metadata=metadata or {}
        )
        
        # Add to log
        self.traffic_logs.append(entry)
        
        # Update indexes
        if plugin_id:
            self.plugin_index[plugin_id].append(entry_id)
        if user_id:
            self.user_index[user_id].append(entry_id)
        if session_id:
            self.session_index[session_id].append(entry_id)
        
        # Update counters
        self._update_counters(entry)
        
        # Update connection log if applicable
        if traffic_type in [TrafficType.CONNECTION_ESTABLISH, TrafficType.CONNECTION_CLOSE]:
            self._update_connection_log(entry)
        
        # Cleanup old entries if needed
        self._cleanup_old_entries()
        
        self.logger.debug(f"Traffic logged: {entry_id} - {traffic_type.value}")
        return entry_id
    
    def get_traffic_logs(self, plugin_id: Optional[str] = None, 
                        user_id: Optional[str] = None, session_id: Optional[str] = None,
                        traffic_type: Optional[TrafficType] = None,
                        start_time: Optional[str] = None, end_time: Optional[str] = None,
                        limit: Optional[int] = None) -> List[TrafficLogEntry]:
        """
        Get traffic logs with optional filtering.
        
        Args:
            plugin_id: Filter by plugin ID
            user_id: Filter by user ID
            session_id: Filter by session ID
            traffic_type: Filter by traffic type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Limit number of results
            
        Returns:
            List of traffic log entries
        """
        # Start with all logs
        logs = self.traffic_logs.copy()
        
        # Apply filters
        if plugin_id:
            entry_ids = set(self.plugin_index.get(plugin_id, []))
            logs = [log for log in logs if log.entry_id in entry_ids]
        
        if user_id:
            entry_ids = set(self.user_index.get(user_id, []))
            logs = [log for log in logs if log.entry_id in entry_ids]
        
        if session_id:
            entry_ids = set(self.session_index.get(session_id, []))
            logs = [log for log in logs if log.entry_id in entry_ids]
        
        if traffic_type:
            logs = [log for log in logs if log.traffic_type == traffic_type]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            logs = [log for log in logs if datetime.fromisoformat(log.timestamp) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            logs = [log for log in logs if datetime.fromisoformat(log.timestamp) <= end_dt]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            logs = logs[:limit]
        
        return logs
    
    def get_traffic_summary(self, hours: int = 24) -> TrafficSummary:
        """
        Get traffic summary for a time period.
        
        Args:
            hours: Number of hours to summarize
            
        Returns:
            Traffic summary
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get logs for period
        logs = self.get_traffic_logs(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )
        
        # Calculate summary statistics
        event_types = defaultdict(int)
        sources = defaultdict(int)
        plugins = defaultdict(int)
        error_count = 0
        warning_count = 0
        durations = []
        plugin_stats = defaultdict(lambda: {"count": 0, "errors": 0, "duration": 0.0})
        error_stats = defaultdict(int)
        
        for log in logs:
            event_types[log.traffic_type.value] += 1
            sources[log.source] += 1
            
            if log.plugin_id:
                plugins[log.plugin_id] += 1
                plugin_stats[log.plugin_id]["count"] += 1
                if log.duration:
                    plugin_stats[log.plugin_id]["duration"] += log.duration
                    durations.append(log.duration)
            
            if log.status == "error":
                error_count += 1
                if log.plugin_id:
                    plugin_stats[log.plugin_id]["errors"] += 1
                if log.error_message:
                    error_stats[log.error_message] += 1
            
            if log.severity == TrafficSeverity.WARNING:
                warning_count += 1
        
        # Calculate averages
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Get top plugins
        top_plugins = []
        for plugin_id, stats in sorted(plugin_stats.items(), 
                                     key=lambda x: x[1]["count"], reverse=True)[:10]:
            top_plugins.append({
                "plugin_id": plugin_id,
                "request_count": stats["count"],
                "error_count": stats["errors"],
                "avg_duration": stats["duration"] / stats["count"] if stats["count"] > 0 else 0.0
            })
        
        # Get top errors
        top_errors = []
        for error_msg, count in sorted(error_stats.items(), 
                                     key=lambda x: x[1], reverse=True)[:10]:
            top_errors.append({
                "error_message": error_msg,
                "count": count
            })
        
        return TrafficSummary(
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            total_events=len(logs),
            event_types=dict(event_types),
            sources=dict(sources),
            plugins=dict(plugins),
            error_count=error_count,
            warning_count=warning_count,
            avg_duration=avg_duration,
            top_plugins=top_plugins,
            top_errors=top_errors
        )
    
    def get_connection_logs(self, plugin_id: Optional[str] = None) -> List[ConnectionLog]:
        """Get connection logs."""
        logs = list(self.connection_logs.values())
        
        if plugin_id:
            logs = [log for log in logs if log.plugin_id == plugin_id]
        
        return logs
    
    def export_traffic_logs(self, format: str = "json", 
                          start_time: Optional[str] = None,
                          end_time: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Export traffic logs.
        
        Args:
            format: Export format (json, csv)
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Exported data
        """
        logs = self.get_traffic_logs(start_time=start_time, end_time=end_time)
        
        if format.lower() == "json":
            return {
                "traffic_logs": [asdict(log) for log in logs],
                "exported_at": datetime.now().isoformat(),
                "total_entries": len(logs)
            }
        elif format.lower() == "csv":
            # Convert to CSV format
            csv_lines = ["entry_id,timestamp,traffic_type,source,target,user_id,plugin_id,status,severity"]
            
            for log in logs:
                csv_line = f"{log.entry_id},{log.timestamp},{log.traffic_type.value},{log.source}"
                csv_line += f",{log.target or ''},{log.user_id or ''},{log.plugin_id or ''}"
                csv_line += f",{log.status},{log.severity.value}"
                csv_lines.append(csv_line)
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_traffic_statistics(self) -> Dict[str, Any]:
        """Get current traffic statistics."""
        return {
            "total_events": self.traffic_counters["total_events"],
            "events_by_type": dict(self.traffic_counters["events_by_type"]),
            "events_by_source": dict(self.traffic_counters["events_by_source"]),
            "events_by_plugin": dict(self.traffic_counters["events_by_plugin"]),
            "error_count": self.traffic_counters["errors"],
            "warning_count": self.traffic_counters["warnings"],
            "active_connections": len([log for log in self.connection_logs.values() 
                                     if not log.closed_at]),
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_counters(self, entry: TrafficLogEntry):
        """Update traffic counters."""
        self.traffic_counters["total_events"] += 1
        self.traffic_counters["events_by_type"][entry.traffic_type.value] += 1
        self.traffic_counters["events_by_source"][entry.source] += 1
        
        if entry.plugin_id:
            self.traffic_counters["events_by_plugin"][entry.plugin_id] += 1
        
        if entry.status == "error":
            self.traffic_counters["errors"] += 1
        
        if entry.severity == TrafficSeverity.WARNING:
            self.traffic_counters["warnings"] += 1
    
    def _update_connection_log(self, entry: TrafficLogEntry):
        """Update connection log."""
        if entry.traffic_type == TrafficType.CONNECTION_ESTABLISH:
            connection_id = entry.request_id or f"conn-{uuid.uuid4().hex[:8]}"
            self.connection_logs[connection_id] = ConnectionLog(
                connection_id=connection_id,
                plugin_id=entry.plugin_id or "unknown",
                user_id=entry.user_id or "unknown",
                established_at=entry.timestamp
            )
        elif entry.traffic_type == TrafficType.CONNECTION_CLOSE:
            connection_id = entry.request_id
            if connection_id and connection_id in self.connection_logs:
                self.connection_logs[connection_id].closed_at = entry.timestamp
        elif entry.traffic_type in [TrafficType.PLUGIN_EXECUTE, TrafficType.API_REQUEST]:
            # Update connection activity
            connection_id = entry.request_id
            if connection_id and connection_id in self.connection_logs:
                conn_log = self.connection_logs[connection_id]
                conn_log.total_requests += 1
                conn_log.last_activity = entry.timestamp
                if entry.status == "error":
                    conn_log.total_errors += 1
                if entry.duration:
                    conn_log.total_duration += entry.duration
    
    def _cleanup_old_entries(self):
        """Clean up old log entries."""
        if len(self.traffic_logs) <= self.max_entries:
            return
        
        # Remove entries older than retention period
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        old_entries = []
        
        for entry in self.traffic_logs:
            if datetime.fromisoformat(entry.timestamp) < cutoff_time:
                old_entries.append(entry)
        
        # Remove old entries
        for entry in old_entries:
            self.traffic_logs.remove(entry)
            
            # Remove from indexes
            if entry.plugin_id and entry.entry_id in self.plugin_index[entry.plugin_id]:
                self.plugin_index[entry.plugin_id].remove(entry.entry_id)
            if entry.user_id and entry.entry_id in self.user_index[entry.user_id]:
                self.user_index[entry.user_id].remove(entry.entry_id)
            if entry.session_id and entry.entry_id in self.session_index[entry.session_id]:
                self.session_index[entry.session_id].remove(entry.entry_id)
        
        # If still over limit, remove oldest entries
        while len(self.traffic_logs) > self.max_entries:
            oldest_entry = min(self.traffic_logs, key=lambda x: x.timestamp)
            self.traffic_logs.remove(oldest_entry)
            
            # Remove from indexes
            if oldest_entry.plugin_id and oldest_entry.entry_id in self.plugin_index[oldest_entry.plugin_id]:
                self.plugin_index[oldest_entry.plugin_id].remove(oldest_entry.entry_id)
            if oldest_entry.user_id and oldest_entry.entry_id in self.user_index[oldest_entry.user_id]:
                self.user_index[oldest_entry.user_id].remove(oldest_entry.entry_id)
            if oldest_entry.session_id and oldest_entry.entry_id in self.session_index[oldest_entry.session_id]:
                self.session_index[oldest_entry.session_id].remove(oldest_entry.entry_id)
        
        self.logger.info(f"Cleaned up {len(old_entries)} old traffic log entries") 