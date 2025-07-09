
import React, { useState, useEffect } from 'react';
import { Panel } from './Panel'; 
import { Container, ContainerStatus } from '../types';
import { Button } from './common/Button';
import { CustomTooltip } from './common/CustomTooltip'; // Import CustomTooltip
import { PlayIcon, StopIcon, TrashIcon, RefreshIcon } from '../constants';
import { useToast } from '../contexts/ToastContext';

interface ContainersPanelProps {
  initialContainers: Container[];
  panelWrapperClassName?: string; 
  onPopoutClick?: () => void;
  isLoading: boolean;
  onRefresh: () => void;
}

const Toggle: React.FC<{ label: string; enabled: boolean; onChange: (enabled: boolean) => void }> = ({ label, enabled, onChange }) => (
    <button
        onClick={() => onChange(!enabled)}
        aria-pressed={enabled}
        className={`px-2.5 py-1 text-xs rounded-md transition-colors
            ${enabled ? 'bg-[var(--brand-accent1)] text-white hover:bg-[var(--brand-accent1-hover)]' : 'bg-[var(--brand-primary-bg-lighter)] text-[var(--brand-text-secondary)] hover:bg-[var(--brand-border)]'}`}
    >
        {label}
    </button>
);

// Safely get the raw environment variable value at the module scope
let moduleLevelImportMetaEnvPanel: Record<string, any> | undefined;
try {
  moduleLevelImportMetaEnvPanel = (import.meta as any).env;
} catch (e) {
  console.error("[ContainersPanel.tsx Module Scope] Error accessing import.meta.env:", e);
  moduleLevelImportMetaEnvPanel = undefined;
}
const GATEKEEPER_PORT_RAW_PANEL = typeof moduleLevelImportMetaEnvPanel !== 'undefined' ? moduleLevelImportMetaEnvPanel.VITE_GATEKEEPER_HTTP_PORT : undefined;

// Helper function to safely get environment variables, similar to App.tsx
function getPanelEnvVariable(rawValue: string | undefined, varName: string, defaultValue: string): string {
  if (typeof moduleLevelImportMetaEnvPanel === 'undefined') { // Check if import.meta.env itself was problematic
    console.warn(
      `[ContainersPanel.tsx] Vite 'import.meta.env' was not accessible at module scope. Defaulting for ${varName}: '${defaultValue}'.`
    );
    return defaultValue;
  }
  if (typeof rawValue === 'string' && rawValue.trim() !== '') {
    return rawValue;
  }
  if (typeof rawValue !== 'undefined') {
     console.warn(
      `[ContainersPanel.tsx] Env var ${varName} from import.meta.env is defined but not a non-empty string (value: ${rawValue}). Defaulting to '${defaultValue}'. Check .env file.`
    );
    return defaultValue;
  }
  console.warn(
    `[ContainersPanel.tsx] Env var ${varName} not defined in .env file. Defaulting to '${defaultValue}'.`
  );
  return defaultValue;
}


