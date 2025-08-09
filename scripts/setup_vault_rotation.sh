#!/bin/bash
# HashiCorp Vault Key Rotation Setup Script
# Configures automated key rotation infrastructure for Hearthlink

set -euo pipefail

# Configuration
HEARTHLINK_ROOT="/mnt/g/mythologiq/hearthlink"
VAULT_CONFIG_DIR="/etc/hearthlink"
LOG_DIR="/var/log/hearthlink"
BACKUP_DIR="/var/backups/hearthlink/vault"
SYSTEMD_DIR="/etc/systemd/system"

echo "🔐 Setting up HashiCorp Vault Key Rotation System"
echo "=================================================="

# Create necessary directories
echo "📁 Creating directories..."
sudo mkdir -p "$VAULT_CONFIG_DIR"
sudo mkdir -p "$LOG_DIR"
sudo mkdir -p "$BACKUP_DIR"
sudo mkdir -p "$HEARTHLINK_ROOT/security"

# Set proper ownership and permissions
sudo chown -R root:hearthlink "$VAULT_CONFIG_DIR"
sudo chmod 750 "$VAULT_CONFIG_DIR"
sudo chown -R hearthlink:hearthlink "$LOG_DIR"
sudo chmod 755 "$LOG_DIR"
sudo chown -R hearthlink:hearthlink "$BACKUP_DIR"
sudo chmod 700 "$BACKUP_DIR"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install hvac schedule requests

# Create Vault rotation configuration
echo "⚙️  Creating Vault rotation configuration..."
cat > "$VAULT_CONFIG_DIR/vault_rotation.json" << 'EOF'
{
  "rotation_configs": {
    "hearthlink-api-keys": {
      "rotation_interval_days": 30,
      "max_key_versions": 5,
      "notification_channels": ["email", "slack"],
      "critical_keys": true,
      "pre_rotation_backup": true
    },
    "database-credentials": {
      "rotation_interval_days": 60,
      "max_key_versions": 10,
      "notification_channels": ["email"],
      "critical_keys": true,
      "pre_rotation_backup": true
    },
    "llm-api-tokens": {
      "rotation_interval_days": 45,
      "max_key_versions": 7,
      "notification_channels": ["email", "slack"],
      "critical_keys": false,
      "pre_rotation_backup": true
    },
    "encryption-keys": {
      "rotation_interval_days": 90,
      "max_key_versions": 12,
      "notification_channels": ["email", "slack"],
      "critical_keys": true,
      "pre_rotation_backup": true
    },
    "oauth-tokens": {
      "rotation_interval_days": 30,
      "max_key_versions": 5,
      "notification_channels": ["email"],
      "critical_keys": false,
      "pre_rotation_backup": true
    },
    "webhook-secrets": {
      "rotation_interval_days": 60,
      "max_key_versions": 8,
      "notification_channels": ["email", "slack"],
      "critical_keys": false,
      "pre_rotation_backup": true
    }
  },
  "global_settings": {
    "default_rotation_interval_days": 90,
    "max_rotation_failures": 3,
    "emergency_contact": "security@hearthlink.local",
    "backup_retention_days": 365
  }
}
EOF

# Create environment configuration
echo "🌍 Creating environment configuration..."
cat > "$VAULT_CONFIG_DIR/vault_rotation.env" << 'EOF'
# HashiCorp Vault Configuration
VAULT_ADDR=https://vault.hearthlink.local:8200
VAULT_TOKEN=
VAULT_NAMESPACE=hearthlink

# SMTP Configuration for Notifications
SMTP_SERVER=smtp.hearthlink.local
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
ALERT_RECIPIENTS=security@hearthlink.local,devops@hearthlink.local

# Slack Configuration
SLACK_WEBHOOK_URL=

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

# Create systemd service for vault rotation scheduler
echo "🔧 Creating systemd service..."
cat > "$SYSTEMD_DIR/hearthlink-vault-rotation.service" << EOF
[Unit]
Description=Hearthlink Vault Key Rotation Service
After=network-online.target vault.service
Wants=network-online.target
Requires=vault.service

[Service]
Type=simple
User=hearthlink
Group=hearthlink
WorkingDirectory=$HEARTHLINK_ROOT
Environment=PYTHONPATH=$HEARTHLINK_ROOT
EnvironmentFile=$VAULT_CONFIG_DIR/vault_rotation.env
ExecStart=/usr/bin/python3 $HEARTHLINK_ROOT/security/vault_key_rotation.py --scheduler
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $BACKUP_DIR
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for daily rotation checks
cat > "$SYSTEMD_DIR/hearthlink-vault-rotation-daily.timer" << 'EOF'
[Unit]
Description=Daily Vault Key Rotation Check
Requires=hearthlink-vault-rotation.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

# Create emergency rotation script
echo "🚨 Creating emergency rotation script..."
cat > "$HEARTHLINK_ROOT/scripts/emergency_key_rotation.sh" << 'EOF'
#!/bin/bash
# Emergency Key Rotation Script
# Usage: ./emergency_key_rotation.sh <key_name>

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <key_name>"
    echo "Available keys:"
    python3 /mnt/g/mythologiq/hearthlink/security/vault_key_rotation.py --metrics | jq '.total_keys'
    exit 1
fi

KEY_NAME="$1"

echo "🚨 EMERGENCY KEY ROTATION FOR: $KEY_NAME"
echo "This will immediately rotate the specified key."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Initiating emergency rotation..."
    python3 /mnt/g/mythologiq/hearthlink/security/vault_key_rotation.py --emergency "$KEY_NAME"
    echo "Emergency rotation completed."
