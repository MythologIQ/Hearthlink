"""
SYN003: Browser Preview Integration

Integration module for browser preview with Synapse main interface,
URL whitelisting, and live preview module integration.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class URLWhitelistManager:
    """Manages URL whitelisting for browser preview."""
    
    def __init__(self, whitelist_file: Optional[str] = None):
        self.whitelist_file = whitelist_file or "browser_preview_whitelist.json"
        self.allowed_domains: Set[str] = set()
        self.allowed_patterns: List[str] = []
        self.blocked_domains: Set[str] = set()
        self._load_whitelist()
    
    def _load_whitelist(self):
        """Load whitelist from file."""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    data = json.load(f)
                    self.allowed_domains = set(data.get('allowed_domains', []))
                    self.allowed_patterns = data.get('allowed_patterns', [])
                    self.blocked_domains = set(data.get('blocked_domains', []))
                logger.info(f"Loaded whitelist: {len(self.allowed_domains)} allowed, "
                          f"{len(self.blocked_domains)} blocked domains")
            else:
                self._create_default_whitelist()
        except Exception as e:
            logger.error(f"Failed to load whitelist: {e}")
            self._create_default_whitelist()
    
    def _create_default_whitelist(self):
        """Create default whitelist with safe domains."""
        self.allowed_domains = {
            'docs.python.org',
            'github.com',
            'stackoverflow.com',
            'developer.mozilla.org',
            'w3schools.com',
            'realpython.com',
            'python.org',
            'pypi.org',
            'readthedocs.io'
        }
        self.allowed_patterns = [
            r'^https://docs\.',
            r'^https://developer\.',
            r'^https://www\.',
            r'^https://api\.'
        ]
        self.blocked_domains = {
            'malicious-site.com',
            'phishing-example.com',
            'malware-test.com'
        }
        self._save_whitelist()
    
    def _save_whitelist(self):
        """Save whitelist to file."""
        try:
            data = {
                'allowed_domains': list(self.allowed_domains),
                'allowed_patterns': self.allowed_patterns,
                'blocked_domains': list(self.blocked_domains),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.whitelist_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Whitelist saved successfully")
        except Exception as e:
            logger.error(f"Failed to save whitelist: {e}")
    
    def is_url_allowed(self, url: str) -> bool:
        """Check if URL is allowed based on whitelist."""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains first
            if domain in self.blocked_domains:
                return False
            
            # Check allowed domains
            if domain in self.allowed_domains:
                return True
            
            # Check allowed patterns
            import re
            for pattern in self.allowed_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def add_allowed_domain(self, domain: str):
        """Add domain to allowed list."""
        self.allowed_domains.add(domain.lower())
        self._save_whitelist()
        logger.info(f"Added allowed domain: {domain}")
    
    def remove_allowed_domain(self, domain: str):
        """Remove domain from allowed list."""
        self.allowed_domains.discard(domain.lower())
        self._save_whitelist()
        logger.info(f"Removed allowed domain: {domain}")
    
    def add_blocked_domain(self, domain: str):
        """Add domain to blocked list."""
        self.blocked_domains.add(domain.lower())
        self._save_whitelist()
        logger.info(f"Added blocked domain: {domain}")
    
    def remove_blocked_domain(self, domain: str):
        """Remove domain from blocked list."""
        self.blocked_domains.discard(domain.lower())
        self._save_whitelist()
        logger.info(f"Removed blocked domain: {domain}")


class LivePreviewModule:
    """Live preview module for real-time content updates."""
    
    def __init__(self, browser_preview):
        self.browser_preview = browser_preview
        self.active_previews: Dict[str, Dict] = {}
        self.update_interval = 30  # seconds
        self.max_concurrent_previews = 5
    
    async def start_live_preview(self, session_id: str, url: str, 
                                callback_func=None) -> str:
        """Start live preview for URL."""
        if len(self.active_previews) >= self.max_concurrent_previews:
            raise ValueError("Maximum concurrent previews reached")
        
        preview_id = f"live_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_previews[preview_id] = {
            'session_id': session_id,
            'url': url,
            'callback': callback_func,
            'last_update': datetime.now(),
            'update_count': 0,
            'active': True
        }
        
        # Start background update task
        asyncio.create_task(self._live_preview_task(preview_id))
        
        logger.info(f"Started live preview {preview_id} for {url}")
        return preview_id
    
    async def stop_live_preview(self, preview_id: str):
        """Stop live preview."""
        if preview_id in self.active_previews:
            self.active_previews[preview_id]['active'] = False
            del self.active_previews[preview_id]
            logger.info(f"Stopped live preview {preview_id}")
    
    async def _live_preview_task(self, preview_id: str):
        """Background task for live preview updates."""
        while preview_id in self.active_previews and self.active_previews[preview_id]['active']:
            try:
                preview_info = self.active_previews[preview_id]
                
                # Fetch updated content
                result = await self.browser_preview.preview_url(
                    preview_info['session_id'],
                    preview_info['url']
                )
                
                if result.get('success'):
                    preview_info['last_update'] = datetime.now()
                    preview_info['update_count'] += 1
                    
                    # Call callback if provided
                    if preview_info['callback']:
                        try:
                            preview_info['callback'](result)
                        except Exception as e:
                            logger.error(f"Live preview callback error: {e}")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Live preview task error for {preview_id}: {e}")
                await asyncio.sleep(self.update_interval)
        
        logger.info(f"Live preview task ended for {preview_id}")
    
    def get_active_previews(self) -> List[Dict]:
        """Get list of active previews."""
        return [
            {
                'preview_id': pid,
                'url': info['url'],
                'last_update': info['last_update'].isoformat(),
                'update_count': info['update_count']
            }
            for pid, info in self.active_previews.items()
        ]


class BrowserPreviewIntegration:
    """Main integration class for browser preview with Synapse."""
    
    def __init__(self, synapse_instance=None):
        self.synapse = synapse_instance
        self.whitelist_manager = URLWhitelistManager()
        
        # Import browser preview
        from .browser_preview import BrowserPreview
        self.browser_preview = BrowserPreview()
        self.live_preview = LivePreviewModule(self.browser_preview)
        
        # Agent sessions
        self.agent_sessions: Dict[str, str] = {}
        
        logger.info("Browser preview integration initialized")
    
    async def create_agent_session(self, agent_id: str) -> str:
        """Create browser session for agent."""
        session_id = await self.browser_preview.create_session(agent_id)
        self.agent_sessions[agent_id] = session_id
        logger.info(f"Created browser session for agent {agent_id}: {session_id}")
        return session_id
    
    async def preview_url_for_agent(self, agent_id: str, url: str, 
                                   method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Preview URL for specific agent with whitelist validation."""
        # Check if agent has session
        if agent_id not in self.agent_sessions:
            await self.create_agent_session(agent_id)
        
        session_id = self.agent_sessions[agent_id]
        
        # Validate URL against whitelist
        if not self.whitelist_manager.is_url_allowed(url):
            return {
                "success": False,
                "error": f"URL not in whitelist: {url}",
                "security_violation": True,
                "session_id": session_id
            }
        
        # Preview URL
        result = await self.browser_preview.preview_url(session_id, url, method, data)
        
        # Add whitelist info to result
        result['whitelist_checked'] = True
        result['whitelist_allowed'] = True
        
        return result
    
    async def start_live_preview_for_agent(self, agent_id: str, url: str, 
                                         callback_func=None) -> str:
        """Start live preview for agent."""
        if agent_id not in self.agent_sessions:
            await self.create_agent_session(agent_id)
        
        session_id = self.agent_sessions[agent_id]
        return await self.live_preview.start_live_preview(session_id, url, callback_func)
    
    async def stop_live_preview(self, preview_id: str):
        """Stop live preview."""
        await self.live_preview.stop_live_preview(preview_id)
    
    def get_agent_session_info(self, agent_id: str) -> Optional[Dict]:
        """Get session information for agent."""
        if agent_id not in self.agent_sessions:
            return None
        
        session_id = self.agent_sessions[agent_id]
        return self.browser_preview.get_session_info(session_id)
    
    def get_all_session_info(self) -> Dict[str, Dict]:
        """Get session information for all agents."""
        return {
            agent_id: self.get_agent_session_info(agent_id)
            for agent_id in self.agent_sessions.keys()
        }
    
    def get_whitelist_status(self) -> Dict:
        """Get whitelist status information."""
        return {
            'allowed_domains': list(self.whitelist_manager.allowed_domains),
            'blocked_domains': list(self.whitelist_manager.blocked_domains),
            'allowed_patterns': self.whitelist_manager.allowed_patterns,
            'whitelist_file': self.whitelist_manager.whitelist_file
        }
    
    def add_allowed_domain(self, domain: str):
        """Add domain to whitelist."""
        self.whitelist_manager.add_allowed_domain(domain)
    
    def remove_allowed_domain(self, domain: str):
        """Remove domain from whitelist."""
        self.whitelist_manager.remove_allowed_domain(domain)
    
    def add_blocked_domain(self, domain: str):
        """Add domain to blocked list."""
        self.whitelist_manager.add_blocked_domain(domain)
    
    def remove_blocked_domain(self, domain: str):
        """Remove domain from blocked list."""
        self.whitelist_manager.remove_blocked_domain(domain)
    
    def get_live_previews(self) -> List[Dict]:
        """Get active live previews."""
        return self.live_preview.get_active_previews()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        self.browser_preview.cleanup_expired_sessions()
        
        # Remove expired sessions from agent mapping
        expired_agents = []
        for agent_id, session_id in self.agent_sessions.items():
            session_info = self.browser_preview.get_session_info(session_id)
            if not session_info:
                expired_agents.append(agent_id)
        
        for agent_id in expired_agents:
            del self.agent_sessions[agent_id]
            logger.info(f"Removed expired session for agent {agent_id}")


# Global integration instance
browser_preview_integration = BrowserPreviewIntegration()


async def create_agent_browser_session(agent_id: str) -> str:
    """Create browser session for agent."""
    return await browser_preview_integration.create_agent_session(agent_id)


async def preview_url_for_agent(agent_id: str, url: str, method: str = "GET", 
                               data: Optional[Dict] = None) -> Dict:
    """Preview URL for agent with whitelist validation."""
    return await browser_preview_integration.preview_url_for_agent(agent_id, url, method, data)


async def start_live_preview_for_agent(agent_id: str, url: str, callback_func=None) -> str:
    """Start live preview for agent."""
    return await browser_preview_integration.start_live_preview_for_agent(agent_id, url, callback_func)


async def stop_live_preview(preview_id: str):
    """Stop live preview."""
    await browser_preview_integration.stop_live_preview(preview_id)


def get_agent_session_info(agent_id: str) -> Optional[Dict]:
    """Get session information for agent."""
    return browser_preview_integration.get_agent_session_info(agent_id)


def get_whitelist_status() -> Dict:
    """Get whitelist status."""
    return browser_preview_integration.get_whitelist_status()


def add_allowed_domain(domain: str):
    """Add domain to whitelist."""
    browser_preview_integration.add_allowed_domain(domain)


def remove_allowed_domain(domain: str):
    """Remove domain from whitelist."""
    browser_preview_integration.remove_allowed_domain(domain)


def cleanup_expired_sessions():
    """Clean up expired sessions."""
    browser_preview_integration.cleanup_expired_sessions() 