"""
Admin Setup Wizard API Routes.

Feature: Admin-First Topic Generation
Updated: 008-academic-level-hierarchy

Endpoints for the admin setup wizard:
- POST /api/admin/setup/upload-syllabus - Upload syllabus PDF for a subject
- GET /api/admin/setup/preview-topics/{syllabus_id} - Preview extracted topics
- POST /api/admin/setup/confirm-topics - Confirm topics
- POST /api/admin/setup/generate-explanations - Generate v1 explanations
- GET /api/admin/setup/status - Get setup status for all subjects
- GET /api/admin/setup/status/{subject_id} - Get setup status for one subject

Updated for Three-Tier Hierarchy:
- Academic Level → Subject → Syllabus → Syllabus Point
- Syllabus upload now requires subject_id (subject must exist)
- Syllabus code and year_range attached to Syllabus model (not Subject)
- SyllabusPoints linked to both syllabus_id and subject_id (backward compat)

Constitutional Compliance:
- Principle I: Topics extracted ONLY from uploaded syllabus (no LLM invention)
- Principle V: Admin-only endpoints with require_admin dependency
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, func, select

from src.database import get_session
from src.middleware.admin_auth import require_admin
from src.models import (
    GeneratedExplanation,
    Resource,
    Student,
    Subject,
    SubjectSetupStatus,
    SyllabusPoint,
)
from src.models.academic_level import AcademicLevel
from src.models.syllabus import Syllabus
from src.models.enums import AddedBy, ResourceType, S3SyncStatus, Visibility
from src.schemas.admin_setup_schemas import (
    AllSubjectsSetupStatusResponse,
    ExtractedTopicPreview,
    GenerateExplanationsRequest,
    GenerateExplanationsResponse,
    SubjectSetupStatusResponse,
    SyllabusParsePreviewResponse,
    SyllabusUploadResponse,
    TopicConfirmationRequest,
    TopicConfirmationResponse,
)
from src.services.syllabus_parser_service import parse_syllabus_pdf

router = APIRouter(prefix="/api/admin/setup", tags=["Admin Setup"])

# Upload directory for syllabus PDFs
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "syllabus"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-syllabus", response_model=SyllabusUploadResponse)
async def upload_syllabus(
    file: UploadFile = File(...),
    subject_id: UUID = Form(...),
    syllabus_code: Optional[str] = Form(None),
    syllabus_year: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> SyllabusUploadResponse:
    """
    Upload syllabus PDF and extract topics.

    Updated for 008-academic-level-hierarchy:
    - Subject must already exist (created via academic-levels flow)
    - Creates a Syllabus record linked to the subject
    - Stores extracted topics for confirmation

    Step 1 of admin setup wizard. This endpoint:
    1. Saves the uploaded PDF
    2. Creates a Resource record for the syllabus
    3. Parses PDF to extract topics
    4. Creates a Syllabus record linked to subject
    5. Returns preview of extracted topics

    Args:
        file: Syllabus PDF file
        subject_id: UUID of existing subject (required)
        syllabus_code: Syllabus code e.g. "9708" (optional, auto-detected from PDF)
        syllabus_year: Year range e.g. "2024-2026" (optional, auto-detected from PDF)

    Returns:
        SyllabusUploadResponse with extracted topic preview

    Raises:
        HTTPException 400: Invalid file type (not PDF)
        HTTPException 404: Subject not found
        HTTPException 409: Syllabus with same code already exists for subject
        HTTPException 422: PDF parsing failed
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed for syllabus upload"
        )

    # Verify subject exists
    subject = session.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found. Create subject first."
        )

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"syllabus_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Parse syllabus PDF
    parse_result = parse_syllabus_pdf(str(file_path))

    if not parse_result.success:
        # Clean up uploaded file on parse failure
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse syllabus PDF: {parse_result.error_message}"
        )

    # Use provided values or fall back to detected
    final_syllabus_code = syllabus_code or parse_result.subject_code or "0000"
    final_syllabus_year = syllabus_year or parse_result.syllabus_year or "2024-2026"

    # Check for duplicate syllabus code under this subject
    existing_syllabus = session.exec(
        select(Syllabus).where(
            Syllabus.subject_id == subject_id,
            Syllabus.code == final_syllabus_code,
        )
    ).first()
    if existing_syllabus:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Syllabus code '{final_syllabus_code}' already exists for this subject"
        )

    # Create Resource record for syllabus
    import hashlib
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    resource = Resource(
        resource_type=ResourceType.PDF,
        title=f"{subject.name} Syllabus {final_syllabus_code} ({final_syllabus_year})",
        file_path=str(file_path),
        uploaded_by_student_id=admin.id,
        admin_approved=True,  # Admin-uploaded, auto-approved
        visibility=Visibility.PUBLIC,
        added_by=AddedBy.ADMIN,
        signature=file_hash,
        s3_sync_status=S3SyncStatus.PENDING,
        resource_metadata={
            "type": "syllabus",
            "syllabus_code": final_syllabus_code,
            "syllabus_year": final_syllabus_year,
            "page_count": parse_result.metadata.get("page_count", 0),
            "topics_extracted": len(parse_result.topics),
        },
    )
    session.add(resource)
    session.commit()
    session.refresh(resource)

    # Create Syllabus record (NEW - 008-academic-level-hierarchy)
    syllabus = Syllabus(
        subject_id=subject_id,
        code=final_syllabus_code,
        year_range=final_syllabus_year,
        version=1,
        is_active=True,
        syllabus_resource_id=resource.id,
    )
    session.add(syllabus)
    session.commit()
    session.refresh(syllabus)

    # Update subject setup status
    subject.setup_status = SubjectSetupStatus.SYLLABUS_UPLOADED.value
    session.add(subject)
    session.commit()
    session.refresh(subject)

    # Store extracted topics in resource metadata for later confirmation
    topics_preview = [
        {
            "code": t.code,
            "title": t.title,
            "description": t.description,
            "learning_outcomes": t.learning_outcomes,
            "confidence": t.confidence,
            "parent_section": t.parent_section,
        }
        for t in parse_result.topics
    ]
    resource.resource_metadata["extracted_topics"] = topics_preview
    resource.resource_metadata["syllabus_id"] = str(syllabus.id)  # Link to syllabus
    session.add(resource)
    session.commit()

    low_confidence_count = len([t for t in parse_result.topics if t.confidence < 0.7])

    return SyllabusUploadResponse(
        subject_id=subject.id,
        syllabus_id=syllabus.id,
        resource_id=resource.id,
        file_name=file.filename,
        page_count=parse_result.metadata.get("page_count", 0),
        syllabus_code=final_syllabus_code,
        subject_name=subject.name,
        syllabus_year=final_syllabus_year,
        topics_extracted=len(parse_result.topics),
        low_confidence_count=low_confidence_count,
        warnings=parse_result.warnings,
        message=f"Successfully uploaded syllabus. {len(parse_result.topics)} topics extracted.",
    )


