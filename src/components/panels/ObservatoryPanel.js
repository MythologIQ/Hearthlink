import React, { useState, useEffect, useRef } from 'react';
import './ObservatoryPanel.css';

const ObservatoryPanel = ({ data, isExpanded, onExpand }) => {
  const [anomalies, setAnomalies] = useState([
    { id: 'anom_001', timestamp: Date.now() - 300000, module: 'Core', severity: 'info', message: 'Memory optimization completed' },
    { id: 'anom_002', timestamp: Date.now() - 180000, module: 'Synapse', severity: 'warning', message: 'Rate limit threshold approached' },
    { id: 'anom_003', timestamp: Date.now() - 60000, module: 'Vault', severity: 'info', message: 'Backup created successfully' }
  ]);

  const [moduleSyncData, setModuleSyncData] = useState({
    alden: { lastSync: Date.now() - 30000, timeDelta: 2, status: 'healthy' },
    alice: { lastSync: Date.now() - 45000, timeDelta: 5, status: 'healthy' },
    core: { lastSync: Date.now() - 15000, timeDelta: 1, status: 'healthy' },
    synapse: { lastSync: Date.now() - 120000, timeDelta: 15, status: 'warning' },
    vault: { lastSync: Date.now() - 60000, timeDelta: 8, status: 'healthy' },
    sentry: { lastSync: Date.now() - 90000, timeDelta: 12, status: 'caution' },
    mimic: { lastSync: Date.now() - 300000, timeDelta: 45, status: 'offline' }
  });

  const [signalHealth, setSignalHealth] = useState({
    alden: { uptime: 99.8, latency: 45, queueDelay: 0 },
    alice: { uptime: 98.9, latency: 52, queueDelay: 2 },
    core: { uptime: 99.9, latency: 28, queueDelay: 0 },
    synapse: { uptime: 97.5, latency: 78, queueDelay: 5 },
    vault: { uptime: 99.2, latency: 35, queueDelay: 1 },
    sentry: { uptime: 96.8, latency: 65, queueDelay: 3 },
    mimic: { uptime: 85.4, latency: 120, queueDelay: 8 }
  });

  const [observationStream, setObservationStream] = useState([
    { id: 'obs_001', timestamp: Date.now() - 120000, type: 'pattern', message: 'Increased query complexity detected in Alden interactions' },
    { id: 'obs_002', timestamp: Date.now() - 200000, type: 'drift', message: 'Memory consolidation pattern shift in episodic storage' },
    { id: 'obs_003', timestamp: Date.now() - 350000, type: 'behavioral', message: 'User engagement duration trending upward' }
  ]);

  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current) {
      drawAgentGraph();
    }
  }, [data, isExpanded]);

  useEffect(() => {
    // Update observation stream every 30 seconds
    const interval = setInterval(() => {
      const newObservation = {
        id: `obs_${Date.now()}`,
        timestamp: Date.now(),
        type: ['pattern', 'drift', 'behavioral', 'performance'][Math.floor(Math.random() * 4)],
        message: generateObservationMessage()
      };
      setObservationStream(prev => [newObservation, ...prev.slice(0, 9)]);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const generateObservationMessage = () => {
    const messages = [
      'Agent communication frequency normalized',
      'Query processing efficiency improved',
      'Memory retrieval patterns optimized',
      'System load balancing adjusted',
      'Error recovery protocols activated',
      'Performance metrics within expected ranges'
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  };

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

  if (isExpanded) {
    return (
      <div className="observatory-panel expanded">
        <div className="panel-header">
          <h2>Observatory - Live Monitoring</h2>
          <div className="panel-subtitle">Real-time system telemetry and strategic insights</div>
        </div>

        <div className="observatory-expanded-content">
          <div className="expanded-section agent-graph-section">
            <h3>Live Agent Communication Graph</h3>
            <canvas 
              ref={canvasRef} 
              className="agent-graph-canvas expanded"
              width="400"
              height="300"
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
                  <div className="anomaly-message">{anomaly.message}</div>
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
              {observationStream.map(obs => (
                <div key={obs.id} className={`observation-item ${obs.type}`}>
                  <div className="observation-timestamp">{getTimeDelta(obs.timestamp)}</div>
                  <div className="observation-type">{obs.type.toUpperCase()}</div>
                  <div className="observation-message">{obs.message}</div>
                </div>
              ))}
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
            {observationStream.slice(0, 2).map(obs => (
              <div key={obs.id} className="ticker-item">
                <span className={`ticker-type ${obs.type}`}>{obs.type.toUpperCase()}:</span>
                <span className="ticker-message">{obs.message.substring(0, 40)}...</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ObservatoryPanel;