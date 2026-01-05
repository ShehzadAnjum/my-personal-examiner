/**
 * TopicBrowser Component
 *
 * Hierarchical tree view of syllabus topics organized by section structure.
 * Parses syllabus codes (e.g., "9708.3.1.2") to create collapsible sections.
 *
 * Organization Strategy:
 * - Parse code format: {subject}.{section}.{subsection}.{topic}
 * - Group by section (e.g., "Section 3: Microeconomics")
 * - Display topics in collapsible Accordion sections
 * - Each topic rendered as TopicCard
 *
 * Features:
 * - Collapsible sections with topic counts
 * - Search integration (future: T022 TopicSearch)
 * - Loading state support
 * - Empty state handling
 * - Responsive grid layout
 *
 * @example
 * ```tsx
 * const { data: topics, isLoading } = useTopics({ subject_code: '9708' });
 *
 * <TopicBrowser
 *   topics={topics}
 *   onTopicClick={(topicId) => router.push(`/teaching/${topicId}`)}
 *   isLoading={isLoading}
 * />
 * ```
 */

'use client';

import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { TopicCard } from './TopicCard';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { BookOpen, ChevronDown } from 'lucide-react';
import type { SyllabusTopic } from '@/lib/types/teaching';

/**
 * Syllabus context for display
 * Feature: 008-academic-level-hierarchy (T052)
 */
export interface SyllabusContext {
  code: string;        // e.g., "9708"
  year_range?: string; // e.g., "2023-2025"
}

export interface TopicBrowserProps {
  topics: SyllabusTopic[];
  onTopicClick?: (topicId: string) => void;
  isLoading?: boolean;
  /** Subject name to display (e.g., "Economics"). If not provided, uses generic "Syllabus" */
  subjectName?: string;
  /** Syllabus context to display (code and year range) */
  syllabusContext?: SyllabusContext;
}

/**
 * Parse syllabus code to extract section number
 * Format: "9708.3.1.2" → section = "3"
 */
function parseSection(code: string): string {
  const parts = code.split('.');
  // Assuming format: {subject}.{section}.{subsection}...
  // Return section part (index 1)
  return parts.length >= 2 ? parts[1] : '0';
}

/**
 * Get section name from section number
 * This is a placeholder - in production, would come from database
 */
function getSectionName(sectionNumber: string): string {
  const sectionNames: Record<string, string> = {
    '1': 'Basic Economic Ideas and Resource Allocation',
    '2': 'The Price System and the Microeconomy',
    '3': 'Government Microeconomic Intervention',
    '4': 'The Macroeconomy',
    '5': 'Government Macroeconomic Intervention',
    '6': 'International Economic Issues',
  };

  return sectionNames[sectionNumber] || `Section ${sectionNumber}`;
}

/**
 * Group topics by section
 */
interface TopicsBySection {
  sectionNumber: string;
  sectionName: string;
  topics: SyllabusTopic[];
}

