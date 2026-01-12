'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Loader2,
  Edit2,
  Trash2,
  Save,
  X,
  List,
} from 'lucide-react';
import {
  previewTopics,
  confirmTopics,
  type ExtractedTopic,
  type TopicsPreviewResponse,
} from '@/lib/api/admin-setup';

/**
 * Topics Page Content
 *
 * Updated for 008-academic-level-hierarchy:
 * - Uses syllabus_id instead of subject_id
 * - Query param: ?syllabus=<syllabus_id>
 */
function TopicsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const syllabusId = searchParams.get('syllabus');  // Changed from 'subject'

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<TopicsPreviewResponse | null>(null);

  // Editable topics
  const [topics, setTopics] = useState<ExtractedTopic[]>([]);
  const [deletedCodes, setDeletedCodes] = useState<Set<string>>(new Set());
  const [editingCode, setEditingCode] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<ExtractedTopic | null>(null);

  useEffect(() => {
    if (syllabusId) {
      loadTopics();
    }
  }, [syllabusId]);

  const loadTopics = async () => {
    if (!syllabusId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await previewTopics(syllabusId);  // Uses syllabus_id now
      setPreview(data);
      setTopics(data.topics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (topic: ExtractedTopic) => {
    setEditingCode(topic.code);
    setEditForm({ ...topic });
  };

  const handleSaveEdit = () => {
    if (!editForm || !editingCode) return;

    setTopics((prev) =>
      prev.map((t) => (t.code === editingCode ? editForm : t))
    );
    setEditingCode(null);
    setEditForm(null);
  };

  const handleCancelEdit = () => {
    setEditingCode(null);
    setEditForm(null);
  };

  const handleDelete = (code: string) => {
    setDeletedCodes((prev) => new Set([...prev, code]));
  };

  const handleRestore = (code: string) => {
    setDeletedCodes((prev) => {
      const next = new Set(prev);
      next.delete(code);
      return next;
    });
  };

  const handleConfirm = async () => {
    if (!syllabusId || !preview) return;

    try {
      setSaving(true);
      setError(null);

      const activeTopics = topics.filter((t) => !deletedCodes.has(t.code));

      await confirmTopics({
        syllabus_id: syllabusId,  // NEW - 008-academic-level-hierarchy
        subject_id: preview.subject_id,  // For backward compat
        topics: activeTopics.map((t) => ({
          code: t.code,
          title: t.title,
          description: t.description,
          learning_outcomes: t.learning_outcomes,
        })),
        delete_topic_codes: Array.from(deletedCodes),
      });

      // Navigate to explanations using subject_id (explanations are per-subject)
      router.push(`/admin/setup/explanations?subject=${preview.subject_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm topics');
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.9) {
      return <Badge className="bg-green-600">High ({Math.round(confidence * 100)}%)</Badge>;
    }
    if (confidence >= 0.7) {
      return <Badge className="bg-yellow-600">Medium ({Math.round(confidence * 100)}%)</Badge>;
    }
    return <Badge variant="destructive">Low ({Math.round(confidence * 100)}%)</Badge>;
  };

  if (!syllabusId) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Missing Syllabus</AlertTitle>
          <AlertDescription>
            No syllabus ID provided. Please upload a syllabus first.
          </AlertDescription>
        </Alert>
        <Link href="/admin/setup/syllabus" className="mt-4 inline-block">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Upload Syllabus
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

  const activeTopicsCount = topics.filter((t) => !deletedCodes.has(t.code)).length;

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Link href="/admin/setup" className="text-sm text-muted-foreground hover:text-foreground flex items-center mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Setup
        </Link>
        <h1 className="text-3xl font-bold mb-2">Review Extracted Topics</h1>
        <p className="text-muted-foreground">
          Review and edit the topics extracted from the syllabus PDF. Delete topics that are incorrect.
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

      {/* Syllabus Info */}
      {preview && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <List className="h-5 w-5" />
              {preview.subject_name} ({preview.syllabus_code})
            </CardTitle>
            <CardDescription>
              {preview.syllabus_year} | {activeTopicsCount} of {topics.length} topics selected
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <Badge className="bg-green-600">{preview.high_confidence_count}</Badge>
                <span className="text-sm">High confidence</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="destructive">{preview.low_confidence_count}</Badge>
                <span className="text-sm">Need review</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">{deletedCodes.size}</Badge>
                <span className="text-sm">Deleted</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Topics List */}
      <div className="space-y-4 mb-6">
        {topics.map((topic) => {
          const isDeleted = deletedCodes.has(topic.code);
          const isEditing = editingCode === topic.code;

          return (
            <Card
              key={topic.code}
              className={isDeleted ? 'opacity-50 bg-red-50' : ''}
            >
              <CardContent className="pt-4">
                {isEditing && editForm ? (
                  // Edit Mode
                  <div className="space-y-4">
                    <div className="grid grid-cols-4 gap-4">
                      <div>
                        <label className="text-sm font-medium">Code</label>
                        <Input
                          value={editForm.code}
                          onChange={(e) =>
                            setEditForm({ ...editForm, code: e.target.value })
                          }
                        />
                      </div>
                      <div className="col-span-3">
                        <label className="text-sm font-medium">Title</label>
                        <Input
                          value={editForm.title}
                          onChange={(e) =>
                            setEditForm({ ...editForm, title: e.target.value })
                          }
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <Textarea
                        value={editForm.description}
                        onChange={(e) =>
                          setEditForm({ ...editForm, description: e.target.value })
                        }
                        rows={2}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        Learning Outcomes (one per line)
                      </label>
                      <Textarea
                        value={editForm.learning_outcomes.join('\n')}
                        onChange={(e) =>
                          setEditForm({
                            ...editForm,
                            learning_outcomes: e.target.value
                              .split('\n')
                              .filter((l) => l.trim()),
                          })
                        }
                        rows={4}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={handleSaveEdit}>
                        <Save className="h-4 w-4 mr-1" />
                        Save
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                        <X className="h-4 w-4 mr-1" />
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono font-bold">{topic.code}</span>
                        <span className="font-medium">{topic.title}</span>
                        {getConfidenceBadge(topic.confidence)}
                      </div>
                      {topic.description !== topic.title && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {topic.description}
                        </p>
                      )}
                      {topic.learning_outcomes.length > 0 && (
                        <div className="text-sm">
                          <span className="font-medium">Learning Outcomes:</span>
                          <ul className="list-disc list-inside ml-2">
                            {topic.learning_outcomes.slice(0, 3).map((lo, i) => (
                              <li key={i} className="text-muted-foreground">
                                {lo}
                              </li>
                            ))}
                            {topic.learning_outcomes.length > 3 && (
                              <li className="text-muted-foreground">
                                ...and {topic.learning_outcomes.length - 3} more
                              </li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      {isDeleted ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRestore(topic.code)}
                        >
                          Restore
                        </Button>
                      ) : (
                        <>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(topic)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-600 hover:text-red-700"
                            onClick={() => handleDelete(topic.code)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <Link href="/admin/setup">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </Link>

        <Button onClick={handleConfirm} disabled={saving || activeTopicsCount === 0}>
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Confirming...
            </>
          ) : (
            <>
              <CheckCircle className="h-4 w-4 mr-2" />
              Confirm {activeTopicsCount} Topics
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

export default function TopicsPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    }>
      <TopicsPageContent />
    </Suspense>
  );
}