@router.get("/preview-topics/{syllabus_id}", response_model=SyllabusParsePreviewResponse)
def preview_extracted_topics(
    syllabus_id: UUID,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> SyllabusParsePreviewResponse:
    """
    Preview extracted topics before confirmation.

    Updated for 008-academic-level-hierarchy:
    - Uses syllabus_id instead of subject_id
    - Syllabus has syllabus_resource_id link to uploaded PDF

    Returns all topics extracted from syllabus PDF with confidence scores.
    Admin can review, edit, and delete topics before confirming.

    Args:
        syllabus_id: Syllabus ID to preview topics for

    Returns:
        SyllabusParsePreviewResponse with topic list

    Raises:
        HTTPException 404: Syllabus not found
        HTTPException 400: No syllabus resource or no extracted topics
    """
    # Get syllabus
    syllabus = session.get(Syllabus, syllabus_id)
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus {syllabus_id} not found"
        )

    # Get subject for name
    subject = session.get(Subject, syllabus.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {syllabus.subject_id} not found"
        )

    # Get syllabus resource
    if not syllabus.syllabus_resource_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No syllabus PDF uploaded for this syllabus."
        )

    resource = session.get(Resource, syllabus.syllabus_resource_id)
    if not resource or not resource.resource_metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Syllabus resource not found or has no extracted topics."
        )

    extracted_topics = resource.resource_metadata.get("extracted_topics", [])

    topics = [
        ExtractedTopicPreview(
            code=t["code"],
            title=t["title"],
            description=t["description"],
            learning_outcomes=t.get("learning_outcomes", []),
            confidence=t.get("confidence", 1.0),
            parent_section=t.get("parent_section"),
        )
        for t in extracted_topics
    ]

    high_confidence = len([t for t in topics if t.confidence >= 0.7])
    low_confidence = len([t for t in topics if t.confidence < 0.7])

    return SyllabusParsePreviewResponse(
        syllabus_id=syllabus.id,
        subject_id=subject.id,
        syllabus_code=syllabus.code,
        subject_name=subject.name,
        syllabus_year=syllabus.year_range,
        topics=topics,
        total_topics=len(topics),
        high_confidence_count=high_confidence,
        low_confidence_count=low_confidence,
        warnings=[],
    )


