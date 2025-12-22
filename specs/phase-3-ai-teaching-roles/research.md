# Phase III Research: AI Teaching Roles

**Date**: 2025-12-20
**Purpose**: Resolve all "NEEDS CLARIFICATION" items from plan.md technical context
**Research Tasks**: 6 (LLM integration, SM-2, interleaving, confidence scoring, fallback, Economics rubrics)

---

## Decision 1: LLM Provider (Claude Sonnet 4.5)

**Chosen**: Anthropic Claude Sonnet 4.5 as primary LLM for all 6 agents

**Rationale**:
1. **Superior Reasoning**: Claude Sonnet 4.5 excels at structured reasoning (PhD-level explanations, strict marking)
2. **Long Context**: 200K token window supports full syllabus point explanations + examples
3. **Reliability**: Lower hallucination rate critical for educational accuracy
4. **Tool Use**: Native function calling for structured outputs (marking breakdown, confidence scores)
5. **Safety**: Built-in safeguards against generating harmful/incorrect educational content

**Configuration** (per agent from agent definitions):
- **Teacher**: Model=claude-sonnet-4-5, temp=0.3 (precise, pedagogically sound)
- **Coach**: Model=claude-sonnet-4-5, temp=0.5 (creative analogies, adaptive)
- **Examiner**: Model=claude-sonnet-4-5, temp=0.2 (deterministic question selection)
- **Marker**: Model=claude-sonnet-4-5, temp=0.1 (strict, consistent scoring)
- **Reviewer**: Model=claude-sonnet-4-5, temp=0.4 (empathetic, constructive)
- **Planner**: Model=gpt-4-turbo, temp=0.3 (SM-2 optimization) - **EXCEPTION** per agent definition

**API Patterns**:
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Standard completion pattern
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4000,
    temperature=0.3,
    system="You are a PhD-level Economics teacher...",
    messages=[
        {"role": "user", "content": "Explain price elasticity of demand"}
    ]
)
```

**Error Handling** (leads to Decision 5: Double Fallback):
- Rate Limits: 429 status → exponential backoff (1s, 2s, 4s)
- Timeouts: Set per-agent (Teacher: 10s, Coach: 5s, Marker: 10s)
- Overloaded: 529 status → circuit breaker pattern

**Alternatives Considered**:
- **OpenAI GPT-4 only**: Good but higher hallucination risk for educational content
- **Google Gemini only**: Newer, less proven for strict academic marking
- **Hybrid approach**: Complexity overhead not justified

**Implementation Files**:
- `backend/src/ai_integration/anthropic_client.py`
- `backend/src/ai_integration/prompt_templates/` (agent-specific system prompts)

---

## Decision 2: Spaced Repetition (SuperMemo 2)

**Chosen**: SuperMemo 2 (SM-2) algorithm for study schedule generation

**Rationale**:
1. **Proven Effectiveness**: Used by Anki (50M+ users), backed by 30+ years of research
2. **Simple Formulas**: Deterministic, testable, no ML black box
3. **Production-Ready**: Clear specification, many reference implementations
4. **Adaptive**: Easiness Factor (EF) adjusts per student performance
5. **Optimal for MVP**: More complex algorithms (SM-15+, FSRS) can come later

**Algorithm Specification** (from original SM-2 paper):

**Formula 1: Interval Calculation**
```
I(1) = 1 day
I(2) = 6 days
I(n) = I(n-1) * EF   for n ≥ 3

Where:
- I(n) = interval after nth repetition
- EF = easiness factor (1.3 to 2.5, default 2.5)
```

**Formula 2: Easiness Factor Update**
```
EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

Where:
- q = quality of recall (0-5 scale)
  - 5: Perfect recall
  - 4: Correct with hesitation
  - 3: Correct with difficulty
  - 2: Incorrect, but remembered
  - 1: Incorrect, forgot
  - 0: Complete blackout
- EF' = new easiness factor (min 1.3)
```

**Mapping Student Performance to Quality (q)**:
```python
def performance_to_quality(marks_percentage: float) -> int:
    """Map exam performance to SM-2 quality rating."""
    if marks_percentage >= 90:   return 5  # A* - perfect
    if marks_percentage >= 80:   return 4  # A - good recall
    if marks_percentage >= 70:   return 3  # B - correct with difficulty
    if marks_percentage >= 60:   return 2  # C - partial recall
    if marks_percentage >= 50:   return 1  # D - minimal recall
    return 0  # E/U - forgot
