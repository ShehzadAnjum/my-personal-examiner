# Skill Evolution Log

## Purpose
Track new patterns, solutions, and learnings discovered during development to evolve our skill library.

## Format
```markdown
### [Date] [Session/Feature] - [Skill Name]

**What we learned:**
[Description of new pattern/solution]

**Where it was used:**
[File paths and context]

**Should update:**
[Which skill file(s) should incorporate this]

**Code example:**
```[language]
[Minimal example demonstrating the pattern]
```
```

---

## 2025-12-25 | 005-teaching-page (US1-US3) - Multiple Learnings

### TanStack Query Optimistic Updates with Rollback

**What we learned:**
Pattern for implementing optimistic UI updates with automatic rollback on error. Critical for instant user feedback in bookmark/save operations.

**Where it was used:**
- `frontend/lib/hooks/useBookmark.tsx` (useSaveBookmark, useRemoveBookmark)
- SavedExplanationsList component delete operations

**Should update:**
- Create NEW: `.claude/skills/tanstack-query-patterns/SKILL.md`
- Section: "Optimistic Updates with Error Rollback"

**Code example:**
```typescript
export function useSaveBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ syllabusPointId }) =>
      teachingApi.saveExplanation(syllabusPointId),

    // Optimistic update: Add to cache immediately
    onMutate: async ({ syllabusPointId, explanation }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['savedExplanations'] });

      // Snapshot for rollback
      const previousSaved = queryClient.getQueryData(['savedExplanations']);

      // Optimistically update
      queryClient.setQueryData(['savedExplanations'], (old = []) => [
        ...old,
        { id: 'temp-' + Date.now(), syllabus_point_id: syllabusPointId, ...}
      ]);

      return { previousSaved }; // Return context for rollback
    },

    // On error: Rollback optimistic update
    onError: (error, variables, context) => {
      if (context?.previousSaved) {
        queryClient.setQueryData(['savedExplanations'], context.previousSaved);
      }
    },

    // On success: Invalidate to fetch fresh data
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedExplanations'] });
    },
  });
}
```

**Benefits:**
- Instant UI feedback (no loading spinner needed)
- Automatic error recovery
- Cache consistency maintained

---

### Hybrid Caching: localStorage + TanStack Query

**What we learned:**
Combine TanStack Query for API state (pointers, metadata) with localStorage for content cache (large JSON payloads) to reduce API calls and enable offline access.

**Where it was used:**
- Explanation page: localStorage for TopicExplanation content
- Saved page: TanStack Query for bookmark pointers, localStorage for explanation preview

**Should update:**
- Create NEW: `.claude/skills/client-side-caching-patterns/SKILL.md`
- Section: "Pointer-Based Architecture with Content Cache"

**Code example:**
```typescript
// Architecture: Pointer-based bookmarks

// Backend: Only store metadata (pointer)
interface SavedExplanation {
  id: string;
  student_id: string;
  syllabus_point_id: string; // Pointer to content
  date_saved: string;
  // NO explanation_content field (stored in localStorage)
}

// Frontend: Load content from localStorage
const loadExplanationFromCache = (syllabusPointId: string): TopicExplanation | null => {
  try {
    const cached = localStorage.getItem(`explanation_${syllabusPointId}`);
    return cached ? JSON.parse(cached) : null;
  } catch (err) {
    console.error('Failed to load from cache:', err);
    return null;
  }
};

// Use TanStack Query for pointers, localStorage for content
const { data: bookmarks } = useSavedExplanations(); // Pointers from API
const enriched = bookmarks.map(b => ({
  ...b,
  explanation: loadExplanationFromCache(b.syllabus_point_id), // Content from cache
  hasCachedContent: !!loadExplanationFromCache(b.syllabus_point_id),
}));
```

**Benefits:**
- Reduced database size (no large JSON in DB)
- Offline access to viewed explanations
- Fast page loads (no API call for content)
- Bookmark sync across devices (pointers in DB)

---

### SQLModel Serialization Fix: Manual Dict Conversion

**What we learned:**
SQLModel 0.0.27 with Pydantic 2.x doesn't expose `.model_dump()` on table model instances. FastAPI response validation requires manual dict conversion.

**Where it was used:**
- `backend/src/routes/questions.py` (get_question endpoint)
- `backend/src/services/search_service.py` (search_questions, search_mark_schemes)

**Should update:**
- Update: `.claude/skills/sqlmodel-database-schema-design/SKILL.md`
- Section: "Common Pitfalls" → Add "Serialization for API Responses"

**Code example:**
```python
# ❌ WRONG: This fails with AttributeError
@router.get("/{question_id}")
async def get_question(question_id: UUID, db: Session = Depends(get_session)) -> dict:
    question = db.get(Question, question_id)
    return question.model_dump()  # AttributeError: 'Question' object has no attribute 'model_dump'

# ✅ CORRECT: Manual dict conversion
@router.get("/{question_id}")
async def get_question(question_id: UUID, db: Session = Depends(get_session)) -> dict:
    question = db.get(Question, question_id)

    # Convert to dict manually to avoid serialization issues
    return {
        "id": str(question.id),
        "subject_id": str(question.subject_id),
        "question_text": question.question_text,
        "max_marks": question.max_marks,
        # ... all other fields
        "created_at": question.created_at.isoformat() if question.created_at else None,
    }
```

