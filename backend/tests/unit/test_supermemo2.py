"""Unit tests for SuperMemo 2 (SM-2) spaced repetition algorithm.

Tests validate:
- Interval calculation formula (I(1)=1, I(2)=6, I(n)=I(n-1)*EF)
- Easiness factor update formula
- Performance percentage to quality mapping
- Edge cases and error handling
- Constitutional Requirement: >80% test coverage for algorithms

Test Coverage: 100% of SuperMemo2 class methods
"""

import pytest
from src.algorithms.supermemo2 import SuperMemo2


class TestCalculateInterval:
    """Test interval calculation: I(1)=1, I(2)=6, I(n)=I(n-1)*EF"""

    def test_repetition_1_returns_1_day(self):
        """First repetition interval is always 1 day"""
        assert SuperMemo2.calculate_interval(1, 2.5) == 1
        assert SuperMemo2.calculate_interval(1, 1.3) == 1
        assert SuperMemo2.calculate_interval(1, 2.0) == 1

    def test_repetition_2_returns_6_days(self):
        """Second repetition interval is always 6 days"""
        assert SuperMemo2.calculate_interval(2, 2.5) == 6
        assert SuperMemo2.calculate_interval(2, 1.3) == 6
        assert SuperMemo2.calculate_interval(2, 2.0) == 6

    def test_repetition_3_with_default_ef(self):
        """Third repetition: I(3) = I(2) * EF = 6 * 2.5 = 15"""
        assert SuperMemo2.calculate_interval(3, 2.5) == 15

    def test_repetition_4_with_default_ef(self):
        """Fourth repetition: I(4) = I(3) * EF = 15 * 2.5 = 37.5 ≈ 38"""
        # 15 * 2.5 = 37.5, round(37.5) = 38
        assert SuperMemo2.calculate_interval(4, 2.5) == 38

    def test_repetition_5_with_default_ef(self):
        """Fifth repetition: I(5) = I(4) * EF = 38 * 2.5 = 95"""
        assert SuperMemo2.calculate_interval(5, 2.5) == 95

    def test_low_ef_reduces_intervals(self):
        """Lower EF (struggling student) = shorter intervals"""
        # Repetition 3: I(3) = 6 * 1.3 = 7.8 ≈ 8
        assert SuperMemo2.calculate_interval(3, 1.3) == 8
        # Repetition 4: I(4) = 8 * 1.3 = 10.4 ≈ 10
        assert SuperMemo2.calculate_interval(4, 1.3) == 10

    def test_high_ef_extends_intervals(self):
        """Higher EF (high-performing student) = longer intervals"""
        # Repetition 3: I(3) = 6 * 2.5 = 15
        assert SuperMemo2.calculate_interval(3, 2.5) == 15
        # Repetition 4: I(4) = 15 * 2.5 = 37.5 ≈ 38
        assert SuperMemo2.calculate_interval(4, 2.5) == 38

    def test_invalid_repetition_number_raises_error(self):
        """Repetition number must be >= 1"""
        with pytest.raises(ValueError, match="Repetition number must be >= 1"):
            SuperMemo2.calculate_interval(0, 2.5)
        with pytest.raises(ValueError, match="Repetition number must be >= 1"):
            SuperMemo2.calculate_interval(-1, 2.5)


class TestUpdateEasinessFactor:
    """Test EF update formula: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))"""

    def test_quality_5_increases_ef(self):
        """Quality 5 (perfect recall) increases EF"""
        # EF' = 2.5 + (0.1 - 0 * (0.08 + 0 * 0.02)) = 2.5 + 0.1 = 2.6
        # But max EF is 2.5, so should cap at 2.5
        new_ef = SuperMemo2.update_easiness_factor(2.5, 5)
        assert new_ef == 2.5  # Capped at MAX_EF

        # From lower EF, should increase
        new_ef = SuperMemo2.update_easiness_factor(2.0, 5)
        assert new_ef == 2.1

    def test_quality_4_maintains_ef(self):
        """Quality 4 (good recall) maintains EF"""
        # EF' = 2.5 + (0.1 - 1 * (0.08 + 1 * 0.02)) = 2.5 + (0.1 - 0.1) = 2.5
        new_ef = SuperMemo2.update_easiness_factor(2.5, 4)
        assert new_ef == 2.5

    def test_quality_3_decreases_ef_slightly(self):
        """Quality 3 (correct with difficulty) decreases EF slightly"""
        # EF' = 2.5 + (0.1 - 2 * (0.08 + 2 * 0.02))
        #     = 2.5 + (0.1 - 2 * 0.12)
        #     = 2.5 + (0.1 - 0.24)
        #     = 2.5 - 0.14 = 2.36
        new_ef = SuperMemo2.update_easiness_factor(2.5, 3)
        assert abs(new_ef - 2.36) < 0.01  # Float comparison

    def test_quality_0_drops_ef_significantly(self):
        """Quality 0 (complete failure) drops EF significantly"""
        # EF' = 2.5 + (0.1 - 5 * (0.08 + 5 * 0.02))
        #     = 2.5 + (0.1 - 5 * 0.18)
        #     = 2.5 + (0.1 - 0.9)
        #     = 2.5 - 0.8 = 1.7
        new_ef = SuperMemo2.update_easiness_factor(2.5, 0)
        assert abs(new_ef - 1.7) < 0.01

    def test_ef_cannot_go_below_min(self):
        """EF is clamped to MIN_EF (1.3)"""
        # From already low EF with quality 0
        new_ef = SuperMemo2.update_easiness_factor(1.3, 0)
        assert new_ef == 1.3  # Cannot go below 1.3

    def test_ef_cannot_exceed_max(self):
        """EF is clamped to MAX_EF (2.5)"""
        new_ef = SuperMemo2.update_easiness_factor(2.5, 5)
        assert new_ef == 2.5  # Cannot exceed 2.5

    def test_invalid_quality_raises_error(self):
        """Quality must be 0-5"""
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            SuperMemo2.update_easiness_factor(2.5, 6)
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            SuperMemo2.update_easiness_factor(2.5, -1)


