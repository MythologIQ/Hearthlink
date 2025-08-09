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

function setupSynapseHandlers() {
  ipcMain.handle('synapse-execute-plugin', async (event, { pluginId, payload, userId }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'synapse_execute_plugin',
        payload: { pluginId, payload, userId }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Synapse execute plugin error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('synapse-list-plugins', async (event) => {
    try {
      const command = {
        id: Date.now(),
        type: 'synapse_list_plugins',
        payload: {}
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Synapse list plugins error:', error);
      return { success: false, error: error.message };
    }
  });
}

module.exports = {
  setupSynapseHandlers
};export {}
