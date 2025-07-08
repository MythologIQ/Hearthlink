#!/usr/bin/env python3
"""
Sentry — Security, Compliance & Oversight Persona

Sentry is the security and compliance overseer for the entire Hearthlink ecosystem,
providing adaptive threat detection, automated audit, user-friendly interventions,
and full override capability (user always in control, with informed risk).

Role: Security, Compliance & Oversight Persona

References:
- hearthlink_system_documentation_master.md: Sentry persona specification
- docs/ENTERPRISE_FEATURES.md: Enterprise security features
- docs/PLATINUM_BLOCKERS.md: Ethical safety rails and compliance
- appendix_h_developer_qa_platinum_checklists.md: QA requirements for error handling

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
from llm.local_llm_client import LocalLLMClient, LLMRequest, LLMResponse, LLMError

# Import enterprise security components
from enterprise.siem_monitoring import (
    SIEMMonitoring, SecurityEvent, EventCategory, EventSeverity,
    ThreatType, SecurityAlert, SecurityIncident
)
from enterprise.rbac_abac_security import RBACABACSecurity
from enterprise.advanced_monitoring import AdvancedMonitoring


class SentryError(HearthlinkError):
    """Base exception for Sentry-related errors."""
    pass


class RiskAssessmentError(SentryError):
    """Exception raised when risk assessment fails."""
    pass


class OverrideError(SentryError):
    """Exception raised when override operations fail."""
    pass


class AuditError(SentryError):
    """Exception raised when audit operations fail."""
    pass


class RiskLevel(Enum):
    """Risk levels for security events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(Enum):
    """Types of security events monitored by Sentry."""
    PLUGIN_PERMISSION_ESCALATION = "plugin_permission_escalation"
    SUSPICIOUS_ACCESS = "suspicious_access"
    DATA_ACCESS_ANOMALY = "data_access_anomaly"
    NETWORK_ANOMALY = "network_anomaly"
    SYSTEM_ANOMALY = "system_anomaly"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MANIFEST_CHANGE = "manifest_change"
    CODE_DRIFT = "code_drift"
    UNAUTHORIZED_CONNECTION = "unauthorized_connection"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class OverrideReason(Enum):
    """Valid reasons for user overrides."""
    FALSE_POSITIVE = "false_positive"
    BUSINESS_NEED = "business_need"
    TESTING = "testing"
    EMERGENCY = "emergency"
    AUTHORIZED_CHANGE = "authorized_change"


@dataclass
class RiskEvent:
    """Risk event for Sentry monitoring."""
    event_id: str
    event_type: EventType
    origin: str
    risk_score: int  # 0-100
    recommended_action: str
    user_override: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    resolution: Optional[str] = None
    escalation_chain: List[str] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OverrideEvent:
    """User override event."""
    override_id: str
    event_id: str
    user_id: str
    reason: OverrideReason
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    risk_acknowledged: bool = True
    escalation_triggered: bool = False


@dataclass
class KillSwitchEvent:
    """Kill switch activation event."""
    kill_id: str
    target_id: str
    target_type: str  # "plugin", "agent", "connection"
    reason: str
    user_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    impact_report: Dict[str, Any] = field(default_factory=dict)
    rollback_available: bool = True


@dataclass
class RiskThresholds:
    """Configurable risk thresholds."""
    low_threshold: int = 30
    medium_threshold: int = 60
    high_threshold: int = 80
    critical_threshold: int = 90
    auto_block_threshold: int = 95
    escalation_threshold: int = 3  # Number of overrides before escalation


@dataclass
class SentryConfig:
    """Sentry configuration."""
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    auto_block_enabled: bool = True
    escalation_enabled: bool = True
    audit_retention_days: int = 365
    real_time_monitoring: bool = True
    whitelist: Set[str] = field(default_factory=set)
    blacklist: Set[str] = field(default_factory=set)


