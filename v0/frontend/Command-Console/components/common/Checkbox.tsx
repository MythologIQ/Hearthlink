import React from 'react';

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({ label, id, ...props }) => {
  const uniqueId = id || `checkbox-${label.replace(/\s+/g, '-')}`;
  return (
    <div className="flex items-center">
      <input
        id={uniqueId}
        type="checkbox"
        className="h-4 w-4 text-[var(--brand-accent1)] bg-[var(--brand-primary-bg-lighter)] border-[var(--brand-border)] rounded focus:ring-[var(--brand-accent1)] focus:ring-offset-[var(--brand-primary-bg-light)]"
        {...props}
      />
      <label htmlFor={uniqueId} className="ml-2 block text-sm text-[var(--brand-text-secondary)]">
        {label}
      </label>
    </div>
  );
};