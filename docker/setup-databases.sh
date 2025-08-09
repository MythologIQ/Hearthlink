#!/bin/bash

# Database setup script for Hearthlink
# This script sets up Neo4j, Redis, and Qdrant within the Hearthlink project structure

HEARTHLINK_ROOT="/mnt/g/MythologIQ/Hearthlink"
DOCKER_ROOT="${HEARTHLINK_ROOT}/docker"
DATA_ROOT="${DOCKER_ROOT}/data"
CONFIG_ROOT="${DOCKER_ROOT}/config"

echo "Setting up Hearthlink databases..."

# Create data directories
mkdir -p "${DATA_ROOT}/neo4j"/{data,logs,import,plugins}
mkdir -p "${DATA_ROOT}/redis"
mkdir -p "${DATA_ROOT}/qdrant"

# Create config directories
mkdir -p "${CONFIG_ROOT}/neo4j"
mkdir -p "${CONFIG_ROOT}/redis"
mkdir -p "${CONFIG_ROOT}/qdrant"

# Neo4j configuration
cat > "${CONFIG_ROOT}/neo4j/neo4j.conf" << EOF
# Neo4j Configuration for Hearthlink
server.default_listen_address=0.0.0.0
server.bolt.listen_address=0.0.0.0:7687
server.http.listen_address=0.0.0.0:7474
server.directories.data=${DATA_ROOT}/neo4j/data
server.directories.logs=${DATA_ROOT}/neo4j/logs
server.directories.import=${DATA_ROOT}/neo4j/import
server.directories.plugins=${DATA_ROOT}/neo4j/plugins
dbms.security.auth_enabled=true
initial.dbms.default_database=hearthlink
EOF

# Redis configuration
cat > "${CONFIG_ROOT}/redis/redis.conf" << EOF
# Redis Configuration for Hearthlink
bind 0.0.0.0
port 6379
requirepass hearthlink_redis_2025
appendonly yes
appendfsync everysec
dir ${DATA_ROOT}/redis
logfile ${DATA_ROOT}/redis/redis.log
EOF

# Qdrant configuration
cat > "${CONFIG_ROOT}/qdrant/config.yaml" << EOF
# Qdrant Configuration for Hearthlink
service:
  http_port: 6333
  grpc_port: 6334
  host: 0.0.0.0

storage:
  storage_path: ${DATA_ROOT}/qdrant
  snapshots_path: ${DATA_ROOT}/qdrant/snapshots
  temp_path: ${DATA_ROOT}/qdrant/tmp

cluster:
  enabled: false

log_level: INFO
EOF

echo "Database configuration files created successfully!"
echo "Data directories: ${DATA_ROOT}"
echo "Config directories: ${CONFIG_ROOT}"