**Why it happens:**
- SQLModel table models (with `table=True`) don't inherit Pydantic's `.model_dump()`
- FastAPI can't auto-serialize table models with UUIDs and datetime fields
- Manual conversion ensures consistent field serialization

---

### Pytest Mock Fix: scalar_one → one, scalars → all

**What we learned:**
SQLModel's `Session.exec()` returns result objects with different method names than raw SQLAlchemy. Mocks must match actual service implementation.

**Where it was used:**
- `backend/tests/unit/test_search_service.py` (pagination tests, filtering tests)

**Should update:**
- Update: `.claude/skills/pytest-testing-patterns/SKILL.md`
- Section: "Mocking Database Queries" → Add "SQLModel Session.exec() Mocking"

**Code example:**
```python
# ❌ WRONG: Mocking with SQLAlchemy method names
mocker.patch.object(mock_db, "exec", side_effect=[
    mocker.MagicMock(scalar_one=lambda: 50),  # Wrong for SQLModel
    mocker.MagicMock(scalars=lambda: [...]),  # Wrong for SQLModel
])

# ✅ CORRECT: Mocking with SQLModel method names
mocker.patch.object(mock_db, "exec", side_effect=[
    mocker.MagicMock(one=lambda: 50),        # Correct for count queries
    mocker.MagicMock(all=lambda: [...]),     # Correct for result queries
])

# Service implementation (must match mock):
count = self.db.exec(count_stmt).one()      # Uses .one() not .scalar_one()
questions = self.db.exec(stmt).all()        # Uses .all() not .scalars()
```

**Key insight:**
- SQLModel wraps SQLAlchemy with different method names
- Check actual service code to know which methods to mock
- Don't assume SQLAlchemy patterns apply to SQLModel

---

### Component Architecture: Separate List from Page

**What we learned:**
For better code organization and reusability, separate list components from page routes. Page handles layout/navigation, list component handles data fetching and rendering.

**Where it was used:**
- Refactored `/teaching/saved/page.tsx` (250+ lines → 53 lines)
- Created `SavedExplanationsList.tsx` (256 lines, reusable)

**Should update:**
- Update: `.claude/skills/shadcn-ui-components/SKILL.md`
- Section: "Component Composition Patterns" → Add "Page vs List Component Separation"

**Code example:**
```typescript
// ❌ BEFORE: Everything in page component (250+ lines)
export default function SavedPage() {
  const [saved, setSaved] = useState([]);
  const [loading, setLoading] = useState(true);
  // ... 200+ lines of data fetching, rendering, error handling
}

// ✅ AFTER: Separation of concerns

// Page: Layout and navigation only (53 lines)
export default function SavedPage() {
  return (
    <div className="container">
      <BackButton />
      <Header />
      <SavedExplanationsList /> {/* Reusable component */}
    </div>
  );
}

// List Component: Data fetching and rendering (256 lines, reusable)
export function SavedExplanationsList() {
  const { data, isLoading, error } = useSavedExplanations(); // TanStack Query
  const { mutate: removeBookmark } = useRemoveBookmark();

  // All business logic encapsulated
  // Can be reused in other contexts (dashboard widget, sidebar, etc.)
}
```

**Benefits:**
- Page components stay small (<100 lines)
- List components are testable in isolation
- Reusable across different pages/contexts
- Clear separation: layout vs business logic

---

## Next Actions

**Skills to Create:**
1. `.claude/skills/tanstack-query-patterns/SKILL.md`
   - Optimistic updates
   - Cache invalidation strategies
   - Error handling patterns

2. `.claude/skills/client-side-caching-patterns/SKILL.md`
   - Hybrid localStorage + API caching
   - Pointer-based architecture
   - Cache invalidation timing

**Skills to Update:**
1. `.claude/skills/sqlmodel-database-schema-design/SKILL.md`
   - Add: Serialization pitfalls section
   - Add: FastAPI response dict conversion pattern

2. `.claude/skills/pytest-testing-patterns/SKILL.md`
   - Add: SQLModel Session.exec() mocking
   - Add: Method name differences (one vs scalar_one, all vs scalars)

3. `.claude/skills/shadcn-ui-components/SKILL.md`
   - Add: Component composition patterns
   - Add: Page vs List component separation

**Process Improvement:**
- Add reminder to check `.claude/agents/` and `.claude/skills/` before starting tasks
- Create checklist: "Did I announce the agent/skill I'm using?"
- After session: Review skill-evolution-log.md and update skills

---

## Template for Future Entries

```markdown
### [YYYY-MM-DD] [Feature] - [Pattern Name]

**What we learned:**
[Description]

**Where it was used:**
[File paths]

**Should update:**
[Skill file(s)]

**Code example:**
```[language]
[Code]
```

**Benefits/Insights:**
[Why this matters]
```
