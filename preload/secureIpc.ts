export {}
const { contextBridge, ipcRenderer } = require('electron');
const { IPC_CHANNELS, validateChannel } = require('./channels');
const { 
  validateString, 
  validateId, 
  validateObject, 
  validateArray, 
  validateUrl, 
  validatePath, 
  checkRateLimit 
} = require('./validation');

// Audit logging for security monitoring
function auditLog(operation, channel, success, error = null) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    operation,
    channel,
    success,
    error: error?.message,
    userAgent: navigator.userAgent,
    origin: window.location.origin
  };
  
  console.log('[SECURITY AUDIT]', logEntry);
  
  // In production, you might want to send this to a logging service
  if (!success && error) {
    console.error('[SECURITY VIOLATION]', error.message);
  }
}

// Secure IPC wrapper that validates inputs and channels
function secureIpcInvoke(channel, ...args) {
  try {
    // Validate channel exists in whitelist
    validateChannel(channel);
    
    // Rate limiting
    checkRateLimit(channel, 60, 60000);
    
    auditLog('ipc_invoke', channel, true);
    return ipcRenderer.invoke(channel, ...args);
  } catch (error) {
    auditLog('ipc_invoke', channel, false, error);
    throw error;
  }
}

// Secure IPC listener wrapper
function secureIpcOn(channel, callback) {
  try {
    validateChannel(channel);
    auditLog('ipc_listen', channel, true);
    
    return ipcRenderer.on(channel, (event, data) => {
      try {
        callback(data);
      } catch (error) {
        auditLog('ipc_callback', channel, false, error);
        console.error(`Callback error for channel ${channel}:`, error);
      }
    });
  } catch (error) {
    auditLog('ipc_listen', channel, false, error);
    throw error;
  }
}

// Main API exposed to renderer process
const electronAPI = {
  // Application information
  getAppVersion: () => 
    secureIpcInvoke(IPC_CHANNELS.app.getVersion),
  
  getAppPath: () => 
    secureIpcInvoke(IPC_CHANNELS.app.getPath),
  
  getResourcePath: (resourcePath) => {
    const validPath = validatePath(resourcePath, 'resourcePath');
    return secureIpcInvoke(IPC_CHANNELS.app.getResourcePath, validPath);
  },
  
  // Documentation with validation
  readDocumentation: (docPath) => {
    const validDocPath = validatePath(docPath, 'docPath');
    return secureIpcInvoke(IPC_CHANNELS.docs.read, validDocPath);
  },
  
  // External links with validation
  openExternal: (url) => {
    const validUrl = validateUrl(url, 'url');
    return secureIpcInvoke(IPC_CHANNELS.external.openUrl, validUrl);
  },
  
  // Voice commands with validation
  sendVoiceCommand: (command) => {
    const validCommand = validateString(command, 'command', 500);
    return secureIpcInvoke(IPC_CHANNELS.voice.sendCommand, validCommand);
  },
  
  onVoiceCommandResponse: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.voice.onResponse, callback);
  },
  
  // Core session management with validation
  createSession: (userId, topic, participants) => {
    const validUserId = validateId(userId, 'userId');
    const validTopic = validateString(topic, 'topic', 200);
    const validParticipants = validateArray(participants, 'participants', 20);
    
    return secureIpcInvoke(IPC_CHANNELS.core.createSession, {
      userId: validUserId,
      topic: validTopic,
      participants: validParticipants
    });
  },
  
  getSession: (sessionId) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    return secureIpcInvoke(IPC_CHANNELS.core.getSession, validSessionId);
  },
  
  addParticipant: (sessionId, userId, participantData) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    const validData = validateObject(participantData, 'participantData');
    
    return secureIpcInvoke(IPC_CHANNELS.core.addParticipant, {
      sessionId: validSessionId,
      userId: validUserId,
      participantData: validData
    });
  },
  
  startTurnTaking: (sessionId, userId, turnOrder) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    const validTurnOrder = validateArray(turnOrder, 'turnOrder', 10);
    
    return secureIpcInvoke(IPC_CHANNELS.core.startTurnTaking, {
      sessionId: validSessionId,
      userId: validUserId,
      turnOrder: validTurnOrder
    });
  },
  
  advanceTurn: (sessionId, userId) => {
    const validSessionId = validateId(sessionId, 'sessionId');
    const validUserId = validateId(userId, 'userId');
    
    return secureIpcInvoke(IPC_CHANNELS.core.advanceTurn, {
      sessionId: validSessionId,
      userId: validUserId
    });
  },
  
  // Vault operations with validation
  getPersonaMemory: (personaId, userId) => {
    const validPersonaId = validateId(personaId, 'personaId');
    const validUserId = validateId(userId, 'userId');
    
    return secureIpcInvoke(IPC_CHANNELS.vault.getPersonaMemory, {
      personaId: validPersonaId,
      userId: validUserId
    });
  },
  
  updatePersonaMemory: (personaId, userId, data) => {
    const validPersonaId = validateId(personaId, 'personaId');
    const validUserId = validateId(userId, 'userId');
    const validData = validateObject(data, 'data');
    
    return secureIpcInvoke(IPC_CHANNELS.vault.updatePersonaMemory, {
      personaId: validPersonaId,
      userId: validUserId,
      data: validData
    });
  },
  
  // Synapse plugin operations with validation
  executePlugin: (pluginId, payload, userId) => {
    const validPluginId = validateId(pluginId, 'pluginId');
    const validPayload = validateObject(payload, 'payload');
    const validUserId = validateId(userId, 'userId');
    
    return secureIpcInvoke(IPC_CHANNELS.synapse.executePlugin, {
      pluginId: validPluginId,
      payload: validPayload,
      userId: validUserId
    });
  },
  
  listPlugins: () => 
    secureIpcInvoke(IPC_CHANNELS.synapse.listPlugins),
  
  // Accessibility features with validation
  toggleAccessibility: (feature) => {
    const validFeature = validateString(feature, 'feature', 50);
    return secureIpcInvoke(IPC_CHANNELS.accessibility.toggle, validFeature);
  },
  
  onAccessibilityUpdate: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.accessibility.onUpdate, callback);
  },
  
  // Menu event listeners
  onNewSession: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.menu.onNewSession, callback);
  },
  
  onOpenUserGuide: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.menu.onOpenUserGuide, callback);
  },
  
  onOpenAccessibilityGuide: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.menu.onOpenAccessibilityGuide, callback);
  },
  
  onOpenTroubleshooting: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    return secureIpcOn(IPC_CHANNELS.menu.onOpenTroubleshooting, callback);
  },
  
  // Cleanup function
  removeAllListeners: (channel) => {
    try {
      validateChannel(channel);
      ipcRenderer.removeAllListeners(channel);
      auditLog('ipc_cleanup', channel, true);
    } catch (error) {
      auditLog('ipc_cleanup', channel, false, error);
      throw error;
    }
  }
};

module.exports = {
  electronAPI,
  secureIpcInvoke,
  secureIpcOn
};export {}
