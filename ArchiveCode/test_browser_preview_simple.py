"""
Simple test for SYN003: Browser Preview Module

Tests core browser preview functionality without importing the full Synapse module.
"""

import asyncio
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Import only the browser preview modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from synapse.browser_preview import (
    BrowserPreview, BrowserSession, SecurityPolicy, 
    URLValidator, ContentSanitizer, ContentSecurityPolicy
)
from synapse.browser_preview_integration import (
    URLWhitelistManager, LivePreviewModule, BrowserPreviewIntegration
)


def test_security_policy():
    """Test security policy configuration."""
    print("Testing SecurityPolicy...")
    
    policy = SecurityPolicy()
    
    assert policy.allowed_protocols == {"https", "http"}
    assert policy.max_redirects == 5
    assert policy.timeout_seconds == 30
    assert policy.content_size_limit == 10 * 1024 * 1024  # 10MB
    assert policy.session_duration_limit == 30 * 60  # 30 minutes
    assert policy.enable_js is False
    assert policy.enable_cookies is False
    assert policy.enable_forms is False
    
    print("✅ SecurityPolicy tests passed")


def test_content_security_policy():
    """Test Content Security Policy implementation."""
    print("Testing ContentSecurityPolicy...")
    
    csp = ContentSecurityPolicy(enable_js=False)
    policy = csp.base_policy
    
    assert "default-src 'self' 'unsafe-inline'" in policy
    assert "script-src 'none'" in policy
    assert "object-src 'none'" in policy
    assert "frame-src 'none'" in policy
    assert "frame-ancestors 'none'" in policy
    
    csp_js = ContentSecurityPolicy(enable_js=True)
    policy_js = csp_js.base_policy
    
    assert "script-src 'self'" in policy_js
    assert "script-src 'none'" not in policy_js
    
    print("✅ ContentSecurityPolicy tests passed")


def test_url_validator():
    """Test URL validation and security checking."""
    print("Testing URLValidator...")
    
    policy = SecurityPolicy()
    validator = URLValidator(policy)
    
    # Test valid URLs
    valid_urls = [
        "https://example.com",
        "http://test.org/path",
        "https://docs.python.org/3/",
        "https://api.github.com/users"
    ]
    
    for url in valid_urls:
        is_valid, msg = validator.validate_url(url)
        assert is_valid, f"URL should be valid: {url}, got: {msg}"
    
    # Test invalid URLs
    invalid_urls = [
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>",
        "file:///etc/passwd",
        "chrome://settings",
        "about:blank",
        "ftp://example.com"
    ]
    
    for url in invalid_urls:
        is_valid, msg = validator.validate_url(url)
        assert not is_valid, f"URL should be invalid: {url}"
        assert "not allowed" in msg or "suspicious" in msg
    
    print("✅ URLValidator tests passed")


def test_content_sanitizer():
    """Test content sanitization functionality."""
    print("Testing ContentSanitizer...")
    
    sanitizer = ContentSanitizer(enable_js=False)
    
    malicious_html = """
    <html>
    <head><script>alert('xss')</script></head>
    <body>
        <iframe src="javascript:alert('xss')"></iframe>
        <img src="x" onerror="alert('xss')">
        <form action="javascript:alert('xss')">
            <input type="text" onchange="alert('xss')">
        </form>
    </body>
    </html>
    """
    
    sanitized = sanitizer.sanitize_html(malicious_html, "https://example.com")
    
    # Check that dangerous elements are removed
    assert "<script>" not in sanitized
    assert "onerror=" not in sanitized
    assert "onchange=" not in sanitized
    assert "javascript:" not in sanitized
    
    # Check that CSP meta tag is added
    assert "Content-Security-Policy" in sanitized
    assert "script-src 'none'" in sanitized
    
    print("✅ ContentSanitizer tests passed")


def test_browser_session():
    """Test browser session management."""
    print("Testing BrowserSession...")
    
    session = BrowserSession(
        session_id="test_session",
        agent_id="test_agent",
        created_at=datetime.now(),
        last_accessed=datetime.now()
    )
    
    assert session.session_id == "test_session"
    assert session.agent_id == "test_agent"
    assert len(session.url_history) == 0
    assert len(session.security_violations) == 0
    assert session.max_session_duration == timedelta(minutes=30)
    assert session.max_content_size == 10 * 1024 * 1024  # 10MB
    
    # Test session timeout
    expired_session = BrowserSession(
        session_id="expired_session",
        agent_id="test_agent",
        created_at=datetime.now() - timedelta(minutes=35),
        last_accessed=datetime.now()
    )
    
    # Session should be expired
    assert datetime.now() - expired_session.created_at > expired_session.max_session_duration
    
    print("✅ BrowserSession tests passed")


