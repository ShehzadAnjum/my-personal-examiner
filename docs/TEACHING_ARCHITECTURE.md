# Teaching System Architecture

**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles)
**Purpose**: Explain the relationship between /teach, /coaching, and resource bank integration

---

## 1. Overview: Two AI Teaching Roles

The system implements **two complementary AI teaching agents**, each designed for different learning scenarios:

### Teacher Agent (`/teach`)
- **Role**: Comprehensive concept explanations
- **Use Case**: Learning a new topic from scratch
- **Teaching Method**: Structured, academic, comprehensive
- **Output Format**:
  - Definition → Key Terms → Explanation → Examples → Diagrams → Worked Examples → Practice Problems
- **Backend**: `src/services/teaching_service.py` → `explain_concept()`
- **Analogy**: Like reading a textbook chapter written by a PhD professor

### Coach Agent (`/coaching`)
- **Role**: Personalized tutoring for struggling students
- **Use Case**: When you don't understand something after reading the teacher's explanation
- **Teaching Method**: Socratic questioning, adaptive, conversational
- **Output Format**:
  - Back-and-forth dialogue with diagnostic questions, hints, and targeted explanations
- **Backend**: `src/services/coaching_service.py` → `start_tutoring_session()` + `respond_to_coach()`
- **Analogy**: Like a 1-on-1 tutoring session where the tutor asks questions to find YOUR specific misconception

---

## 2. Learning Flow Example

### Scenario: Student wants to learn "Price Elasticity of Demand (PED)"

```
Step 1: TEACH (Comprehensive Learning)
  ↓
  Student → Opens /teach → Selects "9708.1.x - PED"
  ↓
  Teacher Agent → Returns structured explanation:
    - Definition: "PED measures responsiveness of quantity demanded to price changes"
    - Key Terms: Elastic, Inelastic, Unit Elastic
    - Explanation: Formula derivation, economic intuition
    - Examples: Luxury goods (elastic) vs necessities (inelastic)
    - Diagrams: Demand curves with different elasticities
    - Worked Examples: Calculate PED for specific scenarios
    - Practice Problems: 3 questions with model answers
  ↓
  Student reads explanation but still confused about "why PED is always negative"

Step 2: COACH (Targeted Tutoring)
  ↓
  Student → Opens /coaching → Types: "I don't understand why PED is always negative"
  ↓
  Coach Agent → Starts Socratic dialogue:
    Coach: "Let's start simple. What happens to quantity demanded when price increases?"
    Student: "It decreases"
    Coach: "Great! Now what does the formula PED = %ΔQd / %ΔP tell us?"
    Student: "The percentage change in quantity divided by percentage change in price"
    Coach: "Perfect. If price increases (+5%), and quantity decreases (-10%), what's the sign?"
    Student: "Oh! It's negative because we're dividing a negative by a positive!"
    Coach: "Exactly! The law of demand ensures the numerator and denominator always have opposite signs. That's why PED is always negative for normal goods."
  ↓
  Session ends with "resolved" outcome

Step 3: PRACTICE (Exam)
  ↓
  Student → Uses practice problems from Teacher Agent
  Student → Takes full exam (Examiner Agent - not yet implemented)
  Student → Gets marked (Marker Agent - not yet implemented)
```

**Key Difference**:
- **Teacher** = Broadcast (same explanation for everyone)
- **Coach** = Personalized (adapts to YOUR misconception)

---

## 3. Resource Bank Integration (Phase II)

### Current Implementation (Phase III - What you have now)
```
Student requests explanation for "PED"
  ↓
  Backend calls LLM API (Claude/GPT-4)
  ↓
  LLM generates explanation from training data
  ↓
  No local resources, no caching of good explanations
```

**Problems**:
- ❌ Every explanation generated from scratch
- ❌ Relies on LLM training data (may not match Cambridge exactly)
- ❌ Expensive (every request = API tokens)
- ❌ Slow (LLM inference time)
- ❌ No offline support

### Future Implementation (Phase II - Resource Bank Complete)
```
Student requests explanation for "9708.1.1 - Scarcity"
  ↓
1. CHECK RESOURCE BANK FIRST (local resources)
   backend/resources/subjects/9708/
     ├── syllabus/9708.1.1-scarcity.md ← Pre-written explanation
     ├── questions/9708_s22_qp_31.pdf ← Past papers
     └── cache/explanations/9708.1.1-v1.json ← Previous LLM responses
  ↓
2. If found in resource bank:
   → Inject into LLM prompt as PRIMARY source
   → LLM personalizes based on student history
   → Fast (cached) + Accurate (Cambridge materials)
  ↓
3. If NOT found:
   → LLM generates from training data (fallback)
   → Cache the good result for future students
  ↓
4. If LLM fails:
   → Return cached explanation (offline mode)
```

