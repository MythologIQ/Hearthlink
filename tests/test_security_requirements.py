"""
Test suite for Security Requirements (All Modules)

Tests comprehensive security implementation including:
- Sentry hooks for monitoring outbound requests and agent interactions
- Permission/role enforcement for external access
- Rate limiting for outbound API and browsing actions
- Audit logging for all external interactions
"""

import asyncio
import json
import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Import security modules
from src.synapse.security_manager import (
    SecurityManager, SecurityLevel, PermissionType, AgentType,
    SecurityEvent, RateLimitConfig, PermissionConfig, check_synapse_permission
)
from src.synapse.sentry_integration import (
    SentryMonitor, monitor_outbound_request, monitor_agent_interaction,
    monitor_browser_preview, monitor_webhook_config, monitor_credential_access
)
from src.synapse.audit_logger import (
    AuditLogger, AuditEventType, AuditLevel, log_outbound_request,
    log_agent_interaction, log_permission_check, log_security_violation
)


class TestSecurityManager:
    """Test security manager functionality."""
    
    @pytest.fixture
    def security_manager(self):
        """Create security manager for testing."""
        return SecurityManager()
    
    def test_security_level_enum(self):
        """Test security level enumeration."""
        assert SecurityLevel.LOW.value == "low"
        assert SecurityLevel.MEDIUM.value == "medium"
        assert SecurityLevel.HIGH.value == "high"
        assert SecurityLevel.CRITICAL.value == "critical"
    
    def test_permission_type_enum(self):
        """Test permission type enumeration."""
        assert PermissionType.BROWSER_PREVIEW.value == "browser_preview"
        assert PermissionType.WEBHOOK_OUTBOUND.value == "webhook_outbound"
        assert PermissionType.CREDENTIAL_ACCESS.value == "credential_access"
        assert PermissionType.API_EXTERNAL.value == "api_external"
        assert PermissionType.NETWORK_ACCESS.value == "network_access"
        assert PermissionType.FILE_SYSTEM.value == "file_system"
    
    def test_agent_type_enum(self):
        """Test agent type enumeration."""
        assert AgentType.ALDEN.value == "alden"
        assert AgentType.ALICE.value == "alice"
        assert AgentType.MIMIC.value == "mimic"
        assert AgentType.SENTRY.value == "sentry"
        assert AgentType.CORE.value == "core"
        assert AgentType.EXTERNAL.value == "external"
    
    def test_rate_limit_config(self):
        """Test rate limit configuration."""
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            burst_limit=5,
            cooldown_seconds=300
        )
        
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.burst_limit == 5
        assert config.cooldown_seconds == 300
    
    def test_permission_config(self):
        """Test permission configuration."""
        config = PermissionConfig(
            agent_type=AgentType.ALDEN,
            allowed_permissions={PermissionType.BROWSER_PREVIEW, PermissionType.API_EXTERNAL},
            security_level=SecurityLevel.MEDIUM
        )
        
        assert config.agent_type == AgentType.ALDEN
        assert PermissionType.BROWSER_PREVIEW in config.allowed_permissions
        assert PermissionType.API_EXTERNAL in config.allowed_permissions
        assert config.security_level == SecurityLevel.MEDIUM
    
    def test_security_event_creation(self):
        """Test security event creation."""
        event = SecurityEvent(
            event_id="test_event",
            timestamp=datetime.now().isoformat(),
            agent_id="test_agent",
            agent_type=AgentType.ALDEN,
            action="test_action",
            target="test_target",
            permission_required=PermissionType.BROWSER_PREVIEW,
            security_level=SecurityLevel.MEDIUM,
            success=True,
            details={"test": "data"}
        )
        
        assert event.event_id == "test_event"
        assert event.agent_id == "test_agent"
        assert event.agent_type == AgentType.ALDEN
        assert event.action == "test_action"
        assert event.success is True
    
    def test_permission_check_local_agent(self, security_manager):
        """Test permission check for local agent."""
        # Test allowed permission
        result = security_manager.check_permission(
            "test_agent", AgentType.ALDEN, PermissionType.BROWSER_PREVIEW,
            "browser_preview", "https://example.com"
        )
        assert result is True
        
        # Test denied permission
        result = security_manager.check_permission(
            "test_agent", AgentType.ALDEN, PermissionType.FILE_SYSTEM,
            "file_access", "/etc/passwd"
        )
        assert result is False
    
    def test_permission_check_external_agent(self, security_manager):
        """Test permission check for external agent."""
        # Test allowed permission
        result = security_manager.check_permission(
            "external_agent", AgentType.EXTERNAL, PermissionType.BROWSER_PREVIEW,
            "browser_preview", "https://example.com"
        )
        assert result is True
        
        # Test denied permission
        result = security_manager.check_permission(
            "external_agent", AgentType.EXTERNAL, PermissionType.CREDENTIAL_ACCESS,
            "credential_access", "example.com"
        )
        assert result is False
    
    def test_rate_limiting(self, security_manager):
        """Test rate limiting functionality."""
        agent_id = "test_agent"
        permission_type = PermissionType.BROWSER_PREVIEW
        
        # Get rate limit config
        config = security_manager.permission_configs[AgentType.ALDEN].rate_limits[permission_type]
        
        # Test within limits
        for i in range(config.requests_per_minute):
            result = security_manager.check_permission(
                agent_id, AgentType.ALDEN, permission_type,
                "browser_preview", f"https://example{i}.com"
            )
            assert result is True
        
        # Test exceeding limits
        result = security_manager.check_permission(
            agent_id, AgentType.ALDEN, permission_type,
            "browser_preview", "https://example-exceed.com"
        )
        assert result is False
    
    def test_security_summary(self, security_manager):
        """Test security summary generation."""
        # Generate some events
        security_manager.check_permission(
            "test_agent", AgentType.ALDEN, PermissionType.BROWSER_PREVIEW,
            "browser_preview", "https://example.com"
        )
        
        security_manager.check_permission(
            "test_agent", AgentType.ALDEN, PermissionType.API_EXTERNAL,
            "api_call", "https://api.example.com"
        )
        
        summary = security_manager.get_security_summary()
        
        assert "summary" in summary
        assert "agent_activity" in summary
        assert "permission_usage" in summary
        assert "rate_limit_status" in summary
        assert summary["summary"]["total_events"] >= 2


class TestSentryIntegration:
    """Test Sentry integration functionality."""
    
    @pytest.fixture
    def mock_sentry(self):
        """Create mock Sentry instance."""
        return MagicMock()
    
    @pytest.fixture
    def sentry_monitor(self, mock_sentry):
        """Create Sentry monitor with mock Sentry."""
        return SentryMonitor(mock_sentry)
    
    def test_sentry_monitor_initialization(self, sentry_monitor):
        """Test Sentry monitor initialization."""
        assert sentry_monitor.sentry is not None
        assert len(sentry_monitor.monitored_modules) == 0
        assert len(sentry_monitor.alert_callbacks) == 0
    
    def test_register_module(self, sentry_monitor):
        """Test module registration."""
        sentry_monitor.register_module("test_module")
        assert "test_module" in sentry_monitor.monitored_modules
    
    def test_add_alert_callback(self, sentry_monitor):
        """Test alert callback registration."""
        def test_callback(message, level, extra):
            pass
        
        sentry_monitor.add_alert_callback(test_callback)
        assert len(sentry_monitor.alert_callbacks) == 1
    
    def test_monitor_outbound_request(self, sentry_monitor):
        """Test outbound request monitoring."""
        result = sentry_monitor.monitor_outbound_request(
            "test_agent", AgentType.ALDEN,
            "https://example.com", "GET",
            {"User-Agent": "test"}, None, 200, 1.5
        )
        
        assert result is True
        
        # Test with error response
        result = sentry_monitor.monitor_outbound_request(
            "test_agent", AgentType.ALDEN,
            "https://example.com", "POST",
            {}, {"data": "test"}, 500, 2.0
        )
        
        assert result is True
    
    def test_monitor_agent_interaction(self, sentry_monitor):
        """Test agent interaction monitoring."""
        result = sentry_monitor.monitor_agent_interaction(
            "test_agent", AgentType.ALDEN,
            "credential_access", "example.com",
            {"domain": "example.com", "type": "login"}
        )
        
        assert result is True
    
    def test_monitor_browser_preview(self, sentry_monitor):
        """Test browser preview monitoring."""
        result = sentry_monitor.monitor_browser_preview(
            "test_agent", AgentType.ALDEN,
            "https://example.com", 1024, []
        )
        
        assert result is True
        
        # Test with security violations
        result = sentry_monitor.monitor_browser_preview(
            "test_agent", AgentType.ALDEN,
            "https://malicious.com", 2048, ["suspicious_script"]
        )
        
        assert result is True
    
    def test_monitor_webhook_config(self, sentry_monitor):
        """Test webhook configuration monitoring."""
        result = sentry_monitor.monitor_webhook_config(
            "test_agent", AgentType.ALDEN,
            "https://api.example.com/webhook", "POST", True
        )
        
        assert result is True
    
    def test_monitor_credential_access(self, sentry_monitor):
        """Test credential access monitoring."""
        result = sentry_monitor.monitor_credential_access(
            "test_agent", AgentType.ALDEN,
            "example.com", "login", "manual_injection"
        )
        
        assert result is True
    
    def test_determine_permission_type(self, sentry_monitor):
        """Test permission type determination."""
        # Test API URLs
        assert sentry_monitor._determine_permission_type("https://api.example.com", "GET") == PermissionType.API_EXTERNAL
        assert sentry_monitor._determine_permission_type("https://example.com/api/", "POST") == PermissionType.API_EXTERNAL
        
        # Test webhook methods
        assert sentry_monitor._determine_permission_type("https://example.com", "POST") == PermissionType.WEBHOOK_OUTBOUND
        assert sentry_monitor._determine_permission_type("https://example.com", "PUT") == PermissionType.WEBHOOK_OUTBOUND
        
        # Test network access
        assert sentry_monitor._determine_permission_type("https://example.com", "GET") == PermissionType.NETWORK_ACCESS
    
    def test_determine_interaction_permission(self, sentry_monitor):
        """Test interaction permission determination."""
        assert sentry_monitor._determine_interaction_permission("credential_access") == PermissionType.CREDENTIAL_ACCESS
        assert sentry_monitor._determine_interaction_permission("file_system_access") == PermissionType.FILE_SYSTEM
        assert sentry_monitor._determine_interaction_permission("api_call") == PermissionType.API_EXTERNAL
        assert sentry_monitor._determine_interaction_permission("network_request") == PermissionType.NETWORK_ACCESS


class TestAuditLogger:
    """Test audit logger functionality."""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    @pytest.fixture
    def audit_logger(self, temp_log_file):
        """Create audit logger with temporary file."""
        return AuditLogger(temp_log_file)
    
    def test_audit_event_type_enum(self):
        """Test audit event type enumeration."""
        assert AuditEventType.OUTBOUND_REQUEST.value == "outbound_request"
        assert AuditEventType.AGENT_INTERACTION.value == "agent_interaction"
        assert AuditEventType.PERMISSION_CHECK.value == "permission_check"
        assert AuditEventType.RATE_LIMIT.value == "rate_limit"
        assert AuditEventType.SECURITY_VIOLATION.value == "security_violation"
        assert AuditEventType.CREDENTIAL_ACCESS.value == "credential_access"
        assert AuditEventType.WEBHOOK_CONFIG.value == "webhook_config"
        assert AuditEventType.BROWSER_PREVIEW.value == "browser_preview"
        assert AuditEventType.SYSTEM_ACCESS.value == "system_access"
    
    def test_audit_level_enum(self):
        """Test audit level enumeration."""
        assert AuditLevel.INFO.value == "info"
        assert AuditLevel.WARNING.value == "warning"
        assert AuditLevel.ERROR.value == "error"
        assert AuditLevel.CRITICAL.value == "critical"
    
    def test_audit_logger_initialization(self, audit_logger, temp_log_file):
        """Test audit logger initialization."""
        assert audit_logger.log_file == Path(temp_log_file)
        assert audit_logger.log_file.exists()
        assert audit_logger.audit_secret is not None
        assert len(audit_logger.event_counters) == len(AuditEventType)
    
    def test_log_outbound_request(self, audit_logger):
        """Test outbound request logging."""
        event_id = audit_logger.log_outbound_request(
            "test_agent", "alden", "https://example.com", "GET",
            True, 200, 1.5, {"User-Agent": "test"}, 1024, None, "session_123"
        )
        
        assert event_id is not None
        assert len(event_id) > 0
        
        # Test failed request
        event_id = audit_logger.log_outbound_request(
            "test_agent", "alden", "https://example.com", "POST",
            False, 500, 2.0, {}, 2048, "Connection timeout", "session_123"
        )
        
        assert event_id is not None
    
    def test_log_agent_interaction(self, audit_logger):
        """Test agent interaction logging."""
        event_id = audit_logger.log_agent_interaction(
            "test_agent", "alden", "credential_access", "example.com",
            True, {"domain": "example.com", "type": "login"}, "session_123"
        )
        
        assert event_id is not None
        
        # Test failed interaction
        event_id = audit_logger.log_agent_interaction(
            "test_agent", "alden", "system_access", "/etc/passwd",
            False, {"reason": "permission_denied"}, "session_123"
        )
        
        assert event_id is not None
    
    def test_log_permission_check(self, audit_logger):
        """Test permission check logging."""
        event_id = audit_logger.log_permission_check(
            "test_agent", "alden", "browser_preview", "browser_preview",
            "https://example.com", True, "permission_granted", "session_123"
        )
        
        assert event_id is not None
        
        # Test denied permission
        event_id = audit_logger.log_permission_check(
            "test_agent", "alden", "file_system", "file_access",
            "/etc/passwd", False, "permission_denied", "session_123"
        )
        
        assert event_id is not None
    
    def test_log_security_violation(self, audit_logger):
        """Test security violation logging."""
        event_id = audit_logger.log_security_violation(
            "test_agent", "alden", "suspicious_activity", "https://malicious.com",
            {"reason": "suspicious_script", "risk_score": 85}, "session_123"
        )
        
        assert event_id is not None
    
    def test_log_browser_preview(self, audit_logger):
        """Test browser preview logging."""
        event_id = audit_logger.log_browser_preview(
            "test_agent", "alden", "https://example.com", 1024, [], "session_123"
        )
        
        assert event_id is not None
        
        # Test with security violations
        event_id = audit_logger.log_browser_preview(
            "test_agent", "alden", "https://malicious.com", 2048,
            ["suspicious_script", "malicious_content"], "session_123"
        )
        
        assert event_id is not None
    
    def test_log_webhook_config(self, audit_logger):
        """Test webhook configuration logging."""
        event_id = audit_logger.log_webhook_config(
            "test_agent", "alden", "https://api.example.com/webhook",
            "POST", True, True, "session_123"
        )
        
        assert event_id is not None
    
    def test_audit_summary(self, audit_logger):
        """Test audit summary generation."""
        # Generate some events
        audit_logger.log_outbound_request(
            "test_agent", "alden", "https://example.com", "GET",
            True, 200, 1.5, {}, 1024, None, "session_123"
        )
        
        audit_logger.log_agent_interaction(
            "test_agent", "alden", "credential_access", "example.com",
            True, {"domain": "example.com"}, "session_123"
        )
        
        summary = audit_logger.get_audit_summary(hours=1)
        
        assert "summary" in summary
        assert "event_types" in summary
        assert "levels" in summary
        assert "agent_activity" in summary
        assert summary["summary"]["total_events"] >= 2
    
    def test_log_integrity_verification(self, audit_logger):
        """Test log integrity verification."""
        # Generate some events
        audit_logger.log_outbound_request(
            "test_agent", "alden", "https://example.com", "GET",
            True, 200, 1.5, {}, 1024, None, "session_123"
        )
        
        integrity = audit_logger.verify_log_integrity()
        
        assert "total_events" in integrity
        assert "valid_signatures" in integrity
        assert "invalid_signatures" in integrity
        assert "integrity_percentage" in integrity
        assert integrity["total_events"] >= 1
        assert integrity["integrity_percentage"] == 100.0


class TestSecurityIntegration:
    """Test integration between security components."""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    @pytest.fixture
    def mock_sentry(self):
        """Create mock Sentry instance."""
        return MagicMock()
    
    @pytest.fixture
    def security_setup(self, temp_log_file, mock_sentry):
        """Set up security components for testing."""
        security_manager = SecurityManager(mock_sentry, temp_log_file)
        sentry_monitor = SentryMonitor(mock_sentry)
        audit_logger = AuditLogger(temp_log_file)
        
        return security_manager, sentry_monitor, audit_logger
    
    def test_comprehensive_security_flow(self, security_setup):
        """Test comprehensive security flow."""
        security_manager, sentry_monitor, audit_logger = security_setup
        
        # Test outbound request with full security flow
        agent_id = "test_agent"
        agent_type = AgentType.ALDEN
        url = "https://api.example.com"
        method = "GET"
        
        # 1. Check permission
        permission_granted = security_manager.check_permission(
            agent_id, agent_type, PermissionType.API_EXTERNAL,
            "api_request", url
        )
        assert permission_granted is True
        
        # 2. Monitor with Sentry
        sentry_result = sentry_monitor.monitor_outbound_request(
            agent_id, agent_type, url, method,
            {"User-Agent": "test"}, None, 200, 1.5
        )
        assert sentry_result is True
        
        # 3. Log to audit
        audit_id = audit_logger.log_outbound_request(
            agent_id, agent_type.value, url, method,
            True, 200, 1.5, {"User-Agent": "test"}, 1024, None, "session_123"
        )
        assert audit_id is not None
        
        # 4. Verify security summary
        security_summary = security_manager.get_security_summary()
        assert security_summary["summary"]["total_events"] >= 1
        
        # 5. Verify audit summary
        audit_summary = audit_logger.get_audit_summary(hours=1)
        assert audit_summary["summary"]["total_events"] >= 1
    
    def test_security_violation_flow(self, security_setup):
        """Test security violation flow."""
        security_manager, sentry_monitor, audit_logger = security_setup
        
        agent_id = "external_agent"
        agent_type = AgentType.EXTERNAL
        
        # Test denied permission
        permission_granted = security_manager.check_permission(
            agent_id, agent_type, PermissionType.CREDENTIAL_ACCESS,
            "credential_access", "example.com"
        )
        assert permission_granted is False
        
        # Log security violation
        audit_id = audit_logger.log_security_violation(
            agent_id, agent_type.value, "permission_denied", "example.com",
            {"reason": "external_agent_credential_access", "risk_score": 90}, "session_123"
        )
        assert audit_id is not None
        
        # Verify in summaries
        security_summary = security_manager.get_security_summary()
        audit_summary = audit_logger.get_audit_summary(hours=1)
        
        assert security_summary["summary"]["denied_requests"] >= 1
        assert audit_summary["summary"]["failed_events"] >= 1
    
    def test_rate_limit_enforcement(self, security_setup):
        """Test rate limit enforcement."""
        security_manager, sentry_monitor, audit_logger = security_setup
        
        agent_id = "test_agent"
        agent_type = AgentType.ALDEN
        permission_type = PermissionType.BROWSER_PREVIEW
        
        # Get rate limit config
        config = security_manager.permission_configs[agent_type].rate_limits[permission_type]
        
        # Exceed rate limit
        for i in range(config.requests_per_minute + 1):
            result = security_manager.check_permission(
                agent_id, agent_type, permission_type,
                "browser_preview", f"https://example{i}.com"
            )
            
            if i < config.requests_per_minute:
                assert result is True
            else:
                assert result is False
        
        # Verify rate limit status
        rate_status = security_manager.get_rate_limit_status_for_agent(agent_id, permission_type)
        assert rate_status["is_blocked"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 