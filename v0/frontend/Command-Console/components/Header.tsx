
import React from 'react';
import { Button } from './common/Button';
import { CustomTooltip } from './common/CustomTooltip'; // Import CustomTooltip
import { SettingsIcon, AlertTriangleIcon, WifiIcon, ShieldCheckIcon, ShieldOffIcon, ZapIcon, RefreshIcon } from '../constants';

interface HeaderProps {
  wsStatus: string;
  onRefreshPythonWs: () => void; // For Python WS (e.g. 8765)
  bridgeStatus: string;
  isConsoleVerified: boolean;
  onToggleDiagnostics: () => void;
  onRefreshSystemStatus: () => void; // For Gatekeeper system status (Bridge, etc.)
}

// StatusIndicatorProps is an internal type for StatusIndicator now
interface StatusIndicatorProps {
  status: string;
  label: string;
  icon: React.ReactElement<{ className?: string }>;
  goodStatus: string[];
  onRefreshClick?: () => void;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label, icon, goodStatus, onRefreshClick }) => {
  const isGood = goodStatus.includes(status.toLowerCase());
  const showRefreshButton = !isGood && onRefreshClick && (status.toLowerCase().includes('error') || status.toLowerCase().includes('disconnected') || status.toLowerCase().includes('offline'));


  return (
    // The native title attribute is kept here for basic accessibility if CSS/JS fails.
    // The CustomTooltip will provide the styled hover effect.
    <div className="flex items-center gap-1.5 sm:gap-2" title={`${label}: ${status}`}> 
      {React.cloneElement(icon, { className: `w-4 h-4 ${isGood ? 'text-[var(--brand-success)]' : 'text-[var(--brand-alert)]'}` })}
      <span className={`text-xs hidden sm:inline ${isGood ? 'text-[var(--brand-text-secondary)]' : 'text-[var(--brand-alert)]'}`}>{label}:</span>
      <span className={`text-xs font-medium ${isGood ? 'text-[var(--brand-success)]' : 'text-[var(--brand-alert)]'}`}>{status}</span>
      {showRefreshButton && (
        <button 
          onClick={onRefreshClick} 
          className="p-0.5 text-[var(--brand-text-secondary)] hover:text-[var(--brand-accent2)] focus:outline-none"
          aria-label={`Refresh ${label} status`}
          title={`Refresh ${label} status`} // Title for the button specifically
        >
          <RefreshIcon className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}

export const Header: React.FC<HeaderProps> = ({ 
    wsStatus, 
    onRefreshPythonWs,
    bridgeStatus, 
    isConsoleVerified, 
    onToggleDiagnostics,
    onRefreshSystemStatus
}) => {
  return (
    <header className="bg-[var(--brand-primary-bg-light)]/80 backdrop-blur-sm border-b border-[var(--brand-border)] p-3 sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2 sm:gap-4">
          <img src="/header.png" alt="MythologIQ Logo" className="h-8 sm:h-10 object-contain"/>
           <div className="h-6 border-l border-[var(--brand-border)] hidden sm:block"></div>
            <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
                 <CustomTooltip content="WebSocket: Real-time communication channel with external server (e.g., Python WS on 8765)." position="bottom" wrapperClassName="focus:outline-none">
                   <StatusIndicator 
                      status={wsStatus} 
                      label="WS" 
                      icon={<WifiIcon />} 
                      goodStatus={['connected', 'online']} 
                      onRefreshClick={onRefreshPythonWs} // Use dedicated refresh for Python WS
                    />
                 </CustomTooltip>
                 <CustomTooltip content="Bridge: Gatekeeper backend server operational status." position="bottom" wrapperClassName="focus:outline-none">
                   <StatusIndicator 
                      status={bridgeStatus} 
                      label="Bridge" 
                      icon={<ZapIcon />} 
                      goodStatus={['connected', 'active']}
                      onRefreshClick={onRefreshSystemStatus} // Use general system status refresh for Bridge
                    />
                 </CustomTooltip>
                 <CustomTooltip content="Console: Verification status of this frontend session by Gatekeeper." position="bottom" wrapperClassName="focus:outline-none">
                   <StatusIndicator 
                      status={isConsoleVerified ? "Verified" : "Unverified"} 
                      label="Console" 
                      icon={isConsoleVerified ? <ShieldCheckIcon /> : <ShieldOffIcon />} 
                      goodStatus={['verified']} 
                      // No direct refresh for console verification, it's part of Gatekeeper's state
                  />
                 </CustomTooltip>
            </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Button variant="ghost" size="sm" onClick={onToggleDiagnostics} className="p-1.5" aria-label="Toggle Diagnostics Panel">
            <AlertTriangleIcon className="w-5 h-5 text-[var(--brand-accent2)]" />
            <span className="ml-1 hidden sm:inline text-[var(--brand-text-secondary)]">Diagnostics</span>
          </Button>
        </div>
      </div>
    </header>
  );
};
