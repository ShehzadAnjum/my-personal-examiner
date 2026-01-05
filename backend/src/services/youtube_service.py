"""
YouTube transcript extraction service for video resources.

Feature: 007-resource-bank-files (User Story 7)
Created: 2025-12-27

Extracts YouTube video transcripts and metadata for inclusion in topic generation.
Uses youtube-transcript-api (unofficial, no API key) for transcripts and YouTube Data API v3
(official) for video metadata.

Constitutional Compliance:
- FR-049: Index YouTube transcripts for searchability
- US7 Acceptance: Extract transcript, parse timestamps, store in metadata
"""

import os
import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptAvailable,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# YouTube Data API v3 (optional - for video metadata)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


class YouTubeQuotaExceeded(Exception):
    """Raised when YouTube API daily quota is exceeded."""

    pass


class YouTubeTranscriptUnavailable(Exception):
    """Raised when transcript cannot be extracted."""

    pass


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID

    Args:
        url: YouTube URL

    Returns:
        Video ID or None if invalid URL

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    if not url:
        return None

    # Try to parse as URL
    parsed = urlparse(url)

    # Format: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            return query_params.get("v", [None])[0]
        # Format: https://www.youtube.com/embed/VIDEO_ID or /v/VIDEO_ID
        elif parsed.path.startswith("/embed/") or parsed.path.startswith("/v/"):
            return parsed.path.split("/")[2]

    # Format: https://youtu.be/VIDEO_ID
    elif parsed.hostname == "youtu.be":
        return parsed.path[1:]  # Remove leading slash

    # Try regex as fallback
    regex_patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard video ID format
        r"^([0-9A-Za-z_-]{11})$",  # Just the video ID
    ]

    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def extract_youtube_transcript(video_id: str, language: str = "en") -> dict:
    """
    Extract YouTube video transcript using youtube-transcript-api.

    Args:
        video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
        language: Preferred transcript language (default: 'en')

    Returns:
        Dict with transcript data:
        {
            'video_id': str,
            'transcript_text': str,  # Full transcript as continuous text
            'transcript_entries': list,  # List of {text, start, duration}
            'language': str,
            'is_generated': bool  # True if auto-generated captions
        }

    Raises:
        YouTubeTranscriptUnavailable: If transcript cannot be extracted

    Constitutional Compliance:
    - FR-049: Makes transcript searchable via full-text search
    """
    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to get manual transcript first (higher quality)
        try:
            transcript = transcript_list.find_manually_created_transcript([language])
            is_generated = False
        except NoTranscriptFound:
            # Fallback to auto-generated transcript
            try:
                transcript = transcript_list.find_generated_transcript([language])
                is_generated = True
            except NoTranscriptFound:
                raise YouTubeTranscriptUnavailable(
                    f"No transcript available in language '{language}'"
                )

        # Fetch transcript data
        transcript_data = transcript.fetch()

        # Extract full text
        full_text = " ".join([entry["text"] for entry in transcript_data])

        return {
            "video_id": video_id,
            "transcript_text": full_text,
            "transcript_entries": transcript_data,  # Contains timestamps
            "language": transcript.language_code,
            "is_generated": is_generated,
        }

    except (VideoUnavailable, TranscriptsDisabled, NoTranscriptAvailable) as e:
        raise YouTubeTranscriptUnavailable(str(e))


def extract_youtube_metadata(video_id: str) -> dict:
    """
    Extract YouTube video metadata using YouTube Data API v3.

    Requires YOUTUBE_API_KEY environment variable.

    Args:
        video_id: YouTube video ID

    Returns:
        Dict with video metadata:
        {
            'title': str,
            'channel': str,
            'duration': str,  # ISO 8601 format (e.g., 'PT15M33S')
            'thumbnail_url': str,
            'description': str,
            'published_at': str
        }

    Raises:
        ValueError: If YOUTUBE_API_KEY not set
        Exception: If API call fails

    Note: Uses YouTube Data API quota (costs 1 unit per request)
    """
    if not YOUTUBE_API_KEY:
        raise ValueError(
            "YOUTUBE_API_KEY environment variable not set. "
            "Cannot fetch video metadata. Will store transcript only."
        )

    try:
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        response = youtube.videos().list(part="snippet,contentDetails", id=video_id).execute()

        if not response.get("items"):
            raise Exception(f"Video {video_id} not found")

        item = response["items"][0]
        snippet = item["snippet"]
        content_details = item["contentDetails"]

        return {
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "duration": content_details["duration"],  # ISO 8601 format
            "thumbnail_url": snippet["thumbnails"]["high"]["url"],
            "description": snippet["description"],
            "published_at": snippet["publishedAt"],
        }

    except ImportError:
        raise ValueError(
            "google-api-python-client not installed. "
            "Run: uv add google-api-python-client"
        )


