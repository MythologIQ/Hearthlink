#!/bin/bash
# Vault Unseal Script - Production Automation
# Automatically unseals Vault using stored unseal keys

set -euo pipefail

# Configuration
VAULT_ADDR=${VAULT_ADDR:-http://localhost:8200}
VAULT_KEYS_DIR="/vault/keys"
LOG_FILE="/vault/logs/vault-unseal.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $*"
    exit 1
}

# Wait for Vault to be accessible
wait_for_vault() {
    log "Waiting for Vault to be accessible..."
    
    for i in {1..30}; do
        if vault status >/dev/null 2>&1; then
            log "Vault is accessible"
            return 0
        fi
        log "Attempt $i: Vault not accessible, waiting..."
        sleep 5
    done
    
    error_exit "Vault is not accessible after 150 seconds"
}

# Check if Vault needs unsealing
check_seal_status() {
    log "Checking Vault seal status..."
    
    local status_output
    if ! status_output=$(vault status 2>/dev/null); then
        error_exit "Failed to get Vault status"
    fi
    
    if echo "$status_output" | grep -q "Sealed.*false"; then
        log "Vault is already unsealed"
        return 1
    fi
    
    if echo "$status_output" | grep -q "Initialized.*false"; then
        error_exit "Vault is not initialized"
    fi
    
    log "Vault is sealed and needs unsealing"
    return 0
}

# Unseal Vault
unseal_vault() {
    log "Starting Vault unseal process..."
    
    if [[ ! -f "$VAULT_KEYS_DIR/unseal-keys.txt" ]]; then
        error_exit "Unseal keys file not found: $VAULT_KEYS_DIR/unseal-keys.txt"
    fi
    
    local unseal_keys
    if ! unseal_keys=$(cat "$VAULT_KEYS_DIR/unseal-keys.txt"); then
        error_exit "Failed to read unseal keys"
    fi
    
    local key_count=0
    local threshold=3
    
    # Get current seal status
    local status_json
    if ! status_json=$(vault status -format=json 2>/dev/null); then
        error_exit "Failed to get Vault status JSON"
    fi
    
    threshold=$(echo "$status_json" | jq -r '.t // 3')
    local progress=$(echo "$status_json" | jq -r '.progress // 0')
    
    log "Unseal threshold: $threshold, current progress: $progress"
    
    # Unseal with required number of keys
    while read -r key && [[ $key_count -lt $threshold ]]; do
        if [[ -n "$key" ]]; then
            ((key_count++))
            log "Using unseal key $key_count of $threshold"
            
            local unseal_output
            if unseal_output=$(vault operator unseal "$key" 2>&1); then
                local new_progress=$(echo "$unseal_output" | grep -o 'Unseal Progress: [0-9]*' | cut -d' ' -f3 || echo "unknown")
                log "Unseal progress: $new_progress/$threshold"
                
                # Check if unsealing is complete
                if echo "$unseal_output" | grep -q "Sealed.*false"; then
                    log "Vault successfully unsealed!"
                    return 0
                fi
            else
                log "Warning: Failed to use unseal key $key_count: $unseal_output"
            fi
        fi
    done <<< "$unseal_keys"
    
    # Final status check
    if vault status 2>/dev/null | grep -q "Sealed.*false"; then
        log "Vault is now unsealed"
        return 0
    else
        error_exit "Failed to unseal Vault after using $key_count keys"
    fi
}

# Verify Vault is operational
verify_vault_operational() {
    log "Verifying Vault is operational..."
    
    # Check status
    if ! vault status >/dev/null 2>&1; then
        error_exit "Vault status check failed"
    fi
    
    # Test basic operation (sys/health endpoint)
    if ! vault read sys/health >/dev/null 2>&1; then
        log "Warning: Cannot read sys/health endpoint (may require authentication)"
    fi
    
    log "Vault is operational"
}

# Main execution
main() {
    log "Starting Vault unseal process..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Wait for Vault
    wait_for_vault
    
    # Check if unsealing is needed
    if check_seal_status; then
        unseal_vault
        verify_vault_operational
        log "Vault unseal process completed successfully!"
    else
        log "Vault unseal process completed - no action needed"
    fi
}

# Execute main function
main "$@"