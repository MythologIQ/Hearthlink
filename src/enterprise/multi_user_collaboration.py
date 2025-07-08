#!/usr/bin/env python3
"""
Multi-User Collaboration Module - Enterprise Feature

Minimum viable implementation of multi-user collaboration features for enterprise environments.
Provides user management, session sharing, and collaborative capabilities.

Features:
- User registration and authentication
- Session sharing and collaboration
- Real-time collaboration state management
- Access control and permissions
- Audit logging for collaborative actions

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
import hashlib
import traceback
import asyncio
from typing import Dict, Any, Optional, List, Union, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class CollaborationError(HearthlinkError):
    """Base exception for collaboration-related errors."""
    pass


class UserManagementError(CollaborationError):
    """Exception raised when user management operations fail."""
    pass


class SessionSharingError(CollaborationError):
    """Exception raised when session sharing operations fail."""
    pass


class PermissionError(CollaborationError):
    """Exception raised when permission checks fail."""
    pass


class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class SessionType(Enum):
    """Types of collaborative sessions."""
    COLLABORATIVE = "collaborative"
    PRESENTATION = "presentation"
    REVIEW = "review"
    BRAINSTORMING = "brainstorming"


class Permission(Enum):
    """Permission types for access control."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SHARE = "share"
    DELETE = "delete"


@dataclass
class User:
    """User entity for multi-user collaboration."""
    user_id: str
    username: str
    email: str
    role: UserRole
    created_at: str
    last_active: str
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborativeSession:
    """Collaborative session for multi-user interaction."""
    session_id: str
    name: str
    description: str
    session_type: SessionType
    created_by: str
    created_at: str
    participants: List[str] = field(default_factory=list)
    permissions: Dict[str, List[Permission]] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationEvent:
    """Event in collaborative session."""
    event_id: str
    session_id: str
    user_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessControl:
    """Access control configuration."""
    user_id: str
    resource_type: str
    resource_id: str
    permissions: List[Permission]
    granted_at: str
    granted_by: str
    expires_at: Optional[str] = None


