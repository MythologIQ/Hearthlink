#!/bin/bash
# Vault Health Monitor - Continuous monitoring and alerting
# Monitors Vault health, performance, and security metrics

set -euo pipefail

# Configuration
VAULT_ADDR=${VAULT_ADDR:-https://localhost:8200}
VAULT_TOKEN_FILE="/opt/hearthlink/vault/keys/monitoring-token.txt"
CHECK_INTERVAL=${CHECK_INTERVAL:-30}
ALERT_WEBHOOK_URL=${ALERT_WEBHOOK_URL:-}
METRICS_FILE="/opt/hearthlink/vault/logs/health-metrics.json"
LOG_FILE="/opt/hearthlink/vault/logs/health-monitor.log"

# State tracking
STATE_FILE="/opt/hearthlink/vault/logs/monitor-state.json"
LAST_ALERT_FILE="/opt/hearthlink/vault/logs/last-alerts.json"

# Alert thresholds
RESPONSE_TIME_THRESHOLD=2000  # 2 seconds in ms
MEMORY_THRESHOLD=80           # 80% memory usage
ERROR_RATE_THRESHOLD=0.05     # 5% error rate
SEAL_CHECK_CRITICAL=true

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
    local labels="${3:-}"
    
    local metric_entry="{\"timestamp\":\"$timestamp\",\"metric\":\"$metric_name\",\"value\":$metric_value"
    if [[ -n "$labels" ]]; then
        metric_entry+=",\"labels\":$labels"
    fi
    metric_entry+="}"
    
    echo "$metric_entry" >> "$METRICS_FILE"
}

# Alert functions
send_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="${3:-warning}"
    local details="${4:-{}}"
    
    log "ALERT [$severity/$alert_type]: $message"
    
    # Check alert throttling
    if should_throttle_alert "$alert_type" "$severity"; then
        log "Alert throttled: $alert_type"
        return 0
    fi
    
    # Update last alert time
    update_last_alert "$alert_type"
    
    # Send webhook alert
    if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
        local payload=$(cat << EOF
{
    "alert_type": "$alert_type",
    "message": "$message",
    "severity": "$severity",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "service": "vault",
    "component": "health_monitor",
    "hostname": "$(hostname)",
    "details": $details
}
EOF
)
        
        if curl -s -X POST \
            -H "Content-Type: application/json" \
            -H "X-Alert-Source: vault-health-monitor" \
            -d "$payload" \
            "$ALERT_WEBHOOK_URL" >/dev/null 2>&1; then
            log "Alert sent successfully: $alert_type"
        else
            log_error "Failed to send alert webhook: $alert_type"
        fi
    fi
    
    # Log to system journal for systemd integration
    logger -t vault-monitor -p daemon.warning "VAULT ALERT [$severity]: $message"
}

should_throttle_alert() {
    local alert_type="$1"
    local severity="$2"
    
    # Never throttle critical alerts
    if [[ "$severity" == "critical" ]]; then
        return 1
    fi
    
    # Check last alert time
    if [[ -f "$LAST_ALERT_FILE" ]]; then
        local last_time=$(jq -r ".\"$alert_type\" // 0" "$LAST_ALERT_FILE" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_time))
        
        # Throttle if less than 5 minutes for warnings, 1 minute for high severity
        local throttle_duration=300  # 5 minutes
        if [[ "$severity" == "high" ]]; then
            throttle_duration=60  # 1 minute
        fi
        
        if [[ $time_diff -lt $throttle_duration ]]; then
            return 0  # Should throttle
        fi
    fi
    
    return 1  # Should not throttle
}

update_last_alert() {
    local alert_type="$1"
    local current_time=$(date +%s)
    
    # Create or update last alerts file
    if [[ -f "$LAST_ALERT_FILE" ]]; then
        local updated=$(jq ". + {\"$alert_type\": $current_time}" "$LAST_ALERT_FILE" 2>/dev/null || echo "{\"$alert_type\": $current_time}")
    else
        local updated="{\"$alert_type\": $current_time}"
    fi
    
    echo "$updated" > "$LAST_ALERT_FILE"
}

