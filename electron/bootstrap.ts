import { app } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import * as http from 'http';

interface BootstrapConfig {
  isDev: boolean;
  userDataPath: string;
  tempPath: string;
}

// Configure app paths and cache
function setupAppPaths(): void {
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

// Check if development server is running
function checkDevServer(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:3005', (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Bootstrap application setup
async function bootstrap(): Promise<BootstrapConfig> {
  setupAppPaths();
  
  // Check if we're in development mode
  const isDev = !app.isPackaged || process.env.NODE_ENV === 'development';
  
  if (isDev) {
    const devServerRunning = await checkDevServer();
    console.log(`Development mode: ${isDev}, Dev server: ${devServerRunning}`);
  }
  
  return {
    isDev,
    userDataPath: app.getPath('userData'),
    tempPath: app.getPath('temp')
  };
}

export {
  bootstrap,
  setupAppPaths,
  checkDevServer,
  type BootstrapConfig
};