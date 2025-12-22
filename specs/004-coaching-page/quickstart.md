# Quickstart: Coaching Page Development & Testing

**Feature**: Coaching Page - Interactive AI Tutoring
**Branch**: `004-coaching-page`
**Prerequisites**: Phase I (auth) complete, Phase III (coaching APIs) functional

---

## Table of Contents

1. [Setup](#setup)
2. [Running Locally](#running-locally)
3. [Testing](#testing)
4. [Security Checklist](#security-checklist)
5. [Common Issues](#common-issues)

---

## Setup

### Prerequisites

Ensure these are installed and functional:

```bash
# Node.js 18+ (for Next.js 16)
node --version  # Should be v18.x or higher

# pnpm (preferred) or npm
pnpm --version

# Backend running (from Phase III)
curl http://localhost:8000/api/health  # Should return 200 OK
```

### Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
pnpm install

# Install shadcn/ui components needed for coaching page
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add card
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add alert
```

### Environment Variables

Create/update `frontend/.env.local`:

```env
# API Base URL (backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Enable React Query Devtools (development only)
NEXT_PUBLIC_ENABLE_DEVTOOLS=true
```

---

## Running Locally

### Start Backend (Phase III APIs)

```bash
# In project root
cd backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Run FastAPI server
uvicorn src.main:app --reload --port 8000

# Verify coaching APIs are functional
curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"topic": "I dont understand price elasticity"}'

# Expected: 200 OK with session + initial_message
```

### Start Frontend (Next.js)

```bash
# In frontend directory
cd frontend

# Run Next.js dev server
pnpm dev

# Server starts at http://localhost:3000
```

### Access Coaching Page

1. Navigate to: `http://localhost:3000/coaching`
2. Login (if not already authenticated)
3. Enter struggle description: "I don't understand price elasticity"
4. Click "Start Session"
5. Verify coach's first question appears
6. Reply to coach, verify response

---

## Testing

### Unit Tests (Jest)

```bash
# In frontend directory
cd frontend

# Run all tests
pnpm test

# Run coaching-specific tests
pnpm test -- coaching

# Run with coverage
pnpm test:coverage

# Watch mode (for development)
pnpm test:watch
```

**Test Files**:
- `components/coaching/__tests__/SessionInitForm.test.tsx`
- `components/coaching/__tests__/ChatInterface.test.tsx`
- `components/coaching/__tests__/MessageBubble.test.tsx`
- `lib/api/__tests__/coaching.test.ts`
- `hooks/__tests__/useSession.test.ts`

**Coverage Target**: >80% (enforced by jest.config.js)

### E2E Tests (Playwright)

```bash
# In frontend directory
cd frontend

# Install Playwright (first time only)
npx playwright install

# Run E2E tests (headless)
pnpm test:e2e

# Run with UI (see browser)
pnpm test:e2e:ui

# Run specific test file
npx playwright test tests/e2e/coaching/start-session.spec.ts

# Debug mode
npx playwright test --debug
```

**Test Files**:
- `tests/e2e/coaching/start-session.spec.ts` (P1)
- `tests/e2e/coaching/chat-conversation.spec.ts` (P1)
- `tests/e2e/coaching/session-outcome.spec.ts` (P2)
- `tests/e2e/coaching/session-history.spec.ts` (P3)

**E2E Test Example**:

```typescript
// tests/e2e/coaching/start-session.spec.ts
import { test, expect } from '@playwright/test';

test('student can start coaching session and receive initial question', async ({ page }) => {
  // 1. Login
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="email"]', 'student@test.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 2. Navigate to coaching page
  await page.goto('http://localhost:3000/coaching');
  await expect(page.locator('h1')).toContainText('Coaching');

  // 3. Start session
  await page.fill('textarea[name="topic"]', "I don't understand price elasticity");
  await page.click('button:has-text("Start Session")');

  // 4. Verify loading state
  await expect(page.locator('text=Coach is preparing')).toBeVisible();

  // 5. Verify coach's first message appears
  await expect(page.locator('[data-role="coach"] >> text=price')).toBeVisible({ timeout: 5000 });

  // 6. Verify session is active
  await expect(page.locator('[data-status="active"]')).toBeVisible();
});
```

### Manual Testing Checklist

**P1 - Start Coaching Session**:
- [ ] Enter struggle description (min 10 chars)
- [ ] Empty description shows error
- [ ] Loading indicator appears
- [ ] Coach's first question appears within 5 seconds
- [ ] Session ID is generated (check URL or localStorage)

**P1 - Chat Conversation**:
- [ ] Send message "Demand goes down?"
- [ ] Message appears immediately (optimistic update)
- [ ] Coach response appears within 10 seconds
- [ ] Typing indicator shows "Coach is thinking..."
- [ ] Messages have timestamps (human-readable)
- [ ] Student messages align right, coach messages align left
- [ ] Long messages (500+ chars) display correctly
- [ ] Very long conversation (20+ messages) scrolls smoothly

**P2 - Session Outcome**:
- [ ] Continue conversation until coach concludes
- [ ] Outcome displays (resolved/needs_more_help/refer_to_teacher)
- [ ] Summary shows what was learned
- [ ] Next actions (1-5) are displayed with links
- [ ] Input is disabled after session ends
- [ ] Message "Session ended. Start new session to continue" appears

**P3 - Session History** (future):
- [ ] Navigate to /coaching/history
- [ ] Past sessions listed with topic, date, outcome
- [ ] Click session to view full transcript
- [ ] Transcript is read-only (no input allowed)

---

## Security Checklist

**Critical**: Multi-tenant isolation must be verified before deployment.

### JWT Verification

```bash
# Test session ownership
# 1. Login as Student A, get JWT token
TOKEN_A="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Create session as Student A
SESSION_ID=$(curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"topic": "test"}' | jq -r '.session.id')

# 3. Login as Student B, get JWT token
TOKEN_B="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 4. Try to access Student A's session with Student B's token
curl -X GET http://localhost:8000/api/coaching/session/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN_B"

# Expected: 403 Forbidden
# Actual: ??? (MUST VERIFY)
```

### Security Tests (Playwright)

```typescript
// tests/e2e/security/multi-tenant-isolation.spec.ts
test('Student B cannot access Student A session', async ({ browser }) => {
  // Create two contexts (two students)
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();

  const pageA = await contextA.newPage();
  const pageB = await contextB.newPage();

  // Student A: Login + create session
  await pageA.goto('http://localhost:3000/login');
  await pageA.fill('input[name="email"]', 'studentA@test.com');
  await pageA.fill('input[name="password"]', 'password123');
  await pageA.click('button[type="submit"]');

  await pageA.goto('http://localhost:3000/coaching');
  await pageA.fill('textarea[name="topic"]', 'Test session');
  await pageA.click('button:has-text("Start Session")');

  // Get session ID from URL
  await pageA.waitForURL(/\/coaching\/[a-f0-9-]+/);
  const sessionId = pageA.url().split('/').pop();

  // Student B: Login
  await pageB.goto('http://localhost:3000/login');
  await pageB.fill('input[name="email"]', 'studentB@test.com');
  await pageB.fill('input[name="password"]', 'password123');
  await pageB.click('button[type="submit"]');

  // Student B: Try to access Student A's session
  await pageB.goto(`http://localhost:3000/coaching/${sessionId}`);

  // Verify 403 error page
  await expect(pageB.locator('text=access denied')).toBeVisible();
  await expect(pageB.locator('text=403')).toBeVisible();
});
```

**Required Before Deployment**:
- [ ] JWT extraction works correctly
- [ ] Backend validates session ownership (student_id === JWT.student_id)
- [ ] Frontend shows 403 error when accessing unauthorized session
- [ ] URL manipulation doesn't bypass security
- [ ] localStorage data is student-scoped (different students can't see each other's cache)

---

## Common Issues

### Issue: "Cannot connect to backend"

**Symptom**: `fetch failed` or `ECONNREFUSED`

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check NEXT_PUBLIC_API_URL in .env.local
cat frontend/.env.local

# Ensure no CORS issues (backend should allow http://localhost:3000)
```

### Issue: "Polling not working, coach response doesn't appear"

**Symptom**: Student message sends, but coach response never appears

**Solution**:
```typescript
// Check refetchInterval in useSession hook
// Verify session status is 'active' (polling only works for active sessions)

// Debug in browser DevTools:
console.log('Polling enabled:', data?.session.status === 'active');
console.log('Refetch interval:', refetchInterval);
```

### Issue: "Optimistic update shows duplicate messages"

**Symptom**: Student message appears twice after sending

**Solution**:
```typescript
// Ensure onMutate cancels outgoing queries
await queryClient.cancelQueries({ queryKey: coachingKeys.session(sessionId) });

// Verify onSuccess invalidates cache (not setQueryData)
queryClient.invalidateQueries({ queryKey: coachingKeys.session(sessionId) });
```

### Issue: "Session not persisting after page refresh"

**Symptom**: Refresh clears conversation history

**Solution**:
```bash
# Check localStorage
localStorage.getItem('coaching-session-YOUR_SESSION_ID')

# Verify useSession reads from localStorage
# Check cache expiry (5 minutes in current implementation)
```

### Issue: "Multi-tenant test fails, Student B can access Student A's session"

**Symptom**: Security test passes when it should fail (403 expected)

**Solution**:
```python
# Backend MUST validate ownership:
# backend/src/routes/coaching.py
@router.get("/api/coaching/session/{session_id}")
async def get_session(
    session_id: str,
    current_student: Student = Depends(get_current_student)
):
    session = await db.get(CoachingSession, session_id)
    if session.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session
```

---

## Performance Benchmarks

**Target Performance** (from spec.md Success Criteria):

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session creation | <3s | Time from "Start Session" click to first coach message visible |
| Message send | <2s | Time from message submit to student message appears |
| Coach response | <10s (p95) | Time from message send to coach response appears |
| Chat scroll | 60 FPS | Smooth scrolling with 50+ messages (check with React DevTools Profiler) |
| Retry success | 95% within 30s | Failed sends auto-retry and succeed within 30s |

**How to Measure**:

```typescript
// Add performance markers in code
performance.mark('session-start');
// ... session creation logic ...
performance.mark('session-complete');
performance.measure('session-creation', 'session-start', 'session-complete');

// View in browser DevTools Performance tab
const measures = performance.getEntriesByType('measure');
console.table(measures);
```

---

## Next Steps

After local development and testing:

1. **Code Review**: Ensure all components follow shadcn/ui patterns
2. **Accessibility**: Test with screen reader, keyboard navigation
3. **Mobile Testing**: Test on mobile devices (375x667, 1024x768)
4. **Backend Integration**: Verify coaching APIs return expected data
5. **Deployment**: Deploy to Vercel staging environment
6. **Load Testing**: Simulate 100+ concurrent sessions

---

**Status**: ✅ Quickstart guide complete. Ready for `/sp.tasks` phase.
