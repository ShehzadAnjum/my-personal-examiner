"""
Celery tasks for Cambridge resource synchronization.

Feature: 007-resource-bank-files (User Story 2)
Created: 2025-12-27

Background tasks:
- sync_cambridge_resources_task: Daily 2AM job to download new past papers
- manual_sync_trigger: Manual sync triggered by admin via API

Retry strategy:
- Max 3 retries with 4-hour delay (14,400 seconds)
- Exponential backoff for temporary failures
- Alert admin if all retries fail
"""

import logging
from datetime import datetime
from typing import Dict

from celery import Task

from src.tasks.celery_app import app

logger = logging.getLogger(__name__)


class SyncTask(Task):
    """
    Custom Celery Task with retry configuration for sync operations.

    Retry strategy:
    - Max 3 attempts
    - 4-hour delay between retries (14,400 seconds)
    - Exponential backoff with jitter
    """
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = 14400  # 4 hours in seconds
    retry_jitter = True  # Add randomness to prevent thundering herd


@app.task(bind=True, base=SyncTask, name='tasks.sync_cambridge_resources')
def sync_cambridge_resources_task(self) -> Dict[str, any]:
    """
    Daily sync task: Download new Cambridge past papers.

    Scheduled via Celery Beat at 2:00 AM daily.

    Workflow:
    1. Call sync_service.sync_cambridge_resources()
    2. Download past papers from last 10 years
    3. Use signature-based change detection
    4. Link mark schemes to question papers
    5. Queue S3 uploads for new resources
    6. Return sync statistics

    Returns:
        Dictionary with sync statistics:
        - sync_date: Timestamp of sync
        - total_found: Total resources on Cambridge website
        - new_downloaded: New resources downloaded
        - skipped_duplicates: Resources skipped (unchanged)
        - failed: Resources that failed to download
        - mark_schemes_linked: Mark schemes linked to papers
        - status: "success" or "failed"

    Raises:
        Exception: On critical sync failure (retried up to 3 times)
    """
    try:
        logger.info("Starting Cambridge resource sync...")

        # Import here to avoid circular dependency
        from src.services.sync_service import sync_cambridge_resources

        # Execute sync
        stats = sync_cambridge_resources(subject_code="9708", years_back=10)

        # Add metadata
        result = {
            'sync_date': datetime.utcnow().isoformat(),
            'status': 'success',
            **stats
        }

        logger.info(
            f"Sync completed successfully: "
            f"{stats['new_downloaded']} new, "
            f"{stats['skipped_duplicates']} skipped, "
            f"{stats['failed']} failed"
        )

        # Queue S3 uploads for new resources
        if stats['new_downloaded'] > 0:
            # S3 uploads already queued in sync_service.py
            # (upload_to_s3_task.delay called after each resource creation)
            logger.info(f"Queued {stats['new_downloaded']} S3 uploads")

        return result

    except Exception as exc:
        logger.error(f"Sync failed (attempt {self.request.retries + 1}/3): {str(exc)}")

        # Check if max retries reached
        if self.request.retries >= 2:  # 0-indexed, so 2 = 3rd attempt
            # Alert admin after all retries exhausted
            logger.critical(
                f"ALERT: Cambridge sync failed after 3 attempts. "
                f"Manual intervention required. Error: {str(exc)}"
            )
            # TODO: Send email/Slack notification to admin
            return {
                'sync_date': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': str(exc),
                'retries_exhausted': True
            }

        # Retry with exponential backoff
        raise self.retry(exc=exc)


@app.task(name='tasks.manual_sync_trigger')
def manual_sync_trigger(subject_code: str = "9708", years_back: int = 10) -> Dict[str, any]:
    """
    Manual sync trigger: Admin-initiated sync via API endpoint.

    Unlike the daily scheduled task, this can be triggered on-demand
    and accepts custom parameters.

    Args:
        subject_code: Cambridge subject code (default: 9708 for Economics)
        years_back: How many years to sync (default: 10)

    Returns:
        Dictionary with sync statistics (same format as scheduled task)
    """
    try:
        logger.info(f"Manual sync triggered for subject {subject_code}, {years_back} years back")

        from src.services.sync_service import sync_cambridge_resources

        stats = sync_cambridge_resources(subject_code=subject_code, years_back=years_back)

        result = {
            'sync_date': datetime.utcnow().isoformat(),
            'status': 'success',
            'trigger': 'manual',
            **stats
        }

        logger.info(
            f"Manual sync completed: "
            f"{stats['new_downloaded']} new, "
            f"{stats['skipped_duplicates']} skipped"
        )

        return result

    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        return {
            'sync_date': datetime.utcnow().isoformat(),
            'status': 'failed',
            'trigger': 'manual',
            'error': str(e)
        }


@app.task(name='tasks.retry_failed_syncs')
def retry_failed_syncs() -> Dict[str, any]:
    """
    Retry past papers that failed to download in previous sync.

    Called manually or scheduled weekly to clean up failed downloads.

    Workflow:
    1. Query resources with s3_sync_status = FAILED
    2. Re-attempt sync for each failed resource
    3. Update status based on retry result

    Returns:
        Dictionary with retry statistics
    """
    try:
        from sqlmodel import Session, select
        from src.database import get_engine
        from src.models.enums import S3SyncStatus
        from src.models.resource import Resource
        from src.tasks.s3_upload_task import upload_to_s3_task

        engine = get_engine()

        with Session(engine) as session:
            # Find failed resources
            statement = select(Resource).where(Resource.s3_sync_status == S3SyncStatus.FAILED)
            failed_resources = session.exec(statement).all()

            retry_count = 0
            success_count = 0

            for resource in failed_resources:
                # Update status to pending_retry
                resource.s3_sync_status = S3SyncStatus.PENDING_RETRY
                session.add(resource)

                # Queue S3 upload task
                upload_to_s3_task.delay(
                    resource_id=str(resource.id),
                    file_path=resource.file_path
                )

                retry_count += 1

            session.commit()

            logger.info(f"Queued {retry_count} failed resources for retry")

            return {
                'status': 'success',
                'retry_count': retry_count,
                'timestamp': datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Retry failed syncs task failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