```

**Production Edge Cases**:
1. **EF Floor**: Never allow EF < 1.3 (prevents infinite loops)
2. **Missed Reviews**: If student misses scheduled review, reset interval to I(1)
3. **Perfect Streak**: Cap EF at 2.5 (diminishing returns beyond)
4. **Exam Proximity**: Override SM-2 intervals if exam date <7 days (daily reviews)

**Database Storage**:
```sql
-- study_plans.easiness_factors JSONB
{
  "9708.1.1": 2.5,  -- Scarcity and Choice (initial)
  "9708.2.1": 2.2,  -- Supply and Demand (adjusted after attempt)
  "9708.3.1": 2.8   -- Elasticity (performing well)
}

-- study_plans.schedule JSONB
[
  {
    "day": 1,
    "topics": ["9708.1.1"],
    "interval": 1,
    "activities": ["study", "practice"],
    "ef": 2.5
  },
  {
    "day": 4,
    "topics": ["9708.1.1"],
    "interval": 3,
    "activities": ["review"],
    "ef": 2.5
  }
]
```

**Alternatives Considered**:
- **Simple Fixed Intervals** (1, 3, 7, 14, 30): Too rigid, doesn't adapt to student
- **FSRS (Free Spaced Repetition Scheduler)**: ML-based, complex, harder to debug
- **SM-15+**: Overengineered for v1.0, incremental gains vs. complexity cost

**Implementation Files**:
- `backend/src/algorithms/supermemo2.py` (core algorithm)
- `backend/src/services/planning_service.py` (uses SM-2)
- `backend/tests/unit/test_supermemo2.py` (validate formulas)

**References**:
- Original Paper: Wozniak, P. A. (1990). "Algorithm SM-2"
- Anki Implementation: https://github.com/ankitects/anki/blob/main/pylib/anki/scheduler/v2.py

---

## Decision 3: Contextual Interleaving Strategy

**Chosen**: Contextual interleaving (mix related topics within sessions, max 3 topics/day)

**Rationale**:
1. **Cognitive Science**: Interleaving improves discrimination between similar concepts
2. **Contextual Grouping**: Related topics share mental models (e.g., elasticity → demand → supply)
3. **Cognitive Load Management**: Max 3 topics prevents overwhelm
4. **Better than Blocking**: Studies show 30% improvement in long-term retention
5. **Better than Random**: Contextual grouping provides coherence

**Algorithm Specification**:

**Step 1: Determine Topic Relatedness**
```python
def topics_are_related(topic1: str, topic2: str, syllabus_data: dict) -> bool:
    """Check if two syllabus points are related."""
    # Same section (e.g., both under 9708.1.x)
    section1 = topic1.rsplit('.', 1)[0]  # "9708.1.1" → "9708.1"
    section2 = topic2.rsplit('.', 1)[0]

    if section1 == section2:
        return True

    # Explicitly tagged as related in syllabus metadata
    if topic2 in syllabus_data[topic1].get('related_topics', []):
        return True

    return False
```

**Step 2: Create Daily Topic Clusters**
```python
def create_daily_clusters(topics: List[str], max_per_day: int = 3) -> List[List[str]]:
    """Group related topics for daily study sessions."""
    clusters = []
    used = set()

    for topic in topics:
        if topic in used:
            continue

        # Start new cluster
        cluster = [topic]
        used.add(topic)

        # Add up to max_per_day - 1 related topics
        for candidate in topics:
            if candidate in used:
                continue
            if len(cluster) >= max_per_day:
                break
            if topics_are_related(topic, candidate, syllabus_data):
                cluster.append(candidate)
                used.add(candidate)

        clusters.append(cluster)

    return clusters
