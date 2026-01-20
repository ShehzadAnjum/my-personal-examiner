# Feature Specification: Embedding Integration for Syllabus and Content

**Feature Branch**: `010-embedding-integration`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Embedding Integration for Syllabus and Content - Implement local embedding storage using Gemini text-embedding-004 model for syllabus topics, sections, and future textbook content. One-time embedding generation after LLM extraction, stored in PostgreSQL pgvector. Enables: (1) Free semantic search across topics, (2) Textbook-to-syllabus alignment without LLM tokens, (3) Content discovery via similarity. Flow: Current extraction unchanged → Post-extraction embedding generation → Store in pgvector column → Query via cosine similarity. Target: 98% token savings on post-extraction operations."

---

## Problem Statement

Currently, every content search and syllabus-related operation requires sending full text to an LLM, consuming 3,000-4,000 tokens per operation. For a typical syllabus lifecycle (extraction, refinements, searches, textbook alignment), this costs approximately 256,000 tokens. This is expensive, slow, and does not scale when adding textbooks or multiple subjects.

**Solution**: Generate embeddings once after initial extraction, store them locally, and use similarity search for all subsequent operations. This reduces post-extraction token usage by ~98%.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Embedding Generation (Priority: P1)

As an admin, after I extract topics from a syllabus PDF, the system automatically generates and stores embeddings for each topic so that future searches don't require LLM calls.

**Why this priority**: This is the foundation - without stored embeddings, no other features work. It provides immediate value by enabling all subsequent token-free operations.

**Independent Test**: After extracting topics from a syllabus, verify that each topic has an associated embedding stored. Subsequent topic searches should return results without making LLM API calls.

**Acceptance Scenarios**:

1. **Given** a syllabus with extracted topics, **When** extraction completes successfully, **Then** embeddings are automatically generated for all topics within 30 seconds.
2. **Given** a topic with code "1.1" and title "Scarcity and choice", **When** embeddings are generated, **Then** the embedding is stored and retrievable by topic ID.
3. **Given** embedding generation fails for some topics, **When** the process completes, **Then** the system logs which topics failed and allows manual retry.

---

### User Story 2 - Semantic Topic Search (Priority: P2)

As a user, I can search for topics using natural language queries (e.g., "market failure externalities") and get relevant results ranked by semantic similarity, without waiting for LLM processing.

**Why this priority**: This is the primary use case that delivers immediate value to users. Once embeddings exist, search becomes instant and free.

**Independent Test**: Search for "government intervention in markets" and verify results include relevant topics like "Market failure", "Subsidies", "Taxation" ranked by relevance, with response time under 500ms.

**Acceptance Scenarios**:

1. **Given** embeddings exist for all syllabus topics, **When** user searches "inflation causes", **Then** results include topics about inflation, monetary policy, and aggregate demand, ranked by relevance.
2. **Given** a search query, **When** results are returned, **Then** response time is under 500 milliseconds.
3. **Given** a search query with no close matches, **When** similarity scores are all below threshold, **Then** system returns "No closely matching topics found" with suggestions.

---

### User Story 3 - Textbook-to-Syllabus Alignment (Priority: P3)

As an admin, I can upload textbook content and the system automatically identifies which syllabus topics each chapter/section covers, without using LLM tokens for matching.

**Why this priority**: This extends the embedding value to new content types. Depends on P1 being complete. Enables rich learning resources without ongoing token costs.

**Independent Test**: Upload a textbook chapter about "Price Elasticity of Demand", verify system identifies matching syllabus topics (e.g., "2.1 Price elasticity of demand") with confidence scores.

**Acceptance Scenarios**:

1. **Given** a textbook chapter text, **When** alignment is requested, **Then** system returns top 5 matching syllabus topics with similarity scores.
2. **Given** a chapter covering multiple topics, **When** alignment completes, **Then** all relevant topics are identified (not just the highest match).
3. **Given** a chapter with no syllabus alignment (e.g., unrelated content), **When** alignment is attempted, **Then** system indicates low confidence and suggests manual review.

---

### User Story 4 - Re-embed on Content Update (Priority: P4)

As an admin, when I update a topic's description or add learning outcomes, the system automatically regenerates that topic's embedding to keep search results accurate.

**Why this priority**: Ensures data consistency over time. Lower priority because initial implementation can work without this (just re-embed all on major changes).

**Independent Test**: Update topic 1.1's description, verify its embedding is regenerated, and confirm search results reflect the updated content.

**Acceptance Scenarios**:

1. **Given** a topic with an existing embedding, **When** the topic description is updated, **Then** the embedding is regenerated within 10 seconds.
2. **Given** multiple topics updated in bulk, **When** updates complete, **Then** all affected embeddings are regenerated.

---

### Edge Cases

- **Empty content**: Topics with no description should use title + code for embedding generation.
- **Duplicate content**: Topics with identical text should still get individual embeddings (allows per-topic metadata).
- **Very long content**: Content exceeding embedding model limits should be truncated with a warning logged.
- **Network failure during embedding**: Failed embeddings should be marked for retry; partial success should not block the extraction workflow.
- **Embedding model unavailable**: System should queue embedding requests and process when service recovers.
- **Migration of existing data**: Existing topics without embeddings should be embeddable via a bulk regeneration action.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate embeddings automatically after successful topic extraction from a syllabus.
- **FR-002**: System MUST store embeddings locally alongside topic data (not in external services).
- **FR-003**: System MUST provide semantic search that returns topics ranked by similarity to query.
- **FR-004**: System MUST complete embedding generation for a typical syllabus (50-60 topics) within 60 seconds.
- **FR-005**: System MUST return semantic search results within 500 milliseconds.
- **FR-006**: System MUST support re-generating embeddings for individual topics or in bulk.
- **FR-007**: System MUST log embedding generation failures without blocking the main extraction workflow.
- **FR-008**: System MUST support aligning external content (textbook chapters) to syllabus topics via embedding similarity.
- **FR-009**: System MUST respect multi-tenant isolation (embeddings scoped to subject/syllabus, not shared across students' data).
- **FR-010**: System MUST handle embedding model rate limits by rotating through available Gemini API keys (1-5) before falling back to OpenAI; log which key/model was used for each embedding.

### Key Entities

- **SyllabusPoint** (existing): Extended with inline `embedding` vector column (768 dimensions), `embedding_model` version string, and `embedded_at` timestamp.
- **Resource** (existing): Extended with embedding vector for textbook/content alignment.
- **EmbeddingJob**: Tracks bulk embedding generation (status, progress, error count).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Post-extraction operations (search, alignment) consume zero LLM tokens, achieving 98%+ token savings compared to current approach.
- **SC-002**: Semantic search returns results in under 500 milliseconds for queries against 1,000+ embedded topics.
- **SC-003**: Embedding generation for a 60-topic syllabus completes within 60 seconds.
- **SC-004**: 95% of semantic searches return at least one relevant topic in the top 3 results (measured by user feedback or manual validation).
- **SC-005**: System handles embedding generation failures gracefully - extraction workflow completes successfully even if embedding fails (with retry mechanism).
- **SC-006**: Textbook chapter alignment correctly identifies the primary syllabus topic 90% of the time (validated against manual mapping).

---

## Assumptions

1. **Embedding model availability**: Gemini text-embedding-004 (or equivalent) has sufficient free tier capacity for our usage (1,500 requests/minute).
2. **Embedding dimensions**: 768 dimensions (Gemini default) provides sufficient semantic resolution for educational content.
3. **Storage capacity**: Local database can accommodate embedding vectors (768 floats x number of topics) without performance impact.
4. **One embedding per topic**: Each topic gets a single embedding from its combined code + title + description; no chunking needed for syllabus content.
5. **Similarity threshold**: Cosine similarity >= 0.7 indicates a relevant match; below 0.5 indicates no meaningful relationship.
6. **Current extraction unchanged**: The existing LLM-based extraction flow remains; embeddings are generated as a post-processing step.

---

## Out of Scope

- Real-time embedding updates during user typing (batch processing only)
- Multi-language embedding support (English only for MVP)
- Fine-tuning custom embedding models
- Cross-subject similarity (embeddings scoped to single syllabus)
- Embedding-based answer evaluation (separate feature)
- UI for embedding management (admin-only, API-driven for MVP)

---

## Dependencies

- **Existing**: LLM extraction flow (must complete before embeddings can be generated)
- **Existing**: SyllabusPoint and Resource database models
- **New**: Vector storage capability in database (pgvector extension or equivalent)
- **External**: Gemini embedding API with multi-key rotation (GEMINI_API_KEY_1 through _5); OpenAI text-embedding-3-small as final fallback

---

## Clarifications

### Session 2026-01-21

- Q: Where should topic embeddings be stored - inline column on SyllabusPoint, separate table, or hybrid? → A: Inline column directly on SyllabusPoint table (simplifies queries, no joins needed)
- Q: How should embedding model fallback work when primary fails? → A: Rotate through all Gemini API keys (1-5, currently 3 configured) first; only fall back to OpenAI after all Gemini keys exhausted
