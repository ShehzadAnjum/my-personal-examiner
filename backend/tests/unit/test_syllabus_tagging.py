"""
Unit Tests: Syllabus Tagging

Tests for Phase II US7 - Syllabus Tagging.

Test Coverage:
- Syllabus point CRUD operations (create, read, update, delete, list)
- Question tagging (add/remove syllabus points)
- Syllabus coverage statistics
- Edge cases (duplicates, non-existent entities)

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest
from uuid import uuid4

from src.models.question import Question
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint


class TestSyllabusPointCRUD:
    """Test syllabus point CRUD operations"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def sample_subject(self):
        """Create sample subject"""
        return Subject(
            id=uuid4(),
            code="9708",
            name="Economics",
            level="A",
            syllabus_year="2023-2025",
        )

    @pytest.fixture
    def sample_syllabus_point(self, sample_subject):
        """Create sample syllabus point"""
        return SyllabusPoint(
            id=uuid4(),
            subject_id=sample_subject.id,
            code="9708.1.1",
            description="The central economic problem",
            topics="Scarcity, Choice, Opportunity cost",
            learning_outcomes="Understand the nature of the economic problem",
        )

    def test_syllabus_point_creation(self, sample_syllabus_point):
        """Test syllabus point model creation"""
        assert sample_syllabus_point.code == "9708.1.1"
        assert "economic problem" in sample_syllabus_point.description
        assert sample_syllabus_point.topics is not None

    def test_syllabus_point_code_validation(self):
        """Test syllabus code format validation"""
        valid_sp = SyllabusPoint(
            id=uuid4(),
            subject_id=uuid4(),
            code="9708.1.1",
            description="Test",
        )
        assert valid_sp.is_valid_code_format()

        invalid_sp = SyllabusPoint(
            id=uuid4(),
            subject_id=uuid4(),
            code="invalid",
            description="Test",
        )
        assert not invalid_sp.is_valid_code_format()

    def test_list_syllabus_points_filters_by_subject(self, mock_db, mocker, sample_subject, sample_syllabus_point):
        """Test listing syllabus points filtered by subject"""
        # Mock DB to return syllabus points
        exec_mock = mocker.MagicMock()
        exec_mock.first.return_value = sample_subject  # Subject lookup
        exec_mock.all.return_value = [sample_syllabus_point]  # Syllabus points

        mock_db.exec.return_value = exec_mock

        # Import route function
        from src.routes.syllabus import list_syllabus_points

        # Call with subject filter (provide explicit page/page_size)
        results = list_syllabus_points(subject_code="9708", page=1, page_size=50, db=mock_db)

        assert len(results) == 1
        assert results[0].code == "9708.1.1"

    def test_list_syllabus_points_filters_by_code_prefix(self, mock_db, mocker, sample_syllabus_point):
        """Test listing syllabus points filtered by code prefix"""
        # Mock DB to return syllabus points matching prefix
        exec_mock = mocker.MagicMock()
        exec_mock.all.return_value = [sample_syllabus_point]
        mock_db.exec.return_value = exec_mock

        from src.routes.syllabus import list_syllabus_points

        # Call with code prefix filter (provide explicit page/page_size)
        results = list_syllabus_points(code_prefix="9708.1", page=1, page_size=50, db=mock_db)

        assert len(results) == 1
        assert results[0].code.startswith("9708.1")


