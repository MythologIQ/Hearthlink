import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.vault.vault import Vault, VaultError
from src.vault.schema import PersonaMemory, CommunalMemory

# Dummy logger for test output
class DummyLogger:
    def info(self, msg, extra=None):
        print(f"[INFO] {msg} {extra if extra else ''}")
    def error(self, msg, extra=None):
        print(f"[ERROR] {msg} {extra if extra else ''}")

def get_test_config(tmpdir):
    return {
        "encryption": {
            "algorithm": "AES-256",
            "key_file": str(tmpdir / "vault.key"),
            "key_env_var": None
        },
        "storage": {
            "type": "file",
            "file_path": str(tmpdir / "vault.db")
        },
        "audit": {
            "log_file": str(tmpdir / "audit.log")
        },
        "schema_version": "1.0.0"
    }

def test_persona_crud(vault, persona_id, user_id):
    # Create
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    mem = vault.get_persona(persona_id, user_id)
    assert mem is not None and mem["data"]["traits"]["openness"] == 50
    # Update
    data2 = {"traits": {"openness": 99}}
    vault.create_or_update_persona(persona_id, user_id, data2)
    mem2 = vault.get_persona(persona_id, user_id)
    assert mem2["data"]["traits"]["openness"] == 99
    # Delete
    vault.delete_persona(persona_id, user_id)
    assert vault.get_persona(persona_id, user_id) is None

def test_communal_crud(vault, memory_id, user_id):
    # Create
    data = {"shared": True}
    vault.create_or_update_communal(memory_id, data, user_id)
    mem = vault.get_communal(memory_id, user_id)
    assert mem is not None and mem["data"]["shared"] is True
    # Update
    data2 = {"shared": False}
    vault.create_or_update_communal(memory_id, data2, user_id)
    mem2 = vault.get_communal(memory_id, user_id)
    assert mem2["data"]["shared"] is False
    # Delete
    vault.delete_communal(memory_id, user_id)
    assert vault.get_communal(memory_id, user_id) is None

def test_memory_isolation(vault, persona_id, user_id, other_user_id):
    data = {"traits": {"openness": 77}}
    vault.create_or_update_persona(persona_id, user_id, data)
    # Other user should not access
    assert vault.get_persona(persona_id, other_user_id) is None
    # Owner can access
    assert vault.get_persona(persona_id, user_id) is not None

def test_export_import_purge(vault, persona_id, user_id):
    data = {"traits": {"openness": 88}}
    vault.create_or_update_persona(persona_id, user_id, data)
    exported = vault.export_persona(persona_id, user_id)
    assert exported is not None
    # Purge
    vault.purge_persona(persona_id, user_id)
    assert vault.get_persona(persona_id, user_id) is None
    # Import
    vault.import_persona(persona_id, user_id, exported)
    assert vault.get_persona(persona_id, user_id) is not None

def test_error_handling(vault, persona_id, user_id):
    # Try to get non-existent persona
    try:
        vault.get_persona("doesnotexist", user_id)
    except Exception:
        assert False, "Should not raise error for missing persona"
    # Try to import invalid data
    try:
        vault.import_persona(persona_id, user_id, "notjson")
        assert False, "Should raise error for invalid import data"
    except Exception:
        pass

def test_audit_log(vault, persona_id, user_id):
    data = {"traits": {"openness": 42}}
    vault.create_or_update_persona(persona_id, user_id, data)
    vault.get_persona(persona_id, user_id)
    vault.export_persona(persona_id, user_id)
    log = vault.export_audit_log()
    assert "create_or_update_persona" in log and "export_persona" in log

def run_all_tests():
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = get_test_config(tmpdir)
        logger = DummyLogger()
        vault = Vault(config, logger)
        persona_id = "alden"
        user_id = "user-1"
        other_user_id = "user-2"
        memory_id = "communal-1"
        print("Testing persona CRUD...")
        test_persona_crud(vault, persona_id, user_id)
        print("Testing communal CRUD...")
        test_communal_crud(vault, memory_id, user_id)
        print("Testing memory isolation...")
        test_memory_isolation(vault, persona_id, user_id, other_user_id)
        print("Testing export/import/purge...")
        test_export_import_purge(vault, persona_id, user_id)
        print("Testing error handling...")
        test_error_handling(vault, persona_id, user_id)
        print("Testing audit log...")
        test_audit_log(vault, persona_id, user_id)
        print("All Vault tests passed.")
    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    run_all_tests() 