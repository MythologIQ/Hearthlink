const { app, BrowserWindow, Menu, shell, ipcMain, dialog, protocol } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const url = require('url');

// Add fetch if not available (Node.js versions < 18)
if (!global.fetch) {
  global.fetch = require('node-fetch');
}

// Configure app paths and cache
app.setPath('userData', path.join(__dirname, 'userData'));
app.setPath('temp', path.join(__dirname, 'temp'));

// Ensure directories exist
const userDataPath = app.getPath('userData');
const tempPath = app.getPath('temp');

if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
}
if (!fs.existsSync(tempPath)) {
    fs.mkdirSync(tempPath, { recursive: true });
}

// Keep a global reference of the window object
let mainWindow;
let staticServer = null;

// ========================================
// STATIC ASSET SERVING CONFIGURATION
// ========================================

// Protocol handler for serving static files
function setupProtocolHandler() {
  protocol.registerFileProtocol('app', (request, callback) => {
    try {
      const url = request.url.substr(6); // Remove 'app://' prefix
      const filePath = path.normalize(path.join(__dirname, 'build', url));
      
      // Security: Ensure the file is within the build directory
      const buildPath = path.resolve(path.join(__dirname, 'build'));
      const resolvedPath = path.resolve(filePath);
      
      if (!resolvedPath.startsWith(buildPath)) {
        console.error('Security violation: Attempted to access file outside build directory:', filePath);
        callback({ error: 403 });
        return;
      }
      
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        console.error('File not found:', filePath);
        callback({ error: 404 });
        return;
      }
      
      callback({ path: filePath });
    } catch (error) {
      console.error('Protocol handler error:', error);
      callback({ error: 500 });
    }
  });
}

// Lightweight static server as fallback
function startStaticServer() {
  return new Promise((resolve, reject) => {
    const buildPath = path.join(__dirname, 'build');
    const port = 3008; // Use different port than dev server (3001 has permission issues)
    
    staticServer = http.createServer((req, res) => {
      try {
        const parsedUrl = url.parse(req.url);
        let filePath = path.join(buildPath, parsedUrl.pathname);
        
        // Security: Ensure the file is within the build directory
        const resolvedPath = path.resolve(filePath);
        const resolvedBuildPath = path.resolve(buildPath);
        
        if (!resolvedPath.startsWith(resolvedBuildPath)) {
          res.writeHead(403, { 'Content-Type': 'text/plain' });
          res.end('Forbidden');
          return;
        }
        
        // Handle directory requests
        if (fs.statSync(filePath).isDirectory()) {
          filePath = path.join(filePath, 'index.html');
        }
        
        // Check if file exists
        if (!fs.existsSync(filePath)) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('File not found');
          return;
        }
        
        // Set appropriate content type
        const ext = path.extname(filePath).toLowerCase();
        const contentTypes = {
          '.html': 'text/html',
          '.css': 'text/css',
          '.js': 'application/javascript',
          '.json': 'application/json',
          '.png': 'image/png',
          '.jpg': 'image/jpeg',
          '.jpeg': 'image/jpeg',
          '.gif': 'image/gif',
          '.svg': 'image/svg+xml',
          '.ico': 'image/x-icon',
          '.woff': 'font/woff',
          '.woff2': 'font/woff2',
          '.ttf': 'font/ttf',
          '.eot': 'application/vnd.ms-fontobject'
        };
        
        const contentType = contentTypes[ext] || 'application/octet-stream';
        res.setHeader('Content-Type', contentType);
        
        // Stream the file
        const stream = fs.createReadStream(filePath);
        stream.pipe(res);
        
        stream.on('error', (error) => {
          console.error('Static server error:', error);
          res.writeHead(500, { 'Content-Type': 'text/plain' });
          res.end('Internal server error');
        });
        
      } catch (error) {
        console.error('Static server error:', error);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal server error');
      }
    });
    
    staticServer.listen(port, '127.0.0.1', () => {
      // console.log(`Static server running on port ${port}`);
      resolve(port);
    });
    
    staticServer.on('error', (error) => {
      console.error('Static server failed to start:', error);
      reject(error);
    });
  });
}

// ========================================
// WINDOW CREATION
// ========================================

