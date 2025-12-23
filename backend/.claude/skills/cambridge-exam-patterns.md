# Skill: Cambridge Exam Patterns

**Version:** 1.0
**Created:** 2025-12-19
**Domain:** PDF Question Extraction, Cambridge International Past Papers
**Purpose:** Encode knowledge about Cambridge exam paper formats, extraction patterns, and PDF parsing strategies

---

## Overview

This skill provides expertise in parsing Cambridge International past paper PDFs, specifically for A-Level subjects (Economics 9708, Mathematics 9709, Accounting 9706, English GP 8021). It encodes lessons learned from implementing PDF question extraction in Phase II.

**Key Capabilities:**
- Identify Cambridge PDF format variations
- Design regex patterns for question extraction
- Handle false positives (section headers, table data)
- Extract marks notation (various formats)
- Parse subpart structures (a, b, c)

---

## Cambridge PDF Filename Standard

### Format
```
{subject_code}_{session}{year}_{paper_type}_{paper_number}[_v{variant}].pdf
```

### Components
- **subject_code:** 4-digit code (9708=Economics, 9709=Math, 9706=Accounting, 8021=English GP)
- **session:** `s` (May/June), `m` (Feb/March), `w` (Oct/Nov)
- **year:** 2-digit year (22=2022, 23=2023)
- **paper_type:** `qp` (Question Paper), `ms` (Mark Scheme), `er` (Examiner Report)
- **paper_number:** 2-digit paper and variant (31=Paper 3 Variant 1, 22=Paper 2 Variant 2)
- **variant:** Optional `_v2`, `_v3` suffix

### Examples
- `9708_s22_qp_31.pdf` → Economics, Summer 2022, Question Paper, Paper 3 Variant 1
- `9708_w21_ms_32.pdf` → Economics, Winter 2021, Mark Scheme, Paper 3 Variant 2
- `9706_m23_qp_42.pdf` → Accounting, March 2023, Question Paper, Paper 4 Variant 2

**Parser:** `CambridgeFilenameParser` (97% test coverage)

---

## Economics 9708 Paper Formats

### Paper 1 (Multiple Choice)
- **Format:** 30 MCQ questions
- **Duration:** 1 hour 15 minutes
- **Marks:** 30 total (1 mark each)
- **Extraction Challenge:** OCR required for diagrams, option extraction
- **Status:** Deferred to later phase (not critical for MVP)

### Paper 2 (Data Response)
- **Format:** 1 data response question (Section A) + choose 1 from 3 essays (Section B)
- **Duration:** 1 hour 30 minutes
- **Marks:** Section A: 20 marks (subparts), Section B: 20 marks (essay)
- **Question Delimiter:** `1 Economic growth...`, `2 (a) With the help...`
- **Marks Notation:** `[8]`, `[12]` (compact, no "marks" word)
- **Subparts:** Lowercase parentheses `(a)`, `(b)`, `(c)`
- **Extraction Pattern:** `(^[1-9]\s+(?!Section)(?=[A-Z(]))`

### Paper 3 (Essays)
- **Format:** Choose 3 from 8 essay questions
- **Duration:** 1 hour 45 minutes
- **Marks:** 25 marks each (75 total)
- **Question Delimiter:** Same as Paper 2
- **Marks Notation:** `[25]` (all questions same marks)
- **Difficulty:** All "hard" (21-30 marks)

### Paper 4 (Data Response & Essays)
- **Format:** Section A: Data response (25 marks), Section B: Essay (25 marks)
- **Duration:** 2 hours 15 minutes
- **Structure:** Similar to Paper 2 but longer questions

**Tested Papers:** 16 PDFs (2018-2022)
**Extraction Accuracy:** 100% (4/4 questions from 9708_s22_qp_22.pdf)

---

## Question Delimiter Patterns

### Economics 9708 Pattern (Proven)
```regex
(^[1-9]\s+(?!Section)(?=[A-Z(]))
```

**Matches:**
- ✅ `1 Economic growth in Russia...` (number + capital letter)
- ✅ `2 (a) With the help of a production...` (number + subpart)
- ✅ `3 (a) With the help of diagrams...` (number + subpart)
- ✅ `4 (a) An economy moves from a deficit...` (number + subpart)

