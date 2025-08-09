#!/bin/bash
# Automated Key Rotation Daemon for HashiCorp Vault
# Continuously monitors and rotates encryption keys based on schedule

set -euo pipefail

# Configuration
VAULT_ADDR=${VAULT_ADDR:-http://localhost:8200}
KEY_ROTATION_INTERVAL=${KEY_ROTATION_INTERVAL:-24h}
ALERT_WEBHOOK_URL=${ALERT_WEBHOOK_URL:-}
LOG_FILE="/vault/logs/key-rotation.log"
TOKEN_FILE="/vault/keys/key-rotation-token.txt"
METRICS_FILE="/vault/logs/key-rotation-metrics.json"

# Convert interval to seconds
convert_to_seconds() {
    local interval="$1"
    case "$interval" in
        *h) echo $(( ${interval%h} * 3600 )) ;;
        *m) echo $(( ${interval%m} * 60 )) ;;
        *s) echo ${interval%s} ;;
        *) echo 86400 ;; # Default to 24 hours
    esac
}

ROTATION_INTERVAL_SECONDS=$(convert_to_seconds "$KEY_ROTATION_INTERVAL")

# Logging functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

log_metric() {
    local metric_name="$1"
    local metric_value="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"timestamp\":\"$timestamp\",\"metric\":\"$metric_name\",\"value\":$metric_value}" >> "$METRICS_FILE"
}

# Alert function
send_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="${3:-warning}"
    
    log "ALERT [$alert_type]: $message"
    
    if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
        local payload=$(cat << EOF
{
    "alert_type": "$alert_type",
    "message": "$message",
    "severity": "$severity",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "service": "vault-key-rotation",
    "hostname": "$(hostname)"
}
EOF
)
        
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$payload" \
            "$ALERT_WEBHOOK_URL" || log_error "Failed to send alert webhook"
    fi
}

# Authentication with Vault
authenticate_vault() {
    if [[ ! -f "$TOKEN_FILE" ]]; then
        log_error "Key rotation token file not found: $TOKEN_FILE"
        send_alert "authentication_failed" "Key rotation token file missing" "critical"
        return 1
    fi
    
    local token=$(cat "$TOKEN_FILE")
    export VAULT_TOKEN="$token"
    
    # Verify token is valid
    if ! vault auth -method=token token="$token" >/dev/null 2>&1; then
        log_error "Failed to authenticate with key rotation token"
        send_alert "authentication_failed" "Invalid or expired key rotation token" "critical"
        return 1
    fi
    
    log "Successfully authenticated with Vault"
    return 0
}

# Check Vault health
check_vault_health() {
    local health_status
    
    if ! health_status=$(vault status -format=json 2>/dev/null); then
        log_error "Vault is not accessible"
        send_alert "vault_unhealthy" "Vault status check failed" "critical"
        return 1
    fi
    
    local sealed=$(echo "$health_status" | jq -r '.sealed // true')
    local standby=$(echo "$health_status" | jq -r '.standby // true')
    
    if [[ "$sealed" == "true" ]]; then
        log_error "Vault is sealed"
        send_alert "vault_sealed" "Vault is sealed and cannot perform key rotation" "critical"
        return 1
    fi
    
    if [[ "$standby" == "true" ]]; then
        log "Vault is in standby mode, skipping rotation on this node"
        return 2
    fi
    
    log "Vault health check passed"
    return 0
}

# Get key status and determine if rotation is needed
check_key_status() {
    local key_path="$1"
    local max_age_seconds="$2"
    
    local key_info
    if ! key_info=$(vault read -format=json "$key_path" 2>/dev/null); then
        log_error "Failed to read key status: $key_path"
        return 1
    fi
    
    local creation_time=$(echo "$key_info" | jq -r '.data.creation_time // .data.created_time // empty')
    if [[ -z "$creation_time" ]]; then
        log_error "Could not determine key creation time for: $key_path"
        return 1
    fi
    
    local current_time=$(date +%s)
    local key_time=$(date -d "$creation_time" +%s 2>/dev/null || echo 0)
    local key_age=$((current_time - key_time))
    
    log "Key $key_path age: ${key_age}s (max: ${max_age_seconds}s)"
    log_metric "key_age_seconds" "$key_age"
    
    if [[ $key_age -gt $max_age_seconds ]]; then
        return 0  # Rotation needed
    else
        return 1  # No rotation needed
    fi
}

# Rotate Vault's internal encryption key
rotate_vault_encryption_key() {
    log "Checking Vault encryption key rotation..."
    
    local key_status
    if ! key_status=$(vault read -format=json sys/key-status 2>/dev/null); then
        log_error "Failed to read Vault key status"
        send_alert "key_rotation_failed" "Cannot read Vault encryption key status" "high"
        return 1
    fi
    
    local install_time=$(echo "$key_status" | jq -r '.data.install_time')
    local current_time=$(date +%s)
    local key_time=$(date -d "$install_time" +%s 2>/dev/null || echo 0)
    local key_age=$((current_time - key_time))
    
    if [[ $key_age -gt $ROTATION_INTERVAL_SECONDS ]]; then
        log "Rotating Vault encryption key (age: ${key_age}s)"
        
        if vault write -f sys/rotate >/dev/null 2>&1; then
            log "Vault encryption key rotated successfully"
            send_alert "key_rotation_success" "Vault encryption key rotated successfully" "info"
            log_metric "vault_key_rotations" 1
            return 0
        else
            log_error "Failed to rotate Vault encryption key"
            send_alert "key_rotation_failed" "Vault encryption key rotation failed" "high"
            return 1
        fi
    else
        log "Vault encryption key is current (age: ${key_age}s)"
        return 0
    fi
}

