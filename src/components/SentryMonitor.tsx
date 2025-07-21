/**
 * Sentry Monitor Component
 * 
 * React component that integrates with the Sentry persona to display
 * system health monitoring in the UI. Observer-only mode until Phase 3
 * write-to-disk is validated operational.
 */

import React, { useState, useEffect } from 'react';
import { Eye, Shield, AlertTriangle, Activity, CheckCircle, XCircle } from 'lucide-react';
// import { getSentryPersona, SentryPersona } from '../personas/sentry/sentry';

interface MonitoringEvent {
  timestamp: string;
  source: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  data: Record<string, any>;
}

interface Alert {
  id: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  source: string;
  acknowledged: boolean;
  resolved: boolean;
}

interface SystemHealth {
  claudeConnector: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastResponse: number;
    errorRate: number;
    queueDepth: number;
  };
  vaultService: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastWrite: number;
    writeSuccessRate: number;
    diskUsage: number;
  };
  launchPage: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastRender: number;
    renderErrors: number;
    loadTime: number;
  };
  synapseGateway: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    activeConnections: number;
    blockedRequests: number;
    errorRate: number;
    lastSecurityEvent: number;
    pluginStatus: Record<string, 'active' | 'inactive' | 'error'>;
  };
  tokenUsage: {
    hourlyTotal: number;
    dailyTotal: number;
    averagePerRequest: number;
    topConsumer: string;
  };
}

// Sentry API service class
class SentryApiService {
  private baseUrl = 'http://localhost:8004/api/sentry';
  
  async getSystemHealth(): Promise<SystemHealth> {
    try {
      const response = await fetch(`${this.baseUrl}/system-health`);
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to get system health:', error);
      // Return fallback data
      return {
        claudeConnector: { status: 'unhealthy', lastResponse: 0, errorRate: 100, queueDepth: 0 },
        vaultService: { status: 'unhealthy', lastWrite: 0, writeSuccessRate: 0, diskUsage: 0 },
        launchPage: { status: 'unhealthy', lastRender: 0, renderErrors: 1, loadTime: 0 },
        synapseGateway: { 
          status: 'unhealthy', 
          activeConnections: 0, 
          blockedRequests: 0, 
          errorRate: 100, 
          lastSecurityEvent: 0,
          pluginStatus: {}
        },
        tokenUsage: { hourlyTotal: 0, dailyTotal: 0, averagePerRequest: 0, topConsumer: 'Unknown' }
      };
    }
  }
  
