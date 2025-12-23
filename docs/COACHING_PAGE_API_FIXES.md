# Coaching Page API Compatibility Fixes

**Date**: 2025-12-21
**Issue**: Frontend/Backend API schema mismatch causing runtime errors

---

## 🐛 Issues Found

### 1. Student ID Not Found Error
**Error**: "Student 660e8400-e29b-41d4-a716-446655440001 not found"
**Cause**: Frontend using non-existent test UUID
**Fix**: 
- Created real test student via `/api/auth/register`
- Email: `test.coaching@example.com`
- Password: `TestPass123!`
- Student ID: `2fbda3c9-f6a3-4581-928a-077042239c38`
- Updated frontend to use this ID

### 2. CreateSessionRequest Schema Mismatch
**Error**: Backend expected `student_id`, `topic`, `struggle_description`
**Frontend sent**: Only `topic`
**Fix**: Updated `CreateSessionRequest` interface to include all required fields

### 3. SendMessageRequest Schema Mismatch
**Error**: Backend expected `student_response`, `request_hint`
**Frontend sent**: `content`
**Fix**: Updated `SendMessageRequest` interface

### 4. StartSessionResponse Schema Mismatch
**Error**: Frontend expected nested `{ session: {...}, initial_message: {...} }`
**Backend returned**: Flat `{ session_id, coach_message, internal_diagnosis, session_notes, outcome }`
**Fix**: Updated `StartSessionResponse` interface to match backend `SessionResponse`

### 5. GetSessionResponse Schema Mismatch
**Error**: "Cannot read properties of undefined (reading 'status')"
**Cause**: Frontend expected `{ session: { status, messages, ... } }`
**Backend returned**: Flat `{ session_id, transcript, outcome, ... }`
**Fix**: Updated `GetSessionResponse` to match backend `TranscriptResponse`

### 6. SendMessageResponse Schema Mismatch
**Error**: Frontend expected `{ student_message, coach_message, session_status, outcome }`
**Backend returned**: `{ session_id, coach_message, internal_diagnosis, session_notes, outcome }`
**Fix**: Updated `SendMessageResponse` interface

### 7. Message Type Too Strict
**Error**: Backend `SessionMessage` doesn't include `id`, `session_id`, `type`, `metadata`
**Fix**: Made these fields optional in frontend `Message` interface

### 8. Session Status vs Outcome
**Error**: Frontend used `session.status`, backend uses `outcome`
**Fix**: Updated ChatInterface to use `sessionData.outcome` instead

### 9. Message Length Validation
**Error**: Frontend validated max 2000 chars, backend accepts max 5000
**Fix**: Updated `VALIDATION_RULES.messageContent.maxLength` to 5000

---

## ✅ Files Updated

### Type Definitions (`frontend/types/coaching.ts`)
- `CreateSessionRequest`: Added `student_id`, `struggle_description`, `context`
- `SendMessageRequest`: Changed `content` → `student_response`, added `request_hint`
- `StartSessionResponse`: Updated to match backend `SessionResponse`
- `GetSessionResponse`: Updated to match backend `TranscriptResponse`
- `SendMessageResponse`: Updated to match backend `SessionResponse`
- `Message`: Made `id`, `session_id`, `type`, `metadata` optional
- `VALIDATION_RULES.messageContent.maxLength`: 2000 → 5000

### API Client (`frontend/lib/api/coaching.ts`)
- `startSession()`: Maps frontend request to backend schema, uses real student_id
- `useStartSession()`: Simplified onSuccess handler
- `useSendMessage()`: Updated optimistic update to use `transcript` instead of `messages`
- `useSendMessage()`: Updated to send `student_response` instead of `content`

### Components
- `SessionInitForm.tsx`:
  - Extracts topic from first 5 words of struggle description
  - Sends `student_id`, `topic`, `struggle_description` to backend
  - Uses `data.session_id` and `data.coach_message` from response
  - Improved error display (no more "[object Object]")

- `ChatInterface.tsx`:
  - Changed `sessionData.session.messages` → `sessionData.transcript`
  - Changed `sessionData.session.status` → `sessionData.outcome`
  - Changed `sessionData.session.topic` → `sessionData.topic`
  - Uses `isSessionActive` based on `outcome === 'in_progress'`
  - Sends `student_response` instead of `content`

---

## 🔄 Backend API Contract (Now Matched)

### POST /api/coaching/tutor-session
**Request**:
```json
{
  "student_id": "uuid",
  "topic": "string",
  "struggle_description": "string",
  "context": "string (optional)"
}
```

**Response** (`SessionResponse`):
```json
{
  "session_id": "uuid",
  "coach_message": "string",
  "internal_diagnosis": {...},
  "session_notes": {...},
  "outcome": "in_progress|resolved|needs_more_help|refer_to_teacher"
}
```

### POST /api/coaching/session/{session_id}/respond
**Request**:
```json
{
  "student_response": "string",
  "request_hint": boolean
}
```

**Response** (`SessionResponse`):
```json
{
  "session_id": "uuid",
  "coach_message": "string",
  "internal_diagnosis": {...},
  "session_notes": {...},
  "outcome": "string"
}
```

### GET /api/coaching/session/{session_id}
**Response** (`TranscriptResponse`):
```json
{
  "session_id": "uuid",
  "student_id": "uuid",
  "topic": "string",
  "struggle_description": "string",
  "transcript": [
    {
      "role": "coach|student",
      "content": "string",
      "timestamp": "ISO 8601"
    }
  ],
  "outcome": "string",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

---

## ✅ Test Student Credentials

For manual testing:
- **Email**: test.coaching@example.com
- **Password**: TestPass123!
- **Student ID**: 2fbda3c9-f6a3-4581-928a-077042239c38

---

## 🎯 Testing the Fix

1. Visit `http://localhost:3000/coaching`
2. Enter: "I don't understand price elasticity"
3. Click "Start Coaching Session"
4. **Expected**: Loading indicator → Coach's first question appears
5. Type response and send
6. **Expected**: Optimistic update → Coach responds

---

**Status**: ✅ All API compatibility issues resolved
**Last Updated**: 2025-12-21