# Authentication
authenticate_vault() {
    if [[ ! -f "$VAULT_TOKEN_FILE" ]]; then
        log_error "Monitoring token file not found: $VAULT_TOKEN_FILE"
        return 1
    fi
    
    local token=$(cat "$VAULT_TOKEN_FILE")
    export VAULT_TOKEN="$token"
    
    # Test authentication
    if ! vault auth -method=token token="$token" >/dev/null 2>&1; then
        log_error "Failed to authenticate with monitoring token"
        send_alert "auth_failure" "Vault monitoring authentication failed" "critical"
        return 1
    fi
    
    return 0
}

# Health checks
check_vault_status() {
    local check_start=$(date +%s%3N)
    local status_output
    local exit_code=0
    
    # Get Vault status
    if status_output=$(vault status -format=json 2>&1); then
        local check_end=$(date +%s%3N)
        local response_time=$((check_end - check_start))
        
        log_metric "vault_health_check_response_time_ms" "$response_time"
        
        # Parse status
        local sealed=$(echo "$status_output" | jq -r '.sealed // true')
        local initialized=$(echo "$status_output" | jq -r '.initialized // false')
        local standby=$(echo "$status_output" | jq -r '.standby // true')
        local ha_enabled=$(echo "$status_output" | jq -r '.ha_enabled // false')
        local is_self=$(echo "$status_output" | jq -r '.is_self // false')
        
        # Log metrics
        log_metric "vault_sealed" "$([ "$sealed" == "true" ] && echo 1 || echo 0)"
        log_metric "vault_initialized" "$([ "$initialized" == "true" ] && echo 1 || echo 0)"
        log_metric "vault_standby" "$([ "$standby" == "true" ] && echo 1 || echo 0)"
        log_metric "vault_ha_enabled" "$([ "$ha_enabled" == "true" ] && echo 1 || echo 0)"
        
        # Check for critical issues
        if [[ "$sealed" == "true" ]]; then
            send_alert "vault_sealed" "Vault is sealed and cannot serve requests" "critical" \
                "{\"initialized\": $initialized, \"ha_enabled\": $ha_enabled}"
            exit_code=1
        elif [[ "$initialized" == "false" ]]; then
            send_alert "vault_uninitialized" "Vault is not initialized" "critical"
            exit_code=1
        elif [[ "$response_time" -gt $RESPONSE_TIME_THRESHOLD ]]; then
            send_alert "vault_slow_response" "Vault response time is ${response_time}ms (threshold: ${RESPONSE_TIME_THRESHOLD}ms)" "warning" \
                "{\"response_time_ms\": $response_time, \"threshold_ms\": $RESPONSE_TIME_THRESHOLD}"
        fi
        
        # Log successful check
        log "Vault status check: sealed=$sealed, initialized=$initialized, standby=$standby, response_time=${response_time}ms"
        
    else
        local check_end=$(date +%s%3N)
        local response_time=$((check_end - check_start))
        
        log_error "Vault status check failed: $status_output"
        log_metric "vault_health_check_failures" "1"
        
        send_alert "vault_unreachable" "Vault is unreachable or not responding" "critical" \
            "{\"error\": \"$status_output\", \"response_time_ms\": $response_time}"
        exit_code=1
    fi
    
    return $exit_code
}

