/**
 * Teaching - Topic Explanation Page
 *
 * Simple approach using useState + useEffect (no TanStack Query complexity).
 *
 * Features:
 * - ✅ Version switching (multiple explanation versions with localStorage)
 * - ✅ Regenerate buttons (Simpler, More Detail, More Examples)
 * - ✅ Local caching with localStorage
 * - ✅ Text selection menu ("Explain This Differently")
 * - ✅ Bookmark functionality
 *
 * Constitutional Compliance:
 * - Principle II: A* standard marking (PhD-level explanations)
 * - Principle VI: Constructive feedback (9-component framework)
 * - Avoid over-engineering: Simple fetch pattern, no unnecessary libraries
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, AlertCircle, RefreshCw, Sparkles, MessageCircle } from 'lucide-react';
import { ExplanationView } from '@/components/teaching/ExplanationView';
import { ExplanationLoadingState } from '@/components/teaching/ExplanationLoadingState';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import * as teachingApi from '@/lib/api/teaching';
import type { TopicExplanation } from '@/lib/types/teaching';

// Cache interface for storing explanation versions
interface CachedExplanation {
  explanation: TopicExplanation;
  timestamp: number;
  versions: Array<{
    explanation: TopicExplanation;
    requestType: string;
    timestamp: number;
  }>;
}

export default function ExplanationPage() {
  const params = useParams();
  const router = useRouter();
  const topicId = params.topicId as string;

  // State for fetching
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // State for version switching
  const [currentVersion, setCurrentVersion] = useState(0);
  const [explanationVersions, setExplanationVersions] = useState<CachedExplanation['versions']>([]);
  const [displayedExplanation, setDisplayedExplanation] = useState<TopicExplanation | null>(null);

  // State for text selection menu
  const [selectedText, setSelectedText] = useState('');
  const [showExplainMenu, setShowExplainMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });

  // State for bookmark
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isBookmarkPending, setIsBookmarkPending] = useState(false);
  const [savedExplanationId, setSavedExplanationId] = useState<string | null>(null);

  // Load cached explanation from localStorage
  const loadCachedExplanation = (conceptId: string): CachedExplanation | null => {
    try {
      const cached = localStorage.getItem(`explanation_${conceptId}`);
      return cached ? JSON.parse(cached) : null;
    } catch (err) {
      console.error('Failed to load cached explanation:', err);
      return null;
    }
  };

  // Save explanation to localStorage cache
  const saveToCached = (conceptId: string, exp: TopicExplanation, requestType: string = 'default') => {
    try {
      const existing = loadCachedExplanation(conceptId);
      const newVersion = {
        explanation: exp,
        requestType,
        timestamp: Date.now(),
      };

      let versions: typeof newVersion[];

      if (existing) {
        // Check if a version with this requestType already exists
        const existingVersionIndex = existing.versions.findIndex(
          v => v.requestType === requestType
        );

        if (existingVersionIndex >= 0) {
          // Update existing version instead of creating duplicate
          versions = [...existing.versions];
          versions[existingVersionIndex] = newVersion;
        } else {
          // Add new version
          versions = [...existing.versions, newVersion];
        }
      } else {
        // First version
        versions = [newVersion];
      }

      const cached: CachedExplanation = {
        explanation: exp,
        timestamp: Date.now(),
        versions,
      };

      localStorage.setItem(`explanation_${conceptId}`, JSON.stringify(cached));
      setExplanationVersions(versions);

      // Set current version to the one we just saved/updated
      const currentIdx = versions.findIndex(v => v.requestType === requestType);
      setCurrentVersion(currentIdx >= 0 ? currentIdx : versions.length - 1);
    } catch (err) {
      console.error('Failed to save to cache:', err);
    }
  };

  // Fetch explanation (simple approach)
  const fetchExplanation = async (context?: string, forceRegenerate = false) => {
    // Check cache first (unless forcing regeneration)
    if (!forceRegenerate && !context) {
      const cached = loadCachedExplanation(topicId);
      if (cached) {
        console.log('📦 Loading explanation from cache');
        setDisplayedExplanation(cached.explanation);
        setExplanationVersions(cached.versions);
        setCurrentVersion(0);
        return;
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const explanation = await teachingApi.explainConcept(topicId, context);
      const requestType = context || 'default';

      // Save to cache (this will also set currentVersion correctly)
      saveToCached(topicId, explanation, requestType);
      setDisplayedExplanation(explanation);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch explanation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load explanation');
    } finally {
      setIsLoading(false);
    }
  };

  // Check bookmark status with localStorage caching for performance
  const checkBookmarkStatus = async () => {
    try {
      // Check localStorage cache first for instant feedback
      const cachedBookmarks = localStorage.getItem('saved_explanations_cache');
      const cacheTimestamp = localStorage.getItem('saved_explanations_timestamp');
      const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

      if (cachedBookmarks && cacheTimestamp) {
        const age = Date.now() - parseInt(cacheTimestamp);
        if (age < CACHE_DURATION) {
          const cached = JSON.parse(cachedBookmarks);
          const savedExp = cached.find((exp: any) => exp.syllabus_point_id === topicId);
          if (savedExp) {
            setIsBookmarked(true);
            setSavedExplanationId(savedExp.id);
          } else {
            setIsBookmarked(false);
            setSavedExplanationId(null);
          }
          return; // Use cache, skip API call
        }
      }

      // Cache miss or expired - fetch from API
      const saved = await teachingApi.getSavedExplanations();

      // Update cache
      localStorage.setItem('saved_explanations_cache', JSON.stringify(saved));
      localStorage.setItem('saved_explanations_timestamp', Date.now().toString());

      const savedExp = saved.find(exp => exp.syllabus_point_id === topicId);
      if (savedExp) {
        setIsBookmarked(true);
        setSavedExplanationId(savedExp.id);
      } else {
        setIsBookmarked(false);
        setSavedExplanationId(null);
      }
    } catch (err) {
      console.error('Failed to check bookmark status:', err);
    }
  };

  // Toggle bookmark with cache invalidation (pointer-based)
  const toggleBookmark = async () => {
    setIsBookmarkPending(true);
    try {
      if (isBookmarked && savedExplanationId) {
        // Remove bookmark
        await teachingApi.removeSavedExplanation(savedExplanationId);
        setIsBookmarked(false);
        setSavedExplanationId(null);
      } else {
        // Add bookmark (pointer-based - no content sent)
        const saved = await teachingApi.saveExplanation(topicId);
        setIsBookmarked(true);
        setSavedExplanationId(saved.id);
      }

      // Invalidate cache so next check fetches fresh data
      localStorage.removeItem('saved_explanations_cache');
      localStorage.removeItem('saved_explanations_timestamp');
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    } finally {
      setIsBookmarkPending(false);
    }
  };

  // Handle text selection for "Explain This Differently" menu
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    console.log('🔍 Text selection:', { text, length: text?.length });

    if (text && text.length > 10) {
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();

      console.log('✅ Showing menu at:', { x: rect?.left, y: rect?.bottom });

      if (rect) {
        setSelectedText(text);
        // Since popup uses position: fixed (viewport-relative), use rect directly without scrollY
        setMenuPosition({ x: rect.left, y: rect.bottom });
        setShowExplainMenu(true);
      }
    } else {
      console.log('❌ Text too short or empty, hiding menu');
      setShowExplainMenu(false);
    }
  }, []);

  // Initialize: Load from cache and fetch if needed
  useEffect(() => {
    fetchExplanation();
    checkBookmarkStatus();
  }, [topicId]);

  // Add document-level text selection handler to work everywhere
  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, [handleTextSelection]);

  // Navigate to coaching with selected text
  const askCoach = () => {
    setShowExplainMenu(false);
    // Store selected text in sessionStorage to pass to coaching page
    sessionStorage.setItem('coaching_initial_text', selectedText);
    router.push('/coaching');
  };

  // Generate alternative explanation
  const explainDifferently = async (type: string) => {
    setShowExplainMenu(false);

    const contextMap: Record<string, string> = {
      simpler: `Please explain the following in simpler terms, suitable for someone with less background knowledge: "${selectedText}"`,
      detailed: `Please provide a more detailed explanation of the following, with additional examples and depth: "${selectedText}"`,
      examples: `Please explain the following using more real-world examples and practical applications: "${selectedText}"`,
      full_simpler: 'Please re-explain this entire concept in simpler, more accessible language suitable for beginners.',
      full_detailed: 'Please provide a more comprehensive and detailed explanation of this concept with additional depth.',
      full_examples: 'Please re-explain this concept with many more real-world examples and practical applications.',
    };

    await fetchExplanation(contextMap[type], true);
    setSelectedText('');
  };

  // Switch between explanation versions
  const switchVersion = (index: number) => {
    if (explanationVersions[index]) {
      setDisplayedExplanation(explanationVersions[index].explanation);
      setCurrentVersion(index);
    }
  };

  // Get user-friendly label for version type
  const getVersionLabel = (requestType: string): string => {
    if (requestType === 'default') return 'Original';
    if (requestType.includes('simpler')) return 'Simpler';
    if (requestType.includes('detailed')) return 'Detailed';
    if (requestType.includes('examples')) return 'More Examples';
    return requestType.substring(0, 20); // Truncate long custom contexts
  };

  // Loading state
  if (isLoading && !displayedExplanation) {
    return (
      <div className="container mx-auto p-6 max-w-4xl w-full">
        <div className="mb-6">
          <Link href="/teaching">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Topics
            </Button>
          </Link>
        </div>
        <ExplanationLoadingState withBlur={true} />
      </div>
    );
  }

  // Error state
  if (error && !displayedExplanation) {
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
                Failed to Load Explanation
              </h2>
              <p className="text-sm text-muted-foreground">{error}</p>
              <div className="flex gap-3 mt-4">
                <Button onClick={() => fetchExplanation(undefined, true)} variant="outline" size="sm" className="gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </Button>
                <Button onClick={() => router.push('/teaching')} variant="ghost" size="sm">
                  Browse Topics
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  return (
    <div className="container mx-auto p-6 max-w-4xl w-full">
      {/* Back Navigation */}
      <div className="mb-6">
        <Link href="/teaching">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Topics
          </Button>
        </Link>
      </div>

      {/* Version Switcher & Regenerate Buttons */}
      {displayedExplanation && explanationVersions.length > 0 && (
        <Card className="p-4 mb-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            {/* Version Switcher */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Version:
              </span>
              <div className="flex gap-1">
                {explanationVersions.map((version, idx) => (
                  <Button
                    key={idx}
                    onClick={() => switchVersion(idx)}
                    variant={currentVersion === idx ? 'default' : 'outline'}
                    size="sm"
                    className="h-8 px-3 text-xs"
                    title={`Version ${idx + 1}: ${getVersionLabel(version.requestType)}`}
                  >
                    v{idx + 1}
                  </Button>
                ))}
              </div>
              {explanationVersions.length > 1 && (
                <span className="text-xs text-muted-foreground hidden md:inline">
                  ({getVersionLabel(explanationVersions[currentVersion]?.requestType || 'default')})
                </span>
              )}
            </div>

            {/* Regenerate Buttons */}
            <div className="flex gap-2 flex-wrap">
              <Button
                onClick={() => explainDifferently('full_simpler')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
              >
                Simpler
              </Button>
              <Button
                onClick={() => explainDifferently('full_detailed')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
              >
                More Detail
              </Button>
              <Button
                onClick={() => explainDifferently('full_examples')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
              >
                More Examples
              </Button>
              <Button
                onClick={() => fetchExplanation(undefined, true)}
                variant="outline"
                size="sm"
                className="h-8 text-xs gap-1"
                disabled={isLoading}
                title="Generate a fresh explanation"
              >
                <RefreshCw className="h-3 w-3" />
                Regenerate
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Loading indicator for regeneration */}
      {isLoading && displayedExplanation && (
        <div className="mb-6">
          <ExplanationLoadingState withBlur={false} message="Generating alternative explanation..." />
        </div>
      )}

      {/* Explanation Content */}
      {displayedExplanation && (
        <ExplanationView
          explanation={displayedExplanation}
          isBookmarked={isBookmarked}
          onBookmarkToggle={toggleBookmark}
          isLoading={isBookmarkPending}
        />
      )}

      {/* Floating "Explain This" Menu */}
      {showExplainMenu && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowExplainMenu(false)}
          />
          <div
            className="fixed z-50 bg-card rounded-lg shadow-2xl border-2 border-primary p-2 min-w-[260px]"
            style={{
              left: `${menuPosition.x}px`,
              top: `${menuPosition.y + 10}px`,
            }}
          >
            <div className="text-xs font-semibold text-muted-foreground px-3 py-2 border-b">
              💡 Help Options
            </div>
            <div className="py-1">
              <button
                onClick={askCoach}
                className="w-full text-left px-3 py-2 text-sm hover:bg-accent transition flex items-center gap-2 font-medium text-primary"
              >
                <MessageCircle className="h-4 w-4" />
                <span>Ask AI Coach</span>
              </button>
              <div className="border-t my-1" />
              <button
                onClick={() => explainDifferently('simpler')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-accent transition flex items-center gap-2"
              >
                <span>🟢</span>
                <span>Simpler Language</span>
              </button>
              <button
                onClick={() => explainDifferently('detailed')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-accent transition flex items-center gap-2"
              >
                <span>🔍</span>
                <span>More Detail</span>
              </button>
              <button
                onClick={() => explainDifferently('examples')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-accent transition flex items-center gap-2"
              >
                <span>📚</span>
                <span>More Examples</span>
              </button>
            </div>
            <div className="text-xs text-muted-foreground px-3 py-2 border-t">
              Selected: &quot;{selectedText.slice(0, 50)}{selectedText.length > 50 ? '...' : ''}&quot;
            </div>
          </div>
        </>
      )}

      {/* Bottom Navigation */}
      <div className="mt-8 pt-6 border-t flex justify-between items-center">
        <Link href="/teaching">
          <Button variant="outline" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Topics
          </Button>
        </Link>

        <Link href="/teaching/saved">
          <Button variant="ghost" size="sm">
            View Saved Explanations →
          </Button>
        </Link>
      </div>
    </div>
  );
}
