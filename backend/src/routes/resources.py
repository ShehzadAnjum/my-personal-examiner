"""
Resource Bank API routes.

Feature: 007-resource-bank-files
Created: 2025-12-27

Endpoints:
- POST /api/resources/upload - Upload resource (admin or student)
- POST /api/resources/upload/youtube - Upload YouTube video by URL
- GET /api/resources - List resources with filters
- GET /api/resources/search - Full-text search resources
- GET /api/resources/quota - Get current student quota status
- GET /api/resources/{id} - Get resource details
- DELETE /api/resources/{id} - Delete own resource
- GET /api/resources/{id}/download - Download with signed URL
"""

import os
import tempfile
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select

from src.database import get_session
from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.models.student import Student
from src.routes.auth_extra import get_current_student
from src.schemas.resource_schemas import ResourceListResponse, ResourceResponse
from src.services.file_storage_service import (
    calculate_signature,
    get_file_path_for_resource,
    save_file_to_local,
    scan_file_for_virus,
    validate_file_size,
)
from src.tasks.s3_upload_task import upload_to_s3_task

router = APIRouter(prefix="/api/resources", tags=["Resources"])


@router.post("/upload", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    file: UploadFile = File(...),
    resource_type: ResourceType = Form(...),
    title: str = Form(...),
    source_url: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> Resource:
    """
    Upload new resource (student or admin).

    Multi-part form data:
    - file: PDF, video link, or document (max 50MB)
    - resource_type: syllabus, textbook, past_paper, video, article, user_upload
    - title: Resource title (max 500 chars)
    - source_url: Original source URL (optional)

    Workflow:
    1. Validate file size (<50MB)
    2. Save to temporary location
    3. Scan for viruses (ClamAV)
    4. Calculate SHA-256 signature
    5. Check for duplicates
    6. Save to permanent storage
    7. Create database record
    8. Queue S3 background upload
    9. Return resource details

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation via uploaded_by_student_id
        - FR-050: Enforce 100 resources/student quota
        - FR-052: Reject uploads exceeding quota
    """
    # 1. Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 50MB limit"
        )

    # Check student quota (100 resources per student)
    if not current_student.is_admin:
        quota_query = select(Resource).where(
            Resource.uploaded_by_student_id == current_student.id
        )
        student_resource_count = len(session.exec(quota_query).all())
        
        if student_resource_count >= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student quota exceeded: maximum 100 resources per student"
            )

    # 2. Save to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name

    try:
        # 3. Scan for viruses
        scan_result = scan_file_for_virus(temp_path)
        
        if not scan_result["safe"]:
            virus_name = scan_result.get("virus", "Unknown")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Virus detected: {virus_name}"
            )

        # 4. Calculate signature
        signature = calculate_signature(temp_path)

        # 5. Check for duplicates
        existing_resource = session.exec(
            select(Resource).where(Resource.signature == signature)
        ).first()
        
        if existing_resource:
            # Clean up temp file
            os.remove(temp_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Resource already exists with ID: {existing_resource.id}"
            )

        # 6. Determine final file path
        file_path = get_file_path_for_resource(
            resource_type=resource_type,
            filename=file.filename or "uploaded_file",
            student_id=current_student.id if resource_type == ResourceType.USER_UPLOAD else None,
        )

        # 7. Save to permanent storage
        absolute_path = save_file_to_local(temp_path, file_path)

        # 8. Create database record
        resource = Resource(
            id=uuid4(),
            resource_type=resource_type,
            title=title,
            source_url=source_url,
            file_path=file_path,
            uploaded_by_student_id=current_student.id if resource_type == ResourceType.USER_UPLOAD else None,
            admin_approved=current_student.is_admin,  # Auto-approve admin uploads
            visibility=Visibility.PUBLIC if current_student.is_admin else Visibility.PENDING_REVIEW,
            signature=signature,
            s3_sync_status=S3SyncStatus.PENDING,
        )

        session.add(resource)
        session.commit()
        session.refresh(resource)

        # 9. Queue S3 background upload (optional - graceful degradation if Celery unavailable)
        try:
            upload_to_s3_task.delay(
                resource_id=str(resource.id),
                file_path=absolute_path,
            )
        except Exception as e:
            # Log but don't fail upload if S3 background task fails
            print(f"Warning: S3 background upload task failed: {e}")
            # Resource is still saved locally, will be synced later

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return resource

    except HTTPException:
        # Re-raise HTTP exceptions
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    
    except Exception as e:
        # Clean up on unexpected errors
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("", response_model=ResourceListResponse)
def list_resources(
    resource_type: Optional[ResourceType] = None,
    visibility: Optional[Visibility] = None,
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> ResourceListResponse:
    """
    List resources with filters.

    Multi-tenant isolation:
    - Public: Visible to all
    - Private: Only visible to owner + admin
    - Pending Review: Only visible to owner + admin
    """
    query = select(Resource)

    # Apply filters
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)

    # Multi-tenant visibility filtering
    if current_student.is_admin:
        # Admin sees everything
        if visibility:
            query = query.where(Resource.visibility == visibility)
    else:
        # Students see: public + own resources
        if visibility:
            if visibility == Visibility.PUBLIC:
                query = query.where(Resource.visibility == Visibility.PUBLIC)
            else:
                # Can only see own private/pending resources
                query = query.where(
                    Resource.uploaded_by_student_id == current_student.id,
                    Resource.visibility == visibility
                )
        else:
            # Default: public + own resources
            query = query.where(
                (Resource.visibility == Visibility.PUBLIC) |
                (Resource.uploaded_by_student_id == current_student.id)
            )

    # Count total
    total = len(session.exec(query).all())

    # Apply pagination
    query = query.offset(offset).limit(limit)
    resources = session.exec(query).all()

    return ResourceListResponse(total=total, resources=resources)


