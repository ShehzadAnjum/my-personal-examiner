"""
Unit tests for student resource quota enforcement.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Tests 100 resources/student quota enforcement and error messages.

Constitutional Compliance:
- FR-050: Maximum 100 resources per student
- FR-052: Reject uploads when quota exceeded
"""

from uuid import uuid4

import pytest
from sqlmodel import Session

from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.services.file_storage_service import validate_student_quota


class TestValidateStudentQuota:
    """Test quota validation function."""

    def test_within_quota_when_zero_resources(self, db_session: Session):
        """Should allow upload when student has 0 resources."""
        student_id = uuid4()

        within_quota, count = validate_student_quota(student_id, db_session)

        assert within_quota is True
        assert count == 0

    def test_within_quota_when_under_100(self, db_session: Session):
        """Should allow upload when student has <100 resources."""
        student_id = uuid4()

        # Create 50 resources
        for i in range(50):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}",
                file_path=f"/fake/path{i}.pdf",
                uploaded_by_student_id=student_id,
                signature=f"sig_{i}",
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                s3_sync_status=S3SyncStatus.PENDING
            )
            db_session.add(resource)
        db_session.commit()

        within_quota, count = validate_student_quota(student_id, db_session)

        assert within_quota is True
        assert count == 50

    def test_within_quota_at_99_resources(self, db_session: Session):
        """Should allow upload when student has exactly 99 resources."""
        student_id = uuid4()

        # Create 99 resources
        for i in range(99):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}",
                file_path=f"/fake/path{i}.pdf",
                uploaded_by_student_id=student_id,
                signature=f"sig_{i}",
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                s3_sync_status=S3SyncStatus.PENDING
            )
            db_session.add(resource)
        db_session.commit()

        within_quota, count = validate_student_quota(student_id, db_session)

        assert within_quota is True
        assert count == 99

    def test_quota_exceeded_at_100_resources(self, db_session: Session):
        """Should reject upload when student has 100 resources."""
        student_id = uuid4()

        # Create 100 resources (quota limit)
        for i in range(100):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}",
                file_path=f"/fake/path{i}.pdf",
                uploaded_by_student_id=student_id,
                signature=f"sig_{i}",
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                s3_sync_status=S3SyncStatus.PENDING
            )
            db_session.add(resource)
        db_session.commit()

        within_quota, count = validate_student_quota(student_id, db_session)

        assert within_quota is False
        assert count == 100

    def test_quota_only_counts_student_own_resources(self, db_session: Session):
        """Should only count resources uploaded by student, not others."""
        student_a = uuid4()
        student_b = uuid4()

        # Student A uploads 50 resources
        for i in range(50):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Student A Resource {i}",
                file_path=f"/fake/a/path{i}.pdf",
                uploaded_by_student_id=student_a,
                signature=f"sig_a_{i}",
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                s3_sync_status=S3SyncStatus.PENDING
            )
            db_session.add(resource)

        # Student B uploads 5 resources
        for i in range(5):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Student B Resource {i}",
                file_path=f"/fake/b/path{i}.pdf",
                uploaded_by_student_id=student_b,
                signature=f"sig_b_{i}",
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                s3_sync_status=S3SyncStatus.PENDING
            )
            db_session.add(resource)

        db_session.commit()

        # Check Student A's quota
        within_quota_a, count_a = validate_student_quota(student_a, db_session)
        assert within_quota_a is True
        assert count_a == 50  # Only Student A's resources

        # Check Student B's quota
        within_quota_b, count_b = validate_student_quota(student_b, db_session)
        assert within_quota_b is True
        assert count_b == 5  # Only Student B's resources
