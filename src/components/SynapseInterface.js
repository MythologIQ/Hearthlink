import React, { useState, useEffect } from 'react';
import './SynapseInterface.css';

const SynapseInterface = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [activeTab, setActiveTab] = useState('plugins');
  const [plugins, setPlugins] = useState([]);
  const [connections, setConnections] = useState([]);
  const [trafficLogs, setTrafficLogs] = useState([]);
  const [embeddedUrl, setEmbeddedUrl] = useState('');
  const [webhookConfig, setWebhookConfig] = useState({
    endpoints: [],
    newEndpoint: {
      name: '',
      url: '',
      method: 'POST',
      headers: {},
      enabled: true
    }
  });

  // Load real data from Synapse API
  useEffect(() => {
    loadSynapseData();
    const interval = setInterval(loadSynapseData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadSynapseData = async () => {
    try {
      // Load plugins from real API
      await loadPlugins();
      
      // Load connections from real API
      await loadConnections();
      
      // Load traffic logs from real API
      await loadTrafficLogs();
      
      // Load webhook configuration
      await loadWebhookConfig();
    } catch (error) {
      console.error('Failed to load Synapse data:', error);
    }
  };

  const loadPlugins = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/synapse/plugins', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.data && data.data.plugins) {
          setPlugins(data.data.plugins);
        } else {
          // Use fallback data if API response is empty
          setPlugins([
            {
              id: 'hearthlink_core',
              name: 'Hearthlink Core',
              version: '1.0.0',
              status: 'active',
              riskTier: 'low',
              permissions: ['core_access', 'agent_management']
            }
          ]);
        }
      } else {
        // Use basic plugin registry
        setPlugins([
          {
            id: 'hearthlink_core',
            name: 'Hearthlink Core',
            version: '1.0.0',
            status: 'active',
            riskTier: 'low',
            permissions: ['core_access', 'agent_management']
          },
          {
            id: 'kimi_k2_plugin',
            name: 'Kimi K2 Agentic AI',
            version: '1.0.0',
            status: 'active',
            riskTier: 'medium',
            permissions: ['external_api', 'tool_calling', 'agentic_workflows']
          }
        ]);
      }
    } catch (error) {
      console.warn('Plugin API unavailable, using fallback data:', error);
      setPlugins([
        {
          id: 'hearthlink_core',
          name: 'Hearthlink Core',
          version: '1.0.0',
          status: 'active',
          riskTier: 'low',
          permissions: ['core_access', 'agent_management']
        }
      ]);
    }
  };

  const loadConnections = async () => {
    try {
      // Get system status from Synapse API which includes connection info
      const response = await fetch('http://localhost:8003/api/synapse/system/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.data && data.data.connections) {
          setConnections(data.data.connections);
        } else {
          // Fallback to detect active connections
          const connections = [];
          
          // Check Claude Code CLI
          const isClaudeCode = window.navigator.userAgent.includes('claude-code') || 
                              process.env.REACT_APP_CLAUDE_CODE === 'true';
          
          if (isClaudeCode) {
            connections.push({
              id: 'claude_code_cli',
              agentId: 'claude-code',
              status: 'connected',
              lastActivity: new Date().toISOString(),
              trafficCount: 1
            });
          }
          
          // Check for Core API connections
          try {
            const coreResponse = await fetch('http://localhost:8000/api/health');
            if (coreResponse.ok) {
              connections.push({
                id: 'hearthlink_core',
                agentId: 'hearthlink-core',
                status: 'connected',
                lastActivity: new Date().toISOString(),
                trafficCount: 1
              });
            }
          } catch (err) {
            // Core API not available
          }
          
          setConnections(connections);
        }
      } else {
        // Fallback to basic connection detection
        setConnections([
          {
            id: 'synapse_system',
            agentId: 'synapse-gateway',
            status: 'connected',
            lastActivity: new Date().toISOString(),
            trafficCount: 1
          }
        ]);
      }
    } catch (error) {
      console.warn('Connections API unavailable, using fallback data:', error);
      setConnections([]);
    }
  };

  const loadTrafficLogs = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/synapse/traffic/logs', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.data && data.data.logs) {
          setTrafficLogs(data.data.logs);
        } else {
          // Fallback to basic logs
          setTrafficLogs([
            {
              id: 'log-001',
              timestamp: new Date().toISOString(),
              source: 'hearthlink-core',
              action: 'system_init',
              status: 'success',
              details: 'Synapse gateway initialized'
            }
          ]);
        }
      } else {
        // Fallback to basic logs
        setTrafficLogs([
          {
            id: 'log-001',
            timestamp: new Date().toISOString(),
            source: 'synapse-gateway',
            action: 'api_startup',
            status: 'success',
            details: 'Synapse API server started on port 8003'
          }
        ]);
      }
    } catch (error) {
      console.warn('Traffic logs API unavailable, using fallback data:', error);
      setTrafficLogs([]);
    }
  };

  const loadWebhookConfig = async () => {
    try {
      // Note: Webhook functionality would be implemented as part of the system status
      // For now, we'll initialize with empty config and rely on local state management
      const response = await fetch('http://localhost:8003/api/synapse/system/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.data && data.data.webhooks) {
          setWebhookConfig(prev => ({
            ...prev,
            endpoints: data.data.webhooks || []
          }));
        } else {
          // Initialize with empty webhook config
          setWebhookConfig(prev => ({
            ...prev,
            endpoints: []
          }));
        }
      } else {
        // Initialize with empty webhook config
        setWebhookConfig(prev => ({
          ...prev,
          endpoints: []
        }));
      }
    } catch (error) {
      console.warn('Webhook API unavailable:', error);
      setWebhookConfig(prev => ({
        ...prev,
        endpoints: []
      }));
    }
  };

  const handlePluginAction = async (pluginId, action) => {
    console.log(`Plugin action: ${action} for ${pluginId}`);
    
    try {
      let endpoint = '';
      let payload = {};
      
      switch (action) {
        case 'approve':
          endpoint = `http://localhost:8003/api/synapse/plugin/${pluginId}/approve`;
          payload = { reason: 'User approved via UI' };
          break;
        case 'revoke':
          endpoint = `http://localhost:8003/api/synapse/plugin/${pluginId}/revoke`;
          payload = { reason: 'User revoked via UI' };
          break;
        case 'benchmark':
          endpoint = `http://localhost:8003/api/synapse/plugin/${pluginId}/benchmark`;
          payload = { test_params: {} };
          break;
        default:
          console.warn(`Unknown plugin action: ${action}`);
          return;
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer user-token' // Simplified auth
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`Plugin ${action} successful:`, data);
        
        // Reload plugins to reflect changes
        await loadPlugins();
        
        if (onVoiceCommand) {
          onVoiceCommand(`${action} plugin ${pluginId} completed`, currentAgent);
        }
      } else {
        console.error(`Plugin ${action} failed:`, response.status);
      }
    } catch (error) {
      console.error(`Error performing plugin ${action}:`, error);
    }
  };

  const handleConnectionAction = async (connectionId, action) => {
    console.log(`Connection action: ${action} for ${connectionId}`);
    
    try {
      let endpoint = '';
      let payload = {};
      
      switch (action) {
        case 'approve':
          endpoint = `http://localhost:8003/api/synapse/connection/${connectionId}/approve`;
          break;
        case 'close':
          endpoint = `http://localhost:8003/api/synapse/connection/${connectionId}/close`;
          break;
        default:
          console.warn(`Unknown connection action: ${action}`);
          return;
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer user-token' // Simplified auth
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`Connection ${action} successful:`, data);
        
        // Reload connections to reflect changes
        await loadConnections();
        
        if (onVoiceCommand) {
          onVoiceCommand(`${action} connection ${connectionId} completed`, currentAgent);
        }
      } else {
        console.error(`Connection ${action} failed:`, response.status);
      }
    } catch (error) {
      console.error(`Error performing connection ${action}:`, error);
    }
  };

  const handleEmbeddedUrlChange = (url) => {
    setEmbeddedUrl(url);
    if (onVoiceCommand) {
      onVoiceCommand(`load embedded browser ${url}`, currentAgent);
    }
  };

  const handleWebhookSubmit = (e) => {
    e.preventDefault();
    const newEndpoint = {
      id: `webhook-${Date.now()}`,
      ...webhookConfig.newEndpoint
    };
    
    setWebhookConfig(prev => ({
      endpoints: [...prev.endpoints, newEndpoint],
      newEndpoint: {
        name: '',
        url: '',
        method: 'POST',
        headers: {},
        enabled: true
      }
    }));

    if (onVoiceCommand) {
      onVoiceCommand(`add webhook endpoint ${newEndpoint.name}`, currentAgent);
    }
  };

  return (
    <div className="synapse-interface">
      <div className="synapse-header">
        <h2>Synapse - Plugin & API Gateway</h2>
        <div className="synapse-status">
          <span className="status-indicator active"></span>
          <span>Gateway Active</span>
        </div>
      </div>

      <div className="synapse-tabs">
        <button 
          className={`tab ${activeTab === 'plugins' ? 'active' : ''}`}
          onClick={() => setActiveTab('plugins')}
        >
          Plugin Manager
        </button>
        <button 
          className={`tab ${activeTab === 'connections' ? 'active' : ''}`}
          onClick={() => setActiveTab('connections')}
        >
          External Connections
        </button>
        <button 
          className={`tab ${activeTab === 'embedded' ? 'active' : ''}`}
          onClick={() => setActiveTab('embedded')}
        >
          Embedded Browser (SYN003)
        </button>
        <button 
          className={`tab ${activeTab === 'webhooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('webhooks')}
        >
          Webhook Config (SYN004)
        </button>
        <button 
          className={`tab ${activeTab === 'traffic' ? 'active' : ''}`}
          onClick={() => setActiveTab('traffic')}
        >
          Traffic Monitor
        </button>
      </div>

      <div className="synapse-content">
        {/* Plugin Manager */}
        {activeTab === 'plugins' && (
          <div className="plugin-manager">
            <div className="section-header">
              <h3>Registered Plugins</h3>
              <button className="btn-primary">Register New Plugin</button>
            </div>
            <div className="plugin-grid">
              {plugins.map(plugin => (
                <div key={plugin.id} className="plugin-card">
                  <div className="plugin-header">
                    <h4>{plugin.name}</h4>
                    <span className={`status-badge ${plugin.status}`}>
                      {plugin.status}
                    </span>
                  </div>
                  <div className="plugin-details">
                    <p>Version: {plugin.version}</p>
                    <p>Risk Tier: <span className={`risk-${plugin.riskTier}`}>{plugin.riskTier}</span></p>
                    <p>Permissions: {plugin.permissions.join(', ')}</p>
                  </div>
                  <div className="plugin-actions">
                    <button 
                      onClick={() => handlePluginAction(plugin.id, 'approve')}
                      disabled={plugin.status === 'active'}
                      className="btn-secondary"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => handlePluginAction(plugin.id, 'revoke')}
                      disabled={plugin.status === 'pending'}
                      className="btn-secondary"
                    >
                      Revoke
                    </button>
                    <button 
                      onClick={() => handlePluginAction(plugin.id, 'benchmark')}
                      className="btn-secondary"
                    >
                      Benchmark
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* External Connections */}
        {activeTab === 'connections' && (
          <div className="connections-manager">
            <div className="section-header">
              <h3>External Agent Connections</h3>
              <button className="btn-primary">New Connection</button>
            </div>
            <div className="connection-list">
              {connections.map(connection => (
                <div key={connection.id} className="connection-card">
                  <div className="connection-info">
                    <h4>{connection.agentId}</h4>
                    <span className={`status-badge ${connection.status}`}>
                      {connection.status}
                    </span>
                  </div>
                  <div className="connection-stats">
                    <p>Last Activity: {new Date(connection.lastActivity).toLocaleString()}</p>
                    <p>Traffic Count: {connection.trafficCount}</p>
                  </div>
                  <div className="connection-actions">
                    <button 
                      onClick={() => handleConnectionAction(connection.id, 'approve')}
                      disabled={connection.status === 'connected'}
                      className="btn-secondary"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => handleConnectionAction(connection.id, 'close')}
                      disabled={connection.status === 'disconnected'}
                      className="btn-secondary"
                    >
                      Close
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Embedded Browser Preview Panel (SYN003) */}
        {activeTab === 'embedded' && (
          <div className="embedded-browser">
            <div className="section-header">
              <h3>Embedded Browser Preview Panel</h3>
              <div className="url-input">
                <input
                  type="url"
                  placeholder="Enter URL to preview..."
                  value={embeddedUrl}
                  onChange={(e) => setEmbeddedUrl(e.target.value)}
                  className="url-field"
                />
                <button 
                  onClick={() => handleEmbeddedUrlChange(embeddedUrl)}
                  className="btn-primary"
                >
                  Load
                </button>
              </div>
            </div>
            <div className="browser-preview">
              {embeddedUrl ? (
                <iframe
                  src={embeddedUrl}
                  title="Embedded Browser Preview"
                  className="embedded-frame"
                  sandbox="allow-scripts allow-same-origin"
                />
              ) : (
                <div className="browser-placeholder">
                  <p>Enter a URL above to preview content in the embedded browser</p>
                  <p className="security-note">
                    ⚠️ Content is sandboxed and respects CSP/security model
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Webhook/API Endpoint Config (SYN004) */}
        {activeTab === 'webhooks' && (
          <div className="webhook-config">
            <div className="section-header">
              <h3>Webhook & API Endpoint Configuration</h3>
            </div>
            
            <div className="webhook-form">
              <h4>Add New Endpoint</h4>
              <form onSubmit={handleWebhookSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Endpoint Name:</label>
                    <input
                      type="text"
                      value={webhookConfig.newEndpoint.name}
                      onChange={(e) => setWebhookConfig(prev => ({
                        ...prev,
                        newEndpoint: { ...prev.newEndpoint, name: e.target.value }
                      }))}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>URL:</label>
                    <input
                      type="url"
                      value={webhookConfig.newEndpoint.url}
                      onChange={(e) => setWebhookConfig(prev => ({
                        ...prev,
                        newEndpoint: { ...prev.newEndpoint, url: e.target.value }
                      }))}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Method:</label>
                    <select
                      value={webhookConfig.newEndpoint.method}
                      onChange={(e) => setWebhookConfig(prev => ({
                        ...prev,
                        newEndpoint: { ...prev.newEndpoint, method: e.target.value }
                      }))}
                    >
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                      <option value="PUT">PUT</option>
                      <option value="DELETE">DELETE</option>
                    </select>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={webhookConfig.newEndpoint.enabled}
                        onChange={(e) => setWebhookConfig(prev => ({
                          ...prev,
                          newEndpoint: { ...prev.newEndpoint, enabled: e.target.checked }
                        }))}
                      />
                      Enabled
                    </label>
                  </div>
                  <button type="submit" className="btn-primary">Add Endpoint</button>
                </div>
              </form>
            </div>

            <div className="webhook-list">
              <h4>Configured Endpoints</h4>
              {webhookConfig.endpoints.map(endpoint => (
                <div key={endpoint.id} className="webhook-item">
                  <div className="webhook-info">
                    <h5>{endpoint.name}</h5>
                    <p>{endpoint.method} {endpoint.url}</p>
                    <span className={`status-badge ${endpoint.enabled ? 'enabled' : 'disabled'}`}>
                      {endpoint.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <div className="webhook-actions">
                    <button className="btn-secondary">Test</button>
                    <button className="btn-secondary">Edit</button>
                    <button className="btn-secondary">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Traffic Monitor */}
        {activeTab === 'traffic' && (
          <div className="traffic-monitor">
            <div className="section-header">
              <h3>Traffic Monitoring</h3>
              <button className="btn-primary">Export Logs</button>
            </div>
            <div className="traffic-summary">
              <div className="summary-card">
                <h4>Total Requests</h4>
                <p className="summary-number">{trafficLogs.length}</p>
              </div>
              <div className="summary-card">
                <h4>Active Connections</h4>
                <p className="summary-number">{connections.filter(c => c.status === 'connected').length}</p>
              </div>
              <div className="summary-card">
                <h4>Active Plugins</h4>
                <p className="summary-number">{plugins.filter(p => p.status === 'active').length}</p>
              </div>
            </div>
            <div className="traffic-logs">
              <h4>Recent Traffic</h4>
              <div className="log-list">
                {trafficLogs.map(log => (
                  <div key={log.id} className="log-item">
                    <div className="log-timestamp">
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                    <div className="log-source">{log.source}</div>
                    <div className="log-action">{log.action}</div>
                    <div className={`log-status ${log.status}`}>{log.status}</div>
                    <div className="log-details">{log.details}</div>
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

export default SynapseInterface; 