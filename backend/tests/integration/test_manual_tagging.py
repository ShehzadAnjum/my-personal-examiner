"""
Integration tests for admin manual tagging workflow.

Feature: 007-resource-bank-files (User Story 6)
Created: 2025-12-27

Tests end-to-end manual tagging workflow:
1. Admin searches for resources using full-text search
2. Admin tags resource to syllabus point with relevance score
3. Verify tag affects future auto-selections
4. Test search endpoint returns ranked results

Constitutional Compliance:
- FR-045: Admin creates adjustable relevance_score links
- FR-046: Page range metadata for textbooks
- FR-047: Full-text search on extracted PDF text
- FR-048: Keyword matching for past papers
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.enums import AddedBy, ResourceType, Visibility
from src.models.resource import Resource
from src.models.student import Student
from src.models.syllabus_point_resource import SyllabusPointResource
from src.services.resource_service import get_resources_for_syllabus_point


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin(db_session: Session):
    admin = Student(
        id=uuid4(),
        email="admin@test.com",
        full_name="Admin User",
        is_admin=True,
        hashed_password="hash_admin",
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def student(db_session: Session):
    student = Student(
        id=uuid4(),
        email="student@test.com",
        full_name="Student User",
        is_admin=False,
        hashed_password="hash_student",
    )
    db_session.add(student)
    db_session.commit()
    return student


class TestManualTaggingWorkflow:
    """Test end-to-end manual tagging workflow."""

    def test_admin_can_tag_resource_to_syllabus_point(self, client, admin, db_session):
        """Admin should be able to tag resource with custom relevance score."""
        # Create resource
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook Chapter 5 - Fiscal Policy",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )
        db_session.add(resource)
        db_session.commit()

        syllabus_point_id = uuid4()

        # Admin tags resource
        response = client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(syllabus_point_id), "relevance_score": 0.95},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 201
        data = response.json()

        assert data["resource_id"] == str(resource.id)
        assert data["syllabus_point_id"] == str(syllabus_point_id)
        assert data["relevance_score"] == 0.95
        assert data["added_by"] == "admin"

        # Verify in database
        tag = db_session.exec(
            select(SyllabusPointResource).where(
                SyllabusPointResource.resource_id == resource.id,
                SyllabusPointResource.syllabus_point_id == syllabus_point_id,
            )
        ).first()

        assert tag is not None
        assert tag.relevance_score == 0.95
        assert tag.added_by == AddedBy.ADMIN

    def test_tagged_resource_appears_in_auto_selection(self, client, admin, db_session):
        """Tagged resource should appear in auto-selection for that syllabus point."""
        syllabus_point_id = uuid4()

        # Create and tag resource
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="9708 June 2023 Paper 2 Q3 - Fiscal Policy",
            file_path="/fake/pastpaper.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper",
        )
        db_session.add(resource)
        db_session.commit()

        # Admin tags resource
        client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(syllabus_point_id), "relevance_score": 0.95},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        # Trigger auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id, session=db_session, limit=5
        )

        # Verify tagged resource is selected
        assert len(selected) == 1
        assert selected[0]["resource_id"] == str(resource.id)
        assert selected[0]["relevance_score"] == 0.95

    def test_non_admin_cannot_tag_resources(self, client, student, db_session):
        """Non-admin users should not be able to tag resources."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Test Resource",
            file_path="/fake/test.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_test",
        )
        db_session.add(resource)
        db_session.commit()

        # Student attempts to tag
        response = client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(uuid4()), "relevance_score": 0.9},
            headers={"Authorization": f"Bearer {student.id}"},
        )

        assert response.status_code == 403

    def test_validates_relevance_score_range(self, client, admin, db_session):
        """Should reject relevance_score outside [0, 1] range."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Test Resource",
            file_path="/fake/test.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_test",
        )
        db_session.add(resource)
        db_session.commit()

        # Try invalid score > 1.0
        response = client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(uuid4()), "relevance_score": 1.5},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 400

    def test_admin_can_update_existing_tag(self, client, admin, db_session):
        """Admin should be able to update relevance_score of existing tag."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Test Resource",
            file_path="/fake/test.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_test",
        )
        db_session.add(resource)
        db_session.commit()

        syllabus_point_id = uuid4()

        # Create initial tag with 0.7
        response1 = client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(syllabus_point_id), "relevance_score": 0.7},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response1.status_code == 201
        assert response1.json()["relevance_score"] == 0.7

        # Update tag to 0.95
        response2 = client.post(
            f"/api/resources/{resource.id}/tag",
            json={"syllabus_point_id": str(syllabus_point_id), "relevance_score": 0.95},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response2.status_code == 201
        assert response2.json()["relevance_score"] == 0.95

        # Verify only one tag exists
        tags = db_session.exec(
            select(SyllabusPointResource).where(
                SyllabusPointResource.resource_id == resource.id
            )
        ).all()

        assert len(tags) == 1
        assert tags[0].relevance_score == 0.95


class TestFullTextSearch:
    """Test full-text search endpoint."""

    def test_search_finds_resources_by_title(self, client, db_session, admin):
        """Search should find resources matching title keywords."""
        # Create resources with different titles
        fiscal_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Fiscal Policy and Government Spending",
            file_path="/fake/fiscal.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_fiscal",
        )

        monetary_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Monetary Policy and Interest Rates",
            file_path="/fake/monetary.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_monetary",
        )

        db_session.add_all([fiscal_resource, monetary_resource])
        db_session.commit()

        # Search for "fiscal"
        response = client.get("/api/resources/search?query=fiscal&limit=20")

        assert response.status_code == 200
        results = response.json()

        # Should find fiscal resource
        titles = [r["title"] for r in results]
        assert "Fiscal Policy and Government Spending" in titles

    def test_search_finds_resources_by_metadata(self, client, db_session, admin):
        """Search should find resources matching metadata keywords."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Economics Question Paper",
            file_path="/fake/paper.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_paper",
            metadata={"tags": ["taxation", "budget-deficit"]},
        )
        db_session.add(resource)
        db_session.commit()

        # Search for "taxation"
        response = client.get("/api/resources/search?query=taxation&limit=20")

        assert response.status_code == 200
        results = response.json()

        # Should find resource by metadata
        assert len(results) >= 1
        resource_ids = [r["resource_id"] for r in results]
        assert str(resource.id) in resource_ids

    def test_search_respects_limit_parameter(self, client, db_session, admin):
        """Search should respect limit parameter."""
        # Create 10 resources
        for i in range(10):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Economics Textbook {i+1}",
                file_path=f"/fake/textbook{i+1}.pdf",
                uploaded_by_student_id=admin.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_textbook{i+1}",
            )
            db_session.add(resource)

        db_session.commit()

        # Search with limit=5
        response = client.get("/api/resources/search?query=economics&limit=5")

        assert response.status_code == 200
        results = response.json()

        assert len(results) <= 5

    def test_search_returns_rank_scores(self, client, db_session, admin):
        """Search should return ts_rank scores."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Fiscal Policy Economics",
            file_path="/fake/fiscal.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_fiscal",
        )
        db_session.add(resource)
        db_session.commit()

        response = client.get("/api/resources/search?query=fiscal&limit=20")

        assert response.status_code == 200
        results = response.json()

        # Verify rank scores included
        assert len(results) >= 1
        assert "rank" in results[0]
        assert isinstance(results[0]["rank"], float)

    def test_search_filters_by_public_visibility(self, client, db_session, admin):
        """Search should only return PUBLIC resources by default."""
        # Create public resource
        public_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Public Fiscal Policy Notes",
            file_path="/fake/public.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_public",
        )

        # Create private resource
        private_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Private Fiscal Policy Notes",
            file_path="/fake/private.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig_private",
        )

        db_session.add_all([public_resource, private_resource])
        db_session.commit()

        # Search with public_only=true (default)
        response = client.get(
            "/api/resources/search?query=fiscal&public_only=true&limit=20"
        )

        assert response.status_code == 200
        results = response.json()

        titles = [r["title"] for r in results]
        assert "Public Fiscal Policy Notes" in titles
        assert "Private Fiscal Policy Notes" not in titles