def extract_timestamps_for_keywords(
    transcript_entries: list[dict], keywords: list[str], context_seconds: int = 30
) -> list[dict]:
    """
    Extract timestamp excerpts from transcript that match keywords.

    Args:
        transcript_entries: List of transcript entries from extract_youtube_transcript
        keywords: List of keywords to search for
        context_seconds: Seconds of context before/after keyword match (default: 30)

    Returns:
        List of timestamp excerpts:
        [
            {
                'keyword': str,
                'timestamp': float,  # Seconds from start
                'text': str,  # Text excerpt with context
                'url': str  # YouTube URL with timestamp (e.g., ?t=123)
            }
        ]

    Example:
        >>> entries = [
        ...     {'text': 'Fiscal policy involves', 'start': 120.5, 'duration': 3.2},
        ...     {'text': 'government spending decisions', 'start': 123.7, 'duration': 2.1}
        ... ]
        >>> extract_timestamps_for_keywords(entries, ['fiscal'])
        [{'keyword': 'fiscal', 'timestamp': 120.5, 'text': '...', 'url': '?t=120'}]
    """
    matches = []

    # Create lowercase keyword set for case-insensitive matching
    keywords_lower = [k.lower() for k in keywords]

    for i, entry in enumerate(transcript_entries):
        text_lower = entry["text"].lower()

        # Check if any keyword matches
        for keyword in keywords_lower:
            if keyword in text_lower:
                # Calculate context window (indices before and after)
                start_time = entry["start"]
                end_time = start_time + context_seconds

                # Collect entries within context window
                context_entries = []
                for j in range(max(0, i - 5), min(len(transcript_entries), i + 10)):
                    context_entry = transcript_entries[j]
                    if (
                        context_entry["start"] >= start_time - context_seconds
                        and context_entry["start"] <= end_time
                    ):
                        context_entries.append(context_entry)

                # Build context text
                context_text = " ".join([e["text"] for e in context_entries])

                matches.append(
                    {
                        "keyword": keyword,
                        "timestamp": start_time,
                        "text": context_text,
                        "url": f"?t={int(start_time)}",  # YouTube timestamp format
                    }
                )

                # Only match each keyword once per entry
                break

    return matches


def validate_youtube_url(url: str) -> bool:
    """
    Validate YouTube URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid YouTube URL, False otherwise
    """
    video_id = extract_video_id(url)
    return video_id is not None and len(video_id) == 11


def process_youtube_video(
    url: str, keywords: Optional[list[str]] = None
) -> dict:
    """
    Complete YouTube video processing: extract metadata, transcript, and timestamps.

    Args:
        url: YouTube video URL
        keywords: Optional keywords for timestamp extraction

    Returns:
        Complete video data:
        {
            'video_id': str,
            'url': str,
            'title': str,  # From API if available
            'channel': str,
            'duration': str,
            'transcript_text': str,
            'transcript_entries': list,
            'language': str,
            'is_generated': bool,
            'timestamp_matches': list,  # If keywords provided
            'error': str | None
        }

    Constitutional Compliance:
    - FR-049: Full transcript indexed for searchability
    - US7 Acceptance Scenario 2: Timestamp extraction for keywords
    """
    # Validate URL
    if not validate_youtube_url(url):
        return {"error": "Invalid YouTube URL format"}

    # Extract video ID
    video_id = extract_video_id(url)

    result = {
        "video_id": video_id,
        "url": url,
        "error": None,
    }

    # Extract transcript (required)
    try:
        transcript_data = extract_youtube_transcript(video_id)
        result.update(transcript_data)
    except YouTubeTranscriptUnavailable as e:
        result["error"] = f"Transcript unavailable: {str(e)}"
        result["transcript_text"] = None

    # Extract metadata (optional - requires API key)
    try:
        metadata = extract_youtube_metadata(video_id)
        result.update(metadata)
    except (ValueError, Exception) as e:
        # Graceful degradation - metadata not critical
        result["title"] = f"YouTube Video {video_id}"
        result["metadata_error"] = str(e)

    # Extract timestamp matches if keywords provided
    if keywords and result.get("transcript_entries"):
        timestamp_matches = extract_timestamps_for_keywords(
            result["transcript_entries"], keywords
        )
        result["timestamp_matches"] = timestamp_matches

    return result


# Quota tracking
class YouTubeQuotaTracker:
    """
    Track YouTube API usage to prevent quota exhaustion.

    YouTube Data API v3 quota: 10,000 units/day (free tier)
    - videos().list() costs 1 unit
    - Phase 1 MVP limit: 10 videos/day (well under quota)
    """

    def __init__(self, daily_limit: int = 10):
        """
        Initialize quota tracker.

        Args:
            daily_limit: Max videos to process per day (default: 10 for Phase 1)
        """
        self.daily_limit = daily_limit
        self._videos_processed_today = 0
        self._reset_date = None

    def check_quota(self) -> bool:
        """
        Check if quota allows processing another video.

        Returns:
            True if quota available, False if exhausted
        """
        from datetime import date

        today = date.today()

        # Reset counter if new day
        if self._reset_date != today:
            self._videos_processed_today = 0
            self._reset_date = today

        return self._videos_processed_today < self.daily_limit

    def increment_usage(self):
        """Increment video processing counter."""
        self._videos_processed_today += 1

        # Log warning if approaching quota
        if self._videos_processed_today >= self.daily_limit * 0.8:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"YouTube quota usage: {self._videos_processed_today}/{self.daily_limit} "
                f"({self._videos_processed_today / self.daily_limit * 100:.0f}%)"
            )

    def get_remaining_quota(self) -> int:
        """Get remaining videos that can be processed today."""
        return max(0, self.daily_limit - self._videos_processed_today)


# Global quota tracker instance
quota_tracker = YouTubeQuotaTracker(daily_limit=10)
