"""
Search Routes

API endpoints for semantic search and content alignment.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Compliance:
- Principle V: Multi-tenant isolation via subject_id scope
- Principle XVI: Token conservation via cached embeddings

Endpoints:
- POST /api/search/semantic - Semantic search across syllabus topics
- POST /api/embeddings/align - Align content to syllabus topics
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.models.subject import Subject
from src.schemas.embedding_schemas import (
    ConfidenceLevel,
    ContentAlignmentRequest,
    ContentAlignmentResponse,
    AlignmentResult,
    EmbeddingErrorResponse,
    SearchResult,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


# =============================================================================
# T033: POST /search/semantic
# =============================================================================


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    responses={
        400: {"model": EmbeddingErrorResponse, "description": "Invalid search query"},
    },
)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Semantic search across syllabus topics.

    Uses vector similarity to find topics matching a natural language query.
    All searches are scoped to a single subject for multi-tenant isolation.

    **Performance**: Target <500ms (FR-005).

    Args:
        request: Search query and filters

    Returns:
        SemanticSearchResponse with ranked results

    Example:
        POST /api/search/semantic
        {
            "query": "market failure externalities",
            "subject_id": "123e4567-e89b-12d3-a456-426614174000",
            "limit": 5,
            "min_similarity": 0.5
        }
    """
    # Verify subject exists
    subject = db.get(Subject, request.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID '{request.subject_id}' not found",
        )

    service = EmbeddingService(db)

    # Check if subject has embeddings
    embedded_count = service.count_embedded_topics(request.subject_id)
    if embedded_count == 0:
        logger.warning(f"No embeddings found for subject {request.subject_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No embedded topics found. Generate embeddings first.",
        )

    # Perform search
    try:
        results, search_time_ms = await service.semantic_search(
            query=request.query,
            subject_id=request.subject_id,
            limit=request.limit,
            min_similarity=request.min_similarity,
        )

        logger.info(
            f"Semantic search for '{request.query[:30]}...' returned "
            f"{len(results)} results in {search_time_ms}ms"
        )

        # Convert to response format
        search_results = [
            SearchResult(
                topic_id=r["topic_id"],
                code=r["code"],
                title=r["title"],
                description=r.get("description"),
                section_title=r.get("section_title"),
                similarity=r["similarity"],
            )
            for r in results
        ]

        return SemanticSearchResponse(
            query=request.query,
            results=search_results,
            search_time_ms=search_time_ms,
            total_embedded_topics=embedded_count,
        )

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


# =============================================================================
# T040: POST /embeddings/align (Content Alignment)
# =============================================================================


# Create a separate router for alignment under /api/embeddings
align_router = APIRouter(prefix="/api/embeddings", tags=["alignment"])


@align_router.post(
    "/align",
    response_model=ContentAlignmentResponse,
    responses={
        400: {"model": EmbeddingErrorResponse, "description": "Invalid content"},
    },
)
async def align_content(
    request: ContentAlignmentRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Align external content to syllabus topics.

    Generates embedding for the content and finds matching syllabus topics
    using semantic similarity. Returns confidence level based on top match.

    **Use case**: Textbook-to-syllabus alignment without LLM tokens.

    Args:
        request: Content and alignment settings

    Returns:
        ContentAlignmentResponse with matching topics and confidence

    Example:
        POST /api/embeddings/align
        {
            "content": "Price Elasticity of Demand measures the responsiveness...",
            "subject_id": "123e4567-e89b-12d3-a456-426614174000",
            "limit": 5,
            "min_similarity": 0.6
        }
    """
    # Verify subject exists
    subject = db.get(Subject, request.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID '{request.subject_id}' not found",
        )

    service = EmbeddingService(db)

    # Check if subject has embeddings
    embedded_count = service.count_embedded_topics(request.subject_id)
    if embedded_count == 0:
        logger.warning(f"No embeddings found for subject {request.subject_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No embedded topics found. Generate embeddings first.",
        )

    # Perform alignment
    try:
        result = await service.align_content(
            content=request.content,
            subject_id=request.subject_id,
            limit=request.limit,
            min_similarity=request.min_similarity,
        )

        logger.info(
            f"Content alignment found {len(result['alignments'])} matches "
            f"(confidence: {result['confidence']}) in {result['processing_time_ms']}ms"
        )

        # Convert to response format
        alignments = [
            AlignmentResult(
                topic_id=a["topic_id"],
                code=a["code"],
                title=a["title"],
                similarity=a["similarity"],
            )
            for a in result["alignments"]
        ]

        return ContentAlignmentResponse(
            content_preview=result["content_preview"],
            alignments=alignments,
            processing_time_ms=result["processing_time_ms"],
            confidence=ConfidenceLevel(result["confidence"]),
        )

    except Exception as e:
        logger.error(f"Content alignment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alignment failed: {str(e)}",
        )
