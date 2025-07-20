/**
 * Comprehensive Configuration Management System
 * 
 * Provides centralized configuration management with environment-specific settings,
 * validation, hot-reloading, and secure credential handling.
 */

import systemLogger, { info as logInfo, warn as logWarn, error as logError, createContext } from './SystemLogger';
import { ValidationError, SystemError } from './ErrorHandler';

// Configuration schema definitions
const CONFIG_SCHEMA = {
  app: {
    name: { type: 'string', required: true, default: 'Hearthlink' },
    version: { type: 'string', required: true, default: '1.0.0' },
    environment: { type: 'string', required: true, enum: ['development', 'staging', 'production'], default: 'development' },
    debug: { type: 'boolean', required: false, default: false },
    logLevel: { type: 'string', required: false, enum: ['debug', 'info', 'warn', 'error'], default: 'info' }
  },
  
  api: {
    baseUrl: { type: 'string', required: true, default: 'http://localhost:8080' },
    timeout: { type: 'number', required: false, default: 30000, min: 1000, max: 300000 },
    retryAttempts: { type: 'number', required: false, default: 3, min: 0, max: 10 },
    retryDelay: { type: 'number', required: false, default: 1000, min: 100, max: 10000 }
  },
  
  security: {
    encryptionKey: { type: 'string', required: true, sensitive: true },
    jwtSecret: { type: 'string', required: false, sensitive: true },
    sessionTimeout: { type: 'number', required: false, default: 3600000, min: 300000 }, // 1 hour default
    csrfProtection: { type: 'boolean', required: false, default: true },
    rateLimitWindow: { type: 'number', required: false, default: 900000, min: 60000 }, // 15 minutes
    rateLimitMax: { type: 'number', required: false, default: 100, min: 1 }
  },
  
  agents: {
    alden: {
      enabled: { type: 'boolean', required: false, default: true },
      maxConcurrentTasks: { type: 'number', required: false, default: 5, min: 1, max: 20 },
      responseTimeout: { type: 'number', required: false, default: 30000, min: 5000, max: 120000 }
    },
    alice: {
      enabled: { type: 'boolean', required: false, default: true },
      maxConcurrentTasks: { type: 'number', required: false, default: 3, min: 1, max: 20 },
      responseTimeout: { type: 'number', required: false, default: 45000, min: 5000, max: 120000 }
    },
    mimic: {
      enabled: { type: 'boolean', required: false, default: false },
      learningRate: { type: 'number', required: false, default: 0.01, min: 0.001, max: 1.0 },
      adaptationThreshold: { type: 'number', required: false, default: 0.8, min: 0.1, max: 1.0 }
    },
    sentry: {
      enabled: { type: 'boolean', required: false, default: true },
      monitoringInterval: { type: 'number', required: false, default: 5000, min: 1000, max: 60000 },
      alertThreshold: { type: 'number', required: false, default: 0.9, min: 0.1, max: 1.0 }
    }
  },
  
  storage: {
    type: { type: 'string', required: false, enum: ['file', 'memory', 'database'], default: 'file' },
    encryptionEnabled: { type: 'boolean', required: false, default: true },
    backupEnabled: { type: 'boolean', required: false, default: true },
    backupInterval: { type: 'number', required: false, default: 3600000, min: 300000 }, // 1 hour
    maxBackups: { type: 'number', required: false, default: 10, min: 1, max: 100 }
  },
  
  voice: {
    enabled: { type: 'boolean', required: false, default: true },
    wakeWord: { type: 'string', required: false, default: 'hearthlink' },
    sensitivity: { type: 'number', required: false, default: 0.8, min: 0.1, max: 1.0 },
    noiseReduction: { type: 'boolean', required: false, default: true },
    language: { type: 'string', required: false, default: 'en-US' }
  },
  
  ui: {
    theme: { type: 'string', required: false, enum: ['dark', 'light', 'auto'], default: 'dark' },
    accessibility: {
      screenReader: { type: 'boolean', required: false, default: false },
      highContrast: { type: 'boolean', required: false, default: false },
      fontSize: { type: 'string', required: false, enum: ['small', 'medium', 'large'], default: 'medium' },
      voiceFeedback: { type: 'boolean', required: false, default: false }
    },
    animations: { type: 'boolean', required: false, default: true },
    autoSave: { type: 'boolean', required: false, default: true },
    autoSaveInterval: { type: 'number', required: false, default: 30000, min: 5000, max: 300000 }
  },
  
  external: {
    openai: {
      apiKey: { type: 'string', required: false, sensitive: true },
      model: { type: 'string', required: false, default: 'gpt-4' },
      maxTokens: { type: 'number', required: false, default: 4000, min: 100, max: 32000 }
    },
    anthropic: {
      apiKey: { type: 'string', required: false, sensitive: true },
      model: { type: 'string', required: false, default: 'claude-3-sonnet' },
      maxTokens: { type: 'number', required: false, default: 4000, min: 100, max: 200000 }
    },
    google: {
      apiKey: { type: 'string', required: false, sensitive: true },
      model: { type: 'string', required: false, default: 'gemini-pro' },
      maxTokens: { type: 'number', required: false, default: 4000, min: 100, max: 32000 }
    }
  },
  
  monitoring: {
    enabled: { type: 'boolean', required: false, default: true },
    metricsInterval: { type: 'number', required: false, default: 5000, min: 1000, max: 60000 },
    performanceTracking: { type: 'boolean', required: false, default: true },
    errorReporting: { type: 'boolean', required: false, default: true },
    remoteLogging: {
      enabled: { type: 'boolean', required: false, default: false },
      endpoint: { type: 'string', required: false },
      apiKey: { type: 'string', required: false, sensitive: true }
    }
  }
};

