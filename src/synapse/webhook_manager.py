"""
SYN004: Webhook & API Endpoint Configuration

Secure webhook management with authentication headers, CLI test tool,
outbound request validation, and rate limiting.
"""

import asyncio
import json
import logging
import secrets
import tempfile
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import aiohttp
from aiohttp import ClientSession, ClientTimeout
import time

from .security_monitor import check_webhook_request, check_api_call, get_security_status

logger = logging.getLogger(__name__)


class AuthType(Enum):
    """Authentication types for webhooks."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"


class WebhookStatus(Enum):
    """Webhook status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    webhook_id: str
    name: str
    url: str
    method: str = "POST"
    auth_type: AuthType = AuthType.NONE
    auth_headers: Dict[str, str] = field(default_factory=dict)
    auth_body: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 5
    rate_limit: int = 60  # requests per minute
    status: WebhookStatus = WebhookStatus.INACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    success_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None


@dataclass
class WebhookTestResult:
    """Webhook test result."""
    success: bool
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    headers_sent: Dict[str, str] = field(default_factory=dict)
    headers_received: Dict[str, str] = field(default_factory=dict)


class WebhookManager:
    """Manages webhook configurations and executions."""
    
    def __init__(self, config_file: str = "webhook_configs.json"):
        self.config_file = Path(config_file)
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.rate_limiters: Dict[str, Any] = {}
        self.test_results: Dict[str, List[WebhookTestResult]] = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """Load webhook configurations from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                for webhook_data in data.get('webhooks', []):
                    webhook = WebhookConfig(**webhook_data)
                    webhook.auth_type = AuthType(webhook.auth_type)
                    webhook.status = WebhookStatus(webhook.status)
                    self.webhooks[webhook.webhook_id] = webhook
                    
                logger.info(f"Loaded {len(self.webhooks)} webhook configurations")
        except Exception as e:
            logger.error(f"Failed to load webhook configs: {e}")
    
    def _save_configs(self):
        """Save webhook configurations to file."""
        try:
            data = {
                'webhooks': [asdict(webhook) for webhook in self.webhooks.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info("Webhook configurations saved")
        except Exception as e:
            logger.error(f"Failed to save webhook configs: {e}")
    
    def create_webhook(self, name: str, url: str, method: str = "POST",
                      auth_type: AuthType = AuthType.NONE,
                      auth_headers: Optional[Dict[str, str]] = None,
                      auth_body: Optional[Dict[str, str]] = None) -> str:
        """Create a new webhook configuration."""
        webhook_id = f"webhook_{secrets.token_hex(8)}"
        
        webhook = WebhookConfig(
            webhook_id=webhook_id,
            name=name,
            url=url,
            method=method.upper(),
            auth_type=auth_type,
            auth_headers=auth_headers or {},
            auth_body=auth_body or {}
        )
        
        self.webhooks[webhook_id] = webhook
        self._save_configs()
        
        logger.info(f"Created webhook: {name} ({webhook_id})")
        return webhook_id
    
    def update_webhook(self, webhook_id: str, **kwargs) -> bool:
        """Update webhook configuration."""
        if webhook_id not in self.webhooks:
            return False
        
        webhook = self.webhooks[webhook_id]
        
        # Update allowed fields
        allowed_fields = ['name', 'url', 'method', 'auth_type', 'auth_headers', 
                         'auth_body', 'timeout', 'retry_count', 'retry_delay', 
                         'rate_limit', 'status']
        
        for field_name, value in kwargs.items():
            if field_name in allowed_fields:
                if field_name == 'auth_type' and isinstance(value, str):
                    value = AuthType(value)
                elif field_name == 'status' and isinstance(value, str):
                    value = WebhookStatus(value)
                setattr(webhook, field_name, value)
        
        self._save_configs()
        logger.info(f"Updated webhook: {webhook_id}")
        return True
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook configuration."""
        if webhook_id not in self.webhooks:
            return False
        
        del self.webhooks[webhook_id]
        self._save_configs()
        logger.info(f"Deleted webhook: {webhook_id}")
        return True
    
    def get_webhook(self, webhook_id: str) -> Optional[WebhookConfig]:
        """Get webhook configuration."""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self) -> List[WebhookConfig]:
        """List all webhook configurations."""
        return list(self.webhooks.values())
    
    async def execute_webhook(self, webhook_id: str, agent_id: str, user_id: str,
                             payload: Optional[Dict[str, Any]] = None,
                             custom_headers: Optional[Dict[str, str]] = None) -> WebhookTestResult:
        """Execute webhook with security checks."""
        if webhook_id not in self.webhooks:
            return WebhookTestResult(
                success=False,
                error_message=f"Webhook not found: {webhook_id}"
            )
        
        webhook = self.webhooks[webhook_id]
        
        # Check security permissions
        security_allowed = await check_webhook_request(agent_id, user_id, webhook.url)
        if not security_allowed:
            return WebhookTestResult(
                success=False,
                error_message="Security check failed: rate limit or permission denied"
            )
        
        # Check if webhook is active
        if webhook.status != WebhookStatus.ACTIVE:
            return WebhookTestResult(
                success=False,
                error_message=f"Webhook is not active: {webhook.status.value}"
            )
        
        # Execute webhook
        result = await self._execute_webhook_internal(webhook, payload, custom_headers)
        
        # Update webhook statistics
        webhook.last_used = datetime.now().isoformat()
        if result.success:
            webhook.success_count += 1
        else:
            webhook.error_count += 1
            webhook.last_error = result.error_message
        
        self._save_configs()
        
        return result
    
    async def _execute_webhook_internal(self, webhook: WebhookConfig,
                                       payload: Optional[Dict[str, Any]] = None,
                                       custom_headers: Optional[Dict[str, str]] = None) -> WebhookTestResult:
        """Internal webhook execution."""
        start_time = time.time()
        
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Hearthlink-Webhook/1.0'
            }
            
            # Add authentication headers
            headers.update(webhook.auth_headers)
            
            # Add custom headers
            if custom_headers:
                headers.update(custom_headers)
            
            # Prepare payload
            final_payload = payload or {}
            if webhook.auth_body:
                final_payload.update(webhook.auth_body)
            
            # Execute request with retries
            for attempt in range(webhook.retry_count + 1):
                try:
                    timeout = ClientTimeout(total=webhook.timeout)
                    
                    async with ClientSession(timeout=timeout) as session:
                        if webhook.method == "GET":
                            async with session.get(webhook.url, headers=headers) as response:
                                response_time = time.time() - start_time
                                response_body = await response.text()
                                
                                return WebhookTestResult(
                                    success=response.status < 400,
                                    status_code=response.status,
                                    response_time=response_time,
                                    response_body=response_body,
                                    headers_sent=headers,
                                    headers_received=dict(response.headers)
                                )
                        else:
                            async with session.post(webhook.url, headers=headers, 
                                                  json=final_payload) as response:
                                response_time = time.time() - start_time
                                response_body = await response.text()
                                
                                return WebhookTestResult(
                                    success=response.status < 400,
                                    status_code=response.status,
                                    response_time=response_time,
                                    response_body=response_body,
                                    headers_sent=headers,
                                    headers_received=dict(response.headers)
                                )
                
                except Exception as e:
                    if attempt == webhook.retry_count:
                        return WebhookTestResult(
                            success=False,
                            error_message=f"Request failed after {webhook.retry_count + 1} attempts: {str(e)}"
                        )
                    
                    # Wait before retry
                    await asyncio.sleep(webhook.retry_delay)
        
        except Exception as e:
            return WebhookTestResult(
                success=False,
                error_message=f"Webhook execution error: {str(e)}"
            )
    
    async def test_webhook(self, webhook_id: str, test_payload: Optional[Dict[str, Any]] = None) -> WebhookTestResult:
        """Test webhook configuration."""
        if webhook_id not in self.webhooks:
            return WebhookTestResult(
                success=False,
                error_message=f"Webhook not found: {webhook_id}"
            )
        
        webhook = self.webhooks[webhook_id]
        
        # Temporarily set status to testing
        original_status = webhook.status
        webhook.status = WebhookStatus.TESTING
        
        # Execute test
        result = await self._execute_webhook_internal(webhook, test_payload)
        
        # Restore status
        webhook.status = original_status
        
        # Store test result
        if webhook_id not in self.test_results:
            self.test_results[webhook_id] = []
        
        self.test_results[webhook_id].append(result)
        
        # Keep only last 10 test results
        if len(self.test_results[webhook_id]) > 10:
            self.test_results[webhook_id] = self.test_results[webhook_id][-10:]
        
        return result
    
    def get_test_results(self, webhook_id: str) -> List[WebhookTestResult]:
        """Get test results for webhook."""
        return self.test_results.get(webhook_id, [])
    
    def validate_webhook_config(self, webhook: WebhookConfig) -> List[str]:
        """Validate webhook configuration."""
        errors = []
        
        # Validate URL
        try:
            parsed = urlparse(webhook.url)
            if not parsed.scheme or not parsed.netloc:
                errors.append("Invalid URL format")
        except Exception:
            errors.append("Invalid URL format")
        
        # Validate method
        if webhook.method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            errors.append("Invalid HTTP method")
        
        # Validate timeout
        if webhook.timeout < 1 or webhook.timeout > 300:
            errors.append("Timeout must be between 1 and 300 seconds")
        
        # Validate retry settings
        if webhook.retry_count < 0 or webhook.retry_count > 10:
            errors.append("Retry count must be between 0 and 10")
        
        if webhook.retry_delay < 1 or webhook.retry_delay > 60:
            errors.append("Retry delay must be between 1 and 60 seconds")
        
        # Validate rate limit
        if webhook.rate_limit < 1 or webhook.rate_limit > 1000:
            errors.append("Rate limit must be between 1 and 1000 requests per minute")
        
        return errors


