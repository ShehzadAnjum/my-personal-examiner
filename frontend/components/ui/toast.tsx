/**
 * Toast Component
 *
 * Toast notifications for success, error, warning, and info messages.
 * Based on shadcn/ui toast pattern with custom implementation.
 *
 * Usage:
 *   const { toast } = useToast();
 *   toast({ title: "Success", description: "Session created!", variant: "success" });
 */

'use client';

import * as React from 'react';
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastProps extends Toast {
  onClose: () => void;
}

export function Toast({ id, title, description, variant = 'default', onClose }: ToastProps) {
  const Icon =
    variant === 'success' ? CheckCircle2
    : variant === 'error' ? AlertCircle
    : variant === 'warning' ? AlertTriangle
    : variant === 'info' ? Info
    : null;

  const variants = {
    default: 'bg-white border-gray-300',
    success: 'bg-green-50 border-green-300',
    error: 'bg-red-50 border-red-300',
    warning: 'bg-yellow-50 border-yellow-300',
    info: 'bg-blue-50 border-blue-300',
  };

  const iconColors = {
    default: 'text-gray-600',
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600',
  };

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg border shadow-lg max-w-md w-full',
        'animate-in slide-in-from-top-5 fade-in duration-300',
        variants[variant]
      )}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      {Icon && (
        <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', iconColors[variant])} aria-hidden="true" />
      )}

      <div className="flex-1 space-y-1">
        {title && (
          <div className="font-semibold text-sm text-gray-900">
            {title}
          </div>
        )}
        {description && (
          <div className="text-sm text-gray-700">
            {description}
          </div>
        )}
      </div>

      <button
        onClick={onClose}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

interface ToasterProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export function Toaster({ toasts, onClose }: ToasterProps) {
  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast {...toast} onClose={() => onClose(toast.id)} />
        </div>
      ))}
    </div>
  );
}
