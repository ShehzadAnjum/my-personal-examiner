/**
 * TopicSearch Component
 *
 * Client-side search for syllabus topics with debouncing and keyword highlighting.
 *
 * Features:
 * - Client-side filtering (instant results <1ms for 200 topics)
 * - 300ms debounce to prevent excessive re-renders
 * - Search across: code, description, learning_outcomes
 * - Keyword highlighting with <mark> tag
 * - Result count display
 * - "No results" state with helpful suggestions
 * - Clear search button
 *
 * Performance:
 * - useMemo caching for filtered results
 * - useDebounce hook for input optimization
 * - Array.filter + includes (case-insensitive)
 *
 * @example
 * ```tsx
 * const { data: topics } = useTopics({ subject_code: '9708' });
 *
 * <TopicSearch
 *   topics={topics}
 *   onSelectTopic={(topicId) => router.push(`/teaching/${topicId}`)}
 * />
 * ```
 */

'use client';

import { useState, useMemo, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { TopicCardCompact } from './TopicCard';
import { Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { SyllabusTopic } from '@/lib/types/teaching';

export interface TopicSearchProps {
  topics: SyllabusTopic[];
  onSelectTopic?: (topicId: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

/**
 * Custom debounce hook
 * Delays updating the debounced value until input stops changing for specified delay
 */
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Highlight matching keywords in text
 * Wraps matches in <mark> tag for visual emphasis
 */
function highlightText(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text;

  const regex = new RegExp(`(${query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);

  return parts.map((part, index) =>
    regex.test(part) ? (
      <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 font-semibold">
        {part}
      </mark>
    ) : (
      part
    )
  );
}

export function TopicSearch({
  topics,
  onSelectTopic,
  placeholder = 'Search topics by code, description, or learning outcome...',
  debounceMs = 300,
}: TopicSearchProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  // Debounce search query (300ms delay)
  const debouncedQuery = useDebounce(searchQuery, debounceMs);

  // Filter topics based on debounced query
  const filteredTopics = useMemo(() => {
    if (!debouncedQuery.trim()) return topics;

    const query = debouncedQuery.toLowerCase().trim();

    return topics.filter((topic) => {
      // Search in code
      if (topic.code.toLowerCase().includes(query)) return true;

      // Search in description
      if (topic.description.toLowerCase().includes(query)) return true;

      // Search in learning outcomes
      if (topic.learning_outcomes?.toLowerCase().includes(query)) return true;

      // Search in topics field (if exists)
      if (topic.topics?.toLowerCase().includes(query)) return true;

      return false;
    });
  }, [topics, debouncedQuery]);

  // Handle topic selection
  const handleSelectTopic = useCallback(
    (topicId: string) => {
      if (onSelectTopic) {
        onSelectTopic(topicId);
      } else {
        router.push(`/teaching/${topicId}`);
      }
    },
    [onSelectTopic, router]
  );

  // Clear search
  const handleClear = useCallback(() => {
    setSearchQuery('');
  }, []);

  const hasQuery = searchQuery.trim().length > 0;
  const hasResults = filteredTopics.length > 0;
  const showingAll = !hasQuery;

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 pr-10"
          aria-label="Search syllabus topics"
        />
        {hasQuery && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
            onClick={handleClear}
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Result Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {showingAll ? (
            <>
              Showing all <span className="font-semibold">{topics.length}</span> topics
            </>
          ) : (
            <>
              Found <span className="font-semibold">{filteredTopics.length}</span> result
              {filteredTopics.length !== 1 ? 's' : ''} for "
              <span className="font-semibold">{searchQuery}</span>"
            </>
          )}
        </p>

        {hasQuery && (
          <Button variant="ghost" size="sm" onClick={handleClear}>
            Clear
          </Button>
        )}
      </div>

      {/* Search Results */}
      {hasResults ? (
        <div className="space-y-2">
          {filteredTopics.map((topic) => (
            <div key={topic.id} onClick={() => handleSelectTopic(topic.id)}>
              <TopicCardCompactWithHighlight topic={topic} query={debouncedQuery} />
            </div>
          ))}
        </div>
      ) : (
        // No Results State
        <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg">
          <Search className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No topics found</h3>
          <p className="text-sm text-muted-foreground text-center max-w-md mb-4">
            No topics match "<span className="font-semibold">{searchQuery}</span>"
          </p>

          <div className="text-sm text-muted-foreground">
            <p className="font-medium mb-2">Try:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Checking your spelling</li>
              <li>Using different keywords (e.g., "demand" instead of "PED")</li>
              <li>Searching by syllabus code (e.g., "3.1.2")</li>
              <li>Browsing all topics instead</li>
            </ul>
          </div>

          <Button variant="outline" size="sm" className="mt-4" onClick={handleClear}>
            Clear search
          </Button>
        </div>
      )}
    </div>
  );
}

/**
 * TopicCardCompact variant with keyword highlighting
 * Internal component used by TopicSearch
 */
function TopicCardCompactWithHighlight({
  topic,
  query,
}: {
  topic: SyllabusTopic;
  query: string;
}) {
  return (
    <div className="group flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all hover:shadow-sm hover:border-primary/50 hover:bg-accent/50">
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-sm font-semibold font-mono text-primary">
            {highlightText(topic.code, query)}
          </span>
        </div>
        <p className="text-sm">
          {highlightText(topic.description, query)}
        </p>

        {/* Show matching learning outcomes (if any) */}
        {query &&
          topic.learning_outcomes &&
          topic.learning_outcomes.toLowerCase().includes(query.toLowerCase()) && (
            <p className="text-xs text-muted-foreground mt-1 italic">
              Matches in learning outcomes: "
              {highlightText(
                topic.learning_outcomes.split('\n').find((line) =>
                  line.toLowerCase().includes(query.toLowerCase())
                ) || '',
                query
              )}
              "
            </p>
          )}
      </div>
    </div>
  );
}
