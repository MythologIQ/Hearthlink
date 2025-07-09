

import React, { useState, useEffect } from 'react';
import { Task } from '../types'; 
import { Button } from './common/Button';
import { RefreshIcon } from '../constants';


interface RecentTasksPanelProps {
  initialTasks: Task[];
  isLoading: boolean;
  onRefresh: () => void;
}

export const RecentTasksPanel: React.FC<RecentTasksPanelProps> = ({ initialTasks, isLoading, onRefresh }) => {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);

  useEffect(() => {
    setTasks(initialTasks);
  }, [initialTasks]);


  if (isLoading && tasks.length === 0) {
    return <div className="p-4 text-center text-[var(--brand-text-secondary)]">Loading recent tasks...</div>;
  }

  return (
    <div className="p-3 h-full flex flex-col">
      <div className="mb-2 text-right">
        <Button 
            size="sm" 
            variant="secondary" 
            onClick={onRefresh} 
            disabled={isLoading}
            className="!px-2 !py-1"
            title="Refresh Tasks"
        >
            <RefreshIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div> 
      {tasks.length === 0 && !isLoading ? (
        <p className="text-[var(--brand-text-secondary)] text-center py-4 flex-grow flex items-center justify-center">No recent tasks.</p>
      ) : (
        <div className="space-y-2 font-jetbrains-mono text-xs overflow-y-auto flex-grow">
          {tasks.map(task => (
            <div key={task.id} className="p-2.5 bg-[var(--brand-primary-bg)] rounded-md shadow">
              <div className="flex justify-between items-center">
                <span className="font-medium text-[var(--brand-text-primary)] truncate" title={task.name}>{task.name}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold
                  ${task.status === 'Completed' ? 'bg-[var(--brand-success)]/30 text-[var(--brand-success)]' : ''}
                  ${task.status === 'In Progress' ? 'bg-[var(--brand-accent1)]/30 text-[var(--brand-accent1)]' : ''}
                  ${task.status === 'Pending' ? 'bg-yellow-500/30 text-yellow-300' : ''}
                  ${task.status === 'Failed' ? 'bg-[var(--brand-alert)]/30 text-[var(--brand-alert)]' : ''}
                `}>
                  {task.status}
                </span>
              </div>
              <p className="text-xs text-[var(--brand-text-secondary)] opacity-80 mt-0.5">{new Date(task.timestamp).toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
