'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle,
  Circle,
  FileUp,
  List,
  Sparkles,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Loader2,
  GraduationCap,
  FolderOpen,
} from 'lucide-react';
import {
  getAllSetupStatus,
  type SubjectSetupStatus,
} from '@/lib/api/admin-setup';
import { useAcademicLevels } from '@/lib/hooks/useAcademicLevels';
import { useSubjects } from '@/lib/hooks/useSubjects';

type SetupStep = 'pending' | 'syllabus_uploaded' | 'topics_generated' | 'explanations_generated' | 'complete';

interface StepConfig {
  label: string;
  description: string;
  icon: React.ReactNode;
  href: (subjectId: string) => string;
}

const STEPS: Record<SetupStep, StepConfig> = {
  pending: {
    label: 'Upload Syllabus',
    description: 'Upload Cambridge syllabus PDF',
    icon: <FileUp className="h-5 w-5" />,
    href: () => '/admin/setup/syllabus',
  },
  syllabus_uploaded: {
    label: 'Review Topics',
    description: 'Review and confirm extracted topics',
    icon: <List className="h-5 w-5" />,
    href: (id) => `/admin/setup/topics?subject=${id}`,
  },
  topics_generated: {
    label: 'Generate Explanations',
    description: 'Generate v1 explanations for all topics',
    icon: <Sparkles className="h-5 w-5" />,
    href: (id) => `/admin/setup/explanations?subject=${id}`,
  },
  explanations_generated: {
    label: 'Review & Complete',
    description: 'Review generated content and mark complete',
    icon: <CheckCircle className="h-5 w-5" />,
    href: (id) => `/admin/setup/explanations?subject=${id}`,
  },
  complete: {
    label: 'Setup Complete',
    description: 'Subject is ready for students',
    icon: <CheckCircle className="h-5 w-5" />,
    href: () => '/teaching',
  },
};

function getStepNumber(status: SetupStep): number {
  const order: SetupStep[] = ['pending', 'syllabus_uploaded', 'topics_generated', 'explanations_generated', 'complete'];
  return order.indexOf(status) + 1;
}

function StepIndicator({ step, status }: { step: number; status: 'complete' | 'current' | 'pending' }) {
  if (status === 'complete') {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-600 text-white">
        <CheckCircle className="h-5 w-5" />
      </div>
    );
  }
  if (status === 'current') {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white font-bold">
        {step}
      </div>
    );
  }
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-gray-300 text-gray-400">
      {step}
    </div>
  );
}