@dataclass
class SentryMemory:
    """Sentry's memory and state."""
    persona_id: str = "sentry"
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Configuration
    config: SentryConfig = field(default_factory=SentryConfig)
    
    # Event tracking
    risk_events: List[RiskEvent] = field(default_factory=list)
    override_events: List[OverrideEvent] = field(default_factory=list)
    kill_switch_events: List[KillSwitchEvent] = field(default_factory=list)
    
    # Statistics
    total_events_processed: int = 0
    total_overrides: int = 0
    total_kill_switches: int = 0
    current_risk_score: int = 0
    
    # Audit trail
    audit_log: List[Dict[str, Any]] = field(default_factory=list)


class SentryPersona:
    """
    Sentry — Security, Compliance & Oversight Persona
    
    Security and compliance overseer for the entire Hearthlink ecosystem,
    providing adaptive threat detection, automated audit, user-friendly
    interventions, and full override capability.
    """
    
    def __init__(self, llm_client: LocalLLMClient, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Sentry persona.
        
        Args:
            llm_client: Configured LLM client
            logger: Optional logger instance
            
        Raises:
            SentryError: If persona initialization fails
        """
        try:
            # Validate LLM client (skip validation for Mock objects in testing)
            if not hasattr(llm_client, '_mock_name') and not isinstance(llm_client, LocalLLMClient):
                raise SentryError("LLM client must be an instance of LocalLLMClient")
            
            self.llm_client = llm_client
            self.logger = logger or HearthlinkLogger()
            self.memory = SentryMemory()
            
            # Initialize enterprise security components
            self.siem = SIEMMonitoring(logger=self.logger)
            self.rbac_abac = RBACABACSecurity(logger=self.logger)
            self.monitoring = AdvancedMonitoring(logger=self.logger)
            
            # Initialize risk assessment engine
            self._initialize_risk_engine()
            
            # Load baseline prompts
            self._load_baseline_prompts()
            
            self.logger.info("Sentry persona initialized successfully")
            
        except Exception as e:
            # Create basic error context without accessing self.memory
            error_context = {
                "error_type": "initialization_error",
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "operation": "sentry_initialization",
                "user_id": str(uuid.uuid4()),
                "persona_id": "sentry",
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to log error context if logger is available
            try:
                if hasattr(self, 'logger') and self.logger:
                    self._log_error_context(error_context)
            except:
                pass  # Ignore logging errors during initialization
            
            raise SentryError(f"Failed to initialize Sentry persona: {e}")
    
    def _initialize_risk_engine(self) -> None:
        """Initialize the risk assessment engine."""
        try:
            # Initialize risk assessment rules
            self.risk_rules = {
                EventType.PLUGIN_PERMISSION_ESCALATION: self._assess_plugin_permission_risk,
                EventType.SUSPICIOUS_ACCESS: self._assess_suspicious_access_risk,
                EventType.DATA_ACCESS_ANOMALY: self._assess_data_access_risk,
                EventType.NETWORK_ANOMALY: self._assess_network_risk,
                EventType.SYSTEM_ANOMALY: self._assess_system_risk,
                EventType.COMPLIANCE_VIOLATION: self._assess_compliance_risk,
                EventType.MANIFEST_CHANGE: self._assess_manifest_risk,
                EventType.CODE_DRIFT: self._assess_code_drift_risk,
                EventType.UNAUTHORIZED_CONNECTION: self._assess_connection_risk,
                EventType.PRIVILEGE_ESCALATION: self._assess_privilege_risk
            }
            
            # Initialize escalation tracking
            self.escalation_tracker = defaultdict(int)
            
            self.logger.info("Risk assessment engine initialized")
            
        except Exception as e:
            raise SentryError(f"Failed to initialize risk engine: {e}")
    
    def _load_baseline_prompts(self) -> None:
        """Load baseline prompts for Sentry."""
        try:
            self.baseline_prompts = {
                "risk_assessment": """
                You are Sentry, the security and compliance overseer for the Hearthlink ecosystem.
                Your role is to assess security risks and provide clear, actionable recommendations.
                
                Current risk event: {event_details}
                Risk score: {risk_score}
                Recommended action: {recommended_action}
                
                Provide a clear explanation of the risk and recommended mitigation steps.
                Always prioritize user safety while respecting user autonomy.
                """,
                
                "override_explanation": """
                User has requested to override a security block.
                Event ID: {event_id}
                Override reason: {reason}
                User explanation: {explanation}
                
                Explain the risks of this override and any recommended precautions.
                Ensure the user understands the potential consequences.
                """,
                
                "kill_switch_warning": """
                Kill switch activation requested.
                Target: {target_id} ({target_type})
                Reason: {reason}
                
                Confirm the kill switch activation and explain the impact.
                Provide rollback instructions if available.
                """
            }
            
        except Exception as e:
            raise SentryError(f"Failed to load baseline prompts: {e}")
    
    def monitor_event(self, event_type: EventType, origin: str, details: Dict[str, Any]) -> RiskEvent:
        """
        Monitor a security event and assess risk.
        
        Args:
            event_type: Type of security event
            origin: Source of the event
            details: Event details
            
        Returns:
            RiskEvent: Assessed risk event
            
        Raises:
            RiskAssessmentError: If risk assessment fails
        """
        try:
            # Generate event ID
            event_id = f"risk-{uuid.uuid4().hex[:8]}"
            
            # Assess risk using appropriate rule
            if event_type in self.risk_rules:
                risk_score, recommended_action = self.risk_rules[event_type](details)
            else:
                risk_score, recommended_action = self._assess_generic_risk(details)
            
            # Create risk event
            risk_event = RiskEvent(
                event_id=event_id,
                event_type=event_type,
                origin=origin,
                risk_score=risk_score,
                recommended_action=recommended_action,
                metadata=details
            )
            
            # Add to memory
            self.memory.risk_events.append(risk_event)
            self.memory.total_events_processed += 1
            
            # Update current risk score
            self._update_risk_score()
            
            # Log the event
            self._log_event("event_monitored", {
                "event_id": event_id,
                "event_type": event_type.value,
                "origin": origin,
                "risk_score": risk_score,
                "recommended_action": recommended_action
            })
            
            # Check for auto-block
            if self.memory.config.auto_block_enabled and risk_score >= self.memory.config.risk_thresholds.auto_block_threshold:
                self._auto_block_event(risk_event)
            
            return risk_event
            
        except Exception as e:
            raise RiskAssessmentError(f"Failed to monitor event: {e}")
    
    def _assess_plugin_permission_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for plugin permission escalation."""
        risk_score = 70  # Base score for permission escalation
        
        # Adjust based on details
        if details.get("plugin_id") in self.memory.config.blacklist:
            risk_score = 95
        elif details.get("plugin_id") in self.memory.config.whitelist:
            risk_score = 30
        
        if details.get("permission_level") == "admin":
            risk_score += 20
        
        if details.get("requested_permissions"):
            risk_score += len(details["requested_permissions"]) * 5
        
        recommended_action = "block" if risk_score >= 80 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_suspicious_access_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for suspicious access patterns."""
        risk_score = 60  # Base score for suspicious access
        
        # Adjust based on access patterns
        if details.get("access_count", 0) > 10:
            risk_score += 20
        
        if details.get("time_window") and details["time_window"] < 300:  # 5 minutes
            risk_score += 15
        
        if details.get("failed_attempts", 0) > 3:
            risk_score += 25
        
        recommended_action = "block" if risk_score >= 75 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_data_access_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for data access anomalies."""
        risk_score = 50  # Base score for data access
        
        # Adjust based on data sensitivity
        if details.get("data_sensitivity") == "high":
            risk_score += 30
        
        if details.get("access_pattern") == "bulk_export":
            risk_score += 20
        
        if details.get("unusual_time"):
            risk_score += 15
        
        recommended_action = "block" if risk_score >= 70 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_network_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for network anomalies."""
        risk_score = 65  # Base score for network anomalies
        
        # Adjust based on network activity
        if details.get("external_connection"):
            risk_score += 20
        
        if details.get("data_volume") and details["data_volume"] > 1000000:  # 1MB
            risk_score += 15
        
        if details.get("encrypted") == False:
            risk_score += 25
        
        recommended_action = "block" if risk_score >= 75 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_system_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for system anomalies."""
        risk_score = 55  # Base score for system anomalies
        
        # Adjust based on system changes
        if details.get("system_change"):
            risk_score += 20
        
        if details.get("resource_usage") and details["resource_usage"] > 80:
            risk_score += 15
        
        if details.get("process_anomaly"):
            risk_score += 25
        
        recommended_action = "block" if risk_score >= 70 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_compliance_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for compliance violations."""
        risk_score = 80  # Base score for compliance violations
        
        # Adjust based on violation type
        if details.get("violation_type") == "data_breach":
            risk_score = 95
        elif details.get("violation_type") == "access_violation":
            risk_score += 10
        
        recommended_action = "block" if risk_score >= 85 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_manifest_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for manifest changes."""
        risk_score = 60  # Base score for manifest changes
        
        # Adjust based on change type
        if details.get("permission_changes"):
            risk_score += 20
        
        if details.get("signature_mismatch"):
            risk_score += 30
        
        if details.get("version_change"):
            risk_score += 10
        
        recommended_action = "block" if risk_score >= 75 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_code_drift_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for code drift."""
        risk_score = 70  # Base score for code drift
        
        # Adjust based on drift severity
        if details.get("drift_percentage", 0) > 50:
            risk_score += 20
        
        if details.get("critical_functions_changed"):
            risk_score += 25
        
        recommended_action = "block" if risk_score >= 80 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_connection_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for unauthorized connections."""
        risk_score = 85  # Base score for unauthorized connections
        
        # Adjust based on connection details
        if details.get("external_domain"):
            risk_score += 10
        
        if details.get("unencrypted"):
            risk_score += 15
        
        recommended_action = "block" if risk_score >= 80 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_privilege_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for privilege escalation."""
        risk_score = 90  # Base score for privilege escalation
        
        # Adjust based on escalation details
        if details.get("target_role") == "admin":
            risk_score += 10
        
        if details.get("escalation_method") == "exploit":
            risk_score = 100
        
        recommended_action = "block" if risk_score >= 85 else "warn"
        return min(risk_score, 100), recommended_action
    
    def _assess_generic_risk(self, details: Dict[str, Any]) -> tuple[int, str]:
        """Assess risk for generic events."""
        risk_score = 50  # Default risk score
        recommended_action = "warn"
        return risk_score, recommended_action
    
    def _update_risk_score(self) -> None:
        """Update current system risk score."""
        try:
            if not self.memory.risk_events:
                self.memory.current_risk_score = 0
                return
            
            # Calculate average risk score from recent events
            recent_events = [
                event for event in self.memory.risk_events
                if datetime.fromisoformat(event.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            if recent_events:
                avg_score = sum(event.risk_score for event in recent_events) / len(recent_events)
                self.memory.current_risk_score = int(avg_score)
            else:
                self.memory.current_risk_score = 0
                
        except Exception as e:
            self.logger.error(f"Failed to update risk score: {e}")
    
    def _auto_block_event(self, risk_event: RiskEvent) -> None:
        """Automatically block high-risk events."""
        try:
            risk_event.recommended_action = "block"
            risk_event.audit_log.append({
                "action": "auto_blocked",
                "by": "sentry",
                "timestamp": datetime.now().isoformat(),
                "reason": "Risk score exceeded auto-block threshold"
            })
            
            self._log_event("auto_block", {
                "event_id": risk_event.event_id,
                "risk_score": risk_event.risk_score,
                "threshold": self.memory.config.risk_thresholds.auto_block_threshold
            })
            
        except Exception as e:
            self.logger.error(f"Failed to auto-block event: {e}")
    
    def override_event(self, event_id: str, user_id: str, reason: OverrideReason, 
                      explanation: str) -> OverrideEvent:
        """
        Override a security event.
        
        Args:
            event_id: ID of the event to override
            user_id: ID of the user performing override
            reason: Reason for override
            explanation: User explanation
            
        Returns:
            OverrideEvent: Created override event
            
        Raises:
            OverrideError: If override fails
        """
        try:
            # Find the risk event
            risk_event = next((event for event in self.memory.risk_events if event.event_id == event_id), None)
            if not risk_event:
                raise OverrideError(f"Risk event {event_id} not found")
            
            # Create override event
            override_id = f"override-{uuid.uuid4().hex[:8]}"
            override_event = OverrideEvent(
                override_id=override_id,
                event_id=event_id,
                user_id=user_id,
                reason=reason,
                explanation=explanation
            )
            
            # Update risk event
            risk_event.user_override = True
            risk_event.resolution = f"Overridden by {user_id}: {explanation}"
            risk_event.audit_log.append({
                "action": "user_override",
                "by": user_id,
                "timestamp": datetime.now().isoformat(),
                "reason": reason.value,
                "explanation": explanation
            })
            
            # Add to memory
            self.memory.override_events.append(override_event)
            self.memory.total_overrides += 1
            
            # Check for escalation
            self._check_escalation(user_id)
            
            # Log the override
            self._log_event("event_overridden", {
                "event_id": event_id,
                "override_id": override_id,
                "user_id": user_id,
                "reason": reason.value,
                "explanation": explanation
            })
            
            return override_event
            
        except Exception as e:
            raise OverrideError(f"Failed to override event: {e}")
    
    def _check_escalation(self, user_id: str) -> None:
        """Check if user overrides require escalation."""
        try:
            if not self.memory.config.escalation_enabled:
                return
            
            # Count recent overrides by user
            recent_overrides = [
                override for override in self.memory.override_events
                if override.user_id == user_id and
                datetime.fromisoformat(override.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            if len(recent_overrides) >= self.memory.config.risk_thresholds.escalation_threshold:
                self.escalation_tracker[user_id] += 1
                
                # Trigger escalation
                self._trigger_escalation(user_id, len(recent_overrides))
                
        except Exception as e:
            self.logger.error(f"Failed to check escalation: {e}")
    
    def _trigger_escalation(self, user_id: str, override_count: int) -> None:
        """Trigger escalation for user with too many overrides."""
        try:
            escalation_event = RiskEvent(
                event_id=f"escalation-{uuid.uuid4().hex[:8]}",
                event_type=EventType.COMPLIANCE_VIOLATION,
                origin="sentry",
                risk_score=85,
                recommended_action="review_required",
                metadata={
                    "user_id": user_id,
                    "override_count": override_count,
                    "escalation_reason": "Excessive overrides"
                }
            )
            
            self.memory.risk_events.append(escalation_event)
            
            self._log_event("escalation_triggered", {
                "user_id": user_id,
                "override_count": override_count,
                "escalation_id": escalation_event.event_id
            })
            
        except Exception as e:
            self.logger.error(f"Failed to trigger escalation: {e}")
    
    def activate_kill_switch(self, target_id: str, target_type: str, reason: str, 
                           user_id: str) -> KillSwitchEvent:
        """
        Activate kill switch for a target.
        
        Args:
            target_id: ID of the target to kill
            target_type: Type of target (plugin, agent, connection)
            reason: Reason for kill switch
            user_id: ID of the user activating kill switch
            
        Returns:
            KillSwitchEvent: Created kill switch event
            
        Raises:
            SentryError: If kill switch activation fails
        """
        try:
            # Create kill switch event
            kill_id = f"kill-{uuid.uuid4().hex[:8]}"
            kill_event = KillSwitchEvent(
                kill_id=kill_id,
                target_id=target_id,
                target_type=target_type,
                reason=reason,
                user_id=user_id
            )
            
            # Generate impact report
            kill_event.impact_report = self._generate_impact_report(target_id, target_type)
            
            # Add to memory
            self.memory.kill_switch_events.append(kill_event)
            self.memory.total_kill_switches += 1
            
            # Log the kill switch
            self._log_event("kill_switch_activated", {
                "kill_id": kill_id,
                "target_id": target_id,
                "target_type": target_type,
                "reason": reason,
                "user_id": user_id
            })
            
            return kill_event
            
        except Exception as e:
            raise SentryError(f"Failed to activate kill switch: {e}")
    
    def _generate_impact_report(self, target_id: str, target_type: str) -> Dict[str, Any]:
        """Generate impact report for kill switch."""
        try:
            impact_report = {
                "target_id": target_id,
                "target_type": target_type,
                "timestamp": datetime.now().isoformat(),
                "affected_sessions": [],
                "affected_data": [],
                "rollback_steps": []
            }
            
            # Add specific impact details based on target type
            if target_type == "plugin":
                impact_report["rollback_steps"] = [
                    "Restore plugin from backup",
                    "Verify plugin integrity",
                    "Re-enable plugin with reduced permissions"
                ]
            elif target_type == "agent":
                impact_report["rollback_steps"] = [
                    "Restart agent process",
                    "Verify agent state",
                    "Re-establish agent connections"
                ]
            elif target_type == "connection":
                impact_report["rollback_steps"] = [
                    "Re-establish connection",
                    "Verify connection security",
                    "Update connection policies"
                ]
            
            return impact_report
            
        except Exception as e:
            self.logger.error(f"Failed to generate impact report: {e}")
            return {"error": str(e)}
    
    def get_risk_dashboard(self) -> Dict[str, Any]:
        """
        Get current risk dashboard data.
        
        Returns:
            Dict containing dashboard data
        """
        try:
            # Get recent risk events
            recent_events = [
                event for event in self.memory.risk_events
                if datetime.fromisoformat(event.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            # Get active overrides
            active_overrides = [
                override for override in self.memory.override_events
                if datetime.fromisoformat(override.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            # Get recent kill switches
            recent_kills = [
                kill for kill in self.memory.kill_switch_events
                if datetime.fromisoformat(kill.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            dashboard_data = {
                "current_risk_score": self.memory.current_risk_score,
                "risk_thresholds": asdict(self.memory.config.risk_thresholds),
                "recent_events": [asdict(event) for event in recent_events],
                "active_overrides": [asdict(override) for override in active_overrides],
                "recent_kills": [asdict(kill) for kill in recent_kills],
                "escalation_status": dict(self.escalation_tracker),
                "statistics": {
                    "total_events": self.memory.total_events_processed,
                    "total_overrides": self.memory.total_overrides,
                    "total_kills": self.memory.total_kill_switches
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get risk dashboard: {e}")
            return {"error": str(e)}
    
    def export_audit_log(self, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Export audit log for compliance.
        
        Args:
            start_date: Start date for export (ISO format)
            end_date: End date for export (ISO format)
            
        Returns:
            Dict containing audit log data
        """
        try:
            # Filter events by date range
            start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
            
            filtered_events = [
                event for event in self.memory.risk_events
                if start_dt <= datetime.fromisoformat(event.timestamp) <= end_dt
            ]
            
            filtered_overrides = [
                override for override in self.memory.override_events
                if start_dt <= datetime.fromisoformat(override.timestamp) <= end_dt
            ]
            
            filtered_kills = [
                kill for kill in self.memory.kill_switch_events
                if start_dt <= datetime.fromisoformat(kill.timestamp) <= end_dt
            ]
            
            audit_log = {
                "export_timestamp": datetime.now().isoformat(),
                "date_range": {
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat()
                },
                "risk_events": [asdict(event) for event in filtered_events],
                "override_events": [asdict(override) for override in filtered_overrides],
                "kill_switch_events": [asdict(kill) for kill in filtered_kills],
                "summary": {
                    "total_events": len(filtered_events),
                    "total_overrides": len(filtered_overrides),
                    "total_kills": len(filtered_kills),
                    "average_risk_score": sum(event.risk_score for event in filtered_events) / len(filtered_events) if filtered_events else 0
                }
            }
            
            return audit_log
            
        except Exception as e:
            raise AuditError(f"Failed to export audit log: {e}")
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """
        Update Sentry configuration.
        
        Args:
            config_updates: Configuration updates to apply
            
        Raises:
            SentryError: If configuration update fails
        """
        try:
            # Update risk thresholds
            if "risk_thresholds" in config_updates:
                thresholds = config_updates["risk_thresholds"]
                for key, value in thresholds.items():
                    if hasattr(self.memory.config.risk_thresholds, key):
                        setattr(self.memory.config.risk_thresholds, key, value)
            
            # Update other config options
            for key, value in config_updates.items():
                if key != "risk_thresholds" and hasattr(self.memory.config, key):
                    setattr(self.memory.config, key, value)
            
            # Log configuration update
            self._log_event("config_updated", {
                "updates": config_updates,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            raise SentryError(f"Failed to update configuration: {e}")
    
    def _log_event(self, action: str, details: Dict[str, Any]) -> None:
        """Log an event to the audit trail."""
        try:
            log_entry = {
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            
            self.memory.audit_log.append(log_entry)
            self.logger.info(f"Sentry event: {action}", extra=details)
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")
    
    def _log_error_context(self, error_context: Dict[str, Any]) -> None:
        """Log error context for debugging."""
        try:
            self.logger.error("Sentry error occurred", extra=error_context)
            
            # Add to audit log
            self.memory.audit_log.append({
                "action": "error",
                "timestamp": datetime.now().isoformat(),
                "error_context": error_context
            })
            
        except Exception as e:
            # Fallback logging
            print(f"Failed to log error context: {e}")
            print(f"Original error context: {error_context}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get Sentry status information.
        
        Returns:
            Dict containing status information
        """
        try:
            return {
                "persona_id": self.memory.persona_id,
                "status": "active",
                "current_risk_score": self.memory.current_risk_score,
                "config": asdict(self.memory.config),
                "statistics": {
                    "total_events_processed": self.memory.total_events_processed,
                    "total_overrides": self.memory.total_overrides,
                    "total_kill_switches": self.memory.total_kill_switches,
                    "active_escalations": len(self.escalation_tracker)
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}


def create_sentry_persona(llm_config: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> SentryPersona:
    """
    Create a Sentry persona instance.
    
    Args:
        llm_config: LLM configuration
        logger: Optional logger instance
        
    Returns:
        SentryPersona: Configured Sentry persona
        
    Raises:
        SentryError: If persona creation fails
    """
    try:
        # Create LLM client
        llm_client = LocalLLMClient(llm_config)
        
        # Create Sentry persona
        sentry = SentryPersona(llm_client, logger)
        
        return sentry
        
    except Exception as e:
        raise SentryError(f"Failed to create Sentry persona: {e}")


if __name__ == "__main__":
    # Test Sentry persona
    try:
        # Create test configuration
        test_config = {
            "model": "test-model",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Create Sentry persona
        sentry = create_sentry_persona(test_config)
        
        # Test monitoring
        test_event = sentry.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-plugin",
            {"plugin_id": "test-plugin", "permission_level": "admin"}
        )
        
        print(f"Test event created: {test_event.event_id}")
        print(f"Risk score: {test_event.risk_score}")
        print(f"Recommended action: {test_event.recommended_action}")
        
        # Test override
        override = sentry.override_event(
            test_event.event_id,
            "test-user",
            OverrideReason.BUSINESS_NEED,
            "Testing override functionality"
        )
        
        print(f"Override created: {override.override_id}")
        
        # Get dashboard
        dashboard = sentry.get_risk_dashboard()
        print(f"Dashboard data: {dashboard}")
        
        print("Sentry persona test completed successfully")
        
    except Exception as e:
        print(f"Sentry persona test failed: {e}")
        traceback.print_exc() 