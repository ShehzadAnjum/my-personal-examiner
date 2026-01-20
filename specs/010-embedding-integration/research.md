# Research: Embedding Integration

**Feature**: 010-embedding-integration
**Date**: 2026-01-21
**Status**: Complete

---

## Research Topics

### 1. pgvector Extension

**Question**: How to install, configure, and optimize pgvector for PostgreSQL?

**Findings**:

#### Installation
```sql
-- Enable extension (requires superuser on Neon)
CREATE EXTENSION IF NOT EXISTS vector;
```

For Neon Serverless PostgreSQL:
- pgvector is pre-installed, just needs enabling
- No additional setup required
- Supports up to 2,000 dimensions per vector

#### Vector Column Definition
```sql
-- Add vector column (768 dimensions for Gemini)
ALTER TABLE syllabus_point ADD COLUMN embedding vector(768);
```

#### Indexing Strategies

| Index Type | Best For | Build Time | Query Speed |
|------------|----------|------------|-------------|
| IVFFlat | Large datasets (>100K) | Fast | Fast (approximate) |
| HNSW | Smaller datasets, high accuracy | Slow | Fastest |
| None | <1,000 vectors | N/A | Direct scan OK |

**Recommendation**: For our scale (~1,000 topics), no index needed initially. Add HNSW if query times exceed 500ms.

```sql
-- Future optimization (only if needed)
CREATE INDEX ON syllabus_point USING hnsw (embedding vector_cosine_ops);
```

#### SQLModel/SQLAlchemy Integration
```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

class SyllabusPoint(SQLModel, table=True):
    embedding: Optional[List[float]] = Field(
        sa_column=Column(Vector(768), nullable=True)
    )
```

---

### 2. Gemini Embedding API

**Question**: How to use text-embedding-004 model, rate limits, dimensions?

**Findings**:

#### Model Specifications

| Property | Value |
|----------|-------|
| Model ID | `text-embedding-004` |
| Dimensions | 768 (default), configurable 1-768 |
| Max Input | 2,048 tokens (~8,000 characters) |
| Output | Normalized L2 vectors |

#### API Usage
```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

result = genai.embed_content(
    model="models/text-embedding-004",
    content="Scarcity and choice in economics",
    task_type="retrieval_document"  # or "retrieval_query" for searches
)

embedding = result['embedding']  # List[float] of 768 dimensions
```

#### Task Types

| Task Type | Use Case |
|-----------|----------|
| `retrieval_document` | Embedding content to be searched |
| `retrieval_query` | Embedding search queries |
| `semantic_similarity` | Comparing two texts |
| `classification` | Categorization tasks |

**Recommendation**: Use `retrieval_document` for topics, `retrieval_query` for searches.

#### Rate Limits (Free Tier)

| Limit | Value |
|-------|-------|
| Requests per minute | 1,500 |
| Tokens per minute | 1,000,000 |
| Requests per day | 1,500 |

**Calculation**: 60 topics × 1 request = 60 requests. Well within limits.

#### Batch Embedding
```python
# Batch up to 100 texts per request
result = genai.embed_content(
    model="models/text-embedding-004",
    content=["Topic 1 text", "Topic 2 text", ...],
    task_type="retrieval_document"
)
embeddings = result['embedding']  # List of List[float]
```

---

### 3. Embedding Fallback Pattern

**Question**: How to implement multi-key rotation with OpenAI fallback?

**Findings**:

#### Key Rotation Strategy

```python
import os
from typing import List, Optional

class EmbeddingClient:
    def __init__(self):
        # Load all Gemini keys
        self.gemini_keys = []
        for i in range(1, 6):  # GEMINI_API_KEY_1 through _5
            key = os.environ.get(f"GEMINI_API_KEY_{i}")
            if key:
                self.gemini_keys.append(key)

        # OpenAI fallback
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.current_key_index = 0

    def get_embedding(self, text: str) -> List[float]:
        # Try each Gemini key
        for i, key in enumerate(self.gemini_keys):
            try:
                return self._embed_with_gemini(text, key)
            except RateLimitError:
                continue
            except Exception as e:
                log.warning(f"Gemini key {i+1} failed: {e}")
                continue

        # Fall back to OpenAI
        if self.openai_key:
            return self._embed_with_openai(text)

        raise EmbeddingError("All embedding providers exhausted")
```

