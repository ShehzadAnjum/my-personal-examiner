/**
 * TanStack Query API Client for Coaching Page
 *
 * This file defines the React hooks and API client functions for interacting
 * with the coaching backend APIs.
 *
 * Pattern: TanStack Query (v5.62+) with retry, caching, and optimistic updates
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  CoachingSession,
  CreateSessionRequest,
  StartSessionResponse,
  SendMessageRequest,
  SendMessageResponse,
  GetSessionResponse,
  ListSessionsResponse,
  PendingMessage,
  APIError,
  Message
} from '@/types/coaching';

// ============================================================================
// API Base Configuration
// ============================================================================

/**
 * Base API URL (from environment variable)
 * Production: https://api.mypersonalexaminer.com
 * Development: http://localhost:8000
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get authentication token from cookie/localStorage
 * (Implementation depends on Phase I auth setup)
 */
function getAuthToken(): string | null {
  // TODO: Implement based on Phase I authentication
  // Options: Cookie, localStorage, or Next.js auth context
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
}

/**
 * Standard fetch wrapper with auth headers
 */
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options?.headers
    }
  });

  if (!response.ok) {
    const error: APIError = await response.json();
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// Query Keys (for cache management)
// ============================================================================

export const coachingKeys = {
  all: ['coaching'] as const,
  sessions: () => [...coachingKeys.all, 'sessions'] as const,
  session: (id: string) => [...coachingKeys.all, 'session', id] as const,
  messages: (sessionId: string) => [...coachingKeys.session(sessionId), 'messages'] as const
};

// ============================================================================
// API Functions (used by hooks)
// ============================================================================

/**
 * POST /api/coaching/tutor-session
 * Start a new coaching session
 */
async function startSession(request: CreateSessionRequest): Promise<StartSessionResponse> {
  // Get student_id from auth token or use test UUID for MVP
  // Test student: test.coaching@example.com (ID: 2fbda3c9-f6a3-4581-928a-077042239c38)
  const studentId = request.student_id || getStudentIdFromAuth() || '2fbda3c9-f6a3-4581-928a-077042239c38';

  return apiFetch<StartSessionResponse>('/api/coaching/tutor-session', {
    method: 'POST',
    body: JSON.stringify({
      student_id: studentId,
      topic: request.topic,
      struggle_description: request.struggle_description,
      context: request.context
    })
  });
}

/**
 * Get student ID from auth context
 * TODO: Implement proper auth integration
 */
function getStudentIdFromAuth(): string | null {
  // TODO: Extract from JWT token or auth context
  // For now, return null to use test UUID
  return null;
}

/**
 * POST /api/coaching/session/{session_id}/respond
 * Send a message to the coach
 */
async function sendMessage(
  sessionId: string,
  request: SendMessageRequest
): Promise<SendMessageResponse> {
  console.log('📡 sendMessage API function called');
  console.log('📡 Session ID:', sessionId);
  console.log('📡 Request payload:', request);
  console.log('📡 URL:', `/api/coaching/session/${sessionId}/respond`);

  const response = await apiFetch<SendMessageResponse>(`/api/coaching/session/${sessionId}/respond`, {
    method: 'POST',
    body: JSON.stringify(request)
  });

  console.log('📡 sendMessage response received:', response);
  return response;
}

/**
 * GET /api/coaching/session/{session_id}
 * Get complete session transcript
 */
async function getSession(sessionId: string): Promise<GetSessionResponse> {
  return apiFetch<GetSessionResponse>(`/api/coaching/session/${sessionId}`);
}

/**
 * GET /api/coaching/sessions
 * List all user's coaching sessions
 */
async function listSessions(): Promise<ListSessionsResponse> {
  return apiFetch<ListSessionsResponse>('/api/coaching/sessions');
}

// ============================================================================
// React Query Hooks
// ============================================================================

/**
 * Hook: Start a new coaching session
 *
 * Usage:
 * ```tsx
 * const startSessionMutation = useStartSession();
 * startSessionMutation.mutate({ topic: "I don't understand elasticity" });
 * ```
 *
 * Returns the new session and initial coach message.
 */
export function useStartSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: startSession,
    onSuccess: (data) => {
      // Note: Backend returns session_id, coach_message, outcome
      // We'll fetch the full session separately if needed
      // For now, just invalidate sessions list
      queryClient.invalidateQueries({ queryKey: coachingKeys.sessions() });
    },
    retry: 2, // Retry up to 2 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000)
  });
}

/**
 * Hook: Send a message to the coach
 *
 * Usage:
 * ```tsx
 * const sendMessageMutation = useSendMessage(sessionId);
 * sendMessageMutation.mutate({ content: "Demand goes down?" });
 * ```
 *
 * Implements optimistic updates (message appears instantly before backend confirms).
 */
