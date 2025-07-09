import React from 'react';
import { useToast } from '../../contexts/ToastContext';
import { Toast } from './Toast';

export const Toaster: React.FC = () => {
  const { toasts } = useToast();

  return (
    <div className="fixed top-5 right-5 z-[200] w-full max-w-xs sm:max-w-sm space-y-3">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          message={toast.message}
          type={toast.type}
        />
      ))}
    </div>
  );
};