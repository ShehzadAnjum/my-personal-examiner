"""
Resource Service

CRUD operations for GeneratedExplanation resources with cache integration.

Feature: 006-resource-bank
Architecture:
- DB is source of truth
- Cache is secondary (fetched from DB if miss)
- Signature-based validation for sync
"""

import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy.orm.attributes import flag_modified

from src.models.enums import GeneratedByType, LLMProvider
from src.models.generated_explanation import GeneratedExplanation
from src.models.syllabus_point import SyllabusPoint
from src.services import cache_service

logger = logging.getLogger(__name__)


class ExplanationNotFoundError(Exception):
    """Raised when explanation doesn't exist"""

    pass


class ExplanationAlreadyExistsError(Exception):
    """Raised when trying to create duplicate explanation"""

    pass


class NoV1ExplanationError(Exception):
    """Raised when v1 doesn't exist for personalization"""

    pass


class SyllabusPointNotFoundError(Exception):
    """Raised when syllabus point doesn't exist"""

    pass


class LLMGenerationError(Exception):
    """Raised when LLM fails to generate content"""

    pass


def get_explanation(
    session: Session,
    syllabus_point_id: UUID,
    version: int = 1,
    use_cache: bool = True,
) -> Optional[dict]:
    """
    Get explanation for a topic, checking cache first.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        version: Version to retrieve (default: 1)
        use_cache: Whether to check cache first

    Returns:
        dict | None: Explanation with is_cached flag, or None if not found

    Cache Strategy:
        1. Check cache first (if enabled)
        2. If cache miss or signature mismatch, fetch from DB
        3. If found in DB, update cache
        4. If not in DB, return None
    """
    # Get syllabus code for display (e.g., '9708.1.1')
    syllabus_code = _get_syllabus_code(session, syllabus_point_id)

    # 1. Check cache first
    if use_cache:
        cached = cache_service.get_from_cache(syllabus_point_id, version)
        if cached:
            # Verify signature matches DB
            db_explanation = _get_from_db(session, syllabus_point_id, version)
            if db_explanation and cached.get("signature") == db_explanation.signature:
                return {
                    **cached,
                    "is_cached": True,
                    "id": str(db_explanation.id),
                    "syllabus_code": syllabus_code,  # Added: actual code
                    "generated_by": db_explanation.generated_by.value,
                    "llm_provider": db_explanation.llm_provider.value,
                    "llm_model": db_explanation.llm_model,
                    "token_cost": db_explanation.token_cost,
                    "quality_rating": db_explanation.quality_rating,
                    "created_at": db_explanation.created_at.isoformat(),
                }

    # 2. Fetch from database
    explanation = _get_from_db(session, syllabus_point_id, version)
    if not explanation:
        return None

    # 3. Update cache
    _update_cache(explanation)

    return _explanation_to_response(explanation, is_cached=False, syllabus_code=syllabus_code)


def _get_from_db(
    session: Session,
    syllabus_point_id: UUID,
    version: int,
) -> Optional[GeneratedExplanation]:
    """
    Get explanation directly from database.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        version: Version number

    Returns:
        GeneratedExplanation | None
    """
    statement = select(GeneratedExplanation).where(
        GeneratedExplanation.syllabus_point_id == syllabus_point_id,
        GeneratedExplanation.version == version,
    )
    return session.exec(statement).first()


def _update_cache(explanation: GeneratedExplanation) -> None:
    """
    Update cache with explanation from DB.

    Args:
        explanation: GeneratedExplanation model
    """
    cache_service.save_to_cache(
        syllabus_point_id=explanation.syllabus_point_id,
        version=explanation.version,
        content=explanation.content,
        signature=explanation.signature,
        metadata={
            "llm_provider": explanation.llm_provider.value,
            "llm_model": explanation.llm_model,
            "generated_by": explanation.generated_by.value,
        },
    )


def _get_syllabus_code(session: Session, syllabus_point_id: UUID) -> Optional[str]:
    """
    Get the syllabus code (e.g., '9708.1.1') for a syllabus point.

    Args:
        session: Database session
        syllabus_point_id: UUID of the syllabus point

    Returns:
        str | None: The syllabus code, or None if not found
    """
    statement = select(SyllabusPoint.code).where(SyllabusPoint.id == syllabus_point_id)
    return session.exec(statement).first()


def _explanation_to_response(
    explanation: GeneratedExplanation,
    is_cached: bool = False,
    syllabus_code: Optional[str] = None,
) -> dict:
    """
    Convert explanation model to response dict.

    Args:
        explanation: GeneratedExplanation model
        is_cached: Whether served from cache
        syllabus_code: The syllabus code (e.g., '9708.1.1') if available

    Returns:
        dict: Response format
    """
    return {
        "id": str(explanation.id),
        "syllabus_point_id": str(explanation.syllabus_point_id),
        "syllabus_code": syllabus_code,  # Added: actual code like '9708.1.1'
        "version": explanation.version,
        "content": explanation.content,
        "generated_by": explanation.generated_by.value,
        "llm_provider": explanation.llm_provider.value,
        "llm_model": explanation.llm_model,
        "token_cost": explanation.token_cost,
        "quality_rating": explanation.quality_rating,
        "signature": explanation.signature,
        "created_at": explanation.created_at.isoformat(),
        "is_cached": is_cached,
    }


