"""Confidence Scoring Algorithm for AI Marking

6-signal heuristic to calculate confidence (0-100) in automated marking results.
Marks with <70% confidence are flagged for manual human review.

Constitutional Requirements:
- Principle II: A* Standard (confidence scoring ensures quality control)
- Principle VII: >80% test coverage (pure functions, easily testable)
"""

from typing import List, Dict, Any


class ConfidenceScorer:
    """
    Calculate confidence score (0-100) for automated marking results.

    Uses 6 signals to detect potential marking errors:
    1. Answer length mismatch (too short or too long)
    2. Mark scheme coverage (how many required points identified)
    3. Partial marks (edge cases harder to mark)
    4. Ambiguous language in student answer
    5. AO3 evaluation subjectivity (inherently harder to mark)
    6. Borderline marks (near grade boundaries)

    Threshold: <70% confidence triggers manual review
    """

    # Threshold for manual review
    MANUAL_REVIEW_THRESHOLD = 70

    # Ambiguous phrases that reduce confidence
    AMBIGUOUS_PHRASES = [
        "might", "maybe", "possibly", "could be", "perhaps",
        "some", "few", "many", "several", "various",
        "etc.", "and so on", "things like", "such as"
    ]

    @staticmethod
    def calculate_confidence(
        marks_awarded: int,
        max_marks: int,
        student_answer: str,
        question: Dict[str, Any],
        marking_details: Dict[str, Any]
    ) -> int:
        """
        Calculate confidence score (0-100) for marking result.

        Args:
            marks_awarded: Marks given to student
            max_marks: Maximum possible marks
            student_answer: Student's written answer
            question: Question dict with marking_scheme
            marking_details: Dict with identified_points, required_points, ao3_present

        Returns:
            Confidence score (0-100)

        Example:
            >>> question = {"max_marks": 12, "marking_scheme": {...}}
            >>> details = {"identified_points": 5, "required_points": 10, "ao3_present": True}
            >>> ConfidenceScorer.calculate_confidence(8, 12, "...", question, details)
            65  # Low confidence, needs review
        """
        confidence = 100

        # Signal 1: Answer Length Mismatch (-20 points)
        confidence -= ConfidenceScorer._check_length_mismatch(
            student_answer, max_marks
        )

        # Signal 2: Mark Scheme Coverage (-25 points)
        confidence -= ConfidenceScorer._check_coverage(
            marking_details.get("identified_points", 0),
            marking_details.get("required_points", 1)
        )

        # Signal 3: Partial Marks Edge Cases (-15 points)
        confidence -= ConfidenceScorer._check_partial_marks(
            marks_awarded, max_marks
        )

        # Signal 4: Ambiguous Language Detection (-20 points)
        confidence -= ConfidenceScorer._check_ambiguous_language(student_answer)

        # Signal 5: AO3 Evaluation Subjectivity (-10 points)
        if marking_details.get("ao3_present", False):
            confidence -= 10

        # Signal 6: Borderline Marks (-15 points)
        confidence -= ConfidenceScorer._check_borderline_marks(
            marks_awarded, max_marks
        )

        # Clamp to 0-100 range
        return max(0, min(100, confidence))

    @staticmethod
    def _check_length_mismatch(student_answer: str, max_marks: int) -> int:
        """
        Check if answer length is appropriate for question marks.

        Rule of thumb: ~20 words per mark expected.

        Args:
            student_answer: Student's written answer
            max_marks: Maximum possible marks

        Returns:
            Penalty points (0 or 20)
        """
        expected_words = max_marks * 20
        actual_words = len(student_answer.split())

        if actual_words == 0:
            return 20  # Empty answer is highly suspicious

        length_ratio = actual_words / expected_words

        # Too short (<30%) or too long (>300%)
        if length_ratio < 0.3 or length_ratio > 3.0:
            return 20

        return 0

    @staticmethod
    def _check_coverage(identified_points: int, required_points: int) -> int:
        """
        Check mark scheme coverage.

        Low coverage suggests AI may have missed key points.

        Args:
            identified_points: Number of mark scheme points found
            required_points: Total required points in scheme

        Returns:
            Penalty points (0-25)
        """
        if required_points == 0:
            return 0

        coverage = identified_points / required_points

        if coverage < 0.5:
            return 25  # Less than 50% coverage
        elif coverage < 0.7:
            return 15  # 50-70% coverage
        elif coverage < 0.85:
            return 5   # 70-85% coverage

        return 0  # Good coverage

    @staticmethod
    def _check_partial_marks(marks_awarded: int, max_marks: int) -> int:
        """
        Check if marks are partial (not 0 or full marks).

        Partial marks are edge cases harder to judge precisely.

        Args:
            marks_awarded: Marks given to student
            max_marks: Maximum possible marks

        Returns:
            Penalty points (0 or 15)
        """
        # 0 or full marks are clear-cut decisions
        if marks_awarded == 0 or marks_awarded == max_marks:
            return 0

        return 15  # Partial marks require nuanced judgment

    @staticmethod
    def _check_ambiguous_language(student_answer: str) -> int:
        """
        Detect ambiguous language in student answer.

        Vague language makes marking harder and less certain.

        Args:
            student_answer: Student's written answer

        Returns:
            Penalty points (0 or 20)
        """
        answer_lower = student_answer.lower()

        # Count ambiguous phrases
        ambiguous_count = sum(
            1 for phrase in ConfidenceScorer.AMBIGUOUS_PHRASES
            if phrase in answer_lower
        )

        # More than 3 ambiguous phrases reduces confidence
        if ambiguous_count > 3:
            return 20

        return 0

    @staticmethod
    def _check_borderline_marks(marks_awarded: int, max_marks: int) -> int:
        """
        Check if marks are near grade boundaries.

        Borderline marks (48-52% range) are harder to judge.

        Args:
            marks_awarded: Marks given to student
            max_marks: Maximum possible marks

        Returns:
            Penalty points (0 or 15)
        """
        if max_marks == 0:
            return 0

        percentage = (marks_awarded / max_marks) * 100

        # Borderline range: 48-52%
        if 48 <= percentage <= 52:
            return 15

        return 0

    @staticmethod
    def needs_manual_review(confidence_score: int) -> bool:
        """
        Determine if marking result needs manual human review.

        Args:
            confidence_score: Calculated confidence (0-100)

        Returns:
            True if confidence < 70% (needs review)

        Example:
            >>> ConfidenceScorer.needs_manual_review(65)
            True
            >>> ConfidenceScorer.needs_manual_review(85)
            False
        """
        return confidence_score < ConfidenceScorer.MANUAL_REVIEW_THRESHOLD


# Convenience functions
def calculate_confidence(
    marks_awarded: int,
    max_marks: int,
    student_answer: str,
    question: Dict[str, Any],
    marking_details: Dict[str, Any]
) -> int:
    """Convenience wrapper for ConfidenceScorer.calculate_confidence"""
    return ConfidenceScorer.calculate_confidence(
        marks_awarded, max_marks, student_answer, question, marking_details
    )


def needs_manual_review(confidence_score: int) -> bool:
    """Convenience wrapper for ConfidenceScorer.needs_manual_review"""
    return ConfidenceScorer.needs_manual_review(confidence_score)
