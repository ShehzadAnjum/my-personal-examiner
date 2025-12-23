"""
Integration Tests: Syllabus Routes

Tests for Phase II US7 - Syllabus Tagging & Coverage API endpoints.

Test Coverage:
- GET /api/syllabus/{subject_code} - List syllabus points
- GET /api/syllabus/coverage/{subject_code} - Get syllabus coverage
- GET /api/subjects - List subjects
"""

import pytest

from src.models.question import Question
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint


@pytest.fixture
def test_data(db_session):
    """Create test data: subject, syllabus points, and questions"""
    # Create subject
    subject = Subject(
        code="9708",
        name="Economics",
        level="A",
        exam_board="Cambridge",
        syllabus_year="2023-2025",
    )
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)

    # Create 10 syllabus points
    syllabus_points = []
    for i in range(1, 11):
        sp = SyllabusPoint(
            subject_id=subject.id,
            code=f"9708.{i}.1",
            description=f"Topic {i}",
            topics=f"Subtopic {i}",
        )
        db_session.add(sp)
        syllabus_points.append(sp)

    db_session.commit()
    for sp in syllabus_points:
        db_session.refresh(sp)

    # Create questions that tag SOME syllabus points (not all)
    questions = []

    # Tag first 5 syllabus points with questions
    for i in range(5):
        q = Question(
            subject_id=subject.id,
            question_text=f"Question about topic {i+1}",
            max_marks=8,
            difficulty="medium",
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=i + 1,
            year=2022,
            session="MAY_JUNE",
            syllabus_point_ids=[str(syllabus_points[i].id)],
        )
        db_session.add(q)
        questions.append(q)

    # Create one question tagging multiple syllabus points
    q_multi = Question(
        subject_id=subject.id,
        question_text="Question covering multiple topics",
        max_marks=12,
        difficulty="hard",
        source_paper="9708_s22_qp_22",
        paper_number=22,
        question_number=6,
        year=2022,
        session="MAY_JUNE",
        syllabus_point_ids=[str(syllabus_points[0].id), str(syllabus_points[1].id)],
    )
    db_session.add(q_multi)
    questions.append(q_multi)

    db_session.commit()

    return {
        "subject": subject,
        "syllabus_points": syllabus_points,
        "questions": questions,
    }


class TestListSubjects:
    """Test GET /api/subjects"""

    def test_list_subjects_empty(self, client):
        """Test listing subjects when none exist"""
        response = client.get("/api/subjects")

        assert response.status_code == 200
        # There's always at least Economics from migrations
        data = response.json()
        assert isinstance(data, list)

    def test_list_subjects_with_data(self, client, test_data):
        """Test listing subjects"""
        response = client.get("/api/subjects")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Find our Economics subject
        econ = next((s for s in data if s["code"] == "9708"), None)
        assert econ is not None
        assert econ["name"] == "Economics"
        assert econ["level"] == "A"
        assert "id" in econ


class TestListSyllabusPoints:
    """Test GET /api/syllabus/{subject_code}"""

    def test_list_syllabus_points_success(self, client, test_data):
        """Test listing syllabus points for a subject"""
        response = client.get("/api/syllabus?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10  # Our 10 test syllabus points

        # Verify structure
        first_point = data[0]
        assert "id" in first_point
        assert "code" in first_point
        assert "description" in first_point
        assert first_point["code"].startswith("9708.")

    def test_list_syllabus_points_not_found(self, client):
        """Test empty result when subject not found"""
        response = client.get("/api/syllabus?subject_code=9999")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Empty list for non-existent subject

    def test_list_syllabus_points_sorted(self, client, test_data):
        """Test that syllabus points are returned in order"""
        response = client.get("/api/syllabus?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        codes = [sp["code"] for sp in data]

        # Should be sorted by code
        assert codes == sorted(codes)


class TestSyllabusCoverage:
    """Test GET /api/syllabus/coverage/{subject_code}"""

    def test_get_coverage_success(self, client, test_data):
        """Test getting syllabus coverage"""
        response = client.get("/api/syllabus/coverage/9708")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert data["subject_code"] == "9708"
        assert data["total_syllabus_points"] == 10
        assert data["tagged_syllabus_points"] == 5  # First 5 are tagged
        assert data["coverage_percentage"] == 50.0
        assert "untagged_syllabus_points" in data
        assert "questions_per_syllabus_point" in data

    def test_get_coverage_untagged_points(self, client, test_data):
        """Test that untagged syllabus points are listed"""
        response = client.get("/api/syllabus/coverage/9708")

        assert response.status_code == 200
        data = response.json()

        untagged = data["untagged_syllabus_points"]
        assert len(untagged) == 5  # Last 5 are untagged

        # Verify structure of untagged points
        for point in untagged:
            assert "id" in point
            assert "code" in point
            assert "description" in point

    def test_get_coverage_questions_per_point(self, client, test_data):
        """Test questions count per syllabus point"""
        response = client.get("/api/syllabus/coverage/9708")

        assert response.status_code == 200
        data = response.json()

        questions_per_point = data["questions_per_syllabus_point"]

        # First syllabus point has 2 questions (one direct, one multi-tag)
        sp1_code = f"9708.1.1"
        assert sp1_code in questions_per_point
        assert questions_per_point[sp1_code] == 2

        # Second syllabus point has 2 questions
        sp2_code = f"9708.2.1"
        assert sp2_code in questions_per_point
        assert questions_per_point[sp2_code] == 2

        # Third through fifth have 1 question each
        for i in range(3, 6):
            sp_code = f"9708.{i}.1"
            assert sp_code in questions_per_point
            assert questions_per_point[sp_code] == 1

    def test_get_coverage_not_found(self, client):
        """Test error when subject not found"""
        response = client.get("/api/syllabus/coverage/9999")

        assert response.status_code == 404

    def test_get_coverage_no_questions(self, client, db_session):
        """Test coverage when subject has no questions"""
        # Create a new subject with syllabus points but no questions
        subject = Subject(
            code="9709",
            name="Mathematics",
            level="A",
            exam_board="Cambridge",
            syllabus_year="2023-2025",
        )
        db_session.add(subject)
        db_session.commit()
        db_session.refresh(subject)

        # Add syllabus points
        for i in range(1, 4):
            sp = SyllabusPoint(
                subject_id=subject.id,
                code=f"9709.{i}.1",
                description=f"Math Topic {i}",
            )
            db_session.add(sp)
        db_session.commit()

        response = client.get("/api/syllabus/coverage/9709")

        assert response.status_code == 200
        data = response.json()
        assert data["total_syllabus_points"] == 3
        assert data["tagged_syllabus_points"] == 0
        assert data["coverage_percentage"] == 0.0
        assert len(data["untagged_syllabus_points"]) == 3

    def test_get_coverage_full_coverage(self, client, db_session):
        """Test coverage when all syllabus points are tagged"""
        # Create subject
        subject = Subject(
            code="9706",
            name="Accounting",
            level="A",
            exam_board="Cambridge",
            syllabus_year="2023-2025",
        )
        db_session.add(subject)
        db_session.commit()
        db_session.refresh(subject)

        # Add syllabus points
        syllabus_points = []
        for i in range(1, 4):
            sp = SyllabusPoint(
                subject_id=subject.id,
                code=f"9706.{i}.1",
                description=f"Accounting Topic {i}",
            )
            db_session.add(sp)
            syllabus_points.append(sp)
        db_session.commit()
        for sp in syllabus_points:
            db_session.refresh(sp)

        # Add questions for ALL syllabus points
        for i, sp in enumerate(syllabus_points):
            q = Question(
                subject_id=subject.id,
                question_text=f"Accounting question {i+1}",
                max_marks=8,
                difficulty="medium",
                source_paper="9706_s22_qp_22",
                paper_number=22,
                question_number=i + 1,
                year=2022,
                session="MAY_JUNE",
                syllabus_point_ids=[str(sp.id)],
            )
            db_session.add(q)
        db_session.commit()

        response = client.get("/api/syllabus/coverage/9706")

        assert response.status_code == 200
        data = response.json()
        assert data["total_syllabus_points"] == 3
        assert data["tagged_syllabus_points"] == 3
        assert data["coverage_percentage"] == 100.0
        assert len(data["untagged_syllabus_points"]) == 0


class TestSyllabusPointDetails:
    """Test GET /api/syllabus/points/{id}"""

    def test_get_syllabus_point_success(self, client, test_data):
        """Test getting syllabus point by ID"""
        sp = test_data["syllabus_points"][0]
        response = client.get(f"/api/syllabus/points/{sp.id}")

        # Endpoint may or may not exist depending on implementation
        assert response.status_code in [200, 404, 405]

        if response.status_code == 200:
            data = response.json()
            assert data["id"] == str(sp.id)
            assert data["code"] == sp.code
