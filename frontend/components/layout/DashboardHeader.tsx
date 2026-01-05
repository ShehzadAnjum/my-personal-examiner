'use client';

import { ReactNode, useEffect, useState } from 'react';
import { UserProfile } from '@/components/user/UserProfile';
import { ThemeToggle } from '@/components/theme-toggle';
import { BookOpen, ChevronRight, Menu, GraduationCap, MessageSquare, FolderOpen, Calendar, FileText } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
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
 * Dashboard Header - Shows app title and optionally topic breadcrumb
 *
 * When on /teaching/[topicId] page, displays:
 * My Personal Examiner > [Topic Code] [Topic Name]
 */
export function DashboardHeader() {
  const pathname = usePathname();
  const [topicInfo, setTopicInfo] = useState<{ code: string; name: string } | null>(null);

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
              <p className="text-xs text-muted-foreground">Economics 9708 A-Level</p>
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
                    <p className="text-xs text-muted-foreground">Learn Economics topics</p>
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
          </div>

          <ThemeToggle />
          <UserProfile />
        </div>
      </div>
    </nav>
  );
}
