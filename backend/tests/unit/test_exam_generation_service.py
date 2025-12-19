"""
Unit Tests: Exam Generation Service

Tests for Phase II US6 - Exam Generation.

Test Coverage:
- Exam generation with different strategies (random, balanced, syllabus_coverage)
- Exam metadata calculation (total marks, duration)
- Question selection logic (count, target_marks)
- Difficulty distribution (balanced strategy)
- Syllabus coverage (round-robin selection)
- Edge cases (insufficient questions, invalid parameters)
- Exam statistics calculation

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest
from uuid import uuid4

from src.models.exam import Exam
from src.models.question import Question
from src.models.subject import Subject
from src.services.exam_generation_service import (
    ExamGenerationError,
    ExamGenerationService,
)


class TestExamGenerationBasic:
    """Test basic exam generation functionality"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create exam generation service with mocked DB"""
        return ExamGenerationService(mock_db)

    @pytest.fixture
    def sample_questions(self):
        """Create sample questions for testing"""
        subject_id = uuid4()
        return [
            Question(
                id=uuid4(),
                subject_id=subject_id,
                question_text=f"Question {i}",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=i,
                year=2022,
                session="MAY_JUNE",
                difficulty="easy" if i <= 3 else ("medium" if i <= 7 else "hard"),
                syllabus_point_ids=[f"9708.{i}.1"],
            )
            for i in range(1, 11)  # 10 questions: 3 easy, 4 medium, 3 hard
        ]

    def test_generate_exam_validates_exam_type(self, service, mock_db, mocker):
        """Test exam type validation"""
        subject_id = uuid4()

        # Mock DB to return empty results
        mocker.patch.object(
            mock_db,
            "exec",
            return_value=mocker.MagicMock(all=lambda: []),
        )

        with pytest.raises(ExamGenerationError, match="Invalid exam type"):
            service.generate_exam(
                subject_id=subject_id,
                exam_type="INVALID_TYPE",
            )

    def test_generate_exam_no_questions_available(self, service, mock_db, mocker):
        """Test error when no questions available"""
        subject_id = uuid4()

        # Mock DB to return empty question list
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        exec_mock = mocker.MagicMock()
        exec_mock.scalars.return_value = scalars_mock
        mock_db.exec.return_value = exec_mock

        with pytest.raises(ExamGenerationError, match="No questions available"):
            service.generate_exam(
                subject_id=subject_id,
                exam_type="PRACTICE",
                question_count=5,
            )

    def test_generate_exam_creates_exam_entity(self, service, mock_db, mocker, sample_questions):
        """Test exam entity creation"""
        subject_id = sample_questions[0].subject_id

        # Mock DB exec to return sample questions
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter(sample_questions)
        exec_mock = mocker.MagicMock()
        exec_mock.scalars.return_value = scalars_mock

        # Mock add, commit, refresh
        mock_db.exec.return_value = exec_mock
        mock_db.add = mocker.MagicMock()
        mock_db.commit = mocker.MagicMock()
        mock_db.refresh = mocker.MagicMock()

        exam = service.generate_exam(
            subject_id=subject_id,
            exam_type="PRACTICE",
            question_count=5,
        )

        # Verify exam was created
        assert mock_db.add.called
        assert mock_db.commit.called


class TestRandomStrategy:
    """Test random question selection strategy"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service"""
        return ExamGenerationService(mock_db)

    @pytest.fixture
    def sample_questions(self):
        """Create 20 sample questions"""
        subject_id = uuid4()
        return [
            Question(
                id=uuid4(),
                subject_id=subject_id,
                question_text=f"Question {i}",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=i,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            )
            for i in range(1, 21)
        ]

    def test_random_selection_exact_count(self, service, sample_questions):
        """Test random selection returns exact count"""
        selected = service._select_random(sample_questions, count=5, target_marks=None)

        assert len(selected) == 5
        assert all(q in sample_questions for q in selected)

    def test_random_selection_insufficient_questions(self, service, sample_questions):
        """Test error when insufficient questions"""
        with pytest.raises(ExamGenerationError, match="Insufficient questions"):
            service._select_random(sample_questions, count=50, target_marks=None)

    def test_random_selection_target_marks(self, service, sample_questions):
        """Test random selection by target marks"""
        selected = service._select_random(sample_questions, count=None, target_marks=40)

        total_marks = sum(q.max_marks for q in selected)
        assert total_marks >= 40
        assert total_marks >= 40 * 0.8  # Within 80% of target

    def test_random_selection_default_limit(self, service, sample_questions):
        """Test default selection limit (20 questions max)"""
        # Create 30 questions
        many_questions = sample_questions * 2  # 40 questions

        selected = service._select_random(many_questions, count=None, target_marks=None)

        assert len(selected) <= 20


