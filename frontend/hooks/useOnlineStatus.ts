/**
 * Hook: Detect online/offline status
 *
 * Monitors browser network connectivity using navigator.onLine API
 * and window online/offline events.
 *
 * Usage:
 * ```tsx
 * const isOnline = useOnlineStatus();
 * if (!isOnline) {
 *   return <OfflineBanner />;
 * }
 * ```
 */

'use client';

import { useState, useEffect } from 'react';

export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
