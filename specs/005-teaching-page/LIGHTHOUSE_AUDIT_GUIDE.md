# Lighthouse Audit Guide: Teaching Page Feature (005)

**Purpose**: Run Lighthouse audits to verify accessibility and performance scores
**Target Scores**: 90+ for both Accessibility and Performance
**Status**: ⏳ PENDING MANUAL TESTING

---

## Prerequisites

- ✅ Frontend server running on http://localhost:3000
- ✅ Backend server running on http://localhost:8000
- ✅ Chrome/Edge browser (Lighthouse built-in)
- ✅ Test user account with login credentials

---

## How to Run Lighthouse Audits

### Step 1: Open Chrome DevTools

1. Open Chrome/Edge browser
2. Navigate to http://localhost:3000
3. Login with test student account
4. Press **F12** or **Ctrl+Shift+I** (Windows/Linux) or **Cmd+Option+I** (Mac)
5. Click on **"Lighthouse"** tab in DevTools

### Step 2: Configure Lighthouse

**For T033 (Accessibility Audit)**:
- ✅ Check **"Accessibility"** category ONLY
- ✅ Device: **Desktop**
- ✅ Clear storage: **Unchecked** (keep cache for realistic test)
- Click **"Analyze page load"**

**For T034 (Performance Audit)**:
- ✅ Check **"Performance"** category ONLY
- ✅ Device: **Mobile** (stricter performance requirements)
- ✅ Throttling: **Simulated Slow 4G** (default)
- ✅ Clear storage: **Checked** (test cold cache scenario)
- Click **"Analyze page load"**

---

## T033: Lighthouse Accessibility Audit

### Pages to Test

Run accessibility audit on these 3 pages:

#### 1. Teaching Browse Page

**URL**: http://localhost:3000/teaching

**Expected Score**: **95-100/100**

**What Lighthouse Checks**:
- ✅ ARIA attributes valid
- ✅ Button/link names present
- ✅ Color contrast (4.5:1 text, 3:1 UI)
- ✅ Document has `<title>`
- ✅ Form elements have labels
- ✅ Headings in sequential order
- ✅ Images have `alt` text or `aria-hidden`
- ✅ Lists structured correctly (`<ul>`, `<li>`)
- ✅ Focus visible (focus rings on interactive elements)
- ✅ No duplicate IDs

**Potential Issues** (and how to fix):
- ⚠️ **Missing skip link** (-5 points): Add skip-to-content link
- ⚠️ **Low contrast on muted text** (-3 points): Increase muted-foreground contrast
- ⚠️ **Missing landmark regions** (-2 points): Add `<nav>`, `<main>`, `<aside>`

**After Audit**:
1. Take screenshot of Lighthouse report
2. If score <90: Fix critical issues listed
3. Re-run audit after fixes
4. Save final score in this document

**Actual Score**: _____________ (to be filled after testing)

---

#### 2. Explanation View Page

**URL**: http://localhost:3000/teaching/[any-topic-id]

**Expected Score**: **95-100/100**

**What to Test**:
- ✅ Accordion sections keyboard accessible
- ✅ Bookmark button has `aria-pressed`
- ✅ Loading states announced to screen readers
- ✅ Error states have clear messages
- ✅ Back button keyboard accessible

**After Audit**:
1. Take screenshot
2. Check "Passed audits" section (should be 30+ items)
3. Fix any failures
4. Save final score

**Actual Score**: _____________ (to be filled after testing)

---

#### 3. Saved Explanations Page

**URL**: http://localhost:3000/teaching/saved

**Expected Score**: **95-100/100**

**What to Test**:
- ✅ Empty state has proper heading structure
- ✅ Card actions (View, Remove) keyboard accessible
- ✅ Toast notifications have `role="status"`
- ✅ Loading skeleton announced

**After Audit**:
1. Take screenshot
2. Save final score

**Actual Score**: _____________ (to be filled after testing)

---

### How to Fix Common Issues

#### Issue: "Links do not have a discernible name"

**Fix**: Add `aria-label` to icon-only links
```tsx
<Link href="/teaching" aria-label="Go to teaching page">
  <HomeIcon />
</Link>
```

#### Issue: "Background and foreground colors do not have sufficient contrast"

**Fix**: Increase contrast in Tailwind config
```typescript
// tailwind.config.ts
colors: {
  muted: {
    DEFAULT: "hsl(215.4 16.3% 40%)", // Increased from 46.9% to 40%
    foreground: "hsl(215.4 16.3% 40%)",
  },
}
```

#### Issue: "Form elements do not have associated labels"

**Fix**: Add `<label>` or `aria-label`
```tsx
<input
  type="search"
  placeholder="Search topics..."
  aria-label="Search syllabus topics"
/>
```

---

## T034: Lighthouse Performance Audit

### Pages to Test

Run performance audit on these 2 pages:

#### 1. Teaching Browse Page (Cold Cache)

**URL**: http://localhost:3000/teaching

**Expected Score**: **90-95/100** (Mobile), **95-100/100** (Desktop)

**Configuration**:
- Device: **Mobile**
- Throttling: **Simulated Slow 4G**
- Clear storage: **✅ Checked**

**What Lighthouse Measures**:
| Metric | Target (Mobile) | Weight |
|--------|-----------------|--------|
| First Contentful Paint (FCP) | <1.8s | 10% |
| Largest Contentful Paint (LCP) | <2.5s | 25% |
| Cumulative Layout Shift (CLS) | <0.1 | 25% |
| Speed Index | <3.4s | 10% |
| Time to Interactive (TTI) | <3.8s | 10% |
| Total Blocking Time (TBT) | <200ms | 30% |

