/**
 * TopicSearchSkeleton Component
 *
 * Loading skeleton for TopicSearch component with pulse animation.
 * Mimics the structure of search bar + topic results grid.
 *
 * Features:
 * - Search bar skeleton with search icon
 * - Result count skeleton
 * - Topic card skeletons in list layout
 * - Pulse animation to indicate loading
 *
 * Usage Context:
 * - Display while topics are being fetched from API
 * - Display while search is debouncing (optional)
 * - Replaces TopicSearch component during loading state
 *
 * @example
 * ```tsx
 * const { data: topics, isLoading } = useTopics({ subject_code: '9708' });
 *
 * {isLoading ? (
 *   <TopicSearchSkeleton />
 * ) : (
 *   <TopicSearch topics={topics} onSelectTopic={handleSelect} />
 * )}
 * ```
 */

import { Skeleton } from '@/components/ui/skeleton';
import { Search } from 'lucide-react';

export interface TopicSearchSkeletonProps {
  /** Number of skeleton topic cards to show (default: 5) */
  count?: number;
}

export function TopicSearchSkeleton({ count = 5 }: TopicSearchSkeletonProps) {
  return (
    <div className="space-y-4 animate-in fade-in-50 duration-500">
      {/* Search Input Skeleton */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground animate-pulse" />
        <Skeleton className="h-10 w-full rounded-md" />
      </div>

      {/* Result Count Skeleton */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-48" />
      </div>

      {/* Topic Results Skeletons */}
      <div className="space-y-2">
        {Array.from({ length: count }).map((_, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-3 border rounded-lg"
          >
            <div className="flex-1 space-y-2">
              {/* Topic code + description skeleton */}
              <div className="flex items-baseline gap-2">
                <Skeleton className="h-4 w-20" /> {/* Code */}
                <Skeleton className="h-4 w-full" /> {/* Description */}
              </div>

              {/* Learning outcome preview skeleton (occasional) */}
              {index % 3 === 0 && <Skeleton className="h-3 w-3/4" />}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Compact variant of TopicSearchSkeleton
 * Smaller skeleton for embedded search components
 *
 * @example
 * ```tsx
 * <TopicSearchSkeletonCompact count={3} />
 * ```
 */
export function TopicSearchSkeletonCompact({ count = 3 }: TopicSearchSkeletonProps) {
  return (
    <div className="space-y-3 animate-in fade-in-50 duration-300">
      {/* Search Input Skeleton */}
      <Skeleton className="h-9 w-full rounded-md" />

      {/* Topic Results Skeletons (compact) */}
      <div className="space-y-1.5">
        {Array.from({ length: count }).map((_, index) => (
          <div
            key={index}
            className="flex items-center gap-2 p-2 border rounded-md"
          >
            <Skeleton className="h-3 w-16" /> {/* Code */}
            <Skeleton className="h-3 w-full" /> {/* Description */}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Grid variant of TopicSearchSkeleton
 * For search results displayed in grid layout instead of list
 *
 * @example
 * ```tsx
 * <TopicSearchSkeletonGrid count={6} columns={2} />
 * ```
 */
export interface TopicSearchSkeletonGridProps extends TopicSearchSkeletonProps {
  /** Number of columns in grid (default: 2) */
  columns?: number;
}

export function TopicSearchSkeletonGrid({
  count = 6,
  columns = 2,
}: TopicSearchSkeletonGridProps) {
  const gridCols = columns === 1 ? 'grid-cols-1' : columns === 3 ? 'grid-cols-3' : 'grid-cols-2';

  return (
    <div className="space-y-4 animate-in fade-in-50 duration-500">
      {/* Search Input Skeleton */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground animate-pulse" />
        <Skeleton className="h-10 w-full rounded-md" />
      </div>

      {/* Result Count Skeleton */}
      <Skeleton className="h-4 w-48" />

      {/* Topic Grid Skeletons */}
      <div className={`grid ${gridCols} gap-4`}>
        {Array.from({ length: count }).map((_, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-3">
            {/* Header */}
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-20" /> {/* Code badge */}
              <Skeleton className="h-4 w-4 rounded-full" /> {/* Icon */}
            </div>

            {/* Description */}
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-4/5" />

            {/* Learning outcomes preview */}
            <div className="space-y-1.5">
              <Skeleton className="h-3 w-32" /> {/* Label */}
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-5/6" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
