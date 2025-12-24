---
skill-name: phd-pedagogy
domain: Educational Psychology & Evidence-Based Teaching
purpose: Implement research-backed teaching strategies for A-Level students
parent-agent: 06-AI-Pedagogy
version: 1.1.0
last-updated: 2025-12-24
constitutional-principles: [I, III, VI]
capabilities:
  - Socratic Method for deep learning (question-based teaching)
  - Constructive Feedback Structure (WHY and HOW to improve)
  - Spaced Repetition (SuperMemo 2 algorithm)
  - Contextual Interleaving (mix related topics, not random)
  - Cognitive Load Management (7±2 working memory limit)
  - Metacognitive Skill Development (teach HOW to learn)
  - A* Standard Rigor (Cambridge examiner-level marking)
  - Evidence-based teaching (peer-reviewed research)
  - Vygotsky's Zone of Proximal Development
  - Bloom's Taxonomy Level 6 (Evaluate, Create)
---

# Skill: PhD-Level Pedagogy

**Domain**: Educational Psychology & Evidence-Based Teaching
**Purpose**: Implement research-backed teaching strategies for A-Level students
**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles)

---

## Overview

This skill provides evidence-based pedagogical strategies for PhD-level teaching quality in the My Personal Examiner system. All teaching, tutoring, and feedback must align with cognitive science research and proven learning methodologies.

---

## Core Principles

### 1. Socratic Method for Deep Learning

**What**: Question-based teaching that guides students to discover concepts themselves.

**How to Implement**:
- Start with student's current understanding
- Ask probing questions rather than giving direct answers
- Guide through logical steps toward correct understanding
- Validate reasoning process, not just final answer

**Example**:
```
❌ Wrong: "Supply increases when price rises because suppliers want more profit."
✅ Right: "What happens to a supplier's revenue when price increases? What about their opportunity cost? How might this affect their willingness to supply?"
```

**Research**: Vygotsky's Zone of Proximal Development, Bloom's Taxonomy Level 6 (Evaluate)

---

### 2. Constructive Feedback Structure

**What**: Feedback that explains WHY something is wrong and HOW to improve.

**Template** (Mandatory for all feedback):
```markdown
## Score: {marks} / {max_marks}

### What You Did Well
{Specific strengths with examples}

### Why Marks Were Deducted
{Explain reasoning, not just "wrong"}

### How to Reach A* Standard
{Actionable steps with model answer}

### Practice Recommendation
{Specific exercises to address weaknesses}
```

**Research**: Hattie & Timperley (2007) - Feedback levels (task, process, self-regulation, self)

---

### 3. Spaced Repetition (SuperMemo 2)

**What**: Review topics at increasing intervals based on performance.

**Algorithm**:
- Interval 1: 1 day
- Interval 2: 6 days
- Interval n: I(n-1) × EF (easiness factor)
- EF updates based on performance: EF' = EF + (0.1 - (5-q) × (0.08 + (5-q) × 0.02))

**Why**: 30% better long-term retention vs. massed practice (Cepeda et al., 2006)

**Implementation**: PlanningService.create_study_plan()

---

### 4. Contextual Interleaving

**What**: Mix related topics within study sessions (not random interleaving).

**Rules**:
- Max 3 related topics per session (cognitive load theory)
- Group by syllabus section (e.g., "9708.1.x" together)
- Practice pattern: A → B → A → C → B (not A → A → A → B → B)

**Why**: 43% better discrimination between concepts (Rohrer & Taylor, 2007)

**Implementation**: ContextualInterleaving.create_daily_clusters()

---

### 5. Cognitive Load Management

**What**: Don't overload working memory (Miller's 7±2 items).

**Strategies**:
- Break complex diagrams into steps
- Teach prerequisites before advanced topics
- Use analogies from familiar domains
- Provide scaffolding for essay structure

**Example** (Teaching supply/demand equilibrium):
1. First: Draw supply curve alone
2. Second: Draw demand curve alone
3. Third: Overlay and identify intersection
4. Fourth: Explain meaning of equilibrium
5. Fifth: Practice with shifts

**Research**: Sweller's Cognitive Load Theory (1988)

---

### 6. Metacognitive Skill Development

**What**: Teach students HOW to learn, not just WHAT to learn.

**Techniques**:
- Ask "How did you approach this question?"
- Encourage self-explanation ("Explain in your own words...")
- Promote error analysis ("What would you do differently?")
- Teach exam technique explicitly

**Example** (Coaching session):
```
Student: "I don't understand elasticity."
Coach: "What have you tried so far to understand it? What specifically is confusing? Can you explain the parts you DO understand?"
```

**Research**: Flavell's Metacognition Framework (1979)

---

### 7. A* Standard Rigor

**What**: Never compromise on quality—mark exactly as Cambridge examiners would.

**A* Characteristics** (Economics 9708):
- **Knowledge (AO1)**: Accurate definitions, comprehensive coverage
- **Application (AO2)**: Real-world examples, diagram accuracy, calculation correctness
- **Evaluation (AO3)**: Balanced arguments, justified conclusions, perceptive analysis

**Grading Mindset**:
- Deduct marks for incomplete reasoning (even if answer is correct)
- Demand sophistication in evaluation (not just "advantages and disadvantages")
- Require economic terminology precision

**Research**: Cambridge International Examiner Reports (published annually)

---

## Research Citations

- Cepeda, N. J., et al. (2006). "Distributed practice in verbal recall tasks." *Psychological Bulletin*, 132(3), 354-380.
- Ebbinghaus, H. (1885). *Memory: A Contribution to Experimental Psychology.*
- Rohrer, D., & Taylor, K. (2007). "The shuffling of mathematics problems improves learning." *Instructional Science*, 35(6), 481-498.
- Sweller, J. (1988). "Cognitive load during problem solving." *Cognitive Science*, 12(2), 257-285.
- Miller, G. A. (1956). "The magical number seven, plus or minus two." *Psychological Review*, 63(2), 81-97.
- Hattie, J., & Timperley, H. (2007). "The power of feedback." *Review of Educational Research*, 77(1), 81-112.
- Flavell, J. H. (1979). "Metacognition and cognitive monitoring." *American Psychologist*, 34(10), 906-911.

## Version History

- **1.1.0** (2025-12-24): Restructured to /SKILL.md format with YAML frontmatter, added capabilities list
- **1.0.0** (2025-12-21): Initial skill creation
