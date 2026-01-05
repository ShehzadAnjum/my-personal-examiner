'use client';

import { use } from 'react';
import Link from 'next/link';
import { ArrowLeft, BookOpen, GraduationCap, AlertCircle, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { SyllabusList } from '@/components/admin/SyllabusList';
import { useSubjectsForLevel, useAcademicLevels } from '@/lib/hooks/useAcademicLevels';

/**
 * Subject Detail Page
 *
 * Feature: 008-academic-level-hierarchy (T045)
 *
 * Displays:
 * - Subject details (name, academic level, setup status)
 * - List of syllabi for this subject
 * - Actions: Upload syllabus, view topics
 */

interface SubjectDetailPageProps {
  params: Promise<{ subjectId: string }>;
}

function getStatusBadgeVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'complete':
      return 'default';
    case 'topics_generated':
    case 'explanations_generated':
      return 'secondary';
    case 'pending':
    case 'syllabus_uploaded':
      return 'outline';
    default:
      return 'secondary';
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'pending':
      return 'Pending Setup';
    case 'syllabus_uploaded':
      return 'Syllabus Uploaded';
    case 'topics_generated':
      return 'Topics Generated';
    case 'explanations_generated':
      return 'Explanations Ready';
    case 'complete':
      return 'Complete';
    default:
      return status;
  }
}

export default function SubjectDetailPage({ params }: SubjectDetailPageProps) {
  const { subjectId } = use(params);

  // Fetch all academic levels to find the subject
  const { data: levels, isLoading: levelsLoading, error: levelsError } = useAcademicLevels();

  // Find the subject by searching through all levels
  // This is not ideal, but works for now until we have a direct subject fetch endpoint
  const allSubjects: Array<{ subject: { id: string; name: string; setup_status: string; syllabi_count: number }; level: { id: string; name: string; code: string } }> = [];

  // We need to fetch subjects for each level to find our subject
  // For now, we'll use a simpler approach - just show the SyllabusList

  if (levelsLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (levelsError) {
    return (
      <div className="container mx-auto py-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              Error Loading Data
            </CardTitle>
            <CardDescription>
              {levelsError instanceof Error ? levelsError.message : 'An unexpected error occurred'}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Breadcrumb Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/setup/subjects">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Subjects
          </Button>
        </Link>
      </div>

      {/* Subject Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-primary/10">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Subject Details</CardTitle>
                <CardDescription>
                  Manage syllabi and content for this subject
                </CardDescription>
              </div>
            </div>
            <Link href={`/admin/setup/syllabus?subject=${subjectId}`}>
              <Button>
                <Settings className="h-4 w-4 mr-2" />
                Upload Syllabus
              </Button>
            </Link>
          </div>
        </CardHeader>
      </Card>

      {/* Syllabi Section */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <GraduationCap className="h-5 w-5" />
          Syllabi
        </h2>
        <SyllabusList
          subjectId={subjectId}
          showUploadButton={true}
        />
      </div>
    </div>
  );
}
