# HashiCorp Vault Policy for Key Rotation Service
# Minimal permissions required for automated key rotation

# Path for storing and managing keys
path "secret/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Path for key metadata
path "secret/metadata/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Path for compliance and audit data
path "secret/data/compliance/*" {
  capabilities = ["create", "read", "update", "list"]
}

# Database secrets engine (if used)
path "database/config/*" {
  capabilities = ["read", "update"]
}

path "database/creds/*" {
  capabilities = ["read"]
}

path "database/rotate-credentials/*" {
  capabilities = ["update"]
}

# PKI secrets engine for certificate rotation
path "pki/issue/*" {
  capabilities = ["create", "update"]
}

path "pki/revoke" {
  capabilities = ["create", "update"]
}

# AWS secrets engine for IAM credential rotation
path "aws/config/root" {
  capabilities = ["read", "update"]
}

path "aws/creds/*" {
  capabilities = ["read"]
}

path "aws/rotate-credentials/*" {
  capabilities = ["update"]
}

# System capabilities for service operation
path "sys/health" {
  capabilities = ["read"]
}

path "sys/capabilities-self" {
  capabilities = ["read"]
}

path "sys/auth" {
  capabilities = ["read"]
}

# Audit log access (read-only)
path "sys/audit" {
  capabilities = ["read"]
}

# Token management for service token renewal
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Lease management
path "sys/leases/lookup" {
  capabilities = ["create"]
}

path "sys/leases/renew" {
  capabilities = ["create"]
}

path "sys/leases/revoke" {
  capabilities = ["create"]
}

# Cubbyhole for temporary storage during rotation
path "cubbyhole/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Identity secrets engine for service account management
path "identity/entity/id/*" {
  capabilities = ["read", "update"]
}

path "identity/entity-alias/id/*" {
  capabilities = ["read", "update"]
}

# Transform secrets engine for format-preserving encryption
path "transform/decode/*" {
  capabilities = ["create", "update"]
}

path "transform/encode/*" {
  capabilities = ["create", "update"]
}

# TOTP secrets engine for time-based one-time passwords
path "totp/keys/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "totp/code/*" {
  capabilities = ["create", "update"]
}