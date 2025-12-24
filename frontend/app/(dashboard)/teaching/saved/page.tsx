/**
 * Saved Explanations Page (Pointer-Based Bookmarks)
 *
 * Display all bookmarked explanations for the current student.
 * Architecture: API returns pointers only, content loaded from localStorage.
 *
 * Flow:
 * 1. Fetch bookmarks (pointers) from API
 * 2. For each bookmark, load explanation from localStorage
 * 3. Show "Regenerate" button if cache missing
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, BookmarkIcon, Trash2, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import * as teachingApi from '@/lib/api/teaching';
import type { SavedExplanation, TopicExplanation } from '@/lib/types/teaching';

// Enriched type with cached explanation content
interface SavedExplanationWithContent extends SavedExplanation {
  explanation?: TopicExplanation; // Loaded from localStorage
  hasCachedContent: boolean;
}

export default function SavedExplanationsPage() {
  const router = useRouter();
  const [savedExplanations, setSavedExplanations] = useState<SavedExplanationWithContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load explanation from localStorage cache
  const loadExplanationFromCache = (syllabusPointId: string): TopicExplanation | null => {
    try {
      const cached = localStorage.getItem(`explanation_${syllabusPointId}`);
      if (!cached) return null;

      const parsed = JSON.parse(cached);
      // Handle both old format (direct TopicExplanation) and new format (with versions)
      return parsed.explanation || parsed;
    } catch (err) {
      console.error('Failed to load explanation from cache:', err);
      return null;
    }
  };

  // Fetch saved explanations (pointers) and enrich with localStorage content
  useEffect(() => {
    async function fetchSaved() {
      try {
        const bookmarks = await teachingApi.getSavedExplanations();

        // Enrich each bookmark with cached explanation content
        const enriched: SavedExplanationWithContent[] = bookmarks.map(bookmark => {
          const cachedExplanation = loadExplanationFromCache(bookmark.syllabus_point_id);
          return {
            ...bookmark,
            explanation: cachedExplanation || undefined,
            hasCachedContent: !!cachedExplanation,
          };
        });

        setSavedExplanations(enriched);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch saved explanations:', err);
        setError(err instanceof Error ? err.message : 'Failed to load saved explanations');
      } finally {
        setIsLoading(false);
      }
    }

    fetchSaved();
  }, []);

  // Remove saved explanation
  const handleRemove = async (id: string) => {
    try {
      await teachingApi.removeSavedExplanation(id);
      setSavedExplanations(prev => prev.filter(exp => exp.id !== id));
    } catch (err) {
      console.error('Failed to remove explanation:', err);
    }
  };

  // Navigate to explanation
  const handleView = (syllabusPointId: string) => {
    router.push(`/teaching/${syllabusPointId}`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="mb-6">
          <Link href="/teaching">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Topics
            </Button>
          </Link>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="mb-6">
          <Link href="/teaching">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Topics
            </Button>
          </Link>
        </div>
        <div className="border border-destructive/50 rounded-lg p-6 bg-destructive/10">
          <div className="flex items-start gap-4">
            <AlertCircle className="h-6 w-6 text-destructive mt-1" />
            <div className="flex-1 space-y-2">
              <h2 className="text-xl font-semibold text-destructive">
                Failed to Load Saved Explanations
              </h2>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Back Navigation */}
      <div className="mb-6">
        <Link href="/teaching">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Topics
          </Button>
        </Link>
      </div>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <BookmarkIcon className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Saved Explanations</h1>
        </div>
        <p className="text-muted-foreground">
          Your bookmarked Economics topics for quick review
        </p>
      </div>

      {/* Saved Explanations List */}
      {savedExplanations.length === 0 ? (
        <Card className="p-12 text-center">
          <BookmarkIcon className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Saved Explanations</h2>
          <p className="text-muted-foreground mb-6">
            You haven't bookmarked any explanations yet. Click "Save for Later" on any explanation to add it here.
          </p>
          <Link href="/teaching">
            <Button>Browse Topics</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {savedExplanations.map((saved) => (
            <Card key={saved.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  {saved.hasCachedContent && saved.explanation ? (
                    <>
                      <h3 className="text-lg font-semibold mb-2">
                        {saved.explanation.concept_name}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                        {saved.explanation.definition}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Saved {new Date(saved.date_saved).toLocaleDateString()}</span>
                        <span>•</span>
                        <span className="font-mono">{saved.explanation.syllabus_code}</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <h3 className="text-lg font-semibold mb-2 text-muted-foreground">
                        Bookmarked Topic
                      </h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        Explanation content not cached. Click "Regenerate" to load this topic again.
                      </p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Saved {new Date(saved.date_saved).toLocaleDateString()}</span>
                      </div>
                    </>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  {saved.hasCachedContent ? (
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleView(saved.syllabus_point_id)}
                    >
                      View
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(saved.syllabus_point_id)}
                      className="gap-2"
                    >
                      <RefreshCw className="h-3.5 w-3.5" />
                      Regenerate
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemove(saved.id)}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Stats */}
      {savedExplanations.length > 0 && (
        <div className="mt-8 pt-6 border-t text-center text-sm text-muted-foreground">
          {savedExplanations.length} saved {savedExplanations.length === 1 ? 'explanation' : 'explanations'}
        </div>
      )}
    </div>
  );
}
