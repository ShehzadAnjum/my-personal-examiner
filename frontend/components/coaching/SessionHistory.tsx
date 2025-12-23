/**
 * SessionHistory Component
 *
 * Display list of past coaching sessions with filtering, sorting, and pagination.
 *
 * Features:
 * - List of past sessions (SessionListItem components)
 * - Filter by outcome (resolved/needs_more_help/refer_to_teacher)
 * - Sort by date (newest/oldest)
 * - Pagination or infinite scroll for 20+ sessions
 * - Empty state when no sessions
 * - Loading and error states
 * - Accessible (ARIA roles, keyboard navigation)
 */

'use client';

import { useState, useEffect } from 'react';
import { Filter, SortDesc } from 'lucide-react';
import { SessionListItem } from './SessionListItem';
import { EmptyHistory } from './EmptyHistory';
import { SessionHistorySkeleton } from './SessionHistorySkeleton';
import { useSessions } from '@/lib/api/coaching';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { trackEvent } from '@/lib/analytics';

type OutcomeFilter = 'all' | 'resolved' | 'needs_more_help' | 'refer_to_teacher';
type SortOrder = 'newest' | 'oldest';

export function SessionHistory() {
  const [outcomeFilter, setOutcomeFilter] = useState<OutcomeFilter>('all');
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');
  const [showFilterMenu, setShowFilterMenu] = useState(false);

  // Fetch sessions from API
  const { data, isLoading, error } = useSessions();

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'Escape': () => {
      if (showFilterMenu) {
        setShowFilterMenu(false);
      }
    },
  });

  const sessions = data?.sessions || [];
  const total = data?.total || 0;

  // Track analytics when history is viewed
  useEffect(() => {
    if (!isLoading && sessions.length > 0) {
      trackEvent('coaching_history_viewed', {
        total_sessions: total,
        visible_sessions: sessions.length,
      });
    }
  }, [isLoading, sessions.length, total]);

  // Apply filters
  const filteredSessions = sessions.filter((session) => {
    if (outcomeFilter === 'all') return true;
    return session.outcome === outcomeFilter;
  });

  // Apply sorting
  const sortedSessions = [...filteredSessions].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();

    return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
  });

  // Loading state
  if (isLoading) {
    return <SessionHistorySkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <p className="text-red-600">Failed to load coaching history</p>
          <p className="text-sm text-gray-600">
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (sessions.length === 0) {
    return <EmptyHistory />;
  }

  // No results after filtering
  if (filteredSessions.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-3">
          <p className="text-gray-600">No sessions match your filter</p>
          <button
            onClick={() => setOutcomeFilter('all')}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Clear Filter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="max-w-4xl mx-auto p-6"
      data-testid="session-history"
      role="region"
      aria-label="Coaching session history"
    >
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Coaching History</h1>
        <p className="text-gray-600 mt-2">
          Review your past coaching sessions ({total} total)
        </p>
      </div>

      {/* Filters and Sorting */}
      <div className="flex items-center justify-between mb-6">
        {/* Outcome Filter */}
        <div className="relative">
          <button
            onClick={() => setShowFilterMenu(!showFilterMenu)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            data-testid="outcome-filter"
            aria-label="Filter by outcome"
            aria-haspopup="true"
            aria-expanded={showFilterMenu}
          >
            <Filter className="w-4 h-4" aria-hidden="true" />
            <span>
              Filter:{' '}
              {outcomeFilter === 'all'
                ? 'All'
                : outcomeFilter === 'resolved'
                ? 'Resolved'
                : outcomeFilter === 'needs_more_help'
                ? 'Needs Help'
                : 'Refer to Teacher'}
            </span>
          </button>

          {/* Filter Dropdown */}
          {showFilterMenu && (
            <div
              className="absolute top-full mt-2 left-0 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[200px]"
              role="menu"
            >
              <button
                onClick={() => {
                  setOutcomeFilter('all');
                  setShowFilterMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
                role="menuitem"
              >
                All Sessions
              </button>
              <button
                onClick={() => {
                  setOutcomeFilter('resolved');
                  setShowFilterMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
                role="menuitem"
              >
                Resolved
              </button>
              <button
                onClick={() => {
                  setOutcomeFilter('needs_more_help');
                  setShowFilterMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
                role="menuitem"
              >
                Needs More Help
              </button>
              <button
                onClick={() => {
                  setOutcomeFilter('refer_to_teacher');
                  setShowFilterMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
                role="menuitem"
              >
                Refer to Teacher
              </button>
            </div>
          )}
        </div>

        {/* Sort Order */}
        <button
          onClick={() => setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest')}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          aria-label={`Sort by ${sortOrder === 'newest' ? 'oldest' : 'newest'} first`}
        >
          <SortDesc className="w-4 h-4" aria-hidden="true" />
          <span>{sortOrder === 'newest' ? 'Newest First' : 'Oldest First'}</span>
        </button>
      </div>

      {/* Session List */}
      <div className="space-y-3" role="list" aria-label="Coaching sessions">
        {sortedSessions.map((session) => (
          <SessionListItem
            key={session.id}
            id={session.id}
            topic={session.topic}
            createdAt={session.created_at}
            outcome={session.outcome as any}
            messageCount={session.message_count}
          />
        ))}
      </div>

      {/* Pagination placeholder (T060) */}
      {total > 20 && (
        <div className="mt-6 flex justify-center">
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            aria-label="Load more sessions"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
