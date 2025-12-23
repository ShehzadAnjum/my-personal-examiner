# Manual Testing Guide - 004 Coaching Page

**Feature:** Interactive AI Coaching Page
**Branch:** 004-coaching-page
**Status:** Implementation Complete (70/78 tasks)
**Remaining:** 8 Manual Testing Tasks

---

## Quick Start

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
pnpm dev
```

**Access:** http://localhost:3000/coaching

---

## T065: Mobile Responsive Testing ⏱️ 30 minutes

### Objective
Verify coaching page works on all screen sizes from mobile (375px) to desktop (1920px).

### Test Devices/Sizes

#### 1. Mobile Portrait (375px - 428px)
- [ ] iPhone SE (375px)
- [ ] iPhone 12/13 (390px)
- [ ] iPhone 14 Pro Max (428px)

**What to Check:**
- [ ] Session init form fits without horizontal scroll
- [ ] Topic input and submit button stack vertically
- [ ] Chat messages are readable (not cut off)
- [ ] Message input area doesn't cover messages
- [ ] Send button is accessible
- [ ] Session history list displays properly
- [ ] No overlapping UI elements

#### 2. Mobile Landscape (667px - 926px)
- [ ] iPhone SE landscape (667px)
- [ ] iPhone 14 Pro Max landscape (926px)

**What to Check:**
- [ ] Chat interface uses horizontal space efficiently
- [ ] Message input doesn't take too much height
- [ ] Session history sidebar (if shown) doesn't crowd chat

#### 3. Tablet Portrait (768px - 834px)
- [ ] iPad Mini (768px)
- [ ] iPad Air (820px)
- [ ] iPad Pro 11" (834px)

**What to Check:**
- [ ] Two-column layout (if implemented)
- [ ] Comfortable reading width for messages
- [ ] Adequate white space

#### 4. Tablet Landscape (1024px - 1366px)
- [ ] iPad Pro 12.9" (1024px)
- [ ] iPad Pro landscape (1366px)

**What to Check:**
- [ ] Multi-column layout works well
- [ ] Chat doesn't stretch too wide
- [ ] Session history visible alongside chat

#### 5. Desktop (1440px - 1920px)
- [ ] Laptop (1440px)
- [ ] Desktop (1920px)

**What to Check:**
- [ ] Maximum width constraint applied (content doesn't stretch edge-to-edge)
- [ ] Centered layout with appropriate margins
- [ ] All interactive elements easily clickable

### Chrome DevTools Testing Steps

1. Open http://localhost:3000/coaching
2. Press `F12` to open DevTools
3. Click "Toggle Device Toolbar" (Ctrl+Shift+M)
4. Select each device from dropdown
5. For each size:
   - Start a new session
   - Send 5-10 messages
   - Check session history
   - Test all interactive elements
   - Take screenshot of any issues

### Pass Criteria
- ✅ No horizontal scrolling on any screen size
- ✅ All buttons/inputs accessible without zooming
- ✅ Text readable at default zoom level
- ✅ No overlapping UI elements
- ✅ Consistent spacing and padding

### Report Format
```markdown
## Mobile Responsive Testing Results

### iPhone SE (375px) - PASS/FAIL
- Session init form: PASS
- Chat interface: PASS
- Message input: FAIL - Button cut off
- Session history: PASS

[Screenshot: issue-375px-button.png]

