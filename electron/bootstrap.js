const { app } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');

// Configure app paths and cache
function setupAppPaths() {
  app.setPath('userData', path.join(__dirname, '..', 'userData'));
  app.setPath('temp', path.join(__dirname, '..', 'temp'));

  // Ensure directories exist
  const userDataPath = app.getPath('userData');
  const tempPath = app.getPath('temp');
  
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
  }
  
  if (!fs.existsSync(tempPath)) {
    fs.mkdirSync(tempPath, { recursive: true });
  }
}

// Check if React dev server is running
function checkDevServer() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:3005', (res) => {
      resolve(true);
    }).on('error', () => {
      resolve(false);
    });
    
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Main bootstrap function
async function bootstrap() {
  console.log('[BOOTSTRAP] Starting Hearthlink bootstrap...');
  
  try {
    // Setup app paths
    setupAppPaths();
    console.log('[BOOTSTRAP] App paths configured');
    
    // Check development environment
    const isDev = !app.isPackaged;
    const devServerRunning = isDev ? await checkDevServer() : false;
    
    console.log('[BOOTSTRAP] Environment:', { 
      isDev, 
      devServerRunning,
      userDataPath: app.getPath('userData'),
      tempPath: app.getPath('temp')
    });
    
    return {
      isDev,
      devServerRunning,
      userDataPath: app.getPath('userData'),
      tempPath: app.getPath('temp')
    };
    
  } catch (error) {
    console.error('[BOOTSTRAP] Bootstrap failed:', error);
    throw error;
  }
}

module.exports = { 
  bootstrap,
  setupAppPaths,
  checkDevServer
};