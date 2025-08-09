import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, Button, Badge, Alert, AlertTitle, AlertDescription } from '@/components/ui/index';
import RefreshCw from 'lucide-react/dist/icons/refresh-cw.js';
import { ExternalLink, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import './ui-controls.css';

interface GrafanaDashboard {
  id: string;
  title: string;
  description: string;
  tags: string[];
  url: string;
  status: 'healthy' | 'warning' | 'error';
  lastUpdated: string;
}

interface GrafanaAlert {
  id: string;
  title: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
  dashboard: string;
}

const GRAFANA_CONFIG = {
  baseUrl: process.env.REACT_APP_GRAFANA_URL || 'http://localhost:3000',
  apiKey: process.env.REACT_APP_GRAFANA_API_KEY || '',
  orgId: process.env.REACT_APP_GRAFANA_ORG_ID || '1',
  theme: 'dark',
  kiosk: 'tv', // Full kiosk mode for embedded display
};

// Production dashboards configuration
const PRODUCTION_DASHBOARDS: GrafanaDashboard[] = [
  {
    id: 'vector-store-health',
    title: 'Vector Store Health & Advanced Observability',
    description: 'PostgreSQL + PGVector metrics, RAG/CAG retrieval, memory slicing, CoT analysis, agent interactions, error correlation',
    tags: ['vector-store', 'postgresql', 'performance', 'rag-cag', 'memory-slicing', 'chain-of-thought', 'agent-interactions', 'error-correlation'],
    url: '/d/vector-store-health/vector-store-health-performance',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'multi-agent-memory',
    title: 'Multi-Agent Memory Sync',
    description: 'Agent conflicts, sync latency, and resolution strategies',
    tags: ['agents', 'memory-sync', 'conflicts'],
    url: '/d/multi-agent-memory/multi-agent-memory-sync',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'alice-persona-metrics',
    title: 'Alice - Cognitive Behavioral Analysis',
    description: 'CBT session metrics, bias detection, and therapeutic outcomes',
    tags: ['alice', 'cbt', 'personas'],
    url: '/d/alice-persona/alice-cognitive-behavioral-analysis',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'sentry-security-dashboard',
    title: 'Sentry - Security Operations Center',
    description: 'Threat detection, incident response, and security metrics',
    tags: ['sentry', 'security', 'incidents'],
    url: '/d/sentry-security/sentry-security-operations-center',
    status: 'warning',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'mimic-adaptation-metrics',
    title: 'Mimic - Persona Adaptation',
    description: 'Dynamic persona switching, adaptation triggers, and user preferences',
    tags: ['mimic', 'adaptation', 'personas'],
    url: '/d/mimic-adaptation/mimic-persona-adaptation',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'vault-security-monitoring',
    title: 'HashiCorp Vault Security',
    description: 'Vault health, key rotation, access patterns, and audit logs',
    tags: ['vault', 'security', 'key-rotation'],
    url: '/d/vault-security/hashicorp-vault-security',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  },
  {
    id: 'system-performance-overview',
    title: 'System Performance Overview',
    description: 'CPU, memory, disk I/O, network, and overall system health',
    tags: ['system', 'performance', 'infrastructure'],
    url: '/d/system-performance/system-performance-overview',
    status: 'healthy',
    lastUpdated: new Date().toISOString()
  }
];

const EmbeddedGrafana: React.FC = () => {
  const [dashboards, setDashboards] = useState<GrafanaDashboard[]>(PRODUCTION_DASHBOARDS);
  const [selectedDashboard, setSelectedDashboard] = useState<GrafanaDashboard>(PRODUCTION_DASHBOARDS[0]);
  const [alerts, setAlerts] = useState<GrafanaAlert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('connected');
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Build Grafana iframe URL with authentication and theme
  const buildGrafanaUrl = useCallback((dashboard: GrafanaDashboard) => {
    const params = new URLSearchParams({
      orgId: GRAFANA_CONFIG.orgId,
      theme: GRAFANA_CONFIG.theme,
      kiosk: GRAFANA_CONFIG.kiosk,
      refresh: '30s', // Auto-refresh every 30 seconds
      from: 'now-1h',   // Show last hour by default
      to: 'now',
      'var-agent': 'All', // Default variable for agent filtering
      'var-environment': 'production'
    });

    return `${GRAFANA_CONFIG.baseUrl}${dashboard.url}?${params.toString()}`;
  }, []);

  // Fetch Grafana health status
  const checkGrafanaHealth = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${GRAFANA_CONFIG.baseUrl}/api/health`, {
        headers: {
          'Authorization': `Bearer ${GRAFANA_CONFIG.apiKey}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        setConnectionStatus('connected');
        return true;
      } else {
        setConnectionStatus('error');
        return false;
      }
    } catch (error) {
      console.error('Grafana health check failed:', error);
      setConnectionStatus('disconnected');
      return false;
    }
  }, []);

  // Fetch active alerts from Grafana
  const fetchAlerts = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${GRAFANA_CONFIG.baseUrl}/api/alerts`, {
        headers: {
          'Authorization': `Bearer ${GRAFANA_CONFIG.apiKey}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const alertsData = await response.json();
        
        // Transform Grafana alerts to our format
        const transformedAlerts: GrafanaAlert[] = alertsData.map((alert: any) => ({
          id: alert.id.toString(),
          title: alert.name || 'Unknown Alert',
          severity: alert.state === 'alerting' ? 'critical' : 
                   alert.state === 'pending' ? 'warning' : 'info',
          message: alert.message || alert.info || 'No message available',
          timestamp: alert.newStateDate || new Date().toISOString(),
          dashboard: alert.dashboardId ? `dashboard-${alert.dashboardId}` : 'unknown'
        }));

        setAlerts(transformedAlerts);
      }
    } catch (error) {
      console.error('Failed to fetch Grafana alerts:', error);
    }
  }, []);

  // Refresh dashboard data
  const refreshDashboard = useCallback(async () => {
    setIsRefreshing(true);
    
    try {
      await Promise.all([
        checkGrafanaHealth(),
        fetchAlerts()
      ]);
      
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Dashboard refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, [checkGrafanaHealth, fetchAlerts]);

  // Initialize component
  useEffect(() => {
    setIsLoading(true);
    
    const initializeGrafana = async () => {
      await refreshDashboard();
      setIsLoading(false);
    };

    initializeGrafana();

    // Set up auto-refresh interval
    const refreshInterval = setInterval(refreshDashboard, 60000); // Refresh every minute

    return () => clearInterval(refreshInterval);
  }, [refreshDashboard]);

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  // Get alert severity color
  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500';
      case 'warning': return 'text-yellow-500';
      case 'info': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  };

  // Handle alert dismissal
  const handleAlertDismiss = async (alertId: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${GRAFANA_CONFIG.baseUrl}/api/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GRAFANA_CONFIG.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          acknowledged_by: 'hearthlink_user',
          acknowledgement_reason: 'Dismissed via Hearthlink UI',
          timestamp: new Date().toISOString()
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        // Remove alert from local state
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
        console.log(`Alert ${alertId} acknowledged successfully`);
      } else {
        throw new Error(`Failed to acknowledge alert: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
      // Fallback: still remove from UI to provide user feedback
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      alert(`Alert dismissed locally. Backend acknowledgment failed: ${error.message}`);
    }
  };

  // Handle dismiss all alerts
  const handleDismissAllAlerts = async () => {
    const confirmed = confirm(`Dismiss All Alerts\n\nThis will acknowledge all ${alerts.length} active alerts.\n\nProceed?`);
    if (!confirmed) return;

    try {
      const dismissPromises = alerts.map(alert => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const promise = fetch(`${GRAFANA_CONFIG.baseUrl}/api/alerts/${alert.id}/acknowledge`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${GRAFANA_CONFIG.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            acknowledged_by: 'hearthlink_user',
            acknowledgement_reason: 'Bulk dismiss via Hearthlink UI',
            timestamp: new Date().toISOString()
          }),
          signal: controller.signal
        });
        
        promise.finally(() => clearTimeout(timeoutId));
        return promise;
      });

      await Promise.all(dismissPromises);
      setAlerts([]);
      console.log(`Successfully dismissed ${alerts.length} alerts`);
    } catch (error) {
      console.error('Failed to dismiss all alerts:', error);
      // Fallback: clear UI anyway
      setAlerts([]);
      alert(`Alerts dismissed locally. Some backend acknowledgments may have failed: ${error.message}`);
    }
  };

  // Handle dashboard details viewer
  const handleDashboardDetails = async (dashboardId: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${GRAFANA_CONFIG.baseUrl}/api/grafana/dashboard/${dashboardId}/logs`, {
        headers: {
          'Authorization': `Bearer ${GRAFANA_CONFIG.apiKey}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const logsData = await response.json();
        const dashboard = dashboards.find(d => d.id === dashboardId);
        
        // Create detailed log viewer window
        const detailsWindow = window.open('', '_blank', 'width=900,height=700,scrollbars=yes');
        detailsWindow.document.write(`
          <html>
            <head>
              <title>Dashboard Details - ${dashboard?.title || dashboardId}</title>
              <style>
                body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; padding: 20px; }
                .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 25px; }
                .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
                .status-healthy { background-color: #10b981; }
                .status-warning { background-color: #f59e0b; }
                .status-error { background-color: #ef4444; }
                .log-entry { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin: 10px 0; }
                .log-timestamp { font-weight: 600; color: #6366f1; }
                .log-level { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
                .log-level-error { background: #fef2f2; color: #dc2626; }
                .log-level-warning { background: #fffbeb; color: #d97706; }
                .log-level-info { background: #eff6ff; color: #2563eb; }
                .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                .metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; }
                .metric-value { font-size: 24px; font-weight: 700; color: #1e293b; }
                .metric-label { font-size: 14px; color: #64748b; margin-top: 5px; }
              </style>
            </head>
            <body>
              <div class="header">
                <h1>Dashboard Health Details</h1>
                <h2>
                  <span class="status-indicator status-${dashboard?.status || 'error'}"></span>
                  ${dashboard?.title || dashboardId}
                </h2>
                <p><strong>Status:</strong> ${dashboard?.status?.toUpperCase() || 'UNKNOWN'}</p>
                <p><strong>Description:</strong> ${dashboard?.description || 'No description available'}</p>
                <p><strong>Last Updated:</strong> ${dashboard?.lastUpdated ? new Date(dashboard.lastUpdated).toLocaleString() : 'Unknown'}</p>
              </div>
              
              <div class="metric-grid">
                <div class="metric-card">
                  <div class="metric-value">${logsData.metrics?.error_count || 0}</div>
                  <div class="metric-label">Errors (24h)</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">${logsData.metrics?.warning_count || 0}</div>
                  <div class="metric-label">Warnings (24h)</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">${logsData.metrics?.uptime_percentage || 'N/A'}%</div>
                  <div class="metric-label">Uptime</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">${logsData.metrics?.avg_response_time || 'N/A'}ms</div>
                  <div class="metric-label">Avg Response</div>
                </div>
              </div>
              
              <h3>Recent Log Entries</h3>
              ${logsData.logs && logsData.logs.length > 0 ? logsData.logs.map(log => 
                `<div class="log-entry">
                  <div class="log-timestamp">[${new Date(log.timestamp).toLocaleString()}]</div>
                  <span class="log-level log-level-${log.level}">${log.level.toUpperCase()}</span>
                  <div style="margin-top: 8px;">${log.message}</div>
                  ${log.details ? `<div style="margin-top: 8px; font-size: 14px; color: #64748b;">${log.details}</div>` : ''}
                </div>`
              ).join('') : '<p>No recent log entries available</p>'}
            </body>
          </html>
        `);
        detailsWindow.document.close();
      } else {
        // Fallback for when API is not available
        const dashboard = dashboards.find(d => d.id === dashboardId);
        alert(
          `Dashboard Details: ${dashboard?.title || dashboardId}\n\n` +
          `Status: ${dashboard?.status?.toUpperCase() || 'UNKNOWN'}\n` +
          `Description: ${dashboard?.description || 'No description'}\n` +
          `Last Updated: ${dashboard?.lastUpdated ? new Date(dashboard.lastUpdated).toLocaleString() : 'Unknown'}\n\n` +
          'Detailed logs are not available at this time.'
        );
      }
    } catch (error) {
      console.error('Failed to fetch dashboard details:', error);
      const dashboard = dashboards.find(d => d.id === dashboardId);
      alert(`Failed to load dashboard details: ${error.message}\n\nDashboard: ${dashboard?.title || dashboardId}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-sm text-gray-600">Loading Grafana dashboards...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-50">
      {/* Header with connection status and controls */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">
              System Observability Dashboard
            </h1>
            
            <div className="flex items-center space-x-2">
              {connectionStatus === 'connected' && (
                <>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">Connected</span>
                </>
              )}
              {connectionStatus === 'disconnected' && (
                <>
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm text-yellow-600">Disconnected</span>
                </>
              )}
              {connectionStatus === 'error' && (
                <>
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-600">Error</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </span>
            
            <Button
              onClick={refreshDashboard}
              disabled={isRefreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>

            <Button
              onClick={() => window.open(`${GRAFANA_CONFIG.baseUrl}${selectedDashboard.url}`, '_blank')}
              variant="outline"
              size="sm"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open in Grafana
            </Button>
          </div>
        </div>

        {/* Active alerts banner */}
        {alerts.length > 0 && (
          <Alert className="mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Active Alerts ({alerts.length})</AlertTitle>
            <AlertDescription>
              <div className="mt-2 space-y-1">
                {alerts.slice(0, 3).map(alert => (
                  <div key={alert.id} className="flex items-center justify-between space-x-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getAlertColor(alert.severity)}>
                        {alert.severity.toUpperCase()}
                      </Badge>
                      <span className="text-sm">{alert.title}: {alert.message}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAlertDismiss(alert.id)}
                      className="text-xs px-2 py-1"
                    >
                      ✓ Dismiss
                    </Button>
                  </div>
                ))}
                {alerts.length > 3 && (
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-600">
                      and {alerts.length - 3} more alerts...
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleDismissAllAlerts}
                      className="text-xs px-2 py-1"
                    >
                      Dismiss All
                    </Button>
                  </div>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Dashboard tabs and content */}
      <div className="flex h-full">
        {/* Sidebar with dashboard list */}
        <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Dashboards</h2>
          
          <div className="space-y-2">
            {dashboards.map(dashboard => (
              <Card
                key={dashboard.id}
                className={`transition-colors ${
                  selectedDashboard.id === dashboard.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedDashboard(dashboard)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-sm text-gray-900 mb-1">
                        {dashboard.title}
                      </h3>
                      <p className="text-xs text-gray-600 mb-2">
                        {dashboard.description}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-1">
                          {dashboard.tags.slice(0, 2).map(tag => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(dashboard.status)}`} />
                          {dashboard.status !== 'healthy' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDashboardDetails(dashboard.id);
                              }}
                              className="text-xs px-1 py-0.5 h-auto"
                            >
                              🔍
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Main dashboard content */}
        <div className="flex-1 bg-gray-100">
          {connectionStatus === 'connected' ? (
            <iframe
              src={buildGrafanaUrl(selectedDashboard)}
              className="w-full h-full border-0"
              title={`Grafana Dashboard: ${selectedDashboard.title}`}
              allow="fullscreen"
              loading="lazy"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Cannot connect to Grafana
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  Please check your Grafana configuration and network connection.
                </p>
                <Button onClick={refreshDashboard} disabled={isRefreshing}>
                  <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Retry Connection
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmbeddedGrafana;