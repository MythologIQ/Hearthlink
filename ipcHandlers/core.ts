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

function setupCoreHandlers() {
  ipcMain.handle('core-create-session', async (event, { userId, topic, participants }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'core_create_session',
        payload: { userId, topic, participants }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Core create session error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('core-get-session', async (event, sessionId) => {
    try {
      const command = {
        id: Date.now(),
        type: 'core_get_session',
        payload: { sessionId }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Core get session error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('core-add-participant', async (event, { sessionId, userId, participantData }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'core_add_participant',
        payload: { sessionId, userId, participantData }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Core add participant error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('core-start-turn-taking', async (event, { sessionId, userId, turnOrder }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'core_start_turn_taking',
        payload: { sessionId, userId, turnOrder }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Core start turn taking error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('core-advance-turn', async (event, { sessionId, userId }) => {
    try {
      const command = {
        id: Date.now(),
        type: 'core_advance_turn',
        payload: { sessionId, userId }
      };
      
      const response = await sendToPython(command);
      return response;
    } catch (error) {
      console.error('Core advance turn error:', error);
      return { success: false, error: error.message };
    }
  });
}

module.exports = {
  setupCoreHandlers
};export {}
