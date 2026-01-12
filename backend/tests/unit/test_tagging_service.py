"""
Unit tests for resource tagging service.

Feature: 007-resource-bank-files (User Story 6)
Created: 2025-12-27

Tests admin tagging functionality, relevance score validation, and full-text search.

Constitutional Compliance:
- FR-045: Admin creates syllabus_point_resources links with adjustable relevance
- FR-046: Page range metadata for textbooks
- FR-047: Full-text search on extracted PDF text
- FR-048: Keyword matching for past paper questions
"""

from uuid import uuid4

import pytest
from sqlmodel import Session

from src.models.enums import AddedBy, ResourceType, Visibility
from src.models.resource import Resource
from src.models.syllabus_point_resource import SyllabusPointResource
from src.services.tagging_service import (
    add_page_range_metadata,
    create_tag,
    search_resources,
    validate_page_range,
)


class TestCreateTag:
    """Test create_tag function for manual tagging."""

    def test_creates_new_tag(self, db_session: Session):
        """Should create new SyllabusPointResource link."""
        student_id = uuid4()
        syllabus_point_id = uuid4()

        # Create resource
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook Chapter 5",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )
        db_session.add(resource)
        db_session.commit()

        # Create tag
        tag = create_tag(
            resource_id=resource.id,
            syllabus_point_id=syllabus_point_id,
            relevance_score=0.95,
            added_by=AddedBy.ADMIN,
            session=db_session,
        )

        # Verify tag created
        assert tag is not None
        assert tag.resource_id == resource.id
        assert tag.syllabus_point_id == syllabus_point_id
        assert tag.relevance_score == 0.95
        assert tag.added_by == AddedBy.ADMIN

        # Verify in database
        db_tag = db_session.exec(
            db_session.query(SyllabusPointResource)
            .filter(
                SyllabusPointResource.resource_id == resource.id,
                SyllabusPointResource.syllabus_point_id == syllabus_point_id,
            )
            .statement
        ).first()
        assert db_tag is not None

    def test_updates_existing_tag(self, db_session: Session):
        """Should update existing tag if resource already tagged to syllabus point."""
        student_id = uuid4()
        syllabus_point_id = uuid4()

        # Create resource
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Past Paper Question",
            file_path="/fake/pastpaper.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper",
        )
        db_session.add(resource)
        db_session.commit()

        # Create initial tag with 0.7 relevance
        initial_tag = create_tag(
            resource_id=resource.id,
            syllabus_point_id=syllabus_point_id,
            relevance_score=0.7,
            added_by=AddedBy.ADMIN,
            session=db_session,
        )

        assert initial_tag.relevance_score == 0.7

        # Update tag to 0.95 relevance
        updated_tag = create_tag(
            resource_id=resource.id,
            syllabus_point_id=syllabus_point_id,
            relevance_score=0.95,
            added_by=AddedBy.ADMIN,
            session=db_session,
        )

        # Verify updated
        assert updated_tag.relevance_score == 0.95
        assert updated_tag.resource_id == resource.id
        assert updated_tag.syllabus_point_id == syllabus_point_id

    def test_validates_relevance_score_range(self, db_session: Session):
        """Should reject relevance_score outside [0, 1] range."""
        student_id = uuid4()

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Test Resource",
            file_path="/fake/test.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_test",
        )
        db_session.add(resource)
        db_session.commit()

        # Test score > 1.0
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            create_tag(
                resource_id=resource.id,
                syllabus_point_id=uuid4(),
                relevance_score=1.5,
                added_by=AddedBy.ADMIN,
                session=db_session,
            )

        # Test score < 0.0
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            create_tag(
                resource_id=resource.id,
                syllabus_point_id=uuid4(),
                relevance_score=-0.1,
                added_by=AddedBy.ADMIN,
                session=db_session,
            )

    def test_raises_error_if_resource_not_found(self, db_session: Session):
        """Should raise HTTPException if resource doesn't exist."""
        from fastapi import HTTPException

        non_existent_id = uuid4()

        with pytest.raises(HTTPException, match="not found"):
            create_tag(
                resource_id=non_existent_id,
                syllabus_point_id=uuid4(),
                relevance_score=0.9,
                added_by=AddedBy.ADMIN,
                session=db_session,
            )

    def test_supports_different_added_by_sources(self, db_session: Session):
        """Should support SYSTEM, ADMIN, and STUDENT as added_by values."""
        student_id = uuid4()
        syllabus_point_id = uuid4()

        # Create 3 resources
        for added_by in [AddedBy.SYSTEM, AddedBy.ADMIN, AddedBy.STUDENT]:
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Resource for {added_by.value}",
                file_path=f"/fake/{added_by.value}.pdf",
                uploaded_by_student_id=student_id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_{added_by.value}",
            )
            db_session.add(resource)
            db_session.commit()

            tag = create_tag(
                resource_id=resource.id,
                syllabus_point_id=syllabus_point_id,
                relevance_score=0.8,
                added_by=added_by,
                session=db_session,
            )

            assert tag.added_by == added_by