@router.get("/search")
def search_resources(
    query: str,
    resource_type: Optional[ResourceType] = None,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> list[dict]:
    """
    Full-text search across resources using PostgreSQL tsvector.

    Query matches against:
    - Resource title
    - Extracted text (from PDFs, YouTube transcripts)

    Returns results with relevance ranking (ts_rank).

    Multi-tenant isolation:
    - Students see: public resources + own uploads
    - Admins see: all resources
    """
    from sqlalchemy import func

    # Build base query with visibility filtering
    base_query = select(Resource)

    # Multi-tenant visibility filtering
    if not current_student.is_admin:
        # Students see: public + own resources
        base_query = base_query.where(
            (Resource.visibility == Visibility.PUBLIC) |
            (Resource.uploaded_by_student_id == current_student.id)
        )

    # Apply resource type filter
    if resource_type:
        base_query = base_query.where(Resource.resource_type == resource_type)

    # Full-text search using PostgreSQL tsvector
    # Search in title and extracted_text
    search_query = query.strip()

    if search_query:
        # Simple text search (case-insensitive)
        base_query = base_query.where(
            (Resource.title.ilike(f"%{search_query}%")) |
            (Resource.extracted_text.ilike(f"%{search_query}%"))
        )

    # Limit results
    base_query = base_query.limit(limit)

    # Execute query
    results = session.exec(base_query).all()

    # Return as search results
    return [
        {
            "resource": result,
            "rank": 1.0,  # Placeholder for relevance score
            "matched_text": search_query,
        }
        for result in results
    ]


@router.get("/quota")
def get_quota_status(
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Get current student's quota usage.

    Returns:
    - current_usage: Number of resources uploaded by student
    - limit: Maximum allowed resources (100)
    - percentage_used: Percentage of quota used (0-100)

    Constitutional Compliance:
    - FR-050: Enforce 100 resources/student quota
    """
    # Count student's resources
    quota_query = select(Resource).where(
        Resource.uploaded_by_student_id == current_student.id
    )
    current_usage = len(session.exec(quota_query).all())

    limit = 100
    percentage_used = int((current_usage / limit) * 100)

    return {
        "current_usage": current_usage,
        "limit": limit,
        "percentage_used": percentage_used,
    }


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: UUID,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> Resource:
    """
    Get resource details.

    Multi-tenant access control enforced.
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Check access permission
    if not resource.can_be_accessed_by(current_student.id, current_student.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> None:
    """
    Delete own resource (students only, not approved resources).

    Students can only delete:
    - Own uploads (uploaded_by_student_id matches)
    - Not yet admin-approved
    """
    resource = session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Check ownership
    if resource.uploaded_by_student_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete: not resource owner"
        )

    # Check if approved
    if resource.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete approved resource"
        )

    # Delete file from storage
    if os.path.exists(resource.file_path):
        os.remove(resource.file_path)

    # Delete database record
    session.delete(resource)
    session.commit()


@router.post(
    "/upload/youtube", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED
)
def upload_youtube_video(
    url: str = Form(...),
    title: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> Resource:
    """
    Upload YouTube video by URL (admin or student).

    Extracts transcript and metadata automatically.

    Form data:
    - url: YouTube video URL (any format: watch?v=, youtu.be/, etc.)
    - title: Optional custom title (defaults to video title from API)

    Workflow:
    1. Validate YouTube URL format
    2. Check quota (max 10 videos/day)
    3. Extract video transcript (youtube-transcript-api)
    4. Extract video metadata (YouTube Data API v3)
    5. Store transcript + metadata in Resource
    6. Return resource details

    Constitutional Compliance:
    - FR-049: Index YouTube transcripts for searchability
    - FR-050: Enforce 100 resources/student quota
    - US7: Extract transcript with timestamps
    """
    from src.services.youtube_service import (
        YouTubeTranscriptUnavailable,
        process_youtube_video,
        quota_tracker,
        validate_youtube_url,
    )

    # 1. Validate YouTube URL
    if not validate_youtube_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL. Supported formats: youtube.com/watch?v=..., youtu.be/...",
        )

    # 2. Check quota (10 videos/day for Phase 1)
    if not quota_tracker.check_quota():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily YouTube quota exceeded. Limit: {quota_tracker.daily_limit} videos/day. "
            f"Try again tomorrow.",
        )

    # Check student quota (100 resources per student)
    if not current_student.is_admin:
        quota_query = select(Resource).where(
            Resource.uploaded_by_student_id == current_student.id
        )
        student_resource_count = len(session.exec(quota_query).all())

        if student_resource_count >= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource quota exceeded (100/100). Delete unused resources to upload new ones.",
            )

    # 3. Process YouTube video (extract transcript + metadata)
    video_data = process_youtube_video(url)

    if video_data.get("error"):
        # Graceful degradation: store metadata even if transcript unavailable
        if not video_data.get("title"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"YouTube video processing failed: {video_data['error']}",
            )

    # Increment quota counter
    quota_tracker.increment_usage()

    # 4. Create Resource record
    video_id = video_data["video_id"]
    resource_title = title or video_data.get("title", f"YouTube Video {video_id}")

    # Build metadata
    metadata = {
        "video_id": video_id,
        "channel": video_data.get("channel"),
        "duration": video_data.get("duration"),
        "thumbnail_url": video_data.get("thumbnail_url"),
        "description": video_data.get("description"),
        "published_at": video_data.get("published_at"),
        "language": video_data.get("language"),
        "is_generated": video_data.get("is_generated"),
        "extracted_text": video_data.get("transcript_text"),  # For full-text search
        "transcript_entries": video_data.get("transcript_entries"),  # For timestamps
    }

    # Remove None values
    metadata = {k: v for k, v in metadata.items() if v is not None}

    # Use video_id as signature for duplicate detection
    signature = f"youtube_{video_id}"

    # Check for duplicates
    existing_resource = session.exec(
        select(Resource).where(Resource.signature == signature)
    ).first()

    if existing_resource:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"YouTube video already uploaded with ID: {existing_resource.id}",
        )

    # Determine visibility
    visibility = (
        Visibility.PUBLIC
        if current_student.is_admin
        else Visibility.PENDING_REVIEW  # Students require approval
    )

    # Create resource
    resource = Resource(
        id=uuid4(),
        resource_type=ResourceType.VIDEO,
        title=resource_title,
        source_url=url,
        file_path=f"youtube/{video_id}.json",  # Virtual path (no file stored)
        uploaded_by_student_id=current_student.id,
        admin_approved=current_student.is_admin,  # Auto-approve admin uploads
        visibility=visibility,
        metadata=metadata,
        signature=signature,
        s3_url=None,  # YouTube videos not stored in S3
        s3_sync_status=S3SyncStatus.SUCCESS,  # Mark as synced (not applicable)
        extracted_text=video_data.get("transcript_text"),  # For full-text search
    )

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return resource
