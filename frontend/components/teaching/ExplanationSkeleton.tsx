import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading skeleton for ExplanationView component
 *
 * Mimics the structure of a full explanation with 9 sections:
 * - Definition, Core Principles, Related Concepts (always expanded)
 * - Key Terms, Examples, Visual Aids, Worked Examples, Misconceptions, Practice (collapsed)
 *
 * Uses pulse animation to indicate loading state.
 *
 * @example
 * ```tsx
 * {isLoading ? (
 *   <ExplanationSkeleton />
 * ) : (
 *   <ExplanationView explanation={data} />
 * )}
 * ```
 */
export function ExplanationSkeleton() {
  return (
    <div className="space-y-6 animate-in fade-in-50 duration-500">
      {/* Header Section */}
      <div className="space-y-3">
        <Skeleton className="h-10 w-3/4" /> {/* Concept name */}
        <Skeleton className="h-4 w-1/2" /> {/* Syllabus code */}
      </div>

      {/* Bookmark Button */}
      <div className="flex justify-end">
        <Skeleton className="h-10 w-40" />
      </div>

      {/* Section 1: Definition (Always Expanded) */}
      <div className="border rounded-lg p-4 space-y-3">
        <Skeleton className="h-6 w-32" /> {/* Section title */}
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>

      {/* Section 2: Key Terms (Collapsed - just header) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-40" />
      </div>

      {/* Section 3: Core Principles (Always Expanded) */}
      <div className="border rounded-lg p-4 space-y-3">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>

      {/* Section 4: Real-World Examples (Collapsed) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-52" />
      </div>

      {/* Section 5: Visual Aids (Collapsed) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-36" />
      </div>

      {/* Section 6: Worked Examples (Collapsed) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-44" />
      </div>

      {/* Section 7: Common Misconceptions (Collapsed) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-56" />
      </div>

      {/* Section 8: Practice Problems (Collapsed) */}
      <div className="border rounded-lg p-4">
        <Skeleton className="h-6 w-48" />
      </div>

      {/* Section 9: Related Concepts (Always Expanded) */}
      <div className="border rounded-lg p-4 space-y-3">
        <Skeleton className="h-6 w-44" />
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-8 w-24" /> {/* Topic tag */}
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-8 w-28" />
        </div>
      </div>
    </div>
  );
}

/**
 * Compact skeleton for explanation preview in lists
 * Shows minimal structure (title + first section)
 *
 * @example
 * ```tsx
 * <ExplanationSkeletonCompact />
 * ```
 */
export function ExplanationSkeletonCompact() {
  return (
    <div className="space-y-4 animate-in fade-in-50 duration-300">
      <div className="space-y-2">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-1/3" />
      </div>
      <div className="border rounded-lg p-4 space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    </div>
  );
}
