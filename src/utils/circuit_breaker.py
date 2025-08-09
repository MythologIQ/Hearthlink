#!/usr/bin/env python3
"""
Circuit Breaker Pattern Implementation
Provides resilient service communication with automatic failure detection and recovery
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: int = 30                   # Request timeout in seconds
    monitoring_window: int = 300        # Rolling window for failure tracking (seconds)
    
class CircuitBreakerMetrics:
    """Metrics tracking for circuit breaker"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.circuit_open_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.recent_failures = []  # Timestamps of recent failures
        self.state_changes = []    # History of state changes
        
    def record_success(self):
        """Record a successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success_time = datetime.now()
        
    def record_failure(self):
        """Record a failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure_time = datetime.now()
        self.recent_failures.append(datetime.now())
        
    def record_state_change(self, old_state: CircuitState, new_state: CircuitState, reason: str):
        """Record a state change"""
        self.state_changes.append({
            'timestamp': datetime.now().isoformat(),
            'from_state': old_state.value,
            'to_state': new_state.value,
            'reason': reason
        })
        
        if new_state == CircuitState.OPEN:
            self.circuit_open_count += 1
            
    def cleanup_old_failures(self, window_seconds: int):
        """Remove failure records older than window"""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        self.recent_failures = [f for f in self.recent_failures if f > cutoff]
        
    def get_failure_rate(self, window_seconds: int) -> float:
        """Get failure rate within time window"""
        self.cleanup_old_failures(window_seconds)
        if self.total_requests == 0:
            return 0.0
        return len(self.recent_failures) / max(1, self.total_requests)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'circuit_open_count': self.circuit_open_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'recent_failures_count': len(self.recent_failures),
            'failure_rate': self.get_failure_rate(300)  # 5 minute window
        }

class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against cascading failures
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_failure_time = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.lock = threading.RLock()
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or raises CircuitBreakerOpenException
            
        Raises:
            CircuitBreakerOpenException: When circuit is open
            TimeoutError: When request times out
        """
        with self.lock:
            current_state = self._get_current_state()
            
            if current_state == CircuitState.OPEN:
                logger.warning(f"Circuit breaker '{self.name}' is OPEN, blocking request")
                raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is open")
                
            if current_state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit breaker '{self.name}' is HALF_OPEN, allowing test request")
                
        # Execute the function
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > self.config.timeout:
                raise TimeoutError(f"Request timeout after {execution_time:.2f}s")
                
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
            
    def _get_current_state(self) -> CircuitState:
        """Determine current state based on time and conditions"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._change_state(CircuitState.HALF_OPEN, "Recovery timeout elapsed")
                
        return self.state
        
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if self.last_failure_time is None:
            return False
            
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.recovery_timeout
        
    def _on_success(self):
        """Handle successful request"""
        with self.lock:
            self.metrics.record_success()
            
            if self.state == CircuitState.HALF_OPEN:
                self.consecutive_successes += 1
                if self.consecutive_successes >= self.config.success_threshold:
                    self._change_state(CircuitState.CLOSED, "Success threshold reached")
                    self.consecutive_failures = 0
                    self.consecutive_successes = 0
                    
            elif self.state == CircuitState.CLOSED:
                self.consecutive_failures = 0
                
    def _on_failure(self, exception: Exception):
        """Handle failed request"""
        with self.lock:
            self.metrics.record_failure()
            self.last_failure_time = time.time()
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            
            logger.error(f"Circuit breaker '{self.name}' recorded failure: {exception}")
            
            if (self.state == CircuitState.CLOSED and 
                self.consecutive_failures >= self.config.failure_threshold):
                self._change_state(CircuitState.OPEN, f"Failure threshold reached ({self.consecutive_failures})")
                
            elif self.state == CircuitState.HALF_OPEN:
                self._change_state(CircuitState.OPEN, "Failed during half-open test")
                
    def _change_state(self, new_state: CircuitState, reason: str):
        """Change circuit breaker state"""
        old_state = self.state
        self.state = new_state
        self.metrics.record_state_change(old_state, new_state, reason)
        
        logger.info(f"Circuit breaker '{self.name}' state: {old_state.value} -> {new_state.value} ({reason})")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status and metrics"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'consecutive_failures': self.consecutive_failures,
                'consecutive_successes': self.consecutive_successes,
                'last_failure_time': self.last_failure_time,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold,
                    'timeout': self.config.timeout
                },
                'metrics': self.metrics.to_dict(),
                'health_status': self._get_health_status()
            }
            
    def _get_health_status(self) -> str:
        """Get overall health status"""
        if self.state == CircuitState.OPEN:
            return "unhealthy"
        elif self.state == CircuitState.HALF_OPEN:
            return "recovering"
        else:
            failure_rate = self.metrics.get_failure_rate(self.config.monitoring_window)
            if failure_rate > 0.1:  # More than 10% failure rate
                return "degraded"
            return "healthy"
            
    def reset(self):
        """Manually reset circuit breaker to closed state"""
        with self.lock:
            old_state = self.state
            self._change_state(CircuitState.CLOSED, "Manual reset")
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset from {old_state.value}")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different services
    """
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.RLock()
        
    def get_or_create(self, service_name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get existing circuit breaker or create new one"""
        with self.lock:
            if service_name not in self.breakers:
                self.breakers[service_name] = CircuitBreaker(service_name, config)
                logger.info(f"Created new circuit breaker for service: {service_name}")
            return self.breakers[service_name]
            
    def get_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get existing circuit breaker"""
        return self.breakers.get(service_name)
        
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        with self.lock:
            return {
                'circuit_breakers': {
                    name: breaker.get_status() 
                    for name, breaker in self.breakers.items()
                },
                'total_breakers': len(self.breakers),
                'healthy_breakers': sum(1 for b in self.breakers.values() 
                                      if b.get_status()['health_status'] == 'healthy'),
                'timestamp': datetime.now().isoformat()
            }
            
    def reset_all(self):
        """Reset all circuit breakers"""
        with self.lock:
            for breaker in self.breakers.values():
                breaker.reset()
            logger.info("All circuit breakers reset")
            
    def remove_breaker(self, service_name: str):
        """Remove a circuit breaker"""
        with self.lock:
            if service_name in self.breakers:
                del self.breakers[service_name]
                logger.info(f"Removed circuit breaker for service: {service_name}")

# Global circuit breaker manager instance
circuit_manager = CircuitBreakerManager()

def with_circuit_breaker(service_name: str, config: CircuitBreakerConfig = None):
    """
    Decorator for adding circuit breaker protection to functions
    
    Args:
        service_name: Name of the service/circuit breaker
        config: Circuit breaker configuration
        
    Usage:
        @with_circuit_breaker('my_service')
        def my_function():
            return call_external_service()
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            breaker = circuit_manager.get_or_create(service_name, config)
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the circuit breaker
    import random
    
    def unreliable_service():
        """Simulate an unreliable service"""
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Service unavailable")
        return "Success!"
    
    # Create circuit breaker
    config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=5)
    breaker = CircuitBreaker("test_service", config)
    
    # Test the service
    for i in range(20):
        try:
            result = breaker.call(unreliable_service)
            print(f"Request {i+1}: {result}")
        except Exception as e:
            print(f"Request {i+1}: {type(e).__name__}: {e}")
        
        print(f"Circuit state: {breaker.state.value}")
        time.sleep(1)
    
    # Print final status
    print("\nFinal Status:")
    print(json.dumps(breaker.get_status(), indent=2, default=str))