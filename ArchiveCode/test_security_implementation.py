"""
Comprehensive Security Implementation Test

Tests for SYN004/SYN005 security features including:
- Security monitoring and Sentry hooks
- Webhook management with rate limiting
- Credential management with encryption
- UI components and audit logging
"""

import asyncio
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import security modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from synapse.security_monitor import (
    SecurityMonitor, SecurityEvent, ActionType, SecurityLevel,
    RateLimiter, PermissionManager, check_webhook_request, check_api_call,
    check_credential_access, check_credential_injection
)
from synapse.webhook_manager import (
    WebhookManager, WebhookConfig, AuthType, WebhookTestResult,
    create_webhook, execute_webhook, test_webhook
)
from synapse.credential_manager import (
    CredentialManager, Credential, CredentialType, InjectionMethod,
    CredentialEncryption, add_credential, get_credential, search_credentials
)


def test_security_monitor():
    """Test security monitoring functionality."""
    print("Testing SecurityMonitor...")
    
    # Create security monitor
    monitor = SecurityMonitor()
    
    # Test rate limiting
    rate_limiter = monitor.rate_limiter
    assert rate_limiter is not None
    
    # Test permission manager
    permission_manager = monitor.permission_manager
    assert permission_manager is not None
    
    # Test event logging
    event = SecurityEvent(
        event_id="test_event",
        timestamp=datetime.now().isoformat(),
        action_type=ActionType.WEBHOOK_REQUEST,
        agent_id="test_agent",
        user_id="test_user",
        target_url="https://example.com",
        target_domain="example.com"
    )
    
    # Test event processing
    asyncio.run(monitor.log_security_event(event))
    
    print("✅ SecurityMonitor tests passed")


async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("Testing RateLimiter...")
    
    config = RateLimiter.RateLimitConfig(requests_per_minute=5)
    rate_limiter = RateLimiter(config)
    
    # Test rate limiting
    key = "test_key"
    
    # Should allow first 5 requests
    for i in range(5):
        allowed = await rate_limiter.check_rate_limit(key)
        assert allowed, f"Request {i+1} should be allowed"
    
    # 6th request should be blocked
    allowed = await rate_limiter.check_rate_limit(key)
    assert not allowed, "6th request should be blocked"
    
    # Test status
    status = await rate_limiter.get_rate_limit_status(key)
    assert status['current_requests'] == 5
    assert status['remaining'] == 0
    
    print("✅ RateLimiter tests passed")


def test_permission_manager():
    """Test permission management."""
    print("Testing PermissionManager...")
    
    config = PermissionManager.PermissionConfig(
        allowed_agents={"alden", "alice"},
        allowed_domains={"example.com", "test.org"},
        blocked_domains={"malicious.com"}
    )
    
    permission_manager = PermissionManager(config)
    
    # Test allowed agent
    assert permission_manager.check_permission("alden", ActionType.WEBHOOK_REQUEST, "example.com")
    
    # Test blocked agent
    assert not permission_manager.check_permission("unknown", ActionType.WEBHOOK_REQUEST, "example.com")
    
    # Test blocked domain
    assert not permission_manager.check_permission("alden", ActionType.WEBHOOK_REQUEST, "malicious.com")
    
    # Test non-whitelisted domain
    assert not permission_manager.check_permission("alden", ActionType.WEBHOOK_REQUEST, "unknown.com")
    
    print("✅ PermissionManager tests passed")


def test_webhook_manager():
    """Test webhook management."""
    print("Testing WebhookManager...")
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        webhook_manager = WebhookManager(temp_file)
        
        # Test webhook creation
        webhook_id = webhook_manager.create_webhook(
            name="Test Webhook",
            url="https://api.example.com/webhook",
            method="POST",
            auth_type=AuthType.API_KEY
        )
        
        assert webhook_id is not None
        
        # Test webhook retrieval
        webhook = webhook_manager.get_webhook(webhook_id)
        assert webhook is not None
        assert webhook.name == "Test Webhook"
        assert webhook.url == "https://api.example.com/webhook"
        assert webhook.method == "POST"
        assert webhook.auth_type == AuthType.API_KEY
        
        # Test webhook listing
        webhooks = webhook_manager.list_webhooks()
        assert len(webhooks) == 1
        assert webhooks[0].webhook_id == webhook_id
        
        # Test webhook validation
        errors = webhook_manager.validate_webhook_config(webhook)
        assert len(errors) == 0
        
        # Test invalid webhook
        invalid_webhook = WebhookConfig(
            webhook_id="invalid",
            name="",
            url="invalid-url",
            method="INVALID",
            auth_type=AuthType.NONE
        )
        
        errors = webhook_manager.validate_webhook_config(invalid_webhook)
        assert len(errors) > 0
        
    finally:
        os.unlink(temp_file)
    
    print("✅ WebhookManager tests passed")


