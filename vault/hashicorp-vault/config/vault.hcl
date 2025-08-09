# HashiCorp Vault Configuration for Hearthlink Production
# Optimized for security, performance, and automated key rotation

# Storage backend - using integrated raft for production
storage "raft" {
  path    = "/vault/data"
  node_id = "hearthlink-vault-1"
  
  # Autopilot configuration for automated operations
  autopilot {
    cleanup_dead_servers      = true
    last_contact_threshold    = "10s"
    max_trailing_logs         = 1000
    min_quorum               = 1
    server_stabilization_time = "10s"
  }
}

# Listener configuration
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false
  tls_cert_file = "/vault/config/certs/server.crt"
  tls_key_file  = "/vault/config/certs/server.key"
  tls_min_version = "tls12"
  
  # Security headers
  tls_cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
  ]
}

# Cluster listener for HA
listener "tcp" {
  address     = "0.0.0.0:8201"
  cluster_address = "0.0.0.0:8201"
  tls_disable = false
  tls_cert_file = "/vault/config/certs/server.crt"
  tls_key_file  = "/vault/config/certs/server.key"
}

# API configuration
api_addr = "https://vault.hearthlink.local:8200"
cluster_addr = "https://vault.hearthlink.local:8201"
cluster_name = "hearthlink-vault-cluster"

# Seal configuration - Auto-unseal with AWS KMS (production)
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"
  endpoint   = "https://kms.us-east-1.amazonaws.com"
}

# Telemetry and monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = false
  enable_hostname_label = true
  
  # StatsD for metrics collection
  statsd_address = "localhost:8125"
  
  # Usage metrics for cost optimization
  usage_gauge_period = "10m"
  maximum_gauge_cardinality = 500
}

# UI configuration
ui = true

# Security settings
default_lease_ttl = "168h"  # 7 days
max_lease_ttl = "8760h"     # 1 year

# Disable mlock for containerized environments
disable_mlock = false

# Logging configuration
log_level = "INFO"
log_format = "json"
log_requests_level = "TRACE"

# Plugin directory
plugin_directory = "/vault/plugins"

# Cache configuration for performance
cache {
  use_auto_auth_token = true
  
  # Agent cache settings
  cache {
    type = "memdb"
  }
}

# Entropy augmentation for better randomness
entropy "seal" {
  mode = "augmentation"
}

# License path (for Enterprise features)
license_path = "/vault/config/vault.hclic"

# Raw storage endpoint (disabled for security)
raw_storage_endpoint = false

# Introspection endpoint (disabled for security)
introspection_endpoint = false

# Unauthenticated metrics access (disabled for security)
unauthenticated_metrics_access = false

# Profiling endpoint (disabled for security)
profiling_endpoint = false

# Activity log configuration
activity_log {
  default_report_months = 12
  retention_months = 24
}

# Request limiter for DoS protection
request_limiter {
  type = "remote-addr"
  
  # Rate limiting rules
  limits {
    rate = 1000
    burst = 1000
    interval = "1m"
  }
}