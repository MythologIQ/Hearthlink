// Mock implementation of Electron for testing

const mockIpcMain = {
  handle: jest.fn(),
  on: jest.fn(),
  removeHandler: jest.fn(),
  removeAllListeners: jest.fn()
};

const mockIpcRenderer = {
  invoke: jest.fn(),
  on: jest.fn(),
  removeAllListeners: jest.fn(),
  send: jest.fn()
};

const mockBrowserWindow = jest.fn().mockImplementation(() => ({
  loadURL: jest.fn().mockResolvedValue(),
  loadFile: jest.fn().mockResolvedValue(),
  once: jest.fn(),
  on: jest.fn(),
  show: jest.fn(),
  hide: jest.fn(),
  close: jest.fn(),
  focus: jest.fn(),
  webContents: {
    openDevTools: jest.fn(),
    send: jest.fn(),
    on: jest.fn()
  }
}));

const mockApp = {
  whenReady: jest.fn().mockResolvedValue(),
  on: jest.fn(),
  quit: jest.fn(),
  getPath: jest.fn().mockReturnValue('/mock/path'),
  setPath: jest.fn(),
  isPackaged: false,
  getVersion: jest.fn().mockReturnValue('1.0.0'),
  getAppPath: jest.fn().mockReturnValue('/mock/app/path'),
  setAsDefaultProtocolClient: jest.fn()
};

const mockMenu = {
  buildFromTemplate: jest.fn().mockReturnValue({}),
  setApplicationMenu: jest.fn()
};

const mockShell = {
  openExternal: jest.fn().mockResolvedValue()
};

const mockDialog = {
  showMessageBox: jest.fn().mockResolvedValue({ response: 0 }),
  showOpenDialog: jest.fn().mockResolvedValue({ 
    canceled: false, 
    filePaths: ['/mock/file/path'] 
  }),
  showSaveDialog: jest.fn().mockResolvedValue({ 
    canceled: false, 
    filePath: '/mock/save/path' 
  })
};

const mockProtocol = {
  registerFileProtocol: jest.fn(),
  registerHttpProtocol: jest.fn(),
  registerStringProtocol: jest.fn(),
  registerBufferProtocol: jest.fn(),
  registerStreamProtocol: jest.fn(),
  unregisterProtocol: jest.fn(),
  isProtocolRegistered: jest.fn().mockReturnValue(false)
};

const mockContextBridge = {
  exposeInMainWorld: jest.fn()
};

const mockNotification = jest.fn().mockImplementation((options) => ({
  show: jest.fn(),
  close: jest.fn(),
  on: jest.fn(),
  ...options
}));

// Export all mocked modules
module.exports = {
  ipcMain: mockIpcMain,
  ipcRenderer: mockIpcRenderer,
  BrowserWindow: mockBrowserWindow,
  app: mockApp,
  Menu: mockMenu,
  shell: mockShell,
  dialog: mockDialog,
  protocol: mockProtocol,
  contextBridge: mockContextBridge,
  Notification: mockNotification
};

// Also export individual components for named imports
module.exports.ipcMain = mockIpcMain;
module.exports.ipcRenderer = mockIpcRenderer;
module.exports.BrowserWindow = mockBrowserWindow;
module.exports.app = mockApp;
module.exports.Menu = mockMenu;
module.exports.shell = mockShell;
module.exports.dialog = mockDialog;
module.exports.protocol = mockProtocol;
module.exports.contextBridge = mockContextBridge;
module.exports.Notification = mockNotification;