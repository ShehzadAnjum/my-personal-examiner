# Quickstart Guide: Teaching Page User Flows

**Feature**: 005-teaching-page (PhD-Level Concept Explanations)
**Date**: 2025-12-23
**Phase**: 1 (Design & Contracts)
**Purpose**: Document user flows and integration scenarios for teaching page

---

## Overview

This guide demonstrates 3 primary user flows for the teaching page feature:

1. **View Explanation Flow** (P1) - Student selects a topic and views PhD-level explanation
2. **Search Topics Flow** (P2) - Student searches for topics by keyword
3. **Bookmark Flow** (P3) - Student saves explanations for later review

---

## Flow 1: View Explanation (User Story 1 - P1)

**User Goal**: Understand "Price Elasticity of Demand" concept for A-Level Economics exam

**Steps**:

1. **Navigate to Teaching Page**
   - User clicks "Teaching" in dashboard sidebar
   - Route: `/teaching`
   - Loads `frontend/app/(dashboard)/teaching/page.tsx`

2. **Browse Topics**
   - Page loads `TopicBrowser` component
   - `useTopics()` hook fetches syllabus topics from `GET /api/teaching/syllabus`
   - Topics displayed in hierarchical tree:
     - AS-Level
       - Paper 2 - Microeconomics
         - 3.1.2 Price Elasticity of Demand (PED)
         - 3.1.3 Income Elasticity of Demand (YED)
         - ... more topics

3. **Select Topic**
   - User clicks "3.1.2 Price Elasticity of Demand" card
   - Navigate to `/teaching/550e8400-e29b-41d4-a716-446655440000` (topic ID)
   - Loads `frontend/app/(dashboard)/teaching/[topicId]/page.tsx`

4. **AI Generation (5-10 seconds)**
   - `ExplanationSkeleton` component shows loading state (pulse animation)
   - `useExplanation(topicId)` hook calls `POST /api/teaching/explain`
   - Backend:
     - Fetches SyllabusPoint from database
     - Calls Teacher Agent (Claude Sonnet 4.5) with PhD-level prompt
     - Generates TopicExplanation with all required components
     - Returns JSON response

5. **View Explanation**
   - `ExplanationView` component displays generated content
   - Sections displayed in order:
     - **Definition** (quote block, always expanded):
       > "PED measures the responsiveness of quantity demanded to a change in price, calculated as % change in quantity demanded / % change in price."
     - **Key Terms** (collapsible):
       - Elastic demand: PED > 1
       - Inelastic demand: PED < 1
       - Unitary elastic: PED = 1
     - **Core Principles** (always expanded):
       - 2-3 paragraphs explaining concept deeply
     - **Examples** (collapsible):
       1. Elastic Demand: Luxury Cars
       2. Inelastic Demand: Gasoline
     - **Visual Aids** (collapsible):
       - Diagram description: "Elastic curve (flat) vs Inelastic curve (steep)"
     - **Worked Examples** (collapsible):
       - Problem: Calculate PED if price rises from $10 to $12...
       - Solution: Step 1, Step 2, Step 3, Interpretation
     - **Common Misconceptions** (collapsible):
       - Misconception: "PED is always negative"
       - Why wrong: Convention reports absolute value
       - Correct understanding: Report as positive (e.g., 1.5)
     - **Practice Problems** (collapsible):
       - 3 problems with answer outlines
     - **Related Concepts** (always expanded):
       - Links to 3.1.3 YED, 3.1.4 Cross Elasticity, 3.2.1 Consumer Surplus

6. **Interact with Explanation**
   - User clicks "Examples" accordion → expands to show 2 examples
   - User reads first example (luxury cars)
   - User collapses "Examples" → collapsed
   - User clicks "Practice Problems" → expands to show 3 problems
   - User attempts first problem mentally
   - User clicks "answer outline" → reveals solution approach

**Expected Outcome**:
- ✅ Explanation loads within 10 seconds
- ✅ All 9 required components present (definition, key terms, examples, etc.)
- ✅ Collapsible sections work smoothly (accordion animation)
- ✅ Typography clear and readable (leading-relaxed, appropriate font sizes)
- ✅ Mobile responsive (works on 375px width)

