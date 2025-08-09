# Hearthlink Production Deployment

This directory contains all the necessary files and configurations for deploying Hearthlink in a production environment using Docker and Docker Compose.

## Quick Start

1. **Prepare Environment**
   ```bash
   cp .env.production.example .env.production
   nano .env.production  # Update all CHANGE_ME values
   ```

2. **Run Deployment**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

3. **Access Application**
   - Main App: https://hearthlink.local
   - Admin: https://admin.hearthlink.local
   - Monitoring: http://localhost:3000

## Architecture Overview

### Services

- **hearthlink-frontend**: React application served by Nginx
- **hearthlink-api**: Node.js API server
- **hearthlink-agents**: Python agent processing service
- **hearthlink-db**: PostgreSQL database
- **hearthlink-redis**: Redis cache and session store
- **hearthlink-vault**: HashiCorp Vault for secrets management

### Monitoring Stack

- **hearthlink-prometheus**: Metrics collection
- **hearthlink-grafana**: Metrics visualization
- **hearthlink-elasticsearch**: Log storage
- **hearthlink-logstash**: Log processing
- **hearthlink-kibana**: Log visualization

### Security & Backup

- **hearthlink-vault**: Secrets management
- **hearthlink-backup**: Automated backup service

## Configuration

### Environment Variables

All configuration is managed through the `.env.production` file. Key sections include:

#### Database Configuration
```bash
DB_PASSWORD=strong_password_here
DB_HOST=hearthlink-db
DB_PORT=5432
```

#### Security Settings
```bash
JWT_SECRET=your_jwt_secret_minimum_32_chars
ENCRYPTION_KEY=your_aes_256_encryption_key_32_bytes
```

#### API Keys
```bash
OPENAI_API_KEY=sk-your_openai_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

#### Monitoring
```bash
GRAFANA_PASSWORD=admin_password
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project
```

### SSL Certificates

SSL certificates should be placed in the `ssl/` directory:
- `ssl/hearthlink.crt` - Certificate file
- `ssl/hearthlink.key` - Private key file

If certificates are not provided, self-signed certificates will be generated automatically.

### Storage Paths

Configure storage paths in the environment file:
```bash
DATA_PATH=/opt/hearthlink/data
LOGS_PATH=/opt/hearthlink/logs
BACKUP_PATH=/opt/hearthlink/backups
```

## Deployment Process

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space minimum
- Linux server (Ubuntu 20.04+ recommended)

### Deployment Steps

1. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd hearthlink/deploy
   
   # Configure environment
   cp .env.production.example .env.production
   nano .env.production
   ```

2. **SSL Certificate Setup** (Optional)
   ```bash
   # Place your SSL certificates
   mkdir -p ssl
   cp your-cert.crt ssl/hearthlink.crt
   cp your-key.key ssl/hearthlink.key
   ```

3. **Run Deployment**
   ```bash
   # Make script executable
   chmod +x scripts/deploy.sh
   
   # Run deployment
   ./scripts/deploy.sh
   ```

4. **Verify Deployment**
   ```bash
   # Check service status
   docker-compose -f docker-compose.production.yml ps
   
   # View logs
   docker-compose -f docker-compose.production.yml logs -f
   
   # Health check
   curl -f http://localhost/health
   ```

### Advanced Deployment Options

```bash
# Skip backup during deployment
./scripts/deploy.sh --skip-backup

# Force deployment (ignore warnings)
./scripts/deploy.sh --force

# Health check only
./scripts/deploy.sh --check-only
```

## Service Management

### Starting Services
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Stopping Services
```bash
docker-compose -f docker-compose.production.yml down
```

### Restarting Services
```bash
docker-compose -f docker-compose.production.yml restart
```

