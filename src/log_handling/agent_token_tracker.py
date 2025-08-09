"""
Agent Token Tracking System

Comprehensive token tracking system for all agents (Claude, Alden, Mimic, Gemini, Alice, external GPTs)
to monitor usage, performance metrics, and compliance with Claude Integration Protocol specifications.

Features:
- Token usage tracking for all agents
- Performance metrics and analysis
- Compliance with Claude Integration Protocol
- Audit trail for token efficiency
- Export and reporting capabilities
"""

import json
import threading
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque


class AgentType(Enum):
    """Supported agent types for token tracking."""
    CLAUDE = "claude"
    ALDEN = "alden"
    MIMIC = "mimic"
    GEMINI = "gemini"
    ALICE = "alice"
    EXTERNAL_GPT = "external_gpt"
    SYSTEM = "system"


@dataclass
class TokenUsageRecord:
    """Token usage record for an agent operation."""
    timestamp: str
    agent_name: str
    agent_type: str
    task_description: str
    module: str
    tokens_used: int
    operation_type: str = "inference"  # inference, training, fine-tuning, etc.
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    response_time_ms: Optional[int] = None
    cost_estimate: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for an agent."""
    agent_name: str
    agent_type: str
    total_tokens_used: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_tokens_per_request: float = 0.0
    avg_response_time_ms: float = 0.0
    total_cost_estimate: float = 0.0
    first_request_time: Optional[str] = None
    last_request_time: Optional[str] = None
    
    def update_metrics(self, record: TokenUsageRecord):
        """Update metrics with a new token usage record."""
        self.total_tokens_used += record.tokens_used
        self.total_requests += 1
        
        if record.success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            
        self.avg_tokens_per_request = self.total_tokens_used / self.total_requests
        
        if record.response_time_ms:
            # Calculate running average of response time
            if self.avg_response_time_ms == 0:
                self.avg_response_time_ms = record.response_time_ms
            else:
                self.avg_response_time_ms = (self.avg_response_time_ms + record.response_time_ms) / 2
        
        if record.cost_estimate:
            self.total_cost_estimate += record.cost_estimate
            
        if not self.first_request_time:
            self.first_request_time = record.timestamp
        self.last_request_time = record.timestamp


class AgentTokenTracker:
    """
    Central token tracking system for all agents.
    
    Implements the token tracking requirements specified in the Claude Integration Protocol.
    """
    
    def __init__(self, log_directory: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the token tracker.
        
        Args:
            log_directory: Directory for log files (defaults to project logs dir)
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Set up log directory
        if log_directory:
            self.log_directory = Path(log_directory)
        else:
            # Default to project logs directory
            self.log_directory = Path(__file__).parent.parent.parent / "logs"
        
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Main token tracking log file
        self.log_file = self.log_directory / "agent_token_tracker.log"
        
        # Performance metrics tracking
        self.metrics: Dict[str, AgentPerformanceMetrics] = defaultdict(
            lambda: AgentPerformanceMetrics(agent_name="", agent_type="")
        )
        
        # Recent records for analysis (keep last 1000 records in memory)
        self.recent_records: deque = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize log file with header if it doesn't exist
        self._initialize_log_file()
        
        self.logger.info(f"Agent token tracker initialized with log file: {self.log_file}")
    
    def _initialize_log_file(self):
        """Initialize the log file with header if it doesn't exist."""
        if not self.log_file.exists():
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Agent Token Tracker Log\n")
                f.write(f"# Initialized: {datetime.now().isoformat()}\n")
                f.write(f"# Format: [timestamp] [agent_name] used X tokens for [task] in [module]\n")
                f.write(f"# JSON format for detailed records\n\n")
    
    def log_token_usage(self, 
                       agent_name: str,
                       agent_type: Union[str, AgentType],
                       tokens_used: int,
                       task_description: str,
                       module: str,
                       **kwargs) -> str:
        """
        Log token usage for an agent.
        
        Args:
            agent_name: Name of the agent (e.g., "claude", "alden", "mimic")
            agent_type: Type of agent (AgentType enum or string)
            tokens_used: Number of tokens used
            task_description: Description of the task
            module: Module/component where the task was performed
            **kwargs: Additional metadata
            
        Returns:
            str: Record ID for the logged entry
        """
        with self._lock:
            # Convert agent_type to string if it's an enum
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            
            # Create record
            record = TokenUsageRecord(
                timestamp=datetime.now().isoformat(),
                agent_name=agent_name,
                agent_type=agent_type_str,
                task_description=task_description,
                module=module,
                tokens_used=tokens_used,
                **kwargs
            )
            
            # Generate record ID
            record_id = f"{agent_name}_{int(time.time() * 1000)}"
            
            # Log to file in both formats
            self._write_to_log_file(record)
            
            # Update metrics
            metric_key = f"{agent_name}_{agent_type_str}"
            if metric_key not in self.metrics:
                self.metrics[metric_key] = AgentPerformanceMetrics(
                    agent_name=agent_name,
                    agent_type=agent_type_str
                )
            self.metrics[metric_key].update_metrics(record)
            
            # Add to recent records
            self.recent_records.append(record)
            
            self.logger.debug(f"Logged token usage: {agent_name} used {tokens_used} tokens for {task_description}")
            
            return record_id
    
    def _write_to_log_file(self, record: TokenUsageRecord):
        """Write token usage record to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # Write simple format line (as specified in Claude Integration Protocol)
                simple_line = f"[{record.timestamp}] [{record.agent_name}] used {record.tokens_used} tokens for [{record.task_description}] in [{record.module}]\n"
                f.write(simple_line)
                
                # Write detailed JSON format line
                json_line = json.dumps(asdict(record), ensure_ascii=False) + "\n"
                f.write(json_line)
                
        except Exception as e:
            self.logger.error(f"Failed to write to token tracker log: {e}")
    
    def get_agent_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for an agent or all agents.
        
        Args:
            agent_name: Specific agent name, or None for all agents
            
        Returns:
            Dictionary containing metrics
        """
        with self._lock:
            if agent_name:
                # Find metrics for specific agent
                agent_metrics = {}
                for key, metrics in self.metrics.items():
                    if metrics.agent_name == agent_name:
                        agent_metrics[key] = asdict(metrics)
                return agent_metrics
            else:
                # Return all metrics
                return {key: asdict(metrics) for key, metrics in self.metrics.items()}
    
    def get_usage_summary(self, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get usage summary for a time period.
        
        Args:
            start_time: Start time for summary (None for all time)
            end_time: End time for summary (None for current time)
            
        Returns:
            Dictionary containing usage summary
        """
        with self._lock:
            # Filter records by time if specified
            records_to_analyze = list(self.recent_records)
            
            if start_time or end_time:
                filtered_records = []
                for record in records_to_analyze:
                    record_time = datetime.fromisoformat(record.timestamp)
                    if start_time and record_time < start_time:
                        continue
                    if end_time and record_time > end_time:
                        continue
                    filtered_records.append(record)
                records_to_analyze = filtered_records
            
            # Calculate summary statistics
            total_tokens = sum(record.tokens_used for record in records_to_analyze)
            total_requests = len(records_to_analyze)
            
            # Group by agent
            agent_usage = defaultdict(lambda: {"tokens": 0, "requests": 0})
            for record in records_to_analyze:
                key = f"{record.agent_name}_{record.agent_type}"
                agent_usage[key]["tokens"] += record.tokens_used
                agent_usage[key]["requests"] += 1
            
            # Group by module
            module_usage = defaultdict(lambda: {"tokens": 0, "requests": 0})
            for record in records_to_analyze:
                module_usage[record.module]["tokens"] += record.tokens_used
                module_usage[record.module]["requests"] += 1
            
            return {
                "summary": {
                    "total_tokens": total_tokens,
                    "total_requests": total_requests,
                    "avg_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
                    "time_period": {
                        "start": start_time.isoformat() if start_time else None,
                        "end": end_time.isoformat() if end_time else None
                    }
                },
                "agent_breakdown": dict(agent_usage),
                "module_breakdown": dict(module_usage)
            }
    
    def get_claude_integration_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report for Claude Integration Protocol requirements.
        
        Returns:
            Dictionary containing compliance status and metrics
        """
        with self._lock:
            # Check if all required agents are being tracked
            required_agents = ["claude", "alden", "mimic", "gemini", "alice"]
            tracked_agents = set()
            
            for metrics in self.metrics.values():
                tracked_agents.add(metrics.agent_name)
            
            missing_agents = [agent for agent in required_agents if agent not in tracked_agents]
            
            # Get Claude-specific metrics for token efficiency analysis
            claude_metrics = {}
            for key, metrics in self.metrics.items():
                if metrics.agent_name == "claude":
                    claude_metrics = asdict(metrics)
                    break
            
            # Check log file format compliance
            log_format_compliant = self.log_file.exists()
            
            return {
                "compliance_status": {
                    "log_file_exists": self.log_file.exists(),
                    "log_format_compliant": log_format_compliant,
                    "all_agents_tracked": len(missing_agents) == 0,
                    "missing_agents": missing_agents
                },
                "claude_metrics": claude_metrics,
                "total_agents_tracked": len(tracked_agents),
                "tracked_agents": list(tracked_agents),
                "log_file_location": str(self.log_file),
                "report_timestamp": datetime.now().isoformat()
            }
    
    def export_logs(self, 
                   format: str = "json",
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   agent_filter: Optional[str] = None) -> str:
        """
        Export token tracking logs in specified format.
        
        Args:
            format: Export format ("json", "csv", "simple")
            start_time: Start time for export
            end_time: End time for export
            agent_filter: Filter by specific agent name
            
        Returns:
            Exported data as string
        """
        try:
            # Read and parse log file
            records = []
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                record_dict = json.loads(line)
                                
                                # Apply filters
                                if start_time:
                                    record_time = datetime.fromisoformat(record_dict['timestamp'])
                                    if record_time < start_time:
                                        continue
                                
                                if end_time:
                                    record_time = datetime.fromisoformat(record_dict['timestamp'])
                                    if record_time > end_time:
                                        continue
                                
                                if agent_filter and record_dict['agent_name'] != agent_filter:
                                    continue
                                
                                records.append(record_dict)
                            except json.JSONDecodeError:
                                continue
            
            # Export in requested format
            if format == "json":
                return json.dumps(records, indent=2, ensure_ascii=False)
            
            elif format == "csv":
                if not records:
                    return ""
                
                import csv
                from io import StringIO
                output = StringIO()
                
                # Get all unique field names
                fieldnames = set()
                for record in records:
                    fieldnames.update(record.keys())
                fieldnames = sorted(fieldnames)
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
                
                return output.getvalue()
            
            elif format == "simple":
                lines = []
                for record in records:
                    line = f"[{record['timestamp']}] [{record['agent_name']}] used {record['tokens_used']} tokens for [{record['task_description']}] in [{record['module']}]"
                    lines.append(line)
                return '\n'.join(lines)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
            return ""
    
    def get_log_file_path(self) -> Path:
        """Get the path to the token tracker log file."""
        return self.log_file
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information."""
        with self._lock:
            return {
                "status": "operational",
                "log_file": str(self.log_file),
                "log_file_exists": self.log_file.exists(),
                "log_file_size": self.log_file.stat().st_size if self.log_file.exists() else 0,
                "total_agents_tracked": len(self.metrics),
                "total_records_in_memory": len(self.recent_records),
                "initialization_time": datetime.now().isoformat()
            }


# Global instance
_global_tracker: Optional[AgentTokenTracker] = None
_tracker_lock = threading.Lock()


def get_token_tracker() -> AgentTokenTracker:
    """Get the global token tracker instance."""
    global _global_tracker
    with _tracker_lock:
        if _global_tracker is None:
            _global_tracker = AgentTokenTracker()
        return _global_tracker


def log_agent_token_usage(agent_name: str, 
                         agent_type: Union[str, AgentType],
                         tokens_used: int,
                         task_description: str,
                         module: str,
                         **kwargs) -> str:
    """
    Convenience function to log token usage.
    
    Args:
        agent_name: Name of the agent
        agent_type: Type of agent
        tokens_used: Number of tokens used
        task_description: Description of the task
        module: Module/component name
        **kwargs: Additional metadata
        
    Returns:
        str: Record ID
    """
    tracker = get_token_tracker()
    return tracker.log_token_usage(
        agent_name=agent_name,
        agent_type=agent_type,
        tokens_used=tokens_used,
        task_description=task_description,
        module=module,
        **kwargs
    )


def get_agent_performance_metrics(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance metrics for an agent or all agents.
    
    Args:
        agent_name: Specific agent name, or None for all agents
        
    Returns:
        Dictionary containing metrics
    """
    tracker = get_token_tracker()
    return tracker.get_agent_metrics(agent_name)


def get_compliance_report() -> Dict[str, Any]:
    """
    Get Claude Integration Protocol compliance report.
    
    Returns:
        Dictionary containing compliance status
    """
    tracker = get_token_tracker()
    return tracker.get_claude_integration_compliance_report()