/**
 * Comprehensive System Health Monitoring and Diagnostics
 * 
 * Provides real-time system health monitoring, performance metrics,
 * diagnostic capabilities, and automated health checks for all components.
 */

import systemLogger, { info as logInfo, warn as logWarn, error as logError, performance, createContext } from './SystemLogger';
import { SystemError, handleError } from './ErrorHandler';
import { get as getConfig, watch as watchConfig } from './ConfigManager';
import { emit, on, MODULES, EVENT_TYPES } from './APIManager';

// Health states
export const HEALTH_STATES = {
  HEALTHY: 'healthy',
  WARNING: 'warning',
  CRITICAL: 'critical',
  UNKNOWN: 'unknown',
  OFFLINE: 'offline'
};

// Health check types
export const HEALTH_CHECK_TYPES = {
  SYSTEM: 'system',
  MODULE: 'module',
  NETWORK: 'network',
  STORAGE: 'storage',
  MEMORY: 'memory',
  CPU: 'cpu',
  API: 'api'
};

// Metric types
export const METRIC_TYPES = {
  COUNTER: 'counter',
  GAUGE: 'gauge',
  HISTOGRAM: 'histogram',
  TIMER: 'timer'
};

// Alert levels
export const ALERT_LEVELS = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical'
};

class HealthMonitor {
  constructor() {
    this.healthChecks = new Map();
    this.metrics = new Map();
    this.alerts = [];
    this.systemHealth = HEALTH_STATES.UNKNOWN;
    this.moduleHealth = new Map();
    this.performanceData = new Map();
    this.diagnostics = new Map();
    this.alertThresholds = new Map();
    this.context = createContext('health-monitor', 'system');
    
    this.monitoringInterval = null;
    this.alertingEnabled = true;
    this.maxAlerts = 1000;
    
    this.initialize();
  }

  async initialize() {
    try {
      // Setup default health checks
      this.setupDefaultHealthChecks();
      
      // Setup metrics collection
      this.setupMetrics();
      
      // Setup alert thresholds
      this.setupAlertThresholds();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Start monitoring
      this.startMonitoring();
      
      logInfo('HealthMonitor initialized successfully', {
        healthChecks: this.healthChecks.size,
        metrics: this.metrics.size
      }, this.context);
      
    } catch (error) {
      logError('Failed to initialize HealthMonitor', {
        error: error.message,
        stack: error.stack
      }, this.context);
      throw new SystemError('Health Monitor initialization failed', { originalError: error });
    }
  }

  setupDefaultHealthChecks() {
    // System health checks
    this.registerHealthCheck('system.memory', {
      type: HEALTH_CHECK_TYPES.MEMORY,
      interval: 30000, // 30 seconds
      timeout: 5000,
      check: this.checkMemoryHealth.bind(this),
      thresholds: { warning: 0.8, critical: 0.95 }
    });

    this.registerHealthCheck('system.cpu', {
      type: HEALTH_CHECK_TYPES.CPU,
      interval: 30000,
      timeout: 5000,
      check: this.checkCPUHealth.bind(this),
      thresholds: { warning: 0.8, critical: 0.95 }
    });

    this.registerHealthCheck('system.storage', {
      type: HEALTH_CHECK_TYPES.STORAGE,
      interval: 60000, // 1 minute
      timeout: 10000,
      check: this.checkStorageHealth.bind(this),
      thresholds: { warning: 0.8, critical: 0.95 }
    });

    this.registerHealthCheck('system.network', {
      type: HEALTH_CHECK_TYPES.NETWORK,
      interval: 30000,
      timeout: 10000,
      check: this.checkNetworkHealth.bind(this),
      thresholds: { warning: 1000, critical: 5000 } // Response time in ms
    });

    // Module health checks
    Object.values(MODULES).forEach(module => {
      this.registerHealthCheck(`module.${module}`, {
        type: HEALTH_CHECK_TYPES.MODULE,
        interval: 45000,
        timeout: 10000,
        check: () => this.checkModuleHealth(module),
        thresholds: { warning: 1000, critical: 5000 }
      });
    });
  }

