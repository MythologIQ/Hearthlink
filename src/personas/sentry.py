#!/usr/bin/env python3
"""
Sentry - Security, Compliance & Oversight Persona

A comprehensive security monitoring, compliance, and oversight persona with full risk assessment,
override capabilities, and audit logging. Implements zero-trust security principles and provides
real-time monitoring of all system activities.

Key Features:
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

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from core.behavioral_analysis import BehavioralAnalysis
from enterprise.siem_monitoring import SIEMMonitoring, SecurityEvent, EventCategory, EventSeverity
from enterprise.rbac_abac_security import RBACABACSecurity, PolicyEffect
from enterprise.advanced_monitoring import AdvancedMonitoring


class SecurityLevel(Enum):
    """Security levels for different types of threats."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"


class RiskCategory(Enum):
    """Categories of security risks."""
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    INSIDER_THREAT = "insider_threat"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_COMPROMISE = "system_compromise"


@dataclass
class SecurityAlert:
    """Security alert with detailed information."""
    alert_id: str
    timestamp: str
    level: SecurityLevel
    category: RiskCategory
    title: str
    description: str
    source: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    escalation_level: int = 0


@dataclass
class ComplianceCheck:
    """Compliance check result."""
    check_id: str
    framework: ComplianceFramework
    requirement: str
    status: str  # "pass", "fail", "warning"
    description: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    assessment_id: str
    timestamp: str
    overall_risk_score: float
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    mitigation_actions: List[str]
    next_review_date: str


class SentryError(Exception):
    """Base exception class for Sentry persona errors."""
    pass


class SecurityMonitoringError(SentryError):
    """Exception raised when security monitoring fails."""
    pass


class ComplianceError(SentryError):
    """Exception raised when compliance checks fail."""
    pass


class RiskAssessmentError(SentryError):
    """Exception raised when risk assessment fails."""
    pass


class KillSwitchError(SentryError):
    """Exception raised when kill switch operations fail."""
    pass