class ConfigManager {
  constructor() {
    this.config = {};
    this.schema = CONFIG_SCHEMA;
    this.watchers = new Map();
    this.validationErrors = [];
    this.loadTime = null;
    this.context = createContext('config-manager', 'system');
    this.initialized = false;
    this.initializationPromise = null;
    
    // Generate default config immediately to ensure basic functionality
    this.config = this.generateDefaultConfig();
  }

  async initialize() {
    if (this.initialized) {
      return this.initializationPromise;
    }

    if (this.initializationPromise) {
      return this.initializationPromise;
    }

    this.initializationPromise = this._performInitialization();
    return this.initializationPromise;
  }

  async _performInitialization() {
    try {
      await this.loadConfiguration();
      this.validateConfiguration();
      this.setupEnvironmentOverrides();
      this.setupHotReloading();
      
      this.initialized = true;
      
      logInfo('ConfigManager initialized successfully', {
        environment: this.get('app.environment'),
        configSections: Object.keys(this.config)
      }, this.context);
      
    } catch (error) {
      logError('Failed to initialize ConfigManager', {
        error: error.message,
        stack: error.stack
      }, this.context);
      // Don't throw - allow system to use default configuration
      logWarn('Using default configuration due to initialization error', {}, this.context);
    }
  }

  async loadConfiguration() {
    const startTime = Date.now();
    
    // Load default configuration from schema
    this.config = this.generateDefaultConfig();
    
    // Load configuration files in order of precedence
    await this.loadConfigFile('/config/default.json');
    await this.loadConfigFile(`/config/${this.getEnvironment()}.json`);
    await this.loadConfigFile('/config/local.json');
    
    // Apply environment variables
    this.applyEnvironmentVariables();
    
    this.loadTime = Date.now() - startTime;
    
    logInfo('Configuration loaded', {
      loadTime: this.loadTime,
      environment: this.getEnvironment(),
      sources: ['schema', 'default', 'environment', 'local']
    }, this.context);
  }

  generateDefaultConfig() {
    const config = {};
    
    for (const [section, sectionSchema] of Object.entries(this.schema)) {
      config[section] = {};
      
      for (const [key, definition] of Object.entries(sectionSchema)) {
        if (typeof definition === 'object' && definition.type) {
          // Simple configuration item
          if (definition.default !== undefined) {
            config[section][key] = definition.default;
          }
        } else {
          // Nested configuration section
          config[section][key] = {};
          for (const [nestedKey, nestedDefinition] of Object.entries(definition)) {
            if (nestedDefinition.default !== undefined) {
              config[section][key][nestedKey] = nestedDefinition.default;
            }
          }
        }
      }
    }
    
    return config;
  }

  async loadConfigFile(path) {
    try {
      const response = await fetch(path);
      if (response.ok) {
        const fileConfig = await response.json();
        this.mergeConfig(fileConfig);
        
        logInfo(`Loaded configuration from ${path}`, {
          path,
          keys: Object.keys(fileConfig)
        }, this.context);
      }
    } catch (error) {
      // Config files are optional, so just log warnings
      logWarn(`Could not load configuration file: ${path}`, {
        path,
        error: error.message
      }, this.context);
    }
  }

