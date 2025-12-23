# Phase III Quickstart Guide: Testing AI Teaching Roles

**Purpose**: Step-by-step guide to test all 6 AI teaching agents
**Prerequisites**: Phase II complete, database seeded, API running
**Estimated Time**: 30 minutes

---

## Prerequisites

### 1. Environment Setup

```bash
# Set environment variables in backend/.env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...  # Fallback
GEMINI_API_KEY=...     # Fallback

DATABASE_URL=postgresql://user:pass@localhost:5432/examiner

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

### 2. Database Migrations

```bash
cd backend
alembic upgrade head  # Applies migrations 003, 004, 005
```

### 3. Start API Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 4. Get Authentication Token

```bash
# Register or login
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test Student"
  }'

# Save the returned JWT token
export TOKEN="<jwt_token_from_response>"
```

---

## Agent 1: Teacher Agent

### Test Concept Explanation

```bash
curl -X POST http://localhost:8000/api/teaching/explain-concept \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "syllabus_point_id": "<UUID_OF_SYLLABUS_POINT>",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response

```json
{
  "explanation_id": "...",
  "syllabus_point_code": "9708.1.1",
  "topic": "Scarcity and Choice",
  "explanation": "Scarcity is the fundamental economic problem...",
  "key_concepts": ["Scarcity", "Opportunity Cost"],
  "examples": [
    {
      "title": "Time Scarcity",
      "description": "Students choosing between studying Economics or Mathematics",
      "relevance": "Demonstrates opportunity cost"
    }
  ],
  "diagrams": [
    {
      "type": "mermaid",
      "content": "graph TD\nA[Limited Resources] --> B[Scarcity]",
      "caption": "The Economic Problem Flow"
    }
  ],
  "practice_problems": [...],
  "estimated_study_time": 45
}
```

### Validation Checklist

- [ ] Explanation is PhD-level (precise, comprehensive)
- [ ] Includes real-world examples
- [ ] Diagrams are present (Mermaid or ASCII)
- [ ] Practice problems provided
- [ ] 100% aligned with Cambridge syllabus

---

## Agent 2: Coach Agent

### Test Tutoring Session

**Step 1: Start Session**

```bash
curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "topic": "price elasticity of demand",
    "struggle_description": "I dont understand why PED is negative",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

**Expected Response**:

```json
{
  "session_id": "<SESSION_UUID>",
  "first_question": "Let's start simple: Can you explain what happens to the quantity demanded when price increases?",
  "session_status": "in_progress",
  "estimated_duration": 15
}
```

**Step 2: Respond to Coach**

```bash
curl -X POST http://localhost:8000/api/coaching/session/<SESSION_UUID>/respond \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "student_answer": "It decreases",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

**Expected Response** (next Socratic question):

```json
{
  "coach_response": "Exactly! That's the inverse relationship. Now, what determines how MUCH it decreases?",
  "session_status": "in_progress",
  "next_question": "What determines how MUCH quantity demanded decreases?"
}
```

### Validation Checklist

- [ ] Coach asks Socratic questions (not direct answers)
- [ ] Questions diagnose misconceptions
- [ ] Adaptive based on student responses
- [ ] Session tracked in coaching_sessions table

---

## Agent 3: Marker Agent

### Test Single Answer Marking

```bash
curl -X POST http://localhost:8000/api/marking/mark-answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "question_id": "<QUESTION_UUID>",
    "student_answer": "Demand is when people want something. It goes down when price goes up.",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response

```json
{
  "marks_awarded": 3,
  "max_marks": 12,
  "percentage": 25,
  "ao1_score": 1,
  "ao1_max": 4,
  "ao2_score": 1,
  "ao2_max": 4,
  "ao3_score": 1,
  "ao3_max": 4,
  "level": "L1",
  "errors": [
    {
      "category": "AO1 - Imprecise Definition",
      "description": "Defined demand as 'what people want' instead of 'quantity willing and able to purchase'",
      "marks_lost": 3
    },
    {
      "category": "AO1 - Missing Ceteris Paribus",
      "description": "No mention of ceteris paribus assumption",
      "marks_lost": 2
    }
  ],
  "confidence_score": 85,
  "needs_review": false,
  "feedback": "Basic understanding shown, but definition lacks precision. Include ceteris paribus..."
}
```

### Validation Checklist

- [ ] Marks awarded are strict (PhD-level)
- [ ] AO1/AO2/AO3 breakdown provided
- [ ] Confidence score calculated (0-100)
- [ ] needs_review = true if confidence < 70%
- [ ] Feedback explains WHY and HOW to improve

---

## Agent 4: Reviewer Agent

### Test Weakness Analysis

```bash
curl -X POST http://localhost:8000/api/feedback/analyze-weaknesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "attempt_id": "<ATTEMPT_UUID>",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response

