/**
 * Coaching Page - Interactive AI Tutoring
 *
 * This page allows students to:
 * 1. Start a new coaching session by describing their struggle
 * 2. Have a conversation with the AI coach (Socratic method)
 * 3. Receive targeted explanations and follow-up questions
 * 4. See session outcome (resolved/needs_more_help/refer_to_teacher)
 *
 * Route: /coaching
 * Phase: MVP (User Story 1 + User Story 2)
 *
 * State Flow:
 * - No session: Show SessionInitForm
 * - Session active: Show ChatInterface (Phase 4)
 */

'use client';

import { useState } from 'react';
import { SessionInitForm } from '@/components/coaching/SessionInitForm';
import { ChatInterface } from '@/components/coaching/ChatInterface';
import { ErrorBoundary } from '@/components/coaching/ErrorBoundary';

export default function CoachingPage() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [firstMessage, setFirstMessage] = useState<string | null>(null);

  const handleSessionStart = (sessionId: string, initialMessage: string) => {
    console.log('Session started:', { sessionId, initialMessage });
    setActiveSessionId(sessionId);
    setFirstMessage(initialMessage);
  };

  const handleStartNewSession = () => {
    console.log('Starting new session - clearing current session');
    setActiveSessionId(null);
    setFirstMessage(null);
  };

  // If we have an active session, show ChatInterface
  if (activeSessionId) {
    return (
      <ErrorBoundary componentName="ChatInterface">
        <ChatInterface
          sessionId={activeSessionId}
          initialMessage={firstMessage || undefined}
          onStartNewSession={handleStartNewSession}
        />
      </ErrorBoundary>
    );
  }

  // No active session: Show session init form
  return (
    <ErrorBoundary componentName="SessionInitForm">
      <SessionInitForm onSuccess={handleSessionStart} />
    </ErrorBoundary>
  );
}
