# Skill: A* Grading Rubrics

**Type**: Assessment Standards
**Created**: 2025-12-18
**Domain**: PhD-Level Marking
**Parent Agent**: 06-AI-Pedagogy

## Overview
A* standard grading criteria for Cambridge A-Levels (90%+ total marks required).

## Constitutional Requirement
**Principle II**: A* Standard Marking Always - PhD-level strictness, no compromises.

## A* Characteristics (All Must Be Present)

### 1. Knowledge (AO1)
- ✅ Precise, accurate definitions
- ✅ Comprehensive understanding demonstrated
- ✅ Technical terminology used correctly throughout
- ✅ No factual errors

### 2. Application (AO2)
- ✅ Highly relevant, specific examples
- ✅ Clear connection between theory and context
- ✅ Appropriate use of data/evidence
- ✅ Real-world scenarios referenced accurately

### 3. Analysis (AO3a)
- ✅ Well-developed chains of reasoning
- ✅ Cause-effect relationships explicitly stated
- ✅ Diagrams present and fully labeled
- ✅ Short-run AND long-run effects considered
- ✅ Assumptions explicitly stated
- ✅ Logical flow throughout

### 4. Evaluation (AO3b)
- ✅ Arguments on BOTH sides presented
- ✅ Relative importance/significance weighed
- ✅ "It depends on..." factors identified
- ✅ Reasoned, justified judgment (not sitting on fence)
- ✅ Alternative viewpoints acknowledged
- ✅ Stakeholder perspectives considered

## A* vs A Distinction

**A Answer** (80-89%):
- Sound knowledge, few minor errors
- Generally effective application
- Clear analysis but may lack depth
- Evaluation present but possibly one-sided

**A* Answer** (90%+):
- Flawless knowledge, zero errors
- Highly effective, precise application
- Sophisticated, multi-layered analysis
- Balanced, nuanced evaluation with reasoned judgment

## Deduction Triggers (Prevents A*)

### Automatic Deductions:
- ❌ Any factual error (-2 to -5 marks)
- ❌ Missing diagram when required (-3 to -5 marks)
- ❌ One-sided evaluation (-4 to -6 marks)
- ❌ No clear judgment/conclusion (-3 to -5 marks)
- ❌ Generic examples ("many countries") (-2 to -3 marks)
- ❌ Weak chain of reasoning (-3 to -5 marks)

## Feedback Template for Non-A*

```markdown
## Why This Score: [XX/25 - Grade A]

### Strengths:
- Clear knowledge of [concept]
- Relevant diagram showing [X]
- Sound analysis of [Y]

### Why Not A*:
- Evaluation was one-sided (only considered benefits, not costs)
- Missing consideration of [alternative factor]
- Example was generic rather than specific

### How to Reach A*:
1. Present arguments on BOTH sides before judgment
2. Consider "it depends on..." factors (e.g., elasticity, time period)
3. Use specific examples with data ("UK 2020 inflation rose to 2.5%")
4. Develop longer chains of reasoning (A causes B, which leads to C, resulting in D)
```

## Usage in Marking Engine

```python
def calculate_grade(total_marks: int, max_marks: int) -> str:
    """Calculate Cambridge A-Level grade"""
    percentage = (total_marks / max_marks) * 100

    if percentage >= 90:
        return "A*"  # Exceptional - all AOs at highest level
    elif percentage >= 80:
        return "A"   # Excellent
    elif percentage >= 70:
        return "B"   # Very Good
    # ...
```

**Usage:** 0 times (Phase III not started)
**Will Use:** Every marking task (100+ times)
**Version**: 1.0.0 | **Last Updated**: 2025-12-18