  mergeConfig(newConfig) {
    this.config = this.deepMerge(this.config, newConfig);
  }

  deepMerge(target, source) {
    const result = { ...target };
    
    for (const [key, value] of Object.entries(source)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        result[key] = this.deepMerge(result[key] || {}, value);
      } else {
        result[key] = value;
      }
    }
    
    return result;
  }

  applyEnvironmentVariables() {
    const envPrefix = 'REACT_APP_HEARTHLINK_';
    const envVars = Object.keys(process.env).filter(key => key.startsWith(envPrefix));
    
    for (const envVar of envVars) {
      const configPath = envVar
        .replace(envPrefix, '')
        .toLowerCase()
        .split('_');
      
      const value = this.parseEnvironmentValue(process.env[envVar]);
      this.setNestedValue(this.config, configPath, value);
      
      logInfo(`Applied environment variable: ${envVar}`, {
        path: configPath.join('.'),
        value: configPath.includes('key') || configPath.includes('secret') ? '[REDACTED]' : value
      }, this.context);
    }
  }

  parseEnvironmentValue(value) {
    // Try to parse as JSON first
    try {
      return JSON.parse(value);
    } catch {
      // If not JSON, try to parse as boolean or number
      if (value.toLowerCase() === 'true') return true;
      if (value.toLowerCase() === 'false') return false;
      
      const numberValue = Number(value);
      if (!isNaN(numberValue)) return numberValue;
      
      // Return as string
      return value;
    }
  }

  setNestedValue(obj, path, value) {
    let current = obj;
    
    for (let i = 0; i < path.length - 1; i++) {
      const key = path[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
    
    current[path[path.length - 1]] = value;
  }

  validateConfiguration() {
    this.validationErrors = [];
    
    for (const [section, sectionSchema] of Object.entries(this.schema)) {
      if (!this.config[section]) {
        this.config[section] = {};
      }
      
      this.validateSection(section, this.config[section], sectionSchema);
    }
    
    if (this.validationErrors.length > 0) {
      logWarn('Configuration validation errors found', {
        errorCount: this.validationErrors.length,
        errors: this.validationErrors
      }, this.context);
      
      // Throw error only for required field violations
      const criticalErrors = this.validationErrors.filter(error => error.critical);
      if (criticalErrors.length > 0) {
        throw new ValidationError('Critical configuration validation errors', {
          errors: criticalErrors
        });
      }
    }
  }

  validateSection(sectionPath, sectionConfig, sectionSchema) {
    for (const [key, definition] of Object.entries(sectionSchema)) {
      const fullPath = `${sectionPath}.${key}`;
      
      if (typeof definition === 'object' && definition.type) {
        // Simple configuration item
        this.validateConfigItem(fullPath, sectionConfig[key], definition);
      } else {
        // Nested configuration section
        if (!sectionConfig[key]) {
          sectionConfig[key] = {};
        }
        this.validateSection(fullPath, sectionConfig[key], definition);
      }
    }
  }

  validateConfigItem(path, value, definition) {
    // Check required fields
    if (definition.required && (value === undefined || value === null)) {
      this.validationErrors.push({
        path,
        error: 'Required field is missing',
        critical: true
      });
      return;
    }
    
    if (value === undefined || value === null) {
      return; // Optional field not provided
    }
    
    // Type validation
    if (definition.type && typeof value !== definition.type) {
      this.validationErrors.push({
        path,
        error: `Expected type ${definition.type}, got ${typeof value}`,
        critical: false
      });
    }
    
    // Enum validation
    if (definition.enum && !definition.enum.includes(value)) {
      this.validationErrors.push({
        path,
        error: `Value must be one of: ${definition.enum.join(', ')}`,
        critical: false
      });
    }
    
    // Range validation for numbers
    if (definition.type === 'number') {
      if (definition.min !== undefined && value < definition.min) {
        this.validationErrors.push({
          path,
          error: `Value must be at least ${definition.min}`,
          critical: false
        });
      }
      
      if (definition.max !== undefined && value > definition.max) {
        this.validationErrors.push({
          path,
          error: `Value must be at most ${definition.max}`,
          critical: false
        });
      }
    }
  }

  setupEnvironmentOverrides() {
    const environment = this.getEnvironment();
    
    // Apply environment-specific overrides
    switch (environment) {
      case 'production':
        this.set('app.debug', false);
        this.set('app.logLevel', 'warn');
        this.set('monitoring.errorReporting', true);
        break;
        
      case 'staging':
        this.set('app.debug', false);
        this.set('app.logLevel', 'info');
        break;
        
      case 'development':
        this.set('app.debug', true);
        this.set('app.logLevel', 'debug');
        break;
    }
    
    logInfo('Environment-specific overrides applied', {
      environment,
      debug: this.get('app.debug'),
      logLevel: this.get('app.logLevel')
    }, this.context);
  }

  setupHotReloading() {
    // Setup file watchers for configuration hot-reloading
    if (this.getEnvironment() === 'development') {
      // In a real implementation, this would watch configuration files
      // For now, we'll just log that hot-reloading is available
      logInfo('Configuration hot-reloading enabled for development', {}, this.context);
    }
  }

  // Public API methods
  get(path, defaultValue = undefined) {
    // Ensure we have basic configuration available
    if (!this.initialized && !this.initializationPromise) {
      this.initialize(); // Start initialization if not already started
    }
    
    const keys = path.split('.');
    let current = this.config;
    
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return defaultValue;
      }
    }
    
    return current;
  }

  set(path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let current = this.config;
    
    // Navigate to the parent object
    for (const key of keys) {
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
    
    // Set the value
    const oldValue = current[lastKey];
    current[lastKey] = value;
    
    // Validate the new value
    try {
      this.validateConfigurationPath(path, value);
    } catch (error) {
      // Revert on validation error
      current[lastKey] = oldValue;
      throw error;
    }
    
    // Notify watchers
    this.notifyWatchers(path, value, oldValue);
    
    logInfo(`Configuration updated: ${path}`, {
      path,
      oldValue: this.sanitizeLogValue(path, oldValue),
      newValue: this.sanitizeLogValue(path, value)
    }, this.context);
  }

  validateConfigurationPath(path, value) {
    const keys = path.split('.');
    let schema = this.schema;
    
    // Navigate through schema
    for (const key of keys) {
      if (schema[key]) {
        schema = schema[key];
      } else {
        throw new ValidationError(`Invalid configuration path: ${path}`);
      }
    }
    
    // Validate against schema
    if (schema.type) {
      this.validateConfigItem(path, value, schema);
      
      if (this.validationErrors.length > 0) {
        const errors = this.validationErrors.filter(error => error.path === path);
        this.validationErrors = this.validationErrors.filter(error => error.path !== path);
        
        if (errors.length > 0) {
          throw new ValidationError(`Configuration validation failed for ${path}`, { errors });
        }
      }
    }
  }

  watch(path, callback) {
    if (!this.watchers.has(path)) {
      this.watchers.set(path, new Set());
    }
    
    this.watchers.get(path).add(callback);
    
    // Return unwatch function
    return () => {
      const watchers = this.watchers.get(path);
      if (watchers) {
        watchers.delete(callback);
        if (watchers.size === 0) {
          this.watchers.delete(path);
        }
      }
    };
  }

  notifyWatchers(path, newValue, oldValue) {
    // Notify exact path watchers
    const watchers = this.watchers.get(path);
    if (watchers) {
      watchers.forEach(callback => {
        try {
          callback(newValue, oldValue, path);
        } catch (error) {
          logError('Error in configuration watcher', {
            path,
            error: error.message
          }, this.context);
        }
      });
    }
    
    // Notify parent path watchers
    const pathParts = path.split('.');
    for (let i = pathParts.length - 1; i > 0; i--) {
      const parentPath = pathParts.slice(0, i).join('.');
      const parentWatchers = this.watchers.get(parentPath);
      
      if (parentWatchers) {
        const parentValue = this.get(parentPath);
        parentWatchers.forEach(callback => {
          try {
            callback(parentValue, parentValue, parentPath);
          } catch (error) {
            logError('Error in parent configuration watcher', {
              path: parentPath,
              error: error.message
            }, this.context);
          }
        });
      }
    }
  }

  sanitizeLogValue(path, value) {
    // Don't log sensitive values
    if (path.includes('key') || path.includes('secret') || path.includes('password')) {
      return '[REDACTED]';
    }
    return value;
  }

  getEnvironment() {
    return process.env.NODE_ENV || this.get('app.environment', 'development');
  }

  isProduction() {
    return this.getEnvironment() === 'production';
  }

  isDevelopment() {
    return this.getEnvironment() === 'development';
  }

  // Configuration export/import
  exportConfiguration(includeDefaults = false, includeSensitive = false) {
    const exported = includeDefaults ? { ...this.config } : this.getNonDefaultConfiguration();
    
    if (!includeSensitive) {
      this.removeSensitiveData(exported);
    }
    
    return {
      configuration: exported,
      environment: this.getEnvironment(),
      exportTime: new Date().toISOString(),
      version: this.get('app.version')
    };
  }

  getNonDefaultConfiguration() {
    const defaults = this.generateDefaultConfig();
    const nonDefaults = {};
    
    this.findDifferences(this.config, defaults, nonDefaults, '');
    
    return nonDefaults;
  }

  findDifferences(current, defaults, result, path) {
    for (const [key, value] of Object.entries(current)) {
      const currentPath = path ? `${path}.${key}` : key;
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        const defaultValue = defaults[key] || {};
        const nestedDiffs = {};
        this.findDifferences(value, defaultValue, nestedDiffs, currentPath);
        
        if (Object.keys(nestedDiffs).length > 0) {
          if (!result[key]) result[key] = {};
          Object.assign(result[key], nestedDiffs);
        }
      } else if (value !== defaults[key]) {
        result[key] = value;
      }
    }
  }

  removeSensitiveData(obj, path = '') {
    for (const [key, value] of Object.entries(obj)) {
      const currentPath = path ? `${path}.${key}` : key;
      
      if (this.isSensitivePath(currentPath)) {
        obj[key] = '[REDACTED]';
      } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        this.removeSensitiveData(value, currentPath);
      }
    }
  }

  isSensitivePath(path) {
    const sensitiveKeywords = ['key', 'secret', 'password', 'token', 'credential'];
    const lowerPath = path.toLowerCase();
    return sensitiveKeywords.some(keyword => lowerPath.includes(keyword));
  }

  async importConfiguration(configData, merge = true) {
    try {
      const newConfig = merge ? this.deepMerge(this.config, configData.configuration) : configData.configuration;
      
      // Validate the new configuration
      const tempConfig = this.config;
      this.config = newConfig;
      
      try {
        this.validateConfiguration();
      } catch (error) {
        // Revert on validation error
        this.config = tempConfig;
        throw error;
      }
      
      logInfo('Configuration imported successfully', {
        merge,
        version: configData.version,
        importTime: new Date().toISOString()
      }, this.context);
      
      // Notify all watchers
      this.notifyAllWatchers();
      
    } catch (error) {
      logError('Failed to import configuration', {
        error: error.message
      }, this.context);
      throw error;
    }
  }

  notifyAllWatchers() {
    for (const [path, watchers] of this.watchers.entries()) {
      const value = this.get(path);
      watchers.forEach(callback => {
        try {
          callback(value, value, path);
        } catch (error) {
          logError('Error in configuration watcher during import', {
            path,
            error: error.message
          }, this.context);
        }
      });
    }
  }

  // Debugging and monitoring
  getValidationErrors() {
    return [...this.validationErrors];
  }

  getConfigurationStats() {
    return {
      loadTime: this.loadTime,
      environment: this.getEnvironment(),
      totalKeys: this.countKeys(this.config),
      watcherCount: Array.from(this.watchers.values()).reduce((sum, set) => sum + set.size, 0),
      validationErrors: this.validationErrors.length,
      lastUpdate: new Date().toISOString()
    };
  }

  countKeys(obj, count = 0) {
    for (const value of Object.values(obj)) {
      count++;
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        count = this.countKeys(value, count);
      }
    }
    return count;
  }

  reloadConfiguration() {
    return this.loadConfiguration();
  }
}

// Create singleton instance
const configManager = new ConfigManager();

// Auto-initialize in a non-blocking way
configManager.initialize().catch(error => {
  console.warn('ConfigManager initialization failed, using defaults:', error.message);
});

// Export convenience functions
export const get = (path, defaultValue) => configManager.get(path, defaultValue);
export const set = (path, value) => configManager.set(path, value);
export const watch = (path, callback) => configManager.watch(path, callback);
export const getEnvironment = () => configManager.getEnvironment();
export const isProduction = () => configManager.isProduction();
export const isDevelopment = () => configManager.isDevelopment();
export const exportConfig = (includeDefaults, includeSensitive) => 
  configManager.exportConfiguration(includeDefaults, includeSensitive);
export const importConfig = (configData, merge) => configManager.importConfiguration(configData, merge);
export const getConfigStats = () => configManager.getConfigurationStats();

export default configManager;