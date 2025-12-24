/**
 * SavedExplanationsList Component
 *
 * Displays a list of bookmarked explanations with remove functionality.
 *
 * Feature: 005-teaching-page (User Story 3: Bookmark Explanations)
 *
 * Architecture:
 * - Uses useSavedExplanations hook for data fetching
 * - Uses useRemoveBookmark hook for delete mutations
 * - Loads explanation content from localStorage cache
 * - Displays "Regenerate" button if cache missing
 *
 * States:
 * - Loading: Skeleton cards with pulse animation
 * - Empty: Message encouraging user to bookmark topics
 * - Success: Grid of TopicCards with remove buttons
 * - Error: Error boundary handles failures
 *
 * @example
 * ```tsx
 * import { SavedExplanationsList } from '@/components/teaching/SavedExplanationsList';
 *
 * export default function SavedPage() {
 *   return <SavedExplanationsList />;
 * }
 * ```
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookmarkIcon, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useSavedExplanations } from '@/lib/hooks/useSavedExplanations';
import { useRemoveBookmark } from '@/lib/hooks/useBookmark';
import { useToast } from '@/lib/hooks/use-toast';
import type { SavedExplanation, TopicExplanation } from '@/lib/types/teaching';

// Enriched type with cached explanation content
interface SavedExplanationWithContent extends SavedExplanation {
  explanation?: TopicExplanation; // Loaded from localStorage
  hasCachedContent: boolean;
}

/**
 * Saved Explanations List Component
 *
 * Renders bookmarked explanations with:
 * - Topic card display with explanation preview
 * - View/Regenerate buttons
 * - Remove bookmark button
 * - Empty state guidance
 * - Loading skeleton
 */
export function SavedExplanationsList() {
  const router = useRouter();
  const { toast } = useToast();
  const [enrichedExplanations, setEnrichedExplanations] = useState<SavedExplanationWithContent[]>([]);

  // TanStack Query hooks
  const { data: savedExplanations = [], isLoading, error } = useSavedExplanations();
  const { mutate: removeBookmark, isPending: isRemoving } = useRemoveBookmark();

  /**
   * Load explanation from localStorage cache
   * Handles both old format (direct TopicExplanation) and new format (with versions)
   */
  const loadExplanationFromCache = (syllabusPointId: string): TopicExplanation | null => {
    try {
      const cached = localStorage.getItem(`explanation_${syllabusPointId}`);
      if (!cached) return null;

      const parsed = JSON.parse(cached);
      // Handle both old format (direct TopicExplanation) and new format (with versions)
      return parsed.explanation || parsed;
    } catch (err) {
      console.error('Failed to load explanation from cache:', err);
      return null;
    }
  };

  /**
   * Enrich saved explanations with cached content
   * Runs whenever savedExplanations changes (after TanStack Query fetch)
   */
  useEffect(() => {
    const enriched: SavedExplanationWithContent[] = savedExplanations.map((bookmark: SavedExplanation) => {
      const cachedExplanation = loadExplanationFromCache(bookmark.syllabus_point_id);
      return {
        ...bookmark,
        explanation: cachedExplanation || undefined,
        hasCachedContent: !!cachedExplanation,
      };
    });

    setEnrichedExplanations(enriched);
  }, [savedExplanations]);

  /**
   * Remove saved explanation with optimistic update
   * Uses TanStack Query mutation with automatic cache invalidation
   */
  const handleRemove = (id: string, conceptName?: string) => {
    removeBookmark(id, {
      onSuccess: () => {
        toast({
          title: 'Bookmark removed',
          description: conceptName ? `"${conceptName}" removed from saved explanations` : 'Explanation removed from saved list',
        });
      },
      onError: (error) => {
        toast({
          variant: 'destructive',
          title: 'Failed to remove bookmark',
          description: error.message || 'Please try again',
        });
      },
    });
  };

  /**
   * Navigate to explanation page
   * If content is cached, view immediately
   * If not cached, trigger regeneration
   */
  const handleView = (syllabusPointId: string) => {
    router.push(`/teaching/${syllabusPointId}`);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="border border-destructive/50 rounded-lg p-6 bg-destructive/10">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-6 w-6 text-destructive mt-1" />
          <div className="flex-1 space-y-2">
            <h2 className="text-xl font-semibold text-destructive">
              Failed to Load Saved Explanations
            </h2>
            <p className="text-sm text-muted-foreground">
              {error instanceof Error ? error.message : 'An error occurred while loading your saved explanations'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (enrichedExplanations.length === 0) {
    return (
      <Card className="p-12 text-center">
        <BookmarkIcon className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
        <h2 className="text-xl font-semibold mb-2">No Saved Explanations</h2>
        <p className="text-muted-foreground mb-6">
          You haven't bookmarked any explanations yet. Click "Save for Later" on any explanation to add it here.
        </p>
        <Button onClick={() => router.push('/teaching')}>
          Browse Topics
        </Button>
      </Card>
    );
  }

  // Success state: Display saved explanations
  return (
    <>
      <div className="space-y-4">
        {enrichedExplanations.map((saved) => (
          <Card key={saved.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                {saved.hasCachedContent && saved.explanation ? (
                  <>
                    <h3 className="text-lg font-semibold mb-2">
                      {saved.explanation.concept_name}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                      {saved.explanation.definition}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>Saved {new Date(saved.date_saved).toLocaleDateString()}</span>
                      <span>•</span>
                      <span className="font-mono">{saved.explanation.syllabus_code}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-semibold mb-2 text-muted-foreground">
                      Bookmarked Topic
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      Explanation content not cached. Click "Regenerate" to load this topic again.
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>Saved {new Date(saved.date_saved).toLocaleDateString()}</span>
                    </div>
                  </>
                )}
              </div>
              <div className="flex flex-col gap-2">
                {saved.hasCachedContent ? (
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => handleView(saved.syllabus_point_id)}
                  >
                    View
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleView(saved.syllabus_point_id)}
                    className="gap-2"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    Regenerate
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemove(saved.id, saved.explanation?.concept_name)}
                  disabled={isRemoving}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Stats */}
      <div className="mt-8 pt-6 border-t text-center text-sm text-muted-foreground">
        {enrichedExplanations.length} saved {enrichedExplanations.length === 1 ? 'explanation' : 'explanations'}
      </div>
    </>
  );
}
