# Phase III: AI Teaching Roles - Instructions

**Phase**: III of V
**Status**: 📋 Planned
**Focus**: 6 Core AI Agents (Teacher, Coach, Examiner, Marker, Reviewer, Planner)
**Last Updated**: 2026-01-05

---

## 🎯 Phase III Objectives

**Primary Goal**: Implement 6 AI teaching agents for PhD-level Economics 9708 instruction

**Key Deliverables**:
1. Teacher Agent - Concept explanations with diagrams/examples
2. Coach Agent - Personalized tutoring with Socratic questioning
3. Examiner Agent - Enhanced exam generation (avoid repeats, target weaknesses)
4. Marker Agent - Strict AO1/AO2/AO3 marking engine (≥85% accuracy)
5. Reviewer Agent - Weakness analysis and A* model answers
6. Planner Agent - n-day study schedules with SuperMemo 2 (SM-2)

**Technology Stack**:
- LLM: Claude Sonnet 4.5 (primary), OpenAI GPT-4.5 (fallback)
- Algorithms: SuperMemo 2 (SM-2), Contextual Interleaving
- Backend: FastAPI + SQLModel (existing)
- Database: PostgreSQL (coaching_sessions, study_plans, improvement_plans tables)

---

## 📋 Phase III-Specific Patterns

### 1. Agent Service Pattern

**Pattern**: Each agent is a service class with LLM integration

```python
# src/services/teaching_service.py
class TeachingService:
    """Teacher Agent - PhD-level concept explanations."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def explain_concept(
        self,
        syllabus_point_id: UUID,
        student_id: UUID,
        session: Session
    ) -> TopicExplanation:
        """
        Generate PhD-level explanation for syllabus topic.

        Uses: phd-pedagogy skill, subject-economics-9708 skill
        """
        # Verify multi-tenant access
        syllabus_point = session.exec(
            select(SyllabusPoint).where(
                SyllabusPoint.id == syllabus_point_id
            )
        ).first()

        if not syllabus_point:
            raise NotFoundError("Syllabus point not found")

        # Generate explanation via LLM
        prompt = self._build_explanation_prompt(syllabus_point)
        response = await self.llm.generate(prompt)

        return TopicExplanation.from_llm_response(response)
```

**Skill**: Use `.claude/skills/anthropic-api-patterns.md`

### 2. Marking Engine Pattern (AO1/AO2/AO3)

**Pattern**: Criterion-by-criterion scoring with confidence tracking

```python
class MarkingService:
    """Marker Agent - Strict Cambridge AO1/AO2/AO3 marking."""

    async def mark_answer(
        self,
        question_id: UUID,
        student_answer: str,
        student_id: UUID,
        session: Session
    ) -> MarkingResult:
        """
        Mark answer against Cambridge mark scheme.

        Returns:
            MarkingResult with:
            - total_marks: int
            - ao1_marks: int (Knowledge)
            - ao2_marks: int (Application)
            - ao3_marks: int (Analysis/Evaluation)
            - confidence_score: float (0-100)
            - needs_review: bool (True if confidence < 70%)
            - errors: List[str]
            - marking_points: List[MarkingPoint]
        """
        # Load question and mark scheme
        question = self._get_question_with_scheme(question_id, session)

        # Apply mark scheme via LLM
        result = await self._apply_mark_scheme(
            question=question,
            student_answer=student_answer,
            mark_scheme=question.mark_scheme
        )

        # Flag low confidence for manual review
        result.needs_review = result.confidence_score < 70.0

        return result
```

**Skill**: Use `.claude/skills/a-star-grading-rubrics.md`

### 3. SuperMemo 2 (SM-2) Pattern

**Pattern**: Spaced repetition with easiness factor tracking

