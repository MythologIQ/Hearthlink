#!/bin/bash
# HashiCorp Vault Key Rotation Service Installation Script
# Production deployment with systemd integration

set -euo pipefail

# Configuration
SERVICE_NAME="vault-key-rotation"
SERVICE_USER="vault-rotation"
SERVICE_GROUP="vault-rotation"
INSTALL_DIR="/opt/hearthlink/security/vault"
CONFIG_DIR="/etc/hearthlink"
LOG_DIR="/var/log/hearthlink"
DATA_DIR="/var/lib/hearthlink"
SYSTEMD_DIR="/etc/systemd/system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Create service user and group
create_service_user() {
    log_info "Creating service user and group..."
    
    if ! getent group "$SERVICE_GROUP" > /dev/null 2>&1; then
        groupadd --system "$SERVICE_GROUP"
        log_success "Created group: $SERVICE_GROUP"
    else
        log_info "Group $SERVICE_GROUP already exists"
    fi
    
    if ! getent passwd "$SERVICE_USER" > /dev/null 2>&1; then
        useradd \
            --system \
            --gid "$SERVICE_GROUP" \
            --home-dir "$INSTALL_DIR" \
            --no-create-home \
            --shell /bin/false \
            --comment "Vault Key Rotation Service" \
            "$SERVICE_USER"
        log_success "Created user: $SERVICE_USER"
    else
        log_info "User $SERVICE_USER already exists"
    fi
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    directories=(
        "$INSTALL_DIR"
        "$CONFIG_DIR"
        "$LOG_DIR"
        "$DATA_DIR"
        "$DATA_DIR/compliance-reports"
        "$DATA_DIR/vault-rotation"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log_info "Directory $dir already exists"
        fi
    done
    
    # Set ownership and permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$DATA_DIR"
    
    chmod 750 "$INSTALL_DIR"
    chmod 750 "$CONFIG_DIR"
    chmod 755 "$LOG_DIR"
    chmod 750 "$DATA_DIR"
    
    log_success "Set directory permissions"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Found Python version: $python_version"
    
    # Install pip if not available
    if ! command -v pip3 &> /dev/null; then
        log_info "Installing pip..."
        apt-get update
        apt-get install -y python3-pip
    fi
    
    # Create requirements file
    cat > "$INSTALL_DIR/requirements.txt" << EOF
hvac==1.2.1
aiohttp==3.9.0
PyYAML==6.0.1
cryptography==41.0.7
prometheus-client==0.19.0
asyncio-mqtt==0.13.0
structlog==23.2.0
python-dotenv==1.0.0
EOF
    
    # Install dependencies
    pip3 install -r "$INSTALL_DIR/requirements.txt"
    log_success "Python dependencies installed"
}

# Copy service files
copy_service_files() {
    log_info "Copying service files..."
    
    # Copy main service script
    if [[ -f "vault-key-rotation.py" ]]; then
        cp "vault-key-rotation.py" "$INSTALL_DIR/"
        chmod 755 "$INSTALL_DIR/vault-key-rotation.py"
        chown "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR/vault-key-rotation.py"
        log_success "Copied service script"
    else
        log_error "vault-key-rotation.py not found in current directory"
        exit 1
    fi
    
    # Copy configuration file
    if [[ -f "vault-rotation.yaml" ]]; then
        cp "vault-rotation.yaml" "$CONFIG_DIR/"
        chmod 640 "$CONFIG_DIR/vault-rotation.yaml"
        chown "root:$SERVICE_GROUP" "$CONFIG_DIR/vault-rotation.yaml"
        log_success "Copied configuration file"
    else
        log_error "vault-rotation.yaml not found in current directory"
        exit 1
    fi
    
    # Copy systemd service file
    if [[ -f "vault-key-rotation.service" ]]; then
        cp "vault-key-rotation.service" "$SYSTEMD_DIR/"
        chmod 644 "$SYSTEMD_DIR/vault-key-rotation.service"
        log_success "Copied systemd service file"
    else
        log_error "vault-key-rotation.service not found in current directory"
        exit 1
    fi
}

# Configure Vault policy
configure_vault_policy() {
    log_info "Configuring Vault policy..."
    
    if command -v vault &> /dev/null; then
        if [[ -f "vault-rotation-policy.hcl" ]]; then
            # Check if Vault is accessible
            if vault status &> /dev/null; then
                vault policy write vault-rotation-policy vault-rotation-policy.hcl
                log_success "Vault policy created"
                
                # Create service token (requires manual setup)
                log_warning "Please create a service token manually:"
                log_warning "vault token create -policy=vault-rotation-policy -renewable -ttl=24h"
                log_warning "Save the token to $CONFIG_DIR/vault-token"
            else
                log_warning "Vault is not accessible. Policy will need to be configured manually."
            fi
        else
            log_error "vault-rotation-policy.hcl not found"
        fi
    else
        log_warning "Vault CLI not found. Policy will need to be configured manually."
    fi
}

# Create environment file
create_environment_file() {
    log_info "Creating environment file..."
    
    cat > "$CONFIG_DIR/vault-rotation.env" << EOF
# Vault Key Rotation Service Environment Variables
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN_FILE=$CONFIG_DIR/vault-token
PYTHONPATH=$INSTALL_DIR
PYTHONUNBUFFERED=1

# Logging
LOG_LEVEL=INFO

# Monitoring
PROMETHEUS_PORT=9100
HEALTH_CHECK_PORT=8080

# Alerting (configure as needed)
# WEBHOOK_URL=http://localhost:3000/webhooks/vault-rotation
# SLACK_WEBHOOK_URL=
# SMTP_HOST=smtp.hearthlink.local
# PAGERDUTY_KEY=
EOF
    
    chmod 640 "$CONFIG_DIR/vault-rotation.env"
    chown "root:$SERVICE_GROUP" "$CONFIG_DIR/vault-rotation.env"
    log_success "Environment file created"
}

# Setup log rotation
setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    cat > "/etc/logrotate.d/vault-key-rotation" << EOF
$LOG_DIR/vault-rotation.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload vault-key-rotation.service > /dev/null 2>&1 || true
    endscript
}

$LOG_DIR/vault-audit.log {
    daily
    rotate 2555
    compress
    delaycompress
    missingok
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
}
EOF
    
    log_success "Log rotation configured"
}

# Configure systemd service
configure_systemd() {
    log_info "Configuring systemd service..."
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable "$SERVICE_NAME.service"
    log_success "Service enabled"
    
    # Start service
    if systemctl start "$SERVICE_NAME.service"; then
        log_success "Service started successfully"
    else
        log_error "Failed to start service"
        systemctl status "$SERVICE_NAME.service"
        exit 1
    fi
    
    # Show service status
    sleep 2
    systemctl status "$SERVICE_NAME.service" --no-pager
}

# Create monitoring endpoints
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create Prometheus configuration
    cat > "$CONFIG_DIR/prometheus-vault-rotation.yml" << EOF
# Prometheus configuration for Vault Key Rotation Service
scrape_configs:
  - job_name: 'vault-key-rotation'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 30s
    metrics_path: /metrics
    
  - job_name: 'vault-key-rotation-health'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 10s
    metrics_path: /health
EOF
    
    log_success "Monitoring configuration created"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME.service"; then
        log_success "Service is running"
    else
        log_error "Service is not running"
        return 1
    fi
    
    # Check log file
    if [[ -f "$LOG_DIR/vault-rotation.log" ]]; then
        log_success "Log file created"
    else
        log_warning "Log file not found"
    fi
    
    # Check configuration
    if [[ -f "$CONFIG_DIR/vault-rotation.yaml" ]]; then
        log_success "Configuration file present"
    else
        log_error "Configuration file missing"
        return 1
    fi
    
    # Test health endpoint (if service is running)
    if command -v curl &> /dev/null; then
        if curl -f -s http://localhost:8080/health > /dev/null; then
            log_success "Health endpoint responding"
        else
            log_warning "Health endpoint not responding (service may still be starting)"
        fi
    fi
    
    return 0
}

# Main installation function
main() {
    log_info "Starting HashiCorp Vault Key Rotation Service installation..."
    
    check_root
    create_service_user
    create_directories
    install_dependencies
    copy_service_files
    create_environment_file
    setup_log_rotation
    configure_vault_policy
    setup_monitoring
    configure_systemd
    
    if verify_installation; then
        log_success "Installation completed successfully!"
        
        cat << EOF

┌─────────────────────────────────────────────────────────────┐
│                    Installation Complete                    │
├─────────────────────────────────────────────────────────────┤
│  Service: vault-key-rotation                                │
│  Status:  systemctl status vault-key-rotation              │
│  Logs:    journalctl -u vault-key-rotation -f              │
│  Config:  $CONFIG_DIR/vault-rotation.yaml          │
│  Health:  http://localhost:8080/health                     │
│  Metrics: http://localhost:9100/metrics                    │
├─────────────────────────────────────────────────────────────┤
│  Next Steps:                                                │
│  1. Configure Vault token in $CONFIG_DIR/vault-token       │
│  2. Review configuration in vault-rotation.yaml            │
│  3. Setup alerting webhooks and SMTP settings              │
│  4. Test key rotation: vault-rotation --force-rotation     │
└─────────────────────────────────────────────────────────────┘

EOF
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Run installation
main "$@"