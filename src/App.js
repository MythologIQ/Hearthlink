import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Import components
import AldenInterface from './personas/alden/AldenInterface';
import AldenMainScreen from './components/AldenMainScreen';
import VaultInterface from './components/VaultInterface';
import CoreInterface from './components/CoreInterface';
import Dashboard from './components/Dashboard';
import SynapseInterface from './components/SynapseInterface';
import VoiceInterface from './components/VoiceInterface';
import AccessibilityPanel from './components/AccessibilityPanel';
import HelpMenu from './components/HelpMenu';
import SettingsManager from './components/SettingsManager';
import ConferenceSystem from './components/ConferenceSystem';
import ClaudeGoogleDelegation from './components/ClaudeGoogleDelegation';
import SynapseGateway from './components/SynapseGateway';
import LaunchPage from './components/LaunchPage';
import SentryMonitor from './components/SentryMonitor.tsx';
import SentryInterface from './components/SentryInterface';
import TokenGenerator from './components/TokenGenerator';
import AliceInterface from './components/AliceInterface';
import MimicInterface from './components/MimicInterface';
import SuperClaudeInterface from './components/SuperClaudeInterface';
// import useTauriIntegration from './hooks/useTauriIntegration';

function App() {
  // console.log('App component rendering...'); // Debug log
  
  // Tauri integration for native desktop features
  // const tauri = useTauriIntegration();
  
  const [currentPersona, setCurrentPersona] = useState('alden');
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    highContrast: false,
    screenReader: false,
    voiceFeedback: false,
    fontSize: 'medium'
  });
  const [showHelp, setShowHelp] = useState(false);
  const [appVersion, setAppVersion] = useState('1.3.0');
  const [isLoading, setIsLoading] = useState(true);
  const [isRadialMenuOpen, setIsRadialMenuOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(() => {
    const forceSettings = localStorage.getItem('forceSettings') === 'true';
    console.log('App.js - showSettings initial state:', { forceSettings, localStorage: localStorage.getItem('forceSettings') });
    return forceSettings || false;
  });
  const [systemSettings, setSystemSettings] = useState({});
  const [showSuperClaude, setShowSuperClaude] = useState(false);

  // Feature flags for conditional rendering
  const [featureFlags, setFeatureFlags] = useState({
    synapseEnabled: true, // Enable Synapse module for configuration
    externalAgentsEnabled: true, // Enable external agents
    devModeEnabled: true // Enable dev mode
  });

  // Voice routing state
  const [currentAgent, setCurrentAgent] = useState('alden');
  const [availableAgents] = useState({
    local: ['alden', 'alice', 'mimic', 'sentry'],
    external: ['gemini-cli', 'google-api', 'trae-cli']
  });

  // Load feature flags from environment or config
  useEffect(() => {
    // In production, this would load from secure config
    const loadFeatureFlags = async () => {
      try {
        // Check for environment variables or config files
        const synapseEnabled = process.env.REACT_APP_SYNAPSE_ENABLED !== 'false'; // Default to true unless explicitly disabled
        const externalAgentsEnabled = process.env.REACT_APP_EXTERNAL_AGENTS_ENABLED !== 'false'; // Default to true unless explicitly disabled
        const devModeEnabled = process.env.NODE_ENV === 'development';
        
        setFeatureFlags({
          synapseEnabled,
          externalAgentsEnabled,
          devModeEnabled
        });
        
        // console.log('Feature flags loaded:', { synapseEnabled, externalAgentsEnabled, devModeEnabled });
      } catch (error) {
        console.warn('Failed to load feature flags, using defaults:', error);
      }
    };
    
    loadFeatureFlags();
  }, []);

  // console.log('App state initialized:', { currentPersona, currentAgent, isLoading }); // Debug log

  useEffect(() => {
    // console.log('App useEffect running...'); // Debug log
    
    // Initialize Electron-specific features
    if (window.electronAPI) {
      // console.log('Electron API detected'); // Debug log
      
      // Get app version
      window.electronAPI.getAppVersion().then(version => {
        // console.log('App version:', version); // Debug log
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
    } else {
      // console.log('Electron API not detected'); // Debug log
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
    // console.log('Changing persona to:', persona); // Debug log
    setCurrentPersona(persona);
    setCurrentAgent(persona); // Update current agent when persona changes
    if (window.accessibility && accessibilitySettings.voiceFeedback) {
      window.accessibility.speak(`Switched to ${persona} persona`);
    }
  };

  const handleAgentChange = (agent) => {
    // console.log('Changing agent to:', agent); // Debug log
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
    // console.log(`Voice command routed to ${targetAgent}:`, command);
    
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


  const handleModuleSelect = (moduleName) => {
    // console.log('Module selected:', moduleName); // Debug log
    
    try {
      // Map module names to persona names
      const moduleMap = {
        'Core': 'core',
        'Alden': 'alden',
        'Alice': 'alice',
        'Synapse': 'synapse',
        'Vault': 'vault',
        'Mimic': 'mimic',
        'Sentry': 'sentry'
      };
      
      const persona = moduleMap[moduleName] || 'alden';
      setCurrentPersona(persona);
      setCurrentAgent(persona.toLowerCase());
      setIsLoading(false); // This will trigger navigation to the selected module
      
      // console.log('Module transition initiated:', persona);
      
    } catch (error) {
      console.error('Error in module selection:', error);
      // Fallback to Alden if there's an error
      setCurrentPersona('alden');
      setCurrentAgent('alden');
      setIsLoading(false);
    }
  };

  // console.log('About to render App component...'); // Debug log

  // Main app content wrapper
  const AppContent = () => (
    <div className={`App ${accessibilitySettings.highContrast ? 'high-contrast' : ''}`}>
      
      {/* Global Stylized Banner */}
      <header className="hearthlink-banner">
        <div className="banner-left">
          <div className="persona-indicator">
            <img 
              src={`./assets/${currentPersona.charAt(0).toUpperCase() + currentPersona.slice(1)}.png`} 
              alt={currentPersona}
              className="persona-icon"
            />
            <div className="persona-name">{currentPersona.toUpperCase()}</div>
          </div>
          
          <div className="status-bar">
            <div className="status-group">
              <div className="status-orb llm-status" title="LLM Status"></div>
              <span className="status-label">LLM</span>
            </div>
            <div className="status-group">
              <div className="status-orb vault-status" title="Vault Status"></div>
              <span className="status-label">VAULT</span>
            </div>
            <div className="status-group">
              <div className="status-orb sentry-status" title="Sentry Status"></div>
              <span className="status-label">SENTRY</span>
            </div>
            <div className="status-group">
              <div className="status-orb synapse-status" title="Synapse Status"></div>
              <span className="status-label">SYNAPSE</span>
            </div>
          </div>
        </div>
        
        <div className="banner-center">
          {/* Hearthlink Icon as Radial Button */}
          <div className="radial-nav-container">
            <button 
              className={`radial-center-btn ${isRadialMenuOpen ? 'active' : ''}`}
              onClick={() => setIsRadialMenuOpen(!isRadialMenuOpen)}
              aria-label="Open module navigation"
            >
              <img 
                src="./assets/Hearthlink.png" 
                alt="Hearthlink" 
                className="hearthlink-icon"
              />
            </button>
            
            {/* Radial Menu Items - Downward Arc Only */}
            <div className={`radial-menu-items ${isRadialMenuOpen ? 'open' : ''}`}>
              {[
                { id: 'synapse', label: 'SYNAPSE', angle: 180, icon: './assets/Synapse.png' },
                { id: 'alden', label: 'ALDEN', angle: 150, icon: './assets/Alden.png' },
                { id: 'alice', label: 'ALICE', angle: 120, icon: './assets/Alice.png' },
                { id: 'sentry', label: 'SENTRY', angle: 90, icon: './assets/Sentry.png' },
                { id: 'mimic', label: 'MIMIC', angle: 60, icon: './assets/Mimic.png' },
                { id: 'core', label: 'CORE', angle: 30, icon: './assets/Core.png' },
                { id: 'vault', label: 'VAULT', angle: 0, icon: './assets/Vault.png' }
              ].map((module) => {
                const radian = (module.angle * Math.PI) / 180;
                const radius = 180;
                const x = Math.cos(radian) * radius;
                const y = Math.sin(radian) * radius;
                
                return (
                  <button
                    key={module.id}
                    className={`radial-menu-item ${currentPersona === module.id ? 'active' : ''}`}
                    style={{
                      transform: `translate(${x}px, ${y}px)`,
                      transitionDelay: `${Math.abs(module.angle - 90) * 2}ms`,
                      zIndex: 10000
                    }}
                    onClick={() => {
                      handlePersonaChange(module.id);
                      setIsRadialMenuOpen(false);
                    }}
                    title={`Switch to ${module.label} module`}
                    aria-label={`Switch to ${module.label} module`}
                  >
                    <img 
                      src={module.icon} 
                      alt={module.label}
                      className="radial-menu-icon"
                    />
                  </button>
                );
              })}
            </div>
            
          </div>
        </div>
        
        <div className="banner-right">
          <div className="system-controls">
            <div className="control-group">
              <button 
                onClick={() => setIsVoiceActive(!isVoiceActive)}
                className={`control-btn voice-toggle ${isVoiceActive ? 'active' : ''}`}
                aria-label="Toggle voice interface"
              >
                <img 
                  src="./assets/Voice.png" 
                  alt="Voice" 
                  className="control-icon"
                />
              </button>
              <span className="control-label">VOICE</span>
            </div>
            <div className="control-group">
              <button 
                onClick={() => setShowHelp(!showHelp)}
                className="control-btn help-toggle"
                aria-label="Open help menu"
              >
                <img 
                  src="./assets/Help.png" 
                  alt="Help" 
                  className="control-icon"
                />
              </button>
              <span className="control-label">HELP</span>
            </div>
            <div className="control-group">
              <button 
                onClick={() => toggleAccessibility('high-contrast')}
                className={`control-btn accessibility-toggle ${accessibilitySettings.highContrast ? 'active' : ''}`}
                aria-label="Toggle high contrast mode"
              >
                <img 
                  src="./assets/Accessibility.png" 
                  alt="Accessibility" 
                  className="control-icon"
                />
              </button>
              <span className="control-label">ACCESS</span>
            </div>
            <div className="control-group">
              <button 
                onClick={() => setShowSettings(!showSettings)}
                className="control-btn settings-toggle"
                aria-label="Open settings"
              >
                <div className="settings-icon control-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                    <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 3c-.46-4.17-3.77-7.48-7.94-7.94V1h-2v2.06C6.83 3.52 3.52 6.83 3.06 11H1v2h2.06c.46 4.17 3.77 7.48 7.94 7.94V23h2v-2.06c4.17-.46 7.48-3.77 7.94-7.94H23v-2h-2.06zM12 19c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/>
                  </svg>
                </div>
              </button>
              <span className="control-label">SETTINGS</span>
            </div>
            <div className="control-group">
              <button 
                onClick={() => setShowSuperClaude(!showSuperClaude)}
                className="control-btn superclaude-toggle"
                aria-label="Open SuperClaude AI"
              >
                <div className="superclaude-icon control-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    <circle cx="12" cy="8" r="2"/>
                    <path d="M12 14c-2.5 0-4.5 1-4.5 2.5V18h9v-1.5C16.5 15 14.5 14 12 14z"/>
                  </svg>
                </div>
              </button>
              <span className="control-label">SUPERCLAUDE</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="App-main">
        {/* Deprecated tabbed navigation removed - now using radial menu in banner */}

        {/* Content Area */}
        <div className="content-area">
          {currentPersona === 'alden' && (
            <AldenMainScreen 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
          {currentPersona === 'alice' && (
            <AliceInterface 
              isVisible={true}
              onClose={() => setCurrentPersona('alden')}
            />
          )}
          {currentPersona === 'vault' && (
            <VaultInterface 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
          {currentPersona === 'mimic' && (
            <MimicInterface 
              isVisible={true}
              onClose={() => setCurrentPersona('alden')}
            />
          )}
          {currentPersona === 'sentry' && (
            <SentryInterface 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
          {currentPersona === 'core' && (
            <CoreInterface 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={handleVoiceCommand}
              currentAgent={currentAgent}
            />
          )}
          {currentPersona === 'synapse' && featureFlags.synapseEnabled && (
            <SynapseGateway 
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

      {/* Settings Manager */}
      <SettingsManager
        isVisible={showSettings}
        onClose={() => setShowSettings(false)}
        onSettingsChange={(settings) => {
          setSystemSettings(settings);
          // Apply settings changes to the application
          if (settings.general) {
            if (settings.general.voiceEnabled !== undefined) {
              setIsVoiceActive(settings.general.voiceEnabled);
            }
          }
        }}
      />

      {/* SuperClaude Advanced AI Interface */}
      <SuperClaudeInterface
        isVisible={showSuperClaude}
        onClose={() => setShowSuperClaude(false)}
      />
    </div>
  );

  // Placeholder components for module routes
  const CoreModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <CoreInterface 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={handleVoiceCommand}
            currentAgent={currentAgent}
          />
        </div>
      </main>
    </AppContent>
  );

  const AldenModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <AldenMainScreen 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={handleVoiceCommand}
            currentAgent={currentAgent}
          />
        </div>
      </main>
    </AppContent>
  );

  const SynapseModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <div className="synapse-interface starcraft-module">
            <div className="module-header">
              <h2>SYNAPSE GATEWAY</h2>
              <div className="module-subtitle">Security Gateway</div>
            </div>
            <div className="module-content">
              <SynapseGateway 
                accessibilitySettings={accessibilitySettings}
                onVoiceCommand={handleVoiceCommand}
                currentAgent={currentAgent}
              />
            </div>
          </div>
        </div>
      </main>
    </AppContent>
  );

  const VaultModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <VaultInterface 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={handleVoiceCommand}
            currentAgent={currentAgent}
          />
        </div>
      </main>
    </AppContent>
  );

  const MimicModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <div className="mimic-interface starcraft-module">
            <div className="module-header">
              <h2>MIMIC ADAPTIVE</h2>
              <div className="module-subtitle">Adaptive Intelligence System</div>
            </div>
            <div className="module-content">
              <p>Mimic adaptive intelligence interface.</p>
              <div className="status-indicator">STATUS: DEVELOPMENT</div>
            </div>
          </div>
        </div>
      </main>
    </AppContent>
  );

  const SentryModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <SentryInterface 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={handleVoiceCommand}
            currentAgent={currentAgent}
          />
        </div>
      </main>
    </AppContent>
  );

  const AliceModule = () => (
    <AppContent>
      <main className="App-main">
        <div className="content-area">
          <AliceInterface 
            isVisible={true}
            onClose={() => {}}
          />
        </div>
      </main>
    </AppContent>
  );

  return (
    <Router>
      
      <Routes>
        {/* Launch Page Route */}
        <Route path="/" element={
          (() => {
            // console.log('Routing decision:', { isLoading, currentPersona, navigateTo: `/${currentPersona}` });
            return isLoading ? 
              <LaunchPage onModuleSelect={handleModuleSelect} /> : 
              <Navigate to={`/${currentPersona}`} replace />;
          })()
        } />
        
        {/* Module Routes */}
        <Route path="/core" element={<CoreModule />} />
        <Route path="/alden" element={<AldenModule />} />
        <Route path="/synapse" element={<SynapseModule />} />
        <Route path="/vault" element={<VaultModule />} />
        <Route path="/mimic" element={<MimicModule />} />
        <Route path="/sentry" element={<SentryModule />} />
        <Route path="/alice" element={<AliceModule />} />
        <Route path="/tokens" element={<TokenGenerator />} />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App; 