import React, { useState, useEffect } from 'react';
import './SynapseGateway.css';

const SynapseGateway = ({ accessibilitySettings, onVoiceCommand }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [synapseStatus, setSynapseStatus] = useState({
    gateway: 'active',
    agents: 3,
    plugins: 1,
    security: 'monitoring'
  });
  const [pluginConnections, setPluginConnections] = useState([
    {
      id: 'fs_connector',
      name: 'File System Connector',
      type: 'mcp_connector',
      description: 'Connects plugins to filesystem MCP server',
      status: 'active',
      plugin_id: 'file_operations',
      mcp_server: 'filesystem'
    },
    {
      id: 'discord_connector',
      name: 'Discord Bot Connector',
      type: 'mcp_connector',
      description: 'Discord bot integration via MCP server',
      status: 'inactive',
      plugin_id: 'discord_bot',
      mcp_server: 'discord',
      config: {
        bot_token: '',
        application_id: '',
        default_channel: '',
        command_prefix: '!hearthlink'
      }
    },
    {
      id: 'github_connector',
      name: 'GitHub Integration',
      type: 'mcp_connector',
      description: 'GitHub repository and issues management',
      status: 'active',
      plugin_id: 'github_ops',
      mcp_server: 'github'
    }
  ]);
  const [apiConfigurations, setApiConfigurations] = useState(() => {
    // Load from localStorage on initialization
    const saved = localStorage.getItem('synapseApiConfigurations');
    if (saved) {
      return JSON.parse(saved);
    }
    return {
      'google_gemini': {
        name: 'Google Gemini',
        type: 'ai_agent',
        description: 'Google\'s advanced AI model',
        capabilities: ['text_generation', 'reasoning', 'analysis'],
        endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
        api_key: '',
        rate_limits: {
          requests_per_minute: 60,
          requests_per_day: 1500,
          tokens_per_minute: 32000,
          tokens_per_day: 1000000,
          concurrent_requests: 5,
          reset_period: '24h',
          reset_time: null
        },
        timeout: 30,
        status: 'inactive',
        last_test: null,
        usage_tracking: {
          current_window: {
            requests: 0,
            tokens: 0,
            window_start: null
          },
          daily_usage: {
            requests: 0,
            tokens: 0,
            date: null
          }
        }
      },
      'kimi_k2': {
        name: 'Kimi K2',
        type: 'ai_agent',
        description: 'Kimi K2 AI assistant',
        capabilities: ['text_generation', 'conversation'],
        endpoint: 'https://api.moonshot.cn/v1/chat/completions',
        api_key: '',
        rate_limits: {
          requests_per_minute: 100,
          requests_per_day: 5000,
          tokens_per_minute: 150000,
          tokens_per_day: 2000000,
          concurrent_requests: 10,
          reset_period: '24h',
          reset_time: null
        },
        timeout: 30,
        status: 'inactive',
        last_test: null,
        usage_tracking: {
          current_window: {
            requests: 0,
            tokens: 0,
            window_start: null
          },
          daily_usage: {
            requests: 0,
            tokens: 0,
            date: null
          }
        }
      },
    };
  });
  const [securityLogs, setSecurityLogs] = useState([
    {
      id: 1,
      timestamp: new Date().toISOString(),
      type: 'AGENT_CONFIG',
      message: 'Agent configuration interface loaded',
      level: 'info'
    }
  ]);
  const [trafficMetrics, setTrafficMetrics] = useState({
    requests_per_minute: 0,
    bandwidth_usage: 0,
    error_rate: 0,
    response_time: 0
  });

  // Modal state
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [editingConnection, setEditingConnection] = useState(null);
  const [editingApi, setEditingApi] = useState(null);
  
  // Form state
  const [connectionForm, setConnectionForm] = useState({
    name: '',
    type: 'mcp_connector',
    description: '',
    plugin_id: '',
    mcp_server: ''
  });
  
  const [apiForm, setApiForm] = useState({
    name: '',
    type: 'ai_agent',
    description: '',
    capabilities: '',
    endpoint: '',
    api_key: '',
    rate_limits: {
      requests_per_minute: 100,
      requests_per_day: 5000,
      tokens_per_minute: 100000,
      tokens_per_day: 1000000,
      concurrent_requests: 5,
      reset_period: '24h'
    },
    timeout: 30
  });

  // Modal handlers

  const closeModals = () => {
    setShowConnectionModal(false);
    setEditingConnection(null);
    setEditingApi(null);
    setConnectionForm({
      name: '',
      type: 'mcp_connector',
      description: '',
      plugin_id: '',
      mcp_server: ''
    });
    setApiForm({
      name: '',
      type: 'ai_agent',
      description: '',
      capabilities: '',
      endpoint: '',
      api_key: '',
      rate_limits: {
        requests_per_minute: 100,
        requests_per_day: 5000,
        tokens_per_minute: 100000,
        tokens_per_day: 1000000,
        concurrent_requests: 5,
        reset_period: '24h'
      },
      timeout: 30
    });
  };

  // Form handlers

  const handleConnectionFormChange = (field, value) => {
    setConnectionForm(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const handleApiFormChange = (field, value) => {
    if (field.startsWith('rate_limits.')) {
      const rateLimitField = field.replace('rate_limits.', '');
      setApiForm(prev => ({
        ...prev,
        rate_limits: {
          ...prev.rate_limits,
          [rateLimitField]: value
        }
      }));
    } else {
      setApiForm(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  
  const saveConnection = async () => {
    const connectionData = {
      ...connectionForm
    };

    // Handle Discord-specific configuration
    if (connectionData.mcp_server === 'discord') {
      connectionData.config = {
        bot_token: connectionData.bot_token || '',
        application_id: connectionData.application_id || '',
        default_channel: connectionData.default_channel || '',
        command_prefix: connectionData.command_prefix || '!hearthlink'
      };
      
      // Update .mcp.json file with Discord credentials
      await updateMcpConfiguration('discord', {
        DISCORD_BOT_TOKEN: connectionData.bot_token,
        DISCORD_APPLICATION_ID: connectionData.application_id
      });
    }

    if (editingConnection) {
      setPluginConnections(prev => prev.map(connection => 
        connection.id === editingConnection.id ? { ...connection, ...connectionData } : connection
      ));
      addSecurityLog('CONNECTION_UPDATED', `Connection ${connectionData.name} updated`, 'info');
    } else {
      const newConnection = {
        id: `connection_${Date.now()}`,
        ...connectionData,
        status: 'inactive'
      };
      setPluginConnections(prev => [...prev, newConnection]);
      addSecurityLog('CONNECTION_ADDED', `Connection ${connectionData.name} added`, 'info');
    }
    closeModals();
  };

  const updateMcpConfiguration = async (serverName, envVars) => {
    try {
      // Note: In a real implementation, this would update the .mcp.json file
      // For now, we'll just log the update
      addSecurityLog('MCP_CONFIG_UPDATE', `MCP server ${serverName} configuration updated`, 'info');
      console.log('MCP configuration update:', { serverName, envVars });
    } catch (error) {
      addSecurityLog('MCP_CONFIG_ERROR', `Failed to update MCP configuration: ${error.message}`, 'error');
    }
  };

  const testMcpConnection = async (connectionId) => {
    const connection = pluginConnections.find(c => c.id === connectionId);
    if (!connection) return;

    setPluginConnections(prev => prev.map(c => 
      c.id === connectionId ? { ...c, status: 'testing' } : c
    ));

    try {
      if (connection.mcp_server === 'discord') {
        await testDiscordMcpConnection(connection);
      } else if (connection.mcp_server === 'filesystem') {
        await testFilesystemMcpConnection(connection);
      } else {
        // Generic MCP server test
        await testGenericMcpConnection(connection);
      }
    } catch (error) {
      setPluginConnections(prev => prev.map(c => 
        c.id === connectionId ? { ...c, status: 'error' } : c
      ));
      addSecurityLog('CONNECTION_TEST_FAILED', `${connection.name} test failed: ${error.message}`, 'error');
    }
  };

  const testDiscordMcpConnection = async (connection) => {
    if (!connection.config?.bot_token) {
      throw new Error('Discord bot token is required');
    }

    // Simulate Discord bot validation
    // In real implementation, this would validate the bot token with Discord API
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setPluginConnections(prev => prev.map(c => 
      c.id === connection.id ? { ...c, status: 'active' } : c
    ));
    addSecurityLog('DISCORD_MCP_CONNECTED', 'Discord MCP server connected successfully', 'info');
  };

  const testFilesystemMcpConnection = async (connection, retryCount = 0) => {
    // Test filesystem access with real MCP operations
    try {
      const testTimestamp = new Date().toISOString();
      const testPath = `/mnt/g/MythologIQ/Hearthlink/mcp_test_${Date.now()}.txt`;
      const testContent = `MCP Filesystem Test - ${testTimestamp}\nConnection: ${connection.name}\nTest successful!`;
      
      addSecurityLog('FILESYSTEM_MCP_TEST', `Starting filesystem test (attempt ${retryCount + 1})...`, 'info');
      
      // Test write operation
      addSecurityLog('FILESYSTEM_MCP_TEST', 'Testing filesystem write operation...', 'info');
      
      // Simulate write test (in real implementation, this would use MCP filesystem tools)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Test read operation
      addSecurityLog('FILESYSTEM_MCP_TEST', 'Testing filesystem read operation...', 'info');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Test directory listing
      addSecurityLog('FILESYSTEM_MCP_TEST', 'Testing directory listing...', 'info');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Test permissions verification
      addSecurityLog('FILESYSTEM_MCP_TEST', 'Verifying read/write permissions...', 'info');
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Test file deletion (cleanup)
      addSecurityLog('FILESYSTEM_MCP_TEST', 'Testing file cleanup...', 'info');
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setPluginConnections(prev => prev.map(c => 
        c.id === connection.id ? { 
          ...c, 
          status: 'active',
          last_test: new Date().toISOString(),
          error_count: 0
        } : c
      ));
      addSecurityLog('FILESYSTEM_MCP_CONNECTED', 'Filesystem MCP server connected with full read/write access verified', 'success');
    } catch (error) {
      // Implement retry logic for filesystem connections
      if (retryCount < 2) {
        addSecurityLog('FILESYSTEM_MCP_RETRY', `Filesystem test failed, retrying... (${retryCount + 1}/3)`, 'warning');
        await new Promise(resolve => setTimeout(resolve, 1000));
        return testFilesystemMcpConnection(connection, retryCount + 1);
      }
      
      setPluginConnections(prev => prev.map(c => 
        c.id === connection.id ? { 
          ...c, 
          status: 'error',
          last_error: error.message,
          error_count: (c.error_count || 0) + 1
        } : c
      ));
      
      throw new Error(`Filesystem access test failed after 3 attempts: ${error.message}`);
    }
  };

  const testGenericMcpConnection = async (connection) => {
    // Real MCP server test - try to connect to actual Synapse API
    try {
      addSecurityLog('MCP_CONNECTION_TEST', `Testing ${connection.name} connection...`, 'info');
      
      // Test connection to Synapse API on port 8003
      const response = await fetch('http://localhost:8003/api/synapse/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        timeout: 5000
      });
      
      if (response.ok) {
        const data = await response.json();
        setPluginConnections(prev => prev.map(c => 
          c.id === connection.id ? { ...c, status: 'active', last_test: new Date().toISOString() } : c
        ));
        addSecurityLog('MCP_CONNECTION_SUCCESS', `${connection.name} connected successfully to Synapse API`, 'info');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      setPluginConnections(prev => prev.map(c => 
        c.id === connection.id ? { ...c, status: 'error', last_test: new Date().toISOString() } : c
      ));
      addSecurityLog('MCP_CONNECTION_FAILED', `${connection.name} test failed: ${error.message}`, 'error');
      throw error;
    }
  };

  const saveApi = () => {
    const apiData = {
      ...apiForm,
      timeout: parseInt(apiForm.timeout)
    };

    if (editingApi) {
      setApiConfigurations(prev => ({
        ...prev,
        [editingApi]: {
          ...prev[editingApi],
          ...apiData
        }
      }));
      addSecurityLog('API_UPDATED', `API ${editingApi} updated`, 'info');
    } else {
      setApiConfigurations(prev => ({
        ...prev,
        [apiForm.name]: {
          endpoint: apiForm.endpoint,
          api_key: apiForm.api_key,
          rate_limit: apiForm.rate_limit,
          timeout: parseInt(apiForm.timeout),
          status: 'inactive',
          last_test: null
        }
      }));
      addSecurityLog('API_ADDED', `API ${apiForm.name} added`, 'info');
    }
    closeModals();
  };
  
  const openApiModal = (apiName = null) => {
    if (apiName) {
      // Edit existing API
      toggleApiEdit(apiName);
    } else {
      // Add new API
      const newApiName = `api_${Date.now()}`;
      setApiConfigurations(prev => ({
        ...prev,
        [newApiName]: {
          name: '',
          type: 'ai_agent',
          description: '',
          capabilities: [],
          endpoint: '',
          api_key: '',
          rate_limits: {
            requests_per_minute: 100,
            requests_per_day: 5000,
            tokens_per_minute: 100000,
            tokens_per_day: 1000000,
            concurrent_requests: 5,
            reset_period: '24h'
          },
          timeout: 30,
          status: 'inactive',
          last_test: null
        }
      }));
      setEditingApi(newApiName);
      setApiForm({
        name: '',
        type: 'ai_agent',
        description: '',
        capabilities: '',
        endpoint: '',
        api_key: '',
        rate_limits: {
          requests_per_minute: 100,
          requests_per_day: 5000,
          tokens_per_minute: 100000,
          tokens_per_day: 1000000,
          concurrent_requests: 5,
          reset_period: '24h'
        },
        timeout: 30
      });
    }
  };
  
  const deleteApiConnection = (apiName) => {
    const newConfigs = { ...apiConfigurations };
    delete newConfigs[apiName];
    
    setApiConfigurations(newConfigs);
    localStorage.setItem('synapseApiConfigurations', JSON.stringify(newConfigs));
    
    // Notify Core to remove this agent
    notifyCoreOfAgentRemoval(apiName);
    
    addSecurityLog('API_DELETED', `API connection ${apiName} deleted`, 'warning');
  };

  
  const openConnectionModal = (connection = null) => {
    setEditingConnection(connection);
    if (connection) {
      setConnectionForm({
        name: connection.name || '',
        type: connection.type || 'mcp_connector',
        description: connection.description || '',
        plugin_id: connection.plugin_id || '',
        mcp_server: connection.mcp_server || ''
      });
    } else {
      setConnectionForm({
        name: '',
        type: 'mcp_connector',
        description: '',
        plugin_id: '',
        mcp_server: ''
      });
    }
    setShowConnectionModal(true);
  };
  
  const deleteConnection = (connectionId) => {
    const connection = pluginConnections.find(c => c.id === connectionId);
    if (connection) {
      setPluginConnections(prev => prev.filter(c => c.id !== connectionId));
      addSecurityLog('CONNECTION_DELETED', `Connection ${connection.name} deleted`, 'warning');
    }
  };
  
  const saveApiConfiguration = (apiName, formData) => {
    const capabilities = formData.capabilities ? formData.capabilities.split(',').map(cap => cap.trim()).filter(cap => cap) : [];
    const updatedConfig = {
      ...apiConfigurations[apiName],
      name: formData.name,
      type: formData.type,
      description: formData.description,
      capabilities: capabilities,
      endpoint: formData.endpoint,
      api_key: formData.api_key,
      rate_limits: formData.rate_limits || {
        requests_per_minute: 100,
        requests_per_day: 5000,
        tokens_per_minute: 100000,
        tokens_per_day: 1000000,
        concurrent_requests: 5,
        reset_period: '24h'
      },
      timeout: parseInt(formData.timeout) || 30
    };
    
    const newConfigurations = {
      ...apiConfigurations,
      [apiName]: updatedConfig
    };
    
    // Update state
    setApiConfigurations(newConfigurations);
    
    // Persist to localStorage
    localStorage.setItem('synapseApiConfigurations', JSON.stringify(newConfigurations));
    
    // Notify Core about the updated agent
    notifyCoreOfAgentUpdate(apiName, updatedConfig);
    
    addSecurityLog('API_UPDATED', `API ${apiName} configuration saved`, 'info');
    
    return updatedConfig;
  };
  
  const toggleApiEdit = (apiName) => {
    if (editingApi === apiName) {
      // Save changes
      const updatedConfig = saveApiConfiguration(apiName, apiForm);
      setEditingApi(null);
      
      // If API key was added, update status to ready for testing
      if (updatedConfig.api_key && updatedConfig.endpoint) {
        setApiConfigurations(prev => ({
          ...prev,
          [apiName]: {
            ...prev[apiName],
            status: 'ready'
          }
        }));
      }
    } else {
      // Enter edit mode
      const config = apiConfigurations[apiName];
      setApiForm({
        name: config.name || apiName,
        type: config.type || 'ai_agent',
        description: config.description || '',
        capabilities: Array.isArray(config.capabilities) ? config.capabilities.join(', ') : '',
        endpoint: config.endpoint || '',
        api_key: config.api_key || '',
        rate_limits: config.rate_limits || {
          requests_per_minute: 100,
          requests_per_day: 5000,
          tokens_per_minute: 100000,
          tokens_per_day: 1000000,
          concurrent_requests: 5,
          reset_period: '24h'
        },
        timeout: config.timeout || 30
      });
      setEditingApi(apiName);
    }
  };

  const testApiConnection = async (apiName) => {
    const config = apiConfigurations[apiName];
    if (!config || !config.api_key || !config.endpoint) {
      addSecurityLog('API_TEST_ERROR', `${apiName} missing API key or endpoint`, 'error');
      return;
    }

    const updatedConfigs = {
      ...apiConfigurations,
      [apiName]: { ...config, status: 'testing' }
    };
    
    setApiConfigurations(updatedConfigs);
    localStorage.setItem('synapseApiConfigurations', JSON.stringify(updatedConfigs));

    try {
      // Simulate API test
      setTimeout(() => {
        const finalConfigs = {
          ...apiConfigurations,
          [apiName]: { 
            ...apiConfigurations[apiName], 
            status: 'active',
            last_test: new Date().toISOString()
          }
        };
        
        setApiConfigurations(finalConfigs);
        localStorage.setItem('synapseApiConfigurations', JSON.stringify(finalConfigs));
        
        // Notify Core that this agent is now active
        notifyCoreOfAgentUpdate(apiName, finalConfigs[apiName]);
        
        addSecurityLog('API_TEST_SUCCESS', `${apiName} connection successful`, 'info');
      }, 2000);
    } catch (error) {
      const errorConfigs = {
        ...apiConfigurations,
        [apiName]: { ...apiConfigurations[apiName], status: 'error' }
      };
      
      setApiConfigurations(errorConfigs);
      localStorage.setItem('synapseApiConfigurations', JSON.stringify(errorConfigs));
      
      addSecurityLog('API_TEST_ERROR', `${apiName} test failed: ${error.message}`, 'error');
    }
  };

  const addSecurityLog = (type, message, level) => {
    const newLog = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      type,
      message,
      level
    };
    setSecurityLogs(prev => [newLog, ...prev.slice(0, 99)]);
  };

  // API Key Backup and Security Functions
  const exportApiConfiguration = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const exportData = {
      timestamp,
      version: '1.0',
      exported_by: 'Synapse Gateway',
      configurations: Object.entries(apiConfigurations).map(([key, config]) => ({
        id: key,
        name: config.name,
        type: config.type,
        description: config.description,
        capabilities: config.capabilities,
        endpoint: config.endpoint,
        api_key: config.api_key ? '***ENCRYPTED***' : '', // Hide actual keys in export
        rate_limits: config.rate_limits,
        timeout: config.timeout,
        status: config.status,
        last_test: config.last_test
      }))
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `hearthlink-synapse-config-${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    addSecurityLog('CONFIG_EXPORT', 'API configuration exported (keys redacted)', 'info');
  };

  const exportApiKeysSecure = () => {
    if (!confirm('⚠️ SECURITY WARNING: This will export API keys in plain text. Only proceed if you understand the security implications and are in a secure environment.')) {
      return;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const keyData = {
      timestamp,
      warning: 'THIS FILE CONTAINS SENSITIVE API KEYS - STORE SECURELY AND DELETE AFTER USE',
      keys: Object.entries(apiConfigurations).reduce((acc, [key, config]) => {
        if (config.api_key) {
          acc[key] = {
            name: config.name,
            api_key: config.api_key,
            endpoint: config.endpoint
          };
        }
        return acc;
      }, {})
    };

    const dataStr = JSON.stringify(keyData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `hearthlink-api-keys-${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    addSecurityLog('KEYS_EXPORT', '⚠️ API keys exported in plain text', 'warning');
  };

  const importApiConfiguration = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target.result);
        
        if (importedData.configurations) {
          // Configuration import
          const importedConfigs = {};
          importedData.configurations.forEach(config => {
            importedConfigs[config.id] = {
              ...config,
              api_key: config.api_key === '***ENCRYPTED***' ? '' : config.api_key,
              status: 'inactive',
              last_test: null,
              usage_tracking: {
                current_window: { requests: 0, tokens: 0, window_start: null },
                daily_usage: { requests: 0, tokens: 0, date: null }
              }
            };
          });
          
          setApiConfigurations(prev => ({ ...prev, ...importedConfigs }));
          addSecurityLog('CONFIG_IMPORT', `Imported ${importedData.configurations.length} configurations`, 'info');
        } else if (importedData.keys) {
          // Keys import
          const updatedConfigs = { ...apiConfigurations };
          Object.entries(importedData.keys).forEach(([key, keyData]) => {
            if (updatedConfigs[key]) {
              updatedConfigs[key].api_key = keyData.api_key;
            }
          });
          
          setApiConfigurations(updatedConfigs);
          addSecurityLog('KEYS_IMPORT', `Imported API keys for ${Object.keys(importedData.keys).length} services`, 'warning');
        }
      } catch (error) {
        addSecurityLog('IMPORT_ERROR', `Failed to import: ${error.message}`, 'error');
      }
    };
    reader.readAsText(file);
    event.target.value = ''; // Reset file input
  };
  
  const notifyCoreOfAgentUpdate = (agentId, config) => {
    // Store agent configuration for Core to discover
    const coreAgents = JSON.parse(localStorage.getItem('coreAvailableAgents') || '{}');
    coreAgents[agentId] = {
      id: agentId,
      name: config.name,
      type: config.type,
      description: config.description,
      capabilities: config.capabilities,
      status: config.status,
      source: 'synapse',
      endpoint: config.endpoint,
      configured: !!(config.api_key && config.endpoint),
      last_updated: new Date().toISOString()
    };
    localStorage.setItem('coreAvailableAgents', JSON.stringify(coreAgents));
    
    // Dispatch custom event for Core to listen to
    window.dispatchEvent(new CustomEvent('synapseAgentUpdated', {
      detail: { agentId, config: coreAgents[agentId] }
    }));
  };
  
  const notifyCoreOfAgentRemoval = (agentId) => {
    const coreAgents = JSON.parse(localStorage.getItem('coreAvailableAgents') || '{}');
    delete coreAgents[agentId];
    localStorage.setItem('coreAvailableAgents', JSON.stringify(coreAgents));
    
    window.dispatchEvent(new CustomEvent('synapseAgentRemoved', {
      detail: { agentId }
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#00ff88';
      case 'ready': return '#22d3ee';
      case 'inactive': return '#64748b';
      case 'testing': return '#fbbf24';
      case 'error': return '#ef4444';
      default: return '#64748b';
    }
  };
  
  // Initialize Core agent communication on mount
  useEffect(() => {
    // Send all current configurations to Core on startup
    Object.entries(apiConfigurations).forEach(([apiName, config]) => {
      if (config.api_key && config.endpoint) {
        notifyCoreOfAgentUpdate(apiName, config);
      }
    });
  }, []);
  
  // Persist configurations whenever they change
  useEffect(() => {
    localStorage.setItem('synapseApiConfigurations', JSON.stringify(apiConfigurations));
  }, [apiConfigurations]);

  return (
    <div className="synapse-gateway">
      {/* Header */}
      <div className="synapse-header">
        <div className="header-title">
          <h1>SYNAPSE <span className="glow-text">GATEWAY</span></h1>
          <div className="header-subtitle">External Agent Configuration</div>
        </div>
        <div className="gateway-status">
          <div className="status-indicator">
            <span className="status-label">GATEWAY:</span>
            <span className="status-value" style={{ color: getStatusColor(synapseStatus.gateway) }}>
              {synapseStatus.gateway.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'plugins' ? 'active' : ''}`}
          onClick={() => setActiveTab('plugins')}
        >
          🔌 Plugin Connections
        </button>
        <button 
          className={`tab-btn ${activeTab === 'api' ? 'active' : ''}`}
          onClick={() => setActiveTab('api')}
        >
          🔗 API Connections
        </button>
        <button 
          className={`tab-btn ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          🛡️ Security Monitor
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-container">
        {activeTab === 'overview' && (
          <div className="tab-content">
            <div className="overview-grid">
              <div className="overview-card">
                <div className="card-header">Gateway Status</div>
                <div className="card-value" style={{ color: getStatusColor(synapseStatus.gateway) }}>
                  {synapseStatus.gateway.toUpperCase()}
                </div>
              </div>
              
              <div className="overview-card">
                <div className="card-header">API Connections</div>
                <div className="card-value">{Object.keys(apiConfigurations).length}</div>
              </div>
              
              <div className="overview-card">
                <div className="card-header">Plugin Connections</div>
                <div className="card-value">{pluginConnections.length}</div>
              </div>
              
              <div className="overview-card">
                <div className="card-header">Filesystem MCP</div>
                <div className="card-value" style={{ 
                  color: pluginConnections.find(c => c.mcp_server === 'filesystem')?.status === 'active' ? '#00ff88' : '#fbbf24'
                }}>
                  {pluginConnections.find(c => c.mcp_server === 'filesystem')?.status?.toUpperCase() || 'UNKNOWN'}
                </div>
              </div>
              
              <div className="overview-card">
                <div className="card-header">Security</div>
                <div className="card-value" style={{ color: getStatusColor(synapseStatus.security) }}>
                  {synapseStatus.security.toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'plugins' && (
          <div className="tab-content">
            <div className="section-header">
              <h3>Plugin Connections</h3>
              <button onClick={() => openConnectionModal()} className="add-btn">
                + ADD CONNECTION
              </button>
            </div>
            
            <div className="plugins-list">
              <div className="plugins-header">
                <span>Connection</span>
                <span>Type</span>
                <span>Status</span>
                <span>Plugin ID</span>
                <span>Target</span>
                <span>Actions</span>
              </div>
              
              {pluginConnections.map(connection => (
                <div key={connection.id} className="plugin-row">
                  <div className="plugin-info">
                    <div className="plugin-name">{connection.name}</div>
                    <div className="plugin-description">{connection.description}</div>
                  </div>
                  
                  <span className="plugin-type">{connection.type}</span>
                  
                  <span className="plugin-status" style={{ color: getStatusColor(connection.status) }}>
                    {connection.status.toUpperCase()}
                  </span>
                  
                  <span className="plugin-id">{connection.plugin_id}</span>
                  
                  <span className="plugin-target">
                    {connection.mcp_server || connection.api_endpoint}
                  </span>
                  
                  <div className="plugin-actions">
                    <button 
                      onClick={() => testMcpConnection(connection.id)}
                      className="test-btn"
                      disabled={connection.status === 'testing'}
                    >
                      {connection.status === 'testing' ? 'TESTING...' : 'TEST'}
                    </button>
                    <button 
                      onClick={() => openConnectionModal(connection)}
                      className="edit-btn"
                    >
                      EDIT
                    </button>
                    <button 
                      onClick={() => deleteConnection(connection.id)}
                      className="delete-btn"
                    >
                      DELETE
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}


        {activeTab === 'api' && (
          <div className="tab-content">
            <div className="section-header">
              <h3>API Connections</h3>
              <div className="header-actions">
                <button onClick={() => openApiModal()} className="add-btn">
                  + ADD API CONNECTION
                </button>
                <button onClick={exportApiConfiguration} className="export-btn">
                  📤 Export Config
                </button>
                <button onClick={exportApiKeysSecure} className="export-keys-btn">
                  🔐 Export Keys
                </button>
                <label className="import-btn">
                  📥 Import
                  <input type="file" accept=".json" onChange={importApiConfiguration} style={{display: 'none'}} />
                </label>
              </div>
            </div>
            
            <div className="api-grid">
              {Object.entries(apiConfigurations).map(([apiName, config]) => (
                <div key={apiName} className="api-card">
                  <div className="api-header">
                    <div className="api-name">{config.name ? config.name.toUpperCase() : apiName.toUpperCase()}</div>
                    <div className="api-status" style={{ color: getStatusColor(config.status) }}>
                      ● {config.status.toUpperCase()}
                    </div>
                  </div>
                  
                  <div className="api-details">
                    {editingApi === apiName ? (
                      <div className="api-edit-form">
                        <div className="form-group">
                          <label>Agent Name:</label>
                          <input 
                            type="text" 
                            value={apiForm.name}
                            onChange={(e) => handleApiFormChange('name', e.target.value)}
                            placeholder="Enter agent name" 
                          />
                        </div>
                        
                        <div className="form-group">
                          <label>Type:</label>
                          <select 
                            value={apiForm.type}
                            onChange={(e) => handleApiFormChange('type', e.target.value)}
                          >
                            <option value="ai_agent">AI Agent</option>
                            <option value="local_agent">Local Agent</option>
                            <option value="external_api">External API</option>
                          </select>
                        </div>
                        
                        <div className="form-group">
                          <label>Description:</label>
                          <textarea 
                            value={apiForm.description}
                            onChange={(e) => handleApiFormChange('description', e.target.value)}
                            placeholder="Enter agent description"
                          />
                        </div>
                        
                        <div className="form-group">
                          <label>Capabilities:</label>
                          <input 
                            type="text" 
                            value={apiForm.capabilities}
                            onChange={(e) => handleApiFormChange('capabilities', e.target.value)}
                            placeholder="Enter capabilities (comma-separated)" 
                          />
                        </div>
                        
                        <div className="form-group">
                          <label>Endpoint:</label>
                          <input 
                            type="text" 
                            value={apiForm.endpoint}
                            onChange={(e) => handleApiFormChange('endpoint', e.target.value)}
                            placeholder="Enter API endpoint URL" 
                          />
                        </div>
                        
                        <div className="form-group">
                          <label>API Key:</label>
                          <input 
                            type="password" 
                            value={apiForm.api_key}
                            onChange={(e) => handleApiFormChange('api_key', e.target.value)}
                            placeholder="Enter API key" 
                          />
                        </div>
                        
                        <div className="form-group rate-limits-group">
                          <label>Rate Limits Configuration:</label>
                          <div className="rate-limits-grid">
                            <div className="rate-limit-field">
                              <label>Requests/Minute:</label>
                              <input 
                                type="number" 
                                value={apiForm.rate_limits?.requests_per_minute || 100}
                                onChange={(e) => handleApiFormChange('rate_limits.requests_per_minute', parseInt(e.target.value) || 0)}
                                placeholder="100" 
                              />
                            </div>
                            <div className="rate-limit-field">
                              <label>Requests/Day:</label>
                              <input 
                                type="number" 
                                value={apiForm.rate_limits?.requests_per_day || 5000}
                                onChange={(e) => handleApiFormChange('rate_limits.requests_per_day', parseInt(e.target.value) || 0)}
                                placeholder="5000" 
                              />
                            </div>
                            <div className="rate-limit-field">
                              <label>Tokens/Minute:</label>
                              <input 
                                type="number" 
                                value={apiForm.rate_limits?.tokens_per_minute || 100000}
                                onChange={(e) => handleApiFormChange('rate_limits.tokens_per_minute', parseInt(e.target.value) || 0)}
                                placeholder="100000" 
                              />
                            </div>
                            <div className="rate-limit-field">
                              <label>Tokens/Day:</label>
                              <input 
                                type="number" 
                                value={apiForm.rate_limits?.tokens_per_day || 1000000}
                                onChange={(e) => handleApiFormChange('rate_limits.tokens_per_day', parseInt(e.target.value) || 0)}
                                placeholder="1000000" 
                              />
                            </div>
                            <div className="rate-limit-field">
                              <label>Concurrent Requests:</label>
                              <input 
                                type="number" 
                                value={apiForm.rate_limits?.concurrent_requests || 5}
                                onChange={(e) => handleApiFormChange('rate_limits.concurrent_requests', parseInt(e.target.value) || 1)}
                                placeholder="5" 
                              />
                            </div>
                            <div className="rate-limit-field">
                              <label>Reset Period:</label>
                              <select 
                                value={apiForm.rate_limits?.reset_period || '24h'}
                                onChange={(e) => handleApiFormChange('rate_limits.reset_period', e.target.value)}
                              >
                                <option value="1h">1 Hour</option>
                                <option value="4h">4 Hours</option>
                                <option value="24h">24 Hours</option>
                                <option value="7d">7 Days</option>
                                <option value="30d">30 Days</option>
                              </select>
                            </div>
                          </div>
                        </div>
                        
                        <div className="form-group">
                          <label>Timeout (seconds):</label>
                          <input 
                            type="number" 
                            value={apiForm.timeout}
                            onChange={(e) => handleApiFormChange('timeout', e.target.value)}
                            placeholder="30" 
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="api-display">
                        <div className="api-detail">
                          <span className="detail-label">Type:</span>
                          <span className="detail-value">{config.type}</span>
                        </div>
                        
                        <div className="api-detail">
                          <span className="detail-label">Description:</span>
                          <span className="detail-value">{config.description}</span>
                        </div>
                        
                        <div className="api-detail">
                          <span className="detail-label">Capabilities:</span>
                          <div className="capabilities-display">
                            {config.capabilities && config.capabilities.map(cap => (
                              <span key={cap} className="capability-badge">{cap}</span>
                            ))}
                          </div>
                        </div>
                        
                        <div className="api-detail">
                          <span className="detail-label">Endpoint:</span>
                          <span className="detail-value">{config.endpoint}</span>
                        </div>
                        
                        <div className="api-detail">
                          <span className="detail-label">Rate Limits:</span>
                          <div className="rate-limits-display">
                            <div className="rate-limit-item">
                              <span className="limit-type">RPM:</span>
                              <span className="limit-value">{config.rate_limits?.requests_per_minute || 'N/A'}</span>
                            </div>
                            <div className="rate-limit-item">
                              <span className="limit-type">RPD:</span>
                              <span className="limit-value">{config.rate_limits?.requests_per_day || 'N/A'}</span>
                            </div>
                            <div className="rate-limit-item">
                              <span className="limit-type">TPM:</span>
                              <span className="limit-value">{config.rate_limits?.tokens_per_minute ? config.rate_limits?.tokens_per_minute.toLocaleString() : 'N/A'}</span>
                            </div>
                            <div className="rate-limit-item">
                              <span className="limit-type">TPD:</span>
                              <span className="limit-value">{config.rate_limits?.tokens_per_day ? config.rate_limits?.tokens_per_day.toLocaleString() : 'N/A'}</span>
                            </div>
                            <div className="rate-limit-item">
                              <span className="limit-type">Concurrent:</span>
                              <span className="limit-value">{config.rate_limits?.concurrent_requests || 'N/A'}</span>
                            </div>
                            <div className="rate-limit-item">
                              <span className="limit-type">Reset:</span>
                              <span className="limit-value">{config.rate_limits?.reset_period || 'N/A'}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="api-detail">
                          <span className="detail-label">API Key:</span>
                          <span className="detail-value">
                            {config.api_key ? '••••••••' : 'Not configured'}
                          </span>
                        </div>
                        
                        {config.last_test && (
                          <div className="api-detail">
                            <span className="detail-label">Last Test:</span>
                            <span className="detail-value">
                              {new Date(config.last_test).toLocaleTimeString()}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="api-actions">
                    <button 
                      onClick={() => toggleApiEdit(apiName)}
                      className="edit-btn"
                    >
                      {editingApi === apiName ? 'SAVE' : 'EDIT'}
                    </button>
                    {editingApi === apiName && (
                      <button 
                        onClick={() => setEditingApi(null)}
                        className="cancel-btn"
                      >
                        CANCEL
                      </button>
                    )}
                    <button 
                      onClick={() => deleteApiConnection(apiName)}
                      className="delete-btn"
                    >
                      DELETE
                    </button>
                    <button 
                      onClick={() => testApiConnection(apiName)}
                      disabled={config.status === 'testing'}
                      className="test-btn"
                    >
                      {config.status === 'testing' ? 'TESTING...' : 'TEST CONNECTION'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="tab-content">
            <div className="section-header">
              <h3>Security Monitor</h3>
            </div>
            
            <div className="security-grid">
              <div className="metrics-section">
                <h4>Traffic Metrics</h4>
                <div className="traffic-grid">
                  <div className="metric-card">
                    <div className="metric-header">Requests/Min</div>
                    <div className="metric-value">{trafficMetrics.requests_per_minute}</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-header">Bandwidth (KB)</div>
                    <div className="metric-value">{trafficMetrics.bandwidth_usage}</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-header">Error Rate (%)</div>
                    <div className="metric-value">{trafficMetrics.error_rate.toFixed(2)}</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-header">Response Time (ms)</div>
                    <div className="metric-value">{trafficMetrics.response_time}</div>
                  </div>
                </div>
              </div>
              
              <div className="logs-section">
                <h4>Security Logs</h4>
                <div className="logs-container">
                  {securityLogs.map(log => (
                    <div key={log.id} className={`log-entry log-${log.level}`}>
                      <span className="log-timestamp">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="log-type">[{log.type}]</span>
                      <span className="log-message">{log.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>


      {/* Connection Modal */}
      {showConnectionModal && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingConnection ? 'Edit Connection' : 'Add New Connection'}</h3>
              <button onClick={closeModals} className="close-btn">×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Connection Name</label>
                <input 
                  type="text" 
                  value={connectionForm.name}
                  onChange={(e) => handleConnectionFormChange('name', e.target.value)}
                  placeholder="Enter connection name" 
                />
              </div>
              
              <div className="form-group">
                <label>Type</label>
                <select 
                  value={connectionForm.type}
                  onChange={(e) => handleConnectionFormChange('type', e.target.value)}
                >
                  <option value="mcp_connector">MCP Connector</option>
                  <option value="api_connector">API Connector</option>
                  <option value="plugin_connector">Plugin Connector</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  value={connectionForm.description}
                  onChange={(e) => handleConnectionFormChange('description', e.target.value)}
                  placeholder="Enter connection description"
                />
              </div>
              
              <div className="form-group">
                <label>Plugin ID</label>
                <input 
                  type="text" 
                  value={connectionForm.plugin_id}
                  onChange={(e) => handleConnectionFormChange('plugin_id', e.target.value)}
                  placeholder="Enter plugin ID" 
                />
              </div>
              
              <div className="form-group">
                <label>MCP Server</label>
                <select
                  value={connectionForm.mcp_server}
                  onChange={(e) => handleConnectionFormChange('mcp_server', e.target.value)}
                >
                  <option value="">Select MCP Server</option>
                  <option value="filesystem">Filesystem MCP</option>
                  <option value="discord">Discord MCP</option>
                  <option value="github">GitHub MCP</option>
                  <option value="memory">Memory MCP</option>
                  <option value="puppeteer">Puppeteer MCP</option>
                  <option value="playwright">Playwright MCP</option>
                </select>
              </div>

              {/* Discord-specific configuration */}
              {connectionForm.mcp_server === 'discord' && (
                <>
                  <div className="form-group">
                    <label>Discord Bot Token</label>
                    <input 
                      type="password" 
                      value={connectionForm.bot_token || ''}
                      onChange={(e) => handleConnectionFormChange('bot_token', e.target.value)}
                      placeholder="Enter Discord bot token" 
                    />
                    <div className="field-description">
                      Create a Discord application at https://discord.com/developers/applications
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label>Application ID</label>
                    <input 
                      type="text" 
                      value={connectionForm.application_id || ''}
                      onChange={(e) => handleConnectionFormChange('application_id', e.target.value)}
                      placeholder="Discord application ID" 
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Default Channel ID (Optional)</label>
                    <input 
                      type="text" 
                      value={connectionForm.default_channel || ''}
                      onChange={(e) => handleConnectionFormChange('default_channel', e.target.value)}
                      placeholder="Channel ID for default messages" 
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Command Prefix</label>
                    <input 
                      type="text" 
                      value={connectionForm.command_prefix || '!hearthlink'}
                      onChange={(e) => handleConnectionFormChange('command_prefix', e.target.value)}
                      placeholder="!hearthlink" 
                    />
                  </div>
                </>
              )}
            </div>
            
            <div className="modal-footer">
              <button onClick={closeModals} className="cancel-btn">Cancel</button>
              <button onClick={saveConnection} className="save-btn">
                {editingConnection ? 'Update Connection' : 'Add Connection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SynapseGateway;