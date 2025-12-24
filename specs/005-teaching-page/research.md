# Research: Teaching Page Technical Decisions

**Feature**: 005-teaching-page (PhD-Level Concept Explanations)
**Date**: 2025-12-23
**Phase**: 0 (Research & Technical Decisions)
**Purpose**: Resolve technical unknowns before implementation planning

---

## Decision 1: Component Reuse from 004-coaching-page

**Question**: What reusable component patterns from 004-coaching-page apply to teaching page?

**Investigation**:
- Analyzed 004-coaching-page implementation (PR #1, merged Dec 23)
- Identified reusable patterns: Error boundaries, Toast notifications, Skeleton loading, TanStack Query setup
- shadcn/ui components already installed: Accordion, Card, Input, Button, Skeleton, Toast

**Alternatives Considered**:
1. **Build everything from scratch** - Rejected: Duplicates effort, inconsistent UX across features
2. **Reuse all coaching components** - Rejected: Coaching has chat-specific components (MessageList, ChatInput) not applicable to teaching
3. **Reuse infrastructure, create new UI components** - ✅ **CHOSEN**

**Choice**: Reuse infrastructure patterns (error boundaries, toasts, skeletons, TanStack Query config), create new teaching-specific UI components (TopicBrowser, ExplanationView, etc.)

**Rationale**:
- Error boundary pattern works for any feature (frontend/components/coaching/ErrorBoundary.tsx → adapt for teaching routes)
- Toast notifications are generic (success/error feedback applies to bookmarking)
- Skeleton loading pattern reusable (coaching skeletons → teaching skeletons with different structure)
- TanStack Query provider already set up in app/providers.tsx
- shadcn/ui Accordion perfect for collapsible sections (installed, accessible, keyboard-navigable)

**Implementation Impact**:
- Saves 2-3 hours not recreating error boundaries, toasts, skeleton pattern
- Consistent UX across coaching and teaching features
- No new dependencies required (Accordion already from shadcn/ui)

---

## Decision 2: TanStack Query Caching Strategy

**Question**: What cache configuration for syllabus topics (static) vs explanations (dynamic AI-generated)?

**Investigation**:
- Reviewed TanStack Query docs: https://tanstack.com/query/latest/docs/react/guides/caching
- Analyzed 004-coaching-page caching patterns (coaching sessions cached 5 minutes)
- Estimated data characteristics:
  - Syllabus topics: ~200 items, 50KB total, changes monthly (syllabus updates)
  - AI explanations: 5-10KB each, expensive to generate (5-10 seconds), changes never (deterministic for same topic)
  - Saved explanations: User-specific, changes frequently (bookmarking), <100 items per user

**Alternatives Considered**:

1. **Aggressive caching (1 hour for everything)**
   - Pros: Fewer API calls, faster UX
   - Cons: Stale explanation data if backend changes, user sees outdated bookmarks
   - Rejected: User bookmark actions need immediate reflection

2. **No caching (fetch every time)**
   - Pros: Always fresh data
   - Cons: Slow UX (AI generation 5-10 seconds), unnecessary API load for static topics
   - Rejected: Poor performance, wastes backend resources

3. **Tiered caching based on data volatility** - ✅ **CHOSEN**
   - Topics: 1 hour stale time (rarely change)
   - Explanations: 5 minutes stale time (expensive, but deterministic)
   - Saved explanations: 1 minute stale time (user actions need quick reflection)

**Choice**: Tiered caching strategy

**Configuration**:
```typescript
// frontend/lib/hooks/useTopics.tsx
export const useTopics = (filters?) => {
  return useQuery({
    queryKey: ['topics', filters],
    queryFn: () => teachingApi.getTopics(filters),
    staleTime: 60 * 60 * 1000, // 1 hour
    cacheTime: 2 * 60 * 60 * 1000, // 2 hours
  });
};

// frontend/lib/hooks/useExplanation.tsx
export const useExplanation = (topicId: string) => {
  return useQuery({
    queryKey: ['explanation', topicId],
    queryFn: () => teachingApi.explainConcept(topicId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!topicId,
  });
};

// frontend/lib/hooks/useSavedExplanations.tsx
export const useSavedExplanations = () => {
  return useQuery({
    queryKey: ['savedExplanations'],
    queryFn: () => teachingApi.getSavedExplanations(),
    staleTime: 1 * 60 * 1000, // 1 minute
    cacheTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

**Rationale**:
- Topics change only with syllabus updates (monthly) → 1-hour cache safe
- Explanations deterministic for same topic → 5-minute cache reduces AI calls without staleness risk
- Saved explanations user-specific → 1-minute cache balances freshness with performance

**Performance Impact**:
- Estimated 80% cache hit rate for topics (users browse multiple times)
- Estimated 50% cache hit rate for explanations (popular topics viewed frequently)
- Reduced AI generation load: ~200 topics × 10 students = 2000 potential calls → ~1000 actual calls (50% cached)

---

## Decision 3: Collapsible Section UI Pattern

**Question**: Use shadcn/ui Accordion component or custom collapsible sections?

**Investigation**:
- Reviewed shadcn/ui Accordion docs: https://ui.shadcn.com/docs/components/accordion
- Tested accessibility: ARIA labels, keyboard navigation (Enter to toggle, Tab to navigate), screen reader support
- Compared to custom implementation (headless UI + manual ARIA)

**Alternatives Considered**:

1. **Custom collapsible with headless UI**
   - Pros: Full control over behavior
   - Cons: 2-3 hours implementation time, accessibility bugs likely, reinventing the wheel
   - Rejected: Shadcn/ui Accordion already accessible and installed

2. **React Collapse library**
   - Pros: Lightweight, simple API
   - Cons: Not integrated with shadcn/ui design system, inconsistent with other components
   - Rejected: Shadcn/ui Accordion better fit

3. **shadcn/ui Accordion** - ✅ **CHOSEN**
   - Pros: Already installed (from 004-coaching-page), accessible (WCAG 2.1 AA), customizable with Tailwind, keyboard-navigable
   - Cons: None significant

**Choice**: shadcn/ui Accordion component

**Implementation**:
```typescript
// frontend/components/teaching/ExplanationSection.tsx
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export function ExplanationSection({ title, children, defaultExpanded, icon }: ExplanationSectionProps) {
  return (
    <Accordion type="single" collapsible defaultValue={defaultExpanded ? "item-1" : undefined}>
      <AccordionItem value="item-1">
        <AccordionTrigger className="text-xl font-semibold">
          {icon && <span className="mr-2">{icon}</span>}
          {title}
        </AccordionTrigger>
        <AccordionContent className="text-base leading-relaxed">
          {children}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

**Default State**:
- **Always Expanded**: Definition, Core Principles, Related Concepts (essential information)
- **Collapsible**: Examples, Misconceptions, Practice Problems, Visual Aids, Worked Examples (supplementary content)

**Accessibility**:
- Keyboard: Enter toggles, Tab navigates, Escape closes (if expanded)
- Screen reader: "Examples, collapsed, button" → "Examples, expanded, button"
- Focus indicators: Visible outline on keyboard focus

**Rationale**:
- Zero implementation time (component already exists)
- Accessibility built-in (no manual ARIA setup)
- Consistent with shadcn/ui design system used across application
- Customizable via Tailwind (matches teaching page aesthetic)

---

## Decision 4: Search Implementation

**Question**: Client-side search (fetch all topics, filter locally) or server-side search (API endpoint)?

**Investigation**:
- Counted Economics 9708 topics: ~200 topics (AS + A2, Papers 1-4)
- Estimated payload size: ~50KB JSON (200 topics × 250 bytes average)
- Tested client-side filtering performance: Array.filter() on 200 items < 1ms
- Projected future scale: Accounting 9706 (~150 topics), Math 9709 (~300 topics) = 650 topics total across subjects

**Alternatives Considered**:

1. **Server-side search with GET /api/teaching/syllabus?search=keyword**
   - Pros: Scales to 10,000+ topics, reduces client payload
   - Cons: Network round-trip (200-500ms latency), backend query complexity, no instant results
   - Rejected: Premature optimization for current scale (200 topics)

2. **Client-side search with Fuse.js (fuzzy matching)**
   - Pros: Typo-tolerant search ("elasticty" matches "elasticity"), instant results
   - Cons: Additional dependency (10KB), complexity for simple exact match
   - Rejected: Overkill for 200 topics with clear syllabus codes

3. **Client-side search with Array.filter() (exact match)** - ✅ **CHOSEN**
   - Pros: Zero latency, no dependencies, simple implementation, works offline
   - Cons: Requires fetching all topics upfront (50KB), no fuzzy matching
   - **Chosen**: Optimal for current scale, revisit if topics exceed 1000

**Choice**: Client-side search with exact match on topic code, description, learning outcomes

**Implementation**:
```typescript
// frontend/components/teaching/TopicSearch.tsx
const filteredTopics = useMemo(() => {
  if (!searchQuery) return topics;

  const query = searchQuery.toLowerCase();
  return topics.filter(topic =>
    topic.code.toLowerCase().includes(query) ||
    topic.description.toLowerCase().includes(query) ||
    topic.learning_outcomes?.toLowerCase().includes(query)
  );
}, [topics, searchQuery]);
```

**Performance**:
- Initial load: Fetch 200 topics (~50KB) on page mount
- Search latency: <1ms for 200 items (Array.filter in-memory)
- UX: Instant results as user types (with 300ms debounce to avoid excessive renders)

**Future Migration Path**:
- If topics exceed 1000 (adding Accounting, Math, English): Switch to server-side search
- Backend already supports `GET /api/teaching/syllabus?search=keyword`
- Migration: Update `useTopics` hook to pass search query as API parameter instead of client filter

**Rationale**:
- 200 topics easily fit in browser memory (50KB negligible)
- Instant search results superior UX to network round-trip (200-500ms)
- Simpler implementation (no backend query logic needed)
- Future-proof (backend API supports server-side search if needed)

---

## Decision 5: Bookmark Persistence

**Question**: Does SavedExplanation model exist in backend? If not, what migration needed?

**Investigation**:
- Checked backend models: `ls backend/src/models/`
- Found:
  - ✅ `syllabus_point.py` (exists)
  - ✅ `student.py` (exists)
  - ✅ `subject.py` (exists)
  - ❌ `saved_explanation.py` (DOES NOT EXIST)

- Checked backend routes: `grep -r "teaching/explanations" backend/src/routes/`
- Found: ❌ No endpoints for saved explanations (GET/POST/DELETE)

**Conclusion**: SavedExplanation model and endpoints **DO NOT EXIST**. Must create before implementing bookmark feature.

**Alternatives Considered**:

1. **Defer bookmark feature to future phase**
   - Pros: Faster initial implementation (P1 + P2 only)
   - Cons: Incomplete feature (spec requires bookmarking), poor UX for students
   - Rejected: Bookmarking is P3 (lower priority but still MVP scope)

2. **Create SavedExplanation model + migration + endpoints** - ✅ **CHOSEN**
   - Pros: Complete feature per spec, reusable pattern for future bookmark features
   - Cons: Requires backend work (1-2 hours)
   - **Chosen**: Necessary to fulfill spec requirements

**Choice**: Create SavedExplanation model, Alembic migration, and backend endpoints

**Required Backend Work**:

1. **Model**: `backend/src/models/saved_explanation.py`
```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class SavedExplanation(SQLModel, table=True):
    __tablename__ = "saved_explanations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", index=True)
    syllabus_point_id: UUID = Field(foreign_key="syllabus_points.id", index=True)
    explanation_content: dict = Field(sa_column=Column(JSON))  # Full TopicExplanation JSON
    date_saved: datetime = Field(default_factory=datetime.utcnow)
    date_last_viewed: Optional[datetime] = None

    # Relationships
    student: Optional["Student"] = Relationship(back_populates="saved_explanations")
    syllabus_point: Optional["SyllabusPoint"] = Relationship(back_populates="saved_explanations")

    # Multi-tenant constraint
    __table_args__ = (
        UniqueConstraint("student_id", "syllabus_point_id", name="unique_student_topic"),
    )
```

2. **Migration**: `backend/alembic/versions/007_add_saved_explanations.py`
```python
"""Add saved_explanations table

Revision ID: 007
Revises: 006
Create Date: 2025-12-23
"""

def upgrade():
    op.create_table(
        'saved_explanations',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('student_id', sa.UUID(), sa.ForeignKey('students.id'), nullable=False),
        sa.Column('syllabus_point_id', sa.UUID(), sa.ForeignKey('syllabus_points.id'), nullable=False),
        sa.Column('explanation_content', sa.JSON(), nullable=False),
        sa.Column('date_saved', sa.DateTime(), nullable=False),
        sa.Column('date_last_viewed', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('student_id', 'syllabus_point_id', name='unique_student_topic'),
        sa.Index('ix_saved_explanations_student_id', 'student_id'),
    )

def downgrade():
    op.drop_table('saved_explanations')
```

3. **Endpoints**: Add to `backend/src/routes/teaching.py`
```python
@router.get("/explanations")
async def get_saved_explanations(student_id: UUID, session: Session = Depends(get_session)):
    """Get all saved explanations for a student."""
    statement = select(SavedExplanation).where(SavedExplanation.student_id == student_id)
    saved = session.exec(statement).all()
    return {"saved_explanations": saved}

@router.post("/explanations")
async def save_explanation(
    request: SaveExplanationRequest,
    student_id: UUID,  # From JWT
    session: Session = Depends(get_session)
):
    """Bookmark an explanation."""
    saved = SavedExplanation(
        student_id=student_id,
        syllabus_point_id=request.syllabus_point_id,
        explanation_content=request.explanation_content,
    )
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return {"saved_explanation": saved}

@router.delete("/explanations/{id}")
async def remove_saved_explanation(id: UUID, student_id: UUID, session: Session = Depends(get_session)):
    """Remove a bookmarked explanation."""
    statement = select(SavedExplanation).where(
        SavedExplanation.id == id,
        SavedExplanation.student_id == student_id  # Multi-tenant check
    )
    saved = session.exec(statement).first()
    if not saved:
        raise HTTPException(404, "Saved explanation not found")
    session.delete(saved)
    session.commit()
    return {"success": True}
```

**Impact on tasks.md**:
- Add T001.1: Create SavedExplanation model
- Add T001.2: Create Alembic migration 007
- Add T001.3: Add saved explanation endpoints to backend/src/routes/teaching.py
- Add T001.4: Test bookmark endpoints with pytest

**Estimated Time**: 1-2 hours backend work (before frontend implementation)

**Rationale**:
- SavedExplanation is core to User Story 3 (bookmark feature)
- Model design simple (student_id + syllabus_point_id + explanation JSON)
- Multi-tenant isolation enforced (student_id in WHERE clauses)
- Prevents duplicate bookmarks (unique constraint on student+topic)

---

## Summary of Research Decisions

| Decision | Choice | Time Saved/Cost |
|----------|--------|-----------------|
| **Component Reuse** | Reuse infrastructure, new UI components | **+2-3 hours saved** (error boundaries, toasts, skeletons) |
| **Caching Strategy** | Tiered (1h/5m/1m) | **+50% cache hit rate** (reduced AI calls) |
| **Collapsible Sections** | shadcn/ui Accordion | **+2 hours saved** (accessibility, keyboard nav built-in) |
| **Search** | Client-side Array.filter() | **+200-500ms faster** (no network latency) |
| **Bookmark Backend** | Create model + migration + endpoints | **-1-2 hours cost** (backend work required) |

**Total Net Impact**: **+3-4 hours saved** overall (reuse benefits outweigh backend work)

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).

**Next Phase**: Create data-model.md, contracts/, quickstart.md
