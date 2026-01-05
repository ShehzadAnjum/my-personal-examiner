"""
Integration tests for multi-tenant resource isolation.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Tests visibility filters and student_id-scoped access control.

Constitutional Compliance:
- Principle V: Multi-tenant isolation mandatory
- FR-037: Visibility filters enforce access control
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app
from src.models.enums import ResourceType, Visibility
from src.models.resource import Resource
from src.models.student import Student


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def student_a(db_session: Session):
    student = Student(id=uuid4(), email="a@test.com", full_name="Student A", is_admin=False, hashed_password="hash")
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def student_b(db_session: Session):
    student = Student(id=uuid4(), email="b@test.com", full_name="Student B", is_admin=False, hashed_password="hash")
    db_session.add(student)
    db_session.commit()
    return student


class TestMultiTenantIsolation:
    """Test resource isolation between students."""

    def test_student_cannot_access_another_private_resource(self, client, student_a, student_b, db_session):
        """Student A cannot access Student B's private resource."""
        # Student B's private resource
        resource_b = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD, title="B's Notes",
            file_path="/fake/b.pdf", uploaded_by_student_id=student_b.id,
            visibility=Visibility.PRIVATE, signature="sig_b"
        )
        db_session.add(resource_b)
        db_session.commit()

        # Student A tries to access
        response = client.get(
            f"/api/resources/{resource_b.id}",
            headers={"Authorization": f"Bearer {student_a.id}"}
        )

        assert response.status_code == 403

    def test_student_can_access_own_private_resource(self, client, student_a, db_session):
        """Student A can access own private resource."""
        resource_a = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD, title="A's Notes",
            file_path="/fake/a.pdf", uploaded_by_student_id=student_a.id,
            visibility=Visibility.PRIVATE, signature="sig_a"
        )
        db_session.add(resource_a)
        db_session.commit()

        response = client.get(
            f"/api/resources/{resource_a.id}",
            headers={"Authorization": f"Bearer {student_a.id}"}
        )

        assert response.status_code == 200

    def test_student_can_access_public_resources(self, client, student_a, student_b, db_session):
        """All students can access public resources."""
        public_resource = Resource(
            id=uuid4(), resource_type=ResourceType.SYLLABUS, title="Public Syllabus",
            file_path="/fake/syllabus.pdf", visibility=Visibility.PUBLIC,
            admin_approved=True, signature="sig_public"
        )
        db_session.add(public_resource)
        db_session.commit()

        # Both students can access
        response_a = client.get(f"/api/resources/{public_resource.id}", headers={"Authorization": f"Bearer {student_a.id}"})
        response_b = client.get(f"/api/resources/{public_resource.id}", headers={"Authorization": f"Bearer {student_b.id}"})

        assert response_a.status_code == 200
        assert response_b.status_code == 200

    def test_list_resources_filters_by_visibility(self, client, student_a, student_b, db_session):
        """List endpoint filters resources by visibility."""
        # Public resource (visible to all)
        public = Resource(
            id=uuid4(), resource_type=ResourceType.SYLLABUS, title="Public",
            file_path="/fake/public.pdf", visibility=Visibility.PUBLIC, signature="sig1"
        )
        # Student A's private (only A can see)
        private_a = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD, title="A Private",
            file_path="/fake/a.pdf", uploaded_by_student_id=student_a.id,
            visibility=Visibility.PRIVATE, signature="sig2"
        )
        # Student B's private (only B can see)
        private_b = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD, title="B Private",
            file_path="/fake/b.pdf", uploaded_by_student_id=student_b.id,
            visibility=Visibility.PRIVATE, signature="sig3"
        )

        db_session.add_all([public, private_a, private_b])
        db_session.commit()

        # Student A lists resources
        response_a = client.get("/api/resources", headers={"Authorization": f"Bearer {student_a.id}"})
        data_a = response_a.json()['resources']
        titles_a = [r['title'] for r in data_a]

        assert "Public" in titles_a
        assert "A Private" in titles_a
        assert "B Private" not in titles_a  # Cannot see B's private

        # Student B lists resources
        response_b = client.get("/api/resources", headers={"Authorization": f"Bearer {student_b.id}"})
        data_b = response_b.json()['resources']
        titles_b = [r['title'] for r in data_b]

        assert "Public" in titles_b
        assert "B Private" in titles_b
        assert "A Private" not in titles_b  # Cannot see A's private
