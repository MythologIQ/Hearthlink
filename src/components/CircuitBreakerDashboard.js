import React, { useState, useEffect } from 'react';
import './CircuitBreakerDashboard.css';

/**
 * Circuit Breaker Monitoring and Alerting Dashboard
 * 
 * Provides real-time monitoring of all circuit breaker protected services
 * with comprehensive metrics, alerting, and manual intervention capabilities.
 */

const CircuitBreakerDashboard = ({ isVisible, onClose }) => {
  // Circuit breaker monitoring state
  const [circuitBreakers, setCircuitBreakers] = useState({});
  const [globalMetrics, setGlobalMetrics] = useState({
    totalServices: 0,
    healthyServices: 0,
    failingServices: 0,
    openCircuits: 0,
    halfOpenCircuits: 0,
    totalRequests: 0,
    successRate: 0,
    averageResponseTime: 0
  });
  const [alerts, setAlerts] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [timeRange, setTimeRange] = useState('1h'); // 1h, 6h, 24h, 7d
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [emergencyMode, setEmergencyMode] = useState(false);

  // Monitored services with circuit breaker protection
  const monitoredServices = {
    'local-llm': {
      name: 'Local LLM API',
      endpoint: 'http://localhost:8001',
      priority: 'high',
      description: 'Local Language Model API service'
    },
    'superclaude': {
      name: 'SuperClaude API',
      endpoint: 'http://localhost:8005',
      priority: 'medium',
      description: 'SuperClaude integration service'
    },
    'external-agent': {
      name: 'External Agent API',
      endpoint: 'http://localhost:8006',
      priority: 'medium',
      description: 'External agent communication service'
    },
    'core-api': {
      name: 'Core API',
      endpoint: 'http://localhost:8000',
      priority: 'high',
      description: 'Core orchestration service'
    },
    'vault-api': {
      name: 'Vault API',
      endpoint: 'http://localhost:8002',
      priority: 'high',
      description: 'Memory and data storage service'
    },
    'synapse-api': {
      name: 'Synapse API',
      endpoint: 'http://localhost:8003',
      priority: 'medium',
      description: 'Plugin management service'
    },
    'sentry-api': {
      name: 'Sentry API',
      endpoint: 'http://localhost:8004',
      priority: 'low',
      description: 'Security monitoring service'
    }
  };

  useEffect(() => {
    if (isVisible && autoRefresh) {
      loadCircuitBreakerData();
      const interval = setInterval(loadCircuitBreakerData, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isVisible, autoRefresh, timeRange]);

  const loadCircuitBreakerData = async () => {
    try {
      // Load circuit breaker status for each service
      const circuitData = {};
      let totalRequests = 0;
      let successfulRequests = 0;
      let healthyCount = 0;
      let failingCount = 0;
      let openCount = 0;
      let halfOpenCount = 0;

      for (const [serviceId, service] of Object.entries(monitoredServices)) {
        try {
          const response = await fetch(`${service.endpoint}/api/circuit-breaker/status`, {
            timeout: 3000
          });
          
          if (response.ok) {
            const data = await response.json();
            circuitData[serviceId] = {
              ...service,
              ...data,
              lastUpdated: new Date(),
              healthStatus: data.state === 'CLOSED' ? 'healthy' : 
                           data.state === 'OPEN' ? 'failing' : 'recovering'
            };

            totalRequests += data.metrics?.totalRequests || 0;
            successfulRequests += data.metrics?.successfulRequests || 0;

            if (data.state === 'CLOSED') healthyCount++;
            else if (data.state === 'OPEN') { failingCount++; openCount++; }
            else if (data.state === 'HALF_OPEN') { failingCount++; halfOpenCount++; }

          } else {
            throw new Error(`HTTP ${response.status}`);
          }
        } catch (error) {
          // Circuit breaker not available or service down
          circuitData[serviceId] = {
            ...service,
            state: 'UNKNOWN',
            healthStatus: 'unknown',
            error: error.message,
            lastUpdated: new Date(),
            metrics: {
              totalRequests: 0,
              successfulRequests: 0,
              failureCount: 0,
              successRate: 0
            }
          };
          failingCount++;
        }
      }

      setCircuitBreakers(circuitData);
      setGlobalMetrics({
        totalServices: Object.keys(monitoredServices).length,
        healthyServices: healthyCount,
        failingServices: failingCount,
        openCircuits: openCount,
        halfOpenCircuits: halfOpenCount,
        totalRequests,
        successRate: totalRequests > 0 ? (successfulRequests / totalRequests) * 100 : 0,
        averageResponseTime: calculateAverageResponseTime(circuitData)
      });

      // Generate alerts for circuit breaker state changes
      checkForAlerts(circuitData);

    } catch (error) {
      console.error('Failed to load circuit breaker data:', error);
    }
  };

  const calculateAverageResponseTime = (circuitData) => {
    const responseTimes = Object.values(circuitData)
      .filter(cb => cb.metrics?.averageResponseTime)
      .map(cb => cb.metrics.averageResponseTime);
    
    return responseTimes.length > 0 
      ? responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length
      : 0;
  };

  const checkForAlerts = (circuitData) => {
    const newAlerts = [];
    const now = new Date();

    Object.entries(circuitData).forEach(([serviceId, cb]) => {
      // High priority service circuit open
      if (cb.state === 'OPEN' && cb.priority === 'high') {
        newAlerts.push({
          id: `${serviceId}-open-${now.getTime()}`,
          severity: 'critical',
          service: cb.name,
          message: `High priority service circuit breaker is OPEN`,
          timestamp: now,
          type: 'circuit_open'
        });
      }

      // High failure rate
      if (cb.metrics?.successRate < 50 && cb.metrics?.totalRequests > 10) {
        newAlerts.push({
          id: `${serviceId}-failures-${now.getTime()}`,
          severity: 'warning',
          service: cb.name,
          message: `Service experiencing high failure rate: ${cb.metrics.successRate.toFixed(1)}%`,
          timestamp: now,
          type: 'high_failure_rate'
        });
      }

      // Slow response times
      if (cb.metrics?.averageResponseTime > 5000) {
        newAlerts.push({
          id: `${serviceId}-slow-${now.getTime()}`,
          severity: 'warning',
          service: cb.name,
          message: `Service response time is slow: ${cb.metrics.averageResponseTime}ms`,
          timestamp: now,
          type: 'slow_response'
        });
      }
    });

    if (newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 50)); // Keep last 50 alerts
    }
  };

  const manualCircuitAction = async (serviceId, action) => {
    try {
      const service = monitoredServices[serviceId];
      const response = await fetch(`${service.endpoint}/api/circuit-breaker/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        setAlerts(prev => [{
          id: `manual-${serviceId}-${Date.now()}`,
          severity: 'info',
          service: circuitBreakers[serviceId]?.name || serviceId,
          message: `Manual circuit breaker ${action} executed successfully`,
          timestamp: new Date(),
          type: 'manual_action'
        }, ...prev]);
        
        // Refresh data
        setTimeout(loadCircuitBreakerData, 1000);
      } else {
        throw new Error(`Failed to ${action} circuit breaker`);
      }
    } catch (error) {
      setAlerts(prev => [{
        id: `error-${serviceId}-${Date.now()}`,
        severity: 'error',
        service: circuitBreakers[serviceId]?.name || serviceId,
        message: `Failed to ${action} circuit breaker: ${error.message}`,
        timestamp: new Date(),
        type: 'error'
      }, ...prev]);
    }
  };

  const emergencyStopAll = async () => {
    if (!window.confirm('Are you sure you want to open ALL circuit breakers? This will stop all external service communication.')) {
      return;
    }

    setEmergencyMode(true);
    const promises = Object.keys(monitoredServices).map(serviceId =>
      manualCircuitAction(serviceId, 'open').catch(console.error)
    );
    
    await Promise.all(promises);
    setTimeout(() => setEmergencyMode(false), 5000);
  };

  const getServiceStatusColor = (healthStatus) => {
    switch (healthStatus) {
      case 'healthy': return '#10b981';
      case 'failing': return '#ef4444';
      case 'recovering': return '#f59e0b';
      case 'unknown': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'warning': return '#d97706';
      case 'info': return '#2563eb';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  };

  if (!isVisible) return null;

  return (
    <div className="circuit-breaker-dashboard">
      <div className="dashboard-header">
        <div className="header-title">
          <h2>🔄 Circuit Breaker Monitoring</h2>
          <div className="header-controls">
            <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
            </select>
            
            <label className="auto-refresh">
              <input 
                type="checkbox" 
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto Refresh
            </label>

            <button 
              onClick={emergencyStopAll}
              className="emergency-btn"
              disabled={emergencyMode}
            >
              🚨 Emergency Stop All
            </button>

            <button onClick={onClose} className="close-btn">✕</button>
          </div>
        </div>
      </div>

      <div className="dashboard-body">
        {/* Global Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">📊</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.totalServices}</div>
              <div className="metric-label">Total Services</div>
            </div>
          </div>

          <div className="metric-card healthy">
            <div className="metric-icon">✅</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.healthyServices}</div>
              <div className="metric-label">Healthy Services</div>
            </div>
          </div>

          <div className="metric-card failing">
            <div className="metric-icon">❌</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.failingServices}</div>
              <div className="metric-label">Failing Services</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🔥</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.openCircuits}</div>
              <div className="metric-label">Open Circuits</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🔄</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.halfOpenCircuits}</div>
              <div className="metric-label">Half-Open Circuits</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <div className="metric-value">{globalMetrics.successRate.toFixed(1)}%</div>
              <div className="metric-label">Success Rate</div>
            </div>
          </div>
        </div>

        <div className="dashboard-content">
          {/* Service Status Grid */}
          <div className="services-section">
            <h3>🔧 Service Circuit Breakers</h3>
            <div className="services-grid">
              {Object.entries(circuitBreakers).map(([serviceId, cb]) => (
                <div 
                  key={serviceId} 
                  className={`service-card ${cb.healthStatus} ${selectedService === serviceId ? 'selected' : ''}`}
                  onClick={() => setSelectedService(selectedService === serviceId ? null : serviceId)}
                >
                  <div className="service-header">
                    <div className="service-name">{cb.name}</div>
                    <div 
                      className="service-status"
                      style={{ backgroundColor: getServiceStatusColor(cb.healthStatus) }}
                    >
                      {cb.state || 'UNKNOWN'}
                    </div>
                  </div>
                  
                  <div className="service-metrics">
                    <div className="metric-row">
                      <span>Requests:</span>
                      <span>{cb.metrics?.totalRequests || 0}</span>
                    </div>
                    <div className="metric-row">
                      <span>Success Rate:</span>
                      <span>{cb.metrics?.successRate?.toFixed(1) || 0}%</span>
                    </div>
                    <div className="metric-row">
                      <span>Failures:</span>
                      <span>{cb.metrics?.failureCount || 0}</span>
                    </div>
                    <div className="metric-row">
                      <span>Avg Response:</span>
                      <span>{cb.metrics?.averageResponseTime || 0}ms</span>
                    </div>
                  </div>

                  {cb.error && (
                    <div className="service-error">
                      Error: {cb.error}
                    </div>
                  )}

                  <div className="service-actions">
                    {cb.state === 'OPEN' && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          manualCircuitAction(serviceId, 'half-open');
                        }}
                        className="action-btn warning"
                      >
                        Try Half-Open
                      </button>
                    )}
                    
                    {cb.state === 'CLOSED' && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          manualCircuitAction(serviceId, 'open');
                        }}
                        className="action-btn danger"
                      >
                        Force Open
                      </button>
                    )}
                    
                    {(cb.state === 'HALF_OPEN' || cb.state === 'OPEN') && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          manualCircuitAction(serviceId, 'reset');
                        }}
                        className="action-btn success"
                      >
                        Reset
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Alerts Section */}
          <div className="alerts-section">
            <h3>🚨 Alerts & Events</h3>
            <div className="alerts-container">
              {alerts.length === 0 ? (
                <div className="no-alerts">No alerts in the selected time range</div>
              ) : (
                <div className="alerts-list">
                  {alerts.slice(0, 20).map(alert => (
                    <div 
                      key={alert.id}
                      className="alert-item"
                      style={{ borderLeftColor: getSeverityColor(alert.severity) }}
                    >
                      <div className="alert-header">
                        <span 
                          className="alert-severity"
                          style={{ backgroundColor: getSeverityColor(alert.severity) }}
                        >
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="alert-service">{alert.service}</span>
                        <span className="alert-time">
                          {alert.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="alert-message">{alert.message}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Detailed Service View */}
          {selectedService && circuitBreakers[selectedService] && (
            <div className="service-details">
              <h3>📋 Service Details: {circuitBreakers[selectedService].name}</h3>
              <div className="details-grid">
                <div className="detail-section">
                  <h4>Configuration</h4>
                  <div className="detail-item">
                    <span>Endpoint:</span>
                    <span>{circuitBreakers[selectedService].endpoint}</span>
                  </div>
                  <div className="detail-item">
                    <span>Priority:</span>
                    <span>{circuitBreakers[selectedService].priority}</span>
                  </div>
                  <div className="detail-item">
                    <span>Description:</span>
                    <span>{circuitBreakers[selectedService].description}</span>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Current Status</h4>
                  <div className="detail-item">
                    <span>Circuit State:</span>
                    <span>{circuitBreakers[selectedService].state}</span>
                  </div>
                  <div className="detail-item">
                    <span>Health Status:</span>
                    <span>{circuitBreakers[selectedService].healthStatus}</span>
                  </div>
                  <div className="detail-item">
                    <span>Last Updated:</span>
                    <span>{circuitBreakers[selectedService].lastUpdated?.toLocaleString()}</span>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Metrics</h4>
                  <div className="detail-item">
                    <span>Total Requests:</span>
                    <span>{circuitBreakers[selectedService].metrics?.totalRequests || 0}</span>
                  </div>
                  <div className="detail-item">
                    <span>Successful:</span>
                    <span>{circuitBreakers[selectedService].metrics?.successfulRequests || 0}</span>
                  </div>
                  <div className="detail-item">
                    <span>Failed:</span>
                    <span>{circuitBreakers[selectedService].metrics?.failureCount || 0}</span>
                  </div>
                  <div className="detail-item">
                    <span>Success Rate:</span>
                    <span>{circuitBreakers[selectedService].metrics?.successRate?.toFixed(2) || 0}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CircuitBreakerDashboard;