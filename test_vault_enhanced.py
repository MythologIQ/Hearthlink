import os
import json
import tempfile
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
from src.vault.vault_enhanced import VaultEnhanced, VaultError, VaultValidationError, VaultIntegrityError
from src.vault.schema import PersonaMemory, CommunalMemory

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

def test_basic_crud(vault, persona_id, user_id):
    """Test basic CRUD operations."""
    print("Testing basic CRUD operations...")
    
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

def test_memory_isolation(vault, persona_id, user_id, other_user_id):
    """Test memory isolation between users."""
    print("Testing memory isolation...")
    
    data = {"traits": {"openness": 77}}
    vault.create_or_update_persona(persona_id, user_id, data)
    
    # Other user should not access
    assert vault.get_persona(persona_id, other_user_id) is None
    
    # Owner can access
    assert vault.get_persona(persona_id, user_id) is not None

def test_schema_validation(vault, persona_id, user_id):
    """Test schema validation."""
    print("Testing schema validation...")
    
    # Test valid data
    valid_data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, valid_data)
    
    # Test invalid import data
    invalid_data = '{"invalid": "schema"}'
    try:
        vault.import_persona(persona_id, user_id, invalid_data)
        assert False, "Should raise validation error for invalid schema"
    except VaultValidationError:
        pass

def test_concurrent_access(vault, persona_id, user_id):
    """Test concurrent access handling."""
    print("Testing concurrent access...")
    
    results = []
    errors = []
    
    def worker(worker_id):
        try:
            data = {"worker": worker_id, "timestamp": time.time()}
            vault.create_or_update_persona(f"{persona_id}_worker_{worker_id}", user_id, data)
            mem = vault.get_persona(f"{persona_id}_worker_{worker_id}", user_id)
            results.append(mem is not None)
        except Exception as e:
            errors.append(str(e))
    
    # Create multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Check results
    assert len(errors) == 0, f"Concurrent access errors: {errors}"
    assert all(results), "Some concurrent operations failed"

def test_data_integrity(vault, persona_id, user_id):
    """Test data integrity verification."""
    print("Testing data integrity...")
    
    # Create some data
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    
    # Verify integrity
    is_valid, issues = vault.verify_integrity()
    assert is_valid, f"Integrity check failed: {issues}"
    
    # Test with corrupted data (simulate by directly modifying file)
    # This would require more complex setup to test actual corruption

def test_backup_restore(vault, persona_id, user_id, tmpdir):
    """Test backup and restore functionality."""
    print("Testing backup and restore...")
    
    # Create data
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    
    # Create backup
    backup_path = str(tmpdir / "backup.json")
    success = vault.create_backup(backup_path)
    assert success, "Backup creation failed"
    
    # Verify backup file exists and contains data
    assert os.path.exists(backup_path)
    with open(backup_path, "r") as f:
        backup_data = json.load(f)
    assert "data" in backup_data
    assert "backup_created_at" in backup_data
    
    # Delete original data
    vault.delete_persona(persona_id, user_id)
    assert vault.get_persona(persona_id, user_id) is None
    
    # Restore from backup
    success = vault.restore_backup(backup_path)
    assert success, "Backup restoration failed"
    
    # Verify data is restored
    mem = vault.get_persona(persona_id, user_id)
    assert mem is not None
    assert mem["data"]["traits"]["openness"] == 50

def test_export_import_validation(vault, persona_id, user_id):
    """Test export/import with validation."""
    print("Testing export/import validation...")
    
    # Create data
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    
    # Export
    exported = vault.export_persona(persona_id, user_id)
    assert exported is not None
    
    # Parse exported data
    exported_data = json.loads(exported)
    assert "persona_id" in exported_data
    assert "user_id" in exported_data
    assert "data" in exported_data
    
    # Delete original
    vault.delete_persona(persona_id, user_id)
    assert vault.get_persona(persona_id, user_id) is None
    
    # Import
    vault.import_persona(persona_id, user_id, exported)
    
    # Verify import
    mem = vault.get_persona(persona_id, user_id)
    assert mem is not None
    assert mem["data"]["traits"]["openness"] == 50

def test_audit_log_filtering(vault, persona_id, user_id):
    """Test audit log filtering."""
    print("Testing audit log filtering...")
    
    # Perform some operations
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    vault.get_persona(persona_id, user_id)
    vault.export_persona(persona_id, user_id)
    
    # Test unfiltered export
    log = vault.export_audit_log()
    log_data = json.loads(log)
    assert len(log_data) > 0
    
    # Test filtered export
    filtered_log = vault.export_audit_log({"action": "create_or_update_persona"})
    filtered_data = json.loads(filtered_log)
    assert len(filtered_data) > 0
    assert all(entry["action"] == "create_or_update_persona" for entry in filtered_data)

def test_error_handling(vault, persona_id, user_id):
    """Test error handling scenarios."""
    print("Testing error handling...")
    
    # Test invalid import data
    try:
        vault.import_persona(persona_id, user_id, "not json")
        assert False, "Should raise error for invalid JSON"
    except Exception:
        pass
    
    # Test accessing non-existent persona
    assert vault.get_persona("doesnotexist", user_id) is None
    
    # Test deleting non-existent persona
    vault.delete_persona("doesnotexist", user_id)  # Should not raise error

def test_cache_functionality(vault, persona_id, user_id):
    """Test caching functionality."""
    print("Testing cache functionality...")
    
    # Create data
    data = {"traits": {"openness": 50}}
    vault.create_or_update_persona(persona_id, user_id, data)
    
    # First access (should cache)
    mem1 = vault.get_persona(persona_id, user_id)
    assert mem1 is not None
    
    # Second access (should use cache)
    mem2 = vault.get_persona(persona_id, user_id)
    assert mem2 is not None
    assert mem1 == mem2
    
    # Update data (should clear cache)
    data2 = {"traits": {"openness": 99}}
    vault.create_or_update_persona(persona_id, user_id, data2)
    
    # Access again (should not use old cache)
    mem3 = vault.get_persona(persona_id, user_id)
    assert mem3 is not None
    assert mem3["data"]["traits"]["openness"] == 99

def run_all_enhanced_tests():
    """Run all enhanced Vault tests."""
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = get_test_config(tmpdir)
        logger = DummyLogger()
        vault = VaultEnhanced(config, logger)
        
        persona_id = "alden"
        user_id = "user-1"
        other_user_id = "user-2"
        
        print("🚀 Starting Enhanced Vault Test Suite")
        print("=" * 50)
        
        test_basic_crud(vault, persona_id, user_id)
        test_memory_isolation(vault, persona_id, user_id, other_user_id)
        test_schema_validation(vault, persona_id, user_id)
        test_concurrent_access(vault, persona_id, user_id)
        test_data_integrity(vault, persona_id, user_id)
        test_backup_restore(vault, persona_id, user_id, tmpdir)
        test_export_import_validation(vault, persona_id, user_id)
        test_audit_log_filtering(vault, persona_id, user_id)
        test_error_handling(vault, persona_id, user_id)
        test_cache_functionality(vault, persona_id, user_id)
        
        print("✅ All Enhanced Vault tests passed!")
        
    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    run_all_enhanced_tests() 