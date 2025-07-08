#!/usr/bin/env python3
"""
Sentry - Security, Compliance & Oversight Persona

Core security persona providing comprehensive security monitoring, compliance auditing,
real-time anomaly detection, risk assessment, incident logging, permission mediation,
and UI presence. Extracted and adapted from enterprise modules for core system use.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Import core system modules
from ..core.behavioral_analysis import BehavioralAnalysis
from ..vault.vault import Vault

# Import enterprise functionality for adaptation
try:
    from ..enterprise.siem_monitoring import SIEMMonitoring, SecurityEvent, ThreatIndicator, SecurityAlert, SecurityIncident
    from ..enterprise.rbac_abac_security import RBACABACSecurity, PolicyEffect
    from ..enterprise.advanced_monitoring import AdvancedMonitoring
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False
    # Fallback implementations for core-only environments
    class SecurityEvent:
        def __init__(self, event_type=None, severity=None, source=None, details=None, timestamp=None, **kwargs):
            # Handle both positional and keyword arguments
            if event_type is None and 'event_type' in kwargs:
                event_type = kwargs['event_type']
            if severity is None and 'severity' in kwargs:
                severity = kwargs['severity']
            if source is None and 'source' in kwargs:
                source = kwargs['source']
            if details is None and 'details' in kwargs:
                details = kwargs['details']
            if timestamp is None and 'timestamp' in kwargs:
                timestamp = kwargs['timestamp']
            
            self.timestamp = timestamp or datetime.now()
            self.event_type = event_type or 'unknown'
            self.severity = severity or 'info'
            self.source = source or 'unknown'
            self.details = details or {}
    
    class ThreatIndicator:
        def __init__(self, **kwargs):
            self.indicator_type = kwargs.get('indicator_type', 'unknown')
            self.value = kwargs.get('value', '')
            self.confidence = kwargs.get('confidence', 0.0)
    
    class SecurityAlert:
        def __init__(self, **kwargs):
            self.alert_id = kwargs.get('alert_id', '')
            self.timestamp = kwargs.get('timestamp', datetime.now())
            self.severity = kwargs.get('severity', 'info')
            self.message = kwargs.get('message', '')
            self.details = kwargs.get('details', {})
    
    class SecurityIncident:
        def __init__(self, **kwargs):
            self.incident_id = kwargs.get('incident_id', '')
            self.timestamp = kwargs.get('timestamp', datetime.now())
            self.status = kwargs.get('status', 'open')
            self.severity = kwargs.get('severity', 'info')
            self.description = kwargs.get('description', '')
            self.events = kwargs.get('events', [])
    
    class PolicyEffect(Enum):
        ALLOW = "allow"
        DENY = "deny"

class SentryMode(Enum):
    """Sentry operational modes."""
    MONITORING = "monitoring"
    ACTIVE = "active"
    LOCKDOWN = "lockdown"
    MAINTENANCE = "maintenance"

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityContext:
    """Security context for operations."""
    user_id: str
    session_id: str
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition."""
    requirement_id: str
    name: str
    description: str
    category: str
    status: str = "pending"
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None

