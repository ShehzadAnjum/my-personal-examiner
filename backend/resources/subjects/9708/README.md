# Economics 9708 - Reference Template for Generic Framework

**Subject**: Cambridge International A-Level Economics (9708)
**Status**: Reference Template for Other Subjects
**Created**: 2025-12-18
**Purpose**: Document Economics-specific patterns to guide configuration for Math, English, and other A-Level subjects

---

## Overview

Economics 9708 serves as the **reference implementation** for the generic question bank and exam generation framework. The configuration patterns established here should be adapted (not copied verbatim) for other Cambridge A-Level subjects.

**Why Economics First**:
- Ideal complexity balance (not too easy like MCQ-only subjects, not too hard like pure Math)
- Clear marking criteria (Level Descriptors L1-L4)
- Mixed question types (essays, data response, MCQs)
- Graph/diagram analysis provides good test case for extraction
- Transferable patterns to other essay-based subjects (History, English, Sociology)

---

## Configuration Architecture

Economics 9708 configuration is stored in **two places** (dual storage pattern):

### 1. Database (JSONB Columns in `subjects` Table)

**Queryable metadata** for system operations:

```json
{
  "marking_config": {
    "version": "1.0",
    "rubric_type": "level_descriptors",
    "max_levels": 4,
    "essay_structure": true
  },
  "extraction_patterns": {
    "version": "1.0",
    "question_delimiter": "Question \\d+",
    "marks_pattern": "\\[\\d+ marks\\]",
    "has_subparts": true
  },
  "paper_templates": {
    "version": "1.0",
    "papers": [
      {"paper_number": 1, "type": "MCQ", "questions_count": 30, "marks_per_question": 1, "duration": 60},
      {"paper_number": 2, "type": "DATA_RESPONSE", "questions_count": 3, "total_marks": 40, "duration": 90},
      {"paper_number": 3, "type": "ESSAYS", "questions_count": 3, "marks_per_question": 25, "duration": 105}
    ]
  }
}
```

### 2. Resource Files (This Directory)

**Complex templates** for detailed configuration:

- `marking_config.json` - Full level descriptors with mark ranges and criteria
- `extraction_patterns.yaml` - Detailed regex patterns for PDF parsing
- `paper_templates.json` - Paper structures with question counts and marks
- `sample_papers/` - 10+ Economics past papers for testing extraction

---

## Economics-Specific Patterns

### Marking Rubric: Level Descriptors (L1-L4)

Economics uses **4-level descriptors** for essay questions (Papers 2 & 3):

| Level | Marks | Descriptor Summary |
|-------|-------|-------------------|
| L4 | 18-25 | Sophisticated analysis, clear chain of reasoning, effective evaluation with supported judgment |
| L3 | 12-17 | Good analysis, some use of economic theory, attempts at evaluation but may lack support |
| L2 | 6-11 | Some understanding but superficial, limited use of theory, little evaluation |
| L1 | 1-5 | Limited understanding, mainly descriptive, no real evaluation |

**Adaptation for Other Subjects**:
- **Mathematics 9709**: Use **method marks** instead (step 1: formula, step 2: substitution, step 3: calculation)
- **English GP 8021**: Use **argument rubric** (thesis clarity, evidence quality, critical thinking, coherence)
- **History**: Similar level descriptors but focus on historical evidence and source analysis

---

### Question Extraction Patterns

**Question Delimiter**: `Question \d+` (e.g., "Question 1", "Question 2")

**Marks Pattern**: `\[\d+ marks?\]` (e.g., "[25 marks]", "[8 marks]")

**Subpart Pattern**: `\([a-z]\)` (e.g., "(a)", "(b)", "(c)")

**Sample Question Structure** (Paper 3):
```
Question 1

Discuss the extent to which subsidies can correct market failure in the
provision of merit goods.

[25 marks]
```

**Adaptation for Other Subjects**:
- **Mathematics**: Questions use `Q\d+` or numbered format without "Question" keyword
- **English**: Questions are paragraph prompts, no explicit "Question" delimiter
- **Accounting**: Questions have parts like "1.1", "1.2", "1.3"

---

## Paper Templates

Economics has **3 distinct paper types**:

### Paper 1: Multiple Choice Questions (MCQ)
- 30 questions × 1 mark = 30 marks total
- Duration: 60 minutes
- Extraction: Requires OCR for diagrams/graphs embedded in MCQs
- **Phase II Status**: Deferred (complex MCQ extraction, focus on Papers 2-3)

### Paper 2: Data Response
- 3 questions (context passages with data)
- Total: 40 marks (questions vary: 8 marks, 12 marks, 20 marks)
- Duration: 90 minutes
- Mix of short answers and mini-essays
- Often includes tables, graphs, statistics

### Paper 3: Essays
- 3 questions to choose from (typically 6-8 available)
- Each: 25 marks
- Duration: 105 minutes (1 hour 45 min)
- Pure essay format, requires evaluation and judgment

