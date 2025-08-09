export {}
// electron/main.ts
import { app, BrowserWindow } from 'electron'
import path from 'path'
import { registerProtocolHandler } from '../services/protocolHandler'

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  // Always load development server for now until production build is fixed
  win.loadURL('http://localhost:3015')
  
  // Only open DevTools if explicitly requested
  if (process.env.DEBUG === 'true') {
    win.webContents.openDevTools()
  }
}

app.whenReady().then(() => {
  registerProtocolHandler()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
export {}
