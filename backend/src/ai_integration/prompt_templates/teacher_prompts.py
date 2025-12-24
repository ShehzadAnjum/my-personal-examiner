"""
Teacher Prompts

PhD-level concept explanation prompts for the Teacher Agent.

Constitutional Compliance:
- Principle III: PhD-level pedagogy (evidence-based teaching strategies)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
- Principle VI: Constructive feedback (clear explanations with examples)
"""

from typing import Dict, List, Optional, Any


class TeacherPrompts:
    """
    Teacher Agent prompts for concept explanation.

    Provides PhD-level explanations with:
    - Clear, precise definitions
    - Real-world examples with data
    - Visual aids (diagrams, graphs)
    - Worked examples
    - Practice problems
    - Common misconceptions
    """

    SYSTEM_PROMPT = """You are a PhD-level Economics teacher with 20+ years of experience teaching Cambridge International A-Level Economics 9708.

Your teaching philosophy:
- **Conceptual Clarity**: Build understanding from first principles
- **Real-World Application**: Every concept tied to concrete examples
- **Active Learning**: Students learn by doing, not just listening
- **Misconception Prevention**: Address common errors proactively
- **Visual Thinking**: Use diagrams and graphs to aid understanding

Constitutional Principles:
- Subject Accuracy is Non-Negotiable: All content MUST match Cambridge syllabus exactly
- PhD-Level Strictness: Zero tolerance for imprecision or vague explanations
- Constructive Feedback: Always explain WHY concepts matter and HOW they connect

Teaching Standards (A* Level):
- **Definitions**: Precise, using exact economic terminology
- **Examples**: Specific, with data and citations (e.g., "UK inflation in 2022 was 9.1%")
- **Diagrams**: Clear labels, axes, equilibrium points annotated
- **Application**: Explicitly connect theory to Cambridge exam questions

You MUST:
1. Define concepts precisely with key terms highlighted
2. Provide at least 2 real-world examples with specific data
3. Include visual aids (Mermaid diagrams or ASCII art where appropriate)
4. Give worked examples showing step-by-step reasoning
5. Identify common misconceptions students make
6. Provide 3-5 practice problems with answers

NEVER:
- Give vague definitions ("demand is what people want" ❌)
- Use generic examples without data ("some goods" ❌)
- Skip intermediate steps in worked examples
- Assume prior knowledge not in syllabus prerequisites
"""

    @staticmethod
    def explain_concept_prompt(
        syllabus_code: str,
        concept_name: str,
        syllabus_description: str,
        learning_outcomes: List[str],
        student_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate prompt for explaining a specific syllabus concept.

        Args:
            syllabus_code: Syllabus point code (e.g., "9708.2.1")
            concept_name: Name of concept (e.g., "Price Elasticity of Demand")
            syllabus_description: Official syllabus description
            learning_outcomes: List of learning outcomes from syllabus
            student_context: Optional dict with student's progress, weaknesses, etc.

        Returns:
            str: Formatted prompt for Teacher Agent
        """
        context_section = ""
        if student_context:
            weaknesses = student_context.get("weaknesses", [])
            if weaknesses:
                context_section = f"""
**Student Context**:
This student has struggled with: {', '.join(weaknesses)}
Please pay extra attention to addressing these areas in your explanation.
"""

        learning_outcomes_text = "\n".join(f"  - {outcome}" for outcome in learning_outcomes)

        return f"""Explain the following Economics 9708 concept to a Cambridge A-Level student.

**SYLLABUS POINT**: {syllabus_code}
**CONCEPT**: {concept_name}

**OFFICIAL SYLLABUS DESCRIPTION**:
{syllabus_description}

**LEARNING OUTCOMES** (student must be able to):
{learning_outcomes_text}
{context_section}

**YOUR TASK**:
Provide a comprehensive, PhD-level explanation of "{concept_name}" that enables the student to:
1. Define the concept precisely using exact economic terminology
2. Apply the concept to real-world scenarios with specific examples
3. Analyze the concept using appropriate diagrams/graphs
4. Evaluate the concept's significance and limitations

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "key_terms": [
    {{
      "term": "<Economic term>",
      "definition": "<Precise definition of the term>"
    }},
    {{...}}
    (REQUIRED: Provide at least 3 key terms with full definitions)
  ],
  "definition": "<Comprehensive definition of the main concept using exact economic terminology>",
  "explanation": {{
    "core_principles": "<Fundamental principles explained step-by-step>",
    "why_it_matters": "<Relevance to economics and real-world policy>",
    "theoretical_foundation": "<Economic theory underpinning this concept>"
  }},
  "examples": [
    {{
      "title": "<Example title>",
      "scenario": "<Real-world scenario with specific data>",
      "analysis": "<How the concept applies to this scenario>",
      "data_source": "<Citation if available>"
    }},
    {{...}} (at least 2 examples)
  ],
  "visual_aids": [
    {{
      "type": "diagram|graph|table",
      "title": "<Diagram title>",
      "description": "<What the diagram shows>",
      "mermaid_code": "<Mermaid.js code if diagram>",
      "ascii_art": "<ASCII art if graph>"
    }}
  ],
  "worked_examples": [
    {{
      "problem": "<Cambridge-style exam question>",
      "step_by_step_solution": "<Detailed solution with reasoning>",
      "marks_breakdown": "<How marks would be awarded>"
    }}
  ],
  "common_misconceptions": [
    {{
      "misconception": "<What students often think>",
      "why_wrong": "<Why this is incorrect>",
      "correct_understanding": "<What they should know instead>"
    }}
  ],
  "practice_problems": [
    {{
      "question": "<Practice question>",
      "difficulty": "easy|medium|hard",
      "answer_outline": "<Key points for answer>",
      "marks": <integer>
    }},
    {{...}},
    {{...}}
    (REQUIRED: Provide exactly 3-5 practice problems, ranging from easy to hard difficulty)
  ],
  "connections": {{
    "related_concepts": ["concept1", "concept2", ...],
    "exam_question_types": ["type1", "type2", ...],
    "syllabus_links": ["9708.x.y", "9708.x.z", ...]
  }}
}}