**Technical Flow**:
```
User → /teaching → TopicBrowser → Click topic 3.1.2
  → /teaching/{topicId} → ExplanationSkeleton (5-10s)
  → POST /api/teaching/explain → Teacher Agent generates AI response
  → ExplanationView displays → User reads and interacts
```

**Caching Behavior**:
- First visit: 5-10 seconds (AI generation)
- Return within 5 minutes: <1 second (TanStack Query cache hit)
- Return after 5 minutes: 5-10 seconds (cache stale, regenerate)

---

## Flow 2: Search Topics (User Story 2 - P2)

**User Goal**: Find all topics related to "elasticity" quickly

**Steps**:

1. **Navigate to Teaching Page**
   - User lands on `/teaching`
   - Page shows `TopicBrowser` + `TopicSearch` components

2. **Type Search Query**
   - User types "elasticity" in search input
   - Debounced 300ms → `TopicSearch` component updates after user stops typing

3. **Client-Side Filtering**
   - `TopicSearch` uses `useMemo` to filter topics array:
     ```typescript
     const filteredTopics = topics.filter(topic =>
       topic.code.toLowerCase().includes('elasticity') ||
       topic.description.toLowerCase().includes('elasticity') ||
       topic.learning_outcomes?.toLowerCase().includes('elasticity')
     );
     ```
   - **Performance**: <1ms for 200 topics (in-memory array filter)

4. **View Search Results**
   - Results displayed in grid (3 columns on desktop, 1 on mobile):
     - 3.1.2 Price Elasticity of Demand (PED)
     - 3.1.3 Income Elasticity of Demand (YED)
     - 3.1.4 Cross Elasticity of Demand (XED)
     - 3.1.5 Price Elasticity of Supply (PES)
   - Matching keywords highlighted in yellow (`<mark>` tag with Tailwind)
   - Result count shown: "4 results for 'elasticity'"

5. **Select Result**
   - User clicks "3.1.3 Income Elasticity of Demand"
   - Navigate to `/teaching/{YED-topic-id}`
   - [Same as Flow 1 steps 4-6]

6. **Clear Search**
   - User clicks X button in search input
   - Search query cleared
   - Results hidden
   - TopicBrowser returns to full hierarchical view

**Expected Outcome**:
- ✅ Instant search results (<1ms latency, no API call)
- ✅ Keyword highlighting shows matches clearly
- ✅ Empty state shown if no results ("No results found for '{query}'")
- ✅ Clear button (X) resets search

**Technical Flow**:
```
User → /teaching → TopicSearch input → Type "elasticity" (debounced 300ms)
  → Client-side filter (useMemo) → Display 4 matching TopicCards
  → Click YED card → /teaching/{YED-id} → [View Explanation Flow]
```

**Caching Behavior**:
- Topics fetched once on page load (1-hour cache)
- Search filtering happens in memory (no API calls)
- If user returns within 1 hour: Topics already cached, instant load

**Future Enhancement** (if topics exceed 1000):
- Switch to server-side search: `GET /api/teaching/syllabus?search=elasticity`
- Backend filters topics, returns subset
- Tradeoff: 200-500ms network latency vs reduced client payload

---

## Flow 3: Bookmark Explanation (User Story 3 - P3)

**User Goal**: Save "Price Elasticity of Demand" explanation for exam revision

**Steps**:

1. **View Explanation** (prerequisite)
   - User already viewing explanation at `/teaching/{PED-topic-id}`
   - [Followed Flow 1 steps 1-5]

2. **Bookmark Explanation**
   - User clicks "Bookmark" button (top-right of page, sticky position)
   - `BookmarkButton` component shows loading spinner (Loader2 icon)
   - `useBookmark()` mutation hook called:
     ```typescript
     bookmarkMutation.mutate({
       syllabusPointId: topicId,
       explanation: explanationData,
     });
     ```
   - API call: `POST /api/teaching/explanations`
   - Request body:
     ```json
     {
       "syllabus_point_id": "550e8400-...",
       "explanation_content": { /* full TopicExplanation JSON */ }
     }
     ```

3. **Backend Processing**
   - Backend creates `SavedExplanation` row in database:
     - student_id: Extracted from JWT
     - syllabus_point_id: From request
     - explanation_content: Full explanation JSON (~5-10KB)
     - date_saved: Current timestamp
   - Unique constraint prevents duplicate bookmarks (student + topic)

