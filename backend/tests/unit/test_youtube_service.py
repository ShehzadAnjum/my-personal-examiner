"""
Unit tests for YouTube transcript extraction service.

Feature: 007-resource-bank-files (User Story 7)
Created: 2025-12-27

Tests YouTube transcript extraction, metadata retrieval, quota tracking,
and error handling for unavailable transcripts.

Constitutional Compliance:
- FR-049: Index YouTube transcripts for searchability
- US7: Extract transcript with timestamps, graceful degradation
"""

from unittest.mock import Mock, patch

import pytest

from src.services.youtube_service import (
    YouTubeQuotaTracker,
    YouTubeTranscriptUnavailable,
    extract_timestamps_for_keywords,
    extract_video_id,
    extract_youtube_metadata,
    extract_youtube_transcript,
    process_youtube_video,
    validate_youtube_url,
)


class TestExtractVideoId:
    """Test extract_video_id function for various URL formats."""

    def test_extracts_from_watch_url(self):
        """Should extract video ID from youtube.com/watch?v= format."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extracts_from_short_url(self):
        """Should extract video ID from youtu.be/ format."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extracts_from_embed_url(self):
        """Should extract video ID from youtube.com/embed/ format."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extracts_from_v_url(self):
        """Should extract video ID from youtube.com/v/ format."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extracts_from_just_video_id(self):
        """Should extract video ID when just ID provided."""
        video_id = extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_returns_none_for_invalid_url(self):
        """Should return None for invalid URLs."""
        assert extract_video_id("https://www.example.com") is None
        assert extract_video_id("") is None
        assert extract_video_id(None) is None


class TestValidateYoutubeUrl:
    """Test validate_youtube_url function."""

    def test_validates_correct_urls(self):
        """Should validate correct YouTube URLs."""
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert validate_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert validate_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is True

    def test_rejects_invalid_urls(self):
        """Should reject invalid URLs."""
        assert validate_youtube_url("https://www.example.com") is False
        assert validate_youtube_url("invalid") is False
        assert validate_youtube_url("") is False


class TestExtractYoutubeTranscript:
    """Test extract_youtube_transcript function."""

    @patch("src.services.youtube_service.YouTubeTranscriptApi")
    def test_extracts_manual_transcript(self, mock_api):
        """Should prefer manual transcript over auto-generated."""
        # Mock transcript list
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.fetch.return_value = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "World", "start": 1.0, "duration": 1.0},
        ]

        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.return_value = mock_transcript

        mock_api.list_transcripts.return_value = mock_transcript_list

        # Extract transcript
        result = extract_youtube_transcript("dQw4w9WgXcQ")

        # Verify
        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["transcript_text"] == "Hello World"
        assert result["language"] == "en"
        assert result["is_generated"] is False
        assert len(result["transcript_entries"]) == 2

    @patch("src.services.youtube_service.YouTubeTranscriptApi")
    def test_falls_back_to_generated_transcript(self, mock_api):
        """Should fallback to auto-generated if no manual transcript."""
        from youtube_transcript_api._errors import NoTranscriptFound

        # Mock transcript list
        mock_generated = Mock()
        mock_generated.language_code = "en"
        mock_generated.fetch.return_value = [
            {"text": "Auto generated", "start": 0.0, "duration": 2.0}
        ]

        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.side_effect = NoTranscriptFound(
            "video_id", ["en"], []
        )
        mock_transcript_list.find_generated_transcript.return_value = mock_generated

        mock_api.list_transcripts.return_value = mock_transcript_list

        # Extract transcript
        result = extract_youtube_transcript("dQw4w9WgXcQ")

        # Verify
        assert result["is_generated"] is True
        assert result["transcript_text"] == "Auto generated"

    @patch("src.services.youtube_service.YouTubeTranscriptApi")
    def test_raises_error_when_no_transcript_available(self, mock_api):
        """Should raise error when no transcript available."""
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.side_effect = NoTranscriptFound(
            "video_id", ["en"], []
        )
        mock_transcript_list.find_generated_transcript.side_effect = NoTranscriptFound(
            "video_id", ["en"], []
        )

        mock_api.list_transcripts.return_value = mock_transcript_list

        # Should raise error
        with pytest.raises(YouTubeTranscriptUnavailable):
            extract_youtube_transcript("dQw4w9WgXcQ")


class TestExtractYoutubeMetadata:
    """Test extract_youtube_metadata function."""

    @patch.dict("os.environ", {"YOUTUBE_API_KEY": "test_api_key"})
    @patch("src.services.youtube_service.build")
    def test_extracts_metadata_from_api(self, mock_build):
        """Should extract video metadata from YouTube Data API."""
        # Mock API response
        mock_youtube = Mock()
        mock_videos = Mock()
        mock_list = Mock()

        mock_list.execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "title": "Test Video",
                        "channelTitle": "Test Channel",
                        "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
                        "description": "Test description",
                        "publishedAt": "2023-01-01T00:00:00Z",
                    },
                    "contentDetails": {"duration": "PT15M33S"},
                }
            ]
        }

        mock_videos.list.return_value = mock_list
        mock_youtube.videos.return_value = mock_videos
        mock_build.return_value = mock_youtube

        # Extract metadata
        result = extract_youtube_metadata("dQw4w9WgXcQ")

        # Verify
        assert result["title"] == "Test Video"
        assert result["channel"] == "Test Channel"
        assert result["duration"] == "PT15M33S"
        assert result["thumbnail_url"] == "https://example.com/thumb.jpg"

    @patch.dict("os.environ", {"YOUTUBE_API_KEY": ""}, clear=True)
    def test_raises_error_when_no_api_key(self):
        """Should raise error when YOUTUBE_API_KEY not set."""
        with pytest.raises(ValueError, match="YOUTUBE_API_KEY"):
            extract_youtube_metadata("dQw4w9WgXcQ")


class TestExtractTimestampsForKeywords:
    """Test extract_timestamps_for_keywords function."""

    def test_extracts_timestamps_for_matching_keywords(self):
        """Should extract timestamps where keywords appear."""
        transcript_entries = [
            {"text": "Introduction to economics", "start": 0.0, "duration": 3.0},
            {"text": "Fiscal policy involves", "start": 120.5, "duration": 3.2},
            {"text": "government spending decisions", "start": 123.7, "duration": 2.1},
            {"text": "Monetary policy is different", "start": 200.0, "duration": 3.0},
        ]

        matches = extract_timestamps_for_keywords(transcript_entries, ["fiscal"])

        # Should find fiscal policy
        assert len(matches) == 1
        assert matches[0]["keyword"] == "fiscal"
        assert matches[0]["timestamp"] == 120.5
        assert "fiscal policy involves" in matches[0]["text"].lower()
        assert matches[0]["url"] == "?t=120"

    def test_case_insensitive_keyword_matching(self):
        """Should match keywords case-insensitively."""
        transcript_entries = [
            {"text": "FISCAL POLICY", "start": 10.0, "duration": 2.0},
        ]

        matches = extract_timestamps_for_keywords(transcript_entries, ["fiscal"])

        assert len(matches) == 1
        assert matches[0]["keyword"] == "fiscal"

    def test_includes_context_around_keyword(self):
        """Should include context before and after keyword."""
        transcript_entries = [
            {"text": "Before context", "start": 100.0, "duration": 2.0},
            {"text": "Fiscal policy keyword", "start": 102.0, "duration": 2.0},
            {"text": "After context", "start": 104.0, "duration": 2.0},
        ]

        matches = extract_timestamps_for_keywords(
            transcript_entries, ["fiscal"], context_seconds=10
        )

        # Should include all three entries
        assert "Before context" in matches[0]["text"]
        assert "Fiscal policy keyword" in matches[0]["text"]
        assert "After context" in matches[0]["text"]

    def test_returns_empty_list_when_no_matches(self):
        """Should return empty list when no keywords match."""
        transcript_entries = [
            {"text": "Economics lecture", "start": 0.0, "duration": 2.0},
        ]

        matches = extract_timestamps_for_keywords(transcript_entries, ["fiscal"])

        assert matches == []


class TestProcessYoutubeVideo:
    """Test process_youtube_video complete workflow."""

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_processes_video_successfully(self, mock_transcript, mock_metadata):
        """Should process video with transcript and metadata."""
        # Mock transcript
        mock_transcript.return_value = {
            "video_id": "dQw4w9WgXcQ",
            "transcript_text": "Full transcript text",
            "transcript_entries": [{"text": "test", "start": 0.0, "duration": 1.0}],
            "language": "en",
            "is_generated": False,
        }

        # Mock metadata
        mock_metadata.return_value = {
            "title": "Test Video",
            "channel": "Test Channel",
            "duration": "PT5M",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "description": "Description",
            "published_at": "2023-01-01T00:00:00Z",
        }

        # Process video
        result = process_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Verify
        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["transcript_text"] == "Full transcript text"
        assert result["title"] == "Test Video"
        assert result["error"] is None

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_graceful_degradation_when_transcript_unavailable(
        self, mock_transcript, mock_metadata
    ):
        """Should store metadata even when transcript fails."""
        # Mock transcript failure
        mock_transcript.side_effect = YouTubeTranscriptUnavailable("No transcript")

        # Mock metadata success
        mock_metadata.return_value = {
            "title": "Test Video",
            "channel": "Test Channel",
            "duration": "PT5M",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "description": "Description",
            "published_at": "2023-01-01T00:00:00Z",
        }

        # Process video
        result = process_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Verify graceful degradation
        assert result["error"] == "Transcript unavailable: No transcript"
        assert result["transcript_text"] is None
        assert result["title"] == "Test Video"  # Metadata still extracted

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_extracts_timestamps_when_keywords_provided(
        self, mock_transcript, mock_metadata
    ):
        """Should extract timestamps when keywords provided."""
        # Mock transcript
        mock_transcript.return_value = {
            "video_id": "dQw4w9WgXcQ",
            "transcript_text": "Full transcript",
            "transcript_entries": [
                {"text": "Fiscal policy discussion", "start": 120.0, "duration": 3.0}
            ],
            "language": "en",
            "is_generated": False,
        }

        # Mock metadata
        mock_metadata.return_value = {"title": "Test Video"}

        # Process with keywords
        result = process_youtube_video(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ", keywords=["fiscal"]
        )

        # Verify timestamps extracted
        assert "timestamp_matches" in result
        assert len(result["timestamp_matches"]) == 1
        assert result["timestamp_matches"][0]["keyword"] == "fiscal"


class TestYoutubeQuotaTracker:
    """Test YouTubeQuotaTracker quota management."""

    def test_allows_processing_within_quota(self):
        """Should allow processing when quota available."""
        tracker = YouTubeQuotaTracker(daily_limit=10)

        # Process 5 videos
        for _ in range(5):
            assert tracker.check_quota() is True
            tracker.increment_usage()

        # Still within quota
        assert tracker.check_quota() is True
        assert tracker.get_remaining_quota() == 5

    def test_blocks_processing_when_quota_exceeded(self):
        """Should block processing when quota exhausted."""
        tracker = YouTubeQuotaTracker(daily_limit=3)

        # Process 3 videos (quota limit)
        for _ in range(3):
            assert tracker.check_quota() is True
            tracker.increment_usage()

        # Quota exhausted
        assert tracker.check_quota() is False
        assert tracker.get_remaining_quota() == 0

    def test_resets_quota_on_new_day(self):
        """Should reset quota counter on new day."""
        from datetime import date, timedelta

        tracker = YouTubeQuotaTracker(daily_limit=10)

        # Process 10 videos (exhaust quota)
        for _ in range(10):
            tracker.increment_usage()

        assert tracker.check_quota() is False

        # Simulate new day
        tracker._reset_date = date.today() - timedelta(days=1)

        # Quota should be available again
        assert tracker.check_quota() is True
        assert tracker.get_remaining_quota() == 10

    def test_logs_warning_when_approaching_quota(self, caplog):
        """Should log warning when approaching quota (80%)."""
        import logging

        tracker = YouTubeQuotaTracker(daily_limit=10)

        # Process 8 videos (80% of quota)
        for _ in range(8):
            tracker.increment_usage()

        # Should have logged warning
        assert any("YouTube quota usage" in record.message for record in caplog.records)