def test_url_whitelist_manager():
    """Test URL whitelist management."""
    print("Testing URLWhitelistManager...")
    
    # Create temporary whitelist file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'allowed_domains': ['example.com', 'test.org'],
            'allowed_patterns': [r'^https://docs\.'],
            'blocked_domains': ['malicious.com'],
            'last_updated': datetime.now().isoformat()
        }, f)
        temp_file = f.name
    
    try:
        manager = URLWhitelistManager(temp_file)
        
        assert "example.com" in manager.allowed_domains
        assert "test.org" in manager.allowed_domains
        assert "malicious.com" in manager.blocked_domains
        assert len(manager.allowed_patterns) == 1
        
        # Test URL validation
        assert manager.is_url_allowed("https://example.com")
        assert manager.is_url_allowed("https://test.org/path")
        assert not manager.is_url_allowed("https://malicious.com")
        assert manager.is_url_allowed("https://docs.python.org/3/")
        assert not manager.is_url_allowed("https://unknown.com")
        
        # Test whitelist modification
        manager.add_allowed_domain("newdomain.com")
        assert "newdomain.com" in manager.allowed_domains
        assert manager.is_url_allowed("https://newdomain.com")
        
        manager.remove_allowed_domain("example.com")
        assert "example.com" not in manager.allowed_domains
        assert not manager.is_url_allowed("https://example.com")
        
    finally:
        os.unlink(temp_file)
    
    print("✅ URLWhitelistManager tests passed")


async def test_browser_preview():
    """Test main browser preview functionality."""
    print("Testing BrowserPreview...")
    
    policy = SecurityPolicy(
        allowed_domains={"example.com", "test.org"},
        enable_js=False
    )
    browser_preview = BrowserPreview(security_policy=policy)
    
    # Test session creation
    session_id = await browser_preview.create_session("test_agent")
    
    assert session_id in browser_preview.sessions
    session = browser_preview.sessions[session_id]
    assert session.agent_id == "test_agent"
    assert session.session_id == session_id
    
    # Test URL preview with mock
    with patch('aiohttp.ClientSession') as mock_session:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {
            'content-type': 'text/html',
            'content-length': '1000'
        }
        mock_response.text = AsyncMock(return_value="<html><body>Test content</body></html>")
        
        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.__aexit__.return_value = None
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = await browser_preview.preview_url(session_id, "https://example.com")
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert "Test content" in result["content"]
    
    # Test URL validation failure
    result = await browser_preview.preview_url(session_id, "javascript:alert('xss')")
    
    assert result["success"] is False
    assert "suspicious" in result["error"]
    assert result["security_violation"] is True
    
    print("✅ BrowserPreview tests passed")


async def test_browser_preview_integration():
    """Test browser preview integration."""
    print("Testing BrowserPreviewIntegration...")
    
    integration = BrowserPreviewIntegration()
    
    # Add test domain to whitelist
    integration.whitelist_manager.add_allowed_domain("example.com")
    
    # Create agent session
    session_id = await integration.create_agent_session("test_agent")
    assert session_id is not None
    
    # Test URL preview with whitelist
    with patch.object(integration.browser_preview, 'preview_url') as mock_preview:
        mock_preview.return_value = {
            "success": True,
            "content": "<html><body>Test content</body></html>",
            "content_type": "text/html",
            "content_size": 1000
        }
        
        result = await integration.preview_url_for_agent("test_agent", "https://example.com")
        
        assert result["success"] is True
        assert result["whitelist_checked"] is True
        assert result["whitelist_allowed"] is True
    
    # Test URL preview whitelist rejection
    result = await integration.preview_url_for_agent("test_agent", "https://unknown.com")
    
    assert result["success"] is False
    assert "not in whitelist" in result["error"]
    assert result["security_violation"] is True
    
    print("✅ BrowserPreviewIntegration tests passed")


async def main():
    """Run all tests."""
    print("🧪 Running SYN003 Browser Preview Tests...\n")
    
    # Run synchronous tests
    test_security_policy()
    test_content_security_policy()
    test_url_validator()
    test_content_sanitizer()
    test_browser_session()
    test_url_whitelist_manager()
    
    # Run asynchronous tests
    await test_browser_preview()
    await test_browser_preview_integration()
    
    print("\n🎉 All SYN003 Browser Preview tests passed!")


if __name__ == "__main__":
    asyncio.run(main()) 