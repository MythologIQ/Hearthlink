import React, { useState, useEffect } from 'react';
import './SettingsManager.css';
import { Vault } from '../vault/vault.js';

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
        spriteMode: true, // Sprite Light Architecture
        profiles: {
          micro: {
            enabled: true,
            model: 'llama3.2:3b',
            parameterRange: '2-3B',
            type: 'micro',
            roles: ['sprite_routing', 'quick_responses', 'simple_tasks', 'voice_commands'],
            temperature: 0.7,
            contextLength: 16384,
            priority: 1,
            alwaysLoaded: true,
            description: 'Always-loaded lightweight model for Sprite Light assistants'
          },
          heavy: {
            enabled: true,
            model: 'llama3:latest',
            parameterRange: '7-8B',
            type: 'heavy',
            roles: ['reasoning', 'coding', 'complex_tasks', 'analysis'],
            temperature: 0.7,
            contextLength: 32768,
            priority: 2,
            hotSwappable: true,
            description: 'Hot-swappable reasoning engine for complex tasks'
          }
        },
        roleAssignments: {
          sprite_routing: 'micro',
          voice_commands: 'micro',
          quick_responses: 'micro',
          simple_tasks: 'micro',
          reasoning: 'heavy',
          coding: 'heavy',
          complex_tasks: 'heavy',
          analysis: 'heavy'
        },
        spriteConfig: {
          confidenceThreshold: 0.75,
          escalationEnabled: true,
          maxRetries: 2,
          swapTimeout: 10000,
          memoryIsolation: true
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
  
  // Sprite Management state variables (moved from renderSpriteManagementSettings)
  const [spriteStatus, setSpriteStatus] = useState(null);
  const [powerMetrics, setPowerMetrics] = useState(null);
  const [spriteLoading, setSpriteLoading] = useState(false);

  // Move sprite loading functions to top level to avoid hook order issues
  const loadSpriteStatus = async () => {
    setSpriteLoading(true);
    try {
      // Import sprite service dynamically to avoid circular dependencies
      const { default: spriteService } = await import('../services/SpriteService.js');
      
      const results = await Promise.allSettled([
        spriteService.getStatus(),
        spriteService.getPowerStatus(),
        spriteService.getTelemetryReport()
      ]);
      
      // Handle partial failures gracefully
      const [statusResult, powerResult, telemetryResult] = results;
      
      const status = statusResult.status === 'fulfilled' ? statusResult.value : {
        error: statusResult.reason?.message || 'Service unavailable',
        initialized: false
      };
      
      const power = powerResult.status === 'fulfilled' ? powerResult.value : {
        error: powerResult.reason?.message || 'Power monitoring unavailable',
        currentState: { 
          memoryPressure: 'unknown',
          isThrottling: false,
          thermalMonitoringAvailable: false
        }
      };
      
      const telemetry = telemetryResult.status === 'fulfilled' ? telemetryResult.value : {
        error: telemetryResult.reason?.message || 'Telemetry unavailable'
      };
      
      setSpriteStatus(status);
      setPowerMetrics({ ...power, telemetry });
      
      // Show implementation warnings to user
      if (statusResult.status === 'rejected' || powerResult.status === 'rejected' || telemetryResult.status === 'rejected') {
        setError('Some Sprite Engine features are not fully implemented and may show limited functionality.');
      }
      
    } catch (error) {
      console.error('Failed to load sprite status:', error);
      setSpriteStatus({ 
        error: `Feature not implemented: Sprite Engine not available - ${error.message}`,
        initialized: false
      });
    }
    setSpriteLoading(false);
  };

  const handlePowerBudgetUpdate = async (field, value) => {
    try {
      const { default: spriteService } = await import('../services/SpriteService.js');
      await spriteService.updatePowerBudget({ [field]: value });
      await loadSpriteStatus(); // Refresh
      setSuccessMessage('Power budget updated successfully');
    } catch (error) {
      setError(`Failed to update power budget: ${error.message}`);
    }
  };

  // Use effect for sprite management only when on sprites tab
  useEffect(() => {
    if (activeTab === 'sprites') {
      loadSpriteStatus();
      // Auto-refresh every 10 seconds when tab is active
      const interval = setInterval(loadSpriteStatus, 10000);
      return () => clearInterval(interval);
    }
  }, [activeTab]);

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
      const vault = new Vault();
      const savedSettings = await vault.retrieve('settings');
      
      if (savedSettings) {
        // Merge saved settings with defaults to ensure new structure is preserved
        setSettings(prev => {
          const merged = { ...prev };
          Object.keys(savedSettings).forEach(key => {
            if (typeof prev[key] === 'object' && typeof savedSettings[key] === 'object') {
              merged[key] = { ...prev[key], ...savedSettings[key] };
            } else {
              merged[key] = savedSettings[key];
            }
          });
          return merged;
        });
        console.log('Settings loaded from Vault:', savedSettings);
      } else {
        console.log('No saved settings found, using defaults');
      }
    } catch (err) {
      console.error('Failed to load settings from Vault:', err);
      setError('Failed to load settings');
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    setError('');
    setSuccessMessage('');
    
    try {
      console.log('SettingsManager - Saving settings to Vault:', settings);
      
      const vault = new Vault();
      await vault.store('settings', settings);
      
      // Also save to localStorage as a backup
      localStorage.setItem('hearthlinkSettings', JSON.stringify(settings));
      
      // Notify parent component
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
    if (!settings.localLLM.profiles || !settings.localLLM.profiles.micro || !settings.localLLM.profiles.heavy) {
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
            checked={settings.localLLM.spriteMode}
            onChange={(e) => updateSetting('localLLM', 'spriteMode', e.target.checked)}
            disabled={!settings.localLLM.enabled}
          />
          Enable Sprite Light Architecture
        </label>
        <div className="setting-description">
          Intelligent resource utilization with Micro-LLM sprites and hot-swappable Heavy-LLM reasoning engines
        </div>
      </div>

      {settings.localLLM.spriteMode && (
        <>
          {/* Micro-LLM Profile */}
          <div className="llm-profile-section">
            <h4>Micro-LLM - Sprite Light Assistants (2-3B Parameters)</h4>
            <div className="profile-badge micro">Always Loaded • Fast • Voice Commands • Routing</div>
            
            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.profiles.micro.enabled}
                  onChange={(e) => updateSetting('localLLM', 'profiles', {
                    ...settings.localLLM.profiles,
                    micro: { ...settings.localLLM.profiles.micro, enabled: e.target.checked }
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Enable Micro-LLM Sprites
              </label>
              <div className="setting-description">
                Always-loaded lightweight models for voice commands and simple tasks
              </div>
            </div>

            {renderModelDropdown(settings.localLLM.profiles.micro, 'micro')}

            <div className="setting-group">
              <label>Temperature</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                value={settings.localLLM.profiles.micro.temperature}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  micro: { ...settings.localLLM.profiles.micro, temperature: parseFloat(e.target.value) }
                })}
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.micro.enabled}
              />
              <span className="slider-value">{settings.localLLM.profiles.micro.temperature}</span>
            </div>

            <div className="setting-group">
              <label>Context Length</label>
              <input 
                type="number" 
                value={settings.localLLM.profiles.micro.contextLength}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  micro: { ...settings.localLLM.profiles.micro, contextLength: parseInt(e.target.value) }
                })}
                min="1024" 
                max="32768"
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.micro.enabled}
              />
              <div className="setting-description">
                Optimized for fast sprite responses and voice commands
              </div>
            </div>

            <div className="setting-group">
              <label>Assigned Roles</label>
              <div className="role-tags">
                {settings.localLLM.profiles.micro.roles.map(role => (
                  <span key={role} className="role-tag micro">{role.replace('_', ' ')}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Heavy-LLM Profile */}
          <div className="llm-profile-section">
            <h4>Heavy-LLM - Reasoning Engine (7-13B Parameters)</h4>
            <div className="profile-badge heavy">Hot-Swappable • Reasoning • Complex Tasks • Analysis</div>
            
            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.profiles.heavy.enabled}
                  onChange={(e) => updateSetting('localLLM', 'profiles', {
                    ...settings.localLLM.profiles,
                    heavy: { ...settings.localLLM.profiles.heavy, enabled: e.target.checked }
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Enable Heavy-LLM Reasoning Engine
              </label>
              <div className="setting-description">
                Hot-swappable models for complex reasoning, coding, and analysis tasks
              </div>
            </div>

            {renderModelDropdown(settings.localLLM.profiles.heavy, 'heavy')}

            <div className="setting-group">
              <label>Temperature</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                value={settings.localLLM.profiles.heavy.temperature}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  heavy: { ...settings.localLLM.profiles.heavy, temperature: parseFloat(e.target.value) }
                })}
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.heavy.enabled}
              />
              <span className="slider-value">{settings.localLLM.profiles.heavy.temperature}</span>
            </div>

            <div className="setting-group">
              <label>Context Length</label>
              <input 
                type="number" 
                value={settings.localLLM.profiles.heavy.contextLength}
                onChange={(e) => updateSetting('localLLM', 'profiles', {
                  ...settings.localLLM.profiles,
                  heavy: { ...settings.localLLM.profiles.heavy, contextLength: parseInt(e.target.value) }
                })}
                min="1024" 
                max="131072"
                disabled={!settings.localLLM.enabled || !settings.localLLM.profiles.heavy.enabled}
              />
              <div className="setting-description">
                Extended context for complex reasoning and analysis
              </div>
            </div>

            <div className="setting-group">
              <label>Assigned Roles</label>
              <div className="role-tags">
                {settings.localLLM.profiles.heavy.roles.map(role => (
                  <span key={role} className="role-tag heavy">{role.replace('_', ' ')}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Role Assignment Section */}
          <div className="role-assignment-section">
            <h4>Sprite Light Role Assignment</h4>
            <div className="setting-description">
              Assign specific roles to Micro-LLM sprites or Heavy-LLM reasoning engines
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
                  <option value="micro">Micro-LLM (Sprites)</option>
                  <option value="heavy">Heavy-LLM (Reasoning)</option>
                </select>
              </div>
            ))}
          </div>

          {/* Sprite Light Configuration */}
          <div className="sprite-config-section">
            <h4>Sprite Light Configuration</h4>
            <div className="setting-description">
              Advanced settings for model orchestration and hot-swapping
            </div>

            <div className="setting-group">
              <label>Confidence Threshold</label>
              <input 
                type="range" 
                min="0.5" 
                max="1.0" 
                step="0.05"
                value={settings.localLLM.spriteConfig.confidenceThreshold}
                onChange={(e) => updateSetting('localLLM', 'spriteConfig', {
                  ...settings.localLLM.spriteConfig,
                  confidenceThreshold: parseFloat(e.target.value)
                })}
                disabled={!settings.localLLM.enabled}
              />
              <span className="slider-value">{settings.localLLM.spriteConfig.confidenceThreshold}</span>
              <div className="setting-description">
                Escalate to Heavy-LLM when Sprite confidence drops below this threshold
              </div>
            </div>

            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.spriteConfig.escalationEnabled}
                  onChange={(e) => updateSetting('localLLM', 'spriteConfig', {
                    ...settings.localLLM.spriteConfig,
                    escalationEnabled: e.target.checked
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Enable Automatic Escalation
              </label>
              <div className="setting-description">
                Automatically escalate tasks from Sprites to Heavy-LLM when needed
              </div>
            </div>

            <div className="setting-group">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={settings.localLLM.spriteConfig.memoryIsolation}
                  onChange={(e) => updateSetting('localLLM', 'spriteConfig', {
                    ...settings.localLLM.spriteConfig,
                    memoryIsolation: e.target.checked
                  })}
                  disabled={!settings.localLLM.enabled}
                />
                Memory Isolation
              </label>
              <div className="setting-description">
                Clear memory and GPU context between model swaps (recommended for security)
              </div>
            </div>

            <div className="setting-group">
              <label>Swap Timeout (ms)</label>
              <input 
                type="number" 
                value={settings.localLLM.spriteConfig.swapTimeout}
                onChange={(e) => updateSetting('localLLM', 'spriteConfig', {
                  ...settings.localLLM.spriteConfig,
                  swapTimeout: parseInt(e.target.value)
                })}
                min="1000" 
                max="30000"
                step="1000"
                disabled={!settings.localLLM.enabled}
              />
              <div className="setting-description">
                Maximum time allowed for model hot-swapping
              </div>
            </div>
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

  const renderSpriteManagementSettings = () => {

    return (
      <div className="settings-section">
        <div className="settings-header">
          <h3>🎯 Sprite Light Architecture Management</h3>
          <button 
            onClick={loadSpriteStatus} 
            disabled={spriteLoading}
            className="refresh-btn"
          >
            {spriteLoading ? '⟳ Loading...' : '🔄 Refresh'}
          </button>
        </div>

        {/* System Status Overview */}
        <div className="setting-group">
          <h4>📊 System Status</h4>
          {spriteStatus ? (
            spriteStatus.error ? (
              <div className="status-error">
                ❌ Error: {spriteStatus.error}
              </div>
            ) : (
              <div className="status-grid">
                <div className="status-card">
                  <div className="status-label">Initialization</div>
                  <div className={`status-value ${spriteStatus.initialized ? 'success' : 'error'}`}>
                    {spriteStatus.initialized ? '✅ Active' : '❌ Not Initialized'}
                  </div>
                </div>
                
                <div className="status-card">
                  <div className="status-label">Active Sprites</div>
                  <div className="status-value">
                    🎯 {spriteStatus.activeSprites?.length || 0} sprites
                  </div>
                </div>
                
                <div className="status-card">
                  <div className="status-label">Loaded Engines</div>
                  <div className="status-value">
                    🔧 {spriteStatus.loadedEngines?.length || 0} engines
                  </div>
                </div>
                
                {powerMetrics && (
                  <div className="status-card">
                    <div className="status-label">Memory Usage</div>
                    <div className="status-value">
                      💾 {Math.round(powerMetrics.memoryUsage)}MB
                    </div>
                  </div>
                )}
              </div>
            )
          ) : (
            <div className="status-loading">Loading system status...</div>
          )}
        </div>

        {/* Power Management */}
        {powerMetrics && (
          <div className="setting-group">
            <h4>⚡ Power Budget Management</h4>
            
            <div className="power-metrics-grid">
              <div className="metric-card">
                <div className="metric-label">System Temperature</div>
                <div className={`metric-value ${powerMetrics.systemTemperature > 80 ? 'warning' : 'normal'}`}>
                  🌡️ {Math.round(powerMetrics.systemTemperature)}°C
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">GPU Temperature</div>
                <div className={`metric-value ${powerMetrics.gpuTemperature > 85 ? 'critical' : powerMetrics.gpuTemperature > 80 ? 'warning' : 'normal'}`}>
                  🎮 {Math.round(powerMetrics.gpuTemperature)}°C
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Memory Pressure</div>
                <div className={`metric-value ${powerMetrics.currentState.memoryPressure === 'critical' ? 'critical' : powerMetrics.currentState.memoryPressure === 'elevated' ? 'warning' : 'normal'}`}>
                  📊 {powerMetrics.currentState.memoryPressure}
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Thermal State</div>
                <div className={`metric-value ${powerMetrics.currentState.isThrottling ? 'warning' : 'normal'}`}>
                  {powerMetrics.currentState.isThrottling ? '🔥 Throttling' : 
                   powerMetrics.currentState.powerSaveMode ? '⚡ Power Save' : '✅ Normal'}
                </div>
              </div>
            </div>

            {/* Power Budget Controls */}
            <div className="power-controls">
              <div className="control-row">
                <label>Max Concurrent Models:</label>
                <input
                  type="number"
                  min="1"
                  max="4"
                  value={powerMetrics.budget?.maxConcurrentModels || 2}
                  onChange={(e) => handlePowerBudgetUpdate('maxConcurrentModels', parseInt(e.target.value))}
                  className="power-input"
                />
              </div>
              
              <div className="control-row">
                <label>Max Memory (MB):</label>
                <input
                  type="number"
                  min="8000"
                  max="32000"
                  step="1000"
                  value={powerMetrics.budget?.maxMemoryUsage || 16000}
                  onChange={(e) => handlePowerBudgetUpdate('maxMemoryUsage', parseInt(e.target.value))}
                  className="power-input"
                />
              </div>
              
              <div className="control-row">
                <label>Max Thermal Threshold (°C):</label>
                <input
                  type="number"
                  min="70"
                  max="95"
                  value={powerMetrics.budget?.maxThermalThreshold || 85}
                  onChange={(e) => handlePowerBudgetUpdate('maxThermalThreshold', parseInt(e.target.value))}
                  className="power-input"
                />
              </div>
            </div>
          </div>
        )}

        {/* Active Sprites */}
        {spriteStatus?.activeSprites && spriteStatus.activeSprites.length > 0 && (
          <div className="setting-group">
            <h4>🎯 Active Sprites</h4>
            <div className="sprites-list">
              {spriteStatus.activeSprites.map((sprite, index) => (
                <div key={index} className="sprite-card">
                  <div className="sprite-header">
                    <span className="sprite-name">{sprite.name}</span>
                    <span className={`sprite-status ${sprite.status}`}>
                      {sprite.status === 'active' ? '✅' : '⏸️'} {sprite.status}
                    </span>
                  </div>
                  <div className="sprite-details">
                    <div>ID: {sprite.id}</div>
                    <div>Loaded: {new Date(sprite.loadedAt).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loaded Engines */}
        {spriteStatus?.loadedEngines && spriteStatus.loadedEngines.length > 0 && (
          <div className="setting-group">
            <h4>🔧 Heavy-LLM Engines</h4>
            <div className="engines-list">
              {spriteStatus.loadedEngines.map((engine, index) => (
                <div key={index} className="engine-card">
                  <div className="engine-header">
                    <span className="engine-name">{engine.name}</span>
                    <span className={`engine-status ${engine.status}`}>
                      {engine.status === 'active' ? '🟢' : 
                       engine.status === 'loading' ? '🟡' : 
                       engine.status === 'unhealthy' ? '🔴' : '⚫'} {engine.status}
                    </span>
                  </div>
                  <div className="engine-details">
                    <div>Model: {engine.model}</div>
                    <div>Loaded: {new Date(engine.loadedAt).toLocaleTimeString()}</div>
                    {engine.loadDuration && (
                      <div>Load Time: {Math.round(engine.loadDuration)}ms</div>
                    )}
                    {engine.capabilities && (
                      <div>Capabilities: {engine.capabilities.join(', ')}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Telemetry Summary */}
        {powerMetrics?.telemetry && (
          <div className="setting-group">
            <h4>📈 Performance Telemetry</h4>
            <div className="telemetry-summary">
              <div className="telemetry-row">
                <span>Total Model Loads:</span>
                <span>{powerMetrics.telemetry.powerMetrics?.totalModelLoads || 0}</span>
              </div>
              <div className="telemetry-row">
                <span>Total Model Swaps:</span>
                <span>{powerMetrics.telemetry.powerMetrics?.totalModelSwaps || 0}</span>
              </div>
              <div className="telemetry-row">
                <span>Average Load Time:</span>
                <span>{Math.round(powerMetrics.telemetry.powerMetrics?.averageLoadTime || 0)}ms</span>
              </div>
              <div className="telemetry-row">
                <span>Peak Memory Usage:</span>
                <span>{Math.round(powerMetrics.telemetry.powerMetrics?.peakMemoryUsage || 0)}MB</span>
              </div>
              <div className="telemetry-row">
                <span>Session Uptime:</span>
                <span>{Math.round((powerMetrics.telemetry.powerMetrics?.sessionUptime || 0) / 1000)}s</span>
              </div>
            </div>
          </div>
        )}
        
        <div className="sprite-management-note">
          <p>
            <strong>📝 Note:</strong> The Sprite Light Architecture provides intelligent model routing 
            with automatic hot-swapping based on task complexity and power constraints. 
            Monitor thermal and memory metrics to optimize performance.
          </p>
        </div>

        {/* Implementation Status Warning */}
        <div className="implementation-status-warning">
          <h4>⚠️ Implementation Status</h4>
          <div className="status-items">
            <div className="status-item">
              <span className="status-icon">🔧</span>
              <div className="status-text">
                <strong>Model Loading:</strong> Requires Local LLM API at localhost:8001 with model load/unload endpoints
              </div>
            </div>
            <div className="status-item">
              <span className="status-icon">🌡️</span>
              <div className="status-text">
                <strong>Thermal Monitoring:</strong> Requires platform-specific system integration (not implemented)
              </div>
            </div>
            <div className="status-item">
              <span className="status-icon">💾</span>
              <div className="status-text">
                <strong>Memory Monitoring:</strong> Basic JavaScript heap monitoring only (platform APIs not implemented)
              </div>
            </div>
            <div className="status-item">
              <span className="status-icon">📊</span>
              <div className="status-text">
                <strong>Sentry Telemetry:</strong> Falls back to localStorage if Sentry SDK not available
              </div>
            </div>
            <div className="status-item">
              <span className="status-icon">🔐</span>
              <div className="status-text">
                <strong>Authentication:</strong> Secure mode authentication system not implemented
              </div>
            </div>
          </div>
          <p className="implementation-note">
            <strong>For Production:</strong> Replace these implementations with real system integrations 
            for full functionality. Current state provides UI and service layer structure.
          </p>
        </div>
      </div>
    );
  };

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
    { id: 'sprites', label: 'Sprite Management', component: renderSpriteManagementSettings },
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