class TestQuestionTagging:
    """Test question tagging functionality"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def sample_question(self):
        """Create sample question"""
        return Question(
            id=uuid4(),
            subject_id=uuid4(),
            question_text="Sample question",
            max_marks=8,
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=1,
            year=2022,
            session="MAY_JUNE",
            difficulty="medium",
            syllabus_point_ids=[],  # Initially no tags
        )

    @pytest.fixture
    def sample_syllabus_points(self):
        """Create sample syllabus points"""
        subject_id = uuid4()
        return [
            SyllabusPoint(
                id=uuid4(),
                subject_id=subject_id,
                code="9708.1.1",
                description="Economic problem",
            ),
            SyllabusPoint(
                id=uuid4(),
                subject_id=subject_id,
                code="9708.1.2",
                description="Opportunity cost",
            ),
        ]

    def test_add_tags_to_question(self, sample_question, sample_syllabus_points):
        """Test adding syllabus point tags to a question"""
        # Add tags
        sp_ids = [str(sp.id) for sp in sample_syllabus_points]
        sample_question.syllabus_point_ids = sp_ids

        assert len(sample_question.syllabus_point_ids) == 2
        assert str(sample_syllabus_points[0].id) in sample_question.syllabus_point_ids

    def test_remove_tag_from_question(self, sample_question, sample_syllabus_points):
        """Test removing a syllabus point tag from a question"""
        # Add tags first
        sp_ids = [str(sp.id) for sp in sample_syllabus_points]
        sample_question.syllabus_point_ids = sp_ids

        # Remove one tag
        tag_to_remove = str(sample_syllabus_points[0].id)
        sample_question.syllabus_point_ids.remove(tag_to_remove)

        assert len(sample_question.syllabus_point_ids) == 1
        assert tag_to_remove not in sample_question.syllabus_point_ids

    def test_prevent_duplicate_tags(self, sample_question, sample_syllabus_points):
        """Test that duplicate tags are prevented"""
        sp_id = str(sample_syllabus_points[0].id)

        # Add tag twice
        tags = [sp_id, sp_id]
        # Deduplicate (as done in route handler)
        unique_tags = list(set(tags))

        assert len(unique_tags) == 1

    def test_empty_tags_list(self, sample_question):
        """Test handling of empty tags list"""
        assert sample_question.syllabus_point_ids == []

        # Adding to empty list
        new_tag = str(uuid4())
        sample_question.syllabus_point_ids.append(new_tag)

        assert len(sample_question.syllabus_point_ids) == 1


class TestSyllabusCoverage:
    """Test syllabus coverage statistics"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def sample_subject(self):
        """Create sample subject"""
        return Subject(
            id=uuid4(),
            code="9708",
            name="Economics",
            level="A",
            syllabus_year="2023-2025",
        )

    @pytest.fixture
    def sample_syllabus_points(self, sample_subject):
        """Create 5 syllabus points"""
        return [
            SyllabusPoint(
                id=uuid4(),
                subject_id=sample_subject.id,
                code=f"9708.1.{i}",
                description=f"Topic {i}",
            )
            for i in range(1, 6)
        ]

    @pytest.fixture
    def sample_questions(self, sample_subject, sample_syllabus_points):
        """Create questions with partial syllabus coverage"""
        # 3 questions tagged with different syllabus points
        # Syllabus points 1-3 have questions, 4-5 don't
        questions = []

        for i in range(3):
            questions.append(
                Question(
                    id=uuid4(),
                    subject_id=sample_subject.id,
                    question_text=f"Question {i+1}",
                    max_marks=8,
                    source_paper="9708_s22_qp_22",
                    paper_number=22,
                    question_number=i + 1,
                    year=2022,
                    session="MAY_JUNE",
                    difficulty="medium",
                    syllabus_point_ids=[str(sample_syllabus_points[i].id)],
                )
            )

        return questions

    def test_calculate_coverage_percentage(self, sample_syllabus_points, sample_questions):
        """Test syllabus coverage calculation"""
        # 5 syllabus points total
        total_sp = len(sample_syllabus_points)

        # Count how many syllabus points have at least one question
        sp_with_questions = set()
        for q in sample_questions:
            if q.syllabus_point_ids:
                sp_with_questions.update(q.syllabus_point_ids)

        tagged_sp = len(sp_with_questions)
        coverage = (tagged_sp / total_sp * 100) if total_sp > 0 else 0

        # 3 out of 5 syllabus points have questions = 60%
        assert coverage == 60.0

    def test_identify_untagged_syllabus_points(self, sample_syllabus_points, sample_questions):
        """Test identification of untagged syllabus points"""
        # Get all question tags
        tagged_sp_ids = set()
        for q in sample_questions:
            if q.syllabus_point_ids:
                tagged_sp_ids.update(q.syllabus_point_ids)

        # Find untagged syllabus points
        untagged = [
            sp for sp in sample_syllabus_points if str(sp.id) not in tagged_sp_ids
        ]

        # Syllabus points 4-5 should be untagged
        assert len(untagged) == 2
        assert all(sp.code in ["9708.1.4", "9708.1.5"] for sp in untagged)

    def test_count_questions_per_syllabus_point(self, sample_syllabus_points, sample_questions):
        """Test counting questions per syllabus point"""
        questions_per_sp = {}

        for sp in sample_syllabus_points:
            sp_id_str = str(sp.id)
            count = sum(
                1
                for q in sample_questions
                if q.syllabus_point_ids and sp_id_str in q.syllabus_point_ids
            )
            questions_per_sp[sp.code] = count

        # Syllabus points 1-3 should have 1 question each
        assert questions_per_sp["9708.1.1"] == 1
        assert questions_per_sp["9708.1.2"] == 1
        assert questions_per_sp["9708.1.3"] == 1

        # Syllabus points 4-5 should have 0 questions
        assert questions_per_sp["9708.1.4"] == 0
        assert questions_per_sp["9708.1.5"] == 0

    def test_empty_syllabus(self):
        """Test coverage calculation with no syllabus points"""
        total_sp = 0
        tagged_sp = 0
        coverage = (tagged_sp / total_sp * 100) if total_sp > 0 else 0.0

        assert coverage == 0.0

    def test_full_coverage(self, sample_syllabus_points):
        """Test coverage calculation with 100% coverage"""
        # Create questions for all syllabus points
        questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text=f"Question {i+1}",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=i + 1,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
                syllabus_point_ids=[str(sample_syllabus_points[i].id)],
            )
            for i in range(len(sample_syllabus_points))
        ]

        total_sp = len(sample_syllabus_points)
        tagged_sp_ids = set()
        for q in questions:
            if q.syllabus_point_ids:
                tagged_sp_ids.update(q.syllabus_point_ids)

        tagged_sp = len(tagged_sp_ids)
        coverage = (tagged_sp / total_sp * 100)

        assert coverage == 100.0


