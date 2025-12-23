/**
 * Coaching History Page
 *
 * Display list of all past coaching sessions.
 *
 * Route: /coaching/history
 * Purpose: View and manage coaching session history
 *
 * Features:
 * - List of past sessions
 * - Filter by outcome
 * - Sort by date
 * - Click to view transcript
 */

'use client';

import { SessionHistory } from '@/components/coaching/SessionHistory';
import { ErrorBoundary } from '@/components/coaching/ErrorBoundary';

export default function CoachingHistoryPage() {
  return (
    <ErrorBoundary componentName="SessionHistory">
      <SessionHistory />
    </ErrorBoundary>
  );
}
