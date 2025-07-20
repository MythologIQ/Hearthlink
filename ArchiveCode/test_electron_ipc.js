#!/usr/bin/env node

/**
 * Simple test to verify Electron IPC bridge works
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');

// Basic window for testing
function createTestWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load a basic HTML page
  win.loadFile('test_page.html');
  
  // Open DevTools for testing
  win.webContents.openDevTools();
  
  console.log('Test window created - you can now test the IPC bridge');
  console.log('Check the DevTools console for window.electronAPI availability');
}

app.whenReady().then(() => {
  createTestWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createTestWindow();
  }
});