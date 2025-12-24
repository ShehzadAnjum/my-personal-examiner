# Manual Testing Guide: Teaching Page Feature (005)

**Feature**: Teaching Page - Concept Explanations
**Branch**: 005-teaching-page
**User Stories**: US1, US2, US3
**Test Date**: 2025-12-25

---

## Prerequisites

- [ ] Backend server running on http://localhost:8000
- [ ] Frontend server running (usually http://localhost:3000)
- [ ] Valid student account created (or use existing test account)
- [ ] Browser DevTools Console open (F12) to monitor errors

---

## User Story 1: Browse Syllabus Topics

**Goal**: Students can browse a hierarchical list of Economics 9708 syllabus topics

### Test Scenario 1.1: Navigate to Teaching Page

1. **Action**: Navigate to `/teaching` (or click "Teaching" in navigation)
2. **Expected**:
   - [ ] Page loads without errors
   - [ ] Page title displays: "Learn Economics 9708"
   - [ ] Subtitle/description visible
   - [ ] Syllabus browser section visible
   - [ ] No console errors

### Test Scenario 1.2: View Topic Hierarchy

1. **Action**: Observe the topic list structure
2. **Expected**:
   - [ ] Topics are grouped by syllabus sections (e.g., "Basic Economic Ideas", "The Price System")
   - [ ] Each section shows a count of subtopics (e.g., "12 topics")
   - [ ] Hierarchy is clearly visible (parent → child relationships)
   - [ ] Topic codes are displayed (e.g., "1.1", "1.2")

### Test Scenario 1.3: Expand/Collapse Sections (if implemented)

1. **Action**: Click on a section header or expand icon
2. **Expected**:
   - [ ] Section expands to show child topics
   - [ ] Expand/collapse animation is smooth
   - [ ] Icon changes state (e.g., chevron rotates)
   - [ ] Other sections remain in their current state

### Test Scenario 1.4: Click on Topic

1. **Action**: Click on a specific topic (e.g., "Price Elasticity of Demand")
2. **Expected**:
   - [ ] Navigates to `/teaching/[topicId]`
   - [ ] Topic ID appears in URL
   - [ ] Page loads explanation (moves to US2 testing)

---

## User Story 2: Generate & Display Explanation

**Goal**: Students request and view PhD-level explanations for selected concepts

### Test Scenario 2.1: First-Time Explanation Generation

**Prerequisites**: Select a topic from the syllabus browser

1. **Action**: Wait for explanation to load (first time for this topic)
2. **Expected**:
   - [ ] Loading spinner or skeleton visible during generation
   - [ ] Loading takes 5-15 seconds (AI generation time)
   - [ ] No timeout errors after 30 seconds

### Test Scenario 2.2: Explanation Content Structure

1. **Action**: Review the displayed explanation
2. **Expected Components** (all should be present):
   - [ ] **Concept Name**: Clear, prominent title (e.g., "Price Elasticity of Demand")
   - [ ] **Syllabus Code**: Displays correct code (e.g., "1.2.3")
   - [ ] **Definition**: Precise, concise definition (1-2 sentences)
   - [ ] **Key Terms**: List of 3-5 terms with definitions
   - [ ] **Core Principles**: 2-3 paragraphs explaining fundamental concepts
   - [ ] **Real-World Examples**: 2-3 examples with analysis
   - [ ] **Visual Aids**: Diagram descriptions (e.g., "supply/demand curve showing...")
   - [ ] **Worked Examples**: Step-by-step problem solutions
   - [ ] **Common Misconceptions**: 2-3 misconceptions with corrections
   - [ ] **Practice Problems**: 2-3 problems with answer outlines
   - [ ] **Related Concepts**: Links/references to connected topics

### Test Scenario 2.3: Collapsible Sections

1. **Action**: Click on section headers (if collapsible)
2. **Expected**:
   - [ ] Sections expand/collapse smoothly
   - [ ] State persists when switching sections
   - [ ] Expand/collapse all button works (if present)

### Test Scenario 2.4: Typography & Formatting

1. **Action**: Review text formatting
2. **Expected**:
   - [ ] Clear visual hierarchy (headings, subheadings)
   - [ ] Math formulas rendered correctly (if MathJax/KaTeX used)
   - [ ] Code blocks formatted properly (if applicable)
   - [ ] Lists are bulleted/numbered appropriately
   - [ ] Text is readable (font size, line height, contrast)

### Test Scenario 2.5: Cached Explanation (Second Load)

1. **Action**: Navigate back to syllabus, then re-select the same topic
2. **Expected**:
   - [ ] Explanation loads INSTANTLY (from localStorage cache)
   - [ ] No loading spinner
   - [ ] Content is identical to first load
   - [ ] Console shows localStorage retrieval (check DevTools)

### Test Scenario 2.6: Navigation

1. **Action**: Click "Back" button (if present)
2. **Expected**:
   - [ ] Returns to `/teaching` (syllabus browser)
   - [ ] Syllabus state is preserved (same scroll position, expansions)

---

## User Story 3: Bookmark Explanations

**Goal**: Students can save explanations for later review

### Test Scenario 3.1: Initial Bookmark State

**Prerequisites**: Viewing an explanation for a topic

1. **Action**: Observe bookmark button state
2. **Expected**:
   - [ ] Bookmark button visible (e.g., "☆ Save for Later" or bookmark icon)
   - [ ] Button is NOT active (outline star, not filled)
   - [ ] Button is enabled (not disabled)

### Test Scenario 3.2: Save Bookmark

1. **Action**: Click the bookmark button
2. **Expected**:
   - [ ] Button changes state immediately (☆ → ★ or "Saved")
   - [ ] Toast notification appears: "Explanation saved" or similar
   - [ ] No page reload
   - [ ] Button text changes to "★ Saved" or "Bookmarked"

### Test Scenario 3.3: Verify Bookmark Saved (Backend)

1. **Action**: Open DevTools → Network tab, filter by XHR/Fetch
2. **Expected**:
   - [ ] POST request to `/api/teaching/explanations/save` or similar
   - [ ] Request payload includes `syllabus_point_id`
   - [ ] Response status: 200 or 201
   - [ ] Response includes saved explanation object with `id`, `date_saved`

### Test Scenario 3.4: Navigate to Saved Page

1. **Action**: Click "Saved Explanations" link/button (or navigate to `/teaching/saved`)
2. **Expected**:
   - [ ] Page loads without errors
   - [ ] Page title: "Saved Explanations" or similar
   - [ ] Saved explanation appears in the list

### Test Scenario 3.5: Saved Explanation List Item

1. **Action**: Review the saved explanation card/item
2. **Expected Display**:
   - [ ] **Concept Name**: "Price Elasticity of Demand" (or topic name)
   - [ ] **Definition Preview**: First 1-2 lines of definition (truncated)
   - [ ] **Date Saved**: "Saved 12/25/2025" or relative time
   - [ ] **Syllabus Code**: "1.2.3" (if available)
   - [ ] **View Button**: Clickable button to open explanation
   - [ ] **Remove/Delete Button**: Trash icon or "Remove" button

### Test Scenario 3.6: View Saved Explanation

1. **Action**: Click "View" button on a saved explanation
2. **Expected**:
   - [ ] Navigates to `/teaching/[topicId]`
   - [ ] Explanation loads from cache (instant load)
   - [ ] Bookmark button shows "★ Saved" (active state)
   - [ ] All content is identical to when first saved

### Test Scenario 3.7: Remove Bookmark

1. **Action**: On the saved page, click "Remove" or trash icon
2. **Expected**:
   - [ ] Confirmation dialog appears (optional, but recommended)
   - [ ] Item disappears from list immediately (optimistic update)
   - [ ] Toast notification: "Bookmark removed"
   - [ ] DELETE request sent to backend (check Network tab)
   - [ ] List updates (remaining items adjust, no gap)

### Test Scenario 3.8: Verify Bookmark Removed (Persistence)

1. **Action**: Navigate back to the topic's explanation page
2. **Expected**:
   - [ ] Bookmark button shows "☆ Save for Later" (inactive state)
   - [ ] Button is enabled and clickable

### Test Scenario 3.9: Empty State (No Saved Explanations)

1. **Action**: Remove all saved explanations, then visit `/teaching/saved`
2. **Expected**:
   - [ ] Empty state message: "No saved explanations yet" or similar
   - [ ] Illustration or icon (optional)
   - [ ] Call-to-action: "Browse Topics" button → links to `/teaching`

### Test Scenario 3.10: Toggle Bookmark from Explanation Page

1. **Action**: On an explanation page, click bookmark button twice (save → unsave)
2. **Expected**:
   - [ ] First click: Saves bookmark (★ Saved)
   - [ ] Second click: Removes bookmark (☆ Save for Later)
   - [ ] Both actions use optimistic updates (instant UI change)
   - [ ] Toast notifications for both actions
   - [ ] No page reload

### Test Scenario 3.11: Bookmark with Cache Missing

1. **Action**:
   - Save a bookmark
   - Clear localStorage: `localStorage.clear()` in DevTools Console
   - Navigate to `/teaching/saved`
2. **Expected**:
   - [ ] Bookmark still appears in list (pointer stored in backend)
   - [ ] Preview shows placeholder text: "Explanation content not cached"
   - [ ] "Regenerate" button appears instead of "View"
   - [ ] Clicking "Regenerate" → navigates to topic page, fetches fresh explanation

---

## Cross-Cutting Tests

### Performance

1. **Action**: Test on slow network (DevTools → Network → Slow 3G)
2. **Expected**:
   - [ ] Loading states visible during API calls
   - [ ] No timeout errors (at least 30s timeout)
   - [ ] Cached content loads instantly even on slow network

### Mobile Responsiveness (if implemented)

1. **Action**: Open DevTools → Device Mode → iPhone 12 Pro
2. **Expected**:
   - [ ] Layout adjusts to mobile screen
   - [ ] Text is readable (no horizontal scroll)
   - [ ] Buttons are tappable (min 44x44px touch targets)
   - [ ] No overlapping elements

### Accessibility (if implemented)

1. **Action**: Test keyboard navigation (Tab, Enter, Escape keys)
2. **Expected**:
   - [ ] Can navigate all interactive elements via keyboard
   - [ ] Focus indicators visible
   - [ ] Screen reader announces page regions (test with NVDA/VoiceOver)

### Error Handling

1. **Action**: Stop backend server, try to load explanation
2. **Expected**:
   - [ ] Error message displays: "Failed to load explanation" or similar
   - [ ] Retry button appears
   - [ ] No white screen of death
   - [ ] Console shows meaningful error (not generic 500)

2. **Action**: Restart backend, click retry
3. **Expected**:
   - [ ] Explanation loads successfully
   - [ ] Error state clears

---

## Test Results Summary

### US1: Browse Syllabus Topics
- [ ] All scenarios passed
- [ ] Issues found: _[List any issues]_

### US2: Generate & Display Explanation
- [ ] All scenarios passed
- [ ] Issues found: _[List any issues]_

### US3: Bookmark Explanations
- [ ] All scenarios passed
- [ ] Issues found: _[List any issues]_

### Cross-Cutting
- [ ] Performance acceptable
- [ ] Mobile responsive (if applicable)
- [ ] Accessible (if applicable)
- [ ] Error handling robust

---

## Notes

**Common Issues to Watch For**:
- CORS errors (backend and frontend on different ports)
- localStorage quota exceeded (if too many explanations cached)
- Slow first load (AI generation takes time)
- Toast notifications stacking (if clicking bookmark rapidly)
- Optimistic updates not rolling back on error

**DevTools Checklist**:
- Console: No errors or warnings
- Network: All API calls return 200/201
- Application → Local Storage: Check cached explanations
- Application → Local Storage: Check TanStack Query cache

---

**Tester**: _[Your Name]_
**Test Date**: 2025-12-25
**Test Duration**: _[Minutes]_
**Pass/Fail**: _[Overall Result]_
