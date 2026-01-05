'use client';

import { useEffect, useState } from 'react';
import { UserProfile } from '@/components/user/UserProfile';
import { ThemeToggle } from '@/components/theme-toggle';
import { BookOpen, ChevronRight, Menu, GraduationCap, MessageSquare, FolderOpen, Calendar, Shield, AlertCircle, FileText } from 'lucide-react';
import { useAdmin } from '@/lib/hooks/useAdmin';
import { useActiveSubject } from '@/lib/hooks/useSubjects';
import { useSyllabiForSubject } from '@/lib/hooks/useAcademicLevels';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';

/**
 * Dashboard Header - Shows app title and hierarchy breadcrumb
 *
 * Feature: 008-academic-level-hierarchy (T051)
 *
 * Shows: My Personal Examiner with hierarchy subtitle:
 * "A-Level > Economics > 9708" (when on teaching pages)
 */
export function DashboardHeader() {
  const pathname = usePathname();
  const [topicInfo, setTopicInfo] = useState<{ code: string; name: string } | null>(null);
  const { isAdmin } = useAdmin();
  const { data: activeSubject, hasSubjects, isLoading: subjectsLoading } = useActiveSubject();

  // Fetch syllabi for active subject to show in hierarchy
  const { data: syllabi } = useSyllabiForSubject(activeSubject?.id || null);
  const activeSyllabus = syllabi?.find((s) => s.is_active) || syllabi?.[0];

  // Listen for custom events from teaching page
  useEffect(() => {
    const handleTopicChange = (e: CustomEvent<{ code: string; name: string }>) => {
      setTopicInfo(e.detail);
    };

    const handleTopicClear = () => {
      setTopicInfo(null);
    };

    window.addEventListener('topic-loaded' as any, handleTopicChange);
    window.addEventListener('topic-cleared' as any, handleTopicClear);

    // Clear topic info when navigating away from teaching page
    if (!pathname?.startsWith('/teaching/')) {
      setTopicInfo(null);
    }

    return () => {
      window.removeEventListener('topic-loaded' as any, handleTopicChange);
      window.removeEventListener('topic-cleared' as any, handleTopicClear);
    };
  }, [pathname]);

  const isTeachingPage = pathname?.startsWith('/teaching/');
  const showTopicInfo = isTeachingPage && topicInfo;

  return (
    <nav className="sticky top-0 z-50 h-16 bg-card/80 backdrop-blur-md border-b border-border shadow-sm">
      <div className="h-full px-4 lg:px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/teaching"
            className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="p-2 bg-primary/10 rounded-lg">
              <BookOpen className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">
                My Personal Examiner
              </h1>
              {subjectsLoading ? (
                <p className="text-xs text-muted-foreground">Loading...</p>
              ) : hasSubjects && activeSubject ? (
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <span>{activeSubject.academic_level_name}</span>
                  <ChevronRight className="h-3 w-3" />
                  <span>{activeSubject.name}</span>
                  {activeSyllabus && (
                    <>
                      <ChevronRight className="h-3 w-3" />
                      <span className="font-mono font-medium">{activeSyllabus.code}</span>
                    </>
                  )}
                </p>
              ) : (
                <p className="text-xs text-amber-600 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  No subject configured
                </p>
              )}
            </div>
          </Link>

          {/* Topic breadcrumb - only shown on teaching page */}
          {showTopicInfo && (
            <>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
              <div className="flex items-center gap-2">
                <div className="px-2 py-1 bg-primary/10 rounded text-xs font-semibold text-primary">
                  {topicInfo.code}
                </div>
                <span className="text-sm font-medium text-foreground max-w-[300px] md:max-w-[500px] truncate">
                  {topicInfo.name}
                </span>
              </div>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Navigation Menu */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="lg:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Open menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetHeader>
                <SheetTitle>Navigation</SheetTitle>
                <SheetDescription>
                  Access all features of My Personal Examiner
                </SheetDescription>
              </SheetHeader>
              <nav className="flex flex-col gap-2 mt-6">
                <Link href="/teaching" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors">
                  <GraduationCap className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">Teaching</p>
                    <p className="text-xs text-muted-foreground">
                      {hasSubjects && activeSubject
                        ? `${activeSubject.academic_level_name} ${activeSubject.name}${activeSyllabus ? ` (${activeSyllabus.code})` : ''}`
                        : 'Browse syllabus topics'}
                    </p>
                  </div>
                </Link>
                <Link href="/coaching" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">Coaching</p>
                    <p className="text-xs text-muted-foreground">Practice with AI tutor</p>
                  </div>
                </Link>
                <Link href="/resources" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors">
                  <FolderOpen className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">Resources</p>
                    <p className="text-xs text-muted-foreground">Upload PDFs, videos & materials</p>
                  </div>
                </Link>
                <div className="flex items-center gap-3 px-4 py-3 rounded-lg opacity-50 cursor-not-allowed">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-muted-foreground">Study Planner</p>
                    <p className="text-xs text-muted-foreground">Coming soon...</p>
                  </div>
                </div>
                {/* Admin link - only visible for admins */}
                {isAdmin && (
                  <>
                    <div className="my-2 border-t border-border" />
                    <Link href="/admin" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors bg-amber-50 dark:bg-amber-950/30">
                      <Shield className="h-5 w-5 text-amber-600" />
                      <div>
                        <p className="font-medium text-amber-700 dark:text-amber-400">Admin</p>
                        <p className="text-xs text-amber-600/70">Manage subjects & content</p>
                      </div>
                    </Link>
                  </>
                )}
              </nav>
            </SheetContent>
          </Sheet>

          {/* Desktop Navigation - Hidden on mobile */}
          <div className="hidden lg:flex items-center gap-1">
            <Link href="/teaching">
              <Button variant="ghost" size="sm">
                <GraduationCap className="h-4 w-4 mr-2" />
                Teaching
              </Button>
            </Link>
            <Link href="/coaching">
              <Button variant="ghost" size="sm">
                <MessageSquare className="h-4 w-4 mr-2" />
                Coaching
              </Button>
            </Link>
            <Link href="/resources">
              <Button variant="ghost" size="sm">
                <FolderOpen className="h-4 w-4 mr-2" />
                Resources
              </Button>
            </Link>
            {/* Admin link - only visible for admins */}
            {isAdmin && (
              <Link href="/admin">
                <Button variant="ghost" size="sm" className="text-amber-600 hover:text-amber-700 hover:bg-amber-50">
                  <Shield className="h-4 w-4 mr-2" />
                  Admin
                </Button>
              </Link>
            )}
          </div>

          <ThemeToggle />
          <UserProfile />
        </div>
      </div>
    </nav>
  );
}
