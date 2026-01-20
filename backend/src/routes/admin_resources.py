"""
Admin Resource Review API routes.

Feature: 007-resource-bank-files (User Story 4)
Created: 2025-12-27

Admin endpoints for reviewing, approving, and rejecting user-uploaded resources.

Endpoints:
- GET /api/admin/resources/pending - List pending review resources
- GET /api/admin/resources/{id}/preview - Preview first 3 pages of PDF
- PUT /api/admin/resources/{id}/approve - Approve resource (visibility→public)
- PUT /api/admin/resources/{id}/reject - Reject and delete resource
- PUT /api/admin/resources/{id}/metadata - Edit resource metadata before approval

Constitutional Compliance:
- FR-028: Approve resources with one-way state transition
- FR-029: Reject resources with file+record deletion
- FR-070/FR-071/FR-072: Linear state machine enforcement
"""

import base64
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.database import get_session
from src.middleware.admin_auth import require_admin
from src.models.enums import Visibility
from src.models.resource import Resource
from src.models.student import Student

router = APIRouter(prefix="/api/admin/resources", tags=["Admin Resources"])


class PendingResourceResponse(BaseModel):
    """Response model for pending resource list."""
    id: str
    title: str
    resource_type: str
    uploaded_by_student_id: str
    student_name: str
    student_email: str
    upload_date: str
    file_size: int
    file_path: str


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates."""
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class PageRangeRequest(BaseModel):
    """Request model for textbook excerpt extraction."""
    start_page: int
    end_page: int


@router.get("/pending")
def list_pending_resources(
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> list[PendingResourceResponse]:
    """
    List all resources pending admin review.

    Filters resources by visibility=PENDING_REVIEW and returns with student info.

    Returns:
        List of pending resources with student name, upload date, file size

    Example:
        GET /api/admin/resources/pending
        Returns: [
            {
                "id": "uuid",
                "title": "My Economics Notes",
                "student_name": "John Doe",
                "student_email": "john@test.com",
                "upload_date": "2025-12-27T10:30:00",
                "file_size": 2048576
            }
        ]
    """
    # Query pending resources with student join
    query = (
        select(Resource, Student)
        .join(Student, Resource.uploaded_by_student_id == Student.id)
        .where(Resource.visibility == Visibility.PENDING_REVIEW)
        .order_by(Resource.created_at.desc())
    )

    results = session.exec(query).all()

    pending_resources = []
    for resource, student in results:
        # Get file size
        file_size = 0
        if os.path.exists(resource.file_path):
            file_size = os.path.getsize(resource.file_path)

        pending_resources.append(
            PendingResourceResponse(
                id=str(resource.id),
                title=resource.title,
                resource_type=resource.resource_type.value,
                uploaded_by_student_id=str(resource.uploaded_by_student_id),
                student_name=student.full_name,
                student_email=student.email,
                upload_date=resource.created_at.isoformat(),
                file_size=file_size,
                file_path=resource.file_path
            )
        )

    return pending_resources


@router.get("/{resource_id}/preview")
def preview_resource(
    resource_id: UUID,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> dict:
    """
    Preview first 3 pages of PDF resource.

    Extracts first 3 pages using PyPDF2, converts to base64-encoded images,
    and returns as JSON array for display in admin UI.

    Args:
        resource_id: UUID of resource to preview

    Returns:
        Dictionary with:
        - pages: Array of base64-encoded page images
        - page_count: Total pages in PDF
        - title: Resource title
        - file_size: File size in bytes

    Example:
        GET /api/admin/resources/{id}/preview
        Returns: {
            "pages": ["data:image/png;base64,...", ...],
            "page_count": 10,
            "title": "My Notes"
        }
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    if not os.path.exists(resource.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource file not found on disk"
        )

    # Extract first 3 pages as images
    try:
        from pdf2image import convert_from_path
        from io import BytesIO

        # Convert first 3 pages to images
        images = convert_from_path(
            resource.file_path,
            first_page=1,
            last_page=3,
            dpi=150  # Reasonable quality for preview
        )

        # Convert images to base64
        page_images = []
        for img in images:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            page_images.append(f"data:image/png;base64,{img_base64}")

        # Get total page count
        import PyPDF2
        with open(resource.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)

        return {
            "pages": page_images,
            "page_count": page_count,
            "title": resource.title,
            "file_size": os.path.getsize(resource.file_path),
            "resource_id": str(resource.id)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.put("/{resource_id}/approve", status_code=status.HTTP_200_OK)
def approve_resource(
    resource_id: UUID,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> dict:
    """
    Approve user-uploaded resource for public access.

    State transition: PENDING_REVIEW → PUBLIC (one-way, irreversible)

    Updates:
    - visibility = PUBLIC
    - admin_approved = True
    - Sets approval_date timestamp in metadata

    Args:
        resource_id: UUID of resource to approve

    Returns:
        Updated resource details

    Raises:
        HTTPException 404: Resource not found
        HTTPException 400: Resource already approved (state machine violation)

    Constitutional Compliance:
        - FR-028: Approve with visibility→public
        - FR-070: Linear state machine (no reversal)
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Enforce state machine: cannot re-approve already approved resource
    if resource.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource already approved (state transition violation)"
        )

    # Update resource to approved state
    resource.visibility = Visibility.PUBLIC
    resource.admin_approved = True

    # Store approval metadata
    if resource.resource_metadata is None:
        resource.resource_metadata = {}

    resource.resource_metadata['approval_date'] = datetime.utcnow().isoformat()
    resource.resource_metadata['approved_by'] = str(admin.id)

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return {
        "id": str(resource.id),
        "title": resource.title,
        "visibility": resource.visibility.value,
        "admin_approved": resource.admin_approved,
        "approval_date": resource.resource_metadata.get('approval_date'),
        "message": "Resource approved and now public"
    }


@router.put("/{resource_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_resource(
    resource_id: UUID,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> None:
    """
    Reject user-uploaded resource (silent rejection).

    Deletes:
    1. File from local storage
    2. Database record

    No notification sent to student (silent rejection per spec).

    Args:
        resource_id: UUID of resource to reject

    Raises:
        HTTPException 404: Resource not found
        HTTPException 400: Cannot reject approved resource

    Constitutional Compliance:
        - FR-029: Reject with file+record deletion
        - FR-071: Linear state machine (cannot reject approved)
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Enforce state machine: cannot reject approved resource
    if resource.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reject approved resource (state transition violation)"
        )

    # Delete file from storage
    if os.path.exists(resource.file_path):
        os.remove(resource.file_path)

    # Delete database record
    session.delete(resource)
    session.commit()

    # No response body (204 No Content)


@router.put("/{resource_id}/metadata")
def update_resource_metadata(
    resource_id: UUID,
    update_request: MetadataUpdateRequest,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> dict:
    """
    Update resource metadata before approval.

    Allows admin to edit:
    - title: Resource title
    - description: Resource description
    - metadata: JSONB field for custom metadata

    Args:
        resource_id: UUID of resource
        update_request: Metadata update fields

    Returns:
        Updated resource details

    Raises:
        HTTPException 404: Resource not found

    Constitutional Compliance:
        - FR-030: Edit metadata before approval
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Update title if provided
    if update_request.title:
        resource.title = update_request.title

    # Update metadata JSONB if provided
    if update_request.resource_metadata:
        if resource.resource_metadata is None:
            resource.resource_metadata = {}

        resource.resource_metadata.update(update_request.resource_metadata)

    # Store description in metadata
    if update_request.description:
        if resource.resource_metadata is None:
            resource.resource_metadata = {}

        resource.resource_metadata['description'] = update_request.description

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return {
        "id": str(resource.id),
        "title": resource.title,
        "resource_metadata": resource.resource_metadata,
        "message": "Metadata updated successfully"
    }


@router.post("/{resource_id}/extract-excerpt")
def extract_textbook_excerpt(
    resource_id: UUID,
    page_range_request: PageRangeRequest,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> dict:
    """
    Extract textbook excerpt from specified page range.

    Extracts pages, stores in metadata.excerpt_text and metadata.excerpt_pages.

    Args:
        resource_id: UUID of textbook resource
        page_range_request: Start and end page numbers (1-indexed)

    Returns:
        Excerpt metadata with character count

    Raises:
        HTTPException 404: Resource not found
        HTTPException 400: Invalid page range

    Constitutional Compliance:
        - FR-031: Textbook excerpt extraction
    """
    from src.services.pdf_extraction_service import extract_text_from_page_range

    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    try:
        # Extract text from page range
        excerpt_text = extract_text_from_page_range(
            resource.file_path,
            page_range_request.start_page,
            page_range_request.end_page
        )

        # Store in metadata
        if resource.resource_metadata is None:
            resource.resource_metadata = {}

        resource.resource_metadata['excerpt_text'] = excerpt_text
        resource.resource_metadata['excerpt_pages'] = f"{page_range_request.start_page}-{page_range_request.end_page}"
        resource.resource_metadata['excerpt_char_count'] = len(excerpt_text)

        session.add(resource)
        session.commit()

        return {
            "id": str(resource.id),
            "page_range": resource.resource_metadata['excerpt_pages'],
            "char_count": len(excerpt_text),
            "message": "Excerpt extracted successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
