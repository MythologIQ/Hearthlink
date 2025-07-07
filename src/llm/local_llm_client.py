#!/usr/bin/env python3
"""
Local LLM Client for Hearthlink

This module provides a unified interface for local LLM engines including:
- Ollama
- LM Studio
- Other compatible local LLM endpoints

Implements platinum-standard error handling, logging, and fallback mechanisms.

References:
- PLATINUM_BLOCKERS.md: Ethical safety rails and dependency mitigation
- hearthlink_system_documentation_master.md: System architecture requirements
- appendix_h_developer_qa_platinum_checklists.md: QA requirements for error handling

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import requests
import logging
import traceback
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class LLMError(HearthlinkError):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Exception raised when LLM connection fails."""
    pass


class LLMResponseError(LLMError):
    """Exception raised when LLM response is invalid or unexpected."""
    pass


class LLMTimeoutError(LLMError):
    """Exception raised when LLM request times out."""
    pass


class LLMAuthenticationError(LLMError):
    """Exception raised when LLM authentication fails."""
    pass


class LLMRateLimitError(LLMError):
    """Exception raised when LLM rate limit is exceeded."""
    pass


@dataclass
class LLMConfig:
    """Configuration for local LLM endpoint."""
    engine: str  # "ollama", "lmstudio", "custom"
    base_url: str
    model: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    enable_retry: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class LLMRequest:
    """Standardized LLM request structure."""
    prompt: str
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    context: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized LLM response structure."""
    content: str
    model: str
    response_time: float
    timestamp: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@dataclass
class LLMErrorContext:
    """Context information for LLM errors."""
    error_type: str
    error_message: str
    traceback: str
    request_id: Optional[str] = None
    engine: str
    model: str
    base_url: str
    timestamp: str
    retry_count: int = 0
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    request_data: Optional[Dict[str, Any]] = None


class CircuitBreaker:
    """Circuit breaker pattern for LLM requests."""
    
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise LLMConnectionError("Circuit breaker is OPEN - too many recent failures")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.threshold:
                self.state = "OPEN"
            
            raise e


class LocalLLMClient:
    """
    Unified client for local LLM engines.
    
    Supports Ollama, LM Studio, and other compatible endpoints
    with platinum-standard error handling and logging.
    """
    
    def __init__(self, config: LLMConfig, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize local LLM client.
        
        Args:
            config: LLM configuration
            logger: Optional logger instance
            
        Raises:
            LLMError: If client initialization fails
        """
        try:
            self.config = config
            self.logger = logger or HearthlinkLogger()
            self.session = requests.Session()
            self.circuit_breaker = CircuitBreaker(
                config.circuit_breaker_threshold,
                config.circuit_breaker_timeout
            ) if config.enable_circuit_breaker else None
            
            # Configure session
            self.session.timeout = config.timeout
            if config.api_key:
                self.session.headers.update({"Authorization": f"Bearer {config.api_key}"})
            if config.custom_headers:
                self.session.headers.update(config.custom_headers)
            
            # Validate configuration
            self._validate_config()
            
            # Test connection
            self._test_connection()
            
            self.logger.logger.info("Local LLM client initialized successfully", 
                                  extra={"extra_fields": {
                                      "event_type": "llm_client_init",
                                      "engine": config.engine,
                                      "model": config.model,
                                      "base_url": config.base_url,
                                      "timeout": config.timeout,
                                      "max_retries": config.max_retries
                                  }})
            
        except Exception as e:
            error_context = LLMErrorContext(
                error_type="initialization_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                engine=config.engine,
                model=config.model,
                base_url=config.base_url,
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            raise LLMError(f"Failed to initialize LLM client: {str(e)}") from e
    
    def _validate_config(self) -> None:
        """Validate LLM configuration."""
        if not self.config.engine:
            raise LLMError("LLM engine must be specified")
        
        if not self.config.base_url:
            raise LLMError("LLM base URL must be specified")
        
        if not self.config.model:
            raise LLMError("LLM model must be specified")
        
        # Validate engine-specific requirements
        if self.config.engine == "ollama":
            if not self.config.base_url.startswith(("http://", "https://")):
                raise LLMError("Ollama base URL must be a valid HTTP URL")
        
        elif self.config.engine == "lmstudio":
            if not self.config.base_url.startswith(("http://", "https://")):
                raise LLMError("LM Studio base URL must be a valid HTTP URL")
        
        # Validate numeric parameters
        if self.config.timeout <= 0:
            raise LLMError("Timeout must be positive")
        
        if self.config.max_retries < 0:
            raise LLMError("Max retries cannot be negative")
        
        if not 0.0 <= self.config.temperature <= 2.0:
            raise LLMError("Temperature must be between 0.0 and 2.0")
        
        if self.config.max_tokens <= 0:
            raise LLMError("Max tokens must be positive")
    
    def _test_connection(self) -> None:
        """Test connection to LLM endpoint."""
        try:
            if self.config.engine == "ollama":
                response = self.session.get(f"{self.config.base_url}/api/tags")
                response.raise_for_status()
                
            elif self.config.engine == "lmstudio":
                # LM Studio health check
                response = self.session.get(f"{self.config.base_url}/v1/models")
                response.raise_for_status()
                
            else:
                # Custom endpoint - basic connectivity test
                response = self.session.get(self.config.base_url)
                response.raise_for_status()
            
            self.logger.logger.info("LLM connection test successful", 
                                  extra={"extra_fields": {"event_type": "llm_connection_test"}})
            
        except Exception as e:
            error_context = LLMErrorContext(
                error_type="connection_test_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                engine=self.config.engine,
                model=self.config.model,
                base_url=self.config.base_url,
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            raise LLMConnectionError(f"LLM connection test failed: {str(e)}") from e
    
    def _log_error_context(self, error_context: LLMErrorContext) -> None:
        """Log error context with full details."""
        self.logger.log_error(
            Exception(error_context.error_message),
            "llm_error",
            {
                "error_type": error_context.error_type,
                "engine": error_context.engine,
                "model": error_context.model,
                "base_url": error_context.base_url,
                "request_id": error_context.request_id,
                "retry_count": error_context.retry_count,
                "response_status": error_context.response_status,
                "traceback": error_context.traceback
            }
        )
    
    def _handle_request_exception(self, e: Exception, request: LLMRequest, 
                                retry_count: int = 0) -> None:
        """Handle and log request exceptions."""
        error_type = "unknown_error"
        if isinstance(e, Timeout):
            error_type = "timeout_error"
        elif isinstance(e, RequestsConnectionError):
            error_type = "connection_error"
        elif isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code == 401:
                error_type = "authentication_error"
            elif e.response.status_code == 429:
                error_type = "rate_limit_error"
            else:
                error_type = "http_error"
        
        error_context = LLMErrorContext(
            error_type=error_type,
            error_message=str(e),
            traceback=traceback.format_exc(),
            request_id=request.request_id,
            engine=self.config.engine,
            model=self.config.model,
            base_url=self.config.base_url,
            timestamp=datetime.now().isoformat(),
            retry_count=retry_count,
            response_status=getattr(e, 'response', {}).get('status_code') if hasattr(e, 'response') else None,
            response_headers=dict(getattr(e, 'response', {}).headers) if hasattr(e, 'response') else None,
            request_data={
                "prompt_length": len(request.prompt),
                "has_system_message": bool(request.system_message),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream
            }
        )
        
        self._log_error_context(error_context)
        
        # Raise appropriate exception type
        if error_type == "timeout_error":
            raise LLMTimeoutError(f"LLM request timed out after {self.config.timeout}s") from e
        elif error_type == "connection_error":
            raise LLMConnectionError(f"LLM connection failed: {str(e)}") from e
        elif error_type == "authentication_error":
            raise LLMAuthenticationError(f"LLM authentication failed: {str(e)}") from e
        elif error_type == "rate_limit_error":
            raise LLMRateLimitError(f"LLM rate limit exceeded: {str(e)}") from e
        else:
            raise LLMError(f"LLM request failed: {str(e)}") from e
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response from local LLM.
        
        Args:
            request: LLM request with prompt and parameters
            
        Returns:
            LLMResponse: Generated response with metadata
            
        Raises:
            LLMError: If generation fails
        """
        start_time = time.time()
        
        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = f"req_{int(time.time() * 1000)}"
        
        try:
            # Log request
            self.logger.logger.info("LLM generation request", 
                                  extra={"extra_fields": {
                                      "event_type": "llm_generation_request",
                                      "request_id": request.request_id,
                                      "engine": self.config.engine,
                                      "model": self.config.model,
                                      "prompt_length": len(request.prompt),
                                      "temperature": request.temperature or self.config.temperature
                                  }})
            
            # Use circuit breaker if enabled
            if self.circuit_breaker:
                response_data = self.circuit_breaker.call(
                    self._generate_with_retry, request
                )
            else:
                response_data = self._generate_with_retry(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Create standardized response
            llm_response = LLMResponse(
                content=response_data.get("content", ""),
                model=self.config.model,
                usage=response_data.get("usage"),
                finish_reason=response_data.get("finish_reason"),
                response_time=response_time,
                timestamp=datetime.now().isoformat(),
                context=request.context,
                request_id=request.request_id
            )
            
            # Log successful response
            self.logger.logger.info("LLM generation completed", 
                                  extra={"extra_fields": {
                                      "event_type": "llm_generation_success",
                                      "request_id": request.request_id,
                                      "response_length": len(llm_response.content),
                                      "response_time": response_time,
                                      "model": self.config.model
                                  }})
            
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            self._handle_request_exception(e, request)
    
    def _generate_with_retry(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate response with retry logic."""
        last_exception = None
        
        for retry_count in range(self.config.max_retries + 1):
            try:
                # Generate response based on engine
                if self.config.engine == "ollama":
                    return self._generate_ollama(request)
                elif self.config.engine == "lmstudio":
                    return self._generate_lmstudio(request)
                else:
                    return self._generate_custom(request)
                    
            except Exception as e:
                last_exception = e
                
                # Log retry attempt
                if retry_count < self.config.max_retries:
                    self.logger.logger.warning("LLM request failed, retrying", 
                                             extra={"extra_fields": {
                                                 "event_type": "llm_retry_attempt",
                                                 "request_id": request.request_id,
                                                 "retry_count": retry_count + 1,
                                                 "max_retries": self.config.max_retries,
                                                 "error": str(e)
                                             }})
                    
                    # Wait before retry
                    time.sleep(self.config.retry_delay * (2 ** retry_count))
                else:
                    # Final attempt failed
                    self.logger.logger.error("LLM request failed after all retries", 
                                           extra={"extra_fields": {
                                               "event_type": "llm_final_failure",
                                               "request_id": request.request_id,
                                               "retry_count": retry_count,
                                               "error": str(e)
                                           }})
        
        # All retries exhausted
        raise last_exception
    
    def _generate_ollama(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate response using Ollama API."""
        url = f"{self.config.base_url}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature or self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens
            }
        }
        
        if request.system_message:
            payload["system"] = request.system_message
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Validate response structure
        if "response" not in data:
            raise LLMResponseError("Invalid Ollama response: missing 'response' field")
        
        # Ollama response format
        return {
            "content": data.get("response", ""),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            },
            "finish_reason": "stop" if data.get("done", False) else "length"
        }
    
    def _generate_lmstudio(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate response using LM Studio API (OpenAI-compatible)."""
        url = f"{self.config.base_url}/v1/chat/completions"
        
        messages = []
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": request.temperature or self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "stream": request.stream
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Validate response structure
        if "choices" not in data or not data["choices"]:
            raise LLMResponseError("Invalid LM Studio response: missing or empty 'choices' field")
        
        choice = data["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            raise LLMResponseError("Invalid LM Studio response: missing message content")
        
        return {
            "content": choice["message"]["content"],
            "usage": data.get("usage"),
            "finish_reason": choice.get("finish_reason")
        }
    
    def _generate_custom(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate response using custom endpoint."""
        url = f"{self.config.base_url}/generate"
        
        payload = {
            "prompt": request.prompt,
            "system_message": request.system_message,
            "temperature": request.temperature or self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "stream": request.stream
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Validate response structure
        if "content" not in data:
            raise LLMResponseError("Invalid custom response: missing 'content' field")
        
        return {
            "content": data.get("content", ""),
            "usage": data.get("usage"),
            "finish_reason": data.get("finish_reason", "stop")
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models for the configured engine."""
        try:
            if self.config.engine == "ollama":
                response = self.session.get(f"{self.config.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [{"name": model["name"], "size": model.get("size")} for model in data.get("models", [])]
            
            elif self.config.engine == "lmstudio":
                response = self.session.get(f"{self.config.base_url}/v1/models")
                response.raise_for_status()
                data = response.json()
                return [{"name": model["id"], "type": model.get("object")} for model in data.get("data", [])]
            
            else:
                # Custom endpoint
                response = self.session.get(f"{self.config.base_url}/models")
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            error_context = LLMErrorContext(
                error_type="list_models_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                engine=self.config.engine,
                model=self.config.model,
                base_url=self.config.base_url,
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM client status and health information."""
        try:
            return {
                "engine": self.config.engine,
                "model": self.config.model,
                "base_url": self.config.base_url,
                "connected": True,
                "timestamp": datetime.now().isoformat(),
                "circuit_breaker_state": self.circuit_breaker.state if self.circuit_breaker else "disabled"
            }
        except Exception as e:
            error_context = LLMErrorContext(
                error_type="status_check_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
                engine=self.config.engine,
                model=self.config.model,
                base_url=self.config.base_url,
                timestamp=datetime.now().isoformat()
            )
            self._log_error_context(error_context)
            return {
                "engine": self.config.engine,
                "model": self.config.model,
                "base_url": self.config.base_url,
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def create_llm_client(config_dict: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> LocalLLMClient:
    """
    Factory function to create LLM client from configuration dictionary.
    
    Args:
        config_dict: Configuration dictionary
        logger: Optional logger instance
        
    Returns:
        LocalLLMClient: Configured LLM client
        
    Raises:
        LLMError: If client creation fails
    """
    try:
        config = LLMConfig(**config_dict)
        return LocalLLMClient(config, logger)
    except Exception as e:
        raise LLMError(f"Failed to create LLM client: {str(e)}") from e 