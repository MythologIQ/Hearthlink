/**
 * Sentry Persona - Observer-Only Monitoring System
 * 
 * Passive monitoring agent that observes system health, token usage,
 * Claude API status, and LaunchPage render health without taking any
 * enforcement actions until Phase 3 write-to-disk is validated.
 */

import { EventEmitter } from 'events';

interface SentryConfig {
  monitoringInterval: number; // ms
  alertThresholds: {
    tokenUsageHourly: number;
    claudeErrorRate: number; // percentage
    renderHealthFailures: number;
    diskUsagePercent: number;
  };
  logSources: {
    tokenTracker: string;
    claudeErrors: string;
    renderHealth: string;
    systemHealth: string;
  };
  alertDestinations: string[];
  enabled: boolean;
}

interface MonitoringEvent {
  timestamp: string;
  source: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  data: Record<string, any>;
  agentId?: string;
  module?: string;
}

interface SystemHealth {
  claudeConnector: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastResponse: number; // ms
    errorRate: number; // percentage over last hour
    queueDepth: number;
  };
  vaultService: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastWrite: number; // ms ago
    writeSuccessRate: number; // percentage
    diskUsage: number; // percentage
  };
  launchPage: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastRender: number; // ms ago
    renderErrors: number; // in last hour
    loadTime: number; // ms
  };
  tokenUsage: {
    hourlyTotal: number;
    dailyTotal: number;
    averagePerRequest: number;
    topConsumer: string;
  };
}

interface Alert {
  id: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  source: string;
  data: Record<string, any>;
  acknowledged: boolean;
  resolved: boolean;
}

export class SentryPersona extends EventEmitter {
  private config: SentryConfig;
  private isMonitoring: boolean = false;
  private monitoringInterval: any | null = null;
  private events: MonitoringEvent[] = [];
  private alerts: Alert[] = [];
  private systemHealth: SystemHealth;
  
  constructor(config: SentryConfig) {
    super();
    this.config = config;
    this.systemHealth = this.initializeSystemHealth();
    
    console.log('🛡️ Sentry Persona initialized - Observer mode only');
  }

  /**
   * Start monitoring all system components
   */
  startMonitoring(): void {
    if (this.isMonitoring) {
      this.logEvent('warning', 'Monitoring already active', {});
      return;
    }

    this.isMonitoring = true;
    this.logEvent('info', 'Sentry monitoring started', { 
      interval: this.config.monitoringInterval 
    });

    // Start monitoring loop
    this.monitoringInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.config.monitoringInterval);

    // Monitor specific log sources
    this.startLogMonitoring();
    
