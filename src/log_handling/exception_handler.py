"""
Unified Exception Logging Handler

Singleton service class for centralized exception logging across all Hearthlink modules.
Provides structured JSON logging with comprehensive context and audit trail support.

Export Workflow:
----------------
- Use ExceptionHandler.export_logs(format, start_time, end_time, level, module) to export logs.
- Supported formats: 'json', 'csv', 'syslog'.
- Filtering: by date range (start_time, end_time), module, and severity (level).
- All exports are local/manual only (never networked).

Sample Usage:
-------------
from src.logging.exception_handler import ExceptionHandler, LogLevel
from datetime import datetime

handler = ExceptionHandler.get_instance()

# Export all ERROR logs from 'vault' module in last 24 hours as CSV
logs_csv = handler.export_logs(
    format='csv',
    start_time=datetime.now().replace(hour=0, minute=0, second=0),
    end_time=datetime.now(),
    level=LogLevel.ERROR,
    module='vault'
)
with open('vault_errors.csv', 'w', encoding='utf-8') as f:
    f.write(logs_csv)

# Export all logs as JSON
logs_json = handler.export_logs(format='json')
with open('all_logs.json', 'w', encoding='utf-8') as f:
    f.write(logs_json)

# Export all logs as syslog-formatted text
logs_syslog = handler.export_logs(format='syslog')
with open('logs.syslog', 'w', encoding='utf-8') as f:
    f.write(logs_syslog)

Sample Output (CSV):
--------------------
timestamp,level,exception_type,message,module,function,line_number,user_id,session_id,plugin_id,request_id,log_id
2025-07-07T10:00:00,ERROR,ValueError,"Invalid input","vault","store_memory",123,user-123,,,,log-20250707-000001

Sample Output (Syslog):
----------------------
Jul  7 10:00:00 hearthlink_exceptions ERROR vault: ValueError: Invalid input (user_id=user-123, log_id=log-20250707-000001)
"""

import json
import sys
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """Context information for exception logging."""
    module: str
    function: Optional[str] = None
    line_number: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    plugin_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExceptionLogEntry:
    """Structured exception log entry."""
    timestamp: str
    level: str
    exception_type: str
    message: str
    stack_trace: str
    module: str
    function: Optional[str]
    line_number: Optional[int]
    user_id: Optional[str]
    session_id: Optional[str]
    plugin_id: Optional[str]
    request_id: Optional[str]
    additional_context: Dict[str, Any]
    log_id: str


