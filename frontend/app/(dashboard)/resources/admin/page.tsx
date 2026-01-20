/**
 * Admin Resource Review Dashboard
 *
 * Feature: 007-resource-bank-files (T089: Admin Review Dashboard)
 * Created: 2025-12-27
 *
 * This page allows admins to:
 * 1. View list of pending resources
 * 2. Preview PDF resources (first 3 pages)
 * 3. Approve resources (changes visibility to PUBLIC)
 * 4. Reject resources (deletes file + record)
 * 5. Edit resource metadata before approval
 * 6. View student information (name, email)
 *
 * Route: /resources/admin
 * Access: Admin only
 *
 * Constitutional Compliance:
 * - FR-028: One-way approve transition
 * - FR-029: Delete on reject
 * - FR-070/FR-071/FR-072: Linear state machine
 */

'use client';

import { useState, useEffect } from 'react';
import { Check, X, Eye, Edit, AlertCircle, FileText } from 'lucide-react';
import {
  listPendingResources,
  getResourcePreview,
  approveResource,
  rejectResource,
  updateResourceMetadata,
  getStudentId,
  type PendingResource,
  type PdfPreview,
} from '@/lib/api/resources';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function AdminResourceReviewPage() {
  // Get authenticated admin ID
  const [adminId, setAdminId] = useState<string | null>(null);

  // State
  const [pendingResources, setPendingResources] = useState<PendingResource[]>([]);
  const [selectedResource, setSelectedResource] = useState<PendingResource | null>(null);
  const [preview, setPreview] = useState<PdfPreview | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Get authenticated admin ID on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const id = await getStudentId();
        setAdminId(id);
      } catch (err) {
        setError('Not authenticated. Please log in.');
      }
    };
    initAuth();
  }, []);

  // Load pending resources when adminId is set
  useEffect(() => {
    if (adminId) {
      loadPendingResources();
    }
  }, [adminId]);

  const loadPendingResources = async () => {
    if (!adminId) return;

    try {
      setLoading(true);
      setError(null);
      const pending = await listPendingResources(adminId);
      setPendingResources(pending);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load pending resources');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async (resource: PendingResource) => {
    if (!adminId) return;

    setSelectedResource(resource);
    setEditTitle(resource.title);
    setEditDescription('');
    setEditMode(false);

    try {
      const previewData = await getResourcePreview(resource.id, adminId);
      setPreview(previewData);
    } catch (err) {
      console.error('Preview failed:', err);
      setPreview(null);
    }
  };

  const handleApprove = async (resourceId: string) => {
    if (!adminId) return;

    if (!confirm('Approve this resource? It will become publicly visible to all students.')) {
      return;
    }

    try {
      setActionLoading(true);
      await approveResource(resourceId, adminId);

      // Remove from pending list
      setPendingResources((prev) => prev.filter((r) => r.id !== resourceId));
      setSelectedResource(null);
      setPreview(null);

      alert('Resource approved successfully!');
    } catch (err) {
      alert(`Approval failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (resourceId: string) => {
    if (!adminId) return;

    const reason = prompt('Enter rejection reason (optional):');
    if (reason === null) return; // User cancelled

    if (!confirm('Reject and DELETE this resource? This action cannot be undone.')) {
      return;
    }

    try {
      setActionLoading(true);
      await rejectResource(resourceId, adminId, reason || undefined);

      // Remove from pending list
      setPendingResources((prev) => prev.filter((r) => r.id !== resourceId));
      setSelectedResource(null);
      setPreview(null);

      alert('Resource rejected and deleted successfully.');
    } catch (err) {
      alert(`Rejection failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateMetadata = async () => {
    if (!selectedResource || !adminId) return;

    try {
      setActionLoading(true);
      await updateResourceMetadata(
        selectedResource.id,
        adminId,
        editTitle,
        editDescription || undefined
      );

      // Update local state
      setPendingResources((prev) =>
        prev.map((r) =>
          r.id === selectedResource.id ? { ...r, title: editTitle } : r
        )
      );
      setSelectedResource({ ...selectedResource, title: editTitle });
      setEditMode(false);

      alert('Metadata updated successfully!');
    } catch (err) {
      alert(`Update failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setActionLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Admin Resource Review</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Review and approve pending resource uploads
        </p>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-red-500 mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending Resources List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Pending Resources ({pendingResources.length})</CardTitle>
            <CardDescription>Click to preview and review</CardDescription>
          </CardHeader>
          <CardContent className="max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-3 border rounded animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : pendingResources.length === 0 ? (
              <div className="text-center text-gray-600 py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p>No pending resources to review</p>
              </div>
            ) : (
              <div className="space-y-2">
                {pendingResources.map((resource) => (
                  <div
                    key={resource.id}
                    className={`p-3 border rounded cursor-pointer transition-colors ${
                      selectedResource?.id === resource.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => handlePreview(resource)}
                  >
                    <div className="font-medium text-sm mb-1">{resource.title}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {resource.student_name} • {formatFileSize(resource.file_size)}
                    </div>
                    <div className="flex gap-1 mt-2">
                      <Badge variant="outline" className="text-xs">
                        {resource.resource_type}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Preview and Actions Panel */}
        <Card className="lg:col-span-2">
          {!selectedResource ? (
            <CardContent className="pt-6 text-center text-gray-600">
              <Eye className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>Select a resource to preview and review</p>
            </CardContent>
          ) : (
            <>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    {editMode ? (
                      <Input
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="text-xl font-bold mb-2"
                      />
                    ) : (
                      <CardTitle>{selectedResource.title}</CardTitle>
                    )}
                    <CardDescription>
                      Uploaded by: {selectedResource.student_name} ({selectedResource.student_email})
                      <br />
                      Date: {new Date(selectedResource.upload_date).toLocaleDateString()} •
                      Size: {formatFileSize(selectedResource.file_size)}
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEditMode(!editMode)}
                    disabled={actionLoading}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Edit Form */}
                {editMode && (
                  <div className="space-y-3 p-4 border rounded bg-gray-50 dark:bg-gray-900">
                    <div>
                      <label className="text-sm font-medium">Title</label>
                      <Input
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Description (optional)</label>
                      <Input
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        placeholder="Add a description..."
                      />
                    </div>
                    <Button
                      onClick={handleUpdateMetadata}
                      disabled={actionLoading || !editTitle.trim()}
                      className="w-full"
                    >
                      Save Changes
                    </Button>
                  </div>
                )}

                {/* Preview */}
                {preview ? (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">
                      Preview (showing {preview.preview_pages.length} of {preview.total_pages}{' '}
                      pages)
                    </div>
                    {preview.preview_pages.map((page) => (
                      <div key={page.page_number} className="border rounded p-2">
                        <div className="text-xs text-gray-600 mb-2">
                          Page {page.page_number}
                        </div>
                        <img
                          src={`data:image/png;base64,${page.image_base64}`}
                          alt={`Page ${page.page_number}`}
                          className="w-full border rounded"
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-600 py-8">
                    <p>Preview not available for this resource type</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4 border-t">
                  <Button
                    onClick={() => handleApprove(selectedResource.id)}
                    disabled={actionLoading}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Approve
                  </Button>
                  <Button
                    onClick={() => handleReject(selectedResource.id)}
                    disabled={actionLoading}
                    variant="destructive"
                    className="flex-1"
                  >
                    <X className="mr-2 h-4 w-4" />
                    Reject & Delete
                  </Button>
                </div>
              </CardContent>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