4. **Success Feedback**
   - Button state changes:
     - Icon: Bookmark (outline) → BookmarkCheck (filled)
     - Text: "Bookmark" → "Bookmarked"
     - Variant: outline → default (filled background)
   - Toast notification appears (top-right, 3-second duration):
     > ✅ "Explanation saved"
     > "You can review this later in Saved Explanations."
   - TanStack Query invalidates `['savedExplanations']` cache

5. **Navigate to Saved Explanations**
   - User clicks "Saved" in teaching page navigation
   - Navigate to `/teaching/saved`
   - Loads `frontend/app/(dashboard)/teaching/saved/page.tsx`

6. **View Saved List**
   - `useSavedExplanations()` hook fetches: `GET /api/teaching/explanations`
   - Backend returns array of SavedExplanation objects (student_id filter applied)
   - `SavedExplanationsList` component displays bookmarks:
     - Grid of TopicCards (3 columns)
     - Each card shows:
       - Topic code (e.g., "3.1.2")
       - Topic name (e.g., "Price Elasticity of Demand")
       - Date saved (e.g., "Dec 23, 2025")
       - X button (remove bookmark)

7. **View Saved Explanation**
   - User clicks on saved "3.1.2 PED" card
   - Navigate to `/teaching/{PED-topic-id}`
   - Explanation loads from TanStack Query cache (if within 5 minutes) OR re-fetches
   - "Bookmarked" button already filled (isBookmarked=true)

8. **Remove Bookmark** (optional)
   - User clicks X button on saved card
   - Confirmation toast: "Are you sure?"
   - User confirms → `DELETE /api/teaching/explanations/{saved-id}`
   - Backend deletes SavedExplanation row (student_id verified)
   - Toast: "Bookmark removed"
   - TanStack Query invalidates `['savedExplanations']` cache
   - Card removed from grid

**Expected Outcome**:
- ✅ Bookmark saved within 1 second
- ✅ Button state updates immediately (loading → bookmarked)
- ✅ Toast notification confirms action
- ✅ Saved list reflects bookmark immediately (cache invalidated)
- ✅ Remove bookmark works smoothly (with confirmation)
- ✅ No duplicate bookmarks allowed (409 error if attempted)

**Technical Flow**:
```
User → /teaching/{topicId} → Click "Bookmark" button
  → POST /api/teaching/explanations → Backend creates SavedExplanation
  → Button state updates + Toast notification + Cache invalidation
  → Navigate to /teaching/saved → GET /api/teaching/explanations
  → SavedExplanationsList displays bookmarks → Click card to view
  → /teaching/{topicId} (cached or re-fetch)
```

**Caching Behavior**:
- After bookmark: `['savedExplanations']` cache invalidated
- Next visit to /teaching/saved: Fetches fresh list (includes new bookmark)
- Saved list cached for 1 minute (fast subsequent visits)

---

## Integration Scenarios

### Scenario 1: First-Time User

**Steps**:
1. User registers account → logs in
2. Navigates to /teaching (first visit)
3. GET /api/teaching/syllabus fetches all topics (200 topics, 50KB)
4. User browses topics, clicks "3.1.2 PED"
5. AI generates explanation (8 seconds, Claude Sonnet 4.5)
6. User reads explanation, bookmarks it
7. User logs out, logs back in next day
8. Navigates to /teaching/saved → sees 1 saved explanation
9. Clicks saved explanation → loads from cache (if <5 min) OR re-fetches