export default function AdminSetupPage() {
  const router = useRouter();
  const [subjects, setSubjects] = useState<SubjectSetupStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hierarchy hooks for 3-step flow (T067)
  const { data: academicLevels, isLoading: levelsLoading } = useAcademicLevels();
  const { data: allSubjects, isLoading: subjectsLoading } = useSubjects();

  useEffect(() => {
    loadSetupStatus();
  }, []);

  const loadSetupStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllSetupStatus();
      setSubjects(data.subjects);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load setup status');
    } finally {
      setLoading(false);
    }
  };

  // Determine current hierarchy step
  const hasLevels = academicLevels && academicLevels.length > 0;
  const hasSubjects = allSubjects && allSubjects.length > 0;

  const getNextAction = (subject: SubjectSetupStatus): { label: string; href: string } | null => {
    const status = subject.setup_status as SetupStep;
    const step = STEPS[status];
    if (!step || status === 'complete') return null;

    return {
      label: `Continue: ${step.label}`,
      href: step.href(subject.subject_id),
    };
  };

  if (loading || levelsLoading || subjectsLoading) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Admin Setup Wizard</h1>
        <p className="text-muted-foreground">
          Configure subjects for student use. Upload syllabi, review topics, and generate explanations.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 3-Step Hierarchy Flow (T067) */}
      {(!hasLevels || !hasSubjects || subjects.length === 0) && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Setup Wizard - 3 Steps</CardTitle>
            <CardDescription>
              Follow these steps to set up your first subject for students
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Step 1: Academic Level */}
              <div className={`flex items-start gap-4 p-4 rounded-lg border ${hasLevels ? 'bg-green-50 border-green-200 dark:bg-green-950/20' : 'bg-blue-50 border-blue-200 dark:bg-blue-950/20'}`}>
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${hasLevels ? 'bg-green-600 text-white' : 'bg-blue-600 text-white'}`}>
                  {hasLevels ? <CheckCircle className="h-5 w-5" /> : '1'}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold flex items-center gap-2">
                    <GraduationCap className="h-4 w-4" />
                    Create Academic Level
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {hasLevels
                      ? `${academicLevels?.length} academic level(s) configured`
                      : 'Create A-Level, IGCSE, or other qualification types'}
                  </p>
                  {!hasLevels && (
                    <Link href="/admin/setup/academic-levels">
                      <Button size="sm" className="mt-2">
                        Create Level
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </Button>
                    </Link>
                  )}
                </div>
              </div>

              {/* Step 2: Subject */}
              <div className={`flex items-start gap-4 p-4 rounded-lg border ${
                hasSubjects ? 'bg-green-50 border-green-200 dark:bg-green-950/20' :
                hasLevels ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20' :
                'bg-muted border-muted-foreground/20 opacity-60'
              }`}>
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  hasSubjects ? 'bg-green-600 text-white' :
                  hasLevels ? 'bg-blue-600 text-white' :
                  'bg-muted-foreground/30 text-muted-foreground'
                }`}>
                  {hasSubjects ? <CheckCircle className="h-5 w-5" /> : '2'}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold flex items-center gap-2">
                    <FolderOpen className="h-4 w-4" />
                    Create Subject
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {hasSubjects
                      ? `${allSubjects?.length} subject(s) configured`
                      : hasLevels
                        ? 'Create subjects like Economics, Accounting under your academic level'
                        : 'Complete Step 1 first'}
                  </p>
                  {hasLevels && !hasSubjects && (
                    <Link href="/admin/setup/subjects">
                      <Button size="sm" className="mt-2">
                        Create Subject
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </Button>
                    </Link>
                  )}
                </div>
              </div>

              {/* Step 3: Syllabus */}
              <div className={`flex items-start gap-4 p-4 rounded-lg border ${
                subjects.length > 0 ? 'bg-green-50 border-green-200 dark:bg-green-950/20' :
                hasSubjects ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20' :
                'bg-muted border-muted-foreground/20 opacity-60'
              }`}>
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  subjects.length > 0 ? 'bg-green-600 text-white' :
                  hasSubjects ? 'bg-blue-600 text-white' :
                  'bg-muted-foreground/30 text-muted-foreground'
                }`}>
                  {subjects.length > 0 ? <CheckCircle className="h-5 w-5" /> : '3'}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold flex items-center gap-2">
                    <FileUp className="h-4 w-4" />
                    Upload Syllabus
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {subjects.length > 0
                      ? `${subjects.length} syllabus(i) uploaded`
                      : hasSubjects
                        ? 'Upload Cambridge syllabus PDF to extract topics'
                        : 'Complete Steps 1 and 2 first'}
                  </p>
                  {hasSubjects && subjects.length === 0 && (
                    <Link href="/admin/setup/syllabus">
                      <Button size="sm" className="mt-2">
                        Upload Syllabus
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subject Cards */}
      {subjects.map((subject) => {
        const currentStep = getStepNumber(subject.setup_status as SetupStep);
        const nextAction = getNextAction(subject);

        return (
          <Card key={subject.subject_id} className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {subject.subject_name}
                    <Badge variant={subject.is_complete ? 'default' : 'secondary'}>
                      {subject.academic_level_name}
                    </Badge>
                  </CardTitle>
                  <CardDescription>
                    Status: {subject.setup_status} | {subject.syllabi_count} syllab{subject.syllabi_count === 1 ? 'us' : 'i'}
                  </CardDescription>
                </div>
                {subject.is_complete && (
                  <Badge className="bg-green-600">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Complete
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {/* Progress Steps */}
              <div className="flex items-center justify-between mb-6">
                {(['pending', 'syllabus_uploaded', 'topics_generated', 'explanations_generated', 'complete'] as SetupStep[]).map((step, idx) => {
                  const stepNum = idx + 1;
                  let status: 'complete' | 'current' | 'pending' = 'pending';
                  if (stepNum < currentStep) status = 'complete';
                  else if (stepNum === currentStep) status = 'current';

                  return (
                    <div key={step} className="flex items-center">
                      <div className="flex flex-col items-center">
                        <StepIndicator step={stepNum} status={status} />
                        <span className="text-xs mt-1 text-center max-w-[80px]">
                          {STEPS[step].label}
                        </span>
                      </div>
                      {idx < 4 && (
                        <div
                          className={`h-0.5 w-12 mx-2 ${
                            stepNum < currentStep ? 'bg-green-600' : 'bg-gray-200'
                          }`}
                        />
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{subject.topics_count}</div>
                  <div className="text-xs text-muted-foreground">Topics</div>
                </div>
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{subject.explanations_count}</div>
                  <div className="text-xs text-muted-foreground">Explanations</div>
                </div>
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {subject.topics_count > 0
                      ? Math.round((subject.explanations_count / subject.topics_count) * 100)
                      : 0}%
                  </div>
                  <div className="text-xs text-muted-foreground">Coverage</div>
                </div>
              </div>

              {/* Next Action */}
              {nextAction && (
                <Link href={nextAction.href}>
                  <Button className="w-full">
                    {nextAction.label}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              )}

              {subject.is_complete && (
                <Link href="/teaching">
                  <Button variant="outline" className="w-full">
                    View in Teaching Page
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        );
      })}

      {/* Add New Subject */}
      {subjects.length > 0 && (
        <Card className="border-dashed">
          <CardContent className="py-8 text-center">
            <Link href="/admin/setup/syllabus">
              <Button variant="outline">
                <FileUp className="h-4 w-4 mr-2" />
                Add Another Subject
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
