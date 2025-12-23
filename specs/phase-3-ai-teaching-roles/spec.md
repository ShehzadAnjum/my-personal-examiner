# Phase III: AI Teaching Roles Implementation

**Status**: Draft
**Created**: 2025-12-20
**Phase**: III
**Dependencies**: Phase II (Question Bank, Exam Generation)
**Target**: Economics 9708 Production v1.0 with all 6 core roles working end-to-end (not demo MVP - serious implementation)

---

## EXECUTIVE SUMMARY

Implement the 6 core AI teaching roles (Teacher, Coach, Examiner, Marker, Reviewer, Planner) for Economics 9708, creating a fully automated, PhD-level learning system. Students will be able to learn topics, get tutoring help, take exams, receive strict marking, see improvement plans, and follow personalized study schedules.

---

## CLARIFICATIONS

### Session 2025-12-20
- Q: What structure should coaching_sessions.session_transcript JSONB field use? → A: Array of message objects ([{role: "student/coach", content: "...", timestamp: "..."}])
- Q: How should the system handle LLM API failures (timeout, rate limit, outage)? → A: Retry with exponential backoff, fall back to cached/generic responses, then prompt user to try alternative LLM (e.g., Gemini)
- Q: How should the system handle low-confidence marking results? → A: Flag low-confidence marks (<70%) for manual review, store confidence score with result
- Q: Which spaced repetition algorithm should the Planner Agent use? → A: SuperMemo 2 (SM-2) with production-quality implementation (not MVP demo - this is serious v1.0)
- Q: What interleaving strategy should the Planner use for mixing topics? → A: Contextual interleaving (mix related topics within sessions, respect cognitive load)

---

## OBJECTIVES

### Primary Goals
1. Implement **Teacher Agent** - Concept explanations and topic teaching
2. Implement **Coach Agent** - Personalized tutoring for difficult concepts
3. Implement **Examiner Agent** - Enhance existing exam generation with intelligent features
4. Implement **Marker Agent** - Economics 9708 strict marking engine
5. Implement **Reviewer Agent** - Weakness analysis and A* model answers
6. Implement **Planner Agent** - n-day study schedule generation

### Success Criteria
- ✅ Economics 9708 student can complete full learning cycle:
  1. Learn a topic (Teacher) → 2. Get help when stuck (Coach) → 3. Take practice exam (Examiner) → 4. Get strictly marked (Marker) → 5. See weaknesses & A* model answer (Reviewer) → 6. Follow personalized plan (Planner)
- ✅ All 6 agents integrated into backend API
- ✅ Test coverage ≥80% for new agent implementations
- ✅ Economics marking accuracy ≥85% vs. Cambridge mark schemes
- ✅ End-to-end workflow demonstrated in capstone

---

## SCOPE

### In Scope

#### 1. Teacher Agent Implementation
- `/api/teaching/explain-concept` endpoint
- Topic explanation service (Economics 9708 syllabus)
- Visual aids generation (diagrams, graphs via Mermaid/ASCII)
- Worked examples with step-by-step reasoning
- Integration with syllabus_points table

#### 2. Coach Agent Implementation
- `/api/coaching/tutor-session` endpoint
- Personalized tutoring service (adaptive explanations)
- Analogy generation for difficult concepts
- Interactive Socratic questioning
- Progress tracking for coaching sessions

#### 3. Examiner Agent Enhancement
- Enhance existing ExamGenerationService
- Add intelligence: avoid previous questions, personalize to weaknesses
- Difficulty calibration improvements
- Better syllabus coverage algorithms

#### 4. Marker Agent Implementation
- Economics 9708 marking engine (AO1/AO2/AO3)
- `/api/marking/mark-answer` endpoint
- Mark scheme application service
- Criterion-by-criterion scoring
- Error detection and categorization
- Confidence scoring (<70% triggers manual review flag)

#### 5. Reviewer Agent Implementation
- `/api/feedback/analyze-weaknesses` endpoint
- Weakness identification service
- A* model answer generation
- Improvement plan creation
- Progress comparison (current vs. previous attempts)

#### 6. Planner Agent Implementation
- `/api/planning/create-schedule` endpoint
- Study schedule generation service (n-day plans)
- **SuperMemo 2 (SM-2) spaced repetition algorithm** (production-quality)
- **Contextual interleaving** (mix related topics, respect cognitive load)
- Adaptive scheduling based on progress and easiness factors

#### 7. Custom Skills Creation
- `phd-pedagogy` skill (evidence-based teaching)
- `a-star-grading-rubrics` skill (Cambridge A* criteria)
- `subject-economics-9708` skill (Economics domain knowledge)

