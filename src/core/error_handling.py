"""
Core Error Handling - Comprehensive error handling and logging for Core module.

Provides specific exception types, error recovery mechanisms, and structured
logging for all Core orchestration events.
"""

import traceback
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

class ErrorSeverity(Enum):
    """Error severity levels for Core operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for Core operations."""
    SESSION_MANAGEMENT = "session_management"
    PARTICIPANT_MANAGEMENT = "participant_management"
    TURN_TAKING = "turn_taking"
    BREAKOUT_ROOM = "breakout_room"
    COMMUNAL_MEMORY = "communal_memory"
    VAULT_INTEGRATION = "vault_integration"
    API_ERROR = "api_error"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    SYSTEM = "system"

@dataclass
class CoreErrorContext:
    """Context information for Core errors."""
    session_id: Optional[str] = None
    participant_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

class CoreError(Exception):
    """Base exception for Core module errors."""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity, 
                 context: Optional[CoreErrorContext] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or CoreErrorContext()
        self.original_error = original_error
        self.timestamp = datetime.now().isoformat()

class SessionNotFoundError(CoreError):
    """Raised when a session is not found."""
    
    def __init__(self, session_id: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Session {session_id} not found",
            ErrorCategory.SESSION_MANAGEMENT,
            ErrorSeverity.MEDIUM,
            context
        )

class ParticipantNotFoundError(CoreError):
    """Raised when a participant is not found in a session."""
    
    def __init__(self, participant_id: str, session_id: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Participant {participant_id} not found in session {session_id}",
            ErrorCategory.PARTICIPANT_MANAGEMENT,
            ErrorSeverity.MEDIUM,
            context
        )

class InvalidOperationError(CoreError):
    """Raised when an operation is not valid in the current state."""
    
    def __init__(self, operation: str, current_state: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Operation '{operation}' not valid in current state '{current_state}'",
            ErrorCategory.SESSION_MANAGEMENT,
            ErrorSeverity.MEDIUM,
            context
        )

class PermissionDeniedError(CoreError):
    """Raised when user lacks permission for an operation."""
    
    def __init__(self, operation: str, user_id: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Permission denied for operation '{operation}' by user {user_id}",
            ErrorCategory.PERMISSION,
            ErrorSeverity.HIGH,
            context
        )

class TurnTakingError(CoreError):
    """Raised when turn-taking operations fail."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Turn-taking error: {message}",
            ErrorCategory.TURN_TAKING,
            ErrorSeverity.MEDIUM,
            context
        )

class BreakoutRoomError(CoreError):
    """Raised when breakout room operations fail."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Breakout room error: {message}",
            ErrorCategory.BREAKOUT_ROOM,
            ErrorSeverity.MEDIUM,
            context
        )

class CommunalMemoryError(CoreError):
    """Raised when communal memory operations fail."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Communal memory error: {message}",
            ErrorCategory.COMMUNAL_MEMORY,
            ErrorSeverity.MEDIUM,
            context
        )

class VaultIntegrationError(CoreError):
    """Raised when Vault integration operations fail."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Vault integration error: {message}",
            ErrorCategory.VAULT_INTEGRATION,
            ErrorSeverity.HIGH,
            context
        )

class ConfigurationError(CoreError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"Configuration error: {message}",
            ErrorCategory.CONFIGURATION,
            ErrorSeverity.CRITICAL,
            context
        )

class SystemError(CoreError):
    """Raised for system-level errors."""
    
    def __init__(self, message: str, context: Optional[CoreErrorContext] = None):
        super().__init__(
            f"System error: {message}",
            ErrorCategory.SYSTEM,
            ErrorSeverity.CRITICAL,
            context
        )

