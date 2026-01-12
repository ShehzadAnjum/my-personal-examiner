"""
Integration tests for YouTube video upload workflow.

Feature: 007-resource-bank-files (User Story 7)
Created: 2025-12-27

Tests end-to-end YouTube upload workflow:
1. Admin uploads YouTube URL
2. System extracts transcript and metadata
3. Resource created with searchable transcript
4. Full-text search finds video by transcript content

Constitutional Compliance:
- FR-049: YouTube transcripts indexed for searchability
- US7: Extract transcript with timestamps, graceful degradation
"""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app
from src.models.enums import ResourceType, Visibility
from src.models.resource import Resource
from src.models.student import Student
from src.services.youtube_service import YouTubeTranscriptUnavailable


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin(db_session: Session):
    admin = Student(
        id=uuid4(),
        email="admin@test.com",
        full_name="Admin User",
        is_admin=True,
        hashed_password="hash_admin",
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def student(db_session: Session):
    student = Student(
        id=uuid4(),
        email="student@test.com",
        full_name="Student User",
        is_admin=False,
        hashed_password="hash_student",
    )
    db_session.add(student)
    db_session.commit()
    return student


class TestYoutubeUploadWorkflow:
    """Test end-to-end YouTube upload workflow."""

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_admin_can_upload_youtube_video(
        self, mock_transcript, mock_metadata, client, admin, db_session
    ):
        """Admin should be able to upload YouTube video by URL."""
        # Mock successful transcript extraction
        mock_transcript.return_value = {
            "video_id": "dQw4w9WgXcQ",
            "transcript_text": "This video explains fiscal policy and government spending decisions.",
            "transcript_entries": [
                {"text": "This video explains", "start": 0.0, "duration": 2.0},
                {"text": "fiscal policy and", "start": 2.0, "duration": 2.0},
                {"text": "government spending decisions", "start": 4.0, "duration": 2.0},
            ],
            "language": "en",
            "is_generated": False,
        }

        # Mock metadata extraction
        mock_metadata.return_value = {
            "title": "Fiscal Policy Explained",
            "channel": "Economics Teacher",
            "duration": "PT15M33S",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "description": "A comprehensive guide to fiscal policy",
            "published_at": "2023-01-01T00:00:00Z",
        }

        # Upload YouTube video
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify resource created
        assert data["resource_type"] == "video"
        assert data["title"] == "Fiscal Policy Explained"
        assert data["source_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert data["visibility"] == "public"  # Admin uploads auto-approved
        assert data["admin_approved"] is True

        # Verify metadata stored
        assert "video_id" in data["metadata"]
        assert data["metadata"]["video_id"] == "dQw4w9WgXcQ"
        assert data["metadata"]["channel"] == "Economics Teacher"
        assert data["metadata"]["duration"] == "PT15M33S"

        # Verify transcript stored
        assert "extracted_text" in data["metadata"]
        assert "fiscal policy" in data["metadata"]["extracted_text"].lower()

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_student_upload_requires_approval(
        self, mock_transcript, mock_metadata, client, student, db_session
    ):
        """Student YouTube uploads should require admin approval."""
        # Mock transcript
        mock_transcript.return_value = {
            "video_id": "abc123",
            "transcript_text": "Student uploaded video",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        # Mock metadata
        mock_metadata.return_value = {"title": "Student Video"}

        # Student uploads video
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=abc123"},
            headers={"Authorization": f"Bearer {student.id}"},
        )

        assert response.status_code == 201
        data = response.json()

        # Should require approval
        assert data["visibility"] == "pending_review"
        assert data["admin_approved"] is False

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_custom_title_overrides_api_title(
        self, mock_transcript, mock_metadata, client, admin
    ):
        """Should use custom title if provided."""
        mock_transcript.return_value = {
            "video_id": "test123",
            "transcript_text": "Test video",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Original Title"}

        # Upload with custom title
        response = client.post(
            "/api/resources/upload/youtube",
            data={
                "url": "https://www.youtube.com/watch?v=test123",
                "title": "My Custom Title",
            },
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "My Custom Title"

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_prevents_duplicate_videos(
        self, mock_transcript, mock_metadata, client, admin, db_session
    ):
        """Should prevent uploading same video twice."""
        # Mock successful extraction
        mock_transcript.return_value = {
            "video_id": "duplicate123",
            "transcript_text": "Test",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Duplicate Video"}

        # Upload first time
        response1 = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=duplicate123"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response1.status_code == 201

        # Try uploading again
        response2 = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=duplicate123"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response2.status_code == 409
        assert "already uploaded" in response2.json()["detail"].lower()

    def test_validates_youtube_url_format(self, client, admin):
        """Should reject invalid YouTube URLs."""
        # Invalid URL
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.example.com/video"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 400
        assert "Invalid YouTube URL" in response.json()["detail"]

    @patch("src.services.youtube_service.quota_tracker")
    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_enforces_daily_quota(
        self, mock_transcript, mock_metadata, mock_quota, client, admin
    ):
        """Should enforce 10 videos/day quota."""
        # Mock quota exceeded
        mock_quota.check_quota.return_value = False
        mock_quota.daily_limit = 10

        # Try to upload
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=test123"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 429
        assert "quota exceeded" in response.json()["detail"].lower()

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_enforces_student_resource_quota(
        self, mock_transcript, mock_metadata, client, student, db_session
    ):
        """Should enforce 100 resources/student quota."""
        # Create 100 existing resources for student
        for i in range(100):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}",
                file_path=f"/fake/resource{i}.pdf",
                uploaded_by_student_id=student.id,
                visibility=Visibility.PRIVATE,
                admin_approved=False,
                signature=f"sig{i}",
            )
            db_session.add(resource)

        db_session.commit()

        # Mock successful extraction
        mock_transcript.return_value = {
            "video_id": "test123",
            "transcript_text": "Test",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Test Video"}

        # Try to upload 101st resource
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=test123"},
            headers={"Authorization": f"Bearer {student.id}"},
        )

        assert response.status_code == 400
        assert "quota exceeded" in response.json()["detail"].lower()
        assert "100/100" in response.json()["detail"]

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_graceful_degradation_when_transcript_unavailable(
        self, mock_transcript, mock_metadata, client, admin
    ):
        """Should store metadata even when transcript unavailable."""
        # Mock transcript failure
        mock_transcript.side_effect = YouTubeTranscriptUnavailable("No transcript")

        # Mock metadata success
        mock_metadata.return_value = {
            "title": "Video Without Transcript",
            "channel": "Test Channel",
            "duration": "PT5M",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "description": "Description",
            "published_at": "2023-01-01T00:00:00Z",
        }

        # Upload video
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=notranscript"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify metadata stored
        assert data["title"] == "Video Without Transcript"
        assert data["metadata"]["channel"] == "Test Channel"

        # Transcript should be None
        assert data["metadata"].get("extracted_text") is None


class TestYoutubeSearchability:
    """Test that YouTube transcripts are searchable."""

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_youtube_transcript_searchable_via_full_text_search(
        self, mock_transcript, mock_metadata, client, admin, db_session
    ):
        """YouTube transcript should be searchable via full-text search endpoint."""
        # Mock transcript with unique keywords
        mock_transcript.return_value = {
            "video_id": "search123",
            "transcript_text": "This lecture covers marginal propensity to consume and aggregate demand.",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Economics Lecture"}

        # Upload video
        upload_response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=search123"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert upload_response.status_code == 201
        video_id = upload_response.json()["id"]

        # Search for transcript keywords
        search_response = client.get(
            "/api/resources/search?query=marginal%20propensity&limit=20"
        )

        assert search_response.status_code == 200
        results = search_response.json()

        # Should find the video
        resource_ids = [r["resource_id"] for r in results]
        assert video_id in resource_ids

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_youtube_video_appears_in_auto_selection(
        self, mock_transcript, mock_metadata, client, admin, db_session
    ):
        """Tagged YouTube video should appear in auto-selection."""
        from src.models.syllabus_point_resource import SyllabusPointResource
        from src.services.resource_service import get_resources_for_syllabus_point

        # Mock transcript
        mock_transcript.return_value = {
            "video_id": "autoselect123",
            "transcript_text": "Fiscal policy video transcript",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Fiscal Policy Video"}

        # Upload video
        upload_response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=autoselect123"},
            headers={"Authorization": f"Bearer {admin.id}"},
        )

        assert upload_response.status_code == 201
        video_resource_id = upload_response.json()["id"]

        # Tag video to syllabus point
        syllabus_point_id = uuid4()
        tag = SyllabusPointResource(
            syllabus_point_id=syllabus_point_id,
            resource_id=video_resource_id,
            relevance_score=0.9,
            added_by="admin",
        )
        db_session.add(tag)
        db_session.commit()

        # Trigger auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id, session=db_session, limit=5
        )

        # Verify video appears
        assert len(selected) == 1
        assert selected[0]["resource_id"] == str(video_resource_id)
        assert selected[0]["resource_type"] == "video"


class TestYoutubeAccessControl:
    """Test YouTube video access control."""

    @patch("src.services.youtube_service.extract_youtube_metadata")
    @patch("src.services.youtube_service.extract_youtube_transcript")
    def test_student_cannot_see_other_students_pending_videos(
        self, mock_transcript, mock_metadata, client, db_session
    ):
        """Student A should not see Student B's pending YouTube videos."""
        # Create two students
        student_a = Student(
            id=uuid4(), email="a@test.com", full_name="Student A", is_admin=False, hashed_password="hash"
        )
        student_b = Student(
            id=uuid4(), email="b@test.com", full_name="Student B", is_admin=False, hashed_password="hash"
        )
        db_session.add_all([student_a, student_b])
        db_session.commit()

        # Mock transcript
        mock_transcript.return_value = {
            "video_id": "private123",
            "transcript_text": "Private video",
            "transcript_entries": [],
            "language": "en",
            "is_generated": False,
        }

        mock_metadata.return_value = {"title": "Student B's Video"}

        # Student B uploads video
        response = client.post(
            "/api/resources/upload/youtube",
            data={"url": "https://www.youtube.com/watch?v=private123"},
            headers={"Authorization": f"Bearer {student_b.id}"},
        )

        assert response.status_code == 201

        # Student A searches
        search_response = client.get(
            "/api/resources/search?query=Student%20B%20Video&public_only=true&limit=20"
        )

        # Should not find Student B's pending video
        results = search_response.json()
        titles = [r["title"] for r in results]
        assert "Student B's Video" not in titles