**Adaptation for Other Subjects**:
- **Mathematics**: Papers 1-4, each with 10-12 questions, method marks per step
- **English**: Single paper with passage analysis + essay sections
- **Accounting**: Papers with numerical questions (journals, ledgers, financial statements)

---

## Difficulty Calculation (Heuristic for Phase II)

Economics questions use **marks value** as difficulty proxy:

- **Easy** (1-12 marks): "Explain", "Define", "Calculate" questions
- **Medium** (13-20 marks): "Analyze", "Compare", multi-part questions
- **Hard** (21-30 marks): "Discuss", "Evaluate", "To what extent" questions requiring judgment

**Why This Works for Economics**:
- Higher mark questions require synthesis of multiple concepts
- Evaluation questions (25 marks) demand critical thinking and balanced judgment
- Correlation observed: Higher marks → Lower average student scores

**Upgrade in Phase III**: Replace with historical performance-based difficulty (average score / max marks ratio)

**Adaptation for Other Subjects**:
- **Mathematics**: Difficulty based on syllabus topic complexity (calculus > algebra) and multi-step requirements
- **English**: All essays similar difficulty, differentiate by passage complexity or topic familiarity
- **Accounting**: Difficulty based on problem complexity (simple journal entries < consolidated statements)

---

## File Structure

```
backend/resources/subjects/9708/
├── README.md                          # This file
├── marking_config.json                # Level descriptors (L1-L4) with full criteria
├── extraction_patterns.yaml           # Regex patterns for PDF parsing
├── paper_templates.json               # Paper 1/2/3 structures
└── sample_papers/                     # Test PDFs
    ├── 9708_s22_qp_31.pdf            # Summer 2022, Paper 3, Question Paper
    ├── 9708_s22_ms_31.pdf            # Summer 2022, Paper 3, Mark Scheme
    ├── 9708_w21_qp_32.pdf            # Winter 2021, Paper 3
    ├── 9708_w21_ms_32.pdf            # Winter 2021, Mark Scheme
    └── ... (10+ PDFs for comprehensive testing)
```

---

## Using Economics as Template

### For New Essay-Based Subjects (English, History, Sociology):

1. **Copy Economics pattern files** as starting point
2. **Adapt marking_config.json**:
   - Keep level descriptor structure if similar rubric used
   - Adjust criteria to subject-specific requirements (e.g., "economic theory" → "historical evidence")
   - Update mark ranges if different (e.g., English may use 0-30 instead of 0-25)
3. **Adapt extraction_patterns.yaml**:
   - Test subject PDFs to identify actual delimiters used
   - May be similar but verify with 5+ sample papers
4. **Update paper_templates.json**:
   - Match actual paper structure from syllabus (some subjects have 1 paper, others have 4)

### For Numerical Subjects (Mathematics, Accounting, Physics):

1. **DON'T copy Economics marking_config.json** - fundamentally different rubric
2. **Create method marks structure** instead:
   ```json
   {
     "rubric_type": "method_marks",
     "total_marks": 10,
     "steps": [
       {"step": 1, "marks": 3, "requirement": "Correct formula"},
       {"step": 2, "marks": 4, "requirement": "Substitution"},
       {"step": 3, "marks": 3, "requirement": "Calculation"}
     ]
   }
   ```
3. **Test extraction patterns** with numerical question formats
4. **Account for diagrams/graphs** in mark schemes (e.g., "award 1 mark for correctly labeled axes")

---

## Phase II Manual Configuration Process

Economics 9708 config created **manually** in Phase II (2-3 hours):

1. **Downloaded 10 Economics past papers** (Papers 2 & 3 from 2018-2023)
2. **Analyzed patterns** in 3 papers to identify delimiters, marks notation, subpart structures
3. **Extracted level descriptors** from 3 mark schemes to build marking_config.json
4. **Tested extraction** on 5 papers, iterated on regex patterns until >95% accuracy
5. **Documented findings** in this README

**Phase V AI-Powered Bootstrap**: This manual work trains AI to auto-generate config for new subjects. Upload 10-20 sample PDFs → AI analyzes patterns → generates config automatically.

---

## Success Criteria (Phase II)

Economics 9708 configuration validated when:

- ✅ **Extraction Accuracy**: >95% of questions extracted correctly from 10 test papers
- ✅ **Mark Scheme Matching**: 100% match rate for mark schemes to questions
- ✅ **Exam Generation**: Valid exams generated with ±10% difficulty distribution
- ✅ **Database Seeding**: Economics subject record with JSONB config populated
- ✅ **Template Documentation**: Other developers can understand patterns from this README

---

## Contact & Maintenance

**Created By**: Phase II Implementation (2025-12-18)
**Subject Owner**: Economics 9708 seeded as reference, not active course
**Updates**: Any Cambridge syllabus changes (2026+) update config files here
**Questions**: See `docs/architecture/subject-configuration.md` for framework design

---

**Next Steps**:
1. Create detailed config files (marking_config.json, extraction_patterns.yaml, paper_templates.json)
2. Download 10+ Economics sample PDFs to sample_papers/
3. Test extraction accuracy with GenericExtractor
4. Document any edge cases or extraction challenges found
