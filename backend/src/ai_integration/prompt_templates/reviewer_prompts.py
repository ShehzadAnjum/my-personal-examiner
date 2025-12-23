"""
Reviewer Prompts

Weakness analysis and A* model answer generation prompts for Reviewer Agent.

Constitutional Compliance:
- Principle II: A* standard marking (exemplar answers demonstrate excellence)
- Principle VI: Constructive feedback (actionable improvement plans)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

from typing import List, Dict, Any, Optional


class ReviewerPrompts:
    """
    Reviewer Agent prompts for analyzing weaknesses and generating model answers.

    Provides:
    - Detailed weakness analysis (AO1/AO2/AO3 categorization)
    - A* model answer generation
    - Improvement plan creation with actionable steps
    - Progress comparison (current vs. previous attempts)
    """

    SYSTEM_PROMPT = """You are a PhD-level Economics examiner specializing in Cambridge International A-Level Economics 9708 with 20+ years of marking experience.

Your review philosophy:
- **Diagnostic Precision**: Categorize every weakness by Assessment Objective (AO1/AO2/AO3)
- **Actionable Feedback**: Every critique paired with specific improvement action
- **A* Exemplars**: Model answers demonstrate perfect execution
- **Growth Mindset**: Focus on gap between current and A* standard
- **Holistic Analysis**: Identify patterns across multiple questions

Constitutional Principles:
- A* Standard Marking Always: Model answers must be perfect exemplars
- Constructive Feedback: Always explain HOW to improve, not just WHAT is wrong
- Subject Accuracy: All feedback must align with Cambridge mark schemes exactly

Review Standards (PhD-Level):
- **Weakness Analysis**: Specific, categorized by AO1/AO2/AO3, with examples from answer
- **Model Answers**: A* quality, show perfect structure/content/evaluation
- **Action Items**: Concrete, measurable, achievable improvement steps
- **Progress Tracking**: Compare current vs. previous attempts quantitatively

You MUST:
1. Categorize ALL weaknesses by Assessment Objective (AO1/AO2/AO3)
2. Provide specific examples from student's answer for each weakness
3. Generate A* model answers that demonstrate perfect execution
4. Create actionable improvement plan with specific steps
5. Compare current performance to previous attempts (if available)

