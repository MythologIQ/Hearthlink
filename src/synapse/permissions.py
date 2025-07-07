"""
Permission Management System

Handles plugin permission validation, enforcement, and user approval workflows.
All plugin permissions must be explicitly approved by the user.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

from .manifest import PermissionType

class PermissionStatus(Enum):
    """Permission approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"

@dataclass
class PermissionRequest:
    """Permission request record."""
    request_id: str
    plugin_id: str
    user_id: str
    permissions: List[str]
    status: PermissionStatus
    requested_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    reason: Optional[str] = None
    risk_assessment: Optional[int] = None

@dataclass
class PermissionGrant:
    """Active permission grant."""
    grant_id: str
    plugin_id: str
    user_id: str
    permissions: List[str]
    granted_at: str
    expires_at: Optional[str] = None
    granted_by: str
    conditions: Dict[str, Any] = field(default_factory=dict)

class PermissionManager:
    """Manages plugin permissions and approval workflows."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Active permission grants
        self.grants: Dict[str, PermissionGrant] = {}
        
        # Permission requests
        self.requests: Dict[str, PermissionRequest] = {}
        
        # Risk thresholds for automatic approval
        self.risk_thresholds = {
            PermissionType.READ_VAULT.value: 10,
            PermissionType.WRITE_VAULT.value: 50,
            PermissionType.READ_CORE.value: 5,
            PermissionType.WRITE_CORE.value: 30,
            PermissionType.NETWORK_ACCESS.value: 40,
            PermissionType.FILE_SYSTEM.value: 60,
            PermissionType.SYSTEM_COMMANDS.value: 80,
            PermissionType.EXTERNAL_API.value: 35
        }
        
        # Permission dependencies
        self.permission_dependencies = {
            PermissionType.WRITE_VAULT.value: [PermissionType.READ_VAULT.value],
            PermissionType.WRITE_CORE.value: [PermissionType.READ_CORE.value],
            PermissionType.EXTERNAL_API.value: [PermissionType.NETWORK_ACCESS.value]
        }
    
    def request_permissions(self, plugin_id: str, user_id: str, 
                          permissions: List[str]) -> str:
        """
        Request permissions for a plugin.
        
        Args:
            plugin_id: Plugin requesting permissions
            user_id: User making the request
            permissions: List of permission types requested
            
        Returns:
            Request ID
        """
        request_id = f"perm-{uuid.uuid4().hex[:8]}"
        
        # Validate permissions
        valid_permissions = self._validate_permissions(permissions)
        if not valid_permissions:
            raise ValueError("Invalid permissions requested")
        
        # Check for dependencies
        all_permissions = self._resolve_dependencies(valid_permissions)
        
        # Assess risk
        risk_score = self._assess_permission_risk(all_permissions)
        
        # Create request
        request = PermissionRequest(
            request_id=request_id,
            plugin_id=plugin_id,
            user_id=user_id,
            permissions=all_permissions,
            status=PermissionStatus.PENDING,
            requested_at=datetime.now().isoformat(),
            risk_assessment=risk_score
        )
        
        self.requests[request_id] = request
        
        self.logger.info(f"Permission request created: {request_id} for {plugin_id}")
        
        return request_id
    
    def approve_permissions(self, request_id: str, user_id: str, 
                          reason: Optional[str] = None) -> bool:
        """
        Approve a permission request.
        
        Args:
            request_id: Request to approve
            user_id: User approving the request
            reason: Optional reason for approval
            
        Returns:
            Success status
        """
        if request_id not in self.requests:
            self.logger.error(f"Permission request not found: {request_id}")
            return False
        
        request = self.requests[request_id]
        
        # Update request status
        request.status = PermissionStatus.APPROVED
        request.reviewed_at = datetime.now().isoformat()
        request.reviewed_by = user_id
        request.reason = reason
        
        # Create permission grant
        grant_id = f"grant-{uuid.uuid4().hex[:8]}"
        grant = PermissionGrant(
            grant_id=grant_id,
            plugin_id=request.plugin_id,
            user_id=request.user_id,
            permissions=request.permissions,
            granted_at=datetime.now().isoformat(),
            granted_by=user_id
        )
        
        self.grants[grant_id] = grant
        
        self.logger.info(f"Permissions approved: {request_id} -> {grant_id}")
        
        return True
    
    def deny_permissions(self, request_id: str, user_id: str, 
                        reason: str) -> bool:
        """
        Deny a permission request.
        
        Args:
            request_id: Request to deny
            user_id: User denying the request
            reason: Reason for denial
            
        Returns:
            Success status
        """
        if request_id not in self.requests:
            self.logger.error(f"Permission request not found: {request_id}")
            return False
        
        request = self.requests[request_id]
        request.status = PermissionStatus.DENIED
        request.reviewed_at = datetime.now().isoformat()
        request.reviewed_by = user_id
        request.reason = reason
        
        self.logger.info(f"Permissions denied: {request_id}")
        
        return True
    
    def revoke_permissions(self, plugin_id: str, user_id: str, 
                          reason: str) -> bool:
        """
        Revoke all permissions for a plugin.
        
        Args:
            plugin_id: Plugin to revoke permissions from
            user_id: User revoking permissions
            reason: Reason for revocation
            
        Returns:
            Success status
        """
        revoked_count = 0
        
        # Find and remove grants for this plugin
        grants_to_remove = []
        for grant_id, grant in self.grants.items():
            if grant.plugin_id == plugin_id:
                grants_to_remove.append(grant_id)
        
        for grant_id in grants_to_remove:
            del self.grants[grant_id]
            revoked_count += 1
        
        # Update any pending requests
        for request in self.requests.values():
            if request.plugin_id == plugin_id and request.status == PermissionStatus.PENDING:
                request.status = PermissionStatus.REVOKED
                request.reviewed_at = datetime.now().isoformat()
                request.reviewed_by = user_id
                request.reason = reason
        
        self.logger.info(f"Revoked {revoked_count} permission grants for {plugin_id}")
        
        return revoked_count > 0
    
    def check_permission(self, plugin_id: str, permission: str) -> bool:
        """
        Check if a plugin has a specific permission.
        
        Args:
            plugin_id: Plugin to check
            permission: Permission to check
            
        Returns:
            True if permission is granted
        """
        for grant in self.grants.values():
            if grant.plugin_id == plugin_id and permission in grant.permissions:
                # Check if grant has expired
                if grant.expires_at:
                    if datetime.fromisoformat(grant.expires_at) < datetime.now():
                        continue
                return True
        
        return False
    
    def get_plugin_permissions(self, plugin_id: str) -> List[str]:
        """
        Get all permissions for a plugin.
        
        Args:
            plugin_id: Plugin to get permissions for
            
        Returns:
            List of granted permissions
        """
        permissions = set()
        
        for grant in self.grants.values():
            if grant.plugin_id == plugin_id:
                # Check if grant has expired
                if grant.expires_at:
                    if datetime.fromisoformat(grant.expires_at) < datetime.now():
                        continue
                permissions.update(grant.permissions)
        
        return list(permissions)
    
    def get_pending_requests(self) -> List[PermissionRequest]:
        """Get all pending permission requests."""
        return [req for req in self.requests.values() 
                if req.status == PermissionStatus.PENDING]
    
    def get_plugin_grants(self, plugin_id: str) -> List[PermissionGrant]:
        """Get all active grants for a plugin."""
        return [grant for grant in self.grants.values() 
                if grant.plugin_id == plugin_id]
    
    def _validate_permissions(self, permissions: List[str]) -> List[str]:
        """Validate permission types."""
        valid_permissions = []
        allowed_permissions = [p.value for p in PermissionType]
        
        for permission in permissions:
            if permission in allowed_permissions:
                valid_permissions.append(permission)
            else:
                self.logger.warning(f"Invalid permission: {permission}")
        
        return valid_permissions
    
    def _resolve_dependencies(self, permissions: List[str]) -> List[str]:
        """Resolve permission dependencies."""
        all_permissions = set(permissions)
        
        for permission in permissions:
            if permission in self.permission_dependencies:
                dependencies = self.permission_dependencies[permission]
                all_permissions.update(dependencies)
        
        return list(all_permissions)
    
    def _assess_permission_risk(self, permissions: List[str]) -> int:
        """Assess risk score for permission combination."""
        total_risk = 0
        
        for permission in permissions:
            risk = self.risk_thresholds.get(permission, 50)
            total_risk += risk
        
        # Normalize to 0-100 scale
        return min(100, total_risk // len(permissions) if permissions else 0)
    
    def export_permissions(self) -> Dict[str, Any]:
        """Export all permission data."""
        return {
            "grants": [asdict(grant) for grant in self.grants.values()],
            "requests": [asdict(request) for request in self.requests.values()],
            "exported_at": datetime.now().isoformat()
        }
    
    def import_permissions(self, data: Dict[str, Any]) -> bool:
        """Import permission data."""
        try:
            # Clear existing data
            self.grants.clear()
            self.requests.clear()
            
            # Import grants
            for grant_data in data.get("grants", []):
                grant = PermissionGrant(**grant_data)
                self.grants[grant.grant_id] = grant
            
            # Import requests
            for request_data in data.get("requests", []):
                request = PermissionRequest(**request_data)
                self.requests[request.request_id] = request
            
            self.logger.info("Permissions imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import permissions: {e}")
            return False 