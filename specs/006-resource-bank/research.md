# Research: Resource Bank

**Feature**: 006-resource-bank
**Date**: 2025-12-25
**Status**: Complete

## Research Tasks Completed

### 1. API Key Encryption Strategy

**Decision**: AES-256-GCM symmetric encryption with environment-based master key

**Rationale**:
- Industry standard for sensitive data at rest
- GCM mode provides authenticated encryption (integrity + confidentiality)
- Single master key simplifies key management vs per-user keys
- Python `cryptography` library is well-maintained and audited

**Alternatives Considered**:
- RSA asymmetric encryption: Rejected - unnecessary complexity, slower
- bcrypt hashing: Rejected - need to decrypt keys for LLM API calls
- AWS KMS/Vault: Rejected - adds external dependency, overkill for MVP

**Implementation**:
```python
from cryptography.fernet import Fernet
# Master key from ENCRYPTION_KEY env var
# encrypt(api_key) → store in DB
# decrypt(encrypted_key) → use for LLM call
```

### 2. Local File Cache Structure

**Decision**: JSON files organized by syllabus_point_id with signature metadata

**Rationale**:
- JSON is human-readable and easy to debug
- File-per-explanation allows efficient partial updates
- Signature in filename enables quick staleness check

**Structure**:
```
backend/cache/resources/explanations/
├── {syllabus_point_id}_v{version}_{signature}.json
└── index.json  # Maps syllabus_point_id → latest file
```

**Alternatives Considered**:
- SQLite cache: Rejected - adds complexity, file-based is simpler
- Redis: Rejected - external service, not needed for single-instance
- Single large JSON: Rejected - poor performance for partial updates

### 3. Signature Algorithm for Sync

**Decision**: SHA-256 hash of content + updated_at timestamp

**Rationale**:
- SHA-256 is fast and collision-resistant
- Including timestamp ensures regenerated identical content is still synced
- 64-char hex string is compact and easy to compare

**Implementation**:
```python
import hashlib
signature = hashlib.sha256(
    f"{json.dumps(content, sort_keys=True)}:{updated_at.isoformat()}".encode()
).hexdigest()
```

### 4. Multi-Tenant Query Pattern

**Decision**: Mandatory student_id filter using SQLModel query pattern

**Rationale**:
- Consistent with existing project patterns (see coaching, teaching routes)
- SQLModel makes it easy to chain .where() clauses
- Type safety from Pydantic/SQLModel schemas

**Pattern**:
```python
# ALWAYS filter by student_id for per-student data
statement = select(StudentLearningPath).where(
    StudentLearningPath.student_id == student_uuid
)
```

### 5. Version Control for Explanations

**Decision**: Integer version number with generator_type enum

**Rationale**:
- Simple integer versioning (1, 2, 3...) is intuitive
- generator_type (system/student) distinguishes admin vs student content
- Allows future promotion workflow (student v2 → shared v1)

**Schema**:
```python
class GeneratedExplanation:
    version: int  # 1 = first version, 2+ = subsequent
    generated_by: Literal["system", "student"]
    generator_student_id: Optional[UUID]  # null for system, set for student
```

### 6. Learning Path Tracking Granularity

**Decision**: Per-topic aggregated stats, not per-session

**Rationale**:
- Simpler data model (one row per student-topic pair)
- Sufficient for mastery tracking and recommendations
- Lower storage overhead than session-level tracking

**Tracked Metrics**:
- view_count: Integer (incremented on each view)
- total_time_spent_seconds: Integer (accumulated)
- last_viewed_at: DateTime
- preferred_version: Integer (which version student last viewed)
- mastery_level: Enum (not_started, learning, familiar, mastered)

### 7. LLM Provider Integration

**Decision**: Reuse existing LLMFallbackOrchestrator with student key injection

**Rationale**:
- Existing orchestrator handles fallback logic
- Can inject student's API key at runtime
- No need to rewrite LLM integration

**Implementation**:
```python
# For v2+ generation, temporarily override API key
orchestrator = LLMFallbackOrchestrator(
    override_api_key=decrypted_student_key,
    override_provider=student_preferred_provider
)
```

### 8. Frontend State Management

**Decision**: TanStack Query with localStorage optimistic cache

**Rationale**:
- Consistent with existing teaching/coaching pages
- TanStack Query handles caching, refetching, optimistic updates
- localStorage for offline resilience (not browser localStorage for main storage)

**Hooks**:
- useResourceExplanation(topicId) → fetches from API, caches in TanStack
- useLearningPath() → tracks progress, syncs on page events

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Encryption algorithm | AES-256-GCM via cryptography library |
| Cache file format | JSON with signature in filename |
| Sync trigger frequency | On-demand + startup (periodic optional) |
| Version numbering | Integer starting at 1 |
| Time tracking method | Accumulated seconds on page leave event |

## Dependencies Verified

| Dependency | Version | Status |
|------------|---------|--------|
| cryptography | 41.0+ | Available in requirements |
| SQLModel | 0.0.14+ | Already in project |
| TanStack Query | 5.62+ | Already in frontend |
| FastAPI | 0.115+ | Already in project |

## Next Steps

Proceed to Phase 1: Generate data-model.md and contracts/