export function useSendMessage(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: SendMessageRequest) => {
      console.log('🚀 useSendMessage mutationFn called');
      console.log('🚀 Session ID:', sessionId);
      console.log('🚀 Request:', request);
      return sendMessage(sessionId, request);
    },

    // Optimistic update: show message immediately
    onMutate: async (request) => {
      console.log('⏳ useSendMessage onMutate called');
      console.log('⏳ Request:', request);
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: coachingKeys.session(sessionId) });

      // Snapshot previous value
      const previousSession = queryClient.getQueryData<GetSessionResponse>(
        coachingKeys.session(sessionId)
      );

      // Optimistically add student message
      if (previousSession) {
        const pendingMessage: Message = {
          role: 'student',
          content: request.student_response,
          timestamp: new Date().toISOString(),
          pending: true
        };

        queryClient.setQueryData<GetSessionResponse>(coachingKeys.session(sessionId), {
          ...previousSession,
          transcript: [
            ...previousSession.transcript,
            pendingMessage
          ]
        });
      }

      // Return context for rollback
      return { previousSession };
    },

    // On error, rollback to previous state
    onError: (err, request, context) => {
      console.log('❌ useSendMessage onError called');
      console.log('❌ Error:', err);
      console.log('❌ Request:', request);
      console.log('❌ Context:', context);
      if (context?.previousSession) {
        queryClient.setQueryData(coachingKeys.session(sessionId), context.previousSession);
      }
    },

    // On success, refetch to get the full updated transcript
    onSuccess: (data) => {
      console.log('Send message response:', data);
      // Just invalidate and refetch the full session
      // The backend will have the complete transcript with both student and coach messages
      queryClient.invalidateQueries({ queryKey: coachingKeys.session(sessionId) });
    },

    retry: 3, // Retry up to 3 times (FR-019)
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  });
}

/**
 * Hook: Get a coaching session with all messages
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useSession(sessionId);
 * ```
 *
 * Includes polling for new coach responses (every 2 seconds).
 * Persists to localStorage for offline access.
 */
export function useSession(sessionId: string | null) {
  const queryClient = useQueryClient();

  const query = useQuery<GetSessionResponse>({
    queryKey: sessionId ? coachingKeys.session(sessionId) : ['coaching', 'null'],
    queryFn: async (): Promise<GetSessionResponse> => {
      if (!sessionId) throw new Error('Session ID required');

      console.log('Fetching session:', sessionId);

      // Try localStorage first for instant load
      const cached = localStorage.getItem(`coaching-session-${sessionId}`);
      if (cached) {
        const parsed = JSON.parse(cached);
        console.log('Found cached session:', parsed);
        // If cache is fresh (<5 min), use it
        if (Date.now() - parsed.lastUpdated < 300000) {
          // Fetch from API in background to sync
          getSession(sessionId).then((apiData) => {
            console.log('Background fetch result:', apiData);
            queryClient.setQueryData(coachingKeys.session(sessionId), apiData);
          });
          return parsed as GetSessionResponse;
        }
      }

      // Cache miss or stale - fetch from API
      const sessionData = await getSession(sessionId);
      console.log('Fetched session from API:', sessionData);

      // Persist to localStorage
      localStorage.setItem(`coaching-session-${sessionId}`, JSON.stringify({
        ...sessionData,
        lastUpdated: Date.now()
      }));

      return sessionData;
    },
    enabled: !!sessionId,
    refetchInterval: (query) => {
      // Poll every 2 seconds if session is in progress
      return query.state.data?.outcome === 'in_progress' ? 2000 : false;
    },
    retry: 2,
    staleTime: 5000 // Consider data stale after 5 seconds
  });

  return query;
}

/**
 * Hook: List all user's coaching sessions
 *
 * Usage:
 * ```tsx
 * const { data, isLoading } = useSessions();
 * ```
 *
 * Used for P3 feature (session history).
 */
export function useSessions() {
  return useQuery({
    queryKey: coachingKeys.sessions(),
    queryFn: listSessions,
    staleTime: 60000 // Consider data fresh for 1 minute
  });
}

// ============================================================================
// Query Client Configuration
// ============================================================================

/**
 * Recommended QueryClient config for coaching feature
 *
 * Usage:
 * ```tsx
 * // In app/providers.tsx or similar
 * const queryClient = new QueryClient(coachingQueryConfig);
 * ```
 */
export const coachingQueryConfig = {
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst' as const, // Use cache when offline
      gcTime: 1000 * 60 * 5, // Garbage collect after 5 minutes
      retry: 2
    },
    mutations: {
      networkMode: 'always' as const, // Retry mutations when back online
      retry: 3
    }
  }
};