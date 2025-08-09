// UI Components Index
// Export all shared UI components for absolute imports

import React from 'react';

export interface CardProps {
  children?: React.ReactNode | React.ReactNode[];
  className?: string;
  onClick?: () => void;
}

export interface CardContentProps {
  children?: React.ReactNode | React.ReactNode[];
  className?: string;
}

export interface ButtonProps {
  children?: React.ReactNode | React.ReactNode[];
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: 'text' | 'email' | 'password' | 'number' | 'date';
  className?: string;
}

export interface BadgeProps {
  children?: React.ReactNode | React.ReactNode[];
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'secondary' | 'outline';
  className?: string;
}

export interface AlertProps {
  children?: React.ReactNode | React.ReactNode[];
  className?: string;
}

export interface AlertTitleProps {
  children?: React.ReactNode | React.ReactNode[];
  className?: string;
}

export interface AlertDescriptionProps {
  children?: React.ReactNode | React.ReactNode[];
  className?: string;
}

// Card Component
export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => (
  <div 
    className={`bg-white rounded-lg shadow-md border border-gray-200 ${onClick ? 'cursor-pointer' : ''} ${className}`}
    onClick={onClick}
  >
    {children}
  </div>
);

// CardContent Component
export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
  <div className={`p-4 ${className}`}>
    {children}
  </div>
);

// Button Component
export const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'primary',
  size = 'md',
  className = '' 
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100'
  };
  
  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 py-2',
    lg: 'h-11 px-8'
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

// Input Component
export const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  type = 'text',
  className = ''
}) => (
  <input
    type={type}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    disabled={disabled}
    className={`flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
  />
);

// Badge Component
export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'default',
  className = '' 
}) => {
  const variantClasses = {
    default: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    secondary: 'bg-gray-100 text-gray-800',
    outline: 'border border-gray-300 bg-white text-gray-700'
  };
  
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

// Alert Components
export const Alert: React.FC<AlertProps> = ({ children, className = '' }) => (
  <div className={`relative w-full rounded-lg border border-gray-200 p-4 bg-white ${className}`}>
    {children}
  </div>
);

export const AlertTitle: React.FC<AlertTitleProps> = ({ children, className = '' }) => (
  <h5 className={`mb-1 font-medium leading-none tracking-tight ${className}`}>
    {children}
  </h5>
);

export const AlertDescription: React.FC<AlertDescriptionProps> = ({ children, className = '' }) => (
  <div className={`text-sm text-gray-600 ${className}`}>
    {children}
  </div>
);

// Default export for the module
const UIComponents = {
  Card,
  CardContent,
  Button,
  Input,
  Badge,
  Alert,
  AlertTitle,
  AlertDescription
};

export default UIComponents;