@router.post("/confirm-topics", response_model=TopicConfirmationResponse)
def confirm_topics(
    request: TopicConfirmationRequest,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> TopicConfirmationResponse:
    """
    Confirm extracted topics and create syllabus_points records.

    Updated for 008-academic-level-hierarchy:
    - Uses syllabus_id to link topics to correct syllabus
    - SyllabusPoints get both syllabus_id and subject_id (backward compat)
    - Topic codes prefixed with syllabus.code (e.g., "9708.1.1")

    Admin can edit topic details before confirmation.
    Topics in delete_topic_codes will not be created.

    Args:
        request: TopicConfirmationRequest with edited topics

    Returns:
        TopicConfirmationResponse with creation counts

    Raises:
        HTTPException 404: Syllabus or Subject not found
        HTTPException 400: Invalid setup state
    """
    # Get syllabus (NEW - 008-academic-level-hierarchy)
    syllabus = session.get(Syllabus, request.syllabus_id)
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus {request.syllabus_id} not found"
        )

    # Get subject (for backward compat and setup status)
    subject = session.get(Subject, syllabus.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {syllabus.subject_id} not found"
        )

    # Validate setup status
    if subject.setup_status not in (
        SubjectSetupStatus.SYLLABUS_UPLOADED.value,
        SubjectSetupStatus.TOPICS_GENERATED.value,  # Allow re-confirmation
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm topics in setup status: {subject.setup_status}. "
                   "Upload syllabus first."
        )

    # Delete existing topics for this syllabus (for re-confirmation)
    existing = session.exec(
        select(SyllabusPoint).where(SyllabusPoint.syllabus_id == syllabus.id)
    ).all()
    for sp in existing:
        session.delete(sp)

    # Create new syllabus points
    created_count = 0
    delete_codes = set(request.delete_topic_codes)

    for topic in request.topics:
        if topic.code in delete_codes:
            continue

        syllabus_point = SyllabusPoint(
            syllabus_id=syllabus.id,  # NEW - primary FK
            subject_id=subject.id,    # DEPRECATED - kept for backward compat
            code=f"{syllabus.code}.{topic.code}",  # Prefix with syllabus code (e.g., "9708.1.1")
            description=topic.title,  # Use title as primary description
            topics=topic.description if topic.description != topic.title else None,
            learning_outcomes="; ".join(topic.learning_outcomes) if topic.learning_outcomes else None,
        )
        session.add(syllabus_point)
        created_count += 1

    # Update subject setup status
    subject.setup_status = SubjectSetupStatus.TOPICS_GENERATED.value
    session.add(subject)
    session.commit()

    return TopicConfirmationResponse(
        syllabus_id=syllabus.id,
        subject_id=subject.id,
        topics_created=created_count,
        topics_deleted=len(delete_codes),
        setup_status=subject.setup_status,
        message=f"Created {created_count} syllabus points for syllabus {syllabus.code}. Ready for explanation generation.",
    )


