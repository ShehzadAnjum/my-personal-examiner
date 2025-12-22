# Research: Coaching Page Technical Decisions

**Feature**: Coaching Page - Interactive AI Tutoring
**Date**: 2025-12-21
**Purpose**: Resolve "NEEDS CLARIFICATION" items from Technical Context and document best practices

---

## Research Questions

### Q1: How to implement real-time chat with REST API (no WebSocket)?

**Context**: Backend provides REST endpoints (POST /api/coaching/session/{id}/respond), not WebSocket. Need to deliver "real-time" feel.

**Research Findings**:

**Decision**: Use polling + optimistic updates
- **Rationale**:
  - REST-only backend (no WebSocket infrastructure)
  - TanStack Query supports polling with `refetchInterval`
  - Optimistic updates make UI feel instant
  - No need for WebSocket overhead for tutoring use case (not live chat)

**Implementation Pattern**:
```typescript
// TanStack Query with polling
const { data: messages } = useQuery({
  queryKey: ['session', sessionId, 'messages'],
  queryFn: () => fetchMessages(sessionId),
  refetchInterval: 2000, // Poll every 2 seconds
  enabled: !!sessionId && !isSessionEnded
});

// Optimistic update on send
const sendMutation = useMutation({
  mutationFn: (message) => sendMessage(sessionId, message),
  onMutate: async (newMessage) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['session', sessionId, 'messages']);
    // Optimistically add message to UI
    queryClient.setQueryData(['session', sessionId, 'messages'], (old) => [
      ...old,
      { ...newMessage, role: 'student', pending: true }
    ]);
  },
  onSuccess: () => {
    // Refetch to get coach response
    queryClient.invalidateQueries(['session', sessionId, 'messages']);
  }
});
```

**Alternatives Considered**:
- **WebSocket**: Rejected - requires backend changes (out of scope for frontend feature)
- **Server-Sent Events (SSE)**: Rejected - backend doesn't support SSE
- **Long polling**: Rejected - standard polling simpler, adequate for use case

**Performance Impact**: 2-second polling = 30 requests/minute (acceptable for tutoring session)

---

### Q2: How to persist session state across page refreshes?

**Context**: FR-013 requires "preserve conversation history across page refreshes"

**Research Findings**:

**Decision**: Dual persistence (localStorage + API fetch)
- **Rationale**:
  - API is source of truth (multi-device access)
  - localStorage provides instant load on refresh
  - Prevents data loss if API fails

**Implementation Pattern**:
```typescript
// Save to localStorage on every message
useEffect(() => {
  if (sessionId && messages) {
    localStorage.setItem(`coaching-session-${sessionId}`, JSON.stringify({
      sessionId,
      messages,
      lastUpdated: Date.now()
    }));
  }
}, [sessionId, messages]);

// Load from localStorage immediately, then hydrate from API
const { data: session, isLoading } = useQuery({
  queryKey: ['session', sessionId],
  queryFn: async () => {
    // Try localStorage first for instant load
    const cached = localStorage.getItem(`coaching-session-${sessionId}`);
    if (cached) {
      const parsed = JSON.parse(cached);
      // If cache is fresh (<5 min), use it
      if (Date.now() - parsed.lastUpdated < 300000) {
        // Still fetch from API in background to sync
        fetchSessionFromAPI(sessionId).then((apiData) => {
          queryClient.setQueryData(['session', sessionId], apiData);
        });
        return parsed;
      }
    }
    // Cache miss or stale - fetch from API
    return fetchSessionFromAPI(sessionId);
  }
});
```

**Alternatives Considered**:
- **API only**: Rejected - slow on refresh, no offline fallback
- **localStorage only**: Rejected - no multi-device sync, violates multi-tenant security
- **IndexedDB**: Rejected - overkill for simple session data

**Security Note**: localStorage is per-domain, student_id validation still happens on API fetch

---

### Q3: How to implement auto-retry for failed message sends?

**Context**: FR-019 requires "automatically retry failed message sends (up to 3 attempts)"

**Research Findings**:

**Decision**: TanStack Query's built-in retry + exponential backoff
- **Rationale**:
  - TanStack Query supports `retry` and `retryDelay` out of box
  - Exponential backoff prevents server overload
  - User sees retry status in UI

**Implementation Pattern**:
```typescript
const sendMutation = useMutation({
  mutationFn: (message) => sendMessage(sessionId, message),
  retry: 3, // Retry up to 3 times
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff: 1s, 2s, 4s
  onError: (error, variables, context) => {
    // After 3 retries failed, show error to user
    toast.error('Message failed to send. Please try again.');
  }
});

// UI shows retry state
{sendMutation.isLoading && <TypingIndicator text="Sending message..." />}
{sendMutation.isError && sendMutation.failureCount < 3 && (
  <RetryIndicator attempt={sendMutation.failureCount} />
)}
```

**Alternatives Considered**:
- **Custom retry logic**: Rejected - reinvents TanStack Query's wheel
- **Infinite retries**: Rejected - violates FR-019 (max 3 attempts)
- **No retry**: Rejected - violates FR-019

**User Experience**: Retry is transparent, user sees "Sending..." indicator

---

### Q4: How to detect and handle network disconnection?

**Context**: FR-020 requires "show connection status when network disconnection is detected"

**Research Findings**:

**Decision**: Browser's `navigator.onLine` + API request failures
- **Rationale**:
  - `navigator.onLine` detects offline state immediately
  - API failures (timeout, network error) supplement detection
  - React hook wraps detection logic