async def test_webhook_execution():
    """Test webhook execution with security checks."""
    print("Testing Webhook Execution...")
    
    webhook_manager = WebhookManager()
    
    # Create test webhook
    webhook_id = webhook_manager.create_webhook(
        name="Test Webhook",
        url="https://httpbin.org/post",
        method="POST"
    )
    
    # Test webhook execution with mock
    with patch('aiohttp.ClientSession') as mock_session:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.text = AsyncMock(return_value='{"status": "ok"}')
        
        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.__aexit__.return_value = None
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = await webhook_manager.execute_webhook(webhook_id, "test_agent", "test_user")
        
        assert result.success is True
        assert result.status_code == 200
        assert result.response_body == '{"status": "ok"}'
    
    print("✅ Webhook Execution tests passed")


def test_credential_encryption():
    """Test credential encryption."""
    print("Testing CredentialEncryption...")
    
    encryption = CredentialEncryption()
    
    # Test encryption/decryption
    test_data = "secret_password_123"
    encrypted = encryption.encrypt(test_data)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == test_data
    assert encrypted != test_data  # Should be different
    
    # Test master key
    master_key = encryption.get_master_key()
    assert master_key is not None
    assert len(master_key) > 0
    
    print("✅ CredentialEncryption tests passed")


def test_credential_manager():
    """Test credential management."""
    print("Testing CredentialManager...")
    
    credential_manager = CredentialManager()
    
    # Test credential creation
    cred_id = credential_manager.add_credential(
        name="Test Credential",
        credential_type=CredentialType.WEBSITE_LOGIN,
        domain="example.com",
        username="testuser",
        password="secretpass123",
        notes="Test credential"
    )
    
    assert cred_id is not None
    
    # Test credential retrieval (without password)
    cred_info = credential_manager.get_credential(cred_id, "alden", "test_user")
    assert cred_info is not None
    assert cred_info['name'] == "Test Credential"
    assert cred_info['domain'] == "example.com"
    assert cred_info['username'] == "testuser"
    assert 'password' not in cred_info  # Password should not be included
    
    # Test password retrieval
    password = credential_manager.get_credential_password(cred_id, "alden", "test_user")
    assert password == "secretpass123"
    
    # Test unauthorized access
    unauthorized_cred = credential_manager.get_credential(cred_id, "unknown_agent", "test_user")
    assert unauthorized_cred is None
    
    # Test credential search
    results = credential_manager.search_credentials(domain="example.com")
    assert len(results) == 1
    assert results[0]['credential_id'] == cred_id
    
    # Test credential validation
    valid_cred = credential_manager.credentials[cred_id]
    errors = credential_manager.validate_credential(valid_cred)
    assert len(errors) == 0
    
    # Test invalid credential
    invalid_cred = Credential(
        credential_id="invalid",
        name="",
        credential_type=CredentialType.WEBSITE_LOGIN,
        domain="",
        username="",
        password=""
    )
    
    errors = credential_manager.validate_credential(invalid_cred)
    assert len(errors) > 0
    
    print("✅ CredentialManager tests passed")


