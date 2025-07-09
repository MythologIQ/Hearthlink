import React, { useState, useEffect } from 'react';
import './App.css';

// Import components
import AldenInterface from './personas/alden/AldenInterface';
import Dashboard from './components/Dashboard';
import VoiceInterface from './components/VoiceInterface';
import AccessibilityPanel from './components/AccessibilityPanel';
import HelpMenu from './components/HelpMenu';

function App() {
  const [currentPersona, setCurrentPersona] = useState('alden');
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    highContrast: false,
    screenReader: false,
    voiceFeedback: false,
    fontSize: 'medium'
  });
  const [showHelp, setShowHelp] = useState(false);
  const [appVersion, setAppVersion] = useState('1.1.0');

  // Voice routing state
  const [currentAgent, setCurrentAgent] = useState('alden');
  const [availableAgents] = useState({
    local: ['alden', 'alice', 'mimic', 'sentry'],
    external: ['gemini-cli', 'google-api', 'trae-cli']
  });

  useEffect(() => {
    // Initialize Electron-specific features
    if (window.electronAPI) {
      // Get app version
      window.electronAPI.getAppVersion().then(version => {
        setAppVersion(version);
      });

      // Set up keyboard shortcuts
      const handleKeyDown = (event) => {
        // F1 - Help
        if (event.key === 'F1') {
          event.preventDefault();
          setShowHelp(true);
        }
        
        // Ctrl+Shift+A - Toggle accessibility panel
        if (event.ctrlKey && event.shiftKey && event.key === 'A') {
          event.preventDefault();
          setShowHelp(prev => !prev);
        }
        
        // Ctrl+Shift+V - Toggle voice interface
        if (event.ctrlKey && event.shiftKey && event.key === 'V') {
          event.preventDefault();
          setIsVoiceActive(prev => !prev);
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, []);

  // Handle accessibility updates
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onAccessibilityUpdate((data) => {
        setAccessibilitySettings(prev => ({
          ...prev,
          [data.feature]: !prev[data.feature]
        }));
      });
    }
  }, []);

  // Apply accessibility settings
  useEffect(() => {
    if (window.accessibility) {
      window.accessibility.setHighContrast(accessibilitySettings.highContrast);
      window.accessibility.setFontSize(accessibilitySettings.fontSize);
    }
  }, [accessibilitySettings]);

  const handlePersonaChange = (persona) => {
    setCurrentPersona(persona);
    setCurrentAgent(persona); // Update current agent when persona changes
    if (window.accessibility && accessibilitySettings.voiceFeedback) {
      window.accessibility.speak(`Switched to ${persona} persona`);
    }
  };

  const handleAgentChange = (agent) => {
    setCurrentAgent(agent);
    // Update persona if agent is a local agent
    if (availableAgents.local.includes(agent)) {
      setCurrentPersona(agent);
    }
    if (window.accessibility && accessibilitySettings.voiceFeedback) {
      window.accessibility.speak(`Switched to ${agent} agent`);
    }
  };

  const handleVoiceCommand = (command, targetAgent) => {
    // Log voice command with agent routing
    console.log(`Voice command routed to ${targetAgent}:`, command);
    
    if (window.electronAPI) {
      window.electronAPI.sendVoiceCommand(command, targetAgent);
    }
    
    if (window.voiceCommands) {
      const processed = window.voiceCommands.processCommand(command, targetAgent);
      if (processed) {
        if (window.showVoiceIndicator) {
          window.showVoiceIndicator(targetAgent);
        }
      }
    }
  };

  const toggleAccessibility = (feature) => {
    if (window.electronAPI) {
      window.electronAPI.toggleAccessibility(feature);
    }
  };

  return (
    <div className={`App ${accessibilitySettings.highContrast ? 'high-contrast' : ''}`}>
      {/* Header */}
      <header className="App-header">
        <div className="header-content">
          <img 
            src="/assets/header-logo.png" 
            alt="Hearthlink" 
            className="header-logo"
          />
          <h1>Hearthlink</h1>
          <div className="header-controls">
            <button 
              onClick={() => setIsVoiceActive(!isVoiceActive)}
              className={`voice-toggle ${isVoiceActive ? 'active' : ''}`}
              aria-label="Toggle voice interface"
            >
              🎤
            </button>
            <button 
              onClick={() => setShowHelp(!showHelp)}
              className="help-toggle"
              aria-label="Open help menu"
            >
              ❓
            </button>
            <button 
              onClick={() => toggleAccessibility('high-contrast')}
              className={`accessibility-toggle ${accessibilitySettings.highContrast ? 'active' : ''}`}
              aria-label="Toggle high contrast mode"
            >
              👁️
            </button>
          </div>
        </div>
        <div className="version-info">v{appVersion}</div>
      </header>

      {/* Main Content */}
      <main className="App-main">
        {/* Persona Selector */}
        <nav className="persona-nav">
          <button 
            onClick={() => handlePersonaChange('alden')}
            className={`persona-btn ${currentPersona === 'alden' ? 'active' : ''}`}
            aria-label="Switch to Alden persona"
          >
            <img src="/assets/Alden.png" alt="Alden" />
            <span>Alden</span>
          </button>
          <button 
            onClick={() => handlePersonaChange('alice')}
            className={`persona-btn ${currentPersona === 'alice' ? 'active' : ''}`}
            aria-label="Switch to Alice persona"
          >
            <img src="/assets/Alice.png" alt="Alice" />
            <span>Alice</span>
          </button>
          <button 
            onClick={() => handlePersonaChange('dashboard')}
            className={`persona-btn ${currentPersona === 'dashboard' ? 'active' : ''}`}
            aria-label="Switch to Dashboard"
          >
            <img src="/assets/Core.png" alt="Dashboard" />
            <span>Dashboard</span>
          </button>
        </nav>

        {/* Content Area */}
        <div className="content-area">
          {currentPersona === 'alden' && (
            <AldenInterface 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
          {currentPersona === 'alice' && (
            <div className="alice-interface">
              <h2>Alice Interface</h2>
              <p>Alice's cognitive behavioral interface will be implemented here.</p>
            </div>
          )}
          {currentPersona === 'dashboard' && (
            <Dashboard 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
        </div>
      </main>

      {/* Voice Interface */}
      {isVoiceActive && (
        <VoiceInterface 
          onCommand={handleVoiceCommand}
          isActive={isVoiceActive}
          onClose={() => setIsVoiceActive(false)}
          currentAgent={currentAgent}
          availableAgents={availableAgents}
          onAgentChange={handleAgentChange}
        />
      )}

      {/* Accessibility Panel */}
      <AccessibilityPanel 
        settings={accessibilitySettings}
        onSettingChange={toggleAccessibility}
        isVisible={showHelp}
        onClose={() => setShowHelp(false)}
      />

      {/* Help Menu */}
      <HelpMenu 
        isVisible={showHelp}
        onClose={() => setShowHelp(false)}
        appVersion={appVersion}
      />

      {/* Voice Command Indicator */}
      {isVoiceActive && (
        <div className="voice-indicator">
          Listening for voice commands... (Current agent: {currentAgent})
        </div>
      )}
    </div>
  );
}

export default App; 