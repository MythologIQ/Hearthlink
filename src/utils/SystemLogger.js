/**
 * Comprehensive System-Wide Logging Framework
 * 
 * Provides centralized logging with structured data, correlation IDs,
 * and integration with system monitoring and audit trails.
 */

class SystemLogger {
  constructor() {
    this.logLevel = process.env.NODE_ENV === 'production' ? 'info' : 'debug';
    this.sessionId = this.generateSessionId();
    this.logBuffer = [];
    this.maxBufferSize = 1000;
    this.enableConsole = process.env.NODE_ENV !== 'production';
    
    // Initialize remote logging if configured
    this.remoteLoggingUrl = process.env.REACT_APP_LOGGING_ENDPOINT;
    this.flushInterval = 5000; // 5 seconds
    
    this.initializeLogging();
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  generateCorrelationId() {
    return `corr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  initializeLogging() {
    // Start periodic log flushing
    if (this.remoteLoggingUrl) {
      setInterval(() => {
        this.flushLogs();
      }, this.flushInterval);
    }

    // Handle application lifecycle events
    window.addEventListener('beforeunload', () => {
      this.flushLogs();
    });

    // Handle uncaught errors
    window.addEventListener('error', (event) => {
      this.error('Uncaught Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });

    this.info('SystemLogger initialized', {
      sessionId: this.sessionId,
      logLevel: this.logLevel,
      remoteLogging: !!this.remoteLoggingUrl
    });
  }

  createLogEntry(level, message, data = {}, context = {}) {
    const timestamp = new Date().toISOString();
    const correlationId = context.correlationId || this.generateCorrelationId();
    
    const logEntry = {
      timestamp,
      level,
      message,
      sessionId: this.sessionId,
      correlationId,
      component: context.component || 'unknown',
      module: context.module || 'system',
      userId: context.userId || 'anonymous',
      agentId: context.agentId || null,
      data: this.sanitizeData(data),
      environment: process.env.NODE_ENV || 'development',
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    return logEntry;
  }

  sanitizeData(data) {
    // Remove sensitive information from log data
    const sensitiveKeys = ['password', 'token', 'secret', 'key', 'credential'];
    const sanitized = { ...data };

    const sanitizeObject = (obj) => {
      if (typeof obj !== 'object' || obj === null) return obj;
      
      const result = Array.isArray(obj) ? [] : {};
      
      for (const [key, value] of Object.entries(obj)) {
        const lowerKey = key.toLowerCase();
        if (sensitiveKeys.some(sensitive => lowerKey.includes(sensitive))) {
          result[key] = '[REDACTED]';
        } else if (typeof value === 'object' && value !== null) {
          result[key] = sanitizeObject(value);
        } else {
          result[key] = value;
        }
      }
      
      return result;
    };

    return sanitizeObject(sanitized);
  }

  shouldLog(level) {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    return levels[level] >= levels[this.logLevel];
  }

  log(level, message, data = {}, context = {}) {
    if (!this.shouldLog(level)) return;

    const logEntry = this.createLogEntry(level, message, data, context);
    
    // Add to buffer
    this.logBuffer.push(logEntry);
    
    // Maintain buffer size
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize);
    }

    // Console logging for development
    if (this.enableConsole) {
      const consoleMethod = console[level] || console.log;
      consoleMethod(`[${level.toUpperCase()}] ${message}`, logEntry);
    }

    // Emit event for real-time monitoring
    window.dispatchEvent(new CustomEvent('systemLog', { detail: logEntry }));

    return logEntry.correlationId;
  }

  debug(message, data = {}, context = {}) {
    return this.log('debug', message, data, context);
  }

  info(message, data = {}, context = {}) {
    return this.log('info', message, data, context);
  }

  warn(message, data = {}, context = {}) {
    return this.log('warn', message, data, context);
  }

  error(message, data = {}, context = {}) {
    return this.log('error', message, data, context);
  }

  // Specialized logging methods
  userAction(action, data = {}, context = {}) {
    return this.info(`User Action: ${action}`, data, {
      ...context,
      component: 'user-interaction'
    });
  }

  apiCall(method, url, duration, status, data = {}, context = {}) {
    const level = status >= 400 ? 'error' : 'info';
    return this.log(level, `API Call: ${method} ${url}`, {
      method,
      url,
      duration,
      status,
      ...data
    }, {
      ...context,
      component: 'api-client'
    });
  }

  agentAction(agentId, action, data = {}, context = {}) {
    return this.info(`Agent Action: ${agentId} - ${action}`, data, {
      ...context,
      agentId,
      component: 'agent-system'
    });
  }

  securityEvent(event, data = {}, context = {}) {
    return this.warn(`Security Event: ${event}`, data, {
      ...context,
      component: 'security',
      module: 'synapse'
    });
  }

  performance(metric, value, data = {}, context = {}) {
    return this.info(`Performance Metric: ${metric}`, {
      metric,
      value,
      ...data
    }, {
      ...context,
      component: 'performance'
    });
  }

  // Context management for correlated logging
  createContext(component, module = 'system', additionalData = {}) {
    return {
      correlationId: this.generateCorrelationId(),
      component,
      module,
      ...additionalData
    };
  }

  withContext(context, callback) {
    try {
      return callback(context);
    } catch (error) {
      this.error('Error in context execution', {
        error: error.message,
        stack: error.stack
      }, context);
      throw error;
    }
  }

  // Log retrieval and export
  getLogs(filters = {}) {
    let filteredLogs = [...this.logBuffer];

    if (filters.level) {
      filteredLogs = filteredLogs.filter(log => log.level === filters.level);
    }

    if (filters.component) {
      filteredLogs = filteredLogs.filter(log => log.component === filters.component);
    }

    if (filters.module) {
      filteredLogs = filteredLogs.filter(log => log.module === filters.module);
    }

    if (filters.since) {
      const sinceDate = new Date(filters.since);
      filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= sinceDate);
    }

    if (filters.correlationId) {
      filteredLogs = filteredLogs.filter(log => log.correlationId === filters.correlationId);
    }

    return filteredLogs;
  }

  exportLogs(format = 'json') {
    const logs = this.getLogs();
    
    if (format === 'json') {
      return JSON.stringify(logs, null, 2);
    } else if (format === 'csv') {
      if (logs.length === 0) return '';
      
      const headers = Object.keys(logs[0]);
      const csvRows = [
        headers.join(','),
        ...logs.map(log => 
          headers.map(header => {
            const value = log[header];
            if (typeof value === 'object') {
              return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
            }
            return `"${String(value).replace(/"/g, '""')}"`;
          }).join(',')
        )
      ];
      
      return csvRows.join('\n');
    }
    
    return logs;
  }

  // Remote logging
  async flushLogs() {
    if (!this.remoteLoggingUrl || this.logBuffer.length === 0) return;

    try {
      const logsToSend = [...this.logBuffer];
      this.logBuffer = [];

      const response = await fetch(this.remoteLoggingUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.REACT_APP_LOGGING_TOKEN || ''}`
        },
        body: JSON.stringify({
          sessionId: this.sessionId,
          logs: logsToSend
        })
      });

      if (!response.ok) {
        // Put logs back in buffer if sending failed
        this.logBuffer = [...logsToSend, ...this.logBuffer];
        this.warn('Failed to send logs to remote endpoint', {
          status: response.status,
          statusText: response.statusText
        });
      }
    } catch (error) {
      this.warn('Error sending logs to remote endpoint', {
        error: error.message
      });
    }
  }

  // Utility methods
  clearLogs() {
    this.logBuffer = [];
    this.info('Log buffer cleared');
  }

  setLogLevel(level) {
    const validLevels = ['debug', 'info', 'warn', 'error'];
    if (validLevels.includes(level)) {
      this.logLevel = level;
      this.info('Log level changed', { newLevel: level });
    } else {
      this.warn('Invalid log level', { attempted: level, valid: validLevels });
    }
  }

  getStats() {
    const levels = {};
    const components = {};
    const modules = {};

    this.logBuffer.forEach(log => {
      levels[log.level] = (levels[log.level] || 0) + 1;
      components[log.component] = (components[log.component] || 0) + 1;
      modules[log.module] = (modules[log.module] || 0) + 1;
    });

    return {
      totalLogs: this.logBuffer.length,
      sessionId: this.sessionId,
      levels,
      components,
      modules,
      bufferSize: this.maxBufferSize,
      remoteLogging: !!this.remoteLoggingUrl
    };
  }
}

// Create singleton instance
const systemLogger = new SystemLogger();

// Export convenience functions
export const debug = (message, data, context) => systemLogger.debug(message, data, context);
export const info = (message, data, context) => systemLogger.info(message, data, context);
export const warn = (message, data, context) => systemLogger.warn(message, data, context);
export const error = (message, data, context) => systemLogger.error(message, data, context);

export const userAction = (action, data, context) => systemLogger.userAction(action, data, context);
export const apiCall = (method, url, duration, status, data, context) => 
  systemLogger.apiCall(method, url, duration, status, data, context);
export const agentAction = (agentId, action, data, context) => 
  systemLogger.agentAction(agentId, action, data, context);
export const securityEvent = (event, data, context) => systemLogger.securityEvent(event, data, context);
export const performance = (metric, value, data, context) => 
  systemLogger.performance(metric, value, data, context);

export const createContext = (component, module, additionalData) => 
  systemLogger.createContext(component, module, additionalData);
export const withContext = (context, callback) => systemLogger.withContext(context, callback);

export const getLogs = (filters) => systemLogger.getLogs(filters);
export const exportLogs = (format) => systemLogger.exportLogs(format);
export const getLogStats = () => systemLogger.getStats();

export default systemLogger;