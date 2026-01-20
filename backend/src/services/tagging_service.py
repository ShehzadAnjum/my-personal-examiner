"""
Resource tagging service for linking resources to syllabus points.

Feature: 007-resource-bank-files (User Story 6)
Created: 2025-12-27

Provides admin tagging interface to manually link resources to syllabus points
with custom relevance scores, improving auto-selection accuracy.

Constitutional Compliance:
- FR-045: Admin creates syllabus_point_resources links with adjustable relevance
- FR-047: Full-text search on PDF extracted text
- FR-048: Index past paper questions for keyword matching
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, text
from sqlmodel import Session, select

from src.models.enums import AddedBy, Visibility
from src.models.resource import Resource
from src.models.syllabus_point_resource import SyllabusPointResource


def create_tag(
    resource_id: UUID,
    syllabus_point_id: UUID,
    relevance_score: float,
    added_by: AddedBy,
    session: Session,
) -> SyllabusPointResource:
    """
    Create or update a resource-to-syllabus-point tag.

    Args:
        resource_id: Resource UUID
        syllabus_point_id: Syllabus point UUID
        relevance_score: Relevance 0.0-1.0 (1.0 = perfect match)
        added_by: Who created the tag (SYSTEM, ADMIN, STUDENT)
        session: Database session

    Returns:
        Created or updated SyllabusPointResource

    Raises:
        ValueError: If relevance_score not in range [0, 1]
        HTTPException: If resource not found
    """
    # Validate relevance score
    if not 0.0 <= relevance_score <= 1.0:
        raise ValueError(f"relevance_score must be between 0 and 1, got {relevance_score}")

    # Verify resource exists
    resource = session.get(Resource, resource_id)
    if not resource:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource {resource_id} not found"
        )

    # Check if tag already exists (composite PK: syllabus_point_id + resource_id)
    existing_tag = session.exec(
        select(SyllabusPointResource).where(
            SyllabusPointResource.syllabus_point_id == syllabus_point_id,
            SyllabusPointResource.resource_id == resource_id,
        )
    ).first()

    if existing_tag:
        # Update existing tag
        existing_tag.relevance_score = relevance_score
        existing_tag.added_by = added_by
        session.add(existing_tag)
        session.commit()
        session.refresh(existing_tag)
        return existing_tag
    else:
        # Create new tag
        new_tag = SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=resource_id,
            relevance_score=relevance_score,
            added_by=added_by,
        )
        session.add(new_tag)
        session.commit()
        session.refresh(new_tag)
        return new_tag


def search_resources(
    query: str,
    session: Session,
    limit: int = 20,
    visibility_filter: Optional[Visibility] = None,
) -> List[dict]:
    """
    Full-text search on resources using PostgreSQL tsvector and ts_rank.

    Searches across:
    - Resource title
    - Resource metadata (extracted_text, tags, description)
    - File path (for syllabus codes like "9708")

    Args:
        query: Search query string (e.g., "fiscal policy")
        session: Database session
        limit: Max results to return (default 20)
        visibility_filter: Optional visibility filter (e.g., PUBLIC only)

    Returns:
        List of dicts with resource_id, title, resource_type, rank

    Algorithm:
    1. Create search vector from title + metadata + file_path
    2. Use ts_rank to score relevance
    3. Order by rank DESC
    4. Return top N results
    """
    # Convert query to tsquery format
    # Replace spaces with & for AND matching
    tsquery = query.strip().replace(" ", " & ")

    # Build SQL for full-text search
    # Use ts_rank for relevance scoring
    stmt = select(
        Resource.id,
        Resource.title,
        Resource.resource_type,
        Resource.file_path,
        Resource.metadata,
        # Calculate ts_rank for search relevance
        func.ts_rank(
            func.to_tsvector("english", func.coalesce(Resource.title, "")),
            func.to_tsquery("english", tsquery),
        ).label("rank"),
    ).where(
        # Match query in title OR metadata
        func.to_tsvector("english", func.coalesce(Resource.title, "")).op("@@")(
            func.to_tsquery("english", tsquery)
        )
        | func.to_tsvector(
            "english", func.coalesce(func.cast(Resource.metadata, text), "")
        ).op("@@")(func.to_tsquery("english", tsquery))
    )

    # Apply visibility filter if provided
    if visibility_filter:
        stmt = stmt.where(Resource.visibility == visibility_filter)

    # Order by rank DESC and limit
    stmt = stmt.order_by(text("rank DESC")).limit(limit)

    # Execute query
    results = session.exec(stmt).all()

    # Format results
    search_results = []
    for row in results:
        search_results.append(
            {
                "resource_id": str(row.id),
                "title": row.title,
                "resource_type": row.resource_type.value,
                "file_path": row.file_path,
                "rank": float(row.rank) if row.rank else 0.0,
            }
        )

    return search_results


def get_resources_for_syllabus_point(
    syllabus_point_id: UUID, session: Session, limit: int = 5
) -> List[dict]:
    """
    Get resources tagged to a specific syllabus point, ordered by relevance.

    Args:
        syllabus_point_id: Syllabus point UUID
        session: Database session
        limit: Max resources to return (default 5)

    Returns:
        List of dicts with resource details and relevance_score
    """
    # Query SyllabusPointResource JOIN Resource
    stmt = (
        select(SyllabusPointResource, Resource)
        .join(Resource, SyllabusPointResource.resource_id == Resource.id)
        .where(
            SyllabusPointResource.syllabus_point_id == syllabus_point_id,
            Resource.visibility == Visibility.PUBLIC,
            Resource.admin_approved == True,  # noqa: E712
        )
        .order_by(SyllabusPointResource.relevance_score.desc())
        .limit(limit)
    )

    results = session.exec(stmt).all()

    # Format results
    tagged_resources = []
    for sp_resource, resource in results:
        tagged_resources.append(
            {
                "resource_id": str(resource.id),
                "title": resource.title,
                "resource_type": resource.resource_type.value,
                "relevance_score": sp_resource.relevance_score,
                "added_by": sp_resource.added_by.value,
                "created_at": sp_resource.created_at.isoformat(),
            }
        )

    return tagged_resources


def validate_page_range(page_range: str) -> bool:
    """
    Validate page range format for textbook excerpts.

    Valid formats:
    - "245" (single page)
    - "245-267" (range)
    - "245, 250, 255" (multiple pages)

    Args:
        page_range: Page range string

    Returns:
        True if valid, False otherwise
    """
    if not page_range or not isinstance(page_range, str):
        return False

    # Remove whitespace
    page_range = page_range.strip()

    # Check single page
    if page_range.isdigit():
        return True

    # Check range format (e.g., "245-267")
    if "-" in page_range:
        parts = page_range.split("-")
        if len(parts) == 2:
            start, end = parts
            if start.strip().isdigit() and end.strip().isdigit():
                return int(start.strip()) <= int(end.strip())

    # Check comma-separated pages (e.g., "245, 250, 255")
    if "," in page_range:
        pages = page_range.split(",")
        return all(p.strip().isdigit() for p in pages)

    return False


def add_page_range_metadata(
    resource_id: UUID, page_range: str, session: Session
) -> Resource:
    """
    Add page range metadata to a resource (for textbook excerpts).

    Args:
        resource_id: Resource UUID
        page_range: Page range string (e.g., "245-267")
        session: Database session

    Returns:
        Updated resource

    Raises:
        ValueError: If page_range format invalid
        HTTPException: If resource not found
    """
    # Validate page range
    if not validate_page_range(page_range):
        raise ValueError(
            f"Invalid page_range format: {page_range}. "
            "Use formats like '245', '245-267', or '245, 250, 255'"
        )

    # Get resource
    resource = session.get(Resource, resource_id)
    if not resource:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource {resource_id} not found"
        )

    # Update metadata
    if resource.resource_metadata is None:
        resource.resource_metadata = {}

    resource.resource_metadata["page_range"] = page_range

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return resource