**Rejects (False Positives Prevented):**
- ❌ `1 hour 30 minutes` (exam duration - lowercase "hour")
- ❌ `2015 2016 2017` (table years - multi-digit)
- ❌ `12 Inflation` (graph label - multi-digit)
- ❌ `2 Section A` (section header - negative lookahead)
- ❌ `4 Section B` (section header - negative lookahead)
- ❌ `8 6 4 2 0` (graph data - no capital/paren)

**Pattern Breakdown:**
- `^` - Line start (MULTILINE mode)
- `[1-9]` - Single digit 1-9 (Economics papers have max 4 questions)
- `\s+` - One or more whitespace
- `(?!Section)` - Negative lookahead: NOT followed by "Section"
- `(?=[A-Z(])` - Positive lookahead: MUST be followed by capital letter or `(`
- `(...)` - Capturing group: preserves delimiter in `re.split()`

**Capturing Group Note:** See AD-004 for merge strategy

### Alternative Patterns (Untested, for Other Subjects)

**Pattern A: "Question N" Format**
```regex
(Question\s+\d+)
```
- Use for: English GP 8021 (likely uses formal "Question 1" style)
- Matches: "Question 1", "Question 2", "Question 10"

**Pattern B: Numbered List with Period**
```regex
(^\d+\.\s+)
```
- Use for: Some textbook-style PDFs
- Matches: "1. ", "2. ", "10. "

**Pattern C: Double-Digit Support**
```regex
(^[1-9]\d*\s+(?!Section)(?=[A-Z(]))
```
- Use for: Papers with 10+ questions (rare for A-Level)
- Matches: "1 ", "2 ", ..., "10 ", "11 "

**Testing Strategy:**
1. Download 3+ sample PDFs for subject
2. Manually inspect first 3 pages
3. Identify actual question format
4. Test pattern with `re.finditer()` before implementing
5. Validate with integration tests

---

## Marks Notation Patterns

### Economics 9708 Pattern (Proven)
```regex
\[(\d+)(?:\s+marks?)?\]
```

**Matches:**
- ✅ `[8]` (compact notation - actual Cambridge format)
- ✅ `[12]` (compact)
- ✅ `[20]` (compact)
- ✅ `[25 marks]` (verbose - backwards compatible)
- ✅ `[8 marks]` (verbose)

**Pattern Breakdown:**
- `\[` - Literal opening bracket
- `(\d+)` - Capture group: one or more digits
- `(?:\s+marks?)?` - Non-capturing group: optional " marks" or " mark"
- `\]` - Literal closing bracket

**Usage:**
```python
import re
text = "Explain inflation. [8]"
marks = re.search(r'\[(\d+)(?:\s+marks?)?\]', text)
if marks:
    print(marks.group(1))  # Output: "8"
```

### Alternative Formats (Untested)

**Parentheses Format:**
```regex
\((\d+)(?:\s+marks?)?\)
```
- Matches: `(8)`, `(12 marks)`
- Use if: Subject uses parentheses instead of brackets

**Plain Format:**
```regex
(\d+)\s+marks?
```
- Matches: `8 marks`, `12 marks`
- Use if: No brackets/parentheses (unlikely for Cambridge)

**Extraction Function:**
```python
def extract_marks(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None
```

---

## Subpart Patterns

### Lowercase Parentheses (Economics 9708)
```regex
\([a-z]\)
```

**Matches:**
- ✅ `(a) Define GDP. [8]`
- ✅ `(b) Explain inflation. [12]`
- ✅ `(c) Assess the impact. [20]`

**Aggregation Strategy:**
1. Extract all subparts with `re.finditer()`
2. Extract marks from each subpart
3. Sum marks for total question marks
4. Concatenate text with delimiter (e.g., "\n\n")

**Example:**
```python
text = "(a) Define GDP. [8]\n(b) Explain inflation. [12]"
subparts = re.finditer(r'\([a-z]\)', text)
total_marks = 8 + 12  # = 20
difficulty = "medium"  # 13-20 marks
```

