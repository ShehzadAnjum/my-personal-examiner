/**
 * Teaching - Topic Explanation Page
 *
 * Resource Bank integration with fallback to on-demand generation.
 *
 * Features:
 * - ✅ Resource Bank integration (v1 admin-generated explanations)
 * - ✅ Version switching (multiple explanation versions with localStorage)
 * - ✅ Regenerate buttons (Simpler, More Detail, More Examples)
 * - ✅ Local caching with localStorage
 * - ✅ Text selection menu ("Explain This Differently")
 * - ✅ Bookmark functionality
 *
 * Content Retrieval Strategy (US1: View Shared Topic Explanation):
 * 1. Check Resource Bank for v1 (admin-generated) explanation
 * 2. If found: Display with "Official" badge, fast loading from cache
 * 3. If not found: Fall back to on-demand LLM generation
 *
 * Constitutional Compliance:
 * - Principle I: Subject Accuracy (Cambridge-aligned cached content)
 * - Principle II: A* standard marking (PhD-level explanations)
 * - Principle VI: Constructive feedback (9-component framework)
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, AlertCircle, RefreshCw, Sparkles, MessageCircle, BadgeCheck, ShieldCheck, Loader2 } from 'lucide-react';
import { ExplanationView } from '@/components/teaching/ExplanationView';
import { ExplanationLoadingState } from '@/components/teaching/ExplanationLoadingState';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToggleBookmark } from '@/lib/hooks/useBookmark';
import { useToast } from '@/lib/hooks/use-toast';
import * as teachingApi from '@/lib/api/teaching';
import * as resourcesApi from '@/lib/api/resources';
import { isResourceNotFoundError } from '@/lib/api/resources';
import type { ExplanationSection } from '@/lib/api/resources';
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
  const { toast } = useToast();

  // State for fetching
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // State for version switching
  const [currentVersion, setCurrentVersion] = useState(0);
  const [explanationVersions, setExplanationVersions] = useState<CachedExplanation['versions']>([]);
  const [displayedExplanation, setDisplayedExplanation] = useState<TopicExplanation | null>(null);

  // Resource Bank state (US1: View Shared Topic Explanation)
  const [isFromResourceBank, setIsFromResourceBank] = useState(false);
  const [resourceBankVersion, setResourceBankVersion] = useState<number | null>(null);
  const [resourceBankMiss, setResourceBankMiss] = useState(false); // True when no v1 exists
  const [resourceBankExplanationId, setResourceBankExplanationId] = useState<string | null>(null); // For admin regenerate

  // Admin state (US2: Admin Generates Baseline Content)
  const [studentId, setStudentId] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAdminGenerating, setIsAdminGenerating] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState<ExplanationSection | null>(null);

  // State for text selection menu
  const [selectedText, setSelectedText] = useState('');
  const [showExplainMenu, setShowExplainMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });

  // TanStack Query bookmark hook (replaces manual state management)
  const { toggle: toggleBookmark, isPending: isBookmarkPending, isBookmarked } = useToggleBookmark(topicId);

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

  // Check if Resource Bank has v1 (for admin UI purposes)
  const checkResourceBankStatus = async () => {
    try {
      console.log('🏦 Checking Resource Bank status for admin UI...');
      const resourceExplanation = await resourcesApi.getExplanation(topicId);
      // V1 exists - store ID for section regeneration
      setResourceBankMiss(false);
      setIsFromResourceBank(true);
      setResourceBankVersion(resourceExplanation.version);
      setResourceBankExplanationId(resourceExplanation.id);
      console.log('📌 Set resourceBankExplanationId from status check:', resourceExplanation.id);
    } catch (err) {
      if (isResourceNotFoundError(err)) {
        console.log('📭 No v1 in Resource Bank (admin can generate)');
        setResourceBankMiss(true);
        setIsFromResourceBank(false);
        setResourceBankExplanationId(null);
      }
    }
  };

  // Fetch explanation with Resource Bank integration (US1)
  // Strategy: Check Resource Bank first, fall back to on-demand LLM generation
  const fetchExplanation = async (context?: string, forceRegenerate = false) => {
    // Check localStorage cache first (unless forcing regeneration)
    if (!forceRegenerate && !context) {
      const cached = loadCachedExplanation(topicId);
      if (cached) {
        console.log('📦 Loading explanation from localStorage cache');
        setDisplayedExplanation(cached.explanation);
        setExplanationVersions(cached.versions);
        setCurrentVersion(0);
        // Still check Resource Bank status for admin UI (async, non-blocking)
        checkResourceBankStatus();
        return;
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Check Resource Bank for v1 (admin-generated) explanation
      // This is the fast path - cached content from backend
      if (!forceRegenerate && !context) {
        try {
          console.log('🏦 Checking Resource Bank for v1 explanation...');
          const resourceExplanation = await resourcesApi.getExplanation(topicId);
          const content = resourceExplanation.content;

          // Convert ResourceExplanation content to TopicExplanation format
          // Resource Bank uses a different schema than the teaching API
          const explanation: TopicExplanation = {
            syllabus_code: resourceExplanation.syllabus_code || resourceExplanation.syllabus_point_id,
            concept_name: content.definition?.split('.')[0] || 'Topic Explanation',
            definition: content.definition || '',
            key_terms: [], // Resource Bank doesn't have key_terms, leave empty
            explanation: content.concept_explanation || '',
            examples: (content.real_world_examples || []).map((ex, idx) => ({
              title: `Example ${idx + 1}`,
              scenario: ex,
              analysis: '',
            })),
            visual_aids: (content.diagrams || []).map((d, idx) => ({
              type: 'suggested' as const,
              title: d.type ? `${d.type.charAt(0).toUpperCase() + d.type.slice(1)} Diagram` : `Diagram ${idx + 1}`,
              description: d.description,
            })),
            worked_examples: [], // Resource Bank uses practice_questions instead
            common_misconceptions: (content.common_misconceptions || []).map(m => ({
              misconception: m.misconception,
              why_wrong: m.correction,
              correct_understanding: m.correction,
            })),
            practice_problems: (content.practice_questions || []).map(q => ({
              question: q.question,
              difficulty: 'medium' as const,
              answer_outline: q.answer || '',
              marks: q.marks || 4,
            })),
            related_concepts: content.related_topics || [],
            generated_by: resourceExplanation.llm_provider,
          };

          console.log('✅ Found v1 explanation in Resource Bank:', {
            id: resourceExplanation.id,
            version: resourceExplanation.version,
            cached: resourceExplanation.is_cached,
          });

          // Mark as from Resource Bank
          setIsFromResourceBank(true);
          setResourceBankVersion(resourceExplanation.version);
          setResourceBankExplanationId(resourceExplanation.id); // Store for admin regenerate
          console.log('📌 Set resourceBankExplanationId:', resourceExplanation.id);

          // Save to localStorage for offline access
          saveToCached(topicId, explanation, 'resource_bank_v1');
          setDisplayedExplanation(explanation);
          setError(null);
          return;
        } catch (resourceError) {
          // Resource Bank miss - NO fallback for initial load
          if (isResourceNotFoundError(resourceError)) {
            console.log('📭 No v1 in Resource Bank - awaiting admin generation');
            setResourceBankMiss(true); // Mark as miss so admin button shows
            setIsFromResourceBank(false);
            setResourceBankVersion(null);

            // DON'T fall back to on-demand generation for initial load
            // Students must wait for admin to generate v1 first
            if (!context) {
              setError('This topic has not been officially explained yet. Please check back later or contact your administrator.');
              return;
            }
          } else {
            console.warn('⚠️ Resource Bank error:', resourceError);
            setError('Failed to load explanation. Please try again.');
            return;
          }
        }
      }

      // Step 2: Generate alternative version (only if v1 exists and student requests variant)
      // This is for regenerate requests (Simpler, More Detail, etc.) when v1 already exists
      if (context && !resourceBankMiss) {
        console.log('🤖 Generating alternative explanation via LLM...');
        const explanation = await teachingApi.explainConcept(topicId, context);
        const requestType = context || 'default';

        // Save to cache (this will also set currentVersion correctly)
        saveToCached(topicId, explanation, requestType);
        setDisplayedExplanation(explanation);
        setError(null);
      } else if (context && resourceBankMiss) {
        // Can't generate variants without v1
        setError('Cannot generate alternative explanations until the official explanation exists.');
        return;
      }
    } catch (err) {
      console.error('Failed to fetch explanation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load explanation');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle bookmark toggle with toast notifications
  const handleBookmarkToggle = () => {
    if (!displayedExplanation) {
      toast({
        variant: 'destructive',
        title: 'Cannot bookmark',
        description: 'Explanation not loaded yet',
      });
      return;
    }

    toggleBookmark(displayedExplanation);

    // Show toast notification (optimistic - shows immediately)
    if (isBookmarked) {
      toast({
        title: 'Bookmark removed',
        description: `"${displayedExplanation.concept_name}" removed from saved explanations`,
      });
    } else {
      toast({
        title: 'Explanation saved',
        description: `"${displayedExplanation.concept_name}" added to saved explanations`,
      });
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

  // Fetch current user info (including admin status)
  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const response = await fetch('/api/student');
        if (response.ok) {
          const data = await response.json();
          setStudentId(data.student_id);
          setIsAdmin(data.is_admin || false);
          console.log('👤 User info:', { studentId: data.student_id, isAdmin: data.is_admin });
        }
      } catch (err) {
        console.error('Failed to fetch user info:', err);
      }
    };
    fetchUserInfo();
  }, []);

  // Initialize: Load from cache and fetch if needed
  useEffect(() => {
    fetchExplanation();
  }, [topicId]);

  // Add document-level text selection handler to work everywhere
  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, [handleTextSelection]);

  // Dispatch topic info to header when explanation loads
  useEffect(() => {
    if (displayedExplanation) {
      const event = new CustomEvent('topic-loaded', {
        detail: {
          code: displayedExplanation.syllabus_code,
          name: displayedExplanation.concept_name,
        },
      });
      window.dispatchEvent(event);
    } else {
      // Clear topic info when no explanation
      window.dispatchEvent(new CustomEvent('topic-cleared'));
    }

    // Cleanup on unmount
    return () => {
      window.dispatchEvent(new CustomEvent('topic-cleared'));
    };
  }, [displayedExplanation]);

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

    // FR-006a: 5 personalization styles with distinct prompts
    const contextMap: Record<string, string> = {
      // Selection-based (for text selection menu)
      simpler: `Please explain the following in simpler terms, suitable for someone with less background knowledge: "${selectedText}"`,
      detailed: `Please provide a more detailed explanation of the following, with additional examples and depth: "${selectedText}"`,
      examples: `Please explain the following using more real-world examples and practical applications: "${selectedText}"`,
      // Full page regeneration (5 styles per FR-006a)
      full_simpler: 'Please re-explain this entire concept in simpler, more accessible language suitable for beginners. Use basic vocabulary and shorter sentences.',
      full_detailed: 'Please provide a more comprehensive and detailed explanation of this concept with additional depth, context, and technical nuance.',
      full_examples: 'Please re-explain this concept with at least 3x more real-world examples and practical applications from various industries and contexts.',
      full_exam_focused: 'Please re-explain this concept with a focus on Cambridge A-Level exam requirements. Include mark scheme alignment, common examiner expectations, and specific tips for scoring full marks.',
      full_visual: 'Please re-explain this concept with emphasis on visual representations. Include additional diagrams, flowcharts, and visual metaphors to aid understanding.',
    };

    await fetchExplanation(contextMap[type], true);
    setSelectedText('');
  };

  // Admin: Regenerate v1 explanation with warning (US2)
  const handleAdminRegenerate = async () => {
    if (!studentId || !isAdmin) {
      toast({
        variant: 'destructive',
        title: 'Permission denied',
        description: 'Admin access required to regenerate official explanations',
      });
      return;
    }

    if (!resourceBankExplanationId) {
      toast({
        variant: 'destructive',
        title: 'Cannot regenerate',
        description: 'No official explanation found to regenerate',
      });
      return;
    }

    // Show confirmation dialog
    const confirmed = window.confirm(
      '⚠️ Warning: This will OVERWRITE the current official (v1) explanation.\n\n' +
      'All students will see the new version.\n\n' +
      'Are you sure you want to regenerate?'
    );

    if (!confirmed) return;

    setIsAdminGenerating(true);
    try {
      // Call regenerate endpoint (overwrites v1)
      const regenerated = await resourcesApi.regenerateV1Explanation(resourceBankExplanationId, studentId);

      toast({
        title: 'Official explanation regenerated',
        description: 'The v1 explanation has been updated for all students.',
      });

      // Clear cache and reload
      localStorage.removeItem(`explanation_${topicId}`);
      await fetchExplanation();
    } catch (err) {
      console.error('Admin regenerate failed:', err);
      toast({
        variant: 'destructive',
        title: 'Regeneration failed',
        description: err instanceof Error ? err.message : 'Failed to regenerate explanation',
      });
    } finally {
      setIsAdminGenerating(false);
    }
  };

  // Admin: Generate v1 explanation for Resource Bank (US2)
  const handleAdminGenerate = async () => {
    if (!studentId || !isAdmin) {
      toast({
        variant: 'destructive',
        title: 'Not authorized',
        description: 'Admin privileges required to generate v1 explanations',
      });
      return;
    }

    setIsAdminGenerating(true);
    try {
      console.log('🔧 Admin generating v1 for Resource Bank...');
      const generated = await resourcesApi.generateV1Explanation(topicId, studentId);

      console.log('✅ V1 generated successfully:', generated.id);

      // Clear the miss flag since v1 now exists
      setResourceBankMiss(false);
      setIsFromResourceBank(true);
      setResourceBankVersion(generated.version);

      // Clear localStorage cache so next load fetches from Resource Bank
      localStorage.removeItem(`explanation_${topicId}`);

      // Refresh the explanation to load the new v1
      await fetchExplanation();

      toast({
        title: 'V1 Generated',
        description: 'Official explanation created and saved to Resource Bank',
      });
    } catch (err) {
      console.error('Failed to generate v1:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      toast({
        variant: 'destructive',
        title: 'Generation failed',
        description: errorMessage,
      });
    } finally {
      setIsAdminGenerating(false);
    }
  };

  // Admin: Regenerate a single section of the explanation
  const handleSectionRegenerate = async (sectionName: ExplanationSection) => {
    console.log('🔧 Section regenerate check:', {
      studentId,
      isAdmin,
      resourceBankExplanationId,
      sectionName,
    });

    if (!studentId || !isAdmin || !resourceBankExplanationId) {
      console.error('❌ Missing requirements:', {
        hasStudentId: !!studentId,
        hasIsAdmin: isAdmin,
        hasExplanationId: !!resourceBankExplanationId,
      });
      toast({
        variant: 'destructive',
        title: 'Cannot regenerate section',
        description: `Admin access and existing explanation required. Debug: studentId=${!!studentId}, isAdmin=${isAdmin}, explanationId=${!!resourceBankExplanationId}`,
      });
      return;
    }

    setRegeneratingSection(sectionName);
    try {
      console.log(`🔧 Admin regenerating section '${sectionName}'...`);
      await resourcesApi.regenerateSection(resourceBankExplanationId, sectionName, studentId);

      toast({
        title: 'Section regenerated',
        description: `The ${sectionName.replace('_', ' ')} section has been updated.`,
      });

      // Clear cache and reload to show updated content
      localStorage.removeItem(`explanation_${topicId}`);
      await fetchExplanation();
    } catch (err) {
      console.error('Section regeneration failed:', err);
      toast({
        variant: 'destructive',
        title: 'Regeneration failed',
        description: err instanceof Error ? err.message : 'Failed to regenerate section',
      });
    } finally {
      setRegeneratingSection(null);
    }
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
    if (requestType === 'resource_bank_v1') return 'Official';
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

  // Error state - Show admin generate button if admin and no v1 exists
  if (error && !displayedExplanation) {
    // Admin can generate v1 when it doesn't exist
    const showAdminGenerate = isAdmin && resourceBankMiss;

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

        {showAdminGenerate ? (
          // Admin view: Show generate button
          <Card className="p-6 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950">
            <div className="flex items-start gap-4">
              <ShieldCheck className="h-8 w-8 text-amber-600 mt-1" />
              <div className="flex-1 space-y-4">
                <div>
                  <h2 className="text-xl font-semibold text-amber-800 dark:text-amber-200">
                    No Official Explanation Yet
                  </h2>
                  <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                    This topic doesn't have an official (v1) explanation in the Resource Bank.
                    As an admin, you can generate one now.
                  </p>
                </div>
                <div className="flex gap-3">
                  <Button
                    onClick={handleAdminGenerate}
                    className="gap-2 bg-amber-600 hover:bg-amber-700 text-white"
                    disabled={isAdminGenerating}
                  >
                    {isAdminGenerating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="h-4 w-4" />
                        Generate Official v1
                      </>
                    )}
                  </Button>
                  <Button onClick={() => router.push('/teaching')} variant="outline" size="sm">
                    Back to Topics
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ) : (
          // Non-admin view: Show error
          <div className="border border-destructive/50 rounded-lg p-6 bg-destructive/10">
            <div className="flex items-start gap-4">
              <AlertCircle className="h-6 w-6 text-destructive mt-1" />
              <div className="flex-1 space-y-2">
                <h2 className="text-xl font-semibold text-destructive">
                  Content Not Available
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
        )}
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
          <div className="space-y-4">
            {/* Row 1: Version Switcher with Resource Bank indicator */}
            <div className="flex items-center gap-3 flex-wrap">
              {/* Resource Bank Badge (US1: View Shared Topic Explanation) */}
              {isFromResourceBank && (
                <Badge variant="secondary" className="gap-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                  <BadgeCheck className="h-3 w-3" />
                  Official v{resourceBankVersion}
                </Badge>
              )}
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
                <span className="text-xs text-muted-foreground">
                  ({getVersionLabel(explanationVersions[currentVersion]?.requestType || 'default')})
                </span>
              )}
            </div>

            {/* Row 2: Personalization Style Buttons (FR-006a: 5 styles) */}
            <div className="flex gap-2 flex-wrap">
              <Button
                onClick={() => explainDifferently('full_simpler')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
                title="Reduced complexity, basic vocabulary"
              >
                Simpler
              </Button>
              <Button
                onClick={() => explainDifferently('full_detailed')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
                title="Deeper explanations, additional context"
              >
                More Detail
              </Button>
              <Button
                onClick={() => explainDifferently('full_examples')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
                title="3x more real-world examples"
              >
                More Examples
              </Button>
              <Button
                onClick={() => explainDifferently('full_exam_focused')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
                title="Mark scheme alignment, examiner tips"
              >
                Exam Focus
              </Button>
              <Button
                onClick={() => explainDifferently('full_visual')}
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={isLoading}
                title="Additional diagrams, visual representations"
              >
                More Visuals
              </Button>
              {/* Admin Regenerate v1 */}
              {isAdmin && isFromResourceBank && (
                <Button
                  onClick={handleAdminRegenerate}
                  variant="outline"
                  size="sm"
                  className="h-8 text-xs gap-1 border-amber-500 text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950"
                  disabled={isLoading || isAdminGenerating}
                  title="Regenerate official v1 (overwrites current)"
                >
                  <RefreshCw className="h-3 w-3" />
                  Regen v1
                </Button>
              )}
            </div>
          </div>

          {/* Admin Generate Section (US2: Admin Generates Baseline Content) */}
          {isAdmin && resourceBankMiss && (
            <div className="mt-4 pt-4 border-t border-amber-200 dark:border-amber-800">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-amber-700 dark:text-amber-300">
                  <ShieldCheck className="h-4 w-4" />
                  <span className="font-medium">Admin:</span>
                  <span className="text-muted-foreground">No official explanation exists for this topic</span>
                </div>
                <Button
                  onClick={handleAdminGenerate}
                  variant="default"
                  size="sm"
                  className="h-8 text-xs gap-1 bg-amber-600 hover:bg-amber-700 text-white"
                  disabled={isAdminGenerating || isLoading}
                >
                  {isAdminGenerating ? (
                    <>
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="h-3 w-3" />
                      Generate Official v1
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
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
          onBookmarkToggle={handleBookmarkToggle}
          isLoading={isBookmarkPending}
          isAdmin={isAdmin && isFromResourceBank}
          onSectionRegenerate={handleSectionRegenerate}
          regeneratingSection={regeneratingSection}
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
