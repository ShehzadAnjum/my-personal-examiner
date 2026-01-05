"""
Celery task for S3 background uploads.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Background redundancy: S3 uploads don't block user workflow
- Exponential backoff: Resilient to temporary S3 outages
"""

import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from celery import Task
from sqlmodel import Session, select

from src.database import get_engine
from src.models.enums import S3SyncStatus
from src.models.resource import Resource
from src.tasks.celery_app import app


class S3UploadTask(Task):
    """Base task class with retry logic."""

    autoretry_for = (ClientError,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = 60  # Start with 60 seconds
    retry_backoff_max = 900  # Max 15 minutes
    retry_jitter = True  # Add randomness to prevent thundering herd


@app.task(bind=True, base=S3UploadTask)
def upload_to_s3_task(self, resource_id: str, file_path: str) -> dict:
    """
    Upload file to S3 with SSE-S3 encryption (background task).

    Args:
        resource_id: Resource UUID (string for JSON serialization)
        file_path: Local file path to upload

    Returns:
        Dict with status and S3 URL

    Retry Logic:
        - Max 3 retries with exponential backoff
        - Backoff: 60s, 120s, 240s (with jitter)
        - Updates resource.s3_sync_status on success/failure

    Constitutional Compliance:
        - FR-058: HTTPS enforced via boto3 defaults
        - FR-059: SSE-S3 encryption for redundancy
    """
    s3_enabled = os.getenv("S3_ENABLED", "true").lower() == "true"
    
    if not s3_enabled:
        # S3 disabled for local development
        return {
            "status": "skipped",
            "message": "S3 uploads disabled in environment",
        }

    # Configure boto3 client with retry
    config = Config(
        retries={
            "max_attempts": 3,
            "mode": "adaptive",  # Exponential backoff with circuit breaker
        }
    )

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        config=config,
    )

    bucket_name = os.getenv("S3_BUCKET_NAME")
    
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable not set")

    try:
        # Generate S3 key from file path
        s3_key = f"resources/{resource_id}/{os.path.basename(file_path)}"

        # Upload with SSE-S3 encryption
        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs={"ServerSideEncryption": "AES256"},  # SSE-S3
        )

        # Generate S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

        # Update resource status in database
        _update_resource_s3_status(
            resource_id=UUID(resource_id),
            s3_url=s3_url,
            status=S3SyncStatus.SUCCESS,
        )

        return {
            "status": "success",
            "s3_url": s3_url,
            "message": f"Uploaded to S3: {s3_key}",
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = f"S3 upload failed: {error_code}"

        # Update resource status
        _update_resource_s3_status(
            resource_id=UUID(resource_id),
            s3_url=None,
            status=S3SyncStatus.FAILED,
        )

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    except Exception as e:
        # Non-retryable error
        _update_resource_s3_status(
            resource_id=UUID(resource_id),
            s3_url=None,
            status=S3SyncStatus.FAILED,
        )

        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
        }


def _update_resource_s3_status(
    resource_id: UUID,
    s3_url: Optional[str],
    status: S3SyncStatus,
) -> None:
    """
    Update resource S3 sync status in database.

    Args:
        resource_id: Resource UUID
        s3_url: S3 object URL (None if failed)
        status: S3SyncStatus enum value
    """
    engine = get_engine()
    
    with Session(engine) as session:
        resource = session.get(Resource, resource_id)
        
        if resource:
            resource.s3_url = s3_url
            resource.s3_sync_status = status
            
            if status == S3SyncStatus.SUCCESS:
                resource.last_synced_at = datetime.utcnow()
            
            session.add(resource)
            session.commit()


@app.task
def batch_retry_failed_uploads() -> dict:
    """
    Batch retry failed S3 uploads (triggered by admin).

    Returns:
        Dict with retry count and status

    Constitutional Compliance:
        - FR-057: Batch retry mechanism for S3 outage recovery
    """
    engine = get_engine()
    
    with Session(engine) as session:
        # Find all failed uploads
        statement = select(Resource).where(
            Resource.s3_sync_status == S3SyncStatus.FAILED
        )
        failed_resources = session.exec(statement).all()

        retry_count = 0
        for resource in failed_resources:
            # Update status to pending_retry
            resource.s3_sync_status = S3SyncStatus.PENDING_RETRY
            session.add(resource)
            
            # Queue upload task
            upload_to_s3_task.delay(
                resource_id=str(resource.id),
                file_path=resource.file_path,
            )
            retry_count += 1

        session.commit()

    return {
        "status": "success",
        "message": f"Queued {retry_count} failed uploads for retry",
        "retry_count": retry_count,
    }
