import React, { useState, useEffect, useRef } from 'react';
import './LocalLLMInterface.css';

const LocalLLMInterface = ({ isVisible, onClose }) => {
  // Core state management
  const [activeTab, setActiveTab] = useState('configuration');
  const [llmConfig, setLlmConfig] = useState({
    engine: 'ollama',
    base_url: 'http://localhost:11434',
    model: 'llama2',
    timeout: 30,
    max_retries: 3,
    temperature: 0.7,
    max_tokens: 2048,
    enable_retry: true,
    enable_circuit_breaker: true
  });
  
  // Connection state
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [availableModels, setAvailableModels] = useState([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  
  // Model selection state
  const [modelSelectorVisible, setModelSelectorVisible] = useState(false);
  const [systemRecommendations, setSystemRecommendations] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [systemSpecs, setSystemSpecs] = useState(null);
  
  // Chat/Testing state
  const [testMessages, setTestMessages] = useState([]);
  const [testInput, setTestInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Voice integration state
  const [voiceConfig, setVoiceConfig] = useState({
    enabled: false,
    engine: 'web_speech_api',
    voice: null,
    language: 'en-US',
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
    auto_speak: false
  });
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Performance monitoring
  const [performanceMetrics, setPerformanceMetrics] = useState({
    total_requests: 0,
    successful_requests: 0,
    failed_requests: 0,
    average_response_time: 0,
    last_response_time: 0,
    circuit_breaker_state: 'CLOSED'
  });
  
  // Plugin state
  const [installedPlugins, setInstalledPlugins] = useState([]);
  const [availablePlugins, setAvailablePlugins] = useState([
    {
      id: 'ollama-optimizer',
      name: 'Ollama Optimizer',
      version: '1.0.0',
      description: 'Optimizes Ollama model parameters for better performance',
      compatible_engines: ['ollama'],
      installed: false
    },
    {
      id: 'voice-enhancer',
      name: 'Voice Quality Enhancer',
      version: '1.2.0',
      description: 'Improves voice synthesis quality and naturalness',
      compatible_engines: ['all'],
      installed: false
    },
    {
      id: 'response-analyzer',
      name: 'Response Quality Analyzer',
      version: '1.1.0',
      description: 'Analyzes and scores LLM response quality',
      compatible_engines: ['all'],
      installed: false
    }
  ]);

  const speechSynthesis = window.speechSynthesis;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = useRef(null);

  useEffect(() => {
    if (isVisible) {
      loadConfiguration();
      loadAvailableVoices();
      initializeSpeechRecognition();
      loadSystemRecommendations();
    }
  }, [isVisible]);

  useEffect(() => {
    if (voiceConfig.enabled && voiceConfig.auto_speak && testMessages.length > 0) {
      const lastMessage = testMessages[testMessages.length - 1];
      if (lastMessage.type === 'assistant' && !lastMessage.spoken) {
        speakText(lastMessage.content);
        setTestMessages(prev => prev.map(msg => 
          msg.id === lastMessage.id ? { ...msg, spoken: true } : msg
        ));
      }
    }
  }, [testMessages, voiceConfig]);

  const loadConfiguration = async () => {
    try {
      // Load configuration from Settings API
      const response = await fetch('http://localhost:8003/api/settings');
      
      if (response.ok) {
        const settings = await response.json();
        
        // Update LLM configuration with settings
        if (settings.localLLM) {
          setLlmConfig(prev => ({
            ...prev,
            engine: settings.localLLM.provider || prev.engine,
            base_url: settings.localLLM.endpoint || prev.base_url,
            model: settings.localLLM.model || prev.model,
            temperature: settings.localLLM.temperature || prev.temperature,
            max_tokens: settings.localLLM.maxTokens || prev.max_tokens,
            timeout: settings.localLLM.healthCheckInterval ? settings.localLLM.healthCheckInterval / 1000 : prev.timeout
          }));
        }
        
        // Update voice configuration if available
        if (settings.voice) {
          setVoiceConfig(prev => ({
            ...prev,
            enabled: settings.voice.enabled || prev.enabled,
            language: settings.voice.language || prev.language
          }));
        }
      } else {
        console.warn('Could not load settings from API, using defaults');
      }
      
      // Load additional config from localStorage as fallback
      const savedConfig = localStorage.getItem('hearthlink_llm_config');
      if (savedConfig) {
        const localConfig = JSON.parse(savedConfig);
        setLlmConfig(prev => ({ ...prev, ...localConfig }));
      }
      
      const savedVoiceConfig = localStorage.getItem('hearthlink_voice_config');
      if (savedVoiceConfig) {
        const localVoiceConfig = JSON.parse(savedVoiceConfig);
        setVoiceConfig(prev => ({ ...prev, ...localVoiceConfig }));
      }
      
      // Load performance metrics
      const savedMetrics = localStorage.getItem('hearthlink_llm_metrics');
      if (savedMetrics) {
        setPerformanceMetrics(prev => ({ ...prev, ...JSON.parse(savedMetrics) }));
      }
    } catch (error) {
      console.error('Failed to load configuration:', error);
    }
  };

  const loadSystemRecommendations = async () => {
    setIsLoadingRecommendations(true);
    try {
      const response = await fetch('http://localhost:8001/api/recommendations');
      if (response.ok) {
        const data = await response.json();
        setSystemRecommendations(data.recommendations || []);
        setSystemSpecs(data.system_specs || null);
      } else {
        console.warn('Failed to load system recommendations');
      }
    } catch (error) {
      console.error('Error loading system recommendations:', error);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const saveConfiguration = async () => {
    try {
      // Save to localStorage first
      localStorage.setItem('hearthlink_llm_config', JSON.stringify(llmConfig));
      localStorage.setItem('hearthlink_voice_config', JSON.stringify(voiceConfig));
      
      // Save to Settings API
      const response = await fetch('http://localhost:8003/api/settings');
      
      if (response.ok) {
        const currentSettings = await response.json();
        
        // Update with current LLM and voice config
        const updatedSettings = {
          ...currentSettings,
          localLLM: {
            ...currentSettings.localLLM,
            provider: llmConfig.engine,
            endpoint: llmConfig.base_url,
            model: llmConfig.model,
            temperature: llmConfig.temperature,
            maxTokens: llmConfig.max_tokens,
            healthCheckInterval: llmConfig.timeout * 1000
          },
          voice: {
            ...currentSettings.voice,
            enabled: voiceConfig.enabled,
            language: voiceConfig.language
          }
        };
        
        // Save updated settings
        const saveResponse = await fetch('http://localhost:8003/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedSettings)
        });
        
        if (saveResponse.ok) {
          console.log('Configuration saved successfully');
        } else {
          console.warn('Failed to save configuration to API');
        }
      }
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  };

  const loadAvailableVoices = () => {
    if (speechSynthesis) {
      const voices = speechSynthesis.getVoices();
      setAvailableVoices(voices);
      
      if (voices.length > 0 && !voiceConfig.voice) {
        const defaultVoice = voices.find(voice => voice.default) || voices[0];
        setVoiceConfig(prev => ({ ...prev, voice: defaultVoice.name }));
      }
    }
  };

  const initializeSpeechRecognition = () => {
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = voiceConfig.language;

      recognition.current.onstart = () => {
        setIsListening(true);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTestInput(transcript);
        handleSendMessage(transcript);
      };

      recognition.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  };

  const testConnection = async () => {
    setIsConnecting(true);
    setConnectionError(null);
    
    const startTime = Date.now();
    
    try {
      // Test connection using Settings API
      const testResponse = await fetch('http://localhost:8003/api/test/local-llm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          localLLM: llmConfig
        })
      });
      
      const testResult = await testResponse.json();
      
      if (testResult.success) {
        setConnectionStatus('connected');
        
        // Try to get available models
        if (llmConfig.engine === 'ollama') {
          try {
            const modelsResponse = await fetch('http://localhost:8003/api/models/ollama');
            const modelsData = await modelsResponse.json();
            
            if (modelsData.success) {
              setAvailableModels(modelsData.models.map(model => model.name));
            } else {
              setAvailableModels([llmConfig.model]);
            }
          } catch (error) {
            console.warn('Could not fetch models:', error);
            setAvailableModels([llmConfig.model]);
          }
        } else {
          setAvailableModels([llmConfig.model]);
        }
        
        const responseTime = (Date.now() - startTime) / 1000;
        
        // Update metrics
        setPerformanceMetrics(prev => ({
          ...prev,
          total_requests: prev.total_requests + 1,
          successful_requests: prev.successful_requests + 1,
          last_response_time: responseTime,
          average_response_time: ((prev.average_response_time * (prev.total_requests - 1)) + responseTime) / prev.total_requests
        }));
      } else {
        throw new Error(testResult.error || 'Connection test failed');
      }
    } catch (error) {
      setConnectionStatus('error');
      setConnectionError(error.message);
      
      const responseTime = (Date.now() - startTime) / 1000;
      setPerformanceMetrics(prev => ({
        ...prev,
        total_requests: prev.total_requests + 1,
        failed_requests: prev.failed_requests + 1,
        last_response_time: responseTime
      }));
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSendMessage = async (message = testInput) => {
    if (!message.trim() || isGenerating) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message.trim(),
      timestamp: new Date()
    };

    setTestMessages(prev => [...prev, userMessage]);
    setTestInput('');
    setIsGenerating(true);
    
    const startTime = Date.now();

    try {
      // Make actual API call to local LLM
      const response = await fetch(`${llmConfig.base_url}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: llmConfig.model,
          prompt: message.trim(),
          stream: false,
          options: {
            temperature: llmConfig.temperature,
            num_predict: llmConfig.max_tokens,
            num_ctx: 2048,
            timeout: llmConfig.timeout * 1000
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || 'No response generated',
        timestamp: new Date(),
        spoken: false
      };

      setTestMessages(prev => [...prev, assistantMessage]);
      
      const responseTime = (Date.now() - startTime) / 1000;
      
      // Update metrics
      setPerformanceMetrics(prev => ({
        ...prev,
        total_requests: prev.total_requests + 1,
        successful_requests: prev.successful_requests + 1,
        last_response_time: responseTime,
        average_response_time: ((prev.average_response_time * (prev.total_requests - 1)) + responseTime) / prev.total_requests
      }));
      
    } catch (error) {
      console.error('LLM API Error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setTestMessages(prev => [...prev, errorMessage]);
      
      const responseTime = (Date.now() - startTime) / 1000;
      setPerformanceMetrics(prev => ({
        ...prev,
        total_requests: prev.total_requests + 1,
        failed_requests: prev.failed_requests + 1,
        last_response_time: responseTime
      }));
    } finally {
      setIsGenerating(false);
    }
  };

  const speakText = (text) => {
    if (!speechSynthesis || !voiceConfig.enabled) return;

    const utterance = new SpeechSynthesisUtterance(text);
    
    const selectedVoice = availableVoices.find(voice => voice.name === voiceConfig.voice);
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    utterance.rate = voiceConfig.rate;
    utterance.pitch = voiceConfig.pitch;
    utterance.volume = voiceConfig.volume;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
    };
    
    speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    if (recognition.current && !isListening) {
      recognition.current.start();
    }
  };

  const stopListening = () => {
    if (recognition.current && isListening) {
      recognition.current.stop();
    }
  };

  const installPlugin = (pluginId) => {
    const plugin = availablePlugins.find(p => p.id === pluginId);
    if (plugin) {
      setInstalledPlugins(prev => [...prev, { ...plugin, installed: true }]);
      setAvailablePlugins(prev => prev.map(p => 
        p.id === pluginId ? { ...p, installed: true } : p
      ));
    }
  };

  const uninstallPlugin = (pluginId) => {
    setInstalledPlugins(prev => prev.filter(p => p.id !== pluginId));
    setAvailablePlugins(prev => prev.map(p => 
      p.id === pluginId ? { ...p, installed: false } : p
    ));
  };

  const handleModelSelect = (modelName) => {
    setLlmConfig(prev => ({ ...prev, model: modelName }));
    setModelSelectorVisible(false);
  };

  const handleModelInstall = async (modelName) => {
    try {
      const response = await fetch('http://localhost:8001/api/models/pull', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: modelName })
      });

      if (response.ok) {
        // Refresh recommendations after installation
        await loadSystemRecommendations();
      } else {
        console.error('Failed to install model:', modelName);
      }
    } catch (error) {
      console.error('Error installing model:', error);
    }
  };

  const renderConfigurationTab = () => (
    <div className="llm-tab-content">
      <div className="config-sections">
        <div className="config-section">
          <h3>LLM Engine Configuration</h3>
          <div className="config-grid">
            <div className="config-field">
              <label>Engine</label>
              <select
                value={llmConfig.engine}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, engine: e.target.value }))}
              >
                <option value="ollama">Ollama</option>
                <option value="lmstudio">LM Studio</option>
                <option value="custom">Custom Endpoint</option>
              </select>
            </div>
            
            <div className="config-field">
              <label>Base URL</label>
              <input
                type="text"
                value={llmConfig.base_url}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, base_url: e.target.value }))}
                placeholder="http://localhost:11434"
              />
            </div>
            
            <div className="config-field">
              <label>Model</label>
              <div className="model-selector-container">
                <div className="current-model-display">
                  <span className="current-model">{llmConfig.model}</span>
                  <button 
                    className="model-selector-button"
                    onClick={() => setModelSelectorVisible(true)}
                  >
                    Select Model
                  </button>
                </div>
                {systemSpecs && (
                  <div className="system-tier-indicator">
                    <span className={`tier-badge ${systemSpecs.performance_tier}`}>
                      {systemSpecs.performance_tier.toUpperCase()} TIER
                    </span>
                    <span className="system-ram">{systemSpecs.total_ram_gb} GB RAM</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="config-field">
              <label>Temperature</label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={llmConfig.temperature}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
              />
              <span>{llmConfig.temperature}</span>
            </div>
            
            <div className="config-field">
              <label>Max Tokens</label>
              <input
                type="number"
                value={llmConfig.max_tokens}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, max_tokens: parseInt(e.target.value) }))}
                min="1"
                max="8192"
              />
            </div>
            
            <div className="config-field">
              <label>Timeout (seconds)</label>
              <input
                type="number"
                value={llmConfig.timeout}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                min="1"
                max="300"
              />
            </div>
          </div>
          
          <div className="config-actions">
            <button onClick={testConnection} disabled={isConnecting}>
              {isConnecting ? 'Testing...' : 'Test Connection'}
            </button>
            <button onClick={saveConfiguration}>Save Configuration</button>
          </div>
          
          <div className="connection-status">
            <div className={`status-indicator ${connectionStatus}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                {connectionStatus === 'connected' && 'Connected'}
                {connectionStatus === 'disconnected' && 'Disconnected'}
                {connectionStatus === 'error' && 'Connection Error'}
              </span>
            </div>
            {connectionError && (
              <div className="error-details">{connectionError}</div>
            )}
          </div>
        </div>

        <div className="config-section">
          <h3>Voice Integration</h3>
          <div className="voice-config">
            <div className="config-field">
              <label>
                <input
                  type="checkbox"
                  checked={voiceConfig.enabled}
                  onChange={(e) => setVoiceConfig(prev => ({ ...prev, enabled: e.target.checked }))}
                />
                Enable Voice Integration
              </label>
            </div>
            
            {voiceConfig.enabled && (
              <>
                <div className="config-field">
                  <label>Voice</label>
                  <select
                    value={voiceConfig.voice || ''}
                    onChange={(e) => setVoiceConfig(prev => ({ ...prev, voice: e.target.value }))}
                  >
                    {availableVoices.map(voice => (
                      <option key={voice.name} value={voice.name}>
                        {voice.name} ({voice.lang})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="config-field">
                  <label>Language</label>
                  <select
                    value={voiceConfig.language}
                    onChange={(e) => setVoiceConfig(prev => ({ ...prev, language: e.target.value }))}
                  >
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="es-ES">Spanish</option>
                    <option value="fr-FR">French</option>
                    <option value="de-DE">German</option>
                    <option value="ja-JP">Japanese</option>
                  </select>
                </div>
                
                <div className="voice-controls">
                  <div className="config-field">
                    <label>Rate: {voiceConfig.rate}</label>
                    <input
                      type="range"
                      min="0.5"
                      max="2"
                      step="0.1"
                      value={voiceConfig.rate}
                      onChange={(e) => setVoiceConfig(prev => ({ ...prev, rate: parseFloat(e.target.value) }))}
                    />
                  </div>
                  
                  <div className="config-field">
                    <label>Pitch: {voiceConfig.pitch}</label>
                    <input
                      type="range"
                      min="0.5"
                      max="2"
                      step="0.1"
                      value={voiceConfig.pitch}
                      onChange={(e) => setVoiceConfig(prev => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                    />
                  </div>
                  
                  <div className="config-field">
                    <label>Volume: {voiceConfig.volume}</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={voiceConfig.volume}
                      onChange={(e) => setVoiceConfig(prev => ({ ...prev, volume: parseFloat(e.target.value) }))}
                    />
                  </div>
                </div>
                
                <div className="config-field">
                  <label>
                    <input
                      type="checkbox"
                      checked={voiceConfig.auto_speak}
                      onChange={(e) => setVoiceConfig(prev => ({ ...prev, auto_speak: e.target.checked }))}
                    />
                    Auto-speak responses
                  </label>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderTestingTab = () => (
    <div className="llm-tab-content">
      <div className="testing-interface">
        <div className="chat-messages">
          {testMessages.map(message => (
            <div key={message.id} className={`chat-message ${message.type}`}>
              <div className="message-content">{message.content}</div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
              {message.type === 'assistant' && voiceConfig.enabled && (
                <button 
                  className="speak-button"
                  onClick={() => speakText(message.content)}
                  disabled={isSpeaking}
                >
                  🔊
                </button>
              )}
            </div>
          ))}
          
          {isGenerating && (
            <div className="chat-message assistant generating">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
        </div>
        
        <div className="chat-input-area">
          <div className="input-controls">
            <textarea
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your message or use voice input..."
              disabled={isGenerating}
              rows="2"
            />
            
            <div className="input-buttons">
              {voiceConfig.enabled && SpeechRecognition && (
                <button
                  className={`voice-button ${isListening ? 'listening' : ''}`}
                  onClick={isListening ? stopListening : startListening}
                  disabled={isGenerating}
                >
                  🎤
                </button>
              )}
              
              <button 
                onClick={() => handleSendMessage()}
                disabled={!testInput.trim() || isGenerating}
                className="send-button"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMonitoringTab = () => (
    <div className="llm-tab-content">
      <div className="monitoring-sections">
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Total Requests</h4>
            <div className="metric-value">{performanceMetrics.total_requests}</div>
          </div>
          
          <div className="metric-card">
            <h4>Success Rate</h4>
            <div className="metric-value">
              {performanceMetrics.total_requests > 0 
                ? ((performanceMetrics.successful_requests / performanceMetrics.total_requests) * 100).toFixed(1)
                : 0}%
            </div>
          </div>
          
          <div className="metric-card">
            <h4>Average Response Time</h4>
            <div className="metric-value">{performanceMetrics.average_response_time.toFixed(2)}s</div>
          </div>
          
          <div className="metric-card">
            <h4>Circuit Breaker</h4>
            <div className={`metric-value status-${performanceMetrics.circuit_breaker_state.toLowerCase()}`}>
              {performanceMetrics.circuit_breaker_state}
            </div>
          </div>
        </div>
        
        <div className="monitoring-section">
          <h3>System Health</h3>
          <div className="health-indicators">
            <div className="health-item">
              <span className="health-label">LLM Connection</span>
              <span className={`health-status ${connectionStatus}`}>
                {connectionStatus.toUpperCase()}
              </span>
            </div>
            
            <div className="health-item">
              <span className="health-label">Voice Integration</span>
              <span className={`health-status ${voiceConfig.enabled ? 'connected' : 'disabled'}`}>
                {voiceConfig.enabled ? 'ENABLED' : 'DISABLED'}
              </span>
            </div>
            
            <div className="health-item">
              <span className="health-label">Speech Recognition</span>
              <span className={`health-status ${SpeechRecognition ? 'connected' : 'error'}`}>
                {SpeechRecognition ? 'AVAILABLE' : 'NOT SUPPORTED'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPluginsTab = () => (
    <div className="llm-tab-content">
      <div className="plugins-sections">
        <div className="plugins-section">
          <h3>Installed Plugins</h3>
          <div className="plugins-list">
            {installedPlugins.length > 0 ? (
              installedPlugins.map(plugin => (
                <div key={plugin.id} className="plugin-card installed">
                  <div className="plugin-info">
                    <h4>{plugin.name}</h4>
                    <p>{plugin.description}</p>
                    <span className="plugin-version">v{plugin.version}</span>
                  </div>
                  <button 
                    className="plugin-action uninstall"
                    onClick={() => uninstallPlugin(plugin.id)}
                  >
                    Uninstall
                  </button>
                </div>
              ))
            ) : (
              <div className="no-plugins">No plugins installed</div>
            )}
          </div>
        </div>
        
        <div className="plugins-section">
          <h3>Available Plugins</h3>
          <div className="plugins-list">
            {availablePlugins.filter(p => !p.installed).map(plugin => (
              <div key={plugin.id} className="plugin-card available">
                <div className="plugin-info">
                  <h4>{plugin.name}</h4>
                  <p>{plugin.description}</p>
                  <span className="plugin-version">v{plugin.version}</span>
                  <div className="plugin-compatibility">
                    Compatible: {plugin.compatible_engines.join(', ')}
                  </div>
                </div>
                <button 
                  className="plugin-action install"
                  onClick={() => installPlugin(plugin.id)}
                >
                  Install
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderModelSelector = () => {
    if (!modelSelectorVisible) return null;

    return (
      <div className="model-selector-overlay">
        <div className="model-selector-modal">
          <div className="modal-header">
            <h3>Select LLM Model</h3>
            <button 
              className="modal-close"
              onClick={() => setModelSelectorVisible(false)}
            >
              ✕
            </button>
          </div>
          
          {systemSpecs && (
            <div className="system-specs">
              <h4>System Specifications</h4>
              <div className="specs-grid">
                <div className="spec-item">
                  <span className="spec-label">RAM:</span>
                  <span className="spec-value">{systemSpecs.total_ram_gb} GB</span>
                </div>
                <div className="spec-item">
                  <span className="spec-label">Available:</span>
                  <span className="spec-value">{systemSpecs.available_ram_gb} GB</span>
                </div>
                <div className="spec-item">
                  <span className="spec-label">CPU Cores:</span>
                  <span className="spec-value">{systemSpecs.cpu_cores}</span>
                </div>
                <div className="spec-item">
                  <span className="spec-label">Performance Tier:</span>
                  <span className={`spec-value tier-${systemSpecs.performance_tier}`}>
                    {systemSpecs.performance_tier.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <div className="modal-content">
            {isLoadingRecommendations ? (
              <div className="loading-recommendations">
                <span>Loading recommendations...</span>
              </div>
            ) : (
              <div className="recommendations-list">
                {systemRecommendations.length > 0 ? (
                  systemRecommendations.map((rec, index) => (
                    <div key={index} className={`recommendation-card ${rec.recommended_use === 'primary' ? 'primary' : ''}`}>
                      <div className="rec-header">
                        <div className="rec-title">
                          <h4>{rec.model}</h4>
                          {rec.recommended_use === 'primary' && (
                            <span className="primary-badge">RECOMMENDED</span>
                          )}
                        </div>
                        <div className="rec-badges">
                          <span className={`performance-badge ${rec.performance_tier}`}>
                            {rec.performance_tier.toUpperCase()}
                          </span>
                          <span className="size-badge">{rec.parameter_size}</span>
                        </div>
                      </div>
                      
                      <div className="rec-details">
                        <div className="rec-info">
                          <div className="info-item">
                            <span className="info-label">Memory Usage:</span>
                            <span className="info-value">{rec.memory_usage}</span>
                          </div>
                          <div className="info-item">
                            <span className="info-label">Speed:</span>
                            <span className="info-value">{rec.speed}</span>
                          </div>
                          <div className="info-item">
                            <span className="info-label">Quality:</span>
                            <span className="info-value">{rec.quality}</span>
                          </div>
                        </div>
                        
                        <div className="rec-suitable">
                          <span className="suitable-label">Suitable for:</span>
                          <div className="suitable-tags">
                            {rec.suitable_for.map((use, i) => (
                              <span key={i} className="suitable-tag">{use}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      <div className="rec-actions">
                        {rec.installed ? (
                          <button 
                            className="select-button"
                            onClick={() => handleModelSelect(rec.model)}
                          >
                            Select Model
                          </button>
                        ) : (
                          <button 
                            className="install-button"
                            onClick={() => handleModelInstall(rec.model)}
                          >
                            Install & Select
                          </button>
                        )}
                        <div className="rec-status">
                          {rec.installed ? (
                            <span className="status-installed">✓ Installed ({rec.size_formatted})</span>
                          ) : (
                            <span className="status-not-installed">Not installed</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-recommendations">
                    No recommendations available. Please check your system configuration.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (!isVisible) return null;

  return (
    <div className="llm-interface-overlay">
      <div className="llm-interface">
        <div className="llm-header">
          <div className="header-title">
            <h2>Local LLM & Voice Integration</h2>
            <span className={`connection-badge ${connectionStatus}`}>
              {connectionStatus.toUpperCase()}
            </span>
          </div>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="llm-navigation">
          <button 
            className={`nav-tab ${activeTab === 'configuration' ? 'active' : ''}`}
            onClick={() => setActiveTab('configuration')}
          >
            Configuration
          </button>
          <button 
            className={`nav-tab ${activeTab === 'testing' ? 'active' : ''}`}
            onClick={() => setActiveTab('testing')}
          >
            Testing
          </button>
          <button 
            className={`nav-tab ${activeTab === 'monitoring' ? 'active' : ''}`}
            onClick={() => setActiveTab('monitoring')}
          >
            Monitoring
          </button>
          <button 
            className={`nav-tab ${activeTab === 'plugins' ? 'active' : ''}`}
            onClick={() => setActiveTab('plugins')}
          >
            Plugins
          </button>
        </div>

        <div className="llm-content">
          {activeTab === 'configuration' && renderConfigurationTab()}
          {activeTab === 'testing' && renderTestingTab()}
          {activeTab === 'monitoring' && renderMonitoringTab()}
          {activeTab === 'plugins' && renderPluginsTab()}
        </div>

        <div className="llm-footer">
          <div className="footer-info">
            <span>Engine: {llmConfig.engine}</span>
            <span>Model: {llmConfig.model}</span>
            {voiceConfig.enabled && <span>Voice: Enabled</span>}
          </div>
          <div className="footer-metrics">
            Requests: {performanceMetrics.total_requests} | 
            Success Rate: {performanceMetrics.total_requests > 0 
              ? ((performanceMetrics.successful_requests / performanceMetrics.total_requests) * 100).toFixed(1)
              : 0}%
          </div>
        </div>
      </div>
      
      {/* Model Selector Modal */}
      {renderModelSelector()}
    </div>
  );
};

export default LocalLLMInterface;