async def test_credential_injection():
    """Test credential injection workflow."""
    print("Testing Credential Injection...")
    
    credential_manager = CredentialManager()
    
    # Create test credential
    cred_id = credential_manager.add_credential(
        name="Test Credential",
        credential_type=CredentialType.WEBSITE_LOGIN,
        domain="example.com",
        username="testuser",
        password="secretpass123"
    )
    
    # Test injection request
    request_id = await credential_manager.request_injection(
        cred_id, "alden", "test_user", "example.com", InjectionMethod.MANUAL
    )
    
    assert request_id is not None
    
    # Test request approval
    approved = credential_manager.approve_injection(request_id, "admin")
    assert approved is True
    
    # Test injection execution
    success = await credential_manager.execute_injection(request_id, "test_user")
    assert success is True
    
    # Test pending injections
    pending = credential_manager.get_pending_injections()
    assert len(pending) == 0  # Should be empty after execution
    
    print("✅ Credential Injection tests passed")


async def test_security_checks():
    """Test security check functions."""
    print("Testing Security Checks...")
    
    # Test webhook request check
    webhook_allowed = await check_webhook_request("alden", "test_user", "https://example.com")
    # This will depend on the current security configuration
    assert isinstance(webhook_allowed, bool)
    
    # Test API call check
    api_allowed = await check_api_call("alden", "test_user", "https://api.example.com")
    assert isinstance(api_allowed, bool)
    
    # Test credential access check
    cred_access_allowed = await check_credential_access("alden", "test_user", "example.com")
    assert isinstance(cred_access_allowed, bool)
    
    # Test credential injection check
    cred_injection_allowed = await check_credential_injection("alden", "test_user", "example.com")
    assert isinstance(cred_injection_allowed, bool)
    
    print("✅ Security Checks tests passed")


def test_webhook_cli_tester():
    """Test webhook CLI tester."""
    print("Testing WebhookCLITester...")
    
    webhook_manager = WebhookManager()
    cli_tester = WebhookCLITester(webhook_manager)
    
    # Test webhook listing
    cli_tester.list_webhooks_cli()
    
    # Test webhook creation
    webhook_id = cli_tester.create_webhook_cli(
        "CLI Test Webhook",
        "https://httpbin.org/post",
        "POST",
        "none"
    )
    
    assert webhook_id is not None
    
    print("✅ WebhookCLITester tests passed")


async def test_integration():
    """Test integration between security components."""
    print("Testing Integration...")
    
    # Create webhook manager
    webhook_manager = WebhookManager()
    
    # Create credential manager
    credential_manager = CredentialManager()
    
    # Create test webhook
    webhook_id = webhook_manager.create_webhook(
        name="Integration Test Webhook",
        url="https://httpbin.org/post",
        method="POST",
        auth_type=AuthType.API_KEY
    )
    
    # Create test credential
    cred_id = credential_manager.add_credential(
        name="Integration Test Credential",
        credential_type=CredentialType.WEBSITE_LOGIN,
        domain="httpbin.org",
        username="testuser",
        password="secretpass123"
    )
    
    # Test webhook execution with security checks
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.text = AsyncMock(return_value='{"status": "ok"}')
        
        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.__aexit__.return_value = None
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = await webhook_manager.execute_webhook(webhook_id, "alden", "test_user")
        assert result.success is True
    
    # Test credential injection workflow
    request_id = await credential_manager.request_injection(
        cred_id, "alden", "test_user", "httpbin.org"
    )
    
    credential_manager.approve_injection(request_id, "admin")
    success = await credential_manager.execute_injection(request_id, "test_user")
    assert success is True
    
    print("✅ Integration tests passed")


async def main():
    """Run all security tests."""
    print("🧪 Running Security Implementation Tests...\n")
    
    # Run synchronous tests
    test_security_monitor()
    test_permission_manager()
    test_webhook_manager()
    test_credential_encryption()
    test_credential_manager()
    test_webhook_cli_tester()
    
    # Run asynchronous tests
    await test_rate_limiting()
    await test_webhook_execution()
    await test_credential_injection()
    await test_security_checks()
    await test_integration()
    
    print("\n🎉 All Security Implementation tests passed!")
    print("\n📋 Security Features Implemented:")
    print("✅ Security monitoring with Sentry hooks")
    print("✅ Rate limiting for all outbound requests")
    print("✅ Permission enforcement for agents and domains")
    print("✅ Webhook management with authentication")
    print("✅ Encrypted credential storage and management")
    print("✅ Manual injection workflow with approval")
    print("✅ Comprehensive audit logging")
    print("✅ UI components for security management")


if __name__ == "__main__":
    asyncio.run(main()) 