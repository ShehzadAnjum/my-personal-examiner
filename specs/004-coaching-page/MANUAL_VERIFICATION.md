# Coaching Page - Manual Verification Checklist

**Feature**: 004-coaching-page
**Created**: 2025-12-25
**Purpose**: Consolidate all manual verification tasks (T065, T068, T071, T073, T074, T076)

---

## Quick Start

```bash
# 1. Start backend (in backend/ directory)
cd backend && source .venv/bin/activate
uvicorn src.main:app --reload --port 8000

# 2. Start frontend (in frontend/ directory)
cd frontend && npm run dev

# 3. Open browser at http://localhost:3000/coaching
```

---

## T065: Mobile Responsive Design Verification

### Test at Three Viewport Sizes

| Viewport | Device | Chrome DevTools Preset |
|----------|--------|------------------------|
| 375x667 | iPhone SE | iPhone SE |
| 1024x768 | iPad (landscape) | iPad |
| 1920x1080 | Desktop | - (default) |

### Checklist (Test at each viewport)

**Session Init Form (`/coaching`)**:
- [ ] Form is centered and readable
- [ ] Textarea is full width (not overflowing)
- [ ] Button is tappable (min 44px height on mobile)
- [ ] Character counter doesn't overlap
- [ ] Back arrow is accessible

**Chat Interface (`/coaching/[sessionId]`)**:
- [ ] Messages don't overflow container
- [ ] Message bubbles have appropriate max-width
- [ ] Input area is sticky at bottom
- [ ] Send button is accessible
- [ ] Typing indicator doesn't cause layout shift
- [ ] Scrolling is smooth

**Session History (`/coaching/history`)**:
- [ ] Cards are full-width on mobile, grid on desktop
- [ ] Filter/sort buttons are accessible
- [ ] Session list is scrollable
- [ ] Empty state is centered

**Session Outcome**:
- [ ] Outcome badge is visible
- [ ] Action buttons are stacked on mobile
- [ ] Links are tappable

### How to Test

1. Open Chrome DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Select device or set dimensions manually
4. Navigate through all coaching pages
5. Check each item above

---

## T068: Accessibility Audit (WCAG 2.1 AA)

### Automated Testing

```bash
# Option 1: Chrome Lighthouse
# DevTools > Lighthouse > Accessibility

# Option 2: axe DevTools Extension
# Install: https://www.deque.com/axe/devtools/
# Run on each page
```

### Checklist

**Keyboard Navigation**:
- [ ] Tab through all interactive elements
- [ ] Focus ring is visible on focused elements
- [ ] Escape closes modals/dropdowns
- [ ] Enter submits form / sends message
- [ ] Arrow keys work in dropdowns

**Screen Reader**:
- [ ] All images have alt text
- [ ] Form labels are associated with inputs
- [ ] Error messages are announced
- [ ] Loading states are announced
- [ ] Coach/student roles are identifiable

**Color & Contrast**:
- [ ] Text contrast ratio ≥ 4.5:1
- [ ] Focus indicators contrast ≥ 3:1
- [ ] Information not conveyed by color alone

**ARIA**:
- [ ] `role="region"` on major sections
- [ ] `aria-label` on icon buttons
- [ ] `aria-live="polite"` on dynamic content
- [ ] `aria-busy` during loading

### Expected Lighthouse Score

- Accessibility: ≥ 90
- Performance: ≥ 80
- Best Practices: ≥ 90

---

## T071: Security Verification (Multi-Tenant Isolation)

### Test Scenario: Student B Cannot Access Student A's Session

**Setup**:
1. Create two test accounts (Student A and Student B)
2. Login as Student A in Browser 1 (or Incognito)
3. Login as Student B in Browser 2 (or different Incognito)

**Test Steps**:

```bash
# Step 1: Student A creates a session
# Navigate to /coaching
# Enter topic: "Test session for security"
# Click "Start Session"
# Note the session ID from URL: /coaching/{SESSION_ID}

# Step 2: Student B tries to access Student A's session
# Copy the SESSION_ID
# In Student B's browser, navigate to: /coaching/{SESSION_ID}
# Expected: 403 Forbidden error page or redirect to own sessions
```

