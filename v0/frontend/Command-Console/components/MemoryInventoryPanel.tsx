


import React, { useState } from 'react';
import { Panel } from './Panel';
import { MemoryItem, MemorySource } from '../types';
import { Button } from './common/Button'; // For potential filter buttons
import { ExternalLinkIcon, ZapIcon, UserIcon } from '../constants'; // Example icons

interface MemoryInventoryPanelProps {
  items: MemoryItem[];
  panelWrapperClassName?: string;
  onPopoutClick?: () => void;
}

const SourceIcon: React.FC<{ source: MemorySource }> = ({ source }) => {
  if (source === MemorySource.AldenRAG) {
    // Fix: Wrap UserIcon in a span and apply title attribute to the span
    return <span title={MemorySource.AldenRAG}><UserIcon className="w-4 h-4 text-[var(--brand-accent1)] mr-2 flex-shrink-0" /></span>;
  }
  if (source === MemorySource.MCPWebcrawl) {
    // Fix: Wrap ZapIcon in a span and apply title attribute to the span
    return <span title={MemorySource.MCPWebcrawl}><ZapIcon className="w-4 h-4 text-[var(--brand-accent2)] mr-2 flex-shrink-0" /></span>;
  }
  return null;
};

export const MemoryInventoryPanel: React.FC<MemoryInventoryPanelProps> = ({ items, panelWrapperClassName, onPopoutClick }) => {
  const [filterSource, setFilterSource] = useState<MemorySource | null>(null);

  const filteredItems = items.filter(item => !filterSource || item.source === filterSource);

  return (
    <Panel
      title="Memory Inventory"
      className={`${panelWrapperClassName} flex flex-col`}
      contentClassName="flex flex-col"
      onPopoutClick={onPopoutClick}
      headerControls={
        <div className="flex gap-2">
            <Button 
                variant={filterSource === null ? "primary" : "secondary"} 
                size="sm" 
                onClick={() => setFilterSource(null)}
                className="!px-2 !py-1"
            >
                All
            </Button>
            <Button 
                variant={filterSource === MemorySource.AldenRAG ? "primary" : "secondary"} 
                size="sm" 
                onClick={() => setFilterSource(MemorySource.AldenRAG)}
                className="!px-2 !py-1"
            >
                Alden
            </Button>
            <Button 
                variant={filterSource === MemorySource.MCPWebcrawl ? "primary" : "secondary"} 
                size="sm" 
                onClick={() => setFilterSource(MemorySource.MCPWebcrawl)}
                className="!px-2 !py-1"
            >
                MCP
            </Button>
        </div>
      }
    >
      <div className="space-y-1.5 overflow-y-auto flex-grow font-jetbrains-mono text-xs">
        {filteredItems.map(item => (
          <div key={item.id} className="p-2 bg-[var(--brand-primary-bg)] rounded-md">
            <div className="flex items-center justify-between mb-0.5">
              <div className="flex items-center">
                <SourceIcon source={item.source} />
                <span className="font-medium text-[var(--brand-text-secondary)] mr-2 truncate" title={item.type}>{item.type}</span>
              </div>
              <span className="text-xs text-[var(--brand-text-secondary)] opacity-80 flex-shrink-0">{item.timestamp}</span>
            </div>
            <p className="text-[var(--brand-text-primary)] text-xs ml-6 mb-0.5 truncate" title={item.description}>{item.description}</p>
            <div className="ml-6 flex items-center justify-between">
              <div className="flex flex-wrap gap-1 mt-0.5">
                {item.tags?.slice(0, 3).map(tag => (
                  <span key={tag} className="px-1.5 py-0.5 text-[10px] bg-[var(--brand-primary-bg-lighter)] text-[var(--brand-text-secondary)] rounded">
                    {tag}
                  </span>
                ))}
              </div>
               <span className="text-[10px] text-[var(--brand-text-secondary)] opacity-70 flex-shrink-0">{item.size}</span>
            </div>
          </div>
        ))}
        {filteredItems.length === 0 && <p className="text-[var(--brand-text-secondary)] text-center py-4">No memory items match filters.</p>}
      </div>
    </Panel>
  );
};