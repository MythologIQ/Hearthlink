#!/usr/bin/env python3
"""
SPEC-2 Phase 2: Vault Key Rotation CLI
Command-line interface for vault key rotation operations.
"""

import asyncio
import click
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.vault.key_rotation import VaultKeyRotationManager, RotationPolicy
from src.vault.vault_rotation_api import initialize_rotation_system

# CLI Configuration
DEFAULT_CONFIG_PATH = "config/vault_config.json"
DEFAULT_DB_PATH = "hearthlink_data/vault_keys.db"

@click.group()
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, help='Path to vault configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """Hearthlink Vault Key Rotation CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    
    # Load configuration
    try:
        if Path(config).exists():
            with open(config) as f:
                ctx.obj['config'] = json.load(f)
        else:
            # Default configuration
            ctx.obj['config'] = {
                "storage": {"file_path": "hearthlink_data/vault.db"},
                "encryption": {"key_file": "hearthlink_data/vault_key.bin"},
                "key_rotation": {
                    "rotation_interval_days": 30,
                    "max_key_versions": 3,
                    "auto_rotation_enabled": True,
                    "performance_threshold_seconds": 5.0,
                    "backup_old_keys": True
                },
                "schema_version": "1.0"
            }
            click.echo(f"⚠️  Configuration file not found, using defaults")
    except Exception as e:
        click.echo(f"❌ Failed to load configuration: {e}", err=True)
        sys.exit(1)

def get_rotation_manager(ctx) -> VaultKeyRotationManager:
    """Get initialized rotation manager"""
    try:
        return VaultKeyRotationManager(ctx.obj['config'])
    except Exception as e:
        click.echo(f"❌ Failed to initialize rotation manager: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def status(ctx):
    """Show current key rotation status"""
    manager = get_rotation_manager(ctx)
    
    try:
        current_key = manager.get_current_key()
        should_rotate, reason = manager.should_rotate()
        metadata = manager.export_key_metadata()
        
        click.echo("🔐 Vault Key Rotation Status")
        click.echo("=" * 40)
        click.echo(f"Current Key Version: {current_key.version}")
        click.echo(f"Key Created: {current_key.created_at}")
        click.echo(f"Should Rotate: {'Yes' if should_rotate else 'No'}")
        click.echo(f"Reason: {reason}")
        click.echo(f"Auto Rotation: {'Enabled' if manager.policy.auto_rotation_enabled else 'Disabled'}")
        click.echo(f"Rotation Interval: {manager.policy.rotation_interval_days} days")
        click.echo(f"Max Key Versions: {manager.policy.max_key_versions}")
        click.echo(f"Total Stored Versions: {metadata.get('total_versions', 0)}")
        
        if ctx.obj['verbose']:
            click.echo("\n📊 Metrics:")
            metrics = metadata.get('metrics', {})
            for key, value in metrics.items():
                click.echo(f"  {key}: {value}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get status: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force rotation even if not due')
@click.option('--trigger', default='cli', help='Trigger type for logging')
@click.pass_context
def rotate(ctx, force, trigger):
    """Perform key rotation"""
    manager = get_rotation_manager(ctx)
    
    if not force:
        should_rotate, reason = manager.should_rotate()
        if not should_rotate:
            click.echo(f"⏳ Rotation not needed: {reason}")
            if not click.confirm("Force rotation anyway?"):
                return
    
    click.echo("🔄 Starting key rotation...")
    start_time = time.time()
    
    try:
        result = asyncio.run(manager.rotate_key(trigger, force))
        duration = time.time() - start_time
        
        if result['success']:
            click.echo(f"✅ Key rotation completed successfully!")
            click.echo(f"   Duration: {result['duration_seconds']:.2f}s")
            click.echo(f"   Old Version: {result['old_version']}")
            click.echo(f"   New Version: {result['new_version']}")
            
            if duration > manager.policy.performance_threshold_seconds:
                click.echo(f"⚠️  Rotation took {duration:.2f}s, exceeding threshold of {manager.policy.performance_threshold_seconds}s")
        else:
            click.echo(f"⏭️  Rotation skipped: {result.get('reason', 'Unknown reason')}")
            
    except Exception as e:
        click.echo(f"❌ Rotation failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--limit', '-l', default=10, help='Number of history entries to show')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def history(ctx, limit, format):
    """Show key rotation history"""
    manager = get_rotation_manager(ctx)
    
    try:
        history_data = manager.get_rotation_history(limit=limit)
        
        if format == 'json':
            click.echo(json.dumps(history_data, indent=2))
            return
        
        if not history_data:
            click.echo("📋 No rotation history found")
            return
        
        click.echo("📋 Key Rotation History")
        click.echo("=" * 80)
        click.echo(f"{'Timestamp':<20} {'Old Ver':<8} {'New Ver':<8} {'Trigger':<15} {'Duration':<10} {'Status':<10}")
        click.echo("-" * 80)
        
        for entry in history_data:
            timestamp = entry['timestamp'][:19]  # Truncate timestamp
            old_ver = entry['old_version'] or 'N/A'
            new_ver = entry['new_version'] or 'N/A'
            trigger = entry['trigger_type'][:14]  # Truncate trigger
            duration = f"{entry['duration_seconds']:.2f}s"
            status = "✅ Success" if entry['success'] else "❌ Failed"
            
            click.echo(f"{timestamp:<20} {old_ver:<8} {new_ver:<8} {trigger:<15} {duration:<10} {status:<10}")
            
            if not entry['success'] and entry.get('error_message'):
                click.echo(f"   Error: {entry['error_message']}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get history: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('version', type=int)
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def rollback(ctx, version, confirm):
    """Rollback to a previous key version (EMERGENCY USE ONLY)"""
    manager = get_rotation_manager(ctx)
    
    try:
        # Verify target version exists
        target_key = manager.get_key_by_version(version)
        if not target_key:
            click.echo(f"❌ Key version {version} not found", err=True)
            sys.exit(1)
        
        current_key = manager.get_current_key()
        
        click.echo("⚠️  WARNING: KEY ROLLBACK OPERATION")
        click.echo("=" * 40)
        click.echo(f"Current Version: {current_key.version}")
        click.echo(f"Target Version: {version}")
        click.echo(f"Target Created: {target_key.created_at}")
        click.echo("\n🚨 This operation will:")
        click.echo("   • Deactivate the current key")
        click.echo("   • Reactivate the target key version")
        click.echo("   • Re-encrypt all vault data")
        click.echo("   • This should only be used in emergencies!")
        
        if not confirm and not click.confirm("\nProceed with rollback?"):
            click.echo("Rollback cancelled")
            return
        
        click.echo(f"🔄 Rolling back to version {version}...")
        start_time = time.time()
        
        result = asyncio.run(manager.rollback_to_version(version))
        duration = time.time() - start_time
        
        if result['success']:
            click.echo(f"✅ Rollback completed successfully!")
            click.echo(f"   Duration: {result['duration_seconds']:.2f}s")
            click.echo(f"   From Version: {result['from_version']}")
            click.echo(f"   To Version: {result['to_version']}")
        else:
            click.echo(f"❌ Rollback failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Rollback failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def versions(ctx):
    """List all stored key versions"""
    manager = get_rotation_manager(ctx)
    
    try:
        versions_data = manager.list_key_versions()
        
        if not versions_data:
            click.echo("📋 No key versions found")
            return
        
        click.echo("🔑 Stored Key Versions")
        click.echo("=" * 70)
        click.echo(f"{'Version':<8} {'Created':<20} {'Rotated':<20} {'Active':<8} {'Metadata':<15}")
        click.echo("-" * 70)
        
        for version_data in versions_data:
            version = version_data['version']
            created = version_data['created_at'][:19]  # Truncate
            rotated = (version_data['rotated_at'][:19] if version_data['rotated_at'] else 'N/A')
            active = "✅ Yes" if version_data['is_active'] else "❌ No"
            metadata = json.dumps(version_data.get('metadata', {}))[:14] + "..."
            
            click.echo(f"{version:<8} {created:<20} {rotated:<20} {active:<8} {metadata:<15}")
        
    except Exception as e:
        click.echo(f"❌ Failed to list versions: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def verify(ctx):
    """Verify key integrity and functionality"""
    manager = get_rotation_manager(ctx)
    
    click.echo("🔍 Verifying key integrity...")
    
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets
        
        versions = manager.list_key_versions()
        test_data = b"Hearthlink key rotation verification test"
        
        results = []
        for version_info in versions:
            version = version_info['version']
            try:
                key_version = manager.get_key_by_version(version)
                if not key_version:
                    results.append((version, False, "Key not found"))
                    continue
                
                # Test encryption/decryption
                aesgcm = AESGCM(key_version.key_data)
                nonce = secrets.token_bytes(12)
                ciphertext = aesgcm.encrypt(nonce, test_data, None)
                decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                
                if decrypted == test_data:
                    results.append((version, True, "Valid"))
                else:
                    results.append((version, False, "Decryption mismatch"))
                    
            except Exception as e:
                results.append((version, False, str(e)))
        
        # Display results
        click.echo("\n📊 Verification Results")
        click.echo("=" * 50)
        click.echo(f"{'Version':<8} {'Status':<10} {'Notes':<30}")
        click.echo("-" * 50)
        
        valid_count = 0
        for version, valid, notes in results:
            status = "✅ Valid" if valid else "❌ Invalid"
            click.echo(f"{version:<8} {status:<10} {notes:<30}")
            if valid:
                valid_count += 1
        
        click.echo("=" * 50)
        click.echo(f"Total: {len(results)} versions, {valid_count} valid, {len(results) - valid_count} invalid")
        
        if valid_count == len(results):
            click.echo("✅ All key versions verified successfully")
        else:
            click.echo("❌ Some key versions failed verification", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Verification failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--interval', type=int, help='Rotation interval in days')
@click.option('--max-versions', type=int, help='Maximum key versions to retain')
@click.option('--auto/--no-auto', help='Enable/disable auto rotation')
@click.option('--threshold', type=float, help='Performance threshold in seconds')
@click.pass_context
def policy(ctx, interval, max_versions, auto, threshold):
    """Show or update rotation policy"""
    manager = get_rotation_manager(ctx)
    
    # If no options provided, show current policy
    if not any([interval, max_versions, auto is not None, threshold]):
        click.echo("📋 Current Rotation Policy")
        click.echo("=" * 30)
        click.echo(f"Rotation Interval: {manager.policy.rotation_interval_days} days")
        click.echo(f"Max Key Versions: {manager.policy.max_key_versions}")
        click.echo(f"Auto Rotation: {'Enabled' if manager.policy.auto_rotation_enabled else 'Disabled'}")
        click.echo(f"Performance Threshold: {manager.policy.performance_threshold_seconds}s")
        click.echo(f"Backup Old Keys: {'Yes' if manager.policy.backup_old_keys else 'No'}")
        return
    
    # Update policy
    updates = []
    if interval is not None:
        manager.policy.rotation_interval_days = interval
        updates.append(f"Rotation interval: {interval} days")
    
    if max_versions is not None:
        manager.policy.max_key_versions = max_versions
        updates.append(f"Max versions: {max_versions}")
    
    if auto is not None:
        manager.policy.auto_rotation_enabled = auto
        updates.append(f"Auto rotation: {'Enabled' if auto else 'Disabled'}")
    
    if threshold is not None:
        manager.policy.performance_threshold_seconds = threshold
        updates.append(f"Performance threshold: {threshold}s")
    
    click.echo("✅ Policy updated:")
    for update in updates:
        click.echo(f"   • {update}")

@cli.command()
@click.pass_context
def metrics(ctx):
    """Show Prometheus metrics"""
    manager = get_rotation_manager(ctx)
    
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        
        click.echo("📊 Prometheus Metrics")
        click.echo("=" * 40)
        
        metrics_output = generate_latest().decode('utf-8')
        click.echo(metrics_output)
        
    except ImportError:
        click.echo("❌ Prometheus client not available", err=True)
    except Exception as e:
        click.echo(f"❌ Failed to generate metrics: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for backup')
@click.pass_context
def backup(ctx, output):
    """Backup key rotation data"""
    manager = get_rotation_manager(ctx)
    
    try:
        metadata = manager.export_key_metadata()
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "vault_config": ctx.obj['config'],
            "key_metadata": metadata,
            "backup_version": "1.0"
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(backup_data, f, indent=2)
            click.echo(f"✅ Backup saved to {output}")
        else:
            click.echo(json.dumps(backup_data, indent=2))
        
    except Exception as e:
        click.echo(f"❌ Backup failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--watch', '-w', is_flag=True, help='Watch for changes (continuous monitoring)')
@click.option('--interval', default=60, help='Watch interval in seconds')
@click.pass_context
def monitor(ctx, watch, interval):
    """Monitor key rotation system"""
    manager = get_rotation_manager(ctx)
    
    def show_status():
        try:
            current_key = manager.get_current_key()
            should_rotate, reason = manager.should_rotate()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            click.echo(f"[{timestamp}] Version: {current_key.version}, " +
                      f"Rotate: {'Yes' if should_rotate else 'No'}, Reason: {reason}")
            
        except Exception as e:
            click.echo(f"❌ Monitor error: {e}", err=True)
    
    if watch:
        click.echo("👁️  Starting continuous monitoring...")
        click.echo("   Press Ctrl+C to stop")
        try:
            while True:
                show_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            click.echo("\n👋 Monitoring stopped")
    else:
        show_status()

if __name__ == '__main__':
    cli()