"""
Embedding Client for Semantic Search and Content Alignment

Provides embeddings using Gemini text-embedding-004 with multi-key rotation
and OpenAI text-embedding-3-small as fallback.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Requirements:
- Principle V: Embeddings scoped to subject for multi-tenant isolation
- Principle XVI: Token conservation via cached embeddings

Research References:
- specs/010-embedding-integration/research.md
"""

import logging
import os
from typing import List, Optional

import google.generativeai as genai
from openai import OpenAI

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions (T012)
# ============================================================================


class EmbeddingError(Exception):
    """Base exception for embedding operations."""

    def __init__(self, message: str, provider: Optional[str] = None):
        self.message = message
        self.provider = provider
        super().__init__(message)


class RateLimitError(EmbeddingError):
    """Rate limit exceeded - try next key or provider."""

    def __init__(self, message: str, provider: str, key_index: int):
        super().__init__(message, provider)
        self.key_index = key_index


class ModelUnavailableError(EmbeddingError):
    """Model temporarily unavailable - retry later."""
    pass


class AllProvidersExhaustedError(EmbeddingError):
    """All embedding providers exhausted - no fallback available."""

    def __init__(self, gemini_keys_tried: int, openai_tried: bool):
        message = f"All embedding providers exhausted: tried {gemini_keys_tried} Gemini keys"
        if openai_tried:
            message += " and OpenAI fallback"
        super().__init__(message)
        self.gemini_keys_tried = gemini_keys_tried
        self.openai_tried = openai_tried


# ============================================================================
# Embedding Client (T010, T011)
# ============================================================================


