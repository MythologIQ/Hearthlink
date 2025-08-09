"""
Synapse Audit Logger

Comprehensive audit logging for all external interactions:
- Outbound requests and agent interactions
- Permission checks and security events
- Rate limiting and access control
- All logged to /logs/synapse-actions.json
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import secrets

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    OUTBOUND_REQUEST = "outbound_request"
    AGENT_INTERACTION = "agent_interaction"
    PERMISSION_CHECK = "permission_check"
    RATE_LIMIT = "rate_limit"
    SECURITY_VIOLATION = "security_violation"
    CREDENTIAL_ACCESS = "credential_access"
    WEBHOOK_CONFIG = "webhook_config"
    BROWSER_PREVIEW = "browser_preview"
    SYSTEM_ACCESS = "system_access"


class AuditLevel(Enum):
    """Audit levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event record."""
    event_id: str
    timestamp: str
    event_type: AuditEventType
    level: AuditLevel
    agent_id: str
    agent_type: str
    action: str
    target: str
    success: bool
    details: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    risk_score: int = 0
    signature: Optional[str] = None


class AuditLogger:
    """Comprehensive audit logger for Synapse."""
    
    def __init__(self, log_file: str = "logs/synapse-actions.json", 
                 max_file_size_mb: int = 100, backup_count: int = 5):
        self.log_file = Path(log_file)
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.backup_count = backup_count
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self._initialize_log_file()
        
        # Audit secret for signing events
        self.audit_secret = self._get_or_create_audit_secret()
        
        # Event counters
        self.event_counters = {
            event_type: 0 for event_type in AuditEventType
        }
        
        logger.info(f"Audit logger initialized: {self.log_file}")
    
    def _initialize_log_file(self):
        """Initialize the audit log file with header."""
        header = {
            "audit_log_header": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
                "description": "Synapse external interactions audit log",
                "format": "jsonl",
                "signature_algorithm": "hmac-sha256"
            }
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(header) + '\n')
    
    def _get_or_create_audit_secret(self) -> str:
        """Get or create audit secret for signing events."""
        secret_file = Path("config/audit_secret.key")
        
        if secret_file.exists():
            with open(secret_file, 'r') as f:
                return f.read().strip()
        else:
            # Create new secret
            secret = secrets.token_hex(32)
            secret_file.parent.mkdir(exist_ok=True)
            with open(secret_file, 'w') as f:
                f.write(secret)
            
            # Set restrictive permissions
            os.chmod(secret_file, 0o600)
            logger.info("Created new audit secret")
            return secret
    
    def _sign_event(self, event_data: Dict[str, Any]) -> str:
        """Sign audit event data."""
        # Create canonical representation
        canonical_data = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        
        # Create HMAC signature
        signature = hmac.new(
            self.audit_secret.encode('utf-8'),
            canonical_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _rotate_log_file(self):
        """Rotate log file if it exceeds size limit."""
        if not self.log_file.exists():
            return
        
        if self.log_file.stat().st_size > self.max_file_size:
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.log_file.with_suffix(f".{timestamp}.json")
            
            # Move current file to backup
            self.log_file.rename(backup_file)
            
            # Reinitialize log file
            self._initialize_log_file()
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            logger.info(f"Rotated audit log: {backup_file}")
    
    def _cleanup_old_backups(self):
        """Clean up old backup files."""
        log_dir = self.log_file.parent
        pattern = f"{self.log_file.stem}.*.json"
        
        backup_files = sorted(
            log_dir.glob(pattern),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Keep only the most recent backup_count files
        for backup_file in backup_files[self.backup_count:]:
            backup_file.unlink()
            logger.info(f"Removed old backup: {backup_file}")
    
    def log_event(self, event_type: AuditEventType, level: AuditLevel, 
                 agent_id: str, agent_type: str, action: str, target: str,
                 success: bool, details: Dict[str, Any], 
                 session_id: Optional[str] = None, user_id: Optional[str] = None,
                 ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                 risk_score: int = 0) -> str:
        """Log an audit event."""
        try:
            # Generate event ID
            event_id = f"audit_{int(datetime.now().timestamp())}_{secrets.token_hex(4)}"
            
            # Create event
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                level=level,
                agent_id=agent_id,
                agent_type=agent_type,
                action=action,
                target=target,
                success=success,
                details=details,
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                risk_score=risk_score
            )
            
            # Convert to dict and sign
            event_dict = asdict(event)
            event_dict['event_type'] = event_type.value
            event_dict['level'] = level.value
            
            # Remove signature field for signing
            event_dict.pop('signature', None)
            
            # Sign the event
            signature = self._sign_event(event_dict)
            event_dict['signature'] = signature
            
            # Write to log file
            self._write_event_to_log(event_dict)
            
            # Update counters
            self.event_counters[event_type] += 1
            
            # Rotate if needed
            self._rotate_log_file()
            
            logger.debug(f"Audit event logged: {event_id} - {action}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return ""
    
    def _write_event_to_log(self, event_dict: Dict[str, Any]):
        """Write event to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit event to log: {e}")
    
    def log_outbound_request(self, agent_id: str, agent_type: str, url: str, 
                           method: str, success: bool, response_status: Optional[int] = None,
                           response_time: Optional[float] = None, headers: Optional[Dict] = None,
                           data_size: Optional[int] = None, error: Optional[str] = None,
                           session_id: Optional[str] = None) -> str:
        """Log outbound HTTP request."""
        details = {
            "url": url,
            "method": method,
            "response_status": response_status,
            "response_time": response_time,
            "data_size": data_size,
            "error": error
        }
        
        # Add safe headers (exclude sensitive ones)
        if headers:
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ['authorization', 'cookie', 'x-api-key']}
            details["headers"] = safe_headers
        
        level = AuditLevel.ERROR if not success else AuditLevel.INFO
        if response_status and response_status >= 400:
            level = AuditLevel.WARNING
        
        return self.log_event(
            AuditEventType.OUTBOUND_REQUEST,
            level,
            agent_id,
            agent_type,
            f"outbound_request_{method.lower()}",
            url,
            success,
            details,
            session_id=session_id
        )
    
    def log_agent_interaction(self, agent_id: str, agent_type: str, 
                            interaction_type: str, target: str, success: bool,
                            details: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """Log agent interaction."""
        level = AuditLevel.ERROR if not success else AuditLevel.INFO
        
        # Determine event type based on interaction
        if "credential" in interaction_type.lower():
            event_type = AuditEventType.CREDENTIAL_ACCESS
            level = AuditLevel.WARNING if success else AuditLevel.ERROR
        elif "system" in interaction_type.lower():
            event_type = AuditEventType.SYSTEM_ACCESS
            level = AuditLevel.WARNING
        else:
            event_type = AuditEventType.AGENT_INTERACTION
        
        return self.log_event(
            event_type,
            level,
            agent_id,
            agent_type,
            f"agent_interaction_{interaction_type}",
            target,
            success,
            details,
            session_id=session_id
        )
    
    def log_permission_check(self, agent_id: str, agent_type: str, 
                           permission_type: str, action: str, target: str,
                           granted: bool, reason: Optional[str] = None,
                           session_id: Optional[str] = None) -> str:
        """Log permission check."""
        details = {
            "permission_type": permission_type,
            "reason": reason
        }
        
        level = AuditLevel.WARNING if not granted else AuditLevel.INFO
        
        return self.log_event(
            AuditEventType.PERMISSION_CHECK,
            level,
            agent_id,
            agent_type,
            f"permission_check_{permission_type}",
            target,
            granted,
            details,
            session_id=session_id
        )
    
    def log_rate_limit(self, agent_id: str, agent_type: str, 
                      permission_type: str, action: str, target: str,
                      rate_limit_exceeded: bool, current_count: int, limit: int,
                      session_id: Optional[str] = None) -> str:
        """Log rate limit event."""
        details = {
            "permission_type": permission_type,
            "current_count": current_count,
            "limit": limit,
            "rate_limit_exceeded": rate_limit_exceeded
        }
        
        level = AuditLevel.WARNING if rate_limit_exceeded else AuditLevel.INFO
        
        return self.log_event(
            AuditEventType.RATE_LIMIT,
            level,
            agent_id,
            agent_type,
            f"rate_limit_{permission_type}",
            target,
            not rate_limit_exceeded,
            details,
            session_id=session_id
        )
    
    def log_security_violation(self, agent_id: str, agent_type: str,
                             violation_type: str, target: str, details: Dict[str, Any],
                             session_id: Optional[str] = None) -> str:
        """Log security violation."""
        return self.log_event(
            AuditEventType.SECURITY_VIOLATION,
            AuditLevel.ERROR,
            agent_id,
            agent_type,
            f"security_violation_{violation_type}",
            target,
            False,
            details,
            session_id=session_id,
            risk_score=100
        )
    
    def log_browser_preview(self, agent_id: str, agent_type: str, url: str,
                          content_size: int, security_violations: List[str],
                          session_id: Optional[str] = None) -> str:
        """Log browser preview action."""
        details = {
            "url": url,
            "content_size": content_size,
            "security_violations": security_violations
        }
        
        level = AuditLevel.WARNING if security_violations else AuditLevel.INFO
        
        return self.log_event(
            AuditEventType.BROWSER_PREVIEW,
            level,
            agent_id,
            agent_type,
            "browser_preview",
            url,
            len(security_violations) == 0,
            details,
            session_id=session_id
        )
    
    def log_webhook_config(self, agent_id: str, agent_type: str, endpoint_url: str,
                          method: str, has_auth: bool, success: bool,
                          session_id: Optional[str] = None) -> str:
        """Log webhook configuration change."""
        details = {
            "endpoint_url": endpoint_url,
            "method": method,
            "has_auth_headers": has_auth
        }
        
        return self.log_event(
            AuditEventType.WEBHOOK_CONFIG,
            AuditLevel.INFO,
            agent_id,
            agent_type,
            "webhook_config",
            endpoint_url,
            success,
            details,
            session_id=session_id
        )
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for specified time period."""
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            events = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('{"audit_log_header"'):
                        try:
                            event = json.loads(line)
                            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')).timestamp()
                            if event_time >= cutoff_time:
                                events.append(event)
                        except (json.JSONDecodeError, KeyError):
                            continue
            
            # Calculate statistics
            total_events = len(events)
            successful_events = len([e for e in events if e.get('success', False)])
            failed_events = total_events - successful_events
            
            # Event type breakdown
            event_types = {}
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Level breakdown
            levels = {}
            for event in events:
                level = event.get('level', 'unknown')
                levels[level] = levels.get(level, 0) + 1
            
            # Agent activity
            agent_activity = {}
            for event in events:
                agent = event.get('agent_id', 'unknown')
                agent_activity[agent] = agent_activity.get(agent, 0) + 1
            
            return {
                "summary": {
                    "total_events": total_events,
                    "successful_events": successful_events,
                    "failed_events": failed_events,
                    "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0,
                    "time_period_hours": hours
                },
                "event_types": event_types,
                "levels": levels,
                "agent_activity": agent_activity,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return {"error": str(e)}
    
    def verify_log_integrity(self) -> Dict[str, Any]:
        """Verify log file integrity by checking signatures."""
        try:
            total_events = 0
            valid_signatures = 0
            invalid_signatures = 0
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip() and not line.startswith('{"audit_log_header"'):
                        try:
                            event = json.loads(line)
                            total_events += 1
                            
                            # Get signature
                            signature = event.pop('signature', None)
                            if not signature:
                                invalid_signatures += 1
                                continue
                            
                            # Verify signature
                            expected_signature = self._sign_event(event)
                            if signature == expected_signature:
                                valid_signatures += 1
                            else:
                                invalid_signatures += 1
                                
                        except (json.JSONDecodeError, KeyError):
                            invalid_signatures += 1
            
            return {
                "total_events": total_events,
                "valid_signatures": valid_signatures,
                "invalid_signatures": invalid_signatures,
                "integrity_percentage": (valid_signatures / total_events * 100) if total_events > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to verify log integrity: {e}")
            return {"error": str(e)}


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    return audit_logger


def log_outbound_request(agent_id: str, agent_type: str, url: str, method: str,
                        success: bool, response_status: Optional[int] = None,
                        response_time: Optional[float] = None, headers: Optional[Dict] = None,
                        data_size: Optional[int] = None, error: Optional[str] = None,
                        session_id: Optional[str] = None) -> str:
    """Log outbound HTTP request."""
    return audit_logger.log_outbound_request(
        agent_id, agent_type, url, method, success, response_status,
        response_time, headers, data_size, error, session_id
    )


def log_agent_interaction(agent_id: str, agent_type: str, interaction_type: str,
                         target: str, success: bool, details: Dict[str, Any],
                         session_id: Optional[str] = None) -> str:
    """Log agent interaction."""
    return audit_logger.log_agent_interaction(
        agent_id, agent_type, interaction_type, target, success, details, session_id
    )


def log_permission_check(agent_id: str, agent_type: str, permission_type: str,
                        action: str, target: str, granted: bool, reason: Optional[str] = None,
                        session_id: Optional[str] = None) -> str:
    """Log permission check."""
    return audit_logger.log_permission_check(
        agent_id, agent_type, permission_type, action, target, granted, reason, session_id
    )


def log_security_violation(agent_id: str, agent_type: str, violation_type: str,
                          target: str, details: Dict[str, Any],
                          session_id: Optional[str] = None) -> str:
    """Log security violation."""
    return audit_logger.log_security_violation(
        agent_id, agent_type, violation_type, target, details, session_id
    ) 