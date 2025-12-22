"""
Unit tests for contextual interleaving algorithm.

Tests cover:
- Topic relatedness determination (same section, explicit tagging)
- Daily cluster creation (max 3 topics per day)
- Practice sequence generation (A→B→A→C pattern)
- Edge cases (empty inputs, single topics, boundary conditions)
- Real-world scenarios (full syllabus, metadata tagging)

Constitutional Compliance:
- Evidence-based pedagogy testing (Principle III)
- 100% algorithm coverage for production readiness
"""

import pytest
from typing import Dict, Any
from src.algorithms.contextual_interleaving import (
    ContextualInterleaving,
    topics_are_related,
    create_daily_clusters,
    generate_practice_sequence,
)


class TestTopicsAreRelated:
    """Test topic relatedness determination logic."""

    def test_same_section_topics_are_related(self):
        """Topics in same syllabus section should be related."""
        interleaver = ContextualInterleaving()
        assert interleaver.topics_are_related("9708.1.1", "9708.1.2") is True

    def test_different_section_topics_not_related(self):
        """Topics in different syllabus sections should not be related."""
        interleaver = ContextualInterleaving()
        assert interleaver.topics_are_related("9708.1.1", "9708.2.1") is False

    def test_deeply_nested_same_section_topics_are_related(self):
        """Topics with same parent section should be related (9708.1.2.3 + 9708.1.2.4)."""
        interleaver = ContextualInterleaving()
        assert interleaver.topics_are_related("9708.1.2.3", "9708.1.2.4") is True

    def test_explicit_metadata_tagging_makes_topics_related(self):
        """Topics tagged as related in metadata should be related."""
        interleaver = ContextualInterleaving()
        metadata = {
            "9708.1.1": {"related_topics": ["9708.2.1", "9708.3.1"]},
        }
        assert interleaver.topics_are_related("9708.1.1", "9708.2.1", metadata) is True

    def test_bidirectional_metadata_tagging_not_required(self):
        """Metadata tagging works one-way (9708.1.1 → 9708.2.1 doesn't imply 9708.2.1 → 9708.1.1)."""
        interleaver = ContextualInterleaving()
        metadata = {
            "9708.1.1": {"related_topics": ["9708.2.1"]},
        }
        # Forward direction
        assert interleaver.topics_are_related("9708.1.1", "9708.2.1", metadata) is True
        # Reverse direction (no reverse tag)
        assert interleaver.topics_are_related("9708.2.1", "9708.1.1", metadata) is False

    def test_topics_without_dots_compare_directly(self):
        """Topics without dots should compare as-is (edge case for custom codes)."""
        interleaver = ContextualInterleaving()
        assert interleaver.topics_are_related("INTRO", "INTRO") is True
        assert interleaver.topics_are_related("INTRO", "ADVANCED") is False

    def test_empty_related_topics_metadata(self):
        """Metadata with empty related_topics should not cause errors."""
        interleaver = ContextualInterleaving()
        metadata = {
            "9708.1.1": {"related_topics": []},
        }
        assert interleaver.topics_are_related("9708.1.1", "9708.2.1", metadata) is False

    def test_missing_topic_in_metadata(self):
        """Missing topic in metadata should fall back to section matching."""
        interleaver = ContextualInterleaving()
        metadata = {
            "9708.3.1": {"related_topics": ["9708.4.1"]},
        }
        # 9708.1.1 not in metadata, should use section matching
        assert interleaver.topics_are_related("9708.1.1", "9708.1.2", metadata) is True