def create_v1_explanation(
    session: Session,
    syllabus_point_id: UUID,
    content: dict,
    llm_provider: LLMProvider,
    llm_model: str,
    token_cost: int = 0,
) -> GeneratedExplanation:
    """
    Create a v1 (admin/system) explanation.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        content: TopicExplanation content dict
        llm_provider: Provider used for generation
        llm_model: Model identifier
        token_cost: Tokens consumed

    Returns:
        GeneratedExplanation: Created explanation

    Raises:
        ExplanationAlreadyExistsError: If v1 already exists

    Admin-Only:
        - This should only be called by admin endpoints
        - v1 is always generated_by=SYSTEM
    """
    # Check if v1 already exists
    existing = _get_from_db(session, syllabus_point_id, version=1)
    if existing:
        raise ExplanationAlreadyExistsError(
            f"V1 explanation already exists for syllabus point {syllabus_point_id}. "
            "Use regenerate endpoint instead."
        )

    # Compute signature
    now = datetime.utcnow()
    signature = cache_service.compute_signature(content, now)

    # Create explanation
    explanation = GeneratedExplanation(
        syllabus_point_id=syllabus_point_id,
        version=1,
        content=content,
        generated_by=GeneratedByType.SYSTEM,
        generator_student_id=None,
        llm_provider=llm_provider,
        llm_model=llm_model,
        token_cost=token_cost,
        quality_rating=None,
        signature=signature,
        created_at=now,
        updated_at=now,
    )

    session.add(explanation)
    session.flush()

    # Update cache
    _update_cache(explanation)

    return explanation


def regenerate_v1_explanation(
    session: Session,
    explanation_id: UUID,
    content: dict,
    llm_provider: LLMProvider,
    llm_model: str,
    token_cost: int = 0,
) -> GeneratedExplanation:
    """
    Regenerate an existing v1 explanation.

    Args:
        session: Database session
        explanation_id: Existing explanation UUID
        content: New TopicExplanation content dict
        llm_provider: Provider used for regeneration
        llm_model: Model identifier
        token_cost: Tokens consumed

    Returns:
        GeneratedExplanation: Updated explanation

    Raises:
        ExplanationNotFoundError: If explanation doesn't exist
    """
    explanation = session.get(GeneratedExplanation, explanation_id)
    if not explanation:
        raise ExplanationNotFoundError(f"Explanation {explanation_id} not found")

    # Update fields
    now = datetime.utcnow()
    explanation.content = content
    explanation.llm_provider = llm_provider
    explanation.llm_model = llm_model
    explanation.token_cost = token_cost
    explanation.signature = cache_service.compute_signature(content, now)
    explanation.updated_at = now

    session.add(explanation)
    session.flush()

    # Update cache
    _update_cache(explanation)

    return explanation


def create_personalized_explanation(
    session: Session,
    syllabus_point_id: UUID,
    student_id: UUID,
    content: dict,
    llm_provider: LLMProvider,
    llm_model: str,
    token_cost: int = 0,
) -> GeneratedExplanation:
    """
    Create a personalized (v2+) explanation for a student.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        student_id: Student who generated (multi-tenant key)
        content: TopicExplanation content dict
        llm_provider: Provider used for generation
        llm_model: Model identifier
        token_cost: Tokens consumed

    Returns:
        GeneratedExplanation: Created explanation

    Raises:
        NoV1ExplanationError: If v1 doesn't exist (required base)

    Version Logic:
        - v1 = admin (must exist)
        - v2+ = student-generated (auto-incremented)
    """
    # Check v1 exists
    v1 = _get_from_db(session, syllabus_point_id, version=1)
    if not v1:
        raise NoV1ExplanationError(
            f"V1 explanation must exist before personalization for {syllabus_point_id}"
        )

    # Get next version for this student
    next_version = _get_next_student_version(session, syllabus_point_id, student_id)

    # Compute signature
    now = datetime.utcnow()
    signature = cache_service.compute_signature(content, now)

    # Create explanation
    explanation = GeneratedExplanation(
        syllabus_point_id=syllabus_point_id,
        version=next_version,
        content=content,
        generated_by=GeneratedByType.STUDENT,
        generator_student_id=student_id,
        llm_provider=llm_provider,
        llm_model=llm_model,
        token_cost=token_cost,
        quality_rating=None,
        signature=signature,
        created_at=now,
        updated_at=now,
    )

    session.add(explanation)
    session.flush()

    return explanation