```

**Step 3: Interleaving Pattern (A→B→A→C→B→C)**
```python
def generate_practice_sequence(cluster: List[str]) -> List[str]:
    """Create interleaved practice sequence for a cluster of topics."""
    # Example cluster: ["Demand", "Supply", "Elasticity"]
    # Output: [D, S, D, E, S, E, D, S, E]

    practice_sets = []
    rounds = 3  # Each topic practiced 3 times

    for round in range(rounds):
        for topic in cluster:
            practice_sets.append(topic)

    # Shuffle with constraint: same topic never appears consecutively
    interleaved = []
    remaining = practice_sets.copy()
    last_topic = None

    while remaining:
        # Find next topic different from last
        candidates = [t for t in remaining if t != last_topic]
        if not candidates:
            candidates = remaining  # Forced repetition if only one topic left

        next_topic = candidates[0]
        interleaved.append(next_topic)
        remaining.remove(next_topic)
        last_topic = next_topic

    return interleaved
```

**Economics 9708 Example**:
```python
# Week 1 schedule with contextual interleaving
week_1_plan = [
    {
        "day": 1,
        "cluster": ["9708.1.1 Scarcity", "9708.1.2 Opportunity Cost"],
        "practice_sequence": ["Scarcity", "Opp Cost", "Scarcity", "Opp Cost"],
        "rationale": "Related: Both under basic economic problem (9708.1.x)"
    },
    {
        "day": 2,
        "cluster": ["9708.2.1 Demand", "9708.2.2 Supply", "9708.2.3 Equilibrium"],
        "practice_sequence": ["D", "S", "D", "Eq", "S", "Eq", "D", "S"],
        "rationale": "Related: All under market theory (9708.2.x)"
    }
]
```

**Constraints**:
- Max 3 topics per day (cognitive load limit)
- Topics must be related (same section or explicitly tagged)
- Practice sets use A→B→A→C→B→C pattern (no consecutive repetitions)

**Alternatives Considered**:
- **Strict Alternation** (A→B→C→A→B→C→...): Too rigid, doesn't group related topics
- **Random Interleaving**: No cognitive coherence, overwhelming
- **Blocked-then-Interleaved**: Delays benefits of interleaving

**Implementation Files**:
- `backend/src/algorithms/contextual_interleaving.py`
- `backend/src/services/planning_service.py` (integrates with SM-2)

**References**:
- Rohrer, D., & Taylor, K. (2007). "The shuffling of mathematics practice problems improves learning."
- Birnbaum, M. S., et al. (2013). "Why interleaving enhances inductive learning"

---

## Decision 4: Marking Confidence Scoring

**Chosen**: Rule-based confidence scoring (0-100) with <70% threshold for manual review

**Rationale**:
1. **No Logprobs Access**: Anthropic API doesn't expose token probabilities
2. **Heuristic-Based**: Use multiple signals to estimate confidence
3. **Conservative Threshold**: 70% ensures only high-confidence marks auto-pass
4. **Production Safety**: Manual review queue prevents incorrect feedback

**Confidence Calculation Algorithm**:

```python
def calculate_confidence(
    marking_result: dict,
    question: Question,
    student_answer: str
) -> int:
    """Calculate 0-100 confidence score for marking result."""

    confidence = 100  # Start optimistic

    # Signal 1: Answer Length Mismatch
    expected_words = question.max_marks * 20  # ~20 words per mark
    actual_words = len(student_answer.split())
    length_ratio = actual_words / expected_words

    if length_ratio < 0.3 or length_ratio > 3.0:
        confidence -= 20  # Very short or very long answers are ambiguous
    elif length_ratio < 0.6 or length_ratio > 1.5:
        confidence -= 10

    # Signal 2: Mark Scheme Coverage
    required_points = len(question.marking_scheme['required_points'])
    identified_points = len(marking_result['points_awarded'])
    coverage = identified_points / required_points if required_points > 0 else 1.0

    if coverage < 0.5:
        confidence -= 25  # Missing major points
    elif coverage < 0.8:
        confidence -= 10

    # Signal 3: Partial Marks (Edge Cases)
    if marking_result['marks_awarded'] not in [0, question.max_marks]:
        # Partial marks are inherently less certain
        confidence -= 15

    # Signal 4: Ambiguous Language Detection
    ambiguous_phrases = [
        "somewhat", "possibly", "might", "could be", "unclear",
        "difficult to determine", "hard to say"
    ]
    if any(phrase in marking_result['feedback'].lower() for phrase in ambiguous_phrases):
        confidence -= 20

    # Signal 5: AO3 Evaluation Questions (Inherently Subjective)
    if question.requires_ao3:
        confidence -= 10  # Evaluation is harder to mark confidently

    # Signal 6: Borderline Marks
    percentage = (marking_result['marks_awarded'] / question.max_marks) * 100
    if 48 <= percentage <= 52:  # Near pass/fail boundary
        confidence -= 15
    elif 68 <= percentage <= 72:  # Near grade boundaries
        confidence -= 10

    # Floor at 0
    return max(0, confidence)
