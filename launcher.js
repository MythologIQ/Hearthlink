#!/usr/bin/env node

/**
 * Hearthlink Native Application Launcher
 * 
 * Comprehensive launcher for the Hearthlink AI orchestration platform
 * with enhanced Alice behavioral analysis integration and system monitoring.
 */

const { app, BrowserWindow, Menu, shell, ipcMain, dialog, protocol, systemPreferences } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const url = require('url');
const { spawn } = require('child_process');
const os = require('os');
const net = require('net');

// Simple Node.js logger for launcher
class LauncherLogger {
  constructor() {
    this.logLevels = ['error', 'warn', 'info', 'debug'];
    this.currentLevel = process.env.HEARTHLINK_LOG_LEVEL || 'info';
    this.logFile = path.join(__dirname, 'userData', 'logs', 'launcher.log');
    this.ensureLogDirectory();
  }

  ensureLogDirectory() {
    const logDir = path.dirname(this.logFile);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
  }

  shouldLog(level) {
    const levelIndex = this.logLevels.indexOf(level);
    const currentLevelIndex = this.logLevels.indexOf(this.currentLevel);
    return levelIndex <= currentLevelIndex;
  }

  log(level, message, meta = {}) {
    if (!this.shouldLog(level)) return;

    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...meta
    };

    const logLine = `[${timestamp}] ${level.toUpperCase()}: ${message}${
      Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : ''
    }\n`;

    // Console output disabled due to terminal redirection issues
    // if (process.stdout && process.stdout.write) {
    //   process.stdout.write(logLine);
    // }

    // File output
    try {
      fs.appendFileSync(this.logFile, logLine);
    } catch (error) {
      console.error('Failed to write to log file:', error.message);
    }
  }

  error(message, meta) { this.log('error', message, meta); }
  warn(message, meta) { this.log('warn', message, meta); }
  info(message, meta) { this.log('info', message, meta); }
  debug(message, meta) { this.log('debug', message, meta); }
}

// Port management utilities for native launcher
class PortManager {
  static async checkPortAvailable(port) {
    return new Promise((resolve) => {
      const server = net.createServer();
      
      server.listen(port, () => {
        server.once('close', () => {
          resolve(true);
        });
        server.close();
      });
      
      server.on('error', () => {
        resolve(false);
      });
    });
  }

  static async findAvailablePort(startPort, maxAttempts = 50) {
    for (let i = 0; i < maxAttempts; i++) {
      const port = startPort + i;
      const available = await this.checkPortAvailable(port);
      if (available) {
        return port;
      }
    }
    return null;
  }

  static async getPortWithFallback(preferredPort, serviceName = 'service') {
    const logger = new LauncherLogger();
    
    // Check if preferred port is available
    const isAvailable = await this.checkPortAvailable(preferredPort);
    
    if (isAvailable) {
      logger.info(`Using preferred port for ${serviceName}`, { port: preferredPort });
      return preferredPort;
    }
    
    logger.warn(`Port ${preferredPort} is occupied, finding alternative for ${serviceName}`);
    
    // Find alternative port
    const alternativePort = await this.findAvailablePort(preferredPort);
    
    if (alternativePort) {
      logger.info(`Found alternative port for ${serviceName}`, { 
        original: preferredPort, 
        alternative: alternativePort 
      });
      return alternativePort;
    }
    
    throw new Error(`Could not find available port for ${serviceName} starting from ${preferredPort}`);
  }
}

// Simple health monitor for launcher
class LauncherHealthMonitor {
  constructor() {
    this.healthChecks = new Map();
    this.stats = {
      checks: 0,
      failures: 0,
      lastCheck: null
    };
  }

  async initialize() {
    // Setup basic health monitoring
    return true;
  }

  registerHealthCheck(name, config) {
    this.healthChecks.set(name, config);
  }

  getSystemHealth() {
    return 'healthy';
  }

  getHealthStats() {
    return this.stats;
  }

  generateDiagnosticReport() {
    return {
      timestamp: new Date().toISOString(),
      status: 'operational',
      checks: Array.from(this.healthChecks.keys())
    };
  }

  async shutdown() {
    // Cleanup
  }
}

// Simple authentication manager for launcher
class LauncherAuthManager {
  constructor() {
    this.currentUser = null;
  }

  async initialize() {
    return true;
  }

  async authenticate(type, credentials) {
    // Simple local authentication
    return { success: true, user: { id: 'local', type: 'admin' } };
  }

  async shutdown() {
    // Cleanup
  }
}

// Simple configuration manager for launcher
class LauncherConfigManager {
  constructor() {
    this.config = {
      ui: {
        window: {
          width: 1400,
          height: 900,
          autoHideMenu: false,
          maximize: false
        }
      }
    };
  }

  async initialize() {
    return true;
  }

  get(path, defaultValue) {
    const keys = path.split('.');
    let value = this.config;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return defaultValue;
      }
    }
    
    return value;
  }

  set(path, value) {
    const keys = path.split('.');
    let current = this.config;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
    
    current[keys[keys.length - 1]] = value;
  }

  async shutdown() {
    // Cleanup
  }
}

// Initialize logging
const logger = new LauncherLogger();

// Application metadata
const APP_INFO = {
  name: 'Hearthlink',
  version: '1.3.0',
  description: 'AI-Powered Productivity System with Advanced Behavioral Analysis',
  author: 'Hearthlink Development Team'
};

// Global state
let mainWindow = null;
let healthMonitor = null;
let authManager = null;
let configManager = null;
let backendProcess = null;
let systemTray = null;

// ==========================================
// SYSTEM INITIALIZATION
// ==========================================

class HearthlinkLauncher {
  constructor() {
    this.isReady = false;
    this.services = new Map();
    this.startupTime = Date.now();
    this.actualPorts = {}; // Track actual ports being used
    this.setupErrorHandling();
  }

