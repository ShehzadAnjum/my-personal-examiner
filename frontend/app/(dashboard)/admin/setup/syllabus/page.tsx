'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  FileUp,
  Upload,
  X,
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Loader2,
  FileText,
} from 'lucide-react';
import { uploadSyllabus, type SyllabusUploadResponse } from '@/lib/api/admin-setup';
import { HierarchySelector } from '@/components/admin/HierarchySelector';

/**
 * Syllabus Upload Page
 *
 * Updated for 008-academic-level-hierarchy:
 * - Admin must select academic level → subject FIRST
 * - Syllabus code and year are optional overrides
 * - Creates Syllabus record linked to selected subject
 *
 * Flow: Select Subject → Upload PDF → Review Topics
 */
export default function SyllabusUploadPage() {
  const router = useRouter();

  // Hierarchy selection (NEW - 008-academic-level-hierarchy)
  const [selectedLevelId, setSelectedLevelId] = useState<string | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(null);

  // File upload state
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SyllabusUploadResponse | null>(null);

  // Override fields (optional - auto-detected from PDF)
  const [syllabusCode, setSyllabusCode] = useState('');
  const [syllabusYear, setSyllabusYear] = useState('');

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      if (files[0].type === 'application/pdf') {
        setFile(files[0]);
        setError(null);
      } else {
        setError('Please upload a PDF file');
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      if (files[0].type === 'application/pdf') {
        setFile(files[0]);
        setError(null);
      } else {
        setError('Please upload a PDF file');
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !selectedSubjectId) return;

    try {
      setUploading(true);
      setError(null);

      const response = await uploadSyllabus(file, selectedSubjectId, {
        syllabus_code: syllabusCode || undefined,
        syllabus_year: syllabusYear || undefined,
      });

      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Check if ready to upload
  const canUpload = file && selectedSubjectId && !uploading;

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      {/* Header */}
      <div className="mb-6">
        <Link href="/admin/setup" className="text-sm text-muted-foreground hover:text-foreground flex items-center mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Setup
        </Link>
        <h1 className="text-3xl font-bold mb-2">Upload Syllabus</h1>
        <p className="text-muted-foreground">
          Select a subject, then upload the Cambridge syllabus PDF to extract topics automatically.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Result */}
      {result && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-700">Upload Successful</AlertTitle>
          <AlertDescription className="text-green-600">
            <div className="mt-2 space-y-1">
              <p><strong>Subject:</strong> {result.subject_name}</p>
              <p><strong>Syllabus Code:</strong> {result.syllabus_code}</p>
              <p><strong>Syllabus Year:</strong> {result.syllabus_year}</p>
              <p><strong>Topics Extracted:</strong> {result.topics_extracted}</p>
              {result.low_confidence_count > 0 && (
                <p className="text-amber-600">
                  <AlertTriangle className="h-3 w-3 inline mr-1" />
                  {result.low_confidence_count} topics need review (low confidence)
                </p>
              )}
            </div>
            {result.warnings.length > 0 && (
              <div className="mt-3 p-2 bg-amber-50 rounded border border-amber-200">
                <p className="font-medium text-amber-700">Warnings:</p>
                <ul className="list-disc list-inside text-sm text-amber-600">
                  {result.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Step 1: Subject Selection (NEW - 008-academic-level-hierarchy) */}
      {!result && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm">1</span>
              Select Subject
            </CardTitle>
            <CardDescription>
              Choose the academic level and subject this syllabus belongs to.
              Create the subject first if it doesn&apos;t exist.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <HierarchySelector
              selectedLevelId={selectedLevelId}
              selectedSubjectId={selectedSubjectId}
              onLevelChange={(level) => {
                setSelectedLevelId(level?.id || null);
                setSelectedSubjectId(null); // Reset subject when level changes
              }}
              onSubjectChange={(subject) => setSelectedSubjectId(subject?.id || null)}
              showSubjectSelector={true}
              disabled={uploading}
            />
            {selectedLevelId && !selectedSubjectId && (
              <p className="text-sm text-muted-foreground mt-2">
                No subjects?{' '}
                <Link href="/admin/setup/subjects" className="text-primary hover:underline">
                  Create a subject first
                </Link>
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Upload Area */}
      {!result && selectedSubjectId && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm">2</span>
              <FileUp className="h-5 w-5" />
              Upload Syllabus PDF
            </CardTitle>
            <CardDescription>
              Upload the official Cambridge syllabus PDF (e.g., 9708_y25_sy.pdf)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Drag & Drop Zone */}
            <div
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : file
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="flex items-center justify-center gap-3">
                  <FileText className="h-10 w-10 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={clearFile}
                    className="ml-4"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <>
                  <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg font-medium mb-1">Drop your PDF here</p>
                  <p className="text-sm text-muted-foreground mb-4">or click to browse</p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Optional Overrides */}
      {!result && file && selectedSubjectId && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-muted text-muted-foreground text-sm">3</span>
              Optional Overrides
            </CardTitle>
            <CardDescription>
              Leave blank to auto-detect from PDF. Fill in to override detected values.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="syllabusCode">Syllabus Code</Label>
                <Input
                  id="syllabusCode"
                  placeholder="e.g., 9708"
                  value={syllabusCode}
                  onChange={(e) => setSyllabusCode(e.target.value)}
                  disabled={uploading}
                />
              </div>
              <div>
                <Label htmlFor="syllabusYear">Syllabus Year Range</Label>
                <Input
                  id="syllabusYear"
                  placeholder="e.g., 2023-2025"
                  value={syllabusYear}
                  onChange={(e) => setSyllabusYear(e.target.value)}
                  disabled={uploading}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Link href="/admin/setup">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </Link>

        {result ? (
          <Link href={`/admin/setup/topics?syllabus=${result.syllabus_id}`}>
            <Button>
              Review Topics
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        ) : (
          <Button onClick={handleUpload} disabled={!canUpload}>
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Extract Topics
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
