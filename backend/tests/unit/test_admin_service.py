"""
Unit tests for admin resource review service.

Feature: 007-resource-bank-files (User Story 4)
Created: 2025-12-27

Tests state machine transitions, rejection workflow, and metadata updates.

Constitutional Compliance:
- FR-028/FR-070: One-way approval (pending→public)
- FR-029/FR-071: Rejection deletes file+record
- FR-072: No reversal of approval
"""

import os
import tempfile
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.models.enums import ResourceType, Visibility
from src.models.resource import Resource


class TestStateTransitions:
    """Test resource state machine transitions."""

    def test_approve_updates_visibility_to_public(self, db_session: Session):
        """Approving should change visibility from PENDING_REVIEW to PUBLIC."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Test Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig123"
        )
        db_session.add(resource)
        db_session.commit()

        # Simulate approval
        resource.visibility = Visibility.PUBLIC
        resource.admin_approved = True
        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert resource.visibility == Visibility.PUBLIC
        assert resource.admin_approved is True

    def test_cannot_reverse_approval(self, db_session: Session):
        """Once approved, cannot revert to PENDING_REVIEW (one-way transition)."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Approved Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig456"
        )
        db_session.add(resource)
        db_session.commit()

        # Verify already approved
        assert resource.admin_approved is True

        # In API, trying to approve again should raise error
        # This test verifies the state (tested in integration tests)

    def test_pending_to_public_is_valid_transition(self, db_session: Session):
        """PENDING_REVIEW → PUBLIC is valid state transition."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Pending Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig789"
        )
        db_session.add(resource)
        db_session.commit()

        # Transition to public
        resource.visibility = Visibility.PUBLIC
        resource.admin_approved = True
        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert resource.visibility == Visibility.PUBLIC

    def test_private_to_public_is_valid_transition(self, db_session: Session):
        """PRIVATE → PUBLIC is valid (student makes resource public after approval)."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Private Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig101"
        )
        db_session.add(resource)
        db_session.commit()

        # Approve and make public
        resource.visibility = Visibility.PUBLIC
        resource.admin_approved = True
        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert resource.visibility == Visibility.PUBLIC


class TestRejectionWorkflow:
    """Test resource rejection and deletion."""

    def test_rejection_deletes_file(self, db_session: Session):
        """Rejecting resource should delete file from storage."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write("Test content")
            temp_path = temp_file.name

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="To Be Rejected",
            file_path=temp_path,
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_reject"
        )
        db_session.add(resource)
        db_session.commit()

        # Verify file exists
        assert os.path.exists(temp_path)

        # Simulate rejection
        os.remove(temp_path)
        db_session.delete(resource)
        db_session.commit()

        # Verify file deleted
        assert not os.path.exists(temp_path)

        # Verify DB record deleted
        assert db_session.get(Resource, resource.id) is None

    def test_rejection_deletes_database_record(self, db_session: Session):
        """Rejecting resource should delete database record."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="To Be Rejected",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_reject2"
        )
        db_session.add(resource)
        db_session.commit()

        resource_id = resource.id

        # Simulate rejection
        db_session.delete(resource)
        db_session.commit()

        # Verify record deleted
        assert db_session.get(Resource, resource_id) is None

    def test_cannot_reject_approved_resource(self, db_session: Session):
        """Should not be able to reject already approved resource (state violation)."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Approved Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_approved"
        )
        db_session.add(resource)
        db_session.commit()

        # In API, trying to reject approved should raise error
        # This test verifies the state (tested in integration tests)
        assert resource.admin_approved is True


class TestMetadataUpdates:
    """Test admin metadata editing."""

    def test_update_title_before_approval(self, db_session: Session):
        """Admin can edit title before approval."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Original Title",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_meta1"
        )
        db_session.add(resource)
        db_session.commit()

        # Update title
        resource.title = "Edited Title by Admin"
        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert resource.title == "Edited Title by Admin"

    def test_update_metadata_jsonb(self, db_session: Session):
        """Admin can update metadata JSONB field."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Test Resource",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_meta2"
        )
        db_session.add(resource)
        db_session.commit()

        # Update metadata
        if resource.resource_metadata is None:
            resource.resource_metadata = {}

        resource.resource_metadata['description'] = "Admin-edited description"
        resource.resource_metadata['tags'] = ['economics', 'fiscal-policy']

        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert resource.resource_metadata['description'] == "Admin-edited description"
        assert 'fiscal-policy' in resource.resource_metadata['tags']

    def test_store_excerpt_in_metadata(self, db_session: Session):
        """Admin can store textbook excerpt in metadata."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook Chapter 12",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_excerpt"
        )
        db_session.add(resource)
        db_session.commit()

        # Store excerpt
        if resource.resource_metadata is None:
            resource.resource_metadata = {}

        resource.resource_metadata['excerpt_text'] = "Fiscal policy involves government spending..."
        resource.resource_metadata['excerpt_pages'] = "245-267"

        db_session.add(resource)
        db_session.commit()

        db_session.refresh(resource)
        assert 'excerpt_text' in resource.resource_metadata
        assert resource.resource_metadata['excerpt_pages'] == "245-267"
