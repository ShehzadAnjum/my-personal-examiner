/**
 * TopicCard Component
 *
 * Displays a syllabus topic in a clickable card format for the topic browser.
 *
 * Features:
 * - Topic code badge (e.g., "9708.3.1.2")
 * - Description text
 * - Learning outcomes preview (first 2 outcomes)
 * - Optional remove button (for saved topics list)
 * - Hover effects for interactivity
 * - Keyboard navigation support
 *
 * Usage Context:
 * - TopicBrowser: Display all syllabus topics for browsing
 * - TopicSearch: Display filtered search results
 * - SavedTopics: Display bookmarked topics with remove option
 *
 * @example
 * ```tsx
 * <TopicCard
 *   topic={syllabusPoint}
 *   onClick={() => router.push(`/teaching/${topic.id}`)}
 * />
 * ```
 *
 * @example
 * ```tsx
 * // With remove button (saved topics)
 * <TopicCard
 *   topic={syllabusPoint}
 *   onClick={() => viewExplanation(topic.id)}
 *   showRemoveButton
 *   onRemove={() => removeTopic(topic.id)}
 * />
 * ```
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, ChevronRight, BookOpen, CheckCircle2 } from 'lucide-react';
import type { SyllabusTopic } from '@/lib/types/teaching';

export interface TopicCardProps {
  topic: SyllabusTopic;
  onClick: () => void;
  showRemoveButton?: boolean;
  onRemove?: () => void;
}

export function TopicCard({
  topic,
  onClick,
  showRemoveButton = false,
  onRemove,
}: TopicCardProps) {
  // Check if topic has cached explanation in localStorage
  const [hasExplanation, setHasExplanation] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const cached = localStorage.getItem(`explanation_${topic.id}`);
      setHasExplanation(!!cached);
    }
  }, [topic.id]);

  // Parse learning outcomes (newline-separated string)
  const learningOutcomes = topic.learning_outcomes
    ? topic.learning_outcomes.split('\n').filter((line) => line.trim().length > 0)
    : [];

  // Preview: show first 2 learning outcomes
  const outcomesPreview = learningOutcomes.slice(0, 2);
  const hasMoreOutcomes = learningOutcomes.length > 2;

  return (
    <Card
      className="group relative cursor-pointer transition-all hover:shadow-md hover:border-primary/50 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2"
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`View explanation for ${topic.code}: ${topic.description}`}
    >
      {/* Remove Button (Saved Topics) */}
      {showRemoveButton && onRemove && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity z-10"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          aria-label={`Remove ${topic.code} from saved topics`}
        >
          <X className="h-4 w-4" />
        </Button>
      )}

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          {/* Topic Code Badge */}
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-primary" aria-hidden="true" />
            <span className="inline-flex items-center rounded-md bg-primary/10 px-2.5 py-1 text-sm font-semibold text-primary font-mono">
              {topic.code}
            </span>

            {/* Already Generated Indicator */}
            {hasExplanation && (
              <div className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-green-500/10 border border-green-500/20">
                <CheckCircle2 className="h-3.5 w-3.5 text-green-600 dark:text-green-400" />
                <span className="text-xs font-medium text-green-600 dark:text-green-400">
                  Explained
                </span>
              </div>
            )}
          </div>

          {/* Arrow Icon (indicates clickable) */}
          <ChevronRight
            className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors"
            aria-hidden="true"
          />
        </div>

        {/* Description */}
        <h3 className="text-base font-semibold leading-tight mt-2 group-hover:text-primary transition-colors">
          {topic.description}
        </h3>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Learning Outcomes Preview */}
        {outcomesPreview.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Learning Outcomes
            </p>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {outcomesPreview.map((outcome, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-primary mt-1.5 block h-1 w-1 rounded-full bg-primary flex-shrink-0" />
                  <span className="flex-1 leading-relaxed">{outcome.trim()}</span>
                </li>
              ))}
            </ul>

            {/* "More Outcomes" Indicator */}
            {hasMoreOutcomes && (
              <p className="text-xs text-muted-foreground italic mt-2">
                + {learningOutcomes.length - 2} more outcome
                {learningOutcomes.length - 2 !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        )}

        {/* Topics Field (if exists) */}
        {topic.topics && (
          <div className="mt-3 pt-3 border-t">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
              Topics Covered
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {topic.topics}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Compact variant of TopicCard for dense lists
 *
 * Shows only code and description, no learning outcomes.
 * Useful for search results or lists with many items.
 *
 * @example
 * ```tsx
 * <TopicCardCompact
 *   topic={syllabusPoint}
 *   onClick={() => router.push(`/teaching/${topic.id}`)}
 * />
 * ```
 */
export function TopicCardCompact({
  topic,
  onClick,
}: Omit<TopicCardProps, 'showRemoveButton' | 'onRemove'>) {
  return (
    <div
      className="group flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all hover:shadow-sm hover:border-primary/50 hover:bg-accent/50"
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`View explanation for ${topic.code}: ${topic.description}`}
    >
      <BookOpen className="h-4 w-4 text-primary flex-shrink-0" aria-hidden="true" />

      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-semibold font-mono text-primary">
            {topic.code}
          </span>
          <span className="text-sm truncate">{topic.description}</span>
        </div>
      </div>

      <ChevronRight
        className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0"
        aria-hidden="true"
      />
    </div>
  );
}
