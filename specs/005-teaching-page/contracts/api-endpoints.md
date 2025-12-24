# API Endpoint Contracts: Teaching Page

**Feature**: 005-teaching-page (PhD-Level Concept Explanations)
**Date**: 2025-12-23
**Phase**: 1 (Design & Contracts)
**Purpose**: Document backend API contracts for teaching page frontend integration

---

## Overview

The teaching page interacts with 5 backend API endpoints:

1. **GET /api/teaching/syllabus** - Fetch syllabus topics (with optional filters)
2. **POST /api/teaching/explain** - Generate AI explanation for a topic
3. **GET /api/teaching/explanations** - Fetch student's saved explanations
4. **POST /api/teaching/explanations** - Bookmark an explanation
5. **DELETE /api/teaching/explanations/:id** - Remove a bookmarked explanation

All endpoints require JWT authentication with `student_id` claim.

---

## Endpoint 1: GET /api/teaching/syllabus

**Purpose**: Retrieve Economics 9708 syllabus topics for browsing/searching

**Method**: `GET`

**Authentication**: Required (JWT with `student_id`)

**Query Parameters**:
- `search` (string, optional) - Keyword search across code, description, learning_outcomes
- `level` (enum, optional) - Filter by 'AS' or 'A2'
- `paper` (integer, optional) - Filter by paper number (1, 2, 3, or 4)

**Request Example**:
```http
GET /api/teaching/syllabus?search=elasticity&level=AS HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT_TOKEN>
```

**Response Success (200)**:
```json
{
  "topics": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "3.1.2",
      "description": "Price Elasticity of Demand (PED): Definition, calculation, determinants",
      "learning_outcomes": "Define PED\nCalculate PED using formula\nAnalyse determinants of PED",
      "subject_id": "subject-uuid",
      "level": "AS",
      "paper_number": 2,
      "section": "Microeconomics - Markets",
      "created_at": "2025-12-01T00:00:00Z",
      "updated_at": "2025-12-01T00:00:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "code": "3.1.3",
      "description": "Income Elasticity of Demand (YED): Definition and applications",
      "learning_outcomes": "Define YED\nCalculate YED\nDistinguish normal vs inferior goods",
      "subject_id": "subject-uuid",
      "level": "AS",
      "paper_number": 2,
      "section": "Microeconomics - Markets",
      "created_at": "2025-12-01T00:00:00Z",
      "updated_at": "2025-12-01T00:00:00Z"
    }
  ]
}
```

**Response Error (401)**:
```json
{
  "detail": "Not authenticated"
}
```

**Response Error (400)**:
```json
{
  "detail": "Invalid query parameters: level must be 'AS' or 'A2'"
}
```

**Frontend Usage**:
```typescript
// frontend/lib/api/teaching.ts
export const getTopics = async (filters?: {
  search?: string;
  level?: 'AS' | 'A2';
  paper?: number;
}) => {
  const params = new URLSearchParams();
  if (filters?.search) params.append('search', filters.search);
  if (filters?.level) params.append('level', filters.level);
  if (filters?.paper) params.append('paper', String(filters.paper));

  const response = await fetch(`/api/teaching/syllabus?${params}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });

  if (!response.ok) throw new Error('Failed to fetch topics');
  return response.json();
};
```

**Caching Strategy**:
- **Frontend (TanStack Query)**: `staleTime: 1 hour, cacheTime: 2 hours`
- **Rationale**: Topics change only with syllabus updates (monthly)
- **Cache Key**: `['topics', filters]` (separate cache per filter combination)

---

## Endpoint 2: POST /api/teaching/explain

**Purpose**: Generate PhD-level AI explanation for a selected topic

**Method**: `POST`

**Authentication**: Required (JWT with `student_id`)

**Request Body**:
```json
{
  "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": "student-uuid",  // Extracted from JWT (not user-provided)
  "context": "I'm struggling with understanding the relationship between PED and total revenue"  // Optional
}
```

**Request Example**:
```http
POST /api/teaching/explain HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
  "context": "Help me understand PED and total revenue"
}
```

**Response Success (200)** (5-10 seconds latency):
```json
{
  "explanation": {
    "syllabus_code": "3.1.2",
    "concept_name": "Price Elasticity of Demand",
    "definition": "PED measures the responsiveness of quantity demanded to a change in price...",
    "key_terms": [
      {
        "term": "Elastic demand",
        "definition": "PED > 1, quantity demanded changes proportionally more than price"
      }
    ],
    "explanation": "Price elasticity of demand measures how sensitive consumers are to price changes...",
    "examples": [
      {
        "title": "Elastic Demand: Luxury Cars",
        "scenario": "A 10% price increase leads to 20% drop in sales",
        "analysis": "Consumers have many substitutes, making demand elastic"
      }
    ],
    "visual_aids": [
      {
        "type": "diagram",
        "title": "Elastic vs Inelastic Demand Curves",
        "description": "Elastic: flatter slope. Inelastic: steeper slope."
      }
    ],
    "worked_examples": [...],
    "common_misconceptions": [...],
    "practice_problems": [...],
    "related_concepts": ["3.1.3 Income Elasticity", "3.2.1 Consumer Surplus"],
    "generated_by": "anthropic"
  }
}
```

**Response Error (404)**:
```json
{
  "detail": "Syllabus point not found"
}
```

**Response Error (500)**:
```json
{
  "detail": "Failed to generate explanation: AI service timeout"
}
```

**Frontend Usage**:
```typescript
// frontend/lib/api/teaching.ts
export const explainConcept = async (
  syllabusPointId: string,
  context?: string
) => {
  const response = await fetch('/api/teaching/explain', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ syllabus_point_id: syllabusPointId, context }),
  });

  if (!response.ok) throw new Error('Failed to generate explanation');
  const data = await response.json();
  return data.explanation;
};
```

**Caching Strategy**:
- **Frontend (TanStack Query)**: `staleTime: 5 minutes, cacheTime: 10 minutes`
- **Rationale**: AI-generated content is expensive but deterministic (same topic → same explanation)
- **Cache Key**: `['explanation', syllabusPointId]`

**Performance**:
- **Expected Latency**: 5-10 seconds (AI generation time)
- **Timeout**: 30 seconds (return error if AI takes longer)
- **Loading State**: ExplanationSkeleton shown during wait

---

## Endpoint 3: GET /api/teaching/explanations

**Purpose**: Fetch all saved explanations for the authenticated student

**Method**: `GET`

**Authentication**: Required (JWT with `student_id`)

**Query Parameters**: None (student_id extracted from JWT)

**Request Example**:
```http
GET /api/teaching/explanations HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT_TOKEN>
```

**Response Success (200)**:
```json
{
  "saved_explanations": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "student_id": "student-uuid",
      "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
      "explanation_content": {
        "syllabus_code": "3.1.2",
        "concept_name": "Price Elasticity of Demand",
        "definition": "...",
        "key_terms": [...],
        "examples": [...],
        "visual_aids": [...],
        "worked_examples": [...],
        "common_misconceptions": [...],
        "practice_problems": [...],
        "related_concepts": [...],
        "generated_by": "anthropic"
      },
      "date_saved": "2025-12-23T10:30:00Z",
      "date_last_viewed": "2025-12-23T14:45:00Z"
    }
  ]
}
```

**Response Error (401)**:
```json
{
  "detail": "Not authenticated"
}
```

**Frontend Usage**:
```typescript
// frontend/lib/api/teaching.ts
export const getSavedExplanations = async () => {
  const response = await fetch('/api/teaching/explanations', {
    headers: { Authorization: `Bearer ${getToken()}` },
  });

  if (!response.ok) throw new Error('Failed to fetch saved explanations');
  const data = await response.json();
  return data.saved_explanations;
};
```

**Caching Strategy**:
- **Frontend (TanStack Query)**: `staleTime: 1 minute, cacheTime: 5 minutes`
- **Rationale**: User-specific data that changes frequently (bookmarking), but 1-minute cache reduces API calls
- **Cache Key**: `['savedExplanations']`
- **Invalidation**: Invalidated when bookmark added/removed

---

## Endpoint 4: POST /api/teaching/explanations

**Purpose**: Bookmark an explanation for future review

**Method**: `POST`

**Authentication**: Required (JWT with `student_id`)

**Request Body**:
```json
{
  "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
  "explanation_content": {
    "syllabus_code": "3.1.2",
    "concept_name": "Price Elasticity of Demand",
    "definition": "...",
    "key_terms": [...],
    "examples": [...],
    "visual_aids": [...],
    "worked_examples": [...],
    "common_misconceptions": [...],
    "practice_problems": [...],
    "related_concepts": [...],
    "generated_by": "anthropic"
  }
}
```

**Request Example**:
```http
POST /api/teaching/explanations HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
  "explanation_content": { ... }
}
```

**Response Success (201)**:
```json
{
  "saved_explanation": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "student_id": "student-uuid",
    "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
    "explanation_content": { ... },
    "date_saved": "2025-12-23T10:30:00Z",
    "date_last_viewed": null
  }
}
```

**Response Error (409)**:
```json
{
  "detail": "Explanation already bookmarked for this topic"
}
```

**Response Error (404)**:
```json
{
  "detail": "Syllabus point not found"
}
```

**Frontend Usage**:
```typescript
// frontend/lib/api/teaching.ts
export const saveExplanation = async (
  syllabusPointId: string,
  explanationContent: TopicExplanation
) => {
  const response = await fetch('/api/teaching/explanations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({
      syllabus_point_id: syllabusPointId,
      explanation_content: explanationContent,
    }),
  });

  if (!response.ok) {
    if (response.status === 409) throw new Error('Already bookmarked');
    throw new Error('Failed to save explanation');
  }

  const data = await response.json();
  return data.saved_explanation;
};
```

**Cache Invalidation**:
- **After Success**: Invalidate `['savedExplanations']` query to refetch updated list
- **Toast Notification**: "Explanation saved for later review"

---

## Endpoint 5: DELETE /api/teaching/explanations/:id

**Purpose**: Remove a bookmarked explanation

**Method**: `DELETE`

**Authentication**: Required (JWT with `student_id`)

**Path Parameters**:
- `id` (UUID) - SavedExplanation ID to delete

**Request Example**:
```http
DELETE /api/teaching/explanations/770e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT_TOKEN>
```

**Response Success (200)**:
```json
{
  "success": true
}
```

**Response Error (404)**:
```json
{
  "detail": "Saved explanation not found or does not belong to you"
}
```

**Response Error (401)**:
```json
{
  "detail": "Not authenticated"
}
```

**Frontend Usage**:
```typescript
// frontend/lib/api/teaching.ts
export const removeSavedExplanation = async (id: string) => {
  const response = await fetch(`/api/teaching/explanations/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${getToken()}` },
  });

  if (!response.ok) {
    if (response.status === 404) throw new Error('Bookmark not found');
    throw new Error('Failed to remove bookmark');
  }

  return response.json();
};
```

**Cache Invalidation**:
- **After Success**: Invalidate `['savedExplanations']` query to refetch updated list
- **Toast Notification**: "Bookmark removed"

---

## Frontend API Client Module

**File**: `frontend/lib/api/teaching.ts`

**Purpose**: Centralized API client for all teaching endpoints

**Implementation**:
```typescript
// frontend/lib/api/teaching.ts
import { TopicExplanation, SyllabusTopic, SavedExplanation } from '@/lib/types/teaching';

