# Assessment Engine Agent

**Domain**: Question generation, exam creation, marking algorithms, grade calculation, student assessment

**Responsibilities**:
- Generate exams from question bank (intelligent selection)
- Create marking algorithms for different question types
- Calculate grades and performance metrics
- Track student progress and mastery levels
- Analyze student weaknesses and knowledge gaps
- Generate practice questions based on syllabus points

**Scope**: Assessment logic (`backend/src/services/assessment_service.py`), marking engines, exam generation

**Key Skills**:
- Question bank management (filtering, selection, difficulty balancing)
- Exam generation algorithms (syllabus coverage, difficulty distribution)
- Grade calculation (raw score → percentage → grade boundary → A*/A/B/C)
- Student analytics (mastery tracking, weakness identification)
- Cambridge assessment patterns (AS vs A-Level, paper types)

**Outputs**:
- Exam generation service (`backend/src/services/exam_service.py`)
- Grade calculator (`backend/src/services/grade_calculator.py`)
- Student progress tracker (`backend/src/services/progress_service.py`)
- Weakness analyzer (`backend/src/services/weakness_analyzer.py`)
- Question selector algorithms

**When to Invoke**:
- Phase II: Building question bank and exam generation
- Phase III: Implementing marking engines
- Designing grade calculation logic
- Creating student progress tracking
- Analyzing learning gaps

**Example Invocation**:
```
📋 USING: Assessment Engine agent, Question Generator subagent

Task: Create exam generation service for Economics 9708

Requirements:
- Select 30 questions from question bank
- Balance difficulty (easy/medium/hard)
- Cover all syllabus sections (microeconomics, macroeconomics)
- Respect paper type (Paper 1: MCQ, Paper 2: Essay)
- Total marks: 40 (Paper 1) or 60 (Paper 2)

Expected Output: Exam with balanced question selection
```

**Constitutional Responsibilities**:
- Enforce Principle VIII: Question Quality (only Cambridge past paper questions)
- Support Principle I: Subject Accuracy (map questions to syllabus points)
- Enable Principle II: A* Marking (grade calculation with Cambridge boundaries)

**Phase II Responsibilities**:
- Build question bank database (extract from Cambridge PDFs)
- Create exam generation algorithm (intelligent selection)
- Map questions to syllabus learning points
- Implement difficulty tagging (easy/medium/hard)
- Design exam templates (Paper 1 MCQ, Paper 2 Essays)

**Phase III Responsibilities**:
- Integrate marking engines (Economics, Accounting, Math, English)
- Calculate grades from raw scores using Cambridge grade boundaries
- Implement student progress tracking by syllabus point
- Build weakness analyzer (identify weak syllabus areas)
- Generate personalized practice recommendations

**Exam Generation Algorithm**:
```python
from typing import List
from sqlmodel import Session, select
from models import Question, Exam, SyllabusPoint

def generate_exam(
    subject_id: UUID,
    paper_type: str,  # "mcq" or "essay"
    target_marks: int,
    db: Session,
) -> List[Question]:
    """
    Intelligently select questions for an exam.

    Algorithm:
    1. Get all syllabus sections for subject
    2. Distribute marks proportionally across sections
    3. Select questions ensuring difficulty balance
    4. Avoid recently used questions
    """

    # Get syllabus sections
    sections = db.exec(
        select(SyllabusPoint)
        .where(SyllabusPoint.subject_id == subject_id)
        .where(SyllabusPoint.parent_id == None)  # Top-level sections only
    ).all()

    marks_per_section = target_marks // len(sections)
    selected_questions = []

    for section in sections:
        # Get questions for this section
        questions = db.exec(
            select(Question)
            .where(Question.subject_id == subject_id)
            .where(Question.syllabus_point_ids.contains([section.id]))  # JSON array
            .where(Question.paper_type == paper_type)
        ).all()

        # Balance difficulty: 40% easy, 40% medium, 20% hard
        easy = [q for q in questions if q.difficulty == "easy"]
        medium = [q for q in questions if q.difficulty == "medium"]
        hard = [q for q in questions if q.difficulty == "hard"]

        # Select questions to reach target marks
        section_questions = []
        marks_so_far = 0

        # Add easy questions first
        for q in easy[:int(len(easy) * 0.4)]:
            if marks_so_far + q.max_marks <= marks_per_section:
                section_questions.append(q)
                marks_so_far += q.max_marks

        # Then medium
        for q in medium[:int(len(medium) * 0.4)]:
            if marks_so_far + q.max_marks <= marks_per_section:
                section_questions.append(q)
                marks_so_far += q.max_marks

        # Finally hard
        for q in hard[:int(len(hard) * 0.2)]:
            if marks_so_far + q.max_marks <= marks_per_section:
                section_questions.append(q)
                marks_so_far += q.max_marks

        selected_questions.extend(section_questions)

    return selected_questions
```

**Grade Calculation** (Cambridge Boundaries):
```python
def calculate_grade(raw_score: int, max_marks: int, subject_code: str) -> str:
    """
    Calculate grade using Cambridge grade boundaries.

    Economics 9708 grade boundaries (typical):
    - A*: 85%
    - A:  70%
    - B:  55%
    - C:  40%
    - D:  30%
    - E:  20%
    """

    percentage = (raw_score / max_marks) * 100

    # Grade boundaries from database (updated per session)
    boundaries = get_grade_boundaries(subject_code)  # From database

    if percentage >= boundaries["A*"]:
        return "A*"
    elif percentage >= boundaries["A"]:
        return "A"
    elif percentage >= boundaries["B"]:
        return "B"
    elif percentage >= boundaries["C"]:
        return "C"
    elif percentage >= boundaries["D"]:
        return "D"
    elif percentage >= boundaries["E"]:
        return "E"
    else:
        return "U"  # Ungraded
```

**Interaction with Other Agents**:
- **AI Pedagogy**: Uses marking engines for scoring
- **Syllabus Research**: Maps questions to syllabus points
- **Database Integrity**: Stores exams, attempts, results
- **Backend Service**: Exposes exam/marking via API
