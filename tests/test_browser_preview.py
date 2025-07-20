"""
Test suite for SYN003: Browser Preview Module

Tests secure browser preview functionality, per-agent session isolation,
URL whitelisting, content sanitization, and security measures.
"""

import asyncio
import json
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Import modules to test
from src.synapse.browser_preview import (
    BrowserPreview, BrowserSession, SecurityPolicy, 
    URLValidator, ContentSanitizer, ContentSecurityPolicy,
    create_browser_session, preview_url, get_session_info
)
from src.synapse.browser_preview_integration import (
    URLWhitelistManager, LivePreviewModule, BrowserPreviewIntegration,
    create_agent_browser_session, preview_url_for_agent, get_whitelist_status
)


class TestSecurityPolicy:
    """Test security policy configuration."""
    
    def test_default_security_policy(self):
        """Test default security policy settings."""
        policy = SecurityPolicy()
        
        assert policy.allowed_protocols == {"https", "http"}
        assert policy.max_redirects == 5
        assert policy.timeout_seconds == 30
        assert policy.content_size_limit == 10 * 1024 * 1024  # 10MB
        assert policy.session_duration_limit == 30 * 60  # 30 minutes
        assert policy.enable_js is False
        assert policy.enable_cookies is False
        assert policy.enable_forms is False
    
    def test_custom_security_policy(self):
        """Test custom security policy configuration."""
        policy = SecurityPolicy(
            allowed_domains={"example.com", "test.org"},
            blocked_domains={"malicious.com"},
            allowed_protocols={"https"},
            max_redirects=3,
            timeout_seconds=15,
            enable_js=True
        )
        
        assert policy.allowed_domains == {"example.com", "test.org"}
        assert policy.blocked_domains == {"malicious.com"}
        assert policy.allowed_protocols == {"https"}
        assert policy.max_redirects == 3
        assert policy.timeout_seconds == 15
        assert policy.enable_js is True


class TestContentSecurityPolicy:
    """Test Content Security Policy implementation."""
    
    def test_base_csp_policy(self):
        """Test base CSP policy generation."""
        csp = ContentSecurityPolicy(enable_js=False)
        policy = csp.base_policy
        
        assert "default-src 'self' 'unsafe-inline'" in policy
        assert "script-src 'none'" in policy
        assert "object-src 'none'" in policy
        assert "frame-src 'none'" in policy
        assert "frame-ancestors 'none'" in policy
    
    def test_csp_with_js_enabled(self):
        """Test CSP policy with JavaScript enabled."""
        csp = ContentSecurityPolicy(enable_js=True)
        policy = csp.base_policy
        
        assert "script-src 'self'" in policy
        assert "script-src 'none'" not in policy
    
    def test_domain_specific_csp(self):
        """Test domain-specific CSP policy."""
        csp = ContentSecurityPolicy(enable_js=False)
        policy = csp.get_policy("example.com")
        
        assert "default-src 'self' 'unsafe-inline'" in policy
        assert "script-src 'none'" in policy


class TestURLValidator:
    """Test URL validation and security checking."""
    
    def test_valid_url_validation(self):
        """Test validation of valid URLs."""
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
    
    def test_invalid_url_validation(self):
        """Test validation of invalid URLs."""
        policy = SecurityPolicy()
        validator = URLValidator(policy)
        
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
    
    def test_domain_restrictions(self):
        """Test domain restriction validation."""
        policy = SecurityPolicy(
            allowed_domains={"example.com", "test.org"},
            blocked_domains={"malicious.com"}
        )
        validator = URLValidator(policy)
        
        # Test allowed domains
        assert validator.validate_url("https://example.com")[0]
        assert validator.validate_url("https://test.org")[0]
        
        # Test blocked domains
        assert not validator.validate_url("https://malicious.com")[0]
        
        # Test non-whitelisted domains
        assert not validator.validate_url("https://unknown.com")[0]


class TestContentSanitizer:
    """Test content sanitization functionality."""
    
    def test_html_sanitization(self):
        """Test HTML content sanitization."""
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
    
    def test_sanitization_with_js_enabled(self):
        """Test sanitization with JavaScript enabled."""
        sanitizer = ContentSanitizer(enable_js=True)
        
        html = "<html><head><script>console.log('test')</script></head><body></body></html>"
        sanitized = sanitizer.sanitize_html(html, "https://example.com")
        
        # Script tags should be preserved but dangerous attributes removed
        assert "<script>" in sanitized
        assert "Content-Security-Policy" in sanitized
        assert "script-src 'self'" in sanitized


class TestBrowserSession:
    """Test browser session management."""
    
    def test_session_creation(self):
        """Test browser session creation."""
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
    
    def test_session_timeout_check(self):
        """Test session timeout checking."""
        session = BrowserSession(
            session_id="test_session",
            agent_id="test_agent",
            created_at=datetime.now() - timedelta(minutes=35),
            last_accessed=datetime.now()
        )
        
        # Session should be expired
        assert datetime.now() - session.created_at > session.max_session_duration


