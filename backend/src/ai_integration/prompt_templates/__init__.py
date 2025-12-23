"""Prompt Templates Module

PhD-level prompts for all 6 AI teaching agents.

Phase III Agents:
- TeacherPrompts: Concept explanations, worked examples, diagrams
- CoachPrompts: Socratic tutoring, misconception diagnosis, analogies
- MarkerPrompts: Strict marking (AO1/AO2/AO3), confidence scoring
- ReviewerPrompts: Weakness analysis, A* model answers, improvement plans
- PlannerPrompts: SM-2 study plans, contextual interleaving, adaptive scheduling
"""

from .teacher_prompts import TeacherPrompts
from .coach_prompts import CoachPrompts
from .marker_prompts import MarkerPrompts
from .reviewer_prompts import ReviewerPrompts
from .planner_prompts import PlannerPrompts

__all__ = [
    "TeacherPrompts",
    "CoachPrompts",
    "MarkerPrompts",
    "ReviewerPrompts",
    "PlannerPrompts",
]
