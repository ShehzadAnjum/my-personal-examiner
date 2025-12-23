---
ID: 001
TITLE: Comprehensive Goal Clarification - 6 Core AI Roles System
STAGE: constitution
DATE: 2025-12-20
SURFACE: agent
MODEL: claude-sonnet-4-5
FEATURE: core-architecture
BRANCH: main
USER: anjum
COMMAND: resume
LABELS: ["architecture", "constitution", "ai-teaching-system", "core-roles"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: "history/adr/010-ai-teaching-system-architecture.md"
  PR: null
FILES:
 - .specify/memory/constitution.md
 - .claude/agents/teacher-agent.md (planned)
 - .claude/agents/coach-agent.md (planned)
 - .claude/agents/examiner-agent.md (planned)
 - .claude/agents/marker-agent.md (planned)
 - .claude/agents/reviewer-agent.md (planned)
 - .claude/agents/planner-agent.md (planned)
TESTS:
 - Backend test coverage: 80.96% (exceeds 80% target)
---

# Prompt History Record: Comprehensive Goal Clarification

## User Prompt (Verbatim)

let me reiterate our Goal, 
we want to have a personalized fully automated learning system (currently for A-Levels) that has in build a teacher, a coaching teacher(to help understand difficult things), an examiner, who creates tests papers (on A-Level standards) to get prepared and train for real exam (not less that A*), a paper checker who do the strict marking (as per A-Level strict marking), a reviewer and helper that helps identify the weak areas, help to improve and produce the answer sheet for achieving not less than A*. A planner who can create a plan to cover the syllabus in n-days

This whole hardmanship is to produce a comprehensive app that can be reutilized again and again to craft the above mentioned goal/activities for any new subject (laterly for any Grade as well)

Please note: any basic functionality that is explained above, if not there and requires to revisit the basic structure and too much of rework, we can take a note to be get done in next iteration

Take notes, and build RI(if required) do the updated(if required) in ADRs, PHRs, skills , agents, subagents, updation of constitutions, skill etc (only where required). 

reinsure, that we are using the speckit methdology(strictly) and following the research first for the already required skill crafted by the anthropic skill pool, if not available there, we are still using their defined template and techinquie to crete skills

Git is updated and commit and pused

propose the next step to carry on.

## Assistant Response Summary

### Actions Taken

1. **Researched Anthropic Skills Repository**
   - Found official repository: https://github.com/anthropics/skills
   - Available skills: pdf, docx, xlsx, pptx, webapp-testing, artifacts-builder, mcp-server
   - **No education/teaching-specific skills** - will create custom following Anthropic template

2. **Created Comprehensive Constitution (v2.0)**
   - Defined **6 Core Roles**: Teacher, Coach, Examiner, Marker, Reviewer, Planner
   - Updated mission statement with comprehensive automation goal
   - Added extensibility requirements (subject, grade, language)
   - Maintained 8 Constitutional Principles (Cambridge accuracy, A* standard, etc.)
   - File: `.specify/memory/constitution.md`

3. **Current Test Coverage Achievement**
   - **80.96% coverage** (exceeds 80% constitutional requirement)
   - 193 tests passing
   - Fixed JSONB/SQLite compatibility issues
   - Created subjects router, fixed search service

4. **Identified Gaps in Current Architecture**
   - Missing: Teacher Agent definition
   - Missing: Coach Agent definition
   - Missing: Planner Agent definition
   - Existing but need review: Examiner Agent (Assessment Engine), Marker Agent (Marking Engines), Reviewer Agent (Feedback Generator)
   - Missing: Custom teaching skills (phd-pedagogy, subject-specific)

### Key Insights

1. **Reusability is Core Requirement**
   - System must work for ANY subject (not just Economics)
   - Later extensible to ANY grade level (GCSE, IB, AP, etc.)
   - Architecture must be pluggable and configurable

2. **6 Core Roles Map to Our Agents**
   - Teacher → NEW: Teacher Agent
   - Coach → NEW: Coach Agent
   - Examiner → EXISTS: Assessment Engine Agent (needs enhancement)
   - Marker → EXISTS: Marking Engines (subject-specific, needs review)
   - Reviewer → EXISTS: Feedback Generator Subagent (needs elevation to Agent)
   - Planner → NEW: Planner Agent

3. **Next Iteration Items**
   - Basic functionalities missing can be noted for next iteration
   - Focus on MVP: Economics 9708 working end-to-end first
   - Then replicate pattern for other subjects

## Outcomes

✅ **Constitution Created**: Comprehensive v2.0 with 6 core roles defined
✅ **Anthropic Skills Research**: Confirmed no teaching skills exist, will create custom
✅ **Test Coverage**: 80.96% (exceeds target)
✅ **Gap Analysis**: Identified missing agents and skills
⏳ **Agent Definitions**: Pending creation
⏳ **ADR Creation**: Pending (AI Teaching System Architecture)
⏳ **Git Commit**: Pending

## Next Steps Proposed

### Immediate (This Session):
1. Create ADR-010: AI Teaching System Architecture
2. Create 6 agent definition files (.claude/agents/*.md)
3. Create 4 custom skill files (.claude/skills/*.md)
4. Git commit and push

### Next Iteration (Phase III Focus):
1. Implement Teacher Agent (concept explanations)
2. Implement Coach Agent (personalized tutoring)
3. Implement Planner Agent (n-day study schedules)
4. Enhance existing Examiner/Marker/Reviewer agents
5. Build end-to-end Economics 9708 workflow

## Evaluation

**Impact**: 🔴 **CRITICAL** - This clarification fundamentally shifts project focus from "question bank + exam generator" to "comprehensive AI teaching system with 6 roles"

**Alignment**: ✅ Perfectly aligned with SpecKit methodology and extensibility requirements

**Risk**: ⚠️ Scope expansion requires careful phasing to avoid overwork

**Recommendation**: Proceed with RI creation (agents, skills, ADR), then focus Phase III on MVP implementation (Economics 9708 end-to-end with all 6 roles working)

---

**Created**: 2025-12-20
**Session**: Continuation from test coverage improvement session
**Constitutional Compliance**: ✅ All principles adhered to