**IMPORTANT - MERMAID DIAGRAM EXAMPLES**:

For ECONOMIC GRAPHS (supply/demand, cost curves, etc.), use Mermaid XY charts:

Example 1 - Supply and Demand Curves:
```
---
config:
  xyChart:
    width: 600
    height: 400
  themeVariables:
    xyChart:
      backgroundColor: "transparent"
---
xychart-beta
    title "Supply and Demand"
    x-axis "Quantity" 0 --> 100
    y-axis "Price ($)" 0 --> 50
    line "Demand" [45, 40, 35, 30, 25, 20, 15, 10, 5]
    line "Supply" [5, 10, 15, 20, 25, 30, 35, 40, 45]
```

Example 2 - Production Possibility Frontier:
```
xychart-beta
    title "Production Possibility Frontier"
    x-axis "Goods A" 0 --> 100
    y-axis "Goods B" 0 --> 100
    line "PPF" [100, 90, 75, 55, 30, 0]
```

For FLOWCHARTS/DIAGRAMS (decision trees, market structures), use graph syntax:
```
graph LR
    A[Perfect Competition] --> B{{Many Firms?}}
    B -->|Yes| C[Price Taker]
    B -->|No| D[Monopoly/Oligopoly]
    C --> E[Allocative Efficiency]
```

CRITICAL RULES:
- For XY charts: Use "xychart-beta" and provide data arrays
- For supply curves: Use ASCENDING data (e.g., [5, 10, 15, 20, 25])
- For demand curves: Use DESCENDING data (e.g., [45, 40, 35, 30, 25])
- Always include x-axis and y-axis labels with ranges
- Keep data arrays consistent in length (recommended: 9 data points)

Explain NOW with PhD-level precision and clarity:"""

    @staticmethod
    def clarify_concept_prompt(
        concept_name: str,
        student_question: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate prompt for clarifying student confusion about a concept.

        Args:
            concept_name: Name of concept student is confused about
            student_question: Student's specific question
            context: Optional context from previous explanation

        Returns:
            str: Formatted prompt for Teacher Agent
        """
        context_section = ""
        if context:
            context_section = f"""
**PREVIOUS EXPLANATION CONTEXT**:
{context}
"""

        return f"""A student is confused about "{concept_name}" and needs clarification.

**STUDENT'S QUESTION**:
"{student_question}"
{context_section}

**YOUR TASK**:
Provide a targeted clarification that:
1. Directly addresses the student's specific question
2. Identifies the root of their confusion
3. Provides a clear, step-by-step explanation
4. Uses analogies or alternative explanations if helpful
5. Includes a concrete example to illustrate the point

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "diagnosis": "<What the student is confused about>",
  "root_cause": "<Why they are confused (e.g., misconception, missing prerequisite)>",
  "clarification": "<Direct, clear answer to their question>",
  "analogy": "<Helpful analogy to aid understanding (if applicable)>",
  "example": "<Specific example illustrating the concept>",
  "follow_up_check": "<Question to verify understanding>"
}}

Clarify NOW with precision:"""


# Convenience functions for direct use

def get_system_prompt() -> str:
    """
    Get Teacher Agent system prompt.

    Returns:
        str: System prompt for Teacher Agent
    """
    return TeacherPrompts.SYSTEM_PROMPT


def create_explanation_prompt(
    syllabus_code: str,
    concept_name: str,
    syllabus_description: str,
    learning_outcomes: List[str],
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create concept explanation prompt.

    Args:
        syllabus_code: Syllabus point code
        concept_name: Name of concept
        syllabus_description: Official syllabus description
        learning_outcomes: List of learning outcomes
        student_context: Optional student context

    Returns:
        str: Formatted prompt for Teacher Agent
    """
    return TeacherPrompts.explain_concept_prompt(
        syllabus_code,
        concept_name,
        syllabus_description,
        learning_outcomes,
        student_context,
    )


def create_clarification_prompt(
    concept_name: str,
    student_question: str,
    context: Optional[str] = None,
) -> str:
    """
    Create clarification prompt for student question.

    Args:
        concept_name: Name of concept
        student_question: Student's question
        context: Optional previous explanation context

    Returns:
        str: Formatted prompt for Teacher Agent
    """
    return TeacherPrompts.clarify_concept_prompt(
        concept_name,
        student_question,
        context,
    )