export const ContainersPanel: React.FC<ContainersPanelProps> = ({ initialContainers, panelWrapperClassName, onPopoutClick, isLoading, onRefresh }) => {
  const [containers, setContainers] = useState<Container[]>(initialContainers);
  const [saveEnabled, setSaveEnabled] = useState(false);
  const [driEnabled, setDriEnabled] = useState(true);
  const [tasksEnabled, setTasksEnabled] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    setContainers(initialContainers || []); // Ensure containers is always an array
  }, [initialContainers]);

  const GATEKEEPER_PORT = getPanelEnvVariable(GATEKEEPER_PORT_RAW_PANEL, 'VITE_GATEKEEPER_HTTP_PORT', '9341');
  const API_BASE_URL = `http://localhost:${GATEKEEPER_PORT}`;

  const handleAction = async (containerId: string, action: 'start' | 'stop' | 'delete' | 'restart') => {
    const container = containers.find(c => c.id === containerId);
    if (!container) return;

    addToast(`Attempting to ${action} ${container.name}...`, 'info', 2000);
    try {
        const response = await fetch(`${API_BASE_URL}/api/containers/${containerId}/${action}`, { method: 'POST' });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.details || result.error || `Failed to ${action} container.`);
        }
        
        addToast(result.message || `Container ${container.name} ${action}ed successfully.`, 'success');
        onRefresh(); // Refresh container list after action
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        addToast(`Error ${action}ing ${container.name}: ${errorMessage}`, 'error', 7000);
        console.error(`Failed to ${action} container ${containerId}:`, error);
    }
  };


  const headerControlsContent = (
    <div className="flex items-center gap-2">
      <CustomTooltip content="Save current container configuration (mock)." position="bottom">
        <Toggle label="Save" enabled={saveEnabled} onChange={setSaveEnabled} />
      </CustomTooltip>
      <CustomTooltip content="Enable/Disable DRI (Direct Resource Isolation) for containers (mock)." position="bottom">
        <Toggle label="Dri" enabled={driEnabled} onChange={setDriEnabled} />
      </CustomTooltip>
      <CustomTooltip content="View or manage automated tasks related to containers (mock)." position="bottom">
        <Toggle label="Tasks" enabled={tasksEnabled} onChange={setTasksEnabled} />
      </CustomTooltip>
      <CustomTooltip content="Refresh container list." position="bottom">
        <button 
          className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]" 
          onClick={onRefresh} 
          disabled={isLoading}
          aria-label="Refresh Containers"
        >
          <RefreshIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}/>
        </button>
      </CustomTooltip>
    </div>
  );
  
  return (
    <Panel 
        title="Container Management" 
        className={`${panelWrapperClassName} flex flex-col`} 
        contentClassName="flex-grow overflow-hidden p-0"
        headerControls={headerControlsContent}
        onPopoutClick={onPopoutClick}
    >
      <div className="flex flex-col h-full overflow-hidden p-3"> 
          <div className="overflow-x-auto flex-grow">
            {isLoading && containers.length === 0 ? (
              <p className="text-[var(--brand-text-secondary)] text-center py-8 text-sm">Loading containers...</p>
            ) : (
              <div className="align-middle inline-block min-w-full">
                <table className="min-w-full divide-y divide-[var(--brand-border)]">
                  <thead className="bg-[var(--brand-primary-bg)]/50 sticky top-0 z-[5]">
                    <tr>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-[var(--brand-text-secondary)] uppercase tracking-wider">Container</th>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-[var(--brand-text-secondary)] uppercase tracking-wider">Status</th>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-[var(--brand-text-secondary)] uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-[var(--brand-primary-bg-light)] divide-y divide-[var(--brand-border)]">
                    {(containers || []).map(container => {
                      const statusDisplay = container.status || 'unknown'; // Default to 'unknown' string
                      const isRunning = typeof statusDisplay === 'string' && (statusDisplay === ContainerStatus.Running || statusDisplay.toLowerCase().startsWith('up'));
                      const isExited = statusDisplay === ContainerStatus.Exited;

                      return (
                        <tr key={container.id}>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <div className="text-sm text-[var(--brand-text-primary)]">{container.name || 'N/A'}</div>
                            <div className="text-xs text-[var(--brand-text-secondary)]">{container.image || 'N/A'}</div>
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              isRunning ? 'bg-[var(--brand-success)]/30 text-[var(--brand-success)]' :
                              isExited ? 'bg-[var(--brand-alert)]/30 text-[var(--brand-alert)]' :
                              'bg-yellow-500/30 text-yellow-300' // Stopped, unknown or other
                            }`}>
                              {statusDisplay}
                            </span>
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center gap-1">
                              <Button variant="ghost" size="sm" onClick={() => handleAction(container.id, 'start')} 
                                      className="p-1 disabled:opacity-50" 
                                      disabled={isRunning}
                                      title="Start">
                                <PlayIcon className="text-[var(--brand-success)] hover:opacity-80" />
                              </Button>
                              <Button variant="ghost" size="sm" onClick={() => handleAction(container.id, 'stop')} 
                                      className="p-1 disabled:opacity-50" 
                                      disabled={!isRunning}
                                      title="Stop">
                                <StopIcon className="text-yellow-400 hover:opacity-80" />
                              </Button>
                              <Button variant="ghost" size="sm" onClick={() => handleAction(container.id, 'delete')} 
                                      className="p-1"
                                      title="Delete">
                                <TrashIcon className="text-[var(--brand-alert)] hover:opacity-80" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {!isLoading && containers.length === 0 && <p className="text-[var(--brand-text-secondary)] text-center py-8 text-sm">No containers found.</p>}
                 { GATEKEEPER_PORT_RAW_PANEL === undefined && typeof moduleLevelImportMetaEnvPanel === 'object' && (
                    <p className="text-center text-xs text-yellow-400 p-2">Warning: VITE_GATEKEEPER_HTTP_PORT not defined. Using default.</p>
                )}
                { typeof moduleLevelImportMetaEnvPanel === 'undefined' && (
                     <p className="text-center text-xs text-red-500 p-2">Critical: Vite env not loaded. API calls will fail.</p>
                )}
              </div>
            )}
          </div>
      </div>
    </Panel>
  );
};