class ExceptionHandler:
    """
    Singleton exception logging handler.
    
    Provides unified exception logging across all Hearthlink modules with:
    - Structured JSON output
    - Comprehensive context capture
    - Audit trail compliance
    - Thread-safe operation
    - Configurable log levels and destinations
    
    Usage:
        # Get the singleton instance
        handler = ExceptionHandler.get_instance()
        
        # Log an exception
        try:
            # Some operation that might fail
            pass
        except Exception as e:
            handler.log_exception(
                exception=e,
                context=LogContext(
                    module="vault",
                    function="store_memory",
                    user_id="user-123"
                ),
                level=LogLevel.ERROR
            )
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the exception handler (only called once)."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._logger = None
        self._log_file = None
        self._log_level = LogLevel.INFO
        self._max_log_size_mb = 10
        self._backup_count = 5
        self._log_counter = 0
        self._counter_lock = threading.Lock()
        
        # Initialize logging
        self._setup_logging()
    
    @classmethod
    def get_instance(cls) -> 'ExceptionHandler':
        """Get the singleton instance of the exception handler."""
        return cls()
    
    def _setup_logging(self):
        """Set up the logging infrastructure."""
        try:
            # Create log directory
            log_dir = self._get_log_directory()
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up log file
            self._log_file = log_dir / "exceptions.log"
            
            # Configure logger
            self._logger = logging.getLogger("hearthlink_exceptions")
            self._logger.setLevel(logging.DEBUG)
            
            # Clear existing handlers
            self._logger.handlers.clear()
            
            # Create file handler
            file_handler = logging.FileHandler(
                self._log_file, 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter for structured JSON
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self._logger.addHandler(file_handler)
            
            # Log initialization
            self._logger.info(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "event_type": "exception_handler_initialized",
                "message": "Exception handler initialized successfully",
                "log_file": str(self._log_file),
                "max_size_mb": self._max_log_size_mb,
                "backup_count": self._backup_count
            }))
            
        except Exception as e:
            # Fallback to stderr if logging setup fails
            print(f"Failed to setup exception logging: {e}", file=sys.stderr)
            self._logger = None
    
    def _get_log_directory(self) -> Path:
        """Get the log directory based on platform."""
        if sys.platform == "win32":
            # Windows: %LOCALAPPDATA%\Hearthlink\logs
            import os
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            if local_appdata:
                return Path(local_appdata) / "Hearthlink" / "logs"
            else:
                return Path.home() / "AppData" / "Local" / "Hearthlink" / "logs"
        else:
            # Unix-like: ~/.hearthlink/logs
            return Path.home() / ".hearthlink" / "logs"
    
    def _get_next_log_id(self) -> str:
        """Get the next unique log ID."""
        with self._counter_lock:
            self._log_counter += 1
            return f"log-{datetime.now().strftime('%Y%m%d')}-{self._log_counter:06d}"
    
    def log_exception(
        self,
        exception: Exception,
        context: LogContext,
        level: LogLevel = LogLevel.ERROR,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an exception with full context.
        
        Args:
            exception: The exception to log
            context: Context information about where the exception occurred
            level: Log severity level
            additional_data: Optional additional data to include
            
        Returns:
            Log ID for the logged exception
        """
        try:
            # Generate unique log ID
            log_id = self._get_next_log_id()
            
            # Get stack trace
            stack_trace = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
            
            # Create log entry
            log_entry = ExceptionLogEntry(
                timestamp=datetime.now().isoformat(),
                level=level.value,
                exception_type=type(exception).__name__,
                message=str(exception),
                stack_trace=stack_trace.strip(),
                module=context.module,
                function=context.function,
                line_number=context.line_number,
                user_id=context.user_id,
                session_id=context.session_id,
                plugin_id=context.plugin_id,
                request_id=context.request_id,
                additional_context=additional_data or {},
                log_id=log_id
            )
            
            # Convert to dictionary
            log_dict = asdict(log_entry)
            
            # Log the exception
            if self._logger:
                self._logger.error(json.dumps(log_dict, ensure_ascii=False))
            else:
                # Fallback to stderr
                print(json.dumps(log_dict, ensure_ascii=False), file=sys.stderr)
            
            return log_id
            
        except Exception as e:
            # Fallback logging if exception logging fails
            fallback_msg = {
                "timestamp": datetime.now().isoformat(),
                "level": "CRITICAL",
                "event_type": "exception_logging_failed",
                "message": f"Failed to log exception: {e}",
                "original_exception": str(exception),
                "original_module": context.module
            }
            
            if self._logger:
                self._logger.critical(json.dumps(fallback_msg))
            else:
                print(json.dumps(fallback_msg), file=sys.stderr)
            
            return "log-failed"
    
    def log_error(
        self,
        message: str,
        context: LogContext,
        level: LogLevel = LogLevel.ERROR,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an error message (without exception object).
        
        Args:
            message: Error message
            context: Context information
            level: Log severity level
            additional_data: Optional additional data
            
        Returns:
            Log ID for the logged error
        """
        try:
            log_id = self._get_next_log_id()
            
            log_entry = ExceptionLogEntry(
                timestamp=datetime.now().isoformat(),
                level=level.value,
                exception_type="Error",
                message=message,
                stack_trace="",  # No stack trace for error messages
                module=context.module,
                function=context.function,
                line_number=context.line_number,
                user_id=context.user_id,
                session_id=context.session_id,
                plugin_id=context.plugin_id,
                request_id=context.request_id,
                additional_context=additional_data or {},
                log_id=log_id
            )
            
            log_dict = asdict(log_entry)
            
            if self._logger:
                self._logger.error(json.dumps(log_dict, ensure_ascii=False))
            else:
                print(json.dumps(log_dict, ensure_ascii=False), file=sys.stderr)
            
            return log_id
            
        except Exception as e:
            fallback_msg = {
                "timestamp": datetime.now().isoformat(),
                "level": "CRITICAL",
                "event_type": "error_logging_failed",
                "message": f"Failed to log error: {e}",
                "original_message": message,
                "original_module": context.module
            }
            
            if self._logger:
                self._logger.critical(json.dumps(fallback_msg))
            else:
                print(json.dumps(fallback_msg), file=sys.stderr)
            
            return "log-failed"
    
    def get_log_file_path(self) -> Optional[Path]:
        """Get the path to the current log file."""
        return self._log_file
    
    def set_log_level(self, level: LogLevel):
        """Set the minimum log level."""
        self._log_level = level
        if self._logger:
            self._logger.setLevel(getattr(logging, level.value))
    
    def export_logs(
        self,
        format: str = 'json',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        module: Optional[str] = None
    ) -> str:
        """
        Export logs with optional filtering and format.
        Args:
            format: 'json', 'csv', or 'syslog'
            start_time: Filter logs from this time
            end_time: Filter logs until this time
            level: Filter by log level
            module: Filter by module
        Returns:
            Exported logs as a string in the requested format
        """
        if not self._log_file or not self._log_file.exists():
            return ''
        logs = []
        try:
            with open(self._log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        log_entry = json.loads(line)
                        # Apply filters
                        if start_time and datetime.fromisoformat(log_entry['timestamp']) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(log_entry['timestamp']) > end_time:
                            continue
                        if level and log_entry['level'] != level.value:
                            continue
                        if module and log_entry['module'] != module:
                            continue
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            # Format output
            if format == 'json':
                return json.dumps(logs, ensure_ascii=False, indent=2)
            elif format == 'csv':
                import csv
                from io import StringIO
                if not logs:
                    return ''
                output = StringIO()
                fieldnames = [
                    'timestamp','level','exception_type','message','module','function','line_number',
                    'user_id','session_id','plugin_id','request_id','log_id'
                ]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for entry in logs:
                    row = {k: entry.get(k, '') for k in fieldnames}
                    writer.writerow(row)
                return output.getvalue()
            elif format == 'syslog':
                lines = []
                for entry in logs:
                    # Syslog format: <timestamp> <app> <level> <module>: <exception_type>: <message> (<context>)
                    dt = datetime.fromisoformat(entry['timestamp'])
                    syslog_time = dt.strftime('%b %d %H:%M:%S')
                    context = []
                    for k in ['user_id','session_id','plugin_id','request_id','log_id']:
                        if entry.get(k):
                            context.append(f"{k}={entry[k]}")
                    context_str = ', '.join(context)
                    line = f"{syslog_time} hearthlink_exceptions {entry['level']} {entry['module']}: {entry['exception_type']}: {entry['message']} ({context_str})"
                    lines.append(line)
                return '\n'.join(lines)
            else:
                return ''
        except Exception as e:
            self.log_error(
                f"Failed to export logs: {e}",
                LogContext(module="logging", function="export_logs"),
                LogLevel.ERROR
            )
            return ''
    
    def clear_logs(self) -> bool:
        """Clear all log files."""
        try:
            if self._log_file and self._log_file.exists():
                self._log_file.unlink()
            
            # Clear backup files
            log_dir = self._log_file.parent if self._log_file else None
            if log_dir and log_dir.exists():
                for backup_file in log_dir.glob("exceptions.log.*"):
                    backup_file.unlink()
            
            return True
            
        except Exception as e:
            self.log_error(
                f"Failed to clear logs: {e}",
                LogContext(module="logging", function="clear_logs"),
                LogLevel.ERROR
            )
            return False


# Convenience function for easy access
def log_exception(
    exception: Exception,
    context: LogContext,
    level: LogLevel = LogLevel.ERROR,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to log an exception.
    
    Args:
        exception: The exception to log
        context: Context information
        level: Log severity level
        additional_data: Optional additional data
        
    Returns:
        Log ID
    """
    return ExceptionHandler.get_instance().log_exception(
        exception, context, level, additional_data
    )


def log_error(
    message: str,
    context: LogContext,
    level: LogLevel = LogLevel.ERROR,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to log an error message.
    
    Args:
        message: Error message
        context: Context information
        level: Log severity level
        additional_data: Optional additional data
        
    Returns:
        Log ID
    """
    return ExceptionHandler.get_instance().log_error(
        message, context, level, additional_data
    ) 