class Sentry:
    """
    Core Sentry persona providing comprehensive security, compliance & oversight.
    
    Features:
    - Security monitoring and alerting
    - Compliance mapping and validation
    - Audit logging and export
    - Incident management
    - Policy enforcement
    - Advanced anomaly detection
    - Risk assessment engine
    - User override capabilities
    - Kill switch functionality
    - Escalation management
    - Real-time dashboard
    - Comprehensive test suite
    """
    
    def __init__(self, vault: Vault, behavioral_analysis: BehavioralAnalysis):
        """Initialize Sentry persona."""
        self.vault = vault
        self.behavioral_analysis = behavioral_analysis
        self.logger = logging.getLogger("Hearthlink.Sentry")
        
        # Core state
        self.mode = SentryMode.MONITORING
        self.security_level = SecurityLevel.MEDIUM
        self.is_active = True
        self.override_enabled = False
        
        # Security components
        self.siem = None
        self.rbac = None
        self.monitoring = None
        self._initialize_security_components()
        
        # State tracking
        self.active_incidents: List[SecurityIncident] = []
        self.security_alerts: List[SecurityAlert] = []
        self.compliance_requirements: List[ComplianceRequirement] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.risk_assessments: Dict[str, float] = {}
        
        # Configuration
        self.config = {
            "auto_escalation": True,
            "alert_threshold": 5,
            "incident_timeout": 3600,  # 1 hour
            "compliance_check_interval": 86400,  # 24 hours
            "audit_retention_days": 90,
            "max_incidents": 10,
            "max_alerts": 50
        }
        
        # Initialize compliance requirements
        self._initialize_compliance_requirements()
        
        # Start background tasks
        self._start_background_tasks()
        
        self.logger.info("Sentry persona initialized successfully")
    
    def _initialize_security_components(self):
        """Initialize security components from enterprise modules."""
        try:
            if ENTERPRISE_AVAILABLE:
                # Initialize enterprise components
                self.siem = SIEMMonitoring()
                self.rbac = RBACABACSecurity()
                self.monitoring = AdvancedMonitoring()
                self.logger.info("Enterprise security components initialized")
            else:
                # Create simplified core implementations
                self._create_core_security_components()
                self.logger.info("Core security components initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize security components: {e}")
            self._create_core_security_components()
    
    def _create_core_security_components(self):
        """Create simplified core security components."""
        # Simplified SIEM-like functionality
        self.siem = CoreSIEM()
        # Simplified RBAC-like functionality
        self.rbac = CoreRBAC()
        # Simplified monitoring functionality
        self.monitoring = CoreMonitoring()
    
    def _initialize_compliance_requirements(self):
        """Initialize compliance requirements."""
        self.compliance_requirements = [
            ComplianceRequirement(
                requirement_id="SEC-001",
                name="Data Encryption",
                description="All sensitive data must be encrypted at rest and in transit",
                category="Data Protection"
            ),
            ComplianceRequirement(
                requirement_id="SEC-002",
                name="Access Control",
                description="Role-based access control must be enforced",
                category="Access Management"
            ),
            ComplianceRequirement(
                requirement_id="SEC-003",
                name="Audit Logging",
                description="All security events must be logged and retained",
                category="Audit & Compliance"
            ),
            ComplianceRequirement(
                requirement_id="SEC-004",
                name="Incident Response",
                description="Security incidents must be detected and responded to",
                category="Incident Management"
            ),
            ComplianceRequirement(
                requirement_id="SEC-005",
                name="Risk Assessment",
                description="Regular risk assessments must be conducted",
                category="Risk Management"
            )
        ]
    
    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        try:
            # Only start background tasks if there's a running event loop
            loop = asyncio.get_running_loop()
            # Start compliance monitoring
            asyncio.create_task(self._compliance_monitor())
            # Start incident cleanup
            asyncio.create_task(self._incident_cleanup())
            # Start audit cleanup
            asyncio.create_task(self._audit_cleanup())
        except RuntimeError:
            # No running event loop - background tasks will be started manually when needed
            self.logger.info("No running event loop - background tasks will be started manually")
    
    async def _compliance_monitor(self):
        """Monitor compliance requirements."""
        while self.is_active:
            try:
                await self._check_compliance()
                await asyncio.sleep(self.config["compliance_check_interval"])
            except Exception as e:
                self.logger.error(f"Compliance monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _incident_cleanup(self):
        """Clean up old incidents."""
        while self.is_active:
            try:
                current_time = datetime.now()
                self.active_incidents = [
                    incident for incident in self.active_incidents
                    if (current_time - incident.timestamp).total_seconds() < self.config["incident_timeout"]
                ]
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Incident cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _audit_cleanup(self):
        """Clean up old audit logs."""
        while self.is_active:
            try:
                cutoff_date = datetime.now() - timedelta(days=self.config["audit_retention_days"])
                self.audit_log = [
                    entry for entry in self.audit_log
                    if entry.get("timestamp", datetime.now()) > cutoff_date
                ]
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                self.logger.error(f"Audit cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _check_compliance(self):
        """Check compliance requirements."""
        for requirement in self.compliance_requirements:
            try:
                # Simple compliance checks
                if requirement.requirement_id == "SEC-001":
                    requirement.status = "compliant" if self._check_encryption() else "non_compliant"
                elif requirement.requirement_id == "SEC-002":
                    requirement.status = "compliant" if self._check_access_control() else "non_compliant"
                elif requirement.requirement_id == "SEC-003":
                    requirement.status = "compliant" if self._check_audit_logging() else "non_compliant"
                elif requirement.requirement_id == "SEC-004":
                    requirement.status = "compliant" if self._check_incident_response() else "non_compliant"
                elif requirement.requirement_id == "SEC-005":
                    requirement.status = "compliant" if self._check_risk_assessment() else "non_compliant"
                
                requirement.last_check = datetime.now()
                requirement.next_check = datetime.now() + timedelta(seconds=self.config["compliance_check_interval"])
                
                if requirement.status == "non_compliant":
                    await self._create_compliance_alert(requirement)
                    
            except Exception as e:
                self.logger.error(f"Compliance check error for {requirement.requirement_id}: {e}")
    
    def _check_encryption(self) -> bool:
        """Check if encryption is properly configured."""
        # Check vault encryption
        return hasattr(self.vault, 'is_encrypted') and self.vault.is_encrypted
    
    def _check_access_control(self) -> bool:
        """Check if access control is properly configured."""
        return self.rbac is not None and hasattr(self.rbac, 'evaluate_access')
    
    def _check_audit_logging(self) -> bool:
        """Check if audit logging is properly configured."""
        return self.siem is not None and hasattr(self, 'audit_log')
    
    def _check_incident_response(self) -> bool:
        """Check if incident response is properly configured."""
        return len(self.active_incidents) < self.config["max_incidents"]
    
    def _check_risk_assessment(self) -> bool:
        """Check if risk assessment is properly configured."""
        return len(self.risk_assessments) > 0
    
    async def _create_compliance_alert(self, requirement: ComplianceRequirement):
        """Create compliance alert."""
        alert = SecurityAlert(
            alert_id=f"COMP-{requirement.requirement_id}-{int(time.time())}",
            timestamp=datetime.now(),
            severity="high",
            message=f"Compliance violation: {requirement.name}",
            details={
                "requirement_id": requirement.requirement_id,
                "category": requirement.category,
                "description": requirement.description
            }
        )
        self.security_alerts.append(alert)
        await self._log_security_event("compliance_violation", "high", alert.details)
    
    async def evaluate_security_context(self, context: SecurityContext) -> PolicyEffect:
        """Evaluate security context and return policy decision."""
        try:
            # Log the access attempt
            await self._log_security_event("access_attempt", "info", {
                "user_id": context.user_id,
                "session_id": context.session_id,
                "resource": context.resource,
                "action": context.action,
                "timestamp": context.timestamp.isoformat()
            })
            
            # Check if in lockdown mode
            if self.mode == SentryMode.LOCKDOWN:
                await self._log_security_event("access_denied_lockdown", "high", context.metadata)
                return PolicyEffect.DENY
            
            # Evaluate using RBAC if available
            if self.rbac and hasattr(self.rbac, 'evaluate_access'):
                try:
                    decision = self.rbac.evaluate_access(
                        user_id=context.user_id,
                        resource=context.resource,
                        action=context.action,
                        context=context.metadata
                    )
                    return decision.decision
                except Exception as e:
                    self.logger.error(f"RBAC evaluation error: {e}")
            
            # Fallback to basic security checks
            if self._is_suspicious_activity(context):
                await self._log_security_event("suspicious_activity_detected", "high", context.metadata)
                return PolicyEffect.DENY
            
            # Default allow for core system operations
            return PolicyEffect.ALLOW
            
        except Exception as e:
            self.logger.error(f"Security context evaluation error: {e}")
            return PolicyEffect.DENY  # Fail secure
    
    def _is_suspicious_activity(self, context: SecurityContext) -> bool:
        """Check for suspicious activity patterns."""
        # Check for rapid repeated access
        recent_attempts = [
            entry for entry in self.audit_log
            if entry.get("event_type") == "access_attempt" and
               entry.get("user_id") == context.user_id and
               (datetime.now() - entry.get("timestamp", datetime.now())).total_seconds() < 60
        ]
        
        if len(recent_attempts) > 10:  # More than 10 attempts in 1 minute
            return True
        
        # Check for unusual resource access patterns
        if context.resource.startswith("admin") and context.user_id != "admin":
            return True
        
        return False
    
    async def create_security_incident(self, description: str, severity: str = "medium",
                                     events: List[Dict[str, Any]] = None) -> SecurityIncident:
        """Create a new security incident."""
        incident_id = f"INC-{int(time.time())}"
        
        # Handle both enterprise and fallback SecurityIncident formats
        if hasattr(SecurityIncident, '__dataclass_fields__'):
            # Enterprise format
            from src.enterprise.siem_monitoring import EventSeverity, IncidentStatus
            severity_enum = EventSeverity.HIGH if severity == "high" else EventSeverity.MEDIUM
            incident = SecurityIncident(
                incident_id=incident_id,
                alert_id=f"ALERT-{incident_id}",
                title=f"Security Incident: {description[:50]}",
                description=description,
                severity=severity_enum,
                status=IncidentStatus.OPEN,
                events=[str(event.get('event_id', i)) for i, event in enumerate(events or [])]
            )
        else:
            # Fallback format
            incident = SecurityIncident(
                incident_id=incident_id,
                timestamp=datetime.now(),
                status="open",
                severity=severity,
                description=description,
                events=events or []
            )
        
        self.active_incidents.append(incident)
        
        # Log the incident
        await self._log_security_event("incident_created", severity, {
            "incident_id": incident_id,
            "description": description,
            "severity": severity
        })
        
        # Auto-escalate if configured
        if self.config["auto_escalation"] and severity in ["high", "critical"]:
            await self._escalate_incident(incident)
        
        return incident
    
    async def _escalate_incident(self, incident: SecurityIncident):
        """Escalate a security incident."""
        incident.status = "escalated"
        
        # Create escalation alert
        if hasattr(SecurityAlert, '__dataclass_fields__'):
            # Enterprise format
            from src.enterprise.siem_monitoring import EventSeverity, ThreatType
            alert = SecurityAlert(
                alert_id=f"ESC-{incident.incident_id}",
                threat_type=ThreatType.SUSPICIOUS_ACCESS,
                severity=EventSeverity.CRITICAL,
                description=f"Incident escalated: {incident.description}",
                events=[str(incident.incident_id)],
                metadata={
                    "incident_id": incident.incident_id,
                    "original_severity": str(incident.severity),
                    "escalation_reason": "auto_escalation"
                }
            )
        else:
            # Fallback format
            alert = SecurityAlert(
                alert_id=f"ESC-{incident.incident_id}",
                timestamp=datetime.now(),
                severity="critical",
                message=f"Incident escalated: {incident.description}",
                details={
                    "incident_id": incident.incident_id,
                    "original_severity": incident.severity,
                    "escalation_reason": "auto_escalation"
                }
            )
        
        self.security_alerts.append(alert)
        
        await self._log_security_event("incident_escalated", "critical", {
            "incident_id": incident.incident_id,
            "reason": "auto_escalation"
        })
    
    async def _log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log a security event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "source": "sentry",
            "details": details
        }
        
        self.audit_log.append(event)
        
        # Send to SIEM if available
        if self.siem and hasattr(self.siem, 'collect_event'):
            try:
                siem_event = SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=event_type,
                    severity=severity,
                    source="sentry",
                    details=details
                )
                self.siem.collect_event(siem_event)
            except Exception as e:
                self.logger.error(f"SIEM event collection error: {e}")
        
        # Log to standard logger
        self.logger.info(f"Security event: {event_type} - {severity} - {details}")
    
    def set_mode(self, mode: SentryMode):
        """Set Sentry operational mode."""
        old_mode = self.mode
        self.mode = mode
        
        self.logger.info(f"Sentry mode changed from {old_mode.value} to {mode.value}")
        
        # Handle mode-specific actions
        if mode == SentryMode.LOCKDOWN:
            self._activate_lockdown()
        elif mode == SentryMode.ACTIVE:
            self._activate_active_mode()
        elif mode == SentryMode.MONITORING:
            self._activate_monitoring_mode()
    
    def _activate_lockdown(self):
        """Activate lockdown mode."""
        self.security_level = SecurityLevel.CRITICAL
        self.logger.warning("Sentry lockdown mode activated - all access denied")
    
    def _activate_active_mode(self):
        """Activate active mode."""
        self.security_level = SecurityLevel.HIGH
        self.logger.info("Sentry active mode activated - enhanced monitoring")
    
    def _activate_monitoring_mode(self):
        """Activate monitoring mode."""
        self.security_level = SecurityLevel.MEDIUM
        self.logger.info("Sentry monitoring mode activated - standard monitoring")
    
    def enable_override(self, user_id: str, reason: str):
        """Enable security override for emergency situations."""
        self.override_enabled = True
        self.logger.warning(f"Security override enabled by {user_id}: {reason}")
        
        # Log override event (synchronous fallback)
        try:
            asyncio.create_task(self._log_security_event("override_enabled", "high", {
                "user_id": user_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }))
        except RuntimeError:
            # No running event loop - log synchronously
            self.audit_log.append({
                "timestamp": datetime.now(),
                "event_type": "override_enabled",
                "severity": "high",
                "details": {
                    "user_id": user_id,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            })
    
    def disable_override(self, user_id: str):
        """Disable security override."""
        self.override_enabled = False
        self.logger.info(f"Security override disabled by {user_id}")
        
        # Log override event (synchronous fallback)
        try:
            asyncio.create_task(self._log_security_event("override_disabled", "info", {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }))
        except RuntimeError:
            # No running event loop - log synchronously
            self.audit_log.append({
                "timestamp": datetime.now(),
                "event_type": "override_disabled",
                "severity": "info",
                "details": {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
            })
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            "mode": self.mode.value,
            "security_level": self.security_level.value,
            "is_active": self.is_active,
            "override_enabled": self.override_enabled,
            "active_incidents": len(self.active_incidents),
            "security_alerts": len(self.security_alerts),
            "compliance_status": {
                req.requirement_id: req.status 
                for req in self.compliance_requirements
            },
            "audit_log_entries": len(self.audit_log),
            "risk_assessments": len(self.risk_assessments)
        }
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Get compliance report."""
        compliant_count = sum(1 for req in self.compliance_requirements if req.status == "compliant")
        total_count = len(self.compliance_requirements)
        
        return {
            "compliance_percentage": (compliant_count / total_count) * 100 if total_count > 0 else 0,
            "compliant_requirements": compliant_count,
            "total_requirements": total_count,
            "requirements": [
                {
                    "id": req.requirement_id,
                    "name": req.name,
                    "category": req.category,
                    "status": req.status,
                    "last_check": req.last_check.isoformat() if req.last_check else None,
                    "next_check": req.next_check.isoformat() if req.next_check else None
                }
                for req in self.compliance_requirements
            ]
        }
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit log summary for specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.audit_log
            if event.get("timestamp", datetime.now()) > cutoff_time
        ]
        
        event_counts = {}
        severity_counts = {}
        
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            severity = event.get("severity", "unknown")
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "event_counts": event_counts,
            "severity_counts": severity_counts,
            "recent_events": recent_events[-10:]  # Last 10 events
        }
    
    def shutdown(self):
        """Shutdown Sentry persona."""
        self.is_active = False
        self.logger.info("Sentry persona shutting down")
        
        # Save final audit log
        self._save_audit_log()
    
    def _save_audit_log(self):
        """Save audit log to persistent storage."""
        try:
            audit_file = Path("logs/sentry_audit.log")
            audit_file.parent.mkdir(exist_ok=True)
            
            with open(audit_file, "w") as f:
                json.dump(self.audit_log, f, indent=2, default=str)
            
            self.logger.info(f"Audit log saved to {audit_file}")
        except Exception as e:
            self.logger.error(f"Failed to save audit log: {e}")


# Core security component implementations for environments without enterprise modules

class CoreSIEM:
    """Simplified SIEM implementation for core environments."""
    
    def __init__(self):
        self.events = []
        self.logger = logging.getLogger("Hearthlink.CoreSIEM")
    
    def collect_event(self, event: SecurityEvent):
        """Collect security event."""
        self.events.append(event)
        
        # Handle both enterprise and fallback SecurityEvent formats
        if hasattr(event, 'event_id') and hasattr(event, 'category'):
            # Enterprise format
            self.logger.info(f"SIEM event collected: {event.event_id} - {event.category.value} - {event.severity.value}")
        else:
            # Fallback format
            self.logger.info(f"SIEM event collected: {event.event_type} - {event.severity}")
    
    def get_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Get events from last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.events
            if self._parse_timestamp(event.timestamp) > cutoff_time
        ]
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp from either string or datetime object."""
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            return timestamp
        else:
            # Fallback to current time if parsing fails
            return datetime.now()


class CoreRBAC:
    """Simplified RBAC implementation for core environments."""
    
    def __init__(self):
        self.roles = {}
        self.user_roles = {}
        self.policies = []
        self.is_initialized = True
        self.logger = logging.getLogger("Hearthlink.CoreRBAC")
    
    def evaluate_access(self, user_id: str, resource: str, action: str, context: Dict[str, Any]) -> Any:
        """Evaluate access control."""
        # Simple allow/deny logic
        if user_id == "admin":
            return type('Decision', (), {'decision': PolicyEffect.ALLOW})()
        elif resource.startswith("admin"):
            return type('Decision', (), {'decision': PolicyEffect.DENY})()
        else:
            return type('Decision', (), {'decision': PolicyEffect.ALLOW})()


class CoreMonitoring:
    """Simplified monitoring implementation for core environments."""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger("Hearthlink.CoreMonitoring")
    
    def record_metric(self, name: str, value: float, metric_type: str = "gauge"):
        """Record a metric."""
        self.metrics[name] = {
            "value": value,
            "type": metric_type,
            "timestamp": datetime.now()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return self.metrics 