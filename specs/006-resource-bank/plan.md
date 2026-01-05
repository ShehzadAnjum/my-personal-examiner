# Implementation Plan: Resource Bank

**Branch**: `006-resource-bank` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-resource-bank/spec.md`

## Summary

Centralized resource management system that stores generated educational content (topic explanations) in a shared PostgreSQL database as the primary source of truth, with local file-based caching for performance. Content is versioned: v1 is admin-generated using system LLM keys, v2+ are student-generated using their own API keys. Individual learning paths are tracked per student including views, time spent, mastery levels, and bookmarks.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.7+ (Frontend)
**Primary Dependencies**: FastAPI 0.115+, SQLModel, Next.js 16+, React 19, TanStack Query 5.62+
**Storage**: PostgreSQL 16 (Neon) - primary, Local file cache (backend/cache/) - secondary
**Testing**: pytest 8.3+ (backend), Jest 29+ (frontend)
**Target Platform**: Web application (Linux server + browser)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <2s explanation load (cache hit), <10s generation, 90%+ cache hit rate
**Constraints**: Multi-tenant isolation required, API keys encrypted at rest
**Scale/Scope**: 50+ syllabus topics, 100+ students, 1000+ cached explanations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| 1. Subject Accuracy Non-Negotiable | PASS | Explanations linked to verified SyllabusPoints |
| 2. A* Standard Marking Always | PASS | LLM prompts use PhD-level pedagogy |
| 3. Syllabus Synchronization First | PASS | GeneratedExplanation FK to SyllabusPoint |
| 4. Spec-Driven Development | PASS | Following /sp.specify → /sp.plan workflow |
| 5. Multi-Tenant Isolation Sacred | PASS | StudentLearningPath filtered by student_id |
| 6. Feedback Constructive & Detailed | PASS | Stored explanations include all 9 components |
| 7. Phase Boundaries Hard Gates | PASS | Resource Bank is standalone feature |
| 8. Question Bank Quality Over Quantity | N/A | Question Bank is separate feature |
| 9. SpecKitPlus Workflow Compliance | PASS | Using /sp.plan command |
| 10. Official Skills Priority | PASS | Using existing project patterns |
| 11. CLAUDE.md Hierarchy | PASS | Following project CLAUDE.md |
| 12. PMP Agent | PASS | TodoWrite tracking progress |

**Gate Result**: PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/006-resource-bank/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI schemas)
│   ├── resources-api.yaml
│   └── learning-path-api.yaml
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── generated_explanation.py    # NEW: Shared explanation storage
│   │   ├── student_learning_path.py    # NEW: Per-student progress
│   │   ├── student_llm_config.py       # NEW: Encrypted API keys
│   │   └── resource_cache.py           # NEW: Cache metadata
│   ├── routes/
│   │   ├── resources.py                # NEW: Resource CRUD endpoints
│   │   └── learning_path.py            # NEW: Learning path endpoints
│   ├── services/
│   │   ├── resource_service.py         # NEW: Resource management logic
│   │   ├── cache_service.py            # NEW: File cache management
│   │   ├── sync_service.py             # NEW: DB↔Cache sync
│   │   └── llm_key_service.py          # NEW: API key encryption
│   └── schemas/
│       ├── resource_schemas.py         # NEW: Request/response schemas
│       └── learning_path_schemas.py    # NEW: Learning path schemas
├── cache/
│   └── resources/                      # NEW: Local file cache directory
│       └── explanations/               # Cached explanation JSON files
└── tests/
    ├── unit/
    │   ├── test_resource_service.py    # NEW
    │   ├── test_cache_service.py       # NEW
    │   └── test_sync_service.py        # NEW
    └── integration/
        └── test_resource_endpoints.py  # NEW

frontend/
├── app/
│   └── (dashboard)/
│       ├── teaching/
│       │   └── [topicId]/
│       │       └── page.tsx            # MODIFY: Use resource bank
│       └── settings/
│           └── page.tsx                # NEW: LLM API key configuration
├── components/
│   ├── teaching/
│   │   └── VersionSwitcher.tsx         # NEW: Switch between v1/v2+
│   └── settings/
│       └── LLMConfigForm.tsx           # NEW: API key input form
└── lib/
    ├── api/
    │   ├── resources.ts                # NEW: Resource API client
    │   └── learning-path.ts            # NEW: Learning path API client
    └── hooks/
        ├── useResourceExplanation.tsx  # NEW: Fetch with cache
        └── useLearningPath.tsx         # NEW: Track progress
```

