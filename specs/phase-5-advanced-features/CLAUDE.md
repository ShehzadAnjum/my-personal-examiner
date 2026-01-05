# Phase V: Advanced Features - Instructions

**Phase**: V of V
**Status**: 📋 Future
**Focus**: CLI Tools, MCP Servers, Additional Subjects
**Last Updated**: 2026-01-05

---

## 🎯 Phase V Objectives

**Primary Goal**: Extend platform with CLI tools, AI integrations, and additional subjects

**Key Deliverables**:
1. CLI Tool - Command-line interface for students and teachers
2. MCP Servers - Model Context Protocol integrations
3. Additional Subjects - Accounting 9706, Mathematics 9709, English GP 8021
4. Advanced Analytics - Learning progress dashboards
5. Multi-language Support - i18n for global accessibility

**Technology Stack**:
- CLI: Python Click/Typer, Rich (terminal formatting)
- MCP: Model Context Protocol SDK
- Analytics: Chart.js, D3.js
- i18n: next-intl, Python gettext

---

## 📋 Phase V-Specific Patterns

### 1. CLI Tool Pattern

**Pattern**: Typer-based CLI with Rich formatting

```python
# cli/main.py
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="My Personal Examiner CLI")
console = Console()

@app.command()
def study(
    topic: str = typer.Argument(..., help="Syllabus topic code"),
    subject: str = typer.Option("9708", "--subject", "-s", help="Subject code")
):
    """
    Start a study session for a topic.

    Example:
        mpe study 1.1.1 --subject 9708
    """
    console.print(f"[bold blue]Starting study session:[/bold blue] {topic}")

    # Call teaching API
    explanation = api.explain_concept(topic, subject)

    # Display in terminal
    display_explanation(explanation)

@app.command()
def practice(
    paper: int = typer.Option(1, "--paper", "-p", help="Paper number (1-4)"),
    questions: int = typer.Option(5, "--questions", "-q", help="Number of questions")
):
    """
    Take a practice exam.

    Example:
        mpe practice --paper 2 --questions 10
    """
    console.print(f"[bold green]Generating {questions} questions from Paper {paper}[/bold green]")

    # Generate personalized exam
    exam = api.generate_exam(paper=paper, num_questions=questions)

    # Interactive Q&A loop
    run_exam_session(exam)

if __name__ == "__main__":
    app()
```

**Skill**: Use `.claude/skills/python-cli-patterns.md` (to be created)

### 2. MCP Server Pattern

**Pattern**: Model Context Protocol server for AI tool integrations

```python
# mcp/server.py
from mcp import Server, Tool, Resource

server = Server("my-personal-examiner")

@server.tool("explain_topic")
async def explain_topic(topic_code: str, subject: str = "9708") -> str:
    """
    Get PhD-level explanation for a syllabus topic.

    Args:
        topic_code: Syllabus topic code (e.g., "1.1.1")
        subject: Subject code (default: 9708 Economics)

    Returns:
        Structured explanation with examples and diagrams
    """
    explanation = await teaching_service.explain_concept(
        topic_code=topic_code,
        subject=subject
    )
    return explanation.to_markdown()

@server.tool("mark_answer")
async def mark_answer(
    question: str,
    answer: str,
    mark_scheme: str
) -> dict:
    """
    Mark a student's answer against a mark scheme.

    Returns:
        Dictionary with marks, feedback, and model answer
    """
    result = await marking_service.mark_answer(
        question=question,
        student_answer=answer,
        mark_scheme=mark_scheme
    )
    return result.to_dict()

@server.resource("syllabus/{subject}")
async def get_syllabus(subject: str) -> Resource:
    """
    Get full syllabus structure for a subject.
    """
    syllabus = await syllabus_service.get_full_syllabus(subject)
    return Resource(
        uri=f"syllabus/{subject}",
        mimeType="application/json",
        text=syllabus.to_json()
    )
```

**Skill**: Use `.claude/skills/mcp-integration.md`

### 3. Multi-Subject Pattern

**Pattern**: Subject-agnostic services with subject-specific configurations

```python
# config/subjects.py
SUBJECT_CONFIGS = {
    "9708": {
        "name": "Economics",
        "level": "A-Level",
        "papers": [1, 2, 3, 4],
        "assessment_objectives": ["AO1", "AO2", "AO3"],
        "syllabus_file": "resources/cambridge-a-level/economics-9708/syllabus/9708_sy.json",
        "marking_patterns": {
            "define": {"ao1": 2, "template": "Clear definition with key terms"},
            "explain": {"ao1": 1, "ao2": 3, "template": "Analysis with examples"},
            "evaluate": {"ao3": 8, "template": "Balanced argument with judgment"},
        }
    },
    "9706": {
        "name": "Accounting",
        "level": "A-Level",
        "papers": [1, 2, 3],
        "assessment_objectives": ["AO1", "AO2"],
        "syllabus_file": "resources/cambridge-a-level/accounting-9706/syllabus/9706_sy.json",
        # Accounting-specific patterns...
    },
    "9709": {
        "name": "Mathematics",
        "level": "A-Level",
        "papers": [1, 2, 3, 4, 5, 6],  # Pure, Mechanics, Stats
        "assessment_objectives": ["AO1", "AO2"],
        # Math-specific patterns...
    }
}

def get_subject_config(subject_code: str) -> dict:
    """Get configuration for a subject."""
    if subject_code not in SUBJECT_CONFIGS:
        raise SubjectNotSupportedError(f"Subject {subject_code} not configured")
    return SUBJECT_CONFIGS[subject_code]
```

