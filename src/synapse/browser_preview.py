"""
SYN003: Embedded Browser Preview Module

Secure browser preview panel with sandboxed iframe, per-agent session isolation,
and comprehensive security measures to prevent remote code execution and JS injection.
"""

import asyncio
import json
import logging
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
import html5lib

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """Per-agent browser session with isolation and security controls."""
    session_id: str
    agent_id: str
    created_at: datetime
    last_accessed: datetime
    url_history: List[str] = field(default_factory=list)
    blocked_domains: Set[str] = field(default_factory=set)
    security_violations: List[str] = field(default_factory=list)
    max_session_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    max_content_size: int = 10 * 1024 * 1024  # 10MB limit


@dataclass
class SecurityPolicy:
    """Security policy configuration for browser preview."""
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    allowed_protocols: Set[str] = field(default_factory=lambda: {"https", "http"})
    max_redirects: int = 5
    timeout_seconds: int = 30
    content_size_limit: int = 10 * 1024 * 1024  # 10MB
    session_duration_limit: int = 30 * 60  # 30 minutes
    enable_js: bool = False
    enable_cookies: bool = False
    enable_forms: bool = False


class ContentSecurityPolicy:
    """Content Security Policy implementation for browser preview."""
    
    def __init__(self, enable_js: bool = False):
        self.enable_js = enable_js
        self.base_policy = self._build_base_policy()
    
    def _build_base_policy(self) -> str:
        """Build base CSP policy."""
        directives = [
            "default-src 'self' 'unsafe-inline'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "media-src 'self'",
            "object-src 'none'",
            "frame-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        
        if not self.enable_js:
            directives.append("script-src 'none'")
        
        return "; ".join(directives)
    
    def get_policy(self, domain: str) -> str:
        """Get CSP policy for specific domain."""
        # Add domain-specific allowances if needed
        return self.base_policy


class URLValidator:
    """URL validation and security checking."""
    
    def __init__(self, security_policy: SecurityPolicy):
        self.policy = security_policy
        self.suspicious_patterns = [
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
            r"file://",
            r"chrome://",
            r"about:",
            r"moz-extension://",
            r"chrome-extension://"
        ]
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL for security compliance."""
        try:
            parsed = urlparse(url)
            
            # Check protocol
            if parsed.scheme not in self.policy.allowed_protocols:
                return False, f"Protocol {parsed.scheme} not allowed"
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False, f"URL contains suspicious pattern: {pattern}"
            
            # Check domain restrictions
            domain = parsed.netloc.lower()
            if domain in self.policy.blocked_domains:
                return False, f"Domain {domain} is blocked"
            
            if self.policy.allowed_domains and domain not in self.policy.allowed_domains:
                return False, f"Domain {domain} not in whitelist"
            
            return True, "URL validated successfully"
            
        except Exception as e:
            return False, f"URL validation error: {str(e)}"


class ContentSanitizer:
    """Content sanitization for security."""
    
    def __init__(self, enable_js: bool = False):
        self.enable_js = enable_js
        self.dangerous_tags = {
            'script', 'iframe', 'object', 'embed', 'applet', 'form',
            'input', 'textarea', 'select', 'button', 'meta'
        }
        self.dangerous_attributes = {
            'onclick', 'onload', 'onerror', 'onmouseover', 'onfocus',
            'onblur', 'onchange', 'onsubmit', 'onkeydown', 'onkeyup'
        }
    
    def sanitize_html(self, html_content: str, base_url: str) -> str:
        """Sanitize HTML content for secure display."""
        try:
            soup = BeautifulSoup(html_content, 'html5lib')
            
            # Remove dangerous tags
            for tag in soup.find_all(self.dangerous_tags):
                tag.decompose()
            
            # Remove dangerous attributes
            for tag in soup.find_all():
                for attr in list(tag.attrs.keys()):
                    if attr.lower() in self.dangerous_attributes:
                        del tag[attr]
                    elif attr.lower().startswith('on'):
                        del tag[attr]
            
            # Add CSP meta tag
            csp = ContentSecurityPolicy(self.enable_js)
            meta_csp = soup.new_tag('meta')
            meta_csp['http-equiv'] = 'Content-Security-Policy'
            meta_csp['content'] = csp.get_policy(base_url)
            
            if soup.head:
                soup.head.insert(0, meta_csp)
            else:
                head = soup.new_tag('head')
                head.insert(0, meta_csp)
                soup.html.insert(0, head)
            
            # Add sandbox attributes to iframe if present
            for iframe in soup.find_all('iframe'):
                iframe['sandbox'] = 'allow-scripts allow-same-origin'
                iframe['loading'] = 'lazy'
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"HTML sanitization error: {e}")
            return f"<html><body><p>Content sanitization failed: {str(e)}</p></body></html>"


class BrowserPreview:
    """Main browser preview implementation with security controls."""
    
    def __init__(self, security_policy: Optional[SecurityPolicy] = None):
        self.security_policy = security_policy or SecurityPolicy()
        self.url_validator = URLValidator(self.security_policy)
        self.content_sanitizer = ContentSanitizer(self.security_policy.enable_js)
        self.sessions: Dict[str, BrowserSession] = {}
        self.session_timeout = timedelta(minutes=30)
    
    async def create_session(self, agent_id: str) -> str:
        """Create new browser session for agent."""
        session_id = f"browser_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = BrowserSession(
            session_id=session_id,
            agent_id=agent_id,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created browser session {session_id} for agent {agent_id}")
        return session_id
    
    async def preview_url(self, session_id: str, url: str, method: str = "GET", 
                         data: Optional[Dict] = None) -> Dict:
        """Preview URL with security validation and content sanitization."""
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.sessions[session_id]
        session.last_accessed = datetime.now()
        
        # Check session timeout
        if datetime.now() - session.created_at > session.max_session_duration:
            raise ValueError("Session expired")
        
        # Validate URL
        is_valid, validation_msg = self.url_validator.validate_url(url)
        if not is_valid:
            session.security_violations.append(f"URL validation failed: {validation_msg}")
            return {
                "success": False,
                "error": f"URL validation failed: {validation_msg}",
                "security_violation": True
            }
        
        # Add to history
        session.url_history.append(url)
        
        try:
            # Fetch content
            content = await self._fetch_content(url, method, data)
            
            # Sanitize content
            sanitized_content = self.content_sanitizer.sanitize_html(
                content['html'], url
            )
            
            return {
                "success": True,
                "url": url,
                "method": method,
                "content": sanitized_content,
                "content_type": content['content_type'],
                "content_size": len(sanitized_content),
                "security_headers": content.get('security_headers', {}),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            session.security_violations.append(f"Content fetch error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def _fetch_content(self, url: str, method: str, data: Optional[Dict]) -> Dict:
        """Fetch content with security controls."""
        timeout = ClientTimeout(total=self.security_policy.timeout_seconds)
        
        async with ClientSession(timeout=timeout) as session:
            headers = {
                'User-Agent': 'Hearthlink-Browser-Preview/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            if method.upper() == "GET":
                async with session.get(url, headers=headers, allow_redirects=False) as response:
                    return await self._process_response(response, url)
            elif method.upper() == "POST":
                if data:
                    async with session.post(url, headers=headers, json=data, 
                                          allow_redirects=False) as response:
                        return await self._process_response(response, url)
                else:
                    async with session.post(url, headers=headers, 
                                          allow_redirects=False) as response:
                        return await self._process_response(response, url)
            else:
                raise ValueError(f"Unsupported method: {method}")
    
    async def _process_response(self, response, original_url: str) -> Dict:
        """Process HTTP response with security checks."""
        content_type = response.headers.get('content-type', 'text/html')
        
        # Check content size
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > self.security_policy.content_size_limit:
            raise ValueError(f"Content too large: {content_length} bytes")
        
        # Handle redirects
        if response.status in [301, 302, 303, 307, 308]:
            location = response.headers.get('location')
            if location:
                # Validate redirect URL
                is_valid, _ = self.url_validator.validate_url(location)
                if not is_valid:
                    raise ValueError(f"Invalid redirect URL: {location}")
        
        # Read content
        content = await response.text()
        
        # Check content size after reading
        if len(content) > self.security_policy.content_size_limit:
            raise ValueError(f"Content too large: {len(content)} bytes")
        
        # Extract security headers
        security_headers = {
            'x-frame-options': response.headers.get('x-frame-options'),
            'x-content-type-options': response.headers.get('x-content-type-options'),
            'x-xss-protection': response.headers.get('x-xss-protection'),
            'content-security-policy': response.headers.get('content-security-policy')
        }
        
        return {
            'html': content,
            'content_type': content_type,
            'status_code': response.status,
            'security_headers': security_headers
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session.session_id,
            "agent_id": session.agent_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "url_history": session.url_history,
            "security_violations": session.security_violations,
            "session_age_minutes": (datetime.now() - session.created_at).total_seconds() / 60
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.created_at > session.max_session_duration:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
    
    def block_domain(self, session_id: str, domain: str):
        """Block domain for specific session."""
        if session_id in self.sessions:
            self.sessions[session_id].blocked_domains.add(domain)
            logger.info(f"Blocked domain {domain} for session {session_id}")


# Global browser preview instance
browser_preview = BrowserPreview()


async def create_browser_session(agent_id: str) -> str:
    """Create new browser session for agent."""
    return await browser_preview.create_session(agent_id)


async def preview_url(session_id: str, url: str, method: str = "GET", 
                     data: Optional[Dict] = None) -> Dict:
    """Preview URL with security validation."""
    return await browser_preview.preview_url(session_id, url, method, data)


def get_session_info(session_id: str) -> Optional[Dict]:
    """Get session information."""
    return browser_preview.get_session_info(session_id)


def cleanup_expired_sessions():
    """Clean up expired sessions."""
    browser_preview.cleanup_expired_sessions() 