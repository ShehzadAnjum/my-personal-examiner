'use client';

import Link from 'next/link';
import { ChevronRight, GraduationCap, BookOpen, FileText } from 'lucide-react';
import { useSyllabiForSubject, type SyllabusSummary } from '@/lib/hooks/useAcademicLevels';
import type { Subject } from '@/lib/hooks/useSubjects';

/**
 * HierarchyBreadcrumb Component
 *
 * Feature: 008-academic-level-hierarchy (T050)
 *
 * Displays the navigation hierarchy:
 * Academic Level > Subject > Syllabus (code)
 *
 * @example
 * <HierarchyBreadcrumb subject={activeSubject} />
 * // Renders: "A-Level > Economics > 9708"
 */

interface HierarchyBreadcrumbProps {
  /** Active subject with academic level info */
  subject: Subject | null;
  /** Optional: specific syllabus to show (otherwise uses first active) */
  activeSyllabusId?: string;
  /** Show icons alongside text */
  showIcons?: boolean;
  /** Compact mode (smaller text) */
  compact?: boolean;
}

export function HierarchyBreadcrumb({
  subject,
  activeSyllabusId,
  showIcons = true,
  compact = false,
}: HierarchyBreadcrumbProps) {
  // Fetch syllabi for the subject
  const { data: syllabi } = useSyllabiForSubject(subject?.id || null);

  // Get active syllabus (prefer active one, or specified one, or first)
  const activeSyllabus = getActiveSyllabus(syllabi, activeSyllabusId);

  if (!subject) {
    return null;
  }

  const textSize = compact ? 'text-sm' : 'text-base';
  const iconSize = compact ? 'h-3 w-3' : 'h-4 w-4';

  return (
    <nav
      className={`flex items-center gap-1.5 ${textSize} text-muted-foreground`}
      aria-label="Hierarchy breadcrumb"
    >
      {/* Academic Level */}
      <span className="flex items-center gap-1.5 text-foreground font-medium">
        {showIcons && <GraduationCap className={iconSize} />}
        <span>{subject.academic_level_name}</span>
      </span>

      <ChevronRight className={`${iconSize} text-muted-foreground/50`} />

      {/* Subject */}
      <span className="flex items-center gap-1.5 text-foreground font-medium">
        {showIcons && <BookOpen className={iconSize} />}
        <span>{subject.name}</span>
      </span>

      {/* Syllabus (if available) */}
      {activeSyllabus && (
        <>
          <ChevronRight className={`${iconSize} text-muted-foreground/50`} />
          <span className="flex items-center gap-1.5 text-foreground font-medium">
            {showIcons && <FileText className={iconSize} />}
            <span className="font-mono">{activeSyllabus.code}</span>
            {activeSyllabus.year_range && (
              <span className="text-muted-foreground font-normal">
                ({activeSyllabus.year_range})
              </span>
            )}
          </span>
        </>
      )}
    </nav>
  );
}

/**
 * Get the active syllabus from a list
 * Priority: specified ID > active syllabus > first syllabus
 */
function getActiveSyllabus(
  syllabi: SyllabusSummary[] | undefined,
  activeSyllabusId?: string
): SyllabusSummary | null {
  if (!syllabi || syllabi.length === 0) {
    return null;
  }

  // If specific ID provided, find it
  if (activeSyllabusId) {
    const found = syllabi.find((s) => s.id === activeSyllabusId);
    if (found) return found;
  }

  // Prefer active syllabus
  const active = syllabi.find((s) => s.is_active);
  if (active) return active;

  // Fallback to first
  return syllabi[0];
}

export default HierarchyBreadcrumb;
