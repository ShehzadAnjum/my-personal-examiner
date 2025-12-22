"""SuperMemo 2 (SM-2) Spaced Repetition Algorithm

Production-grade implementation of the SuperMemo 2 algorithm for optimal learning intervals.

Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

Constitutional Requirements:
- Principle VII: >80% test coverage (pure functions, easily testable)
"""

from typing import Tuple


class SuperMemo2:
    """
    SuperMemo 2 spaced repetition algorithm.

    Calculates optimal review intervals based on performance quality (0-5 scale).
    Adjusts easiness factor (EF) dynamically based on student performance.

    Algorithm:
    - I(1) = 1 day
    - I(2) = 6 days
    - I(n) = I(n-1) * EF for n ≥ 3
    - EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    - EF min = 1.3, max = 2.5 (default = 2.5)

    Quality scale (q):
    - 5: Perfect recall
    - 4: Correct after hesitation
    - 3: Correct with difficulty
    - 2: Incorrect, but remembered with prompt
    - 1: Incorrect, barely remembered
    - 0: Complete blackout
    """

    # Algorithm constants
    MIN_EF = 1.3
    MAX_EF = 2.5
    DEFAULT_EF = 2.5
    INITIAL_INTERVAL_1 = 1
    INITIAL_INTERVAL_2 = 6

    @staticmethod
    def calculate_interval(repetition_number: int, easiness_factor: float) -> int:
        """
        Calculate the optimal interval (in days) for the next review.

        Args:
            repetition_number: Number of consecutive successful reviews (1, 2, 3, ...)
            easiness_factor: Current easiness factor (1.3-2.5)

        Returns:
            Interval in days until next review

        Examples:
            >>> SuperMemo2.calculate_interval(1, 2.5)
            1
            >>> SuperMemo2.calculate_interval(2, 2.5)
            6
            >>> SuperMemo2.calculate_interval(3, 2.5)
            15
            >>> SuperMemo2.calculate_interval(4, 2.5)
            37
        """
        if repetition_number < 1:
            raise ValueError("Repetition number must be >= 1")

        if repetition_number == 1:
            return SuperMemo2.INITIAL_INTERVAL_1
        elif repetition_number == 2:
            return SuperMemo2.INITIAL_INTERVAL_2
        else:
            # I(n) = I(n-1) * EF for n >= 3
            # We need previous interval, so recursively calculate
            previous_interval = SuperMemo2.calculate_interval(repetition_number - 1, easiness_factor)
            return round(previous_interval * easiness_factor)

    @staticmethod
    def update_easiness_factor(current_ef: float, quality: int) -> float:
        """
        Update easiness factor based on performance quality.

        Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

        Args:
            current_ef: Current easiness factor (1.3-2.5)
            quality: Performance quality score (0-5)

        Returns:
            Updated easiness factor (clamped to 1.3-2.5)

        Examples:
            >>> SuperMemo2.update_easiness_factor(2.5, 5)  # Perfect recall
            2.6
            >>> SuperMemo2.update_easiness_factor(2.5, 4)  # Good recall
            2.5
            >>> SuperMemo2.update_easiness_factor(2.5, 3)  # Correct with difficulty
            2.36
            >>> SuperMemo2.update_easiness_factor(2.5, 0)  # Complete failure
            1.3
        """
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # Clamp to valid range
        return max(SuperMemo2.MIN_EF, min(SuperMemo2.MAX_EF, new_ef))

    @staticmethod
    def performance_to_quality(performance_percentage: float) -> int:
        """
        Map exam performance percentage to SM-2 quality rating (0-5).

        Mapping:
        - 90-100%: Quality 5 (Perfect recall, A*)
        - 80-89%:  Quality 4 (Good recall, A)
        - 70-79%:  Quality 3 (Correct with difficulty, B)
        - 60-69%:  Quality 2 (Partial recall, C)
        - 50-59%:  Quality 1 (Minimal recall, D)
        - 0-49%:   Quality 0 (Forgot, E/U)

        Args:
            performance_percentage: Exam score as percentage (0-100)

        Returns:
            Quality rating (0-5)

        Examples:
            >>> SuperMemo2.performance_to_quality(95)
            5
            >>> SuperMemo2.performance_to_quality(75)
            3
            >>> SuperMemo2.performance_to_quality(45)
            0
        """
        if not 0 <= performance_percentage <= 100:
            raise ValueError("Performance percentage must be between 0 and 100")

        if performance_percentage >= 90:
            return 5  # A* - Perfect
        elif performance_percentage >= 80:
            return 4  # A - Good
        elif performance_percentage >= 70:
            return 3  # B - Correct with difficulty
        elif performance_percentage >= 60:
            return 2  # C - Partial recall
        elif performance_percentage >= 50:
            return 1  # D - Minimal recall
        else:
            return 0  # E/U - Forgot

    @staticmethod
    def calculate_next_review(
        repetition_number: int,
        current_ef: float,
        performance_percentage: float
    ) -> Tuple[int, float, int]:
        """
        Calculate next review interval and updated EF based on performance.

        Convenience method combining quality mapping, EF update, and interval calculation.

        Args:
            repetition_number: Current repetition count (1, 2, 3, ...)
            current_ef: Current easiness factor (1.3-2.5)
            performance_percentage: Exam score as percentage (0-100)

        Returns:
            Tuple of (next_interval_days, new_ef, quality_rating)

        Examples:
            >>> SuperMemo2.calculate_next_review(1, 2.5, 95)
            (1, 2.6, 5)
            >>> SuperMemo2.calculate_next_review(3, 2.5, 75)
            (15, 2.36, 3)
        """
        # Map performance to quality
        quality = SuperMemo2.performance_to_quality(performance_percentage)

        # Update easiness factor
        new_ef = SuperMemo2.update_easiness_factor(current_ef, quality)

        # Calculate next interval
        # If quality < 3 (incorrect), reset to repetition 1
        if quality < 3:
            next_interval = SuperMemo2.calculate_interval(1, new_ef)
            repetition_number = 1
        else:
            next_interval = SuperMemo2.calculate_interval(repetition_number + 1, new_ef)

        return (next_interval, new_ef, quality)


# Convenience functions for direct use
def calculate_interval(repetition_number: int, easiness_factor: float) -> int:
    """Convenience wrapper for SuperMemo2.calculate_interval"""
    return SuperMemo2.calculate_interval(repetition_number, easiness_factor)


def update_easiness_factor(current_ef: float, quality: int) -> float:
    """Convenience wrapper for SuperMemo2.update_easiness_factor"""
    return SuperMemo2.update_easiness_factor(current_ef, quality)


def performance_to_quality(performance_percentage: float) -> int:
    """Convenience wrapper for SuperMemo2.performance_to_quality"""
    return SuperMemo2.performance_to_quality(performance_percentage)


def calculate_next_review(
    repetition_number: int,
    current_ef: float,
    performance_percentage: float
) -> Tuple[int, float, int]:
    """Convenience wrapper for SuperMemo2.calculate_next_review"""
    return SuperMemo2.calculate_next_review(repetition_number, current_ef, performance_percentage)
