"""
Teaching Service

Business logic for Teacher Agent (concept explanations).

Phase III User Story 1: Students request PhD-level explanations of
Economics 9708 syllabus concepts with examples, diagrams, and practice problems.

Constitutional Requirements:
- Principle I: Subject accuracy (Cambridge syllabus alignment)
- Principle III: PhD-level pedagogy (evidence-based teaching)
- Principle VI: Constructive feedback (clear explanations)
"""

import json
import logging
from typing import Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session, select

from src.models.syllabus_point import SyllabusPoint
from src.models.student import Student
from src.models.resource import Resource
from src.models.generated_explanation import GeneratedExplanation
from src.models.enums import GeneratedByType, LLMProvider
from src.schemas.teaching_schemas import (
    ExplainConceptRequest,
    TopicExplanation,
    KeyTerm,
    Example,
    VisualAid,
    WorkedExample,
    Misconception,
    PracticeProblem,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator
from src.ai_integration.prompt_templates.teacher_prompts import (
    TeacherPrompts,
    create_explanation_prompt,
)
import hashlib

logger = logging.getLogger(__name__)


class SyllabusPointNotFoundError(Exception):
    """Raised when syllabus point ID not found in database"""

    pass


class StudentNotFoundError(Exception):
    """Raised when student ID not found in database"""

    pass


class LLMResponseError(Exception):
    """Raised when LLM response cannot be parsed or is invalid"""

    pass


async def explain_concept(
    session: Session,
    request: ExplainConceptRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> TopicExplanation:
    """
    Generate PhD-level explanation for a syllabus concept.

    Uses Teacher Agent prompts with Claude Sonnet 4.5 (primary) to generate
    comprehensive explanations with examples, diagrams, and practice problems.

    Args:
        session: Database session
        request: Explanation request with syllabus_point_id, student_id, options
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        TopicExplanation: Structured explanation with all components

    Raises:
        SyllabusPointNotFoundError: If syllabus_point_id not found
        StudentNotFoundError: If student_id not found
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = ExplainConceptRequest(
        ...     syllabus_point_id=UUID("..."),
        ...     student_id=UUID("..."),
        ...     include_diagrams=True,
        ...     include_practice=True
        ... )
        >>> explanation = await explain_concept(session, request)
        >>> explanation.concept_name
        'Price Elasticity of Demand'
        >>> len(explanation.examples) >= 2
        True

    Constitutional Compliance:
        - Principle I: Validates syllabus point exists (Cambridge alignment)
        - Principle III: Uses PhD-level prompts (TeacherPrompts)
        - Principle VI: Returns structured, actionable explanation

    LLM Workflow:
        1. Fetch syllabus point and student context from database
        2. Build explanation prompt with TeacherPrompts
        3. Call LLM with fallback (Claude → GPT-4 → Gemini)
        4. Parse JSON response and validate structure
        5. Return TopicExplanation schema
    """

    # Step 1: Fetch syllabus point from database
    statement = select(SyllabusPoint).where(SyllabusPoint.id == request.syllabus_point_id)
    syllabus_point = session.exec(statement).first()

    if not syllabus_point:
        raise SyllabusPointNotFoundError(
            f"Syllabus point {request.syllabus_point_id} not found"
        )

    # Step 2: Fetch student for context (optional weaknesses, progress)
    statement = select(Student).where(Student.id == request.student_id)
    student = session.exec(statement).first()

    if not student:
        raise StudentNotFoundError(f"Student {request.student_id} not found")

    # Step 3: Build student context (weaknesses, struggles)
    student_context: Dict[str, Any] = {}
    if request.context:
        student_context["context"] = request.context

    # TODO: Add student weaknesses from improvement_plans table when available
    # For now, just pass context from request

    # Step 4: Create explanation prompt
    # Parse learning outcomes from syllabus_point.learning_outcomes (TEXT field)
    learning_outcomes = []
    if syllabus_point.learning_outcomes:
        # Assume learning_outcomes is newline-separated text
        learning_outcomes = [
            line.strip()
            for line in syllabus_point.learning_outcomes.split("\n")
            if line.strip()
        ]

    prompt = create_explanation_prompt(
        syllabus_code=syllabus_point.code,
        concept_name=syllabus_point.description.split(":")[0].strip()
        if ":" in syllabus_point.description
        else syllabus_point.description[:50],
        syllabus_description=syllabus_point.description,
        learning_outcomes=learning_outcomes,
        student_context=student_context if student_context else None,
    )

    # Step 5: Call LLM with fallback orchestration
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Generating explanation for {syllabus_point.code} using LLM fallback"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.3,  # Low temperature for accuracy
            max_tokens=4000,  # Comprehensive PhD-level explanation (max for GPT-4 Turbo fallback)
            system_prompt=TeacherPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate explanation: {str(e)}") from e

    # Step 6: Parse JSON response
    try:
        # Extract JSON from response (LLM might wrap in markdown code blocks)
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()

        response_data = json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Response text: {response_text[:500]}...")
        raise LLMResponseError(f"LLM response not valid JSON: {str(e)}") from e

    # Step 7: Build TopicExplanation from parsed response
    try:
        # Handle both old and new format for backward compatibility
        definition_data = response_data.get("definition", "")
        if isinstance(definition_data, dict):
            # Old format: definition is an object with precise_definition and key_terms
            definition_str = definition_data.get("precise_definition", "")
            # Check for key_terms in old format (nested in definition)
            key_terms_data = definition_data.get("key_terms", [])
        else:
            definition_str = str(definition_data)
            key_terms_data = []

        # Extract key terms (check top level for new format, fallback to definition for old)
        if not key_terms_data:
            key_terms_data = response_data.get("key_terms", [])
        key_terms = [
            KeyTerm(**kt) if isinstance(kt, dict) else KeyTerm(term=str(kt), definition="")
            for kt in key_terms_data
        ]

        # Get explanation text - combine all three components
        explanation_data = response_data.get("explanation", {})
        if isinstance(explanation_data, dict):
            # Combine all three fields from the structured explanation
            core = explanation_data.get("core_principles", "")
            why = explanation_data.get("why_it_matters", "")
            theory = explanation_data.get("theoretical_foundation", "")

            # Build comprehensive explanation text
            parts = []
            if core:
                parts.append(f"**Core Principles**:\n{core}")
            if why:
                parts.append(f"\n\n**Why It Matters**:\n{why}")
            if theory:
                parts.append(f"\n\n**Theoretical Foundation**:\n{theory}")

            explanation_text = "\n".join(parts) if parts else ""
        else:
            explanation_text = str(explanation_data)

        explanation = TopicExplanation(
            syllabus_code=syllabus_point.code,
            concept_name=syllabus_point.description.split(":")[0].strip() if ":" in syllabus_point.description else syllabus_point.description,
            definition=definition_str,
            key_terms=key_terms,
            explanation=explanation_text,
            examples=[
                Example(**ex) if isinstance(ex, dict) else Example(title="", scenario=str(ex), analysis="")
                for ex in response_data.get("examples", [])
            ],
            visual_aids=[
                VisualAid(**va) if isinstance(va, dict) else VisualAid(type="diagram", title="", description=str(va))
                for va in response_data.get("visual_aids", [])
            ]
            if request.include_diagrams
            else [],
            worked_examples=[
                WorkedExample(**we) if isinstance(we, dict) else WorkedExample(problem="", step_by_step_solution=str(we), marks_breakdown="")
                for we in response_data.get("worked_examples", [])
            ],
            common_misconceptions=[
                Misconception(**mc) if isinstance(mc, dict) else Misconception(misconception=str(mc), why_wrong="", correct_understanding="")
                for mc in response_data.get("common_misconceptions", [])
            ],
            practice_problems=[
                PracticeProblem(**pp) if isinstance(pp, dict) else PracticeProblem(question=str(pp), difficulty="medium", answer_outline="", marks=4)
                for pp in response_data.get("practice_problems", [])
            ]
            if request.include_practice
            else [],
            related_concepts=response_data.get("connections", {}).get("syllabus_links", []),
            generated_by=provider.value,
        )

        logger.info(
            f"Successfully generated explanation for {syllabus_point.code} ({len(explanation.examples)} examples, {len(explanation.practice_problems)} practice problems)"
        )

        return explanation

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build TopicExplanation from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


async def generate_explanation_with_resources(
    session: Session,
    syllabus_point: SyllabusPoint,
    resources: list[Resource],
    admin_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    is_v1: bool = False,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> GeneratedExplanation:
    """
    Generate explanation for a syllabus point using selected resources as context.

    This function is used for both:
    - v1 admin generation (is_v1=True, admin_id set)
    - v2+ student generation (is_v1=False, student_id set)

    Args:
        session: Database session
        syllabus_point: SyllabusPoint to generate explanation for
        resources: List of Resource objects to use as context
        admin_id: Admin student ID (for v1 generation)
        student_id: Student ID (for v2+ generation)
        is_v1: Whether this is a v1 (admin) explanation
        llm_orchestrator: Optional LLM orchestrator

    Returns:
        GeneratedExplanation: The generated explanation entity

    Constitutional Compliance:
        - Principle I: Uses resources as context (syllabus-aligned)
        - Principle V: Tracks generator_student_id for multi-tenant
    """
    # Build resource context for prompt
    resource_context = ""
    if resources:
        resource_texts = []
        for r in resources:
            # Get extracted text from resource
            if r.extracted_text:
                resource_texts.append(
                    f"--- Resource: {r.title} ---\n{r.extracted_text[:5000]}\n"
                )
            elif r.resource_metadata and r.resource_metadata.get("excerpt_text"):
                resource_texts.append(
                    f"--- Resource: {r.title} ---\n{r.resource_metadata['excerpt_text'][:5000]}\n"
                )

        if resource_texts:
            resource_context = "\n\n## Reference Materials:\n" + "\n".join(resource_texts)

    # Parse learning outcomes
    learning_outcomes = []
    if syllabus_point.learning_outcomes:
        learning_outcomes = [
            line.strip()
            for line in syllabus_point.learning_outcomes.split("\n")
            if line.strip()
        ]

    # Build prompt with resource context
    base_prompt = create_explanation_prompt(
        syllabus_code=syllabus_point.code,
        concept_name=syllabus_point.description.split(":")[0].strip()
        if ":" in syllabus_point.description
        else syllabus_point.description[:50],
        syllabus_description=syllabus_point.description,
        learning_outcomes=learning_outcomes,
        student_context=None,
    )

    if resource_context:
        prompt = f"{base_prompt}\n\n{resource_context}\n\nUse the reference materials above to enhance your explanation with specific examples and accurate details."
    else:
        prompt = base_prompt

    # Initialize LLM orchestrator
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    # Generate explanation
    try:
        logger.info(f"Generating {'v1' if is_v1 else 'v2+'} explanation for {syllabus_point.code}")

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.3,
            max_tokens=4000,
            system_prompt=TeacherPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise LLMResponseError(f"Failed to generate explanation: {str(e)}") from e

    # Parse JSON response
    try:
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()

        content = json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        raise LLMResponseError(f"LLM response not valid JSON: {str(e)}") from e

    # Determine version number
    if is_v1:
        version = 1
        generated_by = GeneratedByType.SYSTEM
        generator_student_id = None
    else:
        # Find next version number for this topic
        from sqlmodel import func
        max_version = session.exec(
            select(func.max(GeneratedExplanation.version)).where(
                GeneratedExplanation.syllabus_point_id == syllabus_point.id
            )
        ).one()
        version = (max_version or 0) + 1
        generated_by = GeneratedByType.STUDENT
        generator_student_id = student_id

    # Map provider to enum
    provider_map = {
        "anthropic": LLMProvider.ANTHROPIC,
        "openai": LLMProvider.OPENAI,
        "google": LLMProvider.GOOGLE,
    }
    llm_provider = provider_map.get(provider.value, LLMProvider.ANTHROPIC)

    # Create signature from content
    content_str = json.dumps(content, sort_keys=True)
    signature = hashlib.sha256(content_str.encode()).hexdigest()

    # Create GeneratedExplanation entity
    explanation = GeneratedExplanation(
        syllabus_point_id=syllabus_point.id,
        version=version,
        content=content,
        generated_by=generated_by,
        generator_student_id=generator_student_id,
        llm_provider=llm_provider,
        llm_model=f"{provider.value}-default",  # TODO: Get actual model name
        token_cost=0,  # TODO: Track token usage
        signature=signature,
    )

    return explanation
