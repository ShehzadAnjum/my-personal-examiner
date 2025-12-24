---
name: supermemo2-scheduling
description: SuperMemo 2 spaced repetition algorithm for review scheduling. Use when implementing spaced repetition, review scheduling, or memory optimization features.
---

# Skill: SuperMemo 2 (SM-2) Spaced Repetition

**Domain**: Learning Science & Memory Algorithms
**Purpose**: Implement production-quality SM-2 algorithm for study scheduling
**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles - Planner Agent)

---

## Overview

SuperMemo 2 (SM-2) is a spaced repetition algorithm that optimizes review intervals based on performance, achieving 30% better long-term retention than massed practice.

**Implemented in**: `backend/src/algorithms/supermemo2.py`, `backend/src/services/planning_service.py`

---

## Algorithm Specification

### Interval Calculation

**Formula**:
- I(1) = 1 day (first review after learning)
- I(2) = 6 days (second review)
- I(n) = I(n-1) × EF (all subsequent reviews)

**Where**:
- I(n) = Interval before nth review (in days)
- EF = Easiness Factor (1.3 ≤ EF ≤ 2.5, default 2.5)

**Example**:
```
Repetition 1: Study today → Review in 1 day
Repetition 2: Review → Next review in 6 days
Repetition 3 (EF=2.5): Review → Next review in 6 × 2.5 = 15 days
Repetition 4 (EF=2.5): Review → Next review in 15 × 2.5 = 38 days
```

---

### Easiness Factor (EF) Update

**Formula**:
```
EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
```

**Where**:
- EF' = New easiness factor
- EF = Current easiness factor
- q = Quality of recall (0-5 scale)

**Constraints**:
- If EF' < 1.3, set EF' = 1.3 (minimum)
- If EF' > 2.5, set EF' = 2.5 (maximum)

**Quality (q) Mapping from Exam Performance**:
```python
def performance_to_quality(percentage: float) -> int:
    if percentage >= 90: return 5  # A* - Perfect recall
    if percentage >= 80: return 4  # A - Good recall
    if percentage >= 70: return 3  # B - Acceptable recall (min passing)
    if percentage >= 60: return 2  # C - Difficult recall
    if percentage >= 50: return 1  # D - Very difficult recall
    return 0  # E/U - Failed recall
```

---

### EF Impact Examples

**Quality 5 (90-100%, A*)**:
```
EF' = 2.5 + (0.1 - (5-5) × ...) = 2.5 + 0.1 = 2.6 → capped at 2.5
Effect: EF stays at max (interval grows fastest)
```

**Quality 4 (80-89%, A)**:
```
EF' = 2.5 + (0.1 - (5-4) × (0.08 + 1 × 0.02)) = 2.5 + 0.0 = 2.5
Effect: EF unchanged (stable retention)
```

**Quality 3 (70-79%, B)**:
```
EF' = 2.5 + (0.1 - (5-3) × (0.08 + 2 × 0.02)) = 2.5 + (0.1 - 2 × 0.12) = 2.5 - 0.14 = 2.36
Effect: EF decreases slightly (needs more reviews)
```

**Quality 0 (0-49%, Fail)**:
```
EF' = 2.5 + (0.1 - (5-0) × (0.08 + 5 × 0.02)) = 2.5 + (0.1 - 5 × 0.18) = 2.5 - 0.8 = 1.7
Effect: EF drops significantly (reset to shorter intervals)
```

---

## Implementation Guide

### Class Structure

```python
class SuperMemo2:
    MIN_EF = 1.3
    MAX_EF = 2.5
    DEFAULT_EF = 2.5
    
    @staticmethod
    def calculate_interval(repetition_number: int, easiness_factor: float) -> int:
        """Calculate days until next review"""
        if repetition_number == 1:
            return 1
        elif repetition_number == 2:
            return 6
        else:
            previous = SuperMemo2.calculate_interval(repetition_number - 1, easiness_factor)
            return round(previous * easiness_factor)
    
    @staticmethod
    def update_easiness_factor(current_ef: float, quality: int) -> float:
        """Update EF based on performance quality (0-5)"""
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        return max(SuperMemo2.MIN_EF, min(SuperMemo2.MAX_EF, new_ef))
    
    @staticmethod
    def performance_to_quality(performance_percentage: float) -> int:
        """Map exam % to SM-2 quality (0-5)"""
        if performance_percentage >= 90: return 5
        elif performance_percentage >= 80: return 4
        elif performance_percentage >= 70: return 3
        elif performance_percentage >= 60: return 2
        elif performance_percentage >= 50: return 1
        else: return 0
```

