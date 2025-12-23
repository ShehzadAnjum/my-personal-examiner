"""
Coach Prompts

Socratic dialogue prompts for the Coach Agent (personalized tutoring).

Constitutional Compliance:
- Principle III: PhD-level pedagogy (Socratic method, misconception diagnosis)
- Principle VI: Constructive feedback (guide rather than tell)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

from typing import List, Optional, Dict, Any


class CoachPrompts:
    """
    Coach Agent prompts for personalized tutoring using Socratic method.

    Provides:
    - Socratic questioning to guide student discovery
    - Misconception diagnosis and correction
    - Adaptive explanations based on student responses
    - Analogy generation for difficult concepts
    - Hints and scaffolding (not direct answers)
    """

    SYSTEM_PROMPT = """You are a PhD-level Economics tutor specializing in personalized, Socratic coaching for Cambridge International A-Level Economics 9708.

Your coaching philosophy (Socratic Method):
- **Guide, Don't Tell**: Ask questions that lead students to discover answers
- **Diagnose Misconceptions**: Identify root causes of confusion
- **Build on What They Know**: Start from student's current understanding
- **Adaptive Scaffolding**: Provide just enough support, no more
- **Celebrate Progress**: Reinforce correct reasoning positively

Constitutional Principles:
- Subject Accuracy is Non-Negotiable: All guidance must be Cambridge-aligned
- Constructive Feedback: Never say "you're wrong" - instead "let's explore that thinking"
- PhD-Level Pedagogy: Use evidence-based teaching strategies (Socratic method, metacognition)

Coaching Standards (A* Development):
- **Questioning**: Use scaffolded questions (recall → apply → analyze → evaluate)
- **Misconceptions**: Diagnose with Socratic probing, correct gently
- **Analogies**: Create relatable analogies for abstract concepts
- **Hints**: Provide minimal hints that preserve student's discovery
- **Progress Tracking**: Note breakthroughs and remaining gaps

You MUST:
1. Ask clarifying questions before explaining
2. Diagnose misconceptions through Socratic probing
3. Provide hints rather than direct answers
4. Use analogies to make abstract concepts concrete
5. Reinforce correct reasoning positively
6. Track student's progress through the session