@router.post("/generate-explanations", response_model=GenerateExplanationsResponse)
async def generate_explanations(
    request: GenerateExplanationsRequest,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> GenerateExplanationsResponse:
    """
    Generate v1 explanations for topics.

    Uses selected resources as context for LLM generation.
    Skips topics that already have v1 explanations.

    Args:
        request: GenerateExplanationsRequest with topic and resource selections

    Returns:
        GenerateExplanationsResponse with generation counts

    Raises:
        HTTPException 404: Subject not found
        HTTPException 400: Invalid setup state
    """
    # Get subject
    subject = session.get(Subject, request.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {request.subject_id} not found"
        )

    # Validate setup status
    if not subject.can_generate_explanations():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot generate explanations in setup status: {subject.setup_status}. "
                   "Confirm topics first."
        )

    # Get topics to generate for
    if request.syllabus_point_ids:
        topics = session.exec(
            select(SyllabusPoint).where(
                SyllabusPoint.id.in_(request.syllabus_point_ids),
                SyllabusPoint.subject_id == subject.id,
            )
        ).all()
    else:
        # All topics for subject
        topics = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.subject_id == subject.id)
        ).all()

    if not topics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No topics found to generate explanations for."
        )

    # Get selected resources for context
    resources = []
    if request.resource_ids:
        resources = session.exec(
            select(Resource).where(Resource.id.in_(request.resource_ids))
        ).all()

    # Generate explanations
    generated_count = 0
    failed_count = 0
    skipped_count = 0

    from src.services.teaching_service import generate_explanation_with_resources

    for topic in topics:
        # Check if v1 already exists
        existing = session.exec(
            select(GeneratedExplanation).where(
                GeneratedExplanation.syllabus_point_id == topic.id,
                GeneratedExplanation.version == 1,
            )
        ).first()

        if existing:
            skipped_count += 1
            continue

        try:
            # Generate explanation with resource context
            explanation = await generate_explanation_with_resources(
                session=session,
                syllabus_point=topic,
                resources=resources,
                admin_id=admin.id,
                is_v1=True,
            )
            session.add(explanation)
            generated_count += 1
        except Exception as e:
            print(f"Failed to generate explanation for {topic.code}: {e}")
            failed_count += 1

    # Update subject setup status
    if generated_count > 0:
        subject.setup_status = SubjectSetupStatus.EXPLANATIONS_GENERATED.value
        session.add(subject)

    session.commit()

    # Check if all topics have v1 explanations
    total_topics = session.exec(
        select(func.count()).where(SyllabusPoint.subject_id == subject.id)
    ).one()
    total_v1 = session.exec(
        select(func.count()).where(
            GeneratedExplanation.syllabus_point_id.in_(
                select(SyllabusPoint.id).where(SyllabusPoint.subject_id == subject.id)
            ),
            GeneratedExplanation.version == 1,
        )
    ).one()

    if total_v1 >= total_topics:
        subject.setup_status = SubjectSetupStatus.COMPLETE.value
        session.add(subject)
        session.commit()

    return GenerateExplanationsResponse(
        subject_id=subject.id,
        total_topics=len(topics),
        generated_count=generated_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        setup_status=subject.setup_status,
        message=f"Generated {generated_count} explanations. "
                f"Skipped {skipped_count} (already exist). "
                f"Failed {failed_count}.",
    )


