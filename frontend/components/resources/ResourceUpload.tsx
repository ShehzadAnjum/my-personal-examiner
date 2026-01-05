/**
 * Resource Upload Component
 *
 * Feature: 007-resource-bank-files (T090: Upload Component)
 * Created: 2025-12-27
 *
 * Provides file upload functionality with:
 * - Drag-and-drop zone
 * - File picker button
 * - File size validation (max 50MB client-side)
 * - File type validation (PDF, images)
 * - Upload progress bar
 * - YouTube URL input field
 * - Title and description fields
 * - Resource type selector
 * - Quota warning
 *
 * Usage:
 * ```tsx
 * <ResourceUpload
 *   studentId={studentId}
 *   onSuccess={() => console.log('Upload successful')}
 *   onClose={() => setShowUpload(false)}
 * />
 * ```
 */

'use client';

import { useState, useRef } from 'react';
import { Upload, File, Video, AlertCircle, CheckCircle, X } from 'lucide-react';
import {
  uploadFile,
  uploadYouTubeVideo,
  type ResourceType,
} from '@/lib/api/resources';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];

interface ResourceUploadProps {
  studentId: string;
  onSuccess: () => void;
  onClose: () => void;
  quotaRemaining?: number;
}

export function ResourceUpload({
  studentId,
  onSuccess,
  onClose,
  quotaRemaining,
}: ResourceUploadProps) {
  // State
  const [uploadType, setUploadType] = useState<'file' | 'youtube'>('file');
  const [file, setFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [resourceType, setResourceType] = useState<ResourceType>('user_upload');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // File validation
  const validateFile = (selectedFile: File): string | null => {
    // Check file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      return `File size exceeds 50MB limit (${(selectedFile.size / (1024 * 1024)).toFixed(1)}MB)`;
    }

    // Check file type
    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      return `Invalid file type. Allowed: PDF, PNG, JPEG (got: ${selectedFile.type})`;
    }

    return null;
  };

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const validationError = validateFile(droppedFile);

      if (validationError) {
        setError(validationError);
        return;
      }

      setFile(droppedFile);
      setTitle(droppedFile.name.replace(/\.[^/.]+$/, '')); // Set title from filename
      setError(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validationError = validateFile(selectedFile);

      if (validationError) {
        setError(validationError);
        return;
      }

      setFile(selectedFile);
      setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''));
      setError(null);
    }
  };

  const handleFileUpload = async () => {
    if (!file || !title.trim()) {
      setError('Please select a file and enter a title');
      return;
    }

    if (quotaRemaining !== undefined && quotaRemaining <= 0) {
      setError('Quota exceeded. Please delete some resources before uploading.');
      return;
    }

    try {
      setUploading(true);
      setProgress(0);
      setError(null);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      await uploadFile(file, title, resourceType, studentId);

      clearInterval(progressInterval);
      setProgress(100);

      setTimeout(() => {
        onSuccess();
      }, 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const handleYouTubeUpload = async () => {
    if (!youtubeUrl.trim() || !title.trim()) {
      setError('Please enter a YouTube URL and title');
      return;
    }

    // Basic YouTube URL validation
    if (!youtubeUrl.includes('youtube.com') && !youtubeUrl.includes('youtu.be')) {
      setError('Invalid YouTube URL');
      return;
    }

    if (quotaRemaining !== undefined && quotaRemaining <= 0) {
      setError('Quota exceeded. Please delete some resources before uploading.');
      return;
    }

    try {
      setUploading(true);
      setProgress(0);
      setError(null);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 300);

      await uploadYouTubeVideo(youtubeUrl, title, studentId);

      clearInterval(progressInterval);
      setProgress(100);

      setTimeout(() => {
        onSuccess();
      }, 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'YouTube upload failed');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Upload Resource</CardTitle>
            <CardDescription>
              {quotaRemaining !== undefined && (
                <span>
                  {quotaRemaining} upload{quotaRemaining !== 1 ? 's' : ''} remaining
                </span>
              )}
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Upload Type Selector */}
        <div className="flex gap-2">
          <Button
            variant={uploadType === 'file' ? 'default' : 'outline'}
            onClick={() => setUploadType('file')}
            className="flex-1"
          >
            <File className="mr-2 h-4 w-4" />
            File Upload
          </Button>
          <Button
            variant={uploadType === 'youtube' ? 'default' : 'outline'}
            onClick={() => setUploadType('youtube')}
            className="flex-1"
          >
            <Video className="mr-2 h-4 w-4" />
            YouTube
          </Button>
        </div>

        {/* File Upload Mode */}
        {uploadType === 'file' ? (
          <>
            {/* Drag and Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="space-y-2">
                  <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-gray-600">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setFile(null);
                      setTitle('');
                    }}
                  >
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div>
                    <p className="font-medium">Drag and drop your file here</p>
                    <p className="text-sm text-gray-600">or click to browse</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Select File
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileChange}
                  />
                  <p className="text-xs text-gray-500">
                    Max size: 50MB • Allowed: PDF, PNG, JPEG
                  </p>
                </div>
              )}
            </div>

            {/* Title Input */}
            <div>
              <label className="text-sm font-medium mb-1 block">Title *</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter resource title..."
                disabled={uploading}
              />
            </div>

            {/* Description Input */}
            <div>
              <label className="text-sm font-medium mb-1 block">
                Description (optional)
              </label>
              <Input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a description..."
                disabled={uploading}
              />
            </div>

            {/* Resource Type Selector */}
            <div>
              <label className="text-sm font-medium mb-1 block">Type</label>
              <div className="flex gap-2 flex-wrap">
                {['user_upload', 'textbook', 'article'].map((type) => (
                  <Badge
                    key={type}
                    variant={resourceType === type ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => setResourceType(type as ResourceType)}
                  >
                    {type.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Upload Button */}
            <Button
              onClick={handleFileUpload}
              disabled={!file || !title.trim() || uploading}
              className="w-full"
            >
              {uploading ? `Uploading... ${progress}%` : 'Upload File'}
            </Button>
          </>
        ) : (
          /* YouTube Upload Mode */
          <>
            <div>
              <label className="text-sm font-medium mb-1 block">YouTube URL *</label>
              <Input
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                disabled={uploading}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Title *</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter video title..."
                disabled={uploading}
              />
            </div>

            <Button
              onClick={handleYouTubeUpload}
              disabled={!youtubeUrl.trim() || !title.trim() || uploading}
              className="w-full"
            >
              {uploading ? `Processing... ${progress}%` : 'Extract Transcript'}
            </Button>
          </>
        )}

        {/* Upload Progress */}
        {uploading && (
          <div className="space-y-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-center text-gray-600">{progress}% complete</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-2 text-red-600 text-sm p-3 bg-red-50 dark:bg-red-950 rounded">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Quota Warning */}
        {quotaRemaining !== undefined && quotaRemaining <= 10 && quotaRemaining > 0 && (
          <div className="flex items-center gap-2 text-yellow-600 text-sm p-3 bg-yellow-50 dark:bg-yellow-950 rounded">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>
              Only {quotaRemaining} upload{quotaRemaining !== 1 ? 's' : ''} remaining
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
