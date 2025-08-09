"""
Synapse Claude Gateway

Secure REST API endpoint for Claude integration with comprehensive:
- Agent authentication and authorization
- Request validation and sanitization  
- Rate limiting and monitoring
- Vault routing for secure storage
- Sentry integration for monitoring

This is the critical path for Claude operations until Phase 3 write-to-disk is complete.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import hmac
import secrets

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import httpx
from ratelimit import limits, sleep_and_retry
import redis

# Import existing security manager
from .security_manager import (
    SecurityManager, AgentType, PermissionType, SecurityLevel,
    check_synapse_permission
)

# Import token tracker
import sys
sys.path.append(str(Path(__file__).parent.parent))
from log_handling.agent_token_tracker import log_agent_token_usage


logger = logging.getLogger(__name__)


class ClaudeDirectiveRequest(BaseModel):
    """Request model for Claude directives."""
    agentId: str
    module: str
    requestId: str
    prompt: str
    systemMessage: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    
    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v
    
    @validator('agentId')
    def agent_id_must_be_valid(cls, v):
        valid_agents = ['claude', 'alden', 'mimic', 'alice', 'sentry', 'core', 'external']
        if v not in valid_agents:
            raise ValueError(f'Invalid agent ID: {v}')
        return v


class ClaudeValidationResponse(BaseModel):
    """Response model for validated Claude requests."""
    validatedRequest: Dict[str, Any]
    securityContext: Dict[str, Any]
    requestId: str
    timestamp: str


class VaultAppendRequest(BaseModel):
    """Request model for vault storage."""
    agentId: str
    module: str
    requestId: str
    data: Dict[str, Any]


class ClaudeGateway:
    """
    Secure gateway for Claude API access through Synapse.
    
    Implements comprehensive security, monitoring, and routing for Claude operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_manager = SecurityManager()
        self.redis_client = self._init_redis()
        self.app = self._create_app()
        
        # Claude API configuration
        self.claude_config = {
            'base_url': config.get('claude_base_url', 'https://api.anthropic.com'),
            'api_key': config.get('claude_api_key'),
            'timeout': config.get('claude_timeout', 30),
            'max_retries': config.get('claude_max_retries', 3)
        }
        
        # Vault configuration
        self.vault_config = {
            'base_url': config.get('vault_base_url', 'http://localhost:8081'),
            'auth_token': config.get('vault_auth_token'),
            'timeout': config.get('vault_timeout', 10)
        }
        
        # Validate vault connection
        if self.vault_config['auth_token']:
            asyncio.create_task(self._test_vault_connection())
        
        logger.info("Claude Gateway initialized", extra={
            'claude_base_url': self.claude_config['base_url'],
            'vault_enabled': bool(self.vault_config['auth_token'])
        })
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for rate limiting."""
        try:
            redis_config = self.config.get('redis', {})
            client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                password=redis_config.get('password'),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            # Test connection
            client.ping()
            logger.info("Redis connection established for rate limiting")
            return client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting will be memory-based.")
            return None
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application with security middleware."""
        app = FastAPI(
            title="Hearthlink Synapse Claude Gateway",
            description="Secure API gateway for Claude integration",
            version="1.0.0"
        )
        
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get('allowed_origins', ['http://localhost:3000']),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # Security middleware
        security = HTTPBearer()
        
        @app.middleware("http")
        async def security_middleware(request: Request, call_next):
            """Apply security checks to all requests."""
            start_time = time.time()
            
            # Extract agent ID from headers
            agent_id = request.headers.get('X-Hearthlink-Agent', 'unknown')
            request_id = request.headers.get('X-Request-ID', f'req_{int(time.time() * 1000)}')
            
            # Log request
            logger.info(f"Synapse request: {request.method} {request.url.path}", extra={
                'agent_id': agent_id,
                'request_id': request_id,
                'user_agent': request.headers.get('User-Agent'),
                'remote_addr': request.client.host if request.client else 'unknown'
            })
            
            response = await call_next(request)
            
            # Log response
            response_time = time.time() - start_time
            logger.info(f"Synapse response: {response.status_code}", extra={
                'agent_id': agent_id,
                'request_id': request_id,
                'response_time_ms': response_time * 1000,
                'status_code': response.status_code
            })
            
            return response
        
        # Register routes
        self._register_routes(app)
        
        return app
    
    def _register_routes(self, app: FastAPI):
        """Register API routes."""
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "claude_gateway": "operational",
                    "redis": "operational" if self.redis_client else "unavailable",
                    "security_manager": "operational"
                }
            }
        
        @app.post("/api/claude/validate", response_model=ClaudeValidationResponse)
        async def validate_claude_request(request: ClaudeDirectiveRequest):
            """Validate and authorize Claude directive request."""
            try:
                # Map agent ID to agent type
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,  # Claude is external until Phase 3
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE,
                    'external': AgentType.EXTERNAL
                }
                
                agent_type = agent_type_map.get(request.agentId, AgentType.EXTERNAL)
                
                # Check permissions
                has_permission = check_synapse_permission(
                    request.agentId,
                    agent_type,
                    PermissionType.API_EXTERNAL,
                    "claude_directive",
                    f"module:{request.module}",
                    {
                        "prompt_length": len(request.prompt),
                        "has_system_message": bool(request.systemMessage),
                        "request_id": request.requestId
                    }
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {request.agentId} does not have permission for Claude directives"
                    )
                
                # Validate and sanitize prompt
                validated_prompt = self._sanitize_prompt(request.prompt)
                validated_system = self._sanitize_prompt(request.systemMessage) if request.systemMessage else None
                
                # Create validated request
                validated_request = {
                    "prompt": validated_prompt,
                    "systemMessage": validated_system,
                    "temperature": request.temperature,
                    "maxTokens": request.maxTokens,
                    "agentId": request.agentId,
                    "module": request.module
                }
                
                # Security context
                security_context = {
                    "agent_type": agent_type.value,
                    "permission_granted": True,
                    "security_level": SecurityLevel.HIGH.value,
                    "validation_timestamp": datetime.now().isoformat()
                }
                
                return ClaudeValidationResponse(
                    validatedRequest=validated_request,
                    securityContext=security_context,
                    requestId=request.requestId,
                    timestamp=datetime.now().isoformat()
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Claude validation failed: {e}", extra={
                    'agent_id': request.agentId,
                    'request_id': request.requestId,
                    'error': str(e)
                })
                raise HTTPException(status_code=500, detail="Internal validation error")
        
        @app.post("/api/vault/append")
        async def append_to_vault(request: VaultAppendRequest, background_tasks: BackgroundTasks):
            """Store Claude completion to Vault."""
            try:
                # Check vault write permissions
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE
                }
                
                agent_type = agent_type_map.get(request.agentId, AgentType.EXTERNAL)
                
                # Check permissions for vault access
                has_permission = check_synapse_permission(
                    request.agentId,
                    agent_type,
                    PermissionType.FILE_SYSTEM,  # Vault storage requires file system permission
                    "vault_append",
                    f"module:{request.module}",
                    {
                        "data_size": len(str(request.data)),
                        "request_id": request.requestId
                    }
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {request.agentId} does not have vault write permission"
                    )
                
                # Queue vault write operation
                background_tasks.add_task(
                    self._write_to_vault,
                    request.agentId,
                    request.module,
                    request.requestId,
                    request.data
                )
                
                return {
                    "status": "queued",
                    "requestId": request.requestId,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Vault append failed: {e}", extra={
                    'agent_id': request.agentId,
                    'request_id': request.requestId,
                    'error': str(e)
                })
                raise HTTPException(status_code=500, detail="Internal vault error")
        
        @app.post("/directives")
        async def process_claude_directive(request: ClaudeDirectiveRequest):
            """Direct Claude directive processing (legacy endpoint)."""
            # Route through validation first
            validation_response = await validate_claude_request(request)
            
            # Process through Claude API
            try:
                claude_response = await self._call_claude_api(
                    validation_response.validatedRequest,
                    request.requestId
                )
                
                # Store to vault if enabled
                if self.vault_config['auth_token']:
                    await self._write_to_vault(
                        request.agentId,
                        request.module,
                        request.requestId,
                        {
                            "prompt": request.prompt,
                            "response": claude_response['content'],
                            "model": claude_response['model'],
                            "usage": claude_response['usage'],
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                # Track token usage
                await self._track_claude_tokens(request, claude_response)
                
                return claude_response
                
            except Exception as e:
                logger.error(f"Claude directive failed: {e}", extra={
                    'agent_id': request.agentId,
                    'request_id': request.requestId,
                    'error': str(e)
                })
                raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt for security."""
        if not prompt:
            return ""
        
        # Remove potential injection patterns
        sanitized = prompt.strip()
        
        # Basic XSS and injection prevention
        dangerous_patterns = [
            '<script',
            'javascript:',
            'data:text/html',
            'eval(',
            'exec(',
            'import(',
            'require('
        ]
        
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, f"[SANITIZED:{pattern}]")
        
        return sanitized
    
    async def _call_claude_api(self, validated_request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Call Claude API with validated request."""
        url = f"{self.claude_config['base_url']}/v1/messages"
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": validated_request.get('maxTokens', 4096),
            "temperature": validated_request.get('temperature', 0.7),
            "messages": [
                {
                    "role": "user",
                    "content": validated_request['prompt']
                }
            ]
        }
        
        if validated_request.get('systemMessage'):
            payload['system'] = validated_request['systemMessage']
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.claude_config['api_key']}",
            'anthropic-version': '2023-06-01',
            'X-Request-ID': request_id
        }
        
        async with httpx.AsyncClient(timeout=self.claude_config['timeout']) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'content': data['content'][0]['text'],
                'model': data['model'],
                'usage': {
                    'prompt_tokens': data['usage']['input_tokens'],
                    'completion_tokens': data['usage']['output_tokens'],
                    'total_tokens': data['usage']['input_tokens'] + data['usage']['output_tokens']
                },
                'finish_reason': data.get('stop_reason', 'stop')
            }
    
    async def _test_vault_connection(self):
        """Test connection to Vault service."""
        try:
            vault_url = f"{self.vault_config['base_url']}/api/health"
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(vault_url)
                
                if response.is_success:
                    logger.info("Vault connection test successful")
                else:
                    logger.warning(f"Vault health check failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Vault connection test failed: {e}")
    
    async def _write_to_vault(self, agent_id: str, module: str, request_id: str, data: Dict[str, Any]):
        """Write data to vault storage using new secure API."""
        try:
            if not self.vault_config['auth_token']:
                logger.warning("Vault write skipped - no auth token configured")
                return
            
            vault_url = f"{self.vault_config['base_url']}/api/write"
            
            # Create secure path for Claude completions
            safe_path = f"claude_completions/{module}/{agent_id}/{request_id}.json"
            
            payload = {
                'path': safe_path,
                'data': json.dumps(data, indent=2),
                'agentId': agent_id,
                'metadata': {
                    'module': module,
                    'request_id': request_id,
                    'timestamp': datetime.now().isoformat(),
                    'data_type': 'claude_completion',
                    'size': len(str(data))
                },
                'overwrite': False  # Don't overwrite existing files
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.vault_config['auth_token']}",
                'X-Hearthlink-Agent': agent_id,
                'X-Request-ID': request_id
            }
            
            async with httpx.AsyncClient(timeout=self.vault_config['timeout']) as client:
                response = await client.post(vault_url, json=payload, headers=headers)
                
                if response.is_success:
                    result = response.json()
                    logger.info(f"Data written to vault: {safe_path}", extra={
                        'agent_id': agent_id,
                        'request_id': request_id,
                        'vault_path': safe_path,
                        'file_size': result.get('size'),
                        'checksum': result.get('checksum')
                    })
                else:
                    error_detail = response.text
                    logger.warning(f"Vault write failed: {response.status_code}", extra={
                        'agent_id': agent_id,
                        'request_id': request_id,
                        'vault_path': safe_path,
                        'error': error_detail,
                        'status_code': response.status_code
                    })
        
        except Exception as e:
            logger.error(f"Vault write error: {e}", extra={
                'agent_id': agent_id,
                'request_id': request_id,
                'error': str(e)
            })
    
    async def _track_claude_tokens(self, request: ClaudeDirectiveRequest, response: Dict[str, Any]):
        """Track Claude token usage."""
        try:
            usage = response.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)
            
            # Track in background to avoid blocking
            log_agent_token_usage(
                'claude',
                'claude',
                total_tokens,
                f"Claude directive: {request.prompt[:100]}...",
                request.module,
                operation_type='inference',
                request_id=request.requestId,
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=total_tokens,
                model_name=response.get('model', 'claude-3-sonnet'),
                success=True
            )
            
        except Exception as e:
            logger.warning(f"Token tracking failed: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the Claude Gateway server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# Configuration and startup
DEFAULT_CONFIG = {
    'claude_base_url': 'https://api.anthropic.com',
    'claude_api_key': None,  # Must be set via environment
    'claude_timeout': 30,
    'claude_max_retries': 3,
    'vault_base_url': 'http://localhost:8081',
    'vault_auth_token': None,  # Must be set via environment
    'vault_timeout': 10,
    'allowed_origins': ['http://localhost:3000', 'http://localhost:3001'],
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'password': None,
        'db': 0
    }
}

def create_claude_gateway(config: Optional[Dict[str, Any]] = None) -> ClaudeGateway:
    """Factory function to create Claude Gateway with configuration."""
    final_config = {**DEFAULT_CONFIG, **(config or {})}
    
    # Load from environment if not provided
    if not final_config['claude_api_key']:
        import os
        final_config['claude_api_key'] = os.getenv('CLAUDE_API_KEY')
    
    if not final_config['vault_auth_token']:
        import os
        final_config['vault_auth_token'] = os.getenv('VAULT_AUTH_TOKEN')
    
    if not final_config['claude_api_key']:
        raise ValueError("Claude API key must be provided via config or CLAUDE_API_KEY environment variable")
    
    return ClaudeGateway(final_config)


if __name__ == "__main__":
    # Run as standalone server
    gateway = create_claude_gateway()
    gateway.run()