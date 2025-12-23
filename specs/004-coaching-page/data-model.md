# Data Model: Coaching Page

**Feature**: Coaching Page - Interactive AI Tutoring
**Date**: 2025-12-21
**Purpose**: Define TypeScript interfaces for coaching session entities

---

## Overview

The coaching page data model consists of four primary entities:
1. **CoachingSession** - The container for a tutoring conversation
2. **Message** - Individual chat messages (student and coach)
3. **SessionOutcome** - The conclusion status and recommendations
4. **SessionMetadata** - Tracking and analytics data

All entities follow these principles:
- Immutable after creation (messages, sessions)
- Student-scoped (multi-tenant isolation)
- Timestamped for audit and display

---

## Core Entities

### 1. CoachingSession

Represents a complete coaching session from initiation to conclusion.

```typescript
export interface CoachingSession {
  /** Unique session identifier (UUID) */
  id: string;

  /** Student who initiated the session (for multi-tenant isolation) */
  student_id: string;

  /** The initial struggle description provided by student */
  topic: string;

  /** Current status of the session */
  status: 'active' | 'resolved' | 'needs_more_help' | 'refer_to_teacher' | 'abandoned';

  /** Array of all messages in chronological order */
  messages: Message[];

  /** Session outcome (null if session still active) */
  outcome: SessionOutcome | null;

  /** When the session was initiated */
  created_at: string; // ISO 8601 timestamp

  /** Last message timestamp (for sorting sessions) */
  updated_at: string; // ISO 8601 timestamp

  /** When session ended (null if active) */
  ended_at: string | null; // ISO 8601 timestamp
}
```

**Relationships**:
- One-to-many: `Session → Messages`
- One-to-one: `Session → SessionOutcome` (nullable)

**Constraints**:
- `id` must be unique (UUID format)
- `student_id` must match JWT token student_id (enforced by backend)
- `status` transitions: `active` → one of `[resolved, needs_more_help, refer_to_teacher, abandoned]`
- `messages` array is append-only (no edits)
- `created_at` <= `updated_at` <= `ended_at`

---

### 2. Message

Represents a single message in the conversation (from student or coach).

```typescript
export interface Message {
  /** Unique message identifier (UUID) */
  id: string;

  /** Session this message belongs to */
  session_id: string;

  /** Role of message sender */
  role: 'student' | 'coach';

  /** Message content (plain text or markdown) */
  content: string;

  /** When message was created */
  timestamp: string; // ISO 8601 timestamp

  /** Message type (for rendering logic) */
  type: 'question' | 'answer' | 'explanation' | 'clarification' | 'outcome';

  /** Optional metadata (e.g., AI model used, confidence score) */
  metadata?: {
    model?: string; // e.g., "gpt-4", "claude-sonnet-4.5"
    confidence?: number; // 0-1
    tokens_used?: number;
  };

  /** Frontend-only: indicates message is being sent (optimistic update) */
  pending?: boolean;
}
```

**Relationships**:
- Many-to-one: `Message → Session`

**Constraints**:
- `id` must be unique (UUID format)
- `session_id` must reference valid session
- `role` is immutable after creation
- `content` minimum 1 character, maximum 2000 characters (frontend validates)
- `timestamp` is server-generated (backend sets)
- `pending` is client-side only (not persisted)

---

### 3. SessionOutcome

Represents the conclusion of a coaching session with recommendations.

```typescript
export interface SessionOutcome {
  /** Outcome identifier (matches session_id) */
  id: string;

  /** Session this outcome belongs to */
  session_id: string;

  /** Final outcome status */
  status: 'resolved' | 'needs_more_help' | 'refer_to_teacher';

  /** Summary of what was discussed and learned */
  summary: string;

  /** Recommended next actions for the student */
  next_actions: NextAction[];

  /** When the outcome was determined */
  created_at: string; // ISO 8601 timestamp

  /** Coach's confidence in resolution (0-1) */
  confidence?: number;
}

export interface NextAction {
  /** Action type */
  type: 'practice' | 'review_topic' | 'teacher_help' | 'new_session';

  /** Action label shown to user */
  label: string;

  /** Action description */
  description: string;

  /** Link (if applicable, e.g., to practice problems or topic page) */
  link?: string;

  /** Priority (1 = highest) */
  priority: number;
}
```

