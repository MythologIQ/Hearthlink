import React from 'react';

interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const TextInput: React.FC<TextInputProps> = ({ className, leadingIcon, trailingIcon, ...props }) => {
  return (
    <div className="relative">
      {leadingIcon && (
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {/* Fix: Cast leadingIcon to React.ReactElement<{ className?: string }> to inform TypeScript about the expected props. */}
          {React.cloneElement(leadingIcon as React.ReactElement<{ className?: string }>, { className: 'w-4 h-4 text-[var(--brand-text-secondary)]' })}
        </div>
      )}
      <input
        type="text"
        className={`block w-full bg-[var(--brand-primary-bg)] border-[var(--brand-border)] text-[var(--brand-text-primary)] rounded-md shadow-sm py-2 
                    focus:ring-[var(--brand-accent1)] focus:border-[var(--brand-accent1)] sm:text-sm
                    placeholder:text-[var(--brand-text-secondary)]
                    ${leadingIcon ? "pl-10" : "pl-3"} 
                    ${trailingIcon ? "pr-10" : "pr-3"} 
                    ${className}`}
        {...props}
      />
      {trailingIcon && (
        // Assuming trailingIcon might be a button, allow pointer events
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center"> 
          {trailingIcon}
        </div>
      )}
    </div>
  );
};