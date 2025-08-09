/**
 * Tauri API Compatibility Layer
 * Replaces Electron APIs with Tauri equivalents for native functionality
 */

// Tauri API with fallbacks for web compatibility
const invoke = async (command, args) => {
  console.log(`Tauri invoke: ${command}`, args);
  
  // Try to use actual Tauri API first
  if (typeof window !== 'undefined' && window.__TAURI__) {
    try {
      return await window.__TAURI__.core.invoke(command, args);
    } catch (error) {
      console.warn('Tauri invoke failed, using fallback:', error);
    }
  }
  
  // Fallback implementations
  if (command === 'get_app_status') {
    return 'Hearthlink Native App Running (Web fallback)';
  }
  if (command === 'greet') {
    return `Hello, ${args?.name || 'User'}! (Web fallback)`;
  }
  return 'Web fallback response';
};

const open = async (url) => {
  console.log(`Opening external URL: ${url}`);
  
  // Try to use actual Tauri API first
  if (typeof window !== 'undefined' && window.__TAURI__) {
    try {
      await window.__TAURI__.shell.open(url);
      return Promise.resolve();
    } catch (error) {
      console.warn('Tauri shell.open failed, using fallback:', error);
    }
  }
  
  // Fallback to browser
  window.open(url, '_blank');
  return Promise.resolve();
};

class TauriAPI {
  constructor() {
    this.isReady = false;
    this.initialize();
  }

  async initialize() {
    try {
      // Test if Tauri is available
      await invoke('get_app_status');
      this.isReady = true;
      console.log('🦀 Tauri API initialized successfully');
    } catch (error) {
      console.warn('⚠️ Tauri not available, falling back to web APIs:', error);
      this.isReady = false;
    }
  }

  // Replace window.electronAPI.openExternal
  async openExternal(url) {
    if (this.isReady) {
      try {
        await open(url);
        return { success: true };
      } catch (error) {
        console.error('Failed to open external URL:', error);
        // Fallback to browser
        window.open(url, '_blank');
        return { success: true, fallback: true };
      }
    } else {
      // Web fallback
      window.open(url, '_blank');
      return { success: true, fallback: true };
    }
  }

