"""
Standardized Error Wrapper Utilities
Replaces duplicate error handling patterns across the codebase
"""

import logging
import traceback
from typing import Any, Callable, Optional, Dict
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

class StandardError(Exception):
    """Base class for standardized application errors"""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'UNKNOWN_ERROR'
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()

class ValidationError(StandardError):
    """Raised when input validation fails"""
    pass

class ServiceError(StandardError):
    """Raised when external service calls fail"""
    pass

def with_error_handling(error_type: type = StandardError, default_return: Any = None):
    """Decorator for standardized error handling"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", extra={
                    'function': func.__name__,
                    'traceback': traceback.format_exc()
                })
                
                if isinstance(e, StandardError):
                    raise
                
                # Wrap unexpected errors
                raise error_type(
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    error_code=f"{func.__name__.upper()}_ERROR",
                    context={'original_error': str(e)}
                ) from e
        
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
    """Safely execute a function with standardized error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execution failed for {func.__name__}: {e}")
        return default_return