```json
{
  "improvement_plan_id": "plan-123",
  "weaknesses": {
    "AO1": [
      {
        "category": "Imprecise Definitions",
        "examples": ["Question 2: Defined demand as 'what people want'..."],
        "severity": "high",
        "syllabus_points": ["9708.2.1"]
      }
    ],
    "AO2": [...],
    "AO3": [...]
  },
  "action_items": [
    {
      "id": "action-1",
      "action": "Memorize precise definitions for 10 core Economics terms",
      "target_weakness": "AO1 - Imprecise Definitions",
      "due_date": "2025-01-22",
      "completed": false,
      "resources": [
        "9708 syllabus glossary",
        "Teacher Agent: Explain concept for each term"
      ]
    }
  ]
}
```

### Test A* Model Answer Generation

```bash
curl -X POST http://localhost:8000/api/feedback/generate-model-answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "question_id": "<QUESTION_UUID>",
    "student_answer": "Demand is when people want something..."
  }'
```

### Expected Response

```json
{
  "model_answer": "Demand is the quantity of a good consumers are willing and able to purchase at a given price, ceteris paribus. [✅ AO1: PRECISE DEFINITION]...",
  "annotations": [
    {
      "section": "Definition",
      "annotation": "✅ AO1: Precise definition with ceteris paribus",
      "improvement_shown": "Added 'willing and able' + 'ceteris paribus'"
    }
  ],
  "comparison": "[STUDENT] Demand is what people want...\n[A* MODEL] Demand is the quantity...",
  "key_improvements": [
    "Precise definition with ceteris paribus",
    "Theoretical explanation (income/substitution effects)",
    "Specific numerical example"
  ]
}
```

### Validation Checklist

- [ ] Weaknesses categorized by AO1/AO2/AO3
- [ ] Action items are specific and actionable
- [ ] Model answer is genuinely A* quality
- [ ] Annotations explain each improvement
- [ ] Comparison shows before/after

---

## Agent 5: Planner Agent

### Test Study Plan Generation

```bash
curl -X POST http://localhost:8000/api/planning/create-schedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "subject_id": "<ECONOMICS_9708_UUID>",
    "exam_date": "2025-03-15",
    "hours_per_day": 2.0,
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response

```json
{
  "plan_id": "plan-789",
  "total_days": 30,
  "schedule": [
    {
      "day": 1,
      "date": "2025-01-15",
      "topics": ["9708.1.1", "9708.1.2"],
      "interval": 1,
      "activities": ["study", "practice"],
      "hours_allocated": 2.0,
      "ef": 2.5,
      "completed": false
    },
    {
      "day": 4,
      "date": "2025-01-18",
      "topics": ["9708.1.1"],
      "interval": 3,
      "activities": ["review"],
      "hours_allocated": 1.0,
      "ef": 2.5,
      "completed": false
    }
  ],
  "easiness_factors": {
    "9708.1.1": 2.5,
    "9708.1.2": 2.5
  },
  "syllabus_coverage": {
    "total_points": 25,
    "covered_in_plan": 25,
    "coverage_percentage": 100
  }
}
```

### Test Progress Update (SM-2 Adaptation)

```bash
curl -X PATCH http://localhost:8000/api/planning/schedule/<PLAN_ID>/progress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "completed_day": 1,
    "performance_data": {
      "topics_mastered": ["9708.1.1"],
      "practice_scores": {
        "9708.1.1": 95,
        "9708.1.2": 65
      }
    },
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response (SM-2 Updated)

```json
{
  "updated_schedule": [...],
  "easiness_factors_updated": {
    "9708.1.1": 2.7,
    "9708.1.2": 2.2
  },
  "next_day": 4,
  "recommendations": [
    "Great progress on 9708.1.1 (scored 95%) - EF increased to 2.7",
    "9708.1.2 needs more practice (scored 65%) - EF adjusted to 2.2"
  ]
}
```

### Validation Checklist

