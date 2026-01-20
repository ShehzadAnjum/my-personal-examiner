"""
Comprehensive error and security logging utilities.

Feature: 007-resource-bank-files (Phase 10: Polish)
Created: 2025-12-27

Provides structured logging for errors and security events with severity levels.

Constitutional Compliance:
- FR-064: Error logging with ERROR/WARNING/INFO severity levels
- FR-065: Security event logging with 1-year retention
- FR-067: Admin action audit trail
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class LogSeverity(str, Enum):
    """Log severity levels."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class SecurityEventType(str, Enum):
    """Security event types for audit logging."""

    FAILED_AUTH = "failed_auth"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    QUOTA_EXCEEDED = "quota_exceeded"
    ADMIN_ACTION = "admin_action"
    RESOURCE_APPROVED = "resource_approved"
    RESOURCE_REJECTED = "resource_rejected"
    RESOURCE_DELETED = "resource_deleted"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


# Logger instances
error_logger = logging.getLogger("resource_bank.errors")
security_logger = logging.getLogger("resource_bank.security")
upload_logger = logging.getLogger("resource_bank.uploads")


def log_file_upload_failure(
    student_id: UUID,
    filename: str,
    error: str,
    severity: LogSeverity = LogSeverity.ERROR,
):
    """
    Log file upload failure.

    Args:
        student_id: Student who attempted upload
        filename: Name of file being uploaded
        error: Error message
        severity: Log severity level (default: ERROR)

    Constitutional Compliance:
    - FR-064: File upload failures logged with severity levels
    """
    error_logger.log(
        getattr(logging, severity.value),
        f"File upload failed | student_id={student_id} | filename={filename} | error={error}",
    )


def log_s3_sync_failure(
    resource_id: UUID,
    file_path: str,
    error: str,
    retry_count: int = 0,
    severity: LogSeverity = LogSeverity.WARNING,
):
    """
    Log S3 synchronization failure.

    Args:
        resource_id: Resource UUID
        file_path: Path to file
        error: Error message
        retry_count: Number of retry attempts
        severity: Log severity level (default: WARNING for retryable failures)

    Constitutional Compliance:
    - FR-064: S3 sync failures logged with WARNING severity
    - FR-054 to FR-057: S3 outage handling
    """
    error_logger.log(
        getattr(logging, severity.value),
        f"S3 sync failed | resource_id={resource_id} | file_path={file_path} | "
        f"retry_count={retry_count} | error={error}",
    )


def log_ocr_failure(
    resource_id: UUID,
    file_path: str,
    error: str,
    severity: LogSeverity = LogSeverity.WARNING,
):
    """
    Log OCR extraction failure.

    Args:
        resource_id: Resource UUID
        file_path: Path to PDF file
        error: Error message
        severity: Log severity level (default: WARNING, non-critical)

    Constitutional Compliance:
    - FR-064: OCR failures logged with WARNING severity
    """
    error_logger.log(
        getattr(logging, severity.value),
        f"OCR extraction failed | resource_id={resource_id} | file_path={file_path} | error={error}",
    )


def log_cambridge_unreachable(
    url: str,
    error: str,
    severity: LogSeverity = LogSeverity.WARNING,
):
    """
    Log Cambridge website unreachable error.

    Args:
        url: Cambridge URL that was unreachable
        error: Error message (timeout, connection error, etc.)
        severity: Log severity level (default: WARNING)

    Constitutional Compliance:
    - FR-064: Cambridge unreachable logged with WARNING severity
    """
    error_logger.log(
        getattr(logging, severity.value),
        f"Cambridge website unreachable | url={url} | error={error}",
    )


def log_security_event(
    event_type: SecurityEventType,
    student_id: Optional[UUID],
    details: str,
    ip_address: Optional[str] = None,
    resource_id: Optional[UUID] = None,
):
    """
    Log security event for audit trail.

    Args:
        event_type: Type of security event
        student_id: Student involved (if applicable)
        details: Event details
        ip_address: IP address of request (if available)
        resource_id: Resource affected (if applicable)

    Constitutional Compliance:
    - FR-065: Security event logging with 1-year retention
    - FR-067: Admin action audit trail
    """
    timestamp = datetime.utcnow().isoformat()

    security_logger.info(
        f"SECURITY_EVENT | type={event_type.value} | timestamp={timestamp} | "
        f"student_id={student_id} | ip_address={ip_address} | "
        f"resource_id={resource_id} | details={details}"
    )


