"""
Security Monitor for SYN004/SYN005 and All Synapse Modules

Comprehensive security monitoring with Sentry hooks, permission enforcement,
rate limiting, and audit logging for all external interactions.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable
from collections import defaultdict, deque
import hashlib
import hmac
import secrets

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of actions that can be monitored."""
    WEBHOOK_REQUEST = "webhook_request"
    API_CALL = "api_call"
    BROWSER_PREVIEW = "browser_preview"
    CREDENTIAL_ACCESS = "credential_access"
    CREDENTIAL_INJECTION = "credential_injection"
    AGENT_INTERACTION = "agent_interaction"
    PERMISSION_REQUEST = "permission_request"
    SESSION_CREATION = "session_creation"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    timestamp: str
    action_type: ActionType
    agent_id: str
    user_id: str
    target_url: Optional[str] = None
    target_domain: Optional[str] = None
    success: bool = True
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    rate_limit_hit: bool = False
    permission_denied: bool = False


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60  # seconds


@dataclass
class PermissionConfig:
    """Permission configuration."""
    allowed_agents: Set[str] = field(default_factory=set)
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    require_approval: bool = True
    auto_approve_low_risk: bool = False


class RateLimiter:
    """Rate limiting implementation with sliding window."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limits."""
        async with self.lock:
            now = time.time()
            window_start = now - self.config.window_size
            
            # Clean old requests
            if key in self.requests:
                while self.requests[key] and self.requests[key][0] < window_start:
                    self.requests[key].popleft()
            
            # Check limits
            current_requests = len(self.requests[key])
            
            if current_requests >= self.config.requests_per_minute:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    async def get_rate_limit_status(self, key: str) -> Dict[str, Any]:
        """Get current rate limit status for key."""
        async with self.lock:
            now = time.time()
            window_start = now - self.config.window_size
            
            if key in self.requests:
                # Clean old requests
                while self.requests[key] and self.requests[key][0] < window_start:
                    self.requests[key].popleft()
                
                current_requests = len(self.requests[key])
            else:
                current_requests = 0
            
            return {
                "current_requests": current_requests,
                "limit_per_minute": self.config.requests_per_minute,
                "limit_per_hour": self.config.requests_per_hour,
                "burst_limit": self.config.burst_limit,
                "window_size": self.config.window_size,
                "remaining": max(0, self.config.requests_per_minute - current_requests)
            }


class PermissionManager:
    """Permission management and enforcement."""
    
    def __init__(self, config: PermissionConfig):
        self.config = config
        self.approved_requests: Set[str] = set()
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
    
    def check_permission(self, agent_id: str, action_type: ActionType, 
                        target_domain: Optional[str] = None) -> bool:
        """Check if agent has permission for action."""
        # Check if agent is allowed
        if agent_id not in self.config.allowed_agents:
            return False
        
        # Check domain restrictions
        if target_domain:
            if target_domain in self.config.blocked_domains:
                return False
            
            if self.config.allowed_domains and target_domain not in self.config.allowed_domains:
                return False
        
        # Check if approval is required
        if self.config.require_approval and not self.config.auto_approve_low_risk:
            # For now, require manual approval for high-risk actions
            if action_type in [ActionType.CREDENTIAL_INJECTION, ActionType.API_CALL]:
                return False
        
        return True
    
    def request_approval(self, request_id: str, agent_id: str, action_type: ActionType,
                        target_domain: Optional[str] = None) -> str:
        """Request approval for action."""
        self.pending_requests[request_id] = {
            "agent_id": agent_id,
            "action_type": action_type,
            "target_domain": target_domain,
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }
        return request_id
    
    def approve_request(self, request_id: str, approved_by: str) -> bool:
        """Approve a pending request."""
        if request_id in self.pending_requests:
            self.pending_requests[request_id]["status"] = "approved"
            self.pending_requests[request_id]["approved_by"] = approved_by
            self.pending_requests[request_id]["approved_at"] = datetime.now().isoformat()
            self.approved_requests.add(request_id)
            return True
        return False
    
    def deny_request(self, request_id: str, denied_by: str, reason: str) -> bool:
        """Deny a pending request."""
        if request_id in self.pending_requests:
            self.pending_requests[request_id]["status"] = "denied"
            self.pending_requests[request_id]["denied_by"] = denied_by
            self.pending_requests[request_id]["denied_at"] = datetime.now().isoformat()
            self.pending_requests[request_id]["denial_reason"] = reason
            return True
        return False


class SecurityMonitor:
    """Main security monitoring system."""
    
    def __init__(self, log_file: str = "logs/synapse-actions.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize components
        self.rate_limiter = RateLimiter(RateLimitConfig())
        self.permission_manager = PermissionManager(PermissionConfig())
        
        # Security hooks
        self.security_hooks: Dict[ActionType, List[Callable]] = defaultdict(list)
        
        # Event queue for async processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
        # Start background processing
        self.running = True
        asyncio.create_task(self._process_events())
        
        logger.info("Security monitor initialized")
    
    def register_security_hook(self, action_type: ActionType, hook: Callable):
        """Register a security hook for specific action type."""
        self.security_hooks[action_type].append(hook)
        logger.info(f"Registered security hook for {action_type}")
    
    async def log_security_event(self, event: SecurityEvent):
        """Log security event to file and trigger hooks."""
        # Add to processing queue
        await self.event_queue.put(event)
    
    async def _process_events(self):
        """Background event processing."""
        while self.running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Write to log file
                await self._write_event_to_log(event)
                
                # Trigger security hooks
                await self._trigger_hooks(event)
                
                # Mark as processed
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing security event: {e}")
    
    async def _write_event_to_log(self, event: SecurityEvent):
        """Write event to JSON log file."""
        try:
            # Read existing events
            events = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    try:
                        events = json.load(f)
                    except json.JSONDecodeError:
                        events = []
            
            # Add new event
            events.append(asdict(event))
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(events, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to write security event to log: {e}")
    
    async def _trigger_hooks(self, event: SecurityEvent):
        """Trigger security hooks for event."""
        hooks = self.security_hooks.get(event.action_type, [])
        
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(event)
                else:
                    hook(event)
            except Exception as e:
                logger.error(f"Security hook error: {e}")
    
    async def check_and_log_request(self, agent_id: str, user_id: str, 
                                   action_type: ActionType, target_url: Optional[str] = None,
                                   target_domain: Optional[str] = None) -> bool:
        """Check permissions and rate limits, log the request."""
        # Generate event ID
        event_id = f"evt_{secrets.token_hex(8)}"
        
        # Check rate limiting
        rate_limit_key = f"{agent_id}:{action_type.value}"
        rate_limit_allowed = await self.rate_limiter.check_rate_limit(rate_limit_key)
        
        # Check permissions
        permission_allowed = self.permission_manager.check_permission(
            agent_id, action_type, target_domain
        )
        
        # Determine success
        success = rate_limit_allowed and permission_allowed
        
        # Create security event
        event = SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            agent_id=agent_id,
            user_id=user_id,
            target_url=target_url,
            target_domain=target_domain,
            success=success,
            rate_limit_hit=not rate_limit_allowed,
            permission_denied=not permission_allowed,
            error_message=None if success else (
                "Rate limit exceeded" if not rate_limit_allowed else "Permission denied"
            )
        )
        
        # Log event
        await self.log_security_event(event)
        
        return success
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            "rate_limits": {
                "global": await self.rate_limiter.get_rate_limit_status("global"),
                "webhook": await self.rate_limiter.get_rate_limit_status("webhook"),
                "api": await self.rate_limiter.get_rate_limit_status("api"),
                "browser": await self.rate_limiter.get_rate_limit_status("browser")
            },
            "permissions": {
                "allowed_agents": list(self.permission_manager.config.allowed_agents),
                "allowed_domains": list(self.permission_manager.config.allowed_domains),
                "blocked_domains": list(self.permission_manager.config.blocked_domains),
                "pending_requests": len(self.permission_manager.pending_requests)
            },
            "log_file": str(self.log_file),
            "hooks_registered": {
                action_type.value: len(hooks) 
                for action_type, hooks in self.security_hooks.items()
            }
        }
    
    def stop(self):
        """Stop the security monitor."""
        self.running = False
        logger.info("Security monitor stopped")


# Global security monitor instance
security_monitor = SecurityMonitor()


# Sentry hooks for different modules
class SentryHooks:
    """Sentry hooks for monitoring and alerting."""
    
    @staticmethod
    async def webhook_security_hook(event: SecurityEvent):
        """Hook for webhook security events."""
        if not event.success:
            logger.warning(f"Webhook security violation: {event.error_message}")
            # Could trigger alerts, notifications, etc.
    
    @staticmethod
    async def credential_security_hook(event: SecurityEvent):
        """Hook for credential security events."""
        if event.action_type == ActionType.CREDENTIAL_ACCESS:
            logger.info(f"Credential access: {event.agent_id} -> {event.target_domain}")
        elif event.action_type == ActionType.CREDENTIAL_INJECTION:
            logger.warning(f"Credential injection: {event.agent_id} -> {event.target_domain}")
    
    @staticmethod
    async def rate_limit_hook(event: SecurityEvent):
        """Hook for rate limit violations."""
        if event.rate_limit_hit:
            logger.warning(f"Rate limit hit: {event.agent_id} -> {event.action_type}")
    
    @staticmethod
    async def permission_hook(event: SecurityEvent):
        """Hook for permission violations."""
        if event.permission_denied:
            logger.warning(f"Permission denied: {event.agent_id} -> {event.action_type}")


# Register default hooks
def register_default_hooks():
    """Register default security hooks."""
    security_monitor.register_security_hook(ActionType.WEBHOOK_REQUEST, SentryHooks.webhook_security_hook)
    security_monitor.register_security_hook(ActionType.CREDENTIAL_ACCESS, SentryHooks.credential_security_hook)
    security_monitor.register_security_hook(ActionType.CREDENTIAL_INJECTION, SentryHooks.credential_security_hook)
    security_monitor.register_security_hook(ActionType.RATE_LIMIT_VIOLATION, SentryHooks.rate_limit_hook)
    security_monitor.register_security_hook(ActionType.SECURITY_VIOLATION, SentryHooks.permission_hook)


# Initialize default hooks
register_default_hooks()


# Convenience functions for modules
async def check_webhook_request(agent_id: str, user_id: str, target_url: str) -> bool:
    """Check if webhook request is allowed."""
    from urllib.parse import urlparse
    target_domain = urlparse(target_url).netloc
    
    return await security_monitor.check_and_log_request(
        agent_id, user_id, ActionType.WEBHOOK_REQUEST, target_url, target_domain
    )


async def check_api_call(agent_id: str, user_id: str, target_url: str) -> bool:
    """Check if API call is allowed."""
    from urllib.parse import urlparse
    target_domain = urlparse(target_url).netloc
    
    return await security_monitor.check_and_log_request(
        agent_id, user_id, ActionType.API_CALL, target_url, target_domain
    )


async def check_browser_preview(agent_id: str, user_id: str, target_url: str) -> bool:
    """Check if browser preview is allowed."""
    from urllib.parse import urlparse
    target_domain = urlparse(target_url).netloc
    
    return await security_monitor.check_and_log_request(
        agent_id, user_id, ActionType.BROWSER_PREVIEW, target_url, target_domain
    )


async def check_credential_access(agent_id: str, user_id: str, target_domain: str) -> bool:
    """Check if credential access is allowed."""
    return await security_monitor.check_and_log_request(
        agent_id, user_id, ActionType.CREDENTIAL_ACCESS, None, target_domain
    )


async def check_credential_injection(agent_id: str, user_id: str, target_domain: str) -> bool:
    """Check if credential injection is allowed."""
    return await security_monitor.check_and_log_request(
        agent_id, user_id, ActionType.CREDENTIAL_INJECTION, None, target_domain
    )


async def get_security_status() -> Dict[str, Any]:
    """Get current security status."""
    return await security_monitor.get_security_status() 