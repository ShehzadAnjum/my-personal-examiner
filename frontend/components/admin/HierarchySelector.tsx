'use client';

import { useEffect, useState } from 'react';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useAcademicLevels,
  useSubjectsForLevel,
  type AcademicLevelSummary,
  type SubjectSummary,
} from '@/lib/hooks/useAcademicLevels';

/**
 * HierarchySelector Component
 *
 * Feature: 008-academic-level-hierarchy (US2)
 *
 * A reusable component for selecting items in the academic hierarchy:
 * Academic Level → Subject → Syllabus (optional)
 *
 * @example
 * // Select academic level and subject
 * <HierarchySelector
 *   onLevelChange={(level) => console.log(level)}
 *   onSubjectChange={(subject) => console.log(subject)}
 * />
 *
 * @example
 * // With initial values
 * <HierarchySelector
 *   selectedLevelId="uuid"
 *   selectedSubjectId="uuid"
 *   onLevelChange={setLevel}
 *   onSubjectChange={setSubject}
 * />
 */

export interface HierarchySelectorProps {
  /** Currently selected academic level ID */
  selectedLevelId?: string | null;
  /** Currently selected subject ID */
  selectedSubjectId?: string | null;
  /** Callback when academic level changes */
  onLevelChange?: (level: AcademicLevelSummary | null) => void;
  /** Callback when subject changes */
  onSubjectChange?: (subject: SubjectSummary | null) => void;
  /** Whether to show subject selector (default: true) */
  showSubjectSelector?: boolean;
  /** Label for level selector */
  levelLabel?: string;
  /** Label for subject selector */
  subjectLabel?: string;
  /** Placeholder for level selector */
  levelPlaceholder?: string;
  /** Placeholder for subject selector */
  subjectPlaceholder?: string;
  /** Whether the selectors are disabled */
  disabled?: boolean;
  /** Orientation: 'horizontal' | 'vertical' */
  orientation?: 'horizontal' | 'vertical';
  /** Whether level selection is required */
  levelRequired?: boolean;
  /** Whether subject selection is required */
  subjectRequired?: boolean;
  /** Custom class name */
  className?: string;
}