# CLI test tool
class WebhookCLITester:
    """CLI tool for testing webhooks."""
    
    def __init__(self, webhook_manager: WebhookManager):
        self.webhook_manager = webhook_manager
    
    async def test_webhook_cli(self, webhook_id: str, payload_file: Optional[str] = None) -> bool:
        """Test webhook from CLI."""
        print(f"Testing webhook: {webhook_id}")
        
        # Load test payload if provided
        test_payload = None
        if payload_file:
            try:
                with open(payload_file, 'r') as f:
                    test_payload = json.load(f)
                print(f"Loaded test payload from: {payload_file}")
            except Exception as e:
                print(f"Failed to load payload file: {e}")
                return False
        
        # Execute test
        result = await self.webhook_manager.test_webhook(webhook_id, test_payload)
        
        # Display results
        print(f"\nTest Results:")
        print(f"  Success: {result.success}")
        print(f"  Status Code: {result.status_code}")
        print(f"  Response Time: {result.response_time:.3f}s")
        
        if result.error_message:
            print(f"  Error: {result.error_message}")
        
        if result.response_body:
            print(f"  Response Body: {result.response_body[:200]}...")
        
        return result.success
    
    def list_webhooks_cli(self):
        """List webhooks from CLI."""
        webhooks = self.webhook_manager.list_webhooks()
        
        if not webhooks:
            print("No webhooks configured")
            return
        
        print(f"\nConfigured Webhooks ({len(webhooks)}):")
        print("-" * 80)
        
        for webhook in webhooks:
            print(f"ID: {webhook.webhook_id}")
            print(f"Name: {webhook.name}")
            print(f"URL: {webhook.url}")
            print(f"Method: {webhook.method}")
            print(f"Status: {webhook.status.value}")
            print(f"Auth Type: {webhook.auth_type.value}")
            print(f"Success/Error: {webhook.success_count}/{webhook.error_count}")
            print("-" * 80)
    
    def create_webhook_cli(self, name: str, url: str, method: str = "POST",
                          auth_type: str = "none") -> str:
        """Create webhook from CLI."""
        try:
            auth_enum = AuthType(auth_type.lower())
            webhook_id = self.webhook_manager.create_webhook(name, url, method, auth_enum)
            print(f"Created webhook: {webhook_id}")
            return webhook_id
        except Exception as e:
            print(f"Failed to create webhook: {e}")
            return None


# Global webhook manager instance
webhook_manager = WebhookManager()


# Convenience functions
def create_webhook(name: str, url: str, method: str = "POST",
                  auth_type: AuthType = AuthType.NONE) -> str:
    """Create a new webhook."""
    return webhook_manager.create_webhook(name, url, method, auth_type)


async def execute_webhook(webhook_id: str, agent_id: str, user_id: str,
                         payload: Optional[Dict[str, Any]] = None) -> WebhookTestResult:
    """Execute webhook with security checks."""
    return await webhook_manager.execute_webhook(webhook_id, agent_id, user_id, payload)


async def test_webhook(webhook_id: str, payload: Optional[Dict[str, Any]] = None) -> WebhookTestResult:
    """Test webhook configuration."""
    return await webhook_manager.test_webhook(webhook_id, payload)


def list_webhooks() -> List[WebhookConfig]:
    """List all webhooks."""
    return webhook_manager.list_webhooks()


def get_webhook(webhook_id: str) -> Optional[WebhookConfig]:
    """Get webhook configuration."""
    return webhook_manager.get_webhook(webhook_id) 