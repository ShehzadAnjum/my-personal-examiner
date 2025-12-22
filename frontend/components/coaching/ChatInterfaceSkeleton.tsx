/**
 * ChatInterfaceSkeleton Component
 *
 * Skeleton loading state for ChatInterface while session data loads.
 *
 * Features:
 * - Simulates chat message bubbles
 * - Shimmer animation
 * - Accessible loading state
 */

'use client';

import { Skeleton } from '@/components/ui/skeleton';

export function ChatInterfaceSkeleton() {
  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header skeleton */}
      <div className="border-b p-4 flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-6 w-48" /> {/* Topic */}
          <Skeleton className="h-4 w-32" /> {/* Status */}
        </div>
        <Skeleton className="h-10 w-32 rounded-md" /> {/* Button */}
      </div>

      {/* Messages skeleton */}
      <div className="flex-1 overflow-hidden p-4 space-y-4">
        {/* Coach message (left aligned) */}
        <div className="flex items-start gap-3">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" /> {/* Avatar */}
          <div className="space-y-2 max-w-[70%]">
            <Skeleton className="h-4 w-20" /> {/* Name */}
            <Skeleton className="h-20 w-full rounded-lg" /> {/* Message bubble */}
            <Skeleton className="h-3 w-16" /> {/* Timestamp */}
          </div>
        </div>

        {/* Student message (right aligned) */}
        <div className="flex items-start gap-3 justify-end">
          <div className="space-y-2 max-w-[70%]">
            <Skeleton className="h-4 w-16 ml-auto" /> {/* Name */}
            <Skeleton className="h-16 w-full rounded-lg" /> {/* Message bubble */}
            <Skeleton className="h-3 w-16 ml-auto" /> {/* Timestamp */}
          </div>
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" /> {/* Avatar */}
        </div>

        {/* Coach message */}
        <div className="flex items-start gap-3">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="space-y-2 max-w-[70%]">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-24 w-full rounded-lg" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      </div>

      {/* Input skeleton */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Skeleton className="h-12 flex-1 rounded-md" /> {/* Input */}
          <Skeleton className="h-12 w-12 rounded-md" /> {/* Send button */}
        </div>
      </div>
    </div>
  );
}