class TestBrowserPreview:
    """Test main browser preview functionality."""
    
    @pytest.fixture
    def browser_preview(self):
        """Create browser preview instance for testing."""
        policy = SecurityPolicy(
            allowed_domains={"example.com", "test.org"},
            enable_js=False
        )
        return BrowserPreview(security_policy=policy)
    
    @pytest.mark.asyncio
    async def test_session_creation(self, browser_preview):
        """Test browser session creation."""
        session_id = await browser_preview.create_session("test_agent")
        
        assert session_id in browser_preview.sessions
        session = browser_preview.sessions[session_id]
        assert session.agent_id == "test_agent"
        assert session.session_id == session_id
    
    @pytest.mark.asyncio
    async def test_url_preview_success(self, browser_preview):
        """Test successful URL preview."""
        session_id = await browser_preview.create_session("test_agent")
        
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
    
    @pytest.mark.asyncio
    async def test_url_preview_validation_failure(self, browser_preview):
        """Test URL preview with validation failure."""
        session_id = await browser_preview.create_session("test_agent")
        
        result = await browser_preview.preview_url(session_id, "javascript:alert('xss')")
        
        assert result["success"] is False
        assert "suspicious" in result["error"]
        assert result["security_violation"] is True
    
    @pytest.mark.asyncio
    async def test_session_timeout(self, browser_preview):
        """Test session timeout handling."""
        session_id = await browser_preview.create_session("test_agent")
        
        # Manually expire the session
        browser_preview.sessions[session_id].created_at = datetime.now() - timedelta(minutes=35)
        
        with pytest.raises(ValueError, match="Session expired"):
            await browser_preview.preview_url(session_id, "https://example.com")
    
    def test_session_info_retrieval(self, browser_preview):
        """Test session information retrieval."""
        # Create a session manually for testing
        session = BrowserSession(
            session_id="test_session",
            agent_id="test_agent",
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        browser_preview.sessions["test_session"] = session
        
        info = browser_preview.get_session_info("test_session")
        
        assert info is not None
        assert info["session_id"] == "test_session"
        assert info["agent_id"] == "test_agent"
    
    def test_cleanup_expired_sessions(self, browser_preview):
        """Test expired session cleanup."""
        # Create expired session
        expired_session = BrowserSession(
            session_id="expired_session",
            agent_id="test_agent",
            created_at=datetime.now() - timedelta(minutes=35),
            last_accessed=datetime.now()
        )
        browser_preview.sessions["expired_session"] = expired_session
        
        # Create valid session
        valid_session = BrowserSession(
            session_id="valid_session",
            agent_id="test_agent",
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        browser_preview.sessions["valid_session"] = valid_session
        
        browser_preview.cleanup_expired_sessions()
        
        assert "expired_session" not in browser_preview.sessions
        assert "valid_session" in browser_preview.sessions


class TestURLWhitelistManager:
    """Test URL whitelist management."""
    
    @pytest.fixture
    def temp_whitelist_file(self):
        """Create temporary whitelist file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                'allowed_domains': ['example.com', 'test.org'],
                'allowed_patterns': [r'^https://docs\.'],
                'blocked_domains': ['malicious.com'],
                'last_updated': datetime.now().isoformat()
            }, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    def test_whitelist_loading(self, temp_whitelist_file):
        """Test whitelist loading from file."""
        manager = URLWhitelistManager(temp_whitelist_file)
        
        assert "example.com" in manager.allowed_domains
        assert "test.org" in manager.allowed_domains
        assert "malicious.com" in manager.blocked_domains
        assert len(manager.allowed_patterns) == 1
    
    def test_default_whitelist_creation(self):
        """Test default whitelist creation."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            manager = URLWhitelistManager(temp_file)
            
            # Check default allowed domains
            assert "docs.python.org" in manager.allowed_domains
            assert "github.com" in manager.allowed_domains
            assert "stackoverflow.com" in manager.allowed_domains
            
            # Check default patterns
            assert len(manager.allowed_patterns) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_url_validation(self, temp_whitelist_file):
        """Test URL validation against whitelist."""
        manager = URLWhitelistManager(temp_whitelist_file)
        
        # Test allowed domains
        assert manager.is_url_allowed("https://example.com")
        assert manager.is_url_allowed("https://test.org/path")
        
        # Test blocked domains
        assert not manager.is_url_allowed("https://malicious.com")
        
        # Test pattern matching
        assert manager.is_url_allowed("https://docs.python.org/3/")
        
        # Test non-whitelisted domains
        assert not manager.is_url_allowed("https://unknown.com")
    
    def test_whitelist_modification(self, temp_whitelist_file):
        """Test whitelist modification."""
        manager = URLWhitelistManager(temp_whitelist_file)
        
        # Add allowed domain
        manager.add_allowed_domain("newdomain.com")
        assert "newdomain.com" in manager.allowed_domains
        assert manager.is_url_allowed("https://newdomain.com")
        
        # Remove allowed domain
        manager.remove_allowed_domain("example.com")
        assert "example.com" not in manager.allowed_domains
        assert not manager.is_url_allowed("https://example.com")
        
        # Add blocked domain
        manager.add_blocked_domain("evil.com")
        assert "evil.com" in manager.blocked_domains
        assert not manager.is_url_allowed("https://evil.com")


class TestLivePreviewModule:
    """Test live preview module functionality."""
    
    @pytest.fixture
    def mock_browser_preview(self):
        """Create mock browser preview for testing."""
        mock_preview = MagicMock()
        mock_preview.preview_url = AsyncMock(return_value={
            "success": True,
            "content": "<html><body>Updated content</body></html>"
        })
        return mock_preview
    
    @pytest.mark.asyncio
    async def test_live_preview_creation(self, mock_browser_preview):
        """Test live preview creation."""
        live_preview = LivePreviewModule(mock_browser_preview)
        
        callback_called = False
        def test_callback(result):
            nonlocal callback_called
            callback_called = True
        
        preview_id = await live_preview.start_live_preview("test_session", "https://example.com", test_callback)
        
        assert preview_id in live_preview.active_previews
        assert live_preview.active_previews[preview_id]['url'] == "https://example.com"
        assert live_preview.active_previews[preview_id]['active'] is True
    
    @pytest.mark.asyncio
    async def test_live_preview_stop(self, mock_browser_preview):
        """Test live preview stopping."""
        live_preview = LivePreviewModule(mock_browser_preview)
        
        preview_id = await live_preview.start_live_preview("test_session", "https://example.com")
        
        await live_preview.stop_live_preview(preview_id)
        
        assert preview_id not in live_preview.active_previews
    
    def test_max_concurrent_previews(self, mock_browser_preview):
        """Test maximum concurrent previews limit."""
        live_preview = LivePreviewModule(mock_browser_preview)
        
        # Fill up to max
        for i in range(live_preview.max_concurrent_previews):
            live_preview.active_previews[f"preview_{i}"] = {
                'session_id': f"session_{i}",
                'url': f"https://example{i}.com",
                'callback': None,
                'last_update': datetime.now(),
                'update_count': 0,
                'active': True
            }
        
        # Try to add one more
        with pytest.raises(ValueError, match="Maximum concurrent previews reached"):
            asyncio.run(live_preview.start_live_preview("test_session", "https://example.com"))


class TestBrowserPreviewIntegration:
    """Test browser preview integration."""
    
    @pytest.fixture
    def integration(self):
        """Create browser preview integration for testing."""
        return BrowserPreviewIntegration()
    
    @pytest.mark.asyncio
    async def test_agent_session_creation(self, integration):
        """Test agent session creation."""
        session_id = await integration.create_agent_session("test_agent")
        
        assert session_id in integration.agent_sessions
        assert integration.agent_sessions["test_agent"] == session_id
    
    @pytest.mark.asyncio
    async def test_url_preview_with_whitelist(self, integration):
        """Test URL preview with whitelist validation."""
        # Add test domain to whitelist
        integration.whitelist_manager.add_allowed_domain("example.com")
        
        session_id = await integration.create_agent_session("test_agent")
        
        with patch.object(integration.browser_preview, 'preview_url') as mock_preview:
            mock_preview.return_value = {
                "success": True,
                "content": "<html><body>Test</body></html>"
            }
            
            result = await integration.preview_url_for_agent("test_agent", "https://example.com")
            
            assert result["success"] is True
            assert result["whitelist_checked"] is True
            assert result["whitelist_allowed"] is True
    
    @pytest.mark.asyncio
    async def test_url_preview_whitelist_rejection(self, integration):
        """Test URL preview rejection due to whitelist."""
        result = await integration.preview_url_for_agent("test_agent", "https://unknown.com")
        
        assert result["success"] is False
        assert "not in whitelist" in result["error"]
        assert result["security_violation"] is True
    
    def test_whitelist_management(self, integration):
        """Test whitelist management through integration."""
        integration.add_allowed_domain("test.com")
        assert "test.com" in integration.whitelist_manager.allowed_domains
        
        integration.remove_allowed_domain("test.com")
        assert "test.com" not in integration.whitelist_manager.allowed_domains
        
        integration.add_blocked_domain("evil.com")
        assert "evil.com" in integration.whitelist_manager.blocked_domains


# Integration tests
class TestBrowserPreviewIntegrationEndToEnd:
    """End-to-end integration tests for browser preview."""
    
    @pytest.mark.asyncio
    async def test_complete_browser_preview_workflow(self):
        """Test complete browser preview workflow."""
        # Create integration
        integration = BrowserPreviewIntegration()
        
        # Add test domain to whitelist
        integration.add_allowed_domain("example.com")
        
        # Create agent session
        session_id = await integration.create_agent_session("test_agent")
        assert session_id is not None
        
        # Preview URL
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
        
        # Get session info
        session_info = integration.get_agent_session_info("test_agent")
        assert session_info is not None
        assert session_info["agent_id"] == "test_agent"
        
        # Get whitelist status
        whitelist_status = integration.get_whitelist_status()
        assert "example.com" in whitelist_status["allowed_domains"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 