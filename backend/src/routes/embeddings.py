"""
Embedding Routes

API endpoints for embedding generation and management.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Compliance:
- Principle V: Multi-tenant isolation via subject_id scope
- Principle XVI: Token conservation via cached embeddings

Endpoints:
- POST /api/embeddings/generate/{subject_id} - Generate embeddings for a subject
- GET /api/embeddings/status/{job_id} - Check job status
- POST /api/embeddings/retry/{job_id} - Retry failed embeddings
- GET /api/embeddings/stats/{subject_id} - Get embedding statistics
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.models.subject import Subject
from src.schemas.embedding_schemas import (
    EmbeddingErrorResponse,
    EmbeddingJobResponse,
    EmbeddingStatsResponse,
    GenerateEmbeddingsRequest,
)
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


# =============================================================================
# T022: POST /embeddings/generate/{subject_id}
# =============================================================================


@router.post(
    "/generate/{subject_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=EmbeddingJobResponse,
    responses={
        400: {"model": EmbeddingErrorResponse, "description": "No topics found"},
        404: {"model": EmbeddingErrorResponse, "description": "Subject not found"},
    },
)
async def generate_embeddings(
    subject_id: UUID,
    request: GenerateEmbeddingsRequest = GenerateEmbeddingsRequest(),
    db: Session = Depends(get_session),
) -> Any:
    """
    Generate embeddings for all syllabus topics in a subject.

    Creates an embedding job and begins processing. Returns immediately
    with job ID for status tracking.

    **Multi-tenant isolation**: Embeddings are scoped to the subject.

    **Performance**: Target 60 topics in 60 seconds (FR-004).

    Args:
        subject_id: Subject to generate embeddings for
        request: Optional settings (force_regenerate)

    Returns:
        EmbeddingJobResponse with job ID and initial status

    Example:
        POST /api/embeddings/generate/123e4567-e89b-12d3-a456-426614174000
        {"force_regenerate": false}
    """
    # Verify subject exists
    subject = db.get(Subject, subject_id)
    if not subject:
        logger.warning(f"Subject {subject_id} not found for embedding generation")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID '{subject_id}' not found",
        )

    # Create embedding service and generate
    service = EmbeddingService(db)

    try:
        job = await service.generate_embeddings_for_subject(
            subject_id=subject_id,
            force_regenerate=request.force_regenerate,
        )

        logger.info(
            f"Embedding job {job.id} started for subject {subject_id}: "
            f"{job.total_items} topics"
        )

        return EmbeddingJobResponse.from_job(job)

    except ValueError as e:
        logger.warning(f"Embedding generation failed for subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# T023: GET /embeddings/status/{job_id}
# =============================================================================


@router.get(
    "/status/{job_id}",
    response_model=EmbeddingJobResponse,
    responses={
        404: {"model": EmbeddingErrorResponse, "description": "Job not found"},
    },
)
async def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Check embedding generation job status.

    Returns current job progress including completed/failed counts.

    Args:
        job_id: Embedding job ID

    Returns:
        EmbeddingJobResponse with current status

    Example:
        GET /api/embeddings/status/123e4567-e89b-12d3-a456-426614174000
    """
    service = EmbeddingService(db)
    job = service.get_job_status(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding job with ID '{job_id}' not found",
        )

    return EmbeddingJobResponse.from_job(job)


# =============================================================================
# T024: POST /embeddings/retry/{job_id}
# =============================================================================


@router.post(
    "/retry/{job_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=EmbeddingJobResponse,
    responses={
        400: {"model": EmbeddingErrorResponse, "description": "No failed items"},
        404: {"model": EmbeddingErrorResponse, "description": "Job not found"},
    },
)
async def retry_failed_embeddings(
    job_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Retry failed embeddings from a previous job.

    Creates a new job to retry only the failed items from the original job.

    Args:
        job_id: Original job ID with failed items

    Returns:
        EmbeddingJobResponse for the new retry job

    Example:
        POST /api/embeddings/retry/123e4567-e89b-12d3-a456-426614174000
    """
    service = EmbeddingService(db)

    # Check if original job exists
    original_job = service.get_job_status(job_id)
    if not original_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding job with ID '{job_id}' not found",
        )

    # Retry failed items
    retry_job = await service.retry_failed_embeddings(job_id)

    if not retry_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job '{job_id}' has no failed items to retry",
        )

    logger.info(
        f"Retry job {retry_job.id} created for {retry_job.total_items} failed items"
    )

    return EmbeddingJobResponse.from_job(retry_job)


# =============================================================================
# Embedding Statistics Endpoint
# =============================================================================


@router.get(
    "/stats/{subject_id}",
    response_model=EmbeddingStatsResponse,
    responses={
        404: {"model": EmbeddingErrorResponse, "description": "Subject not found"},
    },
)
async def get_embedding_stats(
    subject_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get embedding statistics for a subject.

    Returns coverage metrics for embeddings in the subject.

    Args:
        subject_id: Subject to get stats for

    Returns:
        EmbeddingStatsResponse with coverage metrics

    Example:
        GET /api/embeddings/stats/123e4567-e89b-12d3-a456-426614174000
    """
    # Verify subject exists
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID '{subject_id}' not found",
        )

    service = EmbeddingService(db)

    total_topics = service.count_total_topics(subject_id)
    embedded_topics = service.count_embedded_topics(subject_id)

    coverage_percent = (
        (embedded_topics / total_topics * 100) if total_topics > 0 else 0.0
    )

    return EmbeddingStatsResponse(
        subject_id=subject_id,
        total_topics=total_topics,
        embedded_topics=embedded_topics,
        coverage_percent=round(coverage_percent, 2),
    )
