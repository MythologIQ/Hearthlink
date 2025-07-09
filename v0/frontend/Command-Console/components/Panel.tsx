

import React from 'react';
import { ExternalLinkIcon } from '../constants'; // Ensure ExternalLinkIcon is imported

interface PanelProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  headerControls?: React.ReactNode;
  titleClassName?: string;
  contentClassName?: string;
  onPopoutClick?: () => void; // New prop for popout functionality
}

export const Panel: React.FC<PanelProps> = ({ title, children, className = '', headerControls, titleClassName = '', contentClassName = '', onPopoutClick }) => {
  const hasCustomPadding = contentClassName.includes('p-') || contentClassName.includes('px-') || contentClassName.includes('py-') || contentClassName.includes('pt-') || contentClassName.includes('pb-') || contentClassName.includes('pl-') || contentClassName.includes('pr-');
  const defaultContentPadding = hasCustomPadding ? '' : 'p-3 md:p-4';

  return (
    <div className={`bg-[var(--brand-primary-bg-light)] border border-[var(--brand-border)] rounded-lg shadow-lg flex flex-col ${className}`}>
      <div className={`px-3 md:px-4 py-3 border-b border-[var(--brand-border)] flex justify-between items-center ${titleClassName}`}>
        <h2 className="text-md md:text-lg font-semibold text-[var(--brand-text-primary)] font-orbitron tracking-wide">{title}</h2>
        <div className="flex items-center gap-2">
          {headerControls}
          {onPopoutClick && (
            <button 
              onClick={onPopoutClick} 
              className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]"
              aria-label={`Pop out ${title}`}
              title={`Pop out ${title}`}
            >
              <ExternalLinkIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      <div className={`${defaultContentPadding} flex-grow ${contentClassName}`}>
        {children}
      </div>
    </div>
  );
};
