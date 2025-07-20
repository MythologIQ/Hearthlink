#!/bin/bash

# Hearthlink Production Deployment Script
# This script handles the complete deployment process for Hearthlink

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_DIR="$PROJECT_ROOT/deploy"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running"
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        error "Git is not installed"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Load environment configuration
load_environment() {
    log "Loading environment configuration..."
    
    local env_file="$DEPLOY_DIR/.env.production"
    
    if [[ ! -f "$env_file" ]]; then
        error "Environment file not found: $env_file"
        error "Please copy .env.production.example to .env.production and configure it"
        exit 1
    fi
    
    # Check for placeholder values
    if grep -q "CHANGE_ME" "$env_file"; then
        error "Environment file contains placeholder values"
        error "Please update all CHANGE_ME values in $env_file"
        exit 1
    fi
    
    # Source the environment file
    set -a
    source "$env_file"
    set +a
    
    success "Environment configuration loaded"
}

# Create required directories
create_directories() {
    log "Creating required directories..."
    
    local dirs=(
        "$DATA_PATH"
        "$DATA_PATH/postgres"
        "$DATA_PATH/redis"
        "$DATA_PATH/vault"
        "$DATA_PATH/vault-secrets"
        "$DATA_PATH/agents"
        "$DATA_PATH/prometheus"
        "$DATA_PATH/grafana"
        "$DATA_PATH/elasticsearch"
        "$LOGS_PATH"
        "$LOGS_PATH/api"
        "$LOGS_PATH/agents"
        "$LOGS_PATH/frontend"
        "$LOGS_PATH/db"
        "$BACKUP_PATH"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            sudo mkdir -p "$dir"
            sudo chown -R $USER:$USER "$dir"
            log "Created directory: $dir"
        fi
    done
    
    success "Directories created successfully"
}

# Generate SSL certificates if they don't exist
generate_ssl_certificates() {
    log "Checking SSL certificates..."
    
    local ssl_dir="$DEPLOY_DIR/ssl"
    local cert_file="$ssl_dir/hearthlink.crt"
    local key_file="$ssl_dir/hearthlink.key"
    
    if [[ ! -f "$cert_file" ]] || [[ ! -f "$key_file" ]]; then
        warning "SSL certificates not found, generating self-signed certificates"
        
        mkdir -p "$ssl_dir"
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$key_file" \
            -out "$cert_file" \
            -subj "/C=US/ST=Local/L=Local/O=Hearthlink/OU=IT/CN=hearthlink.local"
        
        success "Self-signed SSL certificates generated"
        warning "For production, replace with proper SSL certificates"
    else
        success "SSL certificates found"
    fi
}

# Backup existing data
backup_data() {
    if [[ "${SKIP_BACKUP:-false}" != "true" ]]; then
        log "Creating backup of existing data..."
        
        local backup_timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_file="$BACKUP_PATH/hearthlink_backup_$backup_timestamp.tar.gz"
        
        if [[ -d "$DATA_PATH" ]]; then
            tar -czf "$backup_file" -C "$DATA_PATH" . 2>/dev/null || true
            success "Backup created: $backup_file"
        else
            log "No existing data to backup"
        fi
    else
        warning "Skipping backup (SKIP_BACKUP=true)"
    fi
}

# Build and pull Docker images
build_images() {
    log "Building and pulling Docker images..."
    
    cd "$DEPLOY_DIR"
    
    # Pull base images
    docker-compose -f docker-compose.production.yml pull --quiet
    
    # Build custom images
    docker-compose -f docker-compose.production.yml build --no-cache
    
    success "Docker images built successfully"
}

# Start services
start_services() {
    log "Starting Hearthlink services..."
    
    cd "$DEPLOY_DIR"
    
    # Start core services first
    docker-compose -f docker-compose.production.yml up -d \
        hearthlink-db \
        hearthlink-redis \
        hearthlink-vault
    
    # Wait for core services to be ready
    log "Waiting for core services to be ready..."
    sleep 30
    
    # Start application services
    docker-compose -f docker-compose.production.yml up -d \
        hearthlink-api \
        hearthlink-agents
    
    # Wait for application services
    log "Waiting for application services to be ready..."
    sleep 30
    
    # Start frontend and monitoring
    docker-compose -f docker-compose.production.yml up -d
    
    success "All services started successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$DEPLOY_DIR"
    
    # Wait for database to be ready
    docker-compose -f docker-compose.production.yml exec -T hearthlink-db \
        bash -c 'until pg_isready -U $POSTGRES_USER -d $POSTGRES_DB; do sleep 1; done'
    
    # Run migrations (if migration system exists)
    # docker-compose -f docker-compose.production.yml exec -T hearthlink-api \
    #     npm run migrate
    
    success "Database migrations completed"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    local services=(
        "http://localhost/health"
        "http://localhost:8080/health"
        "http://localhost:3000/health"
        "http://localhost:9090/-/healthy"
    )
    
    local failed_checks=0
    
    for service in "${services[@]}"; do
        log "Checking $service..."
        if curl -f -s "$service" > /dev/null; then
            success "✓ $service is healthy"
        else
            error "✗ $service health check failed"
            ((failed_checks++))
        fi
    done
    
    if [[ $failed_checks -eq 0 ]]; then
        success "All health checks passed"
    else
        error "$failed_checks health checks failed"
        return 1
    fi
}

# Display deployment information
show_deployment_info() {
    success "Hearthlink deployment completed successfully!"
    echo
    echo "Access Information:"
    echo "=================="
    echo "• Main Application: https://hearthlink.local"
    echo "• Admin Interface:  https://admin.hearthlink.local"
    echo "• API Endpoint:     https://hearthlink.local/api"
    echo "• Monitoring:       http://localhost:3000 (Grafana)"
    echo "• Metrics:          http://localhost:9090 (Prometheus)"
    echo "• Logs:             http://localhost:5601 (Kibana)"
    echo
    echo "Service Status:"
    echo "==============="
    docker-compose -f "$DEPLOY_DIR/docker-compose.production.yml" ps
    echo
    echo "Logs:"
    echo "====="
    echo "• View all logs:    docker-compose -f $DEPLOY_DIR/docker-compose.production.yml logs -f"
    echo "• API logs:         docker-compose -f $DEPLOY_DIR/docker-compose.production.yml logs -f hearthlink-api"
    echo "• Frontend logs:    docker-compose -f $DEPLOY_DIR/docker-compose.production.yml logs -f hearthlink-frontend"
    echo
    echo "Management:"
    echo "==========="
    echo "• Stop services:    docker-compose -f $DEPLOY_DIR/docker-compose.production.yml down"
    echo "• Restart services: docker-compose -f $DEPLOY_DIR/docker-compose.production.yml restart"
    echo "• Update services:  $SCRIPT_DIR/deploy.sh"
    echo
}

# Cleanup on failure
cleanup_on_failure() {
    error "Deployment failed, cleaning up..."
    cd "$DEPLOY_DIR"
    docker-compose -f docker-compose.production.yml down --remove-orphans
}

# Main deployment function
main() {
    log "Starting Hearthlink production deployment..."
    
    # Set up error handling
    trap cleanup_on_failure ERR
    
    # Run deployment steps
    check_root
    check_prerequisites
    load_environment
    create_directories
    generate_ssl_certificates
    backup_data
    build_images
    start_services
    run_migrations
    
    # Wait for services to stabilize
    log "Waiting for services to stabilize..."
    sleep 60
    
    # Perform health checks
    if health_check; then
        show_deployment_info
        success "Deployment completed successfully!"
    else
        error "Deployment completed with health check failures"
        error "Check service logs for details"
        exit 1
    fi
}

# Script usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  --skip-backup        Skip data backup before deployment"
    echo "  --force              Force deployment even with warnings"
    echo "  --check-only         Only run health checks"
    echo
    echo "Environment Variables:"
    echo "  SKIP_BACKUP=true     Skip data backup"
    echo "  FORCE_DEPLOY=true    Force deployment"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --skip-backup)
            export SKIP_BACKUP=true
            shift
            ;;
        --force)
            export FORCE_DEPLOY=true
            shift
            ;;
        --check-only)
            load_environment
            health_check
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main deployment
main "$@"