# Implementation Plan: Embedding Integration for Syllabus and Content

**Branch**: `010-embedding-integration` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-embedding-integration/spec.md`

## Summary

Implement local embedding storage using Gemini text-embedding-004 model to enable token-free semantic search and content alignment. After successful syllabus extraction, embeddings are generated for each topic and stored inline on SyllabusPoint (768-dimension vectors via pgvector). This provides 98%+ token savings for post-extraction operations like topic search and textbook-to-syllabus alignment.

## Technical Context

**Language/Version**: Python 3.12+, TypeScript 5.7+
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22+, pgvector, google-generativeai
**Storage**: PostgreSQL 16 with pgvector extension (Neon Serverless)
**Testing**: pytest 8.3+ (backend), Jest 29+ (frontend)
**Target Platform**: Linux server (Vercel), Web browser
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 500ms semantic search, 60s embedding generation for 60 topics
**Constraints**: Multi-tenant isolation (embeddings scoped to subject/syllabus)
**Scale/Scope**: 1,000+ embedded topics, 50+ textbook chapters

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I: Subject Accuracy | PASS | Embeddings represent syllabus topics exactly as extracted |
| II: A* Standard Marking | N/A | Feature doesn't affect marking |
| III: Syllabus Sync | PASS | Embeddings regenerated when syllabus updated |
| IV: Spec-Driven | PASS | This plan follows spec.md |
| V: Multi-Tenant Isolation | PASS | Embeddings scoped to subject/syllabus, not cross-student |
| VI: Constructive Feedback | N/A | Feature doesn't affect feedback |
| VII: Phase Boundaries | PASS | Feature is self-contained |
| VIII: Question Bank Quality | N/A | Feature doesn't affect questions |
| IX: SpecKitPlus Compliance | PASS | Following /sp.specify → /sp.plan → /sp.tasks |
| X: Official Skills Priority | PASS | No official embedding skill available |
| XIII: RI Announcement | PASS | Will announce agent/skill usage |
| XVI: Token Conservation | PASS | **This feature implements token conservation** |

**Gate Status**: ✅ PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/010-embedding-integration/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── embedding-api.yaml
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── syllabus_point.py      # Add embedding column
│   ├── services/
│   │   └── embedding_service.py   # NEW: Embedding generation
│   ├── ai_integration/
│   │   └── embedding_client.py    # NEW: Gemini/OpenAI wrapper
│   └── routes/
│       └── search.py              # NEW: Semantic search endpoint
├── alembic/versions/
│   └── 020_add_embedding_columns.py  # NEW: Migration
└── tests/
    ├── unit/
    │   └── test_embedding_service.py
    └── integration/
        └── test_semantic_search.py

frontend/
├── lib/
│   ├── api/
│   │   └── search.ts              # Semantic search API client
│   └── hooks/
│       └── useSemanticSearch.ts   # React Query hook
└── components/
    └── search/
        └── SemanticSearchBar.tsx  # Optional UI component
```

**Structure Decision**: Web application structure (existing). Adding embedding service to backend, semantic search API, and optional frontend components.

## Complexity Tracking

> **No violations requiring justification**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---

## Phase 0: Research

### Research Topics

1. **pgvector Extension**: Installation, vector operations, indexing strategies
2. **Gemini Embedding API**: text-embedding-004 model, rate limits, dimensions
3. **Embedding Fallback Pattern**: Multi-key rotation, OpenAI fallback
4. **Vector Similarity Search**: Cosine vs L2 distance, performance optimization

### Findings

See [research.md](./research.md) for detailed findings.

---

## Phase 1: Design & Contracts

### Data Model Changes

See [data-model.md](./data-model.md) for entity definitions.

**SyllabusPoint Extensions**:
- `embedding`: VECTOR(768) - Nullable, inline storage
- `embedding_model`: VARCHAR(50) - Model version used
- `embedded_at`: TIMESTAMP - When embedding was generated

**Resource Extensions** (for textbook alignment):
- `embedding`: VECTOR(768) - Nullable
- `embedding_model`: VARCHAR(50)
- `embedded_at`: TIMESTAMP

### API Contracts

See [contracts/embedding-api.yaml](./contracts/embedding-api.yaml) for OpenAPI spec.

**New Endpoints**:
- `POST /api/embeddings/generate/{syllabus_id}` - Generate embeddings for syllabus topics
- `POST /api/search/semantic` - Semantic search across topics
- `POST /api/embeddings/align` - Align external content to topics
- `GET /api/embeddings/status/{syllabus_id}` - Check embedding generation status

### Integration Scenarios

See [quickstart.md](./quickstart.md) for integration examples.

---

## Implementation Phases

### Phase A: Infrastructure (pgvector + migration)
- Install pgvector extension
- Create Alembic migration for embedding columns
- Test vector operations locally

### Phase B: Embedding Service
- Create embedding client (Gemini multi-key + OpenAI fallback)
- Create embedding service (generate, store, retry)
- Unit tests for embedding generation

### Phase C: Semantic Search
- Implement similarity search endpoint
- Add topic search with relevance ranking
- Performance testing (<500ms target)

### Phase D: Integration
- Hook into syllabus extraction flow
- Add textbook alignment endpoint
- End-to-end integration tests

### Phase E: Polish
- Error handling and retry logic
- Logging and monitoring
- Documentation updates