check_vault_metrics() {
    local metrics_output
    
    # Get Vault metrics
    if metrics_output=$(vault read sys/metrics -format=json 2>/dev/null); then
        
        # Parse key metrics
        local counters=$(echo "$metrics_output" | jq -r '.data.Counters // []')
        local gauges=$(echo "$metrics_output" | jq -r '.data.Gauges // []')
        local samples=$(echo "$metrics_output" | jq -r '.data.Samples // []')
        
        # Process counters
        if [[ "$counters" != "[]" ]]; then
            echo "$counters" | jq -r '.[] | select(.Name | contains("vault.core.handle_request")) | "\(.Name)=\(.Count)"' | while read -r metric; do
                if [[ -n "$metric" ]]; then
                    local name=$(echo "$metric" | cut -d'=' -f1 | sed 's/vault\.core\.handle_request/vault_requests/')
                    local value=$(echo "$metric" | cut -d'=' -f2)
                    log_metric "$name" "$value"
                fi
            done
        fi
        
        # Process gauges (memory, goroutines, etc.)
        if [[ "$gauges" != "[]" ]]; then
            echo "$gauges" | jq -r '.[] | select(.Name | contains("runtime")) | "\(.Name)=\(.Value)"' | while read -r metric; do
                if [[ -n "$metric" ]]; then
                    local name=$(echo "$metric" | cut -d'=' -f1 | sed 's/vault\.runtime/vault_runtime/')
                    local value=$(echo "$metric" | cut -d'=' -f2)
                    log_metric "$name" "$value"
                fi
            done
        fi
        
        # Check for performance issues
        local memory_usage=$(echo "$gauges" | jq -r '.[] | select(.Name == "vault.runtime.alloc_bytes") | .Value' 2>/dev/null || echo "0")
        local goroutines=$(echo "$gauges" | jq -r '.[] | select(.Name == "vault.runtime.num_goroutines") | .Value' 2>/dev/null || echo "0")
        
        if [[ "$memory_usage" -gt 0 && "$goroutines" -gt 0 ]]; then
            # Simple memory usage check (this would need calibration for real environments)
            if [[ "$goroutines" -gt 10000 ]]; then
                send_alert "vault_high_goroutines" "Vault has $goroutines goroutines (potential memory leak)" "warning" \
                    "{\"goroutines\": $goroutines, \"memory_bytes\": $memory_usage}"
            fi
        fi
        
        log "Vault metrics collected successfully"
        return 0
    else
        log_error "Failed to collect Vault metrics"
        log_metric "vault_metrics_collection_failures" "1"
        return 1
    fi
}

check_vault_policies() {
    local policies_output
    
    # List policies
    if policies_output=$(vault policy list -format=json 2>/dev/null); then
        local policy_count=$(echo "$policies_output" | jq '. | length')
        log_metric "vault_policies_count" "$policy_count"
        
        # Check for required policies
        local required_policies=("hearthlink-app" "hearthlink-monitoring" "hearthlink-key-rotation")
        for policy in "${required_policies[@]}"; do
            if echo "$policies_output" | jq -r '.[]' | grep -q "^$policy$"; then
                log_metric "vault_policy_${policy}_exists" "1"
            else
                log_metric "vault_policy_${policy}_exists" "0"
                send_alert "vault_missing_policy" "Required policy '$policy' is missing" "high" \
                    "{\"missing_policy\": \"$policy\"}"
            fi
        done
        
        log "Vault policies check completed: $policy_count policies found"
        return 0
    else
        log_error "Failed to list Vault policies"
        return 1
    fi
}

check_vault_mounts() {
    local mounts_output
    
    # List secret engines
    if mounts_output=$(vault secrets list -format=json 2>/dev/null); then
        local mount_count=$(echo "$mounts_output" | jq '. | length')
        log_metric "vault_secret_engines_count" "$mount_count"
        
        # Check for required mounts
        local required_mounts=("hearthlink-kv/" "database/" "pki/" "transit/")
        for mount in "${required_mounts[@]}"; do
            if echo "$mounts_output" | jq -r 'keys[]' | grep -q "^$mount$"; then
                log_metric "vault_mount_${mount//\//_}_exists" "1"
            else
                log_metric "vault_mount_${mount//\//_}_exists" "0"
                send_alert "vault_missing_mount" "Required secret engine '$mount' is missing" "high" \
                    "{\"missing_mount\": \"$mount\"}"
            fi
        done
        
        log "Vault mounts check completed: $mount_count secret engines found"
        return 0
    else
        log_error "Failed to list Vault secret engines"
        return 1
    fi
}

