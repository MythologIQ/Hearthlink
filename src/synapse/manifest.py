"""
Plugin Manifest System

Handles plugin manifest validation, signing, and schema enforcement.
All plugins must declare capabilities, permissions, version, and sandboxing requirements.
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

class PermissionType(Enum):
    """Plugin permission types."""
    READ_VAULT = "read_vault"
    WRITE_VAULT = "write_vault"
    READ_CORE = "read_core"
    WRITE_CORE = "write_core"
    NETWORK_ACCESS = "network_access"
    FILE_SYSTEM = "file_system"
    SYSTEM_COMMANDS = "system_commands"
    EXTERNAL_API = "external_api"

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
class PluginManifest:
    """Plugin manifest schema."""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    manifest_version: str = "1.0.0"
    requested_permissions: List[str] = field(default_factory=list)
    sandbox: bool = True
    risk_tier: RiskTier = RiskTier.MODERATE
    approved_by_user: bool = False
    manifest_signature: Optional[str] = None
    benchmarks: Optional[BenchmarkResult] = None
    audit_log: List[AuditEvent] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
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
            'requested_permissions': sorted(self.requested_permissions),
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

class ManifestValidator:
    """Validates plugin manifests."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.required_fields = [
            'plugin_id', 'name', 'version', 'description', 'author'
        ]
        self.allowed_permissions = [p.value for p in PermissionType]
        self.max_permissions = 10
        self.max_name_length = 100
        self.max_description_length = 500
    
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
        
        # Validate permissions
        if 'requested_permissions' in manifest_data:
            permissions = manifest_data['requested_permissions']
            if not isinstance(permissions, list):
                errors.append("requested_permissions must be a list")
            else:
                if len(permissions) > self.max_permissions:
                    errors.append(f"Too many permissions requested. Maximum: {self.max_permissions}")
                
                for permission in permissions:
                    if permission not in self.allowed_permissions:
                        errors.append(f"Invalid permission: {permission}")
        
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
        
        # Basic semantic version validation
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        return bool(re.match(pattern, version))
    
    def create_manifest(self, manifest_data: Dict[str, Any]) -> Optional[PluginManifest]:
        """
        Create and validate a plugin manifest.
        
        Args:
            manifest_data: Manifest data dictionary
            
        Returns:
            PluginManifest if valid, None otherwise
        """
        is_valid, errors = self.validate_manifest(manifest_data)
        
        if not is_valid:
            self.logger.error(f"Invalid manifest: {errors}")
            return None
        
        try:
            # Convert risk_tier string to enum
            if 'risk_tier' in manifest_data:
                manifest_data['risk_tier'] = RiskTier(manifest_data['risk_tier'])
            
            manifest = PluginManifest(**manifest_data)
            
            # Calculate and set signature
            manifest.manifest_signature = manifest.calculate_signature()
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"Failed to create manifest: {e}")
            return None
    
    def load_manifest_from_json(self, json_data: str) -> Optional[PluginManifest]:
        """
        Load manifest from JSON string.
        
        Args:
            json_data: JSON string containing manifest data
            
        Returns:
            PluginManifest if valid, None otherwise
        """
        try:
            manifest_data = json.loads(json_data)
            return self.create_manifest(manifest_data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load manifest: {e}")
            return None 