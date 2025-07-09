
import React, { useState, useEffect } from 'react';
import { Panel } from './Panel';
import { Agent } from '../types';
import { UserIcon } from '../constants';
import { useToast } from '../contexts/ToastContext'; // Added useToast

interface AgentPanelProps {
  title: string;
  agents: Agent[];
  headerControls?: React.ReactNode;
  panelWrapperClassName?: string;
}

// New interface for the toggle state
interface AgentCoreStatus {
  [agentId: string]: boolean; // agentId -> isCoreEnabled
}

export const AgentPanel: React.FC<AgentPanelProps> = ({ title, agents, headerControls, panelWrapperClassName }) => {
  // State to manage the "Core Enabled" toggle for each agent
  const [coreEnabledStates, setCoreEnabledStates] = useState<AgentCoreStatus>({});
  const { addToast } = useToast();

  // Initialize or update coreEnabledStates when agents prop changes
  useEffect(() => {
    setCoreEnabledStates(prevCoreStates => {
      const newCoreStates: AgentCoreStatus = {};
      let changed = false;

      agents.forEach(agent => {
        const isAgentAvailable = agent.status?.toLowerCase() === 'available';
        if (isAgentAvailable) {
          // If agent is available, it should be in coreEnabledStates.
          // Default to false if not present, otherwise keep its current state.
          const currentAgentCoreState = prevCoreStates[agent.id] ?? false;
          newCoreStates[agent.id] = currentAgentCoreState;
          if (currentAgentCoreState !== (prevCoreStates[agent.id] ?? false)) {
            changed = true; // This condition mainly covers a new agent becoming available
          }
        }
        // Agents not "Available" won't have a toggle, so their state is effectively removed here
        // if newCoreStates is built fresh and only includes available ones.
      });

      // Determine if the actual set of togglable agents or their states changed
      const prevTogglableAgentIds = Object.keys(prevCoreStates).filter(id => agents.find(a => a.id === id && a.status?.toLowerCase() === 'available'));
      const newTogglableAgentIds = Object.keys(newCoreStates);

      if (prevTogglableAgentIds.length !== newTogglableAgentIds.length) {
        changed = true;
      } else {
        for (const id of newTogglableAgentIds) {
          if (newCoreStates[id] !== prevCoreStates[id]) {
            changed = true;
            break;
          }
        }
      }
      
      return changed ? newCoreStates : prevCoreStates;
    });
  }, [agents]);


  const handleToggleCoreConnection = (agentId: string, agentName: string) => {
    setCoreEnabledStates(prev => {
      const newState = !(prev[agentId] ?? false); // Default to true if undefined (i.e., turning on)
      addToast(`${agentName} Core connection ${newState ? 'enabled' : 'disabled'}. (Mock)`, newState ? 'success' : 'info', 3000);
      // Placeholder for actual API call or state dispatch
      // logger.info(`Toggled Core connection for ${agentName} (ID: ${agentId}) to ${newState}`, 'AgentPanel');
      return { ...prev, [agentId]: newState };
    });
  };

  return (
    <Panel title={title} headerControls={headerControls} className={panelWrapperClassName}>
      <div className="space-y-2">
        {agents.map(agent => {
          const agentStatusLower = agent.status?.toLowerCase() || 'unknown';
          const isAvailable = agentStatusLower === 'available';
          const isCoreEnabled = coreEnabledStates[agent.id] || false;
          
          const isGreenStatus = ['online', 'active', 'connected', 'running'].includes(agentStatusLower);
          const isDockerRunning = agent.role === 'Containerized Service' && (agentStatusLower.startsWith('running') || agentStatusLower.startsWith('up'));

          let statusColorClass = 'bg-yellow-500/30 text-yellow-300'; 

          if (isGreenStatus || isDockerRunning) {
            statusColorClass = 'bg-[var(--brand-success)]/30 text-[var(--brand-success)]';
          } else if (isAvailable) { 
            statusColorClass = 'bg-blue-500/30 text-blue-300';
          } else if (agentStatusLower === 'crawling' || agentStatusLower === 'processing' || agentStatusLower === 'generating') {
            statusColorClass = 'bg-[var(--brand-accent1)]/30 text-[var(--brand-accent1)]';
          } else if (agentStatusLower.includes('offline') || agentStatusLower.includes('disconnected') || agentStatusLower.includes('error')) {
            statusColorClass = 'bg-[var(--brand-alert)]/30 text-[var(--brand-alert)]';
          }
          if (agent.status === 'Offline (API)' && !statusColorClass.includes('alert')) {
             statusColorClass = 'bg-yellow-500/30 text-yellow-300';
          }


          return (
            <div key={agent.id} className="flex items-center p-2.5 bg-[var(--brand-primary-bg)] rounded-md shadow">
              {agent.avatarUrl ? (
                <img src={agent.avatarUrl} alt={agent.name} className="w-7 h-7 rounded-full mr-2.5 flex-shrink-0" />
              ) : (
                <UserIcon className="w-7 h-7 text-[var(--brand-text-secondary)] mr-2.5 flex-shrink-0" />
              )}
              <div className="flex-grow min-w-0"> {/* Added min-w-0 for better truncation if needed */}
                <p className="font-medium text-sm text-[var(--brand-text-primary)] truncate" title={agent.name}>{agent.name}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                <span className={`px-2 py-0.5 text-xs rounded-full font-semibold ${statusColorClass} whitespace-nowrap`}>
                    {agent.status}
                </span>
                {isAvailable && (
                  <button
                    onClick={() => handleToggleCoreConnection(agent.id, agent.name)}
                    aria-pressed={isCoreEnabled}
                    title={isCoreEnabled ? "Disable Core Connection" : "Enable Core Connection"}
                    className={`px-2.5 py-1 text-xs rounded-full font-semibold transition-all duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-[var(--brand-primary-bg)]
                      ${isCoreEnabled 
                        ? 'bg-[var(--brand-accent2)] text-[var(--brand-primary-bg)] hover:bg-opacity-80 focus:ring-[var(--brand-accent2)]' 
                        : 'bg-gray-600/70 text-gray-300 hover:bg-gray-500/90 focus:ring-gray-400 border border-gray-700 hover:border-gray-500'
                      } whitespace-nowrap`}
                  >
                    {isCoreEnabled ? 'Core On' : 'Core Off'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
        {agents.length === 0 && <p className="text-[var(--brand-text-secondary)] text-center py-4 text-sm">No agents to display.</p>}
      </div>
    </Panel>
  );
};
