"""
Sentry Integration for Synapse Security Monitoring

Hooks into all Synapse modules to monitor:
- Outbound requests and agent interactions
- Permission violations and security events
- Rate limiting and access control
- External API calls and browsing actions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps

from .security_manager import (
    SecurityManager, SecurityEvent, SecurityLevel, PermissionType, 
    AgentType, check_synapse_permission
)

logger = logging.getLogger(__name__)


class SentryMonitor:
    """Sentry monitoring for Synapse modules."""
    
    def __init__(self, sentry_instance=None):
        self.sentry = sentry_instance
        self.security_manager = SecurityManager(sentry_instance)
        self.monitored_modules = set()
        self.alert_callbacks = []
    
    def register_module(self, module_name: str):
        """Register a module for monitoring."""
        self.monitored_modules.add(module_name)
        logger.info(f"Registered module for Sentry monitoring: {module_name}")
    
    def add_alert_callback(self, callback):
        """Add callback for security alerts."""
        self.alert_callbacks.append(callback)
    
    def monitor_outbound_request(self, agent_id: str, agent_type: AgentType,
                               url: str, method: str, headers: Dict[str, str] = None,
                               data: Any = None, response_status: int = None,
                               response_time: float = None):
        """Monitor outbound HTTP requests."""
        try:
            # Determine permission type based on URL and method
            permission_type = self._determine_permission_type(url, method)
            
            # Check permission
            action = f"outbound_request_{method.lower()}"
            target = url
            
            details = {
                "url": url,
                "method": method,
                "headers_count": len(headers) if headers else 0,
                "has_data": bool(data),
                "response_status": response_status,
                "response_time": response_time
            }
            
            # Remove sensitive headers from details
            if headers:
                safe_headers = {k: v for k, v in headers.items() 
                              if k.lower() not in ['authorization', 'cookie', 'x-api-key']}
                details["safe_headers"] = safe_headers
            
            success = check_synapse_permission(agent_id, agent_type, permission_type, 
                                             action, target, details)
            
            # Log to Sentry if there are issues
            if not success or response_status and response_status >= 400:
                self._log_sentry_event(
                    f"Outbound request {'failed' if not success else 'error'}",
                    "warning" if not success else "error",
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type.value,
                        "url": url,
                        "method": method,
                        "response_status": response_status,
                        "permission_granted": success
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error monitoring outbound request: {e}")
            self._log_sentry_event("Outbound request monitoring error", "error", 
                                 {"error": str(e), "agent_id": agent_id})
            return False
    
    def monitor_agent_interaction(self, agent_id: str, agent_type: AgentType,
                                interaction_type: str, target: str, 
                                details: Dict[str, Any] = None):
        """Monitor agent interactions."""
        try:
            # Determine permission type based on interaction
            permission_type = self._determine_interaction_permission(interaction_type)
            
            action = f"agent_interaction_{interaction_type}"
            
            success = check_synapse_permission(agent_id, agent_type, permission_type, 
                                             action, target, details or {})
            
            # Log to Sentry for high-risk interactions
            if interaction_type in ['credential_access', 'file_system', 'system_command']:
                self._log_sentry_event(
                    f"High-risk agent interaction: {interaction_type}",
                    "warning",
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type.value,
                        "interaction_type": interaction_type,
                        "target": target,
                        "permission_granted": success
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error monitoring agent interaction: {e}")
            return False
    
    def monitor_browser_preview(self, agent_id: str, agent_type: AgentType,
                              url: str, content_size: int, security_violations: List[str] = None):
        """Monitor browser preview actions."""
        try:
            action = "browser_preview"
            target = url
            
            details = {
                "url": url,
                "content_size": content_size,
                "security_violations": security_violations or []
            }
            
            success = check_synapse_permission(agent_id, agent_type, 
                                             PermissionType.BROWSER_PREVIEW, 
                                             action, target, details)
            
            # Alert on security violations
            if security_violations:
                self._log_sentry_event(
                    f"Browser preview security violations: {len(security_violations)}",
                    "warning",
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type.value,
                        "url": url,
                        "violations": security_violations,
                        "permission_granted": success
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error monitoring browser preview: {e}")
            return False
    
    def monitor_webhook_config(self, agent_id: str, agent_type: AgentType,
                             endpoint_url: str, method: str, 
                             has_auth_headers: bool):
        """Monitor webhook configuration changes."""
        try:
            action = "webhook_config"
            target = endpoint_url
            
            details = {
                "endpoint_url": endpoint_url,
                "method": method,
                "has_auth_headers": has_auth_headers
            }
            
            success = check_synapse_permission(agent_id, agent_type, 
                                             PermissionType.WEBHOOK_OUTBOUND, 
                                             action, target, details)
            
            # Alert on webhook config changes
            self._log_sentry_event(
                f"Webhook configuration {'created' if success else 'denied'}",
                "info" if success else "warning",
                {
                    "agent_id": agent_id,
                    "agent_type": agent_type.value,
                    "endpoint_url": endpoint_url,
                    "method": method,
                    "has_auth": has_auth_headers,
                    "permission_granted": success
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error monitoring webhook config: {e}")
            return False
    
    def monitor_credential_access(self, agent_id: str, agent_type: AgentType,
                                domain: str, credential_type: str, 
                                access_method: str):
        """Monitor credential access attempts."""
        try:
            action = f"credential_access_{access_method}"
            target = domain
            
            details = {
                "domain": domain,
                "credential_type": credential_type,
                "access_method": access_method
            }
            
            success = check_synapse_permission(agent_id, agent_type, 
                                             PermissionType.CREDENTIAL_ACCESS, 
                                             action, target, details)
            
            # Always alert on credential access
            self._log_sentry_event(
                f"Credential access {'granted' if success else 'denied'}",
                "warning" if success else "error",
                {
                    "agent_id": agent_id,
                    "agent_type": agent_type.value,
                    "domain": domain,
                    "credential_type": credential_type,
                    "access_method": access_method,
                    "permission_granted": success
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error monitoring credential access: {e}")
            return False
    
    def _determine_permission_type(self, url: str, method: str) -> PermissionType:
        """Determine permission type based on URL and method."""
        url_lower = url.lower()
        
        if "api." in url_lower or "api/" in url_lower:
            return PermissionType.API_EXTERNAL
        elif method in ["POST", "PUT", "DELETE"]:
            return PermissionType.WEBHOOK_OUTBOUND
        else:
            return PermissionType.NETWORK_ACCESS
    
    def _determine_interaction_permission(self, interaction_type: str) -> PermissionType:
        """Determine permission type based on interaction type."""
        interaction_lower = interaction_type.lower()
        
        if "credential" in interaction_lower:
            return PermissionType.CREDENTIAL_ACCESS
        elif "file" in interaction_lower or "system" in interaction_lower:
            return PermissionType.FILE_SYSTEM
        elif "api" in interaction_lower:
            return PermissionType.API_EXTERNAL
        else:
            return PermissionType.NETWORK_ACCESS
    
    def _log_sentry_event(self, message: str, level: str, extra: Dict[str, Any]):
        """Log event to Sentry."""
        if not self.sentry:
            logger.warning(f"Sentry not available: {message}")
            return
        
        try:
            self.sentry.capture_message(
                message,
                level=level,
                extra=extra
            )
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(message, level, extra)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to log to Sentry: {e}")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        return {
            "monitored_modules": list(self.monitored_modules),
            "security_summary": self.security_manager.get_security_summary(),
            "alert_callbacks_count": len(self.alert_callbacks),
            "last_updated": datetime.now().isoformat()
        }


# Decorator for monitoring functions
def monitor_synapse_operation(permission_type: PermissionType, 
                            security_level: SecurityLevel = SecurityLevel.MEDIUM):
    """Decorator to monitor Synapse operations."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract agent info from function signature
            agent_id = kwargs.get('agent_id', 'unknown')
            agent_type = kwargs.get('agent_type', AgentType.EXTERNAL)
            
            # Monitor the operation
            action = f"{func.__name__}_operation"
            target = kwargs.get('target', 'unknown')
            
            success = check_synapse_permission(agent_id, agent_type, permission_type, 
                                             action, target, kwargs)
            
            if not success:
                raise PermissionError(f"Permission denied for {action}")
            
            # Execute the function
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # Log error to Sentry
                if hasattr(func, '_sentry_monitor'):
                    func._sentry_monitor._log_sentry_event(
                        f"Operation error: {func.__name__}",
                        "error",
                        {"error": str(e), "agent_id": agent_id}
                    )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract agent info from function signature
            agent_id = kwargs.get('agent_id', 'unknown')
            agent_type = kwargs.get('agent_type', AgentType.EXTERNAL)
            
            # Monitor the operation
            action = f"{func.__name__}_operation"
            target = kwargs.get('target', 'unknown')
            
            success = check_synapse_permission(agent_id, agent_type, permission_type, 
                                             action, target, kwargs)
            
            if not success:
                raise PermissionError(f"Permission denied for {action}")
            
            # Execute the function
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Log error to Sentry
                if hasattr(func, '_sentry_monitor'):
                    func._sentry_monitor._log_sentry_event(
                        f"Operation error: {func.__name__}",
                        "error",
                        {"error": str(e), "agent_id": agent_id}
                    )
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global Sentry monitor instance
sentry_monitor = SentryMonitor()


