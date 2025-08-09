#!/usr/bin/env python3
"""
HashiCorp Vault Automated Key Rotation System
Implements secure key cycling, alerting, and compliance monitoring for Hearthlink infrastructure
"""

import os
import sys
import json
import asyncio
import hvac
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/hearthlink/vault_rotation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RotationConfig:
    """Configuration for key rotation"""
    key_name: str
    rotation_interval_days: int
    max_key_versions: int
    notification_channels: List[str]
    critical_keys: bool = False
    pre_rotation_backup: bool = True

@dataclass
class RotationResult:
    """Result of a key rotation operation"""
    key_name: str
    old_version: int
    new_version: int
    rotation_time: str
    success: bool
    error_message: Optional[str] = None
    backup_location: Optional[str] = None

@dataclass
class VaultMetrics:
    """Vault operational metrics"""
    total_keys: int
    keys_rotated_24h: int
    failed_rotations: int
    avg_rotation_time_ms: float
    vault_health_status: str
    last_health_check: str

class VaultKeyRotationManager:
    """
    HashiCorp Vault Key Rotation Manager
    
    Provides automated key rotation capabilities for Hearthlink's security infrastructure:
    - Scheduled key rotation based on policies
    - Emergency rotation capabilities
    - Compliance monitoring and reporting
    - Automated alerting and notifications
    - Key version management and cleanup
    - Backup and recovery procedures
    """
    
    def __init__(
        self,
        vault_url: str = None,
        vault_token: str = None,
        config_path: str = "/etc/hearthlink/vault_rotation.json"
    ):
        """
        Initialize Vault Key Rotation Manager
        
        Args:
            vault_url: HashiCorp Vault server URL
            vault_token: Vault authentication token
            config_path: Path to rotation configuration file
        """
        # Environment configuration
        self.vault_url = vault_url or os.getenv('VAULT_ADDR', 'https://vault.hearthlink.local:8200')
        self.vault_token = vault_token or os.getenv('VAULT_TOKEN')
        self.config_path = config_path
        
        # Initialize Vault client
        self.vault_client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token
        )
        
        # Rotation configurations
        self.rotation_configs: Dict[str, RotationConfig] = {}
        self.load_rotation_config()
        
        # Metrics and monitoring
        self.metrics = VaultMetrics(
            total_keys=0,
            keys_rotated_24h=0,
            failed_rotations=0,
            avg_rotation_time_ms=0.0,
            vault_health_status="unknown",
            last_health_check=datetime.now().isoformat()
        )
        
        # Notification settings
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.hearthlink.local')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.alert_recipients = os.getenv('ALERT_RECIPIENTS', 'security@hearthlink.local').split(',')
        
        # Slack webhook for alerts
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        logger.info("Vault Key Rotation Manager initialized", extra={
            "vault_url": self.vault_url,
            "config_path": self.config_path,
            "total_configs": len(self.rotation_configs)
        })
    
    def load_rotation_config(self):
        """Load rotation configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                for key_name, config in config_data.get('rotation_configs', {}).items():
                    self.rotation_configs[key_name] = RotationConfig(
                        key_name=key_name,
                        rotation_interval_days=config.get('rotation_interval_days', 90),
                        max_key_versions=config.get('max_key_versions', 10),
                        notification_channels=config.get('notification_channels', ['email']),
                        critical_keys=config.get('critical_keys', False),
                        pre_rotation_backup=config.get('pre_rotation_backup', True)
                    )
                    
                logger.info(f"Loaded {len(self.rotation_configs)} rotation configurations")
            else:
                # Create default configuration
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Failed to load rotation configuration: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default rotation configuration"""
        default_configs = {
            "hearthlink-api-keys": {
                "rotation_interval_days": 30,
                "max_key_versions": 5,
                "notification_channels": ["email", "slack"],
                "critical_keys": True,
                "pre_rotation_backup": True
            },
            "database-credentials": {
                "rotation_interval_days": 60,
                "max_key_versions": 10,
                "notification_channels": ["email"],
                "critical_keys": True,
                "pre_rotation_backup": True
            },
            "llm-api-tokens": {
                "rotation_interval_days": 45,
                "max_key_versions": 7,
                "notification_channels": ["email", "slack"],
                "critical_keys": False,
                "pre_rotation_backup": True
            },
            "encryption-keys": {
                "rotation_interval_days": 90,
                "max_key_versions": 12,
                "notification_channels": ["email", "slack"],
                "critical_keys": True,
                "pre_rotation_backup": True
            }
        }
        
        # Create config directory
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Save default configuration
        with open(self.config_path, 'w') as f:
            json.dump({"rotation_configs": default_configs}, f, indent=2)
        
        # Load the default configurations
        self.load_rotation_config()
        
        logger.info("Created default rotation configuration")
    
    async def health_check(self) -> bool:
        """Perform Vault health check"""
        try:
            # Check Vault server health
            health_response = self.vault_client.sys.read_health_status()
            
            if health_response['sealed']:
                self.metrics.vault_health_status = "sealed"
                logger.error("Vault is sealed - cannot perform operations")
                await self.send_alert("CRITICAL: Vault is sealed", "Vault server is sealed and unavailable")
                return False
            
            # Check authentication
            if not self.vault_client.is_authenticated():
                self.metrics.vault_health_status = "unauthenticated"
                logger.error("Vault authentication failed")
                await self.send_alert("CRITICAL: Vault authentication failed", "Unable to authenticate with Vault server")
                return False
            
            # Check key engine accessibility
            try:
                self.vault_client.secrets.kv.v2.list_secrets(path="")
            except Exception as e:
                logger.warning(f"Key engine accessibility check failed: {e}")
            
            self.metrics.vault_health_status = "healthy"
            self.metrics.last_health_check = datetime.now().isoformat()
            
            logger.info("Vault health check passed")
            return True
            
        except Exception as e:
            self.metrics.vault_health_status = "error"
            logger.error(f"Vault health check failed: {e}")
            await self.send_alert("ERROR: Vault health check failed", f"Health check error: {e}")
            return False
    
    async def rotate_key(self, key_name: str, force: bool = False) -> RotationResult:
        """
        Rotate a specific key
        
        Args:
            key_name: Name of the key to rotate
            force: Force rotation regardless of schedule
            
        Returns:
            RotationResult: Result of the rotation operation
        """
        start_time = datetime.now()
        logger.info(f"Starting key rotation for: {key_name}")
        
        try:
            config = self.rotation_configs.get(key_name)
            if not config:
                error_msg = f"No rotation configuration found for key: {key_name}"
                logger.error(error_msg)
                return RotationResult(
                    key_name=key_name,
                    old_version=0,
                    new_version=0,
                    rotation_time=start_time.isoformat(),
                    success=False,
                    error_message=error_msg
                )
            
            # Check if rotation is needed (unless forced)
            if not force and not await self.is_rotation_needed(key_name, config):
                logger.info(f"Rotation not needed for {key_name}")
                return RotationResult(
                    key_name=key_name,
                    old_version=0,
                    new_version=0,
                    rotation_time=start_time.isoformat(),
                    success=True,
                    error_message="Rotation not needed"
                )
            
            # Get current key version
            current_version = await self.get_current_key_version(key_name)
            
            # Create backup if configured
            backup_location = None
            if config.pre_rotation_backup:
                backup_location = await self.backup_key(key_name, current_version)
            
            # Generate new key version
            new_version = await self.generate_new_key_version(key_name, config)
            
            # Update key in Vault
            await self.update_vault_key(key_name, new_version)
            
            # Clean up old versions if needed
            await self.cleanup_old_versions(key_name, config)
            
            # Calculate rotation time
            rotation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update metrics
            self.metrics.keys_rotated_24h += 1
            self.update_average_rotation_time(rotation_time_ms)
            
            result = RotationResult(
                key_name=key_name,
                old_version=current_version,
                new_version=new_version,
                rotation_time=start_time.isoformat(),
                success=True,
                backup_location=backup_location
            )
            
            # Send success notification
            await self.send_rotation_notification(result, config)
            
            logger.info(f"Key rotation completed successfully: {key_name}", extra={
                "old_version": current_version,
                "new_version": new_version,
                "rotation_time_ms": rotation_time_ms
            })
            
            return result
            
        except Exception as e:
            self.metrics.failed_rotations += 1
            error_msg = f"Key rotation failed for {key_name}: {e}"
            logger.error(error_msg)
            
            # Send failure alert
            await self.send_alert(f"KEY ROTATION FAILED: {key_name}", error_msg)
            
            return RotationResult(
                key_name=key_name,
                old_version=0,
                new_version=0,
                rotation_time=start_time.isoformat(),
                success=False,
                error_message=str(e)
            )
    
    async def is_rotation_needed(self, key_name: str, config: RotationConfig) -> bool:
        """Check if key rotation is needed based on schedule"""
        try:
            # Get key metadata
            key_metadata = self.vault_client.secrets.kv.v2.read_secret_metadata(path=key_name)
            
            if not key_metadata:
                return True  # New key, needs initial creation
            
            # Get last rotation time
            created_time = key_metadata['data']['created_time']
            last_rotation = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            
            # Check if rotation interval has passed
            rotation_due = datetime.now() - timedelta(days=config.rotation_interval_days)
            
            return last_rotation < rotation_due
            
        except Exception as e:
            logger.warning(f"Could not determine rotation schedule for {key_name}: {e}")
            return True  # Err on the side of caution
    
    async def get_current_key_version(self, key_name: str) -> int:
        """Get current version of a key"""
        try:
            metadata = self.vault_client.secrets.kv.v2.read_secret_metadata(path=key_name)
            return metadata['data']['current_version']
        except Exception:
            return 0  # New key
    
    async def backup_key(self, key_name: str, version: int) -> str:
        """Create backup of current key version"""
        try:
            backup_dir = f"/var/backups/hearthlink/vault/{datetime.now().strftime('%Y-%m-%d')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Read current key
            current_key = self.vault_client.secrets.kv.v2.read_secret_version(
                path=key_name,
                version=version
            )
            
            # Save backup
            backup_filename = f"{key_name}_v{version}_{int(time.time())}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            with open(backup_path, 'w') as f:
                json.dump(current_key['data'], f, indent=2)
            
            # Set secure permissions
            os.chmod(backup_path, 0o600)
            
            logger.info(f"Created backup for {key_name} at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup key {key_name}: {e}")
            raise
    
    async def generate_new_key_version(self, key_name: str, config: RotationConfig) -> int:
        """Generate new version of a key"""
        try:
            # Key generation logic based on key type
            if "database" in key_name.lower():
                new_key_data = await self.generate_database_credentials()
            elif "api" in key_name.lower():
                new_key_data = await self.generate_api_key()
            elif "encryption" in key_name.lower():
                new_key_data = await self.generate_encryption_key()
            else:
                new_key_data = await self.generate_generic_key()
            
            # Get next version number
            current_version = await self.get_current_key_version(key_name)
            new_version = current_version + 1
            
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to generate new key version for {key_name}: {e}")
            raise
    
    async def generate_database_credentials(self) -> Dict[str, str]:
        """Generate new database credentials"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        return {
            "username": f"hearthlink_user_{int(time.time())}",
            "password": password,
            "connection_string": f"postgresql://hearthlink_user_{int(time.time())}:{password}@localhost:5432/hearthlink",
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_api_key(self) -> Dict[str, str]:
        """Generate new API key"""
        import secrets
        
        api_key = f"hlk_{secrets.token_urlsafe(32)}"
        
        return {
            "api_key": api_key,
            "key_id": f"key_{int(time.time())}",
            "permissions": ["read", "write", "admin"],
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
        }
    
    async def generate_encryption_key(self) -> Dict[str, str]:
        """Generate new encryption key"""
        import secrets
        
        encryption_key = secrets.token_bytes(32).hex()
        
        return {
            "key": encryption_key,
            "algorithm": "AES-256",
            "key_id": f"enc_{int(time.time())}",
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_generic_key(self) -> Dict[str, str]:
        """Generate generic secure key"""
        import secrets
        
        return {
            "key": secrets.token_urlsafe(64),
            "generated_at": datetime.now().isoformat()
        }
    
    async def update_vault_key(self, key_name: str, new_version: int):
        """Update key in Vault with new version"""
        try:
            # Generate key data based on key type
            config = self.rotation_configs[key_name]
            
            if "database" in key_name.lower():
                key_data = await self.generate_database_credentials()
            elif "api" in key_name.lower():
                key_data = await self.generate_api_key()
            elif "encryption" in key_name.lower():
                key_data = await self.generate_encryption_key()
            else:
                key_data = await self.generate_generic_key()
            
            # Store new version in Vault
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=key_name,
                secret=key_data
            )
            
            logger.info(f"Updated Vault key {key_name} to version {new_version}")
            
        except Exception as e:
            logger.error(f"Failed to update Vault key {key_name}: {e}")
            raise
    
    async def cleanup_old_versions(self, key_name: str, config: RotationConfig):
        """Clean up old key versions beyond retention limit"""
        try:
            metadata = self.vault_client.secrets.kv.v2.read_secret_metadata(path=key_name)
            current_version = metadata['data']['current_version']
            
            # Delete versions beyond retention limit
            versions_to_delete = []
            for version in range(1, current_version - config.max_key_versions + 1):
                if version > 0:
                    versions_to_delete.append(version)
            
            if versions_to_delete:
                self.vault_client.secrets.kv.v2.delete_secret_versions(
                    path=key_name,
                    versions=versions_to_delete
                )
                
                logger.info(f"Cleaned up {len(versions_to_delete)} old versions for {key_name}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup old versions for {key_name}: {e}")
    
    async def send_rotation_notification(self, result: RotationResult, config: RotationConfig):
        """Send notification about successful rotation"""
        subject = f"Key Rotation Completed: {result.key_name}"
        message = f"""
