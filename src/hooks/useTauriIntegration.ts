/**
 * Tauri Integration Hook
 * 
 * Provides seamless integration with Tauri's native desktop APIs while
 * maintaining the immersive Hearthlink UI experience.
 */

import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { emit, listen } from '@tauri-apps/api/event';
import { sendNotification } from '@tauri-apps/api/notification';

interface TauriState {
  isNativeApp: boolean;
  isDevConsoleOpen: boolean;
  systemInfo: Record<string, string>;
  canMinimizeToTray: boolean;
}

interface TauriIntegration {
  // State
  state: TauriState;
  
  // Window management
  minimizeToTray: () => Promise<void>;
  setAlwaysOnTop: (onTop: boolean) => Promise<void>;
  toggleDevConsole: () => void;
  
  // File operations
  writeSecureFile: (path: string, content: string) => Promise<string>;
  readSecureFile: (path: string) => Promise<string>;
  
  // Notifications
  showNotification: (title: string, body: string) => Promise<void>;
  
  // Services
  restartServices: () => void;
  
  // Startup management
  enableStartupLaunch: () => Promise<string>;
  disableStartupLaunch: () => Promise<string>;
  checkStartupEnabled: () => Promise<boolean>;
  launchClaudeCodeSilent: () => Promise<string>;
  
  // Utilities
  isDesktopApp: boolean;
}

export function useTauriIntegration(): TauriIntegration {
  const [state, setState] = useState<TauriState>({
    isNativeApp: false,
    isDevConsoleOpen: false,
    systemInfo: {},
    canMinimizeToTray: false
  });

  const isDesktopApp = typeof window !== 'undefined' && '__TAURI__' in window;

  useEffect(() => {
    if (!isDesktopApp) return;

    const initializeTauri = async () => {
      try {
        // Get system info
        const systemInfo = await invoke<Record<string, string>>('get_system_info');
        
        // Get current app state
        const appState = await invoke<any>('get_app_state');
        
        setState(prev => ({
          ...prev,
          isNativeApp: true,
          systemInfo,
          isDevConsoleOpen: appState.is_dev_console_open,
          canMinimizeToTray: true
        }));

        // console.log('🖥️ Tauri integration initialized', { systemInfo });
      } catch (error) {
        console.error('Failed to initialize Tauri:', error);
      }
    };

    // Listen for Tauri events
    const setupEventListeners = async () => {
      // Service restart event
      const unlistenRestart = await listen('restart-services', () => {
        // console.log('🔄 Service restart requested from native menu');
        restartServices();
      });

      // Dev console events
      const unlistenDevConsole = await listen('close-dev-console', () => {
        setState(prev => ({ ...prev, isDevConsoleOpen: false }));
      });

      const unlistenShowDevConsole = await listen('show-dev-console', () => {
        setState(prev => ({ ...prev, isDevConsoleOpen: true }));
      });

      return () => {
        unlistenRestart();
        unlistenDevConsole();
        unlistenShowDevConsole();
      };
    };

    initializeTauri();
    setupEventListeners();
  }, [isDesktopApp]);

  const minimizeToTray = useCallback(async () => {
    if (!isDesktopApp) return;
    
    try {
      await invoke('minimize_to_tray');
      // console.log('🫥 Minimized to system tray');
    } catch (error) {
      console.error('Failed to minimize to tray:', error);
    }
  }, [isDesktopApp]);

  const setAlwaysOnTop = useCallback(async (onTop: boolean) => {
    if (!isDesktopApp) return;
    
    try {
      await invoke('set_always_on_top', { onTop });
      // console.log(`📌 Always on top: ${onTop}`);
    } catch (error) {
      console.error('Failed to set always on top:', error);
    }
  }, [isDesktopApp]);

  const toggleDevConsole = useCallback(() => {
    if (!isDesktopApp) return;
    
    // F12 hotkey is handled natively by Tauri
    // This function is for programmatic toggling
    setState(prev => ({
      ...prev,
      isDevConsoleOpen: !prev.isDevConsoleOpen
    }));
    
    // console.log(`🔧 Dev console ${state.isDevConsoleOpen ? 'closed' : 'opened'}`);
  }, [isDesktopApp, state.isDevConsoleOpen]);

  const writeSecureFile = useCallback(async (path: string, content: string): Promise<string> => {
    if (!isDesktopApp) {
      throw new Error('File operations only available in desktop app');
    }
    
    try {
      const fullPath = await invoke<string>('write_secure_file', { path, content });
      // console.log(`💾 File written: ${fullPath}`);
      return fullPath;
    } catch (error) {
      console.error('Failed to write file:', error);
      throw error;
    }
  }, [isDesktopApp]);

  const readSecureFile = useCallback(async (path: string): Promise<string> => {
    if (!isDesktopApp) {
      throw new Error('File operations only available in desktop app');
    }
    
    try {
      const content = await invoke<string>('read_secure_file', { path });
      // console.log(`📖 File read: ${path}`);
      return content;
    } catch (error) {
      console.error('Failed to read file:', error);
      throw error;
    }
  }, [isDesktopApp]);

  const showNotification = useCallback(async (title: string, body: string) => {
    if (!isDesktopApp) {
      // Fallback to browser notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body });
      }
      return;
    }
    
    try {
      await invoke('show_notification', { title, body });
      // console.log(`🔔 Notification shown: ${title}`);
    } catch (error) {
      console.error('Failed to show notification:', error);
      // Fallback to Tauri's notification API
      await sendNotification({ title, body });
    }
  }, [isDesktopApp]);

  const restartServices = useCallback(() => {
    // console.log('🔄 Restarting Hearthlink services...');
    
    // Emit event to service components
    if (isDesktopApp) {
      emit('hearthlink-restart-services', {});
    }
    
    // Show user feedback
    showNotification('Hearthlink Services', 'Restarting Claude Gateway and Vault Service...');
    
    // In a real implementation, this would:
    // 1. Stop current Python services
    // 2. Restart run_services.py
    // 3. Verify services are healthy
    // 4. Update UI status
  }, [isDesktopApp, showNotification]);

  const enableStartupLaunch = useCallback(async (): Promise<string> => {
    if (!isDesktopApp) {
      throw new Error('Startup configuration only available in desktop app');
    }
    
    try {
      const result = await invoke<string>('enable_startup_launch');
      // console.log('✅ Startup enabled:', result);
      return result;
    } catch (error) {
      console.error('Failed to enable startup:', error);
      throw error;
    }
  }, [isDesktopApp]);

  const disableStartupLaunch = useCallback(async (): Promise<string> => {
    if (!isDesktopApp) {
      throw new Error('Startup configuration only available in desktop app');
    }
    
    try {
      const result = await invoke<string>('disable_startup_launch');
      // console.log('❌ Startup disabled:', result);
      return result;
    } catch (error) {
      console.error('Failed to disable startup:', error);
      throw error;
    }
  }, [isDesktopApp]);

  const checkStartupEnabled = useCallback(async (): Promise<boolean> => {
    if (!isDesktopApp) {
      return false;
    }
    
    try {
      const enabled = await invoke<boolean>('check_startup_enabled');
      // console.log('🔍 Startup status:', enabled ? 'enabled' : 'disabled');
      return enabled;
    } catch (error) {
      console.error('Failed to check startup status:', error);
      return false;
    }
  }, [isDesktopApp]);

  const launchClaudeCodeSilent = useCallback(async (): Promise<string> => {
    if (!isDesktopApp) {
      throw new Error('Claude Code launch only available in desktop app');
    }
    
    try {
      const result = await invoke<string>('launch_claude_code_silent');
      // console.log('🤖 Claude Code launched:', result);
      return result;
    } catch (error) {
      console.error('Failed to launch Claude Code:', error);
      throw error;
    }
  }, [isDesktopApp]);

  return {
    state,
    minimizeToTray,
    setAlwaysOnTop,
    toggleDevConsole,
    writeSecureFile,
    readSecureFile,
    showNotification,
    restartServices,
    enableStartupLaunch,
    disableStartupLaunch,
    checkStartupEnabled,
    launchClaudeCodeSilent,
    isDesktopApp
  };
}

// Utility function to check if running in Tauri
export function isTauriApp(): boolean {
  return typeof window !== 'undefined' && '__TAURI__' in window;
}

// Custom hook for Tauri-specific file operations
export function useTauriFileSystem() {
  const { writeSecureFile, readSecureFile, isDesktopApp } = useTauriIntegration();
  
  const writeConfig = useCallback(async (config: any): Promise<void> => {
    if (!isDesktopApp) return;
    
    const configContent = JSON.stringify(config, null, 2);
    await writeSecureFile('config/user_settings.json', configContent);
  }, [writeSecureFile, isDesktopApp]);
  
  const readConfig = useCallback(async (): Promise<any> => {
    if (!isDesktopApp) return {};
    
    try {
      const configContent = await readSecureFile('config/user_settings.json');
      return JSON.parse(configContent);
    } catch (error) {
      console.warn('No user config found, using defaults');
      return {};
    }
  }, [readSecureFile, isDesktopApp]);
  
  const writeLog = useCallback(async (logEntry: any): Promise<void> => {
    if (!isDesktopApp) return;
    
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] ${JSON.stringify(logEntry)}\n`;
    
    try {
      // Read existing log
      const existingLog = await readSecureFile('logs/app.log');
      const newLog = existingLog + logLine;
      await writeSecureFile('logs/app.log', newLog);
    } catch (error) {
      // Create new log file
      await writeSecureFile('logs/app.log', logLine);
    }
  }, [writeSecureFile, readSecureFile, isDesktopApp]);
  
  return {
    writeConfig,
    readConfig,
    writeLog,
    isDesktopApp
  };
}

export default useTauriIntegration;