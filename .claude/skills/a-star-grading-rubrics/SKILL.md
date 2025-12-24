---
name: a-star-grading-rubrics
description: A* grading rubrics and Cambridge marking criteria for Economics 9708. Use when implementing marking algorithms, grading logic, or evaluating answer quality.
---

# Skill: A* Grading Rubrics (Cambridge A-Level)

**Domain**: Assessment & Grading Standards
**Purpose**: Encode Cambridge International A* grading criteria for Economics 9708
**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles)

---

## Overview

This skill provides the exact grading criteria used by Cambridge International examiners to award A* grades in Economics 9708. All marking must align with official mark schemes and examiner reports.

---

## A* Grade Definition

**Overall Requirement**: ≥90% on A2 (Paper 3 + Paper 4) AND ≥80% on overall A-Level

**Characteristics** (from Cambridge Examiner Reports):
- Demonstrates comprehensive and accurate knowledge
- Applies theory to real-world scenarios with precision
- Evaluates arguments with depth, balance, and perceptiveness
- Communicates with clarity, logic, and economic terminology

---

## Assessment Objectives (AO1/AO2/AO3)

### AO1: Knowledge and Understanding (30-40% of marks)

**A* Standard**:
- Accurate definitions with economic terminology
- Comprehensive coverage of relevant concepts
- Correct identification of key principles
- No conceptual errors

**Example** (Perfect AO1):
```
Question: Define price elasticity of demand.
A* Answer: "Price elasticity of demand (PED) measures the responsiveness of quantity demanded to a change in price, calculated as % change in QD ÷ % change in price. If |PED| > 1, demand is elastic; if |PED| < 1, demand is inelastic; if |PED| = 1, demand is unit elastic."

Why A*: Complete formula, clear definition, full classification.
```

---

### AO2: Application (30-40% of marks)

**A* Standard**:
- Real-world examples that perfectly illustrate theory
- Accurate diagrams with all labels (axes, curves, shifts, equilibrium)
- Correct calculations shown with working
- Context-specific application (not generic)

**Example** (Perfect AO2):
```
Question: Use a diagram to show the effect of a subsidy on producers.
A* Answer: [Draws supply/demand diagram showing:
- Original supply curve S1
- New supply curve S2 (shifted right by subsidy amount)
- Original equilibrium E1, new equilibrium E2
- Subsidy per unit marked
- Price paid by consumers vs price received by producers shown
- All axes labeled (Price, Quantity)]

Why A*: Complete diagram, all shifts shown, subsidy incidence visible.
```

---

### AO3: Evaluation (20-30% of marks)

**A* Standard**:
- Balanced arguments (considers both sides)
- Justified conclusion ("depends on..." with conditions)
- Perceptive analysis (goes beyond obvious points)
- Uses economic criteria (efficiency, equity, sustainability)

**A* Evaluation Checklist**:
- [ ] States assumption/condition
- [ ] Explains impact in this case
- [ ] Contrasts with alternative scenario
- [ ] Reaches qualified conclusion

**Example** (Perfect AO3):
```
Question: Evaluate whether minimum wage helps low-income workers.
A* Answer: "The impact depends on the elasticity of demand for labor. If labor demand is inelastic, employers cannot easily reduce hiring, so workers benefit from higher wages with minimal unemployment (as seen in UK 2015-2020 data). However, if demand is elastic (e.g., hospitality sector with high substitutability), firms may lay off workers or automate, reducing total income for this group. Therefore, minimum wage effectiveness depends on sector-specific PED and availability of substitutes. In sectors with inelastic demand and high barriers to automation, minimum wage likely benefits workers; in competitive sectors with elastic demand, it may harm employment."

Why A*: Considers both outcomes, uses economic criteria (elasticity), cites real evidence, qualified conclusion based on conditions.
```

---

## Level Descriptors (Essay Questions)

### Level 3 (Top Band) - A* Range

