#!/usr/bin/env python3
"""
Database Backup Manager

Implements comprehensive backup strategy for:
- SQLite database (hearthlink.db)
- Vault encrypted storage
- Configuration files
- Recovery procedures

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import sqlite3
import shutil
import json
import gzip
import tarfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class BackupError(HearthlinkError):
    """Exception raised for backup-related errors."""
    pass


@dataclass
class BackupManifest:
    """Backup manifest with metadata."""
    backup_id: str
    timestamp: str
    database_file: str
    database_size: int
    database_checksum: str
    vault_files: List[str]
    vault_size: int
    config_files: List[str]
    backup_type: str  # "full", "incremental", "scheduled"
    retention_days: int
    compression_ratio: float
    backup_duration: float
    status: str  # "completed", "failed", "in_progress"
    error_message: Optional[str] = None


class DatabaseBackupManager:
    """
    Comprehensive backup manager for Hearthlink database and storage systems.
    
    Features:
    - Automated SQLite backup with integrity verification
    - Vault encrypted storage backup
    - Configuration file backup
    - Compression and checksum validation
    - Retention policy management
    - Recovery procedures
    """
    
    def __init__(self, project_root: Optional[Path] = None, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize backup manager.
        
        Args:
            project_root: Root directory of project (auto-detected if None)
            logger: Optional logger instance
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger or HearthlinkLogger()
        
        # Backup configuration
        self.backup_dir = self.project_root / "backups"
        self.database_path = self.project_root / "hearthlink_data" / "hearthlink.db"
        self.vault_path = self.project_root / "hearthlink_data" / "vault_storage"
        self.config_path = self.project_root / "config"
        
        # Backup settings
        self.retention_days = 30
        self.max_backups = 50
        self.compression_enabled = True
        
        # Initialize backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        self.logger.logger.info("Database backup manager initialized", 
                              extra={"extra_fields": {
                                  "event_type": "backup_manager_init",
                                  "backup_dir": str(self.backup_dir),
                                  "database_path": str(self.database_path),
                                  "vault_path": str(self.vault_path)
                              }})
    
    def create_backup(self, backup_type: str = "manual") -> BackupManifest:
        """
        Create comprehensive backup of database and storage.
        
        Args:
            backup_type: Type of backup ("manual", "scheduled", "incremental")
            
        Returns:
            BackupManifest: Backup metadata and results
            
        Raises:
            BackupError: If backup creation fails
        """
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            self.logger.logger.info("Starting backup creation", 
                                  extra={"extra_fields": {
                                      "event_type": "backup_start",
                                      "backup_id": backup_id,
                                      "backup_type": backup_type
                                  }})
            
            # Create backup directory
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)
            
            # Backup SQLite database
            database_info = self._backup_database(backup_path)
            
            # Backup Vault storage
            vault_info = self._backup_vault_storage(backup_path)
            
            # Backup configuration files
            config_info = self._backup_configuration(backup_path)
            
            # Create compressed archive if enabled
            if self.compression_enabled:
                archive_path = self._create_compressed_archive(backup_path, backup_id)
                # Remove uncompressed backup after successful compression
                shutil.rmtree(backup_path)
                backup_path = archive_path
            
            # Calculate backup duration
            backup_duration = (datetime.now() - start_time).total_seconds()
            
            # Create manifest
            manifest = BackupManifest(
                backup_id=backup_id,
                timestamp=start_time.isoformat(),
                database_file=database_info["file"],
                database_size=database_info["size"],
                database_checksum=database_info["checksum"],
                vault_files=vault_info["files"],
                vault_size=vault_info["size"],
                config_files=config_info["files"],
                backup_type=backup_type,
                retention_days=self.retention_days,
                compression_ratio=self._calculate_compression_ratio(backup_path),
                backup_duration=backup_duration,
                status="completed"
            )
            
            # Save manifest
            self._save_manifest(manifest)
            
            self.logger.logger.info("Backup creation completed", 
                                  extra={"extra_fields": {
                                      "event_type": "backup_completed",
                                      "backup_id": backup_id,
                                      "duration": backup_duration,
                                      "database_size": database_info["size"],
                                      "vault_size": vault_info["size"]
                                  }})
            
            return manifest
            
        except Exception as e:
            error_msg = f"Backup creation failed: {str(e)}"
            self.logger.log_error(e, "backup_creation_error", {"backup_id": backup_id})
            
            # Create failed manifest
            manifest = BackupManifest(
                backup_id=backup_id,
                timestamp=start_time.isoformat(),
                database_file="",
                database_size=0,
                database_checksum="",
                vault_files=[],
                vault_size=0,
                config_files=[],
                backup_type=backup_type,
                retention_days=self.retention_days,
                compression_ratio=0.0,
                backup_duration=(datetime.now() - start_time).total_seconds(),
                status="failed",
                error_message=error_msg
            )
            
            self._save_manifest(manifest)
            raise BackupError(error_msg) from e
    
    def _backup_database(self, backup_path: Path) -> Dict[str, Any]:
        """Backup SQLite database with integrity verification."""
        if not self.database_path.exists():
            raise BackupError(f"Database file not found: {self.database_path}")
        
        backup_db_path = backup_path / "hearthlink.db"
        
        # Use SQLite backup API for safe backup
        with sqlite3.connect(str(self.database_path)) as source_conn:
            with sqlite3.connect(str(backup_db_path)) as backup_conn:
                source_conn.backup(backup_conn)
        
        # Verify backup integrity
        self._verify_database_integrity(backup_db_path)
        
        # Calculate checksum
        checksum = self._calculate_file_checksum(backup_db_path)
        
        return {
            "file": str(backup_db_path),
            "size": backup_db_path.stat().st_size,
            "checksum": checksum
        }
    
    def _backup_vault_storage(self, backup_path: Path) -> Dict[str, Any]:
        """Backup Vault encrypted storage."""
        vault_backup_path = backup_path / "vault_storage"
        
        if not self.vault_path.exists():
            self.logger.logger.warning("Vault storage not found", 
                                     extra={"extra_fields": {"vault_path": str(self.vault_path)}})
            return {"files": [], "size": 0}
        
        vault_files = []
        total_size = 0
        
        if self.vault_path.is_file():
            # Vault storage is a single file
            shutil.copy2(self.vault_path, vault_backup_path)
            vault_files.append("vault_storage")
            total_size = vault_backup_path.stat().st_size
        elif self.vault_path.is_dir():
            # Vault storage is a directory
            shutil.copytree(self.vault_path, vault_backup_path, dirs_exist_ok=True)
            
            # Get list of backed up files
            for file_path in vault_backup_path.rglob("*"):
                if file_path.is_file():
                    vault_files.append(str(file_path.relative_to(vault_backup_path)))
                    total_size += file_path.stat().st_size
        else:
            self.logger.logger.warning("Vault storage path is neither file nor directory", 
                                     extra={"extra_fields": {"vault_path": str(self.vault_path)}})
        
        return {
            "files": vault_files,
            "size": total_size
        }
    
    def _backup_configuration(self, backup_path: Path) -> Dict[str, Any]:
        """Backup configuration files."""
        config_backup_path = backup_path / "config"
        
        if not self.config_path.exists():
            self.logger.logger.warning("Config directory not found", 
                                     extra={"extra_fields": {"config_path": str(self.config_path)}})
            return {"files": []}
        
        try:
            # Create config backup directory
            config_backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy configuration files manually to handle permissions
            config_files = []
            for item in self.config_path.iterdir():
                try:
                    if item.is_file():
                        dest_file = config_backup_path / item.name
                        shutil.copy2(item, dest_file)
                        config_files.append(item.name)
                    elif item.is_dir():
                        dest_dir = config_backup_path / item.name
                        shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                        # Add all files in subdirectory
                        for sub_file in dest_dir.rglob("*"):
                            if sub_file.is_file():
                                config_files.append(str(sub_file.relative_to(config_backup_path)))
                except PermissionError as e:
                    self.logger.logger.warning(f"Permission denied copying {item}: {e}")
                except Exception as e:
                    self.logger.logger.warning(f"Error copying {item}: {e}")
            
            return {"files": config_files}
            
        except Exception as e:
            self.logger.logger.warning(f"Config backup failed: {e}")
            return {"files": []}
    
    def _create_compressed_archive(self, backup_path: Path, backup_id: str) -> Path:
        """Create compressed tar.gz archive of backup."""
        archive_path = self.backup_dir / f"{backup_id}.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_path, arcname=backup_id)
        
        return archive_path
    
    def _calculate_compression_ratio(self, backup_path: Path) -> float:
        """Calculate compression ratio for backup."""
        if backup_path.suffix == ".gz":
            # For compressed archives, estimate original size
            compressed_size = backup_path.stat().st_size
            # Rough estimation - actual ratio would need original size tracking
            return 0.3  # Typical compression ratio for mixed data
        return 1.0  # No compression
    
    def _verify_database_integrity(self, db_path: Path) -> None:
        """Verify SQLite database integrity."""
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] != "ok":
                raise BackupError(f"Database integrity check failed: {result[0]}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum for file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _save_manifest(self, manifest: BackupManifest) -> None:
        """Save backup manifest to JSON file."""
        manifest_path = self.backup_dir / f"{manifest.backup_id}_manifest.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(asdict(manifest), f, indent=2)
    
    def restore_backup(self, backup_id: str, verify_before_restore: bool = True) -> bool:
        """
        Restore database and storage from backup.
        
        Args:
            backup_id: ID of backup to restore
            verify_before_restore: Verify backup integrity before restoring
            
        Returns:
            bool: True if restoration successful
            
        Raises:
            BackupError: If restoration fails
        """
        try:
            self.logger.logger.info("Starting backup restoration", 
                                  extra={"extra_fields": {
                                      "event_type": "restore_start",
                                      "backup_id": backup_id
                                  }})
            
            # Load manifest
            manifest = self._load_manifest(backup_id)
            if not manifest:
                raise BackupError(f"Backup manifest not found: {backup_id}")
            
            if manifest.status != "completed":
                raise BackupError(f"Cannot restore incomplete backup: {backup_id}")
            
            # Extract backup if compressed
            backup_path = self._extract_backup(backup_id)
            
            # Verify backup integrity if requested
            if verify_before_restore:
                self._verify_backup_integrity(backup_path, manifest)
            
            # Create backup of current data before restore
            current_backup = self.create_backup("pre_restore")
            
            try:
                # Restore database
                self._restore_database(backup_path)
                
                # Restore vault storage
                self._restore_vault_storage(backup_path)
                
                # Restore configuration
                self._restore_configuration(backup_path)
                
                self.logger.logger.info("Backup restoration completed", 
                                      extra={"extra_fields": {
                                          "event_type": "restore_completed",
                                          "backup_id": backup_id
                                      }})
                
                return True
                
            except Exception as e:
                # Restore failed - attempt to restore previous state
                self.logger.logger.error("Restore failed, attempting rollback", 
                                       extra={"extra_fields": {
                                           "event_type": "restore_rollback",
                                           "backup_id": backup_id,
                                           "error": str(e)
                                       }})
                
                # Try to restore from pre-restore backup
                try:
                    self.restore_backup(current_backup.backup_id, verify_before_restore=False)
                except Exception as rollback_error:
                    self.logger.logger.error("Rollback failed", 
                                           extra={"extra_fields": {"error": str(rollback_error)}})
                
                raise BackupError(f"Restore failed and rollback attempted: {str(e)}") from e
            
        except Exception as e:
            self.logger.log_error(e, "restore_error", {"backup_id": backup_id})
            raise BackupError(f"Backup restoration failed: {str(e)}") from e
    
    def _load_manifest(self, backup_id: str) -> Optional[BackupManifest]:
        """Load backup manifest from JSON file."""
        manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
            return BackupManifest(**manifest_data)
    
    def _extract_backup(self, backup_id: str) -> Path:
        """Extract backup archive if compressed."""
        archive_path = self.backup_dir / f"{backup_id}.tar.gz"
        extract_path = self.backup_dir / f"{backup_id}_extracted"
        
        if archive_path.exists():
            # Extract compressed backup
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=self.backup_dir)
            return self.backup_dir / backup_id
        else:
            # Check for uncompressed backup
            uncompressed_path = self.backup_dir / backup_id
            if uncompressed_path.exists():
                return uncompressed_path
            else:
                raise BackupError(f"Backup files not found: {backup_id}")
    
    def _verify_backup_integrity(self, backup_path: Path, manifest: BackupManifest) -> None:
        """Verify backup integrity against manifest."""
        # Verify database checksum
        db_path = backup_path / "hearthlink.db"
        if db_path.exists():
            current_checksum = self._calculate_file_checksum(db_path)
            if current_checksum != manifest.database_checksum:
                raise BackupError("Database checksum verification failed")
        
        # Verify database integrity
        if db_path.exists():
            self._verify_database_integrity(db_path)
    
    def _restore_database(self, backup_path: Path) -> None:
        """Restore database from backup."""
        backup_db_path = backup_path / "hearthlink.db"
        
        if backup_db_path.exists():
            # Create backup directory if it doesn't exist
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy database file
            shutil.copy2(backup_db_path, self.database_path)
    
    def _restore_vault_storage(self, backup_path: Path) -> None:
        """Restore vault storage from backup."""
        backup_vault_path = backup_path / "vault_storage"
        
        if backup_vault_path.exists():
            # Remove existing vault storage
            if self.vault_path.exists():
                if self.vault_path.is_file():
                    self.vault_path.unlink()
                else:
                    shutil.rmtree(self.vault_path)
            
            # Restore vault storage
            if backup_vault_path.is_file():
                # Restore as file
                shutil.copy2(backup_vault_path, self.vault_path)
            else:
                # Restore as directory
                shutil.copytree(backup_vault_path, self.vault_path)
    
    def _restore_configuration(self, backup_path: Path) -> None:
        """Restore configuration from backup."""
        backup_config_path = backup_path / "config"
        
        if backup_config_path.exists():
            # Create config directory if it doesn't exist
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Copy configuration files
            for item in backup_config_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.config_path / item.name)
                elif item.is_dir():
                    dest_dir = self.config_path / item.name
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(item, dest_dir)
    
    def cleanup_old_backups(self) -> int:
        """
        Remove old backups based on retention policy.
        
        Returns:
            int: Number of backups removed
        """
        removed_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            # Get all backup manifests
            manifest_files = list(self.backup_dir.glob("*_manifest.json"))
            
            for manifest_file in manifest_files:
                try:
                    with open(manifest_file, 'r') as f:
                        manifest_data = json.load(f)
                    
                    backup_date = datetime.fromisoformat(manifest_data["timestamp"])
                    
                    if backup_date < cutoff_date:
                        backup_id = manifest_data["backup_id"]
                        
                        # Remove backup files
                        self._remove_backup_files(backup_id)
                        
                        # Remove manifest
                        manifest_file.unlink()
                        
                        removed_count += 1
                        
                        self.logger.logger.info("Old backup removed", 
                                              extra={"extra_fields": {
                                                  "event_type": "backup_cleanup",
                                                  "backup_id": backup_id,
                                                  "backup_date": backup_date.isoformat()
                                              }})
                
                except Exception as e:
                    self.logger.logger.warning(f"Failed to process manifest {manifest_file}: {e}")
            
            return removed_count
            
        except Exception as e:
            self.logger.log_error(e, "backup_cleanup_error")
            return removed_count
    
    def _remove_backup_files(self, backup_id: str) -> None:
        """Remove all files associated with a backup."""
        # Remove compressed archive
        archive_path = self.backup_dir / f"{backup_id}.tar.gz"
        if archive_path.exists():
            archive_path.unlink()
        
        # Remove uncompressed directory
        dir_path = self.backup_dir / backup_id
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    def list_backups(self) -> List[BackupManifest]:
        """List all available backups."""
        backups = []
        
        manifest_files = list(self.backup_dir.glob("*_manifest.json"))
        
        for manifest_file in manifest_files:
            try:
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                backups.append(BackupManifest(**manifest_data))
            except Exception as e:
                self.logger.logger.warning(f"Failed to load manifest {manifest_file}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        
        return backups
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get overall backup system status."""
        backups = self.list_backups()
        
        total_size = 0
        successful_backups = 0
        failed_backups = 0
        
        for backup in backups:
            if backup.status == "completed":
                successful_backups += 1
                total_size += backup.database_size + backup.vault_size
            else:
                failed_backups += 1
        
        return {
            "total_backups": len(backups),
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "total_backup_size": total_size,
            "backup_directory": str(self.backup_dir),
            "retention_days": self.retention_days,
            "last_successful_backup": backups[0].timestamp if backups and backups[0].status == "completed" else None
        }


