/**
 * Comprehensive System-Wide Error Handling Framework
 * 
 * Provides centralized error handling, recovery strategies, and user feedback
 * for all system components and modules.
 */

import systemLogger, { error as logError, warn as logWarn, createContext } from './SystemLogger';

// Error categories for classification and handling
export const ERROR_CATEGORIES = {
  NETWORK: 'network',
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  VALIDATION: 'validation',
  SYSTEM: 'system',
  USER_INPUT: 'user_input',
  AGENT: 'agent',
  STORAGE: 'storage',
  CONFIGURATION: 'configuration',
  EXTERNAL_API: 'external_api'
};

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

// Recovery strategies
export const RECOVERY_STRATEGIES = {
  RETRY: 'retry',
  FALLBACK: 'fallback',
  USER_ACTION: 'user_action',
  SYSTEM_RESTART: 'system_restart',
  NONE: 'none'
};

/**
 * Custom Error Classes for different error types
 */
export class HearthlinkError extends Error {
  constructor(message, category = ERROR_CATEGORIES.SYSTEM, severity = ERROR_SEVERITY.MEDIUM, details = {}) {
    super(message);
    this.name = 'HearthlinkError';
    this.category = category;
    this.severity = severity;
    this.details = details;
    this.timestamp = new Date().toISOString();
    this.correlationId = details.correlationId || null;
  }
}