**Issues Found:** 1
**Blockers:** 0
```

---

## T068: Accessibility Audit ⏱️ 45 minutes

### Objective
Ensure WCAG 2.1 AA compliance for coaching page.

### Tools Required
- Chrome DevTools Lighthouse
- axe DevTools extension
- NVDA or JAWS screen reader (optional)

### Test Checklist

#### 1. Keyboard Navigation
- [ ] Tab through all interactive elements in logical order
- [ ] All buttons/links reachable via keyboard
- [ ] Focus indicators visible on all focusable elements
- [ ] `Ctrl+Enter` sends message (keyboard shortcut)
- [ ] `Escape` clears input or cancels action
- [ ] No keyboard traps (can tab out of all components)
- [ ] Skip to main content link present (optional)

#### 2. Screen Reader Testing (with NVDA/JAWS)
- [ ] Page title announced correctly
- [ ] Form labels read aloud
- [ ] Button purposes clear from labels
- [ ] Error messages announced
- [ ] Loading states announced ("Sending message...")
- [ ] Chat messages have proper ARIA roles
- [ ] Session outcomes read clearly

#### 3. Color Contrast
- [ ] Text on background: 4.5:1 ratio minimum (normal text)
- [ ] Large text (18pt+): 3:1 ratio minimum
- [ ] Interactive elements: 3:1 ratio for borders/icons
- [ ] Focus indicators: 3:1 ratio against background
- [ ] Error messages: Sufficient contrast

**Test with:**
```bash
# Install axe DevTools extension
# Or use Chrome Lighthouse
```

#### 4. Semantic HTML
- [ ] Headings in logical order (h1 → h2 → h3, no skipping)
- [ ] Form inputs have associated `<label>` elements
- [ ] Buttons use `<button>` (not `<div onClick>`)
- [ ] Links use `<a>` with meaningful text
- [ ] Lists use `<ul>`/`<ol>` + `<li>`
- [ ] Main content in `<main>` landmark

#### 5. ARIA Labels
- [ ] Images have `alt` text or `aria-label`
- [ ] Icon-only buttons have `aria-label`
- [ ] Loading spinners have `aria-live="polite"`
- [ ] Error messages have `role="alert"`
- [ ] Chat messages have `role="log"` or `role="region"`
- [ ] Form validation errors linked via `aria-describedby`

#### 6. Focus Management
- [ ] Focus moves to error message on validation failure
- [ ] Focus stays on page (not lost) after actions
- [ ] Modal dialogs trap focus (if any)
- [ ] Focus returns to trigger element after modal closes

### Automated Testing

#### Lighthouse Accessibility Audit
```bash
# 1. Open http://localhost:3000/coaching
# 2. Open Chrome DevTools (F12)
# 3. Go to Lighthouse tab
# 4. Select "Accessibility" only
# 5. Click "Analyze page load"
```

**Target Score:** 95+ (100 ideal)

#### axe DevTools
```bash
# 1. Install axe DevTools extension
# 2. Open http://localhost:3000/coaching
# 3. Open DevTools → axe DevTools tab
# 4. Click "Scan ALL of my page"
```

**Target:** 0 violations

### Pass Criteria
- ✅ Lighthouse accessibility score ≥ 95
- ✅ axe DevTools: 0 critical/serious violations
- ✅ All keyboard navigation tests pass
- ✅ Color contrast ratios meet WCAG 2.1 AA
- ✅ Screen reader announces all key information

### Report Format
```markdown
## Accessibility Audit Results

### Lighthouse Score: 98/100

### axe DevTools Violations
- **Critical:** 0
- **Serious:** 0
- **Moderate:** 2
  1. Missing aria-label on icon button (Line 45, ChatInterface.tsx)
  2. Color contrast 4.2:1 on secondary text (should be 4.5:1)

### Keyboard Navigation: PASS
- All elements reachable
- Focus indicators visible
- Keyboard shortcuts working

**Issues Found:** 2 moderate
**Blockers:** 0
```

---

## T071: Security Testing ⏱️ 30 minutes

### Objective
Verify the coaching page is secure against common web vulnerabilities.

### Test Checklist

#### 1. XSS (Cross-Site Scripting)

**Test Inputs:**
```javascript
// Try these in the topic/message input fields
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
javascript:alert('XSS')
<svg onload=alert('XSS')>
```

**Expected Result:**
- [ ] Input is sanitized (script tags escaped or removed)
- [ ] Alert boxes do NOT appear
- [ ] Text displayed as plain text, not executed

#### 2. Input Validation

**Test Cases:**

| Input | Expected Behavior | Pass/Fail |
|-------|------------------|-----------|
| Empty topic | Validation error: "Topic required" | |
| Topic > 200 chars | Validation error or truncated | |
| SQL injection: `'; DROP TABLE--` | Treated as plain text | |
| HTML tags: `<h1>Test</h1>` | Escaped or sanitized | |
| Unicode: `测试 🔥` | Accepted and displayed correctly | |
| Newlines/tabs | Preserved or normalized | |

