/**
 * Session Detail Page (Read-Only Transcript)
 *
 * Display a past coaching session in read-only mode.
 *
 * Route: /coaching/[sessionId]
 * Purpose: View historical coaching session transcripts
 *
 * Features:
 * - Reuses ChatInterface component in read-only mode
 * - Displays full conversation history
 * - No message input (session ended)
 * - Shows session outcome
 * - "Back to History" navigation
 */

'use client';

import { use } from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { ChatInterface } from '@/components/coaching/ChatInterface';

interface SessionDetailPageProps {
  params: Promise<{
    sessionId: string;
  }>;
}

export default function SessionDetailPage({ params }: SessionDetailPageProps) {
  // Unwrap the params Promise (Next.js 15+ pattern)
  const { sessionId } = use(params);

  return (
    <div className="h-screen flex flex-col">
      {/* Header with back button */}
      <div className="bg-white border-b p-4 flex items-center gap-4">
        <Link
          href="/coaching/history"
          className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors"
          aria-label="Back to coaching history"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to History</span>
        </Link>

        <div className="flex-1 text-center">
          <h1 className="text-xl font-semibold text-gray-900">Session Transcript</h1>
          <p className="text-sm text-gray-500">Read-only view</p>
        </div>

        <div className="w-32"></div> {/* Spacer for centering */}
      </div>

      {/* Chat interface in read-only mode */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface
          sessionId={sessionId}
          onStartNewSession={() => {
            // Navigate back to coaching page
            window.location.href = '/coaching';
          }}
        />
      </div>
    </div>
  );
}