    // Monitor system resources
    this.startResourceMonitoring();
  }

  /**
   * Stop all monitoring
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) return;

    this.isMonitoring = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    this.logEvent('info', 'Sentry monitoring stopped', {});
  }

  /**
   * Perform comprehensive health check
   */
  private async performHealthCheck(): Promise<void> {
    try {
      // Check Claude Connector health
      await this.checkClaudeHealth();
      
      // Check Vault Service health  
      await this.checkVaultHealth();
      
      // Check LaunchPage render health
      await this.checkLaunchPageHealth();
      
      // Check token usage patterns
      await this.checkTokenUsage();
      
      // Analyze for potential issues
      this.analyzeSystemHealth();
      
    } catch (error) {
      this.logEvent('error', 'Health check failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Check Claude Connector health
   */
  private async checkClaudeHealth(): Promise<void> {
    try {
      // Try to get Claude connector status
      const claudeConnector = (window as any).claudeConnector;
      
      if (!claudeConnector) {
        this.systemHealth.claudeConnector.status = 'unhealthy';
        this.generateAlert('high', 'Claude Connector Missing', 
          'Claude connector not available in global scope', 'claude');
        return;
      }

      // Get health status
      const healthStatus = await claudeConnector.healthCheck();
      
      this.systemHealth.claudeConnector.status = healthStatus.status;
      this.systemHealth.claudeConnector.lastResponse = Date.now();
      
      // Get queue status
      const queueStatus = claudeConnector.getQueueStatus();
      this.systemHealth.claudeConnector.queueDepth = queueStatus.active;
      
      // Check for queue backup
      if (queueStatus.active > 10) {
        this.generateAlert('medium', 'Claude Queue Backup', 
          `Queue depth: ${queueStatus.active} requests`, 'claude');
      }
      
    } catch (error) {
      this.systemHealth.claudeConnector.status = 'unhealthy';
      this.logEvent('error', 'Claude health check failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Check Vault Service health
   */
  private async checkVaultHealth(): Promise<void> {
    try {
      // Check vault health endpoint
      const response = await fetch('http://localhost:8081/api/health');
      
      if (response.ok) {
        const health = await response.json();
        this.systemHealth.vaultService.status = 'healthy';
        
        // Check if writable
        if (!health.writable) {
          this.generateAlert('high', 'Vault Not Writable', 
            'Vault service reports not writable', 'vault');
        }
      } else {
        this.systemHealth.vaultService.status = 'unhealthy';
        this.generateAlert('critical', 'Vault Service Down', 
          `Vault health check failed: ${response.status}`, 'vault');
      }
      
    } catch (error) {
      this.systemHealth.vaultService.status = 'unhealthy';
      this.logEvent('error', 'Vault health check failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Check LaunchPage render health
   */
  private async checkLaunchPageHealth(): Promise<void> {
    try {
      // Check if LaunchPage is rendered and functional
      const launchPage = document.querySelector('.launch-page');
      
      if (!launchPage) {
        this.systemHealth.launchPage.status = 'unhealthy';
        this.generateAlert('medium', 'LaunchPage Not Rendered', 
          'LaunchPage component not found in DOM', 'launchpage');
        return;
      }

      // Check for loading icon
      const loadingIcon = launchPage.querySelector('.loading-icon');
      
      // Check for module icons
      const moduleIcons = launchPage.querySelectorAll('.module-icon');
      
      if (moduleIcons.length < 7) {
        this.systemHealth.launchPage.status = 'degraded';
        this.generateAlert('low', 'LaunchPage Incomplete', 
          `Only ${moduleIcons.length}/7 module icons rendered`, 'launchpage');
      } else {
        this.systemHealth.launchPage.status = 'healthy';
      }
      
      this.systemHealth.launchPage.lastRender = Date.now();
      
    } catch (error) {
      this.systemHealth.launchPage.status = 'unhealthy';
      this.logEvent('error', 'LaunchPage health check failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Check token usage patterns
   */
  private async checkTokenUsage(): Promise<void> {
    try {
      // Try to read token tracker log (observer only)
      const response = await fetch('http://localhost:8081/api/read', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + (window as any).vaultToken || 'default'
        },
        body: JSON.stringify({
          path: 'logs/agent_token_tracker.log',
          agentId: 'sentry'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        this.analyzeTokenUsage(data.content);
      }
      
    } catch (error) {
      this.logEvent('warning', 'Token usage check failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Analyze token usage patterns
   */
  private analyzeTokenUsage(logContent: string): void {
    try {
      const lines = logContent.split('\n').filter(line => line.trim());
      const hourAgo = Date.now() - (60 * 60 * 1000);
      const dayAgo = Date.now() - (24 * 60 * 60 * 1000);
      
      let hourlyTotal = 0;
      let dailyTotal = 0;
      let requestCount = 0;
      const agentUsage: Record<string, number> = {};
      
      for (const line of lines) {
        if (line.startsWith('{')) {
          try {
            const entry = JSON.parse(line);
            const timestamp = new Date(entry.timestamp).getTime();
            
            if (timestamp > dayAgo) {
              dailyTotal += entry.tokens_used || 0;
              agentUsage[entry.agent_name] = (agentUsage[entry.agent_name] || 0) + entry.tokens_used;
              
              if (timestamp > hourAgo) {
                hourlyTotal += entry.tokens_used || 0;
                requestCount++;
              }
            }
          } catch (e) {
            // Skip invalid JSON lines
          }
        }
      }
      
      this.systemHealth.tokenUsage = {
        hourlyTotal,
        dailyTotal,
        averagePerRequest: requestCount > 0 ? hourlyTotal / requestCount : 0,
        topConsumer: Object.keys(agentUsage).sort((a, b) => agentUsage[b] - agentUsage[a])[0] || 'none'
      };
      
      // Check thresholds
      if (hourlyTotal > this.config.alertThresholds.tokenUsageHourly) {
        this.generateAlert('medium', 'High Token Usage', 
          `Hourly usage: ${hourlyTotal} tokens (threshold: ${this.config.alertThresholds.tokenUsageHourly})`, 'tokens');
      }
      
    } catch (error) {
      this.logEvent('error', 'Token usage analysis failed', { 
        error: error.message 
      });
    }
  }

  /**
   * Start monitoring log sources
   */
  private startLogMonitoring(): void {
    // Monitor Claude errors
    this.monitorClaudeErrors();
    
    // Monitor render health
    this.monitorRenderHealth();
  }

  /**
   * Monitor Claude API errors
   */
  private monitorClaudeErrors(): void {
    // Hook into Claude connector error events if available
    const claudeConnector = (window as any).claudeConnector;
    
    if (claudeConnector && claudeConnector.on) {
      claudeConnector.on('error', (error: any) => {
        this.logEvent('error', 'Claude API Error', {
          error: error.message,
          type: error.type,
          statusCode: error.statusCode
        });
        
        if (error.type === 'rate_limit') {
          this.generateAlert('high', 'Claude Rate Limit', 
            'Claude API rate limit exceeded', 'claude');
        }
      });
    }
  }

  /**
   * Monitor render health
   */
  private monitorRenderHealth(): void {
    // Monitor React error boundaries
    window.addEventListener('error', (event) => {
      this.logEvent('error', 'Render Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
      
      this.systemHealth.launchPage.renderErrors++;
    });
    
    // Monitor unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logEvent('error', 'Unhandled Promise Rejection', {
        reason: event.reason
      });
    });
  }

  /**
   * Start resource monitoring
   */
  private startResourceMonitoring(): void {
    // Monitor memory usage
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        if (memory) {
          const usagePercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
          
          if (usagePercent > 80) {
            this.generateAlert('medium', 'High Memory Usage', 
              `Memory usage: ${usagePercent.toFixed(1)}%`, 'system');
          }
        }
      }, 30000); // Check every 30 seconds
    }
  }

  /**
   * Analyze overall system health
   */
  private analyzeSystemHealth(): void {
    const healthScores = {
      claude: this.systemHealth.claudeConnector.status === 'healthy' ? 100 : 
              this.systemHealth.claudeConnector.status === 'degraded' ? 60 : 0,
      vault: this.systemHealth.vaultService.status === 'healthy' ? 100 : 
             this.systemHealth.vaultService.status === 'degraded' ? 60 : 0,
      launchPage: this.systemHealth.launchPage.status === 'healthy' ? 100 : 
                  this.systemHealth.launchPage.status === 'degraded' ? 60 : 0
    };
    
    const overallScore = (healthScores.claude + healthScores.vault + healthScores.launchPage) / 3;
    
    if (overallScore < 30) {
      this.generateAlert('critical', 'System Health Critical', 
        `Overall health score: ${overallScore.toFixed(1)}%`, 'system');
    } else if (overallScore < 60) {
      this.generateAlert('high', 'System Health Degraded', 
        `Overall health score: ${overallScore.toFixed(1)}%`, 'system');
    }
  }

  /**
   * Generate an alert
   */
  private generateAlert(severity: Alert['severity'], title: string, description: string, source: string): void {
    // Check if similar alert already exists and is not resolved
    const existingAlert = this.alerts.find(alert => 
      alert.title === title && 
      !alert.resolved && 
      Date.now() - new Date(alert.timestamp).getTime() < 300000 // 5 minutes
    );
    
    if (existingAlert) {
      return; // Don't spam same alerts
    }
    
    const alert: Alert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      severity,
      title,
      description,
      source,
      data: { ...this.systemHealth },
      acknowledged: false,
      resolved: false
    };
    
    this.alerts.push(alert);
    
    // Keep only last 100 alerts
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-100);
    }
    
    this.logEvent('warning', `Alert generated: ${title}`, {
      severity,
      alertId: alert.id
    });
    
    // Emit alert event
    this.emit('alert', alert);
    
    // Observer mode - just log, no enforcement actions
    console.warn(`🚨 Sentry Alert [${severity.toUpperCase()}]: ${title} - ${description}`);
  }

  /**
   * Log an event
   */
  private logEvent(type: MonitoringEvent['type'], message: string, data: Record<string, any>): void {
    const event: MonitoringEvent = {
      timestamp: new Date().toISOString(),
      source: 'sentry',
      type,
      message,
      data
    };
    
    this.events.push(event);
    
    // Keep only last 1000 events
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }
    
    // Emit event
    this.emit('event', event);
    
    // Console logging based on type
    const prefix = '🛡️ Sentry:';
    switch (type) {
      case 'info':
        console.info(`${prefix} ${message}`, data);
        break;
      case 'warning':
        console.warn(`${prefix} ${message}`, data);
        break;
      case 'error':
        console.error(`${prefix} ${message}`, data);
        break;
      case 'critical':
        console.error(`${prefix} CRITICAL: ${message}`, data);
        break;
    }
  }

  /**
   * Initialize system health structure
   */
  private initializeSystemHealth(): SystemHealth {
    return {
      claudeConnector: {
        status: 'unhealthy',
        lastResponse: 0,
        errorRate: 0,
        queueDepth: 0
      },
      vaultService: {
        status: 'unhealthy',
        lastWrite: 0,
        writeSuccessRate: 0,
        diskUsage: 0
      },
      launchPage: {
        status: 'unhealthy',
        lastRender: 0,
        renderErrors: 0,
        loadTime: 0
      },
      tokenUsage: {
        hourlyTotal: 0,
        dailyTotal: 0,
        averagePerRequest: 0,
        topConsumer: 'none'
      }
    };
  }

  /**
   * Get current system health
   */
  getSystemHealth(): SystemHealth {
    return { ...this.systemHealth };
  }

  /**
   * Get recent events
   */
  getRecentEvents(limit: number = 50): MonitoringEvent[] {
    return this.events.slice(-limit);
  }

  /**
   * Get active alerts
   */
  getActiveAlerts(): Alert[] {
    return this.alerts.filter(alert => !alert.resolved);
  }

  /**
   * Acknowledge an alert
   */
  acknowledgeAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      this.logEvent('info', 'Alert acknowledged', { alertId });
      return true;
    }
    return false;
  }

  /**
   * Resolve an alert
   */
  resolveAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      alert.acknowledged = true;
      this.logEvent('info', 'Alert resolved', { alertId });
      return true;
    }
    return false;
  }

  /**
   * Get monitoring status
   */
  getStatus(): { isMonitoring: boolean; uptime: number; eventCount: number; alertCount: number } {
    return {
      isMonitoring: this.isMonitoring,
      uptime: this.isMonitoring ? Date.now() - new Date(this.events[0]?.timestamp || Date.now()).getTime() : 0,
      eventCount: this.events.length,
      alertCount: this.alerts.filter(a => !a.resolved).length
    };
  }
}

// Default configuration
export const DEFAULT_SENTRY_CONFIG: SentryConfig = {
  monitoringInterval: 30000, // 30 seconds
  alertThresholds: {
    tokenUsageHourly: 10000,
    claudeErrorRate: 10, // 10%
    renderHealthFailures: 3,
    diskUsagePercent: 80
  },
  logSources: {
    tokenTracker: 'logs/agent_token_tracker.log',
    claudeErrors: 'logs/claude_errors.log',
    renderHealth: 'logs/render_health.log',
    systemHealth: 'logs/system_health.log'
  },
  alertDestinations: ['console', 'vault'],
  enabled: true
};

// Global instance
let _sentryInstance: SentryPersona | null = null;

export function getSentryPersona(config?: Partial<SentryConfig>): SentryPersona {
  if (!_sentryInstance) {
    const finalConfig = { ...DEFAULT_SENTRY_CONFIG, ...config };
    _sentryInstance = new SentryPersona(finalConfig);
  }
  return _sentryInstance;
}

export default SentryPersona;