class TestBalancedStrategy:
    """Test difficulty-balanced selection strategy"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service"""
        return ExamGenerationService(mock_db)

    @pytest.fixture
    def sample_questions(self):
        """Create questions with varied difficulty"""
        subject_id = uuid4()
        questions = []

        # 10 easy questions
        for i in range(1, 11):
            questions.append(
                Question(
                    id=uuid4(),
                    subject_id=subject_id,
                    question_text=f"Easy Q{i}",
                    max_marks=4,
                    source_paper="9708_s22_qp_22",
                    paper_number=22,
                    question_number=i,
                    year=2022,
                    session="MAY_JUNE",
                    difficulty="easy",
                )
            )

        # 10 medium questions
        for i in range(11, 21):
            questions.append(
                Question(
                    id=uuid4(),
                    subject_id=subject_id,
                    question_text=f"Medium Q{i}",
                    max_marks=8,
                    source_paper="9708_s22_qp_22",
                    paper_number=22,
                    question_number=i,
                    year=2022,
                    session="MAY_JUNE",
                    difficulty="medium",
                )
            )

        # 10 hard questions
        for i in range(21, 31):
            questions.append(
                Question(
                    id=uuid4(),
                    subject_id=subject_id,
                    question_text=f"Hard Q{i}",
                    max_marks=12,
                    source_paper="9708_s22_qp_22",
                    paper_number=22,
                    question_number=i,
                    year=2022,
                    session="MAY_JUNE",
                    difficulty="hard",
                )
            )

        return questions

    def test_balanced_selection_default_distribution(self, service, sample_questions):
        """Test balanced selection with default distribution (30% easy, 50% medium, 20% hard)"""
        selected = service._select_balanced(
            sample_questions,
            count=10,
            target_marks=None,
            difficulty_distribution=None,
        )

        assert len(selected) == 10

        # Count difficulties
        easy_count = sum(1 for q in selected if q.difficulty == "easy")
        medium_count = sum(1 for q in selected if q.difficulty == "medium")
        hard_count = sum(1 for q in selected if q.difficulty == "hard")

        # Verify approximate distribution (allow ±1 tolerance)
        assert 2 <= easy_count <= 4  # Expected 3 (30% of 10)
        assert 4 <= medium_count <= 6  # Expected 5 (50% of 10)
        assert 1 <= hard_count <= 3  # Expected 2 (20% of 10)

    def test_balanced_selection_custom_distribution(self, service, sample_questions):
        """Test balanced selection with custom distribution"""
        custom_distribution = {"easy": 0.5, "medium": 0.3, "hard": 0.2}

        selected = service._select_balanced(
            sample_questions,
            count=10,
            target_marks=None,
            difficulty_distribution=custom_distribution,
        )

        assert len(selected) == 10

        easy_count = sum(1 for q in selected if q.difficulty == "easy")
        medium_count = sum(1 for q in selected if q.difficulty == "medium")

        # Verify custom distribution applied (allow ±1 tolerance)
        assert 4 <= easy_count <= 6  # Expected 5 (50% of 10)
        assert 2 <= medium_count <= 4  # Expected 3 (30% of 10)

    def test_balanced_selection_target_marks(self, service, sample_questions):
        """Test balanced selection by target marks"""
        selected = service._select_balanced(
            sample_questions,
            count=None,
            target_marks=70,
            difficulty_distribution=None,
        )

        # Verify questions selected (estimate: 70 marks / 7 avg marks = 10 questions)
        assert len(selected) >= 3

    def test_balanced_selection_shuffles_results(self, service, sample_questions):
        """Test balanced selection shuffles questions (not grouped by difficulty)"""
        selected = service._select_balanced(
            sample_questions,
            count=10,
            target_marks=None,
            difficulty_distribution=None,
        )

        # Check that difficulties are mixed (not all easy first, then medium, then hard)
        difficulties = [q.difficulty for q in selected]

        # Count transitions between difficulty levels
        transitions = sum(
            1
            for i in range(len(difficulties) - 1)
            if difficulties[i] != difficulties[i + 1]
        )

        # Expect at least 3 transitions if shuffled (not perfectly grouped)
        assert transitions >= 3


class TestSyllabusCoverageStrategy:
    """Test syllabus coverage-based selection strategy"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service"""
        return ExamGenerationService(mock_db)

    @pytest.fixture
    def sample_questions(self):
        """Create questions with diverse syllabus points"""
        subject_id = uuid4()
        questions = []

        # 3 questions per topic (5 topics)
        for topic_idx in range(1, 6):
            for q_idx in range(1, 4):
                questions.append(
                    Question(
                        id=uuid4(),
                        subject_id=subject_id,
                        question_text=f"Topic {topic_idx} Q{q_idx}",
                        max_marks=8,
                        source_paper="9708_s22_qp_22",
                        paper_number=22,
                        question_number=topic_idx * 10 + q_idx,
                        year=2022,
                        session="MAY_JUNE",
                        difficulty="medium",
                        syllabus_point_ids=[f"9708.{topic_idx}.1"],
                    )
                )

        return questions

    def test_syllabus_coverage_round_robin(self, service, sample_questions):
        """Test syllabus coverage selects one question per topic (round-robin)"""
        selected = service._select_syllabus_coverage(
            sample_questions,
            count=5,
            target_marks=None,
        )

        assert len(selected) == 5

        # Extract topics
        topics = [q.syllabus_point_ids[0] for q in selected if q.syllabus_point_ids]

        # Verify all unique topics (no duplicates)
        assert len(topics) == len(set(topics))

    def test_syllabus_coverage_multiple_rounds(self, service, sample_questions):
        """Test syllabus coverage does multiple rounds if needed"""
        selected = service._select_syllabus_coverage(
            sample_questions,
            count=10,  # More than 5 topics, so need 2 rounds
            target_marks=None,
        )

        assert len(selected) == 10

        # Verify diversity (should have questions from all 5 topics)
        topics = [q.syllabus_point_ids[0] for q in selected if q.syllabus_point_ids]
        unique_topics = set(topics)
        assert len(unique_topics) == 5

    def test_syllabus_coverage_handles_untagged(self, service, sample_questions):
        """Test syllabus coverage handles questions without syllabus points"""
        # Add untagged questions
        subject_id = sample_questions[0].subject_id
        untagged = [
            Question(
                id=uuid4(),
                subject_id=subject_id,
                question_text="Untagged Q",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=100,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
                syllabus_point_ids=[],  # No tags
            )
        ]

        all_questions = sample_questions + untagged

        selected = service._select_syllabus_coverage(
            all_questions,
            count=6,  # 5 topics + 1 untagged
            target_marks=None,
        )

        assert len(selected) == 6


