#!/usr/bin/env python3
"""
Test Suite for Sentry Persona

Comprehensive tests for the Sentry security, compliance, and oversight persona.
Covers risk assessment, event monitoring, overrides, kill switches, and audit logging.

References:
- src/personas/sentry.py: Sentry persona implementation
- docs/hearthlink_system_documentation_master.md: Sentry specification
- docs/PLATINUM_BLOCKERS.md: Ethical safety rails and compliance

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import pytest
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.personas.sentry import (
    SentryPersona, SentryError, RiskAssessmentError, OverrideError, AuditError,
    RiskEvent, OverrideEvent, KillSwitchEvent, RiskThresholds, SentryConfig,
    EventType, OverrideReason, RiskLevel
)
from src.llm.local_llm_client import LocalLLMClient
from src.main import HearthlinkLogger


class TestSentryPersona:
    """Test cases for Sentry persona functionality."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client for testing."""
        mock_client = Mock(spec=LocalLLMClient)
        # Add the generate_response method to the mock
        mock_client.generate_response = Mock(return_value="Test response")
        return mock_client
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        mock_logger = Mock(spec=HearthlinkLogger)
        # Add common logger methods
        mock_logger.info = Mock()
        mock_logger.error = Mock()
        mock_logger.warning = Mock()
        mock_logger.debug = Mock()
        return mock_logger
    
    @pytest.fixture
    def sentry_persona(self, mock_llm_client, mock_logger):
        """Create a Sentry persona instance for testing."""
        with patch('src.personas.sentry.SIEMMonitoring'), \
             patch('src.personas.sentry.RBACABACSecurity'), \
             patch('src.personas.sentry.AdvancedMonitoring'):
            
            sentry = SentryPersona(mock_llm_client, mock_logger)
            return sentry
    
    def test_sentry_initialization(self, mock_llm_client, mock_logger):
        """Test Sentry persona initialization."""
        with patch('src.personas.sentry.SIEMMonitoring'), \
             patch('src.personas.sentry.RBACABACSecurity'), \
             patch('src.personas.sentry.AdvancedMonitoring'):
            
            sentry = SentryPersona(mock_llm_client, mock_logger)
            
            assert sentry.llm_client == mock_llm_client
            assert sentry.logger == mock_logger
            assert sentry.memory.persona_id == "sentry"
            assert isinstance(sentry.memory.config, SentryConfig)
            assert len(sentry.risk_rules) == 10  # All event types covered
            assert mock_logger.info.called
    
    def test_sentry_initialization_without_logger(self, mock_llm_client):
        """Test Sentry initialization without logger."""
        with patch('src.personas.sentry.SIEMMonitoring'), \
             patch('src.personas.sentry.RBACABACSecurity'), \
             patch('src.personas.sentry.AdvancedMonitoring'), \
             patch('src.personas.sentry.HearthlinkLogger') as mock_logger_class:
            
            mock_logger_instance = Mock()
            mock_logger_instance.info = Mock()
            mock_logger_instance.error = Mock()
            mock_logger_instance.warning = Mock()
            mock_logger_instance.debug = Mock()
            mock_logger_class.return_value = mock_logger_instance
            
            sentry = SentryPersona(mock_llm_client)
            
            assert sentry.logger == mock_logger_instance
            mock_logger_class.assert_called_once()
    
    def test_sentry_initialization_error(self, mock_logger):
        """Test Sentry initialization with invalid LLM client."""
        with pytest.raises(SentryError, match="LLM client must be an instance of LocalLLMClient"):
            SentryPersona("invalid_client", mock_logger)
    
    def test_monitor_plugin_permission_escalation(self, sentry_persona):
        """Test monitoring plugin permission escalation event."""
        details = {
            "plugin_id": "test-plugin",
            "permission_level": "admin",
            "requested_permissions": ["read", "write", "execute"]
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.PLUGIN_PERMISSION_ESCALATION
        assert risk_event.origin == "test-origin"
        assert risk_event.risk_score > 70  # Should be high risk
        assert risk_event.recommended_action in ["block", "warn"]
        assert risk_event.metadata == details
        assert len(sentry_persona.memory.risk_events) == 1
        assert sentry_persona.memory.total_events_processed == 1
    
    def test_monitor_suspicious_access(self, sentry_persona):
        """Test monitoring suspicious access event."""
        details = {
            "access_count": 15,
            "time_window": 180,  # 3 minutes
            "failed_attempts": 5
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.SUSPICIOUS_ACCESS,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.SUSPICIOUS_ACCESS
        assert risk_event.risk_score > 60  # Should be medium-high risk
        assert risk_event.recommended_action in ["block", "warn"]
    
    def test_monitor_data_access_anomaly(self, sentry_persona):
        """Test monitoring data access anomaly event."""
        details = {
            "data_sensitivity": "high",
            "access_pattern": "bulk_export",
            "unusual_time": True
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.DATA_ACCESS_ANOMALY,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.DATA_ACCESS_ANOMALY
        assert risk_event.risk_score > 50  # Should be medium-high risk
        assert risk_event.recommended_action in ["block", "warn"]
    
    def test_monitor_network_anomaly(self, sentry_persona):
        """Test monitoring network anomaly event."""
        details = {
            "external_connection": True,
            "data_volume": 2000000,  # 2MB
            "encrypted": False
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.NETWORK_ANOMALY,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.NETWORK_ANOMALY
        assert risk_event.risk_score > 65  # Should be high risk
        assert risk_event.recommended_action in ["block", "warn"]
    
    def test_monitor_compliance_violation(self, sentry_persona):
        """Test monitoring compliance violation event."""
        details = {
            "violation_type": "data_breach"
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.COMPLIANCE_VIOLATION,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.COMPLIANCE_VIOLATION
        assert risk_event.risk_score >= 95  # Should be critical risk
        assert risk_event.recommended_action == "block"
    
    def test_monitor_unauthorized_connection(self, sentry_persona):
        """Test monitoring unauthorized connection event."""
        details = {
            "external_domain": "suspicious.com",
            "unencrypted": True
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.UNAUTHORIZED_CONNECTION,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.UNAUTHORIZED_CONNECTION
        assert risk_event.risk_score >= 85  # Should be very high risk
        assert risk_event.recommended_action in ["block", "warn"]
    
    def test_monitor_privilege_escalation(self, sentry_persona):
        """Test monitoring privilege escalation event."""
        details = {
            "target_role": "admin",
            "escalation_method": "exploit"
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.PRIVILEGE_ESCALATION,
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.PRIVILEGE_ESCALATION
        assert risk_event.risk_score == 100  # Should be maximum risk
        assert risk_event.recommended_action == "block"
    
    def test_monitor_generic_event(self, sentry_persona):
        """Test monitoring generic event type."""
        details = {"test": "data"}
        
        risk_event = sentry_persona.monitor_event(
            EventType.MANIFEST_CHANGE,  # Use any event type
            "test-origin",
            details
        )
        
        assert risk_event.event_type == EventType.MANIFEST_CHANGE
        assert risk_event.risk_score >= 0
        assert risk_event.risk_score <= 100
        assert risk_event.recommended_action in ["block", "warn"]
    
    def test_auto_block_high_risk_event(self, sentry_persona):
        """Test automatic blocking of high-risk events."""
        # Set auto-block threshold to 80
        sentry_persona.memory.config.risk_thresholds.auto_block_threshold = 80
        
        details = {
            "violation_type": "data_breach"  # This should trigger 95+ risk score
        }
        
        risk_event = sentry_persona.monitor_event(
            EventType.COMPLIANCE_VIOLATION,
            "test-origin",
            details
        )
        
        assert risk_event.recommended_action == "block"
        assert len(risk_event.audit_log) > 0
        assert any(log["action"] == "auto_blocked" for log in risk_event.audit_log)
    
    def test_override_event_success(self, sentry_persona):
        """Test successful event override."""
        # Create a risk event first
        risk_event = sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            {"plugin_id": "test-plugin"}
        )
        
        # Override the event
        override = sentry_persona.override_event(
            risk_event.event_id,
            "test-user",
            OverrideReason.BUSINESS_NEED,
            "Testing override functionality"
        )
        
        assert override.event_id == risk_event.event_id
        assert override.user_id == "test-user"
        assert override.reason == OverrideReason.BUSINESS_NEED
        assert override.explanation == "Testing override functionality"
        assert risk_event.user_override is True
        assert risk_event.resolution is not None
        assert len(sentry_persona.memory.override_events) == 1
        assert sentry_persona.memory.total_overrides == 1
    
    def test_override_nonexistent_event(self, sentry_persona):
        """Test override of non-existent event."""
        with pytest.raises(OverrideError, match="Risk event.*not found"):
            sentry_persona.override_event(
                "nonexistent-event-id",
                "test-user",
                OverrideReason.BUSINESS_NEED,
                "Test override"
            )
    
    def test_escalation_triggering(self, sentry_persona):
        """Test escalation triggering for excessive overrides."""
        # Set escalation threshold to 2
        sentry_persona.memory.config.risk_thresholds.escalation_threshold = 2
        
        # Create a risk event
        risk_event = sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            {"plugin_id": "test-plugin"}
        )
        
        # Override twice (should trigger escalation)
        for i in range(2):
            sentry_persona.override_event(
                risk_event.event_id,
                "test-user",
                OverrideReason.BUSINESS_NEED,
                f"Override {i+1}"
            )
        
        # Check if escalation was triggered
        assert "test-user" in sentry_persona.escalation_tracker
        assert sentry_persona.escalation_tracker["test-user"] > 0
        
        # Check if escalation event was created
        escalation_events = [
            event for event in sentry_persona.memory.risk_events
            if event.event_type == EventType.COMPLIANCE_VIOLATION and
            "escalation" in event.event_id
        ]
        assert len(escalation_events) > 0
    
    def test_activate_kill_switch(self, sentry_persona):
        """Test kill switch activation."""
        kill_event = sentry_persona.activate_kill_switch(
            "test-target",
            "plugin",
            "Security threat detected",
            "test-user"
        )
        
        assert kill_event.target_id == "test-target"
        assert kill_event.target_type == "plugin"
        assert kill_event.reason == "Security threat detected"
        assert kill_event.user_id == "test-user"
        assert "rollback_steps" in kill_event.impact_report
        assert len(sentry_persona.memory.kill_switch_events) == 1
        assert sentry_persona.memory.total_kill_switches == 1
    
    def test_kill_switch_impact_report(self, sentry_persona):
        """Test kill switch impact report generation."""
        # Test plugin kill switch
        plugin_kill = sentry_persona.activate_kill_switch(
            "test-plugin",
            "plugin",
            "Test reason",
            "test-user"
        )
        assert "Restore plugin from backup" in plugin_kill.impact_report["rollback_steps"]
        
        # Test agent kill switch
        agent_kill = sentry_persona.activate_kill_switch(
            "test-agent",
            "agent",
            "Test reason",
            "test-user"
        )
        assert "Restart agent process" in agent_kill.impact_report["rollback_steps"]
        
        # Test connection kill switch
        connection_kill = sentry_persona.activate_kill_switch(
            "test-connection",
            "connection",
            "Test reason",
            "test-user"
        )
        assert "Re-establish connection" in connection_kill.impact_report["rollback_steps"]
    
    def test_get_risk_dashboard(self, sentry_persona):
        """Test risk dashboard data retrieval."""
        # Create some test events
        for i in range(3):
            sentry_persona.monitor_event(
                EventType.PLUGIN_PERMISSION_ESCALATION,
                f"test-origin-{i}",
                {"plugin_id": f"test-plugin-{i}"}
            )
        
        # Override one event
        risk_event = sentry_persona.memory.risk_events[0]
        sentry_persona.override_event(
            risk_event.event_id,
            "test-user",
            OverrideReason.BUSINESS_NEED,
            "Test override"
        )
        
        # Activate a kill switch
        sentry_persona.activate_kill_switch(
            "test-target",
            "plugin",
            "Test reason",
            "test-user"
        )
        
        # Get dashboard data
        dashboard = sentry_persona.get_risk_dashboard()
        
        assert "current_risk_score" in dashboard
        assert "risk_thresholds" in dashboard
        assert "recent_events" in dashboard
        assert "active_overrides" in dashboard
        assert "recent_kills" in dashboard
        assert "escalation_status" in dashboard
        assert "statistics" in dashboard
        
        assert dashboard["statistics"]["total_events"] == 3
        assert dashboard["statistics"]["total_overrides"] == 1
        assert dashboard["statistics"]["total_kills"] == 1
        assert len(dashboard["recent_events"]) >= 3
        assert len(dashboard["active_overrides"]) >= 1
        assert len(dashboard["recent_kills"]) >= 1
    
    def test_export_audit_log(self, sentry_persona):
        """Test audit log export functionality."""
        # Create some test events
        for i in range(2):
            sentry_persona.monitor_event(
                EventType.PLUGIN_PERMISSION_ESCALATION,
                f"test-origin-{i}",
                {"plugin_id": f"test-plugin-{i}"}
            )
        
        # Override an event
        risk_event = sentry_persona.memory.risk_events[0]
        sentry_persona.override_event(
            risk_event.event_id,
            "test-user",
            OverrideReason.BUSINESS_NEED,
            "Test override"
        )
        
        # Activate a kill switch
        sentry_persona.activate_kill_switch(
            "test-target",
            "plugin",
            "Test reason",
            "test-user"
        )
        
        # Export audit log
        audit_log = sentry_persona.export_audit_log()
        
        assert "export_timestamp" in audit_log
        assert "date_range" in audit_log
        assert "risk_events" in audit_log
        assert "override_events" in audit_log
        assert "kill_switch_events" in audit_log
        assert "summary" in audit_log
        
        assert len(audit_log["risk_events"]) >= 2
        assert len(audit_log["override_events"]) >= 1
        assert len(audit_log["kill_switch_events"]) >= 1
        assert audit_log["summary"]["total_events"] >= 2
        assert audit_log["summary"]["total_overrides"] >= 1
        assert audit_log["summary"]["total_kills"] >= 1
    
    def test_export_audit_log_with_date_range(self, sentry_persona):
        """Test audit log export with specific date range."""
        # Create an event
        sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            {"plugin_id": "test-plugin"}
        )
        
        # Export with date range
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        audit_log = sentry_persona.export_audit_log(start_date, end_date)
        
        assert audit_log["date_range"]["start"] == start_date
        assert audit_log["date_range"]["end"] == end_date
        assert len(audit_log["risk_events"]) >= 1
    
    def test_update_config(self, sentry_persona):
        """Test configuration updates."""
        # Update risk thresholds
        config_updates = {
            "risk_thresholds": {
                "low_threshold": 20,
                "medium_threshold": 50,
                "high_threshold": 75,
                "critical_threshold": 95
            },
            "auto_block_enabled": False
        }
        
        sentry_persona.update_config(config_updates)
        
        assert sentry_persona.memory.config.risk_thresholds.low_threshold == 20
        assert sentry_persona.memory.config.risk_thresholds.medium_threshold == 50
        assert sentry_persona.memory.config.risk_thresholds.high_threshold == 75
        assert sentry_persona.memory.config.risk_thresholds.critical_threshold == 95
        assert sentry_persona.memory.config.auto_block_enabled is False
    
    def test_get_status(self, sentry_persona):
        """Test status information retrieval."""
        status = sentry_persona.get_status()
        
        assert status["persona_id"] == "sentry"
        assert status["status"] == "active"
        assert "current_risk_score" in status
        assert "config" in status
        assert "statistics" in status
        assert "last_updated" in status
        
        assert status["statistics"]["total_events_processed"] == 0
        assert status["statistics"]["total_overrides"] == 0
        assert status["statistics"]["total_kill_switches"] == 0
        assert status["statistics"]["active_escalations"] == 0
    
    def test_whitelist_blacklist_handling(self, sentry_persona):
        """Test whitelist and blacklist handling in risk assessment."""
        # Add to whitelist
        sentry_persona.memory.config.whitelist.add("trusted-plugin")
        
        # Add to blacklist
        sentry_persona.memory.config.blacklist.add("malicious-plugin")
        
        # Test whitelisted plugin
        whitelist_event = sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            {"plugin_id": "trusted-plugin"}
        )
        assert whitelist_event.risk_score <= 50  # Should be lower risk
        
        # Test blacklisted plugin
        blacklist_event = sentry_persona.monitor_event(
            EventType.PLUGIN_PERMISSION_ESCALATION,
            "test-origin",
            {"plugin_id": "malicious-plugin"}
        )
        assert blacklist_event.risk_score >= 90  # Should be very high risk
    
    def test_risk_score_calculation(self, sentry_persona):
        """Test risk score calculation and updates."""
        # Create multiple events
        for i in range(5):
            sentry_persona.monitor_event(
                EventType.PLUGIN_PERMISSION_ESCALATION,
                f"test-origin-{i}",
                {"plugin_id": f"test-plugin-{i}"}
            )
        
        # Check that risk score is calculated
        assert sentry_persona.memory.current_risk_score > 0
        assert sentry_persona.memory.current_risk_score <= 100
    
    def test_error_handling(self, sentry_persona):
        """Test error handling in various operations."""
        # Test monitoring with invalid data
        with pytest.raises(RiskAssessmentError):
            sentry_persona.monitor_event(
                EventType.PLUGIN_PERMISSION_ESCALATION,
                "test-origin",
                None  # Invalid details
            )
        
        # Test override with invalid event ID
        with pytest.raises(OverrideError):
            sentry_persona.override_event(
                "invalid-event-id",
                "test-user",
                OverrideReason.BUSINESS_NEED,
                "Test override"
            )
        
        # Test audit export with invalid date format
        with pytest.raises(AuditError):
            sentry_persona.export_audit_log("invalid-date", "invalid-date")


class TestSentryIntegration:
    """Integration tests for Sentry with other components."""
    
    @pytest.fixture
    def mock_enterprise_components(self):
        """Mock enterprise security components."""
        with patch('src.personas.sentry.SIEMMonitoring') as mock_siem, \
             patch('src.personas.sentry.RBACABACSecurity') as mock_rbac, \
             patch('src.personas.sentry.AdvancedMonitoring') as mock_monitoring:
            
            yield {
                'siem': mock_siem.return_value,
                'rbac': mock_rbac.return_value,
                'monitoring': mock_monitoring.return_value
            }
    
    def test_sentry_siem_integration(self, mock_llm_client, mock_logger, mock_enterprise_components):
        """Test Sentry integration with SIEM monitoring."""
        sentry = SentryPersona(mock_llm_client, mock_logger)
        
        # Verify SIEM is initialized
        assert sentry.siem is not None
        mock_enterprise_components['siem'].__init__.assert_called_once()
    
    def test_sentry_rbac_integration(self, mock_llm_client, mock_logger, mock_enterprise_components):
        """Test Sentry integration with RBAC/ABAC security."""
        sentry = SentryPersona(mock_llm_client, mock_logger)
        
        # Verify RBAC/ABAC is initialized
        assert sentry.rbac_abac is not None
        mock_enterprise_components['rbac'].__init__.assert_called_once()
    
    def test_sentry_monitoring_integration(self, mock_llm_client, mock_logger, mock_enterprise_components):
        """Test Sentry integration with advanced monitoring."""
        sentry = SentryPersona(mock_llm_client, mock_logger)
        
        # Verify monitoring is initialized
        assert sentry.monitoring is not None
        mock_enterprise_components['monitoring'].__init__.assert_called_once()


class TestSentryFactory:
    """Tests for Sentry persona factory function."""
    
    def test_create_sentry_persona_success(self, mock_logger):
        """Test successful Sentry persona creation."""
        llm_config = {
            "model": "test-model",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        with patch('src.personas.sentry.LocalLLMClient') as mock_llm_class, \
             patch('src.personas.sentry.SentryPersona') as mock_sentry_class:
            
            mock_llm_instance = Mock()
            mock_llm_class.return_value = mock_llm_instance
            
            mock_sentry_instance = Mock()
            mock_sentry_class.return_value = mock_sentry_instance
            
            from src.personas.sentry import create_sentry_persona
            sentry = create_sentry_persona(llm_config, mock_logger)
            
            mock_llm_class.assert_called_once_with(llm_config)
            mock_sentry_class.assert_called_once_with(mock_llm_instance, mock_logger)
            assert sentry == mock_sentry_instance
    
    def test_create_sentry_persona_error(self, mock_logger):
        """Test Sentry persona creation with error."""
        llm_config = {"invalid": "config"}
        
        with patch('src.personas.sentry.LocalLLMClient', side_effect=Exception("LLM error")):
            from src.personas.sentry import create_sentry_persona
            
            with pytest.raises(SentryError, match="Failed to create Sentry persona"):
                create_sentry_persona(llm_config, mock_logger)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 