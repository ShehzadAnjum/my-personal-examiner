/**
 * SessionInitFormSkeleton Component
 *
 * Skeleton loading state for SessionInitForm while session is being created.
 *
 * Features:
 * - Matches SessionInitForm structure
 * - Shimmer animation
 * - Accessible loading state
 */

'use client';

import { Skeleton } from '@/components/ui/skeleton';

export function SessionInitFormSkeleton() {
  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="space-y-4">
        {/* Header skeleton */}
        <div className="space-y-2">
          <Skeleton className="h-9 w-64" /> {/* Title */}
          <Skeleton className="h-5 w-96" /> {/* Description */}
        </div>

        {/* Form skeleton */}
        <div className="space-y-4 mt-6">
          <div className="space-y-2">
            <Skeleton className="h-5 w-48" /> {/* Label */}
            <Skeleton className="h-32 w-full rounded-md" /> {/* Textarea */}
            <div className="flex justify-between items-start">
              <Skeleton className="h-4 w-64" /> {/* Hint text */}
              <Skeleton className="h-4 w-16" /> {/* Character count */}
            </div>
          </div>

          {/* Button skeleton */}
          <Skeleton className="h-10 w-48 rounded-md" />
        </div>
      </div>
    </div>
  );
}