def log_failed_auth(
    email: str,
    ip_address: Optional[str] = None,
    reason: str = "Invalid credentials",
):
    """
    Log failed authentication attempt.

    Args:
        email: Email address used in failed login
        ip_address: IP address of request
        reason: Reason for failure

    Constitutional Compliance:
    - FR-065: Failed auth attempts logged for security monitoring
    """
    log_security_event(
        event_type=SecurityEventType.FAILED_AUTH,
        student_id=None,
        details=f"Failed login attempt | email={email} | reason={reason}",
        ip_address=ip_address,
    )


def log_unauthorized_access(
    student_id: UUID,
    resource_id: Optional[UUID],
    action: str,
    ip_address: Optional[str] = None,
):
    """
    Log unauthorized access attempt.

    Args:
        student_id: Student who attempted unauthorized access
        resource_id: Resource they tried to access (if applicable)
        action: Action they attempted (view, edit, delete, etc.)
        ip_address: IP address of request

    Constitutional Compliance:
    - FR-065: Unauthorized access attempts logged
    """
    log_security_event(
        event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
        student_id=student_id,
        details=f"Unauthorized access attempt | action={action}",
        ip_address=ip_address,
        resource_id=resource_id,
    )


def log_quota_exceeded(
    student_id: UUID,
    quota_type: str,
    current_usage: int,
    limit: int,
):
    """
    Log quota exceeded violation.

    Args:
        student_id: Student who exceeded quota
        quota_type: Type of quota (student_resources, daily_youtube, etc.)
        current_usage: Current usage count
        limit: Quota limit

    Constitutional Compliance:
    - FR-065: Quota exceeded violations logged
    """
    log_security_event(
        event_type=SecurityEventType.QUOTA_EXCEEDED,
        student_id=student_id,
        details=f"Quota exceeded | type={quota_type} | usage={current_usage}/{limit}",
    )


def log_admin_action(
    admin_id: UUID,
    action: str,
    resource_id: Optional[UUID] = None,
    details: Optional[str] = None,
):
    """
    Log admin action for audit trail.

    Args:
        admin_id: Admin student ID
        action: Action performed (approve, reject, tag, delete, etc.)
        resource_id: Resource affected (if applicable)
        details: Additional details

    Constitutional Compliance:
    - FR-067: Admin action audit trail
    """
    log_security_event(
        event_type=SecurityEventType.ADMIN_ACTION,
        student_id=admin_id,
        details=f"Admin action | action={action} | details={details}",
        resource_id=resource_id,
    )


def log_resource_approval(
    admin_id: UUID,
    resource_id: UUID,
    resource_title: str,
):
    """
    Log resource approval by admin.

    Args:
        admin_id: Admin who approved resource
        resource_id: Resource approved
        resource_title: Title of resource

    Constitutional Compliance:
    - FR-067: Admin approval actions logged
    """
    log_admin_action(
        admin_id=admin_id,
        action="approve_resource",
        resource_id=resource_id,
        details=f"Approved resource: {resource_title}",
    )


def log_resource_rejection(
    admin_id: UUID,
    resource_id: UUID,
    resource_title: str,
    reason: Optional[str] = None,
):
    """
    Log resource rejection by admin.

    Args:
        admin_id: Admin who rejected resource
        resource_id: Resource rejected
        resource_title: Title of resource
        reason: Rejection reason (if provided)

    Constitutional Compliance:
    - FR-067: Admin rejection actions logged
    """
    log_admin_action(
        admin_id=admin_id,
        action="reject_resource",
        resource_id=resource_id,
        details=f"Rejected resource: {resource_title} | reason={reason}",
    )


def log_virus_detected(
    student_id: UUID,
    filename: str,
    virus_name: str,
    ip_address: Optional[str] = None,
):
    """
    Log virus detection in uploaded file.

    Args:
        student_id: Student who uploaded infected file
        filename: Name of infected file
        virus_name: Name of detected virus
        ip_address: IP address of upload request

    Constitutional Compliance:
    - FR-064: Virus detection logged as ERROR
    - FR-065: Security event for virus upload
    """
    error_logger.error(
        f"Virus detected | student_id={student_id} | filename={filename} | virus={virus_name}"
    )

    log_security_event(
        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
        student_id=student_id,
        details=f"Virus detected in upload | filename={filename} | virus={virus_name}",
        ip_address=ip_address,
    )


def log_youtube_quota_warning(
    current_usage: int,
    limit: int,
):
    """
    Log YouTube quota warning when approaching limit.

    Args:
        current_usage: Current videos processed today
        limit: Daily video limit

    Constitutional Compliance:
    - FR-064: YouTube quota warnings logged
    """
    upload_logger.warning(
        f"YouTube quota approaching limit | usage={current_usage}/{limit} ({current_usage/limit*100:.0f}%)"
    )