async function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'src', 'assets', 'Hearthlink.png'),
    title: 'Hearthlink - AI Orchestration Hub',
    resizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
      allowRunningInsecureContent: false
    },
    show: false, // Don't show until ready
    titleBarStyle: 'default',
    autoHideMenuBar: false
  });

  // Load the app with proper asset handling
  // Try development server first, fallback to static server
  let startUrl = 'http://127.0.0.1:3005';
  
  // Check if dev server is running with retry logic
  let devServerReady = false;
  for (let attempt = 1; attempt <= 10; attempt++) {
    try {
      // console.log(`🔍 Checking React dev server on port 3005... (attempt ${attempt}/10)`);
      
      // Test with a simple HTTP request
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
        // console.log('✅ React dev server ready, loading...');
        devServerReady = true;
        break;
      } else {
        throw new Error('Dev server returned non-200 status');
      }
      
    } catch (error) {
      // console.log(`⏳ React dev server not ready (attempt ${attempt}/10): ${error.message}`);
      if (attempt < 10) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
      }
    }
  }
  
  if (!devServerReady) {
    // console.log('❌ React dev server not available after 10 attempts');
    
    // Use test page as temporary fallback while build issues are resolved
    const testPath = path.join(__dirname, 'public', 'test.html');
    if (fs.existsSync(testPath)) {
      startUrl = `file://${testPath}`;
      console.log('🧪 Using test page as fallback:', testPath);
    } else {
      // Check if build exists
      const buildPath = path.join(__dirname, 'build', 'index.html');
      if (fs.existsSync(buildPath)) {
        startUrl = `file://${buildPath}`;
        console.log('📁 Using build directory:', buildPath);
      } else {
        // Use static server fallback
        startUrl = `http://127.0.0.1:3008`;
        console.log('🔄 Using static server fallback');
      }
    }
  }
  
  // Set up protocol handler for serving static files
  setupProtocolHandler();
  
  // Load the URL with error handling
  // console.log('Loading URL:', startUrl);
  // console.log('Build directory exists:', fs.existsSync(path.join(__dirname, 'build')));
  // console.log('Index.html exists:', fs.existsSync(path.join(__dirname, 'build', 'index.html')));
  
  // Try loading the main app
  mainWindow.loadURL(startUrl).catch(err => {
    console.error('Failed to load main URL:', err);
    // Fallback to public/index.html
    const fallbackUrl = `file://${path.join(__dirname, 'public', 'index.html')}`;
    // console.log('Trying fallback URL:', fallbackUrl);
    mainWindow.loadURL(fallbackUrl).catch(err2 => {
      console.error('Failed to load fallback URL:', err2);
      // Load test page
      const testUrl = `file://${path.join(__dirname, 'public', 'test.html')}`;
      // console.log('Loading test page:', testUrl);
      mainWindow.loadURL(testUrl);
    });
  });

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus the window
    mainWindow.focus();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Security: Prevent new window creation
  mainWindow.webContents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
  
  // Log asset loading errors
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('Failed to load:', { errorCode, errorDescription, validatedURL });
  });
  
  // Log successful loads
  mainWindow.webContents.on('did-finish-load', () => {
    // console.log('Main window loaded successfully');
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Session',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('new-session');
          }
        },
        {
          label: 'Open User Guide',
          accelerator: 'F1',
          click: () => {
            mainWindow.webContents.send('open-user-guide');
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
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
        { role: 'paste' },
        { role: 'selectall' }
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
      label: 'Help',
      submenu: [
        {
          label: 'User Guide',
          click: () => {
            mainWindow.webContents.send('open-user-guide');
          }
        },
        {
          label: 'Accessibility Guide',
          click: () => {
            mainWindow.webContents.send('open-accessibility-guide');
          }
        },
        {
          label: 'Troubleshooting',
          click: () => {
            mainWindow.webContents.send('open-troubleshooting');
          }
        },
        { type: 'separator' },
        {
          label: 'About Hearthlink',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Hearthlink',
              message: 'Hearthlink v1.1.0',
              detail: 'AI-Powered Productivity System with Voice Commands\n\nBuilt with accessibility and voice-first design principles.\n\n© 2025 Hearthlink Development Team\nMIT License',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  // Add development menu in development mode
  if (process.env.NODE_ENV === 'development') {
    template.push({
      label: 'Development',
      submenu: [
        { role: 'toggleDevTools' },
        { type: 'separator' },
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.reload();
          }
        }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(async () => {
  try {
    // Try to start static server as fallback
    const staticPort = await startStaticServer();
    // console.log(`Static server started on port ${staticPort}`);
    
    // Update environment to use static server if needed
    if (!process.env.ELECTRON_START_URL) {
      process.env.ELECTRON_START_URL = `http://localhost:${staticPort}`;
    }
  } catch (error) {
    console.warn('Static server failed to start, using file protocol:', error.message);
  }
  
  // Start Python backend (temporarily disabled for testing)
  // console.log('Python backend startup disabled for testing');
  
  await createWindow();
  createMenu();

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

// Cleanup on app quit
app.on('before-quit', () => {
  if (staticServer) {
    staticServer.close();
    // console.log('Static server closed');
  }
  
  // Stop Python backend
  if (pythonProcess) {
    // console.log('Stopping Python backend...');
    pythonProcess.kill('SIGTERM');
    
    // Force kill after 5 seconds
    setTimeout(() => {
      if (pythonProcess && !pythonProcess.killed) {
        pythonProcess.kill('SIGKILL');
      }
    }, 5000);
  }
});

// Error handling
process.on('uncaughtException', (error) => {
  // Silent error handling to prevent console issues
});

process.on('unhandledRejection', (reason, promise) => {
  // Silent error handling to prevent console issues
});

// Handle renderer process crashes
app.on('render-process-gone', (event, webContents, details) => {
  // Silent error handling to prevent console issues
});

// Handle renderer process errors
app.on('web-contents-created', (event, contents) => {
  contents.on('crashed', (event, killed) => {
    // Silent error handling to prevent console issues
  });
  
  contents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    // Silent error handling to prevent console issues
  });
});

// IPC handlers for communication with renderer process
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-app-path', () => {
  return app.getAppPath();
});

ipcMain.handle('get-resource-path', (event, resourcePath) => {
  return path.join(process.resourcesPath, resourcePath);
});

ipcMain.handle('read-documentation', (event, docPath) => {
  try {
    const fullPath = path.join(process.resourcesPath, 'docs', 'public', docPath);
    return fs.readFileSync(fullPath, 'utf8');
  } catch (error) {
    console.error('Error reading documentation:', error);
    return null;
  }
});

ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url);
});

// Python backend integration
const { spawn } = require('child_process');
let pythonProcess = null;
let pythonReadyPromise = null;

// Validate Python executable path for security
function validatePythonPath(pythonPath) {
  if (!pythonPath || typeof pythonPath !== 'string') {
    throw new Error('Invalid Python path');
  }
  
  // Remove any command injection attempts
  const sanitized = pythonPath.replace(/[;&|`$(){}[\]]/g, '');
  
  // Whitelist of allowed Python executables
  const allowedPythonPaths = [
    'python',
    'python3',
    'python3.8',
    'python3.9',
    'python3.10',
    'python3.11',
    'python3.12',
    'python3.13',
    '/usr/bin/python',
    '/usr/bin/python3',
    '/usr/local/bin/python',
    '/usr/local/bin/python3',
    'C:\\Python\\python.exe',
    'C:\\Python3\\python.exe',
    'C:\\Program Files\\Python\\python.exe'
  ];
  
  // Check if it's a whitelisted name or starts with a whitelisted path
  const isAllowed = allowedPythonPaths.some(allowed => 
    sanitized === allowed || 
    (allowed.includes('\\') && sanitized.startsWith(allowed.substring(0, allowed.lastIndexOf('\\'))))
  );
  
  if (!isAllowed && !path.isAbsolute(sanitized)) {
    throw new Error('Python path not in whitelist');
  }
  
  return sanitized;
}

// Start Python backend process with security validation
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    try {
      const rawPythonPath = process.env.PYTHON_PATH || 'python';
      const pythonPath = validatePythonPath(rawPythonPath);
      const backendScript = path.join(__dirname, 'src', 'main.py');
      
      // Verify backend script exists and is within project directory
      const projectDir = path.resolve(__dirname);
      const scriptPath = path.resolve(backendScript);
      if (!scriptPath.startsWith(projectDir)) {
        throw new Error('Backend script path traversal blocked');
      }
      
      if (!fs.existsSync(backendScript)) {
        throw new Error('Backend script not found');
      }
      
      console.log('[SECURITY] Starting Python backend:', pythonPath, backendScript);
      
      pythonProcess = spawn(pythonPath, [backendScript, '--ipc'], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { 
          ...process.env, 
          PYTHONPATH: path.join(__dirname, 'src'),
          // Clear potentially dangerous environment variables
          LD_PRELOAD: undefined,
          LD_LIBRARY_PATH: undefined
        }
      });
    } catch (error) {
      console.error('[SECURITY] Python backend validation failed:', error.message);
      reject(error);
      return;
    }
    
    let initBuffer = '';
    
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      // console.log('Python output:', output);
      
      initBuffer += output;
      
      // Check for initialization complete signal
      if (initBuffer.includes('HEARTHLINK_READY')) {
        // console.log('Python backend ready');
        resolve(true);
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error('Python error:', data.toString());
    });
    
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python backend:', error);
      reject(error);
    });
    
    pythonProcess.on('close', (code) => {
      // console.log('Python backend process exited with code:', code);
      pythonProcess = null;
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      if (!pythonProcess?.killed) {
        reject(new Error('Python backend startup timeout'));
      }
    }, 10000);
  });
}

// Send command to Python backend
function sendToPython(command) {
  return new Promise((resolve, reject) => {
    if (!pythonProcess) {
      reject(new Error('Python backend not running'));
      return;
    }
    
    const message = JSON.stringify(command) + '\n';
    pythonProcess.stdin.write(message);
    
    // Listen for response
    const timeout = setTimeout(() => {
      reject(new Error('Python backend response timeout'));
    }, 5000);
    
    const responseHandler = (data) => {
      try {
        const response = JSON.parse(data.toString());
        if (response.id === command.id) {
          clearTimeout(timeout);
          pythonProcess.stdout.removeListener('data', responseHandler);
          resolve(response);
        }
      } catch (error) {
        // Continue listening for valid JSON
      }
    };
    
    pythonProcess.stdout.on('data', responseHandler);
  });
}

// Handle voice command requests
ipcMain.handle('voice-command', async (event, command) => {
  try {
    // console.log('Voice command received:', command);
    
    const pythonCommand = {
      id: Date.now(),
      type: 'voice_command',
      payload: { command: command }
    };
    
    const response = await sendToPython(pythonCommand);
    
    // Send response back to renderer
    mainWindow.webContents.send('voice-command-response', {
      command: command,
      success: response.success,
      response: response.data || `Processed: ${command}`
    });
    
    return response;
  } catch (error) {
    console.error('Voice command error:', error);
    mainWindow.webContents.send('voice-command-response', {
      command: command,
      success: false,
      error: error.message
    });
    return { success: false, error: error.message };
  }
});

// Handle accessibility features
ipcMain.handle('accessibility-toggle', (event, feature) => {
  // console.log('Accessibility feature toggled:', feature);
  
  // Implement accessibility feature toggles
  switch (feature) {
    case 'high-contrast':
      mainWindow.webContents.send('accessibility-update', { feature: 'high-contrast' });
      break;
    case 'screen-reader':
      mainWindow.webContents.send('accessibility-update', { feature: 'screen-reader' });
      break;
    case 'voice-feedback':
      mainWindow.webContents.send('accessibility-update', { feature: 'voice-feedback' });
      break;
  }
});

// Core session management
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

// Vault operations
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

// Synapse plugin operations
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

// Google API Rate Limiter
class GoogleAPIRateLimiter {
  constructor() {
    this.requests = [];
    this.maxRequests = 60; // 60 requests per minute
    this.timeWindow = 60 * 1000; // 60 seconds in milliseconds
  }
  
  canMakeRequest() {
    const now = Date.now();
    // Remove requests older than 1 minute
    this.requests = this.requests.filter(time => now - time < this.timeWindow);
    return this.requests.length < this.maxRequests;
  }
  
  addRequest() {
    this.requests.push(Date.now());
  }
  
  getWaitTime() {
    if (this.requests.length === 0) return 0;
    const oldestRequest = Math.min(...this.requests);
    const waitTime = this.timeWindow - (Date.now() - oldestRequest);
    return Math.max(0, waitTime);
  }
  
  getRemainingRequests() {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < this.timeWindow);
    return this.maxRequests - this.requests.length;
  }
}

const googleRateLimiter = new GoogleAPIRateLimiter();

// Delegation Metrics Tracking
class DelegationMetricsTracker {
  constructor() {
    this.sessions = new Map();
    this.globalMetrics = {
      totalDelegations: 0,
      averageResponseTime: 0,
      averageVerbosity: 0,
      averageQuality: 0,
      contextDriftEvents: 0,
      successRate: 0,
      startTime: Date.now()
    };
  }

  startSession(sessionId, taskData) {
    const session = {
      id: sessionId,
      task: taskData.task,
      context: taskData.context,
      startTime: Date.now(),
      taskComplexity: this.assessTaskComplexity(taskData.task),
      taskType: this.classifyTaskType(taskData.task),
      contextLength: taskData.context ? taskData.context.length : 0
    };
    
    this.sessions.set(sessionId, session);
    // console.log(`[METRICS] Started session ${sessionId}: ${taskData.task.substring(0, 50)}...`);
    return session;
  }

  recordResponse(sessionId, response, success = true, errorType = null) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;
    
    const endTime = Date.now();
    const responseTime = endTime - session.startTime;
    
    session.endTime = endTime;
    session.responseTime = responseTime;
    session.success = success;
    session.errorType = errorType;
    
    if (success && response) {
      session.responseLength = response.length;
      session.verbosityScore = this.calculateVerbosityScore(response);
      session.qualityScore = this.assessResponseQuality(session.task, response);
      session.contextDrift = this.detectContextDrift(session.context, response);
      session.actionableItems = this.extractActionableItems(response);
    }
    
    this.updateGlobalMetrics(session);
    
    // Log metrics
    // console.log(`[METRICS] Session ${sessionId} completed:`);
    // console.log(`  Response Time: ${responseTime}ms`);
    // console.log(`  Response Length: ${session.responseLength} chars`);
    // console.log(`  Verbosity Score: ${session.verbosityScore?.overall?.toFixed(1) || 'N/A'}`);
    // console.log(`  Quality Score: ${session.qualityScore?.overall?.toFixed(1) || 'N/A'}`);
    // console.log(`  Context Drift: ${session.contextDrift?.severity || 'N/A'}`);
    // console.log(`  Actionable Items: ${session.actionableItems?.count || 0}`);
    
    return this.generateReport(session);
  }

  assessTaskComplexity(task) {
    const complexityIndicators = {
      high: ['architecture', 'optimize', 'design', 'implement', 'integrate', 'security', 'performance'],
      medium: ['analyze', 'review', 'improve', 'enhance', 'modify', 'update'],
      low: ['explain', 'describe', 'list', 'show', 'tell', 'what', 'how']
    };
    
    const taskLower = task.toLowerCase();
    for (const [level, indicators] of Object.entries(complexityIndicators)) {
      if (indicators.some(indicator => taskLower.includes(indicator))) {
        return level;
      }
    }
    return 'medium';
  }

  classifyTaskType(task) {
    const taskTypes = {
      'code-generation': ['generate', 'create', 'write', 'build', 'implement'],
      'analysis': ['analyze', 'review', 'assess', 'evaluate', 'examine'],
      'optimization': ['optimize', 'improve', 'enhance', 'speed up', 'performance'],
      'architecture': ['design', 'architecture', 'structure', 'pattern', 'framework'],
      'debugging': ['debug', 'fix', 'error', 'problem', 'issue', 'bug'],
      'explanation': ['explain', 'describe', 'how', 'what', 'why', 'tell']
    };
    
    const taskLower = task.toLowerCase();
    for (const [type, keywords] of Object.entries(taskTypes)) {
      if (keywords.some(keyword => taskLower.includes(keyword))) {
        return type;
      }
    }
    return 'general';
  }

  calculateVerbosityScore(response) {
    const length = response.length;
    const words = response.split(/\s+/).length;
    const sentences = response.split(/[.!?]+/).length;
    
    return {
      overall: Math.min(5, length / 1000), // Simple verbosity score
      characterCount: length,
      wordCount: words,
      sentenceCount: sentences,
      avgWordsPerSentence: words / sentences
    };
  }

  assessResponseQuality(task, response) {
    const relevance = this.assessRelevance(task, response);
    const completeness = this.assessCompleteness(response);
    const actionability = this.assessActionability(response);
    
    return {
      overall: (relevance + completeness + actionability) / 3,
      relevance,
      completeness,
      actionability
    };
  }

  assessRelevance(task, response) {
    const taskKeywords = this.extractKeywords(task);
    const responseKeywords = this.extractKeywords(response);
    const overlap = this.calculateKeywordOverlap(taskKeywords, responseKeywords);
    return Math.min(5, overlap * 10);
  }

  assessCompleteness(response) {
    const completenessIndicators = ['analysis', 'approach', 'implementation', 'details', 'risks', 'outcomes'];
    const found = completenessIndicators.filter(indicator => response.toLowerCase().includes(indicator));
    return Math.min(5, (found.length / completenessIndicators.length) * 5);
  }

  assessActionability(response) {
    const actionableIndicators = ['implement', 'create', 'add', 'modify', 'step', 'first', 'then', 'next'];
    const found = actionableIndicators.filter(indicator => response.toLowerCase().includes(indicator));
    return Math.min(5, (found.length / 4) * 5);
  }

  detectContextDrift(originalContext, response) {
    if (!originalContext) return { drift: 0, severity: 'none' };
    
    const contextKeywords = this.extractKeywords(originalContext);
    const responseKeywords = this.extractKeywords(response);
    const overlap = this.calculateKeywordOverlap(contextKeywords, responseKeywords);
    const drift = 1 - overlap;
    
    let severity = 'none';
    if (drift > 0.5) severity = 'high';
    else if (drift > 0.3) severity = 'medium';
    else if (drift > 0.1) severity = 'low';
    
    return { drift, severity, overlap };
  }

  extractActionableItems(response) {
    const actionPatterns = [
      /\d+\.\s*(.+?)(?=\n|\d+\.|$)/g,
      /[-•]\s*(.+?)(?=\n|[-•]|$)/g,
      /implement\s+(.+?)(?=\n|\.)/gi,
      /create\s+(.+?)(?=\n|\.)/gi
    ];
    
    const items = [];
    actionPatterns.forEach(pattern => {
      const matches = response.matchAll(pattern);
      for (const match of matches) {
        if (match[1] && match[1].trim().length > 10) {
          items.push(match[1].trim());
        }
      }
    });
    
    return { count: items.length, items: items.slice(0, 5) };
  }

  extractKeywords(text) {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 3)
      .filter(word => !['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were'].includes(word));
  }

  calculateKeywordOverlap(keywords1, keywords2) {
    const set1 = new Set(keywords1);
    const set2 = new Set(keywords2);
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return intersection.size / union.size;
  }

  updateGlobalMetrics(session) {
    this.globalMetrics.totalDelegations++;
    
    if (session.success) {
      const total = this.globalMetrics.totalDelegations;
      this.globalMetrics.averageResponseTime = 
        (this.globalMetrics.averageResponseTime * (total - 1) + session.responseTime) / total;
      
      if (session.verbosityScore) {
        this.globalMetrics.averageVerbosity = 
          (this.globalMetrics.averageVerbosity * (total - 1) + session.verbosityScore.overall) / total;
      }
      
      if (session.qualityScore) {
        this.globalMetrics.averageQuality = 
          (this.globalMetrics.averageQuality * (total - 1) + session.qualityScore.overall) / total;
      }
      
      if (session.contextDrift && session.contextDrift.severity !== 'none') {
        this.globalMetrics.contextDriftEvents++;
      }
    }
    
    const successfulSessions = Array.from(this.sessions.values()).filter(s => s.success).length;
    this.globalMetrics.successRate = successfulSessions / this.globalMetrics.totalDelegations;
  }

  generateReport(session) {
    return {
      sessionId: session.id,
      metrics: {
        responseTime: session.responseTime,
        responseLength: session.responseLength,
        verbosity: session.verbosityScore,
        quality: session.qualityScore,
        contextDrift: session.contextDrift,
        actionableItems: session.actionableItems,
        taskComplexity: session.taskComplexity,
        taskType: session.taskType
      },
      recommendations: this.generateRecommendations(session),
      timestamp: new Date().toISOString()
    };
  }

  generateRecommendations(session) {
    const recommendations = [];
    
    if (session.responseTime > 10000) {
      recommendations.push('Consider breaking down complex tasks for faster responses');
    }
    
    if (session.verbosityScore?.overall > 4) {
      recommendations.push('Response was very verbose - consider requesting more concise answers');
    }
    
    if (session.qualityScore?.overall < 3) {
      recommendations.push('Low quality response - provide more specific context next time');
    }
    
    if (session.contextDrift?.severity === 'high') {
      recommendations.push('High context drift detected - refine task description');
    }
    
    return recommendations;
  }

  getGlobalMetrics() {
    const uptime = Date.now() - this.globalMetrics.startTime;
    return {
      ...this.globalMetrics,
      uptime,
      sessionsActive: this.sessions.size,
      contextDriftRate: this.globalMetrics.contextDriftEvents / Math.max(1, this.globalMetrics.totalDelegations)
    };
  }
}

const delegationMetrics = new DelegationMetricsTracker();

// Simulation mode flag
const SIMULATION_MODE = process.env.NODE_ENV === 'development' || !process.env.GOOGLE_API_KEY;

// Data persistence utilities
const metricsFilePath = path.join(userDataPath, 'delegation-metrics.json');

// Load persisted metrics on startup
function loadPersistedMetrics() {
  try {
    if (fs.existsSync(metricsFilePath)) {
      const data = JSON.parse(fs.readFileSync(metricsFilePath, 'utf8'));
      if (data.globalMetrics) {
        delegationMetrics.globalMetrics = { ...delegationMetrics.globalMetrics, ...data.globalMetrics };
      }
      if (data.sessions) {
        data.sessions.forEach(session => {
          delegationMetrics.sessions.set(session.id, session);
        });
      }
      console.log('[PERSISTENCE] Loaded metrics from disk');
    }
  } catch (error) {
    console.error('[PERSISTENCE] Error loading metrics:', error);
  }
}

// Save metrics to disk
function saveMetrics() {
  try {
    const data = {
      globalMetrics: delegationMetrics.globalMetrics,
      sessions: Array.from(delegationMetrics.sessions.entries()).map(([id, session]) => ({ id, ...session })),
      lastSaved: new Date().toISOString()
    };
    fs.writeFileSync(metricsFilePath, JSON.stringify(data, null, 2), 'utf8');
    console.log('[PERSISTENCE] Metrics saved to disk');
  } catch (error) {
    console.error('[PERSISTENCE] Error saving metrics:', error);
  }
}

// Auto-save metrics every 5 minutes
setInterval(saveMetrics, 5 * 60 * 1000);

// Load metrics on startup
loadPersistedMetrics();

// Save metrics on process exit
process.on('exit', saveMetrics);
process.on('SIGINT', () => {
  saveMetrics();
  process.exit(0);
});
process.on('SIGTERM', () => {
  saveMetrics();
  process.exit(0);
});

// Simulation response generator
function generateSimulationResponse(task, context) {
  const taskLower = task.toLowerCase();
  const responses = {
    analyze: `## Analysis Results

Based on the task "${task}", I've conducted a comprehensive analysis:

### Key Findings:
1. **Architecture Review**: The current implementation shows solid foundations with room for optimization
2. **Performance Considerations**: Several bottlenecks identified in the data processing pipeline
3. **Security Assessment**: Current measures are adequate but could be enhanced with additional layers

### Recommendations:
1. **Immediate Actions**:
   - Implement caching mechanisms for frequently accessed data
   - Add input validation to prevent injection attacks
   - Optimize database queries for better performance

2. **Long-term Improvements**:
   - Consider microservices architecture for better scalability
   - Implement comprehensive logging and monitoring
   - Add automated testing coverage

### Implementation Strategy:
The recommended approach is to tackle these improvements incrementally, starting with the most critical performance issues.

*This is a simulated response for development testing.*`,

    optimize: `## Optimization Strategy

For the optimization task: "${task}"

### Performance Analysis:
- **Current Bottlenecks**: Identified 3 major performance issues
- **Memory Usage**: 15% reduction possible with better resource management
- **Response Time**: Projected 40% improvement with proposed changes

### Recommended Optimizations:

1. **Code-Level Improvements**:
   - Implement lazy loading for large datasets
   - Use efficient data structures (Map vs Object)
   - Minimize DOM manipulations

2. **Architecture Optimizations**:
   - Add Redis caching layer
   - Implement connection pooling
   - Use CDN for static assets

3. **Database Optimizations**:
   - Add composite indexes
   - Implement query optimization
   - Use database connection pooling

### Expected Impact:
- **Performance**: 40% faster response times
- **Memory**: 15% reduction in memory usage
- **Scalability**: Support for 3x current load

*This is a simulated response for development testing.*`,

    design: `## Design Architecture

Design proposal for: "${task}"

### Architectural Overview:
A modular, scalable architecture that emphasizes maintainability and performance.

### Core Components:

1. **Presentation Layer**:
   - React components with TypeScript
   - Responsive design with CSS Grid/Flexbox
   - Accessibility-first approach

2. **Business Logic Layer**:
   - Service classes for business operations
   - State management with Redux/Context
   - Validation and error handling

3. **Data Layer**:
   - Repository pattern for data access
   - Caching strategies
   - Database abstraction

### Key Design Patterns:
- **Observer Pattern**: For real-time updates
- **Factory Pattern**: For component creation
- **Singleton Pattern**: For shared resources
- **Strategy Pattern**: For algorithm selection

### Technology Stack:
- **Frontend**: React, TypeScript, CSS-in-JS
- **Backend**: Node.js, Express, PostgreSQL
- **Infrastructure**: Docker, Kubernetes, CI/CD

### Security Considerations:
- Input validation and sanitization
- JWT authentication
- Rate limiting
- CORS configuration

*This is a simulated response for development testing.*`,

    default: `## Task Analysis

I've reviewed the task: "${task}"

### Approach:
Based on the requirements, I recommend a systematic approach that addresses the core objectives while maintaining code quality and performance.

### Key Considerations:
1. **Functionality**: Ensure all requirements are met
2. **Performance**: Optimize for speed and efficiency
3. **Maintainability**: Write clean, documented code
4. **Security**: Implement proper validation and error handling

### Implementation Steps:
1. **Planning Phase**: Define clear requirements and acceptance criteria
2. **Development Phase**: Implement core functionality with tests
3. **Testing Phase**: Comprehensive testing including edge cases
4. **Deployment Phase**: Staged rollout with monitoring

### Best Practices:
- Follow established coding standards
- Implement comprehensive error handling
- Add proper logging and monitoring
- Ensure accessibility compliance

${context ? `\n### Context Considerations:\nBased on the provided context: "${context}", I've tailored this response to address the specific requirements and constraints mentioned.` : ''}

*This is a simulated response for development testing.*`
  };

  if (taskLower.includes('analy')) return responses.analyze;
  if (taskLower.includes('optim')) return responses.optimize;
  if (taskLower.includes('design') || taskLower.includes('architect')) return responses.design;
  
  return responses.default;
}

// Error suggestion system
function getErrorSuggestion(errorType) {
  const suggestions = {
    'rate_limit_exceeded': 'Rate limit exceeded. Wait for the rate limit to reset or upgrade your API quota.',
    'network_error': 'Network connectivity issue. Check your internet connection and try again.',
    'authentication_error': 'API key is invalid or missing. Verify your Google API key in environment variables.',
    'timeout_error': 'Request timed out. The API might be experiencing high load. Try again later.',
    'bad_request': 'Invalid request format. Check the task content and try reformulating the request.',
    'server_error': 'Google API server error. This is likely temporary. Try again in a few minutes.',
    'unknown_error': 'An unexpected error occurred. Check the console logs for more details.'
  };
  
  return suggestions[errorType] || suggestions['unknown_error'];
}

// Google API Integration with Rate Limiting
ipcMain.handle('google-api-call', async (event, message, options = {}) => {
  try {
    // Check rate limit
    if (!googleRateLimiter.canMakeRequest()) {
      const waitTime = googleRateLimiter.getWaitTime();
      return {
        success: false,
        error: `Rate limit exceeded. Please wait ${Math.ceil(waitTime / 1000)} seconds.`,
        rateLimited: true,
        waitTime: waitTime,
        timestamp: new Date().toISOString()
      };
    }
    
    const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY || "AIzaSyDEYEEBVMdoThR2Oex0bwxPjzr_wMyG6oA";
    
    // Add request to rate limiter
    googleRateLimiter.addRequest();
    
    const requestBody = {
      contents: [{
        parts: [{
          text: message
        }]
      }]
    };
    
    // Add generation config if provided
    if (options.temperature !== undefined || options.maxTokens !== undefined) {
      requestBody.generationConfig = {};
      if (options.temperature !== undefined) {
        requestBody.generationConfig.temperature = options.temperature;
      }
      if (options.maxTokens !== undefined) {
        requestBody.generationConfig.maxOutputTokens = options.maxTokens;
      }
    }
    
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GOOGLE_API_KEY}`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`Google API Error: ${data.error?.message || 'Unknown error'}`);
    }
    
    return {
      success: true,
      response: data.candidates[0]?.content?.parts[0]?.text || 'No response from Google API',
      timestamp: new Date().toISOString(),
      rateLimitInfo: {
        remaining: googleRateLimiter.getRemainingRequests(),
        resetTime: new Date(Date.now() + googleRateLimiter.getWaitTime()).toISOString()
      }
    };
  } catch (error) {
    console.error('Google API call error:', error);
    return { 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString(),
      rateLimitInfo: {
        remaining: googleRateLimiter.getRemainingRequests(),
        resetTime: new Date(Date.now() + googleRateLimiter.getWaitTime()).toISOString()
      }
    };
  }
});