  setupMetrics() {
    // System metrics
    this.registerMetric('system.uptime', METRIC_TYPES.GAUGE);
    this.registerMetric('system.memory.used', METRIC_TYPES.GAUGE);
    this.registerMetric('system.memory.total', METRIC_TYPES.GAUGE);
    this.registerMetric('system.cpu.usage', METRIC_TYPES.GAUGE);
    this.registerMetric('system.storage.used', METRIC_TYPES.GAUGE);
    this.registerMetric('system.network.latency', METRIC_TYPES.HISTOGRAM);
    
    // Application metrics
    this.registerMetric('app.requests.total', METRIC_TYPES.COUNTER);
    this.registerMetric('app.requests.errors', METRIC_TYPES.COUNTER);
    this.registerMetric('app.response.time', METRIC_TYPES.HISTOGRAM);
    this.registerMetric('app.sessions.active', METRIC_TYPES.GAUGE);
    
    // Agent metrics
    Object.values(MODULES).forEach(module => {
      this.registerMetric(`agent.${module}.requests`, METRIC_TYPES.COUNTER);
      this.registerMetric(`agent.${module}.errors`, METRIC_TYPES.COUNTER);
      this.registerMetric(`agent.${module}.response_time`, METRIC_TYPES.HISTOGRAM);
    });
  }

  setupAlertThresholds() {
    // Memory thresholds
    this.alertThresholds.set('memory.usage', {
      warning: 0.8,
      critical: 0.95
    });

    // CPU thresholds
    this.alertThresholds.set('cpu.usage', {
      warning: 0.8,
      critical: 0.95
    });

    // Response time thresholds
    this.alertThresholds.set('response.time', {
      warning: 1000, // 1 second
      critical: 5000  // 5 seconds
    });

    // Error rate thresholds
    this.alertThresholds.set('error.rate', {
      warning: 0.05, // 5%
      critical: 0.15  // 15%
    });
  }

  setupEventListeners() {
    // Listen for system events
    on(EVENT_TYPES.SYSTEM_EVENT, (event) => {
      this.handleSystemEvent(event.detail);
    });

    // Listen for error events
    on(EVENT_TYPES.ERROR_EVENT, (event) => {
      this.handleErrorEvent(event.detail);
    });

    // Listen for agent events
    on(EVENT_TYPES.AGENT_EVENT, (event) => {
      this.handleAgentEvent(event.detail);
    });
  }

  startMonitoring() {
    const monitoringInterval = getConfig('monitoring.metricsInterval', 30000); // Increased to 30 seconds
    
    // Add startup grace period - wait 10 seconds before starting health checks
    setTimeout(() => {
      this.monitoringInterval = setInterval(() => {
        this.performHealthChecks();
        this.collectMetrics();
        this.evaluateAlerts();
      }, monitoringInterval);
    }, 10000);

    // Watch for configuration changes
    watchConfig('monitoring.enabled', (enabled) => {
      if (enabled) {
        this.startMonitoring();
      } else {
        this.stopMonitoring();
      }
    });
  }

  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  // Health check registration and management
  registerHealthCheck(name, config) {
    this.healthChecks.set(name, {
      ...config,
      lastRun: null,
      lastResult: null,
      failures: 0,
      consecutiveFailures: 0,
      totalRuns: 0,
      avgDuration: 0
    });

    logInfo(`Health check registered: ${name}`, {
      name,
      type: config.type,
      interval: config.interval
    }, this.context);
  }

  async performHealthChecks() {
    const results = new Map();
    
    for (const [name, healthCheck] of this.healthChecks.entries()) {
      if (this.shouldRunHealthCheck(healthCheck)) {
        try {
          const result = await this.runHealthCheck(name, healthCheck);
          results.set(name, result);
        } catch (error) {
          logError(`Health check failed: ${name}`, {
            error: error.message
          }, this.context);
        }
      }
    }
    
    // Update overall system health
    this.updateSystemHealth(results);
    
    return results;
  }

  shouldRunHealthCheck(healthCheck) {
    if (!healthCheck.lastRun) return true;
    return Date.now() - healthCheck.lastRun >= healthCheck.interval;
  }

