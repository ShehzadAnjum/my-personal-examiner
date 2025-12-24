---
name: contextual-interleaving
description: Contextual interleaving algorithms for spaced repetition and practice problem sequencing. Use when implementing study plans, practice scheduling, or adaptive review systems.
---

# Skill: Contextual Interleaving

**Domain**: Learning Science & Study Strategies
**Purpose**: Implement evidence-based topic mixing for optimal discrimination learning
**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles - Planner Agent)

---

## Overview

Contextual interleaving is a study strategy that mixes related topics within sessions (not random mixing), improving concept discrimination by 43% over blocked practice.

**Key Difference from Random Interleaving**:
- ❌ Random: Mix Physics + Economics + Chemistry (overwhelming)
- ✅ Contextual: Mix Market Structures + Market Failure + Government Intervention (related Economics topics)

**Implemented in**: `backend/src/algorithms/contextual_interleaving.py`, `backend/src/services/planning_service.py`

---

## Core Principles

### 1. Related Topics Only

**Rule**: Only interleave topics from the same syllabus section or related concepts.

**Example** (Economics 9708):
```
✅ Good Cluster:
- 9708.1.1 (Scarcity and choice)
- 9708.1.2 (Production possibility curves)
- 9708.1.3 (Resource allocation)
→ All from Section 1 (Basic economic ideas)

❌ Bad Cluster:
- 9708.1.1 (Scarcity)
- 9708.5.2 (Exchange rates)
- 9708.8.1 (Income distribution)
→ Unrelated topics, cognitive overload
```

**Relatedness Check**:
```python
def topics_are_related(topic1: str, topic2: str) -> bool:
    """Check if topics share same section (9708.X)"""
    section1 = topic1.rsplit(".", 1)[0]  # "9708.1.1" → "9708.1"
    section2 = topic2.rsplit(".", 1)[0]
    return section1 == section2
```

---

### 2. Cognitive Load Limit (Max 3 Topics/Day)

**Rule**: Never schedule more than 3 distinct topics in one study session.

**Why**: Working memory capacity is 7±2 items (Miller, 1956). Three topics with sub-concepts = ~9-12 total items = at limit.

**Example Schedule**:
```
Day 1:
- Topic A: Supply curves (study + practice)
- Topic B: Demand curves (study + practice)
- Topic C: Market equilibrium (study + practice)
→ Total: 3 topics, ~2 hours

Day 2: (Review + New)
- Topic A: Supply curves (review)
- Topic B: Demand curves (review)
- Topic C: Market equilibrium (review)
→ Total: 3 topics, ~1.5 hours
```

---

### 3. Interleaved Practice Pattern

**Pattern**: A → B → A → C → B (not A → A → A → B → B → B)

**Why**: Forces retrieval and re-encoding, strengthening memory.

**Example** (60-min session):
```
Blocked Practice (DON'T do this):
0-20 min: Supply curves (study + 5 practice problems)
20-40 min: Demand curves (study + 5 practice problems)
40-60 min: Equilibrium (study + 5 practice problems)

Interleaved Practice (DO this):
0-15 min: Supply curves (study)
15-30 min: Demand curves (study)
30-45 min: Equilibrium (study)
45-50 min: Supply problem
50-55 min: Demand problem
55-60 min: Equilibrium problem
→ Then cycle: Supply → Demand → Equilibrium → Supply...
```

---

## Algorithm Implementation

### Cluster Creation

```python
class ContextualInterleaving:
    def __init__(self, max_topics_per_day: int = 3, practice_rounds: int = 3):
        self.max_topics_per_day = max_topics_per_day
        self.practice_rounds = practice_rounds
    
    def create_daily_clusters(self, topics: List[str]) -> List[List[str]]:
        """Group topics into daily clusters (max 3 per cluster)"""
        clusters = []
        used = set()
        
        for topic in topics:
            if topic in used:
                continue
            
            # Start new cluster
            cluster = [topic]
            used.add(topic)
            
            # Find related topics to add to cluster
            for candidate in topics:
                if candidate in used:
                    continue
                if len(cluster) >= self.max_topics_per_day:
                    break
                if self.topics_are_related(topic, candidate):
                    cluster.append(candidate)
                    used.add(candidate)
            
            clusters.append(cluster)
        
        return clusters
    
    def topics_are_related(self, topic1: str, topic2: str) -> bool:
        """Check if topics are in same syllabus section"""
        section1 = topic1.rsplit(".", 1)[0]
        section2 = topic2.rsplit(".", 1)[0]
        return section1 == section2
```

---

### Practice Schedule Generation