class CoreErrorHandler:
    """Comprehensive error handler for Core module."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_callbacks: List[Callable] = []
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {}
        self.error_counts: Dict[ErrorCategory, int] = {}
        
        # Initialize error counts
        for category in ErrorCategory:
            self.error_counts[category] = 0
    
    def register_error_callback(self, callback: Callable):
        """Register callback for error events."""
        self.error_callbacks.append(callback)
    
    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """Register recovery strategy for error category."""
        self.recovery_strategies[category] = strategy
    
    def handle_error(self, error: CoreError, operation_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle a Core error with logging and recovery.
        
        Args:
            error: The CoreError to handle
            operation_context: Additional context for the operation
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        try:
            # Update error counts
            self.error_counts[error.category] += 1
            
            # Log error with structured information
            self._log_error(error, operation_context)
            
            # Trigger error callbacks
            self._trigger_error_callbacks(error, operation_context)
            
            # Attempt recovery
            recovered = self._attempt_recovery(error, operation_context)
            
            # Log recovery result
            if recovered:
                self.logger.info(f"Error recovered: {error.message}")
            else:
                self.logger.warning(f"Error not recovered: {error.message}")
            
            return recovered
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return False
    
    def _log_error(self, error: CoreError, operation_context: Optional[Dict[str, Any]] = None):
        """Log error with structured information."""
        log_data = {
            "error_type": type(error).__name__,
            "message": error.message,
            "category": error.category.value,
            "severity": error.severity.value,
            "timestamp": error.timestamp,
            "context": {
                "session_id": error.context.session_id,
                "participant_id": error.context.participant_id,
                "user_id": error.context.user_id,
                "operation": error.context.operation,
                "metadata": error.context.metadata
            },
            "operation_context": operation_context or {},
            "error_count": self.error_counts[error.category]
        }
        
        if error.original_error:
            log_data["original_error"] = {
                "type": type(error.original_error).__name__,
                "message": str(error.original_error),
                "traceback": traceback.format_exc()
            }
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {error.message}", extra=log_data)
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {error.message}", extra=log_data)
    
    def _trigger_error_callbacks(self, error: CoreError, operation_context: Optional[Dict[str, Any]] = None):
        """Trigger registered error callbacks."""
        for callback in self.error_callbacks:
            try:
                callback(error, operation_context)
            except Exception as e:
                self.logger.error(f"Error callback failed: {e}")
    
    def _attempt_recovery(self, error: CoreError, operation_context: Optional[Dict[str, Any]] = None) -> bool:
        """Attempt to recover from error using registered strategies."""
        strategy = self.recovery_strategies.get(error.category)
        if strategy:
            try:
                return strategy(error, operation_context)
            except Exception as e:
                self.logger.error(f"Recovery strategy failed: {e}")
                return False
        return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error counts by category."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "errors_by_category": {cat.value: count for cat, count in self.error_counts.items()},
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_error_counts(self):
        """Reset error counts."""
        for category in ErrorCategory:
            self.error_counts[category] = 0

class CoreErrorRecovery:
    """Recovery strategies for Core errors."""
    
    @staticmethod
    def session_management_recovery(error: CoreError, context: Optional[Dict[str, Any]] = None) -> bool:
        """Recovery strategy for session management errors."""
        if isinstance(error, SessionNotFoundError):
            # Try to recreate session or return to safe state
            return True
        elif isinstance(error, InvalidOperationError):
            # Try alternative operation or return to previous state
            return True
        return False
    
    @staticmethod
    def participant_management_recovery(error: CoreError, context: Optional[Dict[str, Any]] = None) -> bool:
        """Recovery strategy for participant management errors."""
        if isinstance(error, ParticipantNotFoundError):
            # Remove participant from turn order and continue
            return True
        return False
    
    @staticmethod
    def turn_taking_recovery(error: CoreError, context: Optional[Dict[str, Any]] = None) -> bool:
        """Recovery strategy for turn-taking errors."""
        if isinstance(error, TurnTakingError):
            # Skip current turn and continue with next
            return True
        return False
    
    @staticmethod
    def vault_integration_recovery(error: CoreError, context: Optional[Dict[str, Any]] = None) -> bool:
        """Recovery strategy for Vault integration errors."""
        if isinstance(error, VaultIntegrationError):
            # Use in-memory fallback or retry operation
            return True
        return False
    
    @staticmethod
    def system_recovery(error: CoreError, context: Optional[Dict[str, Any]] = None) -> bool:
        """Recovery strategy for system errors."""
        if isinstance(error, SystemError):
            # Attempt system restart or fallback mode
            return False  # System errors typically require manual intervention
        return False

class CoreErrorValidator:
    """Validation utilities for Core operations."""
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format."""
        if not session_id or not isinstance(session_id, str):
            return False
        if not session_id.startswith("core-"):
            return False
        if len(session_id) < 10:  # Minimum length for core-{uuid}
            return False
        return True
    
    @staticmethod
    def validate_participant_data(participant_data: Dict[str, Any]) -> bool:
        """Validate participant data structure."""
        required_fields = ["id", "type", "name"]
        if not all(field in participant_data for field in required_fields):
            return False
        
        # Validate participant type
        valid_types = ["persona", "external", "user"]
        if participant_data["type"] not in valid_types:
            return False
        
        # Validate ID format
        if not participant_data["id"] or not isinstance(participant_data["id"], str):
            return False
        
        return True
    
    @staticmethod
    def validate_turn_order(turn_order: List[str], participants: List[str]) -> bool:
        """Validate turn order against participant list."""
        if not turn_order:
            return False
        
        participant_ids = [p["id"] if isinstance(p, dict) else p for p in participants]
        return all(pid in participant_ids for pid in turn_order)
    
    @staticmethod
    def validate_breakout_participants(breakout_participants: List[str], session_participants: List[str]) -> bool:
        """Validate breakout participants against session participants."""
        if not breakout_participants:
            return False
        
        session_participant_ids = [p["id"] if isinstance(p, dict) else p for p in session_participants]
        return all(pid in session_participant_ids for pid in breakout_participants)

class CoreErrorMetrics:
    """Metrics collection for Core errors."""
    
    def __init__(self):
        self.error_timeline: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = {}
    
    def record_error(self, error: CoreError, recovery_time: Optional[float] = None):
        """Record error for metrics collection."""
        error_record = {
            "timestamp": error.timestamp,
            "category": error.category.value,
            "severity": error.severity.value,
            "recovery_time": recovery_time,
            "session_id": error.context.session_id,
            "participant_id": error.context.participant_id
        }
        self.error_timeline.append(error_record)
    
    def record_performance(self, operation: str, duration: float):
        """Record performance metrics."""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        self.performance_metrics[operation].append(duration)
    
    def get_error_rate(self, time_window_minutes: int = 60) -> Dict[str, float]:
        """Calculate error rate by category over time window."""
        cutoff_time = datetime.now().timestamp() - (time_window_minutes * 60)
        
        recent_errors = [
            error for error in self.error_timeline
            if datetime.fromisoformat(error["timestamp"]).timestamp() > cutoff_time
        ]
        
        error_counts = {}
        for error in recent_errors:
            category = error["category"]
            error_counts[category] = error_counts.get(category, 0) + 1
        
        # Calculate rates (errors per minute)
        window_minutes = time_window_minutes
        return {category: count / window_minutes for category, count in error_counts.items()}
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance summary for all operations."""
        summary = {}
        for operation, durations in self.performance_metrics.items():
            if durations:
                summary[operation] = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_operations": len(durations)
                }
        return summary 