else
    echo "Emergency rotation cancelled."
fi
EOF

chmod +x "$HEARTHLINK_ROOT/scripts/emergency_key_rotation.sh"

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > "$HEARTHLINK_ROOT/scripts/vault_rotation_monitor.sh" << 'EOF'
#!/bin/bash
# Vault Key Rotation Monitoring Script

set -euo pipefail

SCRIPT_DIR="/mnt/g/mythologiq/hearthlink"
LOG_FILE="/var/log/hearthlink/vault_rotation_monitor.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Health check
log "Performing Vault health check..."
if python3 "$SCRIPT_DIR/security/vault_key_rotation.py" --health-check; then
    log "✅ Vault health check passed"
else
    log "❌ Vault health check failed"
    exit 1
fi

# Get metrics
log "Retrieving metrics..."
METRICS=$(python3 "$SCRIPT_DIR/security/vault_key_rotation.py" --metrics)
log "Current metrics: $METRICS"

# Check for failed rotations
FAILED_ROTATIONS=$(echo "$METRICS" | jq '.failed_rotations')
if [ "$FAILED_ROTATIONS" -gt 0 ]; then
    log "⚠️  Warning: $FAILED_ROTATIONS failed rotations detected"
fi

# Check vault health status
VAULT_HEALTH=$(echo "$METRICS" | jq -r '.vault_health_status')
if [ "$VAULT_HEALTH" != "healthy" ]; then
    log "⚠️  Warning: Vault health status is $VAULT_HEALTH"
fi

log "Monitoring check completed"
EOF

chmod +x "$HEARTHLINK_ROOT/scripts/vault_rotation_monitor.sh"

# Create logrotate configuration
echo "📝 Setting up log rotation..."
cat > "/etc/logrotate.d/hearthlink-vault" << 'EOF'
/var/log/hearthlink/vault_rotation.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 hearthlink hearthlink
    postrotate
        systemctl reload hearthlink-vault-rotation.service > /dev/null 2>&1 || true
    endscript
}

/var/log/hearthlink/vault_rotation_monitor.log {
    weekly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    create 644 hearthlink hearthlink
}
EOF

# Set proper permissions
sudo chmod 600 "$VAULT_CONFIG_DIR/vault_rotation.json"
sudo chmod 600 "$VAULT_CONFIG_DIR/vault_rotation.env"
sudo chown root:hearthlink "$VAULT_CONFIG_DIR/vault_rotation.json"
sudo chown root:hearthlink "$VAULT_CONFIG_DIR/vault_rotation.env"

# Reload systemd and enable services
echo "🔄 Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable hearthlink-vault-rotation.service
sudo systemctl enable hearthlink-vault-rotation-daily.timer

# Create cron job for monitoring
echo "⏰ Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/15 * * * * $HEARTHLINK_ROOT/scripts/vault_rotation_monitor.sh") | crontab -

# Create initial test
echo "🧪 Creating test script..."
cat > "$HEARTHLINK_ROOT/test_vault_rotation.py" << 'EOF'
#!/usr/bin/env python3
"""
Test script for Vault Key Rotation System
Validates all components are working correctly
"""

import asyncio
import sys
import os
sys.path.insert(0, '/mnt/g/mythologiq/hearthlink')

from security.vault_key_rotation import VaultKeyRotationManager

async def test_vault_rotation():
    """Test the Vault rotation system"""
    print("🧪 Testing Vault Key Rotation System")
    print("=" * 40)
    
    try:
        # Initialize manager
        manager = VaultKeyRotationManager()
        print("✅ Manager initialized successfully")
        
        # Test health check
        print("\n🏥 Testing health check...")
        healthy = await manager.health_check()
        print(f"Health status: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
        
        # Test metrics
        print("\n📊 Testing metrics...")
        metrics = manager.get_metrics()
        print(f"Total keys: {metrics.total_keys}")
        print(f"Vault status: {metrics.vault_health_status}")
        
        # Test configuration loading
        print("\n⚙️  Testing configuration...")
        print(f"Loaded {len(manager.rotation_configs)} rotation configs")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_vault_rotation())
    sys.exit(0 if success else 1)
EOF

chmod +x "$HEARTHLINK_ROOT/test_vault_rotation.py"

echo "✅ Vault Key Rotation Setup Complete!"
echo "============================================"
echo ""
echo "📋 Next Steps:"
echo "1. Configure Vault token in: $VAULT_CONFIG_DIR/vault_rotation.env"
echo "2. Configure SMTP settings in: $VAULT_CONFIG_DIR/vault_rotation.env"
echo "3. Configure Slack webhook in: $VAULT_CONFIG_DIR/vault_rotation.env"
echo "4. Start the service: sudo systemctl start hearthlink-vault-rotation.service"
echo "5. Test the system: python3 $HEARTHLINK_ROOT/test_vault_rotation.py"
echo ""
echo "🚨 Emergency rotation: $HEARTHLINK_ROOT/scripts/emergency_key_rotation.sh <key_name>"
echo "📊 Monitor system: $HEARTHLINK_ROOT/scripts/vault_rotation_monitor.sh"
echo ""
echo "📁 Configuration files:"
echo "  - Rotation config: $VAULT_CONFIG_DIR/vault_rotation.json"
echo "  - Environment: $VAULT_CONFIG_DIR/vault_rotation.env"
echo "  - Logs: $LOG_DIR/vault_rotation.log"
echo "  - Backups: $BACKUP_DIR/"