def main():
    """Command-line interface for backup manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hearthlink Database Backup Manager")
    parser.add_argument("command", choices=["create", "restore", "list", "cleanup", "status"], 
                       help="Backup command to execute")
    parser.add_argument("--backup-id", help="Backup ID for restore command")
    parser.add_argument("--type", default="manual", help="Backup type (manual, scheduled)")
    
    args = parser.parse_args()
    
    try:
        manager = DatabaseBackupManager()
        
        if args.command == "create":
            manifest = manager.create_backup(args.type)
            print(f"✅ Backup created successfully: {manifest.backup_id}")
            print(f"   Database size: {manifest.database_size:,} bytes")
            print(f"   Vault files: {len(manifest.vault_files)}")
            print(f"   Duration: {manifest.backup_duration:.2f}s")
            
        elif args.command == "restore":
            if not args.backup_id:
                print("❌ --backup-id required for restore command")
                sys.exit(1)
            
            success = manager.restore_backup(args.backup_id)
            if success:
                print(f"✅ Backup restored successfully: {args.backup_id}")
            else:
                print(f"❌ Backup restoration failed: {args.backup_id}")
                sys.exit(1)
        
        elif args.command == "list":
            backups = manager.list_backups()
            if backups:
                print(f"📋 Available backups ({len(backups)}):")
                for backup in backups:
                    status_icon = "✅" if backup.status == "completed" else "❌"
                    print(f"   {status_icon} {backup.backup_id} - {backup.timestamp} ({backup.backup_type})")
                    print(f"      Database: {backup.database_size:,} bytes, Vault: {len(backup.vault_files)} files")
            else:
                print("📋 No backups found")
        
        elif args.command == "cleanup":
            removed = manager.cleanup_old_backups()
            print(f"🧹 Cleaned up {removed} old backups")
        
        elif args.command == "status":
            status = manager.get_backup_status()
            print(f"📊 Backup System Status:")
            print(f"   Total backups: {status['total_backups']}")
            print(f"   Successful: {status['successful_backups']}")
            print(f"   Failed: {status['failed_backups']}")
            print(f"   Total size: {status['total_backup_size']:,} bytes")
            print(f"   Retention: {status['retention_days']} days")
            if status['last_successful_backup']:
                print(f"   Last backup: {status['last_successful_backup']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()