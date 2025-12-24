/**
 * BookmarkButton Component
 *
 * Interactive button for saving/removing explanations as bookmarks.
 *
 * Feature: 005-teaching-page (User Story 3: Bookmark Explanations)
 *
 * States:
 * - Default (not bookmarked): Outlined star icon, "Save Explanation"
 * - Bookmarked: Filled star icon, "Saved", primary color
 * - Loading: Spinner, "Saving..." or "Removing...", disabled
 * - Disabled: Greyed out, not clickable
 *
 * Uses shadcn/ui Button component with variants:
 * - outline: Default state (not bookmarked)
 * - default: Bookmarked state (filled primary)
 *
 * Constitutional Compliance:
 * - Principle VI: Constructive feedback (clear states, instant response)
 * - Accessibility: Keyboard accessible, screen reader announcements
 *
 * @example
 * // With loading state
 * <BookmarkButton
 *   isBookmarked={false}
 *   isLoading={isPending}
 *   onClick={handleBookmark}
 * />
 *
 * @example
 * // Bookmarked state
 * <BookmarkButton
 *   isBookmarked={true}
 *   onClick={handleRemove}
 * />
 */

'use client';

import { Button } from '@/components/ui/button';
import { Bookmark, BookmarkCheck, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BookmarkButtonProps {
  /** Whether explanation is currently bookmarked */
  isBookmarked: boolean;

  /** Whether bookmark action is in progress (saving/removing) */
  isLoading?: boolean;

  /** Click handler for save/remove action */
  onClick: () => void;

  /** Optional CSS class for custom styling */
  className?: string;

  /** Optional size variant */
  size?: 'default' | 'sm' | 'lg' | 'icon';

  /** Show only icon (no text) */
  iconOnly?: boolean;

  /** Disabled state */
  disabled?: boolean;
}

/**
 * Bookmark button with visual feedback for save/remove states
 *
 * Accessibility:
 * - aria-label describes current state and action
 * - Keyboard: Enter/Space to activate
 * - Screen reader: "Save explanation, button" or "Remove bookmark, button"
 * - Loading state announced: "Saving explanation"
 */
export function BookmarkButton({
  isBookmarked,
  isLoading = false,
  onClick,
  className = '',
  size = 'default',
  iconOnly = false,
  disabled = false,
}: BookmarkButtonProps) {
  // Determine button text based on state
  const getButtonText = () => {
    if (isLoading) {
      // If currently bookmarked and loading → user clicked to remove
      // If not bookmarked and loading → user clicked to save
      return isBookmarked ? 'Unsaving...' : 'Saving...';
    }
    return isBookmarked ? '★ Saved' : '☆ Save for Later';
  };

  // Determine icon based on state
  const Icon = isLoading ? Loader2 : isBookmarked ? BookmarkCheck : Bookmark;

  // Determine aria-label for screen readers
  const ariaLabel = isLoading
    ? isBookmarked
      ? 'Removing bookmark'
      : 'Saving explanation'
    : isBookmarked
    ? 'Remove bookmark'
    : 'Save explanation';

  return (
    <Button
      variant={isBookmarked ? 'default' : 'outline'}
      size={size}
      onClick={onClick}
      disabled={isLoading || disabled}
      className={cn(
        'transition-all duration-200',
        isBookmarked && 'bg-primary text-primary-foreground hover:bg-primary/90',
        className
      )}
      aria-label={ariaLabel}
      aria-pressed={isBookmarked}
    >
      <Icon
        className={cn(
          'h-4 w-4',
          !iconOnly && 'mr-2',
          isLoading && 'animate-spin'
        )}
      />
      {!iconOnly && <span>{getButtonText()}</span>}
    </Button>
  );
}

/**
 * Compact bookmark icon button (no text)
 *
 * Use in space-constrained areas like cards or headers.
 *
 * @example
 * <BookmarkIconButton
 *   isBookmarked={isBookmarked}
 *   onClick={handleToggle}
 * />
 */
export function BookmarkIconButton({
  isBookmarked,
  isLoading = false,
  onClick,
  className = '',
  disabled = false,
}: Omit<BookmarkButtonProps, 'size' | 'iconOnly'>) {
  return (
    <BookmarkButton
      isBookmarked={isBookmarked}
      isLoading={isLoading}
      onClick={onClick}
      size="icon"
      iconOnly={true}
      className={className}
      disabled={disabled}
    />
  );
}

/**
 * Bookmark button with count (shows number of times topic is bookmarked)
 *
 * Use for analytics or social proof.
 *
 * @example
 * <BookmarkButtonWithCount
 *   isBookmarked={true}
 *   count={42}
 *   onClick={handleToggle}
 * />
 */
export function BookmarkButtonWithCount({
  isBookmarked,
  isLoading = false,
  onClick,
  count = 0,
  className = '',
  disabled = false,
}: BookmarkButtonProps & { count?: number }) {
  const Icon = isLoading ? Loader2 : isBookmarked ? BookmarkCheck : Bookmark;

  return (
    <Button
      variant={isBookmarked ? 'default' : 'outline'}
      size="default"
      onClick={onClick}
      disabled={isLoading || disabled}
      className={cn(
        'transition-all duration-200 gap-2',
        isBookmarked && 'bg-primary text-primary-foreground hover:bg-primary/90',
        className
      )}
      aria-label={`${isBookmarked ? 'Remove' : 'Save'} bookmark (${count} ${
        count === 1 ? 'student has' : 'students have'
      } saved this)`}
      aria-pressed={isBookmarked}
    >
      <Icon
        className={cn('h-4 w-4', isLoading && 'animate-spin')}
      />
      <span className="text-sm font-medium">{count}</span>
    </Button>
  );
}