class TestGetResourcesForSyllabusPoint:
    """Test GET /api/syllabus/{point_id}/resources endpoint."""

    def test_returns_tagged_resources_for_syllabus_point(self, client, db_session, admin):
        """Should return resources tagged to syllabus point."""
        syllabus_point_id = uuid4()

        # Create and tag resources
        resource1 = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="Official Syllabus",
            file_path="/fake/syllabus.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_syllabus",
        )

        resource2 = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Textbook Chapter",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )

        db_session.add_all([resource1, resource2])
        db_session.commit()

        # Tag resources
        tag1 = SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=resource1.id,
            relevance_score=1.0,
            added_by=AddedBy.ADMIN,
        )

        tag2 = SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=resource2.id,
            relevance_score=0.85,
            added_by=AddedBy.ADMIN,
        )

        db_session.add_all([tag1, tag2])
        db_session.commit()

        # Get resources for syllabus point
        response = client.get(f"/api/syllabus/{syllabus_point_id}/resources?limit=5")

        assert response.status_code == 200
        results = response.json()

        # Should return both resources in order
        assert len(results) == 2
        assert results[0]["title"] == "Official Syllabus"  # 1.0 relevance
        assert results[0]["relevance_score"] == 1.0
        assert results[1]["title"] == "Textbook Chapter"  # 0.85 relevance
        assert results[1]["relevance_score"] == 0.85

    def test_orders_resources_by_relevance_score_desc(self, client, db_session, admin):
        """Should order resources by relevance_score descending."""
        syllabus_point_id = uuid4()

        # Create resources with different relevance scores
        scores = [0.6, 0.9, 0.7, 0.95, 0.8]
        resources = []

        for i, score in enumerate(scores):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Resource {i+1} (Score: {score})",
                file_path=f"/fake/resource{i+1}.pdf",
                uploaded_by_student_id=admin.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_resource{i+1}",
            )
            db_session.add(resource)
            resources.append((resource, score))

        db_session.commit()

        # Tag all resources
        for resource, score in resources:
            tag = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=score,
                added_by=AddedBy.ADMIN,
            )
            db_session.add(tag)

        db_session.commit()

        # Get resources
        response = client.get(f"/api/syllabus/{syllabus_point_id}/resources?limit=5")

        assert response.status_code == 200
        results = response.json()

        # Verify descending order
        assert len(results) == 5
        assert results[0]["relevance_score"] == 0.95  # Highest
        assert results[1]["relevance_score"] == 0.9
        assert results[2]["relevance_score"] == 0.8
        assert results[3]["relevance_score"] == 0.7
        assert results[4]["relevance_score"] == 0.6

    def test_respects_limit_parameter(self, client, db_session, admin):
        """Should respect limit parameter."""
        syllabus_point_id = uuid4()

        # Create 10 tagged resources
        for i in range(10):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Resource {i+1}",
                file_path=f"/fake/resource{i+1}.pdf",
                uploaded_by_student_id=admin.id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_resource{i+1}",
            )
            db_session.add(resource)
            db_session.commit()

            tag = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.9,
                added_by=AddedBy.ADMIN,
            )
            db_session.add(tag)

        db_session.commit()

        # Test limit=3
        response = client.get(f"/api/syllabus/{syllabus_point_id}/resources?limit=3")

        assert response.status_code == 200
        results = response.json()

        assert len(results) == 3


class TestPageRangeMetadata:
    """Test page range metadata functionality."""

    def test_admin_can_add_page_range(self, client, admin, db_session):
        """Admin should be able to add page range to textbook resource."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
            metadata={},
        )
        db_session.add(resource)
        db_session.commit()

        # Add page range
        response = client.post(
            f"/api/resources/{resource.id}/page-range?page_range=245-267",
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["page_range"] == "245-267"

        # Verify in database
        db_session.refresh(resource)
        assert "page_range" in resource.resource_metadata
        assert resource.resource_metadata["page_range"] == "245-267"

    def test_validates_page_range_format(self, client, admin, db_session):
        """Should reject invalid page range formats."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=admin.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )
        db_session.add(resource)
        db_session.commit()

        # Try invalid format
        response = client.post(
            f"/api/resources/{resource.id}/page-range?page_range=invalid",
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 400

    def test_non_admin_cannot_add_page_range(self, client, student, db_session):
        """Non-admin should not be able to add page ranges."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )
        db_session.add(resource)
        db_session.commit()

        response = client.post(
            f"/api/resources/{resource.id}/page-range?page_range=245-267",
            headers={"Authorization": f"Bearer {student.id}"},
        )

        assert response.status_code == 403
