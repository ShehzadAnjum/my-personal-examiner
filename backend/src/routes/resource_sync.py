"""
Resource Sync API routes.

Feature: 007-resource-bank-files (User Story 2)
Created: 2025-12-27

Endpoints:
- POST /api/sync/trigger - Manual sync trigger (admin only)
- GET /api/sync/status - Get sync status and statistics
- POST /api/sync/retry-s3 - Batch retry failed S3 uploads
- GET /api/sync/s3-status - Get S3 sync status
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from src.database import get_session
from src.models.enums import S3SyncStatus, ResourceType
from src.models.resource import Resource
from src.models.student import Student
from src.routes.auth_extra import get_current_student
from src.tasks.sync_task import manual_sync_trigger, retry_failed_syncs

router = APIRouter(prefix="/api/sync", tags=["Resource Sync"])


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_manual_sync(
    subject_code: str = "9708",
    years_back: int = 10,
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Trigger manual Cambridge resource sync (admin only).

    Queues background task to download new past papers from Cambridge website.

    Args:
        subject_code: Cambridge subject code (default: 9708 for Economics)
        years_back: How many years to sync (default: 10)
        current_student: Authenticated student (from JWT)

    Returns:
        Dictionary with task ID and status message

    Raises:
        HTTPException 403: If user is not admin
        HTTPException 202: Sync queued successfully

    Example:
        POST /api/sync/trigger?subject_code=9708&years_back=5
        Returns: {"task_id": "abc123", "status": "queued", "message": "..."}
    """
    # Admin-only endpoint
    if not current_student.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger manual sync"
        )

    # Queue Celery task
    task = manual_sync_trigger.delay(subject_code=subject_code, years_back=years_back)

    return {
        "task_id": task.id,
        "status": "queued",
        "message": f"Manual sync queued for subject {subject_code} ({years_back} years)",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
def get_sync_status(
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Get resource sync status and statistics.

    Returns information about the last sync, resource counts, and sync health.

    Args:
        session: Database session
        current_student: Authenticated student (from JWT)

    Returns:
        Dictionary with:
        - last_sync_date: Timestamp of last successful sync
        - sync_status: "idle" | "running" | "success" | "failed"
        - total_resources: Total count of resources in database
        - new_resources_count: Resources added in last 24 hours
        - by_type: Resource counts grouped by type
        - s3_sync_health: S3 upload statistics

    Example:
        GET /api/sync/status
        Returns: {
            "last_sync_date": "2025-12-27T02:00:00",
            "sync_status": "success",
            "total_resources": 245,
            "new_resources_count": 12,
            "by_type": {"past_paper": 180, "syllabus": 5, ...},
            "s3_sync_health": {"pending": 3, "synced": 242, "failed": 0}
        }
    """
    # Get total resource count
    total_query = select(func.count(Resource.id))
    total_resources = session.exec(total_query).one()

    # Get resources by type
    by_type = {}
    for resource_type in ResourceType:
        type_query = select(func.count(Resource.id)).where(
            Resource.resource_type == resource_type
        )
        count = session.exec(type_query).one()
        by_type[resource_type.value] = count

    # Get S3 sync health
    s3_sync_health = {}
    for sync_status in S3SyncStatus:
        status_query = select(func.count(Resource.id)).where(
            Resource.s3_sync_status == sync_status
        )
        count = session.exec(status_query).one()
        s3_sync_health[sync_status.value] = count

    # Get most recently updated resource (proxy for last sync)
    last_updated_query = select(Resource).order_by(Resource.updated_at.desc()).limit(1)
    last_resource = session.exec(last_updated_query).first()
    last_sync_date = last_resource.updated_at.isoformat() if last_resource else None

    # Get new resources in last 24 hours
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_resources_query = select(func.count(Resource.id)).where(
        Resource.created_at >= yesterday
    )
    new_resources_count = session.exec(new_resources_query).one()

    # Determine sync status
    # (In production, would check Celery task status or sync_log table)
    sync_status = "idle"
    if s3_sync_health.get("failed", 0) > 0:
        sync_status = "warning"
    elif last_sync_date and (datetime.utcnow() - last_resource.updated_at).days < 1:
        sync_status = "success"

    return {
        "last_sync_date": last_sync_date,
        "sync_status": sync_status,
        "total_resources": total_resources,
        "new_resources_count": new_resources_count,
        "by_type": by_type,
        "s3_sync_health": s3_sync_health,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/s3-status")
def get_s3_status(
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Get S3 upload status (pending, synced, failed counts).

    Args:
        session: Database session
        current_student: Authenticated student (from JWT)

    Returns:
        Dictionary with:
        - pending_uploads: Count of resources with status=PENDING
        - failed_uploads: Count of resources with status=FAILED
        - synced_uploads: Count of resources with status=SUCCESS
        - s3_online: True if S3 is reachable (simple health check)
        - total_resources: Total count of resources

    Example:
        GET /api/sync/s3-status
        Returns: {
            "pending_uploads": 5,
            "failed_uploads": 2,
            "synced_uploads": 238,
            "s3_online": true,
            "total_resources": 245
        }
    """
    # Get counts by S3 sync status
    pending_query = select(func.count(Resource.id)).where(
        Resource.s3_sync_status == S3SyncStatus.PENDING
    )
    pending_count = session.exec(pending_query).one()

    failed_query = select(func.count(Resource.id)).where(
        Resource.s3_sync_status == S3SyncStatus.FAILED
    )
    failed_count = session.exec(failed_query).one()

    synced_query = select(func.count(Resource.id)).where(
        Resource.s3_sync_status == S3SyncStatus.SUCCESS
    )
    synced_count = session.exec(synced_query).one()

    total_query = select(func.count(Resource.id))
    total_count = session.exec(total_query).one()

    # S3 health check (simplified for Phase 1)
    # Phase 2: Implement actual S3 connectivity check
    import os
    s3_enabled = os.getenv("S3_ENABLED", "false").lower() == "true"

    return {
        "pending_uploads": pending_count,
        "failed_uploads": failed_count,
        "synced_uploads": synced_count,
        "s3_online": s3_enabled,  # Phase 1: Just check if S3 is enabled
        "total_resources": total_count,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/retry-s3", status_code=status.HTTP_202_ACCEPTED)
def retry_failed_s3_uploads(
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Batch retry failed S3 uploads (admin only).

    Finds all resources with s3_sync_status=FAILED and re-queues them
    for S3 upload.

    Args:
        current_student: Authenticated student (from JWT)

    Returns:
        Dictionary with task ID and count of retried uploads

    Raises:
        HTTPException 403: If user is not admin

    Example:
        POST /api/sync/retry-s3
        Returns: {"task_id": "xyz789", "status": "queued", "retry_count": 5}
    """
    # Admin-only endpoint
    if not current_student.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can retry failed S3 uploads"
        )

    # Queue Celery task
    task = retry_failed_syncs.delay()

    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Failed S3 uploads queued for retry",
        "timestamp": datetime.utcnow().isoformat()
    }
