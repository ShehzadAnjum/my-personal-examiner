"""
Celery application for background tasks.

Feature: 007-resource-bank-files
Created: 2025-12-27

Background tasks:
- S3 upload (async redundancy for local files)
- Daily Cambridge sync (2AM UTC)
- OCR processing for scanned PDFs
"""

import os

from celery import Celery
from celery.schedules import crontab

# Initialize Celery app
app = Celery(
    "resource_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
)

# Celery configuration
app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task execution
    task_acks_late=True,  # Re-queue if worker crashes
    task_reject_on_worker_lost=True,
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Scheduled tasks (Celery Beat)
app.conf.beat_schedule = {
    "daily-cambridge-sync": {
        "task": "tasks.sync_cambridge_resources",  # Task name from sync_task.py
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM UTC daily
        "options": {"queue": "sync"},  # Dedicated queue for long-running tasks
    },
}

# Task routing (optional: route tasks to specific queues)
app.conf.task_routes = {
    "src.tasks.s3_upload_task.upload_to_s3_task": {"queue": "s3_uploads"},
    "src.tasks.ocr_task.extract_text_task": {"queue": "ocr"},
    "src.tasks.sync_task.sync_cambridge_resources": {"queue": "sync"},
}

# Auto-discover tasks from src/tasks/ directory
app.autodiscover_tasks(["src.tasks"])