class TestPerformanceToQuality:
    """Test mapping from exam percentage to SM-2 quality (0-5)"""

    def test_90_to_100_maps_to_quality_5(self):
        """90-100% (A*) → Quality 5"""
        assert SuperMemo2.performance_to_quality(100) == 5
        assert SuperMemo2.performance_to_quality(95) == 5
        assert SuperMemo2.performance_to_quality(90) == 5

    def test_80_to_89_maps_to_quality_4(self):
        """80-89% (A) → Quality 4"""
        assert SuperMemo2.performance_to_quality(89) == 4
        assert SuperMemo2.performance_to_quality(85) == 4
        assert SuperMemo2.performance_to_quality(80) == 4

    def test_70_to_79_maps_to_quality_3(self):
        """70-79% (B) → Quality 3"""
        assert SuperMemo2.performance_to_quality(79) == 3
        assert SuperMemo2.performance_to_quality(75) == 3
        assert SuperMemo2.performance_to_quality(70) == 3

    def test_60_to_69_maps_to_quality_2(self):
        """60-69% (C) → Quality 2"""
        assert SuperMemo2.performance_to_quality(69) == 2
        assert SuperMemo2.performance_to_quality(65) == 2
        assert SuperMemo2.performance_to_quality(60) == 2

    def test_50_to_59_maps_to_quality_1(self):
        """50-59% (D) → Quality 1"""
        assert SuperMemo2.performance_to_quality(59) == 1
        assert SuperMemo2.performance_to_quality(55) == 1
        assert SuperMemo2.performance_to_quality(50) == 1

    def test_below_50_maps_to_quality_0(self):
        """0-49% (E/U) → Quality 0"""
        assert SuperMemo2.performance_to_quality(49) == 0
        assert SuperMemo2.performance_to_quality(25) == 0
        assert SuperMemo2.performance_to_quality(0) == 0

    def test_boundary_values(self):
        """Test exact boundary values"""
        assert SuperMemo2.performance_to_quality(89.99) == 4  # Just below A*
        assert SuperMemo2.performance_to_quality(90.0) == 5   # Exactly A*
        assert SuperMemo2.performance_to_quality(79.99) == 3  # Just below A
        assert SuperMemo2.performance_to_quality(80.0) == 4   # Exactly A

    def test_invalid_percentage_raises_error(self):
        """Performance percentage must be 0-100"""
        with pytest.raises(ValueError, match="Performance percentage must be between 0 and 100"):
            SuperMemo2.performance_to_quality(101)
        with pytest.raises(ValueError, match="Performance percentage must be between 0 and 100"):
            SuperMemo2.performance_to_quality(-1)


