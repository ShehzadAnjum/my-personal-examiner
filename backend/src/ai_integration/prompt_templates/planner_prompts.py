"""
Planner Prompts

Study schedule optimization prompts for Planner Agent.

Uses SuperMemo 2 algorithm and contextual interleaving for evidence-based
study planning.

Constitutional Compliance:
- Principle III: PhD-level pedagogy (evidence-based spaced repetition)
- Principle IV: Spec-driven development (SM-2 algorithm spec)
- Principle VI: Constructive feedback (clear rationale for schedule decisions)
"""

from typing import List, Dict, Any, Optional


class PlannerPrompts:
    """
    Planner Agent prompts for study schedule generation.

    Provides:
    - n-day study plan generation with SM-2 intervals
    - Contextual interleaving (max 3 related topics per day)
    - Adaptive rescheduling based on performance
    - Syllabus coverage validation
    - Topic prioritization
    """

    SYSTEM_PROMPT = """You are a PhD-level educational psychologist specializing in evidence-based study planning for Cambridge International A-Level Economics 9708.

Your planning philosophy:
- **Spaced Repetition**: Use SuperMemo 2 algorithm for optimal retention
- **Contextual Interleaving**: Mix related topics (max 3 per day) for better discrimination
- **Cognitive Load Management**: Respect working memory limits
- **Adaptive Scheduling**: Adjust based on actual performance (easiness factors)
- **100% Coverage**: Ensure all syllabus points covered before exam

Research Basis:
- SM-2 algorithm: 30% better retention than fixed intervals
- Contextual interleaving: 30% improvement vs. blocked practice
- Max 3 topics per day: cognitive load research (Miller's 7±2)
- Adaptive EF: personalizes schedule to student's actual performance

Constitutional Principles:
- Evidence-Based Pedagogy: All planning decisions backed by research
- Subject Accuracy: Syllabus coverage matches Cambridge exactly
- Constructive Feedback: Explain WHY schedule is structured this way

Planning Standards (Production v1.0):
- **SM-2 Intervals**: I(1)=1 day, I(2)=6 days, I(n)=I(n-1)*EF
- **Easiness Factors**: EF ∈ [1.3, 2.5], updated by performance
- **Interleaving**: Max 3 related topics per day (same syllabus section)
- **Coverage**: 100% of syllabus before exam, no gaps
- **Flexibility**: Buffer days for adjustments (10% of total days)

You MUST:
1. Use SM-2 algorithm exactly (I(1)=1, I(2)=6, I(n)=I(n-1)*EF)
2. Limit to max 3 topics per day (cognitive load)
3. Group related topics (same syllabus section, e.g., 9708.1.x)
4. Ensure 100% syllabus coverage before exam date
5. Provide clear rationale for schedule structure

NEVER:
- Exceed 3 topics per day (cognitive overload)
- Mix unrelated topics (breaks contextual interleaving)
- Skip syllabus points (must have 100% coverage)
- Use arbitrary intervals (must use SM-2 formula)
"""

    @staticmethod
    def create_study_plan_prompt(
        subject_code: str,
        syllabus_points: List[str],
        exam_date: str,
        available_days: int,
        hours_per_day: float,
        student_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate prompt for creating an n-day study plan.

        Args:
            subject_code: Subject code (e.g., "9708")
            syllabus_points: List of syllabus point codes to cover
            exam_date: Exam date (YYYY-MM-DD)
            available_days: Number of days available for study
            hours_per_day: Hours student can study per day
            student_context: Optional dict with easiness_factors, weaknesses

        Returns:
            str: Formatted prompt for Planner Agent
        """
        # Format syllabus points by section
        sections: Dict[str, List[str]] = {}
        for point in syllabus_points:
            section = point.rsplit(".", 1)[0]  # "9708.1.1" → "9708.1"
            if section not in sections:
                sections[section] = []
            sections[section].append(point)

        sections_text = "\n".join(
            f"  {section}: {', '.join(points)}"
            for section, points in sorted(sections.items())
        )

        context_section = ""
        if student_context:
            ef_data = student_context.get("easiness_factors", {})
            weaknesses = student_context.get("weaknesses", [])

            if ef_data:
                context_section += f"\n**EASINESS FACTORS** (from previous performance):\n"
                for point, ef in ef_data.items():
                    context_section += f"  {point}: EF={ef:.2f}\n"

            if weaknesses:
                context_section += f"\n**KNOWN WEAKNESSES** (prioritize these):\n"
                context_section += "  " + ", ".join(weaknesses) + "\n"

        return f"""Create a {available_days}-day study plan for Cambridge A-Level Economics {subject_code}.

**EXAM DATE**: {exam_date}
**AVAILABLE DAYS**: {available_days} days
**STUDY TIME**: {hours_per_day} hours per day

**SYLLABUS COVERAGE** ({len(syllabus_points)} topics total):
{sections_text}
{context_section}

**YOUR TASK**:
Generate a day-by-day study schedule using:
1. **SuperMemo 2 (SM-2) algorithm**: I(1)=1, I(2)=6, I(n)=I(n-1)*EF
2. **Contextual interleaving**: Max 3 related topics per day
3. **100% coverage**: All syllabus points covered before exam
4. **Adaptive EF**: Use provided easiness factors if available, else default 2.5

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "plan_metadata": {{
    "total_days": {available_days},
    "exam_date": "{exam_date}",
    "topics_covered": {len(syllabus_points)},
    "coverage_percentage": 100,
    "buffer_days": "<number of buffer days for flexibility>"
  }},
  "daily_schedule": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "topics": ["9708.1.1", "9708.1.2"],  // Max 3, related only
      "activities": ["study", "practice", "review"],
      "hours_allocated": {hours_per_day},
      "sm2_intervals": [1, 1],  // SM-2 interval for each topic (days since last review)
      "easiness_factors": [2.5, 2.5],  // EF for each topic
      "rationale": "<Why these topics grouped today, what SM-2 interval they're at>"
    }},
    {{
      "day": 2,
      "date": "YYYY-MM-DD",
      "topics": ["9708.2.1", "9708.2.2", "9708.2.3"],
      "activities": ["study", "mixed_review"],  // Include review of day 1 topics
      "hours_allocated": {hours_per_day},
      "sm2_intervals": [1, 1, 1],
      "easiness_factors": [2.5, 2.5, 2.5],
      "rationale": "<Rationale for day 2>"
    }},
    {{...}} ({available_days} days total)
  ],
  "coverage_validation": {{
    "all_topics_covered": true,
    "coverage_map": {{"9708.1.1": "day_1", "9708.1.2": "day_1", ...}},
    "review_schedule": {{"9708.1.1": ["day_1", "day_7", "day_21"], ...}}  // SM-2 review dates
  }},
  "interleaving_rationale": {{
    "day_1_grouping": "<Why these specific topics on day 1>",
    "day_2_grouping": "<Why these specific topics on day 2>",
    ...
  }},
  "adaptive_notes": {{
    "weak_areas_prioritized": ["<Topic 1>", "<Topic 2>", ...],
    "ef_adjustments_made": "<How EF data influenced schedule>",
    "buffer_strategy": "<When/how buffer days are used>"
  }}
}}

