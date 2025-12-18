# Skill: Cambridge Exam Patterns

**Type**: Domain Expertise
**Created**: 2025-12-18
**Domain**: Cambridge Assessment
**Parent Agent**: 05-Syllabus-Research

## Overview
Recognize and extract Cambridge International A-Level past paper patterns, question formats, and mark scheme structures.

## Constitutional Requirement
**Principle VIII**: Question Bank Quality Over Quantity - Every question needs verified Cambridge mark scheme.

## Cambridge Filename Format

### Pattern Recognition
```
{subject_code}_{session}_{year}_{component}_{variant}.pdf

Examples:
9708_s22_qp_12.pdf  → Economics, Summer 2022, Question Paper, Component 1, Variant 2
9708_w22_ms_12.pdf  → Economics, Winter 2022, Mark Scheme, Component 1, Variant 2
9706_s23_qp_31.pdf  → Accounting, Summer 2023, Question Paper, Component 3, Variant 1
```

### Component Codes
- `s` = Summer session (May/June)
- `w` = Winter session (October/November)
- `m` = March session
- `qp` = Question Paper
- `ms` = Mark Scheme
- `gt` = Grade Thresholds
- `er` = Examiner Report

### Parsing Pattern
```python
import re

def parse_cambridge_filename(filename: str) -> dict:
    """Parse Cambridge past paper filename"""
    pattern = r'(\d{4})_([smw])(\d{2})_(qp|ms|gt|er)_(\d{2})\.pdf'
    match = re.match(pattern, filename)

    if not match:
        raise ValueError(f"Invalid Cambridge filename: {filename}")

    subject, session, year, doc_type, component = match.groups()

    return {
        "subject_code": subject,
        "session": {"s": "summer", "w": "winter", "m": "march"}[session],
        "year": f"20{year}",
        "document_type": {
            "qp": "question_paper",
            "ms": "mark_scheme",
            "gt": "grade_thresholds",
            "er": "examiner_report"
        }[doc_type],
        "paper_number": int(component[0]),
        "variant": int(component[1])
    }
```

## Question Number Format

### Pattern Recognition
```
1(a)     → Question 1, part (a)
3(c)(i)  → Question 3, part (c), sub-part (i)
5        → Question 5 (no parts)
```

### Regex Pattern
```python
QUESTION_PATTERN = r'(\d+)(?:\(([a-z])\))?(?:\(([ivx]+)\))?'

def parse_question_number(q_num: str) -> dict:
    """Parse question number like '3(c)(ii)'"""
    match = re.match(QUESTION_PATTERN, q_num)
    return {
        "question": int(match.group(1)),
        "part": match.group(2),  # 'a', 'b', 'c', etc.
        "subpart": match.group(3)  # 'i', 'ii', 'iii', etc.
    }
```

## Mark Allocation Patterns

### Total Marks Indicator
```
[8 marks]  → Total marks for question
[Total: 12] → Alternative format
```

### Mark Scheme Format
```
1 mark for: definition of price elasticity
1 mark for: formula PED = %ΔQd / %ΔP
2 marks for: diagram showing inelastic demand
4 marks for: explanation with chain of reasoning
```

### Levels-Based Marking
```
Level 3 (7-8 marks): Thorough, perceptive analysis...
Level 2 (4-6 marks): Sound, mostly accurate...
Level 1 (1-3 marks): Limited understanding...
```

## Question Type Patterns

### Economics 9708
- **Define** (2-4 marks): "Define 'price elasticity of demand'"
- **Explain** (4-8 marks): "Explain how a subsidy affects market equilibrium"
- **Analyze** (8-12 marks): "Analyze the effect of minimum wage"
- **Discuss/Evaluate** (12-25 marks): "Discuss whether..." or "Evaluate..."

### Mark Distribution
```python
MARK_DISTRIBUTION = {
    "definition": range(2, 5),      # 2-4 marks
    "explanation": range(4, 9),     # 4-8 marks
    "analysis": range(8, 13),       # 8-12 marks
    "evaluation": range(12, 26)     # 12-25 marks
}
```

## Extraction Pattern

### From PDF to Database
```python
def extract_question(pdf_text: str, source_paper: str) -> dict:
    """Extract question from Cambridge PDF"""

    # Extract question number
    q_match = re.search(r'^(\d+(?:\([a-z]\))?(?:\([ivx]+)\))?)', pdf_text)
    question_number = q_match.group(1)

    # Extract marks
    marks_match = re.search(r'\[(\d+)\s*marks?\]', pdf_text)
    max_marks = int(marks_match.group(1)) if marks_match else None

    # Extract question text (between number and next question/page)
    text = extract_text_between(q_match.end(), next_question_start)

    return {
        "source_paper": source_paper,  # e.g., "9708_s22_qp_12"
        "question_number": question_number,
        "question_text": text,
        "max_marks": max_marks,
        "difficulty": estimate_difficulty(max_marks, text)  # Heuristic
    }
```

## Mark Scheme Extraction

### Pattern: Knowledge Points
```
1 mark for: definition of...
1 mark for: example of...
up to 2 marks for: explanation showing...
```

### Pattern: Levels Descriptor
```python
def parse_levels_marking(ms_text: str) -> dict:
    """Parse levels-based mark scheme"""
    levels = {}

    pattern = r'Level (\d+) \((\d+)-(\d+) marks?\): (.+?)(?=Level|\Z)'
    for match in re.finditer(pattern, ms_text, re.DOTALL):
        level_num = int(match.group(1))
        min_marks = int(match.group(2))
        max_marks = int(match.group(3))
        descriptor = match.group(4).strip()

        levels[f"L{level_num}"] = {
            "marks": f"{min_marks}-{max_marks}",
            "descriptor": descriptor
        }

    return {"levels": levels}
```

## Quality Checks

### Verification Checklist
- [ ] Source paper matches regex pattern (9708_s22_qp_12)
- [ ] Question number extracted correctly
- [ ] Max marks identified
- [ ] Mark scheme exists for question
- [ ] No duplicate questions in database

### Database Constraint
```python
# In SQLModel
class Question(SQLModel, table=True):
    source_paper: str = Field(
        nullable=False,
        regex=r'\d{4}_[smw]\d{2}_(qp|ms)_\d{2}'  # Validate format
    )
```

## Common Patterns by Subject

### Economics 9708
- Microeconomics: Diagrams mandatory (supply/demand, externalities)
- Macroeconomics: AD-AS diagrams, Phillips curve
- Data response: Extract from tables/graphs

### Mathematics 9709
- Pure math: Step-by-step working required
- Statistics: Hypothesis testing format
- Mechanics: Vector diagrams

## Usage in Question Bank

```python
def validate_question_source(source_paper: str) -> bool:
    """Verify question comes from real Cambridge paper"""
    # Check format
    if not re.match(r'\d{4}_[smw]\d{2}_qp_\d{2}', source_paper):
        return False

    # Could verify against known papers list
    return True
```

**Usage:** 0 times (Phase II not started)
**Will Use:** Question extraction (100+ times)
**Version**: 1.0.0 | **Last Updated**: 2025-12-18
