---
name: resource-bank-content
description: Resource Bank explanation content schema and generation patterns. Use when generating or regenerating topic explanations for the Resource Bank. Enforces 9-component structure with consistent formatting. CRITICAL - Definition field must contain ONLY definition text (no topic code prefix).
---

# Skill: Resource Bank Content Generation

**Domain**: Educational Content Generation
**Purpose**: Ensure consistent, schema-compliant explanation generation for Resource Bank
**Created**: 2025-12-26
**Feature**: 006-resource-bank

---

## Overview

This skill defines the **exact schema** for Resource Bank topic explanations. ALL content generation (initial v1 or section regeneration) MUST follow this structure to ensure consistency across the platform.

---

## 9-Component Explanation Schema

Every explanation MUST contain ALL 9 components in this exact structure:

### Component 1: Definition

```json
{
  "definition": "[Clear, exam-worthy definition in 2-3 sentences]"
}
```

**Requirements**:
- Contains ONLY the definition text (NO topic code prefix, NO topic name)
- Topic code and name are stored in separate fields (syllabus_code, concept_name)
- Definition must be suitable for direct use in exam answers
- 2-3 sentences maximum
- Use precise economic terminology

**Example**:
```
"Fiscal policy refers to the use of government spending and taxation to influence aggregate demand and achieve macroeconomic objectives. It is a demand-side policy implemented through the government's budget decisions."
```

**WRONG** (do NOT include topic code in definition):
```
"9708.5.1 Fiscal Policy:\n\nFiscal policy refers to..."
```

---

### Component 2: Key Terms

```json
{
  "key_terms": [
    {"term": "Term name", "definition": "Clear definition"},
    {"term": "Term name", "definition": "Clear definition"}
  ]
}
```

**Requirements**:
- 4-6 key terms related to the topic
- Each term has a concise definition (1-2 sentences)
- Include technical economic vocabulary

---

### Component 3: Core Principles (concept_explanation)

```json
{
  "concept_explanation": "[3-4 paragraphs explaining the theory]"
}
```

**Requirements**:
- 3-4 substantial paragraphs
- Explain HOW the concept works
- Explain WHY it matters
- Include theoretical frameworks where applicable
- Use clear, academic language

---

### Component 4: Real-World Examples

```json
{
  "real_world_examples": [
    {
      "title": "Descriptive title",
      "scenario": "Specific real-world context with data/dates",
      "analysis": "Economic analysis connecting to theory"
    }
  ]
}
```

**Requirements**:
- 3 distinct real-world examples
- Include specific countries, dates, or data points
- Analysis must connect scenario to theory
- Use current/recent examples where possible

---

### Component 5: Visual Aids (diagrams)

```json
{
  "diagrams": [
    {
      "type": "flowchart|graph|sequence|suggested",
      "title": "Clear title",
      "description": "What this shows and how to interpret it",
      "mermaid_code": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
    }
  ]
}
```

**Requirements**:
- 2-3 visual aids
- Include valid Mermaid code where applicable
- Types: flowchart, graph, sequence for code-based; suggested for non-code
- Description must explain interpretation

**Mermaid Patterns**:
- Supply/Demand: Use `graph LR` with nodes for curves
- Process flows: Use `flowchart TD`
- Cause-effect: Use `flowchart LR`
- Cycles: Use `flowchart TD` with circular connections

---

### Component 6: Worked Examples

```json
{
  "worked_examples": [
    {
      "problem": "Full exam-style question",
      "step_by_step_solution": "Step 1: ...\nStep 2: ...\nStep 3: ...",
      "marks_breakdown": "Step 1 (2 marks): ...\nStep 2 (3 marks): ..."
    }
  ]
}
```

**Requirements**:
- 2 worked examples
- Match Cambridge exam format
- Show clear step-by-step working
- Include marks breakdown aligned to Cambridge criteria

---

### Component 7: Common Misconceptions

```json
{
  "common_misconceptions": [
    {
      "misconception": "What students commonly get wrong",
      "why_wrong": "Explanation of why this is incorrect",
      "correct_understanding": "The accurate understanding"
    }
  ]
}
```

**Requirements**:
- 3 common misconceptions
- Based on actual examiner reports where possible
- Explain WHY the misconception occurs
- Provide clear correction

---

### Component 8: Practice Problems

```json
{
  "practice_questions": [
    {
      "question": "Full question text",
      "difficulty": "easy|medium|hard",
      "answer_outline": "Key points for model answer",
      "marks": 4
    }
  ]
}
```

**Requirements**:
- 3 practice problems: 1 easy (2-4 marks), 1 medium (4-8 marks), 1 hard (8-15 marks)
- Match Cambridge question styles
- Answer outline includes mark allocation
- Cover AO1, AO2, and AO3 skills

---

### Component 9: Related Concepts

```json
{
  "related_topics": ["Topic 1", "Topic 2", "Topic 3"]
}
```

**Requirements**:
- 4-6 related syllabus topics
- Use syllabus codes where known (e.g., "9708.4.3 Monetary Policy")
- Include both prerequisites and follow-on topics

---

## Section Regeneration Prompts

When regenerating a single section, include this context:

```
You are regenerating the {section_name} section for:
**Topic Code**: {code}
**Topic Title**: {title}
**Full Description**: {description}

The output MUST conform to this exact schema:
{schema_for_section}

CRITICAL REQUIREMENTS:
- Definition field: Contains ONLY definition text (NO topic code prefix)
- Practice problems: MUST include easy, medium, AND hard difficulty levels
- Diagrams: MUST include actual Mermaid code (NOT type "suggested")
- All fields must match the exact schema structure
```

---

## Quality Validation

Before returning generated content, validate:

1. **Definition**: Contains ONLY definition text (NO topic code prefix, NO topic name)
2. **Key Terms**: Has 4+ terms with definitions
3. **Core Principles**: Has 3+ paragraphs
4. **Examples**: Has 3 examples with title/scenario/analysis structure
5. **Visual Aids**: Has 2+ aids with actual mermaid_code (NOT type "suggested")
6. **Worked Examples**: Has 2 examples with marks breakdown
7. **Misconceptions**: Has 3 items with why_wrong field
8. **Practice Problems**: Has EXACTLY 3 problems: 1 easy, 1 medium, 1 hard
9. **Related Topics**: Has 4+ related concepts

---

## Usage

**Full Explanation Generation**:
```python
from src.ai_integration.prompts import RESOURCE_BANK_FULL_PROMPT
# Use RESOURCE_BANK_FULL_PROMPT with topic context
```

**Section Regeneration**:
```python
from src.services.resource_service import regenerate_section_with_llm
# Pass section_name and explanation_id
# Service includes schema requirements in prompt
```

---

## Version History

- **1.1.0** (2025-12-26): CRITICAL FIX - Definition field must contain ONLY definition text (no topic code prefix)
- **1.0.0** (2025-12-26): Initial skill creation with 9-component schema