```

**Manual Review Queue**:
```python
# In marking_service.py
result = mark_answer(question, student_answer)
confidence = calculate_confidence(result, question, student_answer)

if confidence < 70:
    result['needs_review'] = True
    queue_for_manual_review(result)  # Human examiner review
else:
    result['needs_review'] = False
```

**Confidence Calibration** (post-deployment):
```python
# Track confidence vs. actual accuracy
# If confidence=80 but human reviewers disagree 30% of the time → recalibrate
def calibrate_confidence_threshold(review_history: List[dict]):
    """Adjust threshold based on human review data."""
    for conf_level in range(50, 95, 5):
        subset = [r for r in review_history if r['confidence'] >= conf_level]
        accuracy = sum(r['human_agreed'] for r in subset) / len(subset)

        if accuracy >= 0.85:  # 85% agreement target
            return conf_level

    return 70  # Default conservative threshold
```

**Alternatives Considered**:
- **LLM Self-Assessment**: Ask Claude "How confident are you?" → unreliable, not calibrated
- **Ensemble Scoring**: Multiple LLM calls, check agreement → 3x cost, not justified for v1.0
- **Always Manual Review**: Defeats automation purpose

**Implementation Files**:
- `backend/src/services/marking_service.py` (uses confidence scoring)
- `.claude/skills/confidence-scoring.md` (algorithm documentation)

---

## Decision 5: Double Fallback Strategy

**Chosen**: Retry with exponential backoff → Cached responses → Alternative LLM prompt

**Rationale**:
1. **Production Resilience**: Claude outages shouldn't block students
2. **Cost Optimization**: Cache avoids redundant API calls for common topics
3. **User Experience**: Graceful degradation vs. hard failures
4. **Manual Escalation**: For critical services (marking), prompt user to try alternative

**Fallback Orchestration**:

```python
async def llm_request_with_fallback(
    prompt: str,
    agent_type: str,
    cache_key: Optional[str] = None,
    max_retries: int = 3
) -> LLMResponse:
    """Execute LLM request with double fallback strategy."""

    # LAYER 1: Retry with Exponential Backoff
    backoff_delays = [1, 2, 4]  # seconds
    last_error = None

    for attempt in range(max_retries):
        try:
            response = await anthropic_client.complete(prompt)
            return LLMResponse(content=response, source="claude")

        except RateLimitError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff_delays[attempt])
                continue
            last_error = e

        except TimeoutError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff_delays[attempt])
                continue
            last_error = e

    # LAYER 2: Cached Responses (for Teacher/Coach only)
    if cache_key and agent_type in ["teacher", "coach"]:
        cached = await redis_client.get(cache_key)
        if cached:
            log_fallback_event("cache", agent_type)
            return LLMResponse(content=cached, source="cache")

    # LAYER 3: Alternative LLM Prompt
    if agent_type in ["teacher", "coach", "reviewer"]:
        # Non-critical services: try alternative LLM
        try:
            response = await gemini_client.complete(prompt)
            log_fallback_event("gemini", agent_type)
            return LLMResponse(content=response, source="gemini")
        except Exception as e:
            last_error = e

    # FINAL: Prompt user to try alternative LLM
    if agent_type in ["marker"]:
        # Critical service: don't auto-fallback, inform user
        raise LLMServiceUnavailableError(
            f"Claude Sonnet unavailable. Please try again or use alternative LLM (Gemini/GPT-4).",
            original_error=last_error
        )

    # Default error
    raise LLMServiceUnavailableError(
        f"All LLM providers unavailable for {agent_type}",
        original_error=last_error
    )
```

**Caching Strategy**:
```python
# Cache common topic explanations (Teacher Agent)
def generate_cache_key(syllabus_point_id: str) -> str:
    return f"teaching:explanation:{syllabus_point_id}"

