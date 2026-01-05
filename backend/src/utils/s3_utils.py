"""
S3 utilities for outage handling and signed URL generation.

Feature: 007-resource-bank-files (Phase 10: Polish)
Created: 2025-12-27

Provides S3 outage resilience and secure download URLs.

Constitutional Compliance:
- FR-054 to FR-057: S3 outage handling and graceful degradation
- FR-062: Signed URL generation for private downloads
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Optional

from src.models.enums import S3SyncStatus


def is_s3_available() -> bool:
    """
    Check if S3 is currently available.

    Returns:
        True if S3 is reachable, False otherwise

    Implementation:
    - Attempts simple S3 connection/list operation
    - Returns False on any exception (connection error, timeout, etc.)
    - Used to determine if uploads should be queued or marked as PENDING_RETRY

    Constitutional Compliance:
    - FR-054: Detect S3 outages to continue with local-only storage
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, EndpointConnectionError

        # Get S3 credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        s3_bucket = os.getenv("S3_BUCKET_NAME")

        if not all([aws_access_key, aws_secret_key, s3_bucket]):
            # S3 not configured
            return False

        # Try to connect to S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        # Simple operation to test connectivity
        s3_client.head_bucket(Bucket=s3_bucket)
        return True

    except (ClientError, EndpointConnectionError, Exception):
        # S3 unavailable
        return False


def handle_s3_outage(resource_id: str, file_path: str) -> dict:
    """
    Handle S3 outage gracefully.

    Args:
        resource_id: Resource UUID
        file_path: Local file path

    Returns:
        Dict with status and s3_sync_status

    Workflow:
    1. Check if S3 is available
    2. If unavailable:
       - Continue with local-only storage
       - Set s3_sync_status = PENDING_RETRY
       - Log warning
    3. If available:
       - Set s3_sync_status = PENDING
       - Queue upload task

    Constitutional Compliance:
    - FR-054: Continue with local-only storage during outages
    - FR-055: Queue failed uploads for retry when S3 recovers
    - FR-056: Set status=PENDING_RETRY for failed uploads
    """
    from src.utils.logging_utils import LogSeverity, log_s3_sync_failure

    # Check S3 availability
    s3_available = is_s3_available()

    if not s3_available:
        # S3 outage - use local-only storage
        log_s3_sync_failure(
            resource_id=resource_id,
            file_path=file_path,
            error="S3 unavailable - local storage only",
            retry_count=0,
            severity=LogSeverity.WARNING,
        )

        return {"status": "local_only", "s3_sync_status": S3SyncStatus.PENDING_RETRY}

    else:
        # S3 available - queue upload
        return {"status": "s3_available", "s3_sync_status": S3SyncStatus.PENDING}


def generate_signed_download_url(
    resource_id: str,
    file_path: str,
    expiration_hours: int = 1,
) -> str:
    """
    Generate signed URL for secure private file downloads.

    Args:
        resource_id: Resource UUID
        file_path: Path to file
        expiration_hours: URL validity in hours (default: 1)

    Returns:
        Signed download URL with HMAC signature

    Security:
    - HMAC-SHA256 signature using secret key
    - Expiration timestamp to prevent replay attacks
    - Resource ID binding to prevent URL reuse

    Constitutional Compliance:
    - FR-062: Signed URLs for private downloads with 1-hour expiration
    """
    # Get signing secret from environment
    secret_key = os.getenv("DOWNLOAD_URL_SECRET_KEY", "default_secret_key_change_in_prod")

    # Calculate expiration timestamp
    expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
    expires_timestamp = int(expires_at.timestamp())

    # Build signature payload
    payload = f"{resource_id}:{file_path}:{expires_timestamp}"

    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Build signed URL
    signed_url = f"/api/resources/{resource_id}/download?expires={expires_timestamp}&signature={signature}"

    return signed_url


def verify_signed_url(
    resource_id: str,
    file_path: str,
    expires: int,
    signature: str,
) -> bool:
    """
    Verify signed download URL signature.

    Args:
        resource_id: Resource UUID
        file_path: Path to file
        expires: Expiration timestamp
        signature: HMAC signature to verify

    Returns:
        True if signature valid and not expired, False otherwise

    Constitutional Compliance:
    - FR-062: Verify HMAC signature for download URLs
    """
    # Check expiration
    current_timestamp = int(datetime.utcnow().timestamp())
    if current_timestamp > expires:
        return False  # URL expired

    # Get signing secret
    secret_key = os.getenv("DOWNLOAD_URL_SECRET_KEY", "default_secret_key_change_in_prod")

    # Rebuild signature
    payload = f"{resource_id}:{file_path}:{expires}"
    expected_signature = hmac.new(
        secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(signature, expected_signature)


def retry_failed_s3_upload(resource_id: str, file_path: str) -> dict:
    """
    Retry failed S3 upload.

    Args:
        resource_id: Resource UUID
        file_path: Local file path

    Returns:
        Dict with status and error (if any)

    Constitutional Compliance:
    - FR-055: Batch retry failed uploads when S3 recovers
    - FR-057: Update s3_sync_status on retry success/failure
    """
    from src.utils.logging_utils import LogSeverity, log_s3_sync_failure

    try:
        import boto3
        from botocore.exceptions import ClientError

        # Get S3 credentials
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        s3_bucket = os.getenv("S3_BUCKET_NAME")

        if not all([aws_access_key, aws_secret_key, s3_bucket]):
            return {"status": "error", "error": "S3 credentials not configured"}

        # Upload to S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        # Determine S3 key
        s3_key = f"resources/{resource_id}/{os.path.basename(file_path)}"

        # Upload with SSE-S3 encryption
        s3_client.upload_file(
            file_path,
            s3_bucket,
            s3_key,
            ExtraArgs={"ServerSideEncryption": "AES256"},  # SSE-S3
        )

        # Generate S3 URL
        s3_url = f"s3://{s3_bucket}/{s3_key}"

        return {"status": "success", "s3_url": s3_url}

    except ClientError as e:
        # S3 error - log and retry later
        log_s3_sync_failure(
            resource_id=resource_id,
            file_path=file_path,
            error=str(e),
            retry_count=0,
            severity=LogSeverity.ERROR,
        )

        return {"status": "error", "error": str(e)}

    except Exception as e:
        # Unexpected error
        log_s3_sync_failure(
            resource_id=resource_id,
            file_path=file_path,
            error=f"Unexpected error: {str(e)}",
            retry_count=0,
            severity=LogSeverity.ERROR,
        )

        return {"status": "error", "error": str(e)}