export function TopicBrowser({
  topics,
  onTopicClick,
  isLoading = false,
  subjectName,
  syllabusContext,
}: TopicBrowserProps) {
  const router = useRouter();

  // Group topics by section
  const topicsBySection = useMemo<TopicsBySection[]>(() => {
    if (!topics || topics.length === 0) return [];

    // Group topics by section number
    const grouped = topics.reduce((acc, topic) => {
      const sectionNumber = parseSection(topic.code);
      if (!acc[sectionNumber]) {
        acc[sectionNumber] = [];
      }
      acc[sectionNumber].push(topic);
      return acc;
    }, {} as Record<string, SyllabusTopic[]>);

    // Convert to array and sort by section number
    return Object.entries(grouped)
      .map(([sectionNumber, sectionTopics]) => ({
        sectionNumber,
        sectionName: getSectionName(sectionNumber),
        topics: sectionTopics.sort((a, b) => a.code.localeCompare(b.code)),
      }))
      .sort((a, b) => a.sectionNumber.localeCompare(b.sectionNumber));
  }, [topics]);

  // Handle topic click
  const handleTopicClick = (topicId: string) => {
    if (onTopicClick) {
      onTopicClick(topicId);
    } else {
      // Default: navigate to explanation page
      router.push(`/teaching/${topicId}`);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-muted-foreground">
          <BookOpen className="h-5 w-5 animate-pulse" />
          <p className="text-sm">Loading syllabus topics...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!topics || topics.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg">
        <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Topics Found</h3>
        <p className="text-sm text-muted-foreground text-center max-w-md">
          No syllabus topics available. This could mean the database hasn't been seeded
          or the subject filter is too restrictive.
        </p>
      </div>
    );
  }

  // Build header text with syllabus context
  const headerText = useMemo(() => {
    if (subjectName && syllabusContext) {
      // Full context: "Economics 9708 (2023-2025)"
      const yearPart = syllabusContext.year_range ? ` (${syllabusContext.year_range})` : '';
      return `${subjectName} ${syllabusContext.code}${yearPart}`;
    }
    if (subjectName) {
      return `${subjectName} Syllabus`;
    }
    if (syllabusContext) {
      const yearPart = syllabusContext.year_range ? ` (${syllabusContext.year_range})` : '';
      return `Syllabus ${syllabusContext.code}${yearPart}`;
    }
    return 'Syllabus';
  }, [subjectName, syllabusContext]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">
            {headerText} ({topics.length} topics)
          </h2>
        </div>
      </div>

      {/* Topic Sections (Accordion) */}
      <Accordion type="multiple" defaultValue={topicsBySection.map((s) => s.sectionNumber)} className="space-y-4">
        {topicsBySection.map((section) => (
          <AccordionItem
            key={section.sectionNumber}
            value={section.sectionNumber}
            className="border rounded-lg px-4"
          >
            <AccordionTrigger className="hover:no-underline py-4">
              <div className="flex items-center justify-between w-full pr-4">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-sm">
                    {section.sectionNumber}
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-base">{section.sectionName}</h3>
                    <p className="text-xs text-muted-foreground">
                      {section.topics.length} topic{section.topics.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
              </div>
            </AccordionTrigger>

            <AccordionContent className="pt-4 pb-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {section.topics.map((topic) => (
                  <TopicCard
                    key={topic.id}
                    topic={topic}
                    onClick={() => handleTopicClick(topic.id)}
                  />
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>

      {/* Footer Stats */}
      <div className="pt-4 border-t">
        <p className="text-xs text-muted-foreground text-center">
          Showing {topics.length} topics across {topicsBySection.length} sections
        </p>
      </div>
    </div>
  );
}

/**
 * Compact variant for embedding in smaller spaces
 * Shows only first section expanded by default
 */
export function TopicBrowserCompact({
  topics,
  onTopicClick,
  isLoading = false,
}: TopicBrowserProps) {
  const router = useRouter();

  const topicsBySection = useMemo<TopicsBySection[]>(() => {
    if (!topics || topics.length === 0) return [];

    const grouped = topics.reduce((acc, topic) => {
      const sectionNumber = parseSection(topic.code);
      if (!acc[sectionNumber]) {
        acc[sectionNumber] = [];
      }
      acc[sectionNumber].push(topic);
      return acc;
    }, {} as Record<string, SyllabusTopic[]>);

    return Object.entries(grouped)
      .map(([sectionNumber, sectionTopics]) => ({
        sectionNumber,
        sectionName: getSectionName(sectionNumber),
        topics: sectionTopics.sort((a, b) => a.code.localeCompare(b.code)),
      }))
      .sort((a, b) => a.sectionNumber.localeCompare(b.sectionNumber));
  }, [topics]);

  const handleTopicClick = (topicId: string) => {
    if (onTopicClick) {
      onTopicClick(topicId);
    } else {
      router.push(`/teaching/${topicId}`);
    }
  };

  if (isLoading || !topics || topics.length === 0) {
    return <div className="text-sm text-muted-foreground">Loading topics...</div>;
  }

  // Only expand first section by default in compact mode
  const defaultExpandedSection = topicsBySection.length > 0 ? topicsBySection[0].sectionNumber : undefined;

  return (
    <Accordion type="single" collapsible defaultValue={defaultExpandedSection} className="space-y-2">
      {topicsBySection.map((section) => (
        <AccordionItem
          key={section.sectionNumber}
          value={section.sectionNumber}
          className="border rounded-lg px-3"
        >
          <AccordionTrigger className="py-3 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Section {section.sectionNumber}</span>
              <span className="text-xs text-muted-foreground">
                ({section.topics.length})
              </span>
            </div>
          </AccordionTrigger>

          <AccordionContent className="pb-3">
            <div className="space-y-2">
              {section.topics.slice(0, 5).map((topic) => (
                <div
                  key={topic.id}
                  onClick={() => handleTopicClick(topic.id)}
                  className="text-sm p-2 hover:bg-accent rounded cursor-pointer transition-colors"
                >
                  <span className="font-mono text-xs text-primary">{topic.code}</span>
                  {' - '}
                  <span>{topic.description}</span>
                </div>
              ))}
              {section.topics.length > 5 && (
                <p className="text-xs text-muted-foreground italic pl-2">
                  + {section.topics.length - 5} more
                </p>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