class EmbeddingClient:
    """
    Client for generating text embeddings with multi-key rotation and fallback.

    Uses Gemini text-embedding-004 as primary (free tier, 768 dimensions).
    Falls back to OpenAI text-embedding-3-small when all Gemini keys exhausted.

    Supports:
    - Multiple Gemini API keys (GEMINI_API_KEY_1 through _5)
    - Automatic key rotation on rate limit
    - OpenAI fallback with 768-dimension output (matching Gemini)
    - Batch embedding for efficiency

    Example:
        >>> client = EmbeddingClient()
        >>> embedding = client.get_embedding("Market failure and externalities")
        >>> len(embedding)  # 768

    Constitutional Compliance:
        - Principle V: Embeddings scoped to subject/syllabus
        - Principle XVI: One-time generation, cached for free queries
    """

    # Embedding dimensions (must match for all providers)
    EMBEDDING_DIMENSIONS = 768

    # Model identifiers for tracking
    GEMINI_MODEL = "gemini/text-embedding-004"
    OPENAI_MODEL = "openai/text-embedding-3-small"

    def __init__(
        self,
        gemini_keys: Optional[List[str]] = None,
        openai_key: Optional[str] = None,
    ):
        """
        Initialize embedding client with available API keys.

        Args:
            gemini_keys: List of Gemini API keys. Defaults to GEMINI_API_KEY_1-5 env vars.
            openai_key: OpenAI API key for fallback. Defaults to OPENAI_API_KEY env var.
        """
        # Load Gemini keys
        self.gemini_keys: List[str] = []
        if gemini_keys:
            self.gemini_keys = gemini_keys
        else:
            # Load from environment: GEMINI_API_KEY_1 through GEMINI_API_KEY_5
            for i in range(1, 6):
                key = os.getenv(f"GEMINI_API_KEY_{i}")
                if key:
                    self.gemini_keys.append(key)
            # Also check legacy GEMINI_API_KEY
            legacy_key = os.getenv("GEMINI_API_KEY")
            if legacy_key and legacy_key not in self.gemini_keys:
                self.gemini_keys.insert(0, legacy_key)

        # Load OpenAI key for fallback
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self._openai_client: Optional[OpenAI] = None

        # Current Gemini key index
        self.current_gemini_key_index = 0

        # Track which model was used for last embedding
        self.last_model_used: Optional[str] = None

        # Log initialization
        total_keys = len(self.gemini_keys) + (1 if self.openai_key else 0)
        if total_keys == 0:
            raise EmbeddingError(
                "No embedding API keys configured. "
                "Set GEMINI_API_KEY_1 or OPENAI_API_KEY environment variables."
            )
        logger.info(
            f"EmbeddingClient initialized with {len(self.gemini_keys)} Gemini key(s) "
            f"and {'1' if self.openai_key else '0'} OpenAI key(s)"
        )

    @property
    def openai_client(self) -> OpenAI:
        """Lazy-initialize OpenAI client."""
        if self._openai_client is None:
            if not self.openai_key:
                raise EmbeddingError("OpenAI API key not configured for fallback")
            self._openai_client = OpenAI(api_key=self.openai_key)
        return self._openai_client

    def _configure_gemini(self, key_index: int) -> None:
        """Configure Gemini with specified key."""
        if key_index >= len(self.gemini_keys):
            raise IndexError(f"Gemini key index {key_index} out of range")
        genai.configure(api_key=self.gemini_keys[key_index])
        self.current_gemini_key_index = key_index

    def _embed_with_gemini(
        self,
        text: str,
        task_type: str = "retrieval_document",
    ) -> List[float]:
        """
        Generate embedding using Gemini text-embedding-004.

        Args:
            text: Text to embed
            task_type: Task type for embedding optimization
                - "retrieval_document": For content being searched
                - "retrieval_query": For search queries

        Returns:
            768-dimension embedding vector

        Raises:
            RateLimitError: If current key is rate limited
            EmbeddingError: For other Gemini errors
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type=task_type,
            )
            embedding = result["embedding"]
            self.last_model_used = self.GEMINI_MODEL
            return embedding
        except Exception as e:
            error_str = str(e).lower()
            if "429" in str(e) or "quota" in error_str or "rate" in error_str:
                raise RateLimitError(
                    f"Gemini rate limit: {e}",
                    provider="gemini",
                    key_index=self.current_gemini_key_index,
                )
            raise EmbeddingError(f"Gemini embedding error: {e}", provider="gemini")

    def _embed_with_openai(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI text-embedding-3-small.

        Configured to output 768 dimensions for compatibility with Gemini.

        Args:
            text: Text to embed

        Returns:
            768-dimension embedding vector

        Raises:
            EmbeddingError: For OpenAI errors
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=self.EMBEDDING_DIMENSIONS,  # Match Gemini output
            )
            embedding = response.data[0].embedding
            self.last_model_used = self.OPENAI_MODEL
            return embedding
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding error: {e}", provider="openai")

    def get_embedding(
        self,
        text: str,
        task_type: str = "retrieval_document",
    ) -> List[float]:
        """
        Generate embedding with automatic key rotation and fallback.

        Tries each Gemini key in order, then falls back to OpenAI.
        Logs which provider/key was used for each embedding.

        Args:
            text: Text to embed (max ~8000 characters for Gemini)
            task_type: Task type for optimization
                - "retrieval_document": For syllabus topics (default)
                - "retrieval_query": For search queries

        Returns:
            768-dimension embedding vector

        Raises:
            AllProvidersExhaustedError: If all providers fail
        """
        # Truncate very long text (Gemini limit is ~2048 tokens)
        if len(text) > 8000:
            logger.warning(
                f"Text truncated from {len(text)} to 8000 chars for embedding"
            )
            text = text[:8000]

        # Try each Gemini key
        for i, key in enumerate(self.gemini_keys):
            try:
                self._configure_gemini(i)
                embedding = self._embed_with_gemini(text, task_type)
                logger.debug(f"Embedding generated with Gemini key {i + 1}")
                return embedding
            except RateLimitError:
                logger.warning(f"Gemini key {i + 1}/{len(self.gemini_keys)} rate limited")
                continue
            except EmbeddingError as e:
                logger.warning(f"Gemini key {i + 1} error: {e}")
                continue

        # Fall back to OpenAI
        if self.openai_key:
            try:
                logger.info("Falling back to OpenAI for embedding")
                embedding = self._embed_with_openai(text)
                return embedding
            except EmbeddingError as e:
                logger.error(f"OpenAI fallback failed: {e}")

        # All providers exhausted
        raise AllProvidersExhaustedError(
            gemini_keys_tried=len(self.gemini_keys),
            openai_tried=bool(self.openai_key),
        )

    def get_embeddings_batch(
        self,
        texts: List[str],
        task_type: str = "retrieval_document",
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Uses Gemini's native batch support when possible.
        Falls back to sequential processing if batch fails.

        Args:
            texts: List of texts to embed (max 100 for Gemini batch)
            task_type: Task type for optimization

        Returns:
            List of 768-dimension embedding vectors

        Raises:
            AllProvidersExhaustedError: If all providers fail for any text
        """
        if not texts:
            return []

        # Try Gemini batch embedding first (up to 100 texts)
        if len(self.gemini_keys) > 0 and len(texts) <= 100:
            for i, key in enumerate(self.gemini_keys):
                try:
                    self._configure_gemini(i)
                    result = genai.embed_content(
                        model="models/text-embedding-004",
                        content=texts,
                        task_type=task_type,
                    )
                    # Batch returns list of embeddings
                    embeddings = result["embedding"]
                    self.last_model_used = self.GEMINI_MODEL
                    logger.info(
                        f"Batch embedding for {len(texts)} texts with Gemini key {i + 1}"
                    )
                    return embeddings
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in str(e) or "quota" in error_str or "rate" in error_str:
                        logger.warning(f"Gemini key {i + 1} rate limited for batch")
                        continue
                    logger.warning(f"Gemini batch error: {e}, falling back to sequential")
                    break

        # Fall back to sequential processing
        logger.info(f"Processing {len(texts)} texts sequentially")
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text, task_type)
            embeddings.append(embedding)
        return embeddings

    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding optimized for search queries.

        Uses "retrieval_query" task type for better search performance.

        Args:
            query: Search query text

        Returns:
            768-dimension embedding vector
        """
        return self.get_embedding(query, task_type="retrieval_query")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<EmbeddingClient(gemini_keys={len(self.gemini_keys)}, "
            f"openai={'yes' if self.openai_key else 'no'})>"
        )