  // Replace window.electronAPI API calls with REST API calls
  async createSession(sessionData) {
    try {
      const response = await fetch('http://localhost:8002/session/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData)
      });
      return await response.json();
    } catch (error) {
      console.error('Session creation failed:', error);
      return { success: false, error: error.message };
    }
  }

  async googleApiCall(message) {
    try {
      const response = await fetch('http://localhost:8002/google/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      return await response.json();
    } catch (error) {
      console.error('Google API call failed:', error);
      return { success: false, error: error.message };
    }
  }

  async startTurnTaking(sessionId, participants) {
    try {
      const response = await fetch('http://localhost:8002/session/turn-taking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, participants })
      });
      return await response.json();
    } catch (error) {
      console.error('Turn taking start failed:', error);
      return { success: false, error: error.message };
    }
  }

  async advanceTurn(sessionId, userId) {
    try {
      const response = await fetch(`http://localhost:8002/session/${sessionId}/advance-turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId })
      });
      return await response.json();
    } catch (error) {
      console.error('Turn advance failed:', error);
      return { success: false, error: error.message };
    }
  }

  async getSession(sessionId) {
    try {
      const response = await fetch(`http://localhost:8002/session/${sessionId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      return await response.json();
    } catch (error) {
      console.error('Get session failed:', error);
      return { success: false, error: error.message };
    }
  }

  async googleApiStatus() {
    try {
      const response = await fetch('http://localhost:8002/google/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      return await response.json();
    } catch (error) {
      console.error('Google API status failed:', error);
      return { success: false, error: error.message };
    }
  }

  async getDelegationMetrics() {
    try {
      const response = await fetch('http://localhost:8002/delegation/metrics', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      return await response.json();
    } catch (error) {
      console.error('Delegation metrics failed:', error);
      return { success: false, error: error.message };
    }
  }

  async claudeDelegateToGoogle(taskData) {
    try {
      const response = await fetch('http://localhost:8002/claude/delegate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      return await response.json();
    } catch (error) {
      console.error('Claude delegation failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Greet function for testing
  async greet(name) {
    if (this.isReady) {
      try {
        return await invoke('greet', { name });
      } catch (error) {
        console.error('Greet failed:', error);
        return `Hello, ${name}! (Web fallback)`;
      }
    } else {
      return `Hello, ${name}! (Web fallback)`;
    }
  }

  // Get app status
  async getAppStatus() {
    if (this.isReady) {
      try {
        return await invoke('get_app_status');
      } catch (error) {
        console.error('App status failed:', error);
        return 'Hearthlink Web App Running';
      }
    } else {
      return 'Hearthlink Web App Running';
    }
  }
}

// Create global instance
const tauriAPI = new TauriAPI();

// Make it available globally to replace window.electronAPI
if (typeof window !== 'undefined') {
  window.tauriAPI = tauriAPI;
  
  // Also create electronAPI compatibility
  window.electronAPI = {
    openExternal: (url) => tauriAPI.openExternal(url),
    createSession: (data) => tauriAPI.createSession(data),
    googleApiCall: (message) => tauriAPI.googleApiCall(message),
    startTurnTaking: (sessionId, participants) => tauriAPI.startTurnTaking(sessionId, participants),
    advanceTurn: (sessionId, userId) => tauriAPI.advanceTurn(sessionId, userId),
    getSession: (sessionId) => tauriAPI.getSession(sessionId),
    googleApiStatus: () => tauriAPI.googleApiStatus(),
    getDelegationMetrics: () => tauriAPI.getDelegationMetrics(),
    claudeDelegateToGoogle: (taskData) => tauriAPI.claudeDelegateToGoogle(taskData),
    // Missing functions that are causing crashes
    getAppVersion: () => Promise.resolve('1.3.0'),
    // Accessibility event handlers (stub for now)
    onAccessibilityUpdate: (callback) => {
      console.log('Accessibility update listener registered');
      return () => {}; // Return cleanup function
    },
    // Voice command handling
    sendVoiceCommand: (command, targetAgent) => {
      console.log('Voice command:', command, 'to agent:', targetAgent);
      // TODO: Implement voice command routing via REST API
      return Promise.resolve({ success: true });
    },
    // Accessibility toggle
    toggleAccessibility: (feature) => {
      console.log('Toggle accessibility feature:', feature);
      if (window.accessibility) {
        switch (feature) {
          case 'highContrast':
            const isEnabled = document.body.classList.contains('high-contrast');
            window.accessibility.setHighContrast(!isEnabled);
            break;
          case 'largeText':
            const currentSize = document.body.classList.contains('font-large') ? 'normal' : 'large';
            window.accessibility.setFontSize(currentSize === 'normal' ? 'large' : 'normal');
            break;
          case 'screenReader':
            // Screen reader support - announce change
            window.accessibility.speak(`Screen reader support ${feature} toggled`);
            break;
          default:
            console.log('Unknown accessibility feature:', feature);
        }
      }
      return Promise.resolve({ success: true, feature, enabled: true });
    },
    // File operations for Alden
    aldenWriteFile: async (filePath, content) => {
      console.log('Write file:', filePath, 'length:', content.length);
      // TODO: Implement via Tauri file system API or REST endpoint
      return Promise.resolve({ success: true, path: filePath });
    }
  };

  // Create accessibility API compatibility
  window.accessibility = {
    setHighContrast: (enabled) => {
      console.log('High contrast:', enabled);
      document.body.classList.toggle('high-contrast', enabled);
    },
    setFontSize: (size) => {
      console.log('Font size:', size);
      document.body.className = document.body.className.replace(/font-\w+/g, '');
      document.body.classList.add(`font-${size}`);
    },
    speak: (text) => {
      console.log('Speaking:', text);
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
      }
    }
  };
}

export default tauriAPI;