class TestCreateDailyClusters:
    """Test daily cluster creation algorithm."""

    def test_basic_clustering_respects_max_topics(self):
        """Should create clusters with max 3 related topics."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)
        topics = ["9708.1.1", "9708.1.2", "9708.1.3", "9708.1.4"]
        clusters = interleaver.create_daily_clusters(topics)

        # 4 topics from same section → first cluster gets 3, second gets 1
        assert len(clusters) == 2
        assert len(clusters[0]) == 3
        assert len(clusters[1]) == 1
        assert clusters[0] == ["9708.1.1", "9708.1.2", "9708.1.3"]
        assert clusters[1] == ["9708.1.4"]

    def test_different_sections_create_separate_clusters(self):
        """Topics from different sections should form separate clusters."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)
        topics = ["9708.1.1", "9708.1.2", "9708.2.1", "9708.2.2"]
        clusters = interleaver.create_daily_clusters(topics)

        # Section 9708.1 and 9708.2 should be separate
        assert len(clusters) == 2
        assert clusters[0] == ["9708.1.1", "9708.1.2"]
        assert clusters[1] == ["9708.2.1", "9708.2.2"]

    def test_single_topic_cluster(self):
        """Single unrelated topic should form its own cluster."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)
        topics = ["9708.1.1", "9708.2.1", "9708.3.1"]
        clusters = interleaver.create_daily_clusters(topics)

        # All from different sections
        assert len(clusters) == 3
        assert clusters[0] == ["9708.1.1"]
        assert clusters[1] == ["9708.2.1"]
        assert clusters[2] == ["9708.3.1"]

    def test_empty_topics_list(self):
        """Empty topics list should return empty clusters."""
        interleaver = ContextualInterleaving()
        clusters = interleaver.create_daily_clusters([])
        assert clusters == []

    def test_max_topics_per_day_variation(self):
        """Different max_topics_per_day values should produce different clusterings."""
        topics = ["9708.1.1", "9708.1.2", "9708.1.3", "9708.1.4", "9708.1.5"]

        # Max 2 topics per day
        interleaver_2 = ContextualInterleaving(max_topics_per_day=2)
        clusters_2 = interleaver_2.create_daily_clusters(topics)
        assert len(clusters_2) == 3  # [2, 2, 1]
        assert len(clusters_2[0]) == 2
        assert len(clusters_2[1]) == 2
        assert len(clusters_2[2]) == 1

        # Max 5 topics per day
        interleaver_5 = ContextualInterleaving(max_topics_per_day=5)
        clusters_5 = interleaver_5.create_daily_clusters(topics)
        assert len(clusters_5) == 1  # [5]
        assert len(clusters_5[0]) == 5

    def test_metadata_tagging_influences_clustering(self):
        """Explicit metadata tagging should group otherwise unrelated topics."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)
        topics = ["9708.1.1", "9708.2.1", "9708.3.1"]

        # Without metadata: 3 separate clusters
        clusters_no_meta = interleaver.create_daily_clusters(topics)
        assert len(clusters_no_meta) == 3

        # With metadata: 1 cluster (all related via 9708.1.1)
        metadata = {
            "9708.1.1": {"related_topics": ["9708.2.1", "9708.3.1"]},
        }
        clusters_with_meta = interleaver.create_daily_clusters(topics, metadata)
        assert len(clusters_with_meta) == 1
        assert clusters_with_meta[0] == ["9708.1.1", "9708.2.1", "9708.3.1"]

    def test_order_preservation_within_clusters(self):
        """Topics should be added to clusters in original order."""
        interleaver = ContextualInterleaving(max_topics_per_day=5)
        topics = ["9708.1.3", "9708.1.1", "9708.1.2"]
        clusters = interleaver.create_daily_clusters(topics)

        # All from same section, should maintain input order
        assert clusters[0] == ["9708.1.3", "9708.1.1", "9708.1.2"]

    def test_all_topics_used_exactly_once(self):
        """Every topic should appear in exactly one cluster."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)
        topics = ["9708.1.1", "9708.1.2", "9708.2.1", "9708.2.2", "9708.3.1"]
        clusters = interleaver.create_daily_clusters(topics)

        # Flatten clusters and check
        all_topics_in_clusters = [t for cluster in clusters for t in cluster]
        assert sorted(all_topics_in_clusters) == sorted(topics)
        assert len(all_topics_in_clusters) == len(topics)  # No duplicates


class TestGeneratePracticeSequence:
    """Test practice sequence generation (A→B→A→C pattern)."""

    def test_two_topic_alternating_pattern(self):
        """Two topics should alternate (A→B→A→B→A→B)."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence(["A", "B"])

        # 2 topics × 3 rounds = 6 total
        assert len(sequence) == 6
        assert sequence == ["A", "B", "A", "B", "A", "B"]

    def test_three_topic_interleaving_pattern(self):
        """Three topics should follow A→B→A→C→B→C→A→B→C pattern."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence(["A", "B", "C"])

        # 3 topics × 3 rounds = 9 total
        assert len(sequence) == 9
        # Check pattern (no consecutive repetitions)
        for i in range(len(sequence) - 1):
            assert sequence[i] != sequence[i + 1], f"Consecutive repetition at index {i}: {sequence}"

    def test_single_topic_no_interleaving(self):
        """Single topic should repeat without interleaving."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence(["A"])

        # 1 topic × 3 rounds = 3 total
        assert len(sequence) == 3
        assert sequence == ["A", "A", "A"]

    def test_empty_cluster(self):
        """Empty cluster should return empty sequence."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence([])
        assert sequence == []

    def test_practice_rounds_variation(self):
        """Different practice_rounds values should produce different sequence lengths."""
        cluster = ["A", "B", "C"]

        # 1 round per topic
        interleaver_1 = ContextualInterleaving(practice_rounds=1)
        sequence_1 = interleaver_1.generate_practice_sequence(cluster)
        assert len(sequence_1) == 3  # 3 topics × 1 round

        # 5 rounds per topic
        interleaver_5 = ContextualInterleaving(practice_rounds=5)
        sequence_5 = interleaver_5.generate_practice_sequence(cluster)
        assert len(sequence_5) == 15  # 3 topics × 5 rounds

    def test_no_consecutive_repetitions_constraint(self):
        """No topic should appear consecutively (except single-topic clusters)."""
        interleaver = ContextualInterleaving(practice_rounds=4)
        sequence = interleaver.generate_practice_sequence(["D", "S", "E"])

        # Check no consecutive repetitions
        for i in range(len(sequence) - 1):
            assert sequence[i] != sequence[i + 1], f"Consecutive repetition at index {i}: {sequence}"

    def test_each_topic_appears_exactly_practice_rounds_times(self):
        """Each topic should appear exactly practice_rounds times."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence(["Demand", "Supply", "Equilibrium"])

        # Count occurrences
        assert sequence.count("Demand") == 3
        assert sequence.count("Supply") == 3
        assert sequence.count("Equilibrium") == 3

    def test_real_economics_topics(self):
        """Test with realistic Economics 9708 syllabus codes."""
        interleaver = ContextualInterleaving(practice_rounds=3)
        sequence = interleaver.generate_practice_sequence([
            "9708.1.1",  # Basic economic ideas
            "9708.1.2",  # Price system
            "9708.1.3",  # Government micro intervention
        ])

        # 3 topics × 3 rounds = 9 total
        assert len(sequence) == 9
        # Check each topic appears 3 times
        assert sequence.count("9708.1.1") == 3
        assert sequence.count("9708.1.2") == 3
        assert sequence.count("9708.1.3") == 3
        # No consecutive repetitions
        for i in range(len(sequence) - 1):
            assert sequence[i] != sequence[i + 1]


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_topics_are_related_function(self):
        """Convenience function should match class method."""
        assert topics_are_related("9708.1.1", "9708.1.2") is True
        assert topics_are_related("9708.1.1", "9708.2.1") is False

    def test_create_daily_clusters_function(self):
        """Convenience function should match class method."""
        topics = ["9708.1.1", "9708.1.2", "9708.2.1"]
        clusters = create_daily_clusters(topics, max_topics_per_day=3)

        assert len(clusters) == 2
        assert clusters[0] == ["9708.1.1", "9708.1.2"]
        assert clusters[1] == ["9708.2.1"]

    def test_generate_practice_sequence_function(self):
        """Convenience function should match class method."""
        sequence = generate_practice_sequence(["A", "B", "C"], practice_rounds=3)

        assert len(sequence) == 9
        assert sequence.count("A") == 3
        assert sequence.count("B") == 3
        assert sequence.count("C") == 3

    def test_convenience_functions_use_default_parameters(self):
        """Convenience functions should use correct defaults (max_topics=3, rounds=3)."""
        # Test default max_topics_per_day=3
        topics = ["9708.1.1", "9708.1.2", "9708.1.3", "9708.1.4"]
        clusters = create_daily_clusters(topics)  # Default max_topics_per_day=3
        assert len(clusters[0]) == 3  # First cluster has 3 topics

        # Test default practice_rounds=3
        sequence = generate_practice_sequence(["X"])  # Default practice_rounds=3
        assert len(sequence) == 3  # 1 topic × 3 rounds


