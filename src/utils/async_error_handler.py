"""
Async Error Handler Utility for Python
Provides consistent error handling for async operations
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ErrorInfo:
    """Information about an async operation error"""
    error_message: str
    attempt: int
    max_attempts: int
    context: Dict[str, Any]
    timestamp: str
    error_type: str = ""

class AsyncErrorHandler:
    """Handles errors in async operations with retry logic and structured logging"""
    
    def __init__(self, retry_attempts: int = 3, retry_delay: float = 1.0):
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.error_log = []
    
    async def execute_with_retry(
        self, 
        async_fn: Callable,
        context: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with retry logic"""
        context = context or {}
        last_error = None
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                result = await async_fn(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"✅ Async operation succeeded on attempt {attempt}", extra={
                        'context': context,
                        'attempt': attempt,
                        'timestamp': datetime.now().isoformat()
                    })
                
                return result
                
            except Exception as error:
                last_error = error
                
                error_info = ErrorInfo(
                    error_message=str(error),
                    attempt=attempt,
                    max_attempts=self.retry_attempts,
                    context=context,
                    timestamp=datetime.now().isoformat(),
                    error_type=type(error).__name__
                )
                
                # Log structured error
                logger.error(f"❌ Async operation failed (attempt {attempt}/{self.retry_attempts})", 
                           extra=asdict(error_info))
                
                # Store error for debugging
                self.error_log.append(error_info)
                
                # Don't retry on final attempt
                if attempt == self.retry_attempts:
                    break
                
                # Wait before retry with exponential backoff
                delay = self.retry_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
        
        # All retries failed
        final_error = Exception(f"Async operation failed after {self.retry_attempts} attempts: {last_error}")
        final_error.original_error = last_error
        final_error.context = context
        
        raise final_error
    
    async def execute_with_timeout(
        self,
        async_fn: Callable,
        timeout_seconds: float = 10.0,
        context: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with timeout"""
        context = context or {}
        
        try:
            return await asyncio.wait_for(
                async_fn(*args, **kwargs),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            timeout_error = Exception(f"Async operation timed out after {timeout_seconds}s")
            timeout_error.context = context
            raise timeout_error
    
    async def execute_with_guards(
        self,
        async_fn: Callable,
        timeout_seconds: float = 10.0,
        context: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with both retry and timeout"""
        context = context or {}
        
        return await self.execute_with_retry(
            lambda: self.execute_with_timeout(async_fn, timeout_seconds, context, *args, **kwargs),
            context
        )
    
    async def execute_batch(
        self,
        async_functions: List[Callable],
        fail_fast: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute multiple async functions with error isolation"""
        context = context or {}
        results = []
        errors = []
        
        for i, async_fn in enumerate(async_functions):
            try:
                result = await self.execute_with_guards(
                    async_fn,
                    context={**context, 'batch_index': i}
                )
                results.append({'index': i, 'success': True, 'result': result})
            except Exception as error:
                error_info = {'index': i, 'success': False, 'error': str(error)}
                errors.append(error_info)
                results.append(error_info)
                
                if fail_fast:
                    raise Exception(f"Batch execution failed at index {i}: {error}")
        
        return {
            'results': results,
            'errors': errors,
            'success_count': len([r for r in results if r['success']]),
            'error_count': len(errors)
        }
    
    def get_error_log(self) -> List[Dict[str, Any]]:
        """Get recent error log"""
        return [asdict(error) for error in self.error_log[-50:]]  # Last 50 errors
    
    def clear_error_log(self):
        """Clear error log"""
        self.error_log.clear()

# Global instance
async_error_handler = AsyncErrorHandler()

# Helper functions
async def with_retry(async_fn: Callable, context: Optional[Dict[str, Any]] = None, *args, **kwargs):
    """Helper function for retry logic"""
    return await async_error_handler.execute_with_retry(async_fn, context, *args, **kwargs)

async def with_timeout(async_fn: Callable, timeout: float = 10.0, context: Optional[Dict[str, Any]] = None, *args, **kwargs):
    """Helper function for timeout logic"""
    return await async_error_handler.execute_with_timeout(async_fn, timeout, context, *args, **kwargs)

async def with_guards(async_fn: Callable, timeout: float = 10.0, context: Optional[Dict[str, Any]] = None, *args, **kwargs):
    """Helper function for both retry and timeout"""
    return await async_error_handler.execute_with_guards(async_fn, timeout, context, *args, **kwargs)
