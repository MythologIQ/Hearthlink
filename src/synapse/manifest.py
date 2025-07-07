"""
Plugin Manifest System

Handles plugin manifest validation, signing, and schema enforcement.
All plugins must declare capabilities, permissions, version, and sandboxing requirements.
Enhanced with multi-level permissions, lifecycle events, and expanded capabilities.
"""

import json
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

class RiskTier(Enum):
    """Plugin risk tiers."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class PermissionLevel(Enum):
    """Permission access levels."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class PermissionType(Enum):
    """Plugin permission types with multi-level support."""
    # Vault permissions
    VAULT_READ = "vault_read"
    VAULT_WRITE = "vault_write"
    VAULT_ADMIN = "vault_admin"
    
    # Core permissions
    CORE_READ = "core_read"
    CORE_WRITE = "core_write"
    CORE_ADMIN = "core_admin"
    
    # Network permissions
    NETWORK_READ = "network_read"
    NETWORK_WRITE = "network_write"
    NETWORK_ADMIN = "network_admin"
    
    # File system permissions
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EXECUTE = "file_execute"
    FILE_ADMIN = "file_admin"
    
    # System permissions
    SYSTEM_READ = "system_read"
    SYSTEM_WRITE = "system_write"
    SYSTEM_EXECUTE = "system_execute"
    SYSTEM_ADMIN = "system_admin"
    
    # External API permissions
    API_READ = "api_read"
    API_WRITE = "api_write"
    API_ADMIN = "api_admin"
    
    # Plugin ecosystem permissions
    PLUGIN_READ = "plugin_read"
    PLUGIN_WRITE = "plugin_write"
    PLUGIN_ADMIN = "plugin_admin"
    
    # User data permissions
    USER_READ = "user_read"
    USER_WRITE = "user_write"
    USER_ADMIN = "user_admin"

class PluginLifecycleEvent(Enum):
    """Plugin lifecycle events."""
    REGISTERED = "registered"
    APPROVED = "approved"
    ACTIVATED = "activated"
    SUSPENDED = "suspended"
    UPDATED = "updated"
    RELOADED = "reloaded"
    REVOKED = "revoked"
    UNINSTALLED = "uninstalled"

@dataclass
class PermissionRequest:
    """Enhanced permission request with multi-level support."""
    permission: str
    level: PermissionLevel
    scope: Optional[str] = None  # Specific resource scope
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[str] = None

@dataclass
class BenchmarkResult:
    """Plugin benchmark results."""
    avg_response_ms: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    throughput: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AuditEvent:
    """Plugin audit event."""
    event_id: str
    event_type: str
    timestamp: str
    user_id: str
    plugin_id: str
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: Optional[int] = None
    resolution: Optional[str] = None

@dataclass
class LifecycleEvent:
    """Plugin lifecycle event record."""
    event_id: str
    event_type: PluginLifecycleEvent
    timestamp: str
    user_id: str
    plugin_id: str
    details: Dict[str, Any] = field(default_factory=dict)
    previous_state: Optional[str] = None
    new_state: Optional[str] = None

@dataclass
class PluginCapability:
    """Plugin capability definition."""
    name: str
    description: str
    version: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: Optional[str] = None
    async_support: bool = False
    batch_support: bool = False

@dataclass
class PluginManifest:
    """Enhanced plugin manifest schema."""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    manifest_version: str = "2.0.0"  # Updated version for enhanced features
    
    # Enhanced permissions
    requested_permissions: List[PermissionRequest] = field(default_factory=list)
    
    # Plugin capabilities
    capabilities: List[PluginCapability] = field(default_factory=list)
    
    # Lifecycle hooks
    lifecycle_hooks: Dict[str, str] = field(default_factory=dict)
    
    # Sandbox configuration
    sandbox: bool = True
    sandbox_config: Dict[str, Any] = field(default_factory=dict)
    
    # Risk and security
    risk_tier: RiskTier = RiskTier.MODERATE
    security_scan: bool = True
    code_review_required: bool = False
    
    # Performance and monitoring
    performance_monitoring: bool = True
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    
    # User approval
    approved_by_user: bool = False
    auto_approve: bool = False
    
    # Signing and validation
    manifest_signature: Optional[str] = None
    code_signature: Optional[str] = None
    
    # Monitoring and audit
    benchmarks: Optional[BenchmarkResult] = None
    audit_log: List[AuditEvent] = field(default_factory=list)
    lifecycle_events: List[LifecycleEvent] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_reload: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        data = asdict(self)
        data['risk_tier'] = self.risk_tier.value
        if self.benchmarks:
            data['benchmarks'] = asdict(self.benchmarks)
        return data
    
    def to_json(self) -> str:
        """Convert manifest to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def calculate_signature(self) -> str:
        """Calculate manifest signature."""
        # Create signature from immutable fields
        signature_data = {
            'plugin_id': self.plugin_id,
            'name': self.name,
            'version': self.version,
            'manifest_version': self.manifest_version,
            'requested_permissions': [
                {
                    'permission': p.permission,
                    'level': p.level.value,
                    'scope': p.scope
                }
                for p in self.requested_permissions
            ],
            'sandbox': self.sandbox,
            'risk_tier': self.risk_tier.value
        }
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    def validate_signature(self) -> bool:
        """Validate manifest signature."""
        if not self.manifest_signature:
            return False
        return self.manifest_signature == self.calculate_signature()
    
    def add_lifecycle_event(self, event_type: PluginLifecycleEvent, user_id: str, 
                          details: Optional[Dict[str, Any]] = None,
                          previous_state: Optional[str] = None,
                          new_state: Optional[str] = None):
        """Add a lifecycle event to the manifest."""
        event = LifecycleEvent(
            event_id=f"lifecycle-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            plugin_id=self.plugin_id,
            details=details or {},
            previous_state=previous_state,
            new_state=new_state
        )
        self.lifecycle_events.append(event)
        self.updated_at = datetime.now().isoformat()
    
    def add_audit_event(self, event_type: str, user_id: str, details: Dict[str, Any],
                       risk_score: Optional[int] = None, resolution: Optional[str] = None):
        """Add an audit event to the manifest."""
        event = AuditEvent(
            event_id=f"audit-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            plugin_id=self.plugin_id,
            details=details,
            risk_score=risk_score,
            resolution=resolution
        )
        self.audit_log.append(event)
        self.updated_at = datetime.now().isoformat()

class ManifestValidator:
    """Enhanced manifest validator with multi-level permission support."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.required_fields = [
            'plugin_id', 'name', 'version', 'description', 'author'
        ]
        self.allowed_permissions = [p.value for p in PermissionType]
        self.allowed_levels = [l.value for l in PermissionLevel]
        self.max_permissions = 20  # Increased for multi-level permissions
        self.max_name_length = 100
        self.max_description_length = 500
        self.max_capabilities = 50
    
    def validate_manifest(self, manifest_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate plugin manifest.
        
        Args:
            manifest_data: Manifest data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in manifest_data:
                errors.append(f"Missing required field: {field}")
            elif not manifest_data[field]:
                errors.append(f"Required field cannot be empty: {field}")
        
        # Validate plugin_id format
        if 'plugin_id' in manifest_data:
            plugin_id = manifest_data['plugin_id']
            if not self._validate_plugin_id(plugin_id):
                errors.append("Invalid plugin_id format. Must be alphanumeric with hyphens/underscores")
        
        # Validate version format
        if 'version' in manifest_data:
            version = manifest_data['version']
            if not self._validate_version(version):
                errors.append("Invalid version format. Must be semantic version (e.g., 1.0.0)")
        
        # Validate enhanced permissions
        if 'requested_permissions' in manifest_data:
            permissions = manifest_data['requested_permissions']
            if not isinstance(permissions, list):
                errors.append("requested_permissions must be a list")
            else:
                if len(permissions) > self.max_permissions:
                    errors.append(f"Too many permissions requested. Maximum: {self.max_permissions}")
                
                for permission in permissions:
                    perm_errors = self._validate_permission_request(permission)
                    errors.extend(perm_errors)
        
        # Validate capabilities
        if 'capabilities' in manifest_data:
            capabilities = manifest_data['capabilities']
            if not isinstance(capabilities, list):
                errors.append("capabilities must be a list")
            else:
                if len(capabilities) > self.max_capabilities:
                    errors.append(f"Too many capabilities. Maximum: {self.max_capabilities}")
                
                for capability in capabilities:
                    cap_errors = self._validate_capability(capability)
                    errors.extend(cap_errors)
        
        # Validate lifecycle hooks
        if 'lifecycle_hooks' in manifest_data:
            hooks = manifest_data['lifecycle_hooks']
            if not isinstance(hooks, dict):
                errors.append("lifecycle_hooks must be a dictionary")
            else:
                for event_type, handler in hooks.items():
                    if event_type not in [e.value for e in PluginLifecycleEvent]:
                        errors.append(f"Invalid lifecycle event: {event_type}")
        
        # Validate string lengths
        if 'name' in manifest_data and len(manifest_data['name']) > self.max_name_length:
            errors.append(f"Name too long. Maximum: {self.max_name_length} characters")
        
        if 'description' in manifest_data and len(manifest_data['description']) > self.max_description_length:
            errors.append(f"Description too long. Maximum: {self.max_description_length} characters")
        
        # Validate risk tier
        if 'risk_tier' in manifest_data:
            risk_tier = manifest_data['risk_tier']
            try:
                RiskTier(risk_tier)
            except ValueError:
                errors.append(f"Invalid risk_tier: {risk_tier}")
        
        # Validate sandbox requirement
        if 'sandbox' in manifest_data:
            sandbox = manifest_data['sandbox']
            if not isinstance(sandbox, bool):
                errors.append("sandbox must be a boolean")
        
        return len(errors) == 0, errors
    
    def _validate_plugin_id(self, plugin_id: str) -> bool:
        """Validate plugin ID format."""
        if not isinstance(plugin_id, str):
            return False
        
        # Must be alphanumeric with hyphens/underscores, 3-50 chars
        import re
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return bool(re.match(pattern, plugin_id))
    
    def _validate_version(self, version: str) -> bool:
        """Validate semantic version format."""
        if not isinstance(version, str):
            return False
        
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        return bool(re.match(pattern, version))
    
    def _validate_permission_request(self, permission: Dict[str, Any]) -> List[str]:
        """Validate a permission request."""
        errors = []
        
        if not isinstance(permission, dict):
            errors.append("Permission must be a dictionary")
            return errors
        
        # Check required fields
        if 'permission' not in permission:
            errors.append("Permission request missing 'permission' field")
        elif permission['permission'] not in self.allowed_permissions:
            errors.append(f"Invalid permission: {permission['permission']}")
        
        if 'level' not in permission:
            errors.append("Permission request missing 'level' field")
        elif permission['level'] not in self.allowed_levels:
            errors.append(f"Invalid permission level: {permission['level']}")
        
        # Validate scope if present
        if 'scope' in permission and permission['scope'] is not None:
            if not isinstance(permission['scope'], str):
                errors.append("Permission scope must be a string")
        
        # Validate conditions if present
        if 'conditions' in permission:
            if not isinstance(permission['conditions'], dict):
                errors.append("Permission conditions must be a dictionary")
        
        return errors
    
    def _validate_capability(self, capability: Dict[str, Any]) -> List[str]:
        """Validate a plugin capability."""
        errors = []
        
        if not isinstance(capability, dict):
            errors.append("Capability must be a dictionary")
            return errors
        
        # Check required fields
        if 'name' not in capability:
            errors.append("Capability missing 'name' field")
        elif not isinstance(capability['name'], str):
            errors.append("Capability name must be a string")
        
        if 'description' not in capability:
            errors.append("Capability missing 'description' field")
        elif not isinstance(capability['description'], str):
            errors.append("Capability description must be a string")
        
        if 'version' not in capability:
            errors.append("Capability missing 'version' field")
        elif not self._validate_version(capability['version']):
            errors.append(f"Invalid capability version: {capability['version']}")
        
        # Validate parameters if present
        if 'parameters' in capability:
            if not isinstance(capability['parameters'], dict):
                errors.append("Capability parameters must be a dictionary")
        
        # Validate return_type if present
        if 'return_type' in capability and capability['return_type'] is not None:
            if not isinstance(capability['return_type'], str):
                errors.append("Capability return_type must be a string")
        
        return errors
    
    def create_manifest(self, manifest_data: Dict[str, Any]) -> Optional[PluginManifest]:
        """
        Create a PluginManifest from validated data.
        
        Args:
            manifest_data: Validated manifest data
            
        Returns:
            PluginManifest instance or None if invalid
        """
        try:
            # Convert permission requests
            permission_requests = []
            if 'requested_permissions' in manifest_data:
                for perm_data in manifest_data['requested_permissions']:
                    perm_request = PermissionRequest(
                        permission=perm_data['permission'],
                        level=PermissionLevel(perm_data['level']),
                        scope=perm_data.get('scope'),
                        conditions=perm_data.get('conditions', {}),
                        expires_at=perm_data.get('expires_at')
                    )
                    permission_requests.append(perm_request)
            
            # Convert capabilities
            capabilities = []
            if 'capabilities' in manifest_data:
                for cap_data in manifest_data['capabilities']:
                    capability = PluginCapability(
                        name=cap_data['name'],
                        description=cap_data['description'],
                        version=cap_data['version'],
                        parameters=cap_data.get('parameters', {}),
                        return_type=cap_data.get('return_type'),
                        async_support=cap_data.get('async_support', False),
                        batch_support=cap_data.get('batch_support', False)
                    )
                    capabilities.append(capability)
            
            # Create manifest
            manifest = PluginManifest(
                plugin_id=manifest_data['plugin_id'],
                name=manifest_data['name'],
                version=manifest_data['version'],
                description=manifest_data['description'],
                author=manifest_data['author'],
                manifest_version=manifest_data.get('manifest_version', '2.0.0'),
                requested_permissions=permission_requests,
                capabilities=capabilities,
                lifecycle_hooks=manifest_data.get('lifecycle_hooks', {}),
                sandbox=manifest_data.get('sandbox', True),
                sandbox_config=manifest_data.get('sandbox_config', {}),
                risk_tier=RiskTier(manifest_data.get('risk_tier', 'moderate')),
                security_scan=manifest_data.get('security_scan', True),
                code_review_required=manifest_data.get('code_review_required', False),
                performance_monitoring=manifest_data.get('performance_monitoring', True),
                resource_limits=manifest_data.get('resource_limits', {}),
                approved_by_user=manifest_data.get('approved_by_user', False),
                auto_approve=manifest_data.get('auto_approve', False),
                manifest_signature=manifest_data.get('manifest_signature'),
                code_signature=manifest_data.get('code_signature')
            )
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"Error creating manifest: {e}")
            return None
    
    def load_manifest_from_json(self, json_data: str) -> Optional[PluginManifest]:
        """
        Load manifest from JSON string.
        
        Args:
            json_data: JSON string containing manifest data
            
        Returns:
            PluginManifest instance or None if invalid
        """
        try:
            manifest_data = json.loads(json_data)
            is_valid, errors = self.validate_manifest(manifest_data)
            
            if not is_valid:
                self.logger.error(f"Invalid manifest: {errors}")
                return None
            
            return self.create_manifest(manifest_data)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading manifest: {e}")
            return None 