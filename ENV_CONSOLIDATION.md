# Environment File Consolidation

This document describes the consolidated environment configuration system for Hearthlink, which unifies all environment variables into a single, well-documented `.env` file.

## Overview

Previously, Hearthlink used multiple environment files (`.env`, `.env.local`, `.env.development`, `.env.pgvector`, etc.) scattered across the project. This consolidation:

- **Centralizes** all environment variables in a single `.env` file
- **Documents** each variable with clear grouping and comments
- **Validates** required variables on startup
- **Standardizes** environment loading across Node.js and Python services
- **Simplifies** deployment and development setup

## File Structure

### Main Environment File
- **`.env`** - Canonical environment file with all variables grouped by service
- **`.env.example`** - Template file (safe to commit) showing all available variables

### Legacy Files (Deprecated)
The following files are no longer used and can be safely removed:
- `.env.local`
- `.env.development` 
- `.env.production`
- `.env.pgvector`
- `deploy/.env.production`

## Environment Variable Groups

### 1. Application Configuration
```bash
NODE_ENV=development          # Application environment
DEBUG=true                    # Enable debug mode
LOG_LEVEL=info               # Logging level (debug, info, warn, error)
```

### 2. Frontend Configuration (React)
```bash
PORT=3005                           # React dev server port
BROWSER=none                        # Disable auto-browser opening
FAST_REFRESH=false                  # Disable React fast refresh
GENERATE_SOURCEMAP=false           # Disable sourcemap generation

REACT_APP_ENV=development          # React app environment
REACT_APP_HEARTHLINK_API=http://localhost:8000/api  # API endpoint
REACT_APP_CLAUDE_CODE=true         # Enable Claude Code integration
```

### 3. Backend API Configuration
```bash
API_PORT=8000                # Backend API server port
API_HOST=localhost           # API host
CORS_ORIGIN=http://localhost:3005  # CORS allowed origin
```

### 4. Database Configuration
```bash
# Primary SQLite database
DATABASE_URL=sqlite:///hearthlink_data/hearthlink.db

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hearthlink
POSTGRES_USER=hearthlink_user
POSTGRES_PASSWORD=your_secure_password_here

# PGVector for semantic memory
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5432
PGVECTOR_DATABASE=hearthlink_vectors
PGVECTOR_USER=hearthlink_user
PGVECTOR_PASSWORD=hearthlink_secure_pass_2025
PGVECTOR_URL=postgresql://hearthlink_user:hearthlink_secure_pass_2025@localhost:5432/hearthlink_vectors
```

### 5. Security Configuration
```bash
JWT_SECRET=your_jwt_secret_key_here_minimum_32_characters
JWT_EXPIRES_IN=24h
REFRESH_TOKEN_SECRET=your_refresh_token_secret_here
ENCRYPTION_KEY=your_32_character_encryption_key_here
SESSION_SECRET=your_session_secret_here
```

### 6. External API Keys
```bash
# AI Services
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
REACT_APP_GEMINI_API_KEY=your_gemini_api_key_here

# Voice & Audio
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
WHISPER_API_KEY=your_whisper_api_key_here
```

## Using the Environment Loaders

### Python Usage

```python
from src.utils.env_loader import env_loader, get_env, get_env_int, get_env_bool

# Direct access
api_key = get_env('ANTHROPIC_API_KEY', required=True)
port = get_env_int('API_PORT', default=8000)
debug = get_env_bool('DEBUG', default=False)

# Configuration objects
database_config = env_loader.get_database_config()
api_keys = env_loader.get_api_keys()
security_config = env_loader.get_security_config()

# Validation
if not env_loader.validate_required_vars('core'):
    print("Missing required core variables")
    sys.exit(1)
```

### Node.js Usage