class TestExamMetadata:
    """Test exam metadata calculation"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service"""
        return ExamGenerationService(mock_db)

    def test_total_marks_calculation(self, service, mocker):
        """Test total marks calculation"""
        questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text=f"Q{i}",
                max_marks=i * 2,  # 2, 4, 6, 8, 10
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=i,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            )
            for i in range(1, 6)
        ]

        # Mock DB
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter(questions)
        exec_mock = mocker.MagicMock()
        exec_mock.scalars.return_value = scalars_mock
        service.db.exec.return_value = exec_mock
        service.db.add = mocker.MagicMock()
        service.db.commit = mocker.MagicMock()
        service.db.refresh = mocker.MagicMock()

        exam = service.generate_exam(
            subject_id=questions[0].subject_id,
            exam_type="PRACTICE",
            question_count=5,
        )

        # Total: 2 + 4 + 6 + 8 + 10 = 30
        assert exam.total_marks == sum(q.max_marks for q in questions)

    def test_duration_auto_calculation(self, service, mocker):
        """Test duration auto-calculation (2 minutes per mark)"""
        questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text=f"Q{i}",
                max_marks=10,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=i,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            )
            for i in range(1, 6)
        ]

        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter(questions)
        exec_mock = mocker.MagicMock()
        exec_mock.scalars.return_value = scalars_mock
        service.db.exec.return_value = exec_mock
        service.db.add = mocker.MagicMock()
        service.db.commit = mocker.MagicMock()
        service.db.refresh = mocker.MagicMock()

        exam = service.generate_exam(
            subject_id=questions[0].subject_id,
            exam_type="PRACTICE",
            question_count=5,
            duration=None,  # Auto-calculate
        )

        # Total marks: 50, Duration: 50 * 2 = 100 minutes
        assert exam.duration == 100

    def test_duration_minimum_30_minutes(self, service, mocker):
        """Test duration minimum is 30 minutes"""
        questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Q1",
                max_marks=5,  # Only 5 marks total
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=1,
                year=2022,
                session="MAY_JUNE",
                difficulty="easy",
            )
        ]

        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter(questions)
        exec_mock = mocker.MagicMock()
        exec_mock.scalars.return_value = scalars_mock
        service.db.exec.return_value = exec_mock
        service.db.add = mocker.MagicMock()
        service.db.commit = mocker.MagicMock()
        service.db.refresh = mocker.MagicMock()

        exam = service.generate_exam(
            subject_id=questions[0].subject_id,
            exam_type="PRACTICE",
            question_count=1,
        )

        # Duration should be minimum 30 minutes (not 10 = 5 * 2)
        assert exam.duration >= 30


class TestExamStatistics:
    """Test exam statistics calculation"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        db = mocker.MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create service"""
        return ExamGenerationService(mock_db)

    def test_get_exam_statistics(self, service, mocker):
        """Test exam statistics calculation"""
        exam_id = uuid4()

        # Create exam with questions
        questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Easy Q",
                max_marks=4,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=1,
                year=2022,
                session="MAY_JUNE",
                difficulty="easy",
            ),
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Medium Q1",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=2,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            ),
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Medium Q2",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=3,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            ),
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Hard Q",
                max_marks=12,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=4,
                year=2022,
                session="MAY_JUNE",
                difficulty="hard",
            ),
        ]

        # Mock get_exam_questions to return these questions
        mocker.patch.object(
            service,
            "get_exam_questions",
            return_value=questions,
        )

        stats = service.get_exam_statistics(exam_id)

        assert stats["total_questions"] == 4
        assert stats["total_marks"] == 32  # 4 + 8 + 8 + 12
        assert stats["difficulty_breakdown"] == {"easy": 1, "medium": 2, "hard": 1}
        assert stats["marks_per_difficulty"] == {"easy": 4, "medium": 16, "hard": 12}
        assert stats["average_marks_per_question"] == 8.0  # 32 / 4