Create study plan NOW using SM-2 + contextual interleaving:"""

    @staticmethod
    def optimize_schedule_prompt(
        current_plan: Dict[str, Any],
        performance_data: List[Dict[str, Any]],
    ) -> str:
        """
        Generate prompt for optimizing schedule based on performance.

        Args:
            current_plan: Current study plan JSON
            performance_data: List of dicts with topic, performance_percentage, date

        Returns:
            str: Formatted prompt for Planner Agent
        """
        # Format performance data
        perf_text = "\n".join(
            f"  {p['topic']}: {p['performance_percentage']:.0f}% on {p['date']}"
            for p in performance_data
        )

        return f"""Optimize this study schedule based on actual student performance.

**CURRENT PLAN**:
- Total days: {current_plan.get('plan_metadata', {}).get('total_days')}
- Exam date: {current_plan.get('plan_metadata', {}).get('exam_date')}

**RECENT PERFORMANCE** (use to update EF):
{perf_text}

**YOUR TASK**:
1. Update easiness factors (EF) using SM-2 formula:
   - Performance → quality (0-5 scale)
   - EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
   - EF ∈ [1.3, 2.5]

2. Reschedule topics with updated intervals:
   - I(n) = I(n-1) * EF' for quality ≥ 3
   - I(n) = 1 (restart) for quality < 3

3. Adjust future days to accommodate changes

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "ef_updates": [
    {{
      "topic": "9708.1.1",
      "old_ef": 2.5,
      "performance": 85,
      "quality": 4,
      "new_ef": 2.60
    }},
    {{...}} (all topics with performance data)
  ],
  "interval_updates": [
    {{
      "topic": "9708.1.1",
      "old_interval": 1,
      "new_interval": 3,
      "next_review_date": "YYYY-MM-DD"
    }},
    {{...}}
  ],
  "updated_schedule": {{
    "daily_schedule": [...],  // Revised schedule with new intervals
    "changes_made": ["<Change 1>", "<Change 2>", ...]
  }}
}}

Optimize NOW:"""


# Convenience functions for direct use

def get_system_prompt() -> str:
    """
    Get Planner Agent system prompt.

    Returns:
        str: System prompt for Planner Agent
    """
    return PlannerPrompts.SYSTEM_PROMPT


def create_study_plan_prompt(
    subject_code: str,
    syllabus_points: List[str],
    exam_date: str,
    available_days: int,
    hours_per_day: float,
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create study plan generation prompt.

    Args:
        subject_code: Subject code
        syllabus_points: List of syllabus point codes
        exam_date: Exam date (YYYY-MM-DD)
        available_days: Number of days available
        hours_per_day: Hours per day
        student_context: Optional student context (EF, weaknesses)

    Returns:
        str: Formatted prompt for Planner Agent
    """
    return PlannerPrompts.create_study_plan_prompt(
        subject_code,
        syllabus_points,
        exam_date,
        available_days,
        hours_per_day,
        student_context,
    )


def create_optimization_prompt(
    current_plan: Dict[str, Any],
    performance_data: List[Dict[str, Any]],
) -> str:
    """
    Create schedule optimization prompt.

    Args:
        current_plan: Current study plan
        performance_data: Recent performance data

    Returns:
        str: Formatted prompt for Planner Agent
    """
    return PlannerPrompts.optimize_schedule_prompt(current_plan, performance_data)
