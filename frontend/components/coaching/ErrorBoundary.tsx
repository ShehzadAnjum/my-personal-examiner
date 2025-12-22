/**
 * ErrorBoundary Component
 *
 * Reusable error boundary for wrapping individual coaching components.
 * Catches JavaScript errors in the component tree and displays a fallback UI.
 *
 * Usage:
 *   <ErrorBoundary fallback={<div>Error</div>}>
 *     <YourComponent />
 *   </ErrorBoundary>
 *
 * Features:
 * - Custom fallback UI
 * - Error logging
 * - Reset functionality
 * - Accessible error messages
 */

'use client';

import React, { Component, ReactNode } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  componentName?: string;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to error reporting service (e.g., Sentry)
    console.error('ErrorBoundary caught error:', {
      component: this.props.componentName || 'Unknown',
      error,
      errorInfo,
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-6"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <AlertCircle className="h-6 w-6 text-red-600" aria-hidden="true" />
            </div>

            <div className="flex-1 space-y-3">
              <div>
                <h3 className="text-lg font-semibold text-red-900">
                  {this.props.componentName
                    ? `${this.props.componentName} Error`
                    : 'Component Error'}
                </h3>
                <p className="mt-1 text-sm text-red-700">
                  Something went wrong while displaying this section.
                </p>
              </div>

              {this.state.error && (
                <details className="text-sm">
                  <summary className="cursor-pointer font-medium text-red-800 hover:text-red-900">
                    Error details
                  </summary>
                  <p className="mt-2 font-mono text-xs text-red-600 break-words bg-white p-3 rounded border border-red-200">
                    {this.state.error.message}
                  </p>
                </details>
              )}

              <button
                onClick={this.handleReset}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-sm shadow-sm"
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