**Benefits**:
- ✅ **Accuracy**: Real Cambridge materials = 100% syllabus alignment
- ✅ **Speed**: Cached explanations = instant load (no LLM call)
- ✅ **Cost**: Fewer LLM tokens = lower API costs
- ✅ **Offline**: Works even if LLM API is down

### Resource Bank Structure (Phase II Architecture)
```
backend/resources/subjects/9708/
├── syllabus/
│   ├── 9708.1.1-scarcity.md              # Pre-written explanations
│   ├── 9708.1.2-opportunity-cost.md      # (Manual curation or AI-generated)
│   └── README.md                         # Template for other subjects
├── questions/
│   ├── raw/
│   │   ├── 9708_s22_qp_31.pdf            # Uploaded past papers
│   │   └── 9708_s22_ms_31.pdf            # Mark schemes
│   └── extracted/
│       ├── 9708_s22_qp_31_q1.json        # Parsed question + metadata
│       └── 9708_s22_qp_31_q2.json
├── mark_schemes/
│   └── 9708_marking_rubrics.json         # AO1/AO2/AO3 criteria
├── examiner_reports/
│   └── 9708_s22_examiner_report.pdf      # Common mistakes, good answers
└── cache/
    ├── explanations/
    │   └── 9708.1.1-scarcity-v1.json     # Cached LLM responses
    └── diagrams/
        └── ped-curve-elastic.svg         # Generated diagrams
```

### How Teacher/Coach Will Use Resource Bank

**Teacher Agent Prompt (with Resource Bank):**
```python
# Phase III (current - no resource bank)
prompt = f"Explain {concept_name} for Economics 9708 Cambridge A-Level"

# Phase II (with resource bank)
resource_bank_content = {
    "syllabus_explanation": load_resource("9708.1.1-scarcity.md"),
    "past_questions": get_questions(syllabus_code="9708.1.1"),
    "mark_schemes": get_mark_schemes(syllabus_code="9708.1.1"),
    "examiner_notes": get_examiner_reports(topic="scarcity")
}

prompt = f"""
Explain {concept_name} for Economics 9708 Cambridge A-Level.

REFERENCE MATERIALS FROM RESOURCE BANK:
1. Official syllabus description:
{resource_bank_content['syllabus_explanation']}

2. Past paper questions on this topic:
{resource_bank_content['past_questions']}

3. Cambridge mark schemes:
{resource_bank_content['mark_schemes']}

4. Examiner feedback (common mistakes):
{resource_bank_content['examiner_notes']}

Use these official Cambridge materials to create an accurate,
syllabus-aligned explanation. Reference specific past paper
questions as worked examples.
"""
```

**Coach Agent (with Resource Bank):**
```python
# Coach uses resource bank to identify common misconceptions
prompt = f"""
Student is struggling with: {struggle_description}

COMMON MISCONCEPTIONS FROM RESOURCE BANK:
{get_common_mistakes(topic)}

Use Socratic questioning to diagnose if student has one of
these known misconceptions.
"""
```

---

## 4. Syllabus Loading Optimization (IMPLEMENTED ✅)

### Problem: Slow Loading on Every Page Visit
**Before**:
```typescript
useEffect(() => {
  const points = await getSyllabusPoints('9708');  // ← Network call every time
  setSyllabusPoints(points);
}, []);
```

**Issues**:
- Fetches 50+ syllabus points from PostgreSQL on every page load
- Slow database query (joins subjects table)
- No offline support
- Wastes backend resources

### Solution: localStorage Cache with Background Sync (IMPLEMENTED)

**After** (implemented in `frontend/app/teach/page.tsx`):
```typescript
useEffect(() => {
  const cached = localStorage.getItem('syllabus_points_9708');

  if (cached && isFresh(cached)) {
    // INSTANT LOAD from cache (no loading spinner)
    setSyllabusPoints(JSON.parse(cached));
    console.log('📦 Loaded syllabus from cache (instant load)');
    return;
  }

  // Background sync if cache is stale
  const points = await getSyllabusPoints('9708');
  localStorage.setItem('syllabus_points_9708', JSON.stringify(points));
}, []);
```

**Benefits**:
- ⚡ **Instant load**: First load fetches from API, subsequent loads instant from cache
- 🔄 **Smart sync**: Cache valid for 24 hours, background sync if stale
- 📡 **Offline mode**: If API fails, uses stale cache (better than nothing)
- 💾 **Persistent**: Survives page refreshes, browser restarts

**Cache Management**:
- **Cache Duration**: 24 hours (configurable)
- **Cache Key**: `syllabus_points_9708` (subject-specific)
- **Version Tracking**: `syllabus_version` (increment when syllabus updated)
- **Clear Cache**: `localStorage.removeItem('syllabus_points_9708')` (manual or on syllabus update)

**Visual Indicator**:
When loading from cache, shows: `⚡ Loaded from cache (instant)` in sidebar header

