/**
 * Hearthlink Environment Loader (Node.js)
 * Centralized environment variable loading with validation and type conversion
 */

const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

class EnvironmentLoader {
    constructor(envFilePath = null) {
        this.projectRoot = path.resolve(__dirname, '../../..');
        this.envFile = envFilePath || path.join(this.projectRoot, '.env');
        this.envVars = {};
        
        // Required environment variables grouped by service
        this.REQUIRED_VARS = {
            core: [
                'NODE_ENV',
                'DATABASE_URL',
                'JWT_SECRET',
                'ENCRYPTION_KEY'
            ],
            frontend: [
                'PORT',
                'REACT_APP_HEARTHLINK_API'
            ],
            database: [
                'POSTGRES_HOST',
                'POSTGRES_PORT',
                'POSTGRES_DB',
                'POSTGRES_USER'
            ],
            ai_services: [
                'ANTHROPIC_API_KEY'
            ],
            security: [
                'JWT_SECRET',
                'ENCRYPTION_KEY',
                'SESSION_SECRET'
            ]
        };
        
        // Optional variables with defaults
        this.DEFAULTS = {
            NODE_ENV: 'development',
            DEBUG: 'true',
            LOG_LEVEL: 'info',
            PORT: '3005',
            API_PORT: '8000',
            API_HOST: 'localhost',
            CORS_ORIGIN: 'http://localhost:3005',
            POSTGRES_PORT: '5432',
            REDIS_PORT: '6379',
            JWT_EXPIRES_IN: '24h',
            EMBEDDING_DIMENSION: '384',
            DEFAULT_SIMILARITY_THRESHOLD: '0.7',
            DEFAULT_MAX_RESULTS: '10',
            HEALTH_CHECK_INTERVAL: '30000',
            HEALTH_CHECK_TIMEOUT: '5000'
        };
        
        this.loadEnvironment();
    }
    
    loadEnvironment() {
        try {
            // Load from .env file if it exists
            if (fs.existsSync(this.envFile)) {
                const result = dotenv.config({ path: this.envFile, override: true });
                if (result.error) {
                    console.warn(`Warning loading .env file: ${result.error.message}`);
                } else {
                    console.log(`Loaded environment from ${this.envFile}`);
                }
            } else {
                console.warn(`Environment file not found: ${this.envFile}`);
            }
            
            // Cache all environment variables
            this.envVars = { ...process.env };
            
            // Apply defaults for missing values
            this.applyDefaults();
            
        } catch (error) {
            console.error(`Failed to load environment: ${error.message}`);
            throw error;
        }
    }
    
    applyDefaults() {
        for (const [key, defaultValue] of Object.entries(this.DEFAULTS)) {
            if (!this.envVars[key] || this.envVars[key].trim() === '') {
                this.envVars[key] = defaultValue;
                process.env[key] = defaultValue;
            }
        }
    }
    
    get(key, defaultValue = null, required = false) {
        const value = this.envVars[key] || defaultValue;
        
        if (required && !value) {
            throw new Error(`Required environment variable '${key}' is missing`);
        }
        
        return value;
    }
    
    getInt(key, defaultValue = null, required = false) {
        const value = this.get(key, defaultValue?.toString(), required);
        
        if (value === null || value === undefined) {
            return null;
        }
        
        const intValue = parseInt(value, 10);
        if (isNaN(intValue)) {
            console.warn(`Invalid integer value for ${key}: ${value}`);
            return defaultValue;
        }
        
        return intValue;
    }
    
    getBool(key, defaultValue = null, required = false) {
        const value = this.get(key, defaultValue?.toString().toLowerCase(), required);
        
        if (value === null || value === undefined) {
            return null;
        }
        
        return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
    }
    
    getFloat(key, defaultValue = null, required = false) {
        const value = this.get(key, defaultValue?.toString(), required);
        
        if (value === null || value === undefined) {
            return null;
        }
        
        const floatValue = parseFloat(value);
        if (isNaN(floatValue)) {
            console.warn(`Invalid float value for ${key}: ${value}`);
            return defaultValue;
        }
        
        return floatValue;
    }
    
    getList(key, separator = ',', defaultValue = null, required = false) {
        const value = this.get(key, defaultValue?.join(separator), required);
        
        if (value === null || value === undefined) {
            return null;
        }
        
        return value.split(separator).map(item => item.trim()).filter(item => item.length > 0);
    }
    
    validateRequiredVars(serviceGroup = null) {
        const missingVars = [];
        let requiredVars = [];
        
        if (serviceGroup) {
            requiredVars = this.REQUIRED_VARS[serviceGroup] || [];
        } else {
            // Validate all required variables
            requiredVars = Object.values(this.REQUIRED_VARS).flat();
        }
        
        for (const varName of requiredVars) {
            if (!this.get(varName)) {
                missingVars.push(varName);
            }
        }
        
        return missingVars;
    }
    
    getDatabaseConfig() {
        return {
            databaseUrl: this.get('DATABASE_URL', null, true),
            postgres: {
                host: this.get('POSTGRES_HOST', 'localhost'),
                port: this.getInt('POSTGRES_PORT', 5432),
                database: this.get('POSTGRES_DB', 'hearthlink'),
                user: this.get('POSTGRES_USER', 'hearthlink_user'),
                password: this.get('POSTGRES_PASSWORD')
            },
            pgvector: {
                host: this.get('PGVECTOR_HOST', 'localhost'),
                port: this.getInt('PGVECTOR_PORT', 5432),
                database: this.get('PGVECTOR_DATABASE', 'hearthlink_vectors'),
                user: this.get('PGVECTOR_USER', 'hearthlink_user'),
                password: this.get('PGVECTOR_PASSWORD'),
                url: this.get('PGVECTOR_URL')
            },
            redis: {
                host: this.get('REDIS_HOST', 'localhost'),
                port: this.getInt('REDIS_PORT', 6379),
                password: this.get('REDIS_PASSWORD')
            },
            neo4j: {
                uri: this.get('NEO4J_URI', 'bolt://localhost:7687'),
                user: this.get('NEO4J_USER', 'neo4j'),
                password: this.get('NEO4J_PASSWORD')
            }
        };
    }
    
    getApiKeys() {
        return {
            anthropic: this.get('ANTHROPIC_API_KEY'),
            openai: this.get('OPENAI_API_KEY'),
            google: this.get('GOOGLE_API_KEY'),
            gemini: this.get('REACT_APP_GEMINI_API_KEY'),
            elevenlabs: this.get('ELEVENLABS_API_KEY'),
            whisper: this.get('WHISPER_API_KEY'),
            sentry: this.get('SENTRY_DSN')
        };
    }
    
    getSecurityConfig() {
        return {
            jwtSecret: this.get('JWT_SECRET', null, true),
            jwtExpiresIn: this.get('JWT_EXPIRES_IN', '24h'),
            refreshTokenSecret: this.get('REFRESH_TOKEN_SECRET'),
            encryptionKey: this.get('ENCRYPTION_KEY', null, true),
            sessionSecret: this.get('SESSION_SECRET'),
            corsOrigin: this.get('CORS_ORIGIN', 'http://localhost:3005')
        };
    }
    
    getServiceConfig() {
        return {
            nodeEnv: this.get('NODE_ENV', 'development'),
            debug: this.getBool('DEBUG', true),
            logLevel: this.get('LOG_LEVEL', 'info'),
            frontendPort: this.getInt('PORT', 3005),
            apiPort: this.getInt('API_PORT', 8000),
            apiHost: this.get('API_HOST', 'localhost'),
            healthCheckInterval: this.getInt('HEALTH_CHECK_INTERVAL', 30000),
            healthCheckTimeout: this.getInt('HEALTH_CHECK_TIMEOUT', 5000)
        };
    }
    
    printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('HEARTHLINK ENVIRONMENT CONFIGURATION');
        console.log('='.repeat(60));
        
        const config = this.getServiceConfig();
        console.log(`Environment: ${config.nodeEnv}`);
        console.log(`Debug Mode: ${config.debug}`);
        console.log(`Log Level: ${config.logLevel}`);
        console.log(`Frontend Port: ${config.frontendPort}`);
        console.log(`API Port: ${config.apiPort}`);
        
        // Validate required variables
        const missingVars = this.validateRequiredVars();
        if (missingVars.length > 0) {
            console.log(`\n⚠️  Missing Required Variables: ${missingVars.join(', ')}`);
        } else {
            console.log('\n✅ All required variables are configured');
        }
        
        console.log('='.repeat(60) + '\n');
    }
}

// Global environment loader instance
const envLoader = new EnvironmentLoader();

// Convenience functions for direct access
function getEnv(key, defaultValue = null, required = false) {
    return envLoader.get(key, defaultValue, required);
}

function getEnvInt(key, defaultValue = null, required = false) {
    return envLoader.getInt(key, defaultValue, required);
}

function getEnvBool(key, defaultValue = null, required = false) {
    return envLoader.getBool(key, defaultValue, required);
}

function validateEnvironment(serviceGroup = null) {
    const missingVars = envLoader.validateRequiredVars(serviceGroup);
    if (missingVars.length > 0) {
        console.error(`Missing required environment variables: ${missingVars.join(', ')}`);
        return false;
    }
    return true;
}

// Export the loader and convenience functions
module.exports = {
    EnvironmentLoader,
    envLoader,
    getEnv,
    getEnvInt,
    getEnvBool,
    validateEnvironment
};

// Print environment summary when run directly
if (require.main === module) {
    envLoader.printSummary();
}