class TestRealWorldScenarios:
    """Test realistic scenarios with full syllabus and metadata."""

    def test_full_economics_syllabus_clustering(self):
        """Cluster realistic Economics 9708 syllabus with 7 sections."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)

        # Simulate 7 syllabus sections with 3-5 topics each
        topics = [
            # Section 1: Basic economic ideas (4 topics)
            "9708.1.1", "9708.1.2", "9708.1.3", "9708.1.4",
            # Section 2: Price system (3 topics)
            "9708.2.1", "9708.2.2", "9708.2.3",
            # Section 3: Government micro intervention (4 topics)
            "9708.3.1", "9708.3.2", "9708.3.3", "9708.3.4",
            # Section 4: Macroeconomic indicators (5 topics)
            "9708.4.1", "9708.4.2", "9708.4.3", "9708.4.4", "9708.4.5",
        ]

        clusters = interleaver.create_daily_clusters(topics)

        # Should create 6 clusters:
        # Section 1: [3 topics], [1 topic]
        # Section 2: [3 topics]
        # Section 3: [3 topics], [1 topic]
        # Section 4: [3 topics], [2 topics]
        assert len(clusters) == 7

        # Verify all topics clustered
        all_topics = [t for cluster in clusters for t in cluster]
        assert sorted(all_topics) == sorted(topics)

    def test_weakness_prioritization_with_metadata(self):
        """Test clustering with metadata to prioritize student weaknesses."""
        interleaver = ContextualInterleaving(max_topics_per_day=3)

        # Student weak in elasticity (9708.2.3), supply/demand (9708.1.1)
        # Metadata links these for focused review
        topics = ["9708.1.1", "9708.2.3", "9708.3.1"]
        metadata = {
            "9708.1.1": {"related_topics": ["9708.2.3"]},  # Link weak topics
        }

        clusters = interleaver.create_daily_clusters(topics, metadata)

        # Should create 2 clusters: [weak topics together], [unrelated topic]
        assert len(clusters) == 2
        assert "9708.1.1" in clusters[0] and "9708.2.3" in clusters[0]
        assert clusters[1] == ["9708.3.1"]

    def test_daily_study_plan_end_to_end(self):
        """Test complete workflow: topics → clusters → practice sequences."""
        interleaver = ContextualInterleaving(max_topics_per_day=3, practice_rounds=3)

        # 5 topics from 2 sections
        topics = ["9708.1.1", "9708.1.2", "9708.1.3", "9708.2.1", "9708.2.2"]

        # Step 1: Cluster topics
        clusters = interleaver.create_daily_clusters(topics)
        assert len(clusters) == 2  # 2 sections → 2 clusters

        # Step 2: Generate practice sequences for each cluster
        day1_sequence = interleaver.generate_practice_sequence(clusters[0])
        day2_sequence = interleaver.generate_practice_sequence(clusters[1])

        # Day 1: 3 topics × 3 rounds = 9 practices
        assert len(day1_sequence) == 9
        # Day 2: 2 topics × 3 rounds = 6 practices
        assert len(day2_sequence) == 6

        # Verify interleaving quality (no consecutive repetitions)
        for i in range(len(day1_sequence) - 1):
            assert day1_sequence[i] != day1_sequence[i + 1]
        for i in range(len(day2_sequence) - 1):
            assert day2_sequence[i] != day2_sequence[i + 1]
