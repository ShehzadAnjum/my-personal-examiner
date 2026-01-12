"""
Resource tagging API endpoints for admin manual tagging.

Feature: 007-resource-bank-files (User Story 6)
Created: 2025-12-27

Provides admin interface to:
- Tag resources to syllabus points with custom relevance scores
- Search resources using full-text search
- View resources linked to syllabus points

Constitutional Compliance:
- FR-045: Admin can create syllabus_point_resources links with adjustable relevance
- FR-046: Admin can specify page ranges for textbooks
- FR-047: Full-text search on extracted PDF text
- FR-048: Index past paper questions for keyword matching
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.database import get_session
from src.middleware.admin_auth import require_admin
from src.models.enums import AddedBy, Visibility
from src.models.student import Student
from src.schemas.resource_schemas import ResourceTagRequest, SyllabusPointResourceResponse
from src.services.tagging_service import (
    add_page_range_metadata,
    create_tag,
    get_resources_for_syllabus_point,
    search_resources,
)

router = APIRouter(prefix="/api")


@router.post(
    "/resources/{resource_id}/tag",
    status_code=status.HTTP_201_CREATED,
    response_model=SyllabusPointResourceResponse,
)
def tag_resource_to_syllabus_point(
    resource_id: UUID,
    request: ResourceTagRequest,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
):
    """
    Tag a resource to a syllabus point with custom relevance score.

    **Admin only**: Manually link resources to syllabus points to improve
    auto-selection accuracy.

    **Request Body**:
    - syllabus_point_id: UUID of the syllabus learning outcome
    - relevance_score: 0.0-1.0 (1.0 = perfect match for topic)

    **Example**:
    ```json
    {
      "syllabus_point_id": "9708.5.1",
      "relevance_score": 0.95
    }
    ```

    **Returns**: Created SyllabusPointResource link

    **Use Cases**:
    - Admin finds excellent textbook chapter on fiscal policy → tags to 9708.5.1 with 0.95
    - Admin identifies past paper question that perfectly matches topic → tags with 1.0
    - Admin marks general economics resource as moderately relevant → tags with 0.6

    Constitutional Compliance:
    - FR-045: Creates syllabus_point_resources link with adjustable relevance_score
    """
    try:
        tag = create_tag(
            resource_id=resource_id,
            syllabus_point_id=request.syllabus_point_id,
            relevance_score=request.relevance_score,
            added_by=AddedBy.ADMIN,
            session=session,
        )

        return SyllabusPointResourceResponse(
            syllabus_point_id=tag.syllabus_point_id,
            resource_id=tag.resource_id,
            relevance_score=tag.relevance_score,
            added_by=tag.added_by,
            created_at=tag.created_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/resources/{resource_id}/page-range",
    status_code=status.HTTP_200_OK,
)
def add_page_range_to_resource(
    resource_id: UUID,
    page_range: str = Query(..., description="Page range (e.g., '245-267' or '245')"),
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
):
    """
    Add page range metadata to a textbook resource.

    **Admin only**: Specify which pages are relevant for a topic.

    **Query Parameters**:
    - page_range: Page range in formats:
      - Single page: "245"
      - Range: "245-267"
      - Multiple pages: "245, 250, 255"

    **Example**:
    ```
    POST /api/resources/{id}/page-range?page_range=245-267
    ```

    **Returns**: Success message

    Constitutional Compliance:
    - FR-046: Stores page ranges in metadata JSONB field
    """
    try:
        resource = add_page_range_metadata(
            resource_id=resource_id, page_range=page_range, session=session
        )

        return {
            "message": f"Page range '{page_range}' added to resource {resource.title}",
            "resource_id": str(resource.id),
            "page_range": page_range,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/resources/search")
def search_resources_endpoint(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    public_only: bool = Query(True, description="Only search PUBLIC resources"),
    session: Session = Depends(get_session),
):
    """
    Full-text search on resources using PostgreSQL ts_rank.

    Searches across:
    - Resource title
    - Extracted text from PDFs (metadata.extracted_text)
    - Resource metadata (tags, description)

    **Query Parameters**:
    - query: Search keywords (e.g., "fiscal policy taxation")
    - limit: Max results (1-100, default 20)
    - public_only: Filter to PUBLIC visibility only (default true)

    **Example**:
    ```
    GET /api/resources/search?query=fiscal%20policy&limit=10
    ```

    **Returns**: List of resources with ts_rank scores

    **Ranking Algorithm**:
    - Uses PostgreSQL `ts_rank` for relevance scoring
    - Searches title and metadata fields
    - Orders by rank DESC (most relevant first)

    Constitutional Compliance:
    - FR-047: Full-text search on extracted PDF text
    - FR-048: Keyword matching for past paper questions
    """
    visibility_filter = Visibility.PUBLIC if public_only else None

    results = search_resources(
        query=query, session=session, limit=limit, visibility_filter=visibility_filter
    )

    return results


@router.get("/syllabus/{syllabus_point_id}/resources")
def get_resources_for_syllabus_endpoint(
    syllabus_point_id: UUID,
    limit: int = Query(5, ge=1, le=20, description="Max resources"),
    session: Session = Depends(get_session),
):
    """
    Get resources tagged to a specific syllabus point, ordered by relevance.

    **Public endpoint**: Returns PUBLIC approved resources only.

    **Query Parameters**:
    - limit: Max resources to return (1-20, default 5)

    **Example**:
    ```
    GET /api/syllabus/9708.5.1/resources?limit=10
    ```

    **Returns**: List of resources with relevance scores

    **Use Cases**:
    - Display recommended resources for a topic page
    - Show "Related Resources" section in teaching UI
    - Preview which resources will be auto-selected for topic generation

    Constitutional Compliance:
    - FR-032: Auto-select top N resources by relevance_score
    """
    resources = get_resources_for_syllabus_point(
        syllabus_point_id=syllabus_point_id, session=session, limit=limit
    )

    return resources