### 4. Analytics Dashboard Pattern

**Pattern**: Learning progress visualization

```typescript
// frontend/components/analytics/ProgressDashboard.tsx
'use client';

import { useStudentProgress } from '@/hooks/useAnalytics';
import { ProgressChart, WeaknessHeatmap, StudyTimeChart } from './charts';

export function ProgressDashboard({ studentId }: { studentId: string }) {
  const { data: progress, isLoading } = useStudentProgress(studentId);

  if (isLoading) return <DashboardSkeleton />;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <ProgressChart
            completed={progress.topicsCompleted}
            total={progress.totalTopics}
          />
        </CardContent>
      </Card>

      {/* Weakness Areas */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Knowledge Gaps</CardTitle>
        </CardHeader>
        <CardContent>
          <WeaknessHeatmap data={progress.weaknessByTopic} />
        </CardContent>
      </Card>

      {/* Study Time */}
      <Card>
        <CardHeader>
          <CardTitle>Study Time (Last 7 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <StudyTimeChart data={progress.studyTimeByDay} />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 📚 Phase V Skills & Agents

### New Skills to Create
1. `python-cli-patterns` - Typer/Click CLI development
2. `rich-terminal-formatting` - Rich library patterns
3. `mcp-server-development` - MCP server implementation
4. `subject-accounting-9706` - Accounting domain knowledge
5. `subject-mathematics-9709` - Mathematics domain knowledge
6. `subject-english-gp-8021` - English GP domain knowledge
7. `analytics-visualization` - Chart.js/D3.js patterns

### Primary Agents
- **Agent 09 - MCP Integration** (MCP server development)
- **Agent 02 - Backend Service** (CLI API integration)
- **Agent 01 - Frontend Web** (Analytics dashboard)
- **Agent 08 - Syllabus Research** (New subject onboarding)

---

## 🚀 CLI Commands (Planned)

```bash
# Installation
pip install my-personal-examiner
# or
uv tool install my-personal-examiner

# Study commands
mpe study 1.1.1 --subject 9708      # Learn a topic
mpe study --random                   # Random topic for the day

# Practice commands
mpe practice --paper 2 --questions 5 # Take practice exam
mpe practice --topic 1.1.1           # Questions on specific topic
mpe practice --weakness              # Target weak areas

# Progress commands
mpe progress                          # Show overall progress
mpe progress --topic 1.1.1           # Progress on specific topic
mpe progress --export pdf            # Export progress report

# Planning commands
mpe plan --exam-date 2026-05-15      # Generate study plan
mpe plan --today                      # Today's study tasks

# Config commands
mpe config --subject 9708            # Set default subject
mpe config --api-key <key>           # Set API key
```

---

## 📁 Resource Structure (Additional Subjects)

```
resources/
├── cambridge-a-level/
│   ├── economics-9708/           # ✅ Implemented (Phase I)
│   ├── accounting-9706/          # Phase V
│   │   ├── syllabus/
│   │   ├── textbooks/
│   │   ├── past-papers/
│   │   ├── mark-schemes/
│   │   └── user-uploads/
│   ├── mathematics-9709/         # Phase V
│   │   └── ...
│   └── english-gp-8021/          # Phase V
│       └── ...
```

---

## ⚠️ Phase V Prerequisites

Before starting Phase V, ensure:
1. ✅ Phase I - Core Infrastructure (complete)
2. ✅ Phase II - Question Bank (complete)
3. ✅ Phase III - AI Teaching Roles (complete)
4. ✅ Phase IV - Web UI (complete)
5. ✅ Economics 9708 fully functional end-to-end
6. ✅ Test coverage ≥80% maintained

---

## 📋 Constitutional Compliance

- **Principle I**: New subjects require Cambridge syllabus verification
- **Principle II**: A* marking standard applies to all subjects
- **Principle IV**: Spec-driven development for each new subject
- **Principle VII**: Test coverage ≥80% for CLI and MCP code

---

**Phase V Status**: 📋 Future
**Prerequisites**: Phases I-IV complete
**Version**: 1.0.0 | **Last Updated**: 2026-01-05
