/**
 * Saved Explanations Page
 *
 * Display all bookmarked explanations for the current student.
 *
 * Feature: 005-teaching-page (User Story 3: Bookmark Explanations)
 *
 * Architecture:
 * - Uses SavedExplanationsList component for main content
 * - TanStack Query handles data fetching and caching
 * - localStorage provides explanation content cache
 *
 * Constitutional Compliance:
 * - Principle V: Multi-tenant isolation (student_id enforced by backend)
 * - Principle VI: Constructive feedback (preserves full explanation content)
 */

'use client';

import Link from 'next/link';
import { ArrowLeft, BookmarkIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SavedExplanationsList } from '@/components/teaching/SavedExplanationsList';

export default function SavedExplanationsPage() {
  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Back Navigation */}
      <div className="mb-6">
        <Link href="/teaching">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Topics
          </Button>
        </Link>
      </div>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <BookmarkIcon className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Saved Explanations</h1>
        </div>
        <p className="text-muted-foreground">
          Your bookmarked Economics topics for quick review
        </p>
      </div>

      {/* Saved Explanations List */}
      <SavedExplanationsList />
    </div>
  );
}
