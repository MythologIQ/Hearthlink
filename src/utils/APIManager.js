/**
 * Comprehensive Cross-Module API Communication Manager
 * 
 * Provides centralized API management, inter-module communication,
 * event-driven architecture, and service orchestration.
 */

import systemLogger, { info as logInfo, warn as logWarn, error as logError, apiCall, createContext } from './SystemLogger';
import { NetworkError, SystemError, ValidationError, handleError } from './ErrorHandler';
import { get as getConfig } from './ConfigManager';
import { checkPermission, PERMISSIONS } from './AuthenticationManager';

// API types and constants
export const API_TYPES = {
  INTERNAL: 'internal',
  EXTERNAL: 'external',
  WEBHOOK: 'webhook',
  EVENT: 'event'
};

export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
  PATCH: 'PATCH'
};

export const EVENT_TYPES = {
  MODULE_EVENT: 'module_event',
  SYSTEM_EVENT: 'system_event',
  USER_EVENT: 'user_event',
  AGENT_EVENT: 'agent_event',
  ERROR_EVENT: 'error_event'
};

// Module registry for inter-module communication
export const MODULES = {
  ALDEN: 'alden',
  ALICE: 'alice',
  MIMIC: 'mimic',
  SENTRY: 'sentry',
  CORE: 'core',
  VAULT: 'vault',
  SYNAPSE: 'synapse'
};

class APIManager {
  constructor() {
    this.services = new Map();
    this.eventListeners = new Map();
    this.apiEndpoints = new Map();
    this.webhooks = new Map();
    this.requestInterceptors = [];
    this.responseInterceptors = [];
    this.rateLimiters = new Map();
    this.circuitBreakers = new Map();
    this.context = createContext('api-manager', 'communication');
    
    this.initialize();
  }

  async initialize() {
    try {
      // Setup internal module APIs
      this.setupModuleAPIs();
      
      // Setup event system
      this.setupEventSystem();
      
      // Setup external API management
      this.setupExternalAPIs();
      
      // Setup request/response interceptors
      this.setupInterceptors();
      
      // Setup rate limiting and circuit breakers
      this.setupRateLimiting();
      
      logInfo('APIManager initialized successfully', {
        moduleCount: this.services.size,
        endpointCount: this.apiEndpoints.size
      }, this.context);
      
    } catch (error) {
      logError('Failed to initialize APIManager', {
        error: error.message,
        stack: error.stack
      }, this.context);
      throw new SystemError('API Manager initialization failed', { originalError: error });
    }
  }

