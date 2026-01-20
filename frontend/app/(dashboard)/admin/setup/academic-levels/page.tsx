'use client';

import { useState } from 'react';
import { GraduationCap, Plus, Pencil, Trash2, ChevronRight, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/lib/hooks/use-toast';
import {
  useAcademicLevels,
  useCreateAcademicLevel,
  useUpdateAcademicLevel,
  useDeleteAcademicLevel,
  type AcademicLevelSummary,
} from '@/lib/hooks/useAcademicLevels';
import { Skeleton } from '@/components/ui/skeleton';
import Link from 'next/link';

/**
 * Academic Levels Management Page
 *
 * Feature: 008-academic-level-hierarchy (US1)
 *
 * Allows admins to:
 * - View all academic levels with subject counts
 * - Create new academic levels
 * - Edit existing academic levels
 * - Delete empty academic levels
 */
export default function AcademicLevelsPage() {
  const { data: levels, isLoading, error } = useAcademicLevels();
  const { toast } = useToast();

  // Create dialog state
  const [createOpen, setCreateOpen] = useState(false);
  const [createData, setCreateData] = useState({
    name: '',
    code: '',
    description: '',
    exam_board: 'Cambridge International',
  });

  // Edit dialog state
  const [editOpen, setEditOpen] = useState(false);
  const [editLevel, setEditLevel] = useState<AcademicLevelSummary | null>(null);
  const [editData, setEditData] = useState({
    name: '',
    description: '',
    exam_board: '',
  });

  // Delete dialog state
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteLevel, setDeleteLevel] = useState<AcademicLevelSummary | null>(null);

  // Mutations
  const createMutation = useCreateAcademicLevel();
  const updateMutation = useUpdateAcademicLevel();
  const deleteMutation = useDeleteAcademicLevel();

  // Handle create
  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({
        name: createData.name,
        code: createData.code,
        description: createData.description || undefined,
        exam_board: createData.exam_board,
      });
      toast({
        title: 'Academic Level Created',
        description: `${createData.name} has been created successfully.`,
      });
      setCreateOpen(false);
      setCreateData({ name: '', code: '', description: '', exam_board: 'Cambridge International' });
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to create academic level',
      });
    }
  };

  // Handle edit
  const handleEdit = async () => {
    if (!editLevel) return;
    try {
      await updateMutation.mutateAsync({
        levelId: editLevel.id,
        data: {
          name: editData.name || undefined,
          description: editData.description || undefined,
          exam_board: editData.exam_board || undefined,
        },
      });
      toast({
        title: 'Academic Level Updated',
        description: `${editData.name || editLevel.name} has been updated.`,
      });
      setEditOpen(false);
      setEditLevel(null);
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to update academic level',
      });
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!deleteLevel) return;
    try {
      await deleteMutation.mutateAsync(deleteLevel.id);
      toast({
        title: 'Academic Level Deleted',
        description: `${deleteLevel.name} has been deleted.`,
      });
      setDeleteOpen(false);
      setDeleteLevel(null);
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete academic level',
      });
    }
  };

  // Open edit dialog
  const openEdit = (level: AcademicLevelSummary) => {
    setEditLevel(level);
    setEditData({
      name: level.name,
      description: '',
      exam_board: level.exam_board,
    });
    setEditOpen(true);
  };

  // Open delete dialog
  const openDelete = (level: AcademicLevelSummary) => {
    setDeleteLevel(level);
    setDeleteOpen(true);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              Error Loading Academic Levels
            </CardTitle>
            <CardDescription>
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Academic Levels</h1>
          <p className="text-muted-foreground">
            Manage academic levels like A-Level, IGCSE, and O-Level
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Level
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Academic Level</DialogTitle>
              <DialogDescription>
                Add a new academic level to organize subjects.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., A-Level"
                  value={createData.name}
                  onChange={(e) => setCreateData({ ...createData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="code">Code</Label>
                <Input
                  id="code"
                  placeholder="e.g., A"
                  value={createData.code}
                  onChange={(e) => setCreateData({ ...createData, code: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="exam_board">Exam Board</Label>
                <Input
                  id="exam_board"
                  placeholder="e.g., Cambridge International"
                  value={createData.exam_board}
                  onChange={(e) => setCreateData({ ...createData, exam_board: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Description of this academic level..."
                  value={createData.description}
                  onChange={(e) => setCreateData({ ...createData, description: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreate}
                disabled={!createData.name || !createData.code || createMutation.isPending}
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Empty State */}
      {levels && levels.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GraduationCap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Academic Levels</h3>
            <p className="text-muted-foreground text-center mb-4">
              Get started by creating your first academic level.
            </p>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Level
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Academic Levels Grid */}
      {levels && levels.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {levels.map((level) => (
            <Card key={level.id} className="relative group">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <GraduationCap className="h-5 w-5 text-primary" />
                      {level.name}
                    </CardTitle>
                    <CardDescription>
                      {level.exam_board} ({level.code})
                    </CardDescription>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEdit(level)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openDelete(level)}
                      disabled={level.subjects_count > 0}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">
                    {level.subjects_count} subject{level.subjects_count !== 1 ? 's' : ''}
                  </span>
                  <Link href={`/admin/setup/academic-levels/${level.id}`}>
                    <Button variant="ghost" size="sm">
                      View Subjects
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Academic Level</DialogTitle>
            <DialogDescription>
              Update the details for {editLevel?.name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-exam_board">Exam Board</Label>
              <Input
                id="edit-exam_board"
                value={editData.exam_board}
                onChange={(e) => setEditData({ ...editData, exam_board: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={editData.description}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Academic Level</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {deleteLevel?.name}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
