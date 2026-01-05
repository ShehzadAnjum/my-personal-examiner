# Reusable Intelligence Analysis: Feature 007-resource-bank-files

**Feature**: Resource Bank File Storage & Multi-Source Content Management
**Date**: 2025-12-27
**Analyst**: Claude Sonnet 4.5

---

## Executive Summary

After analyzing the Resource Bank specification against existing agents (16) and skills (22), I recommend:

- **NEW SKILLS NEEDED**: 3 new skills
- **NEW AGENTS NEEDED**: 0 (existing agents sufficient)
- **SKILL UPDATES NEEDED**: 1 existing skill
- **CONSTITUTION UPDATE**: Required (new technology dependencies)

**Rationale**: Resource Bank introduces new technology patterns (S3 storage, PDF/OCR, YouTube API) but fits within existing agent responsibilities (backend-service, syllabus-research). New skills codify these patterns for reusability.

---

## Existing Coverage Analysis

### Covered by Existing Agents

**Agent 02: backend-service** ✅
- SQLModel models for 4 new tables (resources, syllabus_point_resources, explanation_resource_usage, student_resource_preferences)
- FastAPI routes for resource upload, admin review, tagging
- Alembic migrations for schema changes
- Multi-tenant query patterns (visibility + student_id filtering)
- Service layer for resource management logic

**Agent 05: syllabus-research** ✅
- Daily sync job for Cambridge past papers (WebFetch/WebSearch tools available)
- Syllabus update detection (already has Cambridge website scraping)
- Resource metadata extraction from Cambridge sources

**Agent 07: testing-quality** ✅
- Unit tests for resource service (pytest patterns)
- Integration tests for file upload workflow
- Security tests for multi-tenant isolation

### Covered by Existing Skills

**multi-tenant-query-pattern** ✅
- Visibility filtering (public/private/pending_review)
- Student_id scoping for user uploads
- Admin-only queries for pending resources

**sqlmodel-database-schema-design** ✅
- JSONB metadata field patterns
- Resource table with flexible type system
- Foreign key relationships

**fastapi-route-implementation** ✅
- File upload endpoints with FormData
- Admin review endpoints (approve/reject/edit)
- Resource tagging endpoints

**alembic-migration-creation** ✅
- Create 4 new tables
- Add ENUM types (resource_type, visibility)
- Create indexes for performance

**pytest-testing-patterns** ✅
- Test file uploads with mock S3
- Test OCR processing
- Test multi-tenant isolation

**resource-bank-content** ✅ (ALREADY EXISTS)
- Topic explanation generation (created 2025-12-26)
- 9-component schema enforcement
- LLM prompt construction

---

## Gaps Requiring New Skills

### Gap 1: File Storage Management (S3 + Local)

**Missing Pattern**: No existing skill for S3 upload, local file storage, signature calculation

**New Skill Required**: `file-storage-s3-integration`

**Content**:
- boto3 S3 upload patterns with retry logic
- Local file storage directory organization
- SHA-256 signature calculation for change detection
- Background task queue for async uploads (Celery/asyncio)
- File cleanup and temporary file management
- Multi-part upload for large files

**Usage Frequency**: High (every resource upload, every sync)

**Reusability**: High (future features: student avatars, exam PDFs, chart images)

---

### Gap 2: PDF Parsing & OCR

**Missing Pattern**: No existing skill for PDF text extraction, OCR, scanned document handling

**New Skill Required**: `pdf-extraction-ocr`

**Content**:
- PyPDF2 text extraction patterns
- pytesseract OCR setup and usage (requires tesseract binary)
- Scanned PDF detection (check for text content)
- Full-text search indexing preparation
- PDF metadata extraction (author, creation date, page count)
- Error handling for corrupted PDFs

**Usage Frequency**: Medium (past paper ingestion, textbook processing, user uploads)

**Reusability**: Medium (future features: question extraction from PDFs, mark scheme parsing)

---

### Gap 3: YouTube Transcript Extraction

**Missing Pattern**: No existing skill for YouTube API, transcript extraction, video metadata

**New Skill Required**: `youtube-api-integration`

**Content**:
- youtube-transcript-api usage patterns
- YouTube Data API v3 for video metadata
- Rate limit handling (quota management)
- Transcript timestamp extraction
- Keyword matching in transcripts for relevance scoring
- Error handling for unavailable transcripts

**Usage Frequency**: Low (Phase 1 MVP: max 10 videos)

**Reusability**: Medium (future features: video-based learning paths, transcript search)

---

### Gap 4: Resource Sync Strategy (SKILL UPDATE)

**Missing Pattern**: Differential sync, signature-based change detection, daily batch jobs

**Recommendation**: UPDATE existing skill `syllabus-research` → rename to `cambridge-resource-sync`

**Added Content**:
- Signature-based differential sync (only download if hash changed)
- Daily sync job scheduling (cron patterns)
- First-time vs. subsequent sync logic
- Retry logic for failed downloads
- Resource metadata extraction from Cambridge URLs
- Change detection and notification patterns

**Rationale**: Syllabus research agent already handles Cambridge website interaction, this extends its capabilities to resource sync

**Usage Frequency**: High (daily automated sync)

**Reusability**: High (future subjects: 9706, 8021, 9709)

---

## Agent Analysis: No New Agents Needed

### Why Existing Agents Suffice

**Agent 02 (backend-service)** handles:
- Database models and migrations ✅
- FastAPI routes for uploads, review, tagging ✅
- Service layer business logic ✅
- Multi-tenant isolation ✅

**Agent 05 (syllabus-research)** handles:
- Cambridge website scraping ✅
- Daily sync jobs ✅
- Resource metadata extraction ✅

**Agent 07 (testing-quality)** handles:
- Unit/integration tests ✅
- Security testing ✅

