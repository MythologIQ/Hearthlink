"""
SPEC-2 Phase 2: Vault Key Rotation System
Implements automated 30-day key rotation with version history and rollback support.
"""

import os
import json
import sqlite3
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
from prometheus_client import Counter, Gauge, Histogram

# Prometheus metrics for monitoring
key_rotation_counter = Counter('vault_key_rotation_total', 'Total key rotations performed')
key_rotation_timestamp = Gauge('vault_key_rotation_timestamp', 'Timestamp of last key rotation')
key_version_count = Gauge('vault_key_version_count', 'Number of key versions stored')
key_rotation_duration = Histogram('vault_key_rotation_duration_seconds', 'Time taken for key rotation')

@dataclass
class KeyVersion:
    """Represents a versioned encryption key"""
    version: int
    key_data: bytes
    created_at: str
    rotated_at: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RotationPolicy:
    """Key rotation policy configuration"""
    rotation_interval_days: int = 30
    max_key_versions: int = 3
    auto_rotation_enabled: bool = True
    performance_threshold_seconds: float = 5.0
    backup_old_keys: bool = True

class KeyRotationError(Exception):
    pass

class VaultKeyRotationManager:
    """
    Manages automated key rotation for the Vault system.
    Supports 30-day rotation cycles, version history, and rollback capabilities.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.policy = RotationPolicy(**config.get('key_rotation', {}))
        
        # Database for storing key versions
        self.db_path = Path(config['storage']['file_path']).parent / 'vault_keys.db'
        self._init_key_database()
        
        # Current active key
        self._current_key: Optional[KeyVersion] = None
        self._load_current_key()

    def _init_key_database(self):
        """Initialize SQLite database for key version storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS key_versions (
                    version INTEGER PRIMARY KEY,
                    key_data BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    rotated_at TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rotation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    old_version INTEGER,
                    new_version INTEGER,
                    trigger_type TEXT NOT NULL,
                    duration_seconds REAL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_key_versions_active 
                ON key_versions(is_active, version DESC)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_rotation_log_timestamp 
                ON rotation_log(timestamp DESC)
            ''')
            
            conn.commit()

    def _load_current_key(self):
        """Load the current active key from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT version, key_data, created_at, rotated_at, metadata
                FROM key_versions 
                WHERE is_active = 1 
                ORDER BY version DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                version, key_data, created_at, rotated_at, metadata = row
                self._current_key = KeyVersion(
                    version=version,
                    key_data=key_data,
                    created_at=created_at,
                    rotated_at=rotated_at,
                    is_active=True,
                    metadata=json.loads(metadata) if metadata else {}
                )
                self.logger.info(f"Loaded active key version {version}")
            else:
                # Generate initial key
                self._generate_initial_key()

    def _generate_initial_key(self):
        """Generate the initial master key"""
        key_data = AESGCM.generate_key(bit_length=256)
        now = datetime.now().isoformat()
        
        self._current_key = KeyVersion(
            version=1,
            key_data=key_data,
            created_at=now,
            metadata={'generation_method': 'initial', 'bit_length': 256}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO key_versions (version, key_data, created_at, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                self._current_key.version,
                self._current_key.key_data,
                self._current_key.created_at,
                json.dumps(self._current_key.metadata)
            ))
            conn.commit()
        
        self.logger.info("Generated initial master key version 1")
        key_version_count.set(1)

    def get_current_key(self) -> KeyVersion:
        """Get the current active encryption key"""
        if not self._current_key:
            raise KeyRotationError("No active key found")
        return self._current_key

    def get_key_by_version(self, version: int) -> Optional[KeyVersion]:
        """Retrieve a specific key version for decryption"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT key_data, created_at, rotated_at, is_active, metadata
                FROM key_versions 
                WHERE version = ?
            ''', (version,))
            row = cursor.fetchone()
            
            if row:
                key_data, created_at, rotated_at, is_active, metadata = row
                return KeyVersion(
                    version=version,
                    key_data=key_data,
                    created_at=created_at,
                    rotated_at=rotated_at,
                    is_active=bool(is_active),
                    metadata=json.loads(metadata) if metadata else {}
                )
        return None

    def list_key_versions(self) -> List[Dict[str, Any]]:
        """List all key versions with metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT version, created_at, rotated_at, is_active, metadata
                FROM key_versions 
                ORDER BY version DESC
            ''')
            
            versions = []
            for row in cursor.fetchall():
                version, created_at, rotated_at, is_active, metadata = row
                versions.append({
                    'version': version,
                    'created_at': created_at,
                    'rotated_at': rotated_at,
                    'is_active': bool(is_active),
                    'metadata': json.loads(metadata) if metadata else {}
                })
            
            return versions

    def should_rotate(self) -> Tuple[bool, str]:
        """Check if key rotation is due"""
        if not self.policy.auto_rotation_enabled:
            return False, "Auto-rotation disabled"
            
        if not self._current_key:
            return True, "No active key found"
            
        created_at = datetime.fromisoformat(self._current_key.created_at)
        rotation_due = created_at + timedelta(days=self.policy.rotation_interval_days)
        
        if datetime.now() >= rotation_due:
            return True, f"Key rotation due (created {self.policy.rotation_interval_days} days ago)"
            
        return False, f"Key rotation not due until {rotation_due.isoformat()}"

    async def rotate_key(self, trigger_type: str = "manual", force: bool = False) -> Dict[str, Any]:
        """
        Perform key rotation with performance monitoring
        
        Args:
            trigger_type: Type of trigger ('manual', 'scheduled', 'api')
            force: Force rotation even if not due
            
        Returns:
            Dict containing rotation results
        """
        start_time = datetime.now()
        old_version = self._current_key.version if self._current_key else 0
        
        try:
            with key_rotation_duration.time():
                # Check if rotation is needed
                should_rotate, reason = self.should_rotate()
                if not should_rotate and not force:
                    return {
                        'success': False,
                        'reason': reason,
                        'current_version': old_version
                    }
                
                self.logger.info(f"Starting key rotation: {reason}")
                
                # Generate new key
                new_key_data = AESGCM.generate_key(bit_length=256)
                new_version = old_version + 1
                now = datetime.now().isoformat()
                
                new_key = KeyVersion(
                    version=new_version,
                    key_data=new_key_data,
                    created_at=now,
                    metadata={
                        'generation_method': 'rotation',
                        'bit_length': 256,
                        'trigger_type': trigger_type,
                        'previous_version': old_version
                    }
                )
                
                # Re-encrypt existing data with new key
                await self._re_encrypt_vault_data(new_key)
                
                # Store new key and deactivate old key
                with sqlite3.connect(self.db_path) as conn:
                    # Insert new key
                    conn.execute('''
                        INSERT INTO key_versions (version, key_data, created_at, metadata)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        new_key.version,
                        new_key.key_data,
                        new_key.created_at,
                        json.dumps(new_key.metadata)
                    ))
                    
                    # Deactivate old key
                    if self._current_key:
                        conn.execute('''
                            UPDATE key_versions 
                            SET is_active = 0, rotated_at = ?
                            WHERE version = ?
                        ''', (now, self._current_key.version))
                    
                    conn.commit()
                
                # Clean up old versions if needed
                await self._cleanup_old_versions()
                
                # Update current key
                self._current_key = new_key
                
                # Update metrics
                key_rotation_counter.inc()
                key_rotation_timestamp.set_to_current_time()
                key_version_count.set(await self._count_active_versions())
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log successful rotation
                self._log_rotation(
                    old_version=old_version,
                    new_version=new_version,
                    trigger_type=trigger_type,
                    duration=duration,
                    success=True
                )
                
                # Performance check
                if duration > self.policy.performance_threshold_seconds:
                    self.logger.warning(
                        f"Key rotation took {duration:.2f}s, exceeding threshold of {self.policy.performance_threshold_seconds}s"
                    )
                else:
                    self.logger.info(f"Key rotation completed successfully in {duration:.2f}s")
                
                return {
                    'success': True,
                    'old_version': old_version,
                    'new_version': new_version,
                    'duration_seconds': duration,
                    'trigger_type': trigger_type
                }
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Key rotation failed: {e}")
            
            # Log failed rotation
            self._log_rotation(
                old_version=old_version,
                new_version=old_version + 1,
                trigger_type=trigger_type,
                duration=duration,
                success=False,
                error_message=str(e)
            )
            
            raise KeyRotationError(f"Key rotation failed: {e}")

    async def _re_encrypt_vault_data(self, new_key: KeyVersion):
        """Re-encrypt all vault data with the new key"""
        if not self._current_key:
            return
            
        storage_path = Path(self.config['storage']['file_path'])
        if not storage_path.exists():
            return
            
        # Read data with old key
        with open(storage_path, 'rb') as f:
            encrypted_data = f.read()
            
        # Decrypt with old key
        old_aesgcm = AESGCM(self._current_key.key_data)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = old_aesgcm.decrypt(nonce, ciphertext, None)
        
        # Encrypt with new key
        new_aesgcm = AESGCM(new_key.key_data)
        new_nonce = secrets.token_bytes(12)
        new_ciphertext = new_aesgcm.encrypt(new_nonce, plaintext, None)
        new_encrypted_data = new_nonce + new_ciphertext
        
        # Write back with new encryption
        with open(storage_path, 'wb') as f:
            f.write(new_encrypted_data)
            
        self.logger.info("Successfully re-encrypted vault data with new key")

    async def _cleanup_old_versions(self):
        """Remove old key versions beyond the retention limit"""
        with sqlite3.connect(self.db_path) as conn:
            # Get count of versions
            cursor = conn.execute('SELECT COUNT(*) FROM key_versions')
            total_versions = cursor.fetchone()[0]
            
            if total_versions > self.policy.max_key_versions:
                # Delete oldest versions
                versions_to_delete = total_versions - self.policy.max_key_versions
                conn.execute('''
                    DELETE FROM key_versions 
                    WHERE version IN (
                        SELECT version FROM key_versions 
                        ORDER BY version ASC 
                        LIMIT ?
                    )
                ''', (versions_to_delete,))
                conn.commit()
                
                self.logger.info(f"Cleaned up {versions_to_delete} old key versions")

    async def _count_active_versions(self) -> int:
        """Count the number of stored key versions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM key_versions')
            return cursor.fetchone()[0]

    def _log_rotation(self, old_version: int, new_version: int, trigger_type: str, 
                     duration: float, success: bool, error_message: Optional[str] = None):
        """Log rotation attempt to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO rotation_log 
                (timestamp, old_version, new_version, trigger_type, duration_seconds, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                old_version,
                new_version,
                trigger_type,
                duration,
                success,
                error_message
            ))
            conn.commit()

    def get_rotation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get rotation history for monitoring"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, old_version, new_version, trigger_type, 
                       duration_seconds, success, error_message
                FROM rotation_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                timestamp, old_version, new_version, trigger_type, duration, success, error = row
                history.append({
                    'timestamp': timestamp,
                    'old_version': old_version,
                    'new_version': new_version,
                    'trigger_type': trigger_type,
                    'duration_seconds': duration,
                    'success': bool(success),
                    'error_message': error
                })
            
            return history

    async def rollback_to_version(self, target_version: int) -> Dict[str, Any]:
        """
        Rollback to a previous key version (emergency use only)
        
        Args:
            target_version: Version number to rollback to
            
        Returns:
            Dict containing rollback results
        """
        start_time = datetime.now()
        current_version = self._current_key.version if self._current_key else 0
        
        try:
            # Get target key version
            target_key = self.get_key_by_version(target_version)
            if not target_key:
                raise KeyRotationError(f"Key version {target_version} not found")
                
            self.logger.warning(f"Rolling back from version {current_version} to {target_version}")
            
            # Re-encrypt data with target key
            await self._re_encrypt_vault_data(target_key)
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                # Deactivate current key
                conn.execute('''
                    UPDATE key_versions 
                    SET is_active = 0 
                    WHERE is_active = 1
                ''')
                
                # Activate target key
                conn.execute('''
                    UPDATE key_versions 
                    SET is_active = 1 
                    WHERE version = ?
                ''', (target_version,))
                
                conn.commit()
            
            # Update current key
            target_key.is_active = True
            self._current_key = target_key
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log rollback
            self._log_rotation(
                old_version=current_version,
                new_version=target_version,
                trigger_type="rollback",
                duration=duration,
                success=True
            )
            
            self.logger.info(f"Successfully rolled back to key version {target_version}")
            
            return {
                'success': True,
                'from_version': current_version,
                'to_version': target_version,
                'duration_seconds': duration
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Rollback failed: {e}")
            
            self._log_rotation(
                old_version=current_version,
                new_version=target_version,
                trigger_type="rollback",
                duration=duration,
                success=False,
                error_message=str(e)
            )
            
            raise KeyRotationError(f"Rollback failed: {e}")

    def export_key_metadata(self) -> Dict[str, Any]:
        """Export key rotation metadata for monitoring"""
        versions = self.list_key_versions()
        history = self.get_rotation_history(limit=10)
        
        return {
            'current_key_version': self._current_key.version if self._current_key else None,
            'total_versions': len(versions),
            'key_versions': versions,
            'rotation_history': history,
            'policy': asdict(self.policy),
            'should_rotate': self.should_rotate(),
            'metrics': {
                'last_rotation_timestamp': key_rotation_timestamp._value._value if hasattr(key_rotation_timestamp._value, '_value') else None,
                'total_rotations': key_rotation_counter._value._value if hasattr(key_rotation_counter._value, '_value') else 0,
                'active_versions': key_version_count._value._value if hasattr(key_version_count._value, '_value') else 0
            }
        }

# Async scheduler for automated rotation
class KeyRotationScheduler:
    """Handles scheduled key rotation tasks"""
    
    def __init__(self, rotation_manager: VaultKeyRotationManager, logger: Optional[logging.Logger] = None):
        self.rotation_manager = rotation_manager
        self.logger = logger or logging.getLogger(__name__)
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the rotation scheduler"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Key rotation scheduler started")

    async def stop(self):
        """Stop the rotation scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Key rotation scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._running:
            try:
                should_rotate, reason = self.rotation_manager.should_rotate()
                if should_rotate:
                    self.logger.info(f"Triggering scheduled key rotation: {reason}")
                    await self.rotation_manager.rotate_key(trigger_type="scheduled")
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in rotation scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry