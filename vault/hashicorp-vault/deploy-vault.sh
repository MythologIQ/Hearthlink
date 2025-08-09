#!/bin/bash
# HashiCorp Vault Production Deployment Script
# Deploys Vault with automated key rotation and monitoring

set -euo pipefail

# Configuration
VAULT_DIR="/opt/hearthlink/vault"
COMPOSE_FILE="docker-compose.vault.yml"
ENV_FILE=".env.vault"
LOG_FILE="/var/log/hearthlink/vault-deploy.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error_exit() {
    log "ERROR: $*"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        error_exit "This script must be run as root"
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "openssl" "jq" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error_exit "Required command not found: $cmd"
        fi
    done
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        error_exit "Docker is not running"
    fi
    
    log "Prerequisites check passed"
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    local directories=(
        "$VAULT_DIR"
        "$VAULT_DIR/data"
        "$VAULT_DIR/logs"
        "$VAULT_DIR/keys"
        "$VAULT_DIR/config"
        "$VAULT_DIR/config/certs"
        "/var/log/hearthlink"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        chmod 700 "$dir"
    done
    
    # Set ownership
    chown -R vault:vault "$VAULT_DIR" 2>/dev/null || true
    
    log "Directory structure created"
}

# Generate TLS certificates
generate_certificates() {
    log "Generating TLS certificates..."
    
    local cert_dir="$VAULT_DIR/config/certs"
    local key_file="$cert_dir/server.key"
    local cert_file="$cert_dir/server.crt"
    local config_file="$cert_dir/openssl.cnf"
    
    # Skip if certificates already exist
    if [[ -f "$cert_file" && -f "$key_file" ]]; then
        log "TLS certificates already exist, skipping generation"
        return 0
    fi
    
    # Create OpenSSL configuration
    cat > "$config_file" << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Hearthlink
OU = IT Department
CN = vault.hearthlink.local

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = vault.hearthlink.local
DNS.2 = localhost
IP.1 = 127.0.0.1
IP.2 = 0.0.0.0
EOF
    
    # Generate private key
    openssl genrsa -out "$key_file" 4096
    
    # Generate certificate
    openssl req -new -x509 -key "$key_file" -out "$cert_file" \
        -days 365 -config "$config_file" -extensions v3_req
    
    # Set permissions
    chmod 600 "$key_file"
    chmod 644 "$cert_file"
    
    log "TLS certificates generated successfully"
}

# Create environment file
create_env_file() {
    log "Creating environment file..."
    
    local env_file_path="$(dirname "$0")/$ENV_FILE"
    
    # Generate secure tokens
    local root_token="hvs.$(openssl rand -hex 16)"
    local monitoring_token="hvs.$(openssl rand -hex 16)"
    
    cat > "$env_file_path" << EOF
# HashiCorp Vault Production Environment Configuration
# Generated on $(date)

# Vault Configuration
VAULT_ROOT_TOKEN=$root_token
VAULT_MONITORING_TOKEN=$monitoring_token
VAULT_ADDR=https://vault.hearthlink.local:8200

# Key Rotation
KEY_ROTATION_INTERVAL=24h

# Alerting
ALERT_WEBHOOK_URL=http://host.docker.internal:5001/vault-alerts

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -base64 32)
REDIS_DB=3

# Logging
LOG_LEVEL=INFO

# AWS KMS (for auto-unseal in production)
# AWS_REGION=us-east-1
# AWS_KMS_KEY_ID=arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID

# Security
VAULT_DISABLE_MLOCK=false
VAULT_CLUSTER_NAME=hearthlink-vault-cluster
EOF
    
    chmod 600 "$env_file_path"
    
    log "Environment file created: $env_file_path"
    log "IMPORTANT: Root token is: $root_token"
    log "IMPORTANT: Save this token securely!"
}

# Deploy Vault with Docker Compose
deploy_vault() {
    log "Deploying HashiCorp Vault..."
    
    local deploy_dir="$(dirname "$0")"
    cd "$deploy_dir"
    
    # Pull latest images
    log "Pulling Docker images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Start Vault services
    log "Starting Vault services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for Vault to be ready
    log "Waiting for Vault to be ready..."
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T vault vault status >/dev/null 2>&1; then
            log "Vault is ready"
            break
        fi
        
        ((attempt++))
        log "Attempt $attempt/$max_attempts: Waiting for Vault..."
        sleep 10
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        error_exit "Vault failed to become ready after $((max_attempts * 10)) seconds"
    fi
    
    log "Vault deployed successfully"
}

# Configure systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    local service_file="/etc/systemd/system/hearthlink-vault.service"
    local deploy_dir="$(realpath "$(dirname "$0")")"
    
    cat > "$service_file" << EOF
[Unit]
Description=Hearthlink HashiCorp Vault Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$deploy_dir
ExecStart=/usr/bin/docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
ExecStop=/usr/bin/docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
TimeoutStartSec=300
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable hearthlink-vault.service
    
    log "Systemd service created and enabled"
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    local logrotate_config="/etc/logrotate.d/hearthlink-vault"
    
    cat > "$logrotate_config" << 'EOF'
/var/log/hearthlink/vault-*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    copytruncate
    create 0644 root root
}

/opt/hearthlink/vault/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    copytruncate
    create 0644 vault vault
}
EOF
    
    log "Log rotation configured"
}

# Verify deployment
verify_deployment() {
    log "Verifying Vault deployment..."
    
    # Check container status
    local vault_status
    if ! vault_status=$(docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps --services --filter "status=running"); then
        error_exit "Failed to check container status"
    fi
    
    if ! echo "$vault_status" | grep -q "vault"; then
        error_exit "Vault container is not running"
    fi
    
    # Check Vault health
    if ! docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T vault vault status >/dev/null 2>&1; then
        error_exit "Vault health check failed"
    fi
    
    # Check key rotation daemon
    if ! docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps | grep -q "key-rotator.*Up"; then
        log "Warning: Key rotation daemon may not be running"
    fi
    
    # Check monitoring exporter
    if ! curl -s http://localhost:9410/metrics >/dev/null 2>&1; then
        log "Warning: Vault metrics exporter may not be accessible"
    fi
    
    log "Vault deployment verification completed"
}

# Display deployment summary
display_summary() {
    log "Deployment Summary:"
    log "=================="
    log ""
    log "Vault Status:"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    log ""
    log "Vault UI: https://localhost:8200/ui"
    log "Metrics: http://localhost:9410/metrics"
    log "Configuration: $VAULT_DIR"
    log "Logs: $VAULT_DIR/logs"
    log ""
    log "Important Files:"
    log "- Environment: $ENV_FILE"
    log "- Keys: $VAULT_DIR/keys/"
    log "- Certificates: $VAULT_DIR/config/certs/"
    log ""
    log "Systemd Service:"
    log "- Status: systemctl status hearthlink-vault"
    log "- Start: systemctl start hearthlink-vault"
    log "- Stop: systemctl stop hearthlink-vault"
    log ""
    log "Next Steps:"
    log "1. Save the root token securely"
    log "2. Configure backup strategy"
    log "3. Set up monitoring alerts"
    log "4. Test key rotation manually"
    log "5. Configure your applications to use Vault"
    log ""
    log "Deployment completed successfully!"
}

# Main execution
main() {
    log "Starting HashiCorp Vault production deployment..."
    
    check_prerequisites
    create_directories
    generate_certificates
    create_env_file
    deploy_vault
    create_systemd_service
    setup_log_rotation
    verify_deployment
    display_summary
    
    log "HashiCorp Vault deployment completed successfully!"
}

# Execute main function
main "$@"