const API_BASE = '/api/teaching';

const getToken = () => {
  // Get JWT from localStorage or auth provider
  return localStorage.getItem('token');
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'API request failed');
  }
  return response.json();
};

export const teachingApi = {
  // GET /api/teaching/syllabus
  getTopics: async (filters?: {
    search?: string;
    level?: 'AS' | 'A2';
    paper?: number;
  }): Promise<{ topics: SyllabusTopic[] }> => {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.level) params.append('level', filters.level);
    if (filters?.paper) params.append('paper', String(filters.paper));

    const response = await fetch(`${API_BASE}/syllabus?${params}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse(response);
  },

  // POST /api/teaching/explain
  explainConcept: async (
    syllabusPointId: string,
    context?: string
  ): Promise<{ explanation: TopicExplanation }> => {
    const response = await fetch(`${API_BASE}/explain`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ syllabus_point_id: syllabusPointId, context }),
    });

    return handleResponse(response);
  },

  // GET /api/teaching/explanations
  getSavedExplanations: async (): Promise<{ saved_explanations: SavedExplanation[] }> => {
    const response = await fetch(`${API_BASE}/explanations`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse(response);
  },

  // POST /api/teaching/explanations
  saveExplanation: async (
    syllabusPointId: string,
    explanationContent: TopicExplanation
  ): Promise<{ saved_explanation: SavedExplanation }> => {
    const response = await fetch(`${API_BASE}/explanations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({
        syllabus_point_id: syllabusPointId,
        explanation_content: explanationContent,
      }),
    });

    return handleResponse(response);
  },

  // DELETE /api/teaching/explanations/:id
  removeSavedExplanation: async (id: string): Promise<{ success: boolean }> => {
    const response = await fetch(`${API_BASE}/explanations/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse(response);
  },
};
```

---

## Error Handling Strategy

### HTTP Status Codes
- **200 OK**: Successful GET/DELETE
- **201 Created**: Successful POST (bookmark created)
- **400 Bad Request**: Invalid query parameters or request body
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Syllabus point or saved explanation not found
- **409 Conflict**: Duplicate bookmark attempt
- **500 Internal Server Error**: Backend failure (AI timeout, database error)

### Frontend Error Handling
```typescript
// frontend/lib/hooks/useExplanation.tsx
export const useExplanation = (topicId: string) => {
  return useQuery({
    queryKey: ['explanation', topicId],
    queryFn: () => teachingApi.explainConcept(topicId).then(data => data.explanation),
    retry: 2,  // Retry twice on failure
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),  // Exponential backoff
    onError: (error) => {
      toast({
        title: 'Failed to load explanation',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
};
```

---

## Testing Checklist

**Before Frontend Implementation**:
- [ ] Verify GET /api/teaching/syllabus returns 200 with valid topics
- [ ] Verify POST /api/teaching/explain generates explanation (test with real topic ID)
- [ ] Verify GET /api/teaching/explanations returns empty array for new student
- [ ] Verify POST /api/teaching/explanations creates bookmark (check database)
- [ ] Verify DELETE /api/teaching/explanations removes bookmark (check database)
- [ ] Verify 401 error when JWT token missing
- [ ] Verify 404 error when invalid topic ID provided
- [ ] Verify 409 error when bookmarking same topic twice

**Frontend Integration Tests**:
- [ ] Test TanStack Query hooks with real API endpoints
- [ ] Test cache invalidation after bookmark add/remove
- [ ] Test error toast notifications on API failures
- [ ] Test loading states (ExplanationSkeleton during 5-10 second AI generation)

---

**API Contracts Complete**: All endpoint specifications documented with request/response examples.

**Next**: Create UI component contracts (ui-components.md)