export class NetworkError extends HearthlinkError {
  constructor(message, details = {}) {
    super(message, ERROR_CATEGORIES.NETWORK, ERROR_SEVERITY.MEDIUM, details);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends HearthlinkError {
  constructor(message, details = {}) {
    super(message, ERROR_CATEGORIES.AUTHENTICATION, ERROR_SEVERITY.HIGH, details);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends HearthlinkError {
  constructor(message, details = {}) {
    super(message, ERROR_CATEGORIES.VALIDATION, ERROR_SEVERITY.LOW, details);
    this.name = 'ValidationError';
  }
}

export class AgentError extends HearthlinkError {
  constructor(message, agentId, details = {}) {
    super(message, ERROR_CATEGORIES.AGENT, ERROR_SEVERITY.MEDIUM, { ...details, agentId });
    this.name = 'AgentError';
    this.agentId = agentId;
  }
}

export class SystemError extends HearthlinkError {
  constructor(message, details = {}) {
    super(message, ERROR_CATEGORIES.SYSTEM, ERROR_SEVERITY.CRITICAL, details);
    this.name = 'SystemError';
  }
}

/**
 * Main Error Handler Class
 */
class ErrorHandler {
  constructor() {
    this.errorHistory = [];
    this.maxHistorySize = 500;
    this.retryAttempts = new Map();
    this.maxRetries = 3;
    this.recoveryStrategies = new Map();
    this.userNotificationQueue = [];
    
    this.initializeErrorHandling();
    this.setupRecoveryStrategies();
  }

  initializeErrorHandling() {
    // Global error boundary for React components
    this.setupGlobalErrorBoundary();
    
    // Network error handling
    this.setupNetworkErrorHandling();
    
    // API error interceptors
    this.setupAPIErrorHandling();
    
    systemLogger.info('ErrorHandler initialized', {}, createContext('error-handler', 'system'));
  }

  setupGlobalErrorBoundary() {
    window.addEventListener('error', (event) => {
      const error = new SystemError('Uncaught JavaScript Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
      
      this.handleError(error, { component: 'global-error-boundary' });
    });

    window.addEventListener('unhandledrejection', (event) => {
      const error = new SystemError('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise
      });
      
      this.handleError(error, { component: 'promise-rejection-handler' });
    });
  }

  setupNetworkErrorHandling() {
    // Monitor network status
    window.addEventListener('online', () => {
      systemLogger.info('Network connection restored');
      this.handleNetworkRecovery();
    });

    window.addEventListener('offline', () => {
      const error = new NetworkError('Network connection lost');
      this.handleError(error, { component: 'network-monitor' });
    });
  }

  setupAPIErrorHandling() {
    // Intercept fetch requests for automatic error handling
    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      const startTime = Date.now();
      const [url, options = {}] = args;
      const context = createContext('api-client', 'network');
      
      try {
        const response = await originalFetch(...args);
        const duration = Date.now() - startTime;
        
        if (!response.ok) {
          const error = new NetworkError(`HTTP ${response.status}: ${response.statusText}`, {
            url,
            method: options.method || 'GET',
            status: response.status,
            statusText: response.statusText,
            duration
          });
          
          return this.handleAPIError(error, response, context);
        }
        
        // Log successful API call
        systemLogger.apiCall(
          options.method || 'GET',
          url,
          duration,
          response.status,
          {},
          context
        );
        
        return response;
        
      } catch (error) {
        const duration = Date.now() - startTime;
        
        const networkError = new NetworkError(`Network request failed: ${error.message}`, {
          url,
          method: options.method || 'GET',
          duration,
          originalError: error.message
        });
        
        throw this.handleError(networkError, context);
      }
    };
  }

  setupRecoveryStrategies() {
    // Network errors - retry with exponential backoff
    this.recoveryStrategies.set(ERROR_CATEGORIES.NETWORK, {
      strategy: RECOVERY_STRATEGIES.RETRY,
      maxRetries: 3,
      backoffMultiplier: 2,
      baseDelay: 1000
    });

    // Authentication errors - redirect to login
    this.recoveryStrategies.set(ERROR_CATEGORIES.AUTHENTICATION, {
      strategy: RECOVERY_STRATEGIES.USER_ACTION,
      action: 'redirect_to_login'
    });

    // System errors - attempt restart
    this.recoveryStrategies.set(ERROR_CATEGORIES.SYSTEM, {
      strategy: RECOVERY_STRATEGIES.SYSTEM_RESTART,
      criticalThreshold: 3
    });

    // Agent errors - fallback to different agent
    this.recoveryStrategies.set(ERROR_CATEGORIES.AGENT, {
      strategy: RECOVERY_STRATEGIES.FALLBACK,
      fallbackAgents: ['alden', 'alice', 'core']
    });

    // Validation errors - user correction
    this.recoveryStrategies.set(ERROR_CATEGORIES.VALIDATION, {
      strategy: RECOVERY_STRATEGIES.USER_ACTION,
      action: 'show_validation_message'
    });
  }

  handleError(error, context = {}) {
    const errorId = this.generateErrorId();
    const enhancedError = this.enhanceError(error, errorId, context);
    
    // Add to error history
    this.addToHistory(enhancedError);
    
    // Log the error
    this.logError(enhancedError, context);
    
    // Attempt recovery
    const recoveryResult = this.attemptRecovery(enhancedError, context);
    
    // Notify user if necessary
    this.notifyUser(enhancedError, recoveryResult);
    
    // Emit error event for system monitoring
    this.emitErrorEvent(enhancedError, recoveryResult);
    
    return enhancedError;
  }

  generateErrorId() {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  enhanceError(error, errorId, context) {
    const enhanced = error instanceof HearthlinkError ? error : new SystemError(error.message, {
      originalError: error.name,
      stack: error.stack
    });
    
    enhanced.errorId = errorId;
    enhanced.context = context;
    enhanced.userAgent = navigator.userAgent;
    enhanced.url = window.location.href;
    enhanced.timestamp = new Date().toISOString();
    enhanced.systemState = this.captureSystemState();
    
    return enhanced;
  }

  captureSystemState() {
    return {
      online: navigator.onLine,
      memory: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
        limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
      } : null,
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : null,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };
  }

  addToHistory(error) {
    this.errorHistory.unshift(error);
    
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(0, this.maxHistorySize);
    }
  }

  logError(error, context) {
    const logContext = {
      ...context,
      errorId: error.errorId,
      category: error.category,
      severity: error.severity
    };

    if (error.severity === ERROR_SEVERITY.CRITICAL) {
      logError(`CRITICAL ERROR: ${error.message}`, {
        error: this.serializeError(error)
      }, logContext);
    } else {
      logWarn(`Error occurred: ${error.message}`, {
        error: this.serializeError(error)
      }, logContext);
    }
  }

  serializeError(error) {
    return {
      name: error.name,
      message: error.message,
      category: error.category,
      severity: error.severity,
      details: error.details,
      stack: error.stack,
      errorId: error.errorId,
      timestamp: error.timestamp,
      systemState: error.systemState
    };
  }

  attemptRecovery(error, context) {
    const recoveryConfig = this.recoveryStrategies.get(error.category);
    
    if (!recoveryConfig) {
      return { attempted: false, strategy: RECOVERY_STRATEGIES.NONE };
    }

    switch (recoveryConfig.strategy) {
      case RECOVERY_STRATEGIES.RETRY:
        return this.attemptRetry(error, recoveryConfig, context);
        
      case RECOVERY_STRATEGIES.FALLBACK:
        return this.attemptFallback(error, recoveryConfig, context);
        
      case RECOVERY_STRATEGIES.USER_ACTION:
        return this.requestUserAction(error, recoveryConfig, context);
        
      case RECOVERY_STRATEGIES.SYSTEM_RESTART:
        return this.attemptSystemRestart(error, recoveryConfig, context);
        
      default:
        return { attempted: false, strategy: RECOVERY_STRATEGIES.NONE };
    }
  }

  attemptRetry(error, config, context) {
    const retryKey = `${error.category}_${context.component || 'unknown'}`;
    const currentAttempts = this.retryAttempts.get(retryKey) || 0;
    
    if (currentAttempts >= config.maxRetries) {
      this.retryAttempts.delete(retryKey);
      return { attempted: false, strategy: RECOVERY_STRATEGIES.RETRY, reason: 'max_retries_exceeded' };
    }
    
    this.retryAttempts.set(retryKey, currentAttempts + 1);
    
    const delay = config.baseDelay * Math.pow(config.backoffMultiplier, currentAttempts);
    
    setTimeout(() => {
      systemLogger.info(`Retry attempt ${currentAttempts + 1} for ${error.category}`, {
        errorId: error.errorId,
        delay
      }, context);
    }, delay);
    
    return {
      attempted: true,
      strategy: RECOVERY_STRATEGIES.RETRY,
      attempt: currentAttempts + 1,
      delay
    };
  }

  attemptFallback(error, config, context) {
    if (error instanceof AgentError && config.fallbackAgents) {
      const currentAgent = error.agentId;
      const availableAgents = config.fallbackAgents.filter(agent => agent !== currentAgent);
      
      if (availableAgents.length > 0) {
        const fallbackAgent = availableAgents[0];
        
        systemLogger.info(`Falling back from ${currentAgent} to ${fallbackAgent}`, {
          errorId: error.errorId,
          originalAgent: currentAgent,
          fallbackAgent
        }, context);
        
        // Emit fallback event
        window.dispatchEvent(new CustomEvent('agentFallback', {
          detail: { originalAgent: currentAgent, fallbackAgent, errorId: error.errorId }
        }));
        
        return {
          attempted: true,
          strategy: RECOVERY_STRATEGIES.FALLBACK,
          fallbackAgent
        };
      }
    }
    
    return { attempted: false, strategy: RECOVERY_STRATEGIES.FALLBACK, reason: 'no_fallback_available' };
  }

  requestUserAction(error, config, context) {
    const userAction = {
      errorId: error.errorId,
      action: config.action,
      message: this.getUserFriendlyMessage(error),
      severity: error.severity,
      category: error.category
    };
    
    // Add to notification queue
    this.userNotificationQueue.push(userAction);
    
    // Emit user action event
    window.dispatchEvent(new CustomEvent('userActionRequired', { detail: userAction }));
    
    return {
      attempted: true,
      strategy: RECOVERY_STRATEGIES.USER_ACTION,
      action: config.action
    };
  }

  attemptSystemRestart(error, config, context) {
    const criticalErrors = this.errorHistory.filter(e => 
      e.severity === ERROR_SEVERITY.CRITICAL && 
      Date.now() - new Date(e.timestamp).getTime() < 300000 // 5 minutes
    );
    
    if (criticalErrors.length >= config.criticalThreshold) {
      systemLogger.error('Critical error threshold exceeded, requesting system restart', {
        criticalErrorCount: criticalErrors.length,
        threshold: config.criticalThreshold
      }, context);
      
      // Emit system restart event
      window.dispatchEvent(new CustomEvent('systemRestartRequired', {
        detail: { errorId: error.errorId, criticalErrorCount: criticalErrors.length }
      }));
      
      return {
        attempted: true,
        strategy: RECOVERY_STRATEGIES.SYSTEM_RESTART,
        criticalErrorCount: criticalErrors.length
      };
    }
    
    return { attempted: false, strategy: RECOVERY_STRATEGIES.SYSTEM_RESTART, reason: 'threshold_not_met' };
  }

  getUserFriendlyMessage(error) {
    const messageMap = {
      [ERROR_CATEGORIES.NETWORK]: 'Connection issue detected. Please check your internet connection.',
      [ERROR_CATEGORIES.AUTHENTICATION]: 'Authentication required. Please sign in to continue.',
      [ERROR_CATEGORIES.AUTHORIZATION]: 'You don\'t have permission to perform this action.',
      [ERROR_CATEGORIES.VALIDATION]: 'Please check your input and try again.',
      [ERROR_CATEGORIES.AGENT]: 'AI agent encountered an issue. Trying alternative approach.',
      [ERROR_CATEGORIES.STORAGE]: 'Data storage issue. Your work may not be saved.',
      [ERROR_CATEGORIES.SYSTEM]: 'System error occurred. Our team has been notified.',
      [ERROR_CATEGORIES.EXTERNAL_API]: 'External service is temporarily unavailable.'
    };
    
    return messageMap[error.category] || 'An unexpected error occurred. Please try again.';
  }

  notifyUser(error, recoveryResult) {
    const shouldNotify = error.severity === ERROR_SEVERITY.HIGH || 
                        error.severity === ERROR_SEVERITY.CRITICAL ||
                        !recoveryResult.attempted;
    
    if (shouldNotify) {
      const notification = {
        id: error.errorId,
        message: this.getUserFriendlyMessage(error),
        type: error.severity,
        category: error.category,
        recovery: recoveryResult,
        timestamp: error.timestamp
      };
      
      // Emit notification event
      window.dispatchEvent(new CustomEvent('errorNotification', { detail: notification }));
    }
  }

  emitErrorEvent(error, recoveryResult) {
    const errorEvent = {
      error: this.serializeError(error),
      recovery: recoveryResult,
      timestamp: new Date().toISOString()
    };
    
    window.dispatchEvent(new CustomEvent('systemError', { detail: errorEvent }));
  }

  handleNetworkRecovery() {
    // Clear network-related retry attempts
    for (const [key, value] of this.retryAttempts.entries()) {
      if (key.startsWith(ERROR_CATEGORIES.NETWORK)) {
        this.retryAttempts.delete(key);
      }
    }
    
    // Emit network recovery event
    window.dispatchEvent(new CustomEvent('networkRecovery'));
  }

  handleAPIError(error, response, context) {
    // Handle specific HTTP status codes
    switch (response.status) {
      case 401:
        throw new AuthenticationError('Authentication required', {
          url: error.details.url,
          status: response.status
        });
        
      case 403:
        throw new HearthlinkError('Access forbidden', ERROR_CATEGORIES.AUTHORIZATION, ERROR_SEVERITY.HIGH, {
          url: error.details.url,
          status: response.status
        });
        
      case 429:
        throw new NetworkError('Rate limit exceeded', {
          url: error.details.url,
          status: response.status,
          retryAfter: response.headers.get('Retry-After')
        });
        
      case 500:
      case 502:
      case 503:
      case 504:
        throw new NetworkError('Server error', {
          url: error.details.url,
          status: response.status
        });
        
      default:
        throw error;
    }
  }

  // Public API methods
  getErrorHistory(filters = {}) {
    let filtered = [...this.errorHistory];
    
    if (filters.category) {
      filtered = filtered.filter(error => error.category === filters.category);
    }
    
    if (filters.severity) {
      filtered = filtered.filter(error => error.severity === filters.severity);
    }
    
    if (filters.since) {
      const since = new Date(filters.since);
      filtered = filtered.filter(error => new Date(error.timestamp) >= since);
    }
    
    return filtered;
  }

  getErrorStats() {
    const stats = {
      total: this.errorHistory.length,
      categories: {},
      severities: {},
      recent: this.errorHistory.filter(error => 
        Date.now() - new Date(error.timestamp).getTime() < 3600000 // 1 hour
      ).length
    };
    
    this.errorHistory.forEach(error => {
      stats.categories[error.category] = (stats.categories[error.category] || 0) + 1;
      stats.severities[error.severity] = (stats.severities[error.severity] || 0) + 1;
    });
    
    return stats;
  }

  clearErrorHistory() {
    this.errorHistory = [];
    systemLogger.info('Error history cleared');
  }

  exportErrorHistory(format = 'json') {
    if (format === 'json') {
      return JSON.stringify(this.errorHistory.map(error => this.serializeError(error)), null, 2);
    } else if (format === 'csv') {
      // Implement CSV export if needed
      return this.errorHistory.map(error => 
        `${error.timestamp},${error.category},${error.severity},${error.message}`
      ).join('\n');
    }
    
    return this.errorHistory;
  }
}

// Create singleton instance
const errorHandler = new ErrorHandler();

// Export convenience functions
export const handleError = (error, context) => errorHandler.handleError(error, context);
export const getErrorHistory = (filters) => errorHandler.getErrorHistory(filters);
export const getErrorStats = () => errorHandler.getErrorStats();
export const exportErrorHistory = (format) => errorHandler.exportErrorHistory(format);

export default errorHandler;