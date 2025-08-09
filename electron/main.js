const { app, Menu } = require('electron');
const { bootstrap } = require('./bootstrap.js');
const { setupProtocolHandler } = require('../services/protocolHandler');
const { createWindow } = require('./window');
const { startPythonBackend, stopPythonBackend } = require('../services/pythonBridge');

// Import IPC handlers
const { setupGeneralHandlers } = require('../ipcHandlers/general');
const { setupCoreHandlers } = require('../ipcHandlers/core');
const { setupVaultHandlers } = require('../ipcHandlers/vault');
const { setupSynapseHandlers } = require('../ipcHandlers/synapse');

// Add fetch polyfill if needed
if (!global.fetch) {
  global.fetch = require('node-fetch');
}

// Setup menu
function setupMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Setup IPC handlers
function setupIpcHandlers() {
  setupGeneralHandlers();
  setupCoreHandlers();
  setupVaultHandlers();
  setupSynapseHandlers();
}

// App event handlers
app.whenReady().then(async () => {
  try {
    console.log('🚀 Hearthlink starting...');
    
    // Bootstrap application
    const config = await bootstrap();
    console.log('✅ Bootstrap complete');
    
    // Setup protocol handler for static assets
    setupProtocolHandler();
    console.log('✅ Protocol handler registered');
    
    // Setup menu
    setupMenu();
    console.log('✅ Menu setup complete');
    
    // Setup IPC handlers
    setupIpcHandlers();
    console.log('✅ IPC handlers registered');
    
    // Start Python backend
    try {
      await startPythonBackend();
      console.log('✅ Python backend started');
    } catch (error) {
      console.warn('⚠️ Python backend failed to start:', error.message);
    }
    
    // Create main window
    await createWindow();
    console.log('✅ Main window created');
    
    console.log('🎉 Hearthlink ready!');
    
  } catch (error) {
    console.error('💥 Failed to start Hearthlink:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', async () => {
  const { getMainWindow } = require('./window');
  if (!getMainWindow()) {
    await createWindow();
  }
});

app.on('before-quit', () => {
  stopPythonBackend();
});

// Handle app protocol for static file serving
app.setAsDefaultProtocolClient('app');

module.exports = app;