### Considered but Rejected: "resource-ingestion" Agent

**Initial Consideration**: Create specialized agent for PDF/OCR/YouTube/S3

**Rejection Rationale**:
1. **Too Narrow**: Only used during resource upload (not long-lived enough)
2. **Already Covered**: Backend-service agent has file handling expertise
3. **Skills Sufficient**: New skills provide patterns, agent calls them
4. **Complexity**: 3 skills easier to maintain than 1 agent + 3 skills

**Decision**: Use skills for reusable patterns, existing agents for orchestration

---

## Constitution Updates Required

### New Technology Dependencies

**Add to "Technology Stack (LOCKED by Constitution)" section**:

**Resource Management**:
- **File Storage**: Local (backend/resources/) + AWS S3 (background upload)
- **PDF Processing**: PyPDF2 2.12+ (text extraction), pytesseract 0.3+ (OCR)
- **YouTube API**: youtube-transcript-api 0.6+, YouTube Data API v3
- **Background Jobs**: Celery 5.3+ with Redis broker (or Python asyncio for MVP)
- **Virus Scanning**: ClamAV 0.103+ (optional for Phase 1, required for production)

**Rationale**: Locks technology choices to prevent mid-feature changes (Constitution Principle IV)

### New Dependencies Section

**Add to Constitution dependencies**:

**External Services**:
- AWS S3 or compatible object storage (credentials via environment variables)
- Cambridge International website (past paper downloads)
- YouTube Data API v3 (API key required, quota monitoring)
- ClamAV daemon (virus scanning for uploads)

**Testing Tools**:
- moto 4.2+ (S3 mocking for tests)
- pytest-asyncio 0.23+ (async task testing)
- Playwright (if admin UI testing required)

---

## ADR Requirements

**ADR-008: File Storage Architecture (Local + S3)**
- **Decision**: Use local storage as primary, S3 as background backup
- **Context**: Multi-source resources, large file sizes (50MB limit)
- **Alternatives**: S3-only, local-only, database BLOB storage
- **Consequences**: Improved performance (local reads), redundancy (S3 backup), complexity (sync jobs)

**ADR-009: Differential Sync Strategy (Signature-Based)**
- **Decision**: Use SHA-256 signatures for change detection, only download if changed
- **Context**: Daily sync of Cambridge resources, bandwidth optimization
- **Alternatives**: Full re-download daily, modification date comparison, version numbers
- **Consequences**: Reduced bandwidth, faster syncs, signature calculation overhead

**ADR-010: PDF Processing Strategy (PyPDF2 + OCR)**
- **Decision**: PyPDF2 for native PDFs, pytesseract for scanned PDFs
- **Context**: Mix of native and scanned Cambridge past papers
- **Alternatives**: PDFMiner, pdfplumber, commercial OCR APIs
- **Consequences**: Free open-source, acceptable 85% OCR accuracy, requires tesseract binary

**ADR-011: YouTube Transcript Extraction (youtube-transcript-api)**
- **Decision**: Use youtube-transcript-api for transcript extraction, YouTube Data API for metadata
- **Context**: Low volume (10 videos Phase 1), educational use case
- **Alternatives**: Whisper API (transcription), manual entry, skip video support
- **Consequences**: Free (within quota), automated, rate limit monitoring required

---

## Implementation Recommendations

### Phase 1 (Immediate)

1. **Create 3 new skills**:
   - file-storage-s3-integration
   - pdf-extraction-ocr
   - youtube-api-integration

2. **Update 1 existing skill**:
   - syllabus-research → cambridge-resource-sync (extend with differential sync patterns)

3. **Update Constitution**:
   - Add Resource Management to Technology Stack
   - Add External Services to Dependencies

4. **Create 4 ADRs**:
   - ADR-008: File Storage Architecture
   - ADR-009: Differential Sync Strategy
   - ADR-010: PDF Processing Strategy
   - ADR-011: YouTube Transcript Extraction

### Phase 2 (After MVP)

5. **Skill Evolution**:
   - Monitor skill usage during implementation
   - Consolidate if overlap discovered
   - Add quick-reference guides for common patterns

6. **Agent Evolution**:
   - If resource ingestion patterns become complex (>500 lines), reconsider dedicated agent
   - Track Agent 02 workload (if overloaded, split responsibilities)

---

## Quality Assurance

### Skill Quality Criteria

Each new skill MUST include:
- [ ] Overview (1-2 sentences)
- [ ] When to Use (scenarios)
- [ ] Code examples (minimum 3)
- [ ] Common pitfalls (minimum 2)
- [ ] Testing patterns
- [ ] Constitutional compliance notes
- [ ] Version history

### Skill Testing Strategy

**file-storage-s3-integration**:
- Test S3 upload with moto mocking
- Test signature calculation consistency
- Test retry logic for failed uploads

**pdf-extraction-ocr**:
- Test native PDF extraction (sample past paper)
- Test scanned PDF OCR (sample scanned document)
- Test corrupted PDF error handling

**youtube-api-integration**:
- Test transcript extraction (sample video)
- Test rate limit handling (mock quota exceeded)
- Test unavailable transcript fallback

---

## Summary

**Agent Changes**: 0 new agents (existing coverage sufficient)

**Skill Changes**: 3 new skills + 1 skill update

**Constitution Changes**: 1 section update (Technology Stack)

**ADR Requirements**: 4 new ADRs (file storage, sync, PDF, YouTube)

**Total Effort**: ~4 hours (skills creation) + 2 hours (ADRs) = 6 hours

**Recommendation**: PROCEED with skill creation, constitution update, and ADR generation before `/sp.plan` phase.

---

**Approved**: Pending user review
**Next Steps**: Create skills, update constitution, generate ADRs, then proceed to `/sp.plan`