@router.get("/status", response_model=AllSubjectsSetupStatusResponse)
def get_all_setup_status(
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> AllSubjectsSetupStatusResponse:
    """
    Get setup status for all subjects.

    Updated for 008-academic-level-hierarchy:
    - Includes academic_level_name from parent level
    - Includes syllabi_count for each subject
    - syllabus_uploaded = True if any syllabi exist

    Returns setup status and counts for each subject.
    Used by admin dashboard to show setup progress.
    """
    # Join subjects with academic levels
    statement = select(Subject, AcademicLevel).join(
        AcademicLevel, Subject.academic_level_id == AcademicLevel.id
    )
    results = session.exec(statement).all()

    subject_statuses = []
    for subject, level in results:
        # Count syllabi for this subject
        syllabi_count = session.exec(
            select(func.count()).where(Syllabus.subject_id == subject.id)
        ).one()

        # Count topics
        topics_count = session.exec(
            select(func.count()).where(SyllabusPoint.subject_id == subject.id)
        ).one()

        # Count v1 explanations
        explanations_count = session.exec(
            select(func.count()).where(
                GeneratedExplanation.syllabus_point_id.in_(
                    select(SyllabusPoint.id).where(SyllabusPoint.subject_id == subject.id)
                ),
                GeneratedExplanation.version == 1,
            )
        ).one()

        subject_statuses.append(
            SubjectSetupStatusResponse(
                subject_id=subject.id,
                subject_name=subject.name,
                academic_level_name=level.name,
                setup_status=subject.setup_status,
                syllabi_count=syllabi_count,
                syllabus_uploaded=syllabi_count > 0,
                topics_count=topics_count,
                explanations_count=explanations_count,
                can_proceed_to_topics=subject.can_generate_topics(),
                can_proceed_to_explanations=subject.can_generate_explanations(),
                is_complete=subject.is_setup_complete(),
            )
        )

    all_complete = all(s.is_complete for s in subject_statuses) if subject_statuses else False

    return AllSubjectsSetupStatusResponse(
        subjects=subject_statuses,
        all_complete=all_complete,
        total_subjects=len(subject_statuses),
    )


@router.get("/status/{subject_id}", response_model=SubjectSetupStatusResponse)
def get_subject_setup_status(
    subject_id: UUID,
    session: Session = Depends(get_session),
    admin: Student = Depends(require_admin),
) -> SubjectSetupStatusResponse:
    """
    Get setup status for a specific subject.

    Updated for 008-academic-level-hierarchy:
    - Includes academic_level_name from parent level
    - Includes syllabi_count for the subject
    - syllabus_uploaded = True if any syllabi exist

    Returns detailed setup status including topic and explanation counts.
    """
    # Get subject with academic level
    statement = (
        select(Subject, AcademicLevel)
        .join(AcademicLevel, Subject.academic_level_id == AcademicLevel.id)
        .where(Subject.id == subject_id)
    )
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {subject_id} not found"
        )

    subject, level = result

    # Count syllabi for this subject
    syllabi_count = session.exec(
        select(func.count()).where(Syllabus.subject_id == subject.id)
    ).one()

    # Count topics
    topics_count = session.exec(
        select(func.count()).where(SyllabusPoint.subject_id == subject.id)
    ).one()

    # Count v1 explanations
    explanations_count = session.exec(
        select(func.count()).where(
            GeneratedExplanation.syllabus_point_id.in_(
                select(SyllabusPoint.id).where(SyllabusPoint.subject_id == subject.id)
            ),
            GeneratedExplanation.version == 1,
        )
    ).one()

    return SubjectSetupStatusResponse(
        subject_id=subject.id,
        subject_name=subject.name,
        academic_level_name=level.name,
        setup_status=subject.setup_status,
        syllabi_count=syllabi_count,
        syllabus_uploaded=syllabi_count > 0,
        topics_count=topics_count,
        explanations_count=explanations_count,
        can_proceed_to_topics=subject.can_generate_topics(),
        can_proceed_to_explanations=subject.can_generate_explanations(),
        is_complete=subject.is_setup_complete(),
    )
