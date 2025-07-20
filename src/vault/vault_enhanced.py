import os
import json
import traceback
import fcntl
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import secrets
import threading
from dataclasses import asdict

from .schema import PersonaMemory, CommunalMemory, AuditLogEntry

class VaultError(Exception):
    pass

class VaultValidationError(VaultError):
    pass

class VaultIntegrityError(VaultError):
    pass

class VaultEnhanced:
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self._load_key()
        self._init_storage()
        self.audit_log: List[AuditLogEntry] = []
        self._lock = threading.RLock()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

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
                self.logger.error(f"Vault error: {action} - {error}", extra={"traceback": traceback.format_exc(), "details": details})
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
            key = AESGCM.generate_key(bit_length=256)
            if key_file:
                with open(key_file, "wb") as f:
                    f.write(key)
        self.key = key if isinstance(key, bytes) else base64.urlsafe_b64decode(key)

    def _init_storage(self):
        storage_path = self.config["storage"]["file_path"]
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._create_initial_storage()

    def _create_initial_storage(self):
        initial_data = {
            "persona": {},
            "communal": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "schema_version": self.config["schema_version"],
                "checksum": None
            }
        }
        self._save_all_atomic(initial_data)

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum of data for integrity verification."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _validate_schema(self, data: Dict[str, Any], expected_type: str) -> bool:
        """Validate data against expected schema."""
        if expected_type == "persona":
            required_fields = ["persona_id", "user_id", "data", "created_at", "updated_at", "schema_version"]
        elif expected_type == "communal":
            required_fields = ["memory_id", "data", "created_at", "updated_at", "schema_version"]
        else:
            return False
        
        return all(field in data for field in required_fields)

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

    def _load_all_atomic(self) -> Dict[str, Any]:
        """Load data with file locking and integrity verification."""
        with self._lock:
            try:
                with open(self.storage_path, "rb") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        enc = f.read()
                        dec = self._decrypt(enc)
                        data = json.loads(dec.decode())
                        
                        # Verify integrity
                        stored_checksum = data.get("metadata", {}).get("checksum")
                        if stored_checksum:
                            calculated_checksum = self._calculate_checksum({k: v for k, v in data.items() if k != "metadata"})
                            if stored_checksum != calculated_checksum:
                                raise VaultIntegrityError("Data integrity check failed")
                        
                        return data
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                self._log("load_all", "system", None, "system", None, {}, result="failure", error=e)
                raise VaultError(f"Failed to load Vault storage: {e}")

    def _save_all_atomic(self, data: Dict[str, Any]):
        """Save data atomically with file locking and integrity protection."""
        with self._lock:
            try:
                # Calculate checksum before saving
                data_copy = data.copy()
                if "metadata" not in data_copy:
                    data_copy["metadata"] = {}
                data_copy["metadata"]["checksum"] = self._calculate_checksum({k: v for k, v in data.items() if k != "metadata"})
                data_copy["metadata"]["updated_at"] = datetime.now().isoformat()
                
                # Create backup before writing
                if self.storage_path.exists():
                    backup_path = self.storage_path.with_suffix('.backup')
                    self.storage_path.rename(backup_path)
                
                # Write new data
                enc = self._encrypt(json.dumps(data_copy).encode())
                with open(self.storage_path, "wb") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        f.write(enc)
                        f.flush()
                        os.fsync(f.fileno())  # Ensure data is written to disk
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
                # Remove backup if write was successful
                if backup_path.exists():
                    backup_path.unlink()
                
                # Clear cache
                self._cache.clear()
                
            except Exception as e:
                # Restore backup if available
                backup_path = self.storage_path.with_suffix('.backup')
                if backup_path.exists():
                    backup_path.rename(self.storage_path)
                self._log("save_all", "system", None, "system", None, {}, result="failure", error=e)
                raise VaultError(f"Failed to save Vault storage: {e}")

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if available and not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None

    def _set_cached(self, key: str, data: Dict[str, Any]):
        """Cache data with timestamp."""
        self._cache[key] = (data, datetime.now())

    # Enhanced Persona memory CRUD
    def create_or_update_persona(self, persona_id: str, user_id: str, memory_data: Dict[str, Any]):
        try:
            all_data = self._load_all_atomic()
            persona_memories = all_data["persona"]
            
            if persona_id not in persona_memories:
                persona_mem = PersonaMemory(
                    persona_id=persona_id,
                    user_id=user_id,
                    data=memory_data,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    schema_version=self.config["schema_version"],
                    audit_log=[]
                )
                persona_memories[persona_id] = asdict(persona_mem)
            else:
                # Validate existing data
                if not self._validate_schema(persona_memories[persona_id], "persona"):
                    raise VaultValidationError(f"Invalid schema for persona {persona_id}")
                
                persona_memories[persona_id]["data"] = memory_data
                persona_memories[persona_id]["updated_at"] = datetime.now().isoformat()
            
            self._save_all_atomic(all_data)
            self._log("create_or_update_persona", user_id, persona_id, "persona", None, {"memory_data": memory_data})
        except Exception as e:
            self._log("create_or_update_persona", user_id, persona_id, "persona", None, {"memory_data": memory_data}, result="failure", error=e)
            raise

    def get_persona(self, persona_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            # Check cache first
            cache_key = f"persona:{persona_id}:{user_id}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            all_data = self._load_all_atomic()
            persona_memories = all_data["persona"]
            mem = persona_memories.get(persona_id)
            
            if mem and mem["user_id"] == user_id:
                if not self._validate_schema(mem, "persona"):
                    raise VaultValidationError(f"Invalid schema for persona {persona_id}")
                
                self._set_cached(cache_key, mem)
                self._log("get_persona", user_id, persona_id, "persona", None, {})
                return mem
            
            self._log("get_persona_denied", user_id, persona_id, "persona", None, {}, result="denied")
            return None
        except Exception as e:
            self._log("get_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    def delete_persona(self, persona_id: str, user_id: str):
        try:
            all_data = self._load_all_atomic()
            persona_memories = all_data["persona"]
            mem = persona_memories.get(persona_id)
            
            if mem and mem["user_id"] == user_id:
                del persona_memories[persona_id]
                self._save_all_atomic(all_data)
                
                # Clear cache
                cache_key = f"persona:{persona_id}:{user_id}"
                if cache_key in self._cache:
                    del self._cache[cache_key]
                
                self._log("delete_persona", user_id, persona_id, "persona", None, {})
            else:
                self._log("delete_persona_denied", user_id, persona_id, "persona", None, {}, result="denied")
        except Exception as e:
            self._log("delete_persona", user_id, persona_id, "persona", None, {}, result="failure", error=e)
            raise

    # Enhanced Export/Import with validation
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
            
            # Validate imported data
            if not self._validate_schema(data, "persona"):
                raise VaultValidationError("Invalid persona schema in import data")
            
            # Check schema version compatibility
            imported_version = data.get("schema_version", "1.0.0")
            current_version = self.config["schema_version"]
            if imported_version != current_version:
                self._log("import_persona_schema_mismatch", user_id, persona_id, "persona", None, {
                    "imported_version": imported_version,
                    "current_version": current_version
                })
                # TODO: Implement schema migration logic
            
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

    # Enhanced audit log export with filtering
    def export_audit_log(self, filters: Optional[Dict[str, Any]] = None) -> str:
        try:
            log = [entry.__dict__ for entry in self.audit_log]
            
            # Apply filters if provided
            if filters:
                filtered_log = []
                for entry in log:
                    if all(entry.get(k) == v for k, v in filters.items()):
                        filtered_log.append(entry)
                log = filtered_log
            
            return json.dumps(log, indent=2)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Vault audit log export error: {e}", extra={"traceback": traceback.format_exc()})
            raise

    # Data integrity and recovery methods
    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """Verify data integrity and return status with any issues found."""
        issues = []
        try:
            data = self._load_all_atomic()
            
            # Check persona data integrity
            for persona_id, persona_data in data.get("persona", {}).items():
                if not self._validate_schema(persona_data, "persona"):
                    issues.append(f"Invalid persona schema: {persona_id}")
            
            # Check communal data integrity
            for memory_id, communal_data in data.get("communal", {}).items():
                if not self._validate_schema(communal_data, "communal"):
                    issues.append(f"Invalid communal schema: {memory_id}")
            
            return len(issues) == 0, issues
        except Exception as e:
            issues.append(f"Integrity check failed: {str(e)}")
            return False, issues

    def create_backup(self, backup_path: str) -> bool:
        """Create a backup of the current vault data."""
        try:
            data = self._load_all_atomic()
            backup_data = {
                "backup_created_at": datetime.now().isoformat(),
                "original_checksum": data.get("metadata", {}).get("checksum"),
                "data": data
            }
            
            with open(backup_path, "w") as f:
                json.dump(backup_data, f, indent=2)
            
            self._log("create_backup", "system", None, "system", None, {"backup_path": backup_path})
            return True
        except Exception as e:
            self._log("create_backup", "system", None, "system", None, {"backup_path": backup_path}, result="failure", error=e)
            return False

    def restore_backup(self, backup_path: str) -> bool:
        """Restore vault data from backup."""
        try:
            with open(backup_path, "r") as f:
                backup_data = json.load(f)
            
            data = backup_data["data"]
            self._save_all_atomic(data)
            
            self._log("restore_backup", "system", None, "system", None, {"backup_path": backup_path})
            return True
        except Exception as e:
            self._log("restore_backup", "system", None, "system", None, {"backup_path": backup_path}, result="failure", error=e)
            return False 