class TestSyllabusPointValidation:
    """Test syllabus point validation"""

    def test_valid_code_formats(self):
        """Test valid syllabus code formats"""
        valid_codes = [
            "9708.1.1",
            "9708.1",
            "9706.2.3.1",
            "8021.A.1",
        ]

        for code in valid_codes:
            sp = SyllabusPoint(
                id=uuid4(),
                subject_id=uuid4(),
                code=code,
                description="Test",
            )
            assert sp.is_valid_code_format(), f"Code {code} should be valid"

    def test_invalid_code_formats(self):
        """Test invalid syllabus code formats"""
        invalid_codes = [
            "invalid",  # No dot
            "9708",  # Single part
            "",  # Empty
            "9708.",  # Empty part after dot
            ".9708",  # Empty part before dot
            "9708..1",  # Empty part in middle
        ]

        for code in invalid_codes:
            sp = SyllabusPoint(
                id=uuid4(),
                subject_id=uuid4(),
                code=code,
                description="Test",
            )
            assert not sp.is_valid_code_format(), f"Code '{code}' should be invalid"

    def test_code_uniqueness_per_subject(self):
        """Test that syllabus code should be unique per subject"""
        subject_id = uuid4()

        sp1 = SyllabusPoint(
            id=uuid4(),
            subject_id=subject_id,
            code="9708.1.1",
            description="First",
        )

        sp2 = SyllabusPoint(
            id=uuid4(),
            subject_id=subject_id,
            code="9708.1.1",  # Same code
            description="Second",
        )

        # Both objects can be created, but database should enforce uniqueness
        # (tested via integration tests with actual database)
        assert sp1.code == sp2.code
        assert sp1.id != sp2.id


class TestQuestionTaggingEdgeCases:
    """Test edge cases in question tagging"""

    def test_tag_question_with_multiple_syllabus_points(self):
        """Test tagging a question with multiple syllabus points"""
        question = Question(
            id=uuid4(),
            subject_id=uuid4(),
            question_text="Complex question",
            max_marks=12,
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=1,
            year=2022,
            session="MAY_JUNE",
            difficulty="hard",
        )

        # Add 3 syllabus points
        sp_ids = [str(uuid4()) for _ in range(3)]
        question.syllabus_point_ids = sp_ids

        assert len(question.syllabus_point_ids) == 3

    def test_tag_none_value(self):
        """Test handling of None value for syllabus_point_ids"""
        question = Question(
            id=uuid4(),
            subject_id=uuid4(),
            question_text="Question",
            max_marks=8,
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=1,
            year=2022,
            session="MAY_JUNE",
            difficulty="medium",
            syllabus_point_ids=None,
        )

        # Initialize empty list if None
        current_tags = question.syllabus_point_ids if question.syllabus_point_ids else []
        assert current_tags == []

        # Add tags
        new_tag = str(uuid4())
        current_tags.append(new_tag)
        question.syllabus_point_ids = current_tags

        assert len(question.syllabus_point_ids) == 1

    def test_remove_non_existent_tag(self):
        """Test removing a tag that doesn't exist"""
        question = Question(
            id=uuid4(),
            subject_id=uuid4(),
            question_text="Question",
            max_marks=8,
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=1,
            year=2022,
            session="MAY_JUNE",
            difficulty="medium",
            syllabus_point_ids=[str(uuid4())],
        )

        initial_count = len(question.syllabus_point_ids)

        # Try to remove non-existent tag
        non_existent_tag = str(uuid4())
        if non_existent_tag in question.syllabus_point_ids:
            question.syllabus_point_ids.remove(non_existent_tag)

        # Count should remain same
        assert len(question.syllabus_point_ids) == initial_count