def _get_next_student_version(
    session: Session,
    syllabus_point_id: UUID,
    student_id: UUID,
) -> int:
    """
    Get next version number for a student's personalized explanation.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        student_id: Student UUID

    Returns:
        int: Next available version number (2 or higher)
    """
    # Get highest version for this student on this topic
    statement = select(GeneratedExplanation.version).where(
        GeneratedExplanation.syllabus_point_id == syllabus_point_id,
        GeneratedExplanation.generator_student_id == student_id,
    ).order_by(GeneratedExplanation.version.desc())

    result = session.exec(statement).first()

    if result:
        return result + 1
    return 2  # First student version is v2


def list_versions(
    session: Session,
    syllabus_point_id: UUID,
    student_id: Optional[UUID] = None,
) -> list[dict]:
    """
    List available versions for a topic.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID
        student_id: Optional student to check for ownership

    Returns:
        list[dict]: List of versions with metadata
    """
    statement = select(GeneratedExplanation).where(
        GeneratedExplanation.syllabus_point_id == syllabus_point_id,
    ).order_by(GeneratedExplanation.version)

    explanations = session.exec(statement).all()

    result = []
    for exp in explanations:
        # Only show v1 and versions generated by this student
        if exp.version == 1 or (student_id and exp.generator_student_id == student_id):
            result.append(
                {
                    "version": exp.version,
                    "generated_by": exp.generated_by.value,
                    "created_at": exp.created_at.isoformat(),
                    "is_mine": student_id is not None
                    and exp.generator_student_id == student_id,
                }
            )

    return result


def get_all_signatures(session: Session) -> dict[tuple[str, int], str]:
    """
    Get all signatures from database for sync validation.

    Args:
        session: Database session

    Returns:
        dict: Mapping of (syllabus_point_id, version) to signature
    """
    statement = select(
        GeneratedExplanation.syllabus_point_id,
        GeneratedExplanation.version,
        GeneratedExplanation.signature,
    )

    results = session.exec(statement).all()

    return {
        (str(row[0]), row[1]): row[2]
        for row in results
    }


# ============================================================================
# V1 Generation with LLM Integration (T026: US2)
# ============================================================================

# System prompt for Resource Bank explanation generation
RESOURCE_BANK_SYSTEM_PROMPT = """You are a PhD-level Economics educator creating educational content for Cambridge International A-Level Economics (9708).

Your explanations must be:
- Academically rigorous yet accessible
- Aligned with Cambridge syllabus requirements
- Rich with real-world examples
- Focused on exam success

You MUST respond with valid JSON only. No markdown code blocks, no additional text."""

RESOURCE_BANK_GENERATION_PROMPT = """Generate a comprehensive explanation for the following Cambridge A-Level Economics topic.

**Topic Code**: {syllabus_code}
**Topic Title**: {concept_name}
**Description**: {description}
**Learning Outcomes**: {learning_outcomes}

Generate a JSON response with EXACTLY this structure:

{{
    "definition": "A clear, exam-worthy definition of the concept",
    "concept_explanation": "A detailed 2-3 paragraph explanation covering the core theory, how it works, and why it matters",
    "real_world_examples": [
        "Example 1 with specific context and data",
        "Example 2 with different application"
    ],
    "diagrams": [
        {{
            "type": "supply-demand" or "flow" or "comparison" etc,
            "description": "What this diagram shows and key features",
            "data": {{}}
        }}
    ],
    "common_misconceptions": [
        {{
            "misconception": "What students often get wrong",
            "correction": "The correct understanding"
        }}
    ],
    "exam_tips": [
        "Tip 1 for exam success",
        "Tip 2 for maximizing marks"
    ],
    "related_topics": ["Topic 1", "Topic 2"],
    "practice_questions": [
        {{
            "question": "A typical exam-style question",
            "answer": "Model answer outline",
            "marks": 4
        }}
    ],
    "summary": "A concise summary of key takeaways for revision"
}}

Ensure:
1. Definition is exam-ready (can be quoted in an answer)
2. Examples use real data/scenarios where possible
3. Misconceptions address common student errors
4. Exam tips are actionable and specific
5. Practice questions match Cambridge exam style

Respond with ONLY the JSON object, no additional text."""