class MultiUserCollaboration:
    """
    Multi-user collaboration system for enterprise environments.
    
    Provides user management, session sharing, and collaborative features
    with comprehensive access control and audit logging.
    """
    
    def __init__(self, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize multi-user collaboration system.
        
        Args:
            logger: Optional logger instance
            
        Raises:
            CollaborationError: If initialization fails
        """
        try:
            self.logger = logger or HearthlinkLogger()
            
            # User management
            self.users: Dict[str, User] = {}
            self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
            
            # Session management
            self.sessions: Dict[str, CollaborativeSession] = {}
            self.session_events: Dict[str, List[CollaborationEvent]] = defaultdict(list)
            
            # Access control
            self.access_controls: Dict[str, AccessControl] = {}
            self.user_permissions: Dict[str, Dict[str, List[Permission]]] = defaultdict(lambda: defaultdict(list))
            
            # Audit logging
            self.audit_log: List[Dict[str, Any]] = []
            
            # Initialize default admin user
            self._create_default_admin()
            
            self._log("multi_user_collaboration_initialized", "system", None, "system", {
                "users_count": len(self.users),
                "sessions_count": len(self.sessions)
            })
            
        except Exception as e:
            raise CollaborationError(f"Failed to initialize multi-user collaboration: {str(e)}") from e
    
    def _create_default_admin(self):
        """Create default admin user for system initialization."""
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@hearthlink.local",
            role=UserRole.ADMIN,
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            is_active=True
        )
        self.users["admin"] = admin_user
        
        # Grant admin permissions
        self._grant_permissions("admin", "system", "all", [Permission.ADMIN], "system")
    
    def register_user(self, username: str, email: str, role: UserRole = UserRole.USER) -> str:
        """
        Register a new user in the collaboration system.
        
        Args:
            username: Unique username
            email: User email address
            role: User role for access control
            
        Returns:
            User ID of the newly created user
            
        Raises:
            UserManagementError: If user registration fails
        """
        try:
            # Validate input
            if not username or not email:
                raise UserManagementError("Username and email are required")
            
            # Check for existing user
            for user in self.users.values():
                if user.username == username or user.email == email:
                    raise UserManagementError("Username or email already exists")
            
            # Create new user
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                created_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat(),
                is_active=True
            )
            
            self.users[user_id] = user
            
            # Grant basic permissions based on role
            self._grant_role_permissions(user_id, role)
            
            self._log("user_registered", user_id, None, "user_management", {
                "username": username,
                "email": email,
                "role": role.value
            })
            
            return user_id
            
        except Exception as e:
            raise UserManagementError(f"Failed to register user: {str(e)}") from e
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[str]:
        """
        Authenticate a user (placeholder for future implementation).
        
        Args:
            username: Username to authenticate
            password_hash: Hashed password
            
        Returns:
            User ID if authentication successful, None otherwise
        """
        try:
            # Find user by username
            for user in self.users.values():
                if user.username == username and user.is_active:
                    # Placeholder authentication - in real implementation, verify password hash
                    user.last_active = datetime.now().isoformat()
                    
                    self._log("user_authenticated", user.user_id, None, "authentication", {
                        "username": username
                    })
                    
                    return user.user_id
            
            return None
            
        except Exception as e:
            self._log("authentication_error", "system", None, "error", {
                "error": str(e),
                "username": username
            })
            return None
    
    def create_collaborative_session(self, name: str, description: str, 
                                   session_type: SessionType, created_by: str) -> str:
        """
        Create a new collaborative session.
        
        Args:
            name: Session name
            description: Session description
            session_type: Type of collaborative session
            created_by: User ID of session creator
            
        Returns:
            Session ID of the newly created session
            
        Raises:
            SessionSharingError: If session creation fails
        """
        try:
            # Validate user exists
            if created_by not in self.users:
                raise SessionSharingError("Creator user does not exist")
            
            # Create session
            session_id = str(uuid.uuid4())
            session = CollaborativeSession(
                session_id=session_id,
                name=name,
                description=description,
                session_type=session_type,
                created_by=created_by,
                created_at=datetime.now().isoformat(),
                participants=[created_by],
                permissions={created_by: [Permission.ADMIN]},
                is_active=True
            )
            
            self.sessions[session_id] = session
            self.user_sessions[created_by].add(session_id)
            
            # Grant creator full permissions
            self._grant_permissions(created_by, "session", session_id, 
                                  [Permission.READ, Permission.WRITE, Permission.ADMIN], created_by)
            
            self._log("session_created", created_by, session_id, "session_management", {
                "session_name": name,
                "session_type": session_type.value
            })
            
            return session_id
            
        except Exception as e:
            raise SessionSharingError(f"Failed to create collaborative session: {str(e)}") from e
    
    def join_session(self, session_id: str, user_id: str) -> bool:
        """
        Join a collaborative session.
        
        Args:
            session_id: Session to join
            user_id: User joining the session
            
        Returns:
            True if successfully joined, False otherwise
            
        Raises:
            SessionSharingError: If join operation fails
        """
        try:
            # Validate session exists
            if session_id not in self.sessions:
                raise SessionSharingError("Session does not exist")
            
            session = self.sessions[session_id]
            
            # Check if user is already a participant
            if user_id in session.participants:
                return True
            
            # Add user to session
            session.participants.append(user_id)
            self.user_sessions[user_id].add(session_id)
            
            # Grant basic read permission automatically when joining
            if user_id not in session.permissions:
                session.permissions[user_id] = [Permission.READ]
                # Also update the permission cache
                self._grant_permissions(user_id, "session", session_id, [Permission.READ], "system")
            
            self._log("user_joined_session", user_id, session_id, "session_management", {
                "session_name": session.name
            })
            
            return True
            
        except Exception as e:
            raise SessionSharingError(f"Failed to join session: {str(e)}") from e
    
    def leave_session(self, session_id: str, user_id: str) -> bool:
        """
        Leave a collaborative session.
        
        Args:
            session_id: Session to leave
            user_id: User leaving the session
            
        Returns:
            True if successfully left, False otherwise
        """
        try:
            # Validate session exists
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Remove user from session
            if user_id in session.participants:
                session.participants.remove(user_id)
                self.user_sessions[user_id].discard(session_id)
                
                # Remove session permissions
                if user_id in session.permissions:
                    del session.permissions[user_id]
                
                self._log("user_left_session", user_id, session_id, "session_management", {
                    "session_name": session.name
                })
                
                return True
            
            return False
            
        except Exception as e:
            self._log("leave_session_error", user_id, session_id, "error", {
                "error": str(e)
            })
            return False
    
    def share_session(self, session_id: str, from_user_id: str, 
                     to_user_id: str, permissions: List[Permission]) -> bool:
        """
        Share a session with another user.
        
        Args:
            session_id: Session to share
            from_user_id: User sharing the session
            to_user_id: User to share with
            permissions: Permissions to grant
            
        Returns:
            True if successfully shared, False otherwise
            
        Raises:
            PermissionError: If user lacks permission to share
        """
        try:
            # Validate users exist
            if from_user_id not in self.users or to_user_id not in self.users:
                return False
            
            # Check if session exists
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Check if sharing user has share permission
            if not self._has_permission(from_user_id, "session", session_id, Permission.SHARE):
                raise PermissionError("User does not have permission to share session")
            
            # Grant permissions to target user
            if to_user_id not in session.permissions:
                session.permissions[to_user_id] = []
            
            for permission in permissions:
                if permission not in session.permissions[to_user_id]:
                    session.permissions[to_user_id].append(permission)
            
            # Add user to participants if not already present
            if to_user_id not in session.participants:
                session.participants.append(to_user_id)
                self.user_sessions[to_user_id].add(session_id)
            
            self._log("session_shared", from_user_id, session_id, "session_sharing", {
                "shared_with": to_user_id,
                "permissions": [p.value for p in permissions]
            })
            
            return True
            
        except Exception as e:
            raise PermissionError(f"Failed to share session: {str(e)}") from e
    
    def record_collaboration_event(self, session_id: str, user_id: str, 
                                 event_type: str, data: Dict[str, Any]) -> str:
        """
        Record an event in a collaborative session.
        
        Args:
            session_id: Session where event occurred
            user_id: User who triggered the event
            event_type: Type of event
            data: Event data
            
        Returns:
            Event ID of the recorded event
        """
        try:
            # Validate session exists
            if session_id not in self.sessions:
                raise SessionSharingError("Session does not exist")
            
            # Create event
            event_id = str(uuid.uuid4())
            event = CollaborationEvent(
                event_id=event_id,
                session_id=session_id,
                user_id=user_id,
                event_type=event_type,
                timestamp=datetime.now().isoformat(),
                data=data
            )
            
            self.session_events[session_id].append(event)
            
            # Update session state if needed
            if event_type == "state_update":
                self.sessions[session_id].state.update(data)
            
            self._log("collaboration_event_recorded", user_id, session_id, "collaboration", {
                "event_type": event_type,
                "event_id": event_id
            })
            
            return event_id
            
        except Exception as e:
            self._log("event_recording_error", user_id, session_id, "error", {
                "error": str(e),
                "event_type": event_type
            })
            raise SessionSharingError(f"Failed to record collaboration event: {str(e)}") from e
    
    def get_session_events(self, session_id: str, user_id: str, 
                          limit: Optional[int] = None) -> List[CollaborationEvent]:
        """
        Get events from a collaborative session.
        
        Args:
            session_id: Session to get events from
            user_id: User requesting events
            limit: Maximum number of events to return
            
        Returns:
            List of collaboration events
            
        Raises:
            PermissionError: If user lacks permission to view events
        """
        try:
            # Check permissions
            if not self._has_permission(user_id, "session", session_id, Permission.READ):
                raise PermissionError("User does not have permission to view session events")
            
            events = self.session_events.get(session_id, [])
            
            if limit:
                events = events[-limit:]
            
            return events
            
        except Exception as e:
            raise PermissionError(f"Failed to get session events: {str(e)}") from e
    
    def _grant_permissions(self, user_id: str, resource_type: str, resource_id: str,
                          permissions: List[Permission], granted_by: str):
        """Grant permissions to a user for a specific resource."""
        try:
            access_control = AccessControl(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                permissions=permissions,
                granted_at=datetime.now().isoformat(),
                granted_by=granted_by
            )
            
            control_id = f"{user_id}:{resource_type}:{resource_id}"
            self.access_controls[control_id] = access_control
            
            # Update user permissions cache
            self.user_permissions[user_id][f"{resource_type}:{resource_id}"] = permissions
            
        except Exception as e:
            self._log("permission_grant_error", granted_by, None, "error", {
                "error": str(e),
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id
            })
    
    def _grant_role_permissions(self, user_id: str, role: UserRole):
        """Grant default permissions based on user role."""
        try:
            if role == UserRole.ADMIN:
                permissions = [Permission.ADMIN]
            elif role == UserRole.MANAGER:
                permissions = [Permission.READ, Permission.WRITE, Permission.SHARE]
            elif role == UserRole.USER:
                permissions = [Permission.READ, Permission.WRITE]
            else:  # GUEST
                permissions = [Permission.READ]
            
            self._grant_permissions(user_id, "system", "default", permissions, "system")
            
        except Exception as e:
            self._log("role_permission_error", "system", None, "error", {
                "error": str(e),
                "user_id": user_id,
                "role": role.value
            })
    
    def _has_permission(self, user_id: str, resource_type: str, resource_id: str, 
                       permission: Permission) -> bool:
        """Check if user has specific permission for a resource."""
        try:
            # For session permissions, check both cache and session permissions
            if resource_type == "session":
                # Check session permissions directly
                if resource_id in self.sessions:
                    session = self.sessions[resource_id]
                    if user_id in session.permissions:
                        user_perms = session.permissions[user_id]
                        # Check for admin permission
                        if Permission.ADMIN in user_perms:
                            return True
                        # Check for specific permission
                        if permission in user_perms:
                            return True
            
            # Check user permissions cache
            resource_key = f"{resource_type}:{resource_id}"
            user_perms = self.user_permissions[user_id].get(resource_key, [])
            
            # Check for admin permission
            if Permission.ADMIN in user_perms:
                return True
            
            # Check for specific permission
            return permission in user_perms
            
        except Exception as e:
            self._log("permission_check_error", user_id, None, "error", {
                "error": str(e),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "permission": permission.value
            })
            return False
    
    def get_user_sessions(self, user_id: str) -> List[CollaborativeSession]:
        """Get all sessions for a user."""
        try:
            user_session_ids = self.user_sessions.get(user_id, set())
            sessions = []
            
            for session_id in user_session_ids:
                if session_id in self.sessions:
                    sessions.append(self.sessions[session_id])
            
            return sessions
            
        except Exception as e:
            self._log("get_user_sessions_error", user_id, None, "error", {
                "error": str(e)
            })
            return []
    
    def get_session_participants(self, session_id: str) -> List[User]:
        """Get all participants in a session."""
        try:
            if session_id not in self.sessions:
                return []
            
            session = self.sessions[session_id]
            participants = []
            
            for user_id in session.participants:
                if user_id in self.users:
                    participants.append(self.users[user_id])
            
            return participants
            
        except Exception as e:
            self._log("get_participants_error", "system", session_id, "error", {
                "error": str(e)
            })
            return []
    
    def export_audit_log(self, user_id: str, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export audit log for compliance purposes."""
        try:
            # Check if user has admin permissions
            if not self._has_permission(user_id, "system", "audit", [Permission.READ]):
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
        """Log collaboration events for audit purposes."""
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
                self.logger.logger.info(f"Collaboration {action}", extra=log_entry)
                
        except Exception:
            pass  # Don't let logging errors break collaboration functionality


def create_multi_user_collaboration(logger: Optional[HearthlinkLogger] = None) -> MultiUserCollaboration:
    """
    Factory function to create multi-user collaboration system.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        Configured MultiUserCollaboration instance
    """
    try:
        return MultiUserCollaboration(logger=logger)
    except Exception as e:
        raise CollaborationError(f"Failed to create multi-user collaboration: {str(e)}") from e 