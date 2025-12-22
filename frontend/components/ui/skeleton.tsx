/**
 * Skeleton Component
 *
 * Loading placeholder with shimmer animation.
 * Based on shadcn/ui skeleton pattern.
 *
 * Usage:
 *   <Skeleton className="h-12 w-12 rounded-full" />
 *   <Skeleton className="h-4 w-[250px]" />
 */

import { cn } from '@/lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-gray-200', className)}
      {...props}
      aria-busy="true"
      aria-live="polite"
    />
  );
}
