export {}
const { ipcMain } = require('electron');

// Import Python bridge when available
let sendToPython;
try {
  sendToPython = require('../services/pythonBridge').sendToPython;
} catch (error) {
  console.warn('Python bridge not available, using mock responses');
  sendToPython = async (command) => ({ 
    success: false, 
    error: 'Python backend not connected' 
  });
}

function setupVaultHandlers() {
  ipcMain.handle('vault-get-persona-memory', async (event, { personaId, userId }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'vault_get_persona_memory',
        payload: { personaId, userId }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Vault get persona memory error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('vault-update-persona-memory', async (event, { personaId, userId, data }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'vault_update_persona_memory',
        payload: { personaId, userId, data }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Vault update persona memory error:', error);
      return { success: false, error: error.message };
    }
  });
}

module.exports = {
  setupVaultHandlers
};export {}