  async runHealthCheck(name, healthCheck) {
    const startTime = Date.now();
    
    try {
      healthCheck.lastRun = startTime;
      healthCheck.totalRuns++;
      
      const result = await Promise.race([
        healthCheck.check(),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Health check timeout')), healthCheck.timeout)
        )
      ]);
      
      const duration = Date.now() - startTime;
      healthCheck.avgDuration = (healthCheck.avgDuration * (healthCheck.totalRuns - 1) + duration) / healthCheck.totalRuns;
      
      const healthState = this.evaluateHealthResult(result, healthCheck.thresholds);
      
      healthCheck.lastResult = {
        state: healthState,
        value: result,
        duration,
        timestamp: Date.now()
      };
      
      if (healthState === HEALTH_STATES.HEALTHY) {
        healthCheck.consecutiveFailures = 0;
      } else {
        healthCheck.failures++;
        healthCheck.consecutiveFailures++;
      }
      
      // Log performance metric
      performance(`health_check.${name}`, duration, {
        state: healthState,
        value: result
      }, this.context);
      
      return healthCheck.lastResult;
      
    } catch (error) {
      const duration = Date.now() - startTime;
      
      healthCheck.failures++;
      healthCheck.consecutiveFailures++;
      healthCheck.lastResult = {
        state: HEALTH_STATES.CRITICAL,
        error: error.message,
        duration,
        timestamp: Date.now()
      };
      
      logError(`Health check error: ${name}`, {
        error: error.message,
        duration
      }, this.context);
      
      return healthCheck.lastResult;
    }
  }

  evaluateHealthResult(result, thresholds) {
    if (typeof result !== 'number') {
      return result.healthy ? HEALTH_STATES.HEALTHY : HEALTH_STATES.CRITICAL;
    }
    
    if (thresholds.critical && result >= thresholds.critical) {
      return HEALTH_STATES.CRITICAL;
    }
    
    if (thresholds.warning && result >= thresholds.warning) {
      return HEALTH_STATES.WARNING;
    }
    
    return HEALTH_STATES.HEALTHY;
  }

  // Specific health check implementations
  async checkMemoryHealth() {
    if (performance.memory) {
      const used = performance.memory.usedJSHeapSize;
      const total = performance.memory.totalJSHeapSize;
      const usage = used / total;
      
      this.recordMetric('system.memory.used', used);
      this.recordMetric('system.memory.total', total);
      
      return usage;
    }
    
    return { healthy: true, message: 'Memory API not available' };
  }

  async checkCPUHealth() {
    // Simulate CPU usage check (in real implementation, would use actual CPU monitoring)
    const startTime = performance.now();
    
    // Perform a small computational task to measure CPU responsiveness
    let result = 0;
    for (let i = 0; i < 100000; i++) {
      result += Math.random();
    }
    
    const duration = performance.now() - startTime;
    const cpuUsage = Math.min(duration / 100, 1); // Normalize to 0-1
    
    this.recordMetric('system.cpu.usage', cpuUsage);
    
    return cpuUsage;
  }

  async checkStorageHealth() {
    if (navigator.storage && navigator.storage.estimate) {
      try {
        const estimate = await navigator.storage.estimate();
        const usage = estimate.usage / estimate.quota;
        
        this.recordMetric('system.storage.used', estimate.usage);
        
        return usage;
      } catch (error) {
        return { healthy: false, message: 'Storage check failed' };
      }
    }
    
    return { healthy: true, message: 'Storage API not available' };
  }

  async checkNetworkHealth() {
    const startTime = Date.now();
    
    try {
      // Test network connectivity with a simple request
      const response = await fetch('/api/health', {
        method: 'HEAD',
        cache: 'no-cache'
      });
      
      const latency = Date.now() - startTime;
      
      this.recordMetric('system.network.latency', latency);
      
      return response.ok ? latency : 10000; // Return high latency if not ok
    } catch (error) {
      return 10000; // Return high latency on error
    }
  }

  async checkModuleHealth(module) {
    const startTime = Date.now();
    
    try {
      // In a real implementation, this would make an actual API call to the module
      const response = await fetch(`/api/${module}/health`);
      const latency = Date.now() - startTime;
      
      this.recordMetric(`agent.${module}.response_time`, latency);
      
      if (response.ok) {
        const health = await response.json();
        this.moduleHealth.set(module, HEALTH_STATES.HEALTHY);
        return latency;
      } else {
        this.moduleHealth.set(module, HEALTH_STATES.CRITICAL);
        return 10000;
      }
    } catch (error) {
      this.moduleHealth.set(module, HEALTH_STATES.OFFLINE);
      return 10000;
    }
  }

  // Metrics management
  registerMetric(name, type) {
    this.metrics.set(name, {
      type,
      value: type === METRIC_TYPES.COUNTER ? 0 : null,
      history: [],
      maxHistory: 1000,
      created: Date.now()
    });
  }

  recordMetric(name, value) {
    const metric = this.metrics.get(name);
    if (!metric) return;
    
    const timestamp = Date.now();
    
    switch (metric.type) {
      case METRIC_TYPES.COUNTER:
        metric.value += value;
        break;
      case METRIC_TYPES.GAUGE:
        metric.value = value;
        break;
      case METRIC_TYPES.HISTOGRAM:
      case METRIC_TYPES.TIMER:
        metric.history.push({ value, timestamp });
        if (metric.history.length > metric.maxHistory) {
          metric.history = metric.history.slice(-metric.maxHistory);
        }
        break;
    }
    
    // Emit metric event
    emit(EVENT_TYPES.SYSTEM_EVENT, {
      type: 'metric_recorded',
      metric: name,
      value,
      timestamp
    });
  }

  collectMetrics() {
    // Record system uptime
    this.recordMetric('system.uptime', Date.now() - this.startTime || Date.now());
    
    // Collect additional metrics based on current state
    this.collectApplicationMetrics();
    this.collectPerformanceMetrics();
  }

  collectApplicationMetrics() {
    // Record active sessions (placeholder)
    this.recordMetric('app.sessions.active', 1);
  }

  collectPerformanceMetrics() {
    // Collect performance data from the browser
    if (performance.getEntriesByType) {
      const entries = performance.getEntriesByType('navigation');
      if (entries.length > 0) {
        const navigation = entries[0];
        this.recordMetric('app.response.time', navigation.loadEventEnd - navigation.fetchStart);
      }
    }
  }

  // Alert management
  evaluateAlerts() {
    for (const [name, healthCheck] of this.healthChecks.entries()) {
      if (healthCheck.lastResult) {
        this.checkAlertConditions(name, healthCheck);
      }
    }
    
    // Check metric-based alerts
    this.checkMetricAlerts();
  }

  checkAlertConditions(name, healthCheck) {
    const result = healthCheck.lastResult;
    
    // Add cooldown to prevent alert spam - only alert once per 60 seconds for same check
    const alertKey = `${name}_${result.state}`;
    const now = Date.now();
    const lastAlertTime = this.lastAlerts?.get(alertKey) || 0;
    const cooldownPeriod = 60000; // 60 seconds
    
    if (now - lastAlertTime < cooldownPeriod) {
      return; // Skip this alert due to cooldown
    }
    
    if (!this.lastAlerts) {
      this.lastAlerts = new Map();
    }
    
    if (result.state === HEALTH_STATES.CRITICAL) {
      this.createAlert(ALERT_LEVELS.CRITICAL, `Health check critical: ${name}`, {
        healthCheck: name,
        value: result.value,
        error: result.error
      });
      this.lastAlerts.set(alertKey, now);
    } else if (result.state === HEALTH_STATES.WARNING) {
      this.createAlert(ALERT_LEVELS.WARNING, `Health check warning: ${name}`, {
        healthCheck: name,
        value: result.value
      });
      this.lastAlerts.set(alertKey, now);
    }
    
    // Check for consecutive failures
    if (healthCheck.consecutiveFailures >= 3) {
      this.createAlert(ALERT_LEVELS.CRITICAL, `Consecutive failures: ${name}`, {
        healthCheck: name,
        consecutiveFailures: healthCheck.consecutiveFailures
      });
    }
  }

  checkMetricAlerts() {
    for (const [metricName, thresholds] of this.alertThresholds.entries()) {
      const metric = this.metrics.get(metricName);
      if (metric && metric.value !== null) {
        if (metric.value >= thresholds.critical) {
          this.createAlert(ALERT_LEVELS.CRITICAL, `Metric critical: ${metricName}`, {
            metric: metricName,
            value: metric.value,
            threshold: thresholds.critical
          });
        } else if (metric.value >= thresholds.warning) {
          this.createAlert(ALERT_LEVELS.WARNING, `Metric warning: ${metricName}`, {
            metric: metricName,
            value: metric.value,
            threshold: thresholds.warning
          });
        }
      }
    }
  }

  createAlert(level, message, data = {}) {
    if (!this.alertingEnabled) return;
    
    const alert = {
      id: this.generateAlertId(),
      level,
      message,
      data,
      timestamp: Date.now(),
      acknowledged: false
    };
    
    this.alerts.unshift(alert);
    
    // Maintain alert limit
    if (this.alerts.length > this.maxAlerts) {
      this.alerts = this.alerts.slice(0, this.maxAlerts);
    }
    
    // Log alert
    if (level === ALERT_LEVELS.CRITICAL) {
      logError(`ALERT: ${message}`, data, this.context);
    } else {
      logWarn(`ALERT: ${message}`, data, this.context);
    }
    
    // Emit alert event
    emit(EVENT_TYPES.SYSTEM_EVENT, {
      type: 'alert_created',
      alert
    });
    
    return alert.id;
  }

  updateSystemHealth(healthResults) {
    const states = Array.from(healthResults.values()).map(r => r.state);
    
    if (states.includes(HEALTH_STATES.CRITICAL)) {
      this.systemHealth = HEALTH_STATES.CRITICAL;
    } else if (states.includes(HEALTH_STATES.WARNING)) {
      this.systemHealth = HEALTH_STATES.WARNING;
    } else if (states.every(s => s === HEALTH_STATES.HEALTHY)) {
      this.systemHealth = HEALTH_STATES.HEALTHY;
    } else {
      this.systemHealth = HEALTH_STATES.UNKNOWN;
    }
    
    emit(EVENT_TYPES.SYSTEM_EVENT, {
      type: 'system_health_updated',
      health: this.systemHealth,
      details: Object.fromEntries(healthResults)
    });
  }

  // Event handlers
  handleSystemEvent(event) {
    switch (event.type) {
      case 'api_metrics':
        this.handleAPIMetrics(event.metrics);
        break;
      case 'module_health_update':
        this.handleModuleHealthUpdate(event);
        break;
    }
  }

  handleErrorEvent(event) {
    this.recordMetric('app.requests.errors', 1);
    
    if (event.error.severity === 'critical') {
      this.createAlert(ALERT_LEVELS.CRITICAL, `System error: ${event.error.message}`, {
        error: event.error
      });
    }
  }

  handleAgentEvent(event) {
    const { fromModule, action } = event;
    if (fromModule) {
      this.recordMetric(`agent.${fromModule}.requests`, 1);
    }
  }

  handleAPIMetrics(metrics) {
    // Process API metrics from APIManager
    if (metrics.circuitBreakers) {
      metrics.circuitBreakers.forEach(cb => {
        if (cb.state === 'open') {
          this.createAlert(ALERT_LEVELS.CRITICAL, `Circuit breaker open: ${cb.name}`, {
            circuitBreaker: cb.name,
            failures: cb.failures
          });
        }
      });
    }
  }

  handleModuleHealthUpdate(event) {
    this.moduleHealth.set(event.module, event.health);
  }

  // Diagnostics
  generateDiagnosticReport() {
    return {
      timestamp: Date.now(),
      systemHealth: this.systemHealth,
      moduleHealth: Object.fromEntries(this.moduleHealth),
      healthChecks: this.getHealthCheckSummary(),
      metrics: this.getMetricsSummary(),
      alerts: this.getRecentAlerts(),
      performance: this.getPerformanceSummary()
    };
  }

  getHealthCheckSummary() {
    return Array.from(this.healthChecks.entries()).map(([name, check]) => ({
      name,
      type: check.type,
      state: check.lastResult?.state || HEALTH_STATES.UNKNOWN,
      lastRun: check.lastRun,
      failures: check.failures,
      avgDuration: check.avgDuration
    }));
  }

  getMetricsSummary() {
    return Array.from(this.metrics.entries()).map(([name, metric]) => ({
      name,
      type: metric.type,
      value: metric.value,
      historyLength: metric.history?.length || 0
    }));
  }

  getRecentAlerts(limit = 50) {
    return this.alerts.slice(0, limit);
  }

  getPerformanceSummary() {
    return {
      uptime: Date.now() - (this.startTime || Date.now()),
      memoryUsage: performance.memory ? {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      } : null,
      timing: performance.timing ? {
        navigationStart: performance.timing.navigationStart,
        loadEventEnd: performance.timing.loadEventEnd,
        totalLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
      } : null
    };
  }

  // Utility methods
  generateAlertId() {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Public API methods
  getSystemHealth() {
    return this.systemHealth;
  }

  getModuleHealth(module) {
    return this.moduleHealth.get(module) || HEALTH_STATES.UNKNOWN;
  }

  getHealthCheck(name) {
    return this.healthChecks.get(name);
  }

  getMetric(name) {
    return this.metrics.get(name);
  }

  acknowledgeAlert(alertId) {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = Date.now();
    }
    return alert;
  }

  getHealthStats() {
    return {
      systemHealth: this.systemHealth,
      totalHealthChecks: this.healthChecks.size,
      healthyChecks: Array.from(this.healthChecks.values()).filter(c => 
        c.lastResult?.state === HEALTH_STATES.HEALTHY
      ).length,
      totalMetrics: this.metrics.size,
      totalAlerts: this.alerts.length,
      unacknowledgedAlerts: this.alerts.filter(a => !a.acknowledged).length
    };
  }
}

// Create singleton instance
const healthMonitor = new HealthMonitor();

// Export convenience functions
export const getSystemHealth = () => healthMonitor.getSystemHealth();
export const getModuleHealth = (module) => healthMonitor.getModuleHealth(module);
export const recordMetric = (name, value) => healthMonitor.recordMetric(name, value);
export const createAlert = (level, message, data) => healthMonitor.createAlert(level, message, data);
export const getDiagnosticReport = () => healthMonitor.generateDiagnosticReport();
export const getHealthStats = () => healthMonitor.getHealthStats();
export const acknowledgeAlert = (alertId) => healthMonitor.acknowledgeAlert(alertId);

export default healthMonitor;