**Structure Decision**: Web application structure with existing backend/frontend separation. New models, routes, and services added to existing directories following established patterns.

## Complexity Tracking

> No constitution violations requiring justification.

## Implementation Phases

### Phase 1: Core Data Models & Database (P1 Stories)

**Objective**: Establish database schema for shared resources and learning paths

**Tasks**:
1. Create GeneratedExplanation model with versioning support
2. Create StudentLearningPath model with multi-tenant isolation
3. Create StudentLLMConfig model with encrypted storage
4. Create ResourceCache metadata model
5. Generate Alembic migrations
6. Write unit tests for models

**Dependencies**: Existing SyllabusPoint and Student models
**Output**: Database tables ready, models tested

### Phase 2: Resource Storage & Retrieval (P1 Stories)

**Objective**: Implement CRUD operations for shared explanations

**Tasks**:
1. Create resource_service.py with save/get/list operations
2. Create cache_service.py for local file caching
3. Create resources.py routes for API endpoints
4. Implement signature-based cache invalidation
5. Write integration tests for resource endpoints

**Dependencies**: Phase 1 models
**Output**: API endpoints functional, caching working

### Phase 3: Admin Content Generation (P1 Story 2)

**Objective**: Enable admin to generate v1 baseline content

**Tasks**:
1. Create admin-only generate-v1 endpoint
2. Integrate with existing LLM orchestrator
3. Store generated content with version=1
4. Cache generated content to local files
5. Write tests for admin generation flow

**Dependencies**: Phase 2 resource service, existing LLM integration
**Output**: Admin can generate and store v1 explanations

### Phase 4: Student LLM Configuration (P2 Story 3)

**Objective**: Allow students to configure their own API keys

**Tasks**:
1. Create llm_key_service.py with AES-256 encryption
2. Create student LLM config endpoints (POST/GET/DELETE)
3. Create frontend Settings page with LLM config form
4. Implement key masking (show last 4 chars only)
5. Write security tests for key encryption

**Dependencies**: Phase 1 StudentLLMConfig model
**Output**: Students can securely store API keys

### Phase 5: Personalized Generation (P2 Story 4)

**Objective**: Enable students to generate v2+ personalized versions

**Tasks**:
1. Add generate-personalized endpoint using student's API key
2. Decrypt student API key at runtime for LLM calls
3. Store personalized versions linked to student
4. Create frontend version switcher component
5. Write tests for personalized generation

**Dependencies**: Phase 4 LLM config, Phase 2 resource service
**Output**: Students can create personalized explanations

### Phase 6: Learning Path Tracking (P2 Story 5)

**Objective**: Track per-student learning progress

**Tasks**:
1. Create learning_path_service.py with tracking logic
2. Create track-view endpoint (called on page load)
3. Implement time-spent tracking (on page leave)
4. Create learning dashboard frontend component
5. Write tests for learning path tracking

**Dependencies**: Phase 1 StudentLearningPath model
**Output**: Learning progress tracked and displayed

### Phase 7: Sync Mechanism (P3 Story 6)

**Objective**: Implement DB↔Cache synchronization

**Tasks**:
1. Create sync_service.py with signature comparison
2. Implement on-demand sync endpoint
3. Add startup sync hook
4. Configure periodic sync (optional background task)
5. Write tests for sync scenarios

**Dependencies**: Phase 2 cache service
**Output**: Cache stays in sync with database

### Phase 8: Bookmarks & Polish (P3 Story 7)

**Objective**: Complete remaining features and integration

**Tasks**:
1. Integrate bookmarks with new resource bank
2. Update existing teaching page to use resource bank
3. Add "Explained" badge with version info
4. Performance optimization and testing
5. Documentation and cleanup

**Dependencies**: All previous phases
**Output**: Feature complete and integrated

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| API key exposure | High | AES-256 encryption, never log keys, mask in responses |
| Cache corruption | Medium | Signature validation, auto-rebuild from DB |
| LLM API failures | Medium | Fallback to cached content, clear error messages |
| Multi-tenant leak | High | Mandatory student_id filter on all queries |
| Performance degradation | Medium | Cache-first strategy, lazy loading |

## Success Validation

1. **Unit Tests**: >80% coverage on new services
2. **Integration Tests**: All API endpoints tested
3. **Security Audit**: API key encryption verified
4. **Performance Test**: <2s load time with cache hit
5. **Multi-tenant Test**: Cross-student access denied

## Next Steps

Run `/sp.tasks` to generate the detailed task list from this plan.