async def generate_v1_explanation(
    session: Session,
    syllabus_point_id: UUID,
    llm_orchestrator=None,
) -> GeneratedExplanation:
    """
    Generate a v1 (admin) explanation using LLM.

    This is the core generation function for populating the Resource Bank.
    Uses the system LLM credentials and creates quality-assured baseline content.

    Args:
        session: Database session
        syllabus_point_id: Syllabus point UUID to generate for
        llm_orchestrator: Optional LLMFallbackOrchestrator (created if not provided)

    Returns:
        GeneratedExplanation: Created explanation entity

    Raises:
        SyllabusPointNotFoundError: If syllabus point doesn't exist
        ExplanationAlreadyExistsError: If v1 already exists
        LLMGenerationError: If LLM fails to generate valid content

    Example:
        >>> from src.ai_integration.llm_fallback import LLMFallbackOrchestrator
        >>> orchestrator = LLMFallbackOrchestrator()
        >>> explanation = await generate_v1_explanation(session, uuid, orchestrator)
        >>> print(explanation.version)  # 1

    Constitutional Compliance:
        - Principle I: Subject accuracy via Cambridge-aligned prompts
        - US2: Admin-only content generation
    """
    import json
    from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

    # Step 1: Fetch syllabus point
    statement = select(SyllabusPoint).where(SyllabusPoint.id == syllabus_point_id)
    syllabus_point = session.exec(statement).first()

    if not syllabus_point:
        raise SyllabusPointNotFoundError(
            f"Syllabus point {syllabus_point_id} not found"
        )

    # Step 2: Check if v1 already exists
    existing = _get_from_db(session, syllabus_point_id, version=1)
    if existing:
        raise ExplanationAlreadyExistsError(
            f"V1 explanation already exists for syllabus point {syllabus_point_id}. "
            "Use regenerate endpoint instead."
        )

    # Step 3: Parse learning outcomes
    learning_outcomes = []
    if syllabus_point.learning_outcomes:
        learning_outcomes = [
            line.strip()
            for line in syllabus_point.learning_outcomes.split("\n")
            if line.strip()
        ]

    # Step 4: Build generation prompt
    concept_name = syllabus_point.description.split(":")[0].strip() \
        if ":" in syllabus_point.description \
        else syllabus_point.description[:50]

    prompt = RESOURCE_BANK_GENERATION_PROMPT.format(
        syllabus_code=syllabus_point.code,
        concept_name=concept_name,
        description=syllabus_point.description,
        learning_outcomes="\n".join(f"- {lo}" for lo in learning_outcomes) or "Not specified",
    )

    # Step 5: Call LLM with fallback
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Generating v1 explanation for {syllabus_point.code} using LLM"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.3,  # Low temperature for consistency
            max_tokens=3000,
            system_prompt=RESOURCE_BANK_SYSTEM_PROMPT,
        )

        logger.info(f"LLM response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM generation failed for {syllabus_point_id}: {e}")
        raise LLMGenerationError(f"Failed to generate explanation: {str(e)}") from e

    # Step 6: Parse JSON response
    try:
        json_text = response_text.strip()
        # Handle markdown code blocks
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()

        content = json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Response text: {response_text[:500]}...")
        raise LLMGenerationError(f"LLM response not valid JSON: {str(e)}") from e

    # Step 7: Map provider enum
    from src.models.enums import LLMProvider as ModelLLMProvider
    provider_map = {
        "anthropic": ModelLLMProvider.ANTHROPIC,
        "openai": ModelLLMProvider.OPENAI,
        "gemini": ModelLLMProvider.GOOGLE,
    }
    llm_provider = provider_map.get(provider.value, ModelLLMProvider.ANTHROPIC)

    # Step 8: Save to database using existing create function
    explanation = create_v1_explanation(
        session=session,
        syllabus_point_id=syllabus_point_id,
        content=content,
        llm_provider=llm_provider,
        llm_model=f"{provider.value}-default",  # TODO: Get actual model name
        token_cost=0,  # TODO: Track actual token usage
    )

    session.commit()

    logger.info(
        f"V1 explanation created: id={explanation.id}, "
        f"syllabus_point={syllabus_point.code}"
    )

    return explanation