# Rotate transit encryption key
rotate_transit_key() {
    local key_name="$1"
    local key_path="transit/keys/$key_name"
    
    log "Checking transit key rotation: $key_name"
    
    if check_key_status "$key_path" "$ROTATION_INTERVAL_SECONDS"; then
        log "Rotating transit key: $key_name"
        
        if vault write "transit/keys/$key_name/rotate" >/dev/null 2>&1; then
            log "Transit key rotated successfully: $key_name"
            send_alert "key_rotation_success" "Transit key '$key_name' rotated successfully" "info"
            log_metric "transit_key_rotations" 1
            return 0
        else
            log_error "Failed to rotate transit key: $key_name"
            send_alert "key_rotation_failed" "Transit key '$key_name' rotation failed" "high"
            return 1
        fi
    else
        log "Transit key is current: $key_name"
        return 0
    fi
}

# Rotate PKI root certificate
rotate_pki_root() {
    log "Checking PKI root certificate rotation..."
    
    local cert_info
    if ! cert_info=$(vault read -format=json pki/cert/ca 2>/dev/null); then
        log_error "Failed to read PKI root certificate"
        send_alert "key_rotation_failed" "Cannot read PKI root certificate" "high"
        return 1
    fi
    
    local cert_data=$(echo "$cert_info" | jq -r '.data.certificate')
    local expiry_date=$(echo "$cert_data" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    
    if [[ -n "$expiry_date" ]]; then
        local current_time=$(date +%s)
        local expiry_time=$(date -d "$expiry_date" +%s 2>/dev/null || echo 0)
        local days_until_expiry=$(( (expiry_time - current_time) / 86400 ))
        
        log "PKI root certificate expires in $days_until_expiry days"
        log_metric "pki_cert_days_until_expiry" "$days_until_expiry"
        
        # Rotate if less than 30 days until expiry
        if [[ $days_until_expiry -lt 30 ]]; then
            log "Rotating PKI root certificate (expires in $days_until_expiry days)"
            
            if vault write pki/root/rotate/internal \
                common_name="Hearthlink Root CA" \
                ttl=8760h >/dev/null 2>&1; then
                log "PKI root certificate rotated successfully"
                send_alert "key_rotation_success" "PKI root certificate rotated successfully" "info"
                log_metric "pki_cert_rotations" 1
                return 0
            else
                log_error "Failed to rotate PKI root certificate"
                send_alert "key_rotation_failed" "PKI root certificate rotation failed" "high"
                return 1
            fi
        else
            log "PKI root certificate is current"
            return 0
        fi
    else
        log_error "Could not determine PKI root certificate expiry"
        return 1
    fi
}

# Generate key rotation report
generate_rotation_report() {
    local report_file="/vault/logs/key-rotation-report-$(date +%Y%m%d-%H%M%S).json"
    
    local vault_key_status=$(vault read -format=json sys/key-status 2>/dev/null || echo '{}')
    local transit_key_status=$(vault read -format=json transit/keys/hearthlink 2>/dev/null || echo '{}')
    local pki_cert_info=$(vault read -format=json pki/cert/ca 2>/dev/null || echo '{}')
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "rotation_interval": "$KEY_ROTATION_INTERVAL",
    "vault_encryption_key": $vault_key_status,
    "transit_key": $transit_key_status,
    "pki_certificate": $pki_cert_info,
    "next_rotation_check": "$(date -u -d "+$KEY_ROTATION_INTERVAL" +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    
    log "Key rotation report generated: $report_file"
}

# Main rotation cycle
run_rotation_cycle() {
    log "Starting key rotation cycle..."
    
    local rotation_start_time=$(date +%s)
    local errors=0
    
    # Authenticate with Vault
    if ! authenticate_vault; then
        ((errors++))
        return $errors
    fi
    
    # Check Vault health
    local health_status
    health_status=$(check_vault_health)
    case $? in
        1) ((errors++)); return $errors ;;
        2) log "Skipping rotation on standby node"; return 0 ;;
    esac
    
    # Rotate Vault encryption key
    if ! rotate_vault_encryption_key; then
        ((errors++))
    fi
    
    # Rotate transit keys
    if ! rotate_transit_key "hearthlink"; then
        ((errors++))
    fi
    
    # Rotate PKI root certificate
    if ! rotate_pki_root; then
        ((errors++))
    fi
    
    # Generate rotation report
    generate_rotation_report
    
    local rotation_end_time=$(date +%s)
    local rotation_duration=$((rotation_end_time - rotation_start_time))
    
    log "Key rotation cycle completed in ${rotation_duration}s with $errors errors"
    log_metric "rotation_cycle_duration_seconds" "$rotation_duration"
    log_metric "rotation_cycle_errors" "$errors"
    
    if [[ $errors -gt 0 ]]; then
        send_alert "rotation_cycle_errors" "Key rotation cycle completed with $errors errors" "warning"
    fi
    
    return $errors
}

# Signal handlers
cleanup() {
    log "Received shutdown signal, cleaning up..."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Main daemon loop
main() {
    log "Starting Vault key rotation daemon"
    log "Rotation interval: $KEY_ROTATION_INTERVAL ($ROTATION_INTERVAL_SECONDS seconds)"
    log "Alert webhook: ${ALERT_WEBHOOK_URL:-disabled}"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Send startup alert
    send_alert "daemon_started" "Vault key rotation daemon started" "info"
    
    # Main loop
    while true; do
        run_rotation_cycle
        
        log "Sleeping for $ROTATION_INTERVAL_SECONDS seconds until next rotation cycle..."
        sleep "$ROTATION_INTERVAL_SECONDS" &
        wait $! || break  # Allow interruption
    done
    
    log "Vault key rotation daemon stopped"
    send_alert "daemon_stopped" "Vault key rotation daemon stopped" "warning"
}

# Execute main function
main "$@"