# Cache hit rate target: >60% (most students study same topics)
# Cache TTL: 7 days (syllabus content stable)
# Cache invalidation: Manual trigger if syllabus updates
```

**Circuit Breaker Pattern** (prevent cascade failures):
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failures = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Too many failures, circuit open")

        try:
            result = await func(*args, **kwargs)
            self.reset()
            return result

        except Exception as e:
            self.record_failure()
            raise e

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

    def reset(self):
        self.failures = 0
        self.state = "CLOSED"
```

**Alternatives Considered**:
- **No Fallback**: Unacceptable for production v1.0
- **Single Fallback** (retry only): Doesn't handle extended outages
- **Always Use Multiple LLMs**: 2-3x cost, not justified

**Implementation Files**:
- `backend/src/ai_integration/llm_fallback.py`
- `backend/src/ai_integration/circuit_breaker.py`
- `backend/tests/unit/test_llm_fallback.py`

---

## Decision 6: Economics 9708 Marking Rubrics

**Chosen**: Encode Cambridge mark schemes as structured JSONB with AO1/AO2/AO3 breakdown

**Rationale**:
1. **Faithful to Cambridge**: Direct encoding of official mark schemes
2. **Structured Data**: Enables automated validation and scoring
3. **Extensible**: Easy to add new questions without code changes
4. **Testable**: Can verify against sample papers with known marks

**Mark Scheme Structure** (JSONB encoding):

```json
{
  "max_marks": 12,
  "assessment_objectives": {
    "AO1": 4,
    "AO2": 4,
    "AO3": 4
  },
  "required_points": [
    {
      "id": "AO1-1",
      "text": "Define price elasticity of demand as responsiveness of quantity demanded to price changes",
      "marks": 2,
      "type": "definition"
    },
    {
      "id": "AO1-2",
      "text": "State formula: PED = (% change in Qd) / (% change in P)",
      "marks": 2,
      "type": "formula"
    },
    {
      "id": "AO2-1",
      "text": "Apply concept to real-world example (e.g., luxury vs. necessity goods)",
      "marks": 2,
      "type": "application"
    },
    {
      "id": "AO2-2",
      "text": "Explain why PED varies along demand curve",
      "marks": 2,
      "type": "analysis"
    },
    {
      "id": "AO3-1",
      "text": "Evaluate significance of PED for business pricing decisions",
      "marks": 2,
      "type": "evaluation"
    },
    {
      "id": "AO3-2",
      "text": "Consider limitations of PED (time lag, ceteris paribus assumption)",
      "marks": 2,
      "type": "evaluation"
    }
  ],
  "mark_allocation": {
    "L4": "10-12 marks: Sophisticated, perceptive, balanced evaluation",
    "L3": "7-9 marks: Good analysis, competent application, some evaluation",
    "L2": "4-6 marks: Limited analysis, basic application, little evaluation",
    "L1": "1-3 marks: Minimal knowledge, little/no application or evaluation"
  }
}
```

**Marking Algorithm**:
```python
def mark_economics_answer(
    student_answer: str,
    mark_scheme: dict,
    question_text: str
) -> MarkingResult:
    """Mark Economics answer using encoded Cambridge mark scheme."""

    # Step 1: Extract student's points using LLM
    prompt = f"""
You are a Cambridge Economics examiner. Extract the key points from this student answer:

Question: {question_text}

Student Answer: {student_answer}

Mark Scheme Required Points:
{json.dumps(mark_scheme['required_points'], indent=2)}

For each required point, determine:
1. Is it present in the student's answer? (yes/no)
2. Quality of explanation (excellent/good/weak/missing)
3. Specific quote from student answer (if present)

Return JSON:
{{
  "points_awarded": [
    {{"point_id": "AO1-1", "present": true, "quality": "good", "quote": "..."}}
  ]
}}
"""

    extraction = anthropic_client.complete(prompt)
    points = json.loads(extraction)

    # Step 2: Calculate marks per assessment objective
    ao_scores = {"AO1": 0, "AO2": 0, "AO3": 0}

    for awarded in points['points_awarded']:
        if not awarded['present']:
            continue

        point = next(p for p in mark_scheme['required_points'] if p['id'] == awarded['point_id'])
        ao = awarded['point_id'].split('-')[0]  # "AO1-1" → "AO1"

        # Quality-based mark allocation
        if awarded['quality'] == 'excellent':
            ao_scores[ao] += point['marks']
        elif awarded['quality'] == 'good':
            ao_scores[ao] += point['marks'] * 0.75
        elif awarded['quality'] == 'weak':
            ao_scores[ao] += point['marks'] * 0.5

    # Step 3: Apply mark scheme caps
    for ao in ao_scores:
        ao_scores[ao] = min(ao_scores[ao], mark_scheme['assessment_objectives'][ao])

    total_marks = sum(ao_scores.values())

    # Step 4: Determine level (L1/L2/L3/L4)
    percentage = (total_marks / mark_scheme['max_marks']) * 100
    if percentage >= 83:
        level = "L4"
    elif percentage >= 58:
        level = "L3"
    elif percentage >= 33:
        level = "L2"
    else:
        level = "L1"

    return MarkingResult(
        marks_awarded=round(total_marks),
        max_marks=mark_scheme['max_marks'],
        ao1_score=round(ao_scores['AO1']),
        ao2_score=round(ao_scores['AO2']),
        ao3_score=round(ao_scores['AO3']),
        level=level,
        points_awarded=points['points_awarded']
    )
```