async def regenerate_v1_explanation_with_llm(
    session: Session,
    explanation_id: UUID,
    llm_orchestrator=None,
) -> GeneratedExplanation:
    """
    Regenerate an existing v1 explanation using LLM.

    Args:
        session: Database session
        explanation_id: Existing explanation UUID
        llm_orchestrator: Optional LLMFallbackOrchestrator

    Returns:
        GeneratedExplanation: Updated explanation entity

    Raises:
        ExplanationNotFoundError: If explanation doesn't exist
        LLMGenerationError: If LLM fails
    """
    import json
    from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

    # Get existing explanation
    explanation = session.get(GeneratedExplanation, explanation_id)
    if not explanation:
        raise ExplanationNotFoundError(f"Explanation {explanation_id} not found")

    # Get syllabus point
    syllabus_point = session.get(SyllabusPoint, explanation.syllabus_point_id)
    if not syllabus_point:
        raise SyllabusPointNotFoundError(
            f"Syllabus point {explanation.syllabus_point_id} not found"
        )

    # Parse learning outcomes
    learning_outcomes = []
    if syllabus_point.learning_outcomes:
        learning_outcomes = [
            line.strip()
            for line in syllabus_point.learning_outcomes.split("\n")
            if line.strip()
        ]

    # Build prompt
    concept_name = syllabus_point.description.split(":")[0].strip() \
        if ":" in syllabus_point.description \
        else syllabus_point.description[:50]

    prompt = RESOURCE_BANK_GENERATION_PROMPT.format(
        syllabus_code=syllabus_point.code,
        concept_name=concept_name,
        description=syllabus_point.description,
        learning_outcomes="\n".join(f"- {lo}" for lo in learning_outcomes) or "Not specified",
    )

    # Call LLM
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.3,
            max_tokens=3000,
            system_prompt=RESOURCE_BANK_SYSTEM_PROMPT,
        )
    except Exception as e:
        raise LLMGenerationError(f"Failed to regenerate: {str(e)}") from e

    # Parse JSON
    try:
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()
        content = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise LLMGenerationError(f"Invalid JSON response: {str(e)}") from e

    # Map provider
    from src.models.enums import LLMProvider as ModelLLMProvider
    provider_map = {
        "anthropic": ModelLLMProvider.ANTHROPIC,
        "openai": ModelLLMProvider.OPENAI,
        "gemini": ModelLLMProvider.GOOGLE,
    }
    llm_provider = provider_map.get(provider.value, ModelLLMProvider.ANTHROPIC)

    # Update using existing function
    updated = regenerate_v1_explanation(
        session=session,
        explanation_id=explanation_id,
        content=content,
        llm_provider=llm_provider,
        llm_model=f"{provider.value}-default",
        token_cost=0,
    )

    session.commit()
    return updated


# Valid section names for regeneration
VALID_SECTIONS = [
    "definition",
    "concept_explanation",
    "real_world_examples",
    "diagrams",
    "common_misconceptions",
    "exam_tips",
    "related_topics",
    "practice_questions",
    "summary",
]

# Prompts for individual section regeneration
SECTION_PROMPTS = {
    "definition": """Generate an improved, exam-worthy definition for this concept.

CRITICAL: The definition field should contain ONLY the definition text.
DO NOT include the topic code or topic name in the definition - those are in separate fields.

REQUIREMENTS:
- Contains ONLY the definition text (no topic code prefix, no topic name)
- 2-3 sentences, clear and suitable for direct use in exam answers
- Use precise economic terminology
- Start directly with the definition

CORRECT FORMAT:
{{"definition": "Fiscal policy refers to the use of government spending and taxation to influence aggregate demand and achieve macroeconomic objectives."}}

WRONG FORMAT (do NOT do this):
{{"definition": "9708.5.1 Fiscal Policy:\\n\\nFiscal policy refers to..."}}

Return as JSON: {{"definition": "Your definition text here (no code prefix)"}}""",

    "concept_explanation": """Generate an improved explanation of the core theory.

REQUIREMENTS:
- Include 3-4 substantial paragraphs
- Explain HOW the concept works mechanically
- Explain WHY it matters in economic theory
- Include theoretical frameworks where applicable
- Use clear, academic language with economic terminology

Return as JSON: {{"concept_explanation": "Paragraph 1...\\n\\nParagraph 2...\\n\\nParagraph 3..."}}""",

    "real_world_examples": """Generate 3 improved real-world examples with specific context and data.

REQUIREMENTS (EACH example must have ALL 3 fields):
- title: Descriptive title of the example
- scenario: Specific real-world context with country names, dates, or data points
- analysis: Economic analysis connecting the scenario back to the theory

Return as JSON: {{"real_world_examples": [
  {{"title": "Example Title", "scenario": "In 2023, the UK government...", "analysis": "This demonstrates how..."}}
]}}""",

    "diagrams": """Generate 2-3 visual aids for this concept with WORKING Mermaid diagram code.

CRITICAL: You MUST generate actual Mermaid code, NOT "suggested" diagrams. Do NOT use type "suggested".

For each diagram, provide ALL 4 fields:
1. type: MUST be "flowchart" OR "graph" OR "sequence" (NEVER "suggested")
2. title: Clear descriptive title
3. description: What the diagram shows and how to interpret it
4. mermaid_code: ACTUAL working Mermaid syntax (REQUIRED, see examples below)

Mermaid Code Examples - COPY THESE PATTERNS:

Pattern 1 - Process Flow (type: "flowchart"):
flowchart TD
    A[Central Bank Decision] --> B[Policy Rate Change]
    B --> C[Commercial Bank Rates]
    C --> D[Consumer Spending]
    D --> E[Economic Activity]

Pattern 2 - Relationships (type: "graph"):
graph LR
    A((Supply)) --> B{{Equilibrium}}
    C((Demand)) --> B
    B --> D[Price]
    B --> E[Quantity]

Pattern 3 - Sequence (type: "sequence"):
sequenceDiagram
    participant CB as Central Bank
    participant Banks as Banks
    participant Economy as Economy
    CB->>Banks: Lower rate
    Banks->>Economy: Cheaper loans
    Economy->>Economy: More spending

MANDATORY: Return 2-3 diagrams, ALL must have mermaid_code with ACTUAL code (not empty, not null).

Return as JSON: {{"diagrams": [
  {{"type": "flowchart", "title": "Monetary Policy Process", "description": "Shows transmission mechanism", "mermaid_code": "flowchart TD\\n    A[Central Bank] --> B[Banks]\\n    B --> C[Economy]"}},
  {{"type": "graph", "title": "Supply-Demand Model", "description": "Market equilibrium", "mermaid_code": "graph LR\\n    S((Supply)) --> E{{Equilibrium}}\\n    D((Demand)) --> E"}}
]}}""",

    "common_misconceptions": """Generate 3 common student misconceptions about this concept.

REQUIREMENTS (EACH misconception must have ALL 3 fields):
- misconception: What students commonly get wrong
- why_wrong: Why this understanding is incorrect (explain the error)
- correct_understanding: The accurate understanding

Return as JSON: {{"common_misconceptions": [
  {{"misconception": "Students think...", "why_wrong": "This is incorrect because...", "correct_understanding": "Actually..."}}
]}}""",

    "exam_tips": """Generate 3-4 actionable exam tips for this concept.
Tips should be specific to Cambridge A-Level Economics marking criteria.
Return as JSON: {{"exam_tips": ["Tip 1", "Tip 2", "Tip 3"]}}""",

    "related_topics": """Generate a list of 4-6 related topics that connect to this concept.

REQUIREMENTS:
- Include syllabus codes where known (e.g., "9708.4.3 Monetary Policy")
- Include both prerequisite topics and follow-on topics
- 4-6 related concepts

Return as JSON: {{"related_topics": ["9708.X.X Topic Name", "Topic 2", "Topic 3", "Topic 4"]}}""",

    "practice_questions": """Generate 3 exam-style practice questions with model answers.

REQUIREMENTS:
- MUST include 3 difficulty levels: 1 easy (2-4 marks), 1 medium (4-8 marks), 1 hard (8-15 marks)
- Match Cambridge exam question styles
- Each question must have ALL 4 fields:
  - question: Full question text
  - difficulty: "easy" or "medium" or "hard"
  - answer_outline: Key points for model answer with mark allocation
  - marks: Number (2-4 for easy, 4-8 for medium, 8-15 for hard)

Return as JSON: {{"practice_questions": [
  {{"question": "Define...", "difficulty": "easy", "answer_outline": "Point 1 (1 mark)...", "marks": 2}},
  {{"question": "Explain...", "difficulty": "medium", "answer_outline": "...", "marks": 6}},
  {{"question": "Evaluate...", "difficulty": "hard", "answer_outline": "...", "marks": 12}}
]}}""",

    "summary": """Generate a concise summary of the key takeaways for revision.
The summary should be memorable and cover the essential points.
Return as JSON: {{"summary": "Your improved summary here"}}""",
}