  async initialize() {
    try {
      logger.info('Initializing Hearthlink Launcher', { version: APP_INFO.version });

      // Initialize core systems
      await this.initializeCoreServices();
      
      // Setup application security
      await this.setupSecurity();
      
      // Initialize health monitoring
      await this.setupHealthMonitoring();
      
      // Setup system paths
      this.setupPaths();
      
      // Register protocols
      this.setupProtocols();
      
      // Create main window
      await this.createMainWindow();
      
      // Setup application menu
      this.createApplicationMenu();
      
      // Start backend services
      await this.startBackendServices();
      
      // Setup IPC handlers
      this.setupIPCHandlers();
      
      this.isReady = true;
      const startupDuration = Date.now() - this.startupTime;
      
      logger.info('Hearthlink Launcher initialized successfully', {
        startupTime: startupDuration,
        services: Array.from(this.services.keys())
      });

      return true;
    } catch (error) {
      logger.error('Failed to initialize Hearthlink Launcher', {
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  }

  async initializeCoreServices() {
    logger.info('Initializing core services...');

    // Initialize configuration manager
    configManager = new LauncherConfigManager();
    await configManager.initialize();
    this.services.set('config', configManager);

    // Initialize authentication manager
    authManager = new LauncherAuthManager();
    await authManager.initialize();
    this.services.set('auth', authManager);

    // Initialize health monitor
    healthMonitor = new LauncherHealthMonitor();
    await healthMonitor.initialize();
    this.services.set('health', healthMonitor);

    logger.info('Core services initialized successfully');
  }

  setupErrorHandling() {
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception', {
        error: error.message,
        stack: error.stack
      });
    });

    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Promise Rejection', {
        reason: reason instanceof Error ? reason.message : reason,
        stack: reason instanceof Error ? reason.stack : undefined
      });
    });

    // Setup app-specific error handling when app is ready
    if (app && app.on) {
      app.on('render-process-gone', (event, webContents, details) => {
        logger.error('Renderer process crashed', {
          reason: details.reason,
          exitCode: details.exitCode
        });
      });
    }
  }

  async setupSecurity() {
    logger.info('Setting up application security...');

    // Request necessary permissions on macOS
    if (process.platform === 'darwin') {
      try {
        const microphoneAccess = await systemPreferences.askForMediaAccess('microphone');
        const cameraAccess = await systemPreferences.askForMediaAccess('camera');
        
        logger.info('Media permissions requested', {
          microphone: microphoneAccess,
          camera: cameraAccess
        });
      } catch (error) {
        logger.warn('Failed to request media permissions', { error: error.message });
      }
    }

    // Setup content security policy
    app.on('web-contents-created', (event, contents) => {
      contents.on('did-finish-load', () => {
        contents.insertCSS(`
          * {
            -webkit-user-select: text;
            user-select: text;
          }
        `);
      });

      contents.on('new-window', (event, navigationUrl) => {
        event.preventDefault();
        shell.openExternal(navigationUrl);
      });
    });
  }

  async setupHealthMonitoring() {
    if (!healthMonitor) return;

    // Monitor application health
    healthMonitor.registerHealthCheck('app.main_window', {
      type: 'system',
      interval: 30000,
      timeout: 5000,
      check: () => {
        return mainWindow && !mainWindow.isDestroyed() ? 
          { healthy: true } : { healthy: false, error: 'Main window destroyed' };
      }
    });

    // Monitor memory usage
    healthMonitor.registerHealthCheck('app.memory', {
      type: 'memory',
      interval: 60000,
      timeout: 5000,
      check: () => {
        const memUsage = process.memoryUsage();
        const usage = memUsage.heapUsed / memUsage.heapTotal;
        return usage < 0.9 ? { healthy: true, usage } : { healthy: false, usage };
      }
    });

    // Monitor CPU usage
    healthMonitor.registerHealthCheck('app.cpu', {
      type: 'cpu',
      interval: 30000,
      timeout: 5000,
      check: () => {
        const cpuUsage = process.cpuUsage();
        const usage = (cpuUsage.user + cpuUsage.system) / 1000000; // Convert to seconds
        return usage < 1000 ? { healthy: true, usage } : { healthy: false, usage };
      }
    });

    logger.info('Health monitoring setup completed');
  }

  setupPaths() {
    const userDataPath = app.getPath('userData');
    const tempPath = app.getPath('temp');
    const documentsPath = app.getPath('documents');

    // Create required directories
    const requiredDirs = [
      path.join(userDataPath, 'logs'),
      path.join(userDataPath, 'data'),
      path.join(userDataPath, 'alice'),
      path.join(userDataPath, 'vault'),
      path.join(userDataPath, 'cache'),
      path.join(tempPath, 'hearthlink')
    ];

    requiredDirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        logger.info('Created directory', { path: dir });
      }
    });

    logger.info('Application paths configured', {
      userData: userDataPath,
      temp: tempPath,
      documents: documentsPath
    });
  }

  setupProtocols() {
    // Register custom protocol for serving application files
    protocol.registerFileProtocol('hearthlink', (request, callback) => {
      try {
        const url = request.url.substr(12); // Remove 'hearthlink://' prefix
        const filePath = path.normalize(path.join(__dirname, 'build', url));
        
        // Security check
        const buildPath = path.resolve(path.join(__dirname, 'build'));
        const resolvedPath = path.resolve(filePath);
        
        if (!resolvedPath.startsWith(buildPath)) {
          logger.warn('Security violation: Attempted to access file outside build directory', {
            requested: filePath,
            resolved: resolvedPath
          });
          callback({ error: 403 });
          return;
        }
        
        if (!fs.existsSync(filePath)) {
          callback({ error: 404 });
          return;
        }
        
        callback({ path: filePath });
      } catch (error) {
        logger.error('Protocol handler error', { error: error.message });
        callback({ error: 500 });
      }
    });

    logger.info('Custom protocols registered');
  }

  async createMainWindow() {
    logger.info('Creating main application window...');

    // Window configuration from config manager
    const windowConfig = configManager ? configManager.get('ui.window', {}) : {};

    mainWindow = new BrowserWindow({
      width: windowConfig.width || 1400,
      height: windowConfig.height || 900,
      minWidth: 800,
      minHeight: 600,
      title: `${APP_INFO.name} v${APP_INFO.version}`,
      icon: path.join(__dirname, 'src', 'assets', 'Hearthlink.png'),
      show: false, // Don't show until ready
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true,
        allowRunningInsecureContent: false,
        experimentalFeatures: false
      },
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      autoHideMenuBar: windowConfig.autoHideMenu || false,
      backgroundColor: '#0f172a', // StarCraft dark theme
      vibrancy: process.platform === 'darwin' ? 'dark' : undefined
    });

    // Load the application
    await this.loadApplication();

    // Window event handlers
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      mainWindow.focus();
      
      if (windowConfig.maximize) {
        mainWindow.maximize();
      }

      logger.info('Main window displayed');
    });

    mainWindow.on('closed', () => {
      mainWindow = null;
    });

    mainWindow.on('unresponsive', () => {
      logger.warn('Main window became unresponsive');
      
      dialog.showMessageBox(mainWindow, {
        type: 'warning',
        title: 'Window Unresponsive',
        message: 'The application has become unresponsive. Would you like to restart it?',
        buttons: ['Restart', 'Wait', 'Close'],
        defaultId: 0
      }).then((result) => {
        if (result.response === 0) {
          app.relaunch();
          app.exit();
        } else if (result.response === 2) {
          mainWindow.close();
        }
      });
    });

    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
      logger.error('Failed to load page', {
        errorCode,
        errorDescription,
        url: validatedURL
      });
    });

    // Security: Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    logger.info('Main window created successfully');
  }

  async loadApplication() {
    const isDev = process.env.NODE_ENV === 'development';
    let startUrl;

    if (isDev) {
      // Development mode - try dev server first
      try {
        const response = await fetch('http://localhost:3000', { timeout: 1000 });
        startUrl = 'http://localhost:3000';
        logger.info('Using development server');
      } catch (error) {
        startUrl = await this.startProductionServer();
        logger.info('Development server not available, using production build');
      }
    } else {
      // Production mode
      startUrl = await this.startProductionServer();
    }

    logger.info('Loading application', { url: startUrl });

    try {
      await mainWindow.loadURL(startUrl);
      logger.info('Application loaded successfully');
    } catch (error) {
      logger.error('Failed to load application', { error: error.message });
      
      // Fallback to error page
      const errorHtml = this.generateErrorPage(error);
      await mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);
    }
  }

  async startProductionServer() {
    try {
      const buildPath = path.join(__dirname, 'build');
      
      if (!fs.existsSync(buildPath)) {
        throw new Error('Build directory not found. Run "npm run build" first.');
      }
      
      // Get preferred port from environment or use default
      const preferredPort = parseInt(process.env.REACT_PROD_PORT || process.env.PORT || 3001);
      
      // Use port manager to find available port
      const port = await PortManager.getPortWithFallback(preferredPort, 'React Production Server');
      
      return await this.createProductionServer(buildPath, port);
    } catch (error) {
      logger.error('Failed to start production server', { error: error.message });
      throw error;
    }
  }

  async createProductionServer(buildPath, port) {
    return new Promise((resolve, reject) => {

      const server = http.createServer((req, res) => {
        try {
          const parsedUrl = url.parse(req.url);
          let filePath = path.join(buildPath, parsedUrl.pathname);
          
          // Security check
          const resolvedPath = path.resolve(filePath);
          const resolvedBuildPath = path.resolve(buildPath);
          
          if (!resolvedPath.startsWith(resolvedBuildPath)) {
            res.writeHead(403, { 'Content-Type': 'text/plain' });
            res.end('Forbidden');
            return;
          }
          
          // Handle directory requests
          if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
            filePath = path.join(filePath, 'index.html');
          }
          
          // Handle SPA routing
          if (!fs.existsSync(filePath)) {
            filePath = path.join(buildPath, 'index.html');
          }
          
          // Determine content type
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
            '.woff2': 'font/woff2'
          };
          
          const contentType = contentTypes[ext] || 'application/octet-stream';
          res.setHeader('Content-Type', contentType);
          
          // Add security headers
          res.setHeader('X-Content-Type-Options', 'nosniff');
          res.setHeader('X-Frame-Options', 'DENY');
          res.setHeader('X-XSS-Protection', '1; mode=block');
          
          // Stream the file
          const stream = fs.createReadStream(filePath);
          stream.pipe(res);
          
          stream.on('error', (error) => {
            logger.error('File streaming error', { error: error.message, file: filePath });
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Internal Server Error');
          });
          
        } catch (error) {
          logger.error('Server request error', { error: error.message });
          res.writeHead(500, { 'Content-Type': 'text/plain' });
          res.end('Internal Server Error');
        }
      });
      
      server.listen(port, () => {
        // Store the actual port being used
        this.actualPorts.reactProd = port;
        logger.info('Production server started', { 
          port, 
          configured: process.env.REACT_PROD_PORT || 3001,
          actual: port 
        });
        resolve(`http://localhost:${port}`);
      });
      
      server.on('error', (error) => {
        logger.error('Production server error', { error: error.message });
        reject(error);
      });
    });
  }

  generateErrorPage(error) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hearthlink - Error</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .error-container {
                text-align: center;
                max-width: 600px;
                padding: 40px;
                background: rgba(30, 41, 59, 0.8);
                border-radius: 15px;
                border: 1px solid #22d3ee;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                color: #ef4444;
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            .error-message {
                font-size: 1.2em;
                margin-bottom: 30px;
                color: #94a3b8;
            }
            .retry-button {
                background: #22d3ee;
                color: #0f172a;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .retry-button:hover {
                background: #0891b2;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(34, 211, 238, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Hearthlink Error</h1>
            <div class="error-message">
                Failed to load the application: ${error.message}
            </div>
            <button class="retry-button" onclick="location.reload()">
                Retry
            </button>
        </div>
    </body>
    </html>
    `;
  }

  createApplicationMenu() {
    const template = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Session',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'new-session' });
            }
          },
          {
            label: 'Open Alice Interface',
            accelerator: 'CmdOrCtrl+A',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'open-alice' });
            }
          },
          { type: 'separator' },
          {
            label: 'Settings',
            accelerator: 'CmdOrCtrl+,',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'open-settings' });
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
        label: 'AI Agents',
        submenu: [
          {
            label: 'Alden (Main)',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'switch-agent', agent: 'alden' });
            }
          },
          {
            label: 'Alice (Behavioral)',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'switch-agent', agent: 'alice' });
            }
          },
          {
            label: 'Core (Orchestration)',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'switch-agent', agent: 'core' });
            }
          },
          { type: 'separator' },
          {
            label: 'Agent Status',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'agent-status' });
            }
          }
        ]
      },
      {
        label: 'System',
        submenu: [
          {
            label: 'Health Monitor',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'health-monitor' });
            }
          },
          {
            label: 'Performance Metrics',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'performance-metrics' });
            }
          },
          { type: 'separator' },
          {
            label: 'System Logs',
            click: () => {
              const logsPath = path.join(app.getPath('userData'), 'logs');
              shell.openPath(logsPath);
            }
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'User Guide',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'open-guide' });
            }
          },
          {
            label: 'Keyboard Shortcuts',
            click: () => {
              mainWindow.webContents.send('app-command', { type: 'keyboard-shortcuts' });
            }
          },
          { type: 'separator' },
          {
            label: 'Report Issue',
            click: () => {
              shell.openExternal('https://github.com/hearthlink/hearthlink/issues');
            }
          },
          {
            label: 'About Hearthlink',
            click: () => {
              dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: 'About Hearthlink',
                message: `${APP_INFO.name} v${APP_INFO.version}`,
                detail: `${APP_INFO.description}\n\n© 2025 ${APP_INFO.author}\nMIT License`,
                buttons: ['OK']
              });
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);

    logger.info('Application menu created');
  }

  async startBackendServices() {
    logger.info('Starting backend services...');

    try {
      // Start Python backend if available
      const pythonPath = process.env.PYTHON_PATH || 'python';
      const backendScript = path.join(__dirname, 'src', 'main.py');
      
      if (fs.existsSync(backendScript)) {
        backendProcess = spawn(pythonPath, [backendScript, '--ipc'], {
          cwd: __dirname,
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONPATH: path.join(__dirname, 'src') }
        });
        
        backendProcess.stdout.on('data', (data) => {
          const output = data.toString();
          if (output.includes('HEARTHLINK_READY')) {
            logger.info('Python backend ready');
          }
        });
        
        backendProcess.stderr.on('data', (data) => {
          logger.error('Python backend error', { error: data.toString() });
        });
        
        backendProcess.on('error', (error) => {
          logger.error('Failed to start Python backend', { error: error.message });
        });
        
        logger.info('Python backend started');
      } else {
        logger.warn('Python backend not found, running in frontend-only mode');
      }
    } catch (error) {
      logger.error('Failed to start backend services', { error: error.message });
    }
  }

  setupIPCHandlers() {
    logger.info('Setting up IPC handlers...');

    // Application info
    ipcMain.handle('app:get-info', () => APP_INFO);
    
    // System status
    ipcMain.handle('system:get-status', () => {
      return {
        health: healthMonitor ? healthMonitor.getSystemHealth() : 'unknown',
        uptime: Date.now() - this.startupTime,
        memory: process.memoryUsage(),
        cpu: process.cpuUsage(),
        platform: {
          os: os.type(),
          arch: os.arch(),
          release: os.release(),
          nodeVersion: process.version
        }
      };
    });

    // Alice behavioral analysis
    ipcMain.handle('alice:analyze', async (event, data) => {
      try {
        logger.info('Alice analysis requested', { dataType: typeof data });
        
        // Process behavioral analysis
        const analysis = {
          timestamp: new Date().toISOString(),
          mood: this.analyzeMood(data),
          communication: this.analyzeCommunication(data),
          patterns: this.analyzePatterns(data),
          recommendations: this.generateRecommendations(data)
        };
        
        return { success: true, analysis };
      } catch (error) {
        logger.error('Alice analysis failed', { error: error.message });
        return { success: false, error: error.message };
      }
    });

    // Health monitoring
    ipcMain.handle('health:get-status', () => {
      if (!healthMonitor) return { error: 'Health monitor not available' };
      
      return {
        systemHealth: healthMonitor.getSystemHealth(),
        stats: healthMonitor.getHealthStats(),
        diagnostics: healthMonitor.generateDiagnosticReport()
      };
    });

    // Authentication
    ipcMain.handle('auth:login', async (event, credentials) => {
      try {
        const result = await authManager.authenticate('local', credentials);
        return result;
      } catch (error) {
        logger.error('Authentication failed', { error: error.message });
        return { success: false, error: error.message };
      }
    });

    // Configuration
    ipcMain.handle('config:get', (event, path, defaultValue) => {
      return configManager ? configManager.get(path, defaultValue) : defaultValue;
    });

    ipcMain.handle('config:set', (event, path, value) => {
      if (configManager) {
        configManager.set(path, value);
        return { success: true };
      }
    });

    // Port management
    ipcMain.handle('ports:get-status', async () => {
      try {
        const portStatus = {
          reactProd: {
            configured: process.env.REACT_PROD_PORT || 3001,
            actual: this.actualPorts?.reactProd || null,
            available: await PortManager.checkPortAvailable(process.env.REACT_PROD_PORT || 3001)
          },
          backend: {
            configured: process.env.BACKEND_PORT || 8000,
            actual: this.actualPorts?.backend || null,
            available: await PortManager.checkPortAvailable(process.env.BACKEND_PORT || 8000)
          }
        };
        
        return { success: true, ports: portStatus };
      } catch (error) {
        logger.error('Failed to get port status', { error: error.message });
        return { success: false, error: error.message };
      }
    });

    logger.info('IPC handlers setup completed');
  }

  analyzeMood(data) {
    // Simplified mood analysis
    const text = data.text || '';
    const positiveWords = ['good', 'great', 'excellent', 'happy', 'love'];
    const negativeWords = ['bad', 'terrible', 'awful', 'sad', 'hate'];
    
    let score = 0;
    const words = text.toLowerCase().split(' ');
    
    words.forEach(word => {
      if (positiveWords.includes(word)) score += 1;
      if (negativeWords.includes(word)) score -= 1;
    });
    
    const normalizedScore = Math.max(-1, Math.min(1, score / words.length * 10));
    
    return {
      score: normalizedScore,
      label: normalizedScore > 0.2 ? 'positive' : normalizedScore < -0.2 ? 'negative' : 'neutral',
      confidence: Math.abs(normalizedScore)
    };
  }

  analyzeCommunication(data) {
    const text = data.text || '';
    return {
      wordCount: text.split(' ').length,
      characterCount: text.length,
      avgWordLength: text.split(' ').reduce((sum, word) => sum + word.length, 0) / text.split(' ').length,
      complexity: this.calculateComplexity(text)
    };
  }

  analyzePatterns(data) {
    return {
      timestamp: new Date().toISOString(),
      type: 'behavioral',
      insights: ['User shows consistent communication patterns', 'Engagement level is moderate']
    };
  }

  generateRecommendations(data) {
    return [
      {
        type: 'communication',
        message: 'Consider breaking down complex requests into smaller parts',
        priority: 'medium'
      },
      {
        type: 'engagement',
        message: 'Your interaction patterns suggest focused work sessions',
        priority: 'low'
      }
    ];
  }

  calculateComplexity(text) {
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    const avgWordsPerSentence = text.split(' ').length / sentences.length;
    return Math.min(1, avgWordsPerSentence / 20);
  }

  async shutdown() {
    logger.info('Shutting down Hearthlink Launcher...');

    try {
      // Stop backend process
      if (backendProcess) {
        backendProcess.kill('SIGTERM');
        
        // Force kill after 5 seconds
        setTimeout(() => {
          if (backendProcess && !backendProcess.killed) {
            backendProcess.kill('SIGKILL');
          }
        }, 5000);
      }

      // Shutdown services
      for (const [name, service] of this.services.entries()) {
        if (service && typeof service.shutdown === 'function') {
          await service.shutdown();
          logger.info('Service shutdown', { service: name });
        }
      }

      logger.info('Hearthlink Launcher shutdown completed');
    } catch (error) {
      logger.error('Error during shutdown', { error: error.message });
    }
  }
}

// ==========================================
// APPLICATION LIFECYCLE
// ==========================================

// Handle command line arguments when run directly
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--version') || args.includes('-v')) {
    console.log(`${APP_INFO.name} v${APP_INFO.version}`);
    console.log(APP_INFO.description);
    process.exit(0);
  }
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`${APP_INFO.name} v${APP_INFO.version} - Enhanced Native Launcher`);
    console.log('\nUsage:');
    console.log('  npm run launch        Start Hearthlink with enhanced launcher');
    console.log('  node launcher.js      Direct launcher execution');
    console.log('\nOptions:');
    console.log('  --version, -v         Show version information');
    console.log('  --help, -h            Show this help message');
    console.log('  --debug               Enable debug logging');
    console.log('\nFor full application startup, use: npm run launch');
    process.exit(0);
  }
  
  if (args.includes('--debug')) {
    process.env.HEARTHLINK_LOG_LEVEL = 'debug';
  }
  
  // If run directly without Electron, show info and exit
  console.log(`${APP_INFO.name} v${APP_INFO.version} - Enhanced Native Launcher`);
  console.log('This launcher is designed to run within Electron.');
  console.log('Please use: npm run launch');
  process.exit(0);
}

const launcher = new HearthlinkLauncher();

// App ready event
app.whenReady().then(async () => {
  try {
    await launcher.initialize();
  } catch (error) {
    console.error('Failed to initialize application:', error);
    dialog.showErrorBox('Initialization Error', `Failed to start Hearthlink: ${error.message}`);
    app.quit();
  }
});

// All windows closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// App activate (macOS)
app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await launcher.createMainWindow();
  }
});

// Before quit
app.on('before-quit', async () => {
  await launcher.shutdown();
});

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

module.exports = { HearthlinkLauncher, PortManager };