/**
 * TanStack Query API Client for Coaching Page
 *
 * This file defines the React hooks and API client functions for interacting
 * with the coaching backend APIs.
 *
 * Pattern: TanStack Query (v5.62+) with retry, caching, and optimistic updates
 *
 * NOTE: This is a CONTRACT file (planning phase). Implementation will be in:
 * frontend/lib/api/coaching.ts
 */

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
  APIError
} from './types';

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
  return apiFetch<StartSessionResponse>('/api/coaching/tutor-session', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

/**
 * POST /api/coaching/session/{session_id}/respond
 * Send a message to the coach
 */
async function sendMessage(
  sessionId: string,
  request: SendMessageRequest
): Promise<SendMessageResponse> {
  return apiFetch<SendMessageResponse>(`/api/coaching/session/${sessionId}/respond`, {
    method: 'POST',
    body: JSON.stringify(request)
  });
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
      // Add new session to cache
      queryClient.setQueryData(coachingKeys.session(data.session.id), data);

      // Invalidate sessions list
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
    mutationFn: (request: SendMessageRequest) => sendMessage(sessionId, request),

    // Optimistic update: show message immediately
    onMutate: async (request) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: coachingKeys.session(sessionId) });

      // Snapshot previous value
      const previousSession = queryClient.getQueryData<GetSessionResponse>(
        coachingKeys.session(sessionId)
      );

      // Optimistically add student message
      if (previousSession) {
        const pendingMessage: PendingMessage = {
          session_id: sessionId,
          role: 'student',
          content: request.content,
          type: 'answer',
          pending: true
        };

        queryClient.setQueryData<GetSessionResponse>(coachingKeys.session(sessionId), {
          session: {
            ...previousSession.session,
            messages: [
              ...previousSession.session.messages,
              pendingMessage as any // Cast needed for pending flag
            ]
          }
        });
      }

      // Return context for rollback
      return { previousSession };
    },

    // On error, rollback to previous state
    onError: (err, request, context) => {
      if (context?.previousSession) {
        queryClient.setQueryData(coachingKeys.session(sessionId), context.previousSession);
      }
    },

    // On success, refetch to get coach response
    onSuccess: (data) => {
      // Update session with real messages + coach response
      queryClient.setQueryData<GetSessionResponse>(coachingKeys.session(sessionId), {
        session: {
          ...data.session_status,
          outcome: data.outcome
        } as any // Simplified - full session will be fetched
      });

      // Refetch to get latest state
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
  return useQuery({
    queryKey: sessionId ? coachingKeys.session(sessionId) : ['coaching', 'null'],
    queryFn: async () => {
      if (!sessionId) throw new Error('Session ID required');

      // Try localStorage first for instant load
      const cached = localStorage.getItem(`coaching-session-${sessionId}`);
      if (cached) {
        const parsed = JSON.parse(cached);
        // If cache is fresh (<5 min), use it
        if (Date.now() - parsed.lastUpdated < 300000) {
          // Fetch from API in background to sync
          getSession(sessionId).then((apiData) => {
            queryClient.setQueryData(coachingKeys.session(sessionId), apiData);
          });
          return parsed as GetSessionResponse;
        }
      }

      // Cache miss or stale - fetch from API
      return getSession(sessionId);
    },
    enabled: !!sessionId,
    refetchInterval: (data) => {
      // Poll every 2 seconds if session is active
      return data?.session.status === 'active' ? 2000 : false;
    },
    // Persist to localStorage on success
    onSuccess: (data) => {
      if (sessionId && data) {
        localStorage.setItem(`coaching-session-${sessionId}`, JSON.stringify({
          ...data,
          lastUpdated: Date.now()
        }));
      }
    },
    retry: 2,
    staleTime: 5000 // Consider data stale after 5 seconds
  });
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
// Utility Hooks
// ============================================================================

/**
 * Hook: Detect online/offline status
 *
 * Usage:
 * ```tsx
 * const isOnline = useOnlineStatus();
 * ```
 */
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

/**
 * Hook: Validate session ownership (multi-tenant security)
 *
 * Usage:
 * ```tsx
 * const { isOwner, isLoading } = useSessionOwnership(sessionId);
 * ```
 *
 * Returns false if session belongs to different student (403 error).
 */
export function useSessionOwnership(sessionId: string) {
  const { data: session, error } = useSession(sessionId);

  // TODO: Get current user from auth context
  // const { user } = useAuth();

  return {
    isOwner: !error || !error.message.includes('permission'),
    isLoading: !session && !error,
    error
  };
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

// ============================================================================
// TypeScript Imports (for reference)
// ============================================================================

// NOTE: In actual implementation, add these imports:
// import { useState, useEffect } from 'react';
// import { useQuery, useMutation, useQueryClient, QueryClient } from '@tanstack/react-query';
