"""
Permission Management System

Handles plugin permission validation, enforcement, and user approval workflows.
All plugin permissions must be explicitly approved by the user.
Enhanced with multi-level permissions, granular access control, and improved risk assessment.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

from .manifest import PermissionType, PermissionLevel, PermissionRequest

class PermissionStatus(Enum):
    """Permission approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"

@dataclass
class PermissionRequest:
    """Enhanced permission request record."""
    request_id: str
    plugin_id: str
    user_id: str
    permissions: List[Dict[str, Any]]  # Enhanced permission structure
    status: PermissionStatus
    requested_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    reason: Optional[str] = None
    risk_assessment: Optional[int] = None
    auto_approved: bool = False

@dataclass
class PermissionGrant:
    """Enhanced active permission grant."""
    grant_id: str
    plugin_id: str
    user_id: str
    permissions: List[Dict[str, Any]]  # Enhanced permission structure
    granted_at: str
    expires_at: Optional[str] = None
    granted_by: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    scope_restrictions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PermissionAudit:
    """Permission audit record."""
    audit_id: str
    timestamp: str
    user_id: str
    plugin_id: str
    action: str
    permission: str
    level: str
    scope: Optional[str] = None
    result: str
    details: Dict[str, Any] = field(default_factory=dict)

class PermissionManager:
    """Enhanced permission management system with multi-level support."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Active permission grants
        self.grants: Dict[str, PermissionGrant] = {}
        
        # Permission requests
        self.requests: Dict[str, PermissionRequest] = {}
        
        # Audit trail
        self.audit_log: List[PermissionAudit] = []
        
        # Enhanced risk thresholds for multi-level permissions
        self.risk_thresholds = {
            # Vault permissions
            PermissionType.VAULT_READ.value: {"low": 5, "moderate": 10, "high": 20},
            PermissionType.VAULT_WRITE.value: {"low": 20, "moderate": 40, "high": 60},
            PermissionType.VAULT_ADMIN.value: {"low": 50, "moderate": 70, "high": 90},
            
            # Core permissions
            PermissionType.CORE_READ.value: {"low": 3, "moderate": 8, "high": 15},
            PermissionType.CORE_WRITE.value: {"low": 15, "moderate": 30, "high": 50},
            PermissionType.CORE_ADMIN.value: {"low": 40, "moderate": 60, "high": 80},
            
            # Network permissions
            PermissionType.NETWORK_READ.value: {"low": 10, "moderate": 20, "high": 35},
            PermissionType.NETWORK_WRITE.value: {"low": 25, "moderate": 45, "high": 65},
            PermissionType.NETWORK_ADMIN.value: {"low": 60, "moderate": 80, "high": 95},
            
            # File system permissions
            PermissionType.FILE_READ.value: {"low": 8, "moderate": 15, "high": 25},
            PermissionType.FILE_WRITE.value: {"low": 20, "moderate": 35, "high": 55},
            PermissionType.FILE_EXECUTE.value: {"low": 30, "moderate": 50, "high": 70},
            PermissionType.FILE_ADMIN.value: {"low": 70, "moderate": 85, "high": 95},
            
            # System permissions
            PermissionType.SYSTEM_READ.value: {"low": 5, "moderate": 12, "high": 20},
            PermissionType.SYSTEM_WRITE.value: {"low": 25, "moderate": 45, "high": 65},
            PermissionType.SYSTEM_EXECUTE.value: {"low": 40, "moderate": 60, "high": 80},
            PermissionType.SYSTEM_ADMIN.value: {"low": 80, "moderate": 90, "high": 100},
            
            # External API permissions
            PermissionType.API_READ.value: {"low": 8, "moderate": 18, "high": 30},
            PermissionType.API_WRITE.value: {"low": 20, "moderate": 40, "high": 60},
            PermissionType.API_ADMIN.value: {"low": 50, "moderate": 70, "high": 85},
            
            # Plugin ecosystem permissions
            PermissionType.PLUGIN_READ.value: {"low": 3, "moderate": 8, "high": 15},
            PermissionType.PLUGIN_WRITE.value: {"low": 15, "moderate": 30, "high": 50},
            PermissionType.PLUGIN_ADMIN.value: {"low": 40, "moderate": 60, "high": 80},
            
            # User data permissions
            PermissionType.USER_READ.value: {"low": 10, "moderate": 20, "high": 35},
            PermissionType.USER_WRITE.value: {"low": 25, "moderate": 45, "high": 65},
            PermissionType.USER_ADMIN.value: {"low": 60, "moderate": 80, "high": 95}
        }
        
        # Enhanced permission dependencies
        self.permission_dependencies = {
            PermissionType.VAULT_WRITE.value: [PermissionType.VAULT_READ.value],
            PermissionType.VAULT_ADMIN.value: [PermissionType.VAULT_READ.value, PermissionType.VAULT_WRITE.value],
            PermissionType.CORE_WRITE.value: [PermissionType.CORE_READ.value],
            PermissionType.CORE_ADMIN.value: [PermissionType.CORE_READ.value, PermissionType.CORE_WRITE.value],
            PermissionType.NETWORK_WRITE.value: [PermissionType.NETWORK_READ.value],
            PermissionType.NETWORK_ADMIN.value: [PermissionType.NETWORK_READ.value, PermissionType.NETWORK_WRITE.value],
            PermissionType.FILE_WRITE.value: [PermissionType.FILE_READ.value],
            PermissionType.FILE_EXECUTE.value: [PermissionType.FILE_READ.value],
            PermissionType.FILE_ADMIN.value: [PermissionType.FILE_READ.value, PermissionType.FILE_WRITE.value],
            PermissionType.SYSTEM_WRITE.value: [PermissionType.SYSTEM_READ.value],
            PermissionType.SYSTEM_EXECUTE.value: [PermissionType.SYSTEM_READ.value],
            PermissionType.SYSTEM_ADMIN.value: [PermissionType.SYSTEM_READ.value, PermissionType.SYSTEM_WRITE.value],
            PermissionType.API_WRITE.value: [PermissionType.API_READ.value],
            PermissionType.API_ADMIN.value: [PermissionType.API_READ.value, PermissionType.API_WRITE.value],
            PermissionType.PLUGIN_WRITE.value: [PermissionType.PLUGIN_READ.value],
            PermissionType.PLUGIN_ADMIN.value: [PermissionType.PLUGIN_READ.value, PermissionType.PLUGIN_WRITE.value],
            PermissionType.USER_WRITE.value: [PermissionType.USER_READ.value],
            PermissionType.USER_ADMIN.value: [PermissionType.USER_READ.value, PermissionType.USER_WRITE.value]
        }
        
        # Permission level hierarchy
        self.permission_levels = {
            PermissionLevel.READ.value: 1,
            PermissionLevel.WRITE.value: 2,
            PermissionLevel.EXECUTE.value: 3,
            PermissionLevel.ADMIN.value: 4
        }
    
    def request_permissions(self, plugin_id: str, user_id: str, 
                          permissions: List[Dict[str, Any]]) -> str:
        """
        Request enhanced permissions for a plugin.
        
        Args:
            plugin_id: Plugin requesting permissions
            user_id: User making the request
            permissions: List of enhanced permission requests
            
        Returns:
            Request ID
        """
        request_id = f"perm-{uuid.uuid4().hex[:8]}"
        
        # Validate permissions
        valid_permissions = self._validate_enhanced_permissions(permissions)
        if not valid_permissions:
            raise ValueError("Invalid permissions requested")
        
        # Check for dependencies
        all_permissions = self._resolve_enhanced_dependencies(valid_permissions)
        
        # Assess risk
        risk_score = self._assess_enhanced_permission_risk(all_permissions)
        
        # Check for auto-approval
        auto_approved = self._check_auto_approval(all_permissions, risk_score)
        
        # Create request
        request = PermissionRequest(
            request_id=request_id,
            plugin_id=plugin_id,
            user_id=user_id,
            permissions=all_permissions,
            status=PermissionStatus.APPROVED if auto_approved else PermissionStatus.PENDING,
            requested_at=datetime.now().isoformat(),
            risk_assessment=risk_score,
            auto_approved=auto_approved
        )
        
        self.requests[request_id] = request
        
        # Auto-approve if applicable
        if auto_approved:
            self._auto_approve_permissions(request_id, user_id)
        
        self.logger.info(f"Permission request created: {request_id} for {plugin_id} (auto_approved: {auto_approved})")
        
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
        
        # Add audit record
        self._add_audit_record(user_id, request.plugin_id, "approve", 
                             request.permissions, "approved", {"reason": reason})
        
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
        
        # Add audit record
        self._add_audit_record(user_id, request.plugin_id, "deny", 
                             request.permissions, "denied", {"reason": reason})
        
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
        
        # Find and revoke all grants for this plugin
        grants_to_revoke = [
            grant_id for grant_id, grant in self.grants.items()
            if grant.plugin_id == plugin_id
        ]
        
        for grant_id in grants_to_revoke:
            grant = self.grants[grant_id]
            
            # Add audit record
            self._add_audit_record(user_id, plugin_id, "revoke", 
                                 grant.permissions, "revoked", {"reason": reason})
            
            del self.grants[grant_id]
            revoked_count += 1
        
        # Update request status
        for request in self.requests.values():
            if request.plugin_id == plugin_id and request.status == PermissionStatus.APPROVED:
                request.status = PermissionStatus.REVOKED
                request.reviewed_at = datetime.now().isoformat()
                request.reviewed_by = user_id
                request.reason = reason
        
        self.logger.info(f"Revoked {revoked_count} permission grants for plugin: {plugin_id}")
        
        return revoked_count > 0
    
    def check_permission(self, plugin_id: str, permission: str, level: str = "read", 
                        scope: Optional[str] = None) -> bool:
        """
        Check if a plugin has a specific permission.
        
        Args:
            plugin_id: Plugin to check
            permission: Permission to check
            level: Permission level required
            scope: Optional scope restriction
            
        Returns:
            True if permission is granted
        """
        # Find active grants for this plugin
        active_grants = [
            grant for grant in self.grants.values()
            if grant.plugin_id == plugin_id and self._is_grant_active(grant)
        ]
        
        if not active_grants:
            return False
        
        # Check each grant for the required permission
        for grant in active_grants:
            for perm_data in grant.permissions:
                if (perm_data.get('permission') == permission and
                    self._check_permission_level(perm_data.get('level', 'read'), level) and
                    self._check_permission_scope(perm_data.get('scope'), scope)):
                    return True
        
        return False
    
    def get_plugin_permissions(self, plugin_id: str) -> List[Dict[str, Any]]:
        """
        Get all active permissions for a plugin.
        
        Args:
            plugin_id: Plugin to get permissions for
            
        Returns:
            List of active permissions
        """
        permissions = []
        
        # Find active grants for this plugin
        active_grants = [
            grant for grant in self.grants.values()
            if grant.plugin_id == plugin_id and self._is_grant_active(grant)
        ]
        
        for grant in active_grants:
            permissions.extend(grant.permissions)
        
        return permissions
    
    def get_pending_requests(self) -> List[PermissionRequest]:
        """Get all pending permission requests."""
        return [
            request for request in self.requests.values()
            if request.status == PermissionStatus.PENDING
        ]
    
    def get_plugin_grants(self, plugin_id: str) -> List[PermissionGrant]:
        """Get all permission grants for a plugin."""
        return [
            grant for grant in self.grants.values()
            if grant.plugin_id == plugin_id
        ]
    
    def _validate_enhanced_permissions(self, permissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate enhanced permission structure."""
        valid_permissions = []
        
        for perm in permissions:
            if not isinstance(perm, dict):
                continue
            
            # Check required fields
            if 'permission' not in perm or 'level' not in perm:
                continue
            
            permission = perm['permission']
            level = perm['level']
            
            # Validate permission type
            if permission not in [p.value for p in PermissionType]:
                continue
            
            # Validate permission level
            if level not in [l.value for l in PermissionLevel]:
                continue
            
            valid_permissions.append(perm)
        
        return valid_permissions
    
    def _resolve_enhanced_dependencies(self, permissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve dependencies for enhanced permissions."""
        all_permissions = permissions.copy()
        
        for perm in permissions:
            permission = perm['permission']
            
            if permission in self.permission_dependencies:
                for dep in self.permission_dependencies[permission]:
                    # Check if dependency already exists
                    dep_exists = any(p['permission'] == dep for p in all_permissions)
                    
                    if not dep_exists:
                        # Add dependency with read level
                        all_permissions.append({
                            'permission': dep,
                            'level': 'read',
                            'scope': perm.get('scope'),
                            'conditions': perm.get('conditions', {})
                        })
        
        return all_permissions
    
    def _assess_enhanced_permission_risk(self, permissions: List[Dict[str, Any]]) -> int:
        """Assess risk for enhanced permissions."""
        total_risk = 0
        
        for perm in permissions:
            permission = perm['permission']
            level = perm.get('level', 'read')
            
            if permission in self.risk_thresholds:
                level_thresholds = self.risk_thresholds[permission]
                level_key = self._get_risk_level_key(level)
                risk_score = level_thresholds.get(level_key, level_thresholds.get('moderate', 50))
                total_risk += risk_score
        
        return min(total_risk, 100)  # Cap at 100
    
    def _get_risk_level_key(self, level: str) -> str:
        """Get risk level key based on permission level."""
        level_hierarchy = {
            'read': 'low',
            'write': 'moderate',
            'execute': 'high',
            'admin': 'high'
        }
        return level_hierarchy.get(level, 'moderate')
    
    def _check_auto_approval(self, permissions: List[Dict[str, Any]], risk_score: int) -> bool:
        """Check if permissions can be auto-approved."""
        # Auto-approve if risk score is low and all permissions are basic
        if risk_score <= 20:
            return True
        
        # Auto-approve read-only permissions with low risk
        if risk_score <= 30 and all(perm.get('level') == 'read' for perm in permissions):
            return True
        
        return False
    
    def _auto_approve_permissions(self, request_id: str, user_id: str):
        """Auto-approve permissions."""
        request = self.requests[request_id]
        
        # Create permission grant
        grant_id = f"grant-{uuid.uuid4().hex[:8]}"
        grant = PermissionGrant(
            grant_id=grant_id,
            plugin_id=request.plugin_id,
            user_id=request.user_id,
            permissions=request.permissions,
            granted_at=datetime.now().isoformat(),
            granted_by="system"
        )
        
        self.grants[grant_id] = grant
        
        # Add audit record
        self._add_audit_record("system", request.plugin_id, "auto_approve", 
                             request.permissions, "approved", {"reason": "auto_approval"})
    
    def _check_permission_level(self, granted_level: str, required_level: str) -> bool:
        """Check if granted level satisfies required level."""
        granted_hierarchy = self.permission_levels.get(granted_level, 0)
        required_hierarchy = self.permission_levels.get(required_level, 0)
        return granted_hierarchy >= required_hierarchy
    
    def _check_permission_scope(self, granted_scope: Optional[str], required_scope: Optional[str]) -> bool:
        """Check if granted scope satisfies required scope."""
        if required_scope is None:
            return True
        
        if granted_scope is None:
            return False
        
        # Simple scope matching - can be enhanced with pattern matching
        return granted_scope == required_scope or granted_scope == "*"
    
    def _is_grant_active(self, grant: PermissionGrant) -> bool:
        """Check if a permission grant is still active."""
        if grant.expires_at:
            try:
                expiry = datetime.fromisoformat(grant.expires_at)
                if datetime.now() > expiry:
                    return False
            except ValueError:
                pass
        
        return True
    
    def _add_audit_record(self, user_id: str, plugin_id: str, action: str, 
                         permissions: List[Dict[str, Any]], result: str, details: Dict[str, Any]):
        """Add an audit record."""
        audit = PermissionAudit(
            audit_id=f"audit-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            plugin_id=plugin_id,
            action=action,
            permission=", ".join([p.get('permission', '') for p in permissions]),
            level=", ".join([p.get('level', '') for p in permissions]),
            scope=", ".join([p.get('scope', '') for p in permissions if p.get('scope')]),
            result=result,
            details=details
        )
        
        self.audit_log.append(audit)
    
    def export_permissions(self) -> Dict[str, Any]:
        """Export all permission data."""
        return {
            "grants": [asdict(grant) for grant in self.grants.values()],
            "requests": [asdict(request) for request in self.requests.values()],
            "audit_log": [asdict(audit) for audit in self.audit_log]
        }
    
    def import_permissions(self, data: Dict[str, Any]) -> bool:
        """Import permission data."""
        try:
            # Clear existing data
            self.grants.clear()
            self.requests.clear()
            self.audit_log.clear()
            
            # Import grants
            for grant_data in data.get("grants", []):
                grant = PermissionGrant(**grant_data)
                self.grants[grant.grant_id] = grant
            
            # Import requests
            for request_data in data.get("requests", []):
                request = PermissionRequest(**request_data)
                self.requests[request.request_id] = request
            
            # Import audit log
            for audit_data in data.get("audit_log", []):
                audit = PermissionAudit(**audit_data)
                self.audit_log.append(audit)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing permissions: {e}")
            return False 