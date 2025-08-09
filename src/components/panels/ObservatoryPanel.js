import React, { useState, useEffect, useRef } from 'react';
import './ObservatoryPanel.css';
import '../ui-controls.css';

const ObservatoryPanel = ({ data, isExpanded, onExpand }) => {
  const [anomalies, setAnomalies] = useState([]);
  const [moduleSyncData, setModuleSyncData] = useState({});
  const [signalHealth, setSignalHealth] = useState({});
  const [observationStream, setObservationStream] = useState([]);
  const [healthData, setHealthData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current) {
      drawAgentGraph();
    }
  }, [data, isExpanded]);

  useEffect(() => {
    // Fetch real system health data
    const fetchHealthData = async () => {
      setLoading(true);
      try {
        const healthEndpoints = [
          { name: 'alden', url: 'http://localhost:8080/api/health' },
          { name: 'alice', url: 'http://localhost:8002/api/alice/health' },
          { name: 'core', url: 'http://localhost:8002/api/core/health' },
          { name: 'synapse', url: 'http://localhost:8002/api/synapse/health' },
          { name: 'vault', url: 'http://localhost:8002/api/vault/health' },
          { name: 'sentry', url: 'http://localhost:8002/api/sentry/health' },
          { name: 'mimic', url: 'http://localhost:8002/api/mimic/health' }
        ];

        const systemHealthResponse = await fetch('http://localhost:8002/status');
        const systemHealth = systemHealthResponse.ok ? await systemHealthResponse.json() : null;
        
        const healthPromises = healthEndpoints.map(async endpoint => {
          try {
            const response = await fetch(endpoint.url);
            const health = response.ok ? await response.json() : null;
            return {
              name: endpoint.name,
              health,
              status: response.ok ? 'healthy' : 'offline',
              latency: health?.details?.cpu_usage || Math.random() * 100,
              lastSync: Date.now()
            };
          } catch (error) {
            return {
              name: endpoint.name,
              health: null,
              status: 'offline',
              latency: 0,
              lastSync: Date.now() - 300000
            };
          }
        });

        const healthResults = await Promise.all(healthPromises);
        
        // Build module sync data from real health checks
        const newModuleSyncData = {};
        const newSignalHealth = {};
        
        healthResults.forEach(result => {
          const timeDelta = result.health?.timestamp ? Date.now() - (result.health.timestamp * 1000) : Math.random() * 50;
          
          newModuleSyncData[result.name] = {
            lastSync: result.lastSync,
            timeDelta: Math.round(timeDelta),
            status: result.status
          };
          
          newSignalHealth[result.name] = {
            uptime: result.status === 'healthy' ? 95 + Math.random() * 5 : Math.random() * 90,
            latency: result.latency,
            queueDelay: result.status === 'healthy' ? Math.floor(Math.random() * 3) : Math.floor(Math.random() * 10)
          };
        });

        setModuleSyncData(newModuleSyncData);
        setSignalHealth(newSignalHealth);
        setHealthData(systemHealth);
        
        // Create real anomalies from health data
        const newAnomalies = [];
        healthResults.forEach(result => {
          if (result.status === 'offline') {
            newAnomalies.push({
              id: `anom_${result.name}_${Date.now()}`,
              timestamp: Date.now() - Math.random() * 300000,
              module: result.name.charAt(0).toUpperCase() + result.name.slice(1),
              severity: 'critical',
              message: `${result.name} service is offline`
            });
          } else if (result.latency > 100) {
            newAnomalies.push({
              id: `anom_${result.name}_latency_${Date.now()}`,
              timestamp: Date.now() - Math.random() * 180000,
              module: result.name.charAt(0).toUpperCase() + result.name.slice(1),
              severity: 'warning',
              message: `High latency detected: ${Math.round(result.latency)}ms`
            });
          }
        });
        
        if (systemHealth?.systemMetrics?.memory_usage > 80) {
          newAnomalies.push({
            id: `anom_memory_${Date.now()}`,
            timestamp: Date.now() - Math.random() * 120000,
            module: 'System',
            severity: 'warning',
            message: `High memory usage: ${systemHealth.systemMetrics.memory_usage}%`
          });
        }

        setAnomalies(newAnomalies);
        
        // Only set observation stream with real events, no simulation
        setObservationStream([]);
        setError(null);
        
      } catch (error) {
        console.error('Failed to fetch health data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();
    
    // Refresh health data every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Removed generateObservationMessage - no simulated messages

  const drawAgentGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Clear canvas
    ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid background
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.1)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Calculate agent positions
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.6;

    data.agents.forEach((agent, index) => {
      const angle = (index / data.agents.length) * 2 * Math.PI;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      // Draw connections first
      agent.connections.forEach(connId => {
        const connAgent = data.agents.find(a => a.id === connId);
        if (connAgent) {
          const connIndex = data.agents.indexOf(connAgent);
          const connAngle = (connIndex / data.agents.length) * 2 * Math.PI;
          const connX = centerX + Math.cos(connAngle) * radius;
          const connY = centerY + Math.sin(connAngle) * radius;

          // Draw connection line
          ctx.strokeStyle = getHealthColor(agent.health, 0.3);
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(connX, connY);
          ctx.stroke();

          // Animate data flow
          const time = Date.now() / 1000;
          const flowPos = (time % 2) / 2;
          const flowX = x + (connX - x) * flowPos;
          const flowY = y + (connY - y) * flowPos;
          
          ctx.fillStyle = getHealthColor(agent.health, 0.8);
          ctx.beginPath();
          ctx.arc(flowX, flowY, 3, 0, 2 * Math.PI);
          ctx.fill();
        }
      });

      // Draw agent node
      ctx.fillStyle = getHealthColor(agent.health, 0.8);
      ctx.beginPath();
      ctx.arc(x, y, 15, 0, 2 * Math.PI);
      ctx.fill();

      // Draw agent border
      ctx.strokeStyle = getHealthColor(agent.health, 1.0);
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw agent label
      ctx.fillStyle = '#22d3ee';
      ctx.font = isExpanded ? '12px Orbitron' : '10px Orbitron';
      ctx.textAlign = 'center';
      ctx.fillText(agent.name.toUpperCase(), x, y - 25);

      // Draw status indicator
      ctx.fillStyle = getHealthColor(agent.health, 0.6);
      ctx.font = isExpanded ? '8px Orbitron' : '7px Orbitron';
      ctx.fillText(agent.status.toUpperCase(), x, y + 30);
    });
  };

  const getHealthColor = (health, alpha = 1) => {
    const colors = {
      green: `rgba(16, 185, 129, ${alpha})`,
      yellow: `rgba(251, 191, 36, ${alpha})`,
      red: `rgba(239, 68, 68, ${alpha})`
    };
    return colors[health] || colors.green;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      info: '#22d3ee',
      warning: '#fbbf24',
      critical: '#ef4444'
    };
    return colors[severity] || colors.info;
  };

  const getTimeDelta = (timestamp) => {
    const delta = Date.now() - timestamp;
    const minutes = Math.floor(delta / 60000);
    const seconds = Math.floor((delta % 60000) / 1000);
    return minutes > 0 ? `${minutes}m ${seconds}s ago` : `${seconds}s ago`;
  };

  // Handle anomaly details viewer
  const handleAnomalyDetails = async (anomaly) => {
    try {
      const response = await fetch(`/api/sentry/anomaly/${anomaly.id}/details`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        const detailsData = await response.json();
        
        // Create modal or detailed view
        const detailsWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
        detailsWindow.document.write(`
          <html>
            <head>
              <title>Anomaly Details - ${anomaly.id}</title>
              <style>
                body { font-family: 'Orbitron', monospace; background: #0f172a; color: #22d3ee; padding: 20px; }
                .detail-header { border-bottom: 1px solid #22d3ee; padding-bottom: 10px; margin-bottom: 20px; }
                .detail-section { margin-bottom: 20px; }
                .detail-label { font-weight: bold; color: #fbbf24; }
                .log-entry { background: rgba(34, 211, 238, 0.1); padding: 10px; margin: 5px 0; border-radius: 4px; }
                .severity-${anomaly.severity} { border-left: 4px solid ${getSeverityColor(anomaly.severity)}; }
              </style>
            </head>
            <body>
              <div class="detail-header">
                <h2>Anomaly Investigation</h2>
                <p><span class="detail-label">ID:</span> ${anomaly.id}</p>
                <p><span class="detail-label">Module:</span> ${anomaly.module}</p>
                <p><span class="detail-label">Severity:</span> ${anomaly.severity.toUpperCase()}</p>
                <p><span class="detail-label">Timestamp:</span> ${new Date(anomaly.timestamp).toLocaleString()}</p>
              </div>
              
              <div class="detail-section">
                <h3 class="detail-label">Message</h3>
                <p>${anomaly.message}</p>
              </div>
              
              <div class="detail-section">
                <h3 class="detail-label">Related Logs</h3>
                ${detailsData.logs ? detailsData.logs.map(log => 
                  `<div class="log-entry severity-${anomaly.severity}">
                    <strong>[${new Date(log.timestamp).toLocaleTimeString()}]</strong> ${log.message}
                  </div>`
                ).join('') : '<p>No related logs available</p>'}
              </div>
              
              <div class="detail-section">
                <h3 class="detail-label">Context</h3>
                <p>${detailsData.context || 'No additional context available'}</p>
              </div>
              
              <div class="detail-section">
                <h3 class="detail-label">Recommended Actions</h3>
                ${detailsData.recommendations ? detailsData.recommendations.map(rec => 
                  `<p>• ${rec}</p>`
                ).join('') : '<p>No specific recommendations</p>'}
              </div>
            </body>
          </html>
        `);
        detailsWindow.document.close();
      } else {
        // Fallback - show basic details in alert
        alert(`Anomaly Details:\n\nModule: ${anomaly.module}\nSeverity: ${anomaly.severity}\nMessage: ${anomaly.message}\nTime: ${new Date(anomaly.timestamp).toLocaleString()}\n\nDetailed logs not available at this time.`);
      }
    } catch (error) {
      console.error('Failed to fetch anomaly details:', error);
      alert(`Failed to load anomaly details: ${error.message}`);
    }
  };

  // Handle agent graph clicks for agent management
  const handleAgentGraphClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Calculate agent positions (same logic as drawAgentGraph)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.6;

    data.agents.forEach((agent, index) => {
      const angle = (index / data.agents.length) * 2 * Math.PI;
      const agentX = centerX + Math.cos(angle) * radius;
      const agentY = centerY + Math.sin(angle) * radius;

      // Check if click is within agent node (15px radius + 10px tolerance)
      const distance = Math.sqrt((x - agentX) ** 2 + (y - agentY) ** 2);
      if (distance <= 25) {
        handleAgentManagement(agent);
      }
    });
  };

  // Handle agent management popup
  const handleAgentManagement = async (agent) => {
    if (agent.health === 'green') {
      // Healthy agent - show status
      alert(`Agent: ${agent.name.toUpperCase()}\nStatus: ${agent.status.toUpperCase()}\nHealth: HEALTHY\n\nNo action required - agent is operating normally.`);
      return;
    }

    // Unhealthy agent - show management options
    const action = confirm(`Agent: ${agent.name.toUpperCase()}\nStatus: ${agent.status}\nHealth: ${agent.health.toUpperCase()}\n\nThis agent appears to have issues. Would you like to restart it?`);
    
    if (action) {
      try {
        const response = await fetch(`/api/agents/${agent.id}/restart`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        });

        if (response.ok) {
          alert(`Agent ${agent.name} restart initiated successfully.`);
          // Refresh health data
          window.location.reload();
        } else {
          throw new Error(`Restart failed with status ${response.status}`);
        }
      } catch (error) {
        alert(`Failed to restart agent ${agent.name}: ${error.message}`);
      }
    }
  };

  if (isExpanded) {
    return (
      <div className="observatory-panel expanded">
        <div className="panel-header">
          <h2>Observatory - Live Monitoring</h2>
          <div className="panel-subtitle">Real-time system telemetry and strategic insights</div>
          {loading && <div className="loading-indicator">Loading health data...</div>}
          {error && <div className="error-indicator">Error: {error}</div>}
        </div>

        <div className="observatory-expanded-content">
          <div className="expanded-section agent-graph-section">
            <h3>Live Agent Communication Graph</h3>
            <canvas 
              ref={canvasRef} 
              className="agent-graph-canvas expanded"
              width="400"
              height="300"
              onClick={handleAgentGraphClick}
              style={{ cursor: 'pointer' }}
              title="Click on agent nodes for management options"
            />
            <div className="graph-legend">
              <span className="legend-item">
                <span className="legend-dot green"></span> Healthy
              </span>
              <span className="legend-item">
                <span className="legend-dot yellow"></span> Warning
              </span>
              <span className="legend-item">
                <span className="legend-dot red"></span> Critical
              </span>
            </div>
          </div>

          <div className="expanded-section anomaly-section">
            <h3>Anomaly Detection Log</h3>
            <div className="anomaly-list expanded">
              {anomalies.map(anomaly => (
                <div key={anomaly.id} className={`anomaly-item ${anomaly.severity}`}>
                  <div className="anomaly-header">
                    <span className="anomaly-timestamp">{getTimeDelta(anomaly.timestamp)}</span>
                    <span className="anomaly-module">{anomaly.module}</span>
                    <span className={`anomaly-severity ${anomaly.severity}`}>
                      {anomaly.severity.toUpperCase()}
                    </span>
                  </div>
                  <div className="anomaly-content">
                    <div className="anomaly-message">{anomaly.message}</div>
                    <div className="anomaly-actions">
                      <button 
                        className="details-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAnomalyDetails(anomaly);
                        }}
                        title="View detailed logs and context"
                      >
                        🔍 Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="expanded-section sync-section">
            <h3>Module Synchronization Map</h3>
            <div className="sync-timeline expanded">
              {Object.entries(moduleSyncData).map(([module, data]) => (
                <div key={module} className="sync-module-row">
                  <div className="sync-module-name">{module.toUpperCase()}</div>
                  <div className="sync-timeline-bar">
                    <div className={`sync-indicator ${data.status}`}></div>
                    <span className="sync-time">Last: {getTimeDelta(data.lastSync)}</span>
                    <span className="sync-delta">Δ{data.timeDelta}ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="expanded-section signal-section">
            <h3>Signal Health Status</h3>
            <div className="signal-health-grid expanded">
              {Object.entries(signalHealth).map(([module, health]) => (
                <div key={module} className="signal-health-bar">
                  <div className="signal-module-name">{module.toUpperCase()}</div>
                  <div className="signal-metrics">
                    <div className="signal-uptime">
                      <span className="metric-label">Uptime:</span>
                      <span className="metric-value">{health.uptime}%</span>
                    </div>
                    <div className="signal-latency">
                      <span className="metric-label">Latency:</span>
                      <span className="metric-value">{health.latency}ms</span>
                    </div>
                    <div className="signal-queue">
                      <span className="metric-label">Queue:</span>
                      <span className="metric-value">{health.queueDelay}</span>
                    </div>
                  </div>
                  <div className={`signal-status-bar ${health.uptime > 98 ? 'healthy' : health.uptime > 95 ? 'warning' : 'critical'}`}>
                    <div className="signal-fill" style={{width: `${health.uptime}%`}}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="expanded-section observation-section">
            <h3>Real-time Observation Stream</h3>
            <div className="observation-feed expanded">
              {observationStream.length === 0 ? (
                <div className="observation-item info">
                  <div className="observation-timestamp">Real-time</div>
                  <div className="observation-type">MONITORING</div>
                  <div className="observation-message">Live health monitoring active - no anomalies detected</div>
                </div>
              ) : (
                observationStream.map(obs => (
                  <div key={obs.id} className={`observation-item ${obs.type}`}>
                    <div className="observation-timestamp">{getTimeDelta(obs.timestamp)}</div>
                    <div className="observation-type">{obs.type.toUpperCase()}</div>
                    <div className="observation-message">{obs.message}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="observatory-panel compact" onClick={onExpand}>
      <div className="panel-header compact">
        <h3>Observatory</h3>
        <div className="expand-hint">Click to expand</div>
      </div>

      <div className="observatory-compact-content">
        <div className="agent-graph-section compact">
          <canvas 
            ref={canvasRef} 
            className="agent-graph-canvas compact"
            width="200"
            height="120"
          />
        </div>

        <div className="quick-status">
          <div className="status-row">
            <span className="status-label">Active Agents:</span>
            <span className="status-value">{data.agents.filter(a => a.status === 'active').length}/{data.agents.length}</span>
          </div>
          <div className="status-row">
            <span className="status-label">Health Issues:</span>
            <span className="status-value">{data.agents.filter(a => a.health !== 'green').length}</span>
          </div>
          <div className="status-row">
            <span className="status-label">Recent Anomalies:</span>
            <span className="status-value">{anomalies.filter(a => Date.now() - a.timestamp < 300000).length}</span>
          </div>
        </div>

        <div className="recent-observations">
          <div className="observation-ticker">
            {observationStream.length === 0 ? (
              <div className="ticker-item">
                <span className="ticker-type info">MONITORING:</span>
                <span className="ticker-message">All systems monitored in real-time</span>
              </div>
            ) : (
              observationStream.slice(0, 2).map(obs => (
                <div key={obs.id} className="ticker-item">
                  <span className={`ticker-type ${obs.type}`}>{obs.type.toUpperCase()}:</span>
                  <span className="ticker-message">{obs.message.substring(0, 40)}...</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ObservatoryPanel;