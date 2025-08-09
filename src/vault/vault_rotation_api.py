"""
SPEC-2 Phase 2: Vault Key Rotation REST API
Provides HTTP endpoints for key rotation management and monitoring.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .key_rotation import VaultKeyRotationManager, KeyRotationScheduler, RotationPolicy

# Request/Response Models
class RotationRequest(BaseModel):
    force: bool = Field(False, description="Force rotation even if not due")
    trigger_type: str = Field("api", description="Type of rotation trigger")

class RotationResponse(BaseModel):
    success: bool
    old_version: Optional[int] = None
    new_version: Optional[int] = None
    duration_seconds: float
    trigger_type: str
    reason: Optional[str] = None
    message: str

class KeyStatusResponse(BaseModel):
    current_version: Optional[int]
    should_rotate: bool
    rotation_reason: str
    policy: Dict[str, Any]
    metrics: Dict[str, Any]
    versions: List[Dict[str, Any]]

class RollbackRequest(BaseModel):
    target_version: int = Field(..., description="Key version to rollback to")

class PolicyUpdateRequest(BaseModel):
    rotation_interval_days: Optional[int] = Field(None, ge=1, le=365)
    max_key_versions: Optional[int] = Field(None, ge=1, le=10)
    auto_rotation_enabled: Optional[bool] = None
    performance_threshold_seconds: Optional[float] = Field(None, ge=0.1, le=60.0)

# Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API token for vault operations"""
    # In production, implement proper JWT validation
    if credentials.credentials != "vault-rotation-token":
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

# Global rotation manager instance
rotation_manager: Optional[VaultKeyRotationManager] = None
rotation_scheduler: Optional[KeyRotationScheduler] = None

def get_rotation_manager() -> VaultKeyRotationManager:
    """Get the global rotation manager instance"""
    global rotation_manager
    if rotation_manager is None:
        raise HTTPException(status_code=500, detail="Key rotation manager not initialized")
    return rotation_manager

def initialize_rotation_system(config: Dict[str, Any], logger: Optional[logging.Logger] = None):
    """Initialize the global rotation system"""
    global rotation_manager, rotation_scheduler
    
    try:
        rotation_manager = VaultKeyRotationManager(config, logger)
        rotation_scheduler = KeyRotationScheduler(rotation_manager, logger)
        
        # Start the scheduler in the background
        asyncio.create_task(rotation_scheduler.start())
        
        if logger:
            logger.info("Vault key rotation system initialized")
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to initialize rotation system: {e}")
        raise

async def shutdown_rotation_system():
    """Shutdown the rotation system gracefully"""
    global rotation_scheduler
    if rotation_scheduler:
        await rotation_scheduler.stop()

# API Router
router = APIRouter(prefix="/api/vault", tags=["vault-rotation"])

@router.post("/rotate-keys", response_model=RotationResponse)
async def rotate_keys(
    request: RotationRequest,
    background_tasks: BackgroundTasks,
    _token: str = Depends(verify_token)
):
    """
    Perform key rotation with optional force flag
    
    - **force**: Force rotation even if not due (default: false)
    - **trigger_type**: Type of trigger causing rotation (default: "api")
    """
    manager = get_rotation_manager()
    
    try:
        # Perform rotation asynchronously
        result = await manager.rotate_key(
            trigger_type=request.trigger_type,
            force=request.force
        )
        
        if result['success']:
            return RotationResponse(
                success=True,
                old_version=result.get('old_version'),
                new_version=result.get('new_version'),
                duration_seconds=result['duration_seconds'],
                trigger_type=result['trigger_type'],
                message=f"Key rotation completed successfully in {result['duration_seconds']:.2f}s"
            )
        else:
            return RotationResponse(
                success=False,
                duration_seconds=0.0,
                trigger_type=request.trigger_type,
                reason=result.get('reason'),
                message=result.get('reason', 'Key rotation not performed')
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Key rotation failed: {str(e)}"
        )

@router.get("/key-status", response_model=KeyStatusResponse)
async def get_key_status(_token: str = Depends(verify_token)):
    """
    Get current key status and rotation information
    
    Returns information about:
    - Current active key version
    - Whether rotation is due
    - Rotation policy settings
    - Historical metrics
    - Available key versions
    """
    manager = get_rotation_manager()
    
    try:
        metadata = manager.export_key_metadata()
        should_rotate, reason = manager.should_rotate()
        versions = manager.list_key_versions()
        
        return KeyStatusResponse(
            current_version=metadata.get('current_key_version'),
            should_rotate=should_rotate,
            rotation_reason=reason,
            policy=metadata.get('policy', {}),
            metrics=metadata.get('metrics', {}),
            versions=versions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get key status: {str(e)}"
        )

@router.get("/rotation-history")
async def get_rotation_history(
    limit: int = 50,
    _token: str = Depends(verify_token)
):
    """
    Get key rotation history
    
    - **limit**: Maximum number of history entries to return (default: 50)
    """
    manager = get_rotation_manager()
    
    try:
        history = manager.get_rotation_history(limit=limit)
        return {
            "history": history,
            "total_entries": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get rotation history: {str(e)}"
        )

@router.post("/rollback", response_model=RotationResponse)
async def rollback_key(
    request: RollbackRequest,
    _token: str = Depends(verify_token)
):
    """
    Rollback to a previous key version (emergency use only)
    
    - **target_version**: Key version number to rollback to
    
    ⚠️ **Warning**: This is an emergency operation that should only be used
    if the current key is corrupted or compromised.
    """
    manager = get_rotation_manager()
    
    try:
        result = await manager.rollback_to_version(request.target_version)
        
        return RotationResponse(
            success=result['success'],
            old_version=result.get('from_version'),
            new_version=result.get('to_version'),
            duration_seconds=result['duration_seconds'],
            trigger_type="rollback",
            message=f"Successfully rolled back to key version {request.target_version}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Key rollback failed: {str(e)}"
        )

@router.get("/policy")
async def get_rotation_policy(_token: str = Depends(verify_token)):
    """Get current key rotation policy settings"""
    manager = get_rotation_manager()
    
    try:
        metadata = manager.export_key_metadata()
        return metadata.get('policy', {})
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get rotation policy: {str(e)}"
        )

@router.put("/policy")
async def update_rotation_policy(
    request: PolicyUpdateRequest,
    _token: str = Depends(verify_token)
):
    """
    Update key rotation policy settings
    
    - **rotation_interval_days**: Days between automatic rotations (1-365)
    - **max_key_versions**: Maximum key versions to retain (1-10)
    - **auto_rotation_enabled**: Enable/disable automatic rotation
    - **performance_threshold_seconds**: Max acceptable rotation time (0.1-60.0)
    """
    manager = get_rotation_manager()
    
    try:
        # Update policy settings
        policy_updates = request.dict(exclude_unset=True)
        
        for key, value in policy_updates.items():
            if hasattr(manager.policy, key):
                setattr(manager.policy, key, value)
        
        return {
            "message": "Rotation policy updated successfully",
            "updated_settings": policy_updates,
            "current_policy": {
                "rotation_interval_days": manager.policy.rotation_interval_days,
                "max_key_versions": manager.policy.max_key_versions,
                "auto_rotation_enabled": manager.policy.auto_rotation_enabled,
                "performance_threshold_seconds": manager.policy.performance_threshold_seconds
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update rotation policy: {str(e)}"
        )

@router.get("/metrics")
async def get_prometheus_metrics(_token: str = Depends(verify_token)):
    """
    Get Prometheus metrics for key rotation monitoring
    
    Returns metrics in Prometheus format for Grafana integration:
    - vault_key_rotation_total: Total rotations performed
    - vault_key_rotation_timestamp: Last rotation timestamp
    - vault_key_version_count: Number of key versions stored
    - vault_key_rotation_duration_seconds: Rotation duration histogram
    """
    try:
        metrics_output = generate_latest()
        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate metrics: {str(e)}"
        )

@router.post("/verify-keys")
async def verify_key_integrity(_token: str = Depends(verify_token)):
    """
    Verify that all stored key versions can successfully decrypt test data
    
    This endpoint performs integrity checks on all key versions to ensure
    they are valid and can be used for decryption if needed.
    """
    manager = get_rotation_manager()
    
    try:
        # Test data for verification
        test_data = b"Hearthlink key rotation verification test"
        verification_results = []
        
        versions = manager.list_key_versions()
        
        for version_info in versions:
            version = version_info['version']
            try:
                # Get the key version
                key_version = manager.get_key_by_version(version)
                if not key_version:
                    verification_results.append({
                        'version': version,
                        'status': 'error',
                        'error': 'Key version not found'
                    })
                    continue
                
                # Test encryption/decryption
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                import secrets
                
                aesgcm = AESGCM(key_version.key_data)
                nonce = secrets.token_bytes(12)
                ciphertext = aesgcm.encrypt(nonce, test_data, None)
                decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                
                if decrypted == test_data:
                    verification_results.append({
                        'version': version,
                        'status': 'valid',
                        'is_active': version_info['is_active']
                    })
                else:
                    verification_results.append({
                        'version': version,
                        'status': 'error',
                        'error': 'Decryption mismatch'
                    })
                    
            except Exception as e:
                verification_results.append({
                    'version': version,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Summary
        total_versions = len(verification_results)
        valid_versions = len([r for r in verification_results if r['status'] == 'valid'])
        error_versions = total_versions - valid_versions
        
        return {
            'summary': {
                'total_versions': total_versions,
                'valid_versions': valid_versions,
                'error_versions': error_versions,
                'all_valid': error_versions == 0
            },
            'results': verification_results,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Key verification failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the key rotation system"""
    manager = get_rotation_manager()
    
    try:
        current_key = manager.get_current_key()
        should_rotate, reason = manager.should_rotate()
        
        return {
            "status": "healthy",
            "current_key_version": current_key.version,
            "rotation_due": should_rotate,
            "auto_rotation_enabled": manager.policy.auto_rotation_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Key rotation system unhealthy: {str(e)}"
        )

# FastAPI Response import
from fastapi import Response