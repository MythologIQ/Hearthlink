import React, { useState } from 'react';

export interface Tab {
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
}

interface TabsProps {
  tabs: Tab[];
  initialTab?: number;
  tabsContainerClassName?: string;
  tabButtonClassName?: string;
  activeTabButtonClassName?: string;
  inactiveTabButtonClassName?: string;
  contentContainerClassName?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  initialTab = 0,
  tabsContainerClassName = "flex border-b border-[var(--brand-border)]",
  tabButtonClassName = "py-2 px-4 text-sm font-medium focus:outline-none transition-colors duration-150 font-orbitron",
  activeTabButtonClassName = "text-[var(--brand-accent2)] border-b-2 border-[var(--brand-accent2)]",
  inactiveTabButtonClassName = "text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)] hover:border-[var(--brand-accent1)] border-b-2 border-transparent",
  contentContainerClassName = "flex-grow overflow-auto"
}) => {
  const [activeTabIndex, setActiveTabIndex] = useState(initialTab);

  return (
    <div className="flex flex-col h-full">
      <div className={tabsContainerClassName} role="tablist">
        {tabs.map((tab, index) => (
          <button
            key={tab.title}
            role="tab"
            aria-selected={activeTabIndex === index}
            aria-controls={`tabpanel-${index}`}
            id={`tab-${index}`}
            disabled={tab.disabled}
            className={`${tabButtonClassName} ${
              activeTabIndex === index ? activeTabButtonClassName : inactiveTabButtonClassName
            } ${tab.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => setActiveTabIndex(index)}
          >
            {tab.title}
          </button>
        ))}
      </div>
      <div 
        id={`tabpanel-${activeTabIndex}`}
        role="tabpanel"
        aria-labelledby={`tab-${activeTabIndex}`}
        className={contentContainerClassName}
      >
        {tabs[activeTabIndex]?.content}
      </div>
    </div>
  );
};