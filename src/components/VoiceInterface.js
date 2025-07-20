import React, { useState, useEffect, useRef } from 'react';
import './VoiceInterface.css';

const VoiceInterface = ({ onCommand, isActive, onClose, currentAgent, availableAgents, onAgentChange }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [commands, setCommands] = useState([]);
  const [routingMode, setRoutingMode] = useState('agnostic'); // 'agnostic' or 'isolated'
  const [pinnedAgent, setPinnedAgent] = useState(null);
  const [agentConfirmation, setAgentConfirmation] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [externalAgentsEnabled, setExternalAgentsEnabled] = useState(false);
  const recognitionRef = useRef(null);

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
          };

          recognitionRef.current.onresult = (event) => {
            const result = event.results[event.results.length - 1];
            const text = result[0].transcript;
            setTranscript(text);
            
            if (result.isFinal) {
              handleVoiceInput(text);
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

  // Voice routing logic implementation
  const handleVoiceInput = (input) => {
    const lowerInput = input.toLowerCase();
    let targetAgent = null;
    let routingDecision = null;

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

    // Agent confirmation message
    if (externalAgents.includes(targetAgent)) {
      setAgentConfirmation(`You're speaking with ${targetAgent} now.`);
    } else {
      setAgentConfirmation(`You're speaking with ${targetAgent}.`);
    }

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
      
      {/* Voice Status */}
      <div className={`voice-status ${isListening ? 'listening' : ''}`}>
        <span>{isListening ? '🔴' : '⚪'}</span>
        <span>
          {isListening ? 'Listening...' : 'Voice interface ready'}
          {!voiceEnabled && ' (Disabled)'}
        </span>
      </div>

      {/* Routing Mode Display */}
      <div className="routing-mode">
        <span>Mode: {routingMode === 'agnostic' ? 'Agent Agnostic' : 'Isolated (Pinned)'}</span>
        {pinnedAgent && <span>Pinned: {pinnedAgent}</span>}
      </div>

      {/* Agent Confirmation */}
      {agentConfirmation && (
        <div className="agent-confirmation">
          <strong>Agent Confirmation:</strong> {agentConfirmation}
        </div>
      )}
      
      {/* Voice Transcript */}
      {transcript && (
        <div className="voice-transcript">
          <strong>You said:</strong> {transcript}
        </div>
      )}

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