def get_sentry_monitor() -> SentryMonitor:
    """Get global Sentry monitor instance."""
    return sentry_monitor


def register_module_for_monitoring(module_name: str):
    """Register module for Sentry monitoring."""
    sentry_monitor.register_module(module_name)


def monitor_outbound_request(agent_id: str, agent_type: AgentType,
                           url: str, method: str, headers: Dict[str, str] = None,
                           data: Any = None, response_status: int = None,
                           response_time: float = None) -> bool:
    """Monitor outbound HTTP request."""
    return sentry_monitor.monitor_outbound_request(
        agent_id, agent_type, url, method, headers, data, response_status, response_time
    )


def monitor_agent_interaction(agent_id: str, agent_type: AgentType,
                            interaction_type: str, target: str, 
                            details: Dict[str, Any] = None) -> bool:
    """Monitor agent interaction."""
    return sentry_monitor.monitor_agent_interaction(
        agent_id, agent_type, interaction_type, target, details
    )


def monitor_browser_preview(agent_id: str, agent_type: AgentType,
                          url: str, content_size: int, 
                          security_violations: List[str] = None) -> bool:
    """Monitor browser preview action."""
    return sentry_monitor.monitor_browser_preview(
        agent_id, agent_type, url, content_size, security_violations
    )


def monitor_webhook_config(agent_id: str, agent_type: AgentType,
                         endpoint_url: str, method: str, 
                         has_auth_headers: bool) -> bool:
    """Monitor webhook configuration."""
    return sentry_monitor.monitor_webhook_config(
        agent_id, agent_type, endpoint_url, method, has_auth_headers
    )


def monitor_credential_access(agent_id: str, agent_type: AgentType,
                            domain: str, credential_type: str, 
                            access_method: str) -> bool:
    """Monitor credential access."""
    return sentry_monitor.monitor_credential_access(
        agent_id, agent_type, domain, credential_type, access_method
    ) 