**Expected Results** (from our analysis):
- FCP: ~1.2s ✅ Good
- LCP: ~1.8s ✅ Good
- CLS: ~0.02 ✅ Excellent
- TTI: ~2.5s ✅ Fast
- TBT: ~150ms ✅ Good

**Opportunities** (expected warnings):
- ✅ **Remove unused JavaScript**: Next.js tree-shaking handles this
- ✅ **Properly size images**: No images in current implementation
- ⚠️ **Reduce server response time**: AI generation takes 5-6s (acceptable)

**After Audit**:
1. Take screenshot
2. Note FCP, LCP, CLS, TTI, TBT values
3. Check "Opportunities" section
4. Implement high-impact optimizations (if any)

**Actual Score**: _____________ (to be filled after testing)

**Metrics**:
- FCP: _____________ (target <1.8s)
- LCP: _____________ (target <2.5s)
- CLS: _____________ (target <0.1)
- TTI: _____________ (target <3.8s)
- TBT: _____________ (target <200ms)

---

#### 2. Explanation View Page (Cached)

**URL**: http://localhost:3000/teaching/[topic-id]

**Expected Score**: **95-100/100** (cached explanation loads instantly)

**Configuration**:
- Device: **Desktop** (more realistic for reading long content)
- Throttling: **No throttling**
- Clear storage: **❌ Unchecked** (test with cache)

**Test Scenario**:
1. Visit explanation page once (generates AI explanation)
2. Navigate back to /teaching
3. **Run Lighthouse on same topic page** (should hit localStorage cache)

**Expected Results**:
- FCP: ~0.5s ✅ Fast (cached)
- LCP: ~0.8s ✅ Fast (cached)
- TTI: ~1.2s ✅ Fast (cached)

**After Audit**:
1. Compare cached vs uncached performance
2. Verify cache hit reduces load time by >90%

**Actual Score (Cached)**: _____________ (to be filled after testing)

---

### How to Fix Common Performance Issues

#### Issue: "Eliminate render-blocking resources"

**Current**: Tailwind CSS loaded inline (optimized)
**If needed**: Defer non-critical CSS
```html
<link rel="preload" href="/styles/critical.css" as="style" onload="this.rel='stylesheet'">
```

#### Issue: "Reduce server response time (TTFB)"

**Current**: AI generation takes 5-6s (expected)
**Optimization**: Add Redis cache on backend (see PERFORMANCE_VERIFICATION.md)

#### Issue: "Minimize main-thread work"

**Current**: React rendering <100ms (acceptable)
**If needed**: Use React.memo() on heavy components
```tsx
export const ExplanationSection = React.memo(({ section }) => {
  // ... component code
});
```

#### Issue: "Reduce JavaScript execution time"

**Fix**: Code splitting for heavy dependencies
```typescript
// Lazy load heavy library
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

---

## Lighthouse CI (Automated Testing)

**Optional**: Automate Lighthouse audits in CI/CD pipeline

### Setup Lighthouse CI

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Create lighthouse config
# .lighthouserc.json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/teaching",
        "http://localhost:3000/teaching/sample-topic-id",
        "http://localhost:3000/teaching/saved"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:performance": ["error", {"minScore": 0.9}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 200}]
      }
    }
  }
}
```

### Run Lighthouse CI

```bash
# Start servers
npm run dev &
cd backend && uvicorn src.main:app &

# Run Lighthouse CI
lhci autorun

# View results
lhci open
```

**Benefit**: Catch performance regressions before production

---

## Summary Checklist

### T033: Accessibility Audits

- [ ] Run audit on `/teaching` page
- [ ] Run audit on `/teaching/[topicId]` page
- [ ] Run audit on `/teaching/saved` page
- [ ] All scores ≥90/100
- [ ] Screenshots saved
- [ ] Critical issues fixed (if any)
- [ ] Final scores documented above

**Overall Accessibility Score**: _____________ (average of 3 pages)

**Status**: [ ] ✅ PASSED (≥90) or [ ] ❌ FAILED (<90)

---

### T034: Performance Audits

- [ ] Run audit on `/teaching` page (mobile, cold cache)
- [ ] Run audit on `/teaching/[topicId]` page (desktop, cached)
- [ ] All scores ≥90/100
- [ ] FCP, LCP, CLS, TTI, TBT metrics recorded
- [ ] Screenshots saved
- [ ] High-impact optimizations implemented (if needed)
- [ ] Final scores documented above

**Overall Performance Score**: _____________ (average of 2 pages)

**Status**: [ ] ✅ PASSED (≥90) or [ ] ❌ FAILED (<90)

---

## Next Steps After Audits

1. **If all passed (≥90)**:
   - ✅ Mark T033 and T034 complete in tasks.md
   - ✅ Proceed to T035 (Update CLAUDE.md)

2. **If any failed (<90)**:
   - ❌ Review Lighthouse "Opportunities" and "Diagnostics"
   - ❌ Implement fixes from this guide
   - ❌ Re-run audits
   - ❌ Repeat until all pass

3. **Save audit reports**:
   - Export HTML reports: Lighthouse → "⚙️" → "Save HTML"
   - Save to: `specs/005-teaching-page/lighthouse-reports/`

---

**Created**: 2025-12-25
**Purpose**: Manual testing guide for T033 and T034
**Status**: ⏳ AWAITING MANUAL TESTING
