

import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Checkbox } from './common/Checkbox';
import { Button } from './common/Button';
import { TextInput } from './common/TextInput';
import { LogEntry, LogItemType } from '../types';
import { MemoryIcon, EventIcon, CommandIcon } from '../constants';

interface CombinedLogsPanelProps {
  initialEventCommandLogs: LogEntry[];
  // Add other props if needed, e.g., for fetching system logs
}

const LogItemIcon: React.FC<{type: LogItemType}> = ({ type }) => {
  const commonClasses = "mr-2 flex-shrink-0 w-4 h-4";
  if (type === LogItemType.Memory) return <MemoryIcon className={`${commonClasses} text-[var(--brand-accent2)]`} />;
  if (type === LogItemType.Event) return <EventIcon className={`${commonClasses} text-[var(--brand-success)]`} />;
  if (type === LogItemType.Command) return <CommandIcon className={`${commonClasses} text-[var(--brand-accent1)]`} />;
  return null;
};

export const CombinedLogsPanel: React.FC<CombinedLogsPanelProps> = ({ initialEventCommandLogs }) => {
  // State for Event/Command Logs
  const [eventCommandLogs] = useState<LogEntry[]>(initialEventCommandLogs);
  const [filters, setFilters] = useState<Record<LogItemType, boolean>>({
    [LogItemType.Memory]: true,
    [LogItemType.Event]: true,
    [LogItemType.Command]: true,
  });

  const handleFilterChange = (type: LogItemType) => {
    setFilters(prev => ({ ...prev, [type]: !prev[type] }));
  };

  const filteredEventCommandLogs = useMemo(() => {
    return eventCommandLogs
      .filter(log => filters[log.type])
      .sort((a,b) => {
        // Attempt to parse timestamps, fall back if invalid
        const timeA = new Date(`1970/01/01 ${a.timestamp}`).getTime();
        const timeB = new Date(`1970/01/01 ${b.timestamp}`).getTime();
        if (isNaN(timeA) || isNaN(timeB)) return 0; // Or handle error appropriately
        return timeB - timeA;
      });
  }, [eventCommandLogs, filters]);

  // State for System Logs
  const [systemLogOutput, setSystemLogOutput] = useState<string[]>(['System log viewer initialized.']);
  const [systemLogFilterInput, setSystemLogFilterInput] = useState('');
  const systemLogsEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToSystemBottom = () => {
    systemLogsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToSystemBottom, [systemLogOutput]);

  const handleSystemLogCommand = (command: string) => {
    setSystemLogOutput(prev => [...prev, `> ${command} logs requested at ${new Date().toLocaleTimeString()}`]);
    setTimeout(() => {
        setSystemLogOutput(prev => [...prev, `Sample log from ${command}: ${Math.random().toString(36).substring(7)}`, `Another line for ${command}...`]);
    }, 500);
  };
  
  const filteredSystemLogs = systemLogOutput.filter(log => log.toLowerCase().includes(systemLogFilterInput.toLowerCase()));

  return (
    <div className="p-3 flex flex-col h-full overflow-y-auto">
      {/* Section 1: Event & Command Logs */}
      <div className="mb-4 pb-4 border-b border-[var(--brand-border)]">
        <h3 className="text-md font-semibold text-[var(--brand-text-primary)] font-orbitron mb-2">Activity Logs</h3>
        <div className="mb-3 flex flex-wrap gap-x-4 gap-y-2">
          <Checkbox label="Memory" checked={filters[LogItemType.Memory]} onChange={() => handleFilterChange(LogItemType.Memory)} />
          <Checkbox label="Event" checked={filters[LogItemType.Event]} onChange={() => handleFilterChange(LogItemType.Event)} />
          <Checkbox label="Command" checked={filters[LogItemType.Command]} onChange={() => handleFilterChange(LogItemType.Command)} />
        </div>
        <div className="space-y-1.5 max-h-60 overflow-y-auto flex-grow font-jetbrains-mono text-xs pr-1">
          {filteredEventCommandLogs.map(log => (
            <div key={log.id} className="p-2 bg-[var(--brand-primary-bg)] rounded-md">
              <div className="flex items-center justify-between">
                  <div className="flex items-center">
                      <LogItemIcon type={log.type} />
                      <span className="font-medium text-[var(--brand-text-secondary)] mr-2">{log.type}</span>
                      <span className="text-[var(--brand-text-secondary)] opacity-80">{log.timestamp}</span>
                  </div>
                  {log.status && (
                       <span className={`px-2 py-0.5 rounded-full text-xs font-semibold
                          ${log.status === 'REWIND' ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50' : ''}
                          ${log.status === 'exited' ? 'bg-[var(--brand-alert)]/30 text-[var(--brand-alert)] border border-[var(--brand-alert)]/50' : ''}
                          ${log.status !== 'REWIND' && log.status !== 'exited' ? 'bg-[var(--brand-success)]/30 text-[var(--brand-success)] border border-[var(--brand-success)]/50' : ''}
                       `}>
                          {log.status}
                      </span>
                  )}
              </div>
              <p className="mt-1 text-[var(--brand-text-primary)] ml-6">{log.text}</p>
            </div>
          ))}
          {filteredEventCommandLogs.length === 0 && <p className="text-[var(--brand-text-secondary)] text-center py-4">No activity logs match filters.</p>}
        </div>
      </div>

      {/* Section 2: System Logs */}
      <div>
        <h3 className="text-md font-semibold text-[var(--brand-text-primary)] font-orbitron mb-2">System Logs</h3>
        <TextInput
          value={systemLogFilterInput}
          onChange={(e) => setSystemLogFilterInput(e.target.value)}
          placeholder="Filter system logs (e.g., 'error', 'nexus')"
          className="mb-2 font-jetbrains-mono !bg-[var(--brand-primary-bg)] !border-[var(--brand-border)] placeholder:text-[var(--brand-text-secondary)]"
          aria-label="Filter system logs input"
        />
        <div className="max-h-60 bg-[var(--brand-primary-bg)] p-2 rounded-md overflow-y-auto text-xs font-jetbrains-mono mb-2 border border-[var(--brand-border)] pr-1">
          {filteredSystemLogs.map((line, index) => (
            <div key={index} className={`whitespace-pre-wrap ${line.startsWith('>') ? 'text-[var(--brand-accent1)]' : 'text-[var(--brand-text-secondary)]'}`}>{line}</div>
          ))}
          <div ref={systemLogsEndRef} />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-auto">
          <Button variant="secondary" size="sm" onClick={() => handleSystemLogCommand('Nexus')}>Nexus Logs</Button>
          <Button variant="secondary" size="sm" onClick={() => handleSystemLogCommand('Alden')}>Alden Logs</Button>
          <Button variant="secondary" size="sm" onClick={() => handleSystemLogCommand('MCP')}>MCP Logs</Button>
        </div>
      </div>
    </div>
  );
};