- [ ] SM-2 intervals calculated correctly (1, 6, then EF*previous)
- [ ] Max 3 topics per day (contextual interleaving)
- [ ] Related topics grouped together
- [ ] EF adapts based on performance (0-5 quality scale)
- [ ] 100% syllabus coverage

---

## Agent 6: Examiner Enhancement

### Test Personalized Exam Generation

```bash
curl -X POST http://localhost:8000/api/exams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "subject_code": "9708",
    "exam_type": "PRACTICE",
    "question_count": 5,
    "strategy": "weakness_focused",
    "student_id": "<YOUR_STUDENT_ID>"
  }'
```

### Expected Response

```json
{
  "exam_id": "...",
  "question_ids": [...],
  "total_marks": 50,
  "duration": 90,
  "personalization_applied": {
    "avoided_previous_questions": 12,
    "targeted_weaknesses": ["9708.2.1", "9708.3.1"],
    "difficulty_calibration": "balanced"
  }
}
```

### Validation Checklist

- [ ] Avoids questions student has seen before
- [ ] Targets identified weaknesses
- [ ] Difficulty calibrated to student level
- [ ] Cambridge structure maintained

---

## End-to-End Workflow Test

### Complete Learning Cycle (All 6 Agents)

```bash
# Step 1: Learn topic (Teacher)
EXPLANATION=$(curl -X POST .../api/teaching/explain-concept ...)

# Step 2: Get help when stuck (Coach)
SESSION=$(curl -X POST .../api/coaching/tutor-session ...)

# Step 3: Take practice exam (Examiner)
EXAM=$(curl -X POST .../api/exams ...)

# Step 4: Get marked (Marker)
MARKING=$(curl -X POST .../api/marking/mark-attempt ...)

# Step 5: See weaknesses + model answer (Reviewer)
FEEDBACK=$(curl -X POST .../api/feedback/analyze-weaknesses ...)

# Step 6: Follow study plan (Planner)
PLAN=$(curl -X POST .../api/planning/create-schedule ...)
```

### Success Criteria

- [ ] All 6 agents work without errors
- [ ] Data flows between agents (e.g., Reviewer weaknesses → Planner prioritization)
- [ ] Student can complete full cycle without human intervention
- [ ] All responses are PhD-level quality

---

## Troubleshooting

### Issue: LLM Service Unavailable

**Symptom**: 500 error with "Claude Sonnet unavailable"

**Solution**:
1. Check ANTHROPIC_API_KEY is valid
2. Verify fallback LLM keys (OPENAI_API_KEY, GEMINI_API_KEY)
3. Check retry logic executed (3 attempts with backoff)
4. Review logs for circuit breaker status

### Issue: Confidence Score Always Low

**Symptom**: All answers flagged needs_review=true

**Solution**:
1. Check student answers are substantial (>50 words)
2. Verify marking_scheme exists for question
3. Review confidence calculation heuristics
4. Recalibrate threshold (currently 70%)

### Issue: SM-2 Intervals Too Short/Long

**Symptom**: Reviews scheduled too frequently or too far apart

**Solution**:
1. Verify EF values in range [1.3, 2.5]
2. Check quality score mapping (performance → q score)
3. Review interval formula: I(n) = I(n-1) * EF
4. Validate exam date proximity override (<7 days)

---

## Performance Benchmarks

### Expected Response Times

- Teacher: <5s average, <10s timeout
- Coach: <3s average, <5s timeout
- Marker: <8s average, <10s timeout
- Reviewer: <6s average, <10s timeout
- Planner: <4s average (SM-2 calculation fast)
- Examiner: <3s average (enhanced selection)

### Accuracy Targets

- Marking: ≥85% agreement with Cambridge mark schemes
- Confidence: ≥90% of high-confidence marks agree with humans
- Syllabus Coverage: 100% of Economics 9708 syllabus

---

## Next Steps

After validating all 6 agents:

1. Run `/sp.tasks` to generate atomic implementation tasks
2. Execute tasks via `/sp.implement`
3. Create ADRs for key decisions (SM-2, fallback, confidence)
4. Run end-to-end integration tests
5. Validate marking accuracy vs. 10 Cambridge sample questions
6. Execute phase gate: `scripts/check-phase-3-complete.sh`

---

**Quickstart Version**: 1.0.0
**Created**: 2025-12-20
**Estimated Testing Time**: 30 minutes