class InvalidSectionError(Exception):
    """Raised when an invalid section name is provided"""
    pass


async def regenerate_section_with_llm(
    session: Session,
    explanation_id: UUID,
    section_name: str,
    llm_orchestrator=None,
) -> GeneratedExplanation:
    """
    Regenerate a specific section of an existing v1 explanation.

    Args:
        session: Database session
        explanation_id: Existing explanation UUID
        section_name: Name of section to regenerate (e.g., 'definition', 'diagrams')
        llm_orchestrator: Optional LLMFallbackOrchestrator

    Returns:
        GeneratedExplanation: Updated explanation entity

    Raises:
        ExplanationNotFoundError: If explanation doesn't exist
        InvalidSectionError: If section name is invalid
        LLMGenerationError: If LLM fails
    """
    import json as json_lib
    from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

    # Validate section name
    if section_name not in VALID_SECTIONS:
        raise InvalidSectionError(
            f"Invalid section '{section_name}'. Valid sections: {', '.join(VALID_SECTIONS)}"
        )

    # Get existing explanation
    explanation = session.get(GeneratedExplanation, explanation_id)
    if not explanation:
        raise ExplanationNotFoundError(f"Explanation {explanation_id} not found")

    # Get syllabus point for context
    syllabus_point = session.get(SyllabusPoint, explanation.syllabus_point_id)
    if not syllabus_point:
        raise SyllabusPointNotFoundError(
            f"Syllabus point {explanation.syllabus_point_id} not found"
        )

    # Build prompt with context
    section_prompt = SECTION_PROMPTS[section_name]
    concept_name = syllabus_point.description.split(":")[0].strip() \
        if ":" in syllabus_point.description \
        else syllabus_point.description[:50]

    # Replace placeholders in prompt with actual topic code
    section_prompt_filled = section_prompt.replace("{topic_code}", syllabus_point.code)
    section_prompt_filled = section_prompt_filled.replace("{topic_name}", concept_name)

    full_prompt = f"""You are regenerating the '{section_name}' section for a Cambridge A-Level Economics topic.

**Topic Code**: {syllabus_point.code}
**Topic Title**: {concept_name}
**Full Description**: {syllabus_point.description}

{section_prompt_filled}

IMPORTANT:
- Use the topic code "{syllabus_point.code}" where required
- Ensure ALL required fields are included
- Respond with ONLY valid JSON, no additional text or markdown code blocks."""

    # Call LLM
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=full_prompt,
            temperature=0.3,
            max_tokens=1500,
            system_prompt=RESOURCE_BANK_SYSTEM_PROMPT,
        )
    except Exception as e:
        raise LLMGenerationError(f"Failed to regenerate section: {str(e)}") from e

    # Parse JSON
    try:
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()
        new_section_content = json_lib.loads(json_text)
    except json_lib.JSONDecodeError as e:
        raise LLMGenerationError(f"Invalid JSON response: {str(e)}") from e

    # Validate diagrams section specifically
    if section_name == "diagrams":
        diagrams = new_section_content.get("diagrams", [])
        if not diagrams or not isinstance(diagrams, list):
            raise LLMGenerationError("Diagrams section must contain a list of diagrams")

        for i, diagram in enumerate(diagrams):
            # Reject "suggested" type diagrams
            if diagram.get("type") == "suggested":
                logger.warning(f"Diagram {i} has type 'suggested', rejecting")
                raise LLMGenerationError(
                    "Diagrams must have type 'flowchart', 'graph', or 'sequence', not 'suggested'"
                )

            # Ensure mermaid_code exists and is not empty
            if not diagram.get("mermaid_code") or not diagram.get("mermaid_code").strip():
                logger.warning(f"Diagram {i} missing mermaid_code")
                raise LLMGenerationError(
                    f"All diagrams must include mermaid_code field with valid Mermaid syntax"
                )

            logger.info(f"Validated diagram {i}: type={diagram.get('type')}, has mermaid_code=True")

    # Update the specific section in the existing content
    current_content = explanation.content or {}
    if section_name in new_section_content:
        current_content[section_name] = new_section_content[section_name]
    else:
        # Handle case where LLM returned different key structure
        logger.warning(f"Section {section_name} not found in LLM response, using full response")
        current_content[section_name] = new_section_content

    # Update the explanation - use copy and flag_modified for SQLAlchemy to detect changes
    explanation.content = dict(current_content)  # Create new dict to ensure change detection
    flag_modified(explanation, "content")  # Explicitly mark JSON field as modified
    explanation.updated_at = datetime.utcnow()

    # Update cache with new signature
    new_signature = cache_service.compute_signature(current_content, explanation.updated_at)
    explanation.signature = new_signature
    cache_service.save_to_cache(
        syllabus_point_id=explanation.syllabus_point_id,
        version=explanation.version,
        content=current_content,
        signature=new_signature,
    )

    session.add(explanation)
    session.commit()
    session.refresh(explanation)

    logger.info(
        f"Section '{section_name}' regenerated and committed to DB for explanation {explanation_id}"
    )
    logger.info(f"Updated content keys: {list(explanation.content.keys())}")

    return explanation


