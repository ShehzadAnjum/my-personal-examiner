# Data Model: Resource Bank

**Feature**: 006-resource-bank
**Date**: 2025-12-25
**Source**: [spec.md](./spec.md)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────┐         ┌──────────────────────┐                          │
│  │  SyllabusPoint  │◄────────│ GeneratedExplanation │                          │
│  │   (existing)    │ 1    n  │     (NEW)            │                          │
│  └─────────────────┘         └──────────┬───────────┘                          │
│                                         │                                       │
│                                         │ n                                     │
│                                         │                                       │
│  ┌─────────────────┐         ┌──────────▼───────────┐                          │
│  │    Student      │◄────────│ StudentLearningPath  │                          │
│  │   (existing)    │ 1    n  │     (NEW)            │                          │
│  └────────┬────────┘         └──────────────────────┘                          │
│           │                                                                     │
│           │ 1                                                                   │
│           │                                                                     │
│  ┌────────▼────────┐                                                           │
│  │ StudentLLMConfig│                                                           │
│  │     (NEW)       │                                                           │
│  └─────────────────┘                                                           │
│                                                                                 │
│  ┌─────────────────┐  (Metadata table - no FK relationships)                   │
│  │  ResourceCache  │                                                           │
│  │     (NEW)       │                                                           │
│  └─────────────────┘                                                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Entities

### 1. GeneratedExplanation (NEW)

Stores all generated topic explanations as shared resources.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| syllabus_point_id | UUID | FK → SyllabusPoint.id, NOT NULL | Links to syllabus topic |
| version | Integer | NOT NULL, default 1 | Version number (1 = admin, 2+ = student) |
| content | JSON | NOT NULL | TopicExplanation schema content |
| generated_by | Enum | NOT NULL | 'system' or 'student' |
| generator_student_id | UUID | FK → Student.id, NULLABLE | NULL for v1, set for v2+ |
| llm_provider | String(50) | NOT NULL | 'anthropic', 'openai', 'google' |
| llm_model | String(100) | NOT NULL | Model identifier used |
| token_cost | Integer | NOT NULL, default 0 | Tokens consumed for generation |
| quality_rating | Float | NULLABLE, 0.0-5.0 | Optional curation rating |
| signature | String(64) | NOT NULL | SHA-256 hash for sync |
| created_at | DateTime | NOT NULL, default now() | Creation timestamp |
| updated_at | DateTime | NOT NULL, default now() | Last update timestamp |

**Indexes**:
- `idx_explanation_syllabus_version` ON (syllabus_point_id, version) UNIQUE
- `idx_explanation_generator` ON (generator_student_id) WHERE generator_student_id IS NOT NULL
- `idx_explanation_signature` ON (signature)

**Constraints**:
- CHECK: version >= 1
- CHECK: quality_rating IS NULL OR (quality_rating >= 0 AND quality_rating <= 5)
- CHECK: (generated_by = 'system' AND generator_student_id IS NULL) OR (generated_by = 'student' AND generator_student_id IS NOT NULL)

---

### 2. StudentLearningPath (NEW)

Tracks per-student learning progress for each topic.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| student_id | UUID | FK → Student.id, NOT NULL | Multi-tenant isolation key |
| syllabus_point_id | UUID | FK → SyllabusPoint.id, NOT NULL | Topic being tracked |
| explanation_id | UUID | FK → GeneratedExplanation.id, NULLABLE | Current preferred version |
| view_count | Integer | NOT NULL, default 0 | Times topic viewed |
| total_time_spent_seconds | Integer | NOT NULL, default 0 | Accumulated reading time |
| last_viewed_at | DateTime | NULLABLE | Last view timestamp |
| preferred_version | Integer | NOT NULL, default 1 | Which version student prefers |
| is_bookmarked | Boolean | NOT NULL, default false | Personal bookmark flag |
| mastery_level | Enum | NOT NULL, default 'not_started' | Learning progress |
| created_at | DateTime | NOT NULL, default now() | Record creation |
| updated_at | DateTime | NOT NULL, default now() | Last update |

**Mastery Level Enum Values**:
- `not_started` - Never viewed
- `learning` - Viewed 1-2 times, < 5 min total
- `familiar` - Viewed 3+ times OR > 10 min total
- `mastered` - Marked by student or inferred from exam performance

