/**
 * Teaching Page - Main Route
 *
 * Browse and search syllabus topics for the active subject.
 * Request PhD-level explanations for any concept.
 *
 * Dynamic subject support:
 * - Fetches active subject from database
 * - Shows "No subjects" state if none configured
 * - Prompts admin to set up a subject
 *
 * Constitutional Compliance:
 * - Principle I: Subject Accuracy (Cambridge syllabus topics)
 * - Principle III: PhD-level pedagogy (comprehensive topic coverage)
 * - Principle XIV: UI Discoverability (shows setup prompt when needed)
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TopicBrowser } from '@/components/teaching/TopicBrowser';
import { TopicSearch } from '@/components/teaching/TopicSearch';
import { TopicSearchSkeleton } from '@/components/teaching/TopicSearchSkeleton';
import { HierarchyBreadcrumb } from '@/components/teaching/HierarchyBreadcrumb';
import { useSyllabiForSubject } from '@/lib/hooks/useAcademicLevels';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Search, AlertCircle, Settings, FileUp, ArrowRight } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useToast } from '@/lib/hooks/use-toast';
import { useActiveSubject, formatSubjectShort } from '@/lib/hooks/useSubjects';
import { useAdmin } from '@/lib/hooks/useAdmin';
import * as teachingApi from '@/lib/api/teaching';
import type { SyllabusTopic } from '@/lib/types/teaching';

const CACHE_VERSION_KEY = 'syllabus_version';
const CACHE_DURATION_MS = 1000 * 60 * 60 * 24; // 24 hours

/**
 * Generate cache key based on subject ID (updated for hierarchy)
 */
function getCacheKey(subjectId: string): string {
  return `syllabus_topics_${subjectId}`;
}

