/**
 * Resource Browser Page - Student View
 *
 * Feature: 007-resource-bank-files (T088: Frontend Resource Browser)
 * Created: 2025-12-27
 *
 * This page allows students to:
 * 1. Browse public resources + own private uploads
 * 2. Search resources by keywords
 * 3. Upload new resources (PDFs, YouTube)
 * 4. View quota usage (X/100 resources)
 * 5. Filter by resource type and visibility
 *
 * Route: /resources
 * Access: Authenticated students only
 *
 * State Flow:
 * - Load resources on mount
 * - Real-time quota display
 * - Upload modal/dialog
 * - Search results
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Upload, FileText, Video, Book, AlertCircle } from 'lucide-react';
import {
  listResources,
  searchResources,
  getQuotaStatus,
  getStudentId,
  type FileResource,
  type ResourceSearchResult,
  type QuotaStatus,
  type ResourceType,
  type ResourceVisibility,
} from '@/lib/api/resources';
import { getStudentData } from '@/lib/auth/student-cache';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ResourceUpload } from '@/components/resources/ResourceUpload';

export default function ResourceBrowserPage() {
  const router = useRouter();

  // Get authenticated student ID
  const [studentId, setStudentId] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  // State
  const [resources, setResources] = useState<FileResource[]>([]);
  const [quotaStatus, setQuotaStatus] = useState<QuotaStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedType, setSelectedType] = useState<ResourceType | undefined>(undefined);
  const [selectedVisibility, setSelectedVisibility] = useState<ResourceVisibility | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Check auth and redirect admins FAST using cached data
  useEffect(() => {
    const initAuth = async () => {
      try {
        // TEMPORARY: BYPASS CACHE - Always fetch fresh to debug
        console.log('[Resources] 🔍 DEBUG MODE: Fetching fresh data (bypassing cache)');

        const response = await fetch('/api/student');
        if (!response.ok) {
          throw new Error('Not authenticated');
        }
        const data = await response.json();

        console.log('[Resources] 📡 RAW API RESPONSE:', JSON.stringify(data, null, 2));

        console.log('[Resources] ===== AUTH CHECK =====');
        console.log('[Resources] Email:', data.email);
        console.log('[Resources] is_admin:', data.is_admin);
        console.log('[Resources] is_admin type:', typeof data.is_admin);
        console.log('[Resources] is_admin === true:', data.is_admin === true);
        console.log('[Resources] =======================');

        // ADMIN REDIRECT: If admin, redirect immediately
        if (data.is_admin === true) {
          console.log('[Resources] ✅ ADMIN DETECTED - REDIRECTING NOW');
          console.log('[Resources] Redirecting to: /resources/admin');
          window.location.href = '/resources/admin';
          return; // Stop execution
        }

        // STUDENT: Load page normally
        console.log('[Resources] ✅ STUDENT CONFIRMED - Loading student page');
        setStudentId(data.student_id);
        setIsAdmin(false);
        setAuthChecked(true);
      } catch (err) {
        console.error('[Resources] ❌ Auth error:', err);
        setError('Not authenticated. Please log in.');
        setLoading(false);
        setAuthChecked(true);
      }
    };
    initAuth();
  }, []);

  // Load resources and quota in parallel when studentId or filters change
  // Only load after auth check is complete and user is confirmed to be a student
  useEffect(() => {
    if (authChecked && studentId && !isAdmin) {
      loadResourcesAndQuota();
    }
  }, [studentId, selectedType, selectedVisibility, isAdmin, authChecked]);

  const loadResourcesAndQuota = async () => {
    if (!studentId) return;

    try {
      setLoading(true);
      setError(null);

      // Parallel loading - both requests run simultaneously
      const [resourcesResponse, quotaResponse] = await Promise.all([
        listResources(studentId, selectedVisibility, selectedType),
        getQuotaStatus(studentId),
      ]);

      setResources(resourcesResponse.resources);
      setQuotaStatus(quotaResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  // Debounce timer for search
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleSearch = useCallback((query: string) => {
    if (!studentId) return;

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (!query.trim()) {
      setIsSearching(false);
      loadResourcesAndQuota();
      return;
    }

    // Debounce search by 500ms
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        setLoading(true);
        setIsSearching(true);
        const results = await searchResources(query, studentId, selectedType);
        setResources(results.map((r: ResourceSearchResult) => r.resource));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed');
      } finally {
        setLoading(false);
      }
    }, 500); // 500ms debounce
  }, [studentId, selectedType]);

  const getResourceIcon = (type: ResourceType) => {
    switch (type) {
      case 'video':
        return <Video className="h-5 w-5" />;
      case 'textbook':
      case 'past_paper':
        return <Book className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getVisibilityColor = (visibility: ResourceVisibility) => {
    switch (visibility) {
      case 'public':
        return 'bg-green-500';
      case 'private':
        return 'bg-blue-500';
      case 'pending_review':
        return 'bg-yellow-500';
    }
  };

  // Show loading spinner during auth check (prevents page from rendering)
  if (!authChecked) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-lg text-muted-foreground">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header with Quota */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Resource Library</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Browse resources and upload your own materials
          </p>
        </div>

        {quotaStatus && (
          <Card className="w-64">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Quota Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {quotaStatus.current_usage}/{quotaStatus.limit}
                </span>
                <span className="text-sm text-gray-600">
                  {quotaStatus.percentage_used}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className={`h-2 rounded-full ${
                    quotaStatus.percentage_used > 80
                      ? 'bg-red-500'
                      : quotaStatus.percentage_used > 60
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                  }`}
                  style={{ width: `${quotaStatus.percentage_used}%` }}
                />
              </div>
              {quotaStatus.percentage_used > 80 && (
                <div className="flex items-center gap-1 mt-2 text-sm text-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <span>Approaching limit</span>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search resources by keyword..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  if (!e.target.value.trim()) {
                    loadResourcesAndQuota();
                    setIsSearching(false);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch(searchQuery);
                  }
                }}
              />
            </div>
            <Button onClick={() => handleSearch(searchQuery)}>Search</Button>
            <Button onClick={() => setShowUploadModal(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload
            </Button>
          </div>

          {/* Filter Pills - Role-based visibility */}
          <div className="flex gap-2 mt-4">
            <span className="text-sm text-gray-600">Filters:</span>

            {/* Admin-only: Show "All" filter */}
            {isAdmin && (
              <Badge
                variant={selectedVisibility === undefined ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedVisibility(undefined)}
              >
                All
              </Badge>
            )}

            {/* Everyone: Show "Public" filter */}
            <Badge
              variant={selectedVisibility === 'public' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setSelectedVisibility('public')}
            >
              Public
            </Badge>

            {/* Admin: "Private" (all private) | Student: "My Private" (own only) */}
            <Badge
              variant={selectedVisibility === 'private' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setSelectedVisibility('private')}
            >
              {isAdmin ? 'Private' : 'My Private'}
            </Badge>

            {/* Admin: "Pending Review (All)" | Student: "My Pending" */}
            <Badge
              variant={selectedVisibility === 'pending_review' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setSelectedVisibility('pending_review')}
            >
              {isAdmin ? 'Pending Review (All)' : 'My Pending'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2 mt-2" />
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-gray-200 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        /* Resource Grid */
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {resources.length === 0 ? (
            <Card className="col-span-full">
              <CardContent className="pt-6 text-center text-gray-600">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="font-medium mb-2">
                  {isSearching
                    ? `No resources found matching "${searchQuery}"`
                    : selectedVisibility === 'pending_review'
                    ? isAdmin
                      ? 'No pending resources to review'
                      : 'You have no pending resources'
                    : selectedVisibility === 'private'
                    ? isAdmin
                      ? 'No private resources available'
                      : 'You have no private resources yet'
                    : selectedVisibility === 'public'
                    ? 'No public resources available'
                    : 'No resources available'}
                </p>
                <p className="text-sm text-muted-foreground">
                  {selectedVisibility === 'pending_review'
                    ? isAdmin
                      ? 'Resources appear here when students upload files for admin approval'
                      : 'Your uploads appear here while waiting for admin approval'
                    : selectedVisibility === 'private'
                    ? 'Upload resources and set visibility to "Private" to keep them personal'
                    : 'Click "Upload" to add PDFs, videos, or YouTube transcripts'}
                </p>
              </CardContent>
            </Card>
          ) : (
            resources.map((resource) => (
              <Card key={resource.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      {getResourceIcon(resource.resource_type)}
                      <CardTitle className="text-lg">{resource.title}</CardTitle>
                    </div>
                    <Badge className={getVisibilityColor(resource.visibility)}>
                      {resource.visibility}
                    </Badge>
                  </div>
                  <CardDescription>
                    {resource.resource_type} •{' '}
                    {new Date(resource.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {resource.extracted_text ? (
                      <p className="line-clamp-3">{resource.extracted_text.substring(0, 150)}...</p>
                    ) : (
                      <p className="italic">No preview available</p>
                    )}
                  </div>
                  <div className="flex justify-between items-center mt-4">
                    <Badge variant="outline">{resource.resource_type}</Badge>
                    {resource.s3_sync_status !== 'success' && (
                      <span className="text-xs text-gray-500">
                        Sync: {resource.s3_sync_status}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Results Summary */}
      {!loading && resources.length > 0 && (
        <div className="text-center text-sm text-gray-600">
          Showing {resources.length} resource{resources.length !== 1 ? 's' : ''}
          {isSearching && ` for "${searchQuery}"`}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && studentId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="max-w-2xl w-full">
            <ResourceUpload
              studentId={studentId}
              onSuccess={() => {
                setShowUploadModal(false);
                loadResourcesAndQuota(); // Parallel loading
              }}
              onClose={() => setShowUploadModal(false)}
              quotaRemaining={quotaStatus ? quotaStatus.limit - quotaStatus.current_usage : undefined}
            />
          </div>
        </div>
      )}
    </div>
  );
}
