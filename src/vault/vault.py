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
            # Generate and save a new key
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
            with open(self.storage_path, "wb") as f:
                f.write(self._encrypt(json.dumps({"persona": {}, "communal": {}}).encode()))

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