#### 3. CSRF Protection

**Check:**
- [ ] API calls include CSRF tokens (if applicable)
- [ ] Requests require authentication
- [ ] No sensitive actions on GET requests
- [ ] SameSite cookie attribute set

**How to Test:**
```bash
# Check cookies in DevTools → Application → Cookies
# Look for: SameSite=Lax or SameSite=Strict
```

#### 4. Authentication & Authorization

**Test:**
- [ ] Cannot access other users' sessions via URL manipulation
- [ ] Session IDs not predictable
- [ ] Logout clears session completely
- [ ] Session timeout after inactivity (if implemented)

**URL Manipulation Test:**
```
# Try accessing another session:
http://localhost:3000/coaching/00000000-0000-0000-0000-000000000001
# Should return 403 Forbidden or 404 Not Found
```

#### 5. Data Exposure

**Check:**
- [ ] No API keys in client-side code
- [ ] No sensitive data in console.log()
- [ ] No PII in URLs or query strings
- [ ] Error messages don't reveal system details

**DevTools Check:**
```bash
# 1. Open DevTools → Sources
# 2. Search for: "API_KEY", "SECRET", "PASSWORD"
# 3. Open Network tab
# 4. Check response payloads for sensitive data
```

#### 6. Content Security Policy (CSP)

**Check Response Headers:**
```bash
curl -I http://localhost:3000/coaching
# Look for: Content-Security-Policy header
```

**Expected:**
- [ ] CSP header present
- [ ] Restricts inline scripts
- [ ] Whitelists trusted domains

### Pass Criteria
- ✅ No XSS vulnerabilities
- ✅ All inputs validated/sanitized
- ✅ CSRF protection in place
- ✅ Authentication enforced
- ✅ No data exposure
- ✅ CSP headers configured

### Report Format
```markdown
## Security Testing Results

### XSS Testing: PASS
- Tested 5 payloads
- All inputs sanitized
- No script execution

### Input Validation: PASS
- 8/8 test cases passed
- Edge cases handled correctly

### CSRF: PASS
- SameSite cookies enabled
- CSRF tokens present

### Issues Found: 0
### Blockers: 0
```

---

## T073: Performance Testing ⏱️ 30 minutes

### Objective
Ensure coaching page meets performance benchmarks (Lighthouse score >90).

### Tools Required
- Chrome DevTools Lighthouse
- Network throttling

### Test Checklist

#### 1. Lighthouse Performance Audit

**Steps:**
```bash
# 1. Open http://localhost:3000/coaching
# 2. Open DevTools (F12) → Lighthouse tab
# 3. Select: Performance, Best Practices
# 4. Device: Mobile
# 5. Click "Analyze page load"
```

**Target Scores:**
- [ ] Performance: ≥90
- [ ] Best Practices: ≥90
- [ ] SEO: ≥90 (optional for internal app)

**Key Metrics:**
- [ ] First Contentful Paint (FCP): <1.8s
- [ ] Largest Contentful Paint (LCP): <2.5s
- [ ] Time to Interactive (TTI): <3.8s
- [ ] Total Blocking Time (TBT): <200ms
- [ ] Cumulative Layout Shift (CLS): <0.1

#### 2. Network Performance

**Test on Slow 3G:**
```bash
# DevTools → Network tab → Throttling dropdown → Slow 3G
```

- [ ] Page loads within 10 seconds
- [ ] Loading skeletons appear immediately
- [ ] No blank screen >3 seconds
- [ ] Images load progressively

**Test on Fast 3G:**
- [ ] Page loads within 5 seconds
- [ ] Interactive within 7 seconds

