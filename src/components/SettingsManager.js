import React, { useState, useEffect } from 'react';
import './SettingsManager.css';

const SettingsManager = ({ isVisible, onClose, onSettingsChange }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
      general: {
        theme: 'starcraft',
        language: 'en',
        autoSave: true,
        notifications: true,
        voiceEnabled: true,
        startupModule: 'alden'
      },
      apis: {
        googleAiKey: '',
        ollamaUrl: 'http://localhost:11434',
        customEndpoints: []
      },
      claudeCode: {
        enabled: true,
        cliPath: '',
        autoDetect: true,
        timeout: 30
      },
      localLLM: {
        enabled: false,
        provider: 'ollama',
        endpoint: 'http://localhost:11434',
        dualLLMMode: true,
        profiles: {
          low: {
            enabled: true,
            model: 'llama3.2:3b',
            parameterRange: '2-3B',
            roles: ['routing', 'simple_tasks'],
            temperature: 0.7,
            contextLength: 16384,
            priority: 1
          },
          mid: {
            enabled: true,
            model: 'llama3.1:8b',
            parameterRange: '7-9B',
            roles: ['reasoning', 'coding', 'complex_tasks'],
            temperature: 0.7,
            contextLength: 32768,
            priority: 2
          }
        },
        roleAssignments: {
          routing: 'low',
          reasoning: 'mid',
          coding: 'mid',
          multimodal: 'mid',
          simple_tasks: 'low',
          complex_tasks: 'mid'
        },
        streaming: true,
        autoStart: false,
        fallbackEnabled: true,
        healthCheckInterval: 30000
      },
      agents: {
        alden: { 
          enabled: true, 
          priority: 1,
          prompt: "You are Alden, a highly capable AI assistant and productivity companion. You help users with their daily tasks, provide thoughtful insights, and maintain a friendly, professional demeanor. You excel at understanding context and providing relevant, actionable advice."
        },
        alice: { 
          enabled: true, 
          priority: 2,
          prompt: "You are Alice, a cognitive-behavioral analysis specialist. You focus on analytical thinking, problem-solving, and optimization. You help users break down complex problems, identify patterns, and develop systematic approaches to challenges."
        },
        mimic: { 
          enabled: true, 
          priority: 3,
          prompt: "DYNAMIC - This agent adapts its persona based on context and user needs.",
          isDynamic: true
        },
        sentry: { 
          enabled: true, 
          priority: 4,
          prompt: "HARD-CODED - System monitoring and security specialist with optimized monitoring capabilities.",
          isHardCoded: true
        },
        core: { 
          enabled: true, 
          priority: 0,
          prompt: "You are the Core orchestration system, responsible for managing multi-agent interactions and coordinating complex workflows."
        }
      },
      voice: {
        enabled: true,
        sensitivity: 0.7,
        language: 'en-US',
        wakeWord: 'alden',
        routingMode: 'smart'
      },
      security: {
        encryptionEnabled: true,
        auditLogging: true,
        sessionTimeout: 30,
        autoLock: false
      },
      performance: {
        maxMemoryUsage: 4096,
        cachingEnabled: true,
        preloadModules: true,
        backgroundSync: true
      }
  });

  const [testResults, setTestResults] = useState({});
  const [availableModels, setAvailableModels] = useState([]);
  const [recommendedModels, setRecommendedModels] = useState([]);
  const [systemSpecs, setSystemSpecs] = useState({ ram: 0, gpu: false });
  const [serviceStatus, setServiceStatus] = useState({
    isRunning: false,
    lastCheck: null,
    error: null
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [fetchingModels, setFetchingModels] = useState(false);

  useEffect(() => {
    loadSettings();
    if (isVisible) {
      // Check service status when settings are opened
      setTimeout(() => checkServiceStatus(), 1000);
      // Fetch available models and system specs
      setTimeout(() => {
        fetchAvailableModels();
        detectSystemSpecs();
      }, 1500);
    }
  }, [isVisible]);

  const loadSettings = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/settings');
      if (response.ok) {
        const loadedSettings = await response.json();
        // Properly merge with defaults to ensure new structure is preserved
        setSettings(prev => {
          const merged = { ...prev };
          Object.keys(loadedSettings).forEach(key => {
            if (typeof prev[key] === 'object' && typeof loadedSettings[key] === 'object') {
              merged[key] = { ...prev[key], ...loadedSettings[key] };
            } else {
              merged[key] = loadedSettings[key];
            }
          });
          return merged;
        });
      }
    } catch (err) {
      console.warn('Failed to load settings:', err);
      // Use defaults
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    setError('');
    setSuccessMessage('');
    
    try {
      console.log('SettingsManager - Saving settings:', settings);
      
      // Always save to localStorage first
      localStorage.setItem('hearthlinkSettings', JSON.stringify(settings));
      
      // Try to save to server if available
      try {
        const response = await fetch('http://localhost:8001/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ settings: settings })
        });
        
        if (response.ok) {
          console.log('SettingsManager - Server save successful');
        } else {
          console.warn('SettingsManager - Server save failed, using localStorage only');
        }
      } catch (serverError) {
        console.warn('SettingsManager - Server unavailable, using localStorage only:', serverError);
      }
      
      // Always complete the save process
      onSettingsChange(settings);
      setSuccessMessage('✅ Settings saved successfully!');
      setSaving(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(''), 3000);
      
    } catch (err) {
      console.error('SettingsManager - Save error:', err);
      setError(`Save failed: ${err.message}`);
      setSaving(false);
    }
  };

  const testConnection = async (service) => {
    setTestResults(prev => ({ ...prev, [service]: 'testing' }));
    
    try {
      if (service === 'claude-code') {
        // Test Claude Code CLI availability
        try {
          const response = await fetch('http://localhost:8001/api/claude-code/status', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            timeout: 5000
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.available) {
              setTestResults(prev => ({ 
                ...prev, 
                [service]: 'success',
                [`${service}_details`]: `✅ Claude Code CLI available\n📂 Path: ${data.cli_path || 'Auto-detected'}\n🔧 Version: ${data.version || 'Unknown'}\n💻 Commands: ${data.available_commands ? data.available_commands.length : 0} available`
              }));
            } else {
              setTestResults(prev => ({ 
                ...prev, 
                [service]: 'warning',
                [`${service}_details`]: `⚠️ Claude Code CLI not found\n💡 Install Claude Code CLI or check path\n📍 Common paths:\n   • /usr/local/bin/claude-code\n   • ~/.local/bin/claude-code\n   • C:\\Program Files\\Claude Code\\claude-code.exe`
              }));
            }
          } else {
            throw new Error(`Claude Code service not responding: HTTP ${response.status}`);
          }
        } catch (err) {
          setTestResults(prev => ({ 
            ...prev, 
            [service]: 'failed',
            [`${service}_details`]: `❌ Failed to check Claude Code CLI\n🔧 ${err.message}\n💡 This is a CLI tool - no API key needed`
          }));
        }
      } else if (service === 'local-llm') {
        // Test Local LLM API service with multiple fallback endpoints
        const endpoints = [
          'http://localhost:8001/api/test',
          'http://localhost:11434/api/tags',  // Ollama endpoint
          'http://localhost:8001/health'
        ];
        
        let lastError = null;
        let success = false;
        
        for (const endpoint of endpoints) {
          try {
            const response = await fetch(endpoint, {
              method: endpoint.includes('tags') ? 'GET' : 'POST',
              headers: { 'Content-Type': 'application/json' },
              timeout: 5000
            });
            
            if (response.ok) {
              const data = await response.json();
              
              if (endpoint.includes('tags')) {
                // Ollama tags endpoint
                setTestResults(prev => ({ 
                  ...prev, 
                  [service]: 'success',
                  [`${service}_details`]: `✅ Ollama connected\n🔢 Available Models: ${data.models && data.models.length || 0}\n⚙️ Endpoint: ${endpoint}`
                }));
              } else if (data.success) {
                // Custom API success
                setTestResults(prev => ({ 
                  ...prev, 
                  [service]: 'success',
                  [`${service}_details`]: `✅ ${data.message}\n🤖 Model: ${data.model}\n💬 Test Response: "${data.response && data.response.substring(0, 80) || 'No response'}..."\n📊 Response Time: ${data.response_time && data.response_time.toFixed(2) || 0}s\n🔢 Available Models: ${data.available_models && data.available_models.length || 0}\n⚙️ Dual Profiles: ${Object.keys(data.dual_profiles || {}).join(', ')}`
                }));
              } else {
                // Custom API but failed
                setTestResults(prev => ({ 
                  ...prev, 
                  [service]: 'warning',
                  [`${service}_details`]: `⚠️ ${data.error}\n💡 ${data.suggestion || 'Check Local LLM API service'}`
                }));
              }
              success = true;
              break;
            } else {
              lastError = `HTTP ${response.status}: ${response.statusText}`;
            }
          } catch (err) {
            lastError = err.message;
            continue;
          }
        }
        
        if (!success) {
          throw new Error(`All endpoints failed. Last error: ${lastError}`);
        }

      } else {
        // Use existing backend API for other services
        let requestBody;
        if (service === 'local-llm') {
          // Send localLLM settings for local-llm test
          requestBody = JSON.stringify({ localLLM: settings.localLLM });
        } else {
          // Send API settings for other services
          requestBody = JSON.stringify(settings.apis);
        }
        
        const response = await fetch(`http://localhost:8003/api/test/${service}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: requestBody
        });
        
        const result = await response.json();
        setTestResults(prev => ({ 
          ...prev, 
          [service]: result.success ? 'success' : 'failed',
          [`${service}_details`]: result.details || result.error
        }));
      }
    } catch (err) {
      setTestResults(prev => ({ 
        ...prev, 
        [service]: 'failed',
        [`${service}_details`]: err.message
      }));
    }
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const getDefaultPrompt = (agentId) => {
    const defaultPrompts = {
      alden: "You are Alden, a highly capable AI assistant and productivity companion. You help users with their daily tasks, provide thoughtful insights, and maintain a friendly, professional demeanor. You excel at understanding context and providing relevant, actionable advice.",
      alice: "You are Alice, a cognitive-behavioral analysis specialist. You focus on analytical thinking, problem-solving, and optimization. You help users break down complex problems, identify patterns, and develop systematic approaches to challenges.",
      core: "You are the Core orchestration system, responsible for managing multi-agent interactions and coordinating complex workflows."
    };
    return defaultPrompts[agentId] || "";
  };

  const startLocalLLMService = async () => {
    setTestResults(prev => ({ 
      ...prev, 
      'local-llm': 'testing',
      'local-llm_details': 'Starting Local LLM service...'
    }));

    try {
      // Check if Local LLM API is running
      const response = await fetch('http://localhost:8001/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setServiceStatus({
          isRunning: data.ollama_connected,
          lastCheck: new Date().toISOString(),
          error: data.ollama_connected ? null : 'Ollama backend not connected'
        });
        setTestResults(prev => ({ 
          ...prev, 
          'local-llm': data.ollama_connected ? 'success' : 'warning',
          'local-llm_details': data.ollama_connected 
            ? `✅ Local LLM API running\n🔌 Ollama connected\n📦 ${data.models_available} models available`
            : '⚠️ Local LLM API running but Ollama not connected\n💡 Ensure Ollama is running: ollama serve'
        }));
      } else {
        throw new Error(`Local LLM API not responding: HTTP ${response.status}`);
      }
    } catch (error) {
      setServiceStatus({
        isRunning: false,
        lastCheck: new Date().toISOString(),
        error: error.message
      });
      setTestResults(prev => ({ 
        ...prev, 
        'local-llm': 'failed',
        'local-llm_details': `❌ Failed to connect to Local LLM API\n🔧 ${error.message}\n💡 Ensure Local LLM API is running on port 8001`
      }));
    }
  };

  const stopLocalLLMService = async () => {
    setServiceStatus({
      isRunning: false,
      lastCheck: new Date().toISOString(),
      error: null
    });
    setTestResults(prev => ({ 
      ...prev, 
      'local-llm': 'warning',
      'local-llm_details': 'Service management not implemented in this version'
    }));
  };

  const restartLocalLLMService = async () => {
    setTestResults(prev => ({ 
      ...prev, 
      'local-llm': 'testing',
      'local-llm_details': 'Restarting service...'
    }));
    
    await stopLocalLLMService();
    setTimeout(() => {
      startLocalLLMService();
    }, 2000);
  };

  const checkServiceStatus = async () => {
    setServiceStatus(prev => ({ ...prev, error: null }));
    
    try {
      // Check Local LLM API service
      const response = await fetch('http://localhost:8001/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setServiceStatus({
          isRunning: data.connected,
          lastCheck: new Date().toISOString(),
          error: data.connected ? null : 'Ollama service not connected',
          details: {
            models: data.available_models,
            version: data.version,
            profiles: data.dual_profile_config
          }
        });
        setTestResults(prev => ({ 
          ...prev, 
          'local-llm': 'success',
          'local-llm_details': `Service running: ${data.version || 'Version unknown'}`
        }));
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      setServiceStatus({
        isRunning: false,
        lastCheck: new Date().toISOString(),
        error: error.message
      });
      setTestResults(prev => ({ 
        ...prev, 
        'local-llm': 'failed',
        'local-llm_details': `Service check failed: ${error.message}`
      }));
    }
  };

  const fetchAvailableModels = async () => {
    setFetchingModels(true);
    try {
      // Try multiple endpoints for model fetching
      const endpoints = [
        'http://localhost:11434/api/tags',  // Ollama
        'http://localhost:8001/api/models', // Custom API
        'http://localhost:1234/v1/models'   // LM Studio
      ];
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint);
          if (response.ok) {
            const data = await response.json();
            
            let models = [];
            if (endpoint.includes('ollama')) {
              models = data.models || [];
            } else if (endpoint.includes('8001')) {
              models = data.available_models || [];
            } else if (endpoint.includes('1234')) {
              models = data.data || [];
            }
            
            setAvailableModels(models);
            break;
          }
        } catch (err) {
          console.warn(`Failed to fetch from ${endpoint}:`, err);
        }
      }
    } catch (err) {
      console.error('Failed to fetch available models:', err);
    } finally {
      setFetchingModels(false);
    }
  };

  const detectSystemSpecs = async () => {
    try {
      // Get system specs for model recommendations
      const response = await fetch('http://localhost:8001/api/system-specs');
      if (response.ok) {
        const specs = await response.json();
        setSystemSpecs(specs);
        
        // Generate recommended models based on system specs
        const recommendations = generateModelRecommendations(specs);
        setRecommendedModels(recommendations);
      }
    } catch (err) {
      console.warn('Failed to detect system specs:', err);
      // Default specs for fallback
      setSystemSpecs({ ram: 16, gpu: false });
      setRecommendedModels([
        { name: 'llama3.2:3b', reason: 'Lightweight and efficient' },
        { name: 'llama3.1:8b', reason: 'Balanced performance' }
      ]);
    }
  };

  const generateModelRecommendations = (specs) => {
    const recommendations = [];
    
    // Low-end recommendations (< 8GB RAM)
    if (specs.ram < 8) {
      recommendations.push(
        { name: 'llama3.2:1b', reason: 'Ultra-light for low RAM systems', starred: true },
        { name: 'tinyllama:1.1b', reason: 'Minimal resource usage' }
      );
    }
    // Mid-range recommendations (8-16GB RAM)
    else if (specs.ram >= 8 && specs.ram < 32) {
      recommendations.push(
        { name: 'llama3.2:3b', reason: 'Great balance of speed and capability', starred: true },
        { name: 'llama3.1:8b', reason: 'Enhanced reasoning capabilities' },
        { name: 'mistral:7b', reason: 'Excellent for coding tasks' }
      );
    }
    // High-end recommendations (32GB+ RAM)
    else {
      recommendations.push(
        { name: 'llama3.1:8b', reason: 'Optimal for most tasks', starred: true },
        { name: 'llama3.1:70b', reason: 'Top-tier performance' },
        { name: 'codellama:34b', reason: 'Superior code generation' }
      );
    }
    
    // Add GPU-specific recommendations
    if (specs.gpu) {
      recommendations.push(
        { name: 'llama3.2:3b-instruct-q4_0', reason: 'GPU-optimized version', starred: specs.ram < 16 }
      );
    }
    
    return recommendations;
  };

  const repairWebSocketConnection = async () => {
    try {
      // Attempt to reconnect WebSocket services
      const response = await fetch('http://localhost:8001/api/websocket/repair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setSuccessMessage('✅ WebSocket connection repaired successfully!');
        // Retry fetching models after repair
        setTimeout(() => {
          fetchAvailableModels();
          checkServiceStatus();
        }, 1000);
      } else {
        throw new Error(`Repair failed: ${response.statusText}`);
      }
    } catch (err) {
      setError(`WebSocket repair failed: ${err.message}`);
    }
  };

  const renderWebSocketFallback = () => {
    const hasConnectionIssues = !serviceStatus.isRunning || serviceStatus.error;
    const noModelsAvailable = !fetchingModels && availableModels.length === 0;
    
    if (!hasConnectionIssues && !noModelsAvailable) return null;
    
    return (
      <div className="websocket-fallback">
        <div className="fallback-header">
          <span className="fallback-icon">⚠️</span>
          <strong>Connection Issues Detected</strong>
        </div>
        <div className="fallback-content">
          <p>Local LLM service appears to be unavailable. This could be due to:</p>
          <ul>
            <li>WebSocket connection issues</li>
            <li>Service not running on port 8001</li>
            <li>Network connectivity problems</li>
          </ul>
          <div className="fallback-actions">
            <button 
              onClick={() => repairWebSocketConnection()}
              className="action-btn warning"
            >
              🔧 Repair WebSocket Connection
            </button>
            <button 
              onClick={() => fetchAvailableModels()}
              className="action-btn info"
            >
              🔄 Retry Model Fetch
            </button>
            <button 
              onClick={() => checkServiceStatus()}
              className="action-btn primary"
            >
              📡 Check Service Status
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderModelDropdown = (profile, profileType) => {
    const currentModel = settings.localLLM.profiles[profileType].model;
    const displayModels = availableModels.length > 0 ? availableModels : [
      { name: 'llama3.2:3b' },
      { name: 'llama3.1:8b' },
      { name: 'mistral:7b' },
      { name: 'codellama:7b' }
    ];
    
    return (
      <div className="setting-group">
        <label>Model Selection</label>
        <select 
          value={currentModel}
          onChange={(e) => updateSetting('localLLM', 'profiles', {
            ...settings.localLLM.profiles,
            [profileType]: { ...settings.localLLM.profiles[profileType], model: e.target.value }
          })}
          disabled={!settings.localLLM.enabled || !settings.localLLM.profiles[profileType].enabled}
        >
          {displayModels.map(model => {
            const modelName = model.name || model.id || model;
            const isRecommended = recommendedModels.some(rec => rec.name === modelName);
            const recommendation = recommendedModels.find(rec => rec.name === modelName);
            
            return (
              <option key={modelName} value={modelName}>
                {recommendation?.starred ? '⭐ ' : ''}{modelName}
                {isRecommended ? ` (${recommendation.reason})` : ''}
              </option>
            );
          })}
        </select>
        {fetchingModels && (
          <div className="setting-description">
            🔄 Fetching available models...
          </div>
        )}
        {!fetchingModels && availableModels.length === 0 && (
          <div className="setting-description">
            ⚠️ No models detected. Check your Local LLM service.
          </div>
        )}
      </div>
    );
  };

  const renderSystemRecommendations = () => {
    if (recommendedModels.length === 0) return null;
    
    return (
      <div className="setting-group">
        <label>System Recommendations</label>
        <div className="system-recommendations">
          <div className="system-specs">
            💻 System: {systemSpecs.ram}GB RAM {systemSpecs.gpu ? '• GPU Available' : '• CPU Only'}
          </div>
          {recommendedModels.map(rec => (
            <div key={rec.name} className="recommendation-item">
              <span className="model-name">
                {rec.starred ? '⭐ ' : ''}{rec.name}
              </span>
              <span className="model-reason">{rec.reason}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderGeneralSettings = () => (
    <div className="settings-section">
      <h3>General Settings</h3>
      
      <div className="setting-group">
        <label>Theme</label>
        <select 
          value={settings.general.theme} 
          onChange={(e) => updateSetting('general', 'theme', e.target.value)}
        >
          <option value="starcraft">StarCraft</option>
          <option value="dark">Dark</option>
          <option value="light">Light</option>
        </select>
      </div>

      <div className="setting-group">
        <label>Startup Module</label>
        <select 
          value={settings.general.startupModule} 
          onChange={(e) => updateSetting('general', 'startupModule', e.target.value)}
        >
          <option value="alden">Alden</option>
          <option value="alice">Alice</option>
          <option value="core">Core</option>
          <option value="vault">Vault</option>
        </select>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.general.autoSave}
            onChange={(e) => updateSetting('general', 'autoSave', e.target.checked)}
          />
          Auto-save sessions
        </label>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.general.notifications}
            onChange={(e) => updateSetting('general', 'notifications', e.target.checked)}
          />
          Enable notifications
        </label>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.general.voiceEnabled}
            onChange={(e) => updateSetting('general', 'voiceEnabled', e.target.checked)}
          />
          Voice interface enabled
        </label>
      </div>
    </div>
  );

  const renderApiSettings = () => (
    <div className="settings-section">
      <h3>API Configuration</h3>
      
      <div className="setting-group">
        <label>Google AI Studio Key</label>
        <div className="input-with-test">
          <input 
            type="password" 
            value={settings.apis.googleAiKey}
            onChange={(e) => updateSetting('apis', 'googleAiKey', e.target.value)}
            placeholder="Enter your Google AI Studio API key"
          />
          <button 
            onClick={() => testConnection('google-ai')}
            className={`test-btn ${testResults['google-ai'] || ''}`}
            disabled={testResults['google-ai'] === 'testing'}
          >
            {testResults['google-ai'] === 'testing' ? 'Testing...' : 'Test'}
          </button>
        </div>
        {testResults['google-ai_details'] && (
          <div className={`test-result ${testResults['google-ai']}`}>
            {testResults['google-ai_details']}
          </div>
        )}
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.claudeCode.enabled}
            onChange={(e) => updateSetting('claudeCode', 'enabled', e.target.checked)}
          />
          Enable Claude Code CLI Integration
        </label>
      </div>

      {settings.claudeCode.enabled && (
        <div className="setting-group">
          <label>Claude Code CLI Path (optional - auto-detects if empty)</label>
          <div className="input-with-test">
            <input 
              type="text" 
              value={settings.claudeCode.cliPath}
              onChange={(e) => updateSetting('claudeCode', 'cliPath', e.target.value)}
              placeholder="Auto-detect (leave empty) or /usr/local/bin/claude-code"
            />
            <button 
              onClick={() => testConnection('claude-code')}
              className={`test-btn ${testResults['claude-code'] || ''}`}
              disabled={testResults['claude-code'] === 'testing'}
            >
              {testResults['claude-code'] === 'testing' ? 'Testing...' : 'Test CLI'}
            </button>
          </div>
          <div className="setting-help">
            💡 Claude Code is a CLI tool, not an API - no key required!
          </div>
          {testResults['claude-code_details'] && (
            <div className={`test-result ${testResults['claude-code']}`}>
              {testResults['claude-code_details']}
            </div>
          )}
        </div>
      )}

      <div className="setting-group">
        <label>Ollama URL</label>
        <div className="input-with-test">
          <input 
            type="text" 
            value={settings.apis.ollamaUrl}
            onChange={(e) => updateSetting('apis', 'ollamaUrl', e.target.value)}
            placeholder="http://localhost:11434"
          />
          <button 
            onClick={() => testConnection('ollama')}
            className={`test-btn ${testResults['ollama'] || ''}`}
            disabled={testResults['ollama'] === 'testing'}
          >
            {testResults['ollama'] === 'testing' ? 'Testing...' : 'Test'}
          </button>
        </div>
        {testResults['ollama_details'] && (
          <div className={`test-result ${testResults['ollama']}`}>
            {testResults['ollama_details']}
          </div>
        )}
      </div>
    </div>
  );

  const renderLocalLLMSettings = () => {
    // Safety check for profiles structure
    if (!settings.localLLM.profiles || !settings.localLLM.profiles.low || !settings.localLLM.profiles.mid) {
      return (
        <div className="settings-section">
          <h3>Local LLM Configuration</h3>
          <div className="error-message">
            Loading Local LLM settings... Please refresh if this persists.
          </div>
        </div>
      );
    }
    
    return (
    <div className="settings-section">
      <h3>Local LLM Configuration</h3>
      
      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.localLLM.enabled}
            onChange={(e) => updateSetting('localLLM', 'enabled', e.target.checked)}
          />
          Enable Local LLM
        </label>
        <div className="setting-description">
          Enable local language model integration for offline AI capabilities
        </div>
      </div>

      <div className="setting-group">
        <label>Provider</label>
        <select 
          value={settings.localLLM.provider} 
          onChange={(e) => updateSetting('localLLM', 'provider', e.target.value)}
          disabled={!settings.localLLM.enabled}
        >
          <option value="ollama">Ollama</option>
          <option value="lm-studio">LM Studio</option>
          <option value="text-generation-webui">Text Generation WebUI</option>
          <option value="custom">Custom Endpoint</option>
        </select>
      </div>

      <div className="setting-group">
        <label>Endpoint URL</label>
        <div className="input-with-test">
          <input 
            type="text" 
            value={settings.localLLM.endpoint}
            onChange={(e) => updateSetting('localLLM', 'endpoint', e.target.value)}
            placeholder="http://localhost:11434"
            disabled={!settings.localLLM.enabled}
          />
          <button 
            onClick={() => testConnection('local-llm')}
            className={`test-btn ${testResults['local-llm'] || ''}`}
            disabled={testResults['local-llm'] === 'testing' || !settings.localLLM.enabled}
          >
            {testResults['local-llm'] === 'testing' ? 'Testing...' : 'Test'}
          </button>
        </div>
        {testResults['local-llm_details'] && (
          <div className={`test-result ${testResults['local-llm']}`}>
            {testResults['local-llm_details']}
          </div>
        )}
      </div>

      {renderSystemRecommendations()}

      {renderWebSocketFallback()}

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.localLLM.dualLLMMode}
            onChange={(e) => updateSetting('localLLM', 'dualLLMMode', e.target.checked)}
            disabled={!settings.localLLM.enabled}
          />
          Enable Dual LLM Mode
        </label>
        <div className="setting-description">
          Use two different models for different complexity levels and roles
        </div>
      </div>

      {settings.localLLM.dualLLMMode && (
        <>
          {/* Low Profile LLM */}
          <div className="llm-profile-section">
            <h4>Low Profile LLM (2-3B Parameters)</h4>
            <div className="profile-badge low">Fast • Efficient • Routing</div>
            
            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.profiles.low.enabled}
                  onChange={(e) => updateSetting('localLLM', 'profiles', {
                    ...settings.localLLM.profiles,
                    low: { ...settings.localLLM.profiles.low, enabled: e.target.checked }
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Enable Low Profile Model
              </label>
            </div>

            {renderModelDropdown(settings.localLLM.profiles.low, 'low')}

            <div className="setting-group">
              <label>Temperature</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                value={settings.localLLM.profiles.low.temperature}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  low: { ...settings.localLLM.profiles.low, temperature: parseFloat(e.target.value) }
                })}
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.low.enabled}
              />
              <span className="slider-value">{settings.localLLM.profiles.low.temperature}</span>
            </div>

            <div className="setting-group">
              <label>Context Length</label>
              <input 
                type="number" 
                value={settings.localLLM.profiles.low.contextLength}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  low: { ...settings.localLLM.profiles.low, contextLength: parseInt(e.target.value) }
                })}
                min="1024" 
                max="32768"
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.low.enabled}
              />
              <div className="setting-description">
                Smaller context window for efficiency
              </div>
            </div>

            <div className="setting-group">
              <label>Assigned Roles</label>
              <div className="role-tags">
                {settings.localLLM.profiles.low.roles.map(role => (
                  <span key={role} className="role-tag low">{role}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Mid Profile LLM */}
          <div className="llm-profile-section">
            <h4>Mid Profile LLM (7-9B Parameters)</h4>
            <div className="profile-badge mid">Balanced • Capable • Reasoning</div>
            
            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.profiles.mid.enabled}
                  onChange={(e) => updateSetting('localLLM', 'profiles', {
                    ...settings.localLLM.profiles,
                    mid: { ...settings.localLLM.profiles.mid, enabled: e.target.checked }
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Enable Mid Profile Model
              </label>
            </div>

            {renderModelDropdown(settings.localLLM.profiles.mid, 'mid')}

            <div className="setting-group">
              <label>Temperature</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                value={settings.localLLM.profiles.mid.temperature}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  mid: { ...settings.localLLM.profiles.mid, temperature: parseFloat(e.target.value) }
                })}
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.mid.enabled}
              />
              <span className="slider-value">{settings.localLLM.profiles.mid.temperature}</span>
            </div>

            <div className="setting-group">
              <label>Context Length</label>
              <input 
                type="number" 
                value={settings.localLLM.profiles.mid.contextLength}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  mid: { ...settings.localLLM.profiles.mid, contextLength: parseInt(e.target.value) }
                })}
                min="1024" 
                max="131072"
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.mid.enabled}
              />
              <div className="setting-description">
                Larger context window for complex reasoning
              </div>
            </div>

            <div className="setting-group">
              <label>Assigned Roles</label>
              <div className="role-tags">
                {settings.localLLM.profiles.mid.roles.map(role => (
                  <span key={role} className="role-tag mid">{role}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Role Assignment Section */}
          <div className="role-assignment-section">
            <h4>Role Assignment</h4>
            <div className="setting-description">
              Assign specific roles to different LLM profiles for optimal performance
            </div>
            
            {Object.entries(settings.localLLM.roleAssignments).map(([role, assignedProfile]) => (
              <div key={role} className="role-assignment" title={`${role} is currently assigned to ${assignedProfile} profile`}>
                <span className="role-name">{role.replace('_', ' ')}</span>
                <select
                  value={assignedProfile}
                  onChange={(e) => updateSetting('localLLM', 'roleAssignments', {
                    ...settings.localLLM.roleAssignments,
                    [role]: e.target.value
                  })}
                  disabled={!settings.localLLM.enabled}
                  className="role-select"
                >
                  <option value="low">Low Profile</option>
                  <option value="mid">Mid Profile</option>
                </select>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.localLLM.streaming}
            onChange={(e) => updateSetting('localLLM', 'streaming', e.target.checked)}
            disabled={!settings.localLLM.enabled}
          />
          Enable Streaming
        </label>
        <div className="setting-description">
          Stream responses in real-time for better user experience
        </div>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.localLLM.autoStart}
            onChange={(e) => updateSetting('localLLM', 'autoStart', e.target.checked)}
            disabled={!settings.localLLM.enabled}
          />
          Auto-start Service
        </label>
        <div className="setting-description">
          Automatically start the local LLM service when Hearthlink launches
        </div>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.localLLM.fallbackEnabled}
            onChange={(e) => updateSetting('localLLM', 'fallbackEnabled', e.target.checked)}
            disabled={!settings.localLLM.enabled}
          />
          Enable Fallback
        </label>
        <div className="setting-description">
          Fallback to other backends if local LLM fails
        </div>
      </div>

      <div className="setting-group">
        <label>Health Check Interval (ms)</label>
        <input 
          type="number" 
          value={settings.localLLM.healthCheckInterval}
          onChange={(e) => updateSetting('localLLM', 'healthCheckInterval', parseInt(e.target.value))}
          min="5000" 
          max="300000"
          disabled={!settings.localLLM.enabled}
        />
        <div className="setting-description">
          How often to check local LLM service health
        </div>
      </div>

      <div className="setting-group">
        <label>Service Status</label>
        <div className="service-status">
          <div className={`status-indicator ${serviceStatus.isRunning ? 'running' : 'stopped'}`}>
            <div className="status-dot"></div>
            <span className="status-text">
              {serviceStatus.isRunning ? 'Running' : 'Stopped'}
            </span>
            {serviceStatus.lastCheck && (
              <span className="status-timestamp">
                Last checked: {new Date(serviceStatus.lastCheck).toLocaleTimeString()}
              </span>
            )}
          </div>
          {serviceStatus.error && (
            <div className="status-error">
              {serviceStatus.error}
            </div>
          )}
        </div>
        <div className="action-buttons">
          <button 
            onClick={() => startLocalLLMService()}
            className="action-btn primary"
            disabled={!settings.localLLM.enabled}
          >
            Start Service
          </button>
          <button 
            onClick={() => stopLocalLLMService()}
            className="action-btn secondary"
            disabled={!settings.localLLM.enabled}
          >
            Stop Service
          </button>
          <button 
            onClick={() => restartLocalLLMService()}
            className="action-btn warning"
            disabled={!settings.localLLM.enabled}
          >
            Restart Service
          </button>
          <button 
            onClick={() => checkServiceStatus()}
            className="action-btn info"
            disabled={!settings.localLLM.enabled}
          >
            Check Status
          </button>
        </div>
      </div>
    </div>
  );
  };

  const renderVoiceSettings = () => (
    <div className="settings-section">
      <h3>Voice Configuration</h3>
      
      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.voice.enabled}
            onChange={(e) => updateSetting('voice', 'enabled', e.target.checked)}
          />
          Voice interface enabled
        </label>
      </div>

      <div className="setting-group">
        <label>Voice Sensitivity</label>
        <input 
          type="range" 
          min="0.1" 
          max="1.0" 
          step="0.1"
          value={settings.voice.sensitivity}
          onChange={(e) => updateSetting('voice', 'sensitivity', parseFloat(e.target.value))}
        />
        <span className="range-value">{settings.voice.sensitivity}</span>
      </div>

      <div className="setting-group">
        <label>Wake Word</label>
        <input 
          type="text" 
          value={settings.voice.wakeWord}
          onChange={(e) => updateSetting('voice', 'wakeWord', e.target.value)}
          placeholder="alden"
        />
      </div>

      <div className="setting-group">
        <label>Routing Mode</label>
        <select 
          value={settings.voice.routingMode} 
          onChange={(e) => updateSetting('voice', 'routingMode', e.target.value)}
        >
          <option value="smart">Smart Routing</option>
          <option value="manual">Manual Selection</option>
          <option value="direct">Direct Command</option>
        </select>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="settings-section">
      <h3>Security Settings</h3>
      
      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.security.encryptionEnabled}
            onChange={(e) => updateSetting('security', 'encryptionEnabled', e.target.checked)}
          />
          Enable data encryption
        </label>
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.security.auditLogging}
            onChange={(e) => updateSetting('security', 'auditLogging', e.target.checked)}
          />
          Enable audit logging
        </label>
      </div>

      <div className="setting-group">
        <label>Session Timeout (minutes)</label>
        <input 
          type="number" 
          min="5" 
          max="480"
          value={settings.security.sessionTimeout}
          onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
        />
      </div>

      <div className="setting-group">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={settings.security.autoLock}
            onChange={(e) => updateSetting('security', 'autoLock', e.target.checked)}
          />
          Auto-lock on idle
        </label>
      </div>
    </div>
  );

  const renderAgentPersonaSettings = () => (
    <div className="settings-section">
      <h3>Agent Persona Management</h3>
      <div className="setting-description">
        Configure and customize agent personas for different interaction styles and capabilities.
      </div>
      
      {Object.entries(settings.agents).map(([agentId, agent]) => (
        <div key={agentId} className="agent-persona-card">
          <div className="agent-header">
            <div className="agent-info">
              <h4 className="agent-name">{agentId.charAt(0).toUpperCase() + agentId.slice(1)}</h4>
              <div className="agent-status">
                <span className={`status-indicator ${agent.enabled ? 'enabled' : 'disabled'}`}>
                  {agent.enabled ? 'Active' : 'Disabled'}
                </span>
                <span className="agent-priority">Priority: {agent.priority}</span>
              </div>
            </div>
            <div className="agent-controls">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={agent.enabled}
                  onChange={(e) => updateSetting('agents', agentId, {
                    ...agent,
                    enabled: e.target.checked
                  })}
                />
                Enable
              </label>
            </div>
          </div>

          <div className="agent-prompt-section">
            <label>Agent Persona Prompt</label>
            {agent.isDynamic ? (
              <div className="dynamic-prompt-notice">
                <div className="notice-icon">🔄</div>
                <div className="notice-content">
                  <strong>Dynamic Agent</strong>
                  <p>Mimic adapts its persona based on context and user needs. The prompt is generated dynamically during interactions.</p>
                </div>
              </div>
            ) : agent.isHardCoded ? (
              <div className="hardcoded-prompt-notice">
                <div className="notice-icon">🔒</div>
                <div className="notice-content">
                  <strong>Hard-Coded Agent</strong>
                  <p>Sentry's persona is optimized for system monitoring and security. The prompt is hard-coded for maximum effectiveness.</p>
                </div>
              </div>
            ) : (
              <textarea
                value={agent.prompt}
                onChange={(e) => updateSetting('agents', agentId, {
                  ...agent,
                  prompt: e.target.value
                })}
                rows="4"
                className="prompt-textarea"
                placeholder="Enter the persona prompt for this agent..."
              />
            )}
          </div>

          {(agentId === 'alden' || agentId === 'alice') && (
            <div className="prompt-actions">
              <button 
                onClick={() => updateSetting('agents', agentId, {
                  ...agent,
                  prompt: getDefaultPrompt(agentId)
                })}
                className="action-btn secondary"
              >
                Reset to Default
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const tabs = [
    { id: 'general', label: 'General', component: renderGeneralSettings },
    { id: 'localLLM', label: 'Local LLM', component: renderLocalLLMSettings },
    { id: 'agents', label: 'Agent Personas', component: renderAgentPersonaSettings },
    { id: 'voice', label: 'Voice', component: renderVoiceSettings },
    { id: 'security', label: 'Security', component: renderSecuritySettings }
  ];

  if (!isVisible) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>HEARTHLINK SETTINGS</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="settings-content">
          <div className="settings-tabs">
            {tabs.map(tab => (
              <button 
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          
          <div className="settings-panel">
            {tabs.find(tab => tab.id === activeTab)?.component()}
          </div>
        </div>
        
        <div className="settings-footer">
          {error && <div className="error-message">{error}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}
          <div className="settings-actions">
            <button className="cancel-btn" onClick={onClose}>Cancel</button>
            <button 
              className="save-btn" 
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                saveSettings();
              }}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsManager;
