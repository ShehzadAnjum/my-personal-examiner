"""
Unit tests for confidence scoring algorithm.

Tests cover:
- Answer length mismatch detection
- Mark scheme coverage analysis
- Partial marks edge case detection
- Ambiguous language detection
- AO3 evaluation subjectivity handling
- Borderline marks detection
- Manual review threshold (70%)
- Integrated confidence calculations

Constitutional Compliance:
- A* Standard (confidence scoring ensures quality control)
- 100% algorithm coverage for production readiness
"""

import pytest
from src.algorithms.confidence_scoring import (
    ConfidenceScorer,
    calculate_confidence,
    needs_manual_review,
)


class TestCheckLengthMismatch:
    """Test answer length mismatch detection (Signal 1)."""

    def test_appropriate_length_no_penalty(self):
        """Answer with appropriate length should have no penalty."""
        # 5-mark question expects ~100 words (20 words/mark)
        # 80-120 words is acceptable range (80-120% of expected)
        answer = " ".join(["word"] * 100)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=5)
        assert penalty == 0

    def test_slightly_short_answer_no_penalty(self):
        """Answer at 50% of expected length (above 30% threshold) should be OK."""
        # 10-mark question expects 200 words, 100 words is 50%
        answer = " ".join(["word"] * 100)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=10)
        assert penalty == 0

    def test_very_short_answer_penalty(self):
        """Answer <30% of expected length should trigger penalty."""
        # 10-mark question expects 200 words, 40 words is 20%
        answer = " ".join(["word"] * 40)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=10)
        assert penalty == 20

    def test_empty_answer_penalty(self):
        """Empty answer should trigger maximum penalty."""
        penalty = ConfidenceScorer._check_length_mismatch("", max_marks=10)
        assert penalty == 20

    def test_excessively_long_answer_penalty(self):
        """Answer >300% of expected length should trigger penalty."""
        # 5-mark question expects 100 words, 400 words is 400%
        answer = " ".join(["word"] * 400)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=5)
        assert penalty == 20

    def test_exactly_at_lower_threshold(self):
        """Answer at exactly 30% of expected length should be OK (boundary)."""
        # 10-mark question expects 200 words, 60 words is exactly 30%
        answer = " ".join(["word"] * 60)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=10)
        assert penalty == 0

    def test_exactly_at_upper_threshold(self):
        """Answer at exactly 300% of expected length should be OK (boundary)."""
        # 5-mark question expects 100 words, 300 words is exactly 300%
        answer = " ".join(["word"] * 300)
        penalty = ConfidenceScorer._check_length_mismatch(answer, max_marks=5)
        assert penalty == 0


class TestCheckCoverage:
    """Test mark scheme coverage analysis (Signal 2)."""

    def test_full_coverage_no_penalty(self):
        """100% mark scheme coverage should have no penalty."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=10, required_points=10
        )
        assert penalty == 0

    def test_good_coverage_no_penalty(self):
        """85%+ coverage should have no penalty."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=9, required_points=10
        )
        assert penalty == 0

    def test_medium_coverage_small_penalty(self):
        """70-85% coverage should have small penalty."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=8, required_points=10
        )
        assert penalty == 5

    def test_low_coverage_medium_penalty(self):
        """50-70% coverage should have medium penalty."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=6, required_points=10
        )
        assert penalty == 15

    def test_very_low_coverage_high_penalty(self):
        """<50% coverage should have high penalty."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=4, required_points=10
        )
        assert penalty == 25

    def test_zero_required_points_no_penalty(self):
        """Edge case: 0 required points should not cause error."""
        penalty = ConfidenceScorer._check_coverage(
            identified_points=0, required_points=0
        )
        assert penalty == 0

    def test_exactly_at_thresholds(self):
        """Test exact boundary values."""
        # Exactly 50% falls into 50-70% range (not <50%)
        assert ConfidenceScorer._check_coverage(5, 10) == 15
        # Exactly 70% falls into 70-85% range (not <70%)
        assert ConfidenceScorer._check_coverage(7, 10) == 5
        # Exactly 85% is good coverage (not <85%)
        assert ConfidenceScorer._check_coverage(17, 20) == 0


class TestCheckPartialMarks:
    """Test partial marks edge case detection (Signal 3)."""

    def test_zero_marks_no_penalty(self):
        """0 marks is clear-cut decision, no penalty."""
        penalty = ConfidenceScorer._check_partial_marks(
            marks_awarded=0, max_marks=10
        )
        assert penalty == 0

    def test_full_marks_no_penalty(self):
        """Full marks is clear-cut decision, no penalty."""
        penalty = ConfidenceScorer._check_partial_marks(
            marks_awarded=10, max_marks=10
        )
        assert penalty == 0

    def test_partial_marks_penalty(self):
        """Partial marks (1-9 out of 10) should trigger penalty."""
        for marks in range(1, 10):
            penalty = ConfidenceScorer._check_partial_marks(
                marks_awarded=marks, max_marks=10
            )
            assert penalty == 15

    def test_partial_marks_different_scales(self):
        """Partial marks should trigger penalty regardless of scale."""
        # 3/6 marks
        assert ConfidenceScorer._check_partial_marks(3, 6) == 15
        # 10/25 marks
        assert ConfidenceScorer._check_partial_marks(10, 25) == 15
        # 1/2 marks
        assert ConfidenceScorer._check_partial_marks(1, 2) == 15


class TestCheckAmbiguousLanguage:
    """Test ambiguous language detection (Signal 4)."""

    def test_clear_answer_no_penalty(self):
        """Clear, precise answer should have no penalty."""
        answer = "Supply increases when price rises due to profit motive."
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        assert penalty == 0

    def test_few_ambiguous_phrases_no_penalty(self):
        """1-3 ambiguous phrases should be acceptable."""
        answer = "This might increase supply. Perhaps demand shifts."
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        # Contains "might" and "perhaps" (2 phrases)
        assert penalty == 0

    def test_many_ambiguous_phrases_penalty(self):
        """More than 3 ambiguous phrases should trigger penalty."""
        answer = "Maybe demand might possibly increase. Perhaps some factors could be involved."
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        # Contains "Maybe", "might", "possibly", "Perhaps", "some", "could" (6 phrases)
        assert penalty == 20

    def test_case_insensitive_detection(self):
        """Ambiguous phrase detection should be case-insensitive."""
        answer = "MIGHT increase. MAYBE decrease. POSSIBLY stable. PERHAPS not."
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        # 4 ambiguous phrases (all uppercase)
        assert penalty == 20

    def test_all_ambiguous_phrase_types(self):
        """Test detection of all predefined ambiguous phrases."""
        ambiguous_phrases = [
            "might", "maybe", "possibly", "could be", "perhaps",
            "some", "few", "many", "several", "various",
            "etc.", "and so on", "things like", "such as"
        ]
        # Use first 4 phrases (triggers penalty at >3)
        answer = " ".join(ambiguous_phrases[:4])
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        assert penalty == 20

    def test_exact_threshold(self):
        """Exactly 3 ambiguous phrases should NOT trigger penalty."""
        answer = "might increase. maybe decrease. perhaps stable."
        penalty = ConfidenceScorer._check_ambiguous_language(answer)
        # Exactly 3 phrases
        assert penalty == 0

        # 4 phrases should trigger penalty
        answer_4 = "might increase. maybe decrease. perhaps stable. possibly not."
        penalty_4 = ConfidenceScorer._check_ambiguous_language(answer_4)
        assert penalty_4 == 20


class TestCheckBorderlineMarks:
    """Test borderline marks detection (Signal 6)."""

    def test_clear_pass_no_penalty(self):
        """Clear pass (>52%) should have no penalty."""
        penalty = ConfidenceScorer._check_borderline_marks(
            marks_awarded=8, max_marks=10
        )
        assert penalty == 0  # 80%

    def test_clear_fail_no_penalty(self):
        """Clear fail (<48%) should have no penalty."""
        penalty = ConfidenceScorer._check_borderline_marks(
            marks_awarded=4, max_marks=10
        )
        assert penalty == 0  # 40%

    def test_borderline_marks_penalty(self):
        """Marks in 48-52% range should trigger penalty."""
        # 50% (exactly borderline)
        assert ConfidenceScorer._check_borderline_marks(5, 10) == 15
        # 48% (lower boundary)
        assert ConfidenceScorer._check_borderline_marks(48, 100) == 15
        # 52% (upper boundary)
        assert ConfidenceScorer._check_borderline_marks(52, 100) == 15

    def test_just_below_borderline_no_penalty(self):
        """47% should have no penalty (below borderline)."""
        penalty = ConfidenceScorer._check_borderline_marks(47, 100)
        assert penalty == 0

    def test_just_above_borderline_no_penalty(self):
        """53% should have no penalty (above borderline)."""
        penalty = ConfidenceScorer._check_borderline_marks(53, 100)
        assert penalty == 0

    def test_zero_max_marks_no_penalty(self):
        """Edge case: 0 max_marks should not cause error."""
        penalty = ConfidenceScorer._check_borderline_marks(0, 0)
        assert penalty == 0

    def test_borderline_different_scales(self):
        """Borderline detection should work on different mark scales."""
        # 6/12 = 50%
        assert ConfidenceScorer._check_borderline_marks(6, 12) == 15
        # 12/25 = 48%
        assert ConfidenceScorer._check_borderline_marks(12, 25) == 15
        # 13/25 = 52%
        assert ConfidenceScorer._check_borderline_marks(13, 25) == 15


class TestCalculateConfidence:
    """Test integrated confidence calculation with all signals."""

    def test_perfect_scenario_100_confidence(self):
        """Ideal answer should have 100% confidence."""
        question = {"max_marks": 10}
        marking_details = {
            "identified_points": 10,
            "required_points": 10,
            "ao3_present": False,
        }
        # Appropriate length (200 words), full marks, good coverage
        answer = " ".join(["word"] * 200)

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=10,
            max_marks=10,
            student_answer=answer,
            question=question,
            marking_details=marking_details,
        )

        assert confidence == 100

    def test_worst_case_scenario_low_confidence(self):
        """Problematic answer should have very low confidence."""
        question = {"max_marks": 10}
        marking_details = {
            "identified_points": 2,  # Low coverage
            "required_points": 10,
            "ao3_present": True,  # AO3 subjectivity
        }
        # Empty answer, partial marks (5/10 = 50% borderline), low coverage
        answer = "maybe possibly perhaps might could be some few"  # Ambiguous

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=5,
            max_marks=10,
            student_answer=answer,
            question=question,
            marking_details=marking_details,
        )

        # Expected penalties:
        # - Empty answer length: -20
        # - Low coverage (<50%): -25
        # - Partial marks: -15
        # - Ambiguous language (>3): -20
        # - AO3 present: -10
        # - Borderline (50%): -15
        # Total: 100 - 105 = -5 → clamped to 0
        assert confidence == 0

    def test_moderate_confidence_scenario(self):
        """Typical answer with some issues should have moderate confidence."""
        question = {"max_marks": 12}
        marking_details = {
            "identified_points": 8,  # 67% coverage (medium penalty)
            "required_points": 12,
            "ao3_present": True,
        }
        # Appropriate length, partial marks, some ambiguity
        answer = " ".join(["word"] * 240) + " maybe perhaps"

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=8,
            max_marks=12,
            student_answer=answer,
            question=question,
            marking_details=marking_details,
        )

        # Expected penalties:
        # - Length: 0 (appropriate)
        # - Coverage 67%: -15 (50-70% range)
        # - Partial marks: -15
        # - Ambiguous (2 phrases): 0
        # - AO3: -10
        # - Borderline 67%: 0
        # Total: 100 - 40 = 60
        assert confidence == 60

    def test_ao3_reduces_confidence(self):
        """AO3 questions should have lower confidence due to subjectivity."""
        question = {"max_marks": 12}
        answer = " ".join(["word"] * 240)

        # Without AO3
        details_no_ao3 = {
            "identified_points": 12,
            "required_points": 12,
            "ao3_present": False,
        }
        confidence_no_ao3 = ConfidenceScorer.calculate_confidence(
            marks_awarded=12, max_marks=12, student_answer=answer,
            question=question, marking_details=details_no_ao3
        )

        # With AO3
        details_with_ao3 = {
            "identified_points": 12,
            "required_points": 12,
            "ao3_present": True,
        }
        confidence_with_ao3 = ConfidenceScorer.calculate_confidence(
            marks_awarded=12, max_marks=12, student_answer=answer,
            question=question, marking_details=details_with_ao3
        )

        # AO3 should reduce confidence by 10 points
        assert confidence_no_ao3 - confidence_with_ao3 == 10

    def test_confidence_clamped_to_0_100_range(self):
        """Confidence should always be in 0-100 range."""
        question = {"max_marks": 10}

        # Test lower bound (many penalties)
        details_low = {
            "identified_points": 1,
            "required_points": 10,
            "ao3_present": True,
        }
        confidence_low = ConfidenceScorer.calculate_confidence(
            marks_awarded=5, max_marks=10, student_answer="",
            question=question, marking_details=details_low
        )
        assert 0 <= confidence_low <= 100

        # Test upper bound (no penalties)
        details_high = {
            "identified_points": 10,
            "required_points": 10,
            "ao3_present": False,
        }
        confidence_high = ConfidenceScorer.calculate_confidence(
            marks_awarded=10, max_marks=10, student_answer=" ".join(["word"] * 200),
            question=question, marking_details=details_high
        )
        assert 0 <= confidence_high <= 100
        assert confidence_high == 100

    def test_missing_marking_details_fields(self):
        """Missing fields in marking_details should use defaults."""
        question = {"max_marks": 10}
        # Missing identified_points, required_points, ao3_present
        marking_details = {}
        answer = " ".join(["word"] * 200)

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=10, max_marks=10, student_answer=answer,
            question=question, marking_details=marking_details
        )

        # Should use defaults: identified_points=0, required_points=1, ao3_present=False
        # Coverage: 0/1 = 0% → -25 penalty
        # Other penalties: 0 (full marks, appropriate length)
        assert confidence == 75


class TestNeedsManualReview:
    """Test manual review threshold (70%)."""

    def test_low_confidence_needs_review(self):
        """Confidence <70% should trigger manual review."""
        assert ConfidenceScorer.needs_manual_review(65) is True
        assert ConfidenceScorer.needs_manual_review(50) is True
        assert ConfidenceScorer.needs_manual_review(0) is True

    def test_high_confidence_no_review(self):
        """Confidence ≥70% should not need review."""
        assert ConfidenceScorer.needs_manual_review(70) is False
        assert ConfidenceScorer.needs_manual_review(85) is False
        assert ConfidenceScorer.needs_manual_review(100) is False

    def test_exactly_at_threshold(self):
        """Exactly 70% should NOT need review (boundary)."""
        assert ConfidenceScorer.needs_manual_review(70) is False

    def test_one_point_below_threshold(self):
        """69% should need review."""
        assert ConfidenceScorer.needs_manual_review(69) is True


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_calculate_confidence_function(self):
        """Convenience function should match class method."""
        question = {"max_marks": 10}
        marking_details = {
            "identified_points": 10,
            "required_points": 10,
            "ao3_present": False,
        }
        answer = " ".join(["word"] * 200)

        confidence = calculate_confidence(
            marks_awarded=10, max_marks=10, student_answer=answer,
            question=question, marking_details=marking_details
        )

        assert confidence == 100

    def test_needs_manual_review_function(self):
        """Convenience function should match class method."""
        assert needs_manual_review(65) is True
        assert needs_manual_review(75) is False


class TestRealWorldScenarios:
    """Test realistic Cambridge Economics 9708 marking scenarios."""

    def test_high_quality_a_star_answer(self):
        """A* answer should have high confidence (≥85%)."""
        question = {"max_marks": 12}
        marking_details = {
            "identified_points": 12,
            "required_points": 12,
            "ao3_present": True,  # AO3 evaluation question
        }
        # Well-developed answer with diagrams and evaluation
        answer = (
            "A maximum price (price ceiling) set below equilibrium creates excess demand. "
            "At the maximum price, quantity demanded exceeds quantity supplied, leading to shortages. "
            "This can be demonstrated using a supply and demand diagram. "
            "The welfare effects include consumer surplus gains for those who obtain the good, "
            "but deadweight loss from reduced market efficiency. "
            "However, the policy may achieve equity objectives by making essential goods affordable. "
            "The effectiveness depends on enforcement and whether black markets emerge. "
        ) * 3  # ~240 words

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=12, max_marks=12, student_answer=answer,
            question=question, marking_details=marking_details
        )

        # Expected penalties: -10 (AO3 only)
        # Total: 100 - 10 = 90
        assert confidence == 90
        assert not ConfidenceScorer.needs_manual_review(confidence)

    def test_weak_answer_needs_review(self):
        """Weak answer with partial marks should need review."""
        question = {"max_marks": 12}
        marking_details = {
            "identified_points": 4,  # Low coverage (33%)
            "required_points": 12,
            "ao3_present": False,
        }
        # Vague, short answer
        answer = "Maybe demand increases. Some factors might affect supply. Possibly prices could change."

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=5, max_marks=12, student_answer=answer,
            question=question, marking_details=marking_details
        )

        # Expected penalties:
        # - Length (30 words for 12 marks, expect 240): -20
        # - Coverage 33%: -25
        # - Partial marks: -15
        # - Ambiguous (maybe, some, might, possibly, could = 5): -20
        # Total: 100 - 80 = 20
        assert confidence == 20
        assert ConfidenceScorer.needs_manual_review(confidence)

    def test_borderline_pass_answer(self):
        """Answer near pass/fail boundary should need review."""
        question = {"max_marks": 25}
        marking_details = {
            "identified_points": 10,
            "required_points": 15,
            "ao3_present": False,
        }
        # Decent length, borderline marks (50%)
        answer = " ".join(["word"] * 500)

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=13,  # 52% (just at borderline)
            max_marks=25,
            student_answer=answer,
            question=question,
            marking_details=marking_details,
        )

        # Expected penalties:
        # - Length: 0 (appropriate)
        # - Coverage 67%: -15 (50-70%)
        # - Partial marks: -15
        # - Ambiguous: 0
        # - Borderline 52%: -15
        # Total: 100 - 45 = 55
        assert confidence == 55
        assert ConfidenceScorer.needs_manual_review(confidence)

    def test_perfect_textbook_answer(self):
        """Perfect textbook answer should have maximum confidence."""
        question = {"max_marks": 8}
        marking_details = {
            "identified_points": 8,
            "required_points": 8,
            "ao3_present": False,
        }
        # Clear, comprehensive answer with all points
        answer = (
            "The law of demand states that as price increases, quantity demanded decreases, "
            "ceteris paribus. This inverse relationship occurs because of two effects: "
            "the substitution effect (consumers switch to cheaper alternatives) and "
            "the income effect (higher prices reduce real purchasing power). "
            "This can be illustrated using a downward-sloping demand curve."
        ) * 2  # ~160 words for 8 marks

        confidence = ConfidenceScorer.calculate_confidence(
            marks_awarded=8, max_marks=8, student_answer=answer,
            question=question, marking_details=marking_details
        )

        assert confidence == 100
        assert not ConfidenceScorer.needs_manual_review(confidence)
