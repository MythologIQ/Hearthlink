const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  getResourcePath: (resourcePath) => ipcRenderer.invoke('get-resource-path', resourcePath),
  
  // Documentation
  readDocumentation: (docPath) => ipcRenderer.invoke('read-documentation', docPath),
  
  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // Voice commands
  sendVoiceCommand: (command) => ipcRenderer.invoke('voice-command', command),
  onVoiceCommandResponse: (callback) => {
    ipcRenderer.on('voice-command-response', (event, data) => callback(data));
  },
  
  // Accessibility features
  toggleAccessibility: (feature) => ipcRenderer.invoke('accessibility-toggle', feature),
  onAccessibilityUpdate: (callback) => {
    ipcRenderer.on('accessibility-update', (event, data) => callback(data));
  },
  
  // Menu actions
  onNewSession: (callback) => {
    ipcRenderer.on('new-session', () => callback());
  },
  onOpenUserGuide: (callback) => {
    ipcRenderer.on('open-user-guide', () => callback());
  },
  onOpenAccessibilityGuide: (callback) => {
    ipcRenderer.on('open-accessibility-guide', () => callback());
  },
  onOpenTroubleshooting: (callback) => {
    ipcRenderer.on('open-troubleshooting', () => callback());
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Expose a minimal process API for environment detection
contextBridge.exposeInMainWorld('process', {
  env: {
    NODE_ENV: process.env.NODE_ENV,
    ELECTRON_IS_DEV: process.env.NODE_ENV === 'development'
  },
  platform: process.platform,
  arch: process.arch
});

// Expose file system operations for documentation
contextBridge.exposeInMainWorld('fileSystem', {
  readFile: async (filePath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const fullPath = path.join(process.resourcesPath, filePath);
      return await fs.promises.readFile(fullPath, 'utf8');
    } catch (error) {
      console.error('Error reading file:', error);
      throw error;
    }
  },
  
  exists: async (filePath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const fullPath = path.join(process.resourcesPath, filePath);
      return await fs.promises.access(fullPath).then(() => true).catch(() => false);
    } catch (error) {
      return false;
    }
  },
  
  listFiles: async (dirPath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const fullPath = path.join(process.resourcesPath, dirPath);
      const files = await fs.promises.readdir(fullPath, { withFileTypes: true });
      return files.map(file => ({
        name: file.name,
        isDirectory: file.isDirectory(),
        path: path.join(dirPath, file.name)
      }));
    } catch (error) {
      console.error('Error listing files:', error);
      return [];
    }
  }
});

// Expose accessibility utilities
contextBridge.exposeInMainWorld('accessibility', {
  // Screen reader support
  speak: (text, options = {}) => {
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = options.rate || 1;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      window.speechSynthesis.speak(utterance);
    }
  },
  
  // High contrast mode
  setHighContrast: (enabled) => {
    document.documentElement.classList.toggle('high-contrast', enabled);
  },
  
  // Font size adjustment
  setFontSize: (size) => {
    document.documentElement.style.fontSize = size;
  },
  
  // Focus management
  focusElement: (selector) => {
    const element = document.querySelector(selector);
    if (element) {
      element.focus();
    }
  },
  
  // Keyboard navigation
  setupKeyboardNavigation: () => {
    document.addEventListener('keydown', (event) => {
      // Tab navigation
      if (event.key === 'Tab') {
        // Ensure focus is visible
        document.body.classList.add('keyboard-navigation');
      }
    });
    
    document.addEventListener('mousedown', () => {
      // Remove keyboard navigation class when using mouse
      document.body.classList.remove('keyboard-navigation');
    });
  }
});

// Expose voice command utilities
contextBridge.exposeInMainWorld('voiceCommands', {
  // Initialize speech recognition
  initSpeechRecognition: () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      return recognition;
    }
    return null;
  },
  
  // Process voice commands
  processCommand: (command) => {
    const normalizedCommand = command.toLowerCase().trim();
    
    // Define command patterns
    const commands = {
      'new session': () => window.electronAPI.onNewSession(() => window.location.reload()),
      'open user guide': () => window.electronAPI.onOpenUserGuide(() => window.open('/docs/public/USER_GUIDE.md')),
      'help': () => window.electronAPI.onOpenUserGuide(() => window.open('/docs/public/USER_GUIDE.md')),
      'accessibility': () => window.electronAPI.onOpenAccessibilityGuide(() => window.open('/docs/public/ACCESSIBILITY.md')),
      'troubleshooting': () => window.electronAPI.onOpenTroubleshooting(() => window.open('/docs/public/TROUBLESHOOTING.md')),
      'exit': () => window.close(),
      'quit': () => window.close(),
      'close': () => window.close()
    };
    
    // Execute matching command
    for (const [pattern, action] of Object.entries(commands)) {
      if (normalizedCommand.includes(pattern)) {
        action();
        return true;
      }
    }
    
    return false;
  }
});

// Expose notification utilities
contextBridge.exposeInMainWorld('notifications', {
  show: (title, body, options = {}) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(title, {
        body,
        icon: '/assets/icon.ico',
        ...options
      });
      
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
      
      return notification;
    }
  },
  
  requestPermission: async () => {
    if ('Notification' in window) {
      return await Notification.requestPermission();
    }
    return 'denied';
  }
});

// Security: Prevent access to Node.js APIs
window.addEventListener('DOMContentLoaded', () => {
  // Remove Node.js globals from window
  delete window.require;
  delete window.exports;
  delete window.module;
  delete window.global;
  delete window.process;
  delete window.Buffer;
  
  // Set up security headers
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; img-src 'self' data: blob:; media-src 'self' data: blob:;";
  document.head.appendChild(meta);
});

console.log('Preload script loaded successfully'); 