**Future Enhancement (Phase II)**:
When Resource Bank is implemented, syllabus will be part of the resource bundle:
```
backend/resources/subjects/9708/syllabus.json
  ↓
  Downloaded once on subject activation
  ↓
  Cached in localStorage
  ↓
  Synced only when Cambridge publishes syllabus updates
```

---

## 5. Full Learning Cycle (Phase III Complete)

When all 6 agents are implemented, the full learning cycle will be:

```
1. PLAN (Planner Agent)
   Student → "Generate 30-day study plan for Economics 9708"
   Planner → Creates schedule with spaced repetition (SuperMemo 2)
   Output: Daily study plan with topics, review sessions

2. TEACH (Teacher Agent) ✅ IMPLEMENTED
   Student → Follows plan, learns "Scarcity" concept
   Teacher → Comprehensive explanation with examples
   Output: Structured learning materials

3. COACH (Coach Agent) ✅ IMPLEMENTED
   Student → "I don't understand opportunity cost"
   Coach → Socratic questioning to find misconception
   Output: Resolved understanding

4. EXAM (Examiner Agent)
   Student → "Generate practice exam on microeconomics"
   Examiner → Creates Cambridge-style exam (personalized)
   Output: 3-question exam matching student weaknesses

5. MARK (Marker Agent)
   Student → Submits exam answers
   Marker → Strict marking with AO1/AO2/AO3 criteria
   Output: Score + detailed feedback per criterion

6. REVIEW (Reviewer Agent)
   Student → Views marked exam
   Reviewer → Analyzes weaknesses, generates A* model answer
   Output: Improvement plan linked to Planner
```

**Integration with Resource Bank**:
- **Examiner** uses question bank (Phase II) to avoid repeating questions
- **Marker** uses mark schemes from resource bank for accuracy
- **Reviewer** identifies patterns across attempts, suggests targeted Coach sessions
- **Planner** uses review data to prioritize weak topics

---

## 6. Testing Your Optimizations

### Test Syllabus Caching
1. Open browser DevTools (F12) → Console
2. Navigate to http://localhost:3000/teach
3. First load:
   - See: `🔄 No cache found, fetching from API...`
   - See: `💾 Syllabus cached to localStorage`
   - Syllabus loads in ~1-2 seconds
4. Refresh page (F5):
   - See: `📦 Loaded syllabus from cache (instant load)`
   - See: `✅ Cache is fresh, skipping API call`
   - Syllabus loads instantly (<50ms)
   - UI shows: `⚡ Loaded from cache (instant)`
5. Wait 24 hours (or manually set old timestamp):
   - See: `⏰ Cache is stale, syncing in background...`
   - Syllabus loads instantly from cache, then updates silently

### Clear Cache (When Syllabus Updated)
Open browser console:
```javascript
localStorage.removeItem('syllabus_points_9708');
localStorage.removeItem('syllabus_points_9708_timestamp');
localStorage.removeItem('syllabus_version');
location.reload();
```

---

## 7. Summary Table

| Feature | Teacher Agent | Coach Agent | Resource Bank | Status |
|---------|---------------|-------------|---------------|--------|
| **Purpose** | Concept explanations | Personalized tutoring | Content repository | Teacher/Coach: ✅<br>Bank: Phase II |
| **Teaching Style** | Structured, comprehensive | Socratic, adaptive | Source materials | - |
| **When to Use** | Learning new topics | Struggling with concepts | Always (backend) | - |
| **Output** | Full explanation + examples | Dialogue session | Past papers, mark schemes | - |
| **LLM Usage** | High (generates full content) | Medium (conversational) | Low (caching) | - |
| **Offline Support** | ❌ (Phase II) | ❌ (Phase II) | ✅ (caching) | Partial |
| **Syllabus Caching** | ✅ IMPLEMENTED | N/A | ✅ IMPLEMENTED | Done |
| **Cambridge Accuracy** | Moderate (LLM training) | Moderate | High (real materials) | Improving |

---

## 8. Next Steps

### Immediate (Phase III Completion)
- [ ] Implement Examiner Agent (exam generation)
- [ ] Implement Marker Agent (strict marking)
- [ ] Implement Reviewer Agent (weakness analysis)
- [ ] Implement Planner Agent (study schedules)

### Phase II (Resource Bank)
- [ ] PDF extraction pipeline (past papers)
- [ ] Question bank database
- [ ] Mark scheme parsing
- [ ] Teacher/Coach integration with resource bank
- [ ] Offline mode with full resource bundle

### Phase IV (Frontend UI)
- [ ] Beautiful teaching interface
- [ ] Interactive diagrams (Mermaid rendering)
- [ ] Study plan dashboard
- [ ] Progress tracking visualizations

---

**Version**: 1.0
**Last Updated**: 2025-12-21
**Next Review**: After Phase II completion
