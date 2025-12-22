"""Marker Agent Prompt Templates

PhD-level strict marking prompts for Economics 9708 AO1/AO2/AO3 assessment.

Constitutional Requirements:
- Principle II: A* Standard (zero tolerance, PhD-level strictness)
- Principle VI: Constructive Feedback (explain WHY and HOW to improve)
"""

from typing import Dict, Any


class MarkerPrompts:
    """
    Prompt templates for Marker Agent.

    Implements PhD-level strict marking with:
    - AO1 (Knowledge): Precise definitions, key terms, theoretical understanding
    - AO2 (Application): Real-world examples, data usage, relevance
    - AO3 (Evaluation): Balanced arguments, weighing significance, clear conclusion
    """

    SYSTEM_PROMPT = """You are a PhD-level Economics examiner with 20+ years of Cambridge International A-Level marking experience.

Your role is to mark student answers with ZERO TOLERANCE for imprecision, following Cambridge mark schemes strictly.

Marking Standards (A* Grade):
- AO1 (Knowledge): Precise definitions with key terms, theoretical depth, no vagueness
- AO2 (Application): Specific real-world examples with data, relevant to question context
- AO3 (Evaluation): Balanced arguments (for/against), weighing significance, clear conclusion

Constitutional Principle: "A* Standard Marking Always - PhD-level strictness, no compromises"

You MUST:
1. Apply mark scheme point-by-point (award 0 if point not present or imprecise)
2. Identify ALL errors and categorize by AO1/AO2/AO3
3. Calculate confidence score (0-100) based on marking certainty
4. Flag for manual review if confidence < 70%
5. Provide constructive feedback explaining WHY marks lost and HOW to improve

NEVER award marks for:
- Vague definitions ("demand is what people want" ❌)
- Generic examples without data ("some goods" ❌)
- One-sided arguments without evaluation ❌
- Missing ceteris paribus assumptions ❌
"""

    @staticmethod
    def mark_answer_prompt(
        question_text: str,
        max_marks: int,
        marking_scheme: Dict[str, Any],
        student_answer: str,
    ) -> str:
        """
        Generate prompt for marking a single answer.

        Args:
            question_text: The question being answered
            max_marks: Maximum possible marks
            marking_scheme: Cambridge mark scheme (AO1/AO2/AO3 breakdown)
            student_answer: Student's written answer

        Returns:
            Formatted marking prompt
        """
        return f"""Mark the following Economics 9708 student answer strictly according to Cambridge standards.

**QUESTION** ({max_marks} marks):
{question_text}

**MARK SCHEME**:
{MarkerPrompts._format_mark_scheme(marking_scheme)}

**STUDENT ANSWER**:
{student_answer}

**INSTRUCTIONS**:
1. Award marks ONLY if mark scheme points are present AND precise
2. Identify specific errors and categorize by AO:
   - AO1 errors: Imprecise definitions, missing key terms, theoretical gaps
   - AO2 errors: Generic examples, no data, irrelevant applications
   - AO3 errors: No evaluation, one-sided, missing conclusion
3. Calculate confidence score (0-100) considering:
   - Answer length vs expected ({max_marks * 20} words expected)
   - Mark scheme coverage (how many points identified)
   - Partial marks uncertainty
   - Ambiguous language in answer
   - AO3 subjectivity
   - Borderline marks (48-52% range)

**OUTPUT FORMAT** (JSON):
{{
  "marks_awarded": <int>,
  "max_marks": {max_marks},
  "percentage": <float>,
  "ao1_score": <int>,
  "ao1_max": <int from scheme>,
  "ao2_score": <int>,
  "ao2_max": <int from scheme>,
  "ao3_score": <int>,
  "ao3_max": <int from scheme>,
  "level": "<L1|L2|L3|L4>",
  "errors": [
    {{
      "category": "AO1 - Imprecise Definition",
      "description": "Defined demand as 'what people want' instead of 'quantity willing and able to purchase at given price, ceteris paribus'",
      "marks_lost": 2
    }}
  ],
  "points_awarded": [
    {{
      "point_id": "AO1-1",
      "present": true,
      "quality": "good|weak|missing",
      "quote": "exact quote from student answer"
    }}
  ],
  "confidence_score": <0-100>,
  "needs_review": <true if confidence < 70>,
  "feedback": "Constructive explanation of WHY marks lost and HOW to improve to A* standard"
}}

Mark NOW with zero tolerance for imprecision:"""

    @staticmethod
    def _format_mark_scheme(scheme: Dict[str, Any]) -> str:
        """Format mark scheme for display in prompt"""
        if not scheme:
            return "No mark scheme provided (award 0 marks)"

        formatted = []

        # AO1 points
        if "ao1_points" in scheme:
            formatted.append("**AO1 (Knowledge)**:")
            for i, point in enumerate(scheme["ao1_points"], 1):
                formatted.append(f"  {i}. {point} (1 mark)")

        # AO2 points
        if "ao2_points" in scheme:
            formatted.append("\n**AO2 (Application)**:")
            for i, point in enumerate(scheme["ao2_points"], 1):
                formatted.append(f"  {i}. {point} (1 mark)")

        # AO3 points
        if "ao3_points" in scheme:
            formatted.append("\n**AO3 (Evaluation)**:")
            for i, point in enumerate(scheme["ao3_points"], 1):
                formatted.append(f"  {i}. {point} (1 mark)")

        # Level descriptors
        if "levels" in scheme:
            formatted.append("\n**LEVELS**:")
            for level, descriptor in scheme["levels"].items():
                formatted.append(f"  {level}: {descriptor}")

        return "\n".join(formatted)

    @staticmethod
    def explain_marking_prompt(
        question_text: str,
        student_answer: str,
        marks_awarded: int,
        max_marks: int,
        errors: list,
    ) -> str:
        """
        Generate prompt to explain marking decision to student.

        Args:
            question_text: The question
            student_answer: Student's answer
            marks_awarded: Marks given
            max_marks: Maximum marks
            errors: List of errors found

        Returns:
            Explanation prompt
        """
        return f"""Explain the marking decision to this Economics student in a constructive, PhD-level manner.

**QUESTION**:
{question_text}

**STUDENT ANSWER**:
{student_answer}

**MARKS**: {marks_awarded}/{max_marks} ({(marks_awarded/max_marks)*100:.0f}%)

**ERRORS IDENTIFIED**:
{MarkerPrompts._format_errors(errors)}

**TASK**:
Provide clear, constructive feedback that:
1. Explains WHY each mark was lost (what was imprecise/missing)
2. Shows HOW to improve to A* standard (specific actions)
3. Maintains encouraging but honest tone
4. References Cambridge mark scheme expectations

Keep feedback under 200 words, focused on top 3 improvements."""

    @staticmethod
    def _format_errors(errors: list) -> str:
        """Format error list for display"""
        if not errors:
            return "No errors - perfect answer!"

        formatted = []
        for i, error in enumerate(errors, 1):
            formatted.append(
                f"{i}. [{error.get('category', 'Unknown')}] "
                f"{error.get('description', 'No description')} "
                f"(-{error.get('marks_lost', 0)} marks)"
            )

        return "\n".join(formatted)


# Convenience functions
def get_system_prompt() -> str:
    """Get Marker Agent system prompt"""
    return MarkerPrompts.SYSTEM_PROMPT


def create_marking_prompt(
    question_text: str,
    max_marks: int,
    marking_scheme: Dict[str, Any],
    student_answer: str,
) -> str:
    """Create marking prompt for a question"""
    return MarkerPrompts.mark_answer_prompt(
        question_text, max_marks, marking_scheme, student_answer
    )
