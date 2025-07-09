const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    icon: path.join(__dirname, 'assets', 'icon.ico'),
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

  // Load the app
  const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, 'build', 'index.html')}`;
  mainWindow.loadURL(startUrl);

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
app.whenReady().then(() => {
  createWindow();
  createMenu();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent navigation to external URLs
app.on('web-contents-created', (event, contents) => {
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    if (parsedUrl.origin !== 'file://') {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
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

// Handle voice command requests
ipcMain.handle('voice-command', (event, command) => {
  // Process voice commands here
  console.log('Voice command received:', command);
  
  // Send response back to renderer
  mainWindow.webContents.send('voice-command-response', {
    command: command,
    success: true,
    response: `Processed: ${command}`
  });
});

// Handle accessibility features
ipcMain.handle('accessibility-toggle', (event, feature) => {
  console.log('Accessibility feature toggled:', feature);
  
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

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  
  dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
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