#### OpenAI Fallback Configuration

| Property | Gemini | OpenAI |
|----------|--------|--------|
| Model | text-embedding-004 | text-embedding-3-small |
| Dimensions | 768 | 1536 (default), 768 (configurable) |
| Cost | Free tier | $0.02/1M tokens |

**Important**: Configure OpenAI to output 768 dimensions for compatibility:
```python
response = openai.embeddings.create(
    model="text-embedding-3-small",
    input=text,
    dimensions=768  # Match Gemini output
)
```

#### Error Handling

```python
class EmbeddingError(Exception):
    """Base embedding error"""
    pass

class RateLimitError(EmbeddingError):
    """Rate limit exceeded - try next key"""
    pass

class ModelUnavailableError(EmbeddingError):
    """Model temporarily unavailable - retry later"""
    pass
```

---

### 4. Vector Similarity Search

**Question**: Cosine vs L2 distance, performance optimization?

**Findings**:

#### Distance Metrics

| Metric | Operator | Best For | Notes |
|--------|----------|----------|-------|
| Cosine | `<=>` | Text similarity | Normalized vectors (Gemini default) |
| L2 (Euclidean) | `<->` | Spatial data | Magnitude matters |
| Inner Product | `<#>` | Classification | Dot product |

**Recommendation**: Use cosine similarity (`<=>`) for semantic search. Gemini outputs normalized vectors, so cosine is ideal.

#### Query Examples

```sql
-- Find top 5 similar topics to a query embedding
SELECT id, code, title,
       1 - (embedding <=> $1) as similarity
FROM syllabus_point
WHERE embedding IS NOT NULL
  AND subject_id = $2
ORDER BY embedding <=> $1
LIMIT 5;
```

#### SQLModel Query
```python
from sqlalchemy import func, select
from pgvector.sqlalchemy import Vector

# Cosine similarity search
query_embedding = [0.1, 0.2, ...]  # 768 floats
stmt = (
    select(SyllabusPoint)
    .where(SyllabusPoint.embedding.isnot(None))
    .where(SyllabusPoint.subject_id == subject_id)
    .order_by(SyllabusPoint.embedding.cosine_distance(query_embedding))
    .limit(5)
)
results = session.exec(stmt).all()
```

#### Similarity Thresholds

| Score | Interpretation |
|-------|----------------|
| >= 0.9 | Very strong match |
| 0.7 - 0.9 | Good match |
| 0.5 - 0.7 | Weak match |
| < 0.5 | No meaningful relationship |

**Recommendation**: Use 0.7 as minimum threshold for "relevant" results.

#### Performance Optimization

1. **Filter before search**: Always include `subject_id` filter to reduce search space
2. **Limit results**: Use `LIMIT` to stop early
3. **Index only if needed**: For <1,000 vectors, full scan is fast enough
4. **Batch queries**: If searching multiple terms, batch them

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector dimensions | 768 | Gemini default, sufficient for educational content |
| Distance metric | Cosine similarity | Best for normalized text embeddings |
| Index type | None (initially) | <1,000 vectors, add HNSW if needed |
| Similarity threshold | 0.7 | Balance between recall and precision |
| Batch size | 100 texts | Gemini batch limit |
| Storage | Inline column | Simplifies queries, per clarification |
| Fallback order | Gemini keys 1-5 → OpenAI | Maximize free tier, per clarification |

---

## Dependencies Verified

- [x] pgvector available on Neon PostgreSQL
- [x] google-generativeai Python package available
- [x] openai Python package available (for fallback)
- [x] SQLModel supports pgvector via SQLAlchemy integration

---

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Gemini Embedding API](https://ai.google.dev/gemini-api/docs/embeddings)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Neon pgvector Docs](https://neon.tech/docs/extensions/pgvector)
