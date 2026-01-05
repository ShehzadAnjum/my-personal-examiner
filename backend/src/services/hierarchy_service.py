"""
Hierarchy Service

Business logic for managing the three-tier hierarchy:
Academic Level → Subject → Syllabus

Feature: 008-academic-level-hierarchy

Constitutional Requirements:
- Principle I: Subject accuracy - all subjects must match official syllabi
- Principle V: Multi-tenant isolation - applies to user-scoped operations only
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from src.models.academic_level import AcademicLevel
from src.models.subject import Subject, SubjectSetupStatus
from src.models.syllabus import Syllabus
from src.models.syllabus_point import SyllabusPoint
from src.schemas.academic_level_schemas import (
    AcademicLevelCreate,
    AcademicLevelDetail,
    AcademicLevelNode,
    AcademicLevelSummary,
    AcademicLevelUpdate,
    HierarchyTree,
    SubjectCreate,
    SubjectNode,
    SubjectSummaryForLevel,
    SyllabusNode,
)
from src.schemas.syllabus_schemas import (
    SyllabusCreate,
    SyllabusDetail,
    SyllabusSummary,
)


class HierarchyServiceError(Exception):
    """Base exception for hierarchy service errors."""
    pass


class DuplicateCodeError(HierarchyServiceError):
    """Raised when trying to create an entity with a duplicate code."""
    pass


class NotFoundError(HierarchyServiceError):
    """Raised when an entity is not found."""
    pass


class DependencyError(HierarchyServiceError):
    """Raised when trying to delete an entity with dependencies."""
    pass


class HierarchyService:
    """Service for managing the academic level hierarchy."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    # ===========================================================================
    # Academic Level Operations (T013-T015)
    # ===========================================================================

    def create_academic_level(self, data: AcademicLevelCreate) -> AcademicLevel:
        """
        Create a new academic level.

        Args:
            data: Academic level creation data

        Returns:
            Created AcademicLevel entity

        Raises:
            DuplicateCodeError: If an academic level with this code already exists
        """
        # Check for duplicate code
        existing = self.session.exec(
            select(AcademicLevel).where(AcademicLevel.code == data.code.upper())
        ).first()
        if existing:
            raise DuplicateCodeError(
                f"Academic level with code '{data.code}' already exists"
            )

        # Create new academic level
        academic_level = AcademicLevel(
            name=data.name,
            code=data.code.upper(),
            description=data.description,
            exam_board=data.exam_board,
        )
        self.session.add(academic_level)
        self.session.commit()
        self.session.refresh(academic_level)
        return academic_level

    def list_academic_levels(self, include_counts: bool = True) -> list[AcademicLevelSummary]:
        """
        List all academic levels with optional subject counts.

        Args:
            include_counts: Whether to include subjects_count

        Returns:
            List of AcademicLevelSummary objects
        """
        if include_counts:
            # Query with subject counts using subquery
            subq = (
                select(Subject.academic_level_id, func.count(Subject.id).label("count"))
                .group_by(Subject.academic_level_id)
                .subquery()
            )
            results = self.session.exec(
                select(AcademicLevel, func.coalesce(subq.c.count, 0))
                .outerjoin(subq, AcademicLevel.id == subq.c.academic_level_id)
                .order_by(AcademicLevel.name)
            ).all()
            return [
                AcademicLevelSummary(
                    id=level.id,
                    name=level.name,
                    code=level.code,
                    exam_board=level.exam_board,
                    subjects_count=count,
                )
                for level, count in results
            ]
        else:
            levels = self.session.exec(
                select(AcademicLevel).order_by(AcademicLevel.name)
            ).all()
            return [
                AcademicLevelSummary(
                    id=level.id,
                    name=level.name,
                    code=level.code,
                    exam_board=level.exam_board,
                    subjects_count=0,
                )
                for level in levels
            ]

    def get_academic_level(self, level_id: UUID) -> AcademicLevelDetail:
        """
        Get an academic level by ID with its subjects.

        Args:
            level_id: Academic level UUID

        Returns:
            AcademicLevelDetail with subjects

        Raises:
            NotFoundError: If academic level not found
        """
        level = self.session.get(AcademicLevel, level_id)
        if not level:
            raise NotFoundError(f"Academic level with ID {level_id} not found")

        # Get subjects with syllabi counts
        subjects = self.session.exec(
            select(Subject).where(Subject.academic_level_id == level_id)
        ).all()

        subject_summaries = []
        for subject in subjects:
            syllabi_count = self.session.exec(
                select(func.count(Syllabus.id)).where(Syllabus.subject_id == subject.id)
            ).one()
            subject_summaries.append(
                SubjectSummaryForLevel(
                    id=subject.id,
                    name=subject.name,
                    setup_status=subject.setup_status,
                    syllabi_count=syllabi_count,
                )
            )

        return AcademicLevelDetail(
            id=level.id,
            name=level.name,
            code=level.code,
            description=level.description,
            exam_board=level.exam_board,
            created_at=level.created_at,
            updated_at=level.updated_at,
            subjects=subject_summaries,
        )

    def update_academic_level(
        self, level_id: UUID, data: AcademicLevelUpdate
    ) -> AcademicLevel:
        """
        Update an academic level.

        Args:
            level_id: Academic level UUID
            data: Update data

        Returns:
            Updated AcademicLevel

        Raises:
            NotFoundError: If academic level not found
        """
        level = self.session.get(AcademicLevel, level_id)
        if not level:
            raise NotFoundError(f"Academic level with ID {level_id} not found")

        # Update fields if provided
        if data.name is not None:
            level.name = data.name
        if data.description is not None:
            level.description = data.description
        if data.exam_board is not None:
            level.exam_board = data.exam_board
        level.updated_at = datetime.utcnow()

        self.session.add(level)
        self.session.commit()
        self.session.refresh(level)
        return level

    def delete_academic_level(self, level_id: UUID) -> None:
        """
        Delete an academic level.

        Args:
            level_id: Academic level UUID

        Raises:
            NotFoundError: If academic level not found
            DependencyError: If level has subjects (RESTRICT)
        """
        level = self.session.get(AcademicLevel, level_id)
        if not level:
            raise NotFoundError(f"Academic level with ID {level_id} not found")

        # Check for dependent subjects
        subject_count = self.session.exec(
            select(func.count(Subject.id)).where(Subject.academic_level_id == level_id)
        ).one()
        if subject_count > 0:
            raise DependencyError(
                f"Cannot delete academic level with {subject_count} subject(s). "
                "Delete or reassign subjects first."
            )

        self.session.delete(level)
        self.session.commit()

    # ===========================================================================
    # Subject Operations (US2)
    # ===========================================================================

    def create_subject_for_level(
        self, level_id: UUID, data: SubjectCreate
    ) -> Subject:
        """
        Create a new subject under an academic level.

        Args:
            level_id: Parent academic level UUID
            data: Subject creation data

        Returns:
            Created Subject entity

        Raises:
            NotFoundError: If academic level not found
            DuplicateCodeError: If subject with same name exists under this level
        """
        # Verify academic level exists
        level = self.session.get(AcademicLevel, level_id)
        if not level:
            raise NotFoundError(f"Academic level with ID {level_id} not found")

        # Check for duplicate name under this level
        existing = self.session.exec(
            select(Subject).where(
                Subject.academic_level_id == level_id,
                Subject.name == data.name,
            )
        ).first()
        if existing:
            raise DuplicateCodeError(
                f"Subject '{data.name}' already exists under {level.name}"
            )

        # Create new subject
        subject = Subject(
            academic_level_id=level_id,
            name=data.name,
            setup_status=SubjectSetupStatus.PENDING.value,
        )
        self.session.add(subject)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def list_subjects_for_level(self, level_id: UUID) -> list[SubjectSummaryForLevel]:
        """
        List all subjects under an academic level.

        Args:
            level_id: Academic level UUID

        Returns:
            List of SubjectSummaryForLevel objects

        Raises:
            NotFoundError: If academic level not found
        """
        # Verify academic level exists
        level = self.session.get(AcademicLevel, level_id)
        if not level:
            raise NotFoundError(f"Academic level with ID {level_id} not found")

        subjects = self.session.exec(
            select(Subject)
            .where(Subject.academic_level_id == level_id)
            .order_by(Subject.name)
        ).all()

        result = []
        for subject in subjects:
            syllabi_count = self.session.exec(
                select(func.count(Syllabus.id)).where(Syllabus.subject_id == subject.id)
            ).one()
            result.append(
                SubjectSummaryForLevel(
                    id=subject.id,
                    name=subject.name,
                    setup_status=subject.setup_status,
                    syllabi_count=syllabi_count,
                )
            )
        return result

    # ===========================================================================
    # Syllabus Operations (US3)
    # ===========================================================================

    def create_syllabus_for_subject(
        self, subject_id: UUID, data: SyllabusCreate
    ) -> Syllabus:
        """
        Create a new syllabus for a subject.

        Args:
            subject_id: Parent subject UUID
            data: Syllabus creation data

        Returns:
            Created Syllabus entity

        Raises:
            NotFoundError: If subject not found
            DuplicateCodeError: If syllabus with same code exists for this subject
        """
        # Verify subject exists
        subject = self.session.get(Subject, subject_id)
        if not subject:
            raise NotFoundError(f"Subject with ID {subject_id} not found")

        # Check for duplicate code under this subject
        existing = self.session.exec(
            select(Syllabus).where(
                Syllabus.subject_id == subject_id,
                Syllabus.code == data.code,
            )
        ).first()
        if existing:
            raise DuplicateCodeError(
                f"Syllabus code '{data.code}' already exists for subject {subject.name}"
            )

        # Create new syllabus
        syllabus = Syllabus(
            subject_id=subject_id,
            code=data.code,
            year_range=data.year_range,
            version=1,
            is_active=True,
        )
        self.session.add(syllabus)
        self.session.commit()
        self.session.refresh(syllabus)
        return syllabus

    def list_syllabi_for_subject(self, subject_id: UUID) -> list[SyllabusSummary]:
        """
        List all syllabi for a subject.

        Args:
            subject_id: Subject UUID

        Returns:
            List of SyllabusSummary objects

        Raises:
            NotFoundError: If subject not found
        """
        # Verify subject exists
        subject = self.session.get(Subject, subject_id)
        if not subject:
            raise NotFoundError(f"Subject with ID {subject_id} not found")

        syllabi = self.session.exec(
            select(Syllabus)
            .where(Syllabus.subject_id == subject_id)
            .order_by(Syllabus.year_range.desc())
        ).all()

        result = []
        for syllabus in syllabi:
            topics_count = self.session.exec(
                select(func.count(SyllabusPoint.id)).where(
                    SyllabusPoint.syllabus_id == syllabus.id
                )
            ).one()
            result.append(
                SyllabusSummary(
                    id=syllabus.id,
                    code=syllabus.code,
                    year_range=syllabus.year_range,
                    is_active=syllabus.is_active,
                    topics_count=topics_count,
                )
            )
        return result

    # ===========================================================================
    # Hierarchy Tree (US4)
    # ===========================================================================

    def get_hierarchy_tree(self) -> HierarchyTree:
        """
        Get the complete hierarchy tree.

        Returns:
            HierarchyTree with all academic levels, subjects, and syllabi
        """
        levels = self.session.exec(
            select(AcademicLevel).order_by(AcademicLevel.name)
        ).all()

        level_nodes = []
        for level in levels:
            subjects = self.session.exec(
                select(Subject)
                .where(Subject.academic_level_id == level.id)
                .order_by(Subject.name)
            ).all()

            subject_nodes = []
            for subject in subjects:
                syllabi = self.session.exec(
                    select(Syllabus)
                    .where(Syllabus.subject_id == subject.id)
                    .order_by(Syllabus.year_range.desc())
                ).all()

                syllabus_nodes = []
                for syllabus in syllabi:
                    topics_count = self.session.exec(
                        select(func.count(SyllabusPoint.id)).where(
                            SyllabusPoint.syllabus_id == syllabus.id
                        )
                    ).one()
                    syllabus_nodes.append(
                        SyllabusNode(
                            id=syllabus.id,
                            code=syllabus.code,
                            year_range=syllabus.year_range,
                            is_active=syllabus.is_active,
                            topics_count=topics_count,
                        )
                    )

                subject_nodes.append(
                    SubjectNode(
                        id=subject.id,
                        name=subject.name,
                        syllabi=syllabus_nodes,
                    )
                )

            level_nodes.append(
                AcademicLevelNode(
                    id=level.id,
                    name=level.name,
                    code=level.code,
                    subjects=subject_nodes,
                )
            )

        return HierarchyTree(academic_levels=level_nodes)
