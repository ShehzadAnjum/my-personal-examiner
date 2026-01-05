# Phase II: Question Bank & PDF Extraction - Instructions

**Phase**: II of V
**Status**: 🔄 In Progress
**Focus**: PDF parsing, question extraction, mark scheme alignment
**Last Updated**: 2026-01-05

---

## 🎯 Phase II Objectives

**Primary Goal**: Extract questions from Cambridge past papers and align with mark schemes

**Key Deliverables**:
1. PDF question paper extraction (9708 Economics)
2. Mark scheme extraction and alignment
3. Question storage with syllabus tagging
4. Search and filtering by topic/year/paper

**Technology Stack**:
- PDF Parsing: pypdf2, pdfplumber
- OCR: pytesseract (for scanned papers)
- Database: PostgreSQL (SQLModel)
- Patterns: Regex-based extraction

---

## 📋 Phase II-Specific Patterns

### 1. Cambridge Paper Format (9708)

**Paper Types**:
- Paper 1: Multiple choice (MCQ)
- Paper 2: Data response & essay
- Paper 3: Multiple choice (A2)
- Paper 4: Data response & essay (A2)

**File Naming**:
- `9708_s22_qp_21.pdf` - Summer 2022, Question Paper, Variant 21
- `9708_s22_ms_21.pdf` - Summer 2022, Mark Scheme, Variant 21

**Skill**: Use `.claude/skills/cambridge-exam-patterns.md`

### 2. Question Extraction Pattern

**Format Detection**:
```python
# Question number patterns
QUESTION_PATTERNS = [
    r'^(\d+)\s+(.+)',           # "1 Define opportunity cost..."
    r'^(\d+)\s*\(a\)\s+(.+)',   # "1 (a) Explain..."
    r'^\(([a-z])\)\s+(.+)',     # "(a) Describe..."
]

# Marks patterns
MARKS_PATTERNS = [
    r'\[(\d+)\]$',              # [4]
    r'\((\d+)\s*marks?\)',      # (4 marks)
    r'\s+(\d+)$',               # trailing number
]
```

**Skill**: Use `.claude/skills/cambridge-exam-patterns.md`

### 3. Mark Scheme Alignment

**Pattern**: Match questions to mark scheme entries by number/subpart

```python
def align_mark_scheme(question_id: str, mark_scheme_entries: List[dict]):
    """
    Align question with mark scheme entries.

    Args:
        question_id: "1a", "2b(i)", etc.
        mark_scheme_entries: Parsed MS entries

    Returns:
        Matched mark scheme with marking points
    """
    # Normalize question ID
    normalized = question_id.lower().replace(" ", "")

    for entry in mark_scheme_entries:
        if entry['question_id'] == normalized:
            return entry

    return None
```

### 4. Syllabus Tagging Pattern

**Pattern**: Map questions to syllabus points

```python
class QuestionTag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    question_id: UUID = Field(foreign_key="question.id")
    syllabus_point_id: UUID = Field(foreign_key="syllabuspoint.id")
    confidence: float = Field(default=1.0)  # 0.0-1.0
    tagged_by: str = Field(default="auto")  # "auto" or "manual"
```

---

## 🔐 Phase II Quality Requirements

### Extraction Accuracy
- **Target**: 95% question extraction accuracy
- **Validation**: Manual review of 20 papers
- **Metrics**: Precision, recall, F1 score

### Mark Scheme Alignment
- **Target**: 90% correct alignment
- **Edge cases**: Multi-part questions, alternative answers

---

## 📚 Phase II Skills & Agents

### Primary Agents
- **Agent 02 - Backend Service** (PDF parsing, database)
- **Agent 08 - Assessment Engine** (question extraction)

### Skills Used
1. `cambridge-exam-patterns` - PDF format detection
2. `sqlmodel-database-schema-design` - Question/MS models
3. `multi-tenant-query-pattern` - User-scoped queries

---

## 📁 Related Specs

- `specs/002-question-bank/` - Feature spec
- `history/adr/003-economics-pdf-extraction-patterns.md`
- `history/adr/004-regex-capturing-group-merge-strategy.md`
- `history/adr/005-minimal-mark-scheme-extraction.md`

---

**Phase II Status**: 🔄 In Progress
**Next Phase**: Phase III (AI Marking & Teaching)
**Version**: 1.0.0 | **Last Updated**: 2026-01-05