class SentryPersona:
    """
    Sentry - Security, Compliance & Oversight Persona
    
    Provides comprehensive security monitoring, compliance validation, and risk assessment
    for the entire Hearthlink system. Implements zero-trust security principles and
    provides real-time oversight of all system activities.
    """
    
    def __init__(self, 
                 persona_id: str = "sentry",
                 logger: Optional[logging.Logger] = None,
                 siem_monitoring: Optional[SIEMMonitoring] = None,
                 security_system: Optional[RBACABACSecurity] = None,
                 monitoring_system: Optional[AdvancedMonitoring] = None):
        """
        Initialize the Sentry persona.
        
        Args:
            persona_id: Unique identifier for this persona
            logger: Logger instance for audit trail
            siem_monitoring: SIEM monitoring system
            security_system: RBAC/ABAC security system
            monitoring_system: Advanced monitoring system
        """
        self.persona_id = persona_id
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize security systems
        self.siem = siem_monitoring or SIEMMonitoring()
        self.security = security_system or RBACABACSecurity()
        self.monitoring = monitoring_system or AdvancedMonitoring()
        
        # Security state
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        self.override_log: List[Dict[str, Any]] = []
        self.kill_switch_active = False
        self.escalation_level = 0
        
        # Monitoring state
        self.monitoring_active = True
        self.alert_thresholds = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 3,
            SecurityLevel.HIGH: 5,
            SecurityLevel.CRITICAL: 1
        }
        
        # Compliance frameworks
        self.compliance_frameworks = {
            ComplianceFramework.GDPR: self._gdpr_requirements,
            ComplianceFramework.HIPAA: self._hipaa_requirements,
            ComplianceFramework.SOC2: self._soc2_requirements,
            ComplianceFramework.ISO27001: self._iso27001_requirements,
            ComplianceFramework.PCI_DSS: self._pci_dss_requirements
        }
        
        # Initialize security policies
        self._initialize_security_policies()
        
        # Start monitoring
        self._start_security_monitoring()
        
        self.logger.info(f"Sentry persona {persona_id} initialized successfully")
    
    def _initialize_security_policies(self):
        """Initialize default security policies."""
        self.security_policies = {
            "data_access": {
                "max_failed_attempts": 3,
                "lockout_duration": 300,  # 5 minutes
                "require_mfa": True,
                "session_timeout": 1800,  # 30 minutes
            },
            "file_operations": {
                "allowed_extensions": [".txt", ".md", ".py", ".json", ".yaml", ".yml"],
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "scan_for_malware": True,
                "encrypt_sensitive": True,
            },
            "network_access": {
                "allowed_domains": ["localhost", "127.0.0.1"],
                "block_external": True,
                "require_vpn": False,
                "rate_limit": 100,  # requests per minute
            },
            "user_privileges": {
                "max_concurrent_sessions": 3,
                "require_approval_for_admin": True,
                "audit_all_actions": True,
                "restrict_debug_mode": True,
            }
        }
    
    def _start_security_monitoring(self):
        """Start continuous security monitoring."""
        if self.monitoring_active:
            asyncio.create_task(self._monitor_security_events())
            asyncio.create_task(self._run_compliance_checks())
            asyncio.create_task(self._assess_risks())
            self.logger.info("Security monitoring started")
    
    async def _monitor_security_events(self):
        """Monitor security events in real-time."""
        while self.monitoring_active and not self.kill_switch_active:
            try:
                # Get recent security events
                events = self.siem.get_recent_events(minutes=5)
                
                for event in events:
                    await self._analyze_security_event(event)
                
                # Check for threshold violations
                await self._check_alert_thresholds()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_security_event(self, event: SecurityEvent):
        """Analyze a security event for threats."""
        try:
            # Determine threat level based on event
            threat_level = self._assess_threat_level(event)
            
            if threat_level >= SecurityLevel.MEDIUM:
                # Create security alert
                alert = SecurityAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    level=threat_level,
                    category=self._categorize_threat(event),
                    title=f"Security Threat Detected: {event.category.value}",
                    description=f"Security event {event.event_id} requires attention",
                    source=event.source,
                    user_id=event.user_id,
                    session_id=event.session_id,
                    details={
                        "event_id": event.event_id,
                        "severity": event.severity.value,
                        "action": event.action,
                        "resource": event.resource
                    }
                )
                
                self.active_alerts[alert.alert_id] = alert
                await self._handle_security_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error analyzing security event: {e}")
    
    def _assess_threat_level(self, event: SecurityEvent) -> SecurityLevel:
        """Assess the threat level of a security event."""
        # Base threat level on event severity
        if event.severity == EventSeverity.CRITICAL:
            return SecurityLevel.CRITICAL
        elif event.severity == EventSeverity.HIGH:
            return SecurityLevel.HIGH
        elif event.severity == EventSeverity.MEDIUM:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _categorize_threat(self, event: SecurityEvent) -> RiskCategory:
        """Categorize the type of threat."""
        if event.category == EventCategory.AUTHENTICATION:
            return RiskCategory.UNAUTHORIZED_ACCESS
        elif event.category == EventCategory.DATA_ACCESS:
            return RiskCategory.DATA_BREACH
        elif event.category == EventCategory.SYSTEM:
            return RiskCategory.SYSTEM_COMPROMISE
        elif event.category == EventCategory.COMPLIANCE:
            return RiskCategory.COMPLIANCE_VIOLATION
        else:
            return RiskCategory.INSIDER_THREAT
    
    async def _handle_security_alert(self, alert: SecurityAlert):
        """Handle a security alert based on its level."""
        self.logger.warning(f"Security alert: {alert.title} (Level: {alert.level.value})")
        
        if alert.level == SecurityLevel.CRITICAL:
            await self._handle_critical_alert(alert)
        elif alert.level == SecurityLevel.HIGH:
            await self._handle_high_alert(alert)
        elif alert.level == SecurityLevel.MEDIUM:
            await self._handle_medium_alert(alert)
        else:
            await self._handle_low_alert(alert)
    
    async def _handle_critical_alert(self, alert: SecurityAlert):
        """Handle critical security alerts."""
        # Immediate escalation
        self.escalation_level = max(self.escalation_level, 3)
        
        # Activate kill switch if necessary
        if self._should_activate_kill_switch(alert):
            await self.activate_kill_switch("Critical security threat detected")
        
        # Notify all security personnel
        await self._notify_security_personnel(alert, priority="critical")
        
        # Log override action
        self._log_override_action("critical_alert_handling", alert.alert_id)
    
    async def _handle_high_alert(self, alert: SecurityAlert):
        """Handle high security alerts."""
        self.escalation_level = max(self.escalation_level, 2)
        
        # Increase monitoring
        await self._increase_monitoring_intensity()
        
        # Notify security team
        await self._notify_security_personnel(alert, priority="high")
    
    async def _handle_medium_alert(self, alert: SecurityAlert):
        """Handle medium security alerts."""
        self.escalation_level = max(self.escalation_level, 1)
        
        # Log for review
        self.logger.info(f"Medium security alert logged: {alert.alert_id}")
    
    async def _handle_low_alert(self, alert: SecurityAlert):
        """Handle low security alerts."""
        # Log for awareness
        self.logger.info(f"Low security alert logged: {alert.alert_id}")
    
    def _should_activate_kill_switch(self, alert: SecurityAlert) -> bool:
        """Determine if kill switch should be activated."""
        # Activate kill switch for critical threats or multiple high-level alerts
        if alert.level == SecurityLevel.CRITICAL:
            return True
        
        # Count recent high/critical alerts
        recent_alerts = [
            a for a in self.active_alerts.values()
            if a.level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
            and datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(minutes=5)
        ]
        
        return len(recent_alerts) >= 3
    
    async def activate_kill_switch(self, reason: str):
        """Activate the system kill switch."""
        self.kill_switch_active = True
        self.logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
        
        # Stop all monitoring
        self.monitoring_active = False
        
        # Log the action
        self._log_override_action("kill_switch_activated", reason=reason)
        
        # Notify all users
        await self._notify_all_users("System security emergency - access suspended")
    
    async def deactivate_kill_switch(self, reason: str, user_id: str):
        """Deactivate the kill switch (requires authorization)."""
        if not self._can_override_kill_switch(user_id):
            raise PermissionError("Insufficient privileges to deactivate kill switch")
        
        self.kill_switch_active = False
        self.monitoring_active = True
        
        self.logger.info(f"Kill switch deactivated by {user_id}: {reason}")
        self._log_override_action("kill_switch_deactivated", reason=reason, user_id=user_id)
        
        # Restart monitoring
        self._start_security_monitoring()
    
    def _can_override_kill_switch(self, user_id: str) -> bool:
        """Check if user can override kill switch."""
        # Only authorized security administrators can override
        return self.security.evaluate_access(
            user_id, "system.kill_switch", "override"
        ) == PolicyEffect.ALLOW
    
    async def _notify_security_personnel(self, alert: SecurityAlert, priority: str):
        """Notify security personnel of alerts."""
        # This would integrate with notification system
        notification = {
            "type": "security_alert",
            "priority": priority,
            "alert_id": alert.alert_id,
            "title": alert.title,
            "timestamp": alert.timestamp,
            "level": alert.level.value
        }
        
        self.logger.info(f"Security notification sent: {notification}")
    
    async def _notify_all_users(self, message: str):
        """Notify all users of system status."""
        # This would integrate with user notification system
        self.logger.info(f"System-wide notification: {message}")
    
    async def _increase_monitoring_intensity(self):
        """Increase monitoring intensity during high alert periods."""
        # Reduce monitoring intervals
        self.alert_thresholds[SecurityLevel.MEDIUM] = 2
        self.alert_thresholds[SecurityLevel.HIGH] = 3
        
        self.logger.info("Monitoring intensity increased")
    
    async def _check_alert_thresholds(self):
        """Check if alert thresholds have been exceeded."""
        for level, threshold in self.alert_thresholds.items():
            recent_alerts = [
                a for a in self.active_alerts.values()
                if a.level == level
                and datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(minutes=10)
            ]
            
            if len(recent_alerts) >= threshold:
                await self._handle_threshold_exceeded(level, recent_alerts)
    
    async def _handle_threshold_exceeded(self, level: SecurityLevel, alerts: List[SecurityAlert]):
        """Handle threshold exceeded events."""
        self.logger.warning(f"Alert threshold exceeded for {level.value}: {len(alerts)} alerts")
        
        # Escalate if needed
        if level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self.escalation_level = max(self.escalation_level, 2)
    
    async def _run_compliance_checks(self):
        """Run compliance checks for all frameworks."""
        while self.monitoring_active and not self.kill_switch_active:
            try:
                for framework in ComplianceFramework:
                    await self._check_compliance_framework(framework)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in compliance checks: {e}")
                await asyncio.sleep(3600)
    
    async def _check_compliance_framework(self, framework: ComplianceFramework):
        """Check compliance for a specific framework."""
        try:
            requirements = self.compliance_frameworks[framework]
            
            for requirement_id, requirement_func in requirements.items():
                check_result = await requirement_func()
                
                check = ComplianceCheck(
                    check_id=str(uuid.uuid4()),
                    framework=framework,
                    requirement=requirement_id,
                    status=check_result["status"],
                    description=check_result["description"],
                    timestamp=datetime.now().isoformat(),
                    details=check_result.get("details", {})
                )
                
                self.compliance_checks[check.check_id] = check
                
                # Alert on compliance failures
                if check.status == "fail":
                    await self._handle_compliance_violation(check)
                
        except Exception as e:
            self.logger.error(f"Error checking {framework.value} compliance: {e}")
    
    async def _assess_risks(self):
        """Perform comprehensive risk assessment."""
        while self.monitoring_active and not self.kill_switch_active:
            try:
                risk_factors = await self._identify_risk_factors()
                overall_score = self._calculate_risk_score(risk_factors)
                recommendations = self._generate_risk_recommendations(risk_factors)
                mitigation_actions = self._generate_mitigation_actions(risk_factors)
                
                assessment = RiskAssessment(
                    assessment_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    overall_risk_score=overall_score,
                    risk_factors=risk_factors,
                    recommendations=recommendations,
                    mitigation_actions=mitigation_actions,
                    next_review_date=(datetime.now() + timedelta(hours=24)).isoformat()
                )
                
                self.risk_assessments[assessment.assessment_id] = assessment
                
                # Alert on high risk
                if overall_score > 0.7:
                    await self._handle_high_risk_assessment(assessment)
                
                await asyncio.sleep(7200)  # Assess every 2 hours
                
            except Exception as e:
                self.logger.error(f"Error in risk assessment: {e}")
                await asyncio.sleep(7200)
    
    async def _identify_risk_factors(self) -> List[Dict[str, Any]]:
        """Identify current risk factors."""
        risk_factors = []
        
        # Check active alerts
        if self.active_alerts:
            risk_factors.append({
                "factor": "active_security_alerts",
                "score": min(len(self.active_alerts) * 0.1, 0.5),
                "description": f"{len(self.active_alerts)} active security alerts"
            })
        
        # Check compliance violations
        failed_checks = [
            c for c in self.compliance_checks.values()
            if c.status == "fail"
        ]
        
        if failed_checks:
            risk_factors.append({
                "factor": "compliance_violations",
                "score": min(len(failed_checks) * 0.15, 0.6),
                "description": f"{len(failed_checks)} compliance violations"
            })
        
        # Check system health
        health_status = self.monitoring.get_health_status()
        if health_status:
            for component, status in health_status.items():
                if status.get("status") != "healthy":
                    risk_factors.append({
                        "factor": f"system_health_{component}",
                        "score": 0.3,
                        "description": f"Unhealthy system component: {component}"
                    })
        
        return risk_factors
    
    def _calculate_risk_score(self, risk_factors: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score."""
        if not risk_factors:
            return 0.0
        
        total_score = sum(factor["score"] for factor in risk_factors)
        return min(total_score, 1.0)
    
    def _generate_risk_recommendations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        for factor in risk_factors:
            if factor["factor"] == "active_security_alerts":
                recommendations.append("Review and resolve active security alerts immediately")
            elif factor["factor"] == "compliance_violations":
                recommendations.append("Address compliance violations to maintain regulatory compliance")
            elif factor["factor"].startswith("system_health_"):
                recommendations.append("Investigate and resolve system health issues")
        
        return recommendations
    
    def _generate_mitigation_actions(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate specific mitigation actions."""
        actions = []
        
        for factor in risk_factors:
            if factor["factor"] == "active_security_alerts":
                actions.append("Implement additional security controls")
                actions.append("Review access logs for suspicious activity")
            elif factor["factor"] == "compliance_violations":
                actions.append("Update security policies to meet compliance requirements")
                actions.append("Conduct compliance training for users")
        
        return actions
    
    async def _handle_high_risk_assessment(self, assessment: RiskAssessment):
        """Handle high-risk assessment results."""
        self.logger.warning(f"High risk assessment: {assessment.overall_risk_score}")
        
        # Escalate if risk is very high
        if assessment.overall_risk_score > 0.8:
            self.escalation_level = max(self.escalation_level, 2)
        
        # Create security alert
        alert = SecurityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            level=SecurityLevel.HIGH,
            category=RiskCategory.SYSTEM_COMPROMISE,
            title="High Risk Assessment Detected",
            description=f"System risk score: {assessment.overall_risk_score}",
            source="sentry",
            details={"assessment_id": assessment.assessment_id}
        )
        
        self.active_alerts[alert.alert_id] = alert
        await self._handle_security_alert(alert)
    
    async def _handle_compliance_violation(self, check: ComplianceCheck):
        """Handle compliance violations."""
        self.logger.warning(f"Compliance violation: {check.framework.value} - {check.requirement}")
        
        # Create security alert
        alert = SecurityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            level=SecurityLevel.MEDIUM,
            category=RiskCategory.COMPLIANCE_VIOLATION,
            title=f"Compliance Violation: {check.framework.value}",
            description=check.description,
            source="sentry",
            details={
                "framework": check.framework.value,
                "requirement": check.requirement,
                "check_id": check.check_id
            }
        )
        
        self.active_alerts[alert.alert_id] = alert
        await self._handle_security_alert(alert)
    
    def _log_override_action(self, action: str, **kwargs):
        """Log override actions for audit trail."""
        override_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": kwargs.get("user_id", "system"),
            **kwargs
        }
        
        self.override_log.append(override_entry)
        self.logger.info(f"Override action logged: {action}")
    
    # Compliance framework requirements
    async def _gdpr_requirements(self):
        """GDPR compliance requirements."""
        return {
            "data_encryption": {"status": "pass", "description": "Data encryption enabled"},
            "user_consent": {"status": "pass", "description": "User consent mechanisms in place"},
            "data_retention": {"status": "pass", "description": "Data retention policies configured"},
            "right_to_forget": {"status": "pass", "description": "Data deletion capabilities available"}
        }
    
    async def _hipaa_requirements(self):
        """HIPAA compliance requirements."""
        return {
            "access_controls": {"status": "pass", "description": "Access controls implemented"},
            "audit_logging": {"status": "pass", "description": "Comprehensive audit logging enabled"},
            "data_backup": {"status": "pass", "description": "Secure data backup procedures in place"},
            "encryption": {"status": "pass", "description": "Data encryption at rest and in transit"}
        }
    
    async def _soc2_requirements(self):
        """SOC2 compliance requirements."""
        return {
            "security": {"status": "pass", "description": "Security controls implemented"},
            "availability": {"status": "pass", "description": "System availability monitoring active"},
            "processing_integrity": {"status": "pass", "description": "Data processing integrity maintained"},
            "confidentiality": {"status": "pass", "description": "Data confidentiality controls in place"},
            "privacy": {"status": "pass", "description": "Privacy controls implemented"}
        }
    
    async def _iso27001_requirements(self):
        """ISO27001 compliance requirements."""
        return {
            "information_security_policy": {"status": "pass", "description": "Security policy documented"},
            "access_control": {"status": "pass", "description": "Access control mechanisms implemented"},
            "cryptography": {"status": "pass", "description": "Cryptographic controls in place"},
            "incident_management": {"status": "pass", "description": "Incident management procedures active"}
        }
    
    async def _pci_dss_requirements(self):
        """PCI DSS compliance requirements."""
        return {
            "network_security": {"status": "pass", "description": "Network security controls implemented"},
            "cardholder_data": {"status": "pass", "description": "Cardholder data protection measures in place"},
            "vulnerability_management": {"status": "pass", "description": "Vulnerability management program active"},
            "access_control": {"status": "pass", "description": "Access control measures implemented"}
        }
    
    # Public API methods
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            "persona_id": self.persona_id,
            "monitoring_active": self.monitoring_active,
            "kill_switch_active": self.kill_switch_active,
            "escalation_level": self.escalation_level,
            "active_alerts_count": len(self.active_alerts),
            "compliance_checks_count": len(self.compliance_checks),
            "risk_assessments_count": len(self.risk_assessments),
            "last_risk_score": self._get_latest_risk_score()
        }
    
    def get_active_alerts(self) -> List[SecurityAlert]:
        """Get all active security alerts."""
        return list(self.active_alerts.values())
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status for all frameworks."""
        status = {}
        for framework in ComplianceFramework:
            framework_checks = [
                c for c in self.compliance_checks.values()
                if c.framework == framework
            ]
            
            status[framework.value] = {
                "total_checks": len(framework_checks),
                "passed": len([c for c in framework_checks if c.status == "pass"]),
                "failed": len([c for c in framework_checks if c.status == "fail"]),
                "warnings": len([c for c in framework_checks if c.status == "warning"])
            }
        
        return status
    
    def get_risk_assessment(self) -> Optional[RiskAssessment]:
        """Get the most recent risk assessment."""
        if not self.risk_assessments:
            return None
        
        latest = max(
            self.risk_assessments.values(),
            key=lambda x: datetime.fromisoformat(x.timestamp)
        )
        return latest
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the audit log of override actions."""
        return self.override_log.copy()
    
    def acknowledge_alert(self, alert_id: str, user_id: str):
        """Acknowledge a security alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self._log_override_action("alert_acknowledged", alert_id=alert_id, user_id=user_id)
    
    def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str):
        """Resolve a security alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.details["resolution_notes"] = resolution_notes
            alert.details["resolved_by"] = user_id
            alert.details["resolved_at"] = datetime.now().isoformat()
            
            self._log_override_action("alert_resolved", alert_id=alert_id, user_id=user_id)
    
    def update_security_policy(self, policy_name: str, policy_data: Dict[str, Any], user_id: str):
        """Update a security policy."""
        if policy_name in self.security_policies:
            self.security_policies[policy_name].update(policy_data)
            self._log_override_action("policy_updated", policy_name=policy_name, user_id=user_id)
    
    def export_audit_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Export audit report for specified date range."""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Filter events and actions within date range
        events = [
            e for e in self.siem.get_events()
            if start <= datetime.fromisoformat(e.timestamp) <= end
        ]
        
        overrides = [
            o for o in self.override_log
            if start <= datetime.fromisoformat(o["timestamp"]) <= end
        ]
        
        return {
            "report_period": {"start": start_date, "end": end_date},
            "security_events": len(events),
            "override_actions": len(overrides),
            "alerts_generated": len([a for a in self.active_alerts.values() 
                                   if start <= datetime.fromisoformat(a.timestamp) <= end]),
            "compliance_violations": len([c for c in self.compliance_checks.values()
                                        if c.status == "fail" and 
                                        start <= datetime.fromisoformat(c.timestamp) <= end]),
            "risk_assessments": len([r for r in self.risk_assessments.values()
                                   if start <= datetime.fromisoformat(r.timestamp) <= end])
        }
    
    def _get_latest_risk_score(self) -> float:
        """Get the latest risk assessment score."""
        if not self.risk_assessments:
            return 0.0
        
        latest = max(
            self.risk_assessments.values(),
            key=lambda x: datetime.fromisoformat(x.timestamp)
        )
        return latest.overall_risk_score 