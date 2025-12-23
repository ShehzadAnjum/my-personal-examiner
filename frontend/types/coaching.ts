/**
 * TypeScript API Contracts for Coaching Page
 *
 * These types define the API request/response shapes for the coaching feature.
 * Based on data-model.md entities.
 *
 * API Endpoints:
 * - POST /api/coaching/tutor-session - Start new coaching session
 * - POST /api/coaching/session/{id}/respond - Send message to coach
 * - GET /api/coaching/session/{id} - Get session transcript
 * - GET /api/coaching/sessions - List user's coaching sessions (optional)
 */

// ============================================================================
// Core Entity Types (from data-model.md)
// ============================================================================

export interface CoachingSession {
  id: string;
  student_id: string;
  topic: string;
  status: 'active' | 'resolved' | 'needs_more_help' | 'refer_to_teacher' | 'abandoned';
  messages: Message[];
  outcome: SessionOutcome | null;
  created_at: string;
  updated_at: string;
  ended_at: string | null;
}

export interface Message {
  id?: string; // Optional: Backend SessionMessage doesn't have id
  session_id?: string; // Optional: Backend SessionMessage doesn't have session_id
  role: 'student' | 'coach';
  content: string;
  timestamp: string;
  type?: 'question' | 'answer' | 'explanation' | 'clarification' | 'outcome'; // Optional
  metadata?: {
    model?: string;
    confidence?: number;
    tokens_used?: number;
  };
  pending?: boolean; // Frontend-only
}

export interface SessionOutcome {
  id: string;
  session_id: string;
  status: 'resolved' | 'needs_more_help' | 'refer_to_teacher';
  summary: string;
  next_actions: NextAction[];
  created_at: string;
  confidence?: number;
}

export interface NextAction {
  type: 'practice' | 'review_topic' | 'teacher_help' | 'new_session';
  label: string;
  description: string;
  link?: string;
  priority: number;
}

// ============================================================================
// API Request Types
// ============================================================================

/**
 * POST /api/coaching/tutor-session
 * Request to start a new coaching session
 */
export interface CreateSessionRequest {
  /** UUID of student requesting coaching */
  student_id: string;
  /** Topic student is struggling with (concept name or syllabus point) */
  topic: string;
  /** Student's description of their confusion or struggle (min 10 chars, max 2000 chars) */
  struggle_description: string;
  /** Optional context about prior struggles or learning style */
  context?: string;
}

/**
 * POST /api/coaching/session/{session_id}/respond
 * Request to send a message to the coach
 */
export interface SendMessageRequest {
  /** Student's response to coach's question (min 1 char, max 5000 chars) */
  student_response: string;
  /** Whether student is requesting a hint */
  request_hint?: boolean;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * POST /api/coaching/tutor-session
 * Response when starting a new coaching session
 */
export interface StartSessionResponse {
  /** Session ID */
  session_id: string;
  /** Coach's first message */
  coach_message: string;
  /** Internal diagnosis (for tracking) */
  internal_diagnosis: {
    misconception_detected: string | null;
    knowledge_gaps: string[];
    current_understanding_level: string;
    recommended_next_step: string;
  };
  /** Session notes */
  session_notes: {
    progress_made: string;
    remaining_gaps: string[];
    outcome: string;
  };
  /** Current outcome */
  outcome: string;
}

/**
 * POST /api/coaching/session/{session_id}/respond
 * Response when sending a message to the coach
 */
export interface SendMessageResponse {
  /** Session ID */
  session_id: string;
  /** Coach's response message */
  coach_message: string;
  /** Internal diagnosis */
  internal_diagnosis: {
    misconception_detected: string | null;
    knowledge_gaps: string[];
    current_understanding_level: string;
    recommended_next_step: string;
  };
  /** Session notes */
  session_notes: {
    progress_made: string;
    remaining_gaps: string[];
    outcome: string;
  };
  /** Current outcome */
  outcome: string;
}

/**
 * GET /api/coaching/session/{session_id}
 * Response when fetching a complete session transcript
 */
export interface GetSessionResponse {
  /** Session ID */
  session_id: string;
  /** Student ID */
  student_id: string;
  /** Topic being coached */
  topic: string;
  /** Original struggle description */
  struggle_description: string | null;
  /** Full session transcript (all messages) */
  transcript: Message[];
  /** Current session outcome status */
  outcome: string;
  /** Session creation timestamp */
  created_at: string;
  /** Session last update timestamp */
  updated_at: string;
}

/**
 * GET /api/coaching/sessions
 * Response when listing all user's coaching sessions
 * (Optional endpoint - may not exist in backend yet)
 */
export interface ListSessionsResponse {
  /** Array of sessions */
  sessions: SessionListItem[];
  /** Total count (for pagination) */
  total: number;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Simplified session for list display
 * (Used in session history - P3 feature)
 */
export type SessionListItem = Pick<CoachingSession, 'id' | 'topic' | 'status' | 'created_at' | 'updated_at'> & {
  /** Number of messages in session */
  message_count: number;
};

/**
 * Message for optimistic UI update (no id/timestamp yet)
 */
export type PendingMessage = Omit<Message, 'id' | 'timestamp'> & {
  pending: true;
};

/**
 * API error response (standard FastAPI format)
 */
export interface APIError {
  detail: string;
  status_code: number;
}

// ============================================================================
// Frontend State Types (not from API)
// ============================================================================

/**
 * UI state for chat interface
 * (Client-side only, not persisted)
 */
export interface ChatUIState {
  activeSession: CoachingSession | null;
  isTyping: boolean;
  isWaitingForResponse: boolean;
  draftMessage: string;
  isAtBottom: boolean;
  isOnline: boolean;
  error: string | null;
}

/**
 * Message send operation state
 * (Client-side only, for retry logic)
 */
export interface MessageSendState {
  isSending: boolean;
  retryAttempt: number;
  error: string | null;
}

// ============================================================================
// Validation Constants
// ============================================================================

export const VALIDATION_RULES = {
  topic: {
    minLength: 10,
    maxLength: 500,
    pattern: /^[a-zA-Z0-9\s.,!?'-]+$/,
    errorMessage: 'Please describe your struggle in 10-500 characters'
  },
  messageContent: {
    minLength: 1,
    maxLength: 5000,
    errorMessage: 'Message must be between 1-5000 characters'
  },
  sessionId: {
    pattern: /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    errorMessage: 'Invalid session ID format'
  }
} as const;
