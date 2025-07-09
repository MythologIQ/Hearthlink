import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}) => {
  const baseStyles = "font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--brand-primary-bg-light)] transition ease-in-out duration-150 disabled:opacity-60 disabled:cursor-not-allowed";
  
  let variantStyles = '';
  switch (variant) {
    case 'primary':
      variantStyles = 'bg-[var(--brand-accent1)] hover:bg-[var(--brand-accent1-hover)] text-white focus:ring-[var(--brand-accent1)]';
      break;
    case 'secondary':
      variantStyles = 'bg-[var(--brand-primary-bg-lighter)] hover:bg-[var(--brand-border)] text-[var(--brand-text-secondary)] focus:ring-[var(--brand-text-secondary)] border border-[var(--brand-border)] hover:border-[var(--brand-accent2)]';
      break;
    case 'danger':
      variantStyles = 'bg-[var(--brand-alert)] hover:bg-red-700 text-white focus:ring-[var(--brand-alert)]';
      break;
    case 'ghost':
      variantStyles = 'bg-transparent hover:bg-[var(--brand-primary-bg-lighter)] text-[var(--brand-text-secondary)] focus:ring-[var(--brand-accent2)] border border-transparent hover:border-[var(--brand-border)]';
      break;
  }

  let sizeStyles = '';
  switch (size) {
    case 'sm':
      sizeStyles = 'px-2.5 py-1.5 text-xs';
      break;
    case 'md':
      sizeStyles = 'px-4 py-2 text-sm';
      break;
    case 'lg':
      sizeStyles = 'px-6 py-3 text-base';
      break;
  }

  return (
    <button
      type="button"
      className={`${baseStyles} ${variantStyles} ${sizeStyles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};