export function HierarchySelector({
  selectedLevelId = null,
  selectedSubjectId = null,
  onLevelChange,
  onSubjectChange,
  showSubjectSelector = true,
  levelLabel = 'Academic Level',
  subjectLabel = 'Subject',
  levelPlaceholder = 'Select level',
  subjectPlaceholder = 'Select subject',
  disabled = false,
  orientation = 'horizontal',
  levelRequired = false,
  subjectRequired = false,
  className = '',
}: HierarchySelectorProps) {
  // Internal state for level and subject
  const [internalLevelId, setInternalLevelId] = useState<string | null>(selectedLevelId);
  const [internalSubjectId, setInternalSubjectId] = useState<string | null>(selectedSubjectId);

  // Sync with external state
  useEffect(() => {
    setInternalLevelId(selectedLevelId);
  }, [selectedLevelId]);

  useEffect(() => {
    setInternalSubjectId(selectedSubjectId);
  }, [selectedSubjectId]);

  // Fetch data
  const { data: levels, isLoading: levelsLoading } = useAcademicLevels();
  const { data: subjects, isLoading: subjectsLoading } = useSubjectsForLevel(
    showSubjectSelector ? internalLevelId : null
  );

  // Handle level change
  const handleLevelChange = (value: string) => {
    const newLevelId = value === 'none' ? null : value;
    setInternalLevelId(newLevelId);
    // Reset subject when level changes
    setInternalSubjectId(null);
    onSubjectChange?.(null);

    const level = levels?.find((l) => l.id === newLevelId) || null;
    onLevelChange?.(level);
  };

  // Handle subject change
  const handleSubjectChange = (value: string) => {
    const newSubjectId = value === 'none' ? null : value;
    setInternalSubjectId(newSubjectId);

    const subject = subjects?.find((s) => s.id === newSubjectId) || null;
    onSubjectChange?.(subject);
  };

  const containerClasses = orientation === 'horizontal'
    ? `flex flex-wrap items-end gap-4 ${className}`
    : `flex flex-col gap-4 ${className}`;

  const selectorClasses = orientation === 'horizontal' ? 'flex-1 min-w-[200px]' : 'w-full';

  return (
    <div className={containerClasses}>
      {/* Academic Level Selector */}
      <div className={selectorClasses}>
        <Label className="text-sm font-medium mb-2 block">
          {levelLabel}
          {levelRequired && <span className="text-destructive ml-1">*</span>}
        </Label>
        {levelsLoading ? (
          <Skeleton className="h-10 w-full" />
        ) : (
          <Select
            value={internalLevelId || 'none'}
            onValueChange={handleLevelChange}
            disabled={disabled}
          >
            <SelectTrigger>
              <SelectValue placeholder={levelPlaceholder} />
            </SelectTrigger>
            <SelectContent>
              {!levelRequired && <SelectItem value="none">All Levels</SelectItem>}
              {levels?.map((level) => (
                <SelectItem key={level.id} value={level.id}>
                  {level.name} ({level.code})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* Subject Selector */}
      {showSubjectSelector && (
        <div className={selectorClasses}>
          <Label className="text-sm font-medium mb-2 block">
            {subjectLabel}
            {subjectRequired && <span className="text-destructive ml-1">*</span>}
          </Label>
          {subjectsLoading ? (
            <Skeleton className="h-10 w-full" />
          ) : (
            <Select
              value={internalSubjectId || 'none'}
              onValueChange={handleSubjectChange}
              disabled={disabled || !internalLevelId}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={
                    !internalLevelId
                      ? 'Select a level first'
                      : subjectPlaceholder
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {!subjectRequired && <SelectItem value="none">All Subjects</SelectItem>}
                {subjects?.map((subject) => (
                  <SelectItem key={subject.id} value={subject.id}>
                    {subject.name}
                  </SelectItem>
                ))}
                {subjects?.length === 0 && (
                  <SelectItem value="none" disabled>
                    No subjects in this level
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Compact version of HierarchySelector for inline use
 */
export interface CompactHierarchySelectorProps {
  selectedLevelId?: string | null;
  selectedSubjectId?: string | null;
  onLevelChange?: (levelId: string | null) => void;
  onSubjectChange?: (subjectId: string | null) => void;
  showSubjectSelector?: boolean;
  disabled?: boolean;
  className?: string;
}

export function CompactHierarchySelector({
  selectedLevelId = null,
  selectedSubjectId = null,
  onLevelChange,
  onSubjectChange,
  showSubjectSelector = true,
  disabled = false,
  className = '',
}: CompactHierarchySelectorProps) {
  const { data: levels, isLoading: levelsLoading } = useAcademicLevels();
  const { data: subjects, isLoading: subjectsLoading } = useSubjectsForLevel(
    showSubjectSelector ? selectedLevelId : null
  );

  const handleLevelChange = (value: string) => {
    const newLevelId = value === 'all' ? null : value;
    onLevelChange?.(newLevelId);
    // Reset subject when level changes
    if (selectedSubjectId) {
      onSubjectChange?.(null);
    }
  };

  const handleSubjectChange = (value: string) => {
    const newSubjectId = value === 'all' ? null : value;
    onSubjectChange?.(newSubjectId);
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {levelsLoading ? (
        <Skeleton className="h-8 w-32" />
      ) : (
        <Select
          value={selectedLevelId || 'all'}
          onValueChange={handleLevelChange}
          disabled={disabled}
        >
          <SelectTrigger className="h-8 w-auto">
            <SelectValue placeholder="Level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            {levels?.map((level) => (
              <SelectItem key={level.id} value={level.id}>
                {level.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {showSubjectSelector && selectedLevelId && (
        <>
          <span className="text-muted-foreground">/</span>
          {subjectsLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <Select
              value={selectedSubjectId || 'all'}
              onValueChange={handleSubjectChange}
              disabled={disabled}
            >
              <SelectTrigger className="h-8 w-auto">
                <SelectValue placeholder="Subject" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Subjects</SelectItem>
                {subjects?.map((subject) => (
                  <SelectItem key={subject.id} value={subject.id}>
                    {subject.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </>
      )}
    </div>
  );
}

export default HierarchySelector;
