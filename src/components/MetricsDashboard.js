/**
 * SPEC-2 Metrics Dashboard - Performance and Load Test Integration
 * 
 * Real-time dashboard for monitoring:
 * - Performance test results
 * - Load test metrics
 * - System health indicators
 * - SPEC-2 compliance status
 */

import React, { useState, useEffect, useRef } from 'react';
import './MetricsDashboard.css';

const MetricsDashboard = ({ isActive = true, refreshInterval = 10000 }) => {
  const [metricsData, setMetricsData] = useState({
    performanceTests: {
      smokeTests: null,
      loadTests: null,
      lastRun: null
    },
    systemHealth: {
      apiLatency: 0,
      memoryUsage: 0,
      activeConnections: 0,
      uptime: 0
    },
    spec2Compliance: {
      taskManagement: 'unknown',
      vaultIntegration: 'unknown',
      memoryDebug: 'unknown',
      auditLogging: 'unknown'
    },
    realTimeMetrics: {
      requestsPerSecond: 0,
      errorRate: 0,
      responseTime: 0
    }
  });

  const [selectedView, setSelectedView] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch metrics data
  const fetchMetrics = async () => {
    if (!isActive) return;

    setIsLoading(true);
    setError(null);

    try {
      // Fetch performance test results
      const [smokeResponse, loadResponse, healthResponse, complianceResponse] = await Promise.all([
        fetch('/api/metrics/smoke-tests', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }).catch(() => ({ ok: false })),
        fetch('/api/metrics/load-tests', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }).catch(() => ({ ok: false })),
        fetch('/api/metrics/system-health', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }).catch(() => ({ ok: false })),
        fetch('/api/metrics/spec2-compliance', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }).catch(() => ({ ok: false }))
      ]);

      const smokeData = smokeResponse.ok ? await smokeResponse.json() : null;
      const loadData = loadResponse.ok ? await loadResponse.json() : null;
      const healthData = healthResponse.ok ? await healthResponse.json() : {};
      const complianceData = complianceResponse.ok ? await complianceResponse.json() : {};

      setMetricsData(prev => ({
        ...prev,
        performanceTests: {
          smokeTests: smokeData,
          loadTests: loadData,
          lastRun: new Date().toISOString()
        },
        systemHealth: {
          apiLatency: healthData.apiLatency || 0,
          memoryUsage: healthData.memoryUsage || 0,
          activeConnections: healthData.activeConnections || 0,
          uptime: healthData.uptime || 0
        },
        spec2Compliance: {
          taskManagement: complianceData.taskManagement || 'unknown',
          vaultIntegration: complianceData.vaultIntegration || 'unknown',
          memoryDebug: complianceData.memoryDebug || 'unknown',
          auditLogging: complianceData.auditLogging || 'unknown'
        }
      }));

    } catch (err) {
      console.error('Failed to fetch metrics data:', err);
      setError('Failed to load metrics data');
    } finally {
      setIsLoading(false);
    }
  };

  // Setup WebSocket for real-time metrics
  const setupWebSocket = () => {
    if (!isActive || wsRef.current) return;

    try {
      const wsUrl = `ws://localhost:8002/ws/metrics`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Metrics WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          
          setMetricsData(prev => {
            const updated = { ...prev };
            
            if (update.type === 'real_time_metrics') {
              updated.realTimeMetrics = {
                ...updated.realTimeMetrics,
                ...update.data
              };
            } else if (update.type === 'system_health') {
              updated.systemHealth = {
                ...updated.systemHealth,
                ...update.data
              };
            } else if (update.type === 'test_completed') {
              if (update.testType === 'smoke') {
                updated.performanceTests.smokeTests = update.results;
              } else if (update.testType === 'load') {
                updated.performanceTests.loadTests = update.results;
              }
              updated.performanceTests.lastRun = new Date().toISOString();
            }
            
            return updated;
          });
        } catch (err) {
          console.error('Failed to process WebSocket message:', err);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Metrics WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('Metrics WebSocket disconnected');
        wsRef.current = null;
        
        if (isActive) {
          setTimeout(setupWebSocket, 5000);
        }
      };

    } catch (err) {
      console.error('Failed to setup WebSocket:', err);
    }
  };

  // Setup polling and WebSocket
  useEffect(() => {
    if (!isActive) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    fetchMetrics();
    setupWebSocket();

    if (autoRefresh) {
      intervalRef.current = setInterval(fetchMetrics, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isActive, autoRefresh, refreshInterval]);

  // Run performance tests
  const runSmokeTests = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/metrics/run-smoke-tests', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const results = await response.json();
        setMetricsData(prev => ({
          ...prev,
          performanceTests: {
            ...prev.performanceTests,
            smokeTests: results,
            lastRun: new Date().toISOString()
          }
        }));
      }
    } catch (err) {
      setError('Failed to run smoke tests');
    } finally {
      setIsLoading(false);
    }
  };

  const runLoadTests = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/metrics/run-load-tests', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          testProfile: 'standard',
          duration: 60
        })
      });
      
      if (response.ok) {
        const results = await response.json();
        setMetricsData(prev => ({
          ...prev,
          performanceTests: {
            ...prev.performanceTests,
            loadTests: results,
            lastRun: new Date().toISOString()
          }
        }));
      }
    } catch (err) {
      setError('Failed to run load tests');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions
  const formatLatency = (ms) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatMemory = (bytes) => {
    if (!bytes) return '0 MB';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const formatUptime = (seconds) => {
    if (!seconds) return '0s';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': 
      case 'healthy':
      case 'active':
        return 'status-good';
      case 'warning':
      case 'degraded':
        return 'status-warning';
      case 'failed':
      case 'error':
      case 'inactive':
        return 'status-error';
      default:
        return 'status-unknown';
    }
  };

  const getPerformanceGrade = (smokeTests, loadTests) => {
    if (!smokeTests && !loadTests) return 'N/A';
    
    const smokeGrade = smokeTests?.status === 'PASSED' ? 'A' : 'F';
    const loadGrade = loadTests?.overall_metrics?.performance_grade || 'N/A';
    
    if (smokeGrade === 'F') return 'F';
    if (loadGrade === 'F') return 'F';
    if (loadGrade === 'A' && smokeGrade === 'A') return 'A';
    if (loadGrade === 'B' || smokeGrade === 'A') return 'B';
    return 'C';
  };

  if (!isActive) {
    return (
      <div className="metrics-dashboard inactive">
        <div className="inactive-message">
          Metrics Dashboard - Inactive
        </div>
      </div>
    );
  }

  const { performanceTests, systemHealth, spec2Compliance, realTimeMetrics } = metricsData;
  const overallGrade = getPerformanceGrade(performanceTests.smokeTests, performanceTests.loadTests);

  return (
    <div className="metrics-dashboard">
      <div className="dashboard-header">
        <div className="title-section">
          <h3>📊 SPEC-2 Metrics Dashboard</h3>
          <div className="last-updated">
            Last Updated: {performanceTests.lastRun ? new Date(performanceTests.lastRun).toLocaleTimeString() : 'Never'}
          </div>
        </div>
        
        <div className="controls">
          <button
            className={`run-test-btn ${isLoading ? 'loading' : ''}`}
            onClick={runSmokeTests}
            disabled={isLoading}
          >
            {isLoading ? '🔄' : '🔍'} Run Smoke Tests
          </button>
          
          <button
            className={`run-test-btn ${isLoading ? 'loading' : ''}`}
            onClick={runLoadTests}
            disabled={isLoading}
          >
            {isLoading ? '🔄' : '⚡'} Run Load Tests
          </button>
          
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto Refresh
          </label>
        </div>
      </div>

      <div className="view-tabs">
        {['overview', 'performance', 'health', 'compliance'].map(view => (
          <button
            key={view}
            className={`tab ${selectedView === view ? 'active' : ''}`}
            onClick={() => setSelectedView(view)}
          >
            {view.charAt(0).toUpperCase() + view.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="dashboard-content">
        {selectedView === 'overview' && (
          <div className="overview-view">
            <div className="overview-cards">
              <div className="metric-card performance">
                <div className="card-icon">⚡</div>
                <div className="card-content">
                  <div className="card-value">{overallGrade}</div>
                  <div className="card-label">Performance Grade</div>
                </div>
              </div>
              
              <div className="metric-card health">
                <div className="card-icon">💚</div>
                <div className="card-content">
                  <div className="card-value">{formatLatency(systemHealth.apiLatency)}</div>
                  <div className="card-label">API Latency</div>
                </div>
              </div>
              
              <div className="metric-card realtime">
                <div className="card-icon">🔄</div>
                <div className="card-content">
                  <div className="card-value">{realTimeMetrics.requestsPerSecond.toFixed(1)}</div>
                  <div className="card-label">Requests/sec</div>
                </div>
              </div>
              
              <div className="metric-card memory">
                <div className="card-icon">🧠</div>
                <div className="card-content">
                  <div className="card-value">{formatMemory(systemHealth.memoryUsage)}</div>
                  <div className="card-label">Memory Usage</div>
                </div>
              </div>
            </div>

            <div className="quick-status">
              <h4>SPEC-2 Component Status</h4>
              <div className="status-grid">
                <div className={`status-item ${getStatusColor(spec2Compliance.taskManagement)}`}>
                  <span className="status-label">Task Management</span>
                  <span className="status-value">{spec2Compliance.taskManagement}</span>
                </div>
                <div className={`status-item ${getStatusColor(spec2Compliance.vaultIntegration)}`}>
                  <span className="status-label">Vault Integration</span>
                  <span className="status-value">{spec2Compliance.vaultIntegration}</span>
                </div>
                <div className={`status-item ${getStatusColor(spec2Compliance.memoryDebug)}`}>
                  <span className="status-label">Memory Debug</span>
                  <span className="status-value">{spec2Compliance.memoryDebug}</span>
                </div>
                <div className={`status-item ${getStatusColor(spec2Compliance.auditLogging)}`}>
                  <span className="status-label">Audit Logging</span>
                  <span className="status-value">{spec2Compliance.auditLogging}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedView === 'performance' && (
          <div className="performance-view">
            <div className="test-results">
              <div className="test-section">
                <h4>Smoke Test Results</h4>
                {performanceTests.smokeTests ? (
                  <div className="test-summary">
                    <div className={`test-status ${performanceTests.smokeTests.status === 'PASSED' ? 'passed' : 'failed'}`}>
                      {performanceTests.smokeTests.status}
                    </div>
                    <div className="test-details">
                      <span>Success Rate: {(performanceTests.smokeTests.overall_success_rate * 100).toFixed(1)}%</span>
                      <span>Total Tests: {performanceTests.smokeTests.total_tests}</span>
                      <span>Execution Time: {performanceTests.smokeTests.execution_time_seconds.toFixed(1)}s</span>
                    </div>
                  </div>
                ) : (
                  <div className="no-data">No smoke test data available</div>
                )}
              </div>

              <div className="test-section">
                <h4>Load Test Results</h4>
                {performanceTests.loadTests ? (
                  <div className="test-summary">
                    <div className={`test-status grade-${performanceTests.loadTests.overall_metrics.performance_grade.toLowerCase()}`}>
                      Grade {performanceTests.loadTests.overall_metrics.performance_grade}
                    </div>
                    <div className="test-details">
                      <span>Total Requests: {performanceTests.loadTests.overall_metrics.total_requests}</span>
                      <span>Success Rate: {(performanceTests.loadTests.overall_metrics.overall_success_rate * 100).toFixed(1)}%</span>
                      <span>Avg Latency: {performanceTests.loadTests.overall_metrics.average_latency_ms.toFixed(1)}ms</span>
                    </div>
                  </div>
                ) : (
                  <div className="no-data">No load test data available</div>
                )}
              </div>
            </div>

            <div className="real-time-metrics">
              <h4>Real-Time Performance</h4>
              <div className="metrics-grid">
                <div className="metric-item">
                  <label>Requests/Second:</label>
                  <span>{realTimeMetrics.requestsPerSecond.toFixed(2)}</span>
                </div>
                <div className="metric-item">
                  <label>Error Rate:</label>
                  <span className={realTimeMetrics.errorRate > 0.05 ? 'high-error' : ''}>{(realTimeMetrics.errorRate * 100).toFixed(2)}%</span>
                </div>
                <div className="metric-item">
                  <label>Response Time:</label>
                  <span>{formatLatency(realTimeMetrics.responseTime)}</span>
                </div>
                <div className="metric-item">
                  <label>Active Connections:</label>
                  <span>{systemHealth.activeConnections}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedView === 'health' && (
          <div className="health-view">
            <div className="health-metrics">
              <h4>System Health</h4>
              <div className="health-grid">
                <div className="health-item">
                  <label>API Latency:</label>
                  <span className={systemHealth.apiLatency > 1000 ? 'high-latency' : ''}>{formatLatency(systemHealth.apiLatency)}</span>
                </div>
                <div className="health-item">
                  <label>Memory Usage:</label>
                  <span className={systemHealth.memoryUsage > 512 * 1024 * 1024 ? 'high-memory' : ''}>{formatMemory(systemHealth.memoryUsage)}</span>
                </div>
                <div className="health-item">
                  <label>Uptime:</label>
                  <span>{formatUptime(systemHealth.uptime)}</span>
                </div>
                <div className="health-item">
                  <label>Active Connections:</label>
                  <span>{systemHealth.activeConnections}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedView === 'compliance' && (
          <div className="compliance-view">
            <div className="compliance-status">
              <h4>SPEC-2 Compliance Status</h4>
              <div className="compliance-details">
                {Object.entries(spec2Compliance).map(([component, status]) => (
                  <div key={component} className={`compliance-item ${getStatusColor(status)}`}>
                    <div className="component-name">{component.replace(/([A-Z])/g, ' $1').trim()}</div>
                    <div className="component-status">{status}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricsDashboard;