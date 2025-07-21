const { ipcMain, app, shell } = require('electron');
const path = require('path');
const fs = require('fs').promises;

function setupGeneralHandlers() {
  ipcMain.handle('get-app-version', () => {
    return app.getVersion();
  });

  ipcMain.handle('get-app-path', () => {
    return app.getAppPath();
  });

  ipcMain.handle('get-resource-path', (event, resourcePath) => {
    return path.join(__dirname, '..', resourcePath);
  });

  ipcMain.handle('read-documentation', async (event, docPath) => {
    try {
      const fullPath = path.join(__dirname, '..', 'docs', docPath);
      const content = await fs.readFile(fullPath, 'utf8');
      return { success: true, content };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('open-external', (event, url) => {
    try {
      shell.openExternal(url);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('voice-command', async (event, command) => {
    try {
      console.log('Voice command received:', command);
      
      // Mock voice command processing
      // In a real implementation, this would route to the voice processing service
      const response = {
        success: true,
        action: 'processed',
        response: `Processed voice command: ${command}`
      };
      
      // Send response back to renderer
      const { getMainWindow } = require('../electron/window');
      const mainWindow = getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send('voice-command-response', {
          command,
          response,
          timestamp: Date.now()
        });
      }
      
      return response;
    } catch (error) {
      console.error('Voice command error:', error);
      const { getMainWindow } = require('../electron/window');
      const mainWindow = getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send('voice-command-response', {
          command,
          error: error.message,
          timestamp: Date.now()
        });
      }
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('accessibility-toggle', (event, feature) => {
    try {
      console.log(`Accessibility feature toggled: ${feature}`);
      // In a real implementation, this would toggle accessibility features
      return { success: true, feature, enabled: true };
    } catch (error) {
      console.error('Accessibility toggle error:', error);
      return { success: false, error: error.message };
    }
  });
}

module.exports = {
  setupGeneralHandlers
};