**Expected Experience**:
- Smooth onboarding (no empty states after bookmark)
- Fast subsequent visits (topics cached 1 hour)
- Personalized saved list (only user's bookmarks)

### Scenario 2: Power User (10 bookmarks, daily usage)

**Steps**:
1. User logs in daily
2. Navigates to /teaching → topics cached from yesterday (1-hour cache)
3. Searches "elasticity" → instant results (client-side filter)
4. Views new topic "3.1.6 Elasticity and Revenue" → AI generates
5. Bookmarks explanation (#11 bookmark)
6. Navigates to /teaching/saved → sees 11 bookmarks
7. Clicks bookmark #3 "Consumer Surplus" → loads from cache (viewed 2 min ago)
8. Removes bookmark #8 "Inferior Goods" → toast confirms removal

**Expected Experience**:
- Fast topic browsing (cache hit rate >80%)
- Quick bookmark access (1-minute cache on saved list)
- Efficient saved list management (remove old bookmarks)

### Scenario 3: Mobile Student (375px screen, slow 3G)

**Steps**:
1. User on mobile phone (iPhone SE, 375px width)
2. Navigates to /teaching (slow 3G, 2 Mbps)
3. Topics load (50KB payload, 5-second load on 3G)
4. TopicBrowser collapses to single column
5. User types search "demand" → debounced 300ms
6. Results show in single column (not 3-column grid)
7. User clicks "3.1.1 Demand Curve" → AI generates (10 seconds on 3G)
8. ExplanationView displays in single column (max-width 600px)
9. User expands "Examples" section → smooth animation
10. User bookmarks → toast notification appears (mobile-friendly position)

**Expected Experience**:
- Responsive layout adapts to 375px
- Readable typography on small screen (text-base, leading-relaxed)
- Touch-friendly buttons (min 44px tap target)
- Accessible collapsible sections (keyboard + touch navigation)

---

## Error Handling Scenarios

### Scenario 4: AI Service Timeout

**Steps**:
1. User requests explanation for topic "3.1.2 PED"
2. POST /api/teaching/explain called
3. Teacher Agent times out after 30 seconds
4. Backend returns 500 error: "Failed to generate explanation: AI service timeout"
5. Frontend catches error in `useExplanation` hook
6. Toast notification appears:
   > ❌ "Failed to load explanation"
   > "AI service timeout. Please try again."
7. "Retry" button shown on page
8. User clicks "Retry" → re-fetches explanation
9. Second attempt succeeds (3 seconds)

**Expected Experience**:
- Clear error message (not generic "Something went wrong")
- Retry option (don't force full page reload)
- Error logged for monitoring (backend logs timeout incidents)

### Scenario 5: Duplicate Bookmark Attempt

**Steps**:
1. User views explanation "3.1.2 PED"
2. Clicks "Bookmark" → success (201 Created)
3. User navigates away, returns to same explanation
4. Clicks "Bookmark" again (forgot they already bookmarked)
5. POST /api/teaching/explanations returns 409 Conflict: "Already bookmarked"
6. Frontend catches error in `useBookmark` mutation
7. Toast notification:
   > ℹ️ "Already bookmarked"
   > "This explanation is already in your saved list."
8. Button remains in "Bookmarked" state (no change)

**Expected Experience**:
- Graceful handling (not crash or generic error)
- Helpful message ("Already bookmarked" not "Error 409")
- Button state consistent with reality (remains bookmarked)

---

## Performance Benchmarks

### Load Times (Expected)
- **Topics List**: <1 second (50KB payload, cached 1 hour)
- **Search Results**: <1ms (client-side filter)
- **AI Explanation**: 5-10 seconds (Teacher Agent generation)
- **Cached Explanation**: <1 second (TanStack Query cache hit)
- **Bookmark Save**: <1 second (POST request)
- **Saved List**: <1 second (GET request, cached 1 minute)

### Cache Hit Rates (Projected)
- **Topics**: 80% (users browse multiple times, 1-hour cache)
- **Explanations**: 50% (popular topics viewed frequently, 5-minute cache)
- **Saved List**: 70% (users check saved list multiple times per session, 1-minute cache)

### Lighthouse Scores (Target)
- **Performance**: 90+ (optimized images, lazy loading, code splitting)
- **Accessibility**: 90+ (WCAG 2.1 AA compliance, ARIA labels, keyboard nav)
- **Best Practices**: 90+ (HTTPS, no mixed content, secure cookies)
- **SEO**: 90+ (meta tags, semantic HTML, structured data)

---

## Next Steps

**After quickstart review**:
1. Update `specs/phase-4-web-ui/CLAUDE.md` with teaching page patterns (Task T030)
2. Run `/sp.tasks` to generate task breakdown
3. Execute `/sp.implement` to build teaching page
4. Manual testing against quickstart flows
5. Deploy to staging for user acceptance testing

**Quickstart Guide Complete**: All user flows documented with technical details.
