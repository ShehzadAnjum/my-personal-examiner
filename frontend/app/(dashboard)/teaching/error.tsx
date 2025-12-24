/**
 * Teaching Route Error Boundary
 *
 * Catches errors in the teaching section and displays a teaching-specific
 * error UI with helpful recovery actions.
 *
 * Route: /teaching/** (all teaching routes)
 * Purpose: Graceful error handling for topic explanations and learning sessions
 *
 * Features:
 * - User-friendly error messages
 * - Technical details (collapsible)
 * - Retry option
 * - Navigation to safe routes (browse topics, saved explanations, home)
 * - Error logging for monitoring
 *
 * Pattern: Reused from 004-coaching-page error boundary
 */

'use client';

import { useEffect } from 'react';
import { AlertCircle, Home, RefreshCw, BookOpen } from 'lucide-react';
import Link from 'next/link';

export default function TeachingError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to error reporting service (e.g., Sentry, Datadog)
    console.error('Teaching error boundary caught:', error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-6">
      <div className="max-w-lg space-y-6 text-center">
        {/* Error Icon */}
        <div className="flex justify-center">
          <div className="rounded-full bg-red-100 p-6 dark:bg-red-900/20">
            <AlertCircle
              className="h-12 w-12 text-red-600 dark:text-red-400"
              aria-hidden="true"
            />
          </div>
        </div>

        {/* Error Message */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Explanation Loading Error
          </h1>
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            We encountered an issue while loading your explanation. This could be due to a
            network problem, an invalid topic, or a temporary server issue. Don't worry -
            your saved explanations are safe!
          </p>
        </div>

        {/* Technical Details (collapsible) */}
        {error.message && (
          <details className="text-left">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
              Technical details
            </summary>
            <div className="mt-2 rounded-lg bg-gray-50 dark:bg-gray-800 p-4">
              <p className="text-sm text-red-600 dark:text-red-400 font-mono break-words">
                {error.message}
              </p>
              {error.digest && (
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
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
            href="/teaching"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium shadow-sm"
          >
            <BookOpen className="w-5 h-5" aria-hidden="true" />
            Browse Topics
          </Link>

          <Link
            href="/teaching/saved"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium shadow-sm"
          >
            View Saved
          </Link>

          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium shadow-sm"
          >
            <Home className="w-5 h-5" aria-hidden="true" />
            Home
          </Link>
        </div>

        {/* Help Text */}
        <p className="text-sm text-gray-500 dark:text-gray-400">
          If this problem persists, please try browsing topics or contact support with the
          error ID above.
        </p>
      </div>
    </div>
  );
}