### Roman Numerals (Rare)
```regex
\([ivxIVX]+\)
```
- Matches: `(i)`, `(ii)`, `(iii)`, `(iv)`
- Use if: Subject uses roman numerals for subparts

### Uppercase Parentheses (Rare)
```regex
\([A-Z]\)
```
- Matches: `(A)`, `(B)`, `(C)`
- Use if: Subject uses uppercase for main parts

**Testing:** Always check 3+ sample PDFs to confirm subpart format

---

## Header/Footer Patterns to Remove

### Cambridge Standard Headers
```regex
Cambridge International.*?Economics.*?9708
```
- Matches: "Cambridge International AS & A Level Economics 9708"
- Remove: Appears on every page

### Page Turn Indicators
```regex
\[Turn\s+over\]?
```
- Matches: "[Turn over]", "[Turn over"
- Remove: End-of-page markers

### Copyright Notices
```regex
©\s+UCLES\s+\d{4}
```
- Matches: "© UCLES 2022", "© UCLES 2021"
- Remove: Footer copyright

### Paper Code Footers
```regex
9708/\d{2}/[A-Z]/[A-Z]/\d{2}
```
- Matches: "9708/22/M/J/22", "9708/21/O/N/21"
- Remove: Paper identification codes

**Cleaning Function:**
```python
def remove_headers_footers(text: str, patterns: list[dict]) -> str:
    cleaned = text
    for pattern_dict in patterns:
        pattern = pattern_dict.get("pattern", "")
        if pattern:
            cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE | re.IGNORECASE)
    return cleaned.strip()
```

---

## Diagram Detection

### Detection Indicators (Economics 9708)
```python
indicators = ["Figure", "Diagram", "Graph", "curve", "axis"]
```

**Examples:**
- ✅ "Using Figure 1, explain the supply and demand curves."
- ✅ "The diagram shows a production possibility curve."
- ✅ "Graph 1.1 shows Russia's inflation rate."

**Detection Function:**
```python
def detect_diagram_reference(text: str, indicators: list[str]) -> bool:
    for indicator in indicators:
        if re.search(indicator, text, re.IGNORECASE):
            return True
    return False
```

**Future Enhancement:** Extract diagram description for placeholder
- Format: `[DIAGRAM: Supply and demand curves]`
- Helps students understand missing visual content

---

## Difficulty Calculation Heuristics

### Phase II Heuristic (Marks-Based)
```python
def calculate_difficulty_from_marks(marks: int) -> str:
    if marks <= 12:
        return "easy"
    elif marks <= 20:
        return "medium"
    else:  # 21-30
        return "hard"
```

**Rationale:**
- Economics 9708 mark distribution:
  - 1-12 marks: Short answer, definitions (easy)
  - 13-20 marks: Multi-part questions, application (medium)
  - 21-30 marks: Essays, evaluation (hard)

**Limitations:**
- Subject-specific (different subjects may have different scales)
- Doesn't account for historical performance
- Phase III upgrade: Use student success rates

### Phase III Enhancement (Performance-Based)
```sql
-- Calculate difficulty from historical attempts
SELECT
    question_id,
    AVG(marks_awarded / max_marks) as success_rate,
    CASE
        WHEN AVG(marks_awarded / max_marks) >= 0.7 THEN 'easy'
        WHEN AVG(marks_awarded / max_marks) >= 0.4 THEN 'medium'
        ELSE 'hard'
    END as difficulty
FROM attempted_questions
GROUP BY question_id
HAVING COUNT(*) >= 10  -- Minimum 10 attempts for reliability
```

---

## Regex Techniques for PDF Parsing

### Lookaheads (Zero-Width Assertions)

**Positive Lookahead `(?=...)`**
- Asserts: Pattern ahead must match
- Does not consume characters
- Example: `\d+(?=[A-Z])` matches "1" in "1 Economic" but not "1 hour"

**Negative Lookahead `(?!...)`**
- Asserts: Pattern ahead must NOT match
- Does not consume characters
- Example: `\d+(?!Section)` matches "1" in "1 Economic" but not "1 Section"