**Checklist**:
- [ ] Student B sees error page (not Student A's conversation)
- [ ] Backend returns 403 Forbidden (check Network tab)
- [ ] No data leakage in error response
- [ ] localStorage is student-scoped
- [ ] History shows only own sessions

**API Level Test** (curl):

```bash
# Get tokens for both students
TOKEN_A="your_student_a_jwt_token"
TOKEN_B="your_student_b_jwt_token"

# Student A creates session
curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"topic": "security test", "student_id": "student_a_uuid"}'

# Note the session_id from response

# Student B tries to access it
curl -X GET http://localhost:8000/api/coaching/session/{SESSION_ID} \
  -H "Authorization: Bearer $TOKEN_B"

# Expected: {"detail": "Not authorized"} with status 403
```

---

## T073: Performance Benchmarks

### Target Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Session creation | < 3 seconds | Start button click → first coach message visible |
| Message send | < 2 seconds | Submit → student message appears |
| Coach response | < 10 seconds (p95) | Student message → coach response appears |
| Chat scroll | 60 FPS | React DevTools Profiler |
| First paint | < 2 seconds | Lighthouse First Contentful Paint |

### Measurement Methods

**Browser Performance API**:
```javascript
// In browser console before testing
performance.clearMarks();
performance.clearMeasures();

// Add marks in code (already implemented in components)
// Then check:
performance.getEntriesByType('measure').forEach(m =>
  console.log(`${m.name}: ${m.duration.toFixed(2)}ms`)
);
```

**Network Tab**:
1. Open DevTools > Network
2. Clear logs
3. Perform action (create session, send message)
4. Check timing for API calls

**React DevTools Profiler**:
1. Install React DevTools extension
2. Go to Profiler tab
3. Record while scrolling chat
4. Check for dropped frames

### Checklist

- [ ] Session creation: _____ ms (target: < 3000ms)
- [ ] Message send optimistic update: _____ ms (target: < 200ms)
- [ ] Coach response: _____ ms (target: < 10000ms)
- [ ] Chat scroll FPS: _____ (target: 60)
- [ ] Lighthouse Performance score: _____ (target: ≥ 80)

---

## T074: Demo Video (<90 seconds)

### Recording Setup

**Tools**:
- OBS Studio (recommended)
- Loom
- Chrome DevTools Recorder
- macOS QuickTime / Windows Game Bar

**Settings**:
- Resolution: 1920x1080
- Framerate: 30fps
- Format: MP4

### Demo Script (90 seconds max)

```
0:00 - 0:10  | Title screen: "AI Coaching Session Demo"
0:10 - 0:20  | Show coaching page (/coaching)
0:20 - 0:35  | Enter struggle: "I don't understand price elasticity"
             | Click "Start Session"
0:35 - 0:45  | Show coach's first message appearing
             | Highlight typing indicator
0:45 - 1:00  | Send student response: "Demand goes down?"
             | Show optimistic update (message appears immediately)
1:00 - 1:10  | Show coach's response
1:10 - 1:20  | Continue until session ends (or time-lapse)
1:20 - 1:30  | Show session outcome (resolved/needs_more_help)
             | Show next actions
```

### Checklist

- [ ] Video is < 90 seconds
- [ ] Shows complete flow: start → chat → outcome
- [ ] No PII or real credentials visible
- [ ] Audio narration (optional but recommended)
- [ ] Saved to: `docs/demos/coaching-demo.mp4`

---

## T076: Manual Testing Checklist

### P1 - Start Coaching Session

- [ ] Navigate to `/coaching`
- [ ] Enter valid struggle (10+ chars): "I don't understand elasticity"
- [ ] Click "Start Session"
- [ ] Loading indicator appears
- [ ] Coach's first question appears within 5 seconds
- [ ] URL changes to `/coaching/{sessionId}`
- [ ] **Error case**: Empty description shows validation error
- [ ] **Error case**: Too short (<10 chars) shows error
- [ ] **Error case**: Network error shows retry option

### P1 - Chat Conversation

- [ ] Send message: "Demand goes down?"
- [ ] Message appears immediately (optimistic update)
- [ ] Typing indicator: "Coach is thinking..."
- [ ] Coach response appears within 10 seconds
- [ ] Messages have readable timestamps
- [ ] Student messages: right-aligned, blue background
- [ ] Coach messages: left-aligned, gray background
- [ ] **Long message test**: 500+ character message displays correctly
- [ ] **Long conversation test**: 20+ messages scroll smoothly
- [ ] **Offline test**: Offline banner appears when disconnected
- [ ] **Retry test**: Failed message shows retry button

### P2 - Session Outcome

- [ ] Continue conversation until coach concludes session
- [ ] Outcome badge appears (resolved/needs_more_help/refer_to_teacher)
- [ ] Summary text describes what was learned
- [ ] Next actions list (1-5 items) with links
- [ ] Input field is disabled
- [ ] Message shows: "Session ended"
- [ ] "Start New Session" button works

### P3 - Session History

- [ ] Navigate to `/coaching/history`
- [ ] Past sessions listed with:
  - [ ] Topic
  - [ ] Date (relative: "2 hours ago")
  - [ ] Outcome badge
  - [ ] Message count
- [ ] Filter by outcome works
- [ ] Sort by date works
- [ ] Click session → view transcript
- [ ] Transcript is read-only (no input)
- [ ] Empty state shows when no sessions

---

## Completion Sign-off

| Task | Status | Verified By | Date |
|------|--------|-------------|------|
| T065 Mobile Responsive | [ ] Pass / [ ] Fail | __________ | ___/___/___ |
| T068 Accessibility | [ ] Pass / [ ] Fail | __________ | ___/___/___ |
| T071 Security | [ ] Pass / [ ] Fail | __________ | ___/___/___ |
| T073 Performance | [ ] Pass / [ ] Fail | __________ | ___/___/___ |
| T074 Demo Video | [ ] Complete | __________ | ___/___/___ |
| T076 Manual Testing | [ ] Pass / [ ] Fail | __________ | ___/___/___ |

**All Verified**: [ ] Yes → Ready for production deployment

---

**Notes/Issues Found**:

(Document any issues discovered during verification here)
