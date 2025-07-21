// Version 1.0 - Secure IPC channel definitions
// These channels represent the narrow, versioned APIs exposed to the renderer

const CHANNEL_VERSION = '1.0';

// Define secure IPC channels with version control
const IPC_CHANNELS = {
  version: CHANNEL_VERSION,
  
  // Application lifecycle
  app: {
    getVersion: 'app:getVersion:v1',
    getPath: 'app:getPath:v1',
    getResourcePath: 'app:getResourcePath:v1'
  },
  
  // Documentation access
  docs: {
    read: 'docs:read:v1'
  },
  
  // External interactions
  external: {
    openUrl: 'external:openUrl:v1'
  },
  
  // Voice command system
  voice: {
    sendCommand: 'voice:sendCommand:v1',
    onResponse: 'voice:onResponse:v1'
  },
  
  // Core orchestration
  core: {
    createSession: 'core:createSession:v1',
    getSession: 'core:getSession:v1',
    addParticipant: 'core:addParticipant:v1',
    startTurnTaking: 'core:startTurnTaking:v1',
    advanceTurn: 'core:advanceTurn:v1'
  },
  
  // Vault memory management
  vault: {
    getPersonaMemory: 'vault:getPersonaMemory:v1',
    updatePersonaMemory: 'vault:updatePersonaMemory:v1'
  },
  
  // Synapse plugin system
  synapse: {
    executePlugin: 'synapse:executePlugin:v1',
    listPlugins: 'synapse:listPlugins:v1'
  },
  
  // Accessibility features
  accessibility: {
    toggle: 'accessibility:toggle:v1',
    onUpdate: 'accessibility:onUpdate:v1'
  },
  
  // Menu events
  menu: {
    onNewSession: 'menu:onNewSession:v1',
    onOpenUserGuide: 'menu:onOpenUserGuide:v1',
    onOpenAccessibilityGuide: 'menu:onOpenAccessibilityGuide:v1',
    onOpenTroubleshooting: 'menu:onOpenTroubleshooting:v1'
  }
};

// Channel validation - ensures only known channels are used
function validateChannel(channel) {
  const flatChannels = [];
  
  function flatten(obj, prefix = '') {
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string') {
        flatChannels.push(value);
      } else if (typeof value === 'object' && value !== null) {
        flatten(value, `${prefix}${key}.`);
      }
    }
  }
  
  flatten(IPC_CHANNELS);
  
  if (!flatChannels.includes(channel)) {
    throw new Error(`Unknown IPC channel: ${channel}`);
  }
  
  return channel;
}

module.exports = {
  IPC_CHANNELS,
  CHANNEL_VERSION,
  validateChannel
};