**Indexes**:
- `idx_learningpath_student_syllabus` ON (student_id, syllabus_point_id) UNIQUE
- `idx_learningpath_student_bookmarked` ON (student_id) WHERE is_bookmarked = true
- `idx_learningpath_student_mastery` ON (student_id, mastery_level)

**Constraints**:
- CHECK: view_count >= 0
- CHECK: total_time_spent_seconds >= 0
- CHECK: preferred_version >= 1

---

### 3. StudentLLMConfig (NEW)

Encrypted storage for student's own LLM API keys.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| student_id | UUID | FK → Student.id, NOT NULL | Owner of this config |
| provider | Enum | NOT NULL | 'openai', 'anthropic', 'google' |
| api_key_encrypted | String(512) | NOT NULL | AES-256-GCM encrypted key |
| is_active | Boolean | NOT NULL, default true | Whether key is active |
| created_at | DateTime | NOT NULL, default now() | When key was added |
| updated_at | DateTime | NOT NULL, default now() | Last update |
| usage_this_month | Integer | NOT NULL, default 0 | Token count this billing period |
| usage_reset_at | DateTime | NOT NULL | When usage counter resets |

**Provider Enum Values**:
- `openai`
- `anthropic`
- `google`

**Indexes**:
- `idx_llmconfig_student_provider` ON (student_id, provider) UNIQUE
- `idx_llmconfig_student_active` ON (student_id) WHERE is_active = true

**Constraints**:
- CHECK: usage_this_month >= 0

---

### 4. ResourceCache (NEW)

Metadata tracking for local file cache (not stored in PostgreSQL).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| syllabus_point_id | String(36) | PK part 1 | UUID as string |
| version | Integer | PK part 2 | Version number |
| file_path | String(500) | NOT NULL | Relative path to cached file |
| signature | String(64) | NOT NULL | SHA-256 hash for sync comparison |
| cached_at | DateTime | NOT NULL | When file was cached |
| last_synced_at | DateTime | NOT NULL | Last sync check timestamp |
| file_size_bytes | Integer | NOT NULL | Size of cached file |

**Note**: This entity is stored in a local SQLite database or JSON index file, NOT in PostgreSQL. It's used for cache management only.

---

## State Transitions

### Mastery Level Transitions

```
                    View (1st time)
    not_started ─────────────────────► learning
                                           │
                                           │ View 3+ times OR time > 10 min
                                           ▼
                                       familiar
                                           │
                                           │ Student marks OR exam performance
                                           ▼
                                       mastered
```

**Transition Rules**:
- `not_started → learning`: First view of topic
- `learning → familiar`: view_count >= 3 OR total_time_spent_seconds >= 600
- `familiar → mastered`: Manual mark by student OR derived from exam performance > 80%
- Any state can transition back if student explicitly resets

---

## Validation Rules

### GeneratedExplanation

1. **Content Validation**: Must conform to TopicExplanation JSON schema
2. **Version Uniqueness**: Only one explanation per (syllabus_point_id, version) pair
3. **Generator Consistency**: v1 must have generated_by='system', v2+ must have generated_by='student' with valid generator_student_id

### StudentLearningPath

1. **Multi-Tenant**: All queries MUST filter by student_id
2. **Preferred Version**: Must reference an existing GeneratedExplanation version
3. **Time Tracking**: total_time_spent_seconds only increments, never decreases

### StudentLLMConfig

1. **Encryption Required**: api_key_encrypted must never contain plaintext
2. **Key Masking**: Only last 4 characters shown in any response
3. **Provider Uniqueness**: One active key per provider per student

---

## Relationships Summary

| From | To | Type | Description |
|------|-----|------|-------------|
| GeneratedExplanation | SyllabusPoint | Many-to-One | Each explanation belongs to one topic |
| GeneratedExplanation | Student | Many-to-One (optional) | v2+ linked to generating student |
| StudentLearningPath | Student | Many-to-One | Multi-tenant isolation |
| StudentLearningPath | SyllabusPoint | Many-to-One | Track progress per topic |
| StudentLearningPath | GeneratedExplanation | Many-to-One (optional) | Current preferred version |
| StudentLLMConfig | Student | Many-to-One | Student owns their keys |

---

## Migration Notes

1. **New Tables**: Create in order: GeneratedExplanation → StudentLLMConfig → StudentLearningPath
2. **Foreign Keys**: SyllabusPoint and Student tables must exist (Phase I)
3. **Indexes**: Create after table creation for performance
4. **Encryption Key**: ENCRYPTION_KEY environment variable required before first insert to StudentLLMConfig
