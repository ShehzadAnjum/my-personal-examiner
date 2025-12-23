/**
 * useToast Hook & ToastProvider
 *
 * Context-based toast notification system.
 *
 * Usage:
 *   // Wrap app with ToastProvider in layout.tsx:
 *   <ToastProvider><App /></ToastProvider>
 *
 *   // In components:
 *   const { toast } = useToast();
 *   toast({ title: "Success!", description: "Session created", variant: "success" });
 */

'use client';

import * as React from 'react';
import { Toaster, Toast as ToastType } from '@/components/ui/toast';

interface ToastContextValue {
  toast: (props: Omit<ToastType, 'id'>) => void;
  dismiss: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastType[]>([]);

  const toast = React.useCallback((props: Omit<ToastType, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    const duration = props.duration || 5000; // Default 5 seconds

    const newToast: ToastType = {
      ...props,
      id,
      duration,
    };

    setToasts((prev) => [...prev, newToast]);

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        dismiss(id);
      }, duration);
    }
  }, []);

  const dismiss = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast, dismiss }}>
      {children}
      <Toaster toasts={toasts} onClose={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}
