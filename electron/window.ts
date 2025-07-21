const { BrowserWindow } = require('electron');
const path = require('path');
const http = require('http');
const { startStaticServer } = require('../services/staticServer');

let mainWindow;

async function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, '..', 'src', 'assets', 'Hearthlink.png'),
    title: 'Hearthlink - AI Orchestration Hub',
    resizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '..', 'preload.js'),
      webSecurity: true,
      allowRunningInsecureContent: false
    },
    show: false, // Don't show until ready
    titleBarStyle: 'default',
    autoHideMenuBar: false
  });

  // Load the app with proper asset handling
  const startUrl = await determineStartUrl();
  
  try {
    await mainWindow.loadURL(startUrl);
    console.log(`✅ Application loaded from: ${startUrl}`);
  } catch (error) {
    console.error('Failed to load application:', error);
    throw error;
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  return mainWindow;
}

async function determineStartUrl() {
  // Try development server first, fallback to static server
  let startUrl = 'http://127.0.0.1:3005';
  
  // Check if dev server is running with retry logic
  let devServerReady = false;
  for (let attempt = 1; attempt <= 10; attempt++) {
    try {
      const response = await new Promise((resolve, reject) => {
        const req = http.get('http://127.0.0.1:3005', (res) => {
          resolve(res);
        });
        req.on('error', reject);
        req.setTimeout(3000, () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });
      });
      
      if (response.statusCode === 200) {
        devServerReady = true;
        console.log(`✅ React dev server detected on port 3005`);
        break;
      }
    } catch (error) {
      if (attempt === 10) {
        console.log(`❌ React dev server not found after ${attempt} attempts`);
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  // Fallback to static server if dev server not available
  if (!devServerReady) {
    try {
      const staticPort = await startStaticServer();
      startUrl = `http://127.0.0.1:${staticPort}`;
      console.log(`✅ Using static server on port ${staticPort}`);
    } catch (error) {
      console.error('Failed to start static server:', error);
      // Final fallback to protocol handler
      startUrl = 'app://./index.html';
      console.log('✅ Using app:// protocol handler');
    }
  }
  
  return startUrl;
}

function getMainWindow() {
  return mainWindow;
}

module.exports = {
  createWindow,
  getMainWindow
};