```python
def calculate_sm2_interval(
    quality: int,  # 0-5 grade (0=complete blackout, 5=perfect)
    repetition: int,  # Current repetition number
    easiness_factor: float,  # EF (default 2.5)
    previous_interval: int  # Days since last review
) -> tuple[int, float]:
    """
    Calculate next review interval using SuperMemo 2 algorithm.

    Returns:
        (next_interval_days, new_easiness_factor)
    """
    # Update easiness factor
    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)  # EF must be >= 1.3

    # Calculate interval
    if quality < 3:
        # Failed - reset to beginning
        return (1, new_ef)

    if repetition == 1:
        return (1, new_ef)
    elif repetition == 2:
        return (6, new_ef)
    else:
        return (round(previous_interval * new_ef), new_ef)
```

**Skill**: Use `.claude/skills/supermemo2-scheduling.md`

### 4. Contextual Interleaving Pattern

**Pattern**: Mix related topics within cognitive load limits

```python
def generate_interleaved_schedule(
    topics: list[SyllabusPoint],
    exam_date: date,
    hours_per_day: float
) -> list[StudyDay]:
    """
    Generate study schedule with contextual interleaving.

    Rules:
    - Max 3 topics per day
    - Group related topics (same syllabus section)
    - Respect cognitive load (2 hours max per topic per session)
    - Apply SM-2 intervals for review scheduling
    """
    schedule = []

    # Group topics by syllabus section
    grouped = group_by_section(topics)

    for day_num in range(1, days_until_exam + 1):
        day_topics = select_topics_for_day(
            grouped_topics=grouped,
            day_num=day_num,
            max_topics=3,
            max_hours=hours_per_day
        )

        schedule.append(StudyDay(
            day=day_num,
            topics=day_topics,
            activities=["study", "practice", "review"]
        ))

    return schedule
```

**Skill**: Use `.claude/skills/contextual-interleaving.md`

### 5. Coach Session Pattern

**Pattern**: Interactive tutoring with session transcript

```python
class CoachingService:
    """Coach Agent - Personalized Socratic tutoring."""

    async def tutor_session(
        self,
        topic: str,
        struggle_description: str,
        student_id: UUID,
        session: Session
    ) -> CoachingSession:
        """
        Start interactive coaching session.

        Session transcript format:
        [
            {"role": "student", "content": "...", "timestamp": "ISO8601"},
            {"role": "coach", "content": "...", "timestamp": "ISO8601"}
        ]
        """
        # Create session record
        coaching_session = CoachingSession(
            student_id=student_id,
            topic=topic,
            struggle_description=struggle_description,
            session_transcript=[],
            outcome="in_progress"
        )
        session.add(coaching_session)
        session.commit()

        # Generate initial Socratic question
        initial_response = await self._generate_socratic_question(
            topic=topic,
            struggle=struggle_description
        )

        coaching_session.session_transcript.append({
            "role": "coach",
            "content": initial_response,
            "timestamp": datetime.utcnow().isoformat()
        })

        return coaching_session
```

---

## 🔐 Phase III Quality Requirements

### Marking Accuracy
- **Target**: ≥85% accuracy vs Cambridge mark schemes
- **Validation**: Test against 20 sample Cambridge papers
- **Fallback**: Manual review queue for confidence <70%

### LLM Latency
- **Target**: <5s for Teacher/Coach, <10s for Marker
- **Mitigation**: Cache common explanations, streaming responses

### Test Coverage
- **Target**: ≥80% for all new agent services
- **Required**: Unit tests + integration tests for each endpoint

---

## 📚 Phase III Skills & Agents

### Primary Skills
1. `phd-pedagogy` - Evidence-based teaching patterns
2. `a-star-grading-rubrics` - Cambridge A* marking criteria
3. `subject-economics-9708` - Economics domain knowledge
4. `supermemo2-scheduling` - SM-2 spaced repetition
5. `contextual-interleaving` - Topic mixing strategies
6. `confidence-scoring` - Answer evaluation confidence
7. `anthropic-api-patterns` - Claude API integration

### Primary Agents
- **Agent 10 - AI Pedagogy** (phd-pedagogy skill design)
- **Agent 06 - Teacher** (TeachingService, explanations)
- **Agent 04 - Coach** (CoachingService, tutoring)
- **Agent 05 - Examiner** (enhanced exam generation)
- **Agent 03 - Marker** (MarkingService, AO1/AO2/AO3)
- **Agent 07 - Reviewer** (ReviewService, model answers)
- **Agent 11 - Planner** (PlanningService, SM-2 schedules)