---

## Usage in Study Planning

### Initial Schedule Creation

**PlanningService.create_study_plan()**:
1. Group topics by section (contextual interleaving)
2. For each topic cluster:
   - Schedule Repetition 1 (study + practice): I(1) = same day
   - Schedule Repetition 2 (review): I(2) = next day (cumulative 1 day)
   - Schedule Repetition 3 (review): I(3) = +6 days (cumulative 7 days)
   - Schedule Repetition 4+ (if time permits): I(n) = I(n-1) × EF

**Example** (30-day plan, Topic "9708.1.1"):
```
Day 1: Study topic (Repetition 1)
Day 2: Review topic (Repetition 2)  [I(1) = 1 day later]
Day 8: Review topic (Repetition 3)  [I(2) = 6 days later]
Day 23: Review topic (Repetition 4) [I(3) = 15 days later, I(3) = 6 × 2.5]
```

---

### Adaptive Rescheduling

**PlanningService.update_progress()**:
After student completes a study day:
1. Collect performance % for each topic
2. Map to quality (0-5)
3. Update EF using formula
4. Recalculate future intervals with new EF
5. Optionally reschedule upcoming reviews

**Example** (Topic performed poorly):
```
Original: EF = 2.5, Next review in 15 days
Student scores 65% (quality = 2)
New EF: 2.5 + (0.1 - 3 × 0.14) = 2.08
New interval: 6 × 2.08 = 12 days (review sooner)
```

---

## Research Evidence

**Original Paper**:
- Woźniak, P. A., & Gorzelańczyk, E. J. (1994). "Optimization of repetition spacing in the practice of learning." *Acta Neurobiologiae Experimentalis*, 54, 59-62.

**Why SM-2 (not SM-15+)**:
- Simplicity: Easy to implement and explain
- Effectiveness: 85-90% of SM-15 benefit with 10% of complexity
- Stability: Proven over 30+ years
- Production-ready: No complex neural networks or user burden

**Performance**:
- 30% better retention vs. massed practice (Cepeda et al., 2006)
- 80-95% recall rate after 1 year (Woźniak, 1990)
- Optimal for declarative knowledge (facts, concepts, definitions)

---

## Edge Cases & Handling

### Case 1: Student Fails (Quality 0-2)
**Action**: Reset to shorter intervals
- Drop EF significantly
- Insert additional review sessions
- Mark topic for "needs attention" in improvement plan

### Case 2: Student Aces Everything (Quality 5)
**Action**: Keep EF at max, let intervals grow
- Don't artificially cap intervals
- Monitor for overconfidence (regression testing)

### Case 3: Long Gap in Study (>2 weeks)
**Action**: Recalibrate
- Assume EF dropped by 10-20%
- Insert "refresher" review before continuing schedule
- Gather new performance data to update EF

### Case 4: Insufficient Time Before Exam
**Action**: Prioritize weak topics
- Use improvement plans to identify weaknesses
- Schedule weak topics with higher frequency
- Skip high-EF topics if necessary (already mastered)

---

## Integration with Contextual Interleaving

SM-2 determines WHEN to review.
Contextual interleaving determines WHICH topics to mix in each session.

**Combined Strategy**:
```
Day 1: Topics A, B, C (same section, Repetition 1)
Day 2: Topics A, B, C (Repetition 2, I=1)
Day 8: Topics A, B (Repetition 3, I=6) + Topics D, E (Repetition 1)
Day 15: Topics D, E (Repetition 3, I=6) + Topic F (Repetition 1)
```

**Rule**: Max 3 topics per day (cognitive load), scheduled by SM-2 intervals.

---

## Constitutional Alignment

- **Principle III**: PhD-Level Pedagogy → Evidence-based SM-2 algorithm
- **Principle VI**: Constructive Feedback → EF updates reflect performance

---

**Version**: 1.0.0 | **Created**: 2025-12-21
**Algorithm**: SuperMemo 2 (P. Woźniak, 1988)
**Status**: Production-ready implementation