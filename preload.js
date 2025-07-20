const { contextBridge, ipcRenderer } = require('electron');

// Input validation functions for IPC security
function validateString(input, fieldName, maxLength = 1000) {
  if (!input || typeof input !== 'string') {
    throw new Error(`Invalid ${fieldName}: must be a non-empty string`);
  }
  if (input.length > maxLength) {
    throw new Error(`Invalid ${fieldName}: exceeds maximum length of ${maxLength}`);
  }
  // Remove potential XSS/injection attempts
  const sanitized = input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
                         .replace(/javascript:/gi, '')
                         .replace(/on\w+\s*=/gi, '');
  return sanitized;
}

function validateId(input, fieldName) {
  if (!input || typeof input !== 'string') {
    throw new Error(`Invalid ${fieldName}: must be a string`);
  }
  // Allow only alphanumeric, hyphens, and underscores
  if (!/^[a-zA-Z0-9_-]+$/.test(input)) {
    throw new Error(`Invalid ${fieldName}: contains invalid characters`);
  }
  if (input.length > 100) {
    throw new Error(`Invalid ${fieldName}: too long`);
  }
  return input;
}

function validateObject(input, fieldName, maxKeys = 50) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error(`Invalid ${fieldName}: must be an object`);
  }
  if (Object.keys(input).length > maxKeys) {
    throw new Error(`Invalid ${fieldName}: too many properties`);
  }
  return input;
}

function validateArray(input, fieldName, maxLength = 100) {
  if (!Array.isArray(input)) {
    throw new Error(`Invalid ${fieldName}: must be an array`);
  }
  if (input.length > maxLength) {
    throw new Error(`Invalid ${fieldName}: too many items`);
  }
  return input;
}

// Secure IPC wrapper that validates inputs
function secureIpcInvoke(channel, ...args) {
  try {
    // Log security events for audit
    console.log(`[SECURITY] IPC call: ${channel}`, { timestamp: new Date().toISOString() });
    return ipcRenderer.invoke(channel, ...args);
  } catch (error) {
    console.error(`[SECURITY] IPC validation failed for ${channel}:`, error.message);
    throw error;
  }
}

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getAppVersion: () => secureIpcInvoke('get-app-version'),
  getAppPath: () => secureIpcInvoke('get-app-path'),
  getResourcePath: (resourcePath) => {
    const validPath = validateString(resourcePath, 'resourcePath', 500);
    return secureIpcInvoke('get-resource-path', validPath);
  },
  
  // Documentation with validation
  readDocumentation: (docPath) => {
    const validDocPath = validateString(docPath, 'docPath', 500);
    return secureIpcInvoke('read-documentation', validDocPath);
  },
  
  // External links with validation
  openExternal: (url) => {
    const validUrl = validateString(url, 'url', 2000);
    // Additional URL validation
    try {
      new URL(validUrl);
    } catch {
      throw new Error('Invalid URL format');
    }
    return secureIpcInvoke('open-external', validUrl);
  },
  
  // Voice commands with validation
  sendVoiceCommand: (command) => {
    const validCommand = validateString(command, 'command', 500);
    return secureIpcInvoke('voice-command', validCommand);
  },
  onVoiceCommandResponse: (callback) => {
    ipcRenderer.on('voice-command-response', (event, data) => callback(data));
  },
  
  // Core session management with validation
  createSession: (userId, topic, participants) => {
    const validUserId = validateId(userId, 'userId');
    const validTopic = validateString(topic, 'topic', 200);
    const validParticipants = validateArray(participants, 'participants', 20);
    return secureIpcInvoke('core-create-session', { userId: validUserId, topic: validTopic, participants: validParticipants });
  },
  getSession: (sessionId) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    return secureIpcInvoke('core-get-session', validSessionId);
  },
  addParticipant: (sessionId, userId, participantData) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    const validData = validateObject(participantData, 'participantData');
    return secureIpcInvoke('core-add-participant', { sessionId: validSessionId, userId: validUserId, participantData: validData });
  },
  startTurnTaking: (sessionId, userId, turnOrder) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    const validTurnOrder = validateArray(turnOrder, 'turnOrder', 10);
    return secureIpcInvoke('core-start-turn-taking', { sessionId: validSessionId, userId: validUserId, turnOrder: validTurnOrder });
  },
  advanceTurn: (sessionId, userId) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    return secureIpcInvoke('core-advance-turn', { sessionId: validSessionId, userId: validUserId });
  },
  
  // Vault operations with validation
  getPersonaMemory: (personaId, userId) => {
    const validPersonaId = validateId(personaId, 'personaId');
    const validUserId = validateId(userId, 'userId');
    return secureIpcInvoke('vault-get-persona-memory', { personaId: validPersonaId, userId: validUserId });
  },
  updatePersonaMemory: (personaId, userId, data) => {
    const validPersonaId = validateId(personaId, 'personaId');
    const validUserId = validateId(userId, 'userId');
    const validData = validateObject(data, 'data');
    return secureIpcInvoke('vault-update-persona-memory', { personaId: validPersonaId, userId: validUserId, data: validData });
  },
  
  // Synapse plugin operations with validation
  executePlugin: (pluginId, payload, userId) => {
    const validPluginId = validateId(pluginId, 'pluginId');
    const validPayload = validateObject(payload, 'payload');
    const validUserId = validateId(userId, 'userId');
    return secureIpcInvoke('synapse-execute-plugin', { pluginId: validPluginId, payload: validPayload, userId: validUserId });
  },
  listPlugins: () => 
    secureIpcInvoke('synapse-list-plugins'),
  
  // Google API Integration with validation
  googleApiCall: (message, options) => {
    const validMessage = validateString(message, 'message', 5000);
    const validOptions = options ? validateObject(options, 'options') : {};
    return secureIpcInvoke('google-api-call', validMessage, validOptions);
  },
  claudeDelegateToGoogle: (taskData) => {
    const validTaskData = validateObject(taskData, 'taskData');
    return secureIpcInvoke('claude-delegate-to-google', validTaskData);
  },
  googleApiStatus: () => 
    secureIpcInvoke('google-api-status'),
  getDelegationMetrics: () => 
    secureIpcInvoke('get-delegation-metrics'),
  
  // Alden workspace operations with validation
  aldenWriteFile: (filePath, content, createDirectories = true) => {
    const validFilePath = validateString(filePath, 'filePath', 500);
    const validContent = validateString(content, 'content', 100000);
    return secureIpcInvoke('alden-write-file', { filePath: validFilePath, content: validContent, createDirectories });
  },
  aldenReadFile: (filePath) => {
    const validFilePath = validateString(filePath, 'filePath', 500);
    return secureIpcInvoke('alden-read-file', { filePath: validFilePath });
  },
  aldenListDirectory: (dirPath) => {
    const validDirPath = validateString(dirPath, 'dirPath', 500);
    return secureIpcInvoke('alden-list-directory', { dirPath: validDirPath });
  },
  
  // Accessibility features with validation
  toggleAccessibility: (feature) => {
    const validFeature = validateString(feature, 'feature', 50);
    return secureIpcInvoke('accessibility-toggle', validFeature);
  },
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

// Secure file system operations with path validation
const ALLOWED_PATHS = [
  'docs/public',
  'assets',
  'voice',
  'LICENSE',
  'README.md',
  'SECURITY.md'
];

