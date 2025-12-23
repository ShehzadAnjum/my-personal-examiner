"""
Exam Generation Service

Generates custom exams from question bank with intelligent question selection.

Phase II User Story 6: Exam Generation
- Generate practice exams (custom question count)
- Generate timed exams (time-limited)
- Generate full papers (mimic real Cambridge papers)
- Support multiple generation strategies (random, difficulty-balanced, syllabus-based)
"""

import random
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlmodel import Session

from src.models.exam import Exam
from src.models.question import Question
from src.models.subject import Subject


class ExamGenerationError(Exception):
    """Raised when exam generation fails"""

    pass


class ExamGenerationService:
    """
    Service for generating exams from question bank

    Supports multiple generation strategies and exam types.
    Ensures question variety, difficulty balance, and marks distribution.
    """

    def __init__(self, db: Session):
        """
        Initialize exam generation service

        Args:
            db: Database session
        """
        self.db = db

    def generate_exam(
        self,
        subject_id: UUID,
        exam_type: str,
        paper_number: int | None = None,
        question_count: int | None = None,
        target_marks: int | None = None,
        duration: int | None = None,
        difficulty_distribution: dict[str, float] | None = None,
        year: int | None = None,
        session: str | None = None,
        strategy: str = "balanced",
        student_id: UUID | None = None,
    ) -> Exam:
        """
        Generate exam with intelligent question selection

        Args:
            subject_id: Subject UUID
            exam_type: PRACTICE, TIMED, or FULL_PAPER
            paper_number: Optional paper number (22, 31, 32, 42)
            question_count: Number of questions (default: auto-calculate)
            target_marks: Target total marks (default: auto-calculate)
            duration: Exam duration in minutes (default: auto-calculate)
            difficulty_distribution: Desired difficulty mix (e.g., {"easy": 0.3, "medium": 0.5, "hard": 0.2})
            year: Filter questions by year
            session: Filter questions by session
            strategy: Selection strategy (random, balanced, syllabus_coverage)
            student_id: Optional student ID (for personalized exams)

        Returns:
            Exam: Generated exam entity

        Raises:
            ExamGenerationError: If generation fails (insufficient questions, etc.)

        Examples:
            >>> service = ExamGenerationService(db)
            >>> exam = service.generate_exam(
            ...     subject_id=economics_id,
            ...     exam_type="PRACTICE",
            ...     question_count=5,
            ...     target_marks=30,
            ...     duration=45,
            ...     strategy="balanced"
            ... )
            >>> len(exam.question_ids)
            5
        """
        # Validate exam type
        if exam_type not in ("PRACTICE", "TIMED", "FULL_PAPER"):
            raise ExamGenerationError(f"Invalid exam type: {exam_type}")

        # Build question filter criteria
        filters = [Question.subject_id == subject_id]

        if paper_number:
            filters.append(Question.paper_number == paper_number)

        if year:
            filters.append(Question.year == year)

        if session:
            filters.append(Question.session == session)

        # Get available questions
        stmt = select(Question).where(and_(*filters))
        result = self.db.exec(stmt)
        available_questions = list(result.scalars())

        if not available_questions:
            raise ExamGenerationError("No questions available for the specified criteria")

        # Select questions based on strategy
        if strategy == "random":
            selected_questions = self._select_random(
                available_questions, question_count, target_marks
            )
        elif strategy == "balanced":
            selected_questions = self._select_balanced(
                available_questions, question_count, target_marks, difficulty_distribution
            )
        elif strategy == "syllabus_coverage":
            selected_questions = self._select_syllabus_coverage(
                available_questions, question_count, target_marks
            )
        else:
            raise ExamGenerationError(f"Unknown selection strategy: {strategy}")

        if not selected_questions:
            raise ExamGenerationError("Could not select sufficient questions")

        # Calculate exam metadata
        actual_marks = sum(q.max_marks for q in selected_questions)

        # Auto-calculate duration if not provided (2 minutes per mark as heuristic)
        if duration is None:
            duration = max(30, actual_marks * 2)  # Minimum 30 minutes

        # Create exam entity
        exam = Exam(
            student_id=student_id,
            subject_id=subject_id,
            exam_type=exam_type,
            paper_number=paper_number,
            question_ids=[str(q.id) for q in selected_questions],  # Store as list of UUID strings
            total_marks=actual_marks,
            duration=duration,
            status="PENDING",
        )

        # Save to database
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)

        return exam

    def _select_random(
        self,
        questions: list[Question],
        count: int | None,
        target_marks: int | None,
    ) -> list[Question]:
        """
        Random question selection

        Args:
            questions: Available questions
            count: Desired question count
            target_marks: Desired total marks

        Returns:
            list[Question]: Selected questions
        """
        if count:
            # Select exactly 'count' questions
            if len(questions) < count:
                raise ExamGenerationError(
                    f"Insufficient questions: need {count}, have {len(questions)}"
                )
            return random.sample(questions, count)

        elif target_marks:
            # Select questions to approximate target marks
            random.shuffle(questions)
            selected = []
            total = 0

            for q in questions:
                if total >= target_marks:
                    break
                selected.append(q)
                total += q.max_marks

            if total < target_marks * 0.8:  # Within 80% of target
                raise ExamGenerationError(
                    f"Could not reach target marks: got {total}, need {target_marks}"
                )

            return selected

        else:
            # Default: select all questions (limited to 20)
            return random.sample(questions, min(20, len(questions)))

    def _select_balanced(
        self,
        questions: list[Question],
        count: int | None,
        target_marks: int | None,
        difficulty_distribution: dict[str, float] | None,
    ) -> list[Question]:
        """
        Difficulty-balanced question selection

        Args:
            questions: Available questions
            count: Desired question count
            target_marks: Desired total marks
            difficulty_distribution: Desired difficulty mix

        Returns:
            list[Question]: Selected questions with balanced difficulty
        """
        # Default distribution: 30% easy, 50% medium, 20% hard
        if not difficulty_distribution:
            difficulty_distribution = {"easy": 0.3, "medium": 0.5, "hard": 0.2}

        # Group questions by difficulty
        by_difficulty = {"easy": [], "medium": [], "hard": []}

        for q in questions:
            difficulty = q.difficulty if q.difficulty in by_difficulty else "medium"
            by_difficulty[difficulty].append(q)

        # Calculate target count per difficulty
        if count:
            target_count = count
        elif target_marks:
            # Estimate question count from target marks (average 6-8 marks per question)
            target_count = max(3, target_marks // 7)
        else:
            target_count = 10

        # Select questions per difficulty level
        selected = []

        for difficulty, proportion in difficulty_distribution.items():
            needed = int(target_count * proportion)
            available = by_difficulty[difficulty]

            if available:
                # Take up to 'needed' questions from this difficulty
                take_count = min(needed, len(available))
                selected.extend(random.sample(available, take_count))

        # If we haven't reached target count, fill with random questions
        if len(selected) < target_count:
            remaining_questions = [q for q in questions if q not in selected]
            needed = target_count - len(selected)

            if remaining_questions:
                take_count = min(needed, len(remaining_questions))
                selected.extend(random.sample(remaining_questions, take_count))

        # Ensure we don't exceed target
        if len(selected) > target_count:
            selected = random.sample(selected, target_count)

        # Shuffle to mix difficulties
        random.shuffle(selected)

        return selected

    def _select_syllabus_coverage(
        self,
        questions: list[Question],
        count: int | None,
        target_marks: int | None,
    ) -> list[Question]:
        """
        Syllabus coverage-based selection (maximize topic diversity)

        Args:
            questions: Available questions
            count: Desired question count
            target_marks: Desired total marks

        Returns:
            list[Question]: Selected questions with diverse syllabus coverage
        """
        # Group questions by syllabus points
        by_syllabus = {}

        for q in questions:
            # Use first syllabus point as primary topic
            if q.syllabus_point_ids and len(q.syllabus_point_ids) > 0:
                topic = q.syllabus_point_ids[0]
            else:
                topic = "untagged"

            if topic not in by_syllabus:
                by_syllabus[topic] = []

            by_syllabus[topic].append(q)

        # Calculate target count
        if count:
            target_count = count
        elif target_marks:
            target_count = max(3, target_marks // 7)
        else:
            target_count = 10

        # Select one question per topic (round-robin)
        selected = []
        topics = list(by_syllabus.keys())
        topic_index = 0

        while len(selected) < target_count:
            if not any(by_syllabus.values()):
                break  # No more questions available

            topic = topics[topic_index]

            if by_syllabus[topic]:
                # Pick random question from this topic
                q = random.choice(by_syllabus[topic])
                selected.append(q)
                by_syllabus[topic].remove(q)  # Don't select same question twice

            # Move to next topic (round-robin)
            topic_index = (topic_index + 1) % len(topics)

        return selected

    def get_exam_questions(self, exam_id: UUID) -> list[Question]:
        """
        Get all questions for an exam (in order)

        Args:
            exam_id: Exam UUID

        Returns:
            list[Question]: Questions in exam order

        Raises:
            ExamGenerationError: If exam not found

        Examples:
            >>> service = ExamGenerationService(db)
            >>> questions = service.get_exam_questions(exam_id)
            >>> len(questions)
            5
        """
        # Get exam
        stmt = select(Exam).where(Exam.id == exam_id)
        result = self.db.exec(stmt)
        exam = result.scalars().first()

        if not exam:
            raise ExamGenerationError(f"Exam {exam_id} not found")

        # Get questions (preserve order)
        question_ids = exam.question_ids if exam.question_ids else []
        questions = []

        for qid in question_ids:
            stmt_q = select(Question).where(Question.id == UUID(qid))
            result_q = self.db.exec(stmt_q)
            q = result_q.scalars().first()

            if q:
                questions.append(q)

        return questions

    def get_exam_statistics(self, exam_id: UUID) -> dict[str, Any]:
        """
        Get exam statistics (difficulty breakdown, marks distribution, etc.)

        Args:
            exam_id: Exam UUID

        Returns:
            dict with:
                - total_questions: Total question count
                - total_marks: Total marks
                - difficulty_breakdown: Count per difficulty
                - marks_per_difficulty: Marks per difficulty
                - average_marks_per_question: Average marks

        Examples:
            >>> service = ExamGenerationService(db)
            >>> stats = service.get_exam_statistics(exam_id)
            >>> stats['difficulty_breakdown']
            {"easy": 2, "medium": 3, "hard": 1}
        """
        questions = self.get_exam_questions(exam_id)

        # Calculate statistics
        total_questions = len(questions)
        total_marks = sum(q.max_marks for q in questions)

        difficulty_breakdown = {"easy": 0, "medium": 0, "hard": 0}
        marks_per_difficulty = {"easy": 0, "medium": 0, "hard": 0}

        for q in questions:
            difficulty = q.difficulty if q.difficulty in difficulty_breakdown else "medium"
            difficulty_breakdown[difficulty] += 1
            marks_per_difficulty[difficulty] += q.max_marks

        average_marks_per_question = total_marks / total_questions if total_questions > 0 else 0

        return {
            "total_questions": total_questions,
            "total_marks": total_marks,
            "difficulty_breakdown": difficulty_breakdown,
            "marks_per_difficulty": marks_per_difficulty,
            "average_marks_per_question": round(average_marks_per_question, 1),
        }