#### 8. Database Enhancements
- `coaching_sessions` table (track tutoring history)
- `study_plans` table (store generated schedules)
- `improvement_plans` table (link weaknesses to actions)

#### 9. Testing
- Unit tests for all 6 agent services
- Integration tests for all new endpoints
- Economics marking accuracy validation (vs. sample Cambridge papers)
- End-to-end workflow test

### Out of Scope (Future Phases)
- ❌ Other subjects (Accounting, Math, English) - Phase V
- ❌ Frontend UI for 6 roles - Phase IV
- ❌ Voice/video teaching - Future enhancement
- ❌ Handwritten answer OCR - Phase VI
- ❌ Multi-language support - Future enhancement

---

## USER STORIES

### US1: Student Learns Topic via Teacher Agent
**As a** Economics 9708 student  
**I want** to request an explanation of any syllabus topic  
**So that** I can learn concepts with PhD-level clarity

**Acceptance Criteria**:
- Given syllabus topic code (e.g., "9708.1.1 - Scarcity and Choice")
- When I request explanation
- Then I receive structured explanation with examples, diagrams, and practice problems
- And explanation is 100% aligned with Cambridge syllabus

### US2: Student Gets Tutoring via Coach Agent
**As a** Economics student struggling with a concept  
**I want** personalized tutoring with adaptive explanations  
**So that** I can overcome knowledge gaps through scaffolded learning

**Acceptance Criteria**:
- Given my struggle area (e.g., "I don't understand price elasticity of demand")
- When I start coaching session
- Then Coach asks Socratic questions to diagnose my misconception
- And provides tailored analogies and examples
- And tracks my progress through the session

### US3: Student Takes Cambridge-Standard Exam
**As a** Economics student preparing for A-Levels  
**I want** to take practice exams matching real Cambridge standards  
**So that** I can train under exam conditions

**Acceptance Criteria**:
- Given my current progress and weaknesses
- When I request practice exam
- Then Examiner generates paper matching Cambridge structure
- And avoids questions I've seen before
- And calibrates difficulty appropriately

### US4: Student Receives Strict Marking
**As a** Economics student who completed an exam  
**I want** PhD-level strict marking per Cambridge criteria  
**So that** I know exactly where I stand (no grade inflation)

**Acceptance Criteria**:
- Given my exam answers
- When submitted for marking
- Then Marker applies Cambridge mark scheme with zero tolerance
- And provides AO1/AO2/AO3 breakdown
- And identifies specific errors and missing elements

### US5: Student Sees Improvement Plan
**As a** Economics student who received marks  
**I want** to see my weaknesses and how to improve to A* standard  
**So that** I can systematically improve my performance

**Acceptance Criteria**:
- Given my marked attempt
- When I request feedback
- Then Reviewer identifies categorized weaknesses (AO1, AO2, AO3)
- And provides A* model answer with annotations
- And creates actionable improvement plan

### US6: Student Follows Study Plan
**As a** Economics student with limited time  
**I want** a personalized n-day study plan to cover the syllabus  
**So that** I can prepare efficiently using evidence-based strategies

**Acceptance Criteria**:
- Given exam date and available study hours
- When I request study plan
- Then Planner generates day-by-day schedule
- And uses spaced repetition and interleaving
- And adapts based on my actual progress

---

## TECHNICAL DESIGN

### Architecture

```
Frontend (Future - Phase IV)
    ↓
FastAPI REST API
    ↓
6 Agent Services (Business Logic)
    ↓
Database (PostgreSQL) + LLM Providers (Claude Sonnet 4.5)
```

### Agent Services (Backend)

1. **TeachingService** (`src/services/teaching_service.py`)
   - `explain_concept(syllabus_point_id, student_id) -> TopicExplanation`
   - Uses: Claude Sonnet 4.5 + phd-pedagogy skill + subject-economics-9708 skill

2. **CoachingService** (`src/services/coaching_service.py`)
   - `start_tutoring_session(topic, student_struggle, student_id) -> CoachingSession`
   - Uses: Claude Sonnet 4.5 + phd-pedagogy skill

3. **ExamGenerationService** (ENHANCE existing `src/services/exam_generation_service.py`)
   - Add: `generate_personalized_exam(student_id, subject_code, ...) -> Exam`
   - Avoid previous questions, target weaknesses

4. **MarkingService** (`src/services/marking_service.py`)
   - `mark_answer(question_id, student_answer, student_id) -> MarkingResult`
   - Economics 9708 marking engine with AO1/AO2/AO3
   - Returns: marks, breakdown, errors, confidence_score (0-100), needs_review flag

