"""Algorithms Module

Core algorithms for Phase III AI Teaching Roles:
- SuperMemo 2 (SM-2) spaced repetition
- Confidence scoring for marking quality assurance
- Contextual interleaving for study planning
"""

from .supermemo2 import (
    SuperMemo2,
    calculate_interval,
    update_easiness_factor,
    performance_to_quality,
    calculate_next_review,
)
from .confidence_scoring import (
    ConfidenceScorer,
    calculate_confidence,
    needs_manual_review,
)
from .contextual_interleaving import (
    ContextualInterleaving,
    topics_are_related,
    create_daily_clusters,
    generate_practice_sequence,
)

__all__ = [
    # SuperMemo 2
    "SuperMemo2",
    "calculate_interval",
    "update_easiness_factor",
    "performance_to_quality",
    "calculate_next_review",
    # Confidence Scoring
    "ConfidenceScorer",
    "calculate_confidence",
    "needs_manual_review",
    # Contextual Interleaving
    "ContextualInterleaving",
    "topics_are_related",
    "create_daily_clusters",
    "generate_practice_sequence",
]