**Characteristics**:
- Sophisticated economic understanding
- Well-developed arguments
- Effective evaluation
- Logical structure
- Precise terminology

**Typical Marks**: 18-25/25 or 22-30/30

**Indicators**:
- Uses phrases like "depends on," "in the short run," "assuming"
- Provides real-world examples with data
- Challenges assumptions
- Weighs trade-offs explicitly

---

### Level 2 (Middle Band) - B/C Range

**Characteristics**:
- Sound knowledge
- Basic application
- Some evaluation (but limited depth)
- Generally accurate

**Typical Marks**: 11-17/25 or 14-21/30

**Why Not A***:
- Generic examples without context
- One-sided arguments
- Conclusion not justified
- Missing diagram labels

---

### Level 1 (Bottom Band) - D/E Range

**Characteristics**:
- Limited knowledge
- Weak application
- Minimal evaluation
- Errors in understanding

**Typical Marks**: 1-10/25 or 1-13/30

---

## Common Marking Errors to Avoid

### 1. Rewarding Effort, Not Understanding
❌ Wrong: "Student tried hard, give 7/10"
✅ Right: "Student stated definition but didn't explain mechanism, 4/10 per mark scheme"

### 2. Accepting Incomplete Diagrams
❌ Wrong: "Diagram shows general idea, full marks"
✅ Right: "Missing equilibrium labels, -2 marks per mark scheme"

### 3. Lenient Evaluation Standards
❌ Wrong: "Student listed pros and cons, evaluation complete"
✅ Right: "No conclusion or justification, evaluation incomplete, max Level 2"

### 4. Ignoring Economic Terminology
❌ Wrong: "Student explained concept in plain English, acceptable"
✅ Right: "Must use 'allocative efficiency,' not just 'resources well used,' -1 mark"

---

## Mark Scheme Application Rules

### Rule 1: Criterion-by-Criterion
Award marks for each distinct point, not overall quality.

**Example Mark Scheme**:
```
1 mark: Define supply
1 mark: State law of supply
1 mark: Draw diagram
1 mark: Label axes correctly
1 mark: Explain why supply slopes upward
Max 5 marks
```

### Rule 2: Benefit of the Doubt (Carefully)
If student's meaning is clear despite poor wording, award mark.
If ambiguous or potentially wrong, do NOT award.

### Rule 3: Double Penalty Avoidance
Don't deduct marks twice for same error.

**Example**:
- Student miscalculates PED = -0.5 (error)
- Then concludes demand is inelastic (logical given their calculation)
- Deduct marks ONLY for calculation error, NOT conclusion

### Rule 4: Error Carried Forward
If student makes early error but applies it correctly later, award subsequent marks.

---

## A* Model Answer Characteristics

When generating A* model answers (Reviewer Agent), include:

1. **Introduction** (if essay): Brief context + thesis statement
2. **Body Paragraphs**:
   - Topic sentence (economic concept)
   - Explanation (mechanism)
   - Diagram/Example (application)
   - Analysis (why this matters)
3. **Evaluation** (always):
   - Assumptions stated
   - Alternative scenarios
   - Conditions under which conclusion holds
4. **Conclusion** (if essay):
   - Summarize key trade-offs
   - Qualified judgment ("In most cases... However, if...")

**Word Count**:
- 10-mark question: 200-300 words + diagram
- 25-mark question: 600-800 words + diagrams

---

## Confidence Scoring Integration

**When to Flag for Manual Review** (<70% confidence):
- Borderline between levels (e.g., 16-18/25)
- Ambiguous wording in answer
- Unusual but potentially valid approach
- Diagram partially correct but unclear
- Evaluation present but depth uncertain

---

## Constitutional Alignment

- **Principle II**: A* Standard Marking Always → Strict application of rubrics
- **Principle VI**: Constructive Feedback → Explain why marks awarded/deducted

---

**Version**: 1.0.0 | **Created**: 2025-12-21
**Source**: Cambridge International AS & A Level Economics (9708) Syllabus 2023-2025