  setupModuleAPIs() {
    // Register internal module services
    this.registerService(MODULES.ALDEN, {
      baseUrl: '/api/alden',
      endpoints: {
        process: { method: HTTP_METHODS.POST, path: '/process' },
        status: { method: HTTP_METHODS.GET, path: '/status' },
        capabilities: { method: HTTP_METHODS.GET, path: '/capabilities' }
      },
      requiredPermissions: [PERMISSIONS.AGENT_INTERACT]
    });

    this.registerService(MODULES.ALICE, {
      baseUrl: '/api/alice',
      endpoints: {
        analyze: { method: HTTP_METHODS.POST, path: '/analyze' },
        status: { method: HTTP_METHODS.GET, path: '/status' },
        memory: { method: HTTP_METHODS.GET, path: '/memory' }
      },
      requiredPermissions: [PERMISSIONS.AGENT_INTERACT]
    });

    this.registerService(MODULES.MIMIC, {
      baseUrl: '/api/mimic',
      endpoints: {
        learn: { method: HTTP_METHODS.POST, path: '/learn' },
        adapt: { method: HTTP_METHODS.POST, path: '/adapt' },
        status: { method: HTTP_METHODS.GET, path: '/status' }
      },
      requiredPermissions: [PERMISSIONS.AGENT_INTERACT]
    });

    this.registerService(MODULES.SENTRY, {
      baseUrl: '/api/sentry',
      endpoints: {
        monitor: { method: HTTP_METHODS.POST, path: '/monitor' },
        alerts: { method: HTTP_METHODS.GET, path: '/alerts' },
        status: { method: HTTP_METHODS.GET, path: '/status' }
      },
      requiredPermissions: [PERMISSIONS.SYSTEM_ADMIN]
    });

    this.registerService(MODULES.CORE, {
      baseUrl: '/api/core',
      endpoints: {
        orchestrate: { method: HTTP_METHODS.POST, path: '/orchestrate' },
        status: { method: HTTP_METHODS.GET, path: '/status' },
        metrics: { method: HTTP_METHODS.GET, path: '/metrics' }
      },
      requiredPermissions: [PERMISSIONS.SYSTEM_ADMIN]
    });

    this.registerService(MODULES.VAULT, {
      baseUrl: '/api/vault',
      endpoints: {
        store: { method: HTTP_METHODS.POST, path: '/store' },
        retrieve: { method: HTTP_METHODS.GET, path: '/retrieve' },
        search: { method: HTTP_METHODS.POST, path: '/search' },
        delete: { method: HTTP_METHODS.DELETE, path: '/delete' }
      },
      requiredPermissions: [PERMISSIONS.VAULT_READ, PERMISSIONS.VAULT_WRITE]
    });

    this.registerService(MODULES.SYNAPSE, {
      baseUrl: '/api/synapse',
      endpoints: {
        secure: { method: HTTP_METHODS.POST, path: '/secure' },
        audit: { method: HTTP_METHODS.GET, path: '/audit' },
        permissions: { method: HTTP_METHODS.GET, path: '/permissions' }
      },
      requiredPermissions: [PERMISSIONS.SYSTEM_ADMIN]
    });
  }

  setupEventSystem() {
    // Setup internal event bus
    this.eventBus = new EventTarget();
    
    // Setup event type listeners
    Object.values(EVENT_TYPES).forEach(eventType => {
      this.eventListeners.set(eventType, new Set());
    });
    
    // Setup cross-module event routing
    this.setupCrossModuleEvents();
  }

  setupCrossModuleEvents() {
    // Agent communication events
    this.on(EVENT_TYPES.AGENT_EVENT, async (event) => {
      const { fromModule, toModule, action, data } = event.detail;
      
      if (toModule && this.services.has(toModule)) {
        await this.routeModuleEvent(fromModule, toModule, action, data);
      }
    });

    // System events
    this.on(EVENT_TYPES.SYSTEM_EVENT, async (event) => {
      const { type, data } = event.detail;
      await this.handleSystemEvent(type, data);
    });

    // Error events
    this.on(EVENT_TYPES.ERROR_EVENT, async (event) => {
      const { error, context } = event.detail;
      await this.handleErrorEvent(error, context);
    });
  }

  setupExternalAPIs() {
    // Setup external API configurations
    const externalApis = getConfig('external', {});
    
    Object.entries(externalApis).forEach(([name, config]) => {
      if (config.apiKey) {
        this.registerExternalAPI(name, config);
      }
    });
  }