// Claude Code to Google API Task Delegation with Metrics
ipcMain.handle('claude-delegate-to-google', async (event, taskData) => {
  const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  try {
    const { task, context, requiresReview = true } = taskData;
    
    // Start metrics tracking
    delegationMetrics.startSession(sessionId, taskData);
    
    // Check rate limit
    if (!googleRateLimiter.canMakeRequest()) {
      const waitTime = googleRateLimiter.getWaitTime();
      
      // Record failed session
      delegationMetrics.recordResponse(sessionId, null, false, 'rate_limit_exceeded');
      
      return {
        success: false,
        error: `Rate limit exceeded. Please wait ${Math.ceil(waitTime / 1000)} seconds.`,
        rateLimited: true,
        waitTime: waitTime,
        timestamp: new Date().toISOString(),
        sessionId: sessionId
      };
    }
    
    // Construct delegation message
    const delegationMessage = `
TASK DELEGATION FROM CLAUDE CODE:

Task: ${task}
Context: ${context || 'No additional context provided'}

Please provide a detailed response that I can review and implement. Include:
1. Analysis of the task
2. Recommended approach
3. Implementation details
4. Potential risks or considerations
5. Expected outcomes

Format your response clearly for review and implementation.`;

    let googleResponse;
    
    if (SIMULATION_MODE) {
      // Simulation mode - generate realistic responses without API calls
      console.log('[SIMULATION] Running in simulation mode');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      // Generate contextual simulation response
      googleResponse = generateSimulationResponse(task, context);
      
      console.log('[SIMULATION] Generated simulated response');
    } else {
      // Real API mode
      const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY || "AIzaSyDEYEEBVMdoThR2Oex0bwxPjzr_wMyG6oA";
      
      // Add request to rate limiter
      googleRateLimiter.addRequest();
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GOOGLE_API_KEY}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: delegationMessage
            }]
          }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 2048
          }
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(`Google API Error: ${data.error?.message || 'Unknown error'}`);
      }
      
      googleResponse = data.candidates[0]?.content?.parts[0]?.text || 'No response from Google API';
    }
    
    // Record successful response and get metrics
    const metricsReport = delegationMetrics.recordResponse(sessionId, googleResponse, true);
    
    return {
      success: true,
      task: task,
      googleResponse: googleResponse,
      requiresReview: requiresReview,
      delegatedAt: new Date().toISOString(),
      sessionId: sessionId,
      metrics: metricsReport?.metrics,
      recommendations: metricsReport?.recommendations,
      rateLimitInfo: {
        remaining: googleRateLimiter.getRemainingRequests(),
        resetTime: new Date(Date.now() + googleRateLimiter.getWaitTime()).toISOString()
      }
    };
    
  } catch (error) {
    console.error('Claude delegation error:', error);
    
    // Enhanced error categorization
    let errorType = 'unknown_error';
    let errorMessage = error.message;
    let recoverable = false;
    let retryAfter = 0;
    
    if (error.message.includes('rate limit') || error.message.includes('quota')) {
      errorType = 'rate_limit_exceeded';
      recoverable = true;
      retryAfter = 60; // 1 minute
    } else if (error.message.includes('network') || error.message.includes('ECONNRESET')) {
      errorType = 'network_error';
      recoverable = true;
      retryAfter = 10; // 10 seconds
    } else if (error.message.includes('API key') || error.message.includes('authentication')) {
      errorType = 'authentication_error';
      recoverable = false;
    } else if (error.message.includes('timeout')) {
      errorType = 'timeout_error';
      recoverable = true;
      retryAfter = 30; // 30 seconds
    } else if (error.message.includes('400') || error.message.includes('Bad Request')) {
      errorType = 'bad_request';
      recoverable = false;
    } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
      errorType = 'server_error';
      recoverable = true;
      retryAfter = 60; // 1 minute
    }
    
    // Record failed response with detailed error information
    delegationMetrics.recordResponse(sessionId, null, false, errorType);
    
    // Auto-save metrics after error
    saveMetrics();
    
    return { 
      success: false, 
      error: errorMessage,
      errorType: errorType,
      recoverable: recoverable,
      retryAfter: retryAfter,
      timestamp: new Date().toISOString(),
      sessionId: sessionId,
      rateLimitInfo: {
        remaining: googleRateLimiter.getRemainingRequests(),
        resetTime: new Date(Date.now() + googleRateLimiter.getWaitTime()).toISOString()
      },
      troubleshooting: {
        suggestion: getErrorSuggestion(errorType),
        documentation: "Check the AI Collaboration Log for detailed error information"
      }
    };
  }
});

