'use client';

import { useState } from 'react';
import { BookOpen, Plus, ChevronRight, AlertCircle, GraduationCap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import {
  useAcademicLevels,
  useSubjectsForLevel,
  useCreateSubjectForLevel,
  type AcademicLevelSummary,
  type SubjectSummary,
} from '@/lib/hooks/useAcademicLevels';
import { Skeleton } from '@/components/ui/skeleton';
import Link from 'next/link';

/**
 * Subjects Management Page
 *
 * Feature: 008-academic-level-hierarchy (US2)
 *
 * Allows admins to:
 * - View all subjects organized by academic level
 * - Create new subjects under a specific academic level
 * - Navigate to subject details for syllabus management
 */

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

export default function SubjectsPage() {
  const { data: levels, isLoading: levelsLoading, error: levelsError } = useAcademicLevels();
  const { toast } = useToast();

  // Selected academic level for filtering
  const [selectedLevelId, setSelectedLevelId] = useState<string | null>(null);

  // Fetch subjects for selected level
  const { data: subjects, isLoading: subjectsLoading } = useSubjectsForLevel(selectedLevelId);

  // Create dialog state
  const [createOpen, setCreateOpen] = useState(false);
  const [createLevelId, setCreateLevelId] = useState<string>('');
  const [createData, setCreateData] = useState({
    name: '',
  });

  // Mutations
  const createMutation = useCreateSubjectForLevel();

  // Handle create
  const handleCreate = async () => {
    if (!createLevelId) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Please select an academic level',
      });
      return;
    }

    try {
      await createMutation.mutateAsync({
        levelId: createLevelId,
        data: {
          name: createData.name,
        },
      });
      toast({
        title: 'Subject Created',
        description: `${createData.name} has been created successfully.`,
      });
      setCreateOpen(false);
      setCreateData({ name: '' });
      setCreateLevelId('');
      // Auto-select the level where subject was created
      setSelectedLevelId(createLevelId);
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to create subject',
      });
    }
  };

  // Get selected level info
  const selectedLevel = levels?.find((l) => l.id === selectedLevelId);

  // Loading state
  if (levelsLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-12 w-64" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      </div>
    );
  }

  // Error state
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Subjects</h1>
          <p className="text-muted-foreground">
            Manage subjects under each academic level
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button disabled={!levels || levels.length === 0}>
              <Plus className="h-4 w-4 mr-2" />
              Add Subject
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Subject</DialogTitle>
              <DialogDescription>
                Add a new subject under an academic level.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="level">Academic Level</Label>
                <Select value={createLevelId} onValueChange={setCreateLevelId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select academic level" />
                  </SelectTrigger>
                  <SelectContent>
                    {levels?.map((level) => (
                      <SelectItem key={level.id} value={level.id}>
                        {level.name} ({level.code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Subject Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Economics"
                  value={createData.name}
                  onChange={(e) => setCreateData({ ...createData, name: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreate}
                disabled={!createData.name || !createLevelId || createMutation.isPending}
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* No Academic Levels Warning */}
      {levels && levels.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GraduationCap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Academic Levels</h3>
            <p className="text-muted-foreground text-center mb-4">
              You need to create an academic level before adding subjects.
            </p>
            <Link href="/admin/setup/academic-levels">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Academic Level
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Academic Level Selector */}
      {levels && levels.length > 0 && (
        <div className="flex items-center gap-4">
          <Label className="text-sm font-medium">Filter by Level:</Label>
          <Select
            value={selectedLevelId || 'all'}
            onValueChange={(value) => setSelectedLevelId(value === 'all' ? null : value)}
          >
            <SelectTrigger className="w-64">
              <SelectValue placeholder="All levels" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              {levels.map((level) => (
                <SelectItem key={level.id} value={level.id}>
                  {level.name} ({level.subjects_count} subjects)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Subjects Grid - When level selected */}
      {selectedLevelId && (
        <>
          {subjectsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-40" />
              ))}
            </div>
          ) : subjects && subjects.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Subjects</h3>
                <p className="text-muted-foreground text-center mb-4">
                  No subjects found under {selectedLevel?.name}. Create your first subject.
                </p>
                <Button onClick={() => {
                  setCreateLevelId(selectedLevelId);
                  setCreateOpen(true);
                }}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Subject
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {subjects?.map((subject) => (
                <SubjectCard
                  key={subject.id}
                  subject={subject}
                  levelName={selectedLevel?.name || ''}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* All Subjects View - When no level selected */}
      {!selectedLevelId && levels && levels.length > 0 && (
        <div className="space-y-8">
          {levels.map((level) => (
            <LevelSection key={level.id} level={level} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Subject Card Component
 */
function SubjectCard({ subject, levelName }: { subject: SubjectSummary; levelName: string }) {
  return (
    <Card className="relative group">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              {subject.name}
            </CardTitle>
            <CardDescription>{levelName}</CardDescription>
          </div>
          <Badge variant={getStatusBadgeVariant(subject.setup_status)}>
            {getStatusLabel(subject.setup_status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">
            {subject.syllabi_count} {subject.syllabi_count === 1 ? 'syllabus' : 'syllabi'}
          </span>
          <Link href={`/admin/setup/subjects/${subject.id}`}>
            <Button variant="ghost" size="sm">
              Manage
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Level Section Component - Shows subjects grouped by level
 */
function LevelSection({ level }: { level: AcademicLevelSummary }) {
  const { data: subjects, isLoading } = useSubjectsForLevel(level.id);

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <GraduationCap className="h-5 w-5 text-muted-foreground" />
        <h2 className="text-xl font-semibold">{level.name}</h2>
        <Badge variant="outline">{level.code}</Badge>
        <span className="text-sm text-muted-foreground">
          {level.subjects_count} {level.subjects_count === 1 ? 'subject' : 'subjects'}
        </span>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2].map((i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      ) : subjects && subjects.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="py-8 text-center text-muted-foreground">
            No subjects under this level yet
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {subjects?.map((subject) => (
            <SubjectCard
              key={subject.id}
              subject={subject}
              levelName={level.name}
            />
          ))}
        </div>
      )}
    </div>
  );
}
