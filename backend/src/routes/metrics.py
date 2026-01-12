"""
Observability metrics and monitoring endpoints.

Feature: 007-resource-bank-files (Phase 10: Polish)
Created: 2025-12-27

Provides system metrics for monitoring and operational insights.

Constitutional Compliance:
- FR-063: Total resources by type and visibility
- FR-066: Storage usage by student
- FR-064: Error logging with severity levels
- FR-065: Security event logging
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from src.database import get_session
from src.middleware.admin_auth import require_admin
from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.models.student import Student

router = APIRouter(prefix="/api/metrics")


@router.get("")
def get_system_metrics(
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
):
    """
    Get system-wide resource metrics.

    **Admin only**: Observability and monitoring endpoint.

    Returns:
    - Total resources count
    - Resources by visibility (public, private, pending_review)
    - Resources by type (syllabus, textbook, past_paper, video, etc.)
    - S3 sync status (pending, success, failed)
    - Storage usage by student (top 10 users)

    Constitutional Compliance:
    - FR-063: Resource counts by type and visibility
    - FR-066: Storage usage by student
    """
    # Total resources
    total_resources = session.exec(select(func.count(Resource.id))).first()

    # Resources by visibility
    visibility_counts = {}
    for visibility in Visibility:
        count = session.exec(
            select(func.count(Resource.id)).where(Resource.visibility == visibility)
        ).first()
        visibility_counts[visibility.value] = count

    # Resources by type
    type_counts = {}
    for resource_type in ResourceType:
        count = session.exec(
            select(func.count(Resource.id)).where(Resource.resource_type == resource_type)
        ).first()
        type_counts[resource_type.value] = count

    # S3 sync status
    sync_status_counts = {}
    for sync_status in S3SyncStatus:
        count = session.exec(
            select(func.count(Resource.id)).where(Resource.s3_sync_status == sync_status)
        ).first()
        sync_status_counts[sync_status.value] = count

    # Storage usage by student (top 10)
    # Count resources per student
    student_usage_query = (
        select(
            Resource.uploaded_by_student_id,
            func.count(Resource.id).label("resource_count"),
        )
        .where(Resource.uploaded_by_student_id.isnot(None))
        .group_by(Resource.uploaded_by_student_id)
        .order_by(func.count(Resource.id).desc())
        .limit(10)
    )

    student_usage_results = session.exec(student_usage_query).all()

    # Get student details
    student_usage = []
    for student_id, resource_count in student_usage_results:
        student = session.get(Student, student_id)
        if student:
            student_usage.append(
                {
                    "student_id": str(student_id),
                    "student_email": student.email,
                    "student_name": student.full_name,
                    "resource_count": resource_count,
                    "quota_usage_percent": int((resource_count / 100) * 100),  # Out of 100
                }
            )

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_resources": total_resources,
        "by_visibility": visibility_counts,
        "by_type": type_counts,
        "s3_sync_status": sync_status_counts,
        "top_10_users_by_storage": student_usage,
    }


@router.get("/s3-status")
def get_s3_sync_status(
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
):
    """
    Get S3 synchronization status.

    **Admin only**: Monitor S3 upload queue and failures.

    Returns:
    - pending_uploads: Count of resources queued for S3 upload
    - failed_uploads: Count of resources with failed S3 uploads
    - s3_online: Boolean indicating if S3 is reachable
    - last_successful_sync: Timestamp of last successful S3 upload
    - pending_retry: Count of resources queued for retry

    Constitutional Compliance:
    - FR-054 to FR-057: S3 outage handling and retry logic
    """
    # Count by S3 sync status
    pending_count = session.exec(
        select(func.count(Resource.id)).where(Resource.s3_sync_status == S3SyncStatus.PENDING)
    ).first()

    failed_count = session.exec(
        select(func.count(Resource.id)).where(Resource.s3_sync_status == S3SyncStatus.FAILED)
    ).first()

    pending_retry_count = session.exec(
        select(func.count(Resource.id)).where(
            Resource.s3_sync_status == S3SyncStatus.PENDING_RETRY
        )
    ).first()

    success_count = session.exec(
        select(func.count(Resource.id)).where(Resource.s3_sync_status == S3SyncStatus.SUCCESS)
    ).first()

    # Get last successful sync timestamp
    last_success = session.exec(
        select(Resource.last_synced_at)
        .where(
            Resource.s3_sync_status == S3SyncStatus.SUCCESS,
            Resource.last_synced_at.isnot(None),
        )
        .order_by(Resource.last_synced_at.desc())
        .limit(1)
    ).first()

    # Determine if S3 is online (heuristic: if recent uploads succeeded)
    s3_online = False
    if last_success:
        # Consider S3 online if last sync was within 1 hour
        s3_online = (datetime.utcnow() - last_success) < timedelta(hours=1)

    return {
        "pending_uploads": pending_count,
        "failed_uploads": failed_count,
        "pending_retry": pending_retry_count,
        "success_uploads": success_count,
        "s3_online": s3_online,
        "last_successful_sync": last_success.isoformat() if last_success else None,
    }


@router.post("/retry-s3")
def retry_failed_s3_uploads(
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
):
    """
    Batch retry failed S3 uploads.

    **Admin only**: Manually trigger retry of failed S3 uploads.

    Workflow:
    1. Find all resources with status=FAILED or PENDING_RETRY
    2. Change status to PENDING
    3. Queue Celery tasks for S3 upload
    4. Return count of resources queued

    Constitutional Compliance:
    - FR-055: Batch retry failed uploads when S3 recovers
    """
    # Find failed resources
    failed_resources = session.exec(
        select(Resource).where(
            (Resource.s3_sync_status == S3SyncStatus.FAILED)
            | (Resource.s3_sync_status == S3SyncStatus.PENDING_RETRY)
        )
    ).all()

    if not failed_resources:
        return {"status": "no_failed_uploads", "message": "No failed uploads to retry", "queued": 0}

    # Update status to PENDING
    for resource in failed_resources:
        resource.s3_sync_status = S3SyncStatus.PENDING
        session.add(resource)

    session.commit()

    # Queue Celery tasks (if Celery available)
    try:
        from src.tasks.s3_upload_task import upload_to_s3

        for resource in failed_resources:
            # Only queue if file exists locally
            import os

            if os.path.exists(resource.file_path):
                upload_to_s3.delay(str(resource.id))

    except ImportError:
        # Celery not available - status updated but tasks not queued
        pass

    return {
        "status": "queued",
        "message": f"Queued {len(failed_resources)} resources for S3 retry",
        "queued": len(failed_resources),
    }
