"""
Synapse Security Manager

Comprehensive security management for all Synapse modules including:
- Sentry hooks for monitoring outbound requests and agent interactions
- Permission/role enforcement for external access
- Rate limiting for outbound API and browsing actions
- Audit logging for all external interactions
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict
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


class PermissionType(Enum):
    """Permission types for external access."""
    BROWSER_PREVIEW = "browser_preview"
    WEBHOOK_OUTBOUND = "webhook_outbound"
    CREDENTIAL_ACCESS = "credential_access"
    API_EXTERNAL = "api_external"
    NETWORK_ACCESS = "network_access"
    FILE_SYSTEM = "file_system"


class AgentType(Enum):
    """Agent types for permission enforcement."""
    ALDEN = "alden"
    ALICE = "alice"
    MIMIC = "mimic"
    SENTRY = "sentry"
    CORE = "core"
    EXTERNAL = "external"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    timestamp: str
    agent_id: str
    agent_type: AgentType
    action: str
    target: str
    permission_required: PermissionType
    security_level: SecurityLevel
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: int = 0
    sentry_alerted: bool = False


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    cooldown_seconds: int = 300


@dataclass
class PermissionConfig:
    """Permission configuration for agents."""
    agent_type: AgentType
    allowed_permissions: Set[PermissionType] = field(default_factory=set)
    rate_limits: Dict[PermissionType, RateLimitConfig] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.MEDIUM


class SentryHook:
    """Sentry integration for security monitoring."""
    
    def __init__(self, sentry_instance=None):
        self.sentry = sentry_instance
        self.alert_thresholds = {
            SecurityLevel.LOW: 10,      # 10 events per minute
            SecurityLevel.MEDIUM: 5,    # 5 events per minute
            SecurityLevel.HIGH: 2,      # 2 events per minute
            SecurityLevel.CRITICAL: 1   # 1 event per minute
        }
        self.event_counts = defaultdict(int)
        self.last_reset = time.time()
    
    def log_security_event(self, event: SecurityEvent):
        """Log security event to Sentry."""
        if not self.sentry:
            logger.warning("Sentry not available for security event logging")
            return
        
        try:
            # Check if we should alert based on frequency
            current_time = time.time()
            if current_time - self.last_reset > 60:  # Reset every minute
                self.event_counts.clear()
                self.last_reset = current_time
            
            key = f"{event.agent_type.value}_{event.security_level.value}"
            self.event_counts[key] += 1
            
            # Check threshold
            threshold = self.alert_thresholds[event.security_level]
            if self.event_counts[key] >= threshold:
                self._send_sentry_alert(event)
                event.sentry_alerted = True
            
            # Log all events to Sentry
            self.sentry.capture_message(
                f"Security Event: {event.action} by {event.agent_id}",
                level="warning" if event.success else "error",
                extra={
                    "event_id": event.event_id,
                    "agent_type": event.agent_type.value,
                    "action": event.action,
                    "target": event.target,
                    "permission": event.permission_required.value,
                    "security_level": event.security_level.value,
                    "success": event.success,
                    "risk_score": event.risk_score,
                    "details": event.details
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event to Sentry: {e}")
    
    def _send_sentry_alert(self, event: SecurityEvent):
        """Send high-priority alert to Sentry."""
        if not self.sentry:
            return
        
        try:
            self.sentry.capture_message(
                f"SECURITY ALERT: High frequency {event.security_level.value} events from {event.agent_type.value}",
                level="error",
                extra={
                    "event_count": self.event_counts[f"{event.agent_type.value}_{event.security_level.value}"],
                    "threshold": self.alert_thresholds[event.security_level],
                    "agent_id": event.agent_id,
                    "action": event.action
                }
            )
        except Exception as e:
            logger.error(f"Failed to send Sentry alert: {e}")


class RateLimiter:
    """Rate limiting for external actions."""
    
    def __init__(self):
        self.request_counts: Dict[str, List[float]] = defaultdict(list)
        self.blocked_agents: Dict[str, float] = {}
    
    def check_rate_limit(self, agent_id: str, permission_type: PermissionType, 
                        config: RateLimitConfig) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Check if agent is blocked
        if agent_id in self.blocked_agents:
            if current_time - self.blocked_agents[agent_id] < config.cooldown_seconds:
                return False
            else:
                del self.blocked_agents[agent_id]
        
        # Get request history for this agent/permission combination
        key = f"{agent_id}_{permission_type.value}"
        requests = self.request_counts[key]
        
        # Remove old requests (older than 1 hour)
        requests = [req_time for req_time in requests if current_time - req_time < 3600]
        self.request_counts[key] = requests
        
        # Check minute limit
        minute_requests = [req_time for req_time in requests if current_time - req_time < 60]
        if len(minute_requests) >= config.requests_per_minute:
            self.blocked_agents[agent_id] = current_time
            return False
        
        # Check hour limit
        if len(requests) >= config.requests_per_hour:
            self.blocked_agents[agent_id] = current_time
            return False
        
        # Check burst limit
        recent_requests = [req_time for req_time in requests if current_time - req_time < 10]
        if len(recent_requests) >= config.burst_limit:
            return False
        
        # Add current request
        requests.append(current_time)
        return True
    
    def get_rate_limit_status(self, agent_id: str, permission_type: PermissionType) -> Dict[str, Any]:
        """Get current rate limit status for agent."""
        key = f"{agent_id}_{permission_type.value}"
        requests = self.request_counts[key]
        current_time = time.time()
        
        minute_requests = [req_time for req_time in requests if current_time - req_time < 60]
        hour_requests = [req_time for req_time in requests if current_time - req_time < 3600]
        
        return {
            "agent_id": agent_id,
            "permission_type": permission_type.value,
            "requests_last_minute": len(minute_requests),
            "requests_last_hour": len(hour_requests),
            "is_blocked": agent_id in self.blocked_agents,
            "blocked_until": self.blocked_agents.get(agent_id, None)
        }


class SecurityManager:
    """Main security manager for Synapse modules."""
    
    def __init__(self, sentry_instance=None, log_file: str = "logs/synapse-actions.json"):
        self.sentry_hook = SentryHook(sentry_instance)
        self.rate_limiter = RateLimiter()
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Permission configurations
        self.permission_configs = self._initialize_permission_configs()
        
        # Security event history
        self.security_events: List[SecurityEvent] = []
        self.max_events = 10000  # Keep last 10k events in memory
        
        # Risk scoring weights
        self.risk_weights = {
            "external_agent": 10,
            "credential_access": 8,
            "network_access": 5,
            "file_system": 7,
            "high_frequency": 3,
            "failed_auth": 5
        }
    
    def _initialize_permission_configs(self) -> Dict[AgentType, PermissionConfig]:
        """Initialize permission configurations for different agent types."""
        configs = {}
        
        # Local agents (Alden, Alice, Mimic, Sentry, Core)
        local_agents = [AgentType.ALDEN, AgentType.ALICE, AgentType.MIMIC, 
                       AgentType.SENTRY, AgentType.CORE]
        
        for agent_type in local_agents:
            configs[agent_type] = PermissionConfig(
                agent_type=agent_type,
                allowed_permissions={
                    PermissionType.BROWSER_PREVIEW,
                    PermissionType.WEBHOOK_OUTBOUND,
                    PermissionType.CREDENTIAL_ACCESS,
                    PermissionType.API_EXTERNAL,
                    PermissionType.NETWORK_ACCESS
                },
                rate_limits={
                    PermissionType.BROWSER_PREVIEW: RateLimitConfig(30, 500, 5),
                    PermissionType.WEBHOOK_OUTBOUND: RateLimitConfig(60, 1000, 10),
                    PermissionType.CREDENTIAL_ACCESS: RateLimitConfig(10, 100, 2),
                    PermissionType.API_EXTERNAL: RateLimitConfig(40, 800, 8),
                    PermissionType.NETWORK_ACCESS: RateLimitConfig(50, 900, 10)
                },
                security_level=SecurityLevel.MEDIUM
            )
        
        # External agents (restricted)
        configs[AgentType.EXTERNAL] = PermissionConfig(
            agent_type=AgentType.EXTERNAL,
            allowed_permissions={
                PermissionType.BROWSER_PREVIEW,
                PermissionType.API_EXTERNAL
            },
            rate_limits={
                PermissionType.BROWSER_PREVIEW: RateLimitConfig(10, 100, 2),
                PermissionType.API_EXTERNAL: RateLimitConfig(20, 200, 3)
            },
            security_level=SecurityLevel.HIGH
        )
        
        return configs
    
    def check_permission(self, agent_id: str, agent_type: AgentType, 
                        permission_type: PermissionType, action: str, 
                        target: str, details: Dict[str, Any] = None) -> bool:
        """Check if agent has permission for action."""
        # Get agent configuration
        config = self.permission_configs.get(agent_type)
        if not config:
            return False
        
        # Check if permission is allowed
        if permission_type not in config.allowed_permissions:
            self._log_security_event(agent_id, agent_type, action, target, 
                                   permission_type, config.security_level, False, details)
            return False
        
        # Check rate limits
        rate_config = config.rate_limits.get(permission_type)
        if rate_config and not self.rate_limiter.check_rate_limit(agent_id, permission_type, rate_config):
            rate_limit_details = {"reason": "rate_limit_exceeded"}
            if details:
                rate_limit_details.update(details)
            self._log_security_event(agent_id, agent_type, action, target, 
                                   permission_type, config.security_level, False, 
                                   rate_limit_details)
            return False
        
        # Log successful permission check
        self._log_security_event(agent_id, agent_type, action, target, 
                               permission_type, config.security_level, True, details)
        return True
    
    def _log_security_event(self, agent_id: str, agent_type: AgentType, action: str, 
                           target: str, permission_type: PermissionType, 
                           security_level: SecurityLevel, success: bool, 
                           details: Dict[str, Any] = None):
        """Log security event."""
        event_id = f"sec_{int(time.time())}_{secrets.token_hex(4)}"
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(agent_type, permission_type, 
                                              security_level, success, details)
        
        event = SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            agent_type=agent_type,
            action=action,
            target=target,
            permission_required=permission_type,
            security_level=security_level,
            success=success,
            details=details or {},
            risk_score=risk_score
        )
        
        # Add to memory
        self.security_events.append(event)
        if len(self.security_events) > self.max_events:
            self.security_events.pop(0)
        
        # Log to file
        self._write_event_to_log(event)
        
        # Send to Sentry
        self.sentry_hook.log_security_event(event)
        
        logger.info(f"Security event logged: {event_id} - {action} by {agent_id} - {'SUCCESS' if success else 'DENIED'}")
    
    def _calculate_risk_score(self, agent_type: AgentType, permission_type: PermissionType,
                            security_level: SecurityLevel, success: bool, 
                            details: Dict[str, Any] = None) -> int:
        """Calculate risk score for security event."""
        score = 0
        
        # Agent type risk
        if agent_type == AgentType.EXTERNAL:
            score += self.risk_weights["external_agent"]
        
        # Permission type risk
        if permission_type == PermissionType.CREDENTIAL_ACCESS:
            score += self.risk_weights["credential_access"]
        elif permission_type == PermissionType.NETWORK_ACCESS:
            score += self.risk_weights["network_access"]
        elif permission_type == PermissionType.FILE_SYSTEM:
            score += self.risk_weights["file_system"]
        
        # Security level risk
        if security_level == SecurityLevel.HIGH:
            score += 5
        elif security_level == SecurityLevel.CRITICAL:
            score += 10
        
        # Failed authentication
        if not success and details and details.get("reason") == "auth_failed":
            score += self.risk_weights["failed_auth"]
        
        # High frequency activity
        if details and details.get("reason") == "rate_limit_exceeded":
            score += self.risk_weights["high_frequency"]
        
        return min(score, 100)  # Cap at 100
    
    def _write_event_to_log(self, event: SecurityEvent):
        """Write security event to log file."""
        try:
            log_entry = {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "agent_id": event.agent_id,
                "agent_type": event.agent_type.value,
                "action": event.action,
                "target": event.target,
                "permission_required": event.permission_required.value,
                "security_level": event.security_level.value,
                "success": event.success,
                "risk_score": event.risk_score,
                "sentry_alerted": event.sentry_alerted,
                "details": event.details
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write security event to log: {e}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary and statistics."""
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        day_ago = current_time - timedelta(days=1)
        
        # Filter events by time
        recent_events = [e for e in self.security_events 
                        if datetime.fromisoformat(e.timestamp) > hour_ago]
        daily_events = [e for e in self.security_events 
                       if datetime.fromisoformat(e.timestamp) > day_ago]
        
        # Calculate statistics
        total_events = len(self.security_events)
        recent_count = len(recent_events)
        daily_count = len(daily_events)
        
        success_count = len([e for e in self.security_events if e.success])
        denied_count = total_events - success_count
        
        high_risk_events = len([e for e in self.security_events if e.risk_score > 50])
        
        # Agent activity
        agent_activity = defaultdict(int)
        for event in self.security_events:
            agent_activity[event.agent_type.value] += 1
        
        # Permission usage
        permission_usage = defaultdict(int)
        for event in self.security_events:
            permission_usage[event.permission_required.value] += 1
        
        return {
            "summary": {
                "total_events": total_events,
                "recent_events_1h": recent_count,
                "daily_events_24h": daily_count,
                "successful_requests": success_count,
                "denied_requests": denied_count,
                "high_risk_events": high_risk_events,
                "success_rate": (success_count / total_events * 100) if total_events > 0 else 0
            },
            "agent_activity": dict(agent_activity),
            "permission_usage": dict(permission_usage),
            "rate_limit_status": self._get_rate_limit_status(),
            "last_updated": current_time.isoformat()
        }
    
    def _get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status for all agents."""
        status = {}
        for agent_type in AgentType:
            config = self.permission_configs.get(agent_type)
            if config:
                status[agent_type.value] = {
                    "allowed_permissions": [p.value for p in config.allowed_permissions],
                    "rate_limits": {
                        p.value: {
                            "requests_per_minute": rl.requests_per_minute,
                            "requests_per_hour": rl.requests_per_hour,
                            "burst_limit": rl.burst_limit
                        }
                        for p, rl in config.rate_limits.items()
                    },
                    "security_level": config.security_level.value
                }
        return status
    
    def get_agent_permissions(self, agent_type: AgentType) -> Set[PermissionType]:
        """Get allowed permissions for agent type."""
        config = self.permission_configs.get(agent_type)
        return config.allowed_permissions if config else set()
    
    def get_rate_limit_status_for_agent(self, agent_id: str, 
                                       permission_type: PermissionType) -> Dict[str, Any]:
        """Get rate limit status for specific agent and permission."""
        return self.rate_limiter.get_rate_limit_status(agent_id, permission_type)
    
    def clear_security_events(self):
        """Clear security events (for testing/debugging)."""
        self.security_events.clear()
        logger.info("Security events cleared")


# Global security manager instance
security_manager = SecurityManager()


def check_synapse_permission(agent_id: str, agent_type: AgentType, 
                           permission_type: PermissionType, action: str, 
                           target: str, details: Dict[str, Any] = None) -> bool:
    """Check permission for Synapse operations."""
    return security_manager.check_permission(agent_id, agent_type, permission_type, 
                                           action, target, details)


def get_security_summary() -> Dict[str, Any]:
    """Get security summary."""
    return security_manager.get_security_summary()


def get_agent_permissions(agent_type: AgentType) -> Set[PermissionType]:
    """Get allowed permissions for agent type."""
    return security_manager.get_agent_permissions(agent_type) 