**Combined Example:**
```regex
^[1-9]\s+(?!Section)(?=[A-Z(])
#         ^^^^^^^^^^  ^^^^^^^^
#         NOT Section  MUST BE capital/paren
```

### Capturing vs Non-Capturing Groups

**Capturing Group `(...)`**
- Captures matched text for extraction
- Used in `re.split()` to preserve delimiters
- Access via `match.group(1)`, `match.group(2)`

**Non-Capturing Group `(?:...)`**
- Groups pattern without capturing
- Used for optional parts `(?:\s+marks?)?`
- Faster (no capture overhead)

**Example:**
```regex
\[(\d+)(?:\s+marks?)?\]
#  ^^^^  ^^^^^^^^^^^^
#  Capture  Non-capture (optional)
```

### Multiline Mode

**Flag:** `re.MULTILINE` or `(?m)`
**Effect:** `^` matches line start, `$` matches line end (not just string start/end)

**Example:**
```python
text = "Header\n1 Question one\n2 Question two"
# Without MULTILINE
re.findall(r'^\d+', text)  # Matches: ['Header starts with letter']

# With MULTILINE
re.findall(r'^\d+', text, re.MULTILINE)  # Matches: ['1', '2']
```

---

## `re.split()` Quirk: Capturing Groups

### Problem
When pattern contains capturing group, `re.split()` returns captured text in the list:

```python
text = "Header\n1 Question one\n2 Question two"

# Without capturing group
chunks = re.split(r'^\d+\s+', text, flags=re.MULTILINE)
# Result: ['Header\n', 'Question one\n', 'Question two']
# ❌ Lost "1 " and "2 "

# With capturing group
chunks = re.split(r'(^\d+\s+)', text, flags=re.MULTILINE)
# Result: ['Header\n', '1 ', 'Question one\n', '2 ', 'Question two']
# ✅ Preserves delimiters BUT alternates [header, delim1, text1, delim2, text2, ...]
```

### Solution: Auto-Merge
```python
def split_by_delimiter(text, delimiter_pattern, flags=re.MULTILINE):
    split_result = re.split(delimiter_pattern, text, flags=flags)

    # Detect alternating pattern (delimiters are short)
    if len(split_result) > 2 and all(len(chunk) < 10 for chunk in split_result[1::2]):
        # Merge [header, delim1, text1, delim2, text2] → [header, delim1+text1, delim2+text2]
        merged = [split_result[0]]
        for i in range(1, len(split_result) - 1, 2):
            merged.append(split_result[i] + split_result[i + 1])
        return merged

    return split_result
```

**Heuristic:** Delimiters (`"1 "`) are < 10 chars, question text is 100s of chars

**Documented in:** AD-004 (Capturing Group Merge Strategy)

---

## PDF Extraction Workflow

### Step 1: Analyze Sample PDFs
1. Download 10+ PDFs from subject (various years/sessions)
2. Identify paper types (MCQ, Data Response, Essays)
3. Manually inspect first 3 pages of each
4. Note:
   - Question delimiter format
   - Marks notation format
   - Subpart structure
   - Headers/footers to remove
   - False positive sources (section headers, table data, etc.)

### Step 2: Design Extraction Patterns
1. Start with broad pattern (e.g., `^\d+\s+`)
2. Test with `re.finditer()` on sample text
3. Identify false positives
4. Refine with lookaheads/lookbehinds
5. Test until false positive rate = 0%

### Step 3: Implement GenericExtractor
1. Store patterns in `subject.extraction_patterns` JSONB
2. Use `split_by_delimiter()` with capturing group
3. Parse each chunk with `_parse_question()`
4. Extract question number, marks, subparts
5. Calculate difficulty
6. Detect diagrams

### Step 4: Integration Testing
1. Create test with real PDF
2. Assert question count, marks, difficulty
3. Verify source_paper metadata
4. Check false positive rate
5. Target: 100% extraction accuracy

### Step 5: Document Patterns
1. Create ADR for pattern design decisions
2. Document false positives prevented
3. Record extraction accuracy metrics
4. Add to this skill for reuse