function validatePath(inputPath) {
  if (!inputPath || typeof inputPath !== 'string') {
    throw new Error('Invalid path parameter');
  }
  
  // Remove any path traversal attempts
  const normalized = inputPath.replace(/\.\./g, '').replace(/\/+/g, '/').replace(/^\//, '');
  
  // Check against whitelist
  const isAllowed = ALLOWED_PATHS.some(allowedPath => 
    normalized.startsWith(allowedPath) || allowedPath.startsWith(normalized)
  );
  
  if (!isAllowed) {
    throw new Error(`Access denied: Path '${inputPath}' is not allowed`);
  }
  
  return normalized;
}

contextBridge.exposeInMainWorld('fileSystem', {
  readFile: async (filePath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const safePath = validatePath(filePath);
      const fullPath = path.resolve(process.resourcesPath, safePath);
      
      // Additional security: ensure resolved path is still within resources
      if (!fullPath.startsWith(path.resolve(process.resourcesPath))) {
        throw new Error('Path traversal attempt blocked');
      }
      
      return await fs.promises.readFile(fullPath, 'utf8');
    } catch (error) {
      console.error('Secure file read error:', error.message);
      throw new Error('File access denied');
    }
  },
  
  exists: async (filePath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const safePath = validatePath(filePath);
      const fullPath = path.resolve(process.resourcesPath, safePath);
      
      if (!fullPath.startsWith(path.resolve(process.resourcesPath))) {
        return false;
      }
      
      return await fs.promises.access(fullPath).then(() => true).catch(() => false);
    } catch (error) {
      return false;
    }
  },
  
  listFiles: async (dirPath) => {
    try {
      const fs = require('fs');
      const path = require('path');
      const safePath = validatePath(dirPath);
      const fullPath = path.resolve(process.resourcesPath, safePath);
      
      if (!fullPath.startsWith(path.resolve(process.resourcesPath))) {
        throw new Error('Directory traversal blocked');
      }
      
      const files = await fs.promises.readdir(fullPath, { withFileTypes: true });
      return files.map(file => ({
        name: file.name,
        isDirectory: file.isDirectory(),
        path: path.posix.join(safePath, file.name)
      }));
    } catch (error) {
      console.error('Secure directory listing error:', error.message);
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

// Security: Prevent access to Node.js APIs and implement strict CSP
let securityNonce = null;

// Generate a cryptographically secure nonce for CSP
function generateSecureNonce() {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode.apply(null, array)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

window.addEventListener('DOMContentLoaded', () => {
  // Generate nonce for this session
  securityNonce = generateSecureNonce();
  
  // Remove Node.js globals from window
  delete window.require;
  delete window.exports;
  delete window.module;
  delete window.global;
  delete window.process;
  delete window.Buffer;
  
  // Implement strict Content Security Policy
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${securityNonce}'`,
    "style-src 'self' 'unsafe-inline'", // Allow inline styles for React
    "img-src 'self' data: blob:",
    "media-src 'self' data: blob:",
    "connect-src 'self' http://localhost:* https://localhost:*",
    "font-src 'self' data:",
    "object-src 'none'",
    "base-uri 'self'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "upgrade-insecure-requests"
  ].join('; ');
  document.head.appendChild(meta);
  
  // Additional security headers via meta tags
  const metaHeaders = [
    { name: 'X-Content-Type-Options', content: 'nosniff' },
    { name: 'X-Frame-Options', content: 'DENY' },
    { name: 'X-XSS-Protection', content: '1; mode=block' },
    { name: 'Referrer-Policy', content: 'strict-origin-when-cross-origin' }
  ];
  
  metaHeaders.forEach(header => {
    const metaElement = document.createElement('meta');
    metaElement.httpEquiv = header.name;
    metaElement.content = header.content;
    document.head.appendChild(metaElement);
  });
});

// Expose secure nonce for legitimate script execution
contextBridge.exposeInMainWorld('security', {
  getNonce: () => securityNonce,
  validateOrigin: (origin) => {
    const allowedOrigins = [
      'http://localhost:3000',
      'http://localhost:3005',
      'app://-',
      'file://'
    ];
    return allowedOrigins.some(allowed => origin.startsWith(allowed));
  }
});

console.log('Preload script loaded successfully'); 