# ============================================================================
# Resource Auto-Selection for Topic Generation (T059-T062: US5)
# ============================================================================

def get_resources_for_syllabus_point(
    syllabus_point_id: str,
    session: Session,
    limit: int = 5
) -> List[Dict]:
    """
    Get top N resources for syllabus point, ordered by relevance.

    Auto-selection algorithm:
    1. Query SyllabusPointResource JOIN Resource
    2. Filter by syllabus_point_id and visibility=PUBLIC
    3. Order by relevance_score DESC
    4. Limit to top N (default: 5)

    Args:
        syllabus_point_id: Syllabus point code (e.g., "9708.5.1")
        session: SQLModel database session
        limit: Maximum number of resources to return (default: 5)

    Returns:
        List of dictionaries with resource details and relevance scores

    Constitutional Compliance:
        - FR-032: Auto-select top 5 by relevance
    """
    from src.models.enums import Visibility as ResourceVisibility
    from src.models.resource import Resource
    from src.models.syllabus_point_resource import SyllabusPointResource

    # Query tagged resources
    query = (
        select(SyllabusPointResource, Resource)
        .join(Resource, SyllabusPointResource.resource_id == Resource.id)
        .where(
            SyllabusPointResource.syllabus_point_id == syllabus_point_id,
            Resource.visibility == ResourceVisibility.PUBLIC,
            Resource.admin_approved == True
        )
        .order_by(SyllabusPointResource.relevance_score.desc())
        .limit(limit)
    )

    results = session.exec(query).all()

    selected_resources = []
    for sp_resource, resource in results:
        selected_resources.append({
            'resource': resource,
            'relevance_score': sp_resource.relevance_score,
            'resource_type': resource.resource_type.value,
            'title': resource.title,
            'resource_id': str(resource.id)
        })

    return selected_resources


