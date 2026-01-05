'use client';

import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useSyllabiForSubject, type SyllabusSummary } from '@/lib/hooks/useAcademicLevels';
import { BookOpen, Calendar, CheckCircle, Plus, FileText } from 'lucide-react';

/**
 * SyllabusList Component
 *
 * Feature: 008-academic-level-hierarchy (T045)
 *
 * Displays a list of syllabi for a given subject with:
 * - Syllabus code (e.g., "9708")
 * - Year range (e.g., "2023-2025")
 * - Active/inactive status
 * - Topic count
 * - Link to upload new syllabus
 *
 * @example
 * <SyllabusList subjectId={selectedSubjectId} subjectName="Economics" />
 */

export interface SyllabusListProps {
  /** Subject UUID to fetch syllabi for */
  subjectId: string;
  /** Subject name for display */
  subjectName?: string;
  /** Whether to show the "Upload Syllabus" button */
  showUploadButton?: boolean;
  /** Compact mode - no header, just list */
  compact?: boolean;
}

export function SyllabusList({
  subjectId,
  subjectName,
  showUploadButton = true,
  compact = false,
}: SyllabusListProps) {
  const { data: syllabi, isLoading, error } = useSyllabiForSubject(subjectId);

  if (isLoading) {
    return <SyllabusListSkeleton compact={compact} />;
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <p className="text-destructive text-sm">
            Failed to load syllabi: {error.message}
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!syllabi || syllabi.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-6">
            <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No Syllabi</h3>
            <p className="text-sm text-muted-foreground mb-4">
              No syllabi have been uploaded for this subject yet.
            </p>
            {showUploadButton && (
              <Link href={`/admin/setup/syllabus?subject=${subjectId}`}>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Syllabus
                </Button>
              </Link>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="space-y-2">
        {syllabi.map((syllabus) => (
          <SyllabusCard key={syllabus.id} syllabus={syllabus} compact />
        ))}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Syllabi {subjectName ? `for ${subjectName}` : ''}
          </CardTitle>
          <CardDescription>
            {syllabi.length} syllab{syllabi.length === 1 ? 'us' : 'i'} uploaded
          </CardDescription>
        </div>
        {showUploadButton && (
          <Link href={`/admin/setup/syllabus?subject=${subjectId}`}>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-1" />
              Add Syllabus
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {syllabi.map((syllabus) => (
          <SyllabusCard key={syllabus.id} syllabus={syllabus} />
        ))}
      </CardContent>
    </Card>
  );
}

interface SyllabusCardProps {
  syllabus: SyllabusSummary;
  compact?: boolean;
}

function SyllabusCard({ syllabus, compact = false }: SyllabusCardProps) {
  return (
    <div
      className={`flex items-center justify-between p-3 rounded-lg border bg-card ${
        compact ? 'text-sm' : ''
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center justify-center rounded-md bg-primary/10 text-primary font-mono font-bold ${
            compact ? 'h-8 w-12 text-sm' : 'h-10 w-14'
          }`}
        >
          {syllabus.code}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-medium">
              {syllabus.year_range}
            </span>
            {syllabus.is_active ? (
              <Badge className="bg-green-600" variant="default">
                <CheckCircle className="h-3 w-3 mr-1" />
                Active
              </Badge>
            ) : (
              <Badge variant="secondary">Inactive</Badge>
            )}
          </div>
          <div className="text-sm text-muted-foreground flex items-center gap-2">
            <Calendar className="h-3 w-3" />
            Version {syllabus.version}
            <span className="mx-1">•</span>
            {syllabus.topics_count} topic{syllabus.topics_count !== 1 ? 's' : ''}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Link href={`/admin/setup/topics?syllabus=${syllabus.id}`}>
          <Button variant="outline" size="sm">
            View Topics
          </Button>
        </Link>
      </div>
    </div>
  );
}

function SyllabusListSkeleton({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32 mt-1" />
      </CardHeader>
      <CardContent className="space-y-3">
        {[1, 2].map((i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </CardContent>
    </Card>
  );
}

export default SyllabusList;