NEVER:
- Give direct answers immediately (guide discovery first)
- Say "you're wrong" or "that's incorrect" (diagnose misconception instead)
- Skip ahead without checking understanding
- Use jargon without ensuring student knows the terms
"""

    @staticmethod
    def tutor_session_prompt(
        topic: str,
        struggle_description: str,
        student_context: Optional[Dict[str, Any]] = None,
        session_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate prompt for starting or continuing a tutoring session.

        Args:
            topic: Topic student is struggling with
            struggle_description: Student's description of their struggle
            student_context: Optional dict with student's progress, weaknesses
            session_history: Optional list of previous messages in this session

        Returns:
            str: Formatted prompt for Coach Agent
        """
        context_section = ""
        if student_context:
            prior_struggles = student_context.get("weaknesses", [])
            if prior_struggles:
                context_section = f"""
**STUDENT HISTORY**:
This student has previously struggled with: {', '.join(prior_struggles)}
Consider whether current struggle is related.
"""

        history_section = ""
        if session_history:
            history_text = "\n".join(
                f"  {msg['role'].upper()}: {msg['content']}"
                for msg in session_history[-5:]  # Last 5 messages
            )
            history_section = f"""
**SESSION HISTORY** (last 5 messages):
{history_text}
"""

        return f"""A student needs personalized tutoring help with Economics 9708.

**TOPIC**: {topic}

**STUDENT'S STRUGGLE**:
"{struggle_description}"
{context_section}{history_section}

**YOUR COACHING APPROACH**:
Use the Socratic method to guide this student to understanding.

**Step 1: Diagnose** (if this is the start of the session)
- Ask 1-2 clarifying questions to understand root cause of confusion
- Probe for misconceptions with gentle questions
- Identify what they already understand vs. what they're missing

**Step 2: Guide Discovery** (after diagnosis)
- Ask scaffolded questions that lead to the answer
- Start from what they know, build incrementally
- Provide minimal hints if student is stuck
- Use analogies to make abstract concepts concrete

**Step 3: Check Understanding**
- Ask student to explain concept back to you
- Pose a similar problem to verify transfer
- Celebrate correct reasoning, gently correct misconceptions

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "coach_message": "<Your Socratic response to the student>",
  "internal_diagnosis": {{
    "misconception_detected": "<Specific misconception if identified>",
    "knowledge_gaps": ["gap1", "gap2", ...],
    "current_understanding_level": "none|partial|good",
    "recommended_next_step": "diagnose|guide|practice|refer"
  }},
  "session_notes": {{
    "progress_made": "<What student has learned this session>",
    "remaining_gaps": ["gap1", "gap2", ...],
    "outcome": "in_progress|resolved|needs_more_help|refer_to_teacher"
  }}
}}

Coach NOW using Socratic method:"""

    @staticmethod
    def generate_analogy_prompt(
        concept_name: str,
        student_background: Optional[str] = None,
    ) -> str:
        """
        Generate prompt for creating helpful analogies.

        Args:
            concept_name: Economic concept needing analogy
            student_background: Optional info about student's interests/background

        Returns:
            str: Formatted prompt for Coach Agent
        """
        background_section = ""
        if student_background:
            background_section = f"""
**STUDENT BACKGROUND**:
{student_background}

Tailor your analogy to their interests/experience if possible.
"""

        return f"""Create a helpful analogy to explain "{concept_name}" to an A-Level Economics student.

{background_section}

**CRITERIA FOR GOOD ANALOGIES**:
1. **Relatable**: Uses familiar, everyday situations
2. **Accurate**: Maps correctly to the economic concept
3. **Simple**: Easy to understand without extra explanation
4. **Memorable**: Sticks in student's mind
5. **Transferable**: Helps with exam questions, not just memorization

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "analogy": "<The analogy>",
  "explanation": "<How the analogy maps to the economic concept>",
  "limitations": "<Where the analogy breaks down (important!)>",
  "example_application": "<How student can use this analogy in exam>"
}}

Create analogy NOW:"""

    @staticmethod
    def diagnose_misconception_prompt(
        student_answer: str,
        question_asked: str,
        concept_being_tested: str,
    ) -> str:
        """
        Generate prompt for diagnosing student misconceptions.

        Args:
            student_answer: What the student said/wrote
            question_asked: The question or prompt given to student
            concept_being_tested: Underlying concept

        Returns:
            str: Formatted prompt for Coach Agent
        """
        return f"""Diagnose the misconception in this student's response.

**CONCEPT BEING TESTED**: {concept_being_tested}

**QUESTION ASKED**:
"{question_asked}"

**STUDENT'S ANSWER**:
"{student_answer}"

**YOUR TASK**:
Identify the specific misconception and create a Socratic sequence to correct it.

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "misconception": {{
    "what_student_thinks": "<Student's current understanding>",
    "why_its_wrong": "<Root cause of error>",
    "correct_understanding": "<What they should understand>"
  }},
  "socratic_sequence": [
    {{
      "question": "<Probing question 1>",
      "purpose": "<What this question reveals/guides toward>"
    }},
    {{
      "question": "<Probing question 2>",
      "purpose": "<What this question reveals/guides toward>"
    }},
    {{...}} (3-5 questions total)
  ],
  "if_student_still_stuck": {{
    "hint": "<Minimal hint to get them unstuck>",
    "analogy": "<Helpful analogy if needed>"
  }}
}}

Diagnose NOW:"""


# Convenience functions for direct use

def get_system_prompt() -> str:
    """
    Get Coach Agent system prompt.

    Returns:
        str: System prompt for Coach Agent
    """
    return CoachPrompts.SYSTEM_PROMPT


def create_tutoring_prompt(
    topic: str,
    struggle_description: str,
    student_context: Optional[Dict[str, Any]] = None,
    session_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Create tutoring session prompt.

    Args:
        topic: Topic student is struggling with
        struggle_description: Student's description of struggle
        student_context: Optional student context
        session_history: Optional session history

    Returns:
        str: Formatted prompt for Coach Agent
    """
    return CoachPrompts.tutor_session_prompt(
        topic,
        struggle_description,
        student_context,
        session_history,
    )


def create_analogy_prompt(
    concept_name: str,
    student_background: Optional[str] = None,
) -> str:
    """
    Create analogy generation prompt.

    Args:
        concept_name: Economic concept needing analogy
        student_background: Optional student background info

    Returns:
        str: Formatted prompt for Coach Agent
    """
    return CoachPrompts.generate_analogy_prompt(concept_name, student_background)


def create_misconception_diagnosis_prompt(
    student_answer: str,
    question_asked: str,
    concept_being_tested: str,
) -> str:
    """
    Create misconception diagnosis prompt.

    Args:
        student_answer: Student's answer
        question_asked: Question asked
        concept_being_tested: Underlying concept

    Returns:
        str: Formatted prompt for Coach Agent
    """
    return CoachPrompts.diagnose_misconception_prompt(
        student_answer,
        question_asked,
        concept_being_tested,
    )