```javascript
const { envLoader, getEnv, getEnvInt, getEnvBool } = require('./src/utils/envLoader');

// Direct access
const apiKey = getEnv('ANTHROPIC_API_KEY', null, true); // required
const port = getEnvInt('API_PORT', 8000);
const debug = getEnvBool('DEBUG', false);

// Configuration objects
const databaseConfig = envLoader.getDatabaseConfig();
const apiKeys = envLoader.getApiKeys();
const securityConfig = envLoader.getSecurityConfig();

// Validation
if (!envLoader.validateRequiredVars('core')) {
    console.error('Missing required core variables');
    process.exit(1);
}
```

## Environment Validation

### Required Variables by Service Group

#### Core Service
- `NODE_ENV`
- `DATABASE_URL`
- `JWT_SECRET`
- `ENCRYPTION_KEY`

#### Frontend Service
- `PORT`
- `REACT_APP_HEARTHLINK_API`

#### Database Service
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`

#### AI Services
- `ANTHROPIC_API_KEY`

#### Security Service
- `JWT_SECRET`
- `ENCRYPTION_KEY`
- `SESSION_SECRET`

### Validation Script

Run the environment validation script:

```bash
# Python
python scripts/verify_env.py

# Node.js
node src/utils/envLoader.js
```

## Migration Guide

### For Developers

1. **Remove legacy environment files**:
   ```bash
   rm .env.local .env.development .env.pgvector
   ```

2. **Copy the canonical .env**:
   ```bash
   cp .env.example .env
   ```

3. **Fill in your actual values** in `.env`

4. **Update your code** to use the new environment loaders:
   - Python: `from src.utils.env_loader import get_env`
   - Node.js: `const { getEnv } = require('./src/utils/envLoader')`

### For Deployment

1. **Environment-specific configurations** should override variables via:
   - System environment variables
   - Docker environment files
   - Kubernetes ConfigMaps/Secrets
   - Cloud provider environment settings

2. **Never commit** the actual `.env` file with real values

3. **Use the verification script** in CI/CD pipelines to ensure required variables are present

## Security Best Practices

### Environment File Security
- ✅ **DO** use `.env.example` as a template
- ✅ **DO** document all variables with comments
- ✅ **DO** use strong, unique secrets
- ✅ **DO** validate required variables on startup
- ❌ **DON'T** commit `.env` files with real values
- ❌ **DON'T** use default passwords in production
- ❌ **DON'T** expose API keys in client-side code (except `REACT_APP_*` variables)

### Secret Management
- Use environment variables for secrets in production
- Consider using secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate secrets regularly
- Use different secrets for different environments

## Troubleshooting

### Common Issues

1. **Missing Environment File**
   ```
   Error: Environment file not found: /path/to/.env
   ```
   **Solution**: Copy `.env.example` to `.env` and fill in values

2. **Missing Required Variables**
   ```
   Error: Required environment variable 'JWT_SECRET' is missing
   ```
   **Solution**: Add the missing variable to your `.env` file

3. **Invalid Variable Types**
   ```
   Warning: Invalid integer value for PORT: 'abc'
   ```
   **Solution**: Ensure numeric variables contain valid numbers

4. **Database Connection Issues**
   ```
   Error: Unable to connect to database
   ```
   **Solution**: Verify database configuration variables and ensure services are running

### Getting Help

1. **Run the verification script**: `python scripts/verify_env.py`
2. **Check the environment summary**: Import and call `env_loader.print_summary()`
3. **Review this documentation** for variable requirements
4. **Check the `.env.example`** file for proper variable format

## CI/CD Integration

The environment validation is automatically run in CI/CD via the GitHub Actions workflow:

```yaml
# .github/workflows/env-consolidation.yml
name: Environment Validation
on: [push, pull_request]
jobs:
  validate-env:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Environment Configuration
        run: python scripts/verify_env.py --check-example
```

This ensures that:
- All required variables are documented in `.env.example`
- Environment loaders can successfully parse the configuration
- No deprecated environment files are accidentally committed

## Changelog

### v1.0.0 - Environment Consolidation
- Consolidated all environment files into single `.env`
- Created Python and Node.js environment loaders
- Added comprehensive validation and type conversion
- Implemented CI/CD validation workflow
- Added detailed documentation and migration guide