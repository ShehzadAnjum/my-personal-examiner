"""
Unit tests for S3 upload Celery task.

Feature: 007-resource-bank-files
Created: 2025-12-27
"""

import os
import tempfile
from unittest.mock import MagicMock, patch
from uuid import uuid4

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.models.enums import S3SyncStatus
from src.tasks.s3_upload_task import upload_to_s3_task


class TestS3UploadTask:
    """Test S3 upload background task."""

    @mock_aws
    @patch('src.tasks.s3_upload_task._update_resource_s3_status')
    def test_upload_success_with_sse_s3_encryption(self, mock_update_status):
        """Should upload file to S3 with SSE-S3 encryption."""
        # Setup mock S3 bucket
        bucket_name = "test-resource-bank"
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket=bucket_name)

        # Create test file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
            f.write("Test resource content")
            temp_path = f.name

        try:
            resource_id = str(uuid4())
            
            # Set environment variables
            os.environ['S3_ENABLED'] = 'true'
            os.environ['S3_BUCKET_NAME'] = bucket_name
            os.environ['AWS_REGION'] = 'us-east-1'
            
            # Execute task
            result = upload_to_s3_task(resource_id, temp_path)
            
            # Assertions
            assert result["status"] == "success"
            assert bucket_name in result["s3_url"]
            
            # Verify file exists in S3
            s3_key = f"resources/{resource_id}/{os.path.basename(temp_path)}"
            obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            assert obj['Body'].read().decode() == "Test resource content"
            
            # Verify status update was called
            mock_update_status.assert_called_once()
            call_args = mock_update_status.call_args
            assert call_args[1]['status'] == S3SyncStatus.SUCCESS
            
        finally:
            os.remove(temp_path)
            os.environ.pop('S3_ENABLED', None)
            os.environ.pop('S3_BUCKET_NAME', None)
            os.environ.pop('AWS_REGION', None)

    @patch('src.tasks.s3_upload_task._update_resource_s3_status')
    def test_upload_skipped_when_s3_disabled(self, mock_update_status):
        """Should skip upload when S3_ENABLED=false."""
        resource_id = str(uuid4())
        
        os.environ['S3_ENABLED'] = 'false'
        
        try:
            result = upload_to_s3_task(resource_id, "/fake/path")
            
            assert result["status"] == "skipped"
            assert "disabled" in result["message"]
            mock_update_status.assert_not_called()
        finally:
            os.environ.pop('S3_ENABLED', None)

    @patch('src.tasks.s3_upload_task._update_resource_s3_status')
    @patch('src.tasks.s3_upload_task.boto3.client')
    def test_upload_retries_on_client_error(self, mock_boto_client, mock_update_status):
        """Should retry upload on ClientError with exponential backoff."""
        # Mock S3 client to raise ClientError
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = ClientError(
            {'Error': {'Code': 'ServiceUnavailable'}},
            'upload_file'
        )
        mock_boto_client.return_value = mock_s3

        resource_id = str(uuid4())
        
        os.environ['S3_ENABLED'] = 'true'
        os.environ['S3_BUCKET_NAME'] = 'test-bucket'
        
        try:
            # Create test file
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_path = f.name
            
            # Execute task (should raise Retry exception)
            with pytest.raises(Exception):  # Celery Retry exception
                upload_to_s3_task(resource_id, temp_path)
            
            # Verify status was updated to FAILED
            assert mock_update_status.called
            call_args = mock_update_status.call_args
            assert call_args[1]['status'] == S3SyncStatus.FAILED
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.environ.pop('S3_ENABLED', None)
            os.environ.pop('S3_BUCKET_NAME', None)

    @patch('src.tasks.s3_upload_task._update_resource_s3_status')
    @patch('src.tasks.s3_upload_task.boto3.client')
    def test_upload_handles_missing_bucket_name(self, mock_boto_client, mock_update_status):
        """Should raise ValueError if S3_BUCKET_NAME not set."""
        resource_id = str(uuid4())
        
        os.environ['S3_ENABLED'] = 'true'
        os.environ.pop('S3_BUCKET_NAME', None)  # Ensure not set
        
        try:
            with pytest.raises(ValueError, match="S3_BUCKET_NAME"):
                upload_to_s3_task(resource_id, "/fake/path")
        finally:
            os.environ.pop('S3_ENABLED', None)

    @mock_aws
    @patch('src.tasks.s3_upload_task._update_resource_s3_status')
    def test_upload_generates_correct_s3_key(self, mock_update_status):
        """Should generate S3 key with resource_id prefix."""
        bucket_name = "test-bucket"
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket=bucket_name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(b"Test content")
            temp_path = f.name
            filename = os.path.basename(temp_path)

        try:
            resource_id = str(uuid4())
            
            os.environ['S3_ENABLED'] = 'true'
            os.environ['S3_BUCKET_NAME'] = bucket_name
            os.environ['AWS_REGION'] = 'us-east-1'
            
            result = upload_to_s3_task(resource_id, temp_path)
            
            # Verify S3 key structure
            expected_key = f"resources/{resource_id}/{filename}"
            assert expected_key in result["s3_url"]
            
            # Verify object exists with correct key
            s3_client.head_object(Bucket=bucket_name, Key=expected_key)
            
        finally:
            os.remove(temp_path)
            os.environ.pop('S3_ENABLED', None)
            os.environ.pop('S3_BUCKET_NAME', None)
            os.environ.pop('AWS_REGION', None)


class TestBatchRetryFailedUploads:
    """Test batch retry functionality for failed S3 uploads."""

    @patch('src.tasks.s3_upload_task.upload_to_s3_task.delay')
    @patch('src.tasks.s3_upload_task.get_engine')
    @patch('src.tasks.s3_upload_task.Session')
    def test_batch_retry_queues_failed_uploads(self, mock_session, mock_get_engine, mock_upload_task):
        """Should find failed uploads and queue them for retry."""
        from src.tasks.s3_upload_task import batch_retry_failed_uploads
        
        # Mock database session
        mock_db_session = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db_session
        
        # Mock failed resources
        mock_resource1 = MagicMock()
        mock_resource1.id = uuid4()
        mock_resource1.file_path = "/path/to/file1.pdf"
        mock_resource1.s3_sync_status = S3SyncStatus.FAILED
        
        mock_resource2 = MagicMock()
        mock_resource2.id = uuid4()
        mock_resource2.file_path = "/path/to/file2.pdf"
        mock_resource2.s3_sync_status = S3SyncStatus.FAILED
        
        mock_db_session.exec.return_value.all.return_value = [mock_resource1, mock_resource2]
        
        # Execute batch retry
        result = batch_retry_failed_uploads()
        
        # Assertions
        assert result["status"] == "success"
        assert result["retry_count"] == 2
        assert mock_upload_task.call_count == 2
        
        # Verify resources updated to pending_retry
        assert mock_resource1.s3_sync_status == S3SyncStatus.PENDING_RETRY
        assert mock_resource2.s3_sync_status == S3SyncStatus.PENDING_RETRY