class TestCalculateNextReview:
    """Test integrated workflow: performance → quality → EF → interval"""

    def test_perfect_performance_increases_ef_and_interval(self):
        """95% (A*) → Quality 5 → EF increases → longer interval"""
        # After completing repetition 1 with 95%, next interval is for rep 2
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(1, 2.5, 95)
        assert quality == 5
        assert new_ef == 2.5  # Already at max
        assert next_interval == 6  # Next interval is for repetition 2 = 6 days

        # After completing repetition 2 with perfect performance
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(2, 2.5, 95)
        assert quality == 5
        assert next_interval == 15  # Next interval is for repetition 3: I(3) = 6 * 2.5 = 15

    def test_good_performance_maintains_ef(self):
        """85% (A) → Quality 4 → EF stable"""
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(2, 2.5, 85)
        assert quality == 4
        assert new_ef == 2.5  # Maintained
        assert next_interval == 15  # I(3) = 6 * 2.5

    def test_poor_performance_decreases_ef_and_resets(self):
        """65% (C) → Quality 2 → EF decreases → reset to interval 1"""
        # Quality 2 < 3, so should reset to repetition 1
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(5, 2.5, 65)
        assert quality == 2
        assert new_ef < 2.5  # EF should decrease
        assert next_interval == 1  # Reset to interval 1 (quality < 3)

    def test_failure_resets_interval(self):
        """45% (F) → Quality 0 → Reset to interval 1"""
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(10, 2.5, 45)
        assert quality == 0
        assert new_ef < 2.5  # EF drops significantly
        assert next_interval == 1  # Reset to start

    def test_borderline_b_grade_continues_schedule(self):
        """70% (B) → Quality 3 → EF decreases slightly but continues"""
        next_interval, new_ef, quality = SuperMemo2.calculate_next_review(2, 2.5, 70)
        assert quality == 3
        assert new_ef < 2.5  # Slight decrease (2.36)
        # Quality 3 >= 3, so continues to next repetition
        # I(3) = 6 * 2.36 ≈ 14
        assert next_interval == 14


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""

    def test_calculate_interval_wrapper(self):
        """Convenience function works identically to class method"""
        from src.algorithms.supermemo2 import calculate_interval
        assert calculate_interval(1, 2.5) == SuperMemo2.calculate_interval(1, 2.5)
        assert calculate_interval(3, 2.5) == SuperMemo2.calculate_interval(3, 2.5)

    def test_update_easiness_factor_wrapper(self):
        """Convenience function works identically to class method"""
        from src.algorithms.supermemo2 import update_easiness_factor
        assert update_easiness_factor(2.5, 4) == SuperMemo2.update_easiness_factor(2.5, 4)

    def test_performance_to_quality_wrapper(self):
        """Convenience function works identically to class method"""
        from src.algorithms.supermemo2 import performance_to_quality
        assert performance_to_quality(85) == SuperMemo2.performance_to_quality(85)

    def test_calculate_next_review_wrapper(self):
        """Convenience function works identically to class method"""
        from src.algorithms.supermemo2 import calculate_next_review
        result1 = calculate_next_review(2, 2.5, 85)
        result2 = SuperMemo2.calculate_next_review(2, 2.5, 85)
        assert result1 == result2


class TestRealWorldScenarios:
    """Test realistic student learning scenarios"""

    def test_high_performer_schedule(self):
        """Simulate A* student (90%+) - intervals grow quickly"""
        ef = 2.5
        intervals = []

        # Simulate completing repetitions 1, 2, 3, 4, 5
        for rep in range(1, 6):
            interval, ef, quality = SuperMemo2.calculate_next_review(rep, ef, 95)
            intervals.append(interval)

        # After rep 1 → next interval is 6 (for rep 2)
        # After rep 2 → next interval is 15 (for rep 3)
        # After rep 3 → next interval is 38 (for rep 4)
        # After rep 4 → next interval is 95 (for rep 5)
        # After rep 5 → next interval is 238 (for rep 6)
        assert intervals[0] == 6    # After rep 1
        assert intervals[1] == 15   # After rep 2
        assert intervals[2] >= 37   # After rep 3: ~38
        assert intervals[3] >= 90   # After rep 4: ~95
        assert intervals[4] >= 230  # After rep 5: ~238

    def test_struggling_student_schedule(self):
        """Simulate struggling student (70-75%) - EF decreases, intervals grow slower"""
        ef = 2.5
        intervals = []

        # Simulate completing repetitions 1, 2, 3, 4 with 72% each time
        for rep in range(1, 5):
            interval, ef, quality = SuperMemo2.calculate_next_review(rep, ef, 72)
            intervals.append(interval)

        # Expected: EF decreases to ~2.36 → 2.22 → 2.08 → 1.94
        # Quality 3 (70-79%) allows continuation but intervals grow slower than high performer
        assert intervals[0] == 6    # After rep 1: 6 days (quality 3, EF=2.36)
        assert intervals[1] == 13   # After rep 2: 13 days (slower than 15 for high performer)
        assert intervals[2] == 25   # After rep 3: 25 days (slower than 38 for high performer)
        assert intervals[3] <= 50   # After rep 4: ~45 days (slower than 95 for high performer)
        assert ef < 2.0  # EF should have decreased to ~1.94

    def test_student_with_occasional_failure(self):
        """Simulate realistic pattern: good → good → fail → good"""
        ef = 2.5

        # Complete Rep 1 with 90% (A*) → next interval for rep 2
        i1, ef, q = SuperMemo2.calculate_next_review(1, ef, 90)
        assert i1 == 6 and q == 5  # Next interval is 6 (for rep 2)

        # Complete Rep 2 with 85% (A) → next interval for rep 3
        i2, ef, q = SuperMemo2.calculate_next_review(2, ef, 85)
        assert i2 == 15 and q == 4  # Next interval is 15 (for rep 3)

        # Complete Rep 3 with 45% (Fail) → quality < 3, reset to rep 1
        i3, ef, q = SuperMemo2.calculate_next_review(3, ef, 45)
        assert i3 == 1  # Reset: next interval is 1 (back to rep 1 interval)
        assert q == 0
        assert ef < 2.5  # EF dropped significantly

        # After reset, complete Rep 1 again with 88% (A) → next interval for rep 2
        i4, ef, q = SuperMemo2.calculate_next_review(1, ef, 88)
        assert i4 == 6  # Next interval is 6 (for rep 2)
        assert q == 4


# Run with: pytest backend/tests/unit/test_supermemo2.py -v
# Expected: ~40 tests, 100% coverage of SuperMemo2 class
