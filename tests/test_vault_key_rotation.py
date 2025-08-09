"""
SPEC-2 Phase 2: Vault Key Rotation Tests
Comprehensive test suite for key rotation functionality, performance, and reliability.
"""

import pytest
import asyncio
import tempfile
import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.vault.key_rotation import (
    VaultKeyRotationManager,
    KeyRotationScheduler,
    RotationPolicy,
    KeyVersion,
    KeyRotationError
)

@pytest.fixture
def temp_config():
    """Create temporary configuration for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            "storage": {
                "file_path": f"{temp_dir}/test_vault.db"
            },
            "encryption": {
                "key_file": f"{temp_dir}/test_key.bin"
            },
            "key_rotation": {
                "rotation_interval_days": 1,  # Short interval for testing
                "max_key_versions": 3,
                "auto_rotation_enabled": True,
                "performance_threshold_seconds": 5.0,
                "backup_old_keys": True
            },
            "schema_version": "1.0"
        }
        yield config

@pytest.fixture
def rotation_manager(temp_config):
    """Create key rotation manager for testing"""
    logger = Mock()
    manager = VaultKeyRotationManager(temp_config, logger)
    return manager

class TestVaultKeyRotationManager:
    """Test suite for VaultKeyRotationManager"""

    def test_initialization(self, temp_config):
        """Test manager initialization"""
        manager = VaultKeyRotationManager(temp_config)
        
        assert manager.config == temp_config
        assert manager.policy.rotation_interval_days == 1
        assert manager.policy.max_key_versions == 3
        assert manager.policy.auto_rotation_enabled is True
        
        # Check database initialization
        assert Path(manager.db_path).exists()
        
        # Check initial key generation
        current_key = manager.get_current_key()
        assert current_key is not None
        assert current_key.version == 1
        assert len(current_key.key_data) == 32  # 256 bits
        assert current_key.is_active is True

    def test_key_generation(self, rotation_manager):
        """Test key generation and storage"""
        initial_key = rotation_manager.get_current_key()
        assert initial_key.version == 1
        assert initial_key.is_active is True
        
        # Test key retrieval by version
        retrieved_key = rotation_manager.get_key_by_version(1)
        assert retrieved_key is not None
        assert retrieved_key.version == 1
        assert retrieved_key.key_data == initial_key.key_data

    def test_should_rotate_logic(self, rotation_manager):
        """Test rotation scheduling logic"""
        # Initially should not rotate (just created)
        should_rotate, reason = rotation_manager.should_rotate()
        assert should_rotate is False
        assert "not due" in reason.lower()
        
        # Test with disabled auto-rotation
        rotation_manager.policy.auto_rotation_enabled = False
        should_rotate, reason = rotation_manager.should_rotate()
        assert should_rotate is False
        assert "disabled" in reason.lower()
        
        # Re-enable auto-rotation
        rotation_manager.policy.auto_rotation_enabled = True
        
        # Simulate old key (manually update database)
        old_timestamp = (datetime.now() - timedelta(days=2)).isoformat()
        
        with sqlite3.connect(rotation_manager.db_path) as conn:
            conn.execute(
                "UPDATE key_versions SET created_at = ? WHERE version = 1",
                (old_timestamp,)
            )
            conn.commit()
        
        # Reload current key
        rotation_manager._load_current_key()
        
        should_rotate, reason = rotation_manager.should_rotate()
        assert should_rotate is True
        assert "due" in reason.lower()

    @pytest.mark.asyncio
    async def test_key_rotation_basic(self, rotation_manager):
        """Test basic key rotation functionality"""
        initial_key = rotation_manager.get_current_key()
        initial_version = initial_key.version
        
        # Force rotation
        result = await rotation_manager.rotate_key("test", force=True)
        
        assert result['success'] is True
        assert result['old_version'] == initial_version
        assert result['new_version'] == initial_version + 1
        assert result['trigger_type'] == "test"
        assert result['duration_seconds'] > 0
        
        # Verify new key is active
        new_key = rotation_manager.get_current_key()
        assert new_key.version == initial_version + 1
        assert new_key.is_active is True
        
        # Verify old key is deactivated
        old_key = rotation_manager.get_key_by_version(initial_version)
        assert old_key is not None
        assert old_key.is_active is False
        assert old_key.rotated_at is not None

    @pytest.mark.asyncio
    async def test_key_rotation_performance(self, rotation_manager):
        """Test key rotation performance requirements"""
        start_time = time.time()
        
        result = await rotation_manager.rotate_key("performance_test", force=True)
        
        duration = time.time() - start_time
        
        assert result['success'] is True
        assert duration < 5.0  # Performance requirement
        assert result['duration_seconds'] < 5.0

    @pytest.mark.asyncio
    async def test_data_re_encryption(self, rotation_manager, temp_config):
        """Test that existing data is re-encrypted with new keys"""
        # Create some test data in vault storage
        test_data = {"test_key": "test_value", "number": 123}
        storage_path = Path(temp_config['storage']['file_path'])
        
        # Simulate existing encrypted data
        current_key = rotation_manager.get_current_key()
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets
        
        aesgcm = AESGCM(current_key.key_data)
        nonce = secrets.token_bytes(12)
        plaintext = json.dumps(test_data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_data = nonce + ciphertext
        
        # Write encrypted data to storage
        with open(storage_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Perform rotation
        result = await rotation_manager.rotate_key("re_encryption_test", force=True)
        assert result['success'] is True
        
        # Verify data can still be decrypted with new key
        new_key = rotation_manager.get_current_key()
        new_aesgcm = AESGCM(new_key.key_data)
        
        with open(storage_path, 'rb') as f:
            new_encrypted_data = f.read()
        
        new_nonce = new_encrypted_data[:12]
        new_ciphertext = new_encrypted_data[12:]
        decrypted_plaintext = new_aesgcm.decrypt(new_nonce, new_ciphertext, None)
        decrypted_data = json.loads(decrypted_plaintext.decode())
        
        assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_key_version_cleanup(self, rotation_manager):
        """Test automatic cleanup of old key versions"""
        # Set low max versions for testing
        rotation_manager.policy.max_key_versions = 2
        
        initial_version = rotation_manager.get_current_key().version
        
        # Perform multiple rotations
        for i in range(4):
            result = await rotation_manager.rotate_key(f"cleanup_test_{i}", force=True)
            assert result['success'] is True
        
        # Check that only max_key_versions are retained
        versions = rotation_manager.list_key_versions()
        assert len(versions) <= rotation_manager.policy.max_key_versions
        
        # Verify newest versions are kept
        current_key = rotation_manager.get_current_key()
        assert current_key.version == initial_version + 4

    @pytest.mark.asyncio
    async def test_rollback_functionality(self, rotation_manager):
        """Test key rollback capability"""
        initial_version = rotation_manager.get_current_key().version
        
        # Perform rotation to create version 2
        await rotation_manager.rotate_key("rollback_test", force=True)
        current_version = rotation_manager.get_current_key().version
        assert current_version == initial_version + 1
        
        # Rollback to initial version
        result = await rotation_manager.rollback_to_version(initial_version)
        
        assert result['success'] is True
        assert result['from_version'] == current_version
        assert result['to_version'] == initial_version
        
        # Verify rollback
        active_key = rotation_manager.get_current_key()
        assert active_key.version == initial_version
        assert active_key.is_active is True

    def test_rotation_history_logging(self, rotation_manager):
        """Test rotation history logging"""
        # Initially no history
        history = rotation_manager.get_rotation_history(limit=10)
        assert len(history) == 0
        
        # Perform rotation (synchronous for simplicity)
        asyncio.run(rotation_manager.rotate_key("history_test", force=True))
        
        # Check history
        history = rotation_manager.get_rotation_history(limit=10)
        assert len(history) == 1
        
        entry = history[0]
        assert entry['trigger_type'] == "history_test"
        assert entry['success'] is True
        assert entry['duration_seconds'] > 0
        assert entry['old_version'] == 1
        assert entry['new_version'] == 2

    def test_key_metadata_export(self, rotation_manager):
        """Test key metadata export functionality"""
        metadata = rotation_manager.export_key_metadata()
        
        assert 'current_key_version' in metadata
        assert 'total_versions' in metadata
        assert 'key_versions' in metadata
        assert 'rotation_history' in metadata
        assert 'policy' in metadata
        assert 'should_rotate' in metadata
        assert 'metrics' in metadata
        
        # Verify policy data
        policy_data = metadata['policy']
        assert policy_data['rotation_interval_days'] == 1
        assert policy_data['max_key_versions'] == 3
        assert policy_data['auto_rotation_enabled'] is True

    @pytest.mark.asyncio
    async def test_rotation_not_due(self, rotation_manager):
        """Test that rotation is skipped when not due"""
        result = await rotation_manager.rotate_key("not_due_test", force=False)
        
        assert result['success'] is False
        assert 'not due' in result['reason'].lower()
        assert result['trigger_type'] == "not_due_test"

    def test_error_handling(self, rotation_manager):
        """Test error handling in various scenarios"""
        # Test invalid version rollback
        with pytest.raises(KeyRotationError):
            asyncio.run(rotation_manager.rollback_to_version(999))
        
        # Test database corruption handling
        # Corrupt the database file
        with open(rotation_manager.db_path, 'wb') as f:
            f.write(b'corrupted data')
        
        with pytest.raises(Exception):
            rotation_manager.get_current_key()

class TestKeyRotationScheduler:
    """Test suite for KeyRotationScheduler"""
    
    @pytest.fixture
    def scheduler(self, rotation_manager):
        """Create scheduler for testing"""
        logger = Mock()
        return KeyRotationScheduler(rotation_manager, logger)

    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, scheduler):
        """Test scheduler start and stop"""
        assert scheduler._running is False
        
        await scheduler.start()
        assert scheduler._running is True
        
        await scheduler.stop()
        assert scheduler._running is False

    @pytest.mark.asyncio
    async def test_scheduled_rotation(self, scheduler, rotation_manager):
        """Test automatic scheduled rotation"""
        # Mock should_rotate to return True
        with patch.object(rotation_manager, 'should_rotate', return_value=(True, "Test rotation due")):
            with patch.object(rotation_manager, 'rotate_key', new_callable=AsyncMock) as mock_rotate:
                mock_rotate.return_value = {'success': True}
                
                # Start scheduler briefly
                await scheduler.start()
                
                # Give it a moment to run
                await asyncio.sleep(0.1)
                
                await scheduler.stop()
                
                # Verify rotation was called
                mock_rotate.assert_called_once_with(trigger_type="scheduled")

class TestRotationPolicy:
    """Test suite for RotationPolicy"""
    
    def test_policy_defaults(self):
        """Test default policy values"""
        policy = RotationPolicy()
        
        assert policy.rotation_interval_days == 30
        assert policy.max_key_versions == 3
        assert policy.auto_rotation_enabled is True
        assert policy.performance_threshold_seconds == 5.0
        assert policy.backup_old_keys is True

    def test_policy_customization(self):
        """Test custom policy values"""
        policy = RotationPolicy(
            rotation_interval_days=7,
            max_key_versions=5,
            auto_rotation_enabled=False,
            performance_threshold_seconds=10.0
        )
        
        assert policy.rotation_interval_days == 7
        assert policy.max_key_versions == 5
        assert policy.auto_rotation_enabled is False
        assert policy.performance_threshold_seconds == 10.0

class TestKeyVersion:
    """Test suite for KeyVersion dataclass"""
    
    def test_key_version_creation(self):
        """Test KeyVersion creation and attributes"""
        key_data = b'test_key_data_32_bytes_exactly!!'
        created_at = datetime.now().isoformat()
        metadata = {'test': 'value'}
        
        key_version = KeyVersion(
            version=1,
            key_data=key_data,
            created_at=created_at,
            metadata=metadata
        )
        
        assert key_version.version == 1
        assert key_version.key_data == key_data
        assert key_version.created_at == created_at
        assert key_version.rotated_at is None
        assert key_version.is_active is True
        assert key_version.metadata == metadata

@pytest.mark.benchmark
class TestRotationPerformance:
    """Performance benchmarks for key rotation"""
    
    @pytest.mark.asyncio
    async def test_rotation_benchmark(self, rotation_manager, benchmark):
        """Benchmark key rotation performance"""
        
        async def rotation_operation():
            return await rotation_manager.rotate_key("benchmark", force=True)
        
        # Run benchmark
        result = await benchmark(rotation_operation)
        
        assert result['success'] is True
        assert result['duration_seconds'] < 5.0  # Performance requirement

    def test_key_generation_benchmark(self, temp_config, benchmark):
        """Benchmark key generation performance"""
        
        def key_generation():
            return VaultKeyRotationManager(temp_config)
        
        manager = benchmark(key_generation)
        assert manager.get_current_key() is not None

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, rotation_manager):
        """Test concurrent key operations"""
        
        async def read_operation():
            return rotation_manager.get_current_key()
        
        async def metadata_operation():
            return rotation_manager.export_key_metadata()
        
        # Run operations concurrently
        tasks = [
            read_operation(),
            read_operation(),
            metadata_operation(),
            metadata_operation()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert len(results) == 4
        assert all(result is not None for result in results)

@pytest.mark.integration
class TestRotationIntegration:
    """Integration tests for key rotation system"""
    
    @pytest.mark.asyncio
    async def test_full_rotation_cycle(self, rotation_manager):
        """Test complete rotation lifecycle"""
        # 1. Initial state
        initial_key = rotation_manager.get_current_key()
        assert initial_key.version == 1
        
        # 2. Create test data
        test_data = {"integration": "test", "value": 42}
        # Simulate vault storage would happen here
        
        # 3. Perform rotation
        result = await rotation_manager.rotate_key("integration_test", force=True)
        assert result['success'] is True
        
        # 4. Verify new key
        new_key = rotation_manager.get_current_key()
        assert new_key.version == 2
        assert new_key != initial_key
        
        # 5. Check history
        history = rotation_manager.get_rotation_history(limit=5)
        assert len(history) == 1
        assert history[0]['success'] is True
        
        # 6. Verify metadata
        metadata = rotation_manager.export_key_metadata()
        assert metadata['current_key_version'] == 2
        assert metadata['total_versions'] == 2

    @pytest.mark.asyncio
    async def test_multiple_rotations_and_cleanup(self, rotation_manager):
        """Test multiple rotations with version cleanup"""
        rotation_manager.policy.max_key_versions = 3
        
        initial_version = rotation_manager.get_current_key().version
        
        # Perform 5 rotations
        for i in range(5):
            result = await rotation_manager.rotate_key(f"multi_rotation_{i}", force=True)
            assert result['success'] is True
        
        # Verify final state
        final_key = rotation_manager.get_current_key()
        assert final_key.version == initial_version + 5
        
        # Verify cleanup occurred
        versions = rotation_manager.list_key_versions()
        assert len(versions) <= 3
        
        # Verify history is maintained
        history = rotation_manager.get_rotation_history(limit=10)
        assert len(history) == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])