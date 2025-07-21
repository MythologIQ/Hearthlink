const { contextBridge } = require('electron');
const { electronAPI } = require('./preload/secureIpc');

// Generate a cryptographically secure nonce for CSP
function generateSecureNonce() {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode.apply(null, array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

let securityNonce = null;

// Expose the secure electron API
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Expose minimal process information for environment detection
contextBridge.exposeInMainWorld('process', {
  env: {
    NODE_ENV: process.env.NODE_ENV,
    ELECTRON_IS_DEV: process.env.NODE_ENV === 'development'
  },
  platform: process.platform,
  arch: process.arch
});

// Expose accessibility utilities
contextBridge.exposeInMainWorld('accessibility', {
  // Screen reader support
  speak: (text, options = {}) => {
    if (window.speechSynthesis && typeof text === 'string' && text.length < 1000) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = Math.max(0.1, Math.min(2, options.rate || 1));
      utterance.pitch = Math.max(0, Math.min(2, options.pitch || 1));
      utterance.volume = Math.max(0, Math.min(1, options.volume || 1));
      window.speechSynthesis.speak(utterance);
    }
  },
  
  // High contrast mode
  setHighContrast: (enabled) => {
    if (typeof enabled === 'boolean') {
      document.documentElement.classList.toggle('high-contrast', enabled);
    }
  },
  
  // Font size adjustment
  setFontSize: (size) => {
    if (typeof size === 'string' && /^\\d+(\\.\\d+)?(px|em|rem|%)$/.test(size)) {
      document.documentElement.style.fontSize = size;
    }
  },
  
  // Focus management
  focusElement: (selector) => {
    if (typeof selector === 'string' && selector.length < 100) {
      try {
        const element = document.querySelector(selector);
        if (element && element.focus) {
          element.focus();
        }
      } catch (error) {
        console.warn('Invalid selector for focus:', selector);
      }
    }
  },
  
  // Keyboard navigation setup
  setupKeyboardNavigation: () => {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
      }
    });
    
    document.addEventListener('mousedown', () => {
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
      recognition.maxAlternatives = 1;
      
      return recognition;
    }
    return null;
  },
  
  // Process voice commands with enhanced security
  processCommand: (command) => {
    if (typeof command !== 'string' || command.length > 500) {
      return false;
    }
    
    const normalizedCommand = command.toLowerCase().trim();
    
    // Define safe command patterns
    const commandPatterns = [
      { pattern: 'new session', action: 'newSession' },
      { pattern: 'open user guide', action: 'userGuide' },
      { pattern: 'help', action: 'userGuide' },
      { pattern: 'accessibility', action: 'accessibility' },
      { pattern: 'troubleshooting', action: 'troubleshooting' }
    ];
    
    // Execute matching command
    for (const { pattern, action } of commandPatterns) {
      if (normalizedCommand.includes(pattern)) {
        // Emit custom event instead of direct execution
        window.dispatchEvent(new CustomEvent('voiceCommand', { 
          detail: { action, command: normalizedCommand } 
        }));
        return true;
      }
    }
    
    return false;
  }
});

// Expose notification utilities
contextBridge.exposeInMainWorld('notifications', {
  show: (title, body, options = {}) => {
    if (typeof title !== 'string' || typeof body !== 'string') {
      return null;
    }
    
    if (title.length > 100 || body.length > 500) {
      return null;
    }
    
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(title, {
        body,
        icon: '/assets/icon.ico',
        tag: 'hearthlink',
        ...options
      });
      
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
      
      // Auto-close after 5 seconds
      setTimeout(() => notification.close(), 5000);
      
      return notification;
    }
    return null;
  },
  
  requestPermission: async () => {
    if ('Notification' in window) {
      return await Notification.requestPermission();
    }
    return 'denied';
  }
});

// Expose security utilities
contextBridge.exposeInMainWorld('security', {
  getNonce: () => securityNonce,
  validateOrigin: (origin) => {
    if (typeof origin !== 'string') return false;
    
    const allowedOrigins = [
      'http://localhost:3000',
      'http://localhost:3005',
      'http://127.0.0.1:3000',
      'http://127.0.0.1:3005',
      'app://-'
    ];
    
    return allowedOrigins.some(allowed => origin.startsWith(allowed));
  },
  
  getChannelVersion: () => require('./preload/channels').CHANNEL_VERSION
});

// DOM Content Loaded handler for security setup
window.addEventListener('DOMContentLoaded', () => {
  // Generate nonce for this session
  securityNonce = generateSecureNonce();
  
  // Remove potentially dangerous globals
  delete window.require;
  delete window.exports;
  delete window.module;
  delete window.global;
  delete window.Buffer;
  
  // Setup Content Security Policy
  const cspMeta = document.createElement('meta');
  cspMeta.httpEquiv = 'Content-Security-Policy';
  cspMeta.content = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${securityNonce}' 'unsafe-eval'`, // unsafe-eval needed for React dev
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "media-src 'self' data: blob:",
    "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*",
    "font-src 'self' data:",
    "object-src 'none'",
    "base-uri 'self'",
    "frame-ancestors 'none'",
    "form-action 'self'"
  ].join('; ');
  
  document.head.appendChild(cspMeta);
  
  // Additional security headers
  const securityHeaders = [
    { name: 'X-Content-Type-Options', content: 'nosniff' },
    { name: 'X-Frame-Options', content: 'DENY' },
    { name: 'X-XSS-Protection', content: '1; mode=block' },
    { name: 'Referrer-Policy', content: 'strict-origin-when-cross-origin' }
  ];
  
  securityHeaders.forEach(({ name, content }) => {
    const meta = document.createElement('meta');
    meta.httpEquiv = name;
    meta.content = content;
    document.head.appendChild(meta);
  });
  
  console.log('✅ Secure preload script loaded - Channel version:', require('./preload/channels').CHANNEL_VERSION);
});

// Error handling for unhandled rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // In production, you might want to report this to a logging service
});

window.addEventListener('error', (event) => {
  console.error('Uncaught error:', event.error);
  // In production, you might want to report this to a logging service
});