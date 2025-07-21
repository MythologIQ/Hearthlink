import React, { useState, useEffect, useRef } from 'react';
import './VoiceInterface.css';
import VoiceTTSManager from './VoiceTTSManager';

const VoiceInterface = ({ onCommand, isActive, onClose, currentAgent, availableAgents, onAgentChange }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [commands, setCommands] = useState([]);
  const [routingMode, setRoutingMode] = useState('agnostic'); // 'agnostic' or 'isolated'
  const [pinnedAgent, setPinnedAgent] = useState(null);
  const [agentConfirmation, setAgentConfirmation] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [externalAgentsEnabled, setExternalAgentsEnabled] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [confidence, setConfidence] = useState(0);
  const [routingBreadcrumbs, setRoutingBreadcrumbs] = useState([]);
  const [persistentHUD, setPersistentHUD] = useState(false);
  const [secureMode, setSecureMode] = useState(false);
  const [deferenceOptions, setDeferenceOptions] = useState([]);
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const ttsManagerRef = useRef(null);

  // Voice routing logic based on VOICE_ACCESS_POLICY.md
  const localAgents = ['alden', 'alice', 'mimic', 'sentry'];
  const externalAgents = ['gemini-cli', 'google-api', 'trae-cli'];

  useEffect(() => {
    if (isActive && voiceEnabled) {
      // Check for browser support
      if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        setVoiceEnabled(false);
        return;
      }

      // Initialize speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        try {
          recognitionRef.current = new SpeechRecognition();
          recognitionRef.current.continuous = false;
          recognitionRef.current.interimResults = true;
          recognitionRef.current.lang = 'en-US';
          
          recognitionRef.current.onstart = () => {
            setIsListening(true);
            setTranscript('');
            setAgentConfirmation('');
            initAudioVisualization();
          };

          recognitionRef.current.onresult = (event) => {
            const result = event.results[event.results.length - 1];
            const text = result[0].transcript;
            const confidenceScore = result[0].confidence || 0.8; // Default confidence
            setTranscript(text);
            setConfidence(confidenceScore);
            
            if (result.isFinal) {
              handleVoiceInput(text, confidenceScore);
            }
          };

          recognitionRef.current.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            setIsListening(false);
            logVoiceEvent('error', { error: event.error });
          };

          recognitionRef.current.onend = () => {
            setIsListening(false);
          };
        } catch (error) {
          console.error('Failed to initialize speech recognition:', error);
          setVoiceEnabled(false);
        }
      }
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.warn('Error stopping speech recognition:', error);
        }
      }
    };
  }, [isActive, voiceEnabled]);

  // Initialize audio visualization for enhanced HUD
  const initAudioVisualization = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;
      
      // Start audio level monitoring
      const updateAudioLevel = () => {
        if (analyserRef.current && isListening) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          const level = Math.max(...dataArray) / 255;
          setAudioLevel(level);
          requestAnimationFrame(updateAudioLevel);
        }
      };
      updateAudioLevel();
    } catch (error) {
      console.warn('Audio visualization not available:', error);
    }
  };

  // Agent deference system - analyzes if another agent would be better suited
  const analyzeAgentDeference = (input, currentTarget) => {
    const deferenceRules = {
      'scheduling': 'alden',
      'calendar': 'alden',
      'appointment': 'alden',
      'emotion': 'alice',
      'therapy': 'alice',
      'feeling': 'alice',
      'persona': 'mimic',
      'character': 'mimic',
      'role': 'mimic',
      'security': 'sentry',
      'threat': 'sentry',
      'monitor': 'sentry'
    };

    const lowerInput = input.toLowerCase();
    const suggestedAgent = Object.keys(deferenceRules).find(keyword => 
      lowerInput.includes(keyword)
    );

    if (suggestedAgent && deferenceRules[suggestedAgent] !== currentTarget) {
      const betterAgent = deferenceRules[suggestedAgent];
      return {
        suggested: betterAgent,
        reason: `This request involves ${suggestedAgent}, which ${betterAgent} specializes in.`,
        confidence: 0.8
      };
    }

    return null;
  };

  // Secure mode activation check
  const checkSecureModeActivation = (input) => {
    const secureActivationPhrases = [
      'hearthlink secure mode activate',
      'activate secure mode',
      'enable secure mode'
    ];

    return secureActivationPhrases.some(phrase => 
      input.toLowerCase().includes(phrase)
    );
  };

  // Enhanced Alden misroute recovery
  const handleMisroute = (input, originalTarget) => {
    const recoveryResponse = `I didn't quite understand which agent you meant to reach. Based on "${input}", would you like me to:`;
    const suggestions = [];

    // Analyze input for likely agents
    const agentKeywords = {
      'alden': ['schedule', 'calendar', 'productivity', 'task'],
      'alice': ['emotion', 'therapy', 'counseling', 'feeling'],
      'mimic': ['persona', 'character', 'role', 'creative'],
      'sentry': ['security', 'threat', 'monitor', 'protect']
    };

    Object.keys(agentKeywords).forEach(agent => {
      const keywords = agentKeywords[agent];
      if (keywords.some(keyword => input.toLowerCase().includes(keyword))) {
        suggestions.push({
          agent,
          reason: `Handle this with ${agent} (detected relevant keywords)`
        });
      }
    });

    if (suggestions.length === 0) {
      suggestions.push({
        agent: 'alden',
        reason: 'Let me handle this as your general assistant'
      });
    }

    setDeferenceOptions(suggestions);
    setAgentConfirmation(`${recoveryResponse} ${suggestions.map((s, i) => 
      `${i + 1}. ${s.reason}`
    ).join(', ')}`);

    return suggestions;
  };

  // Voice routing logic implementation
  const handleVoiceInput = (input, confidenceScore = 0.8) => {
    const lowerInput = input.toLowerCase();
    let targetAgent = null;
    let routingDecision = null;

    // Check for voice adjustment commands first
    if (ttsManagerRef.current && ttsManagerRef.current.processVoiceAdjustmentCommand) {
      const wasVoiceCommand = ttsManagerRef.current.processVoiceAdjustmentCommand(input, currentAgent);
      if (wasVoiceCommand) {
        routingDecision = 'voice_adjustment_processed';
        setAgentConfirmation('Voice settings updated.');
        return;
      }
    }

    // Check for secure mode activation
    if (checkSecureModeActivation(input)) {
      setSecureMode(true);
      setAgentConfirmation('Secure mode activated. Please provide authentication.');
      routingDecision = 'secure_mode_activated';
      // TODO: Implement authentication challenge
      return;
    }

    // Agent Agnostic Mode: Listen for any active agent by name
    if (routingMode === 'agnostic') {
      for (const agent of localAgents) {
        if (lowerInput.includes(`hey ${agent}`) || lowerInput.includes(`${agent},`)) {
          targetAgent = agent;
          routingDecision = 'local_agent_detected';
          break;
        }
      }

      // Check for external agents (only if enabled)
      if (externalAgentsEnabled) {
        for (const agent of externalAgents) {
          if (lowerInput.includes(`hey ${agent}`) || lowerInput.includes(`${agent},`)) {
            targetAgent = agent;
            routingDecision = 'external_agent_detected';
            break;
          }
        }
      }

      // If no agent specified, delegate to currently active agent
      if (!targetAgent) {
        targetAgent = currentAgent || 'alden';
        routingDecision = 'delegated_to_active';
      }
    } else {
      // Isolated Mode: All voice input routes to pinned agent
      targetAgent = pinnedAgent || currentAgent || 'alden';
      routingDecision = 'isolated_mode';
    }

    // Safety reinforcement: External agent routing confirmation
    if (externalAgents.includes(targetAgent) && !externalAgentsEnabled) {
      setAgentConfirmation(`External agent ${targetAgent} is not enabled. Please enable in Core → Settings → External Agents → Voice Interaction.`);
      logVoiceEvent('external_agent_blocked', { agent: targetAgent, input });
      return;
    }

    // Check for agent deference - suggest better suited agent if available
    const deferenceOption = analyzeAgentDeference(input, targetAgent);
    if (deferenceOption && deferenceOption.confidence > 0.7) {
      setDeferenceOptions([{
        agent: deferenceOption.suggested,
        reason: deferenceOption.reason,
        original: targetAgent
      }]);
      setAgentConfirmation(`${deferenceOption.reason} Would you like to switch to ${deferenceOption.suggested} instead?`);
      
      // Add routing breadcrumb for deference suggestion
      setRoutingBreadcrumbs(prev => [...prev, {
        step: 'deference_suggested',
        from: targetAgent,
        to: deferenceOption.suggested,
        reason: deferenceOption.reason,
        timestamp: new Date()
      }]);
    } else {
      // Standard agent confirmation message
      if (externalAgents.includes(targetAgent)) {
        setAgentConfirmation(`You're speaking with ${targetAgent} now.`);
      } else {
        setAgentConfirmation(`You're speaking with ${targetAgent}.`);
      }
      
      // Clear deference options if no suggestion
      setDeferenceOptions([]);
    }

    // Add routing breadcrumb
    setRoutingBreadcrumbs(prev => [...prev, {
      step: routingDecision,
      agent: targetAgent,
      confidence: confidenceScore,
      timestamp: new Date()
    }]);

    // Log voice session to Vault
    logVoiceSession(input, targetAgent, routingDecision);

    // Process command
    const processed = processVoiceCommand(input, targetAgent);
    
    if (processed) {
      setCommands(prev => [...prev, { 
        command: input, 
        agent: targetAgent,
        routing: routingDecision,
        timestamp: new Date(), 
        processed: true 
      }]);
      
      // Update current agent if needed
      if (onAgentChange && targetAgent !== currentAgent) {
        onAgentChange(targetAgent);
      }
    } else {
      setCommands(prev => [...prev, { 
        command: input, 
        agent: targetAgent,
        routing: routingDecision,
        timestamp: new Date(), 
        processed: false 
      }]);
    }
    
    onCommand(input, targetAgent);
    setTranscript('');
  };

  // Process voice command based on agent
  const processVoiceCommand = (command, agent) => {
    // Basic command processing
    const lowerCommand = command.toLowerCase();
    
    // Universal commands
    if (lowerCommand.includes('new session') || lowerCommand.includes('start session')) {
      return true;
    }
    if (lowerCommand.includes('help') || lowerCommand.includes('user guide')) {
      return true;
    }
    if (lowerCommand.includes('accessibility')) {
      return true;
    }
    if (lowerCommand.includes('troubleshooting')) {
      return true;
    }
    if (lowerCommand.includes('exit') || lowerCommand.includes('quit')) {
      return true;
    }

    // Agent-specific commands
    if (agent === 'alden') {
      if (lowerCommand.includes('schedule') || lowerCommand.includes('today')) {
        return true;
      }
    }
    if (agent === 'alice') {
      if (lowerCommand.includes('session review') || lowerCommand.includes('analytics')) {
        return true;
      }
    }
    if (agent === 'mimic') {
      if (lowerCommand.includes('rewrite') || lowerCommand.includes('paragraph')) {
        return true;
      }
    }
    if (agent === 'sentry') {
      if (lowerCommand.includes('security') || lowerCommand.includes('kill switch')) {
        return true;
      }
    }

    return false;
  };

  // Log voice session to Vault (per VOICE_ACCESS_POLICY.md)
  const logVoiceSession = (transcript, agent, routingDecision) => {
    const sessionData = {
      timestamp: new Date().toISOString(),
      transcript,
      agent,
      routing_decision: routingDecision,
      mode: routingMode,
      external_enabled: externalAgentsEnabled,
      session_id: `voice_${Date.now()}`,
      duration: 0, // Would be calculated in real implementation
      purpose: 'user_interaction'
    };

    // Log to Vault (simulated)
    if (window.vaultAPI) {
      window.vaultAPI.logVoiceSession(sessionData);
    } else {
      console.log('Voice session logged to Vault:', sessionData);
    }

    logVoiceEvent('session_logged', sessionData);
  };

  // Log voice events for audit trail
  const logVoiceEvent = (eventType, data) => {
    const eventData = {
      timestamp: new Date().toISOString(),
      event_type: eventType,
      ...data
    };

    if (window.vaultAPI) {
      window.vaultAPI.logVoiceEvent(eventData);
    } else {
      console.log('Voice event logged:', eventData);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && voiceEnabled) {
      try {
        recognitionRef.current.start();
        logVoiceEvent('listening_started', { mode: routingMode, pinned_agent: pinnedAgent });
      } catch (error) {
        console.error('Failed to start speech recognition:', error);
        setVoiceEnabled(false);
        setAgentConfirmation('Voice recognition failed to start. Please check browser permissions.');
      }
    } else if (!voiceEnabled) {
      setAgentConfirmation('Voice recognition is not available in this browser.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      logVoiceEvent('listening_stopped');
    }
  };

  const clearCommands = () => {
    setCommands([]);
  };

  const toggleRoutingMode = () => {
    const newMode = routingMode === 'agnostic' ? 'isolated' : 'agnostic';
    setRoutingMode(newMode);
    logVoiceEvent('routing_mode_changed', { new_mode: newMode });
  };

  const pinAgent = (agent) => {
    setPinnedAgent(agent);
    setRoutingMode('isolated');
    logVoiceEvent('agent_pinned', { agent });
  };

  const unpinAgent = () => {
    setPinnedAgent(null);
    setRoutingMode('agnostic');
    logVoiceEvent('agent_unpinned');
  };

  // Handle agent switching from deference suggestions
  const handleAgentSwitch = (newAgent) => {
    if (onAgentChange) {
      onAgentChange(newAgent);
    }
    setDeferenceOptions([]);
    setAgentConfirmation(`Switched to ${newAgent}. You can now speak with ${newAgent}.`);
    
    // Log the agent switch
    logVoiceEvent('agent_switched_via_deference', { 
      from: currentAgent, 
      to: newAgent 
    });
  };

  if (!isActive) return null;

  return (
    <div className="voice-interface">
      <h3>
        🎤 Voice Interface
        <button 
          onClick={onClose}
          className="close-btn"
          aria-label="Close voice interface"
        >
          ✕
        </button>
      </h3>
      
      {/* Enhanced Voice HUD */}
      <div className="enhanced-voice-hud">
        {/* Voice Status with Audio Visualization */}
        <div className={`voice-status ${isListening ? 'listening' : ''}`}>
          <div className="status-indicator">
            <span>{isListening ? '🔴' : '⚪'}</span>
            <span>
              {isListening ? 'Listening...' : 'Voice interface ready'}
              {!voiceEnabled && ' (Disabled)'}
            </span>
          </div>
          
          {/* Audio Level Visualization */}
          {isListening && (
            <div className="audio-visualization">
              <div className="waveform">
                {[...Array(8)].map((_, i) => (
                  <div 
                    key={i}
                    className="waveform-bar"
                    style={{ 
                      height: `${Math.max(5, audioLevel * 100 * (0.5 + Math.random() * 0.5))}%`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
              <div className="audio-level-indicator">
                <div 
                  className="level-bar" 
                  style={{ width: `${audioLevel * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Routing Mode and Breadcrumbs */}
        <div className="routing-info">
          <div className="routing-mode">
            <span>Mode: {routingMode === 'agnostic' ? 'Agent Agnostic' : 'Isolated (Pinned)'}</span>
            {pinnedAgent && <span>Pinned: {pinnedAgent}</span>}
            <button 
              onClick={() => setPersistentHUD(!persistentHUD)}
              className={`hud-toggle ${persistentHUD ? 'active' : ''}`}
              title="Toggle persistent HUD"
            >
              📌
            </button>
          </div>
          
          {/* Routing Breadcrumbs */}
          {routingBreadcrumbs.length > 0 && (
            <div className="routing-breadcrumbs">
              <strong>Routing Path:</strong>
              {routingBreadcrumbs.slice(-3).map((breadcrumb, index) => (
                <span key={index} className="breadcrumb">
                  {breadcrumb.step}
                  {breadcrumb.agent && ` → ${breadcrumb.agent}`}
                  {breadcrumb.confidence && (
                    <span className={`confidence ${breadcrumb.confidence > 0.8 ? 'high' : breadcrumb.confidence > 0.6 ? 'medium' : 'low'}`}>
                      ({Math.round(breadcrumb.confidence * 100)}%)
                    </span>
                  )}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Enhanced Transcript with Confidence */}
        {transcript && (
          <div className="voice-transcript">
            <div className="transcript-content">
              <strong>You said:</strong> {transcript}
              {confidence > 0 && (
                <span className={`confidence-indicator ${confidence > 0.8 ? 'high' : confidence > 0.6 ? 'medium' : 'low'}`}>
                  (Confidence: {Math.round(confidence * 100)}%)
                </span>
              )}
            </div>
          </div>
        )}

        {/* Agent Deference Options */}
        {deferenceOptions.length > 0 && (
          <div className="deference-options">
            <div className="deference-header">
              <strong>Agent Suggestion:</strong>
            </div>
            {deferenceOptions.map((option, index) => (
              <div key={index} className="deference-option">
                <span>{option.reason}</span>
                <button 
                  onClick={() => handleAgentSwitch(option.agent)}
                  className="switch-agent-btn"
                >
                  Switch to {option.agent}
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Agent Confirmation */}
        {agentConfirmation && (
          <div className={`agent-confirmation ${secureMode ? 'secure' : ''}`}>
            <strong>{secureMode ? 'Secure Mode:' : 'Agent Confirmation:'}</strong> {agentConfirmation}
            {secureMode && <span className="secure-indicator">🔒</span>}
          </div>
        )}
      </div>

      {/* Voice Output System - TTS Manager */}
      <VoiceTTSManager
        ref={ttsManagerRef}
        currentAgent={currentAgent}
        isEnabled={voiceEnabled}
        allowLiveAdjustment={true}
        onVoiceParametersChange={(persona, parameter, value) => {
          // Log voice parameter changes
          logVoiceEvent('voice_parameter_changed', {
            persona,
            parameter,
            value,
            timestamp: new Date().toISOString()
          });
        }}
      />

      {/* Routing Controls */}
      <div className="routing-controls">
        <button onClick={toggleRoutingMode} className="mode-btn">
          Switch to {routingMode === 'agnostic' ? 'Isolated' : 'Agnostic'} Mode
        </button>
        {routingMode === 'isolated' && (
          <div className="pin-controls">
            <select 
              value={pinnedAgent || ''} 
              onChange={(e) => pinAgent(e.target.value)}
              className="agent-select"
            >
              <option value="">Select agent to pin</option>
              {localAgents.map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </select>
            {pinnedAgent && (
              <button onClick={unpinAgent} className="unpin-btn">
                Unpin
              </button>
            )}
          </div>
        )}
      </div>
      
      {/* Available Commands */}
      <div className="voice-commands">
        <h4>Available Commands:</h4>
        <div className="command-category">
          <strong>Universal:</strong>
          <div className="voice-command">"New session" - Start a new session</div>
          <div className="voice-command">"Help" - Open user guide</div>
          <div className="voice-command">"Accessibility" - Open accessibility guide</div>
          <div className="voice-command">"Exit" or "Quit" - Close the application</div>
        </div>
        <div className="command-category">
          <strong>Agent-Specific:</strong>
          <div className="voice-command">"Hey Alden, what's on my schedule today?"</div>
          <div className="voice-command">"Mimic, help me rewrite this paragraph"</div>
          <div className="voice-command">"Alice, show me session review"</div>
          <div className="voice-command">"Sentry, check security status"</div>
        </div>
      </div>
      
      {/* Command History */}
      {commands.length > 0 && (
        <div className="command-history">
          <h4>Recent Commands:</h4>
          {commands.slice(-5).map((cmd, index) => (
            <div key={index} className={`command-item ${cmd.processed ? 'processed' : 'failed'}`}>
              <div className="command-header">
                <span className="command-text">{cmd.command}</span>
                <span className="command-agent">→ {cmd.agent}</span>
                <span className="command-status">
                  {cmd.processed ? '✓' : '✗'}
                </span>
              </div>
              <div className="command-details">
                <span className="command-routing">{cmd.routing}</span>
                <span className="command-time">
                  {cmd.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
          <button onClick={clearCommands} className="clear-btn">
            Clear History
          </button>
        </div>
      )}
      
      {/* Voice Controls */}
      <div className="voice-controls">
        {!isListening ? (
          <button onClick={startListening} className="start-btn" disabled={!voiceEnabled}>
            Start Listening
          </button>
        ) : (
          <button onClick={stopListening} className="stop-btn">
            Stop Listening
          </button>
        )}
        <button onClick={onClose} className="close-btn">
          Close
        </button>
      </div>
    </div>
  );
};

export default VoiceInterface; 