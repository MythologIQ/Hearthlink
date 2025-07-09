import React, { useState } from 'react';

interface CustomTooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  className?: string; // For additional styling of the tooltip itself
  wrapperClassName?: string; // For styling the wrapper div
  position?: 'top' | 'bottom' | 'left' | 'right'; 
}

export const CustomTooltip: React.FC<CustomTooltipProps> = ({
  content,
  children,
  className = '',
  wrapperClassName = '',
  position = 'bottom',
}) => {
  const [isVisible, setIsVisible] = useState(false);

  let positionClasses = '';
  switch (position) {
    case 'top':
      positionClasses = 'bottom-full left-1/2 -translate-x-1/2 mb-2';
      break;
    case 'left':
      positionClasses = 'top-1/2 -translate-y-1/2 right-full mr-2';
      break;
    case 'right':
      positionClasses = 'top-1/2 -translate-y-1/2 left-full ml-2';
      break;
    case 'bottom':
    default:
      positionClasses = 'top-full left-1/2 -translate-x-1/2 mt-2';
      break;
  }

  return (
    <div
      className={`relative inline-block ${wrapperClassName}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)} // Added for keyboard accessibility
      onBlur={() => setIsVisible(false)}  // Added for keyboard accessibility
      tabIndex={0} // Make it focusable for keyboard users
    >
      {children}
      {isVisible && (
        <div
          role="tooltip"
          // Ensure tooltip is not announced by default if children are already descriptive
          // Or use aria-describedby on children to point to tooltip id if tooltip is always rendered (but hidden)
          className={`absolute z-[60] px-2.5 py-1.5 text-xs font-medium text-[var(--brand-text-primary)] bg-[var(--brand-primary-bg-lighter)] border border-[var(--brand-border)] rounded-md shadow-lg whitespace-nowrap
                      ${positionClasses}
                      ${className}
                      transition-opacity duration-150 ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        >
          {content}
        </div>
      )}
    </div>
  );
};