**Cambridge Mark Scheme Sources**:
- Official Cambridge mark schemes: https://www.cambridgeinternational.org/exam-administration/admin-support/samples-and-specimens/
- Examiner reports (for rationale): Published annually per session
- Specimen papers with marking guidance

**Validation Strategy**:
```python
# Test against 10 sample questions with official marks
test_cases = [
    {
        "question": "Explain the concept of price elasticity of demand. [12]",
        "student_answer": "...",
        "official_marks": 10,
        "official_breakdown": {"AO1": 4, "AO2": 4, "AO3": 2}
    }
]

for case in test_cases:
    result = mark_economics_answer(case['student_answer'], mark_scheme, case['question'])

    # Allow ±2 marks tolerance (Cambridge guideline)
    assert abs(result.marks_awarded - case['official_marks']) <= 2

    # AO breakdown should match within ±1 mark per objective
    for ao in ['AO1', 'AO2', 'AO3']:
        assert abs(result[f'{ao.lower()}_score'] - case['official_breakdown'][ao]) <= 1
```

**Alternatives Considered**:
- **Unstructured Prompting**: "Mark this answer" → unreliable, not testable
- **Keyword Matching**: Too simplistic, misses context and analysis depth
- **ML Classifier**: Requires large training set, not interpretable

**Implementation Files**:
- `backend/src/services/marking_service.py` (Economics marker)
- `backend/src/schemas/mark_scheme_schema.py` (JSONB validation)

---

## Summary of Technical Decisions

| Decision | Technology Chosen | Rationale |
|----------|-------------------|-----------|
| **LLM Provider** | Claude Sonnet 4.5 (primary), GPT-4/Gemini (fallback) | Superior reasoning, long context, educational safety |
| **Spaced Repetition** | SuperMemo 2 (SM-2) | Proven algorithm, simple formulas, production-ready |
| **Interleaving** | Contextual (related topics, max 3/day) | Cognitive coherence + load management |
| **Confidence Scoring** | Rule-based heuristics, <70% manual review | No logprobs access, conservative threshold |
| **Fallback Strategy** | Retry → Cache → Alt LLM → User prompt | Production resilience, graceful degradation |
| **Marking Rubrics** | Structured JSONB encoding of Cambridge schemes | Testable, faithful to Cambridge, extensible |

---

## Implementation Checklist

- [ ] Create `anthropic_client.py` with retry logic
- [ ] Create `supermemo2.py` with SM-2 formulas + unit tests
- [ ] Create `contextual_interleaving.py` with topic clustering
- [ ] Create `confidence_scoring.py` with heuristic calculator
- [ ] Create `llm_fallback.py` with double fallback orchestrator
- [ ] Create `marking_service.py` with Economics rubric engine
- [ ] Validate SM-2 algorithm against reference implementation
- [ ] Validate marking accuracy vs. 10 Cambridge sample questions (≥85% agreement)
- [ ] Create ADRs for SM-2, fallback, confidence decisions
- [ ] Update `research.md` → COMPLETE

---

**Research Status**: COMPLETE
**Next Phase**: Phase 1 (Data Model, Contracts, Quickstart)
**Date**: 2025-12-20