### Viewing Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f hearthlink-api
```

### Scaling Services
```bash
# Scale agent service
docker-compose -f docker-compose.production.yml up -d --scale hearthlink-agents=3
```

## Monitoring & Maintenance

### Health Checks

All services include health checks that can be monitored:

```bash
# Check all container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Manual health check
curl -f http://localhost/health
curl -f http://localhost:8080/health
curl -f http://localhost:9090/-/healthy
```

### Metrics Dashboard

Access Grafana at http://localhost:3000 with admin credentials from your environment file. Pre-configured dashboards include:

- System Overview
- Application Performance
- Database Metrics
- Agent Performance
- Error Rates and Alerts

### Log Management

Logs are aggregated in Elasticsearch and viewable through Kibana at http://localhost:5601. Log locations:

- Application logs: `$LOGS_PATH/api/`
- Agent logs: `$LOGS_PATH/agents/`
- Frontend logs: `$LOGS_PATH/frontend/`
- Database logs: `$LOGS_PATH/db/`

### Backup & Recovery

Automated backups run daily at 2 AM (configurable). Manual backup:

```bash
# Create manual backup
docker-compose -f docker-compose.production.yml exec hearthlink-backup backup-now

# List backups
docker-compose -f docker-compose.production.yml exec hearthlink-backup list-backups

# Restore from backup
docker-compose -f docker-compose.production.yml exec hearthlink-backup restore-backup <backup-name>
```

## Security Considerations

### Network Security

- All services run in isolated Docker networks
- External access limited to necessary ports (80, 443)
- Internal service communication encrypted
- Rate limiting enabled on all public endpoints

### Data Protection

- All sensitive data encrypted at rest
- Secrets managed through HashiCorp Vault
- Database connections encrypted
- Regular security updates applied

### Access Control

- Admin interface restricted by IP (configurable)
- API authentication required for all operations
- Role-based access control implemented
- Session management with secure cookies

## Troubleshooting

### Common Issues

1. **Services Won't Start**
   ```bash
   # Check container logs
   docker-compose -f docker-compose.production.yml logs <service-name>
   
   # Check disk space
   df -h
   
   # Check memory usage
   free -h
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose -f docker-compose.production.yml exec hearthlink-db pg_isready
   
   # Check database logs
   docker-compose -f docker-compose.production.yml logs hearthlink-db
   ```

3. **SSL Certificate Issues**
   ```bash
   # Verify certificate files
   ls -la ssl/
   
   # Test certificate validity
   openssl x509 -in ssl/hearthlink.crt -text -noout
   ```

4. **Permission Issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER $DATA_PATH
   sudo chown -R $USER:$USER $LOGS_PATH
   ```

### Performance Tuning

1. **Resource Allocation**
   - Adjust container memory limits in docker-compose.yml
   - Scale services based on load
   - Monitor resource usage through Grafana

2. **Database Optimization**
   - Tune PostgreSQL settings for your workload
   - Set up read replicas for scaling
   - Monitor query performance

3. **Caching**
   - Configure Redis caching policies
   - Implement application-level caching
   - Use CDN for static assets

## Updates & Maintenance

### Updating Hearthlink

1. **Backup Current State**
   ```bash
   ./scripts/deploy.sh --skip-backup=false
   ```

2. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

3. **Deploy Updates**
   ```bash
   ./scripts/deploy.sh
   ```

### Regular Maintenance

- **Daily**: Check service health and logs
- **Weekly**: Review monitoring dashboards and alerts
- **Monthly**: Update Docker images and security patches
- **Quarterly**: Review and rotate secrets

## Support

For deployment issues or questions:

1. Check the troubleshooting section above
2. Review service logs for error messages
3. Consult the monitoring dashboards
4. Check the main project documentation

## File Structure

```
deploy/
├── docker-compose.production.yml    # Main compose file
├── .env.production                  # Environment configuration
├── Dockerfile.frontend              # Frontend container
├── Dockerfile.backend               # Backend container (if needed)
├── Dockerfile.agents                # Agent service container (if needed)
├── nginx/
│   ├── nginx.conf                   # Main nginx configuration
│   └── default.conf                 # Site configuration
├── ssl/
│   ├── hearthlink.crt              # SSL certificate
│   └── hearthlink.key              # SSL private key
├── scripts/
│   ├── deploy.sh                   # Main deployment script
│   └── health-check.sh             # Health check script
├── monitoring/
│   ├── prometheus.yml              # Prometheus configuration
│   └── grafana/                    # Grafana dashboards and config
├── logging/
│   └── logstash.conf              # Logstash configuration
└── README.md                       # This file
```