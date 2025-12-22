/**
 * SessionInitForm Component
 *
 * Form for starting a new coaching session.
 * Student describes their struggle/topic (10-500 chars).
 *
 * Features:
 * - Textarea with character counter
 * - Client-side validation
 * - Loading state during session creation
 * - Error handling with retry
 * - Accessible (ARIA labels, keyboard navigation)
 */

'use client';

import { useState } from 'react';
import { useStartSession } from '@/lib/api/coaching';
import { validateTopic } from '@/lib/validation/coaching';
import { SessionInitFormSkeleton } from './SessionInitFormSkeleton';
import { useToast } from '@/hooks/useToast';
import { trackEvent } from '@/lib/analytics';
import { cn } from '@/lib/utils';

interface SessionInitFormProps {
  onSuccess: (sessionId: string, firstMessage: string) => void;
}

export function SessionInitForm({ onSuccess }: SessionInitFormProps) {
  const [topic, setTopic] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const { toast } = useToast();
  const startSessionMutation = useStartSession();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate topic
    const error = validateTopic(topic);
    if (error) {
      setValidationError(error);
      return;
    }

    // Clear validation error
    setValidationError(null);

    // Extract a simple topic from the struggle description (first 5 words or "General Economics")
    const extractedTopic = topic
      .trim()
      .split(/\s+/)
      .slice(0, 5)
      .join(' ') || 'General Economics';

    // Start session
    startSessionMutation.mutate(
      {
        student_id: '2fbda3c9-f6a3-4581-928a-077042239c38', // TODO: Get from auth (test.coaching@example.com)
        topic: extractedTopic,
        struggle_description: topic.trim()
      },
      {
        onSuccess: (data) => {
          console.log('Session creation success:', data);

          // Track analytics event
          trackEvent('coaching_session_started', {
            session_id: data.session_id,
            topic: extractedTopic,
          });

          toast({
            title: 'Coaching Session Started',
            description: 'Your AI coach is ready to help you!',
            variant: 'success',
            duration: 3000,
          });
          onSuccess(data.session_id, data.coach_message);
        },
        onError: (error) => {
          console.error('Session creation error:', error);
          toast({
            title: 'Failed to Start Session',
            description: error instanceof Error ? error.message : 'Please try again.',
            variant: 'error',
            duration: 5000,
          });
        }
      }
    );
  };

  const handleTopicChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTopic(e.target.value);
    // Clear validation error when user starts typing
    if (validationError) {
      setValidationError(null);
    }
  };

  const isLoading = startSessionMutation.isPending;
  const error = startSessionMutation.error;
  const charCount = topic.length;
  const maxChars = 500;

  if (isLoading) {
    return <SessionInitFormSkeleton />;
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-bold">AI Coaching Session</h1>
          <p className="text-muted-foreground mt-2">
            Describe what you're struggling with, and I'll help you understand it.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="topic"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              What are you struggling with?
            </label>
            <textarea
              id="topic"
              name="topic"
              value={topic}
              onChange={handleTopicChange}
              placeholder="Example: I don't understand price elasticity"
              className={cn(
                'flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
                (validationError || error) && 'border-destructive'
              )}
              aria-label="Describe your struggle"
              aria-describedby="topic-hint topic-error char-count"
              aria-invalid={!!validationError || !!error}
              disabled={isLoading}
              maxLength={maxChars + 50} // Allow a bit over for better UX
            />
            <div className="flex justify-between items-start">
              <p
                id="topic-hint"
                className="text-xs text-muted-foreground"
              >
                Be specific about what confuses you (10-500 characters)
              </p>
              <p
                id="char-count"
                className={cn(
                  'text-xs',
                  charCount > maxChars ? 'text-destructive' : 'text-muted-foreground'
                )}
                aria-live="polite"
              >
                {charCount}/{maxChars}
              </p>
            </div>
            {validationError && (
              <p
                id="topic-error"
                className="text-sm text-destructive"
                role="alert"
              >
                {validationError}
              </p>
            )}
            {error && (
              <div className="space-y-2">
                <p className="text-sm text-destructive" role="alert">
                  {error instanceof Error
                    ? error.message
                    : typeof error === 'object' && error !== null && 'message' in error
                    ? String((error as any).message)
                    : 'Failed to start session. Please try again.'}
                </p>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={isLoading || !topic.trim()}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
            >
              Start Coaching Session
            </button>
            {error && (
              <button
                type="button"
                onClick={() => startSessionMutation.reset()}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
              >
                Try again
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
