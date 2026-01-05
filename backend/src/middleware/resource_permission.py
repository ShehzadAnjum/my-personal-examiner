"""
Resource permission middleware for signed URL generation and verification.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Principle V: Multi-tenant isolation via signed URLs
- HMAC SHA-256 signatures for time-limited download authorization
"""

import hmac
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID


def generate_signed_url(
    resource_id: UUID,
    student_id: Optional[UUID],
    expires_in: int = 3600,  # 1 hour default
) -> str:
    """
    Generate time-limited signed URL for resource download.

    Args:
        resource_id: Resource UUID
        student_id: Student UUID (for private resources)
        expires_in: Expiration time in seconds (default: 1 hour)

    Returns:
        Query string with signature: ?sig=...&exp=...&student=...

    Constitutional Compliance:
        - Multi-tenant isolation: student_id in signature
        - Time-limited access: expiry timestamp
    """
    secret_key = os.getenv("SIGNING_SECRET_KEY")
    if not secret_key:
        raise ValueError("SIGNING_SECRET_KEY environment variable not set")

    # Calculate expiry timestamp
    expiry = datetime.utcnow() + timedelta(seconds=expires_in)
    expiry_ts = int(expiry.timestamp())

    # Create HMAC signature: resource_id:student_id:expiry
    student_str = str(student_id) if student_id else "null"
    message = f"{resource_id}:{student_str}:{expiry_ts}"
    
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Build query string
    query_params = f"sig={signature}&exp={expiry_ts}"
    if student_id:
        query_params += f"&student={student_id}"

    return query_params


def verify_signed_url(
    resource_id: UUID,
    signature: str,
    expiry_ts: int,
    student_id: Optional[UUID] = None,
) -> bool:
    """
    Verify signed URL for resource download.

    Args:
        resource_id: Resource UUID
        signature: HMAC signature from query string
        expiry_ts: Expiration timestamp from query string
        student_id: Student UUID from query string (optional)

    Returns:
        True if signature is valid and not expired, False otherwise

    Constitutional Compliance:
        - Time-limited access: Reject expired URLs
        - HMAC verification: Constant-time comparison prevents timing attacks
    """
    secret_key = os.getenv("SIGNING_SECRET_KEY")
    if not secret_key:
        return False

    # Check expiry
    current_ts = int(datetime.utcnow().timestamp())
    if current_ts > expiry_ts:
        return False

    # Recreate signature
    student_str = str(student_id) if student_id else "null"
    message = f"{resource_id}:{student_str}:{expiry_ts}"
    
    expected_signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison (prevents timing attacks)
    return hmac.compare_digest(signature, expected_signature)


def check_resource_access(
    resource_visibility: str,
    resource_owner_id: Optional[UUID],
    requesting_student_id: Optional[UUID],
    is_admin: bool = False,
) -> bool:
    """
    Check if student can access resource based on visibility rules.

    Multi-tenant isolation rules:
    - Public: Visible to all authenticated users
    - Private: Only owner + admin
    - Pending Review: Only owner + admin

    Args:
        resource_visibility: Resource visibility (public/private/pending_review)
        resource_owner_id: Student who uploaded resource (NULL for official)
        requesting_student_id: Student requesting access
        is_admin: Whether requesting student is admin

    Returns:
        True if access allowed, False otherwise

    Constitutional Compliance:
        - Principle V: Multi-tenant data isolation enforced
    """
    # Admin can access everything
    if is_admin:
        return True

    # Public resources: accessible to all authenticated users
    if resource_visibility == "public":
        return True

    # Private/Pending resources: only owner can access
    if requesting_student_id and resource_owner_id == requesting_student_id:
        return True

    # Deny access
    return False