export default function TeachingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAdmin } = useAdmin();
  const { data: activeSubject, hasSubjects, isLoading: subjectsLoading } = useActiveSubject();

  const [activeTab, setActiveTab] = useState<'browse' | 'search'>('browse');
  const [topics, setTopics] = useState<SyllabusTopic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingCache, setUsingCache] = useState(false);

  // Fetch syllabi to get active syllabus context (T052)
  const { data: syllabi } = useSyllabiForSubject(activeSubject?.id || null);
  const activeSyllabus = syllabi?.find((s) => s.is_active) || syllabi?.[0];

  // Fetch topics with localStorage caching (only when we have an active subject)
  useEffect(() => {
    // Wait for subjects to load
    if (subjectsLoading) return;

    // If no subjects, don't try to fetch topics
    if (!hasSubjects || !activeSubject) {
      setIsLoading(false);
      setTopics([]);
      return;
    }

    const CACHE_KEY = getCacheKey(activeSubject.id);

    async function fetchTopics() {
      try {
        // Try to load from localStorage first (instant load)
        const cached = localStorage.getItem(CACHE_KEY);
        const cacheTimestamp = localStorage.getItem(`${CACHE_KEY}_timestamp`);

        if (cached && cacheTimestamp) {
          const cachedTopics = JSON.parse(cached);
          const age = Date.now() - parseInt(cacheTimestamp);

          // Instantly show cached data
          console.log('📦 Loaded syllabus from cache (instant load)');
          setTopics(cachedTopics);
          setIsLoading(false);
          setUsingCache(true);

          // If cache is fresh (<24h), we're done
          if (age < CACHE_DURATION_MS) {
            console.log('✅ Cache is fresh, skipping API call');
            return;
          }

          console.log('⏰ Cache is stale, syncing in background...');
        } else {
          // No cache, show loading state
          setIsLoading(true);
          setUsingCache(false);
          console.log('🔄 No cache found, fetching from API...');
        }

        // Fetch from API using active subject ID
        const fetchedTopics = await teachingApi.getTopics({ subject_id: activeSubject!.id });

        // Update state
        setTopics(fetchedTopics);
        setError(null);

        // Save to cache with timestamp
        localStorage.setItem(CACHE_KEY, JSON.stringify(fetchedTopics));
        localStorage.setItem(`${CACHE_KEY}_timestamp`, Date.now().toString());
        localStorage.setItem(CACHE_VERSION_KEY, '1');

        console.log('💾 Syllabus cached to localStorage');
        setUsingCache(false);
      } catch (err) {
        console.error('Failed to fetch syllabus topics:', err);

        // If we have cache, keep showing it even if API fails
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached && !topics.length) {
          const cachedTopics = JSON.parse(cached);
          setTopics(cachedTopics);
          console.log('⚠️ API failed, using stale cache');
          setUsingCache(true);
        } else if (!topics.length) {
          setError('Failed to load topics. Please refresh the page.');
          toast({
            variant: 'destructive',
            title: 'Failed to load topics',
            description: 'An error occurred while fetching syllabus topics. Please try again.',
          });
        }
      } finally {
        setIsLoading(false);
      }
    }

    fetchTopics();
  }, [toast, topics.length, subjectsLoading, hasSubjects, activeSubject]);

  // Handle topic selection (navigate to explanation page)
  const handleTopicClick = (topicId: string) => {
    router.push(`/teaching/${topicId}`);
  };

  const handleRetry = () => {
    if (!activeSubject) return;
    setIsLoading(true);
    setError(null);
    // Clear cache and refetch
    const CACHE_KEY = getCacheKey(activeSubject.id);
    localStorage.removeItem(CACHE_KEY);
    localStorage.removeItem(`${CACHE_KEY}_timestamp`);
    window.location.reload();
  };

  // Show loading state while checking subjects
  if (subjectsLoading) {
    return (
      <div className="container mx-auto p-6 max-w-7xl">
        <TopicSearchSkeleton count={6} />
      </div>
    );
  }

  // Show "No subjects" state when no subjects are configured
  if (!hasSubjects) {
    return (
      <div className="container mx-auto p-6 max-w-7xl">
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <div className="p-4 bg-amber-100 dark:bg-amber-900/30 rounded-full mb-6">
            <BookOpen className="h-12 w-12 text-amber-600" />
          </div>
          <h1 className="text-3xl font-bold mb-3">No Subjects Configured</h1>
          <p className="text-muted-foreground max-w-md mb-8">
            {isAdmin
              ? 'Set up your first subject by uploading a Cambridge syllabus PDF.'
              : 'Please contact your administrator to set up a subject.'}
          </p>

          {isAdmin && (
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/admin/setup/syllabus">
                <Button size="lg" className="gap-2">
                  <FileUp className="h-5 w-5" />
                  Upload Syllabus
                </Button>
              </Link>
              <Link href="/admin">
                <Button variant="outline" size="lg" className="gap-2">
                  <Settings className="h-5 w-5" />
                  Admin Dashboard
                </Button>
              </Link>
            </div>
          )}

          {!isAdmin && (
            <Card className="max-w-md">
              <CardHeader>
                <CardTitle className="text-lg">Getting Started</CardTitle>
                <CardDescription>
                  Your administrator needs to complete the initial setup before you can start learning.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Once a subject is configured, you&apos;ll see syllabus topics here with PhD-level explanations available.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Hierarchy Breadcrumb (T050) */}
      <div className="mb-4">
        <HierarchyBreadcrumb subject={activeSubject} />
      </div>

      {/* Page Header with Gradient Background */}
      <div className="mb-8 relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-secondary/5 to-accent/10 p-8 border border-primary/20">
        {/* Decorative gradient blobs */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/20 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/20 rounded-full blur-3xl -z-10" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-primary/10 rounded-xl backdrop-blur-sm">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Teaching
              </h1>
              <p className="text-sm text-muted-foreground">
                PhD-Level {activeSubject?.name || 'Subject'} Explanations
              </p>
            </div>
          </div>
          <p className="text-base text-foreground/80 max-w-2xl">
            Browse {activeSubject ? formatSubjectShort(activeSubject) : ''} syllabus topics and request comprehensive, PhD-level explanations
          </p>
          {usingCache && (
            <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full">
              <span className="text-green-600 dark:text-green-400">⚡</span>
              <span className="text-sm font-medium text-green-600 dark:text-green-400">Loaded from cache (instant)</span>
            </div>
          )}
        </div>
      </div>

      {/* Error State (Persistent Alert) */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Failed to Load Topics</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button variant="outline" size="sm" onClick={handleRetry}>
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Browse/Search Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'browse' | 'search')}>
        <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
          <TabsTrigger value="browse" className="gap-2">
            <BookOpen className="h-4 w-4" />
            Browse
          </TabsTrigger>
          <TabsTrigger value="search" className="gap-2">
            <Search className="h-4 w-4" />
            Search
          </TabsTrigger>
        </TabsList>

        {/* Browse Tab */}
        <TabsContent value="browse" className="mt-0">
          {isLoading ? (
            <TopicSearchSkeleton count={6} />
          ) : (
            <TopicBrowser
              topics={topics}
              onTopicClick={handleTopicClick}
              subjectName={activeSubject ? formatSubjectShort(activeSubject) : undefined}
              syllabusContext={activeSyllabus ? {
                code: activeSyllabus.code,
                year_range: activeSyllabus.year_range,
              } : undefined}
            />
          )}
        </TabsContent>

        {/* Search Tab */}
        <TabsContent value="search" className="mt-0">
          {isLoading ? (
            <TopicSearchSkeleton count={5} />
          ) : (
            <TopicSearch topics={topics} onSelectTopic={handleTopicClick} />
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Stats (Footer) - Modern Cards */}
      {!isLoading && !error && (
        <div className="mt-12 pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Topics Count */}
            <div className="relative group overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 p-6 border border-primary/20 hover:border-primary/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-2xl -z-10 group-hover:scale-150 transition-transform duration-500" />
              <div className="text-5xl font-black text-primary mb-2">{topics.length}</div>
              <div className="text-sm font-medium text-muted-foreground">Topics Available</div>
            </div>

            {/* Subject Info */}
            <div className="relative group overflow-hidden rounded-2xl bg-gradient-to-br from-secondary/10 to-secondary/5 p-6 border border-secondary/20 hover:border-secondary/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-2xl -z-10 group-hover:scale-150 transition-transform duration-500" />
              <div className="text-3xl font-black text-secondary mb-2">{activeSubject?.name || '—'}</div>
              <div className="text-sm font-medium text-muted-foreground">
                {activeSubject ? `${activeSubject.academic_level_name}` : 'No Subject'}
              </div>
            </div>

            {/* Quality Level */}
            <div className="relative group overflow-hidden rounded-2xl bg-gradient-to-br from-accent/10 to-accent/5 p-6 border border-accent/20 hover:border-accent/40 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-accent/10 rounded-full blur-2xl -z-10 group-hover:scale-150 transition-transform duration-500" />
              <div className="text-3xl font-black text-accent mb-2">PhD-Level</div>
              <div className="text-sm font-medium text-muted-foreground">Explanation Quality</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