  setupInterceptors() {
    // Request interceptors
    this.addRequestInterceptor(async (config) => {
      // Add authentication headers
      const authHeader = await this.getAuthenticationHeader();
      if (authHeader) {
        config.headers = { ...config.headers, ...authHeader };
      }
      
      // Add request ID for tracing
      config.headers['X-Request-ID'] = this.generateRequestId();
      
      return config;
    });

    this.addRequestInterceptor(async (config) => {
      // Check permissions for external APIs
      if (config.apiType === API_TYPES.EXTERNAL) {
        checkPermission(PERMISSIONS.API_EXTERNAL);
      }
      
      return config;
    });

    // Response interceptors
    this.addResponseInterceptor(async (response, config) => {
      // Log API call
      const duration = Date.now() - config.startTime;
      apiCall(
        config.method,
        config.url,
        duration,
        response.status,
        { requestId: config.headers['X-Request-ID'] },
        this.context
      );
      
      return response;
    });

    this.addResponseInterceptor(async (response, config) => {
      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        if (retryAfter) {
          await this.handleRateLimit(config.url, parseInt(retryAfter) * 1000);
        }
      }
      
      return response;
    });
  }

  setupRateLimiting() {
    // Setup rate limiters for different API types
    this.rateLimiters.set(API_TYPES.EXTERNAL, {
      requests: new Map(),
      limit: getConfig('api.rateLimits.external.requestsPerMinute', 60),
      window: 60000 // 1 minute
    });

    this.rateLimiters.set(API_TYPES.INTERNAL, {
      requests: new Map(),
      limit: getConfig('api.rateLimits.internal.requestsPerMinute', 300),
      window: 60000
    });

    // Setup circuit breakers
    this.setupCircuitBreakers();
  }

  setupCircuitBreakers() {
    const circuitBreakerConfig = getConfig('api.circuitBreaker', {
      failureThreshold: 5,
      timeout: 60000,
      resetTimeout: 300000
    });

    // Create circuit breakers for external services
    const externalApis = getConfig('external', {});
    Object.keys(externalApis).forEach(apiName => {
      this.circuitBreakers.set(apiName, {
        state: 'closed', // closed, open, half-open
        failures: 0,
        lastFailure: null,
        ...circuitBreakerConfig
      });
    });
  }

  // Service registration and management
  registerService(moduleName, config) {
    this.services.set(moduleName, {
      ...config,
      registered: Date.now(),
      health: 'unknown'
    });

    // Register endpoints
    if (config.endpoints) {
      Object.entries(config.endpoints).forEach(([name, endpoint]) => {
        const endpointKey = `${moduleName}.${name}`;
        this.apiEndpoints.set(endpointKey, {
          module: moduleName,
          name,
          ...endpoint,
          fullPath: `${config.baseUrl}${endpoint.path}`
        });
      });
    }

    logInfo(`Service registered: ${moduleName}`, {
      module: moduleName,
      endpointCount: Object.keys(config.endpoints || {}).length
    }, this.context);
  }

  registerExternalAPI(name, config) {
    this.services.set(`external:${name}`, {
      type: API_TYPES.EXTERNAL,
      baseUrl: config.baseUrl || `https://api.${name}.com`,
      apiKey: config.apiKey,
      model: config.model,
      maxTokens: config.maxTokens,
      registered: Date.now(),
      health: 'unknown'
    });

    logInfo(`External API registered: ${name}`, {
      apiName: name,
      baseUrl: config.baseUrl
    }, this.context);
  }

  // API calling methods
  async call(endpoint, data = {}, options = {}) {
    const endpointConfig = this.apiEndpoints.get(endpoint);
    if (!endpointConfig) {
      throw new ValidationError(`API endpoint not found: ${endpoint}`);
    }

    const service = this.services.get(endpointConfig.module);
    if (!service) {
      throw new SystemError(`Service not found: ${endpointConfig.module}`);
    }

    // Check permissions
    if (service.requiredPermissions) {
      service.requiredPermissions.forEach(permission => {
        checkPermission(permission);
      });
    }

    const config = {
      method: endpointConfig.method,
      url: endpointConfig.fullPath,
      apiType: API_TYPES.INTERNAL,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      startTime: Date.now(),
      ...options
    };

    // Add body for non-GET requests
    if (config.method !== HTTP_METHODS.GET && data) {
      config.body = JSON.stringify(data);
    }

    return await this.makeRequest(config);
  }

  async callExternal(apiName, path, data = {}, options = {}) {
    const service = this.services.get(`external:${apiName}`);
    if (!service) {
      throw new ValidationError(`External API not found: ${apiName}`);
    }

    // Check circuit breaker
    const circuitBreaker = this.circuitBreakers.get(apiName);
    if (circuitBreaker && circuitBreaker.state === 'open') {
      if (Date.now() - circuitBreaker.lastFailure < circuitBreaker.resetTimeout) {
        throw new NetworkError(`Circuit breaker open for ${apiName}`);
      } else {
        circuitBreaker.state = 'half-open';
      }
    }

    // Check rate limiting
    await this.checkRateLimit(API_TYPES.EXTERNAL, `external:${apiName}`);

    const config = {
      method: options.method || HTTP_METHODS.POST,
      url: `${service.baseUrl}${path}`,
      apiType: API_TYPES.EXTERNAL,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${service.apiKey}`,
        ...options.headers
      },
      body: JSON.stringify(data),
      startTime: Date.now(),
      ...options
    };

    try {
      const response = await this.makeRequest(config);
      
      // Reset circuit breaker on success
      if (circuitBreaker) {
        circuitBreaker.failures = 0;
        circuitBreaker.state = 'closed';
      }
      
      return response;
    } catch (error) {
      // Handle circuit breaker failure
      if (circuitBreaker) {
        circuitBreaker.failures++;
        circuitBreaker.lastFailure = Date.now();
        
        if (circuitBreaker.failures >= circuitBreaker.failureThreshold) {
          circuitBreaker.state = 'open';
          logWarn(`Circuit breaker opened for ${apiName}`, {
            failures: circuitBreaker.failures
          }, this.context);
        }
      }
      
      throw error;
    }
  }

  async makeRequest(config) {
    try {
      // Apply request interceptors
      for (const interceptor of this.requestInterceptors) {
        config = await interceptor(config);
      }

      // Make the actual request
      const response = await fetch(config.url, {
        method: config.method,
        headers: config.headers,
        body: config.body
      });

      // Apply response interceptors
      for (const interceptor of this.responseInterceptors) {
        await interceptor(response, config);
      }

      if (!response.ok) {
        throw new NetworkError(`HTTP ${response.status}: ${response.statusText}`, {
          status: response.status,
          statusText: response.statusText,
          url: config.url
        });
      }

      return await response.json();
    } catch (error) {
      handleError(error, { component: 'api-manager', url: config.url });
      throw error;
    }
  }

  // Event system methods
  emit(eventType, data) {
    const event = new CustomEvent(eventType, { detail: data });
    this.eventBus.dispatchEvent(event);
    
    // Also emit to window for global listening
    window.dispatchEvent(event);
  }

  on(eventType, callback) {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      listeners.add(callback);
      this.eventBus.addEventListener(eventType, callback);
    }
  }

  off(eventType, callback) {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      listeners.delete(callback);
      this.eventBus.removeEventListener(eventType, callback);
    }
  }

  // Cross-module communication
  async sendToModule(toModule, action, data = {}, fromModule = 'system') {
    const moduleContext = createContext('module-communication', 'api', {
      fromModule,
      toModule,
      action
    });

    try {
      logInfo(`Sending to module: ${toModule}`, {
        fromModule,
        toModule,
        action
      }, moduleContext);

      this.emit(EVENT_TYPES.AGENT_EVENT, {
        fromModule,
        toModule,
        action,
        data,
        timestamp: Date.now()
      });

      return { success: true };
    } catch (error) {
      logError(`Failed to send to module: ${toModule}`, {
        error: error.message
      }, moduleContext);
      throw error;
    }
  }

  async routeModuleEvent(fromModule, toModule, action, data) {
    try {
      const endpoint = `${toModule}.${action}`;
      return await this.call(endpoint, data);
    } catch (error) {
      logError(`Failed to route module event`, {
        fromModule,
        toModule,
        action,
        error: error.message
      }, this.context);
      throw error;
    }
  }

  // System event handlers
  async handleSystemEvent(type, data) {
    logInfo(`System event: ${type}`, { type, data }, this.context);
    
    switch (type) {
      case 'module_health_check':
        await this.performHealthChecks();
        break;
      case 'api_metrics_update':
        await this.updateAPIMetrics();
        break;
      default:
        logInfo(`Unhandled system event: ${type}`, { type }, this.context);
    }
  }

  async handleErrorEvent(error, context) {
    logError(`API error event`, {
      error: error.message,
      context
    }, this.context);
  }

  // Rate limiting
  async checkRateLimit(apiType, identifier) {
    const limiter = this.rateLimiters.get(apiType);
    if (!limiter) return;

    const now = Date.now();
    const requests = limiter.requests.get(identifier) || [];
    
    // Remove old requests outside the window
    const validRequests = requests.filter(time => now - time < limiter.window);
    
    if (validRequests.length >= limiter.limit) {
      throw new NetworkError(`Rate limit exceeded for ${identifier}`, {
        limit: limiter.limit,
        window: limiter.window
      });
    }
    
    validRequests.push(now);
    limiter.requests.set(identifier, validRequests);
  }

  async handleRateLimit(url, retryAfter) {
    logWarn(`Rate limit hit for ${url}`, {
      retryAfter,
      url
    }, this.context);
    
    // Implement exponential backoff or queue
    return new Promise(resolve => {
      setTimeout(resolve, retryAfter);
    });
  }

  // Interceptor management
  addRequestInterceptor(interceptor) {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor) {
    this.responseInterceptors.push(interceptor);
  }

  // Health checking
  async performHealthChecks() {
    const healthResults = new Map();
    
    for (const [moduleName, service] of this.services.entries()) {
      try {
        const statusEndpoint = `${moduleName}.status`;
        const response = await this.call(statusEndpoint);
        
        service.health = response.status === 'healthy' ? 'healthy' : 'unhealthy';
        healthResults.set(moduleName, service.health);
      } catch (error) {
        service.health = 'unhealthy';
        healthResults.set(moduleName, 'unhealthy');
      }
    }
    
    logInfo('Health check completed', {
      results: Object.fromEntries(healthResults)
    }, this.context);
    
    return healthResults;
  }

  // Metrics and monitoring
  async updateAPIMetrics() {
    const metrics = {
      totalServices: this.services.size,
      healthyServices: Array.from(this.services.values()).filter(s => s.health === 'healthy').length,
      activeRateLimiters: this.rateLimiters.size,
      circuitBreakers: Array.from(this.circuitBreakers.entries()).map(([name, cb]) => ({
        name,
        state: cb.state,
        failures: cb.failures
      }))
    };
    
    this.emit(EVENT_TYPES.SYSTEM_EVENT, {
      type: 'api_metrics',
      metrics,
      timestamp: Date.now()
    });
    
    return metrics;
  }

  // Utility methods
  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async getAuthenticationHeader() {
    // In a real implementation, this would get the current authentication token
    return {
      'X-Session-ID': 'current-session-id'
    };
  }

  // Public API methods
  getServices() {
    return Array.from(this.services.entries()).map(([name, service]) => ({
      name,
      type: service.type || API_TYPES.INTERNAL,
      health: service.health,
      registered: service.registered
    }));
  }

  getEndpoints() {
    return Array.from(this.apiEndpoints.entries()).map(([key, endpoint]) => ({
      key,
      module: endpoint.module,
      method: endpoint.method,
      path: endpoint.fullPath
    }));
  }

  getAPIStats() {
    return {
      services: this.services.size,
      endpoints: this.apiEndpoints.size,
      eventListeners: Array.from(this.eventListeners.entries()).reduce((sum, [, listeners]) => sum + listeners.size, 0),
      rateLimiters: this.rateLimiters.size,
      circuitBreakers: this.circuitBreakers.size
    };
  }
}

// Create singleton instance
const apiManager = new APIManager();

// Export convenience functions
export const call = (endpoint, data, options) => apiManager.call(endpoint, data, options);
export const callExternal = (apiName, path, data, options) => apiManager.callExternal(apiName, path, data, options);
export const sendToModule = (toModule, action, data, fromModule) => apiManager.sendToModule(toModule, action, data, fromModule);
export const emit = (eventType, data) => apiManager.emit(eventType, data);
export const on = (eventType, callback) => apiManager.on(eventType, callback);
export const off = (eventType, callback) => apiManager.off(eventType, callback);
export const getServices = () => apiManager.getServices();
export const getEndpoints = () => apiManager.getEndpoints();
export const getAPIStats = () => apiManager.getAPIStats();

export default apiManager;