```python
def generate_practice_schedule(
    cluster: List[str],
    total_time_minutes: int
) -> List[Tuple[str, str]]:  # [(topic, activity), ...]
    """Generate A→B→A→C→B interleaved practice schedule"""
    
    schedule = []
    study_time_per_topic = total_time_minutes // (len(cluster) * 2)  # Study + practice
    
    # Phase 1: Initial study (sequential)
    for topic in cluster:
        schedule.append((topic, "study", study_time_per_topic))
    
    # Phase 2: Interleaved practice (A→B→A→C→B→...)
    practice_rounds = 3
    for round_num in range(practice_rounds):
        for topic in cluster:
            schedule.append((topic, "practice", study_time_per_topic // practice_rounds))
    
    return schedule
```

---

## Integration with SM-2

Contextual interleaving determines WHICH topics are grouped.
SM-2 determines WHEN those groups are reviewed.

**Combined Example**:
```
Day 1: Cluster [A, B, C] - Repetition 1 (study + practice)
Day 2: Cluster [A, B, C] - Repetition 2 (review)  [SM-2: I(1)=1]
Day 8: Cluster [A, B] - Repetition 3 (review)  [SM-2: I(2)=6]
       + Cluster [D, E] - Repetition 1 (new topics)
Day 23: Cluster [A] - Repetition 4 (review)  [SM-2: I(3)=15]
        + Cluster [D, E] - Repetition 3 (review)
```

**Scheduling Logic**:
1. SM-2 says "Topic A due today, Topic B due today"
2. Contextual interleaving says "A and B are related, schedule together"
3. Create cluster [A, B] with interleaved practice
4. If Topic C also due and related, add to cluster: [A, B, C]
5. If 4+ topics due, split into multiple clusters (max 3/cluster)

---

## Research Evidence

**Key Studies**:
- Rohrer & Taylor (2007): 43% better discrimination between similar concepts
- Kornell & Bjork (2008): 78% vs 38% accuracy on category learning tasks
- Pan (2015): Superior for mathematics problem types

**Mechanism**:
- Blocked practice: "This is easy, I've got it" (false confidence)
- Interleaved practice: "I need to think about which strategy to use" (deeper processing)

**Best For**:
- Discriminating similar concepts (e.g., monopoly vs oligopoly)
- Problem-solving with multiple strategies
- Categories that can be confused (e.g., fiscal vs monetary policy)

**Not Ideal For**:
- Completely unrelated topics (causes confusion)
- Initial learning of very difficult concepts (start with blocked, then interleave)

---

## Implementation Rules

### Rule 1: Section-Based Clustering
Group topics by Cambridge syllabus sections:
- Section 1: Basic economic ideas (9708.1.x)
- Section 2: The price system (9708.2.x)
- Section 3: Government intervention (9708.3.x)
- etc.

### Rule 2: Max 3 Topics Per Day
Never exceed cognitive load limit.

**Exception**: If student is very advanced (based on historical performance), can increase to 4 topics.

### Rule 3: Balance New vs Review
Each cluster should have mix of:
- At least 1 new topic (if available)
- At least 1 review topic (if due per SM-2)

**Example Cluster**:
- Topic A: New (Repetition 1)
- Topic B: Review (Repetition 3)
- Topic C: Review (Repetition 2)

### Rule 4: Respect Weak Topics
If topic has low EF (<2.0), prioritize it:
- Schedule earlier in the day (when fresh)
- Allocate more time
- Reduce cluster size to 2 topics if necessary

---

## Edge Cases

### Case 1: Orphan Topic (No Related Topics)
**Action**: Schedule alone or with 1 loosely related topic.
```
Example: Topic "9708.8.1" (only subsection in Section 8)
→ Schedule alone or with previous section's topics
```

### Case 2: Too Many Related Topics
**Action**: Split into multiple days.
```
Example: Section 1 has 8 subsections
Day 1: Topics 1.1, 1.2, 1.3
Day 3: Topics 1.4, 1.5, 1.6
Day 5: Topics 1.7, 1.8
```

### Case 3: Student Overwhelmed
**Action**: Reduce to 2 topics/day temporarily.
- Monitor performance scores
- If 3 consecutive days <70%, drop to 2 topics
- Resume 3 topics after student improves

---

## Validation Metrics

**Success Indicators**:
- Student can distinguish between related concepts (e.g., MC questions on monopoly vs oligopoly)
- Performance on mixed-topic exams >80%
- Retention after 1 week >70%

**Failure Indicators**:
- Student confuses related concepts
- Performance drops when topics are mixed
- Requests to "do one topic at a time"

**Remediation**:
- Reduce cluster size
- Add explicit comparison exercises ("How is A different from B?")
- Use analogies to highlight differences

---

## Constitutional Alignment

- **Principle III**: PhD-Level Pedagogy → Evidence-based interleaving (43% improvement)
- **Principle VI**: Constructive Feedback → Explain why topics are grouped

---

**Version**: 1.0.0 | **Created**: 2025-12-21
**Research**: Rohrer & Taylor (2007), Kornell & Bjork (2008)
**Status**: Production-ready implementation