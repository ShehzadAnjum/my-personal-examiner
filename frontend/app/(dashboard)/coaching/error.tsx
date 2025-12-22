/**
 * Coaching Route Error Boundary
 *
 * Catches errors in the coaching section and displays a coaching-specific
 * error UI with helpful recovery actions.
 *
 * Route: /coaching/** (all coaching routes)
 * Purpose: Graceful error handling for coaching sessions
 */

'use client';

import { useEffect } from 'react';
import { AlertCircle, Home, RefreshCw } from 'lucide-react';
import Link from 'next/link';

export default function CoachingError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to error reporting service (e.g., Sentry)
    console.error('Coaching error boundary caught:', error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-6">
      <div className="max-w-lg space-y-6 text-center">
        {/* Error Icon */}
        <div className="flex justify-center">
          <div className="rounded-full bg-red-100 p-6">
            <AlertCircle className="h-12 w-12 text-red-600" aria-hidden="true" />
          </div>
        </div>

        {/* Error Message */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">
            Coaching Session Error
          </h1>
          <p className="text-gray-600 leading-relaxed">
            We encountered an issue with your coaching session. This could be due to a
            network problem or an unexpected error. Don't worry - your previous sessions
            are safe!
          </p>
        </div>

        {/* Technical Details (collapsible) */}
        {error.message && (
          <details className="text-left">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
              Technical details
            </summary>
            <div className="mt-2 rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-red-600 font-mono break-words">
                {error.message}
              </p>
              {error.digest && (
                <p className="mt-2 text-xs text-gray-500">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
          </details>
        )}

        {/* Recovery Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md hover:shadow-lg"
          >
            <RefreshCw className="w-5 h-5" aria-hidden="true" />
            Try Again
          </button>

          <Link
            href="/coaching"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium shadow-sm"
          >
            <Home className="w-5 h-5" aria-hidden="true" />
            New Session
          </Link>

          <Link
            href="/coaching/history"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium shadow-sm"
          >
            View History
          </Link>
        </div>

        {/* Help Text */}
        <p className="text-sm text-gray-500">
          If this problem persists, please contact support with the error ID above.
        </p>
      </div>
    </div>
  );
}
