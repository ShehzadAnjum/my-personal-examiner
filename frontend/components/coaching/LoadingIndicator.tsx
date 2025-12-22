/**
 * LoadingIndicator Component
 *
 * Displays a loading state while the coach prepares the session.
 *
 * Features:
 * - Animated spinner
 * - Descriptive text
 * - Accessible (aria-live, role)
 */

'use client';

export function LoadingIndicator() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] space-y-4"
      role="status"
      aria-live="polite"
    >
      <div className="relative w-16 h-16">
        <div className="absolute top-0 left-0 w-full h-full border-4 border-primary/20 rounded-full"></div>
        <div className="absolute top-0 left-0 w-full h-full border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div className="text-center space-y-2">
        <p className="text-lg font-medium">Coach is preparing your session...</p>
        <p className="text-sm text-muted-foreground">
          This usually takes a few seconds
        </p>
      </div>
      <span className="sr-only">Loading coaching session</span>
    </div>
  );
}