---

## Subject-Specific Patterns (Future)

### Mathematics 9709 (To Be Analyzed)
- **Expected Format:** Similar to Economics (numbered questions)
- **Marks:** Variable (1-10 marks per question)
- **Subparts:** Likely `(a)`, `(b)`, `(c)` or `(i)`, `(ii)`, `(iii)`
- **Diagrams:** High frequency (geometry, graphs)
- **Status:** Download sample PDFs and analyze

### Accounting 9706 (To Be Analyzed)
- **Expected Format:** Numerical questions, possibly `Q1`, `Q2` format
- **Marks:** 20-25 marks per question
- **Subparts:** Likely `(a)`, `(b)`
- **Tables:** High frequency (financial statements)
- **Status:** Download sample PDFs and analyze

### English GP 8021 (To Be Analyzed)
- **Expected Format:** Likely "Question 1", "Question 2" (formal)
- **Marks:** Variable (different sections)
- **Subparts:** Rare (essay questions)
- **Passages:** Long text excerpts to analyze
- **Status:** Download sample PDFs and analyze

**Workflow:** Apply Step 1 (Analyze Sample PDFs) for each subject before implementing

---

## Testing Strategy

### Unit Tests
- `test_split_by_delimiter()` - Validate split logic
- `test_extract_marks()` - Validate marks extraction
- `test_remove_headers_footers()` - Validate cleaning
- `test_detect_diagram_reference()` - Validate diagram detection
- `test_calculate_difficulty_from_marks()` - Validate heuristic

### Integration Tests
- `test_extract_questions_from_paper_2()` - Real PDF extraction
- `test_extract_multi_page_question()` - Multi-page handling
- `test_extract_question_with_table()` - Table extraction (pdfplumber)

### Coverage Targets
- **Extraction utilities:** >95% (currently 96%)
- **Filename parser:** >95% (currently 97%)
- **Generic extractor:** >80% (currently 63%, missing PDF I/O lines)

### Accuracy Metrics
- **False positive rate:** 0% (no non-questions extracted)
- **Extraction accuracy:** 100% (all actual questions found)
- **Marks accuracy:** 100% (all marks extracted correctly)

---

## Common Pitfalls

### Pitfall 1: Assuming Formats Without Verification
❌ **Wrong:** "Economics papers use 'Question 1' format"
✅ **Right:** Download PDFs, verify actual format is "1 Economic..."

### Pitfall 2: Not Testing False Positives
❌ **Wrong:** Pattern `^\d+\s+` matches questions
✅ **Right:** Pattern matches 19 things, only 4 are questions → refine

### Pitfall 3: Forgetting re.split() Quirk
❌ **Wrong:** Use capturing group without merge logic
✅ **Right:** Detect alternating chunks, merge delimiter+text pairs

### Pitfall 4: Hard-Coding Patterns in Code
❌ **Wrong:** `if subject == "9708": pattern = "..."`
✅ **Right:** Read pattern from `subject.extraction_patterns` JSONB

### Pitfall 5: Skipping Integration Tests
❌ **Wrong:** Unit tests pass, assume extraction works
✅ **Right:** Test with real PDFs, catch format mismatches early

---

## Related Documentation

- **ADR-002:** Generic Extraction Framework
- **ADR-003:** Economics PDF Extraction Patterns
- **ADR-004:** Capturing Group Merge Strategy
- **PHR-001:** Phase 4 PDF Extraction Implementation
- **Code:** `src/question_extractors/extraction_patterns.py`
- **Tests:** `tests/unit/test_generic_extractor.py`
- **Config:** `resources/subjects/9708/extraction_patterns.yaml`

---

## Version History

- **1.0 (2025-12-19):** Initial creation
  - Economics 9708 patterns documented
  - Regex techniques codified
  - PDF extraction workflow defined
  - Testing strategy established

---

**Skill Owner:** Backend Service Agent, System Architect
**Maintenance:** Update monthly with new subject patterns, Cambridge format changes
**Status:** Production-ready for Economics 9708, extensible to other subjects
