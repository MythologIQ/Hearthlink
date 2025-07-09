


import React from 'react';
import { Button } from './common/Button';
import { SettingsIcon, UploadCloudIcon, CodeIcon, DatabaseIcon, ZapIcon, ServerIcon, PlayIcon, InformationCircleIcon } from '../constants';
import { useToast } from '../contexts/ToastContext';

interface ToolbarItem {
  id: string;
  label: string;
  icon: React.FC<{ className?: string }>;
  action: () => void;
  colorClass?: string; // Optional color class for the icon
}

const ToolbarDivider: React.FC = () => (
  <div className="h-5 w-px bg-[var(--brand-border)] mx-1"></div>
);

export const Toolbar: React.FC = () => {
  const { addToast } = useToast();

  const systemControlItems: ToolbarItem[] = [
    {
      id: 'startAlden',
      label: 'Start Alden Backend',
      icon: PlayIcon,
      action: () => addToast(
        "Manual Start: Open a new terminal, navigate to Alden's main directory (e.g., Nexus-suite/Alden/), and run its startup command (e.g., python main_alden_script.py or Start_Alden.bat). Refer to Alden's docs for the exact command.",
        'info',
        10000 // Longer duration for instructions
      ),
      colorClass: "text-green-400"
    },
    {
      id: 'startGatekeeper',
      label: 'Start Gatekeeper Backend',
      icon: PlayIcon,
      action: () => addToast(
        "Manual Start: Open a new terminal, navigate to Nexus-suite/Nexus/backend/, and run `node gatekeeper.js`. Ensure your .env file is configured correctly in that directory.",
        'info',
        10000
      ),
      colorClass: "text-green-400"
    },
     {
      id: 'consoleInfo',
      label: 'Console Frontend Info',
      icon: InformationCircleIcon,
      action: () => addToast(
        "Console Status: This Command Console frontend is typically started using `npm run dev` in the Nexus-suite/Nexus/frontend/Command-Console/ directory. It connects to the Gatekeeper backend.",
        'info',
        10000
      ),
      colorClass: "text-blue-400"
    },
  ];

  const toolItems: ToolbarItem[] = [
    { id: 'settings', label: 'Console Settings', icon: SettingsIcon, action: () => addToast('Console Settings panel opened (mock)', 'info', 3000) },
    { id: 'upload', label: 'Upload File to RAG', icon: UploadCloudIcon, action: () => addToast('File upload dialog triggered (mock)', 'info', 3000) },
    { id: 'code', label: 'Open Code Snippet Editor', icon: CodeIcon, action: () => addToast('Code editor opened (mock)', 'info', 3000) },
    { id: 'db', label: 'Database Viewer', icon: DatabaseIcon, action: () => addToast('Database viewer opened (mock)', 'info', 3000) },
  ];

  const serviceItems: ToolbarItem[] = [
    { 
      id: 'mcp', 
      label: 'MCP Server (Crawl4ai-RAG)', 
      icon: ServerIcon, 
      action: () => {
        addToast('Opening Crawl4ai-RAG server interface... Usually prompted via AI Agent.', 'info', 4000);
        // Ensure this port is correct and the server is expected to be accessible this way.
        window.open('http://localhost:8051', '_blank'); 
      } 
    },
    { id: 'plugins', label: 'Manage Plugins', icon: ZapIcon, action: () => addToast('Plugin manager opened (mock)', 'info', 3000) },
  ];


  const renderToolbarButton = (item: ToolbarItem) => {
    // Fix: Assign item.icon to a capitalized local variable IconComponent.
    // This can help JSX correctly interpret it as a React component,
    // especially in complex scenarios or with certain build tool configurations,
    // addressing issues where item.icon might be misinterpreted.
    const IconComponent = item.icon;
    return (
     <Button
        key={item.id}
        variant="ghost"
        size="sm"
        onClick={item.action}
        title={item.label}
        className="!p-2 flex-shrink-0 group hover:!bg-[var(--brand-accent1-hover)]"
        aria-label={item.label}
    >
        <IconComponent className={`w-5 h-5 ${item.colorClass || 'text-[var(--brand-text-secondary)]'} group-hover:text-white transition-colors`} />
    </Button>
    );
  };

  return (
    <div className="bg-[var(--brand-primary-bg-light)] border-t border-[var(--brand-border)] p-1.5 flex items-center space-x-1.5 overflow-x-auto shadow-md">
      {systemControlItems.map(renderToolbarButton)}
      <ToolbarDivider />
      {toolItems.map(renderToolbarButton)}
      <ToolbarDivider />
      {serviceItems.map(renderToolbarButton)}
    </div>
  );
};
