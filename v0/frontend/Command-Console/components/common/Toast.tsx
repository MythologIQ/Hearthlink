import React from 'react';
import { useToast } from '../../contexts/ToastContext';
import { ToastMessage, ToastType } from '../../types';
import { CloseIcon, AlertTriangleIcon, ShieldCheckIcon, ZapIcon } from '../../constants'; // Assuming ZapIcon for info

interface ToastProps extends Omit<ToastMessage, 'duration'> {}

const typeStyles: Record<ToastType, { bg: string; border: string; text: string; icon: React.ReactNode }> = {
  success: {
    bg: 'bg-green-500/90 border-green-600', // Darker green
    border: 'border-green-700',
    text: 'text-white',
    icon: <ShieldCheckIcon className="w-5 h-5 text-white" />,
  },
  error: {
    bg: 'bg-red-600/90 border-red-700', // Darker red
    border: 'border-red-800',
    text: 'text-white',
    icon: <AlertTriangleIcon className="w-5 h-5 text-white" />,
  },
  info: {
    bg: 'bg-blue-600/90 border-blue-700', // Darker blue
    border: 'border-blue-800',
    text: 'text-white',
    icon: <ZapIcon className="w-5 h-5 text-white" />, // Example, choose appropriate
  },
  warning: {
    bg: 'bg-yellow-500/90 border-yellow-600', // Darker yellow
    border: 'border-yellow-700',
    text: 'text-black', // Ensure contrast on yellow
    icon: <AlertTriangleIcon className="w-5 h-5 text-black" />,
  },
};

export const Toast: React.FC<ToastProps> = ({ id, message, type }) => {
  const { removeToast } = useToast();
  const styles = typeStyles[type];

  return (
    <div
      role="alert"
      className={`relative w-full p-3 pr-8 rounded-md shadow-xl border text-sm font-medium flex items-start gap-3
                  ${styles.bg} ${styles.border} ${styles.text} animate-fadeInRight`}
    >
      <div className="flex-shrink-0 mt-0.5">{styles.icon}</div>
      <div className="flex-grow break-words">{message}</div>
      <button
        onClick={() => removeToast(id)}
        className={`absolute top-1.5 right-1.5 p-1 rounded-full hover:bg-black/20 transition-colors`}
        aria-label="Close toast"
      >
        <CloseIcon className={`w-4 h-4 ${type === 'warning' ? 'text-black/70' : 'text-white/70'}`} />
      </button>
    </div>
  );
};

// Add basic fade-in animation to index.html or a global CSS file if you don't have one
// For now, adding a simple keyframe animation definition here as a comment
/*
@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.animate-fadeInRight {
  animation: fadeInRight 0.3s ease-out forwards;
}
*/
// In index.html <style> block, you can add:
/*
@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
.animate-fadeInRight { animation: fadeInRight 0.3s ease-out forwards; }
*/