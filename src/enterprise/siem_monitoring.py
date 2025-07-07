#!/usr/bin/env python3
"""
SIEM Monitoring Module - Enterprise Feature

Minimum viable implementation of Security Information and Event Management (SIEM)
for enterprise environments. Provides security event monitoring, threat detection,
and incident response capabilities.

Features:
- Security event collection and correlation
- Threat detection and alerting
- Incident response automation
- Security metrics and reporting
- Integration with RBAC/ABAC security

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
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class SIEMError(HearthlinkError):
    """Base exception for SIEM-related errors."""
    pass


class EventCollectionError(SIEMError):
    """Exception raised when event collection fails."""
    pass


class ThreatDetectionError(SIEMError):
    """Exception raised when threat detection fails."""
    pass


class IncidentResponseError(SIEMError):
    """Exception raised when incident response fails."""
    pass


class EventSeverity(Enum):
    """Security event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(Enum):
    """Security event categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_ACCESS = "system_access"
    NETWORK_ACCESS = "network_access"
    MALWARE = "malware"
    COMPLIANCE = "compliance"
    AUDIT = "audit"


class ThreatType(Enum):
    """Types of security threats."""
    BRUTE_FORCE = "brute_force"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_ACTIVITY = "malware_activity"
    SUSPICIOUS_ACCESS = "suspicious_access"
    COMPLIANCE_VIOLATION = "compliance_violation"


class IncidentStatus(Enum):
    """Incident status values."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class SecurityEvent:
    """Security event data."""
    event_id: str
    timestamp: str
    source: str
    category: EventCategory
    severity: EventSeverity
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatIndicator:
    """Threat indicator for detection."""
    indicator_id: str
    threat_type: ThreatType
    pattern: str
    description: str
    severity: EventSeverity
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SecurityAlert:
    """Security alert generated from threat detection."""
    alert_id: str
    threat_type: ThreatType
    severity: EventSeverity
    description: str
    events: List[str] = field(default_factory=list)  # Event IDs
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "new"
    assigned_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityIncident:
    """Security incident for response management."""
    incident_id: str
    alert_id: str
    title: str
    description: str
    severity: EventSeverity
    status: IncidentStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_to: Optional[str] = None
    events: List[str] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityMetrics:
    """Security metrics for reporting."""
    period_start: str
    period_end: str
    total_events: int
    alerts_generated: int
    incidents_created: int
    threat_detection_rate: float
    mean_time_to_detect: float
    mean_time_to_resolve: float
    events_by_severity: Dict[str, int] = field(default_factory=dict)
    events_by_category: Dict[str, int] = field(default_factory=dict)
    incidents_by_status: Dict[str, int] = field(default_factory=dict)


