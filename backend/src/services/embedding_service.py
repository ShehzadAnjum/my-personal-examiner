"""
Embedding Service for Semantic Search and Content Alignment

Provides embedding generation, storage, and retrieval for syllabus topics.
Enables token-free semantic search and textbook-to-syllabus alignment.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Requirements:
- Principle V: Multi-tenant isolation via subject_id scope
- Principle XVI: 98% token savings via cached embeddings

Performance Requirements:
- FR-004: 60 topics embedded in 60 seconds
- FR-005: Semantic search <500ms
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.ai_integration.embedding_client import (
    AllProvidersExhaustedError,
    EmbeddingClient,
    EmbeddingError,
)
from src.models.embedding_job import (
    EmbeddingJob,
    EmbeddingJobStatus,
    EmbeddingJobType,
)
from src.models.syllabus_point import SyllabusPoint

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for managing syllabus topic embeddings.

    Provides:
    - Embedding generation with progress tracking
    - Batch embedding for subjects
    - Semantic search via cosine similarity
    - Content-to-syllabus alignment
    - Re-embedding on content updates

    Multi-tenant isolation:
    - All queries scoped to subject_id
    - No cross-subject embedding comparisons

    Example:
        >>> service = EmbeddingService(db_session)
        >>> job = await service.generate_embeddings_for_subject(subject_id)
        >>> results = await service.semantic_search("market failure", subject_id)
    """

    def __init__(self, db: Session, embedding_client: Optional[EmbeddingClient] = None):
        """
        Initialize embedding service.

        Args:
            db: SQLAlchemy database session
            embedding_client: Optional embedding client (creates default if not provided)
        """
        self.db = db
        self._client = embedding_client

    @property
    def client(self) -> EmbeddingClient:
        """Lazy-initialize embedding client."""
        if self._client is None:
            self._client = EmbeddingClient()
        return self._client

    # =========================================================================
    # T016: Generate embedding for single topic
    # =========================================================================

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            768-dimension embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            return self.client.get_embedding(text)
        except AllProvidersExhaustedError as e:
            logger.error(f"All embedding providers exhausted: {e}")
            raise
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")

    # =========================================================================
    # T017: Batch embedding generation
    # =========================================================================

    async def generate_embeddings_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Uses batch API when possible for efficiency.

        Args:
            texts: List of texts to embed

        Returns:
            List of 768-dimension embedding vectors
        """
        if not texts:
            return []
        return self.client.get_embeddings_batch(texts)

    # =========================================================================
    # T018: Generate embeddings for all topics in a subject
    # =========================================================================

    async def generate_embeddings_for_subject(
        self,
        subject_id: UUID,
        force_regenerate: bool = False,
        created_by: Optional[UUID] = None,
    ) -> EmbeddingJob:
        """
        Generate embeddings for all syllabus topics in a subject.

        Creates an EmbeddingJob to track progress. Non-blocking - returns
        immediately with job for status tracking.

        Args:
            subject_id: Subject to generate embeddings for
            force_regenerate: If True, regenerate even if embeddings exist
            created_by: User who triggered the job

        Returns:
            EmbeddingJob for progress tracking

        Raises:
            ValueError: If no topics found for subject
        """
        # Get topics for subject
        stmt = select(SyllabusPoint).where(SyllabusPoint.subject_id == subject_id)
        if not force_regenerate:
            stmt = stmt.where(SyllabusPoint.embedding.is_(None))

        topics = list(self.db.exec(stmt).scalars().all())

        if not topics:
            # Check if subject has any topics at all
            all_topics = self.db.exec(
                select(SyllabusPoint).where(SyllabusPoint.subject_id == subject_id)
            ).scalars().all()
            if not all_topics:
                raise ValueError(f"No topics found for subject {subject_id}")
            # All topics already have embeddings
            logger.info(f"All {len(all_topics)} topics already have embeddings")
            job = EmbeddingJob(
                subject_id=subject_id,
                job_type=EmbeddingJobType.SYLLABUS,
                total_items=0,
                completed_items=0,
                status=EmbeddingJobStatus.COMPLETED,
                created_by=created_by,
            )
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job

        # Create job
        job = EmbeddingJob(
            subject_id=subject_id,
            job_type=EmbeddingJobType.SYLLABUS,
            total_items=len(topics),
            created_by=created_by,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        logger.info(
            f"Created embedding job {job.id} for {len(topics)} topics in subject {subject_id}"
        )

        # Process embeddings (in-process for now, could be moved to background task)
        await self._process_embedding_job(job, topics)

        return job

    # =========================================================================
    # T19: EmbeddingJob progress tracking
    # =========================================================================

    async def _process_embedding_job(
        self,
        job: EmbeddingJob,
        topics: List[SyllabusPoint],
    ) -> None:
        """
        Process embedding generation for a job.

        Updates job status and topic embeddings in database.

        Args:
            job: EmbeddingJob to track progress
            topics: Topics to embed
        """
        job.start()
        self.db.commit()

        # Prepare texts for batch embedding
        texts = [topic.get_embedding_text() for topic in topics]

        try:
            # Try batch embedding first
            embeddings = await self.generate_embeddings_batch(texts)

            # Update topics with embeddings
            for topic, embedding in zip(topics, embeddings):
                topic.embedding = embedding
                topic.embedding_model = self.client.last_model_used
                topic.embedded_at = datetime.utcnow()
                job.record_success()

            self.db.commit()
            job.complete()
            self.db.commit()

            logger.info(
                f"Completed embedding job {job.id}: "
                f"{job.completed_items}/{job.total_items} successful"
            )

        except AllProvidersExhaustedError as e:
            # All providers failed - mark job as failed
            job.fail(str(e))
            self.db.commit()
            logger.error(f"Embedding job {job.id} failed: {e}")

        except Exception as e:
            # Partial failure - try individual topics
            logger.warning(f"Batch embedding failed, trying individual: {e}")
            await self._process_topics_individually(job, topics)

    async def _process_topics_individually(
        self,
        job: EmbeddingJob,
        topics: List[SyllabusPoint],
    ) -> None:
        """
        Process topics one by one (fallback when batch fails).

        Args:
            job: EmbeddingJob to track progress
            topics: Topics to embed
        """
        for topic in topics:
            try:
                text = topic.get_embedding_text()
                embedding = await self.generate_embedding(text)

                topic.embedding = embedding
                topic.embedding_model = self.client.last_model_used
                topic.embedded_at = datetime.utcnow()
                job.record_success()

            except Exception as e:
                logger.warning(f"Failed to embed topic {topic.code}: {e}")
                job.record_failure(topic.id)

            # Commit after each topic for progress tracking
            self.db.commit()

        job.complete()
        self.db.commit()

        logger.info(
            f"Completed embedding job {job.id}: "
            f"{job.completed_items} succeeded, {job.failed_items} failed"
        )

    def get_job_status(self, job_id: UUID) -> Optional[EmbeddingJob]:
        """
        Get embedding job status.

        Args:
            job_id: Job ID to check

        Returns:
            EmbeddingJob if found, None otherwise
        """
        return self.db.get(EmbeddingJob, job_id)

    # =========================================================================
    # T029-T030: Semantic search (US2)
    # =========================================================================

    async def semantic_search(
        self,
        query: str,
        subject_id: UUID,
        limit: int = 5,
        min_similarity: float = 0.5,
    ) -> Tuple[List[dict], int]:
        """
        Search for topics using semantic similarity.

        Args:
            query: Natural language search query
            subject_id: Subject to search within (multi-tenant isolation)
            limit: Maximum results to return
            min_similarity: Minimum cosine similarity threshold (0-1)

        Returns:
            Tuple of (results list, search time in ms)
            Each result contains: topic_id, code, title, description, similarity

        Performance: Target <500ms (FR-005)
        """
        import time

        start_time = time.time()

        # Generate query embedding
        query_embedding = self.client.get_query_embedding(query)

        # Build cosine similarity query using pgvector
        # Embed vector literal directly in SQL (safe - generated by embedding model)
        query_vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Note: We embed the vector literal directly because SQLAlchemy's :param::type
        # syntax conflicts with PostgreSQL's :: cast operator
        sql = text(f"""
            SELECT
                id,
                code,
                description,
                section_title,
                1 - (embedding::vector <=> '{query_vector_str}'::vector) as similarity
            FROM syllabus_points
            WHERE embedding IS NOT NULL
              AND subject_id = :subject_id
              AND 1 - (embedding::vector <=> '{query_vector_str}'::vector) >= :min_similarity
            ORDER BY embedding::vector <=> '{query_vector_str}'::vector
            LIMIT :limit
        """)

        result = self.db.execute(
            sql,
            {
                "subject_id": str(subject_id),
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )

        rows = result.fetchall()

        results = [
            {
                "topic_id": str(row.id),
                "code": row.code,
                "title": row.description[:100] if row.description else "",
                "description": row.description,
                "section_title": row.section_title,
                "similarity": round(float(row.similarity), 4),
            }
            for row in rows
        ]

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Semantic search for '{query[:50]}...' found {len(results)} results "
            f"in {elapsed_ms}ms"
        )

        return results, elapsed_ms

    # =========================================================================
    # T37-T38: Content alignment (US3)
    # =========================================================================

    async def align_content(
        self,
        content: str,
        subject_id: UUID,
        limit: int = 5,
        min_similarity: float = 0.6,
    ) -> dict:
        """
        Align external content to syllabus topics.

        Generates embedding for content and finds matching topics.
        Returns confidence level based on similarity scores.

        Args:
            content: Content to align (e.g., textbook chapter)
            subject_id: Subject to align against
            limit: Maximum matching topics
            min_similarity: Minimum similarity threshold

        Returns:
            Dict with content_preview, alignments, processing_time_ms, confidence
        """
        import time

        start_time = time.time()

        # Generate content embedding (uses retrieval_document task type)
        content_embedding = self.client.get_embedding(content)

        # Search for matching topics
        # Embed vector literal directly in SQL (safe - generated by embedding model)
        query_vector_str = "[" + ",".join(str(x) for x in content_embedding) + "]"

        sql = text(f"""
            SELECT
                id,
                code,
                description,
                1 - (embedding::vector <=> '{query_vector_str}'::vector) as similarity
            FROM syllabus_points
            WHERE embedding IS NOT NULL
              AND subject_id = :subject_id
              AND 1 - (embedding::vector <=> '{query_vector_str}'::vector) >= :min_similarity
            ORDER BY embedding::vector <=> '{query_vector_str}'::vector
            LIMIT :limit
        """)

        result = self.db.execute(
            sql,
            {
                "subject_id": str(subject_id),
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )

        rows = result.fetchall()

        alignments = [
            {
                "topic_id": str(row.id),
                "code": row.code,
                "title": row.description[:100] if row.description else "",
                "similarity": round(float(row.similarity), 4),
            }
            for row in rows
        ]

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Calculate confidence based on top similarity score
        if alignments:
            top_similarity = alignments[0]["similarity"]
            if top_similarity >= 0.85:
                confidence = "high"
            elif top_similarity >= 0.7:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            confidence = "low"

        logger.info(
            f"Content alignment found {len(alignments)} matches "
            f"(confidence: {confidence}) in {elapsed_ms}ms"
        )

        return {
            "content_preview": content[:200],
            "alignments": alignments,
            "processing_time_ms": elapsed_ms,
            "confidence": confidence,
        }

    # =========================================================================
    # T42-T43: Re-embed on content update (US4)
    # =========================================================================

    async def regenerate_embedding(self, topic_id: UUID) -> bool:
        """
        Regenerate embedding for a single topic.

        Args:
            topic_id: Topic to regenerate

        Returns:
            True if successful, False otherwise
        """
        topic = self.db.get(SyllabusPoint, topic_id)
        if not topic:
            logger.warning(f"Topic {topic_id} not found for re-embedding")
            return False

        try:
            text = topic.get_embedding_text()
            embedding = await self.generate_embedding(text)

            topic.embedding = embedding
            topic.embedding_model = self.client.last_model_used
            topic.embedded_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"Regenerated embedding for topic {topic.code}")
            return True

        except Exception as e:
            logger.error(f"Failed to regenerate embedding for topic {topic_id}: {e}")
            return False

    async def bulk_regenerate_embeddings(
        self,
        topic_ids: List[UUID],
        subject_id: UUID,
        created_by: Optional[UUID] = None,
    ) -> EmbeddingJob:
        """
        Regenerate embeddings for multiple topics.

        Args:
            topic_ids: Topics to regenerate
            subject_id: Subject for job tracking
            created_by: User who triggered regeneration

        Returns:
            EmbeddingJob for progress tracking
        """
        topics = []
        for topic_id in topic_ids:
            topic = self.db.get(SyllabusPoint, topic_id)
            if topic:
                topics.append(topic)

        if not topics:
            raise ValueError("No valid topics found for regeneration")

        # Create job
        job = EmbeddingJob(
            subject_id=subject_id,
            job_type=EmbeddingJobType.BULK_REGENERATE,
            total_items=len(topics),
            created_by=created_by,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # Process
        await self._process_embedding_job(job, topics)

        return job

    async def retry_failed_embeddings(self, job_id: UUID) -> Optional[EmbeddingJob]:
        """
        Retry failed embeddings from a previous job.

        Args:
            job_id: Job with failed items

        Returns:
            New EmbeddingJob for retry, or None if no failed items
        """
        original_job = self.db.get(EmbeddingJob, job_id)
        if not original_job:
            logger.warning(f"Job {job_id} not found")
            return None

        if not original_job.failed_item_ids:
            logger.info(f"Job {job_id} has no failed items to retry")
            return None

        return await self.bulk_regenerate_embeddings(
            topic_ids=original_job.failed_item_ids,
            subject_id=original_job.subject_id,
            created_by=original_job.created_by,
        )

    # =========================================================================
    # Utility methods
    # =========================================================================

    def count_embedded_topics(self, subject_id: UUID) -> int:
        """Count topics with embeddings in a subject."""
        result = self.db.execute(
            text("""
                SELECT COUNT(*) FROM syllabus_points
                WHERE subject_id = :subject_id AND embedding IS NOT NULL
            """),
            {"subject_id": str(subject_id)},
        )
        return result.scalar() or 0

    def count_total_topics(self, subject_id: UUID) -> int:
        """Count total topics in a subject."""
        result = self.db.execute(
            text("""
                SELECT COUNT(*) FROM syllabus_points
                WHERE subject_id = :subject_id
            """),
            {"subject_id": str(subject_id)},
        )
        return result.scalar() or 0
