/**
 * useBookmark Hook
 *
 * TanStack Query mutation hooks for saving and removing bookmarked explanations.
 *
 * Feature: 005-teaching-page (User Story 3: Bookmark Explanations)
 *
 * Cache Invalidation Strategy:
 * - On save: Invalidate ['savedExplanations'] to refresh list
 * - On remove: Invalidate ['savedExplanations'] to refresh list
 * - Optimistic updates: Immediately update UI before server response
 * - Rollback on error: Revert optimistic update if mutation fails
 *
 * Constitutional Compliance:
 * - Principle V: Multi-tenant isolation (student_id enforced by backend)
 * - Principle VI: Constructive feedback (preserves full TopicExplanation JSON)
 * - FR-012: Prevent duplicate bookmarks (unique constraint on backend)
 */

'use client';

import {
  useMutation,
  useQueryClient,
  UseMutationResult,
} from '@tanstack/react-query';
import * as teachingApi from '@/lib/api/teaching';
import { TopicExplanation, SavedExplanation } from '@/lib/types/teaching';

/**
 * Save an explanation as a bookmark
 *
 * @returns TanStack Query mutation with saveExplanation function
 *
 * @example
 * // In ExplanationView component
 * const { mutate: saveExplanation, isPending } = useSaveBookmark();
 *
 * const handleBookmark = () => {
 *   saveExplanation(
 *     { syllabusPointId: topicId, explanation },
 *     {
 *       onSuccess: () => toast.success('Explanation saved!'),
 *       onError: (error) => toast.error(error.message),
 *     }
 *   );
 * };
 *
 * @example
 * // With optimistic updates
 * const { mutate: saveExplanation } = useSaveBookmark();
 * saveExplanation({ syllabusPointId, explanation });
 * // UI updates immediately before server confirms
 */
export function useSaveBookmark(): UseMutationResult<
  SavedExplanation,
  Error,
  { syllabusPointId: string; explanation: TopicExplanation }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ syllabusPointId }) =>
      teachingApi.saveExplanation(syllabusPointId),

    // Optimistic update: Add to cache immediately
    onMutate: async ({ syllabusPointId, explanation }) => {
      // Cancel outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['savedExplanations'] });

      // Snapshot previous value for rollback
      const previousSaved = queryClient.getQueryData<SavedExplanation[]>([
        'savedExplanations',
      ]);

      // Optimistically add new saved explanation to cache
      queryClient.setQueryData<SavedExplanation[]>(
        ['savedExplanations'],
        (old = []) => [
          ...old,
          {
            id: 'temp-' + Date.now(), // Temporary ID until server responds
            student_id: 'TEMP_STUDENT_ID',
            syllabus_point_id: syllabusPointId,
            explanation_content: explanation,
            date_saved: new Date().toISOString(),
            date_last_viewed: null,
          },
        ]
      );

      return { previousSaved };
    },

    // On error: Rollback optimistic update
    onError: (error, variables, context) => {
      if (context?.previousSaved) {
        queryClient.setQueryData(
          ['savedExplanations'],
          context.previousSaved
        );
      }
    },

    // On success: Replace optimistic data with server response
    onSuccess: (data) => {
      // Invalidate saved explanations to fetch fresh data
      queryClient.invalidateQueries({ queryKey: ['savedExplanations'] });
    },
  });
}

/**
 * Remove a saved explanation (unbookmark)
 *
 * @returns TanStack Query mutation with removeBookmark function
 *
 * @example
 * // In SavedExplanationCard component
 * const { mutate: removeBookmark, isPending } = useRemoveBookmark();
 *
 * const handleRemove = () => {
 *   removeBookmark(
 *     savedExplanationId,
 *     {
 *       onSuccess: () => toast.success('Bookmark removed'),
 *       onError: (error) => toast.error(error.message),
 *     }
 *   );
 * };
 *
 * @example
 * // With confirmation dialog
 * const { mutate: removeBookmark } = useRemoveBookmark();
 * const handleRemove = async () => {
 *   if (confirm('Remove this bookmark?')) {
 *     removeBookmark(savedExplanationId);
 *   }
 * };
 */
export function useRemoveBookmark(): UseMutationResult<
  { success: boolean },
  Error,
  string
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (savedExplanationId: string) =>
      teachingApi.removeSavedExplanation(savedExplanationId),

    // Optimistic update: Remove from cache immediately
    onMutate: async (savedExplanationId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['savedExplanations'] });

      // Snapshot previous value for rollback
      const previousSaved = queryClient.getQueryData<SavedExplanation[]>([
        'savedExplanations',
      ]);

      // Optimistically remove from cache
      queryClient.setQueryData<SavedExplanation[]>(
        ['savedExplanations'],
        (old = []) => old.filter((s) => s.id !== savedExplanationId)
      );

      return { previousSaved };
    },

    // On error: Rollback optimistic update
    onError: (error, variables, context) => {
      if (context?.previousSaved) {
        queryClient.setQueryData(
          ['savedExplanations'],
          context.previousSaved
        );
      }
    },

    // On success: Invalidate to ensure consistency
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedExplanations'] });
    },
  });
}

/**
 * Toggle bookmark status (save if not bookmarked, remove if bookmarked)
 *
 * Convenience hook that combines save and remove mutations.
 *
 * @example
 * // In ExplanationView component
 * const { toggle, isPending, isBookmarked } = useToggleBookmark(topicId);
 *
 * return (
 *   <Button onClick={() => toggle(explanation)} disabled={isPending}>
 *     {isBookmarked ? '★ Saved' : '☆ Save'}
 *   </Button>
 * );
 */
export function useToggleBookmark(syllabusPointId: string): {
  toggle: (explanation: TopicExplanation) => void;
  isPending: boolean;
  isBookmarked: boolean;
  savedExplanationId: string | null;
} {
  const queryClient = useQueryClient();
  const { mutate: saveExplanation, isPending: isSaving } = useSaveBookmark();
  const { mutate: removeBookmark, isPending: isRemoving } =
    useRemoveBookmark();

  // Check if currently bookmarked
  const savedExplanations =
    queryClient.getQueryData<SavedExplanation[]>(['savedExplanations']) || [];
  const saved = savedExplanations.find(
    (s) => s.syllabus_point_id === syllabusPointId
  );

  const toggle = (explanation: TopicExplanation) => {
    if (saved) {
      // Already bookmarked → remove
      removeBookmark(saved.id);
    } else {
      // Not bookmarked → save
      saveExplanation({ syllabusPointId, explanation });
    }
  };

  return {
    toggle,
    isPending: isSaving || isRemoving,
    isBookmarked: !!saved,
    savedExplanationId: saved?.id || null,
  };
}
