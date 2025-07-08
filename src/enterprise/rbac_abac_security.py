#!/usr/bin/env python3
"""
RBAC/ABAC Security Module - Enterprise Feature

Minimum viable implementation of Role-Based Access Control (RBAC) and 
Attribute-Based Access Control (ABAC) for enterprise environments.

Features:
- Role-based access control with hierarchical roles
- Attribute-based access control with dynamic policies
- Policy evaluation and enforcement
- Access decision logging and audit
- Integration with multi-user collaboration

References:
- docs/ENTERPRISE_FEATURES.md: Enterprise feature specifications
- docs/PLATINUM_BLOCKERS.md: Ethical safety rails and compliance
- Process Refinement SOP: Development and documentation standards

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
import re
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


class SecurityError(HearthlinkError):
    """Base exception for security-related errors."""
    pass


class PolicyError(SecurityError):
    """Exception raised when policy operations fail."""
    pass


class AccessControlError(SecurityError):
    """Exception raised when access control operations fail."""
    pass


class RoleError(SecurityError):
    """Exception raised when role operations fail."""
    pass


class ResourceType(Enum):
    """Resource types for access control."""
    SYSTEM = "system"
    SESSION = "session"
    DATA = "data"
    PERSONA = "persona"
    VAULT = "vault"
    API = "api"
    FILE = "file"


class Action(Enum):
    """Actions that can be performed on resources."""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    SHARE = "share"


class PolicyEffect(Enum):
    """Policy effects for access decisions."""
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class Role:
    """Role definition for RBAC."""
    role_id: str
    name: str
    description: str
    permissions: List[str]  # List of permission strings
    parent_roles: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class UserRole:
    """User-role assignment."""
    user_id: str
    role_id: str
    assigned_at: str
    assigned_by: str
    expires_at: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Policy:
    """ABAC policy definition."""
    policy_id: str
    name: str
    description: str
    effect: PolicyEffect
    resources: List[str]  # Resource patterns
    actions: List[str]    # Action patterns
    conditions: Dict[str, Any]  # Attribute-based conditions
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class AccessRequest:
    """Access request for evaluation."""
    request_id: str
    user_id: str
    resource: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AccessDecision:
    """Access control decision."""
    request_id: str
    decision: PolicyEffect
    reason: str
    policies_applied: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class RBACABACSecurity:
    """
    RBAC/ABAC security system for enterprise environments.
    
    Provides role-based and attribute-based access control with
    comprehensive policy evaluation and audit logging.
    """
    
    def __init__(self, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize RBAC/ABAC security system.
        
        Args:
            logger: Optional logger instance
            
        Raises:
            SecurityError: If initialization fails
        """
        try:
            self.logger = logger or HearthlinkLogger()
            
            # Role management
            self.roles: Dict[str, Role] = {}
            self.user_roles: Dict[str, List[UserRole]] = defaultdict(list)
            
            # Policy management
            self.policies: Dict[str, Policy] = {}
            self.policy_evaluators: Dict[str, Callable] = {}
            
            # Access control
            self.access_decisions: List[AccessDecision] = []
            self.access_requests: List[AccessRequest] = []
            
            # Audit logging
            self.audit_log: List[Dict[str, Any]] = []
            
            # Initialize default roles and policies
            self._initialize_default_roles()
            self._initialize_default_policies()
            self._setup_policy_evaluators()
            
            self._log("rbac_abac_security_initialized", "system", None, "system", {
                "roles_count": len(self.roles),
                "policies_count": len(self.policies)
            })
            
        except Exception as e:
            raise SecurityError(f"Failed to initialize RBAC/ABAC security: {str(e)}") from e
    
    def _initialize_default_roles(self):
        """Initialize default roles for the system."""
        default_roles = [
            Role(
                role_id="super_admin",
                name="Super Administrator",
                description="Full system access with all permissions",
                permissions=["*:*:*"],  # All permissions
                parent_roles=[],
                attributes={"level": "highest", "scope": "global"}
            ),
            Role(
                role_id="admin",
                name="Administrator",
                description="System administration with most permissions",
                permissions=["system:*:*", "session:*:*", "data:*:*"],
                parent_roles=["super_admin"],
                attributes={"level": "high", "scope": "system"}
            ),
            Role(
                role_id="manager",
                name="Manager",
                description="Team management with elevated permissions",
                permissions=["session:*:*", "data:read:*", "data:write:own"],
                parent_roles=["admin"],
                attributes={"level": "medium", "scope": "team"}
            ),
            Role(
                role_id="user",
                name="User",
                description="Standard user with basic permissions",
                permissions=["session:read:*", "session:write:own", "data:read:own"],
                parent_roles=["manager"],
                attributes={"level": "standard", "scope": "personal"}
            ),
            Role(
                role_id="guest",
                name="Guest",
                description="Limited access for temporary users",
                permissions=["session:read:public", "data:read:public"],
                parent_roles=[],
                attributes={"level": "low", "scope": "public"}
            )
        ]
        
        for role in default_roles:
            self.roles[role.role_id] = role
    
    def _initialize_default_policies(self):
        """Initialize default ABAC policies."""
        default_policies = [
            Policy(
                policy_id="deny_guest_admin",
                name="Deny Guest Admin Access",
                description="Prevent guests from accessing admin functions",
                effect=PolicyEffect.DENY,
                resources=["system:*", "admin:*"],
                actions=["*"],
                conditions={"user_role": "guest"},
                priority=100
            ),
            Policy(
                policy_id="allow_user_own_data",
                name="Allow Users Own Data Access",
                description="Allow users to access their own data",
                effect=PolicyEffect.ALLOW,
                resources=["data:*"],
                actions=["read", "write"],
                conditions={"resource_owner": "user_id"},
                priority=50
            ),
            Policy(
                policy_id="time_based_access",
                name="Time-Based Access Control",
                description="Restrict access based on time of day",
                effect=PolicyEffect.DENY,
                resources=["*"],
                actions=["*"],
                conditions={"time_hour": {"not_between": [22, 6]}},
                priority=25
            ),
            Policy(
                policy_id="deny_late_night_access",
                name="Deny Late Night Access",
                description="Deny access during late night hours",
                effect=PolicyEffect.DENY,
                resources=["*"],
                actions=["*"],
                conditions={"time_hour": 23},
                priority=30
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.policy_id] = policy
    
    def _setup_policy_evaluators(self):
        """Setup policy evaluation functions."""
        self.policy_evaluators = {
            "user_role": self._evaluate_user_role,
            "resource_owner": self._evaluate_resource_owner,
            "time_hour": self._evaluate_time_hour,
            "location": self._evaluate_location,
            "device_type": self._evaluate_device_type
        }
    
    def create_role(self, name: str, description: str, permissions: List[str],
                   parent_roles: Optional[List[str]] = None) -> str:
        """
        Create a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permissions
            parent_roles: List of parent role IDs
            
        Returns:
            Role ID of the newly created role
            
        Raises:
            RoleError: If role creation fails
        """
        try:
            # Validate input
            if not name or not permissions:
                raise RoleError("Role name and permissions are required")
            
            # Check for existing role
            for role in self.roles.values():
                if role.name == name:
                    raise RoleError("Role name already exists")
            
            # Create role
            role_id = str(uuid.uuid4())
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                permissions=permissions,
                parent_roles=parent_roles or []
            )
            
            self.roles[role_id] = role
            
            self._log("role_created", "system", None, "role_management", {
                "role_name": name,
                "permissions_count": len(permissions)
            })
            
            return role_id
            
        except Exception as e:
            raise RoleError(f"Failed to create role: {str(e)}") from e
    
    def assign_role_to_user(self, user_id: str, role_id: str, 
                           assigned_by: str, expires_at: Optional[str] = None) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User to assign role to
            role_id: Role to assign
            assigned_by: User assigning the role
            expires_at: Optional expiration date
            
        Returns:
            True if successfully assigned, False otherwise
            
        Raises:
            RoleError: If role assignment fails
        """
        try:
            # Validate role exists
            if role_id not in self.roles:
                raise RoleError("Role does not exist")
            
            # Check if user already has this role
            existing_assignments = self.user_roles[user_id]
            for assignment in existing_assignments:
                if assignment.role_id == role_id and assignment.expires_at is None:
                    return True  # Already assigned
            
            # Create assignment
            assignment = UserRole(
                user_id=user_id,
                role_id=role_id,
                assigned_at=datetime.now().isoformat(),
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            
            self.user_roles[user_id].append(assignment)
            
            self._log("role_assigned", assigned_by, None, "role_management", {
                "user_id": user_id,
                "role_id": role_id,
                "expires_at": expires_at
            })
            
            return True
            
        except Exception as e:
            raise RoleError(f"Failed to assign role: {str(e)}") from e
    
    def remove_role_from_user(self, user_id: str, role_id: str, 
                             removed_by: str) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: User to remove role from
            role_id: Role to remove
            removed_by: User removing the role
            
        Returns:
            True if successfully removed, False otherwise
        """
        try:
            assignments = self.user_roles[user_id]
            
            for assignment in assignments[:]:  # Copy list to avoid modification during iteration
                if assignment.role_id == role_id:
                    assignments.remove(assignment)
                    
                    self._log("role_removed", removed_by, None, "role_management", {
                        "user_id": user_id,
                        "role_id": role_id
                    })
                    
                    return True
            
            return False
            
        except Exception as e:
            self._log("role_removal_error", removed_by, None, "error", {
                "error": str(e),
                "user_id": user_id,
                "role_id": role_id
            })
            return False
    
    def create_policy(self, name: str, description: str, effect: PolicyEffect,
                     resources: List[str], actions: List[str], 
                     conditions: Dict[str, Any], priority: int = 0) -> str:
        """
        Create a new ABAC policy.
        
        Args:
            name: Policy name
            description: Policy description
            effect: Policy effect (allow/deny)
            resources: Resource patterns
            actions: Action patterns
            conditions: Attribute-based conditions
            priority: Policy priority (higher = more important)
            
        Returns:
            Policy ID of the newly created policy
            
        Raises:
            PolicyError: If policy creation fails
        """
        try:
            # Validate input
            if not name or not resources or not actions:
                raise PolicyError("Policy name, resources, and actions are required")
            
            # Check for existing policy
            for policy in self.policies.values():
                if policy.name == name:
                    raise PolicyError("Policy name already exists")
            
            # Create policy
            policy_id = str(uuid.uuid4())
            policy = Policy(
                policy_id=policy_id,
                name=name,
                description=description,
                effect=effect,
                resources=resources,
                actions=actions,
                conditions=conditions,
                priority=priority
            )
            
            self.policies[policy_id] = policy
            
            self._log("policy_created", "system", None, "policy_management", {
                "policy_name": name,
                "effect": effect.value,
                "priority": priority
            })
            
            return policy_id
            
        except Exception as e:
            raise PolicyError(f"Failed to create policy: {str(e)}") from e
    
    def evaluate_access(self, user_id: str, resource: str, action: str,
                       context: Optional[Dict[str, Any]] = None) -> AccessDecision:
        """
        Evaluate access request using RBAC and ABAC.
        
        Args:
            user_id: User requesting access
            resource: Resource being accessed
            action: Action being performed
            context: Additional context for evaluation
            
        Returns:
            Access decision with result and reasoning
        """
        try:
            context = context or {}
            
            # Create access request
            request_id = str(uuid.uuid4())
            request = AccessRequest(
                request_id=request_id,
                user_id=user_id,
                resource=resource,
                action=action,
                context=context
            )
            
            self.access_requests.append(request)
            
            # Get user roles
            user_roles = self._get_user_roles(user_id)
            
            # Get user permissions from roles
            user_permissions = self._get_user_permissions(user_id, user_roles)
            
            # Evaluate RBAC
            rbac_decision = self._evaluate_rbac(user_permissions, resource, action)
            
            # Evaluate ABAC policies
            abac_decision = self._evaluate_abac_policies(user_id, resource, action, context)
            
            # Combine decisions (ABAC takes precedence for DENY)
            final_decision = self._combine_decisions(rbac_decision, abac_decision)
            
            # Create access decision
            decision = AccessDecision(
                request_id=request_id,
                decision=final_decision["effect"],
                reason=final_decision["reason"],
                policies_applied=final_decision["policies"],
                metadata={
                    "rbac_decision": rbac_decision,
                    "abac_decision": abac_decision
                }
            )
            
            self.access_decisions.append(decision)
            
            self._log("access_evaluated", user_id, None, "access_control", {
                "resource": resource,
                "action": action,
                "decision": final_decision["effect"].value,
                "reason": final_decision["reason"]
            })
            
            return decision
            
        except Exception as e:
            self._log("access_evaluation_error", user_id, None, "error", {
                "error": str(e),
                "resource": resource,
                "action": action
            })
            
            # Default to deny on error
            return AccessDecision(
                request_id=str(uuid.uuid4()),
                decision=PolicyEffect.DENY,
                reason=f"Access evaluation failed: {str(e)}",
                policies_applied=[]
            )
    
    def _get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles assigned to a user (including inherited)."""
        try:
            user_roles = []
            assignments = self.user_roles.get(user_id, [])
            
            # Get directly assigned roles
            for assignment in assignments:
                if assignment.role_id in self.roles:
                    role = self.roles[assignment.role_id]
                    if role.is_active:
                        user_roles.append(role)
            
            # Get inherited roles
            inherited_roles = []
            for role in user_roles:
                inherited_roles.extend(self._get_inherited_roles(role))
            
            user_roles.extend(inherited_roles)
            
            return user_roles
            
        except Exception as e:
            self._log("get_user_roles_error", user_id, None, "error", {
                "error": str(e)
            })
            return []
    
    def _get_inherited_roles(self, role: Role) -> List[Role]:
        """Get roles inherited from parent roles."""
        try:
            inherited = []
            
            for parent_id in role.parent_roles:
                if parent_id in self.roles:
                    parent_role = self.roles[parent_id]
                    if parent_role.is_active:
                        inherited.append(parent_role)
                        # Recursively get parent's inherited roles
                        inherited.extend(self._get_inherited_roles(parent_role))
            
            return inherited
            
        except Exception as e:
            self._log("get_inherited_roles_error", "system", None, "error", {
                "error": str(e),
                "role_id": role.role_id
            })
            return []
    
    def _get_user_permissions(self, user_id: str, user_roles: List[Role]) -> Set[str]:
        """Get all permissions for a user from their roles."""
        try:
            permissions = set()
            
            for role in user_roles:
                permissions.update(role.permissions)
            
            return permissions
            
        except Exception as e:
            self._log("get_user_permissions_error", user_id, None, "error", {
                "error": str(e)
            })
            return set()
    
    def _evaluate_rbac(self, user_permissions: Set[str], resource: str, action: str) -> Dict[str, Any]:
        """Evaluate RBAC permissions."""
        try:
            # Check for wildcard permissions
            if "*:*:*" in user_permissions:
                return {
                    "effect": PolicyEffect.ALLOW,
                    "reason": "User has wildcard permissions",
                    "policies": ["rbac_wildcard"]
                }
            
            # Check for resource-specific wildcard
            resource_wildcard = f"{resource}:*:*"
            if resource_wildcard in user_permissions:
                return {
                    "effect": PolicyEffect.ALLOW,
                    "reason": f"User has wildcard permissions for resource {resource}",
                    "policies": ["rbac_resource_wildcard"]
                }
            
            # Check for action-specific permission
            action_permission = f"{resource}:{action}:*"
            if action_permission in user_permissions:
                return {
                    "effect": PolicyEffect.ALLOW,
                    "reason": f"User has permission for {action} on {resource}",
                    "policies": ["rbac_action_permission"]
                }
            
            # Check for specific permission
            specific_permission = f"{resource}:{action}:specific"
            if specific_permission in user_permissions:
                return {
                    "effect": PolicyEffect.ALLOW,
                    "reason": f"User has specific permission for {action} on {resource}",
                    "policies": ["rbac_specific_permission"]
                }
            
            return {
                "effect": PolicyEffect.DENY,
                "reason": "User lacks required permissions",
                "policies": ["rbac_no_permission"]
            }
            
        except Exception as e:
            return {
                "effect": PolicyEffect.DENY,
                "reason": f"RBAC evaluation failed: {str(e)}",
                "policies": ["rbac_error"]
            }
    
    def _evaluate_abac_policies(self, user_id: str, resource: str, action: str,
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ABAC policies."""
        try:
            # Sort policies by priority (highest first)
            sorted_policies = sorted(
                self.policies.values(),
                key=lambda p: p.priority,
                reverse=True
            )
            
            for policy in sorted_policies:
                if not policy.is_active:
                    continue
                
                # Check if policy applies to this resource and action
                if self._policy_applies(policy, resource, action):
                    # Evaluate policy conditions
                    if self._evaluate_policy_conditions(policy, user_id, context):
                        return {
                            "effect": policy.effect,
                            "reason": f"Policy '{policy.name}' applied",
                            "policies": [policy.policy_id]
                        }
            
            return {
                "effect": PolicyEffect.ALLOW,
                "reason": "No ABAC policies applied",
                "policies": []
            }
            
        except Exception as e:
            return {
                "effect": PolicyEffect.DENY,
                "reason": f"ABAC evaluation failed: {str(e)}",
                "policies": ["abac_error"]
            }
    
    def _policy_applies(self, policy: Policy, resource: str, action: str) -> bool:
        """Check if policy applies to the given resource and action."""
        try:
            # Check resource patterns
            resource_matches = any(self._pattern_matches(pattern, resource) for pattern in policy.resources)
            
            # Check action patterns
            action_matches = any(self._pattern_matches(pattern, action) for pattern in policy.actions)
            
            return resource_matches and action_matches
            
        except Exception as e:
            self._log("policy_applies_error", "system", None, "error", {
                "error": str(e),
                "policy_id": policy.policy_id
            })
            return False
    
    def _pattern_matches(self, pattern: str, value: str) -> bool:
        """Check if a value matches a pattern (supports wildcards)."""
        try:
            # Convert pattern to regex
            regex_pattern = pattern.replace("*", ".*")
            return bool(re.match(regex_pattern, value))
        except Exception:
            return False
    
    def _evaluate_policy_conditions(self, policy: Policy, user_id: str,
                                  context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions."""
        try:
            for condition_key, condition_value in policy.conditions.items():
                # Skip time-based conditions if no time context is provided
                if condition_key == "time_hour" and "time_hour" not in context:
                    continue
                
                evaluator = self.policy_evaluators.get(condition_key)
                if evaluator:
                    if not evaluator(condition_value, user_id, context):
                        return False
                else:
                    # Default condition evaluation
                    if not self._evaluate_default_condition(condition_key, condition_value, user_id, context):
                        return False
            
            return True
            
        except Exception as e:
            self._log("condition_evaluation_error", user_id, None, "error", {
                "error": str(e),
                "policy_id": policy.policy_id
            })
            return False
    
    def _evaluate_user_role(self, condition_value: Any, user_id: str,
                           context: Dict[str, Any]) -> bool:
        """Evaluate user role condition."""
        try:
            user_roles = self._get_user_roles(user_id)
            user_role_names = [role.name.lower() for role in user_roles]
            
            if isinstance(condition_value, str):
                return condition_value.lower() in user_role_names
            elif isinstance(condition_value, list):
                return any(role.lower() in user_role_names for role in condition_value)
            
            return False
            
        except Exception as e:
            self._log("user_role_evaluation_error", user_id, None, "error", {
                "error": str(e)
            })
            return False
    
    def _evaluate_resource_owner(self, condition_value: Any, user_id: str,
                                context: Dict[str, Any]) -> bool:
        """Evaluate resource owner condition."""
        try:
            if condition_value == "user_id":
                # Check if user is the owner of the resource
                resource_owner = context.get("resource_owner")
                return resource_owner == user_id
            
            return False
            
        except Exception as e:
            self._log("resource_owner_evaluation_error", user_id, None, "error", {
                "error": str(e)
            })
            return False
    
    def _evaluate_time_hour(self, condition_value: Any, user_id: str,
                           context: Dict[str, Any]) -> bool:
        """Evaluate time-based condition."""
        try:
            # Only apply time-based policies if time_hour is explicitly provided in context
            if "time_hour" not in context:
                return True  # Skip time-based evaluation if no time context
            
            time_hour = context["time_hour"]
            
            # Handle direct integer comparison (e.g., time_hour: 23)
            if isinstance(condition_value, int):
                return time_hour == condition_value
            
            if isinstance(condition_value, dict) and "not_between" in condition_value:
                start, end = condition_value["not_between"]
                # Handle the case where start > end (e.g., 22 to 6 spans midnight)
                if start > end:
                    # Return True if time is NOT between start and end (spans midnight)
                    return not (start <= time_hour or time_hour <= end)
                else:
                    # Return True if time is NOT between start and end
                    return not (start <= time_hour <= end)
            elif isinstance(condition_value, dict) and "between" in condition_value:
                start, end = condition_value["between"]
                # Handle the case where start > end (e.g., 22 to 6 spans midnight)
                if start > end:
                    # Return True if time is between start and end (spans midnight)
                    return start <= time_hour or time_hour <= end
                else:
                    # Return True if time is between start and end
                    return start <= time_hour <= end
            
            return True
            
        except Exception as e:
            self._log("time_evaluation_error", user_id, None, "error", {
                "error": str(e)
            })
            return True
    
    def _evaluate_location(self, condition_value: Any, user_id: str,
                          context: Dict[str, Any]) -> bool:
        """Evaluate location-based condition."""
        try:
            user_location = context.get("location", "unknown")
            
            if isinstance(condition_value, str):
                return user_location == condition_value
            elif isinstance(condition_value, list):
                return user_location in condition_value
            
            return True
            
        except Exception as e:
            self._log("location_evaluation_error", user_id, None, "error", {
                "error": str(e)
            })
            return True
    
    def _evaluate_device_type(self, condition_value: Any, user_id: str,
                             context: Dict[str, Any]) -> bool:
        """Evaluate device type condition."""
        try:
            device_type = context.get("device_type", "unknown")
            
            if isinstance(condition_value, str):
                return device_type == condition_value
            elif isinstance(condition_value, list):
                return device_type in condition_value
            
            return True
            
        except Exception as e:
            self._log("device_evaluation_error", user_id, None, "error", {
                "error": str(e)
            })
            return True
    
    def _evaluate_default_condition(self, condition_key: str, condition_value: Any,
                                  user_id: str, context: Dict[str, Any]) -> bool:
        """Evaluate default condition."""
        try:
            context_value = context.get(condition_key)
            return context_value == condition_value
            
        except Exception as e:
            self._log("default_condition_error", user_id, None, "error", {
                "error": str(e),
                "condition_key": condition_key
            })
            return False
    
    def _combine_decisions(self, rbac_decision: Dict[str, Any],
                          abac_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Combine RBAC and ABAC decisions."""
        try:
            # If ABAC denies, deny regardless of RBAC
            if abac_decision["effect"] == PolicyEffect.DENY:
                return {
                    "effect": PolicyEffect.DENY,
                    "reason": f"ABAC denied: {abac_decision['reason']}",
                    "policies": rbac_decision["policies"] + abac_decision["policies"]
                }
            
            # If RBAC denies, deny
            if rbac_decision["effect"] == PolicyEffect.DENY:
                return {
                    "effect": PolicyEffect.DENY,
                    "reason": f"RBAC denied: {rbac_decision['reason']}",
                    "policies": rbac_decision["policies"] + abac_decision["policies"]
                }
            
            # Both allow
            return {
                "effect": PolicyEffect.ALLOW,
                "reason": f"RBAC and ABAC allowed: {rbac_decision['reason']}",
                "policies": rbac_decision["policies"] + abac_decision["policies"]
            }
            
        except Exception as e:
            return {
                "effect": PolicyEffect.DENY,
                "reason": f"Decision combination failed: {str(e)}",
                "policies": []
            }
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        return self._get_user_roles(user_id)
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user."""
        user_roles = self._get_user_roles(user_id)
        return self._get_user_permissions(user_id, user_roles)
    
    def export_audit_log(self, user_id: str, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export audit log for compliance purposes."""
        try:
            # Check if user has admin permissions
            user_permissions = self.get_user_permissions(user_id)
            if "*:*:*" not in user_permissions and "system:read:audit" not in user_permissions:
                return []
            
            # Filter audit log by date range if provided
            filtered_log = self.audit_log
            
            if start_date:
                filtered_log = [entry for entry in filtered_log if entry.get("timestamp", "") >= start_date]
            
            if end_date:
                filtered_log = [entry for entry in filtered_log if entry.get("timestamp", "") <= end_date]
            
            return filtered_log
            
        except Exception as e:
            self._log("audit_export_error", user_id, None, "error", {
                "error": str(e)
            })
            return []
    
    def _log(self, action: str, user_id: str, session_id: Optional[str],
             event_type: str, details: Dict[str, Any]):
        """Log security events for audit purposes."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "user_id": user_id,
                "session_id": session_id,
                "event_type": event_type,
                "details": details
            }
            
            self.audit_log.append(log_entry)
            
            if self.logger:
                self.logger.logger.info(f"Security {action}", extra=log_entry)
                
        except Exception:
            pass  # Don't let logging errors break security functionality


def create_rbac_abac_security(logger: Optional[HearthlinkLogger] = None) -> RBACABACSecurity:
    """
    Factory function to create RBAC/ABAC security system.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        Configured RBACABACSecurity instance
    """
    try:
        return RBACABACSecurity(logger=logger)
    except Exception as e:
        raise SecurityError(f"Failed to create RBAC/ABAC security: {str(e)}") from e 