'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useToast } from '@/lib/hooks/use-toast';
import {
  BookOpen,
  FileUp,
  CheckSquare,
  Sparkles,
  Database,
  FolderOpen,
  Shield,
  AlertTriangle,
  Loader2,
  ArrowRight,
  Users,
  Settings,
  BarChart3,
  FileCheck,
  Trash2,
  RefreshCw,
  GraduationCap,
} from 'lucide-react';
import { useAdmin } from '@/lib/hooks/useAdmin';
import { useAcademicLevels } from '@/lib/hooks/useAcademicLevels';
import { getAllSetupStatus, type SubjectSetupStatus } from '@/lib/api/admin-setup';
import { clearSyllabusCache } from '@/lib/hooks/useTopics';

interface AdminCard {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
  badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline';
  disabled?: boolean;
  category: 'setup' | 'content' | 'system';
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAdmin, isLoading: adminLoading } = useAdmin();
  const { data: academicLevels } = useAcademicLevels();
  const [setupStatus, setSetupStatus] = useState<SubjectSetupStatus[]>([]);
  const [pendingResources, setPendingResources] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [clearingCache, setClearingCache] = useState(false);

  /**
   * Clear all frontend caches (localStorage)
   */
  const handleClearAllCache = () => {
    setClearingCache(true);
    try {
      // Clear syllabus/topics cache
      clearSyllabusCache();

      // Clear explanation cache
      Object.keys(localStorage).forEach((key) => {
        if (
          key.startsWith('explanation_') ||
          key.startsWith('saved_explanations') ||
          key.startsWith('coaching_') ||
          key.startsWith('resource_')
        ) {
          localStorage.removeItem(key);
        }
      });

      toast({
        title: 'Cache Cleared',
        description: 'All frontend caches have been cleared. Refresh the page to see changes.',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to clear cache. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setClearingCache(false);
    }
  };

  /**
   * Clear only syllabus/topics cache
   */
  const handleClearSyllabusCache = () => {
    setClearingCache(true);
    try {
      clearSyllabusCache();
      toast({
        title: 'Syllabus Cache Cleared',
        description: 'Topics will be fetched fresh from the server on next load.',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to clear syllabus cache.',
        variant: 'destructive',
      });
    } finally {
      setClearingCache(false);
    }
  };

  useEffect(() => {
    if (!adminLoading && !isAdmin) {
      router.push('/teaching');
    }
  }, [isAdmin, adminLoading, router]);

  useEffect(() => {
    if (isAdmin) {
      loadDashboardData();
    }
  }, [isAdmin]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load setup status
      const status = await getAllSetupStatus();
      setSetupStatus(status.subjects);

      // Load pending resources count
      try {
        const response = await fetch('/api/student');
        if (response.ok) {
          const { student_id } = await response.json();
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const pendingResponse = await fetch(
            `${API_BASE_URL}/api/admin/resources/pending?student_id=${student_id}`
          );
          if (pendingResponse.ok) {
            const pending = await pendingResponse.json();
            setPendingResources(Array.isArray(pending) ? pending.length : 0);
          }
        }
      } catch (e) {
        console.error('Failed to load pending resources:', e);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (adminLoading || loading) {
    return (
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="container mx-auto p-6 max-w-6xl">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Access Denied</AlertTitle>
          <AlertDescription>
            You do not have admin privileges. Redirecting...
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Calculate summary stats
  const incompleteSubjects = setupStatus.filter(s => !s.is_complete).length;
  const totalTopics = setupStatus.reduce((sum, s) => sum + s.topics_count, 0);
  const totalExplanations = setupStatus.reduce((sum, s) => sum + s.explanations_count, 0);

  // Define admin cards
  const academicLevelsCount = academicLevels?.length ?? 0;
  const adminCards: AdminCard[] = [
    // Setup Category
    {
      title: 'Academic Levels',
      description: 'Manage academic levels like A-Level, IGCSE, and O-Level',
      href: '/admin/setup/academic-levels',
      icon: <GraduationCap className="h-6 w-6" />,
      badge: `${academicLevelsCount} level${academicLevelsCount !== 1 ? 's' : ''}`,
      badgeVariant: 'default',
      category: 'setup',
    },
    {
      title: 'Subject Setup Wizard',
      description: 'Upload syllabi, extract topics, and generate v1 explanations',
      href: '/admin/setup',
      icon: <BookOpen className="h-6 w-6" />,
      badge: incompleteSubjects > 0 ? `${incompleteSubjects} incomplete` : 'All complete',
      badgeVariant: incompleteSubjects > 0 ? 'destructive' : 'default',
      category: 'setup',
    },
    {
      title: 'Upload Syllabus',
      description: 'Add a new subject by uploading Cambridge syllabus PDF',
      href: '/admin/setup/syllabus',
      icon: <FileUp className="h-6 w-6" />,
      category: 'setup',
    },

    // Content Management Category
    {
      title: 'Resource Review',
      description: 'Approve or reject user-uploaded resources',
      href: '/resources/admin',
      icon: <FileCheck className="h-6 w-6" />,
      badge: pendingResources > 0 ? `${pendingResources} pending` : undefined,
      badgeVariant: pendingResources > 0 ? 'destructive' : undefined,
      category: 'content',
    },
    {
      title: 'Resource Tagging',
      description: 'Tag resources to syllabus topics for better organization',
      href: '/resources/admin',
      icon: <CheckSquare className="h-6 w-6" />,
      category: 'content',
    },

    // System Category
    {
      title: 'Data Backup',
      description: 'Export localStorage cache and database backup instructions',
      href: '/admin/backup',
      icon: <Database className="h-6 w-6" />,
      category: 'system',
    },
    {
      title: 'System Metrics',
      description: 'View system health and performance metrics',
      href: '/admin/metrics',
      icon: <BarChart3 className="h-6 w-6" />,
      disabled: true,
      badge: 'Coming Soon',
      badgeVariant: 'secondary',
      category: 'system',
    },
  ];

  const setupCards = adminCards.filter(c => c.category === 'setup');
  const contentCards = adminCards.filter(c => c.category === 'content');
  const systemCards = adminCards.filter(c => c.category === 'system');

  const renderCard = (card: AdminCard) => (
    <Link
      key={card.title}
      href={card.disabled ? '#' : card.href}
      className={card.disabled ? 'cursor-not-allowed' : ''}
    >
      <Card className={`h-full transition-all hover:shadow-md ${card.disabled ? 'opacity-60' : 'hover:border-primary/50'}`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="p-2 bg-primary/10 rounded-lg w-fit">
              {card.icon}
            </div>
            {card.badge && (
              <Badge variant={card.badgeVariant || 'secondary'}>
                {card.badge}
              </Badge>
            )}
          </div>
          <CardTitle className="text-lg mt-3">{card.title}</CardTitle>
          <CardDescription>{card.description}</CardDescription>
        </CardHeader>
        {!card.disabled && (
          <CardContent className="pt-0">
            <div className="flex items-center text-sm text-primary">
              Open <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </CardContent>
        )}
      </Card>
    </Link>
  );

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
            <Shield className="h-6 w-6 text-amber-600" />
          </div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        </div>
        <p className="text-muted-foreground">
          Manage subjects, content, and system settings
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{setupStatus.length}</div>
            <p className="text-sm text-muted-foreground">Subjects</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{totalTopics}</div>
            <p className="text-sm text-muted-foreground">Topics</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{totalExplanations}</div>
            <p className="text-sm text-muted-foreground">Explanations</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-amber-600">{pendingResources}</div>
            <p className="text-sm text-muted-foreground">Pending Reviews</p>
          </CardContent>
        </Card>
      </div>

      {/* Setup Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          Subject Setup
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {setupCards.map(renderCard)}
        </div>
      </div>

      {/* Content Management Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FolderOpen className="h-5 w-5" />
          Content Management
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contentCards.map(renderCard)}
        </div>
      </div>

      {/* System Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Settings className="h-5 w-5" />
          System
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {systemCards.map(renderCard)}
        </div>
      </div>

      {/* Cache Management Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Trash2 className="h-5 w-5" />
          Cache Management
        </h2>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Clear Frontend Cache</CardTitle>
            <CardDescription>
              Clear cached data stored in your browser. Use this after database resets or when you see stale data.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                onClick={handleClearSyllabusCache}
                disabled={clearingCache}
              >
                {clearingCache ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Clear Syllabus Cache
              </Button>
              <Button
                variant="destructive"
                onClick={handleClearAllCache}
                disabled={clearingCache}
              >
                {clearingCache ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Clear All Cache
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-3">
              <strong>Syllabus Cache:</strong> Topics list (24hr cache)<br />
              <strong>All Cache:</strong> Topics, explanations, coaching sessions, resources
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
