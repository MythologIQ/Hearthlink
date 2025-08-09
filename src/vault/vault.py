import os
import json
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

from .schema import PersonaMemory, CommunalMemory, AuditLogEntry

class VaultError(Exception):
    pass

class VaultManager:
    """Production-ready manager class for Vault operations with health checks and connection pooling"""
    
    def __init__(self, config: Dict[str, Any] = None, logger=None):
        import logging
        self.logger = logger or logging.getLogger(__name__)
        self._is_initialized = False
        self._is_healthy = False
        self.vault = None
        
        # Create proper config structure for Vault class
        default_config = {
            "encryption": {
                "key_env_var": "HEARTHLINK_VAULT_KEY",
                "key_file": "hearthlink_data/vault_key.key"
            },
            "storage": {
                "file_path": "hearthlink_data/vault_storage"
            },
            "schema_version": "1.0.0",
            "backup_enabled": True,
            "audit_enabled": True,
            "connection_pool": {
                "max_retries": 3,
                "retry_delay": 0.1,
                "timeout": 30.0
            }
        }
        
        self.config = {**default_config, **(config or {})}
        self._initialize_vault()
    
    def _initialize_vault(self) -> bool:
        """Initialize vault with deterministic order and proper error handling"""
        try:
            # Ensure storage directory exists
            storage_path = Path(self.config["storage"]["file_path"])
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create vault instance
            self.vault = Vault(self.config, self.logger)
            
            # Test basic operations to ensure vault is working
            test_id = f"_vault_health_check_{datetime.now().isoformat()}"
            test_data = {"test": True, "timestamp": datetime.now().isoformat()}
            
            # Test write
            self.vault.create_or_update_communal(test_id, test_data, "system")
            
            # Test read
            retrieved = self.vault.get_communal(test_id, "system")
            if not retrieved or retrieved.get("data", {}).get("test") != True:
                raise VaultError("Health check read failed")
            
            # Clean up test data
            self.vault.delete_communal(test_id, "system")
            
            self._is_initialized = True
            self._is_healthy = True
            self.logger.info("VaultManager initialized successfully with health check passed")
            return True
            
        except Exception as e:
            self._is_initialized = False
            self._is_healthy = False
            self.logger.error(f"VaultManager initialization failed: {e}")
            # Don't raise here - allow system to continue with degraded vault
            return False
    
    def health(self) -> Dict[str, Any]:
        """Check vault health status"""
        return {
            "initialized": self._is_initialized,
            "healthy": self._is_healthy,
            "storage_exists": self.vault and Path(self.config["storage"]["file_path"]).exists(),
            "key_available": self.vault and hasattr(self.vault, 'key') and self.vault.key is not None,
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if vault is ready for operations"""
        return self._is_initialized and self._is_healthy and self.vault is not None
    
    async def store_memory(self, content: Dict[str, Any], path: str, 
                          encrypt: bool = True, metadata: Dict[str, Any] = None) -> bool:
        """Store memory content at specified path with retry logic"""
        if not self.ready():
            self.logger.error("VaultManager not ready for store operation")
            return False
            
        max_retries = self.config.get("connection_pool", {}).get("max_retries", 3)
        retry_delay = self.config.get("connection_pool", {}).get("retry_delay", 0.1)
        
        for attempt in range(max_retries):
            try:
                # Ensure content has proper structure
                store_data = {
                    "content": content,
                    "metadata": metadata or {},
                    "encrypted": encrypt,
                    "stored_at": datetime.now().isoformat()
                }
                
                self.vault.create_or_update_communal(
                    memory_id=path,
                    memory_data=store_data,
                    user_id="system"
                )
                
                self.logger.debug(f"Successfully stored memory at path: {path}")
                return True
                
            except Exception as e:
                self.logger.warning(f"VaultManager store_memory attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error(f"VaultManager store_memory failed after {max_retries} attempts: {e}")
                    self._is_healthy = False
                    return False
        
        return False
    
    async def retrieve_memory(self, path: str, decrypt: bool = True) -> Optional[Dict[str, Any]]:
        """Retrieve memory content from specified path with retry logic"""
        if not self.ready():
            self.logger.error("VaultManager not ready for retrieve operation")
            return None
            
        max_retries = self.config.get("connection_pool", {}).get("max_retries", 3)
        retry_delay = self.config.get("connection_pool", {}).get("retry_delay", 0.1)
        
        for attempt in range(max_retries):
            try:
                result = self.vault.get_communal(
                    memory_id=path,
                    user_id="system"
                )
                
                if result and "data" in result:
                    # Extract the actual content from the stored structure
                    stored_data = result["data"]
                    if isinstance(stored_data, dict) and "content" in stored_data:
                        self.logger.debug(f"Successfully retrieved memory from path: {path}")
                        return stored_data["content"]
                    else:
                        # Handle legacy format
                        return stored_data
                
                self.logger.debug(f"No memory found at path: {path}")
                return None
                
            except Exception as e:
                self.logger.warning(f"VaultManager retrieve_memory attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error(f"VaultManager retrieve_memory failed after {max_retries} attempts: {e}")
                    self._is_healthy = False
                    return None
        
        return None
    
    async def list_memories(self, prefix: str = "") -> List[str]:
        """List all memory paths with optional prefix filter"""
        if not self.ready():
            return []
            
        try:
            all_data = self.vault._load_all()
            communal_memories = all_data.get("communal", {})
            
            if prefix:
                return [path for path in communal_memories.keys() if path.startswith(prefix)]
            else:
                return list(communal_memories.keys())
                
        except Exception as e:
            self.logger.error(f"VaultManager list_memories failed: {e}")
            return []
    
    async def delete_memory(self, path: str) -> bool:
        """Delete memory at specified path"""
        if not self.ready():
            return False
            
        try:
            self.vault.delete_communal(path, "system")
            self.logger.debug(f"Successfully deleted memory at path: {path}")
            return True
        except Exception as e:
            self.logger.error(f"VaultManager delete_memory failed: {e}")
            return False

class Vault:
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self._load_key()
        self._init_storage()
        self.audit_log: List[AuditLogEntry] = []

    def _log(self, action: str, user_id: str, persona_id: Optional[str], memory_type: str, key: Optional[str], details: Dict[str, Any], result: str = "success", error: Optional[Exception] = None):
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            user_id=user_id,
            persona_id=persona_id,
            memory_type=memory_type,
            key=key,
            details=details,
            result=result if not error else f"error: {str(error)}"
        )
        self.audit_log.append(entry)
        if self.logger:
            if error:
                # Use logger.logger.error for HearthlinkLogger compatibility
                if hasattr(self.logger, 'logger'):
                    self.logger.logger.error(f"Vault error: {action} - {error}", extra={"traceback": traceback.format_exc(), "details": details})
                else:
                    self.logger.error(f"Vault error: {action} - {error}", extra={"traceback": traceback.format_exc(), "details": details})
            else:
                # Use logger.logger.info for HearthlinkLogger compatibility
                if hasattr(self.logger, 'logger'):
                    self.logger.logger.info(f"Vault action: {action}", extra={"details": details})
                else:
                    self.logger.info(f"Vault action: {action}", extra={"details": details})

    def _load_key(self):
        key_env = self.config["encryption"].get("key_env_var")
        key_file = self.config["encryption"].get("key_file")
        key = os.environ.get(key_env) if key_env else None
        if not key and key_file and os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read()
        if not key:
            # Generate and save a new key
            key = AESGCM.generate_key(bit_length=256)
            if key_file:
                with open(key_file, "wb") as f:
                    f.write(key)
        self.key = key if isinstance(key, bytes) else base64.urlsafe_b64decode(key)

    def _init_storage(self):
        """Initialize storage with proper error handling and validation"""
        storage_path = self.config["storage"]["file_path"]
        self.storage_path = Path(storage_path)
        
        # Ensure parent directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not self.storage_path.exists():
            try:
                initial_data = {"persona": {}, "communal": {}}
                encrypted_data = self._encrypt(json.dumps(initial_data).encode())
                with open(self.storage_path, "wb") as f:
                    f.write(encrypted_data)
                if self.logger:
                    self.logger.info(f"Initialized new vault storage at {self.storage_path}")
            except Exception as e:
                raise VaultError(f"Failed to initialize storage: {e}")
        else:
            # Validate existing storage file
            try:
                self._load_all()  # Test that we can decrypt and parse the file
                if self.logger:
                    self.logger.info(f"Validated existing vault storage at {self.storage_path}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Existing storage file corrupted, reinitializing: {e}")
                # Backup corrupted file before reinitializing
                backup_path = self.storage_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                try:
                    import shutil
                    shutil.copy2(self.storage_path, backup_path)
                except:
                    pass  # Best effort backup
                
                # Reinitialize storage
                initial_data = {"persona": {}, "communal": {}}
                encrypted_data = self._encrypt(json.dumps(initial_data).encode())
                with open(self.storage_path, "wb") as f:
                    f.write(encrypted_data)

    def _encrypt(self, data: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = secrets.token_bytes(12)
        ct = aesgcm.encrypt(nonce, data, None)
        return nonce + ct

    def _decrypt(self, data: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = data[:12]
        ct = data[12:]
        return aesgcm.decrypt(nonce, ct, None)

    def _load_all(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "rb") as f:
                enc = f.read()
            dec = self._decrypt(enc)
            return json.loads(dec.decode())
        except Exception as e:
            self._log("load_all", "system", None, "system", None, {}, result="failure", error=e)
            raise VaultError(f"Failed to load Vault storage: {e}")

    def _save_all(self, data: Dict[str, Any]):
        try:
            enc = self._encrypt(json.dumps(data).encode())
            with open(self.storage_path, "wb") as f:
                f.write(enc)
        except Exception as e:
            self._log("save_all", "system", None, "system", None, {}, result="failure", error=e)
            raise VaultError(f"Failed to save Vault storage: {e}")

    # Persona memory CRUD
    def create_or_update_persona(self, persona_id: str, user_id: str, memory_data: Dict[str, Any]):
        try:
            all_data = self._load_all()
            persona_memories = all_data["persona"]
            if persona_id not in persona_memories:
                persona_memories[persona_id] = PersonaMemory(
                    persona_id=persona_id,
                    user_id=user_id,
                    data=memory_data,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    schema_version=self.config["schema_version"],
                    audit_log=[]
                ).__dict__
            else:
                persona_memories[persona_id]["data"] = memory_data
                persona_memories[persona_id]["updated_at"] = datetime.now().isoformat()
            self._save_all(all_data)
            self._log("create_or_update_persona", user_id, persona_id, "persona", None, {"memory_data": memory_data})
        except Exception as e:
            self._log("create_or_update_persona", user_id, persona_id, "persona", None, {"memory_data": memory_data}, result="failure", error=e)
            raise

    def get_persona(self, persona_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            all_data = self._load_all()
            persona_memories = all_data["persona"]
            mem = persona_memories.get(persona_id)
            if mem and mem["user_id"] == user_id:
                self._log("get_persona", user_id, persona_id, "persona", None, {})
                return mem
            self._log("get_persona_denied", user_id, persona_id, "persona", None, {}, result="denied")
            return None
        except Exception as e:
            self._log("get_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    def delete_persona(self, persona_id: str, user_id: str):
        try:
            all_data = self._load_all()
            persona_memories = all_data["persona"]
            mem = persona_memories.get(persona_id)
            if mem and mem["user_id"] == user_id:
                del persona_memories[persona_id]
                self._save_all(all_data)
                self._log("delete_persona", user_id, persona_id, "persona", None, {})
            else:
                self._log("delete_persona_denied", user_id, persona_id, "persona", None, {}, result="denied")
        except Exception as e:
            self._log("delete_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    # Communal memory CRUD
    def create_or_update_communal(self, memory_id: str, memory_data: Dict[str, Any], user_id: str):
        try:
            all_data = self._load_all()
            communal_memories = all_data["communal"]
            communal_memories[memory_id] = CommunalMemory(
                memory_id=memory_id,
                data=memory_data,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                schema_version=self.config["schema_version"],
                audit_log=[]
            ).__dict__
            self._save_all(all_data)
            self._log("create_or_update_communal", user_id, None, "communal", memory_id, {"memory_data": memory_data})
        except Exception as e:
            self._log("create_or_update_communal", user_id, None, "communal", memory_id, {"memory_data": memory_data}, result="failure", error=e)
            raise

    def get_communal(self, memory_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            all_data = self._load_all()
            communal_memories = all_data["communal"]
            mem = communal_memories.get(memory_id)
            self._log("get_communal", user_id, None, "communal", memory_id, {})
            return mem
        except Exception as e:
            self._log("get_communal", user_id, None, "communal", memory_id, {}, result="failure", error=e)
            raise

    def delete_communal(self, memory_id: str, user_id: str):
        try:
            all_data = self._load_all()
            communal_memories = all_data["communal"]
            if memory_id in communal_memories:
                del communal_memories[memory_id]
                self._save_all(all_data)
                self._log("delete_communal", user_id, None, "communal", memory_id, {})
            else:
                self._log("delete_communal_denied", user_id, None, "communal", memory_id, {}, result="denied")
        except Exception as e:
            self._log("delete_communal", user_id, None, "communal", memory_id, {}, result="failure", error=e)
            raise

    # Export/Import
    def export_persona(self, persona_id: str, user_id: str) -> Optional[str]:
        try:
            mem = self.get_persona(persona_id, user_id)
            if mem:
                export = json.dumps(mem, indent=2)
                self._log("export_persona", user_id, persona_id, "persona", None, {})
                return export
            return None
        except Exception as e:
            self._log("export_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    def import_persona(self, persona_id: str, user_id: str, import_data: str):
        try:
            data = json.loads(import_data)
            self.create_or_update_persona(persona_id, user_id, data["data"])
            self._log("import_persona", user_id, persona_id, "persona", None, {})
        except Exception as e:
            self._log("import_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    def purge_persona(self, persona_id: str, user_id: str):
        try:
            self.delete_persona(persona_id, user_id)
            self._log("purge_persona", user_id, persona_id, "persona", None, {})
        except Exception as e:
            self._log("purge_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    def export_communal(self, memory_id: str, user_id: str) -> Optional[str]:
        try:
            mem = self.get_communal(memory_id, user_id)
            if mem:
                export = json.dumps(mem, indent=2)
                self._log("export_communal", user_id, None, "communal", memory_id, {})
                return export
            return None
        except Exception as e:
            self._log("export_communal", user_id, None, "communal", memory_id, {}, result="failure", error=e)
            raise

    def import_communal(self, memory_id: str, user_id: str, import_data: str):
        try:
            data = json.loads(import_data)
            self.create_or_update_communal(memory_id, data["data"], user_id)
            self._log("import_communal", user_id, None, "communal", memory_id, {})
        except Exception as e:
            self._log("import_communal", user_id, None, "communal", memory_id, {}, result="failure", error=e)
            raise

    def purge_communal(self, memory_id: str, user_id: str):
        try:
            self.delete_communal(memory_id, user_id)
            self._log("purge_communal", user_id, None, "communal", memory_id, {})
        except Exception as e:
            self._log("purge_communal", user_id, None, "communal", memory_id, {}, result="failure", error=e)
            raise

    # Audit log export
    def export_audit_log(self) -> str:
        try:
            log = [entry.__dict__ for entry in self.audit_log]
            return json.dumps(log, indent=2)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Vault audit log export error: {e}", extra={"traceback": traceback.format_exc()})
            raise 