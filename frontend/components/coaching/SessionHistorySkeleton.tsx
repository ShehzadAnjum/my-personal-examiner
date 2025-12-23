/**
 * SessionHistorySkeleton Component
 *
 * Skeleton loading state for SessionHistory while sessions are loading.
 *
 * Features:
 * - Simulates list of session cards
 * - Shimmer animation
 * - Accessible loading state
 */

'use client';

import { Skeleton } from '@/components/ui/skeleton';

export function SessionHistorySkeleton() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header skeleton */}
      <div className="mb-6">
        <Skeleton className="h-9 w-64 mb-2" /> {/* Title */}
        <Skeleton className="h-5 w-96" /> {/* Description */}
      </div>

      {/* Filters skeleton */}
      <div className="flex items-center justify-between mb-6">
        <Skeleton className="h-10 w-40 rounded-lg" /> {/* Filter button */}
        <Skeleton className="h-10 w-40 rounded-lg" /> {/* Sort button */}
      </div>

      {/* Session list skeleton */}
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between gap-4">
              {/* Left side: topic and metadata */}
              <div className="flex-1 space-y-2">
                <Skeleton className="h-6 w-3/4" /> {/* Topic */}
                <div className="flex items-center gap-4">
                  <Skeleton className="h-4 w-32" /> {/* Date */}
                  <Skeleton className="h-4 w-24" /> {/* Message count */}
                </div>
              </div>

              {/* Right side: outcome badge */}
              <Skeleton className="h-6 w-24 rounded-full" /> {/* Outcome badge */}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination skeleton (optional) */}
      <div className="mt-6 flex justify-center">
        <Skeleton className="h-10 w-32 rounded-lg" /> {/* Load more button */}
      </div>
    </div>
  );
}
