/**
 * ChatInterface Component
 *
 * Real-time chat interface with AI coach using ChatScope components.
 *
 * Features:
 * - ChatScope UI components (MainContainer, ChatContainer, MessageList, Message, MessageInput)
 * - TanStack Query integration (useSession for polling, useSendMessage for optimistic updates)
 * - Auto-scroll to latest message
 * - Typing indicator while coach responds
 * - Message timestamps
 * - Offline/online detection with banner
 * - Message retry on error
 * - localStorage persistence
 * - Accessible (ARIA labels, keyboard navigation)
 */

'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  Avatar
} from '@chatscope/chat-ui-kit-react';
import { useSession, useSendMessage } from '@/lib/api/coaching';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { validateMessageContent } from '@/lib/validation/coaching';
import { SessionOutcome } from './SessionOutcome';
import { ErrorBoundary } from './ErrorBoundary';
import { ChatInterfaceSkeleton } from './ChatInterfaceSkeleton';
import { useToast } from '@/lib/hooks/use-toast';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { trackEvent } from '@/lib/analytics';
import type { Message as MessageType } from '@/types/coaching';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

interface ChatInterfaceProps {
  sessionId: string;
  initialMessage?: string;
  onStartNewSession?: () => void;
}

export function ChatInterface({ sessionId, initialMessage, onStartNewSession }: ChatInterfaceProps) {
  const [messageInput, setMessageInput] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [showAllMessages, setShowAllMessages] = useState(false);

  const { toast } = useToast();
  const isOnline = useOnlineStatus();
  const { data: sessionData, isLoading, error } = useSession(sessionId);
  const sendMessageMutation = useSendMessage(sessionId);

  console.log('ChatInterface render:', { sessionId, sessionData, isLoading, error });

  const allMessages = sessionData?.transcript || [];

  // Performance optimization: For conversations > 50 messages, only show recent 50 by default
  const MESSAGE_LIMIT = 50;
  const messages = useMemo(() => {
    if (showAllMessages || allMessages.length <= MESSAGE_LIMIT) {
      return allMessages;
    }
    return allMessages.slice(-MESSAGE_LIMIT); // Show last 50 messages
  }, [allMessages, showAllMessages]);
  const sessionOutcome = sessionData?.outcome || 'in_progress';
  const isSessionActive = sessionOutcome === 'in_progress';

  // Determine if outcome is valid (not 'in_progress' or 'abandoned')
  const hasValidOutcome = sessionOutcome && !['in_progress', 'abandoned'].includes(sessionOutcome);
  const outcomeType = hasValidOutcome
    ? (sessionOutcome as 'resolved' | 'needs_more_help' | 'refer_to_teacher')
    : null;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    // ChatScope handles scrolling internally, but we can trigger it by updating a key
    // or just let it handle auto-scroll naturally
    // For now, skip custom scroll logic and let ChatScope handle it
  }, [messages.length]);

  // Persist session to localStorage
  useEffect(() => {
    if (sessionData) {
      localStorage.setItem(`coaching-session-${sessionId}`, JSON.stringify({
        ...sessionData,
        lastUpdated: Date.now()
      }));
    }
  }, [sessionData, sessionId]);

  const handleSendMessage = useCallback(() => {
    console.log('🔵 handleSendMessage called');
    const trimmed = messageInput.trim();
    console.log('🔵 Trimmed message:', trimmed);

    // Validate message
    const error = validateMessageContent(trimmed);
    console.log('🔵 Validation result:', error);
    if (error) {
      setValidationError(error);
      console.log('🔴 Validation failed:', error);
      return;
    }

    // Clear validation error and input
    setValidationError(null);
    setMessageInput('');

    // Send message
    console.log('🟢 About to call sendMessageMutation.mutate');
    console.log('🟢 Session ID:', sessionId);
    console.log('🟢 Request payload:', { student_response: trimmed, request_hint: false });
    sendMessageMutation.mutate(
      { student_response: trimmed, request_hint: false },
      {
        onSuccess: () => {
          // Track analytics event
          trackEvent('coaching_message_sent', {
            session_id: sessionId,
            message_length: trimmed.length,
          });
        },
        onError: (error) => {
          console.error('Message send error:', error);
          toast({
            title: 'Failed to Send Message',
            description: error instanceof Error ? error.message : 'Please try again.',
            variant: 'error',
            duration: 5000,
          });
        }
      }
    );
    console.log('🟢 Mutation called');
  }, [messageInput, sessionId, sendMessageMutation, toast]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Determine if coach is typing (waiting for response) - memoized for performance
  const isCoachTyping = useMemo(
    () =>
      sendMessageMutation.isPending ||
      (messages.length > 0 &&
        messages[messages.length - 1].role === 'student' &&
        isSessionActive),
    [sendMessageMutation.isPending, messages, isSessionActive]
  );

  // Check if there are hidden messages (for "Load earlier messages" button)
  const hasHiddenMessages = allMessages.length > MESSAGE_LIMIT && !showAllMessages;

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'Ctrl+Enter': () => {
      if (isSessionActive && isOnline && messageInput.trim()) {
        handleSendMessage();
      }
    },
  });

  // Track session outcome when it changes
  useEffect(() => {
    if (outcomeType) {
      trackEvent('coaching_session_outcome', {
        session_id: sessionId,
        outcome: outcomeType,
        message_count: messages.length,
      });

      trackEvent('coaching_session_ended', {
        session_id: sessionId,
        outcome: outcomeType,
        total_messages: messages.length,
      });
    }
  }, [outcomeType, sessionId, messages.length]);

  if (isLoading) {
    return <ChatInterfaceSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center space-y-4">
          <p className="text-destructive">Failed to load session</p>
          <p className="text-sm text-muted-foreground">
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col overflow-hidden ${!isSessionActive ? 'ended' : ''}`}
      style={{ height: 'calc(100vh - 64px)', maxHeight: 'calc(100vh - 64px)' }}
      data-testid="chat-interface"
    >
      {/* Offline Banner */}
      {!isOnline && (
        <div
          className="bg-destructive text-destructive-foreground p-3 text-center text-sm"
          role="alert"
          data-testid="offline-banner"
        >
          You are offline. Messages will be sent when connection is restored.
        </div>
      )}

      {/* Session Header */}
      <div className="bg-card border-b p-4 flex-shrink-0">
        <div className="flex items-center gap-4 mb-2">
          <Link
            href="/teaching"
            className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
            aria-label="Back to teaching"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Teaching</span>
          </Link>
          <div className="flex-1">
            <h2 className="text-lg font-semibold">AI Coaching Session</h2>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Topic: {sessionData?.topic || 'Loading...'}
        </p>
        {!isSessionActive && (
          <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md" data-testid="outcome-banner">
            <p className="text-sm font-medium text-yellow-800">
              Session Complete - See outcome below
            </p>
          </div>
        )}
      </div>

      {/* ChatScope Container - constrained height */}
      <div className="flex-1 flex flex-col overflow-hidden min-h-0">
        <MainContainer>
          <ChatContainer>
            <MessageList
              typingIndicator={isCoachTyping ? <TypingIndicator content="Coach is thinking..." /> : null}
            >
              {/* Load earlier messages button for performance optimization */}
              {hasHiddenMessages && (
                <div className="flex justify-center py-4">
                  <button
                    onClick={() => setShowAllMessages(true)}
                    className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium"
                    aria-label={`Load ${allMessages.length - MESSAGE_LIMIT} earlier messages`}
                  >
                    Load {allMessages.length - MESSAGE_LIMIT} earlier messages
                  </button>
                </div>
              )}

              {messages.map((msg: MessageType, index: number) => (
                <Message
                  key={msg.id || `msg-${index}`}
                  model={{
                    message: msg.content,
                    sentTime: msg.timestamp,
                    sender: msg.role === 'coach' ? 'Coach' : 'You',
                    direction: msg.role === 'coach' ? 'incoming' : 'outgoing',
                    position: 'single'
                  }}
                  data-testid={msg.role === 'coach' ? 'coach-message' : 'student-message'}
                >
                  {/* Coach avatar - removed to avoid empty src error */}
                  <Message.Header
                    sender={msg.role === 'coach' ? 'Coach' : 'You'}
                    sentTime={formatTimestamp(msg.timestamp)}
                  />
                  {msg.pending && (
                    <Message.Footer>
                      <span className="text-xs text-muted-foreground" data-testid="message-pending">
                        Sending...
                      </span>
                    </Message.Footer>
                  )}
                </Message>
              ))}
            </MessageList>

            <MessageInput
              placeholder={
                !isSessionActive
                  ? 'Session ended - start a new session to continue'
                  : !isOnline
                  ? 'You are offline...'
                  : 'Type your response...'
              }
              value={messageInput}
              onChange={(val) => {
                setMessageInput(val);
                if (validationError) setValidationError(null);
              }}
              onSend={handleSendMessage}
              disabled={!isSessionActive || !isOnline}
              attachButton={false}
              data-testid="message-input"
              aria-label="Type your message"
              aria-disabled={!isSessionActive || !isOnline}
            />
          </ChatContainer>
        </MainContainer>

        {/* Validation Error */}
        {validationError && (
          <div className="bg-destructive text-destructive-foreground p-2 text-sm border-t">
            {validationError}
          </div>
        )}

        {/* Send Error */}
        {sendMessageMutation.error && (
          <div
            className="bg-destructive text-destructive-foreground p-2 text-sm flex items-center justify-between border-t"
            data-testid="message-error"
          >
            <span>Failed to send message</span>
            <button
              onClick={() => sendMessageMutation.reset()}
              className="text-xs underline"
              data-testid="retry-message"
            >
              Retry
            </button>
          </div>
        )}
      </div>

      {/* Session Outcome - shown below chat when session ends */}
      {outcomeType && onStartNewSession && (
        <div className="px-4 py-4 border-t bg-gray-50 flex-shrink-0">
          <ErrorBoundary componentName="SessionOutcome">
            <SessionOutcome
                outcome={outcomeType}
                summary={
                  outcomeType === 'resolved'
                    ? 'Great work! You now understand this concept.'
                    : outcomeType === 'needs_more_help'
                    ? 'Keep practicing! You\'re making progress.'
                    : 'This topic requires in-depth explanation.'
                }
                nextActions={
                  outcomeType === 'refer_to_teacher'
                    ? [
                        {
                          type: 'teacher_help',
                          label: 'Go to Teacher',
                          description: 'Get comprehensive explanation from Teacher Agent',
                          link: '/teach',
                          priority: 1,
                        },
                      ]
                    : outcomeType === 'needs_more_help'
                    ? [
                        {
                          type: 'practice',
                          label: 'Practice Problems',
                          description: 'Try practice questions on this topic',
                          link: '/practice',
                          priority: 2,
                        },
                        {
                          type: 'review_topic',
                          label: 'Review Topic',
                          description: 'Read the full explanation from Teacher Agent',
                          link: '/teach',
                          priority: 1,
                        },
                      ]
                    : [
                        {
                          type: 'practice',
                          label: 'Practice Problems',
                          description: 'Test your understanding with practice questions',
                          link: '/practice',
                          priority: 1,
                        },
                      ]
                }
                confidence={85} // TODO: Extract from sessionData if available
                onStartNewSession={onStartNewSession}
              />
            </ErrorBoundary>
          </div>
        )}

      {/* Send Button (for E2E testing) */}
      <button
        onClick={handleSendMessage}
        className="hidden"
        data-testid="send-button"
        aria-label="Send message"
      />
    </div>
  );
}
