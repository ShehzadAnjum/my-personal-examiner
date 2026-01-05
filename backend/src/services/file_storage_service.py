"""
File storage service for Resource Bank.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Principle I: SHA-256 signatures ensure content integrity
- Principle V: student_id-scoped directories for multi-tenant isolation
"""

import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID

import pyclamd

from src.models.enums import ResourceType


def calculate_signature(file_path: str) -> str:
    """
    Calculate SHA-256 hash of file for duplicate detection.

    Args:
        file_path: Absolute path to file

    Returns:
        SHA-256 hash as hexadecimal string (64 chars)

    Constitutional Compliance:
        - Principle I: Content integrity verification
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read in 64KB chunks for memory efficiency
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def get_file_path_for_resource(
    resource_type: ResourceType,
    filename: str,
    student_id: Optional[UUID] = None,
    subject_code: str = "9708",  # Default to Economics
) -> str:
    """
    Generate file path based on resource type and ownership.

    Directory structure:
    - Official: backend/resources/{type}/{subject_code}/
    - User uploads: backend/resources/user_uploads/{student_id}/

    Args:
        resource_type: Type of resource (syllabus, past_paper, etc.)
        filename: Original filename
        student_id: Student ID for user uploads (None for official)
        subject_code: Subject code (default: 9708)

    Returns:
        Relative path from backend/ directory

    Constitutional Compliance:
        - Principle V: student_id-scoped isolation for user uploads
    """
    base_dir = Path("backend/resources")
    
    if resource_type == ResourceType.USER_UPLOAD:
        if not student_id:
            raise ValueError("student_id required for user uploads")
        # Multi-tenant isolation: student-scoped directory
        resource_dir = base_dir / "user_uploads" / str(student_id)
    elif resource_type == ResourceType.SYLLABUS:
        resource_dir = base_dir / "syllabus" / subject_code
    elif resource_type == ResourceType.PAST_PAPER:
        resource_dir = base_dir / "past_papers" / subject_code
    elif resource_type == ResourceType.TEXTBOOK:
        resource_dir = base_dir / "textbooks" / subject_code / "Textbooks"
    elif resource_type == ResourceType.VIDEO:
        resource_dir = base_dir / "videos" / "metadata"
    elif resource_type == ResourceType.ARTICLE:
        resource_dir = base_dir / "downloads"
    else:
        resource_dir = base_dir / "downloads"
    
    return str(resource_dir / filename)


def save_file_to_local(
    source_path: str,
    destination_path: str,
) -> str:
    """
    Save uploaded file to local storage.

    Args:
        source_path: Temporary upload path
        destination_path: Final storage path (relative from backend/)

    Returns:
        Absolute path to saved file

    Raises:
        OSError: If directory creation or file copy fails
    """
    # Ensure destination directory exists
    dest_file = Path(destination_path)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file to destination
    shutil.copy2(source_path, dest_file)
    
    return str(dest_file.absolute())


def scan_file_for_virus(file_path: str) -> dict:
    """
    Scan file for viruses using ClamAV daemon.

    Args:
        file_path: Absolute path to file

    Returns:
        Dict with keys:
        - safe (bool): True if no virus detected
        - virus (str): Virus name if detected
        - warning (str): Warning message if scan unavailable

    Constitutional Compliance:
        - Security: Scan before DB commit to prevent malware storage

    Phase 1 Behavior:
        - If ClamAV unavailable: Log warning, allow upload (manual review)
        - Phase 2: Fail upload if ClamAV unavailable
    """
    try:
        # Connect to ClamAV daemon
        cd = pyclamd.ClamdUnixSocket()
        
        # Scan file
        result = cd.scan_file(file_path)
        
        if result is None:
            # No virus detected
            return {"safe": True}
        else:
            # Virus detected
            virus_name = result[file_path][1]
            # Delete infected file immediately
            os.remove(file_path)
            return {"safe": False, "virus": virus_name}
            
    except FileNotFoundError:
        # ClamAV daemon not running
        # Phase 1: Allow upload with warning (manual review)
        return {
            "safe": True,
            "warning": "ClamAV daemon unavailable - manual review required"
        }
    except Exception as e:
        # Other errors (socket error, permission denied, etc.)
        return {
            "safe": True,
            "warning": f"Virus scan failed: {str(e)} - manual review required"
        }


def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """
    Validate file size is within limits.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB (default: 50)

    Returns:
        True if within limits, False otherwise

    Constitutional Compliance:
        - FR-051: Enforce file size limits per specification
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Original filename

    Returns:
        File extension (lowercase, with dot)
    """
    return Path(filename).suffix.lower()


def create_student_directory(student_id: UUID) -> str:
    """
    Create student-specific upload directory.

    Creates backend/resources/user_uploads/{student_id}/ directory
    for multi-tenant file isolation.

    Args:
        student_id: Student UUID

    Returns:
        Absolute path to student directory

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation via student_id-scoped directories
        - FR-037: Visibility filters enforced at filesystem level
    """
    student_dir = Path("backend/resources/user_uploads") / str(student_id)
    student_dir.mkdir(parents=True, exist_ok=True)
    return str(student_dir.absolute())


def validate_student_quota(student_id: UUID, session) -> tuple[bool, int]:
    """
    Validate student hasn't exceeded resource upload quota.

    Constitutional requirement:
    - FR-050: Maximum 100 resources per student
    - FR-052: Reject uploads when quota exceeded

    Args:
        student_id: Student UUID
        session: SQLModel database session

    Returns:
        Tuple of (within_quota: bool, current_count: int)
        - within_quota: True if student can upload more resources
        - current_count: Current number of resources uploaded by student

    Example:
        within_quota, count = validate_student_quota(student.id, session)
        if not within_quota:
            raise HTTPException(400, f"Quota exceeded: {count}/100 resources")
    """
    from sqlmodel import select
    from src.models.resource import Resource

    # Count resources uploaded by student
    quota_query = select(Resource).where(
        Resource.uploaded_by_student_id == student_id
    )
    student_resources = session.exec(quota_query).all()
    current_count = len(student_resources)

    # Check against quota (100 resources)
    STUDENT_QUOTA = 100
    within_quota = current_count < STUDENT_QUOTA

    return (within_quota, current_count)
