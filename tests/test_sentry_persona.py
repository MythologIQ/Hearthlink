#!/usr/bin/env python3
"""
Comprehensive test suite for Sentry persona.

Tests all security monitoring, compliance validation, and risk assessment capabilities
including alert management, kill switch functionality, and audit logging.
"""

import asyncio
import json
import logging
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personas.sentry import (
    SentryPersona, SecurityLevel, ComplianceFramework, RiskCategory,
    SecurityAlert, ComplianceCheck, RiskAssessment
)
from enterprise.siem_monitoring import SIEMMonitoring, SecurityEvent, EventCategory, EventSeverity
from enterprise.rbac_abac_security import RBACABACSecurity, PolicyEffect
from enterprise.advanced_monitoring import AdvancedMonitoring


class TestSentryPersona(unittest.TestCase):
    """Test suite for Sentry persona functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.logger = logging.getLogger("test_sentry")
        self.siem_mock = Mock(spec=SIEMMonitoring)
        self.security_mock = Mock(spec=RBACABACSecurity)
        self.monitoring_mock = Mock(spec=AdvancedMonitoring)
        
        # Create Sentry persona with mocked dependencies
        self.sentry = SentryPersona(
            persona_id="test-sentry",
            logger=self.logger,
            siem_monitoring=self.siem_mock,
            security_system=self.security_mock,
            monitoring_system=self.monitoring_mock
        )
    
    def test_initialization(self):
        """Test Sentry persona initialization."""
        self.assertEqual(self.sentry.persona_id, "test-sentry")
        self.assertTrue(self.sentry.monitoring_active)
        self.assertFalse(self.sentry.kill_switch_active)
        self.assertEqual(self.sentry.escalation_level, 0)
        self.assertIsInstance(self.sentry.security_policies, dict)
        self.assertIsInstance(self.sentry.active_alerts, dict)
        self.assertIsInstance(self.sentry.compliance_checks, dict)
        self.assertIsInstance(self.sentry.risk_assessments, dict)
    
    def test_security_policies_initialization(self):
        """Test security policies are properly initialized."""
        expected_policies = ["data_access", "file_operations", "network_access", "user_privileges"]
        
        for policy in expected_policies:
            self.assertIn(policy, self.sentry.security_policies)
            self.assertIsInstance(self.sentry.security_policies[policy], dict)
    
    def test_alert_thresholds_initialization(self):
        """Test alert thresholds are properly set."""
        expected_thresholds = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 3,
            SecurityLevel.HIGH: 5,
            SecurityLevel.CRITICAL: 1
        }
        
        for level, threshold in expected_thresholds.items():
            self.assertEqual(self.sentry.alert_thresholds[level], threshold)
    
    def test_compliance_frameworks_initialization(self):
        """Test compliance frameworks are properly initialized."""
        expected_frameworks = [
            ComplianceFramework.GDPR,
            ComplianceFramework.HIPAA,
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
            ComplianceFramework.PCI_DSS
        ]
        
        for framework in expected_frameworks:
            self.assertIn(framework, self.sentry.compliance_frameworks)
    
    def test_threat_level_assessment(self):
        """Test threat level assessment for different event severities."""
        # Test critical event
        critical_event = SecurityEvent(
            event_id="test-1",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.CRITICAL,
            user_id="user1",
            action="failed_login"
        )
        
        level = self.sentry._assess_threat_level(critical_event)
        self.assertEqual(level, SecurityLevel.CRITICAL)
        
        # Test high event
        high_event = SecurityEvent(
            event_id="test-2",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.DATA_ACCESS,
            severity=EventSeverity.HIGH,
            user_id="user2",
            action="unauthorized_access"
        )
        
        level = self.sentry._assess_threat_level(high_event)
        self.assertEqual(level, SecurityLevel.HIGH)
        
        # Test medium event
        medium_event = SecurityEvent(
            event_id="test-3",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.SYSTEM,
            severity=EventSeverity.MEDIUM,
            user_id="user3",
            action="system_warning"
        )
        
        level = self.sentry._assess_threat_level(medium_event)
        self.assertEqual(level, SecurityLevel.MEDIUM)
        
        # Test low event
        low_event = SecurityEvent(
            event_id="test-4",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.COMPLIANCE,
            severity=EventSeverity.LOW,
            user_id="user4",
            action="policy_check"
        )
        
        level = self.sentry._assess_threat_level(low_event)
        self.assertEqual(level, SecurityLevel.LOW)
    
    def test_threat_categorization(self):
        """Test threat categorization for different event categories."""
        # Test authentication event
        auth_event = SecurityEvent(
            event_id="test-1",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.HIGH,
            user_id="user1",
            action="failed_login"
        )
        
        category = self.sentry._categorize_threat(auth_event)
        self.assertEqual(category, RiskCategory.UNAUTHORIZED_ACCESS)
        
        # Test data access event
        data_event = SecurityEvent(
            event_id="test-2",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.DATA_ACCESS,
            severity=EventSeverity.HIGH,
            user_id="user2",
            action="data_export"
        )
        
        category = self.sentry._categorize_threat(data_event)
        self.assertEqual(category, RiskCategory.DATA_BREACH)
        
        # Test system event
        system_event = SecurityEvent(
            event_id="test-3",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.SYSTEM,
            severity=EventSeverity.HIGH,
            user_id="user3",
            action="system_compromise"
        )
        
        category = self.sentry._categorize_threat(system_event)
        self.assertEqual(category, RiskCategory.SYSTEM_COMPROMISE)
        
        # Test compliance event
        compliance_event = SecurityEvent(
            event_id="test-4",
            timestamp=datetime.now().isoformat(),
            source="test",
            category=EventCategory.COMPLIANCE,
            severity=EventSeverity.HIGH,
            user_id="user4",
            action="policy_violation"
        )
        
        category = self.sentry._categorize_threat(compliance_event)
        self.assertEqual(category, RiskCategory.COMPLIANCE_VIOLATION)
    
    def test_kill_switch_activation(self):
        """Test kill switch activation and deactivation."""
        # Test activation
        asyncio.run(self.sentry.activate_kill_switch("Test emergency"))
        
        self.assertTrue(self.sentry.kill_switch_active)
        self.assertFalse(self.sentry.monitoring_active)
        
        # Test deactivation (with mock authorization)
        self.security_mock.evaluate_access.return_value = PolicyEffect.ALLOW
        
        asyncio.run(self.sentry.deactivate_kill_switch("Test resolution", "admin"))
        
        self.assertFalse(self.sentry.kill_switch_active)
        self.assertTrue(self.sentry.monitoring_active)
    
    def test_kill_switch_authorization(self):
        """Test kill switch deactivation authorization."""
        # Test unauthorized deactivation
        self.security_mock.evaluate_access.return_value = PolicyEffect.DENY
        
        with self.assertRaises(PermissionError):
            asyncio.run(self.sentry.deactivate_kill_switch("Test", "user"))
    
    def test_alert_management(self):
        """Test alert creation, acknowledgment, and resolution."""
        # Create a test alert
        alert = SecurityAlert(
            alert_id="test-alert-1",
            timestamp=datetime.now().isoformat(),
            level=SecurityLevel.HIGH,
            category=RiskCategory.UNAUTHORIZED_ACCESS,
            title="Test Alert",
            description="Test alert description",
            source="test"
        )
        
        self.sentry.active_alerts[alert.alert_id] = alert
        
        # Test acknowledgment
        self.sentry.acknowledge_alert(alert.alert_id, "user1")
        self.assertTrue(alert.acknowledged)
        
        # Test resolution
        self.sentry.resolve_alert(alert.alert_id, "user1", "Test resolution")
        self.assertTrue(alert.resolved)
        self.assertEqual(alert.details["resolution_notes"], "Test resolution")
        self.assertEqual(alert.details["resolved_by"], "user1")
    
    def test_security_policy_updates(self):
        """Test security policy updates."""
        # Update a policy
        new_policy_data = {"max_failed_attempts": 5}
        self.sentry.update_security_policy("data_access", new_policy_data, "admin")
        
        self.assertEqual(
            self.sentry.security_policies["data_access"]["max_failed_attempts"], 
            5
        )
    
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        # Test with no risk factors
        risk_factors = []
        score = self.sentry._calculate_risk_score(risk_factors)
        self.assertEqual(score, 0.0)
        
        # Test with risk factors
        risk_factors = [
            {"factor": "test1", "score": 0.3, "description": "Test risk 1"},
            {"factor": "test2", "score": 0.4, "description": "Test risk 2"}
        ]
        score = self.sentry._calculate_risk_score(risk_factors)
        self.assertEqual(score, 0.7)
        
        # Test score capping at 1.0
        risk_factors = [
            {"factor": "test1", "score": 0.6, "description": "Test risk 1"},
            {"factor": "test2", "score": 0.5, "description": "Test risk 2"}
        ]
        score = self.sentry._calculate_risk_score(risk_factors)
        self.assertEqual(score, 1.0)
    
    def test_risk_recommendations_generation(self):
        """Test risk recommendation generation."""
        risk_factors = [
            {"factor": "active_security_alerts", "score": 0.3, "description": "3 active alerts"},
            {"factor": "compliance_violations", "score": 0.4, "description": "2 violations"}
        ]
        
        recommendations = self.sentry._generate_risk_recommendations(risk_factors)
        
        self.assertIn("Review and resolve active security alerts immediately", recommendations)
        self.assertIn("Address compliance violations to maintain regulatory compliance", recommendations)
    
    def test_mitigation_actions_generation(self):
        """Test mitigation actions generation."""
        risk_factors = [
            {"factor": "active_security_alerts", "score": 0.3, "description": "3 active alerts"},
            {"factor": "compliance_violations", "score": 0.4, "description": "2 violations"}
        ]
        
        actions = self.sentry._generate_mitigation_actions(risk_factors)
        
        self.assertIn("Implement additional security controls", actions)
        self.assertIn("Review access logs for suspicious activity", actions)
        self.assertIn("Update security policies to meet compliance requirements", actions)
        self.assertIn("Conduct compliance training for users", actions)
    
    def test_security_status_reporting(self):
        """Test security status reporting."""
        status = self.sentry.get_security_status()
        
        expected_keys = [
            "persona_id", "monitoring_active", "kill_switch_active",
            "escalation_level", "active_alerts_count", "compliance_checks_count",
            "risk_assessments_count", "last_risk_score"
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        self.assertEqual(status["persona_id"], "test-sentry")
        self.assertTrue(status["monitoring_active"])
        self.assertFalse(status["kill_switch_active"])
        self.assertEqual(status["escalation_level"], 0)
    
    def test_compliance_status_reporting(self):
        """Test compliance status reporting."""
        # Add some test compliance checks
        check1 = ComplianceCheck(
            check_id="check-1",
            framework=ComplianceFramework.GDPR,
            requirement="data_encryption",
            status="pass",
            description="Data encryption enabled",
            timestamp=datetime.now().isoformat()
        )
        
        check2 = ComplianceCheck(
            check_id="check-2",
            framework=ComplianceFramework.GDPR,
            requirement="user_consent",
            status="fail",
            description="User consent missing",
            timestamp=datetime.now().isoformat()
        )
        
        self.sentry.compliance_checks[check1.check_id] = check1
        self.sentry.compliance_checks[check2.check_id] = check2
        
        status = self.sentry.get_compliance_status()
        
        self.assertIn("gdpr", status)
        gdpr_status = status["gdpr"]
        self.assertEqual(gdpr_status["total_checks"], 2)
        self.assertEqual(gdpr_status["passed"], 1)
        self.assertEqual(gdpr_status["failed"], 1)
        self.assertEqual(gdpr_status["warnings"], 0)
    
    def test_audit_log_functionality(self):
        """Test audit log functionality."""
        # Perform some actions that should be logged
        self.sentry._log_override_action("test_action", user_id="user1", details="test")
        self.sentry.acknowledge_alert("test-alert", "user1")
        self.sentry.update_security_policy("test_policy", {}, "user1")
        
        audit_log = self.sentry.get_audit_log()
        
        self.assertGreater(len(audit_log), 0)
        
        # Check that actions are properly logged
        action_types = [entry["action"] for entry in audit_log]
        self.assertIn("test_action", action_types)
        self.assertIn("alert_acknowledged", action_types)
        self.assertIn("policy_updated", action_types)
    
    def test_export_audit_report(self):
        """Test audit report export functionality."""
        # Add some test data
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()
        
        # Add test alerts
        alert = SecurityAlert(
            alert_id="test-alert-1",
            timestamp=datetime.now().isoformat(),
            level=SecurityLevel.HIGH,
            category=RiskCategory.UNAUTHORIZED_ACCESS,
            title="Test Alert",
            description="Test alert description",
            source="test"
        )
        self.sentry.active_alerts[alert.alert_id] = alert
        
        # Add test compliance check
        check = ComplianceCheck(
            check_id="check-1",
            framework=ComplianceFramework.GDPR,
            requirement="data_encryption",
            status="fail",
            description="Data encryption missing",
            timestamp=datetime.now().isoformat()
        )
        self.sentry.compliance_checks[check.check_id] = check
        
        # Export report
        report = self.sentry.export_audit_report(start_date, end_date)
        
        expected_keys = [
            "report_period", "security_events", "override_actions",
            "alerts_generated", "compliance_violations", "risk_assessments"
        ]
        
        for key in expected_keys:
            self.assertIn(key, report)
        
        self.assertEqual(report["alerts_generated"], 1)
        self.assertEqual(report["compliance_violations"], 1)
    
    @patch('asyncio.create_task')
    def test_security_monitoring_startup(self, mock_create_task):
        """Test security monitoring startup."""
        # Reset monitoring state
        self.sentry.monitoring_active = False
        
        # Start monitoring
        self.sentry._start_security_monitoring()
        
        self.assertTrue(self.sentry.monitoring_active)
        # Verify monitoring tasks were created
        self.assertGreater(mock_create_task.call_count, 0)
    
    def test_escalation_level_management(self):
        """Test escalation level management."""
        # Test escalation for critical alert
        alert = SecurityAlert(
            alert_id="test-alert",
            timestamp=datetime.now().isoformat(),
            level=SecurityLevel.CRITICAL,
            category=RiskCategory.SYSTEM_COMPROMISE,
            title="Critical Alert",
            description="Critical system compromise",
            source="test"
        )
        
        asyncio.run(self.sentry._handle_critical_alert(alert))
        self.assertEqual(self.sentry.escalation_level, 3)
        
        # Test escalation for high alert
        alert.level = SecurityLevel.HIGH
        asyncio.run(self.sentry._handle_high_alert(alert))
        self.assertEqual(self.sentry.escalation_level, 3)  # Should remain at highest level
        
        # Test escalation for medium alert
        alert.level = SecurityLevel.MEDIUM
        asyncio.run(self.sentry._handle_medium_alert(alert))
        self.assertEqual(self.sentry.escalation_level, 3)  # Should remain at highest level
    
    def test_override_action_logging(self):
        """Test override action logging with various parameters."""
        # Test basic logging
        self.sentry._log_override_action("test_action")
        
        # Test logging with parameters
        self.sentry._log_override_action("test_action", user_id="user1", alert_id="alert1", reason="test")
        
        audit_log = self.sentry.get_audit_log()
        self.assertEqual(len(audit_log), 2)
        
        # Check first entry
        first_entry = audit_log[0]
        self.assertEqual(first_entry["action"], "test_action")
        self.assertIn("timestamp", first_entry)
        
        # Check second entry
        second_entry = audit_log[1]
        self.assertEqual(second_entry["action"], "test_action")
        self.assertEqual(second_entry["user_id"], "user1")
        self.assertEqual(second_entry["alert_id"], "alert1")
        self.assertEqual(second_entry["reason"], "test")


class TestSentryComplianceFrameworks(unittest.TestCase):
    """Test suite for compliance framework functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.sentry = SentryPersona(persona_id="test-sentry")
    
    async def test_gdpr_compliance_requirements(self):
        """Test GDPR compliance requirements."""
        requirements = await self.sentry._gdpr_requirements()
        
        expected_requirements = [
            "data_encryption", "user_consent", "data_retention", "right_to_forget"
        ]
        
        for req in expected_requirements:
            self.assertIn(req, requirements)
            self.assertIn("status", requirements[req])
            self.assertIn("description", requirements[req])
    
    async def test_hipaa_compliance_requirements(self):
        """Test HIPAA compliance requirements."""
        requirements = await self.sentry._hipaa_requirements()
        
        expected_requirements = [
            "access_controls", "audit_logging", "data_backup", "encryption"
        ]
        
        for req in expected_requirements:
            self.assertIn(req, requirements)
            self.assertIn("status", requirements[req])
            self.assertIn("description", requirements[req])
    
    async def test_soc2_compliance_requirements(self):
        """Test SOC2 compliance requirements."""
        requirements = await self.sentry._soc2_requirements()
        
        expected_requirements = [
            "security", "availability", "processing_integrity", "confidentiality", "privacy"
        ]
        
        for req in expected_requirements:
            self.assertIn(req, requirements)
            self.assertIn("status", requirements[req])
            self.assertIn("description", requirements[req])
    
    async def test_iso27001_compliance_requirements(self):
        """Test ISO27001 compliance requirements."""
        requirements = await self.sentry._iso27001_requirements()
        
        expected_requirements = [
            "information_security_policy", "access_control", "cryptography", "incident_management"
        ]
        
        for req in expected_requirements:
            self.assertIn(req, requirements)
            self.assertIn("status", requirements[req])
            self.assertIn("description", requirements[req])
    
    async def test_pci_dss_compliance_requirements(self):
        """Test PCI DSS compliance requirements."""
        requirements = await self.sentry._pci_dss_requirements()
        
        expected_requirements = [
            "network_security", "cardholder_data", "vulnerability_management", "access_control"
        ]
        
        for req in expected_requirements:
            self.assertIn(req, requirements)
            self.assertIn("status", requirements[req])
            self.assertIn("description", requirements[req])


if __name__ == "__main__":
    # Set up logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2) 