def calculate_relevance_score(
    resource,
    syllabus_point_id: str,
    keywords: Optional[list[str]] = None
) -> float:
    """
    Calculate relevance score for resource to syllabus point.

    Scoring algorithm:
    - Syllabus resources: Always 1.0 (authoritative)
    - Tagged resources: Use stored relevance_score
    - Keyword matching: 0.1 per keyword match (max 0.8)
    - Resource type bonus: past_paper +0.1, textbook +0.05

    Args:
        resource: Resource object
        syllabus_point_id: Syllabus point code
        keywords: Optional list of keywords to match

    Returns:
        Relevance score (0.0 to 1.0)
    """
    from src.models.enums import ResourceType

    # Syllabus resources always have perfect relevance
    if resource.resource_type == ResourceType.SYLLABUS:
        return 1.0

    base_score = 0.1

    # Keyword matching score
    keyword_score = 0.0
    if keywords:
        title_lower = resource.title.lower()
        metadata_text = str(resource.resource_metadata).lower() if resource.resource_metadata else ""

        for keyword in keywords:
            if keyword.lower() in title_lower or keyword.lower() in metadata_text:
                keyword_score += 0.1

        keyword_score = min(keyword_score, 0.8)

    # Resource type bonus
    type_bonus = 0.0
    if resource.resource_type == ResourceType.PAST_PAPER:
        type_bonus = 0.1
    elif resource.resource_type == ResourceType.TEXTBOOK:
        type_bonus = 0.05

    return min(base_score + keyword_score + type_bonus, 1.0)


def track_resource_usage(
    generated_explanation_id: UUID,
    resource_id: UUID,
    contribution_weight: float,
    session: Session
):
    """
    Track which resources were used in topic generation.

    Creates ExplanationResourceUsage record linking explanation to resources.

    Args:
        generated_explanation_id: UUID of GeneratedExplanation
        resource_id: UUID of Resource used
        contribution_weight: Float 0.0-1.0 indicating importance
        session: SQLModel database session

    Constitutional Compliance:
        - FR-036: Track resource usage for attribution
    """
    from src.models.explanation_resource_usage import ExplanationResourceUsage

    usage = ExplanationResourceUsage(
        generated_explanation_id=generated_explanation_id,
        resource_id=resource_id,
        contribution_weight=contribution_weight
    )

    session.add(usage)
    session.commit()
    session.refresh(usage)

    return usage


def prepare_resources_for_llm_prompt(
    selected_resources: list[dict],
    session: Session
) -> str:
    """
    Format selected resources for inclusion in LLM prompt.

    Extracts text content from resources and formats with attribution.

    Args:
        selected_resources: List from get_resources_for_syllabus_point
        session: SQLModel database session

    Returns:
        Formatted string with resource content and attribution

    Constitutional Compliance:
        - FR-035: Include resources in prompts with attribution
    """
    from src.models.enums import ResourceType

    if not selected_resources:
        return ""

    prompt_parts = ["--- REFERENCE RESOURCES ---\n"]

    for idx, res_dict in enumerate(selected_resources, start=1):
        resource = res_dict['resource']
        relevance_pct = int(res_dict['relevance_score'] * 100)

        # Header
        prompt_parts.append(f"\n[{idx}] {resource.title} (Relevance: {relevance_pct}%)")

        # Source attribution
        if resource.source_url:
            prompt_parts.append(f"Source: {resource.source_url}")
        elif resource.resource_type == ResourceType.SYLLABUS:
            prompt_parts.append("Source: Official Cambridge Syllabus")
        elif resource.resource_type == ResourceType.PAST_PAPER:
            prompt_parts.append("Source: Cambridge Past Paper")

        # Extract content
        if resource.resource_metadata and 'extracted_text' in resource.resource_metadata:
            text = resource.resource_metadata['extracted_text']

            if resource.resource_type == ResourceType.PAST_PAPER:
                prompt_parts.append("Question Text:")
                excerpt = text[:500] + "..." if len(text) > 500 else text
                prompt_parts.append(excerpt)

            elif resource.resource_type == ResourceType.TEXTBOOK:
                if 'excerpt_text' in resource.resource_metadata:
                    prompt_parts.append("Excerpt:")
                    excerpt = resource.resource_metadata['excerpt_text'][:800]
                    prompt_parts.append(excerpt)
                else:
                    excerpt = text[:500] + "..." if len(text) > 500 else text
                    prompt_parts.append(excerpt)

            elif resource.resource_type == ResourceType.SYLLABUS:
                prompt_parts.append("Learning Outcomes:")
                prompt_parts.append(text[:1000])

        prompt_parts.append("")

    return "\n".join(prompt_parts)
