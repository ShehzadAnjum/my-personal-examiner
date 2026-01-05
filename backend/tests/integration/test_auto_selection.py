"""
Integration tests for resource auto-selection workflow.

Feature: 007-resource-bank-files (User Story 5)
Created: 2025-12-27

Tests end-to-end auto-selection algorithm:
1. Create resources with different relevance scores
2. Link resources to syllabus points
3. Trigger auto-selection
4. Verify top 5 returned in correct order

Constitutional Compliance:
- FR-032: Auto-select top 5 resources by relevance
- FR-035: Include resources in LLM prompt with attribution
- FR-036: Track resource usage in explanations
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.enums import ResourceType, Visibility
from src.models.explanation_resource_usage import ExplanationResourceUsage
from src.models.generated_explanation import GeneratedExplanation
from src.models.resource import Resource
from src.models.student import Student
from src.models.syllabus_point_resource import SyllabusPointResource
from src.services.resource_service import (
    get_resources_for_syllabus_point,
    prepare_resources_for_llm_prompt,
    track_resource_usage,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def student(db_session: Session):
    student = Student(
        id=uuid4(),
        email="student@test.com",
        full_name="Test Student",
        is_admin=False,
        hashed_password="hash123"
    )
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def admin(db_session: Session):
    admin = Student(
        id=uuid4(),
        email="admin@test.com",
        full_name="Admin User",
        is_admin=True,
        hashed_password="hash456"
    )
    db_session.add(admin)
    db_session.commit()
    return admin


class TestAutoSelectionWorkflow:
    """Test end-to-end auto-selection workflow."""

    def test_auto_selects_top_5_resources_by_relevance(self, db_session: Session, student):
        """Should auto-select top 5 resources ordered by relevance_score DESC."""
        syllabus_point_id = "9708.5.1"

        # Create 8 resources with different types and relevance scores
        resources_data = [
            (ResourceType.SYLLABUS, "Cambridge Syllabus 9708", 1.0, True),
            (ResourceType.PAST_PAPER, "9708 June 2023 Paper 2 Q3", 0.95, True),
            (ResourceType.PAST_PAPER, "9708 Nov 2022 Paper 2 Q2", 0.90, True),
            (ResourceType.TEXTBOOK, "Economics Textbook Ch 5", 0.85, True),
            (ResourceType.USER_UPLOAD, "Student Notes on Fiscal Policy", 0.80, False),
            (ResourceType.PAST_PAPER, "9708 June 2021 Paper 2 Q4", 0.75, True),
            (ResourceType.TEXTBOOK, "Economics Workbook Ch 5", 0.70, True),
            (ResourceType.USER_UPLOAD, "Summary Notes", 0.65, False),
        ]

        created_resources = []
        for resource_type, title, relevance, admin_tagged in resources_data:
            resource = Resource(
                id=uuid4(),
                resource_type=resource_type,
                title=title,
                file_path=f"/fake/{title.replace(' ', '_').lower()}.pdf",
                uploaded_by_student_id=student.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_{title[:10]}"
            )
            db_session.add(resource)
            created_resources.append((resource, relevance, admin_tagged))

        db_session.commit()

        # Link resources to syllabus point with relevance scores
        for resource, relevance, admin_tagged in created_resources:
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=relevance,
                tagged_by_admin=admin_tagged
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Trigger auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Verify top 5 returned in correct order
        assert len(selected) == 5

        # Verify order by relevance_score DESC
        assert selected[0]['relevance_score'] == 1.0  # Syllabus
        assert selected[0]['title'] == "Cambridge Syllabus 9708"

        assert selected[1]['relevance_score'] == 0.95  # Past paper 1
        assert selected[1]['title'] == "9708 June 2023 Paper 2 Q3"

        assert selected[2]['relevance_score'] == 0.90  # Past paper 2
        assert selected[2]['title'] == "9708 Nov 2022 Paper 2 Q2"

        assert selected[3]['relevance_score'] == 0.85  # Textbook
        assert selected[3]['title'] == "Economics Textbook Ch 5"

        assert selected[4]['relevance_score'] == 0.80  # Student notes
        assert selected[4]['title'] == "Student Notes on Fiscal Policy"

        # Verify lower-ranked resources excluded
        resource_ids = [r['resource_id'] for r in selected]
        assert str(created_resources[5][0].id) not in resource_ids  # 0.75
        assert str(created_resources[6][0].id) not in resource_ids  # 0.70
        assert str(created_resources[7][0].id) not in resource_ids  # 0.65

    def test_respects_limit_parameter(self, db_session: Session, student):
        """Should respect custom limit parameter (default 5)."""
        syllabus_point_id = "9708.5.2"

        # Create 10 resources
        for i in range(10):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER,
                title=f"Past Paper {i+1}",
                file_path=f"/fake/paper{i+1}.pdf",
                uploaded_by_student_id=student.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_paper{i+1}"
            )
            db_session.add(resource)
            db_session.commit()

            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.9 - (i * 0.05),
                tagged_by_admin=True
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Test limit=3
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=3
        )

        assert len(selected) == 3
        assert selected[0]['title'] == "Past Paper 1"
        assert selected[1]['title'] == "Past Paper 2"
        assert selected[2]['title'] == "Past Paper 3"

        # Test limit=10
        selected_all = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=10
        )

        assert len(selected_all) == 10

    def test_excludes_pending_and_private_resources(self, db_session: Session, student):
        """Should only include PUBLIC approved resources in auto-selection."""
        syllabus_point_id = "9708.5.3"

        # Create resources with different visibility states
        public_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="Public Approved Resource",
            file_path="/fake/public.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_public"
        )

        pending_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Pending Review Resource",
            file_path="/fake/pending.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_pending"
        )

        private_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Private Resource",
            file_path="/fake/private.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig_private"
        )

        public_unapproved = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Public But Unapproved",
            file_path="/fake/unapproved.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=False,
            signature="sig_unapproved"
        )

        db_session.add_all([public_resource, pending_resource, private_resource, public_unapproved])
        db_session.commit()

        # Link all to syllabus point with high relevance
        for resource in [public_resource, pending_resource, private_resource, public_unapproved]:
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.95,
                tagged_by_admin=True
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Trigger auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Should only return the public approved resource
        assert len(selected) == 1
        assert selected[0]['title'] == "Public Approved Resource"

    def test_end_to_end_with_llm_prompt_formatting(self, db_session: Session, student):
        """Test complete workflow: select resources and format for LLM prompt."""
        syllabus_point_id = "9708.5.4"

        # Create syllabus resource
        syllabus = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="9708 Syllabus - Fiscal Policy",
            file_path="/fake/syllabus.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_syllabus",
            source_url="https://www.cambridgeinternational.org/9708"
        )

        # Create past paper with extracted text
        past_paper = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="9708 June 2023 Paper 2 Q3",
            file_path="/fake/pastpaper.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper",
            metadata={"extracted_text": "Explain how fiscal policy can be used to reduce inflation..."}
        )

        db_session.add_all([syllabus, past_paper])
        db_session.commit()

        # Link to syllabus point
        SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=syllabus.id,
            relevance_score=1.0,
            tagged_by_admin=True
        )
        SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=past_paper.id,
            relevance_score=0.9,
            tagged_by_admin=True
        )

        db_session.commit()

        # Step 1: Auto-select resources
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        assert len(selected) == 2

        # Step 2: Format for LLM prompt
        prompt = prepare_resources_for_llm_prompt(
            selected_resources=selected,
            session=db_session
        )

        # Verify prompt formatting
        assert "--- REFERENCE RESOURCES ---" in prompt
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "9708 Syllabus - Fiscal Policy" in prompt
        assert "(Relevance: 100%)" in prompt
        assert "9708 June 2023 Paper 2 Q3" in prompt
        assert "(Relevance: 90%)" in prompt
        assert "Source: https://www.cambridgeinternational.org/9708" in prompt

    def test_tracks_resource_usage_after_generation(self, db_session: Session, student):
        """Test tracking which resources were used in explanation generation."""
        syllabus_point_id = "9708.5.5"

        # Create explanation
        explanation = GeneratedExplanation(
            id=uuid4(),
            syllabus_point_id=syllabus_point_id,
            student_id=student.id,
            content="Fiscal policy explanation using syllabus and past papers...",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            prompt_tokens=200,
            completion_tokens=400
        )
        db_session.add(explanation)
        db_session.commit()

        # Create resources
        resources = []
        for i in range(3):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER if i < 2 else ResourceType.TEXTBOOK,
                title=f"Resource {i+1}",
                file_path=f"/fake/resource{i+1}.pdf",
                uploaded_by_student_id=student.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_res{i+1}"
            )
            db_session.add(resource)
            resources.append(resource)

        db_session.commit()

        # Track usage with different contribution weights
        weights = [0.9, 0.7, 0.5]
        for resource, weight in zip(resources, weights):
            track_resource_usage(
                generated_explanation_id=explanation.id,
                resource_id=resource.id,
                contribution_weight=weight,
                session=db_session
            )

        # Verify all usage records created
        usages = db_session.exec(
            select(ExplanationResourceUsage)
            .where(ExplanationResourceUsage.generated_explanation_id == explanation.id)
        ).all()

        assert len(usages) == 3

        # Verify contribution weights
        usage_weights = {u.contribution_weight for u in usages}
        assert usage_weights == {0.9, 0.7, 0.5}

        # Verify resource IDs
        usage_resource_ids = {u.resource_id for u in usages}
        expected_resource_ids = {r.id for r in resources}
        assert usage_resource_ids == expected_resource_ids

    def test_handles_no_resources_gracefully(self, db_session: Session):
        """Should return empty list when no resources linked to syllabus point."""
        syllabus_point_id = "9708.5.999"

        # No resources created for this syllabus point

        # Trigger auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        assert selected == []

        # Format prompt with empty resources
        prompt = prepare_resources_for_llm_prompt(
            selected_resources=selected,
            session=db_session
        )

        assert prompt == ""

    def test_mixed_resource_types_prioritize_by_relevance(self, db_session: Session, student):
        """Verify different resource types are prioritized purely by relevance_score."""
        syllabus_point_id = "9708.5.6"

        # Create mixed resource types with intentionally mixed scores
        mixed_resources = [
            (ResourceType.USER_UPLOAD, "Student Notes", 0.95),
            (ResourceType.SYLLABUS, "Official Syllabus", 1.0),
            (ResourceType.TEXTBOOK, "Textbook Chapter", 0.85),
            (ResourceType.PAST_PAPER, "Past Paper Q1", 0.90),
        ]

        for resource_type, title, relevance in mixed_resources:
            resource = Resource(
                id=uuid4(),
                resource_type=resource_type,
                title=title,
                file_path=f"/fake/{title.replace(' ', '_').lower()}.pdf",
                uploaded_by_student_id=student.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_{title[:5]}"
            )
            db_session.add(resource)
            db_session.commit()

            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=relevance,
                tagged_by_admin=True
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Auto-select
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Verify ordered by relevance regardless of type
        assert len(selected) == 4
        assert selected[0]['title'] == "Official Syllabus"  # 1.0
        assert selected[1]['title'] == "Student Notes"  # 0.95
        assert selected[2]['title'] == "Past Paper Q1"  # 0.90
        assert selected[3]['title'] == "Textbook Chapter"  # 0.85


class TestMultiTenantAutoSelection:
    """Test auto-selection respects multi-tenant isolation."""

    def test_student_only_sees_public_approved_resources(self, db_session: Session):
        """Student A should not see Student B's private resources in auto-selection."""
        syllabus_point_id = "9708.5.7"

        student_a = Student(
            id=uuid4(),
            email="studenta@test.com",
            full_name="Student A",
            is_admin=False,
            hashed_password="hash_a"
        )

        student_b = Student(
            id=uuid4(),
            email="studentb@test.com",
            full_name="Student B",
            is_admin=False,
            hashed_password="hash_b"
        )

        db_session.add_all([student_a, student_b])
        db_session.commit()

        # Student A uploads public resource
        public_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Student A Public Notes",
            file_path="/fake/student_a_public.pdf",
            uploaded_by_student_id=student_a.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_a_public"
        )

        # Student B uploads private resource
        private_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Student B Private Notes",
            file_path="/fake/student_b_private.pdf",
            uploaded_by_student_id=student_b.id,
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig_b_private"
        )

        db_session.add_all([public_resource, private_resource])
        db_session.commit()

        # Link both to same syllabus point
        for resource in [public_resource, private_resource]:
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.9,
                tagged_by_admin=False
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Auto-selection (simulates any student viewing)
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Should only return public approved resource
        assert len(selected) == 1
        assert selected[0]['title'] == "Student A Public Notes"
        assert selected[0]['resource'].uploaded_by_student_id == student_a.id
