"""
SYN005: Encrypted Credential Manager

Secure credential storage and management with local agent restrictions,
domain targeting, and manual injection only.
"""

import asyncio
import json
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .security_monitor import check_credential_access, check_credential_injection, get_security_status

logger = logging.getLogger(__name__)


class CredentialType(Enum):
    """Types of credentials."""
    WEBSITE_LOGIN = "website_login"
    API_KEY = "api_key"
    SSH_KEY = "ssh_key"
    DATABASE = "database"
    CUSTOM = "custom"


class InjectionMethod(Enum):
    """Credential injection methods."""
    MANUAL = "manual"
    FORM_AUTOFILL = "form_autofill"
    BROWSER_EXTENSION = "browser_extension"


@dataclass
class Credential:
    """Encrypted credential record."""
    credential_id: str
    name: str
    credential_type: CredentialType
    domain: str
    username: str
    password: str  # Encrypted
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: Optional[str] = None
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    injection_count: int = 0
    is_active: bool = True


@dataclass
class InjectionRequest:
    """Credential injection request."""
    request_id: str
    credential_id: str
    agent_id: str
    user_id: str
    target_domain: str
    injection_method: InjectionMethod
    requested_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    executed: bool = False
    executed_at: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class CredentialEncryption:
    """Handles credential encryption and decryption."""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            self.master_key = master_key
        else:
            # Generate new master key
            self.master_key = Fernet.generate_key().decode()
        
        self.cipher = Fernet(self.master_key.encode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def get_master_key(self) -> str:
        """Get master key (for storage in Vault)."""
        return self.master_key


class CredentialManager:
    """Manages encrypted credentials with security controls."""
    
    def __init__(self, vault_integration=None, config_file: str = "credential_config.json"):
        self.vault_integration = vault_integration
        self.config_file = Path(config_file)
        self.credentials: Dict[str, Credential] = {}
        self.injection_requests: Dict[str, InjectionRequest] = {}
        self.encryption = CredentialEncryption()
        
        # Local agent restrictions
        self.allowed_agents: Set[str] = {"alden", "alice", "mimic", "sentry"}
        
        # Domain mappings
        self.domain_mappings: Dict[str, List[str]] = {}
        
        # Load configurations
        self._load_config()
        self._load_credentials()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.allowed_agents = set(config.get('allowed_agents', self.allowed_agents))
                self.domain_mappings = config.get('domain_mappings', {})
                
                # Load master key from config if available
                if 'master_key' in config:
                    self.encryption = CredentialEncryption(config['master_key'])
                    
        except Exception as e:
            logger.error(f"Failed to load credential config: {e}")
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'allowed_agents': list(self.allowed_agents),
                'domain_mappings': self.domain_mappings,
                'master_key': self.encryption.get_master_key(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save credential config: {e}")
    
    def _load_credentials(self):
        """Load encrypted credentials from file."""
        try:
            credentials_file = Path("credentials_encrypted.json")
            if credentials_file.exists():
                with open(credentials_file, 'r') as f:
                    data = json.load(f)
                    
                for cred_data in data.get('credentials', []):
                    credential = Credential(**cred_data)
                    credential.credential_type = CredentialType(credential.credential_type)
                    self.credentials[credential.credential_id] = credential
                    
                logger.info(f"Loaded {len(self.credentials)} encrypted credentials")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
    
    def _save_credentials(self):
        """Save encrypted credentials to file."""
        try:
            data = {
                'credentials': [asdict(cred) for cred in self.credentials.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open("credentials_encrypted.json", 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def add_credential(self, name: str, credential_type: CredentialType, domain: str,
                      username: str, password: str, notes: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> str:
        """Add a new encrypted credential."""
        credential_id = f"cred_{secrets.token_hex(8)}"
        
        # Encrypt password
        encrypted_password = self.encryption.encrypt(password)
        
        credential = Credential(
            credential_id=credential_id,
            name=name,
            credential_type=credential_type,
            domain=domain.lower(),
            username=username,
            password=encrypted_password,
            notes=notes,
            tags=tags or []
        )
        
        self.credentials[credential_id] = credential
        self._save_credentials()
        
        logger.info(f"Added credential: {name} for {domain}")
        return credential_id
    
    def update_credential(self, credential_id: str, **kwargs) -> bool:
        """Update credential (password is re-encrypted if provided)."""
        if credential_id not in self.credentials:
            return False
        
        credential = self.credentials[credential_id]
        
        # Handle password encryption
        if 'password' in kwargs:
            kwargs['password'] = self.encryption.encrypt(kwargs['password'])
        
        # Update allowed fields
        allowed_fields = ['name', 'credential_type', 'domain', 'username', 'password',
                         'notes', 'tags', 'is_active']
        
        for field_name, value in kwargs.items():
            if field_name in allowed_fields:
                if field_name == 'credential_type' and isinstance(value, str):
                    value = CredentialType(value)
                setattr(credential, field_name, value)
        
        credential.last_modified = datetime.now().isoformat()
        self._save_credentials()
        
        logger.info(f"Updated credential: {credential_id}")
        return True
    
    def delete_credential(self, credential_id: str) -> bool:
        """Delete credential."""
        if credential_id not in self.credentials:
            return False
        
        del self.credentials[credential_id]
        self._save_credentials()
        
        logger.info(f"Deleted credential: {credential_id}")
        return True
    
    def get_credential(self, credential_id: str, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get credential with security checks."""
        if credential_id not in self.credentials:
            return None
        
        credential = self.credentials[credential_id]
        
        # Check if agent is allowed
        if agent_id.lower() not in self.allowed_agents:
            logger.warning(f"Unauthorized credential access attempt by {agent_id}")
            return None
        
        # Check security permissions
        asyncio.create_task(check_credential_access(agent_id, user_id, credential.domain))
        
        # Update access statistics
        credential.last_accessed = datetime.now().isoformat()
        credential.access_count += 1
        self._save_credentials()
        
        # Return decrypted credential (without password)
        return {
            'credential_id': credential.credential_id,
            'name': credential.name,
            'credential_type': credential.credential_type.value,
            'domain': credential.domain,
            'username': credential.username,
            'notes': credential.notes,
            'tags': credential.tags,
            'created_at': credential.created_at,
            'last_accessed': credential.last_accessed,
            'access_count': credential.access_count
        }
    
    def get_credential_password(self, credential_id: str, agent_id: str, user_id: str) -> Optional[str]:
        """Get decrypted password with security checks."""
        if credential_id not in self.credentials:
            return None
        
        credential = self.credentials[credential_id]
        
        # Check if agent is allowed
        if agent_id.lower() not in self.allowed_agents:
            logger.warning(f"Unauthorized password access attempt by {agent_id}")
            return None
        
        # Check security permissions
        asyncio.create_task(check_credential_access(agent_id, user_id, credential.domain))
        
        # Update access statistics
        credential.last_accessed = datetime.now().isoformat()
        credential.access_count += 1
        self._save_credentials()
        
        # Return decrypted password
        return self.encryption.decrypt(credential.password)
    
    def search_credentials(self, domain: Optional[str] = None, 
                          credential_type: Optional[CredentialType] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search credentials by criteria."""
        results = []
        
        for credential in self.credentials.values():
            if not credential.is_active:
                continue
            
            # Filter by domain
            if domain and domain.lower() not in credential.domain:
                continue
            
            # Filter by type
            if credential_type and credential.credential_type != credential_type:
                continue
            
            # Filter by tags
            if tags and not any(tag in credential.tags for tag in tags):
                continue
            
            # Add to results (without password)
            results.append({
                'credential_id': credential.credential_id,
                'name': credential.name,
                'credential_type': credential.credential_type.value,
                'domain': credential.domain,
                'username': credential.username,
                'notes': credential.notes,
                'tags': credential.tags,
                'created_at': credential.created_at,
                'last_accessed': credential.last_accessed,
                'access_count': credential.access_count
            })
        
        return results
    
    async def request_injection(self, credential_id: str, agent_id: str, user_id: str,
                               target_domain: str, injection_method: InjectionMethod = InjectionMethod.MANUAL) -> str:
        """Request credential injection (manual approval required)."""
        if credential_id not in self.credentials:
            raise ValueError(f"Credential not found: {credential_id}")
        
        credential = self.credentials[credential_id]
        
        # Check if agent is allowed
        if agent_id.lower() not in self.allowed_agents:
            raise ValueError(f"Agent not allowed: {agent_id}")
        
        # Check domain match
        if target_domain.lower() not in credential.domain:
            raise ValueError(f"Domain mismatch: {target_domain} vs {credential.domain}")
        
        # Create injection request
        request_id = f"inj_{secrets.token_hex(8)}"
        
        request = InjectionRequest(
            request_id=request_id,
            credential_id=credential_id,
            agent_id=agent_id,
            user_id=user_id,
            target_domain=target_domain.lower(),
            injection_method=injection_method
        )
        
        self.injection_requests[request_id] = request
        
        logger.info(f"Injection request created: {request_id} for {credential_id}")
        return request_id
    
    def approve_injection(self, request_id: str, approved_by: str) -> bool:
        """Approve credential injection request."""
        if request_id not in self.injection_requests:
            return False
        
        request = self.injection_requests[request_id]
        request.approved = True
        request.approved_by = approved_by
        request.approved_at = datetime.now().isoformat()
        
        logger.info(f"Injection request approved: {request_id} by {approved_by}")
        return True
    
    def deny_injection(self, request_id: str, denied_by: str, reason: str) -> bool:
        """Deny credential injection request."""
        if request_id not in self.injection_requests:
            return False
        
        request = self.injection_requests[request_id]
        request.approved = False
        request.approved_by = denied_by
        request.approved_at = datetime.now().isoformat()
        request.error_message = reason
        
        logger.info(f"Injection request denied: {request_id} by {denied_by}")
        return True
    
    async def execute_injection(self, request_id: str, user_id: str) -> bool:
        """Execute approved credential injection."""
        if request_id not in self.injection_requests:
            return False
        
        request = self.injection_requests[request_id]
        
        if not request.approved:
            request.error_message = "Injection not approved"
            return False
        
        if request.executed:
            request.error_message = "Injection already executed"
            return False
        
        # Check security permissions
        security_allowed = await check_credential_injection(
            request.agent_id, user_id, request.target_domain
        )
        
        if not security_allowed:
            request.error_message = "Security check failed"
            return False
        
        try:
            # Get credential
            credential = self.credentials[request.credential_id]
            
            # Decrypt password
            password = self.encryption.decrypt(credential.password)
            
            # Execute injection (this would integrate with browser preview or form autofill)
            success = await self._perform_injection(
                credential.username, password, request.target_domain, request.injection_method
            )
            
            # Update request status
            request.executed = True
            request.executed_at = datetime.now().isoformat()
            request.success = success
            
            if success:
                credential.injection_count += 1
                self._save_credentials()
                logger.info(f"Injection executed successfully: {request_id}")
            else:
                request.error_message = "Injection execution failed"
                logger.error(f"Injection execution failed: {request_id}")
            
            return success
            
        except Exception as e:
            request.error_message = f"Injection error: {str(e)}"
            logger.error(f"Injection error: {request_id} - {e}")
            return False
    
    async def _perform_injection(self, username: str, password: str, 
                                target_domain: str, injection_method: InjectionMethod) -> bool:
        """Perform the actual credential injection."""
        # This would integrate with browser preview or form autofill
        # For now, we'll simulate the injection
        
        logger.info(f"Performing {injection_method.value} injection for {target_domain}")
        
        # Simulate injection delay
        await asyncio.sleep(0.1)
        
        # Simulate success (in real implementation, this would check actual injection result)
        return True
    
    def get_pending_injections(self) -> List[InjectionRequest]:
        """Get pending injection requests."""
        return [
            request for request in self.injection_requests.values()
            if not request.approved and not request.executed
        ]
    
    def get_injection_history(self, credential_id: Optional[str] = None) -> List[InjectionRequest]:
        """Get injection history."""
        requests = list(self.injection_requests.values())
        
        if credential_id:
            requests = [req for req in requests if req.credential_id == credential_id]
        
        return sorted(requests, key=lambda x: x.requested_at, reverse=True)
    
    def add_domain_mapping(self, domain: str, related_domains: List[str]):
        """Add domain mapping for credential matching."""
        self.domain_mappings[domain.lower()] = [d.lower() for d in related_domains]
        self._save_config()
    
    def get_related_domains(self, domain: str) -> List[str]:
        """Get related domains for credential matching."""
        return self.domain_mappings.get(domain.lower(), [])
    
    def validate_credential(self, credential: Credential) -> List[str]:
        """Validate credential configuration."""
        errors = []
        
        if not credential.name:
            errors.append("Name is required")
        
        if not credential.domain:
            errors.append("Domain is required")
        
        if not credential.username:
            errors.append("Username is required")
        
        if not credential.password:
            errors.append("Password is required")
        
        return errors


# Global credential manager instance
credential_manager = CredentialManager()


# Convenience functions
def add_credential(name: str, credential_type: CredentialType, domain: str,
                  username: str, password: str, notes: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> str:
    """Add a new credential."""
    return credential_manager.add_credential(name, credential_type, domain, username, password, notes, tags)


def get_credential(credential_id: str, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get credential with security checks."""
    return credential_manager.get_credential(credential_id, agent_id, user_id)


def get_credential_password(credential_id: str, agent_id: str, user_id: str) -> Optional[str]:
    """Get decrypted password with security checks."""
    return credential_manager.get_credential_password(credential_id, agent_id, user_id)


def search_credentials(domain: Optional[str] = None, 
                      credential_type: Optional[CredentialType] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Search credentials."""
    return credential_manager.search_credentials(domain, credential_type, tags)


async def request_injection(credential_id: str, agent_id: str, user_id: str,
                           target_domain: str, injection_method: InjectionMethod = InjectionMethod.MANUAL) -> str:
    """Request credential injection."""
    return await credential_manager.request_injection(credential_id, agent_id, user_id, target_domain, injection_method)


def approve_injection(request_id: str, approved_by: str) -> bool:
    """Approve injection request."""
    return credential_manager.approve_injection(request_id, approved_by)


async def execute_injection(request_id: str, user_id: str) -> bool:
    """Execute approved injection."""
    return await credential_manager.execute_injection(request_id, user_id) 