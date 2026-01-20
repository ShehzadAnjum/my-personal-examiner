# Quickstart: Embedding Integration

**Feature**: 010-embedding-integration
**Date**: 2026-01-21
**Spec**: [spec.md](./spec.md)

---

## Integration Scenarios

### Scenario 1: Post-Extraction Embedding Generation

After syllabus topics are extracted via LLM, automatically generate embeddings.

```python
# In syllabus extraction service (after successful extraction)
from backend.src.services.embedding_service import EmbeddingService

async def extract_syllabus(subject_id: UUID, pdf_content: bytes) -> ExtractResult:
    # ... existing LLM extraction logic ...
    topics = await llm_extract_topics(pdf_content)

    # Save topics to database
    await save_topics(subject_id, topics)

    # Trigger embedding generation (async, non-blocking)
    embedding_service = EmbeddingService(db_session)
    job = await embedding_service.generate_embeddings_async(subject_id)

    return ExtractResult(
        topics=topics,
        embedding_job_id=job.id,
        message="Topics extracted. Embedding generation started."
    )
```

**Key Points**:
- Embedding generation is async (doesn't block extraction completion)
- Returns job ID for status tracking
- Extraction succeeds even if embedding fails

---

### Scenario 2: Semantic Topic Search

Search for topics using natural language queries.

```python
# API endpoint usage
from backend.src.services.embedding_service import EmbeddingService

@router.post("/search/semantic")
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    service = EmbeddingService(db)

    results = await service.semantic_search(
        query=request.query,
        subject_id=request.subject_id,
        limit=request.limit,
        min_similarity=request.min_similarity
    )

    return SemanticSearchResponse(
        query=request.query,
        results=results,
        search_time_ms=elapsed_ms
    )
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "market failure externalities",
    "subject_id": "550e8400-e29b-41d4-a716-446655440000",
    "limit": 5,
    "min_similarity": 0.6
  }'
```

**Example Response**:
```json
{
  "query": "market failure externalities",
  "results": [
    {
      "topic_id": "topic-uuid-1",
      "code": "3.1",
      "title": "Market failure and externalities",
      "description": "Causes of market failure...",
      "similarity": 0.92
    },
    {
      "topic_id": "topic-uuid-2",
      "code": "3.2",
      "title": "Government intervention",
      "description": "Methods to correct market failure...",
      "similarity": 0.78
    }
  ],
  "search_time_ms": 45,
  "total_embedded_topics": 58
}
```

---

### Scenario 3: Textbook Chapter Alignment

Align textbook content to syllabus topics.

```python
# Align textbook chapter to syllabus
from backend.src.services.embedding_service import EmbeddingService

async def align_textbook_chapter(
    chapter_text: str,
    subject_id: UUID,
    db: Session
):
    service = EmbeddingService(db)

    alignment = await service.align_content(
        content=chapter_text,
        subject_id=subject_id,
        limit=5,
        min_similarity=0.6
    )

    return alignment
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/embeddings/align \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Price elasticity of demand measures the responsiveness of quantity demanded to a change in price. When demand is elastic (PED > 1), a price increase leads to a proportionally larger fall in quantity demanded...",
    "subject_id": "550e8400-e29b-41d4-a716-446655440000",
    "content_title": "Chapter 4: Elasticity",
    "limit": 5
  }'
```

**Example Response**:
```json
{
  "content_preview": "Price elasticity of demand measures the responsiveness...",
  "alignments": [
    {
      "topic_id": "topic-uuid-1",
      "code": "2.1",
      "title": "Price elasticity of demand (PED)",
      "similarity": 0.94
    },
    {
      "topic_id": "topic-uuid-2",
      "code": "2.2",
      "title": "Income elasticity of demand (YED)",
      "similarity": 0.71
    }
  ],
  "processing_time_ms": 120,
  "confidence": "high"
}
```

---

### Scenario 4: Re-embed on Topic Update

Automatically regenerate embedding when topic content changes.

```python
# In topic update service
from backend.src.services.embedding_service import EmbeddingService

async def update_topic(
    topic_id: UUID,
    updates: TopicUpdate,
    db: Session
):
    # Update topic in database
    topic = await db.get(SyllabusPoint, topic_id)
    topic.title = updates.title or topic.title
    topic.description = updates.description or topic.description
    await db.commit()

    # Regenerate embedding for this topic
    service = EmbeddingService(db)
    await service.regenerate_embedding(topic_id)

    return topic
```

---

### Scenario 5: Check Embedding Job Status

Monitor embedding generation progress.

```python
# Poll for job completion
import asyncio

async def wait_for_embeddings(job_id: UUID, timeout_seconds: int = 120):
    start = time.time()

    while time.time() - start < timeout_seconds:
        response = await client.get(f"/api/embeddings/status/{job_id}")
        job = response.json()

        if job["status"] == "completed":
            return {"success": True, "completed": job["completed_items"]}

        if job["status"] == "failed":
            return {"success": False, "error": job["error_message"]}

        if job["status"] == "partial":
            # Some failed, trigger retry
            await client.post(f"/api/embeddings/retry/{job_id}")

        await asyncio.sleep(2)

    return {"success": False, "error": "Timeout waiting for embeddings"}
```

---

## Frontend Integration

### React Query Hook for Semantic Search

```typescript
// frontend/lib/hooks/useSemanticSearch.ts
import { useQuery, useMutation } from '@tanstack/react-query';

interface SearchParams {
  query: string;
  subjectId: string;
  limit?: number;
  minSimilarity?: number;
}

interface SearchResult {
  topic_id: string;
  code: string;
  title: string;
  description?: string;
  similarity: number;
}

export function useSemanticSearch() {
  return useMutation({
    mutationFn: async (params: SearchParams): Promise<SearchResult[]> => {
      const response = await fetch('/api/search/semantic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: params.query,
          subject_id: params.subjectId,
          limit: params.limit ?? 5,
          min_similarity: params.minSimilarity ?? 0.5,
        }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      return data.results;
    },
  });
}

// Usage in component
function TopicSearch({ subjectId }: { subjectId: string }) {
  const [query, setQuery] = useState('');
  const search = useSemanticSearch();

  const handleSearch = () => {
    search.mutate({ query, subjectId });
  };

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search topics..."
      />
      <button onClick={handleSearch}>Search</button>

      {search.data?.map((result) => (
        <div key={result.topic_id}>
          <strong>{result.code}</strong>: {result.title}
          <span>({(result.similarity * 100).toFixed(0)}% match)</span>
        </div>
      ))}
    </div>
  );
}
```

### Embedding Job Status Hook

```typescript
// frontend/lib/hooks/useEmbeddingJob.ts
import { useQuery } from '@tanstack/react-query';

interface EmbeddingJob {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'partial';
  total_items: number;
  completed_items: number;
  failed_items: number;
}

export function useEmbeddingJob(jobId: string | null) {
  return useQuery({
    queryKey: ['embedding-job', jobId],
    queryFn: async (): Promise<EmbeddingJob> => {
      const response = await fetch(`/api/embeddings/status/${jobId}`);
      if (!response.ok) throw new Error('Failed to fetch job status');
      return response.json();
    },
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Poll every 2s while in progress
      if (data?.status === 'in_progress' || data?.status === 'pending') {
        return 2000;
      }
      return false;
    },
  });
}

// Usage
function EmbeddingProgress({ jobId }: { jobId: string }) {
  const { data: job, isLoading } = useEmbeddingJob(jobId);

  if (isLoading) return <div>Loading...</div>;
  if (!job) return null;

  const progress = (job.completed_items / job.total_items) * 100;

  return (
    <div>
      <div>Status: {job.status}</div>
      <progress value={progress} max={100} />
      <span>{job.completed_items} / {job.total_items}</span>
    </div>
  );
}
```

---

## Environment Variables

```bash
# Required for embedding generation
GEMINI_API_KEY_1=your-gemini-key-1
GEMINI_API_KEY_2=your-gemini-key-2
GEMINI_API_KEY_3=your-gemini-key-3
# GEMINI_API_KEY_4=optional
# GEMINI_API_KEY_5=optional

# Fallback (optional but recommended)
OPENAI_API_KEY=your-openai-key

# Database (existing)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## Testing Examples

### Unit Test: Embedding Generation

```python
# backend/tests/unit/test_embedding_service.py
import pytest
from unittest.mock import Mock, patch

from backend.src.services.embedding_service import EmbeddingService

@pytest.fixture
def mock_gemini():
    with patch('google.generativeai.embed_content') as mock:
        mock.return_value = {'embedding': [0.1] * 768}
        yield mock

async def test_generate_embedding_success(mock_gemini, db_session):
    service = EmbeddingService(db_session)

    embedding = await service.generate_embedding("Test topic content")

    assert len(embedding) == 768
    mock_gemini.assert_called_once()

async def test_fallback_to_openai(mock_gemini, db_session):
    mock_gemini.side_effect = Exception("Rate limit")

    with patch('openai.embeddings.create') as mock_openai:
        mock_openai.return_value.data = [Mock(embedding=[0.2] * 768)]

        service = EmbeddingService(db_session)
        embedding = await service.generate_embedding("Test content")

        assert len(embedding) == 768
        mock_openai.assert_called_once()
```

### Integration Test: Semantic Search

```python
# backend/tests/integration/test_semantic_search.py
import pytest

async def test_semantic_search_returns_relevant_topics(client, seeded_subject):
    # Seed topics with embeddings
    # ...

    response = await client.post("/api/search/semantic", json={
        "query": "market failure",
        "subject_id": str(seeded_subject.id),
        "limit": 5
    })

    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) > 0
    assert data["results"][0]["similarity"] >= 0.5
    assert data["search_time_ms"] < 500  # Performance requirement
```