// Get Google API Rate Limit Status
ipcMain.handle('google-api-status', async (event) => {
  return {
    success: true,
    rateLimitInfo: {
      remaining: googleRateLimiter.getRemainingRequests(),
      maxRequests: googleRateLimiter.maxRequests,
      timeWindow: googleRateLimiter.timeWindow,
      canMakeRequest: googleRateLimiter.canMakeRequest(),
      waitTime: googleRateLimiter.getWaitTime(),
      resetTime: new Date(Date.now() + googleRateLimiter.getWaitTime()).toISOString()
    },
    timestamp: new Date().toISOString()
  };
});

// Get Delegation Metrics
ipcMain.handle('get-delegation-metrics', async (event) => {
  try {
    const globalMetrics = delegationMetrics.getGlobalMetrics();
    const recentSessions = Array.from(delegationMetrics.sessions.values())
      .slice(-10) // Get last 10 sessions
      .map(session => ({
        id: session.id,
        task: session.task.substring(0, 100) + '...',
        taskType: session.taskType,
        taskComplexity: session.taskComplexity,
        responseTime: session.responseTime,
        success: session.success,
        verbosityScore: session.verbosityScore?.overall,
        qualityScore: session.qualityScore?.overall,
        contextDrift: session.contextDrift?.severity,
        actionableItems: session.actionableItems?.count,
        timestamp: new Date(session.startTime).toISOString()
      }));
    
    return {
      success: true,
      globalMetrics: globalMetrics,
      recentSessions: recentSessions,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error getting delegation metrics:', error);
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
});

// Alden Workspace File Operations
ipcMain.handle('alden-write-file', async (event, { filePath, content, createDirectories = true }) => {
  try {
    // Security: Ensure the file path is within allowed directories
    const allowedPaths = [
      path.resolve('./'),
      path.resolve('../'),
      path.resolve(process.cwd())
    ];
    
    const resolvedPath = path.resolve(filePath);
    const isAllowed = allowedPaths.some(allowedPath => 
      resolvedPath.startsWith(allowedPath)
    );
    
    if (!isAllowed) {
      throw new Error('File path not allowed for security reasons');
    }
    
    // Create directories if needed
    if (createDirectories) {
      const dir = path.dirname(resolvedPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
    
    // Write the file
    fs.writeFileSync(resolvedPath, content, 'utf8');
    
    console.log(`[ALDEN] Successfully wrote file: ${resolvedPath}`);
    
    return {
      success: true,
      filePath: resolvedPath,
      size: content.length,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('[ALDEN] File write error:', error);
    return {
      success: false,
      error: error.message,
      filePath: filePath,
      timestamp: new Date().toISOString()
    };
  }
});

// Alden Read File
ipcMain.handle('alden-read-file', async (event, { filePath }) => {
  try {
    const resolvedPath = path.resolve(filePath);
    
    if (!fs.existsSync(resolvedPath)) {
      throw new Error('File does not exist');
    }
    
    const content = fs.readFileSync(resolvedPath, 'utf8');
    const stats = fs.statSync(resolvedPath);
    
    return {
      success: true,
      filePath: resolvedPath,
      content: content,
      size: stats.size,
      modified: stats.mtime.toISOString(),
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('[ALDEN] File read error:', error);
    return {
      success: false,
      error: error.message,
      filePath: filePath,
      timestamp: new Date().toISOString()
    };
  }
});

// Alden List Directory
ipcMain.handle('alden-list-directory', async (event, { dirPath }) => {
  try {
    const resolvedPath = path.resolve(dirPath);
    
    if (!fs.existsSync(resolvedPath)) {
      throw new Error('Directory does not exist');
    }
    
    const files = fs.readdirSync(resolvedPath, { withFileTypes: true });
    const fileList = files.map(file => ({
      name: file.name,
      path: path.join(resolvedPath, file.name),
      isDirectory: file.isDirectory(),
      isFile: file.isFile()
    }));
    
    return {
      success: true,
      dirPath: resolvedPath,
      files: fileList,
      count: fileList.length,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('[ALDEN] Directory list error:', error);
    return {
      success: false,
      error: error.message,
      dirPath: dirPath,
      timestamp: new Date().toISOString()
    };
  }
});

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, focus our window instead
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
} 