**Relationships**:
- One-to-one: `SessionOutcome → Session`

**Constraints**:
- `id` matches `session_id` (1-to-1 relationship)
- `status` must match parent session's status
- `next_actions` array must have at least 1 action, maximum 5
- `summary` minimum 50 characters (ensures meaningful summary)
- `confidence` is optional, 0-1 range

---

### 4. SessionMetadata

**Note**: This is a future enhancement (P3 - Analytics). Not required for P1-P2 implementation.

```typescript
export interface SessionMetadata {
  /** Session this metadata belongs to */
  session_id: string;

  /** Number of messages in session */
  message_count: number;

  /** Session duration in seconds */
  duration_seconds: number;

  /** Topics discussed (extracted from conversation) */
  topics: string[];

  /** Concepts clarified */
  concepts_clarified: string[];

  /** Student engagement score (0-1, based on message frequency/length) */
  engagement_score?: number;

  /** Misconceptions identified */
  misconceptions?: string[];
}
```

**Status**: Not implemented in P1-P2. Defined for future reference.

---

## Frontend-Only Types

These types are used for UI state management, not persisted.

### ChatUIState

```typescript
export interface ChatUIState {
  /** Current active session (null if no session) */
  activeSession: CoachingSession | null;

  /** Whether user is currently typing */
  isTyping: boolean;

  /** Whether waiting for coach response */
  isWaitingForResponse: boolean;

  /** Current message being composed */
  draftMessage: string;

  /** Whether chat is scrolled to bottom */
  isAtBottom: boolean;

  /** Network online status */
  isOnline: boolean;

  /** Error message (if any) */
  error: string | null;
}
```

### MessageSendState

```typescript
export interface MessageSendState {
  /** Whether message is being sent */
  isSending: boolean;

  /** Retry attempt count (0-3) */
  retryAttempt: number;

  /** Error message (if failed after 3 retries) */
  error: string | null;
}
```

---

## API Response Types

These types represent what the backend API returns.

### StartSessionResponse

```typescript
export interface StartSessionResponse {
  /** Newly created session */
  session: CoachingSession;

  /** First coach message (diagnostic question) */
  initial_message: Message;
}
```

**API Endpoint**: `POST /api/coaching/tutor-session`
**Request Body**: `{ topic: string }`

---

### SendMessageResponse

```typescript
export interface SendMessageResponse {
  /** The student's message (echo) */
  student_message: Message;

  /** The coach's response */
  coach_message: Message;

  /** Updated session status (in case session ended) */
  session_status: CoachingSession['status'];

  /** Session outcome (if session ended, otherwise null) */
  outcome: SessionOutcome | null;
}
```

**API Endpoint**: `POST /api/coaching/session/{session_id}/respond`
**Request Body**: `{ content: string }`

---

### GetSessionResponse

```typescript
export interface GetSessionResponse {
  /** Complete session with all messages */
  session: CoachingSession;
}
```

**API Endpoint**: `GET /api/coaching/session/{session_id}`

---

## Validation Rules

### Client-Side Validation (Before API Call)

```typescript
export const ValidationRules = {
  /** Topic/struggle description validation */
  topic: {
    minLength: 10,
    maxLength: 500,
    pattern: /^[a-zA-Z0-9\s.,!?'-]+$/, // Alphanumeric + punctuation
    errorMessage: 'Please describe your struggle in 10-500 characters'
  },

  /** Message content validation */
  messageContent: {
    minLength: 1,
    maxLength: 2000,
    errorMessage: 'Message must be between 1-2000 characters'
  },

  /** Session ID validation */
  sessionId: {
    pattern: /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i, // UUID v4
    errorMessage: 'Invalid session ID format'
  }
};
```

---

## Data Flow Diagram