#### 3. Bundle Size Analysis

**Check JavaScript Bundle Size:**
```bash
# DevTools → Network tab → JS filter
# Reload page and check total JS transferred
```

**Targets:**
- [ ] Initial JS bundle: <500KB gzipped
- [ ] Total JS: <1MB gzipped
- [ ] No duplicate libraries

**Check for Code Splitting:**
```bash
# Look for multiple JS chunks (not one huge bundle)
# Example: main.js, coaching.chunk.js, vendors.chunk.js
```

#### 4. Runtime Performance

**Test with 50+ Messages:**
```bash
# 1. Start a session
# 2. Send 50+ messages (use script or manually)
# 3. Open DevTools → Performance tab
# 4. Click Record, scroll through messages, stop recording
```

**Check:**
- [ ] No frame drops during scroll
- [ ] Smooth animations (60fps)
- [ ] No memory leaks (heap size stable)

**Memory Test:**
```bash
# DevTools → Memory tab → Take heap snapshot
# Send 100 messages
# Take another heap snapshot
# Compare: Should not grow >10MB
```

#### 5. Image Optimization

- [ ] Images use modern formats (WebP, AVIF)
- [ ] Images lazy-loaded (below fold)
- [ ] Responsive images with srcset
- [ ] No images larger than displayed size

#### 6. Caching

**Check Cache Headers:**
```bash
# DevTools → Network tab
# Look for: Cache-Control headers on static assets
```

- [ ] Static assets cached (max-age=31536000)
- [ ] HTML not cached (no-cache or short max-age)
- [ ] Service Worker registered (if applicable)

### Pass Criteria
- ✅ Lighthouse Performance ≥90
- ✅ FCP <1.8s, LCP <2.5s, TTI <3.8s
- ✅ JS bundle <500KB gzipped
- ✅ Smooth scrolling with 50+ messages
- ✅ No memory leaks

### Report Format
```markdown
## Performance Testing Results

### Lighthouse Scores (Mobile)
- Performance: 94/100 ✅
- Best Practices: 96/100 ✅

### Core Web Vitals
- FCP: 1.2s ✅
- LCP: 2.1s ✅
- TTI: 3.2s ✅
- TBT: 150ms ✅
- CLS: 0.05 ✅

### Bundle Size
- Initial JS: 420KB gzipped ✅
- Total JS: 850KB gzipped ✅

### Runtime Performance
- Scrolling: 60fps ✅
- Memory: Stable (no leaks) ✅

**Issues Found:** 0
**Optimizations Applied:** React.memo, lazy loading
```

---

## T074: Demo Video Creation ⏱️ 45 minutes

### Objective
Create a 2-3 minute demo video showing the coaching page in action.

### Script Outline

**Duration: 2-3 minutes**

#### Scene 1: Introduction (15 seconds)
```
[Screen: Coaching page at /coaching]

Voiceover: "Welcome to the AI Coaching feature of My Personal Examiner.
This tool helps students overcome learning struggles through Socratic questioning."
```

#### Scene 2: Starting a Session (30 seconds)
```
[Screen: Session init form]

Voiceover: "Let's say a student is struggling with price elasticity.
They simply describe their struggle in the topic field."

[Type: "I don't understand price elasticity of demand"]

Voiceover: "With one click, the AI Coach starts a personalized coaching session."

[Click "Start Coaching Session"]
```

#### Scene 3: Socratic Dialogue (60 seconds)
```
[Screen: Chat interface with Coach's first question]

Voiceover: "The Coach doesn't give direct answers. Instead, it asks Socratic questions
to help the student think critically and discover concepts themselves."

[Show 3-4 message exchanges:]
- Coach: "Can you describe what happens when the price of something changes?"
- Student: "People buy less of it?"
- Coach: "Exactly! Now, why do you think that happens?"
- Student: "Maybe because it's more expensive?"
- Coach: "Good thinking! There are two key effects at play here..."

Voiceover: "Through guided questioning, the student builds genuine understanding."
```