Key rotation completed successfully:

Key Name: {result.key_name}
Old Version: {result.old_version}
New Version: {result.new_version}
Rotation Time: {result.rotation_time}
Backup Location: {result.backup_location or 'None'}

This is an automated notification from the Hearthlink Vault Key Rotation system.
        """
        
        # Send notifications based on configured channels
        for channel in config.notification_channels:
            if channel == "email":
                await self.send_email_notification(subject, message)
            elif channel == "slack":
                await self.send_slack_notification(subject, message)
    
    async def send_alert(self, subject: str, message: str):
        """Send critical alert notification"""
        logger.critical(f"ALERT: {subject} - {message}")
        
        # Send to all configured notification channels
        await self.send_email_notification(f"ALERT: {subject}", message)
        if self.slack_webhook_url:
            await self.send_slack_notification(f"🚨 ALERT: {subject}", message)
    
    async def send_email_notification(self, subject: str, message: str):
        """Send email notification"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, skipping email notification")
                return
            
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(self.alert_recipients)
            msg['Subject'] = f"[Hearthlink Vault] {subject}"
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, self.alert_recipients, text)
            server.quit()
            
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def send_slack_notification(self, subject: str, message: str):
        """Send Slack notification"""
        try:
            if not self.slack_webhook_url:
                logger.warning("Slack webhook not configured, skipping Slack notification")
                return
            
            payload = {
                "text": f"*{subject}*",
                "attachments": [
                    {
                        "color": "good" if "Completed" in subject else "danger",
                        "text": message,
                        "footer": "Hearthlink Vault Key Rotation",
                        "ts": int(time.time())
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def update_average_rotation_time(self, rotation_time_ms: float):
        """Update average rotation time metric"""
        if self.metrics.avg_rotation_time_ms == 0:
            self.metrics.avg_rotation_time_ms = rotation_time_ms
        else:
            # Simple moving average
            self.metrics.avg_rotation_time_ms = (
                (self.metrics.avg_rotation_time_ms + rotation_time_ms) / 2
            )
    
    async def emergency_rotation(self, key_name: str) -> RotationResult:
        """Perform emergency key rotation"""
        logger.critical(f"EMERGENCY ROTATION INITIATED for {key_name}")
        
        # Send immediate alert
        await self.send_alert(
            f"Emergency Rotation Started: {key_name}",
            f"Emergency key rotation has been initiated for {key_name}. This indicates a potential security incident."
        )
        
        # Force rotation
        result = await self.rotate_key(key_name, force=True)
        
        if result.success:
            await self.send_alert(
                f"Emergency Rotation Completed: {key_name}",
                f"Emergency rotation completed successfully for {key_name}. New version: {result.new_version}"
            )
        else:
            await self.send_alert(
                f"Emergency Rotation FAILED: {key_name}",
                f"CRITICAL: Emergency rotation failed for {key_name}. Error: {result.error_message}"
            )
        
        return result
    
    async def rotate_all_keys(self) -> List[RotationResult]:
        """Rotate all configured keys based on their schedules"""
        logger.info("Starting scheduled rotation for all keys")
        
        results = []
        for key_name in self.rotation_configs.keys():
            try:
                result = await self.rotate_key(key_name)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to rotate key {key_name}: {e}")
                results.append(RotationResult(
                    key_name=key_name,
                    old_version=0,
                    new_version=0,
                    rotation_time=datetime.now().isoformat(),
                    success=False,
                    error_message=str(e)
                ))
        
        # Generate summary report
        successful_rotations = [r for r in results if r.success]
        failed_rotations = [r for r in results if not r.success]
        
        summary = f"""
Scheduled Key Rotation Summary:
- Total keys processed: {len(results)}
- Successful rotations: {len(successful_rotations)}
- Failed rotations: {len(failed_rotations)}

Failed rotations:
{chr(10).join([f"  - {r.key_name}: {r.error_message}" for r in failed_rotations])}
        """
        
        if failed_rotations:
            await self.send_alert("Key Rotation Summary - Failures Detected", summary)
        else:
            logger.info("All scheduled rotations completed successfully")
        
        return results
    
    def get_metrics(self) -> VaultMetrics:
        """Get current metrics"""
        # Update total keys count
        try:
            self.metrics.total_keys = len(self.rotation_configs)
        except Exception:
            pass
        
        return self.metrics
    
    async def start_scheduler(self):
        """Start the key rotation scheduler"""
        logger.info("Starting Vault key rotation scheduler")
        
        # Schedule daily health checks
        schedule.every().day.at("06:00").do(lambda: asyncio.create_task(self.health_check()))
        
        # Schedule daily key rotation checks
        schedule.every().day.at("02:00").do(lambda: asyncio.create_task(self.rotate_all_keys()))
        
        # Schedule weekly metrics reporting
        schedule.every().monday.at("09:00").do(lambda: asyncio.create_task(self.send_metrics_report()))
        
        # Main scheduler loop
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    async def send_metrics_report(self):
        """Send weekly metrics report"""
        metrics = self.get_metrics()
        
        report = f"""
Weekly Vault Key Rotation Metrics Report:

System Health:
- Vault Status: {metrics.vault_health_status}
- Last Health Check: {metrics.last_health_check}

Key Statistics:
- Total Keys Managed: {metrics.total_keys}
- Keys Rotated (24h): {metrics.keys_rotated_24h}
- Failed Rotations: {metrics.failed_rotations}
- Average Rotation Time: {metrics.avg_rotation_time_ms:.2f}ms

Configuration:
- Rotation Configs: {len(self.rotation_configs)}
- Critical Keys: {sum(1 for c in self.rotation_configs.values() if c.critical_keys)}

This is an automated weekly report from the Hearthlink Vault Key Rotation system.
        """
        
        await self.send_email_notification("Weekly Vault Metrics Report", report)
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Vault Key Rotation Manager cleanup completed")

# CLI Interface
async def main():
    """Main CLI interface for Vault key rotation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hearthlink Vault Key Rotation Manager")
    parser.add_argument("--rotate", help="Rotate specific key")
    parser.add_argument("--rotate-all", action="store_true", help="Rotate all keys")
    parser.add_argument("--emergency", help="Emergency rotation for specific key")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    parser.add_argument("--metrics", action="store_true", help="Show metrics")
    parser.add_argument("--scheduler", action="store_true", help="Start scheduler daemon")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = VaultKeyRotationManager()
    
    try:
        if args.health_check:
            healthy = await manager.health_check()
            print(f"Vault Health: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
            
        elif args.metrics:
            metrics = manager.get_metrics()
            print("Vault Key Rotation Metrics:")
            print(json.dumps(asdict(metrics), indent=2))
            
        elif args.rotate:
            result = await manager.rotate_key(args.rotate)
            print(f"Rotation Result: {'✅ Success' if result.success else '❌ Failed'}")
            print(json.dumps(asdict(result), indent=2))
            
        elif args.rotate_all:
            results = await manager.rotate_all_keys()
            successful = sum(1 for r in results if r.success)
            print(f"Rotation Summary: {successful}/{len(results)} successful")
            
        elif args.emergency:
            result = await manager.emergency_rotation(args.emergency)
            print(f"Emergency Rotation: {'✅ Success' if result.success else '❌ Failed'}")
            print(json.dumps(asdict(result), indent=2))
            
        elif args.scheduler:
            print("Starting Vault key rotation scheduler...")
            await manager.start_scheduler()
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())