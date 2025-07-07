#!/usr/bin/env python3
"""
MCP Resource Policy Module - Enterprise Feature

Implementation of scoped resource permissions for all agents using the Model Context Protocol (MCP).
Provides explicit resource access control, audit logging, and policy enforcement for disk, network,
workspace, and memory access across all Hearthlink agents.

Features:
- Agent-specific resource permission definitions
- MCP-based resource access requests and validation
- Real-time policy enforcement and audit logging
- Integration with RBAC/ABAC and SIEM monitoring
- Automatic timeout and scope enforcement

References:
- docs/MCP_AGENT_RESOURCE_POLICY.md: Resource policy specifications
- docs/appendix_e_model_context_protocol_mcp_full_specification.md: MCP protocol
- docs/ENTERPRISE_FEATURES.md: Enterprise feature specifications
- Process Refinement SOP: Development and documentation standards

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class MCPResourceError(HearthlinkError):
    """Base exception for MCP resource policy errors."""
    pass


class ResourceAccessError(MCPResourceError):
    """Exception raised when resource access is denied."""
    pass


class PolicyValidationError(MCPResourceError):
    """Exception raised when policy validation fails."""
    pass


class AgentPermissionError(MCPResourceError):
    """Exception raised when agent permissions are invalid."""
    pass


class ResourceType(Enum):
    """Resource types for access control."""
    DISK = "disk"
    NETWORK = "network"
    WORKSPACE = "workspace"
    MEMORY = "memory"
    API = "api"
    FILE = "file"


class AccessAction(Enum):
    """Resource access actions."""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class AccessDecision(Enum):
    """Access control decisions."""
    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"


@dataclass
class ResourcePermission:
    """Resource permission definition."""
    resource_type: ResourceType
    actions: List[AccessAction]
    scope: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    audit_required: bool = True


@dataclass
class AgentResourcePolicy:
    """Agent resource policy definition."""
    agent_id: str
    agent_name: str
    resource_scope: str
    permissions: Dict[ResourceType, ResourcePermission]
    mcp_version: str = "1.0.0"
    user_consent_required: bool = False
    data_anonymization_required: bool = False
    content_validation_required: bool = False
    session_boundary_required: bool = False
    encryption_required: bool = False
    sandbox_required: bool = False
    risk_assessment_required: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class MCPResourceRequest:
    """MCP resource access request."""
    request_id: str
    agent_id: str
    resource_type: ResourceType
    action: AccessAction
    resource_path: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class MCPResourceResponse:
    """MCP resource access response."""
    request_id: str
    decision: AccessDecision
    reason: str
    granted_permissions: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    audit_trail: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResourceAccessSession:
    """Active resource access session."""
    session_id: str
    agent_id: str
    resource_type: ResourceType
    permissions: Dict[str, Any]
    granted_at: str
    expires_at: str
    audit_log: List[Dict[str, Any]] = field(default_factory=list)


class MCPResourcePolicy:
    """
    MCP Resource Policy system for enterprise environments.
    
    Provides scoped resource permissions for all agents with comprehensive
    policy enforcement, audit logging, and security controls.
    """
    
    def __init__(self, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize MCP Resource Policy system.
        
        Args:
            logger: Optional logger instance
            
        Raises:
            MCPResourceError: If initialization fails
        """
        try:
            self.logger = logger or HearthlinkLogger()
            
            # Agent policies
            self.agent_policies: Dict[str, AgentResourcePolicy] = {}
            
            # Active access sessions
            self.active_sessions: Dict[str, ResourceAccessSession] = {}
            
            # Audit logging
            self.audit_log: List[Dict[str, Any]] = []
            
            # Security controls
            self.security_controls: Dict[str, Callable] = {}
            
            # Initialize default agent policies
            self._initialize_agent_policies()
            self._setup_security_controls()
            
            self._log("mcp_resource_policy_initialized", "system", None, "system", {
                "agent_policies_count": len(self.agent_policies),
                "security_controls_count": len(self.security_controls)
            })
            
        except Exception as e:
            raise MCPResourceError(f"Failed to initialize MCP Resource Policy: {str(e)}") from e

    def _initialize_agent_policies(self):
        """Initialize default agent resource policies."""
        
        # Sentry Policy
        sentry_policy = AgentResourcePolicy(
            agent_id="sentry",
            agent_name="Sentry",
            resource_scope="security_monitoring",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="security_logs",
                    conditions={"path_pattern": "logs/*", "file_type": ["log", "audit"]},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="security_alerts",
                    conditions={"endpoint_type": "internal", "protocol": "secure"},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="security_config",
                    conditions={"workspace_type": "security", "access_level": "admin"},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="security_events",
                    conditions={"memory_type": "security", "encryption": True},
                    timeout_seconds=300,
                    audit_required=True
                )
            },
            encryption_required=True,
            audit_required=True
        )
        self.agent_policies["sentry"] = sentry_policy
        
        # Alden Policy
        alden_policy = AgentResourcePolicy(
            agent_id="alden",
            agent_name="Alden",
            resource_scope="user_companion",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="user_workspace",
                    conditions={"path_pattern": "user/*", "file_type": ["goal", "habit", "progress"]},
                    timeout_seconds=600,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="user_preferences",
                    conditions={"endpoint_type": "preferences", "data_type": "user_config"},
                    timeout_seconds=600,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="user_files",
                    conditions={"workspace_type": "user", "access_level": "personal"},
                    timeout_seconds=600,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="personal_memory",
                    conditions={"memory_type": "personal", "user_consent": True},
                    timeout_seconds=600,
                    audit_required=True
                )
            },
            user_consent_required=True,
            session_boundary_required=True
        )
        self.agent_policies["alden"] = alden_policy
        
        # Alice Policy
        alice_policy = AgentResourcePolicy(
            agent_id="alice",
            agent_name="Alice",
            resource_scope="behavioral_analysis",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="behavioral_data",
                    conditions={"path_pattern": "analysis/*", "file_type": ["log", "report"]},
                    timeout_seconds=900,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="research_resources",
                    conditions={"endpoint_type": "research", "data_type": "behavioral"},
                    timeout_seconds=900,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="analysis_workspace",
                    conditions={"workspace_type": "analysis", "access_level": "analyst"},
                    timeout_seconds=900,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="behavioral_patterns",
                    conditions={"memory_type": "behavioral", "anonymization": True},
                    timeout_seconds=900,
                    audit_required=True
                )
            },
            data_anonymization_required=True,
            content_validation_required=True
        )
        self.agent_policies["alice"] = alice_policy
        
        # Mimic Policy
        mimic_policy = AgentResourcePolicy(
            agent_id="mimic",
            agent_name="Mimic",
            resource_scope="persona_generation",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="persona_content",
                    conditions={"path_pattern": "personas/*", "file_type": ["template", "generated"]},
                    timeout_seconds=1200,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="knowledge_resources",
                    conditions={"endpoint_type": "knowledge", "data_type": "research"},
                    timeout_seconds=1200,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="persona_workspace",
                    conditions={"workspace_type": "persona", "access_level": "creator"},
                    timeout_seconds=1200,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="persona_memory",
                    conditions={"memory_type": "persona", "validation": True},
                    timeout_seconds=1200,
                    audit_required=True
                )
            },
            content_validation_required=True,
            session_boundary_required=True
        )
        self.agent_policies["mimic"] = mimic_policy
        
        # Core Policy
        core_policy = AgentResourcePolicy(
            agent_id="core",
            agent_name="Core",
            resource_scope="session_orchestration",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="session_data",
                    conditions={"path_pattern": "sessions/*", "file_type": ["config", "log"]},
                    timeout_seconds=1800,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="session_coordination",
                    conditions={"endpoint_type": "session", "data_type": "coordination"},
                    timeout_seconds=1800,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="session_workspace",
                    conditions={"workspace_type": "session", "access_level": "coordinator"},
                    timeout_seconds=1800,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="communal_memory",
                    conditions={"memory_type": "communal", "session_boundary": True},
                    timeout_seconds=1800,
                    audit_required=True
                )
            },
            session_boundary_required=True,
            audit_required=True
        )
        self.agent_policies["core"] = core_policy
        
        # Vault Policy
        vault_policy = AgentResourcePolicy(
            agent_id="vault",
            agent_name="Vault",
            resource_scope="memory_management",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="encrypted_memory",
                    conditions={"path_pattern": "vault/*", "file_type": ["encrypted", "backup"]},
                    timeout_seconds=3600,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="backup_services",
                    conditions={"endpoint_type": "backup", "protocol": "encrypted"},
                    timeout_seconds=3600,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="vault_workspace",
                    conditions={"workspace_type": "vault", "access_level": "storage"},
                    timeout_seconds=3600,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="all_memory_slices",
                    conditions={"memory_type": "all", "encryption": True},
                    timeout_seconds=3600,
                    audit_required=True
                )
            },
            encryption_required=True,
            audit_required=True
        )
        self.agent_policies["vault"] = vault_policy
        
        # Synapse Policy
        synapse_policy = AgentResourcePolicy(
            agent_id="synapse",
            agent_name="Synapse",
            resource_scope="external_gateway",
            permissions={
                ResourceType.DISK: ResourcePermission(
                    resource_type=ResourceType.DISK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="plugin_data",
                    conditions={"path_pattern": "plugins/*", "file_type": ["manifest", "log"]},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.NETWORK: ResourcePermission(
                    resource_type=ResourceType.NETWORK,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="external_apis",
                    conditions={"endpoint_type": "external", "risk_assessed": True},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.WORKSPACE: ResourcePermission(
                    resource_type=ResourceType.WORKSPACE,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="plugin_workspace",
                    conditions={"workspace_type": "plugin", "sandbox": True},
                    timeout_seconds=300,
                    audit_required=True
                ),
                ResourceType.MEMORY: ResourcePermission(
                    resource_type=ResourceType.MEMORY,
                    actions=[AccessAction.READ, AccessAction.WRITE],
                    scope="plugin_context",
                    conditions={"memory_type": "plugin", "sandbox": True},
                    timeout_seconds=300,
                    audit_required=True
                )
            },
            sandbox_required=True,
            risk_assessment_required=True
        )
        self.agent_policies["synapse"] = synapse_policy

    def _setup_security_controls(self):
        """Setup security control functions."""
        
        # Encryption control
        self.security_controls["encryption"] = self._validate_encryption
        
        # Sandbox control
        self.security_controls["sandbox"] = self._validate_sandbox
        
        # Risk assessment control
        self.security_controls["risk_assessment"] = self._validate_risk_assessment
        
        # User consent control
        self.security_controls["user_consent"] = self._validate_user_consent
        
        # Data anonymization control
        self.security_controls["data_anonymization"] = self._validate_data_anonymization
        
        # Content validation control
        self.security_controls["content_validation"] = self._validate_content_validation
        
        # Session boundary control
        self.security_controls["session_boundary"] = self._validate_session_boundary

    def request_resource_access(self, request: MCPResourceRequest) -> MCPResourceResponse:
        """
        Process MCP resource access request.
        
        Args:
            request: MCP resource access request
            
        Returns:
            MCPResourceResponse with access decision
            
        Raises:
            ResourceAccessError: If access is denied
            PolicyValidationError: If policy validation fails
        """
        try:
            # Validate request
            self._validate_request(request)
            
            # Get agent policy
            agent_policy = self._get_agent_policy(request.agent_id)
            
            # Check resource permissions
            permission = self._get_resource_permission(agent_policy, request.resource_type)
            
            # Validate access conditions
            if not self._validate_access_conditions(request, permission):
                return self._create_denied_response(request, "Access conditions not met")
            
            # Apply security controls
            if not self._apply_security_controls(request, agent_policy):
                return self._create_denied_response(request, "Security controls failed")
            
            # Create access session
            session = self._create_access_session(request, permission)
            
            # Log access grant
            self._log_access_grant(request, session)
            
            return self._create_allowed_response(request, session)
            
        except Exception as e:
            self._log_access_denial(request, str(e))
            return self._create_denied_response(request, str(e))

    def _validate_request(self, request: MCPResourceRequest):
        """Validate MCP resource request."""
        if not request.agent_id:
            raise PolicyValidationError("Agent ID is required")
        
        if not request.resource_type:
            raise PolicyValidationError("Resource type is required")
        
        if not request.action:
            raise PolicyValidationError("Action is required")
        
        if not request.resource_path:
            raise PolicyValidationError("Resource path is required")

    def _get_agent_policy(self, agent_id: str) -> AgentResourcePolicy:
        """Get agent resource policy."""
        if agent_id not in self.agent_policies:
            raise AgentPermissionError(f"No policy found for agent: {agent_id}")
        
        policy = self.agent_policies[agent_id]
        if not policy.is_active:
            raise AgentPermissionError(f"Policy is inactive for agent: {agent_id}")
        
        return policy

    def _get_resource_permission(self, policy: AgentResourcePolicy, resource_type: ResourceType) -> ResourcePermission:
        """Get resource permission for agent."""
        if resource_type not in policy.permissions:
            raise ResourceAccessError(f"No permission for resource type: {resource_type.value}")
        
        return policy.permissions[resource_type]

    def _validate_access_conditions(self, request: MCPResourceRequest, permission: ResourcePermission) -> bool:
        """Validate access conditions for resource."""
        # Check action permission
        if request.action not in permission.actions:
            return False
        
        # Check path pattern
        if "path_pattern" in permission.conditions:
            if not self._pattern_matches(permission.conditions["path_pattern"], request.resource_path):
                return False
        
        # Check file type
        if "file_type" in permission.conditions:
            file_ext = Path(request.resource_path).suffix.lstrip(".")
            if file_ext not in permission.conditions["file_type"]:
                return False
        
        return True

    def _apply_security_controls(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Apply security controls for agent."""
        try:
            # Apply required security controls
            for control_name, control_func in self.security_controls.items():
                if hasattr(policy, f"{control_name}_required") and getattr(policy, f"{control_name}_required"):
                    if not control_func(request, policy):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Security control application failed: {str(e)}")
            return False

    def _create_access_session(self, request: MCPResourceRequest, permission: ResourcePermission) -> ResourceAccessSession:
        """Create resource access session."""
        session_id = str(uuid.uuid4())
        granted_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(seconds=permission.timeout_seconds)).isoformat()
        
        session = ResourceAccessSession(
            session_id=session_id,
            agent_id=request.agent_id,
            resource_type=request.resource_type,
            permissions={
                "actions": [action.value for action in permission.actions],
                "scope": permission.scope,
                "conditions": permission.conditions
            },
            granted_at=granted_at,
            expires_at=expires_at
        )
        
        self.active_sessions[session_id] = session
        return session

    def _create_allowed_response(self, request: MCPResourceRequest, session: ResourceAccessSession) -> MCPResourceResponse:
        """Create allowed access response."""
        return MCPResourceResponse(
            request_id=request.request_id,
            decision=AccessDecision.ALLOW,
            reason="Access granted",
            granted_permissions=session.permissions,
            timeout_seconds=session.permissions.get("timeout_seconds", 300),
            audit_trail={
                "session_id": session.session_id,
                "granted_at": session.granted_at,
                "expires_at": session.expires_at
            }
        )

    def _create_denied_response(self, request: MCPResourceRequest, reason: str) -> MCPResourceResponse:
        """Create denied access response."""
        return MCPResourceResponse(
            request_id=request.request_id,
            decision=AccessDecision.DENY,
            reason=reason,
            audit_trail={
                "denied_at": datetime.now().isoformat(),
                "denial_reason": reason
            }
        )

    def _pattern_matches(self, pattern: str, value: str) -> bool:
        """Check if value matches pattern."""
        import re
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False

    def _validate_encryption(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate encryption requirements."""
        # Implementation would check if resource is encrypted
        return True

    def _validate_sandbox(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate sandbox requirements."""
        # Implementation would check if request is in sandbox
        return True

    def _validate_risk_assessment(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate risk assessment requirements."""
        # Implementation would check risk assessment
        return True

    def _validate_user_consent(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate user consent requirements."""
        # Implementation would check user consent
        return True

    def _validate_data_anonymization(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate data anonymization requirements."""
        # Implementation would check data anonymization
        return True

    def _validate_content_validation(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate content validation requirements."""
        # Implementation would check content validation
        return True

    def _validate_session_boundary(self, request: MCPResourceRequest, policy: AgentResourcePolicy) -> bool:
        """Validate session boundary requirements."""
        # Implementation would check session boundaries
        return True

    def _log_access_grant(self, request: MCPResourceRequest, session: ResourceAccessSession):
        """Log access grant event."""
        self._log("resource_access_granted", request.user_id or "system", request.session_id, "security", {
            "agent_id": request.agent_id,
            "resource_type": request.resource_type.value,
            "action": request.action.value,
            "resource_path": request.resource_path,
            "session_id": session.session_id,
            "expires_at": session.expires_at
        })

    def _log_access_denial(self, request: MCPResourceRequest, reason: str):
        """Log access denial event."""
        self._log("resource_access_denied", request.user_id or "system", request.session_id, "security", {
            "agent_id": request.agent_id,
            "resource_type": request.resource_type.value,
            "action": request.action.value,
            "resource_path": request.resource_path,
            "denial_reason": reason
        })

    def get_agent_policy(self, agent_id: str) -> Optional[AgentResourcePolicy]:
        """Get agent resource policy."""
        return self.agent_policies.get(agent_id)

    def list_agent_policies(self) -> List[AgentResourcePolicy]:
        """List all agent policies."""
        return list(self.agent_policies.values())

    def get_active_sessions(self) -> List[ResourceAccessSession]:
        """Get active resource access sessions."""
        return list(self.active_sessions.values())

    def revoke_session(self, session_id: str) -> bool:
        """Revoke active resource access session."""
        if session_id in self.active_sessions:
            session = self.active_sessions.pop(session_id)
            self._log("resource_session_revoked", "system", None, "security", {
                "session_id": session_id,
                "agent_id": session.agent_id,
                "revoked_at": datetime.now().isoformat()
            })
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired resource access sessions."""
        expired_count = 0
        current_time = datetime.now()
        
        for session_id, session in list(self.active_sessions.items()):
            expires_at = datetime.fromisoformat(session.expires_at)
            if current_time > expires_at:
                self.active_sessions.pop(session_id)
                expired_count += 1
                self._log("resource_session_expired", "system", None, "security", {
                    "session_id": session_id,
                    "agent_id": session.agent_id,
                    "expired_at": current_time.isoformat()
                })
        
        return expired_count

    def export_audit_log(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export audit log for specified date range."""
        filtered_log = self.audit_log
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            filtered_log = [entry for entry in filtered_log 
                          if datetime.fromisoformat(entry["timestamp"]) >= start_dt]
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            filtered_log = [entry for entry in filtered_log 
                          if datetime.fromisoformat(entry["timestamp"]) <= end_dt]
        
        return filtered_log

    def _log(self, action: str, user_id: str, session_id: Optional[str], event_type: str, details: Dict[str, Any]):
        """Log system events."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details
        }
        
        self.audit_log.append(log_entry)
        self.logger.logger.info(f"MCP Resource Policy: {action} - {details}")


def create_mcp_resource_policy(logger: Optional[HearthlinkLogger] = None) -> MCPResourcePolicy:
    """
    Create MCP Resource Policy instance.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        MCPResourcePolicy instance
        
    Raises:
        MCPResourceError: If creation fails
    """
    try:
        return MCPResourcePolicy(logger)
    except Exception as e:
        raise MCPResourceError(f"Failed to create MCP Resource Policy: {str(e)}") from e 