**Implementation Pattern**:
```typescript
// Custom hook for online detection
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

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

// UI component
function CoachingPage() {
  const isOnline = useOnlineStatus();

  return (
    <>
      {!isOnline && (
        <Banner variant="warning">
          You are offline. Messages will be sent when connection is restored.
        </Banner>
      )}
      <ChatInterface />
    </>
  );
}

// TanStack Query network mode
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst', // Use cache when offline
    },
    mutations: {
      networkMode: 'always', // Retry mutations when back online
    },
  },
});
```

**Alternatives Considered**:
- **Ping API for detection**: Rejected - wasteful, `navigator.onLine` is sufficient
- **Service Worker**: Rejected - overkill for simple offline detection
- **No detection**: Rejected - violates FR-020

**User Experience**: Banner appears at top when offline, disappears when reconnected

---

### Q5: How to implement session ownership verification (multi-tenant)?

**Context**: FR-022 to FR-024 require multi-tenant isolation (students can only access their own sessions)

**Research Findings**:

**Decision**: JWT extraction + session ownership check on every API call
- **Rationale**:
  - Backend already uses JWT for auth (Phase I)
  - Frontend extracts student_id from JWT
  - API validates session.student_id === JWT.student_id
  - Frontend pre-validates before rendering (defense in depth)

**Implementation Pattern**:
```typescript
// API client with JWT
async function fetchSession(sessionId: string) {
  const token = getAuthToken(); // From cookie or localStorage
  const response = await fetch(`/api/coaching/session/${sessionId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.status === 403) {
    throw new Error('You do not have permission to access this session');
  }

  return response.json();
}

// Frontend validation (optional, backend is source of truth)
function CoachingSessionPage({ params }: { params: { sessionId: string } }) {
  const { user } = useAuth(); // Current logged-in student
  const { data: session, error } = useQuery({
    queryKey: ['session', params.sessionId],
    queryFn: () => fetchSession(params.sessionId)
  });

  if (error?.message.includes('permission')) {
    return <ErrorPage code={403} message="Session not found or access denied" />;
  }

  // Additional check (defense in depth)
  if (session && session.student_id !== user.id) {
    return <ErrorPage code={403} message="Unauthorized access" />;
  }

  return <ChatInterface session={session} />;
}
```

**Backend Contract** (assumed from Phase I):
```typescript
// Backend validates ownership
@router.get("/api/coaching/session/{session_id}")
async def get_session(
    session_id: str,
    current_student: Student = Depends(get_current_student) // Extracted from JWT
):
    session = await db.get(CoachingSession, session_id)
    if session.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session
```

**Alternatives Considered**:
- **Frontend-only check**: Rejected - not secure, backend must enforce
- **No check**: Rejected - violates Principle V (Multi-Tenant Isolation is Sacred)
- **URL obfuscation**: Rejected - security through obscurity is not security

**Testing Required**: Integration test verifying Student A cannot access Student B's session (E2E with Playwright)

---

### Q6: Best practices for shadcn/ui + Tailwind CSS 4?

**Context**: Project uses shadcn/ui (component library) + Tailwind CSS 4

**Research Findings**:

**Decision**: Use shadcn/ui primitives, customize with Tailwind
- **Rationale**:
  - shadcn/ui provides accessible, unstyled components
  - Tailwind handles all styling
  - Components are copied to codebase (not npm package) - full control

**Components Needed**:
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add card
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add alert
```

**Pattern**:
```tsx
// MessageBubble.tsx - uses shadcn primitives + Tailwind
import { Avatar } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";

export function MessageBubble({ message, isStudent }: MessageBubbleProps) {
  return (
    <div className={cn(
      "flex gap-3 mb-4",
      isStudent ? "flex-row-reverse" : "flex-row"
    )}>
      <Avatar>
        {isStudent ? <StudentIcon /> : <CoachIcon />}
      </Avatar>
      <Card className={cn(
        "p-4 max-w-[70%]",
        isStudent ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"
      )}>
        <p className="text-sm">{message.content}</p>
        <span className="text-xs opacity-70 mt-2 block">
          {formatTimestamp(message.timestamp)}
        </span>
      </Card>
    </div>
  );
}
```

**Documentation**: https://ui.shadcn.com/docs

---

### Q7: How to handle coach response streaming (if supported)?

**Context**: Backend may support streaming responses (common in AI applications)

**Research Findings**:

**Decision**: Detect streaming support, gracefully degrade to polling
- **Rationale**:
  - Streaming improves UX (words appear as generated)
  - If backend adds streaming later, frontend is ready
  - Falls back to polling if streaming not available

**Implementation Pattern**:
```typescript
// Check if response is streaming
async function sendMessage(sessionId: string, content: string) {
  const response = await fetch(`/api/coaching/session/${sessionId}/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });

  // Check if response is SSE stream
  if (response.headers.get('content-type')?.includes('text/event-stream')) {
    // Handle streaming
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      // Update UI with partial response
      onStreamChunk(chunk);
    }
  } else {
    // Handle regular JSON response
    return response.json();
  }
}
```

**Alternatives Considered**:
- **Assume streaming always**: Rejected - backend may not support it yet
- **No streaming support**: Accepted as fallback - polling works

**Current Status**: Assume no streaming (use polling), add streaming later if backend supports

---

## Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Real-time updates | Polling (2s interval) + optimistic updates | REST API only, no WebSocket |
| Session persistence | localStorage + API (dual) | Instant load + multi-device sync |
| Message retry | TanStack Query retry (3 attempts, exponential backoff) | Built-in, tested, reliable |
| Offline detection | `navigator.onLine` + API failures | Browser native, no extra requests |
| Multi-tenant security | JWT + session ownership check | Backend enforces, frontend validates |
| UI components | shadcn/ui + Tailwind CSS 4 | Project standard, accessible |
| Streaming | Detect and support, gracefully degrade | Future-proof, works without streaming |

---

**Status**: ✅ All research complete. All NEEDS CLARIFICATION items resolved. Proceeding to Phase 1 (Design).