#### Scene 4: Session Outcome (20 seconds)
```
[Screen: Session outcome modal showing "Resolved"]

Voiceover: "When the student's misconception is resolved, the session ends with
a summary and recommendations for further study."

[Show outcome: "Great progress! You now understand the substitution and income effects."]
```

#### Scene 5: Session History (15 seconds)
```
[Screen: Session history list]

Voiceover: "Students can review all past sessions, making it easy to revisit
concepts and track their learning journey."
```

#### Scene 6: Closing (10 seconds)
```
[Screen: Coaching page overview]

Voiceover: "AI Coaching: Socratic questioning that builds deep understanding.
Available 24/7 for every Cambridge Economics student."

[Fade to logo]
```

### Recording Setup

**Tools:**
- OBS Studio (free, cross-platform)
- Or Loom (web-based)
- Or QuickTime Player (Mac)

**Settings:**
```
Resolution: 1920x1080
Frame rate: 30fps
Format: MP4 (H.264)
Audio: 44.1kHz, mono or stereo
```

**Pre-Recording Checklist:**
- [ ] Clear browser cache
- [ ] Disable browser extensions (cleaner UI)
- [ ] Close unnecessary tabs
- [ ] Hide bookmarks bar
- [ ] Full-screen browser window
- [ ] Test microphone audio
- [ ] Prepare test data (pre-seed database if needed)

### Recording Steps

1. **Record Voiceover First (Optional)**
   - Write script
   - Record audio separately
   - Sync with screen recording later

2. **Record Screen**
   ```bash
   # Start OBS Studio
   # Add browser source: http://localhost:3000/coaching
   # Start recording
   # Follow script
   # Stop recording
   ```

3. **Edit (Optional)**
   - Trim dead space
   - Add zoom-ins for important UI elements
   - Add text overlays for key points
   - Add background music (low volume)

### Deliverables
- [ ] MP4 file: `004-coaching-page-demo.mp4`
- [ ] Upload to: YouTube (unlisted) or project repository
- [ ] Add link to PR description

### Pass Criteria
- ✅ Shows complete user flow (start → dialogue → outcome)
- ✅ Audio clear and professional
- ✅ No technical glitches visible
- ✅ 2-3 minutes duration
- ✅ Demonstrates key features

---

## T076: Manual Checklist Execution ⏱️ 20 minutes

### Objective
Verify all key features work end-to-end through manual testing.

### Test Checklist

#### Session Initialization
- [ ] Navigate to `/coaching`
- [ ] Page loads without errors
- [ ] Session init form visible
- [ ] Topic input accepts text
- [ ] Empty topic shows validation error
- [ ] Valid topic enables "Start Coaching Session" button
- [ ] Click button creates new session
- [ ] Redirects to `/coaching/[sessionId]`
- [ ] Chat interface loads

#### Chat Conversation
- [ ] Coach's first message appears
- [ ] Message input field active
- [ ] Type a response
- [ ] Click send button (or press Ctrl+Enter)
- [ ] Message appears in chat immediately (optimistic update)
- [ ] Loading indicator shown while waiting for Coach
- [ ] Coach's response appears
- [ ] Send 5+ messages back and forth
- [ ] All messages display correctly
- [ ] Timestamps visible
- [ ] Avatar/name shown for each message
- [ ] Scroll works smoothly
- [ ] Long messages wrap properly
- [ ] No messages overlap

#### Error Handling
- [ ] Disconnect internet
- [ ] Try to send a message
- [ ] Error toast appears
- [ ] Message marked as failed
- [ ] Reconnect internet
- [ ] Retry sending message
- [ ] Success toast appears

#### Session Outcomes
- [ ] Continue chatting until Coach suggests ending
- [ ] Session outcome modal appears
- [ ] Outcome type shown (resolved/needs_more_help/refer_to_teacher)
- [ ] Summary text visible
- [ ] "View History" button works
- [ ] "Start New Session" button works

