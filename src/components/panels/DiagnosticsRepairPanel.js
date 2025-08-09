import React, { useState, useEffect, useRef } from 'react';
import './DiagnosticsRepairPanel.css';
import '../ui-controls.css';

const DiagnosticsRepairPanel = ({ data, isExpanded, onExpand }) => {
  const [realtimeLatency, setRealtimeLatency] = useState(data.latency.current);
  const [heartbeatAnimation, setHeartbeatAnimation] = useState(0);
  const latencyCanvasRef = useRef(null);

  useEffect(() => {
    // Simulate real-time latency updates
    const interval = setInterval(() => {
      setRealtimeLatency(prev => {
        const change = (Math.random() - 0.5) * 10;
        return Math.max(20, Math.min(200, prev + change));
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Heartbeat animation
    const interval = setInterval(() => {
      setHeartbeatAnimation(prev => (prev + 1) % 60);
    }, 50);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (latencyCanvasRef.current && isExpanded) {
      drawLatencyChart();
    }
  }, [realtimeLatency, isExpanded]);

  const drawLatencyChart = () => {
    const canvas = latencyCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Clear canvas
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.1)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Generate sample data points
    const dataPoints = 50;
    const points = [];
    for (let i = 0; i < dataPoints; i++) {
      const x = (i / (dataPoints - 1)) * canvas.width;
      const latency = data.latency.floor + Math.sin(i * 0.2) * 20 + Math.random() * 15;
      const y = canvas.height - ((latency - data.latency.floor) / (data.latency.peak - data.latency.floor)) * canvas.height;
      points.push({ x, y, latency });
    }

    // Draw warning threshold
    const warningY = canvas.height - ((80 - data.latency.floor) / (data.latency.peak - data.latency.floor)) * canvas.height;
    ctx.strokeStyle = 'rgba(251, 191, 36, 0.5)';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, warningY);
    ctx.lineTo(canvas.width, warningY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw critical threshold
    const criticalY = canvas.height - ((100 - data.latency.floor) / (data.latency.peak - data.latency.floor)) * canvas.height;
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, criticalY);
    ctx.lineTo(canvas.width, criticalY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw latency line
    ctx.strokeStyle = '#22d3ee';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.stroke();

    // Draw area under curve
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, 'rgba(34, 211, 238, 0.3)');
    gradient.addColorStop(1, 'rgba(34, 211, 238, 0.05)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.lineTo(canvas.width, canvas.height);
    ctx.lineTo(0, canvas.height);
    ctx.closePath();
    ctx.fill();

    // Draw current latency indicator
    const currentX = canvas.width - 1;
    const currentY = canvas.height - ((realtimeLatency - data.latency.floor) / (data.latency.peak - data.latency.floor)) * canvas.height;
    ctx.fillStyle = '#fbbf24';
    ctx.beginPath();
    ctx.arc(currentX, currentY, 4, 0, 2 * Math.PI);
    ctx.fill();
  };

  const getUptimeDisplay = () => {
    const { days, hours, minutes } = data.uptime;
    return `${days}d ${hours}h ${minutes}m`;
  };

  const getHeartbeatColor = () => {
    switch (data.heartbeat) {
      case 'stable': return '#10b981';
      case 'degraded': return '#fbbf24';
      case 'failing': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getLatencyColor = (latency) => {
    if (latency > 100) return '#ef4444';
    if (latency > 80) return '#fbbf24';
    if (latency > 60) return '#22d3ee';
    return '#10b981';
  };

  const getTimeDelta = (timestamp) => {
    const delta = Date.now() - timestamp;
    const minutes = Math.floor(delta / 60000);
    const seconds = Math.floor((delta % 60000) / 1000);
    return minutes > 0 ? `${minutes}m ${seconds}s ago` : `${seconds}s ago`;
  };

  const getFailureIcon = (type) => {
    const icons = {
      timeout: '⏱️',
      null: '❌',
      overload: '🔥',
      recovery: '🔄'
    };
    return icons[type] || '⚠️';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      low: '#22d3ee',
      medium: '#fbbf24',
      high: '#ef4444',
      critical: '#dc2626',
      info: '#10b981'
    };
    return colors[severity] || '#6b7280';
  };

  // Handle system restart
  const handleSystemRestart = async () => {
    const confirmed = confirm(
      'CRITICAL ACTION: System Restart\n\n' +
      'This will restart the entire Hearthlink system, including all agents and services.\n' +
      'All active sessions will be terminated.\n\n' +
      'Are you sure you want to proceed?'
    );

    if (!confirmed) return;

    try {
      const response = await fetch('/api/core/restart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          restart_type: 'full_system',
          reason: 'manual_restart_via_diagnostics',
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        alert('System restart initiated successfully. The application will restart in 5 seconds.');
        
        // Show countdown
        let countdown = 5;
        const countdownInterval = setInterval(() => {
          if (countdown > 0) {
            document.title = `Restarting in ${countdown}s...`;
            countdown--;
          } else {
            clearInterval(countdownInterval);
            window.location.reload();
          }
        }, 1000);
      } else {
        throw new Error(`Restart failed with status ${response.status}`);
      }
    } catch (error) {
      alert(`Failed to restart system: ${error.message}`);
    }
  };

  // Handle maintenance mode toggle
  const handleMaintenanceMode = async () => {
    const isEntering = !window.maintenanceMode;
    const action = isEntering ? 'ENTER' : 'EXIT';
    
    const confirmed = confirm(
      `${action} MAINTENANCE MODE\n\n` +
      (isEntering 
        ? 'This will put the system in maintenance mode:\n• All user operations will be disabled\n• Only critical system functions will remain active\n• Diagnostic tools will remain available'
        : 'This will exit maintenance mode and return to normal operation.'
      ) +
      '\n\nProceed?'
    );

    if (!confirmed) return;

    try {
      const response = await fetch('/api/core/maintenance-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          enable: isEntering,
          reason: `manual_${isEntering ? 'enable' : 'disable'}_via_diagnostics`,
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        const result = await response.json();
        window.maintenanceMode = isEntering;
        
        alert(
          `Maintenance mode ${isEntering ? 'enabled' : 'disabled'} successfully.\n` +
          (result.message || 'System state updated.')
        );
        
        // Visual feedback
        document.body.classList.toggle('maintenance-mode', isEntering);
      } else {
        throw new Error(`Maintenance mode toggle failed with status ${response.status}`);
      }
    } catch (error) {
      alert(`Failed to toggle maintenance mode: ${error.message}`);
    }
  };

  // Handle failure resolution
  const handleFailureResolve = async (event, index) => {
    const confirmed = confirm(
      `Mark Failure as Resolved\n\n` +
      `Event: ${event.type.toUpperCase()}\n` +
      `Message: ${event.message}\n` +
      `Severity: ${event.severity.toUpperCase()}\n\n` +
      'This will mark the failure as resolved and add a resolution log entry.\n\n' +
      'Proceed?'
    );

    if (!confirmed) return;

    try {
      const response = await fetch(`/api/diagnostics/failures/${event.id || index}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          failure_id: event.id || `failure_${index}_${Date.now()}`,
          resolution_type: 'manual',
          resolved_by: 'user',
          resolution_notes: 'Manually resolved via Diagnostics Panel',
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update local state to remove resolved failure
        data.failureEvents = data.failureEvents.filter((_, i) => i !== index);
        
        // Add success repair operation
        data.selfRepairOps.unshift({
          timestamp: Date.now(),
          action: 'failure_resolution',
          details: `Resolved ${event.type} failure: ${event.message}`,
          success: true
        });

        alert(`Failure resolved successfully.\n${result.message || 'Resolution recorded in system logs.'}`);
        
        // Force re-render
        window.location.reload();
      } else {
        throw new Error(`Resolution failed with status ${response.status}`);
      }
    } catch (error) {
      alert(`Failed to resolve failure: ${error.message}`);
    }
  };

  if (isExpanded) {
    return (
      <div className="diagnostics-repair-panel expanded">
        <div className="panel-header">
          <h2>System Diagnostics & Repair</h2>
          <div className="panel-subtitle">Core health, runtime status, and operational self-repair</div>
        </div>

        <div className="diagnostics-expanded-content">
          <div className="uptime-heartbeat-section">
            <h3>System Uptime & Health</h3>
            <div className="uptime-display">
              <div className="uptime-clock">
                <div className="uptime-value">{getUptimeDisplay()}</div>
                <div className="uptime-label">System Uptime</div>
              </div>
              <div className="heartbeat-indicator expanded">
                <div 
                  className={`heartbeat-pulse ${data.heartbeat}`}
                  style={{
                    transform: `scale(${1 + Math.sin(heartbeatAnimation * 0.2) * 0.1})`,
                    filter: `brightness(${1 + Math.sin(heartbeatAnimation * 0.2) * 0.3})`
                  }}
                >
                  💓
                </div>
                <div className="heartbeat-status">
                  <span className="status-text">{data.heartbeat.toUpperCase()}</span>
                  <span className="status-bpm">72 BPM</span>
                </div>
              </div>
              <div className="system-actions">
                <button 
                  className="restart-button"
                  onClick={handleSystemRestart}
                  title="Restart the entire system"
                >
                  RESTART SYSTEM
                </button>
                <button 
                  className="maintenance-button"
                  onClick={handleMaintenanceMode}
                  title="Enter maintenance mode"
                >
                  MAINTENANCE MODE
                </button>
              </div>
            </div>
          </div>

          <div className="latency-performance-section">
            <h3>Performance Metrics</h3>
            <div className="latency-container">
              <canvas 
                ref={latencyCanvasRef} 
                className="latency-chart-canvas"
                width="400"
                height="200"
              />
              <div className="latency-stats">
                <div className="stat-item">
                  <span className="stat-label">Current:</span>
                  <span className="stat-value" style={{color: getLatencyColor(realtimeLatency)}}>
                    {Math.round(realtimeLatency)}ms
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Average:</span>
                  <span className="stat-value">{data.latency.average}ms</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Peak:</span>
                  <span className="stat-value">{data.latency.peak}ms</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Floor:</span>
                  <span className="stat-value">{data.latency.floor}ms</span>
                </div>
              </div>
            </div>
          </div>

          <div className="prompt-response-section">
            <h3>Prompt/Response Analysis</h3>
            <div className="prompt-response-stream expanded">
              {data.recentPrompts.map((prompt, index) => (
                <div key={prompt.id} className="prompt-response-item">
                  <div className="prompt-header">
                    <span className="prompt-timestamp">{getTimeDelta(prompt.timestamp)}</span>
                    <span className="prompt-tokens">
                      In: {prompt.tokens} | Out: {prompt.responseTokens}
                    </span>
                  </div>
                  <div className="prompt-content">
                    <div className="prompt-text">
                      <strong>Prompt:</strong> {prompt.content}
                    </div>
                    <div className="response-text">
                      <strong>Response:</strong> {prompt.response}
                    </div>
                  </div>
                  <div className="prompt-metrics">
                    <span className="processing-time">
                      Processing: {Math.round(Math.random() * 1000 + 200)}ms
                    </span>
                    <span className="token-rate">
                      Rate: {Math.round(prompt.responseTokens / ((Math.random() * 1000 + 200) / 1000))} tokens/s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="failure-events-section">
            <h3>Failure Events Timeline</h3>
            <div className="failure-timeline expanded">
              {data.failureEvents.map((event, index) => (
                <div key={index} className={`failure-event ${event.severity}`}>
                  <div className="event-icon">
                    {getFailureIcon(event.type)}
                  </div>
                  <div className="event-content">
                    <div className="event-header">
                      <span className="event-time">{getTimeDelta(event.timestamp)}</span>
                      <span className={`event-type ${event.type}`}>
                        {event.type.toUpperCase()}
                      </span>
                      <span className={`event-severity ${event.severity}`}>
                        {event.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="event-message">{event.message}</div>
                    <div className="event-actions">
                      <button 
                        className="resolve-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFailureResolve(event, index);
                        }}
                        title="Mark failure as resolved"
                      >
                        ✓ Resolve
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="self-repair-section">
            <h3>Self-Repair Operations</h3>
            <div className="repair-operations expanded">
              {data.selfRepairOps.map((op, index) => (
                <div key={index} className={`repair-operation ${op.success ? 'success' : 'failure'}`}>
                  <div className="repair-status">
                    <span className={`repair-indicator ${op.success ? 'success' : 'failure'}`}>
                      {op.success ? '✅' : '❌'}
                    </span>
                    <span className="repair-timestamp">{getTimeDelta(op.timestamp)}</span>
                  </div>
                  <div className="repair-content">
                    <div className="repair-action">{op.action.replace('_', ' ').toUpperCase()}</div>
                    <div className="repair-details">{op.details}</div>
                  </div>
                  <div className="repair-metrics">
                    <span className="repair-duration">
                      Duration: {Math.round(Math.random() * 5000 + 500)}ms
                    </span>
                    <span className="repair-impact">
                      Impact: {op.success ? 'Positive' : 'Failed'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="health-light-section">
            <h3>System Health Status</h3>
            <div className="health-light-container">
              <div className={`health-light ${data.heartbeat}`}>
                <div className="light-core"></div>
                <div className="light-glow"></div>
              </div>
              <div className="health-status-text">
                <div className="status-primary">
                  System Status: <span className={data.heartbeat}>{data.heartbeat.toUpperCase()}</span>
                </div>
                <div className="status-details">
                  {data.heartbeat === 'stable' && 'All systems operating within normal parameters'}
                  {data.heartbeat === 'degraded' && 'Some systems experiencing minor issues'}
                  {data.heartbeat === 'failing' && 'Critical systems require immediate attention'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="diagnostics-repair-panel compact" onClick={onExpand}>
      <div className="panel-header compact">
        <h3>Diagnostics & Repair</h3>
        <div className="expand-hint">Click to expand</div>
      </div>

      <div className="diagnostics-compact-content">
        <div className="compact-uptime">
          <div className="uptime-display compact">
            <div className="uptime-value">{getUptimeDisplay()}</div>
            <div 
              className={`heartbeat-pulse compact ${data.heartbeat}`}
              style={{
                transform: `scale(${1 + Math.sin(heartbeatAnimation * 0.2) * 0.05})`,
              }}
            >
              💓
            </div>
          </div>
        </div>

        <div className="compact-metrics">
          <div className="metric-row">
            <span className="metric-label">Latency:</span>
            <span 
              className="metric-value"
              style={{ color: getLatencyColor(realtimeLatency) }}
            >
              {Math.round(realtimeLatency)}ms
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Failures:</span>
            <span className="metric-value">{data.failureEvents.length}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Repairs:</span>
            <span className="metric-value">
              {data.selfRepairOps.filter(op => op.success).length}
            </span>
          </div>
        </div>

        <div className="compact-health-light">
          <div className={`health-indicator ${data.heartbeat}`}>
            <div className="indicator-dot"></div>
            <span className="indicator-text">{data.heartbeat.toUpperCase()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticsRepairPanel;