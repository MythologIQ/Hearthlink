"""
Vault Service - Secure Write-to-Disk Gateway

Provides the ONLY trusted route to disk for all Hearthlink agents.
Implements comprehensive security, authorization, and audit logging.

This is the critical Phase 3 component that enables secure file system access.
"""

import os
import json
import hashlib
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
import secrets
import shutil

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import aiofiles
import aiofiles.os

# Import security manager for authorization
import sys
sys.path.append(str(Path(__file__).parent.parent))
from synapse.security_manager import (
    SecurityManager, AgentType, PermissionType, SecurityLevel,
    check_synapse_permission
)
from log_handling.agent_token_tracker import log_agent_token_usage


logger = logging.getLogger(__name__)


class VaultWriteRequest(BaseModel):
    """Request model for vault write operations."""
    path: str
    data: str
    agentId: str
    metadata: Optional[Dict[str, Any]] = None
    overwrite: bool = False
    
    @validator('path')
    def path_must_be_safe(cls, v):
        """Validate path is safe and within allowed directories."""
        if not v:
            raise ValueError('Path cannot be empty')
        
        # Normalize path to prevent directory traversal
        normalized = os.path.normpath(v)
        
        # Check for directory traversal attempts
        if '..' in normalized or normalized.startswith('/'):
            raise ValueError('Path contains invalid directory traversal')
        
        # Only allow specific safe directories
        allowed_prefixes = [
            'claude_completions/',
            'agent_outputs/',
            'user_data/',
            'logs/',
            'temp/',
            'exports/'
        ]
        
        if not any(normalized.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(f'Path must start with one of: {", ".join(allowed_prefixes)}')
        
        return normalized
    
    @validator('agentId')
    def agent_id_must_be_valid(cls, v):
        valid_agents = ['claude', 'alden', 'mimic', 'alice', 'sentry', 'core', 'user']
        if v not in valid_agents:
            raise ValueError(f'Invalid agent ID: {v}')
        return v


class VaultReadRequest(BaseModel):
    """Request model for vault read operations."""
    path: str
    agentId: str
    
    @validator('path')
    def path_must_be_safe(cls, v):
        """Validate path is safe for reading."""
        if not v:
            raise ValueError('Path cannot be empty')
        
        normalized = os.path.normpath(v)
        
        if '..' in normalized or normalized.startswith('/'):
            raise ValueError('Path contains invalid directory traversal')
        
        return normalized


class VaultDeleteRequest(BaseModel):
    """Request model for vault delete operations."""
    path: str
    agentId: str
    recursive: bool = False
    
    @validator('path')
    def path_must_be_safe(cls, v):
        if not v:
            raise ValueError('Path cannot be empty')
        
        normalized = os.path.normpath(v)
        
        if '..' in normalized or normalized.startswith('/'):
            raise ValueError('Path contains invalid directory traversal')
        
        # Extra protection for delete operations
        if normalized in ['', '.', '/', 'logs', 'claude_completions', 'agent_outputs']:
            raise ValueError('Cannot delete protected directories')
        
        return normalized


@dataclass
class VaultAuditLog:
    """Audit log entry for vault operations."""
    operation: str  # 'write', 'read', 'delete', 'list'
    path: str
    agent_id: str
    timestamp: str
    success: bool
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VaultService:
    """
    Secure vault service for file system operations.
    
    Provides the ONLY trusted route to disk for Hearthlink agents.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vault_root = Path(config.get('vault_root', './vault_data')).resolve()
        self.audit_log_path = self.vault_root / 'audit.log'
        self.security_manager = SecurityManager()
        
        # Ensure vault directory exists
        self.vault_root.mkdir(parents=True, exist_ok=True)
        (self.vault_root / 'claude_completions').mkdir(exist_ok=True)
        (self.vault_root / 'agent_outputs').mkdir(exist_ok=True)
        (self.vault_root / 'user_data').mkdir(exist_ok=True)
        (self.vault_root / 'logs').mkdir(exist_ok=True)
        (self.vault_root / 'temp').mkdir(exist_ok=True)
        (self.vault_root / 'exports').mkdir(exist_ok=True)
        
        # Authorization tokens
        self.auth_tokens = set(config.get('auth_tokens', []))
        if not self.auth_tokens:
            # Generate a default token if none provided
            default_token = secrets.token_urlsafe(32)
            self.auth_tokens.add(default_token)
            logger.warning(f"No auth tokens configured. Generated default: {default_token}")
        
        self.app = self._create_app()
        
        logger.info(f"Vault service initialized", extra={
            'vault_root': str(self.vault_root),
            'auth_tokens_count': len(self.auth_tokens)
        })
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="Hearthlink Vault Service",
            description="Secure file system gateway for Hearthlink agents",
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
        @app.middleware("http")
        async def security_middleware(request: Request, call_next):
            """Apply security and audit logging."""
            start_time = time.time()
            
            # Extract headers
            agent_id = request.headers.get('X-Hearthlink-Agent', 'unknown')
            request_id = request.headers.get('X-Request-ID', f'vault_{int(time.time() * 1000)}')
            
            # Log request
            logger.info(f"Vault request: {request.method} {request.url.path}", extra={
                'agent_id': agent_id,
                'request_id': request_id,
                'remote_addr': request.client.host if request.client else 'unknown'
            })
            
            response = await call_next(request)
            
            # Log response
            response_time = time.time() - start_time
            logger.info(f"Vault response: {response.status_code}", extra={
                'agent_id': agent_id,
                'request_id': request_id,
                'response_time_ms': response_time * 1000,
                'status_code': response.status_code
            })
            
            return response
        
        self._register_routes(app)
        return app
    
    def _register_routes(self, app: FastAPI):
        """Register API routes."""
        
        security = HTTPBearer()
        
        async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
            """Verify authorization token."""
            if credentials.credentials not in self.auth_tokens:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization token"
                )
            return credentials.credentials
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "vault_root": str(self.vault_root),
                "writable": os.access(self.vault_root, os.W_OK)
            }
        
        @app.post("/api/write")
        async def write_file(
            request: VaultWriteRequest,
            token: str = Depends(verify_token),
            background_tasks: BackgroundTasks = BackgroundTasks()
        ):
            """Write file to vault storage."""
            try:
                # Check permissions
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE,
                    'user': AgentType.EXTERNAL
                }
                
                agent_type = agent_type_map.get(request.agentId, AgentType.EXTERNAL)
                
                # Authorize write operation
                has_permission = check_synapse_permission(
                    request.agentId,
                    agent_type,
                    PermissionType.FILE_SYSTEM,
                    "vault_write",
                    request.path,
                    {
                        "file_size": len(request.data.encode('utf-8')),
                        "overwrite": request.overwrite,
                        "metadata": request.metadata
                    }
                )
                
                if not has_permission:
                    await self._audit_log(VaultAuditLog(
                        operation="write",
                        path=request.path,
                        agent_id=request.agentId,
                        timestamp=datetime.now().isoformat(),
                        success=False,
                        error_message="Permission denied"
                    ))
                    
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {request.agentId} does not have vault write permission"
                    )
                
                # Perform write operation
                file_path = self.vault_root / request.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if file exists and overwrite is not allowed
                if file_path.exists() and not request.overwrite:
                    raise HTTPException(
                        status_code=409,
                        detail="File already exists and overwrite not allowed"
                    )
                
                # Write file
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(request.data)
                
                # Calculate checksum
                file_size = len(request.data.encode('utf-8'))
                checksum = hashlib.sha256(request.data.encode('utf-8')).hexdigest()
                
                # Add metadata file
                if request.metadata:
                    metadata_path = file_path.with_suffix('.metadata.json')
                    metadata_content = {
                        'agent_id': request.agentId,
                        'timestamp': datetime.now().isoformat(),
                        'file_size': file_size,
                        'checksum': checksum,
                        'metadata': request.metadata
                    }
                    
                    async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(metadata_content, indent=2))
                
                # Audit log in background
                background_tasks.add_task(
                    self._audit_log,
                    VaultAuditLog(
                        operation="write",
                        path=request.path,
                        agent_id=request.agentId,
                        timestamp=datetime.now().isoformat(),
                        success=True,
                        file_size=file_size,
                        checksum=checksum,
                        metadata=request.metadata
                    )
                )
                
                return {
                    "status": "success",
                    "path": request.path,
                    "size": file_size,
                    "checksum": checksum,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                await self._audit_log(VaultAuditLog(
                    operation="write",
                    path=request.path,
                    agent_id=request.agentId,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=str(e)
                ))
                
                logger.error(f"Vault write failed: {e}", extra={
                    'agent_id': request.agentId,
                    'path': request.path,
                    'error': str(e)
                })
                
                raise HTTPException(status_code=500, detail=f"Write operation failed: {str(e)}")
        
        @app.post("/api/read")
        async def read_file(
            request: VaultReadRequest,
            token: str = Depends(verify_token)
        ):
            """Read file from vault storage."""
            try:
                # Check permissions
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE,
                    'user': AgentType.EXTERNAL
                }
                
                agent_type = agent_type_map.get(request.agentId, AgentType.EXTERNAL)
                
                # Authorize read operation
                has_permission = check_synapse_permission(
                    request.agentId,
                    agent_type,
                    PermissionType.FILE_SYSTEM,
                    "vault_read",
                    request.path,
                    {}
                )
                
                if not has_permission:
                    await self._audit_log(VaultAuditLog(
                        operation="read",
                        path=request.path,
                        agent_id=request.agentId,
                        timestamp=datetime.now().isoformat(),
                        success=False,
                        error_message="Permission denied"
                    ))
                    
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {request.agentId} does not have vault read permission"
                    )
                
                file_path = self.vault_root / request.path
                
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail="File not found")
                
                if not file_path.is_file():
                    raise HTTPException(status_code=400, detail="Path is not a file")
                
                # Read file
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                file_size = len(content.encode('utf-8'))
                checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                # Try to read metadata if it exists
                metadata_path = file_path.with_suffix('.metadata.json')
                metadata = None
                if metadata_path.exists():
                    async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata_content = await f.read()
                        metadata = json.loads(metadata_content)
                
                # Audit log
                await self._audit_log(VaultAuditLog(
                    operation="read",
                    path=request.path,
                    agent_id=request.agentId,
                    timestamp=datetime.now().isoformat(),
                    success=True,
                    file_size=file_size,
                    checksum=checksum
                ))
                
                return {
                    "content": content,
                    "size": file_size,
                    "checksum": checksum,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                await self._audit_log(VaultAuditLog(
                    operation="read",
                    path=request.path,
                    agent_id=request.agentId,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=str(e)
                ))
                
                logger.error(f"Vault read failed: {e}", extra={
                    'agent_id': request.agentId,
                    'path': request.path,
                    'error': str(e)
                })
                
                raise HTTPException(status_code=500, detail=f"Read operation failed: {str(e)}")
        
        @app.delete("/api/delete")
        async def delete_file(
            request: VaultDeleteRequest,
            token: str = Depends(verify_token)
        ):
            """Delete file or directory from vault storage."""
            try:
                # Check permissions
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE,
                    'user': AgentType.EXTERNAL
                }
                
                agent_type = agent_type_map.get(request.agentId, AgentType.EXTERNAL)
                
                # Authorize delete operation (requires highest permission level)
                has_permission = check_synapse_permission(
                    request.agentId,
                    agent_type,
                    PermissionType.FILE_SYSTEM,
                    "vault_delete",
                    request.path,
                    {"recursive": request.recursive}
                )
                
                if not has_permission:
                    await self._audit_log(VaultAuditLog(
                        operation="delete",
                        path=request.path,
                        agent_id=request.agentId,
                        timestamp=datetime.now().isoformat(),
                        success=False,
                        error_message="Permission denied"
                    ))
                    
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {request.agentId} does not have vault delete permission"
                    )
                
                file_path = self.vault_root / request.path
                
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail="Path not found")
                
                # Delete file or directory
                if file_path.is_file():
                    await aiofiles.os.remove(file_path)
                    # Also remove metadata file if it exists
                    metadata_path = file_path.with_suffix('.metadata.json')
                    if metadata_path.exists():
                        await aiofiles.os.remove(metadata_path)
                elif file_path.is_dir():
                    if request.recursive:
                        shutil.rmtree(file_path)
                    else:
                        await aiofiles.os.rmdir(file_path)
                else:
                    raise HTTPException(status_code=400, detail="Unknown file type")
                
                # Audit log
                await self._audit_log(VaultAuditLog(
                    operation="delete",
                    path=request.path,
                    agent_id=request.agentId,
                    timestamp=datetime.now().isoformat(),
                    success=True
                ))
                
                return {
                    "status": "success",
                    "path": request.path,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                await self._audit_log(VaultAuditLog(
                    operation="delete",
                    path=request.path,
                    agent_id=request.agentId,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=str(e)
                ))
                
                logger.error(f"Vault delete failed: {e}", extra={
                    'agent_id': request.agentId,
                    'path': request.path,
                    'error': str(e)
                })
                
                raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")
        
        @app.get("/api/list")
        async def list_directory(
            path: str = "",
            agent_id: str = "user",
            token: str = Depends(verify_token)
        ):
            """List directory contents."""
            try:
                # Normalize path
                safe_path = os.path.normpath(path) if path else ""
                
                # Check permissions
                agent_type_map = {
                    'claude': AgentType.EXTERNAL,
                    'alden': AgentType.ALDEN,
                    'mimic': AgentType.MIMIC,
                    'alice': AgentType.ALICE,
                    'sentry': AgentType.SENTRY,
                    'core': AgentType.CORE,
                    'user': AgentType.EXTERNAL
                }
                
                agent_type = agent_type_map.get(agent_id, AgentType.EXTERNAL)
                
                has_permission = check_synapse_permission(
                    agent_id,
                    agent_type,
                    PermissionType.FILE_SYSTEM,
                    "vault_list",
                    safe_path,
                    {}
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent {agent_id} does not have vault list permission"
                    )
                
                dir_path = self.vault_root / safe_path if safe_path else self.vault_root
                
                if not dir_path.exists():
                    raise HTTPException(status_code=404, detail="Directory not found")
                
                if not dir_path.is_dir():
                    raise HTTPException(status_code=400, detail="Path is not a directory")
                
                # List contents
                items = []
                for item in dir_path.iterdir():
                    if item.name.endswith('.metadata.json'):
                        continue  # Skip metadata files in listing
                    
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                
                # Audit log
                await self._audit_log(VaultAuditLog(
                    operation="list",
                    path=safe_path,
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                    success=True
                ))
                
                return {
                    "path": safe_path,
                    "items": sorted(items, key=lambda x: (x["type"], x["name"])),
                    "count": len(items),
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                await self._audit_log(VaultAuditLog(
                    operation="list",
                    path=safe_path if 'safe_path' in locals() else path,
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=str(e)
                ))
                
                logger.error(f"Vault list failed: {e}", extra={
                    'agent_id': agent_id,
                    'path': path,
                    'error': str(e)
                })
                
                raise HTTPException(status_code=500, detail=f"List operation failed: {str(e)}")
    
    async def _audit_log(self, entry: VaultAuditLog):
        """Write audit log entry."""
        try:
            log_line = json.dumps(asdict(entry)) + '\n'
            
            async with aiofiles.open(self.audit_log_path, 'a', encoding='utf-8') as f:
                await f.write(log_line)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8081):
        """Run the vault service."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# Configuration and startup
DEFAULT_VAULT_CONFIG = {
    'vault_root': './vault_data',
    'auth_tokens': [],  # Must be set via environment or config
    'allowed_origins': ['http://localhost:3000', 'http://localhost:8080'],
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'backup_enabled': True,
    'backup_interval': 3600  # 1 hour
}

def create_vault_service(config: Optional[Dict[str, Any]] = None) -> VaultService:
    """Factory function to create Vault service."""
    final_config = {**DEFAULT_VAULT_CONFIG, **(config or {})}
    
    # Load auth tokens from environment if not provided
    if not final_config['auth_tokens']:
        import os
        tokens_env = os.getenv('VAULT_AUTH_TOKENS')
        if tokens_env:
            final_config['auth_tokens'] = tokens_env.split(',')
    
    return VaultService(final_config)


if __name__ == "__main__":
    # Run as standalone server
    vault = create_vault_service()
    vault.run()