check_encryption_key_age() {
    local key_status_output
    
    # Get encryption key status
    if key_status_output=$(vault read sys/key-status -format=json 2>/dev/null); then
        local install_time=$(echo "$key_status_output" | jq -r '.data.install_time')
        local current_time=$(date +%s)
        local key_time=$(date -d "$install_time" +%s 2>/dev/null || echo 0)
        local key_age_seconds=$((current_time - key_time))
        local key_age_days=$((key_age_seconds / 86400))
        
        log_metric "vault_encryption_key_age_seconds" "$key_age_seconds"
        log_metric "vault_encryption_key_age_days" "$key_age_days"
        
        # Alert if key is older than 2 days (should be rotated daily)
        if [[ $key_age_days -gt 2 ]]; then
            send_alert "vault_key_rotation_overdue" "Vault encryption key is $key_age_days days old (should be rotated daily)" "warning" \
                "{\"key_age_days\": $key_age_days, \"install_time\": \"$install_time\"}"
        fi
        
        log "Vault encryption key age: $key_age_days days"
        return 0
    else
        log_error "Failed to check encryption key status"
        return 1
    fi
}

# Main monitoring loop iteration
run_health_checks() {
    local check_start_time=$(date +%s)
    local total_errors=0
    
    log "Starting Vault health check cycle..."
    
    # Authenticate with Vault
    if ! authenticate_vault; then
        ((total_errors++))
        return $total_errors
    fi
    
    # Run individual checks
    check_vault_status || ((total_errors++))
    check_vault_metrics || ((total_errors++))
    check_vault_policies || ((total_errors++))
    check_vault_mounts || ((total_errors++))
    check_encryption_key_age || ((total_errors++))
    
    local check_end_time=$(date +%s)
    local cycle_duration=$((check_end_time - check_start_time))
    
    log_metric "vault_health_check_cycle_duration_seconds" "$cycle_duration"
    log_metric "vault_health_check_cycle_errors" "$total_errors"
    
    log "Health check cycle completed in ${cycle_duration}s with $total_errors errors"
    
    # Update monitoring state
    update_monitor_state "$total_errors" "$cycle_duration"
    
    return $total_errors
}

update_monitor_state() {
    local error_count="$1"
    local cycle_duration="$2"
    
    local state=$(cat << EOF
{
    "last_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "last_error_count": $error_count,
    "last_cycle_duration": $cycle_duration,
    "status": "$([ $error_count -eq 0 ] && echo "healthy" || echo "unhealthy")",
    "uptime": $(( $(date +%s) - ${MONITOR_START_TIME:-$(date +%s)} ))
}
EOF
)
    
    echo "$state" > "$STATE_FILE"
}

# Signal handlers
cleanup() {
    log "Received shutdown signal, cleaning up..."
    
    # Send shutdown alert
    send_alert "monitor_shutdown" "Vault health monitor is shutting down" "info"
    
    # Clean up temporary files
    rm -f "$STATE_FILE.tmp"
    
    exit 0
}

reload_config() {
    log "Received reload signal, reloading configuration..."
    # Configuration reload logic would go here
    log "Configuration reloaded"
}

trap cleanup SIGTERM SIGINT
trap reload_config SIGHUP

# Main daemon function
main() {
    log "Starting Vault health monitor daemon"
    log "Check interval: ${CHECK_INTERVAL}s"
    log "Alert webhook: ${ALERT_WEBHOOK_URL:-disabled}"
    
    # Create necessary directories
    mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$METRICS_FILE")" "$(dirname "$STATE_FILE")"
    
    # Initialize monitoring state
    export MONITOR_START_TIME=$(date +%s)
    update_monitor_state 0 0
    
    # Send startup alert
    send_alert "monitor_started" "Vault health monitor started" "info"
    
    # Main monitoring loop
    while true; do
        if ! run_health_checks; then
            log "Health check cycle completed with errors"
        fi
        
        # Sleep until next check
        sleep "$CHECK_INTERVAL" &
        wait $! || break  # Allow interruption
    done
    
    log "Vault health monitor stopped"
}

# Execute main function
main "$@"