class SIEMMonitoring:
    """
    SIEM monitoring system for enterprise environments.
    
    Provides security event monitoring, threat detection, and incident
    response capabilities with comprehensive reporting and metrics.
    """
    
    def __init__(self, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize SIEM monitoring system.
        
        Args:
            logger: Optional logger instance
            
        Raises:
            SIEMError: If initialization fails
        """
        try:
            self.logger = logger or HearthlinkLogger()
            
            # Event management
            self.events: List[SecurityEvent] = []
            self.event_index: Dict[str, List[int]] = defaultdict(list)
            
            # Threat detection
            self.threat_indicators: Dict[str, ThreatIndicator] = {}
            self.detection_rules: Dict[str, Callable] = {}
            
            # Alert management
            self.alerts: Dict[str, SecurityAlert] = {}
            self.alert_history: List[SecurityAlert] = []
            
            # Incident management
            self.incidents: Dict[str, SecurityIncident] = {}
            self.incident_history: List[SecurityIncident] = []
            
            # Metrics and reporting
            self.metrics_history: List[SecurityMetrics] = []
            
            # Configuration
            self.config = {
                "event_retention_days": 90,
                "alert_threshold": 3,
                "correlation_window_minutes": 15,
                "auto_incident_creation": True,
                "high_severity_auto_alert": True
            }
            
            # Initialize threat indicators and detection rules
            self._initialize_threat_indicators()
            self._setup_detection_rules()
            
            self._log("siem_monitoring_initialized", "system", None, "system", {
                "indicators_count": len(self.threat_indicators),
                "detection_rules_count": len(self.detection_rules)
            })
            
        except Exception as e:
            raise SIEMError(f"Failed to initialize SIEM monitoring: {str(e)}") from e
    
    def _initialize_threat_indicators(self):
        """Initialize default threat indicators."""
        default_indicators = [
            ThreatIndicator(
                indicator_id="brute_force_auth",
                threat_type=ThreatType.BRUTE_FORCE,
                pattern="multiple_failed_auth",
                description="Multiple failed authentication attempts",
                severity=EventSeverity.HIGH,
                conditions={
                    "event_count": 5,
                    "time_window_minutes": 10,
                    "event_category": EventCategory.AUTHENTICATION.value,
                    "action": "login_failed"
                }
            ),
            ThreatIndicator(
                indicator_id="privilege_escalation",
                threat_type=ThreatType.PRIVILEGE_ESCALATION,
                pattern="role_assignment_change",
                description="Suspicious role assignment changes",
                severity=EventSeverity.HIGH,
                conditions={
                    "event_category": EventCategory.AUTHORIZATION.value,
                    "action": "role_assigned",
                    "target_role": ["admin", "super_admin"]
                }
            ),
            ThreatIndicator(
                indicator_id="data_access_anomaly",
                threat_type=ThreatType.SUSPICIOUS_ACCESS,
                pattern="unusual_data_access",
                description="Unusual data access patterns",
                severity=EventSeverity.MEDIUM,
                conditions={
                    "event_category": EventCategory.DATA_ACCESS.value,
                    "access_count": 10,
                    "time_window_minutes": 5
                }
            ),
            ThreatIndicator(
                indicator_id="compliance_violation",
                threat_type=ThreatType.COMPLIANCE_VIOLATION,
                pattern="policy_violation",
                description="Compliance policy violations",
                severity=EventSeverity.MEDIUM,
                conditions={
                    "event_category": EventCategory.COMPLIANCE.value,
                    "severity": EventSeverity.HIGH.value
                }
            )
        ]
        
        for indicator in default_indicators:
            self.threat_indicators[indicator.indicator_id] = indicator
    
    def _setup_detection_rules(self):
        """Setup threat detection rules."""
        self.detection_rules = {
            "brute_force_auth": self._detect_brute_force,
            "privilege_escalation": self._detect_privilege_escalation,
            "data_access_anomaly": self._detect_data_access_anomaly,
            "compliance_violation": self._detect_compliance_violation
        }
    
    def collect_event(self, source: str, category: EventCategory, severity: EventSeverity,
                     user_id: Optional[str] = None, session_id: Optional[str] = None,
                     resource: Optional[str] = None, action: Optional[str] = None,
                     details: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect a security event.
        
        Args:
            source: Event source
            category: Event category
            severity: Event severity
            user_id: Optional user ID
            session_id: Optional session ID
            resource: Optional resource
            action: Optional action
            details: Optional event details
            
        Returns:
            Event ID of the collected event
            
        Raises:
            EventCollectionError: If event collection fails
        """
        try:
            # Create security event
            event_id = str(uuid.uuid4())
            event = SecurityEvent(
                event_id=event_id,
                timestamp=datetime.now().isoformat(),
                source=source,
                category=category,
                severity=severity,
                user_id=user_id,
                session_id=session_id,
                resource=resource,
                action=action,
                details=details or {}
            )
            
            # Store event
            self.events.append(event)
            
            # Index event for quick lookup
            self.event_index[category.value].append(len(self.events) - 1)
            if user_id:
                self.event_index[f"user:{user_id}"].append(len(self.events) - 1)
            if session_id:
                self.event_index[f"session:{session_id}"].append(len(self.events) - 1)
            
            # Trigger threat detection
            self._trigger_threat_detection(event)
            
            # Auto-alert for high severity events
            if severity in [EventSeverity.HIGH, EventSeverity.CRITICAL] and self.config["high_severity_auto_alert"]:
                self._create_high_severity_alert(event)
            
            self._log("security_event_collected", user_id, session_id, "event_collection", {
                "event_id": event_id,
                "category": category.value,
                "severity": severity.value,
                "source": source
            })
            
            return event_id
            
        except Exception as e:
            raise EventCollectionError(f"Failed to collect security event: {str(e)}") from e
    
    def _trigger_threat_detection(self, event: SecurityEvent):
        """Trigger threat detection for a security event."""
        try:
            for indicator_id, indicator in self.threat_indicators.items():
                if not indicator.is_active:
                    continue
                
                # Check if event matches indicator pattern
                if self._event_matches_indicator(event, indicator):
                    # Run detection rule
                    detection_rule = self.detection_rules.get(indicator.pattern)
                    if detection_rule:
                        threat_detected = detection_rule(event, indicator)
                        if threat_detected:
                            self._create_threat_alert(event, indicator)
            
        except Exception as e:
            self._log("threat_detection_error", event.user_id, event.session_id, "error", {
                "error": str(e),
                "event_id": event.event_id
            })
    
    def _event_matches_indicator(self, event: SecurityEvent, indicator: ThreatIndicator) -> bool:
        """Check if event matches threat indicator conditions."""
        try:
            conditions = indicator.conditions
            
            # Check event category
            if "event_category" in conditions:
                if event.category.value != conditions["event_category"]:
                    return False
            
            # Check action
            if "action" in conditions and event.action:
                if event.action != conditions["action"]:
                    return False
            
            # Check severity
            if "severity" in conditions:
                if event.severity.value != conditions["severity"]:
                    return False
            
            # Check target role (for privilege escalation)
            if "target_role" in conditions and event.details:
                target_role = event.details.get("target_role")
                if target_role not in conditions["target_role"]:
                    return False
            
            return True
            
        except Exception as e:
            self._log("indicator_matching_error", event.user_id, event.session_id, "error", {
                "error": str(e),
                "indicator_id": indicator.indicator_id
            })
            return False
    
    def _detect_brute_force(self, event: SecurityEvent, indicator: ThreatIndicator) -> bool:
        """Detect brute force attacks."""
        try:
            conditions = indicator.conditions
            time_window = timedelta(minutes=conditions.get("time_window_minutes", 10))
            threshold = conditions.get("event_count", 5)
            
            # Get recent failed auth events for the same user
            if not event.user_id:
                return False
            
            recent_events = self._get_recent_events(
                category=EventCategory.AUTHENTICATION,
                user_id=event.user_id,
                time_window=time_window
            )
            
            failed_auth_count = sum(
                1 for e in recent_events
                if e.action == "login_failed"
            )
            
            return failed_auth_count >= threshold
            
        except Exception as e:
            self._log("brute_force_detection_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
            return False
    
    def _detect_privilege_escalation(self, event: SecurityEvent, indicator: ThreatIndicator) -> bool:
        """Detect privilege escalation attempts."""
        try:
            # Check if this is a role assignment to admin roles
            if event.action == "role_assigned" and event.details:
                target_role = event.details.get("target_role")
                if target_role in ["admin", "super_admin"]:
                    # Check if user already has high privileges
                    user_events = self._get_recent_events(
                        category=EventCategory.AUTHORIZATION,
                        user_id=event.user_id,
                        time_window=timedelta(hours=24)
                    )
                    
                    # If user had recent role changes, this might be suspicious
                    role_changes = sum(
                        1 for e in user_events
                        if e.action in ["role_assigned", "role_removed"]
                    )
                    
                    return role_changes > 2
            
            return False
            
        except Exception as e:
            self._log("privilege_escalation_detection_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
            return False
    
    def _detect_data_access_anomaly(self, event: SecurityEvent, indicator: ThreatIndicator) -> bool:
        """Detect unusual data access patterns."""
        try:
            conditions = indicator.conditions
            time_window = timedelta(minutes=conditions.get("time_window_minutes", 5))
            threshold = conditions.get("access_count", 10)
            
            if not event.user_id:
                return False
            
            # Get recent data access events
            recent_events = self._get_recent_events(
                category=EventCategory.DATA_ACCESS,
                user_id=event.user_id,
                time_window=time_window
            )
            
            return len(recent_events) >= threshold
            
        except Exception as e:
            self._log("data_access_detection_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
            return False
    
    def _detect_compliance_violation(self, event: SecurityEvent, indicator: ThreatIndicator) -> bool:
        """Detect compliance violations."""
        try:
            # Check if event severity matches compliance violation criteria
            if event.severity in [EventSeverity.HIGH, EventSeverity.CRITICAL]:
                return True
            
            # Check for specific compliance violations in event details
            if event.details:
                violation_type = event.details.get("violation_type")
                if violation_type in ["data_breach", "policy_violation", "audit_failure"]:
                    return True
            
            return False
            
        except Exception as e:
            self._log("compliance_detection_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
            return False
    
    def _get_recent_events(self, category: Optional[EventCategory] = None,
                          user_id: Optional[str] = None, session_id: Optional[str] = None,
                          time_window: timedelta = timedelta(hours=1)) -> List[SecurityEvent]:
        """Get recent events matching criteria."""
        try:
            cutoff_time = datetime.now() - time_window
            recent_events = []
            
            for event in self.events:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time < cutoff_time:
                    continue
                
                # Apply filters
                if category and event.category != category:
                    continue
                if user_id and event.user_id != user_id:
                    continue
                if session_id and event.session_id != session_id:
                    continue
                
                recent_events.append(event)
            
            return recent_events
            
        except Exception as e:
            self._log("get_recent_events_error", user_id, session_id, "error", {
                "error": str(e)
            })
            return []
    
    def _create_threat_alert(self, event: SecurityEvent, indicator: ThreatIndicator):
        """Create a threat alert."""
        try:
            alert_id = str(uuid.uuid4())
            alert = SecurityAlert(
                alert_id=alert_id,
                threat_type=indicator.threat_type,
                severity=indicator.severity,
                description=indicator.description,
                events=[event.event_id]
            )
            
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Auto-create incident for high severity alerts
            if indicator.severity in [EventSeverity.HIGH, EventSeverity.CRITICAL] and self.config["auto_incident_creation"]:
                self._create_incident_from_alert(alert)
            
            self._log("threat_alert_created", event.user_id, event.session_id, "threat_detection", {
                "alert_id": alert_id,
                "threat_type": indicator.threat_type.value,
                "severity": indicator.severity.value
            })
            
        except Exception as e:
            self._log("alert_creation_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
    
    def _create_high_severity_alert(self, event: SecurityEvent):
        """Create alert for high severity events."""
        try:
            alert_id = str(uuid.uuid4())
            alert = SecurityAlert(
                alert_id=alert_id,
                threat_type=ThreatType.SUSPICIOUS_ACCESS,
                severity=event.severity,
                description=f"High severity event: {event.category.value}",
                events=[event.event_id]
            )
            
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
            
        except Exception as e:
            self._log("high_severity_alert_error", event.user_id, event.session_id, "error", {
                "error": str(e)
            })
    
    def _create_incident_from_alert(self, alert: SecurityAlert):
        """Create incident from security alert."""
        try:
            incident_id = str(uuid.uuid4())
            incident = SecurityIncident(
                incident_id=incident_id,
                alert_id=alert.alert_id,
                title=f"Security Incident: {alert.threat_type.value}",
                description=alert.description,
                severity=alert.severity,
                status=IncidentStatus.OPEN,
                events=alert.events
            )
            
            self.incidents[incident_id] = incident
            self.incident_history.append(incident)
            
            self._log("incident_created", "system", None, "incident_management", {
                "incident_id": incident_id,
                "alert_id": alert.alert_id,
                "threat_type": alert.threat_type.value
            })
            
        except Exception as e:
            self._log("incident_creation_error", "system", None, "error", {
                "error": str(e),
                "alert_id": alert.alert_id
            })
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus,
                              assigned_to: Optional[str] = None, action_taken: Optional[str] = None) -> bool:
        """
        Update incident status.
        
        Args:
            incident_id: Incident to update
            status: New status
            assigned_to: User assigned to incident
            action_taken: Description of action taken
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            incident.status = status
            incident.updated_at = datetime.now().isoformat()
            
            if assigned_to:
                incident.assigned_to = assigned_to
            
            if action_taken:
                incident.actions_taken.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": action_taken,
                    "by": assigned_to or "system"
                })
            
            self._log("incident_updated", assigned_to, None, "incident_management", {
                "incident_id": incident_id,
                "status": status.value,
                "action_taken": action_taken
            })
            
            return True
            
        except Exception as e:
            self._log("incident_update_error", assigned_to, None, "error", {
                "error": str(e),
                "incident_id": incident_id
            })
            return False
    
    def get_security_metrics(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> SecurityMetrics:
        """
        Get security metrics for reporting.
        
        Args:
            start_date: Start date for metrics period
            end_date: End date for metrics period
            
        Returns:
            Security metrics for the period
        """
        try:
            # Set default period if not provided
            if not end_date:
                end_date = datetime.now().isoformat()
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            # Filter events by date range
            period_events = [
                event for event in self.events
                if start_date <= event.timestamp <= end_date
            ]
            
            # Calculate metrics
            events_by_severity = defaultdict(int)
            events_by_category = defaultdict(int)
            
            for event in period_events:
                events_by_severity[event.severity.value] += 1
                events_by_category[event.category.value] += 1
            
            # Filter alerts and incidents by date range
            period_alerts = [
                alert for alert in self.alert_history
                if start_date <= alert.timestamp <= end_date
            ]
            
            period_incidents = [
                incident for incident in self.incident_history
                if start_date <= incident.created_at <= end_date
            ]
            
            incidents_by_status = defaultdict(int)
            for incident in period_incidents:
                incidents_by_status[incident.status.value] += 1
            
            # Calculate detection and resolution times
            detection_times = []
            resolution_times = []
            
            for incident in period_incidents:
                if incident.events:
                    # Find earliest event
                    earliest_event = min(
                        (event for event in self.events if event.event_id in incident.events),
                        key=lambda e: e.timestamp,
                        default=None
                    )
                    
                    if earliest_event:
                        detection_time = datetime.fromisoformat(incident.created_at) - datetime.fromisoformat(earliest_event.timestamp)
                        detection_times.append(detection_time.total_seconds() / 60)  # minutes
                
                if incident.status == IncidentStatus.RESOLVED:
                    resolution_time = datetime.fromisoformat(incident.updated_at) - datetime.fromisoformat(incident.created_at)
                    resolution_times.append(resolution_time.total_seconds() / 60)  # minutes
            
            metrics = SecurityMetrics(
                period_start=start_date,
                period_end=end_date,
                total_events=len(period_events),
                events_by_severity=dict(events_by_severity),
                events_by_category=dict(events_by_category),
                alerts_generated=len(period_alerts),
                incidents_created=len(period_incidents),
                incidents_by_status=dict(incidents_by_status),
                threat_detection_rate=len(period_alerts) / max(len(period_events), 1),
                mean_time_to_detect=sum(detection_times) / max(len(detection_times), 1),
                mean_time_to_resolve=sum(resolution_times) / max(len(resolution_times), 1)
            )
            
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            self._log("metrics_calculation_error", "system", None, "error", {
                "error": str(e)
            })
            
            # Return empty metrics on error
            return SecurityMetrics(
                period_start=start_date or datetime.now().isoformat(),
                period_end=end_date or datetime.now().isoformat(),
                total_events=0,
                alerts_generated=0,
                incidents_created=0,
                threat_detection_rate=0.0,
                mean_time_to_detect=0.0,
                mean_time_to_resolve=0.0
            )
    
    def get_active_alerts(self) -> List[SecurityAlert]:
        """Get all active alerts."""
        return [alert for alert in self.alerts.values() if alert.status == "new"]
    
    def get_active_incidents(self) -> List[SecurityIncident]:
        """Get all active incidents."""
        return [
            incident for incident in self.incidents.values()
            if incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]
        ]
    
    def export_security_report(self, user_id: str, start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> Dict[str, Any]:
        """Export comprehensive security report."""
        try:
            # Get metrics
            metrics = self.get_security_metrics(start_date, end_date)
            
            # Get active alerts and incidents
            active_alerts = self.get_active_alerts()
            active_incidents = self.get_active_incidents()
            
            # Compile report
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "generated_by": user_id,
                "period": {
                    "start": metrics.period_start,
                    "end": metrics.period_end
                },
                "metrics": asdict(metrics),
                "active_alerts": len(active_alerts),
                "active_incidents": len(active_incidents),
                "threat_summary": {
                    "total_threats": len(self.alert_history),
                    "threats_by_type": defaultdict(int)
                },
                "recommendations": self._generate_security_recommendations(metrics)
            }
            
            # Add threat type breakdown
            for alert in self.alert_history:
                report["threat_summary"]["threats_by_type"][alert.threat_type.value] += 1
            
            self._log("security_report_exported", user_id, None, "reporting", {
                "report_id": report["report_id"]
            })
            
            return report
            
        except Exception as e:
            self._log("report_export_error", user_id, None, "error", {
                "error": str(e)
            })
            return {}
    
    def _generate_security_recommendations(self, metrics: SecurityMetrics) -> List[str]:
        """Generate security recommendations based on metrics."""
        recommendations = []
        
        # High incident rate
        if metrics.incidents_created > 10:
            recommendations.append("High incident rate detected. Review security policies and user training.")
        
        # Low detection rate
        if metrics.threat_detection_rate < 0.1:
            recommendations.append("Low threat detection rate. Consider adding more threat indicators.")
        
        # High resolution time
        if metrics.mean_time_to_resolve > 480:  # 8 hours
            recommendations.append("Long incident resolution times. Review incident response procedures.")
        
        # High severity events
        if metrics.events_by_severity.get("critical", 0) > 0:
            recommendations.append("Critical events detected. Immediate attention required.")
        
        return recommendations
    
    def _log(self, action: str, user_id: str, session_id: Optional[str],
             event_type: str, details: Dict[str, Any]):
        """Log SIEM events for audit purposes."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "user_id": user_id,
                "session_id": session_id,
                "event_type": event_type,
                "details": details
            }
            
            if self.logger:
                self.logger.logger.info(f"SIEM {action}", extra=log_entry)
                
        except Exception:
            pass  # Don't let logging errors break SIEM functionality


def create_siem_monitoring(logger: Optional[HearthlinkLogger] = None) -> SIEMMonitoring:
    """
    Factory function to create SIEM monitoring system.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        Configured SIEMMonitoring instance
    """
    try:
        return SIEMMonitoring(logger=logger)
    except Exception as e:
        raise SIEMError(f"Failed to create SIEM monitoring: {str(e)}") from e 