class TestSearchResources:
    """Test search_resources full-text search function."""

    def test_searches_title_field(self, db_session: Session):
        """Should find resources matching title."""
        student_id = uuid4()

        # Create resources with different titles
        fiscal_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Fiscal Policy and Government Spending",
            file_path="/fake/fiscal.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_fiscal",
        )

        monetary_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Monetary Policy and Interest Rates",
            file_path="/fake/monetary.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_monetary",
        )

        db_session.add_all([fiscal_resource, monetary_resource])
        db_session.commit()

        # Search for "fiscal"
        results = search_resources(query="fiscal", session=db_session, limit=20)

        # Should find fiscal resource
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert "Fiscal Policy and Government Spending" in titles

    def test_searches_metadata_field(self, db_session: Session):
        """Should find resources matching metadata text."""
        student_id = uuid4()

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Economics Question Paper",
            file_path="/fake/paper.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_paper",
            metadata={"tags": ["taxation", "budget-deficit", "fiscal-policy"]},
        )
        db_session.add(resource)
        db_session.commit()

        # Search for "taxation"
        results = search_resources(query="taxation", session=db_session, limit=20)

        # Should find resource by metadata
        assert len(results) >= 1
        resource_ids = [r["resource_id"] for r in results]
        assert str(resource.id) in resource_ids

    def test_respects_visibility_filter(self, db_session: Session):
        """Should filter results by visibility."""
        student_id = uuid4()

        # Create public resource
        public_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Public Fiscal Policy Notes",
            file_path="/fake/public.pdf",
            uploaded_by_student_id=student_id,
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
            uploaded_by_student_id=student_id,
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig_private",
        )

        db_session.add_all([public_resource, private_resource])
        db_session.commit()

        # Search with PUBLIC filter
        results = search_resources(
            query="fiscal",
            session=db_session,
            limit=20,
            visibility_filter=Visibility.PUBLIC,
        )

        # Should only return public resource
        titles = [r["title"] for r in results]
        assert "Public Fiscal Policy Notes" in titles
        assert "Private Fiscal Policy Notes" not in titles

    def test_respects_limit_parameter(self, db_session: Session):
        """Should limit results to specified number."""
        student_id = uuid4()

        # Create 10 resources
        for i in range(10):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Economics Textbook {i+1}",
                file_path=f"/fake/textbook{i+1}.pdf",
                uploaded_by_student_id=student_id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_textbook{i+1}",
            )
            db_session.add(resource)

        db_session.commit()

        # Search with limit=5
        results = search_resources(query="economics", session=db_session, limit=5)

        # Should return max 5 results
        assert len(results) <= 5

    def test_returns_rank_scores(self, db_session: Session):
        """Should include ts_rank scores in results."""
        student_id = uuid4()

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Fiscal Policy Economics",
            file_path="/fake/fiscal.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_fiscal",
        )
        db_session.add(resource)
        db_session.commit()

        results = search_resources(query="fiscal", session=db_session, limit=20)

        # Verify rank field exists
        assert len(results) >= 1
        assert "rank" in results[0]
        assert isinstance(results[0]["rank"], float)

    def test_returns_empty_list_when_no_matches(self, db_session: Session):
        """Should return empty list when no resources match query."""
        results = search_resources(
            query="nonexistentkeyword12345", session=db_session, limit=20
        )

        assert results == []


class TestPageRangeValidation:
    """Test validate_page_range and add_page_range_metadata functions."""

    def test_validates_single_page(self):
        """Should accept single page number."""
        assert validate_page_range("245") is True
        assert validate_page_range("1") is True
        assert validate_page_range("999") is True

    def test_validates_page_range(self):
        """Should accept page range format."""
        assert validate_page_range("245-267") is True
        assert validate_page_range("1-10") is True
        assert validate_page_range("100-200") is True

    def test_validates_comma_separated_pages(self):
        """Should accept comma-separated pages."""
        assert validate_page_range("245, 250, 255") is True
        assert validate_page_range("1, 5, 10, 15") is True

    def test_rejects_invalid_formats(self):
        """Should reject invalid page range formats."""
        assert validate_page_range("abc") is False
        assert validate_page_range("245-abc") is False
        assert validate_page_range("245-100") is False  # End < start
        assert validate_page_range("") is False
        assert validate_page_range(None) is False

    def test_adds_page_range_to_metadata(self, db_session: Session):
        """Should add page_range to resource metadata."""
        student_id = uuid4()

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
            metadata={},
        )
        db_session.add(resource)
        db_session.commit()

        # Add page range
        updated_resource = add_page_range_metadata(
            resource_id=resource.id, page_range="245-267", session=db_session
        )

        # Verify metadata updated
        assert updated_resource.resource_metadata is not None
        assert "page_range" in updated_resource.resource_metadata
        assert updated_resource.resource_metadata["page_range"] == "245-267"

    def test_raises_error_for_invalid_page_range(self, db_session: Session):
        """Should raise ValueError for invalid page range."""
        student_id = uuid4()

        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook",
        )
        db_session.add(resource)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid page_range format"):
            add_page_range_metadata(
                resource_id=resource.id, page_range="invalid", session=db_session
            )

    def test_raises_error_if_resource_not_found(self, db_session: Session):
        """Should raise HTTPException if resource doesn't exist."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException, match="not found"):
            add_page_range_metadata(
                resource_id=uuid4(), page_range="245-267", session=db_session
            )
