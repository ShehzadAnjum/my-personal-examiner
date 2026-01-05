"""
Cache Service

File-based caching for resource bank explanations with signature validation.

Feature: 006-resource-bank
Architecture:
- Cache location: backend/cache/resources/explanations/
- File format: JSON with metadata
- Signature-based validation using SHA-256
- DB is primary, cache is secondary (DB → Cache sync direction)
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

# Default cache directory (relative to backend root)
DEFAULT_CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "resources" / "explanations"


def get_cache_dir() -> Path:
    """
    Get the cache directory path.

    Uses CACHE_DIR environment variable if set, otherwise default.

    Returns:
        Path: Cache directory path
    """
    cache_dir = os.environ.get("CACHE_DIR")
    if cache_dir:
        return Path(cache_dir) / "resources" / "explanations"
    return DEFAULT_CACHE_DIR


def ensure_cache_dir() -> Path:
    """
    Ensure cache directory exists.

    Returns:
        Path: Cache directory path
    """
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_path(syllabus_point_id: UUID, version: int) -> Path:
    """
    Get the file path for a cached explanation.

    Args:
        syllabus_point_id: Syllabus point UUID
        version: Explanation version number

    Returns:
        Path: Full path to cache file
    """
    cache_dir = ensure_cache_dir()
    filename = f"{syllabus_point_id}_v{version}.json"
    return cache_dir / filename


def compute_signature(content: dict, timestamp: datetime) -> str:
    """
    Compute SHA-256 signature for cache validation.

    Signature is computed from:
    - JSON-serialized content (sorted keys for consistency)
    - ISO timestamp

    Args:
        content: Explanation content dict
        timestamp: Creation/update timestamp

    Returns:
        str: 64-character hex SHA-256 hash
    """
    # Sort keys for consistent hashing
    content_str = json.dumps(content, sort_keys=True)
    timestamp_str = timestamp.isoformat()

    combined = f"{content_str}:{timestamp_str}"
    return hashlib.sha256(combined.encode()).hexdigest()


def save_to_cache(
    syllabus_point_id: UUID,
    version: int,
    content: dict,
    signature: str,
    metadata: Optional[dict] = None,
) -> Path:
    """
    Save explanation to local cache.

    Args:
        syllabus_point_id: Syllabus point UUID
        version: Explanation version number
        content: Explanation content dict
        signature: Pre-computed SHA-256 signature
        metadata: Optional additional metadata

    Returns:
        Path: Path to saved cache file

    File Format:
        {
            "syllabus_point_id": "uuid",
            "version": 1,
            "content": { ... },
            "signature": "sha256-hash",
            "cached_at": "iso-datetime",
            "metadata": { ... }
        }
    """
    cache_path = get_cache_path(syllabus_point_id, version)

    cache_data = {
        "syllabus_point_id": str(syllabus_point_id),
        "version": version,
        "content": content,
        "signature": signature,
        "cached_at": datetime.utcnow().isoformat(),
        "metadata": metadata or {},
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    return cache_path


def get_from_cache(
    syllabus_point_id: UUID,
    version: int,
) -> Optional[dict]:
    """
    Get explanation from local cache.

    Args:
        syllabus_point_id: Syllabus point UUID
        version: Explanation version number

    Returns:
        dict | None: Cached data if found and valid, None otherwise

    Returns None if:
        - File doesn't exist
        - File is corrupted (invalid JSON)
    """
    cache_path = get_cache_path(syllabus_point_id, version)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Corrupted cache file - will be refreshed from DB
        return None


def validate_cache_signature(
    syllabus_point_id: UUID,
    version: int,
    expected_signature: str,
) -> bool:
    """
    Validate cache entry against expected signature.

    Args:
        syllabus_point_id: Syllabus point UUID
        version: Explanation version number
        expected_signature: Signature from database

    Returns:
        bool: True if cache is valid and up-to-date
    """
    cached_data = get_from_cache(syllabus_point_id, version)

    if not cached_data:
        return False

    return cached_data.get("signature") == expected_signature


def delete_from_cache(syllabus_point_id: UUID, version: int) -> bool:
    """
    Delete a cache entry.

    Args:
        syllabus_point_id: Syllabus point UUID
        version: Explanation version number

    Returns:
        bool: True if deleted, False if not found
    """
    cache_path = get_cache_path(syllabus_point_id, version)

    if cache_path.exists():
        cache_path.unlink()
        return True

    return False


def list_cached_entries() -> list[dict]:
    """
    List all cached entries with their signatures.

    Returns:
        list[dict]: List of cached entries with:
            - syllabus_point_id: UUID string
            - version: int
            - signature: str
            - cached_at: str (ISO datetime)
            - file_path: str
    """
    cache_dir = ensure_cache_dir()
    entries = []

    for cache_file in cache_dir.glob("*.json"):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                entries.append(
                    {
                        "syllabus_point_id": data.get("syllabus_point_id"),
                        "version": data.get("version"),
                        "signature": data.get("signature"),
                        "cached_at": data.get("cached_at"),
                        "file_path": str(cache_file),
                    }
                )
        except (json.JSONDecodeError, IOError):
            # Skip corrupted files
            continue

    return entries


def clear_cache() -> int:
    """
    Clear all cached entries.

    Returns:
        int: Number of files deleted

    Warning:
        Use with caution - will remove all cached explanations.
    """
    cache_dir = ensure_cache_dir()
    count = 0

    for cache_file in cache_dir.glob("*.json"):
        cache_file.unlink()
        count += 1

    return count


def get_cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        dict: Cache stats including:
            - total_entries: int
            - total_size_bytes: int
            - oldest_entry: str (ISO datetime)
            - newest_entry: str (ISO datetime)
    """
    entries = list_cached_entries()
    cache_dir = ensure_cache_dir()

    total_size = sum(
        f.stat().st_size for f in cache_dir.glob("*.json") if f.is_file()
    )

    cached_times = [e.get("cached_at") for e in entries if e.get("cached_at")]
    cached_times.sort()

    return {
        "total_entries": len(entries),
        "total_size_bytes": total_size,
        "oldest_entry": cached_times[0] if cached_times else None,
        "newest_entry": cached_times[-1] if cached_times else None,
    }


def get_stale_entries(db_signatures: dict[tuple[str, int], str]) -> list[dict]:
    """
    Find cache entries that are stale (signature mismatch with DB).

    Args:
        db_signatures: Dict mapping (syllabus_point_id, version) to signature

    Returns:
        list[dict]: List of stale entries that need refresh
    """
    entries = list_cached_entries()
    stale = []

    for entry in entries:
        key = (entry.get("syllabus_point_id"), entry.get("version"))
        db_sig = db_signatures.get(key)

        if db_sig is None:
            # Entry exists in cache but not in DB - stale
            stale.append(entry)
        elif db_sig != entry.get("signature"):
            # Signature mismatch - needs refresh
            stale.append(entry)

    return stale