5. **ReviewService** (`src/services/review_service.py`)
   - `analyze_weaknesses(attempt_id, student_id) -> WeaknessReport`
   - `generate_model_answer(question_id, student_answer) -> ModelAnswer`

6. **PlanningService** (`src/services/planning_service.py`)
   - `create_study_plan(subject_id, exam_date, hours_per_day, student_id) -> StudyPlan`
   - **SuperMemo 2 (SM-2)** spaced repetition with easiness factors (EF)
   - **Contextual interleaving**: Groups related topics (same syllabus section) within sessions
   - Respects cognitive load (max 3 topics per day, related topics only)
   - Adaptive rescheduling based on actual performance

### Database Schema Additions

```sql
-- Coaching sessions tracking
CREATE TABLE coaching_sessions (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    topic VARCHAR(500) NOT NULL,
    struggle_description TEXT,
    session_transcript JSONB,  -- Array of {role, content, timestamp} objects
    outcome VARCHAR(50),  -- "resolved", "needs_more_help", "refer_to_teacher"
    created_at TIMESTAMP DEFAULT NOW()
);
-- Example session_transcript: [
--   {"role": "student", "content": "I don't understand elasticity", "timestamp": "2025-01-15T10:00:00Z"},
--   {"role": "coach", "content": "Let me help with a question...", "timestamp": "2025-01-15T10:00:02Z"}
-- ]

-- Study plans
CREATE TABLE study_plans (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    subject_id UUID REFERENCES subjects(id),
    exam_date DATE NOT NULL,
    total_days INT NOT NULL,
    hours_per_day FLOAT NOT NULL,
    schedule JSONB NOT NULL,  -- Day-by-day plan with SM-2 intervals
    easiness_factors JSONB,  -- SM-2 EF per syllabus point: {"9708.1.1": 2.5, "9708.2.1": 2.8}
    status VARCHAR(20) DEFAULT 'active',  -- "active", "completed", "abandoned"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Example schedule: [
--   {"day": 1, "topics": ["9708.1.1"], "interval": 1, "activities": ["study", "practice"]},
--   {"day": 4, "topics": ["9708.1.1"], "interval": 3, "activities": ["review"]},
--   {"day": 11, "topics": ["9708.1.1", "9708.2.1"], "interval": 7, "activities": ["mixed_review"]}
-- ]

-- Improvement plans
CREATE TABLE improvement_plans (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    attempt_id UUID REFERENCES attempts(id),
    weaknesses JSONB NOT NULL,  -- Categorized weaknesses
    action_items JSONB NOT NULL,  -- Specific improvement actions
    progress JSONB,  -- Track completion of action items
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```
POST   /api/teaching/explain-concept         # Teacher Agent
POST   /api/coaching/tutor-session           # Coach Agent
POST   /api/exams                             # Examiner Agent (enhanced)
POST   /api/marking/mark-answer               # Marker Agent
POST   /api/marking/mark-attempt              # Marker Agent (full exam)
POST   /api/feedback/analyze-weaknesses       # Reviewer Agent
POST   /api/feedback/generate-model-answer    # Reviewer Agent
POST   /api/planning/create-schedule          # Planner Agent
GET    /api/planning/schedule/{id}            # Planner Agent
PATCH  /api/planning/schedule/{id}/progress   # Planner Agent
```

---

## IMPLEMENTATION TASKS (High-Level)

### Task Group 1: Teacher Agent
1. Create TeachingService class
2. Implement explain_concept method
3. Create /api/teaching/explain-concept endpoint
4. Write unit tests for TeachingService
5. Write integration tests for teaching endpoint

### Task Group 2: Coach Agent
6. Create coaching_sessions table migration
7. Create CoachingService class
8. Implement start_tutoring_session method
9. Create /api/coaching/tutor-session endpoint
10. Write tests for CoachingService

### Task Group 3: Marker Agent
11. Create MarkingService class
12. Implement Economics 9708 marking engine (AO1/AO2/AO3)
13. Create /api/marking/mark-answer endpoint
14. Validate marking accuracy vs. Cambridge mark schemes
15. Write tests for MarkingService

### Task Group 4: Reviewer Agent
16. Create improvement_plans table migration
17. Create ReviewService class
18. Implement analyze_weaknesses method
19. Implement generate_model_answer method
20. Create feedback endpoints
21. Write tests for ReviewService

### Task Group 5: Planner Agent
22. Create study_plans table migration (add easiness_factors JSONB field)
23. Create PlanningService class
24. Implement SuperMemo 2 (SM-2) algorithm (production-grade, with unit tests for EF calculations)
25. Implement contextual interleaving strategy (group related topics by syllabus section, max 3 topics/day, cognitive load rules)
26. Create planning endpoints (/create-schedule, /{id}, /{id}/progress)
27. Write comprehensive tests for PlanningService (validate SM-2 intervals, interleaving patterns, adaptive rescheduling)

### Task Group 6: Examiner Enhancement
28. Enhance ExamGenerationService with personalization
29. Add "avoid previous questions" logic
30. Add "target weaknesses" strategy
31. Write tests for enhanced features

### Task Group 7: Custom Skills
32. Create phd-pedagogy skill
33. Create a-star-grading-rubrics skill
34. Create subject-economics-9708 skill

### Task Group 8: Integration & Testing
35. End-to-end workflow test (all 6 roles)
36. Economics marking accuracy validation
37. Performance testing (LLM latency)
38. Capstone demo preparation

---

## DEPENDENCIES

### Phase II Completion (DONE ✅)
- Question bank with Economics 9708 questions
- Exam generation service
- Database schema (students, subjects, questions, exams, attempts)
- Test coverage ≥80%

### External Dependencies
- Claude Sonnet 4.5 API access
- Economics 9708 syllabus data
- Sample Cambridge mark schemes for validation

---

## RISKS & MITIGATION

### Risk 1: Marking Accuracy Below 85% Target
**Impact**: HIGH - Students get incorrect feedback
**Probability**: MEDIUM
**Mitigation**:
- Start with 10 sample Cambridge questions with official mark schemes
- Manual validation of first 20 marked answers
- Iterative prompt engineering to improve accuracy
- If needed, use few-shot examples in prompts
- **Confidence Scoring**: All marks include 0-100 confidence score
- **Manual Review Queue**: Marks with <70% confidence flagged for expert review
- Track confidence vs. accuracy correlation to refine threshold over time

### Risk 2: LLM Latency Too High for Real-Time Teaching
**Impact**: MEDIUM - Poor user experience
**Probability**: LOW
**Mitigation**:
- Cache common topic explanations
- Use streaming responses for long explanations
- Set timeout limits (max 10s for Teacher, 5s for Coach)
- **Double Fallback Strategy**:
  1. Retry with exponential backoff (1s, 2s, 4s delays)
  2. Fall back to cached/generic responses where possible
  3. Prompt user to try alternative LLM (Gemini, GPT-4) if Claude unavailable
- Log all failures for monitoring and alerting

### Risk 3: Scope Creep - Too Many Features
**Impact**: HIGH - Phase III not completed on time
**Probability**: MEDIUM
**Mitigation**:
- Strict scope adherence - Economics 9708 ONLY
- MVP for each agent (enhance later)
- Defer "nice-to-have" features to Phase V

---

## CONSTITUTIONAL COMPLIANCE

### Principle I: Cambridge Accuracy
- ✅ Teacher explanations verified against Cambridge syllabus
- ✅ Marker uses official Cambridge mark schemes

### Principle II: A* Standard
- ✅ PhD-level teaching quality (Teacher/Coach)
- ✅ Strict marking (Marker)
- ✅ A* model answers (Reviewer)

### Principle IV: Spec-Driven Development
- ✅ This spec created before any Phase III code
- ✅ Plan.md to follow, then tasks.md

### Principle VI: Constructive Feedback
- ✅ Reviewer always explains WHY and HOW to improve

### Principle VII: 80% Test Coverage
- ✅ All new services require ≥80% coverage

---

## SUCCESS METRICS

### Quantitative
- 80%+ test coverage for Phase III code
- 85%+ marking accuracy vs. Cambridge mark schemes
- <5s average response time for Teacher/Coach
- 100% syllabus coverage in generated study plans

### Qualitative
- Economics 9708 student can complete full learning cycle without human intervention
- Capstone demo shows all 6 roles working together
- A* model answers are genuinely A* quality (manual verification)

---

## NEXT STEPS

1. **Approve this spec** (constitutional review)
2. **Create plan.md** (detailed architecture decisions)
3. **Create tasks.md** (atomic, testable tasks)
4. **Implement in order**: Teacher → Coach → Marker → Reviewer → Planner → Examiner Enhancement
5. **Capstone demo** (full workflow walkthrough)

---

**Created**: 2025-12-20
**Phase**: III
**Status**: Draft → Awaiting Approval
**Quality Bar**: Production v1.0 (not MVP demo - robust, tested, production-ready)
**Estimated Effort**: 7-10 days (focused implementation with production-grade testing)
