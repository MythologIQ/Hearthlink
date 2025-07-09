

import React, { useState, useEffect, useCallback } from 'react';
import { Panel } from './Panel';
import { CloseIcon, AlertTriangleIcon, RefreshIcon } from '../constants'; // Added RefreshIcon
import { Button } from './common/Button';
import { useToast } from '../contexts/ToastContext';

interface DiagnosticsPanelProps {
  onClose: () => void;
  onRefreshSystemStatus: () => void; // To trigger header status refresh
}

interface GatekeeperDiagnostics {
  uptime: string;
  memoryUsageMB: string;
  nodeVersion: string;
  platform: string;
  lastApiError?: { message: string; timestamp: string; route: string } | null;
}

interface WebSocketDiagnostics {
  connectedClients: number;
  // Potentially more data like message rates if backend supports it
}
interface DiagnosticsData {
  gatekeeper?: GatekeeperDiagnostics;
  websockets?: WebSocketDiagnostics;
  // other components can be added
  error?: string; // For displaying fetch errors
}

// Helper function to safely get environment variables, similar to App.tsx
let moduleLevelImportMetaEnvDiag: Record<string, any> | undefined;
try {
  moduleLevelImportMetaEnvDiag = (import.meta as any).env;
} catch (e) {
  console.error("[DiagnosticsPanel.tsx Module Scope] Error accessing import.meta.env:", e);
  moduleLevelImportMetaEnvDiag = undefined;
}

const GATEKEEPER_PORT_RAW_DIAG = typeof moduleLevelImportMetaEnvDiag !== 'undefined' ? moduleLevelImportMetaEnvDiag.VITE_GATEKEEPER_HTTP_PORT : undefined;

function getDiagEnvVariable(rawValue: string | undefined, varName: string, defaultValue: string): string {
  if (typeof moduleLevelImportMetaEnvDiag === 'undefined') { // Check if import.meta.env itself was problematic
     console.warn(
      `[DiagnosticsPanel.tsx] Vite 'import.meta.env' was not accessible at module scope. Defaulting for ${varName}: '${defaultValue}'.`
    );
    return defaultValue;
  }
  if (typeof rawValue === 'string' && rawValue.trim() !== '') return rawValue;
  return defaultValue;
}
const GATEKEEPER_PORT_DIAG = getDiagEnvVariable(GATEKEEPER_PORT_RAW_DIAG, 'VITE_GATEKEEPER_HTTP_PORT', '9341');
const API_BASE_URL_DIAG = `http://localhost:${GATEKEEPER_PORT_DIAG}`;


export const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({ onClose, onRefreshSystemStatus }) => {
  const [diagnostics, setDiagnostics] = useState<DiagnosticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const { addToast } = useToast();

  const fetchDiagnostics = useCallback(async () => {
    setIsLoading(true);
    setDiagnostics(prev => ({ ...prev, error: undefined })); 
    try {
      const response = await fetch(`${API_BASE_URL_DIAG}/api/system/diagnostics`);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch diagnostics: ${response.status} ${errorText || ''}`);
      }
      const data = await response.json();
      setDiagnostics(data);
      setLastUpdated(new Date().toLocaleTimeString());
      addToast('Diagnostics data refreshed.', 'success', 2000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch diagnostics:", error);
      addToast(`Error fetching diagnostics: ${errorMessage}`, "error", 7000);
      setDiagnostics({ error: errorMessage }); 
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    fetchDiagnostics();
  }, [fetchDiagnostics]);

  const handleRefreshAll = () => {
    addToast('Refreshing system status and diagnostics...', 'info', 2000);
    onRefreshSystemStatus(); 
    fetchDiagnostics(); 
  };

  const renderDataPoint = (label: string, value?: string | number | null, accent: boolean = false) => {
    if (value === undefined || value === null) return null;
    return (
      <li>{label}: <span className={accent ? "text-[var(--brand-accent2)]" : "text-[var(--brand-text-primary)]"}>{String(value)}</span></li>
    );
  }

  return (
    <div className="fixed inset-0 bg-[var(--brand-primary-bg)]/70 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
        <Panel 
            title="System Diagnostics" 
            headerControls={
                <div className="flex items-center gap-2">
                    <button 
                        onClick={handleRefreshAll} 
                        className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]" 
                        aria-label="Refresh diagnostics"
                        title="Refresh Diagnostics"
                        disabled={isLoading}
                    >
                        <RefreshIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}/>
                    </button>
                    <button 
                        onClick={onClose} 
                        className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]" 
                        aria-label="Close diagnostics"
                        title="Close Diagnostics"
                    >
                        <CloseIcon className="w-4 h-4" />
                    </button>
                </div>
            }
            className="w-full max-w-2xl min-h-[400px] shadow-2xl !bg-[var(--brand-primary-bg-light)]"
            contentClassName="space-y-4"
        >
        {isLoading && (
            <div className="flex items-center justify-center h-full text-[var(--brand-text-secondary)]">
                <RefreshIcon className="w-6 h-6 animate-spin mr-2" /> Loading diagnostics data...
            </div>
        )}

        {!isLoading && diagnostics?.error && (
            <div className="p-3 bg-[var(--brand-alert)]/20 border border-[var(--brand-alert)]/50 rounded-md text-sm text-[var(--brand-alert)]">
                <div className="flex items-center">
                    <AlertTriangleIcon className="w-5 h-5 mr-2 flex-shrink-0" />
                    <p><span className="font-semibold">Error:</span> {diagnostics.error}</p>
                </div>
            </div>
        )}
        
        {!isLoading && !diagnostics?.error && diagnostics && (
            <>
                {diagnostics.gatekeeper && (
                    <div>
                        <h3 className="text-md font-semibold text-[var(--brand-text-primary)] mb-1 font-orbitron">Gatekeeper Status</h3>
                        <ul className="list-disc list-inside text-sm text-[var(--brand-text-secondary)] space-y-1 pl-2">
                            {renderDataPoint("Uptime", diagnostics.gatekeeper.uptime, true)}
                            {renderDataPoint("Memory Usage", `${diagnostics.gatekeeper.memoryUsageMB} MB`)}
                            {renderDataPoint("Node.js Version", diagnostics.gatekeeper.nodeVersion)}
                            {renderDataPoint("Platform", diagnostics.gatekeeper.platform)}
                            {diagnostics.gatekeeper.lastApiError ? (
                                <li className="text-yellow-400">Last API Error: 
                                    <span className="block pl-4 text-xs">
                                        "{diagnostics.gatekeeper.lastApiError.message}" on {diagnostics.gatekeeper.lastApiError.route} at {new Date(diagnostics.gatekeeper.lastApiError.timestamp).toLocaleTimeString()}
                                    </span>
                                </li>
                            ) : renderDataPoint("Last API Error", "None recorded recently")}
                        </ul>
                    </div>
                )}

                {diagnostics.websockets && (
                    <div>
                        <h3 className="text-md font-semibold text-[var(--brand-text-primary)] mb-1 font-orbitron">WebSocket Server</h3>
                        <ul className="list-disc list-inside text-sm text-[var(--brand-text-secondary)] space-y-1 pl-2">
                            {renderDataPoint("Connected Clients", diagnostics.websockets.connectedClients, true)}
                        </ul>
                    </div>
                )}
            </>
        )}
         {!isLoading && lastUpdated && (
            <p className="text-xs text-[var(--brand-text-secondary)] mt-3 text-right">
                Last updated: {lastUpdated}
            </p>
        )}
        </Panel>
    </div>
  );
};