NEVER:
- Give generic feedback ("improve your definitions" ❌)
- Model answers below A* standard
- Action items that aren't specific and measurable
- Skip categorization by AO1/AO2/AO3
"""

    @staticmethod
    def analyze_weaknesses_prompt(
        attempt_data: Dict[str, Any],
        attempted_questions: List[Dict[str, Any]],
        previous_attempts: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate prompt for analyzing student weaknesses across an attempt.

        Args:
            attempt_data: Dict with overall_score, grade, exam details
            attempted_questions: List of dicts with question, answer, marks, feedback
            previous_attempts: Optional list of previous attempts for comparison

        Returns:
            str: Formatted prompt for Reviewer Agent
        """
        # Format attempted questions
        questions_text = ""
        for i, aq in enumerate(attempted_questions, 1):
            questions_text += f"""
**QUESTION {i}** ({aq['max_marks']} marks):
{aq['question_text']}

**STUDENT'S ANSWER**:
{aq['student_answer'] or '[No answer provided]'}

**MARKS AWARDED**: {aq['marks_awarded']}/{aq['max_marks']}

**MARKING FEEDBACK**:
{aq.get('marking_feedback', {}).get('errors', [])}
"""

        # Format previous attempts if available
        history_section = ""
        if previous_attempts:
            history_text = "\n".join(
                f"  - Attempt {i}: Score {att['overall_score']}, Grade {att['grade']}, Date {att['submitted_at']}"
                for i, att in enumerate(previous_attempts, 1)
            )
            history_section = f"""
**PREVIOUS ATTEMPTS** (for comparison):
{history_text}
"""

        return f"""Analyze this student's exam attempt to identify weaknesses and create an improvement plan.

**OVERALL PERFORMANCE**:
- Score: {attempt_data['overall_score']} (Grade: {attempt_data.get('grade', 'Pending')})
- Exam: {attempt_data.get('exam_type', 'N/A')}
{history_section}

**QUESTIONS AND ANSWERS**:
{questions_text}

**YOUR TASK**:
Provide a comprehensive weakness analysis and improvement plan.

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "weakness_analysis": {{
    "AO1_knowledge": [
      {{
        "weakness": "<Specific knowledge gap>",
        "examples_from_answer": ["<Quote from student answer>", ...],
        "severity": "low|medium|high",
        "syllabus_points_affected": ["9708.x.y", ...]
      }},
      {{...}} (all AO1 weaknesses)
    ],
    "AO2_application": [
      {{
        "weakness": "<Specific application issue>",
        "examples_from_answer": ["<Quote from student answer>", ...],
        "severity": "low|medium|high",
        "syllabus_points_affected": ["9708.x.y", ...]
      }},
      {{...}} (all AO2 weaknesses)
    ],
    "AO3_evaluation": [
      {{
        "weakness": "<Specific evaluation issue>",
        "examples_from_answer": ["<Quote from student answer>", ...],
        "severity": "low|medium|high",
        "syllabus_points_affected": ["9708.x.y", ...]
      }},
      {{...}} (all AO3 weaknesses)
    ]
  }},
  "improvement_plan": {{
    "priority_areas": ["<Top 3 areas to focus on>"],
    "action_items": [
      {{
        "id": "ACTION_1",
        "action": "<Specific, measurable improvement action>",
        "target_weakness": "<Which weakness this addresses>",
        "how_to_do_it": "<Step-by-step guidance>",
        "success_criteria": "<How to know if improved>",
        "resources": ["<Syllabus section>", "<Practice question type>", ...]
      }},
      {{...}} (5-10 action items, prioritized)
    ],
    "practice_recommendations": [
      {{
        "syllabus_point": "9708.x.y",
        "question_type": "<Type of question to practice>",
        "focus": "<What to focus on when practicing>"
      }},
      {{...}}
    ]
  }},
  "progress_comparison": {{
    "compared_to_previous": "<Comparison if previous attempts available>",
    "improvements": ["<What has improved>", ...],
    "regressions": ["<What has gotten worse>", ...],
    "trend": "improving|stable|declining"
  }}
}}

Analyze NOW with diagnostic precision:"""

    @staticmethod
    def generate_model_answer_prompt(
        question_text: str,
        max_marks: int,
        marking_scheme: Dict[str, Any],
        student_answer: Optional[str] = None,
        marks_awarded: Optional[int] = None,
    ) -> str:
        """
        Generate prompt for creating A* model answer.

        Args:
            question_text: The exam question
            max_marks: Maximum marks for question
            marking_scheme: Dict with mark scheme details
            student_answer: Optional student's actual answer
            marks_awarded: Optional marks student received

        Returns:
            str: Formatted prompt for Reviewer Agent
        """
        student_section = ""
        if student_answer:
            student_section = f"""
**STUDENT'S ANSWER** ({marks_awarded}/{max_marks} marks):
{student_answer}

Your model answer should demonstrate what an A* response looks like in contrast to this.
"""

        return f"""Generate an A* model answer for this Economics 9708 exam question.

**QUESTION** ({max_marks} marks):
{question_text}

**MARK SCHEME**:
{ReviewerPrompts._format_mark_scheme(marking_scheme)}
{student_section}

**YOUR TASK**:
Create a model answer that demonstrates perfect A* execution.

**A* MODEL ANSWER CRITERIA**:
- **AO1 (Knowledge)**: Precise definitions, exact terminology, theoretical depth
- **AO2 (Application)**: Specific real-world examples with data, diagrams labeled correctly
- **AO3 (Evaluation)**: Balanced arguments (pros/cons), weighing significance, clear conclusion
- **Structure**: Introduction, development, conclusion (if essay)
- **Conciseness**: No waffle, every sentence adds value
- **Cambridge Style**: Matches past paper exemplar quality

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "model_answer": "<The A* answer>",
  "marks_breakdown": {{
    "AO1_marks": <marks>,
    "AO2_marks": <marks>,
    "AO3_marks": <marks>,
    "total": {max_marks}
  }},
  "why_this_is_a_star": {{
    "knowledge_demonstration": "<What makes AO1 perfect>",
    "application_demonstration": "<What makes AO2 perfect>",
    "evaluation_demonstration": "<What makes AO3 perfect>",
    "structure_excellence": "<Why structure is perfect>"
  }},
  "key_features_to_learn": [
    "<Feature 1 student should emulate>",
    "<Feature 2 student should emulate>",
    ...
  ]
}}

Generate A* model answer NOW:"""

    @staticmethod
    def _format_mark_scheme(marking_scheme: Dict[str, Any]) -> str:
        """Format mark scheme for display in prompt."""
        if isinstance(marking_scheme, dict):
            formatted = []
            for key, value in marking_scheme.items():
                if isinstance(value, list):
                    formatted.append(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    formatted.append(f"  {key}: {value}")
            return "\n".join(formatted)
        return str(marking_scheme)


# Convenience functions for direct use

def get_system_prompt() -> str:
    """
    Get Reviewer Agent system prompt.

    Returns:
        str: System prompt for Reviewer Agent
    """
    return ReviewerPrompts.SYSTEM_PROMPT


def create_weakness_analysis_prompt(
    attempt_data: Dict[str, Any],
    attempted_questions: List[Dict[str, Any]],
    previous_attempts: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Create weakness analysis prompt.

    Args:
        attempt_data: Overall attempt details
        attempted_questions: List of attempted questions with feedback
        previous_attempts: Optional previous attempts for comparison

    Returns:
        str: Formatted prompt for Reviewer Agent
    """
    return ReviewerPrompts.analyze_weaknesses_prompt(
        attempt_data,
        attempted_questions,
        previous_attempts,
    )


def create_model_answer_prompt(
    question_text: str,
    max_marks: int,
    marking_scheme: Dict[str, Any],
    student_answer: Optional[str] = None,
    marks_awarded: Optional[int] = None,
) -> str:
    """
    Create A* model answer generation prompt.

    Args:
        question_text: Exam question
        max_marks: Maximum marks
        marking_scheme: Mark scheme details
        student_answer: Optional student answer
        marks_awarded: Optional marks awarded

    Returns:
        str: Formatted prompt for Reviewer Agent
    """
    return ReviewerPrompts.generate_model_answer_prompt(
        question_text,
        max_marks,
        marking_scheme,
        student_answer,
        marks_awarded,
    )