```
┌──────────────┐
│   Student    │
└──────┬───────┘
       │ 1. Enters struggle
       ▼
┌──────────────────────────────────┐
│  POST /api/coaching/tutor-session│
│  Body: { topic: string }         │
└──────────┬───────────────────────┘
           │ Returns StartSessionResponse
           ▼
    ┌──────────────┐
    │CoachingSession│ ◄─── Creates
    └──────┬────────┘
           │ Contains
           ▼
      ┌─────────┐
      │ Message │ (coach's first question)
      └─────────┘

       │ 2. Student replies
       ▼
┌──────────────────────────────────────┐
│ POST /api/coaching/session/{id}/respond│
│ Body: { content: string }              │
└──────────┬─────────────────────────────┘
           │ Returns SendMessageResponse
           ▼
      ┌─────────┐
      │ Message │ (student message)
      └─────────┘
           +
      ┌─────────┐
      │ Message │ (coach response)
      └─────────┘

       │ N. Session ends
       ▼
  ┌────────────────┐
  │ SessionOutcome │
  └────────────────┘
```

---

## TypeScript Utility Types

```typescript
/** Extract just the fields needed for session list display */
export type SessionListItem = Pick<CoachingSession, 'id' | 'topic' | 'status' | 'created_at' | 'updated_at'>;

/** Create new session request */
export type CreateSessionRequest = {
  topic: string;
};

/** Send message request */
export type SendMessageRequest = {
  content: string;
};

/** Message for optimistic UI update (no id yet) */
export type PendingMessage = Omit<Message, 'id' | 'timestamp'> & {
  pending: true;
};
```

---

## Example Data

### Active Session Example

```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "student_id": "student-123",
  "topic": "I don't understand price elasticity",
  "status": "active",
  "messages": [
    {
      "id": "msg-001",
      "session_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "role": "coach",
      "content": "Let's explore price elasticity together. Can you tell me what happens when the price of a product increases?",
      "timestamp": "2025-12-21T10:00:00Z",
      "type": "question"
    },
    {
      "id": "msg-002",
      "session_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "role": "student",
      "content": "Demand goes down?",
      "timestamp": "2025-12-21T10:00:30Z",
      "type": "answer"
    },
    {
      "id": "msg-003",
      "session_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "role": "coach",
      "content": "Exactly! But *how much* does demand go down? That's what elasticity measures. If price increases by 10%, does demand decrease by 5%, 10%, or 20%? Let's think about a product you buy - what would you do if its price doubled?",
      "timestamp": "2025-12-21T10:01:00Z",
      "type": "explanation"
    }
  ],
  "outcome": null,
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:01:00Z",
  "ended_at": null
}
```

### Resolved Session Example

```json
{
  "id": "x9y8z7w6-v5u4-3t2s-1r0q-p9o8n7m6l5k4",
  "student_id": "student-456",
  "topic": "Confused about monopoly vs perfect competition",
  "status": "resolved",
  "messages": [
    // ... 8 messages omitted for brevity ...
  ],
  "outcome": {
    "id": "x9y8z7w6-v5u4-3t2s-1r0q-p9o8n7m6l5k4",
    "session_id": "x9y8z7w6-v5u4-3t2s-1r0q-p9o8n7m6l5k4",
    "status": "resolved",
    "summary": "We clarified the key differences between monopoly and perfect competition: number of firms, barriers to entry, price-setting power, and efficiency outcomes. You now understand that monopolies have price-setting power while perfectly competitive firms are price-takers.",
    "next_actions": [
      {
        "type": "practice",
        "label": "Practice Problems: Market Structures",
        "description": "Test your understanding with 10 questions on monopoly vs perfect competition",
        "link": "/practice/market-structures",
        "priority": 1
      },
      {
        "type": "review_topic",
        "label": "Review: Price Discrimination",
        "description": "Dive deeper into how monopolies can price discriminate",
        "link": "/topics/price-discrimination",
        "priority": 2
      }
    ],
    "created_at": "2025-12-21T11:15:00Z",
    "confidence": 0.95
  },
  "created_at": "2025-12-21T11:00:00Z",
  "updated_at": "2025-12-21T11:15:00Z",
  "ended_at": "2025-12-21T11:15:00Z"
}
```

---

**Status**: ✅ Data model complete. All entities defined with TypeScript interfaces, validation rules, and example data.
