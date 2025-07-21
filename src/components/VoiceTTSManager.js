import React, { useState, useEffect, useRef } from 'react';
import './VoiceTTSManager.css';

/**
 * VoiceTTSManager - Complete Text-to-Speech system for Hearthlink personas
 * 
 * Features:
 * - Individual voice assignment for each persona (Alden, Alice, Mimic, Sentry)
 * - Real-time voice parameter control (pitch, rate, volume)
 * - Live voice commands for speech adjustment
 * - Voice preview and selection interface
 * - Custom voice presets and profiles
 */

const VoiceTTSManager = ({ 
  currentAgent, 
  onVoiceParametersChange, 
  isEnabled = true,
  allowLiveAdjustment = true 
}) => {
  const [isSupported, setIsSupported] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentUtterance, setCurrentUtterance] = useState(null);
  const [voiceQueue, setVoiceQueue] = useState([]);
  
  // Voice assignments for each persona
  const [personaVoices, setPersonaVoices] = useState({
    alden: {
      voiceURI: 'Microsoft David Desktop - English (United States)',
      name: 'David',
      pitch: 1.0,
      rate: 1.0,
      volume: 0.8,
      preset: 'professional'
    },
    alice: {
      voiceURI: 'Microsoft Zira Desktop - English (United States)',
      name: 'Zira',
      pitch: 1.2,
      rate: 0.9,
      volume: 0.7,
      preset: 'empathetic'
    },
    mimic: {
      voiceURI: 'Google UK English Male',
      name: 'UK Male',
      pitch: 0.8,
      rate: 1.1,
      volume: 0.9,
      preset: 'dynamic'
    },
    sentry: {
      voiceURI: 'Microsoft Mark Desktop - English (United States)',
      name: 'Mark',
      pitch: 0.7,
      rate: 0.8,
      volume: 1.0,
      preset: 'authoritative'
    }
  });

  // Voice presets for different contexts
  const voicePresets = {
    professional: { pitch: 1.0, rate: 1.0, volume: 0.8, description: 'Clear and professional' },
    empathetic: { pitch: 1.2, rate: 0.9, volume: 0.7, description: 'Warm and caring' },
    dynamic: { pitch: 0.9, rate: 1.2, volume: 0.9, description: 'Energetic and versatile' },
    authoritative: { pitch: 0.7, rate: 0.8, volume: 1.0, description: 'Strong and commanding' },
    casual: { pitch: 1.1, rate: 1.1, volume: 0.8, description: 'Relaxed and friendly' },
    dramatic: { pitch: 1.3, rate: 0.7, volume: 0.9, description: 'Expressive and theatrical' }
  };

  const synthRef = useRef(null);
  const [showVoiceControl, setShowVoiceControl] = useState(false);

  useEffect(() => {
    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      setIsSupported(true);
      
      // Load available voices
      const loadVoices = () => {
        const voices = synthRef.current.getVoices();
        setAvailableVoices(voices);
        
        // Auto-assign best voices if not already set
        if (voices.length > 0) {
          autoAssignOptimalVoices(voices);
        }
      };

      // Load voices immediately and on voiceschanged event
      loadVoices();
      synthRef.current.onvoiceschanged = loadVoices;
    } else {
      console.warn('Speech Synthesis not supported in this browser');
      setIsSupported(false);
    }

    return () => {
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  // Auto-assign optimal voices based on available system voices
  const autoAssignOptimalVoices = (voices) => {
    const voiceAssignments = {
      alden: findBestVoice(voices, ['david', 'male', 'english'], 'professional'),
      alice: findBestVoice(voices, ['zira', 'female', 'english'], 'empathetic'),
      mimic: findBestVoice(voices, ['google', 'male', 'uk'], 'dynamic'),
      sentry: findBestVoice(voices, ['mark', 'male', 'deep'], 'authoritative')
    };

    setPersonaVoices(prev => {
      const updated = { ...prev };
      Object.keys(voiceAssignments).forEach(persona => {
        if (voiceAssignments[persona]) {
          updated[persona] = {
            ...updated[persona],
            voiceURI: voiceAssignments[persona].voiceURI,
            name: voiceAssignments[persona].name
          };
        }
      });
      return updated;
    });
  };

  // Find best matching voice based on keywords and preferences
  const findBestVoice = (voices, keywords, preferredPreset) => {
    let bestVoice = null;
    let bestScore = 0;

    voices.forEach(voice => {
      let score = 0;
      const voiceName = voice.name.toLowerCase();
      const voiceURI = voice.voiceURI.toLowerCase();

      keywords.forEach(keyword => {
        if (voiceName.includes(keyword) || voiceURI.includes(keyword)) {
          score += 1;
        }
      });

      // Prefer local voices
      if (voice.localService) score += 0.5;
      
      // Prefer English voices
      if (voice.lang.startsWith('en')) score += 0.3;

      if (score > bestScore) {
        bestScore = score;
        bestVoice = voice;
      }
    });

    return bestVoice;
  };

  // Main speak function for AI responses
  const speak = (text, agent = currentAgent, options = {}) => {
    if (!isSupported || !text || !isEnabled) return;

    // Stop current speech if interrupting
    if (options.interrupt && synthRef.current.speaking) {
      synthRef.current.cancel();
    }

    const agentVoice = personaVoices[agent] || personaVoices.alden;
    const selectedVoice = availableVoices.find(voice => 
      voice.voiceURI === agentVoice.voiceURI || voice.name === agentVoice.name
    );

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Apply voice settings
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    utterance.pitch = options.pitch ?? agentVoice.pitch;
    utterance.rate = options.rate ?? agentVoice.rate;
    utterance.volume = options.volume ?? agentVoice.volume;

    // Event handlers
    utterance.onstart = () => {
      setIsSpeaking(true);
      setCurrentUtterance(utterance);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentUtterance(null);
      processVoiceQueue();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setCurrentUtterance(null);
    };

    // Queue or speak immediately
    if (synthRef.current.speaking) {
      setVoiceQueue(prev => [...prev, { utterance, agent, text }]);
    } else {
      synthRef.current.speak(utterance);
    }
  };

  // Process queued speech
  const processVoiceQueue = () => {
    if (voiceQueue.length > 0) {
      const next = voiceQueue[0];
      setVoiceQueue(prev => prev.slice(1));
      synthRef.current.speak(next.utterance);
    }
  };

  // Stop current speech
  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setVoiceQueue([]);
      setIsSpeaking(false);
      setCurrentUtterance(null);
    }
  };

  // Pause/resume speech
  const pauseSpeaking = () => {
    if (synthRef.current && synthRef.current.speaking) {
      if (synthRef.current.paused) {
        synthRef.current.resume();
      } else {
        synthRef.current.pause();
      }
    }
  };

  // Update voice parameters for a persona
  const updatePersonaVoice = (persona, parameter, value) => {
    setPersonaVoices(prev => ({
      ...prev,
      [persona]: {
        ...prev[persona],
        [parameter]: value
      }
    }));

    // Notify parent component
    if (onVoiceParametersChange) {
      onVoiceParametersChange(persona, parameter, value);
    }
  };

  // Apply voice preset to persona
  const applyPreset = (persona, presetName) => {
    const preset = voicePresets[presetName];
    if (preset) {
      setPersonaVoices(prev => ({
        ...prev,
        [persona]: {
          ...prev[persona],
          ...preset,
          preset: presetName
        }
      }));
    }
  };

  // Process live voice adjustment commands
  const processVoiceAdjustmentCommand = (command, agent = currentAgent) => {
    if (!allowLiveAdjustment) return false;

    const lowerCommand = command.toLowerCase();
    const currentVoice = personaVoices[agent];
    
    // Speech rate adjustments
    if (lowerCommand.includes('speak more slowly') || lowerCommand.includes('slow down')) {
      const newRate = Math.max(0.1, currentVoice.rate - 0.2);
      updatePersonaVoice(agent, 'rate', newRate);
      speak(`I'll speak more slowly now.`, agent, { interrupt: true });
      return true;
    }
    
    if (lowerCommand.includes('speak faster') || lowerCommand.includes('speed up')) {
      const newRate = Math.min(2.0, currentVoice.rate + 0.2);
      updatePersonaVoice(agent, 'rate', newRate);
      speak(`I'll speak faster now.`, agent, { interrupt: true });
      return true;
    }

    // Pitch adjustments
    if (lowerCommand.includes('lower the pitch') || lowerCommand.includes('deeper voice')) {
      const newPitch = Math.max(0.1, currentVoice.pitch - 0.2);
      updatePersonaVoice(agent, 'pitch', newPitch);
      speak(`I've lowered my pitch.`, agent, { interrupt: true });
      return true;
    }
    
    if (lowerCommand.includes('higher pitch') || lowerCommand.includes('raise the pitch')) {
      const newPitch = Math.min(2.0, currentVoice.pitch + 0.2);
      updatePersonaVoice(agent, 'pitch', newPitch);
      speak(`I've raised my pitch.`, agent, { interrupt: true });
      return true;
    }

    // Volume adjustments
    if (lowerCommand.includes('speak up') || lowerCommand.includes('louder') || lowerCommand.includes('increase volume')) {
      const newVolume = Math.min(1.0, currentVoice.volume + 0.1);
      updatePersonaVoice(agent, 'volume', newVolume);
      speak(`I'll speak louder now.`, agent, { interrupt: true });
      return true;
    }
    
    if (lowerCommand.includes('quieter') || lowerCommand.includes('softer') || lowerCommand.includes('lower volume')) {
      const newVolume = Math.max(0.1, currentVoice.volume - 0.1);
      updatePersonaVoice(agent, 'volume', newVolume);
      speak(`I'll speak more quietly now.`, agent, { interrupt: true });
      return true;
    }

    // Preset applications
    Object.keys(voicePresets).forEach(presetName => {
      if (lowerCommand.includes(`use ${presetName} voice`) || lowerCommand.includes(`${presetName} preset`)) {
        applyPreset(agent, presetName);
        speak(`I've switched to ${presetName} voice mode.`, agent, { interrupt: true });
        return true;
      }
    });

    return false;
  };

  // Preview voice with sample text
  const previewVoice = (persona) => {
    const sampleTexts = {
      alden: "Hello! I'm Alden, your productivity and scheduling assistant. How can I help you stay organized today?",
      alice: "Hi there. I'm Alice, and I'm here to listen and support you through whatever you're feeling right now.",
      mimic: "Greetings! I'm Mimic, your dynamic persona creator. I can become any character you need for your tasks.",
      sentry: "Security status: All systems operational. I'm Sentry, monitoring and protecting your digital workspace."
    };
    
    speak(sampleTexts[persona] || sampleTexts.alden, persona, { interrupt: true });
  };

  // Get voice status for UI display
  const getVoiceStatus = () => ({
    isSupported,
    isSpeaking,
    currentAgent,
    availableVoices: availableVoices.length,
    queueLength: voiceQueue.length,
    currentVoice: personaVoices[currentAgent]
  });

  if (!isSupported) {
    return (
      <div className="voice-tts-manager unsupported">
        <div className="unsupported-message">
          <h3>🔇 Voice Output Not Available</h3>
          <p>Your browser doesn't support text-to-speech functionality.</p>
          <p>Please use a modern browser like Chrome, Firefox, or Edge for voice features.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-tts-manager">
      {/* Voice Status Display */}
      <div className="voice-status-display">
        <div className={`speaking-indicator ${isSpeaking ? 'active' : ''}`}>
          <span className="status-icon">{isSpeaking ? '🔊' : '🔇'}</span>
          <span className="status-text">
            {isSpeaking ? `${currentAgent} is speaking...` : 'Voice output ready'}
          </span>
          {voiceQueue.length > 0 && (
            <span className="queue-indicator">({voiceQueue.length} queued)</span>
          )}
        </div>

        {/* Voice Control Buttons */}
        <div className="voice-controls">
          <button 
            onClick={pauseSpeaking}
            disabled={!isSpeaking}
            className="control-btn pause-btn"
            title={synthRef.current?.paused ? "Resume" : "Pause"}
          >
            {synthRef.current?.paused ? '▶️' : '⏸️'}
          </button>
          <button 
            onClick={stopSpeaking}
            disabled={!isSpeaking}
            className="control-btn stop-btn"
            title="Stop speaking"
          >
            ⏹️
          </button>
          <button 
            onClick={() => setShowVoiceControl(!showVoiceControl)}
            className="control-btn settings-btn"
            title="Voice settings"
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* Voice Configuration Panel */}
      {showVoiceControl && (
        <div className="voice-config-panel">
          <h4>🎤 Voice Configuration</h4>
          
          {/* Current Agent Voice Settings */}
          <div className="current-agent-settings">
            <h5>{currentAgent.toUpperCase()} Voice Settings</h5>
            
            {/* Voice Selection */}
            <div className="setting-group">
              <label>Voice:</label>
              <select
                value={personaVoices[currentAgent].voiceURI}
                onChange={(e) => {
                  const selectedVoice = availableVoices.find(v => v.voiceURI === e.target.value);
                  updatePersonaVoice(currentAgent, 'voiceURI', e.target.value);
                  updatePersonaVoice(currentAgent, 'name', selectedVoice?.name || 'Unknown');
                }}
              >
                {availableVoices.map(voice => (
                  <option key={voice.voiceURI} value={voice.voiceURI}>
                    {voice.name} ({voice.lang})
                  </option>
                ))}
              </select>
            </div>

            {/* Voice Parameters */}
            <div className="parameter-controls">
              <div className="parameter-slider">
                <label>Pitch: {personaVoices[currentAgent].pitch.toFixed(1)}</label>
                <input
                  type="range"
                  min="0.1"
                  max="2.0"
                  step="0.1"
                  value={personaVoices[currentAgent].pitch}
                  onChange={(e) => updatePersonaVoice(currentAgent, 'pitch', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="parameter-slider">
                <label>Speed: {personaVoices[currentAgent].rate.toFixed(1)}</label>
                <input
                  type="range"
                  min="0.1"
                  max="2.0"
                  step="0.1"
                  value={personaVoices[currentAgent].rate}
                  onChange={(e) => updatePersonaVoice(currentAgent, 'rate', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="parameter-slider">
                <label>Volume: {personaVoices[currentAgent].volume.toFixed(1)}</label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={personaVoices[currentAgent].volume}
                  onChange={(e) => updatePersonaVoice(currentAgent, 'volume', parseFloat(e.target.value))}
                />
              </div>
            </div>

            {/* Voice Presets */}
            <div className="voice-presets">
              <label>Voice Presets:</label>
              <div className="preset-buttons">
                {Object.entries(voicePresets).map(([presetName, preset]) => (
                  <button
                    key={presetName}
                    onClick={() => applyPreset(currentAgent, presetName)}
                    className={`preset-btn ${personaVoices[currentAgent].preset === presetName ? 'active' : ''}`}
                    title={preset.description}
                  >
                    {presetName}
                  </button>
                ))}
              </div>
            </div>

            {/* Preview Button */}
            <button
              onClick={() => previewVoice(currentAgent)}
              className="preview-btn"
            >
              🎵 Preview Voice
            </button>
          </div>

          {/* All Personas Quick View */}
          <div className="all-personas-summary">
            <h5>All Persona Voices</h5>
            {Object.entries(personaVoices).map(([persona, voice]) => (
              <div key={persona} className="persona-voice-summary">
                <span className="persona-name">{persona.toUpperCase()}</span>
                <span className="voice-info">{voice.name} | {voice.preset}</span>
                <button
                  onClick={() => previewVoice(persona)}
                  className="mini-preview-btn"
                >
                  ▶️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Voice Command Help */}
      {allowLiveAdjustment && (
        <div className="voice-command-help">
          <details>
            <summary>💬 Voice Commands for Speech Control</summary>
            <div className="command-list">
              <div><strong>Speed:</strong> "speak more slowly", "speak faster"</div>
              <div><strong>Pitch:</strong> "lower the pitch", "higher pitch"</div>
              <div><strong>Volume:</strong> "speak up", "quieter"</div>
              <div><strong>Presets:</strong> "use professional voice", "casual preset"</div>
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

// Export both component and utility functions
export default VoiceTTSManager;
export { VoiceTTSManager };