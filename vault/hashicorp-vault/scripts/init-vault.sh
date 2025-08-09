#!/bin/bash
# Vault Initialization Script - Production Setup
# Initializes Vault, creates policies, and sets up automated key rotation

set -euo pipefail

# Configuration
VAULT_ADDR=${VAULT_ADDR:-http://localhost:8200}
VAULT_KEYS_DIR="/vault/keys"
VAULT_POLICIES_DIR="/policies"
LOG_FILE="/vault/logs/vault-init.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $*"
    exit 1
}

# Wait for Vault to be ready
wait_for_vault() {
    log "Waiting for Vault to be ready..."
    
    for i in {1..30}; do
        if vault status >/dev/null 2>&1; then
            log "Vault is ready"
            return 0
        fi
        log "Attempt $i: Vault not ready, waiting..."
        sleep 5
    done
    
    error_exit "Vault failed to become ready after 150 seconds"
}

# Initialize Vault if not already initialized
init_vault() {
    log "Checking Vault initialization status..."
    
    if vault status 2>/dev/null | grep -q "Initialized.*true"; then
        log "Vault is already initialized"
        return 0
    fi
    
    log "Initializing Vault with 5 key shares and threshold of 3..."
    
    # Create keys directory
    mkdir -p "$VAULT_KEYS_DIR"
    chmod 700 "$VAULT_KEYS_DIR"
    
    # Initialize Vault
    vault operator init \
        -key-shares=5 \
        -key-threshold=3 \
        -format=json > "$VAULT_KEYS_DIR/init-output.json"
    
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to initialize Vault"
    fi
    
    # Extract keys and token
    jq -r '.unseal_keys_b64[]' "$VAULT_KEYS_DIR/init-output.json" > "$VAULT_KEYS_DIR/unseal-keys.txt"
    jq -r '.root_token' "$VAULT_KEYS_DIR/init-output.json" > "$VAULT_KEYS_DIR/root-token.txt"
    
    # Secure the files
    chmod 600 "$VAULT_KEYS_DIR"/*
    
    log "Vault initialized successfully"
    log "Unseal keys stored in: $VAULT_KEYS_DIR/unseal-keys.txt"
    log "Root token stored in: $VAULT_KEYS_DIR/root-token.txt"
}

# Unseal Vault
unseal_vault() {
    log "Checking if Vault needs unsealing..."
    
    if ! vault status 2>/dev/null | grep -q "Sealed.*true"; then
        log "Vault is already unsealed"
        return 0
    fi
    
    log "Unsealing Vault..."
    
    if [[ ! -f "$VAULT_KEYS_DIR/unseal-keys.txt" ]]; then
        error_exit "Unseal keys file not found: $VAULT_KEYS_DIR/unseal-keys.txt"
    fi
    
    # Unseal with first 3 keys
    head -3 "$VAULT_KEYS_DIR/unseal-keys.txt" | while read -r key; do
        vault operator unseal "$key" || error_exit "Failed to unseal with key"
    done
    
    log "Vault unsealed successfully"
}

# Authenticate with root token
authenticate_vault() {
    log "Authenticating with Vault..."
    
    if [[ ! -f "$VAULT_KEYS_DIR/root-token.txt" ]]; then
        error_exit "Root token file not found: $VAULT_KEYS_DIR/root-token.txt"
    fi
    
    ROOT_TOKEN=$(cat "$VAULT_KEYS_DIR/root-token.txt")
    export VAULT_TOKEN="$ROOT_TOKEN"
    
    # Verify authentication
    if ! vault auth -method=token token="$ROOT_TOKEN" >/dev/null 2>&1; then
        error_exit "Failed to authenticate with root token"
    fi
    
    log "Successfully authenticated with Vault"
}

# Enable secret engines
enable_secret_engines() {
    log "Enabling secret engines..."
    
    # KV version 2 for application secrets
    if ! vault secrets list | grep -q "hearthlink-kv/"; then
        vault secrets enable -path=hearthlink-kv kv-v2
        log "Enabled KV v2 secrets engine at hearthlink-kv/"
    fi
    
    # Database secrets engine for dynamic DB credentials
    if ! vault secrets list | grep -q "database/"; then
        vault secrets enable database
        log "Enabled database secrets engine"
    fi
    
    # PKI for certificate management
    if ! vault secrets list | grep -q "pki/"; then
        vault secrets enable pki
        vault secrets tune -max-lease-ttl=8760h pki
        log "Enabled PKI secrets engine"
    fi
    
    # Transit for encryption as a service
    if ! vault secrets list | grep -q "transit/"; then
        vault secrets enable transit
        log "Enabled transit secrets engine"
    fi
    
    log "Secret engines enabled successfully"
}

# Create Vault policies
create_policies() {
    log "Creating Vault policies..."
    
    # Create hearthlink application policy
    cat > /tmp/hearthlink-app-policy.hcl << 'EOF'
# Hearthlink Application Policy
# Read/write access to application secrets
path "hearthlink-kv/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "hearthlink-kv/metadata/*" {
  capabilities = ["list"]
}

# Database dynamic credentials
path "database/creds/hearthlink-readonly" {
  capabilities = ["read"]
}

path "database/creds/hearthlink-readwrite" {
  capabilities = ["read"]  
}

# Transit encryption
path "transit/encrypt/hearthlink" {
  capabilities = ["update"]
}

path "transit/decrypt/hearthlink" {
  capabilities = ["update"]
}

# PKI certificate generation
path "pki/issue/hearthlink" {
  capabilities = ["create", "update"]
}
EOF

    vault policy write hearthlink-app /tmp/hearthlink-app-policy.hcl
    log "Created hearthlink-app policy"
    
    # Create monitoring policy
    cat > /tmp/hearthlink-monitoring-policy.hcl << 'EOF'
# Hearthlink Monitoring Policy
# Read-only access for monitoring and metrics

path "sys/health" {
  capabilities = ["read"]
}

path "sys/metrics" {
  capabilities = ["read"]
}

path "sys/seal-status" {
  capabilities = ["read"]
}

path "sys/leader" {
  capabilities = ["read"]
}
EOF

    vault policy write hearthlink-monitoring /tmp/hearthlink-monitoring-policy.hcl
    log "Created hearthlink-monitoring policy"
    
    # Create key rotation policy
    cat > /tmp/hearthlink-key-rotation-policy.hcl << 'EOF'
# Hearthlink Key Rotation Policy
# Permissions for automated key rotation

path "sys/rotate" {
  capabilities = ["update"]
}

path "sys/key-status" {
  capabilities = ["read"]
}

path "transit/keys/hearthlink" {
  capabilities = ["read", "update"]
}

path "transit/keys/hearthlink/rotate" {
  capabilities = ["update"]
}

path "pki/root/rotate/internal" {
  capabilities = ["update"]
}
EOF

    vault policy write hearthlink-key-rotation /tmp/hearthlink-key-rotation-policy.hcl
    log "Created hearthlink-key-rotation policy"
    
    # Clean up temporary files
    rm -f /tmp/hearthlink-*-policy.hcl
    
    log "Policies created successfully"
}

# Configure authentication methods
configure_auth() {
    log "Configuring authentication methods..."
    
    # Enable AppRole for application authentication
    if ! vault auth list | grep -q "approle/"; then
        vault auth enable approle
        log "Enabled AppRole authentication"
    fi
    
    # Create AppRole for Hearthlink application
    vault write auth/approle/role/hearthlink \
        token_policies="hearthlink-app" \
        token_ttl=1h \
        token_max_ttl=4h \
        bind_secret_id=true \
        secret_id_ttl=24h
    
    # Generate role ID and secret ID
    ROLE_ID=$(vault read -field=role_id auth/approle/role/hearthlink/role-id)
    SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/hearthlink/secret-id)
    
    # Store credentials securely
    echo "$ROLE_ID" > "$VAULT_KEYS_DIR/hearthlink-role-id.txt"
    echo "$SECRET_ID" > "$VAULT_KEYS_DIR/hearthlink-secret-id.txt"
    chmod 600 "$VAULT_KEYS_DIR"/hearthlink-*.txt
    
    log "AppRole configured for Hearthlink application"
    
    # Create monitoring token
    MONITORING_TOKEN=$(vault write -field=token auth/token/create \
        policies="hearthlink-monitoring" \
        ttl=8760h \
        renewable=true)
    
    echo "$MONITORING_TOKEN" > "$VAULT_KEYS_DIR/monitoring-token.txt"
    chmod 600 "$VAULT_KEYS_DIR/monitoring-token.txt"
    
    log "Monitoring token created"
}

# Configure database connections
configure_database() {
    log "Configuring database connections..."
    
    # Configure PostgreSQL connection
    vault write database/config/hearthlink-postgres \
        plugin_name=postgresql-database-plugin \
        connection_url="postgresql://{{username}}:{{password}}@postgres:5432/hearthlink?sslmode=require" \
        allowed_roles="hearthlink-readonly,hearthlink-readwrite" \
        username="vault" \
        password="vault_password"
    
    # Create database roles
    vault write database/roles/hearthlink-readonly \
        db_name=hearthlink-postgres \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
        default_ttl="1h" \
        max_ttl="24h"
    
    vault write database/roles/hearthlink-readwrite \
        db_name=hearthlink-postgres \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
        default_ttl="1h" \
        max_ttl="24h"
    
    log "Database connections configured"
}

# Configure PKI
configure_pki() {
    log "Configuring PKI..."
    
    # Generate root CA
    vault write pki/root/generate/internal \
        common_name="Hearthlink Root CA" \
        ttl=8760h
    
    # Configure CA and CRL URLs
    vault write pki/config/urls \
        issuing_certificates="$VAULT_ADDR/v1/pki/ca" \
        crl_distribution_points="$VAULT_ADDR/v1/pki/crl"
    
    # Create role for certificate generation
    vault write pki/roles/hearthlink \
        allowed_domains="hearthlink.local,*.hearthlink.local" \
        allow_subdomains=true \
        max_ttl="72h" \
        generate_lease=true
    
    log "PKI configured successfully"
}

# Configure transit encryption
configure_transit() {
    log "Configuring transit encryption..."
    
    # Create encryption key
    vault write -f transit/keys/hearthlink
    
    log "Transit encryption key created"
}

# Set up key rotation schedule
setup_key_rotation() {
    log "Setting up automated key rotation..."
    
    # Create periodic token for key rotation
    KEY_ROTATION_TOKEN=$(vault write -field=token auth/token/create \
        policies="hearthlink-key-rotation" \
        ttl=8760h \
        renewable=true \
        period=24h)
    
    echo "$KEY_ROTATION_TOKEN" > "$VAULT_KEYS_DIR/key-rotation-token.txt"
    chmod 600 "$VAULT_KEYS_DIR/key-rotation-token.txt"
    
    log "Key rotation token created"
}

# Main execution
main() {
    log "Starting Vault initialization process..."
    
    # Create directories
    mkdir -p "$VAULT_KEYS_DIR" /vault/logs
    
    # Initialize Vault
    wait_for_vault
    init_vault
    unseal_vault
    authenticate_vault
    
    # Configure Vault
    enable_secret_engines
    create_policies
    configure_auth
    configure_database
    configure_pki
    configure_transit
    setup_key_rotation
    
    log "Vault initialization completed successfully!"
    log "Important files created in $VAULT_KEYS_DIR:"
    log "  - root-token.txt (Root token - keep secure!)"
    log "  - unseal-keys.txt (Unseal keys - keep secure!)"
    log "  - hearthlink-role-id.txt (Application role ID)"
    log "  - hearthlink-secret-id.txt (Application secret ID)"
    log "  - monitoring-token.txt (Monitoring token)"
    log "  - key-rotation-token.txt (Key rotation token)"
    log ""
    log "Next steps:"
    log "1. Secure the unseal keys and root token"
    log "2. Start the key rotation daemon"
    log "3. Configure application to use AppRole authentication"
    log "4. Set up monitoring and alerting"
}

# Execute main function
main "$@"