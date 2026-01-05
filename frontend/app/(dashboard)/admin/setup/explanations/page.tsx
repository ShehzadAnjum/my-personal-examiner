'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import {
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  Loader2,
  Sparkles,
  FileText,
  BookOpen,
  PartyPopper,
} from 'lucide-react';
import {
  getSubjectSetupStatus,
  generateExplanations,
  type SubjectSetupStatus,
} from '@/lib/api/admin-setup';

interface Resource {
  id: string;
  title: string;
  resource_type: string;
  file_path: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getStudentId(): Promise<string> {
  const response = await fetch('/api/student');
  if (!response.ok) throw new Error('Not authenticated');
  const data = await response.json();
  return data.student_id;
}

async function fetchResources(subjectId: string): Promise<Resource[]> {
  // Fetch resources that could be used for this subject
  // For now, fetch all public resources
  const studentId = await getStudentId();
  const response = await fetch(
    `${API_BASE_URL}/api/resources?student_id=${studentId}&visibility=public`
  );
  if (!response.ok) return [];
  const data = await response.json();
  return data.resources || [];
}

function ExplanationsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const subjectId = searchParams.get('subject');

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<SubjectSetupStatus | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [selectedResources, setSelectedResources] = useState<Set<string>>(new Set());
  const [generationResult, setGenerationResult] = useState<{
    generated_count: number;
    failed_count: number;
    skipped_count: number;
  } | null>(null);

  useEffect(() => {
    if (subjectId) {
      loadData();
    }
  }, [subjectId]);

  const loadData = async () => {
    if (!subjectId) return;

    try {
      setLoading(true);
      setError(null);

      const [statusData, resourcesData] = await Promise.all([
        getSubjectSetupStatus(subjectId),
        fetchResources(subjectId),
      ]);

      setStatus(statusData);
      setResources(resourcesData);

      // Auto-select syllabus resources (all PDFs marked as syllabus type)
      // In 008-academic-level-hierarchy, syllabus resources are linked via Syllabus model
      const syllabusResources = resourcesData.filter((r: any) =>
        r.resource_metadata?.type === 'syllabus'
      );
      if (syllabusResources.length > 0) {
        setSelectedResources(new Set(syllabusResources.map((r: any) => r.id)));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleResourceToggle = (resourceId: string) => {
    setSelectedResources((prev) => {
      const next = new Set(prev);
      if (next.has(resourceId)) {
        next.delete(resourceId);
      } else {
        next.add(resourceId);
      }
      return next;
    });
  };

  const handleGenerate = async () => {
    if (!subjectId) return;

    try {
      setGenerating(true);
      setError(null);

      const result = await generateExplanations({
        subject_id: subjectId,
        syllabus_point_ids: [], // Empty = all topics
        resource_ids: Array.from(selectedResources),
      });

      setGenerationResult({
        generated_count: result.generated_count,
        failed_count: result.failed_count,
        skipped_count: result.skipped_count,
      });

      // Refresh status
      const newStatus = await getSubjectSetupStatus(subjectId);
      setStatus(newStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleComplete = () => {
    router.push('/admin/setup');
  };

  if (!subjectId) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Missing Subject</AlertTitle>
          <AlertDescription>
            No subject ID provided. Please go back and select a subject.
          </AlertDescription>
        </Alert>
        <Link href="/admin/setup" className="mt-4 inline-block">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Setup
          </Button>
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  const coverage = status
    ? status.topics_count > 0
      ? Math.round((status.explanations_count / status.topics_count) * 100)
      : 0
    : 0;

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Link href="/admin/setup" className="text-sm text-muted-foreground hover:text-foreground flex items-center mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Setup
        </Link>
        <h1 className="text-3xl font-bold mb-2">Generate Explanations</h1>
        <p className="text-muted-foreground">
          Generate v1 explanations for all topics using selected resources as context.
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

      {/* Success/Complete State */}
      {status?.is_complete && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <PartyPopper className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-700">Setup Complete!</AlertTitle>
          <AlertDescription className="text-green-600">
            All {status.topics_count} topics have explanations. This subject is ready for students.
          </AlertDescription>
        </Alert>
      )}

      {/* Generation Result */}
      {generationResult && (
        <Alert className="mb-6 border-blue-500 bg-blue-50">
          <CheckCircle className="h-4 w-4 text-blue-600" />
          <AlertTitle className="text-blue-700">Generation Complete</AlertTitle>
          <AlertDescription className="text-blue-600">
            <ul className="mt-2 space-y-1">
              <li>Generated: {generationResult.generated_count}</li>
              <li>Skipped (already exist): {generationResult.skipped_count}</li>
              {generationResult.failed_count > 0 && (
                <li className="text-red-600">Failed: {generationResult.failed_count}</li>
              )}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Subject Status */}
      {status && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              {status.subject_name} ({status.academic_level_name})
            </CardTitle>
            <CardDescription>
              {status.topics_count} topics | {status.explanations_count} explanations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Explanation Coverage</span>
                  <span className="font-medium">{coverage}%</span>
                </div>
                <Progress value={coverage} className="h-2" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{status.topics_count}</div>
                  <div className="text-xs text-muted-foreground">Topics</div>
                </div>
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{status.explanations_count}</div>
                  <div className="text-xs text-muted-foreground">Explained</div>
                </div>
                <div className="text-center p-3 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {status.topics_count - status.explanations_count}
                  </div>
                  <div className="text-xs text-muted-foreground">Remaining</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resource Selection */}
      {!status?.is_complete && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Select Resources for Context
            </CardTitle>
            <CardDescription>
              Select resources to use as context when generating explanations.
              The LLM will reference these materials for accurate, Cambridge-aligned content.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {resources.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4">
                No resources available. You can generate explanations without resource context,
                or upload resources first from the Resources page.
              </p>
            ) : (
              <div className="space-y-3">
                {resources.map((resource) => (
                  <div
                    key={resource.id}
                    className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <Checkbox
                      id={resource.id}
                      checked={selectedResources.has(resource.id)}
                      onCheckedChange={() => handleResourceToggle(resource.id)}
                    />
                    <label
                      htmlFor={resource.id}
                      className="flex-1 cursor-pointer"
                    >
                      <div className="font-medium">{resource.title}</div>
                      <div className="text-sm text-muted-foreground">
                        {resource.resource_type}
                      </div>
                    </label>
                    <Badge variant="outline">{resource.resource_type}</Badge>
                  </div>
                ))}
              </div>
            )}
            {selectedResources.size > 0 && (
              <p className="text-sm text-muted-foreground mt-4">
                {selectedResources.size} resource{selectedResources.size !== 1 ? 's' : ''} selected
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Link href="/admin/setup">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Setup
          </Button>
        </Link>

        {status?.is_complete ? (
          <div className="flex gap-2">
            <Link href="/teaching">
              <Button variant="outline">
                View Teaching Page
              </Button>
            </Link>
            <Button onClick={handleComplete}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Complete Setup
            </Button>
          </div>
        ) : (
          <Button
            onClick={handleGenerate}
            disabled={generating || !status || status.topics_count === 0}
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Explanations
              </>
            )}
          </Button>
        )}
      </div>

      {/* Warning about generation time */}
      {!status?.is_complete && status && status.topics_count > 0 && (
        <Alert className="mt-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Generation Time</AlertTitle>
          <AlertDescription>
            Generating explanations for {status.topics_count - status.explanations_count} topics
            may take several minutes. Please do not close this page during generation.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

export default function ExplanationsPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    }>
      <ExplanationsPageContent />
    </Suspense>
  );
}