  async getActiveAlerts(): Promise<Alert[]> {
    try {
      const response = await fetch(`${this.baseUrl}/alerts`);
      if (response.ok) {
        const data = await response.json();
        return data.alerts || [];
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to get active alerts:', error);
      return [];
    }
  }
  
  async getRecentEvents(limit: number = 50): Promise<MonitoringEvent[]> {
    try {
      const response = await fetch(`${this.baseUrl}/events?limit=${limit}`);
      if (response.ok) {
        const data = await response.json();
        return data.events || [];
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to get recent events:', error);
      return [];
    }
  }
  
  async getStatus(): Promise<{ isMonitoring: boolean }> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      if (response.ok) {
        const data = await response.json();
        return { isMonitoring: data.is_monitoring };
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to get monitoring status:', error);
      return { isMonitoring: false };
    }
  }
  
  async acknowledgeAlert(alertId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/alerts/${alertId}/acknowledge`, {
        method: 'POST'
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
      return false;
    }
  }
  
  async resolveAlert(alertId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/alerts/${alertId}/resolve`, {
        method: 'POST'
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      return false;
    }
  }
  
  async startMonitoring(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/start`, {
        method: 'POST'
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      return false;
    }
  }
  
  async stopMonitoring(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/stop`, {
        method: 'POST'
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
      return false;
    }
  }
}

const SentryMonitor: React.FC = () => {
  const [sentryApi] = useState(() => new SentryApiService());
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [recentEvents, setRecentEvents] = useState<MonitoringEvent[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [showDetails, setShowDetails] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const updateData = async () => {
    try {
      const [health, alerts, events, status] = await Promise.all([
        sentryApi.getSystemHealth(),
        sentryApi.getActiveAlerts(),
        sentryApi.getRecentEvents(50),
        sentryApi.getStatus()
      ]);

      setSystemHealth(health);
      setActiveAlerts(alerts);
      setRecentEvents(events);
      setIsMonitoring(status.isMonitoring);
    } catch (error) {
      console.error('Failed to update monitoring data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Initial data load
    updateData();

    // Start monitoring automatically
    sentryApi.startMonitoring();

    // Update data periodically
    const healthInterval = setInterval(() => {
      updateData();
    }, 5000);

    return () => {
      clearInterval(healthInterval);
    };
  }, [sentryApi]);

  const handleAcknowledgeAlert = async (alertId: string) => {
    const success = await sentryApi.acknowledgeAlert(alertId);
    if (success) {
      updateData(); // Refresh data after acknowledging
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    const success = await sentryApi.resolveAlert(alertId);
    if (success) {
      updateData(); // Refresh data after resolving
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      case 'unhealthy': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />;
      case 'degraded': return <AlertTriangle className="w-4 h-4" />;
      case 'unhealthy': return <XCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-blue-100 text-blue-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };


  if (isLoading) {
    return (
      <div className="bg-starcraft-darker p-6 rounded-lg border border-starcraft-blue/30">
        <div className="flex items-center justify-center py-8">
          <div className="text-starcraft-blue">Loading Sentry Monitor...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-starcraft-darker p-6 rounded-lg border border-starcraft-blue/30">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-starcraft-blue" />
          <h2 className="text-xl font-orbitron font-bold text-starcraft-blue">
            SENTRY MONITOR
          </h2>
          <div className={`px-2 py-1 rounded text-xs font-bold ${
            isMonitoring ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'
          }`}>
            {isMonitoring ? 'ACTIVE' : 'OFFLINE'}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => updateData()}
            className="text-starcraft-gold hover:text-starcraft-blue transition-colors"
            title="Refresh data"
          >
            <Activity className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-starcraft-gold hover:text-starcraft-blue transition-colors"
            title="Toggle details"
          >
            <Eye className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* System Health Overview */}
      {systemHealth && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Claude Connector */}
          <div className="bg-starcraft-dark/50 p-4 rounded border border-starcraft-blue/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-starcraft-gold">Claude</span>
              <div className={`flex items-center gap-1 ${getStatusColor(systemHealth.claudeConnector.status)}`}>
                {getStatusIcon(systemHealth.claudeConnector.status)}
                <span className="text-xs font-bold uppercase">{systemHealth.claudeConnector.status}</span>
              </div>
            </div>
            <div className="text-xs text-slate-400 space-y-1">
              <div>Queue: {systemHealth.claudeConnector.queueDepth} requests</div>
              <div>Error Rate: {systemHealth.claudeConnector.errorRate.toFixed(1)}%</div>
            </div>
          </div>

          {/* Vault Service */}
          <div className="bg-starcraft-dark/50 p-4 rounded border border-starcraft-blue/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-starcraft-gold">Vault</span>
              <div className={`flex items-center gap-1 ${getStatusColor(systemHealth.vaultService.status)}`}>
                {getStatusIcon(systemHealth.vaultService.status)}
                <span className="text-xs font-bold uppercase">{systemHealth.vaultService.status}</span>
              </div>
            </div>
            <div className="text-xs text-slate-400 space-y-1">
              <div>Success Rate: {systemHealth.vaultService.writeSuccessRate.toFixed(1)}%</div>
              <div>Disk Usage: {systemHealth.vaultService.diskUsage.toFixed(1)}%</div>
            </div>
          </div>

          {/* Launch Page */}
          <div className="bg-starcraft-dark/50 p-4 rounded border border-starcraft-blue/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-starcraft-gold">Launch Page</span>
              <div className={`flex items-center gap-1 ${getStatusColor(systemHealth.launchPage.status)}`}>
                {getStatusIcon(systemHealth.launchPage.status)}
                <span className="text-xs font-bold uppercase">{systemHealth.launchPage.status}</span>
              </div>
            </div>
            <div className="text-xs text-slate-400 space-y-1">
              <div>Render Errors: {systemHealth.launchPage.renderErrors}</div>
              <div>Load Time: {systemHealth.launchPage.loadTime}ms</div>
            </div>
          </div>

          {/* Synapse Gateway */}
          {systemHealth.synapseGateway && (
            <div className="bg-starcraft-dark/50 p-4 rounded border border-starcraft-blue/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-starcraft-gold">Synapse</span>
                <div className={`flex items-center gap-1 ${getStatusColor(systemHealth.synapseGateway.status)}`}>
                  {getStatusIcon(systemHealth.synapseGateway.status)}
                  <span className="text-xs font-bold uppercase">{systemHealth.synapseGateway.status}</span>
                </div>
              </div>
              <div className="text-xs text-slate-400 space-y-1">
                <div>Connections: {systemHealth.synapseGateway.activeConnections}</div>
                <div>Blocked: {systemHealth.synapseGateway.blockedRequests}</div>
                <div>Error Rate: {systemHealth.synapseGateway.errorRate.toFixed(1)}%</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-starcraft-gold mb-3">Active Alerts</h3>
          <div className="space-y-2">
            {activeAlerts.slice(0, 3).map(alert => (
              <div key={alert.id} className="bg-starcraft-dark/30 p-3 rounded border border-red-500/30">
                <div className="flex items-center justify-between mb-1">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${getSeverityColor(alert.severity)}`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-400">{formatTimestamp(alert.timestamp)}</span>
                </div>
                <div className="text-sm font-medium text-white">{alert.title}</div>
                <div className="text-xs text-slate-300 mb-2">{alert.description}</div>
                <div className="flex items-center gap-2">
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledgeAlert(alert.id)}
                      className="px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors"
                    >
                      Acknowledge
                    </button>
                  )}
                  {!alert.resolved && (
                    <button
                      onClick={() => handleResolveAlert(alert.id)}
                      className="px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                    >
                      Resolve
                    </button>
                  )}
                  {alert.acknowledged && (
                    <span className="text-xs text-yellow-400">✓ Acknowledged</span>
                  )}
                  {alert.resolved && (
                    <span className="text-xs text-green-400">✓ Resolved</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Token Usage Summary */}
      {systemHealth && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-starcraft-gold mb-3">Token Usage</h3>
          <div className="bg-starcraft-dark/30 p-4 rounded border border-starcraft-blue/20">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-starcraft-blue">
                  {systemHealth.tokenUsage.hourlyTotal.toLocaleString()}
                </div>
                <div className="text-xs text-slate-400">Hourly</div>
              </div>
              <div>
                <div className="text-xl font-bold text-starcraft-blue">
                  {systemHealth.tokenUsage.dailyTotal.toLocaleString()}
                </div>
                <div className="text-xs text-slate-400">Daily</div>
              </div>
              <div>
                <div className="text-xl font-bold text-starcraft-blue">
                  {Math.round(systemHealth.tokenUsage.averagePerRequest)}
                </div>
                <div className="text-xs text-slate-400">Avg/Request</div>
              </div>
              <div>
                <div className="text-sm font-bold text-starcraft-blue">
                  {systemHealth.tokenUsage.topConsumer}
                </div>
                <div className="text-xs text-slate-400">Top Consumer</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Events (if details shown) */}
      {showDetails && (
        <div>
          <h3 className="text-lg font-semibold text-starcraft-gold mb-3">Recent Events</h3>
          <div className="bg-starcraft-dark/30 rounded border border-starcraft-blue/20 max-h-64 overflow-y-auto">
            {recentEvents.length === 0 ? (
              <div className="p-4 text-center text-slate-400">No recent events</div>
            ) : (
              <div className="space-y-1">
                {recentEvents.slice(-10).reverse().map((event, index) => (
                  <div key={index} className="px-3 py-2 border-b border-starcraft-blue/10 last:border-b-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-medium ${
                        event.type === 'error' ? 'text-red-400' :
                        event.type === 'warning' ? 'text-yellow-400' :
                        event.type === 'critical' ? 'text-red-500' :
                        'text-starcraft-blue'
                      }`}>
                        {event.type.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-400">{formatTimestamp(event.timestamp)}</span>
                    </div>
                    <div className="text-sm text-slate-200 mt-1">{event.message}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Observer Mode Notice */}
      <div className="mt-6 p-3 bg-blue-900/30 border border-blue-500/30 rounded">
        <div className="flex items-center gap-2 text-blue-200">
          <Eye className="w-4 h-4" />
          <span className="text-sm font-medium">Observer Mode Active</span>
        </div>
        <div className="text-xs text-blue-300 mt-1">
          Sentry is monitoring system health but will not take enforcement actions until Phase 3 write-to-disk is validated operational.
        </div>
      </div>
    </div>
  );
};

export default SentryMonitor;