---

## 📁 Database Schema (Phase III Additions)

```sql
-- Coaching sessions tracking
CREATE TABLE coaching_sessions (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id) NOT NULL,
    topic VARCHAR(500) NOT NULL,
    struggle_description TEXT,
    session_transcript JSONB,  -- [{role, content, timestamp}]
    outcome VARCHAR(50),  -- "resolved", "needs_more_help", "refer_to_teacher"
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_coaching_student (student_id)
);

-- Study plans with SM-2 tracking
CREATE TABLE study_plans (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id) NOT NULL,
    subject_id UUID REFERENCES subjects(id) NOT NULL,
    exam_date DATE NOT NULL,
    total_days INT NOT NULL,
    hours_per_day FLOAT NOT NULL,
    schedule JSONB NOT NULL,  -- [{day, topics, interval, activities}]
    easiness_factors JSONB,  -- {"topic_id": 2.5, ...}
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_study_plan_student (student_id)
);

-- Improvement plans from Reviewer Agent
CREATE TABLE improvement_plans (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id) NOT NULL,
    attempt_id UUID REFERENCES attempts(id) NOT NULL,
    weaknesses JSONB NOT NULL,  -- {ao1: [], ao2: [], ao3: []}
    action_items JSONB NOT NULL,  -- [{action, priority, estimated_hours}]
    progress JSONB,  -- Track completion
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_improvement_student (student_id)
);
```

**Skill**: Use `.claude/skills/sqlmodel-database-schema-design.md`
**Skill**: Use `.claude/skills/alembic-migration-creation.md`

---

## 🚀 API Endpoints (Phase III)

```
# Teacher Agent
POST   /api/teaching/explain-concept

# Coach Agent
POST   /api/coaching/tutor-session
POST   /api/coaching/session/{id}/message
GET    /api/coaching/session/{id}
PATCH  /api/coaching/session/{id}/end

# Examiner Agent (enhanced)
POST   /api/exams/personalized

# Marker Agent
POST   /api/marking/mark-answer
POST   /api/marking/mark-attempt

# Reviewer Agent
POST   /api/feedback/analyze-weaknesses
POST   /api/feedback/generate-model-answer

# Planner Agent
POST   /api/planning/create-schedule
GET    /api/planning/schedule/{id}
PATCH  /api/planning/schedule/{id}/progress
```

**Skill**: Use `.claude/skills/fastapi-route-implementation.md`

---

## ⚠️ Risks & Mitigations

### Risk 1: Marking Accuracy Below 85%
**Impact**: HIGH - Students get incorrect feedback
**Mitigation**:
- Confidence scoring on all marks
- Manual review queue for low confidence
- Few-shot examples in prompts
- Iterative prompt engineering

### Risk 2: LLM Latency Too High
**Impact**: MEDIUM - Poor user experience
**Mitigation**:
- Cache common explanations
- Streaming responses
- Fallback LLM (GPT-4.5 if Claude unavailable)
- Timeout limits (5s Teacher, 10s Marker)

### Risk 3: Scope Creep
**Impact**: HIGH - Phase not completed
**Mitigation**:
- Economics 9708 ONLY (no other subjects)
- MVP for each agent (enhance later)
- Strict adherence to spec

---

## 📋 Constitutional Compliance

- **Principle I**: Cambridge accuracy verified against official mark schemes
- **Principle II**: PhD-level marking (A* standard, no inflation)
- **Principle IV**: Spec-driven development followed
- **Principle VI**: Constructive feedback with WHY and HOW
- **Principle VII**: ≥80% test coverage for new services

---

**Phase III Status**: 📋 Planned
**Prerequisites**: Phase II complete (Question Bank)
**Next Phase**: Phase IV (Web UI)
**Version**: 1.0.0 | **Last Updated**: 2026-01-05