#### Session History
- [ ] Navigate to `/coaching` (or click "View History")
- [ ] All past sessions listed
- [ ] Sessions sorted by date (newest first)
- [ ] Each session shows: topic, date, outcome
- [ ] Click on a session
- [ ] Navigates to session detail page
- [ ] Full transcript loads
- [ ] Cannot send new messages (read-only)

#### Keyboard Shortcuts
- [ ] Focus message input
- [ ] Press `Ctrl+Enter`
- [ ] Message sends
- [ ] Press `Escape` while typing
- [ ] Input clears (or action cancels)

#### Performance (Subjective)
- [ ] Page loads in <3 seconds
- [ ] Chat scrolling smooth (no lag)
- [ ] Messages appear instantly after sending
- [ ] No freezing or stuttering
- [ ] Loading states appear/disappear quickly

#### Visual Polish
- [ ] No console errors (check DevTools)
- [ ] No broken images
- [ ] Consistent spacing and alignment
- [ ] Buttons have hover states
- [ ] Focus states visible when tabbing
- [ ] Loading skeletons appear during async operations
- [ ] Toast notifications styled correctly

### Pass Criteria
- ✅ All checklist items pass
- ✅ No critical bugs found
- ✅ User flow smooth and intuitive

### Report Format
```markdown
## Manual Checklist Execution Results

### Passed: 35/35 items

### Failed: 0

### Notes:
- Session initialization: Smooth, no issues
- Chat conversation: 10 messages tested, all displayed correctly
- Error handling: Network error handled gracefully
- Session outcomes: "Resolved" outcome tested
- Session history: 3 sessions visible, all clickable
- Keyboard shortcuts: Both shortcuts working
- Performance: Fast and responsive
- Visual polish: No issues

**Overall Status: PASS ✅**
```

---

## Summary Report Template

After completing all tasks, create a summary report:

```markdown
# Manual Testing Summary - 004 Coaching Page

**Date:** YYYY-MM-DD
**Tester:** [Your Name]
**Branch:** 004-coaching-page
**Build:** [Commit SHA]

---

## Test Results

| Task | Status | Issues Found | Blockers |
|------|--------|--------------|----------|
| T065: Mobile Responsive | ✅ PASS | 0 | 0 |
| T068: Accessibility | ✅ PASS | 2 (moderate) | 0 |
| T071: Security | ✅ PASS | 0 | 0 |
| T073: Performance | ✅ PASS | 0 | 0 |
| T074: Demo Video | ✅ COMPLETE | - | - |
| T076: Manual Checklist | ✅ PASS | 0 | 0 |

---

## Overall Assessment

✅ **READY FOR PRODUCTION**

All manual tests passed. 2 moderate accessibility issues found (non-blocking).

### Issues to Address (Post-Merge)
1. Add aria-label to icon button (ChatInterface.tsx:45)
2. Increase color contrast on secondary text (4.2:1 → 4.5:1)

### Recommendations
- Monitor error rates in production
- Collect user feedback on Socratic questioning quality
- A/B test different coaching strategies

---

**Next Steps:**
1. Create issues for 2 accessibility fixes
2. Merge PR #1
3. Deploy to staging
4. Monitor for 24 hours
5. Deploy to production
```

---

## Tools & Resources

### Browser Extensions
- [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools/lhdoppojpmngadmnindnejefpokejbdd)
- [WAVE](https://wave.webaim.org/extension/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) (built into Chrome)

### Screen Readers
- [NVDA](https://www.nvaccess.org/) (Windows, free)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) (Windows, paid)
- VoiceOver (Mac/iOS, built-in)

### Recording Tools
- [OBS Studio](https://obsproject.com/) (free, all platforms)
- [Loom](https://www.loom.com/) (web-based)
- QuickTime Player (Mac, built-in)

### Testing Checklist Tools
- Google Sheets or Excel
- Markdown checklist (this document)
- Notion or Trello

---

**Questions?** Refer to:
- `specs/004-coaching-page/spec.md` - Feature specification
- `specs/004-coaching-page/plan.md` - Implementation plan
- `frontend/README.md` - Setup instructions
