/**
 * Startup Settings Component
 * 
 * Provides UI controls for configuring Hearthlink's startup behavior,
 * including auto-launch and Claude Code CLI integration.
 */

import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { Power, Settings, CheckCircle, AlertCircle } from 'lucide-react';
import { useTauriIntegration } from '../hooks/useTauriIntegration';

interface StartupSettingsProps {
  className?: string;
}

export const StartupSettings: React.FC<StartupSettingsProps> = ({ 
  className = '' 
}) => {
  const { isDesktopApp, showNotification } = useTauriIntegration();
  const [isStartupEnabled, setIsStartupEnabled] = useState(false);
  const [isClaudeCodeRunning, setIsClaudeCodeRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isDesktopApp) return;

    // Check if startup is already enabled
    const checkStartupStatus = async () => {
      try {
        const enabled = await invoke<boolean>('check_startup_enabled');
        setIsStartupEnabled(enabled);
      } catch (err) {
        console.error('Failed to check startup status:', err);
      }
    };

    checkStartupStatus();
  }, [isDesktopApp]);

  const handleToggleStartup = async () => {
    if (!isDesktopApp) return;

    setLoading(true);
    setError(null);

    try {
      if (isStartupEnabled) {
        const result = await invoke<string>('disable_startup_launch');
        setIsStartupEnabled(false);
        await showNotification('Startup Disabled', result);
      } else {
        const result = await invoke<string>('enable_startup_launch');
        setIsStartupEnabled(true);
        await showNotification('Startup Enabled', result);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      console.error('Failed to toggle startup:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLaunchClaudeCode = async () => {
    if (!isDesktopApp) return;

    setLoading(true);
    setError(null);

    try {
      const result = await invoke<string>('launch_claude_code_silent');
      setIsClaudeCodeRunning(true);
      await showNotification('Claude Code Started', result);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      await showNotification('Claude Code Failed', message);
      console.error('Failed to launch Claude Code:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isDesktopApp) {
    return (
      <div className={`${className} bg-gray-800 rounded-lg p-4`}>
        <div className="text-yellow-400 flex items-center gap-2">
          <AlertCircle size={20} />
          <span>Startup settings only available in desktop app</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} bg-gradient-to-br from-purple-900/30 to-blue-900/30 rounded-lg p-6 border border-purple-500/20`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-500/20 rounded-lg">
          <Power className="text-purple-400" size={24} />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Startup Configuration</h3>
          <p className="text-gray-400 text-sm">Configure system startup and support services</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-500/50 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <AlertCircle size={16} />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Startup Settings */}
      <div className="space-y-4">
        {/* Auto-launch Toggle */}
        <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
          <div className="flex items-center gap-3">
            <Settings className="text-blue-400" size={20} />
            <div>
              <div className="text-white font-medium">Launch at Startup</div>
              <div className="text-gray-400 text-sm">
                Automatically start Hearthlink when system boots
              </div>
            </div>
          </div>
          <button
            onClick={handleToggleStartup}
            disabled={loading}
            className={`
              relative w-12 h-6 rounded-full transition-colors duration-200
              ${isStartupEnabled ? 'bg-green-500' : 'bg-gray-600'}
              ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div
              className={`
                absolute top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200
                ${isStartupEnabled ? 'transform translate-x-7' : 'transform translate-x-1'}
              `}
            />
          </button>
        </div>

        {/* Claude Code Support */}
        <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
          <div className="flex items-center gap-3">
            <div className={`p-1 rounded ${isClaudeCodeRunning ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
              <CheckCircle 
                className={isClaudeCodeRunning ? 'text-green-400' : 'text-gray-400'} 
                size={20} 
              />
            </div>
            <div>
              <div className="text-white font-medium">Claude Code CLI Support</div>
              <div className="text-gray-400 text-sm">
                Silent background process for Synapse forwarding
              </div>
            </div>
          </div>
          <button
            onClick={handleLaunchClaudeCode}
            disabled={loading || isClaudeCodeRunning}
            className={`
              px-4 py-2 rounded-lg font-medium transition-colors
              ${isClaudeCodeRunning 
                ? 'bg-green-500/20 text-green-400 cursor-not-allowed' 
                : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
              }
              ${loading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {loading ? 'Starting...' : isClaudeCodeRunning ? 'Running' : 'Start Claude'}
          </button>
        </div>

        {/* Status Information */}
        <div className="mt-6 p-4 bg-gray-900/30 rounded-lg">
          <h4 className="text-white font-medium mb-2">Current Status</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Startup Launch:</span>
              <span className={isStartupEnabled ? 'text-green-400' : 'text-gray-400'}>
                {isStartupEnabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Claude Code CLI:</span>
              <span className={isClaudeCodeRunning ? 'text-green-400' : 'text-gray-400'}>
                {isClaudeCodeRunning ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* Help Text */}
        <div className="text-xs text-gray-500 leading-relaxed">
          <p className="mb-2">
            <strong>Auto-launch:</strong> When enabled, Hearthlink will start automatically when your system boots. 
            The application will launch minimized to the system tray.
          </p>
          <p>
            <strong>Claude Code CLI:</strong> Launches Claude Code in background mode to enable Synapse to forward 
            prompts and capture responses. This provides seamless integration with your Claude Code workflow.
          </p>
        </div>
      </div>
    </div>
  );
};

export default StartupSettings;