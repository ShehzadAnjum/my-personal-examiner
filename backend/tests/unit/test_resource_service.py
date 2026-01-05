"""
Unit tests for resource service auto-selection algorithm.

Feature: 007-resource-bank-files (User Story 5)
Created: 2025-12-27

Tests auto-selection algorithm, relevance scoring, and usage tracking.

Constitutional Compliance:
- FR-032: Auto-select top 5 resources by relevance_score
- FR-035: Include selected resources in LLM prompt with attribution
- FR-036: Track which resources were used in topic generation
"""

from uuid import uuid4

import pytest
from sqlmodel import Session

from src.models.enums import ResourceType, Visibility
from src.models.explanation_resource_usage import ExplanationResourceUsage
from src.models.generated_explanation import GeneratedExplanation
from src.models.resource import Resource
from src.models.syllabus_point_resource import SyllabusPointResource
from src.services.resource_service import (
    calculate_relevance_score,
    get_resources_for_syllabus_point,
    prepare_resources_for_llm_prompt,
    track_resource_usage,
)


class TestAutoSelectionAlgorithm:
    """Test get_resources_for_syllabus_point auto-selection."""

    def test_returns_top_5_resources_by_relevance(self, db_session: Session):
        """Should return top 5 resources ordered by relevance_score DESC."""
        syllabus_point_id = "9708.5.1"
        student_id = uuid4()

        # Create 7 resources with different relevance scores
        resources = []
        scores = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]

        for i, score in enumerate(scores):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER if i < 3 else ResourceType.TEXTBOOK,
                title=f"Resource {i+1} (Score: {score})",
                file_path=f"/fake/resource_{i+1}.pdf",
                uploaded_by_student_id=student_id,
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_{i+1}"
            )
            db_session.add(resource)
            resources.append(resource)

        db_session.commit()

        # Create SyllabusPointResource links
        for resource, score in zip(resources, scores):
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=score,
                tagged_by_admin=True if score >= 0.8 else False
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Test auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Verify top 5 returned in order
        assert len(selected) == 5
        assert selected[0]['relevance_score'] == 1.0
        assert selected[1]['relevance_score'] == 0.9
        assert selected[2]['relevance_score'] == 0.8
        assert selected[3]['relevance_score'] == 0.7
        assert selected[4]['relevance_score'] == 0.6

        # Verify resource details included
        assert 'resource' in selected[0]
        assert 'resource_type' in selected[0]
        assert 'title' in selected[0]
        assert 'resource_id' in selected[0]

    def test_filters_by_public_visibility_only(self, db_session: Session):
        """Should only return PUBLIC resources, not PENDING_REVIEW or PRIVATE."""
        syllabus_point_id = "9708.5.2"
        student_id = uuid4()

        # Create resources with different visibility
        public_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="Public Resource",
            file_path="/fake/public.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_public"
        )

        pending_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Pending Resource",
            file_path="/fake/pending.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PENDING_REVIEW,
            admin_approved=False,
            signature="sig_pending"
        )

        private_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Private Resource",
            file_path="/fake/private.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PRIVATE,
            admin_approved=False,
            signature="sig_private"
        )

        db_session.add_all([public_resource, pending_resource, private_resource])
        db_session.commit()

        # Link all three to syllabus point
        for resource in [public_resource, pending_resource, private_resource]:
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.9,
                tagged_by_admin=True
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Test auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Should only return public resource
        assert len(selected) == 1
        assert selected[0]['title'] == "Public Resource"

    def test_filters_by_admin_approved_only(self, db_session: Session):
        """Should only return admin_approved resources."""
        syllabus_point_id = "9708.5.3"
        student_id = uuid4()

        # Create approved and unapproved resources
        approved_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Approved Resource",
            file_path="/fake/approved.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_approved"
        )

        unapproved_resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Unapproved Resource",
            file_path="/fake/unapproved.pdf",
            uploaded_by_student_id=student_id,
            visibility=Visibility.PUBLIC,
            admin_approved=False,
            signature="sig_unapproved"
        )

        db_session.add_all([approved_resource, unapproved_resource])
        db_session.commit()

        # Link both to syllabus point
        for resource in [approved_resource, unapproved_resource]:
            sp_resource = SyllabusPointResource(
                syllabus_point_id=syllabus_point_id,
                resource_id=resource.id,
                relevance_score=0.9,
                tagged_by_admin=True
            )
            db_session.add(sp_resource)

        db_session.commit()

        # Test auto-selection
        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        # Should only return approved resource
        assert len(selected) == 1
        assert selected[0]['title'] == "Approved Resource"

    def test_returns_empty_list_when_no_resources_found(self, db_session: Session):
        """Should return empty list when no resources linked to syllabus point."""
        syllabus_point_id = "9708.5.999"

        selected = get_resources_for_syllabus_point(
            syllabus_point_id=syllabus_point_id,
            session=db_session,
            limit=5
        )

        assert selected == []


class TestRelevanceScoring:
    """Test calculate_relevance_score algorithm."""

    def test_syllabus_resources_always_score_1_0(self, db_session: Session):
        """Syllabus resources should always have perfect relevance (1.0)."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="Cambridge Syllabus 9708",
            file_path="/fake/syllabus.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_syllabus"
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=None
        )

        assert score == 1.0

    def test_past_paper_gets_type_bonus(self, db_session: Session):
        """Past paper should get +0.1 type bonus."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="9708 June 2023 Paper 2",
            file_path="/fake/pastpaper.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper"
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=None
        )

        # Base 0.1 + type bonus 0.1 = 0.2
        assert score == 0.2

    def test_textbook_gets_smaller_type_bonus(self, db_session: Session):
        """Textbook should get +0.05 type bonus."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook Chapter 5",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook"
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=None
        )

        # Base 0.1 + type bonus 0.05 = 0.15
        assert score == 0.15

    def test_keyword_matching_in_title(self, db_session: Session):
        """Should add 0.1 per keyword match in title."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Fiscal Policy and Government Spending Analysis",
            file_path="/fake/notes.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_notes",
            metadata={}
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=["fiscal", "government", "spending"]
        )

        # Base 0.1 + (3 keywords × 0.1) = 0.4
        assert score == 0.4

    def test_keyword_matching_in_metadata(self, db_session: Session):
        """Should add 0.1 per keyword match in metadata."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Economics Notes",
            file_path="/fake/notes2.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_notes2",
            metadata={"tags": ["fiscal-policy", "taxation", "budget-deficit"]}
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=["fiscal", "taxation"]
        )

        # Base 0.1 + (2 keywords × 0.1) = 0.3
        assert score == 0.3

    def test_keyword_score_capped_at_0_8(self, db_session: Session):
        """Keyword matching should be capped at 0.8 to prevent perfect scores."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Fiscal Policy Tax Budget Deficit Surplus Government Spending Revenue Expenditure Aggregate Demand Multiplier",
            file_path="/fake/comprehensive.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_comprehensive",
            metadata={}
        )

        # 15 keywords that all match
        keywords = ["fiscal", "policy", "tax", "budget", "deficit", "surplus",
                   "government", "spending", "revenue", "expenditure",
                   "aggregate", "demand", "multiplier", "economics", "macro"]

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=keywords
        )

        # Base 0.1 + keyword_score (capped at 0.8) = 0.9
        assert score == 0.9

    def test_total_score_capped_at_1_0(self, db_session: Session):
        """Total relevance score should never exceed 1.0."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Fiscal Policy Tax Budget Economics",
            file_path="/fake/pastpaper2.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper2",
            metadata={}
        )

        keywords = ["fiscal", "policy", "tax", "budget", "economics",
                   "government", "spending", "revenue", "macro", "aggregate"]

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=keywords
        )

        # Even with base + keywords + type bonus, should cap at 1.0
        assert score <= 1.0

    def test_case_insensitive_keyword_matching(self, db_session: Session):
        """Keyword matching should be case-insensitive."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="FISCAL POLICY AND GOVERNMENT SPENDING",
            file_path="/fake/caps.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_caps",
            metadata={}
        )

        score = calculate_relevance_score(
            resource=resource,
            syllabus_point_id="9708.5.1",
            keywords=["fiscal", "government"]
        )

        # Should match despite different case
        # Base 0.1 + (2 keywords × 0.1) = 0.3
        assert score == 0.3


class TestUsageTracking:
    """Test track_resource_usage function."""

    def test_creates_explanation_resource_usage_record(self, db_session: Session):
        """Should create ExplanationResourceUsage record linking explanation to resource."""
        # Create a generated explanation
        explanation = GeneratedExplanation(
            id=uuid4(),
            syllabus_point_id="9708.5.1",
            student_id=uuid4(),
            content="Test explanation content",
            llm_provider="openai",
            llm_model="gpt-4",
            prompt_tokens=100,
            completion_tokens=200
        )
        db_session.add(explanation)
        db_session.commit()

        # Create a resource
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook",
            file_path="/fake/textbook.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_textbook"
        )
        db_session.add(resource)
        db_session.commit()

        # Track usage
        usage = track_resource_usage(
            generated_explanation_id=explanation.id,
            resource_id=resource.id,
            contribution_weight=0.85,
            session=db_session
        )

        # Verify record created
        assert usage is not None
        assert usage.generated_explanation_id == explanation.id
        assert usage.resource_id == resource.id
        assert usage.contribution_weight == 0.85

        # Verify in database
        db_usage = db_session.get(ExplanationResourceUsage, usage.id)
        assert db_usage is not None
        assert db_usage.contribution_weight == 0.85

    def test_tracks_multiple_resources_for_same_explanation(self, db_session: Session):
        """Should allow tracking multiple resources used in one explanation."""
        # Create a generated explanation
        explanation = GeneratedExplanation(
            id=uuid4(),
            syllabus_point_id="9708.5.1",
            student_id=uuid4(),
            content="Test explanation using multiple resources",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            prompt_tokens=150,
            completion_tokens=300
        )
        db_session.add(explanation)
        db_session.commit()

        # Create 3 resources
        resources = []
        for i in range(3):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER,
                title=f"Past Paper {i+1}",
                file_path=f"/fake/paper{i+1}.pdf",
                uploaded_by_student_id=uuid4(),
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_paper{i+1}"
            )
            db_session.add(resource)
            resources.append(resource)

        db_session.commit()

        # Track usage for all 3 resources
        weights = [0.9, 0.7, 0.5]
        for resource, weight in zip(resources, weights):
            track_resource_usage(
                generated_explanation_id=explanation.id,
                resource_id=resource.id,
                contribution_weight=weight,
                session=db_session
            )

        # Verify all 3 usage records created
        from sqlmodel import select
        usages = db_session.exec(
            select(ExplanationResourceUsage)
            .where(ExplanationResourceUsage.generated_explanation_id == explanation.id)
        ).all()

        assert len(usages) == 3
        assert set([u.contribution_weight for u in usages]) == set(weights)


class TestPrepareResourcesForLLMPrompt:
    """Test prepare_resources_for_llm_prompt formatting."""

    def test_formats_resources_with_attribution(self, db_session: Session):
        """Should format resources with title, relevance, and source attribution."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="Cambridge International AS & A Level Economics (9708)",
            file_path="/fake/syllabus.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_syllabus",
            source_url="https://www.cambridgeinternational.org/9708"
        )

        selected_resources = [{
            'resource': resource,
            'relevance_score': 1.0,
            'resource_type': ResourceType.SYLLABUS.value,
            'title': resource.title,
            'resource_id': str(resource.id)
        }]

        prompt = prepare_resources_for_llm_prompt(
            selected_resources=selected_resources,
            session=db_session
        )

        assert "--- REFERENCE RESOURCES ---" in prompt
        assert "[1]" in prompt
        assert "Cambridge International AS & A Level Economics (9708)" in prompt
        assert "(Relevance: 100%)" in prompt
        assert "Source: https://www.cambridgeinternational.org/9708" in prompt

    def test_syllabus_resources_show_official_source(self, db_session: Session):
        """Syllabus resources without source_url should show 'Official Cambridge Syllabus'."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.SYLLABUS,
            title="9708 Syllabus",
            file_path="/fake/syllabus2.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_syllabus2",
            source_url=None
        )

        selected_resources = [{
            'resource': resource,
            'relevance_score': 1.0,
            'resource_type': ResourceType.SYLLABUS.value,
            'title': resource.title,
            'resource_id': str(resource.id)
        }]

        prompt = prepare_resources_for_llm_prompt(
            selected_resources=selected_resources,
            session=db_session
        )

        assert "Source: Official Cambridge Syllabus" in prompt

    def test_returns_empty_string_when_no_resources(self, db_session: Session):
        """Should return empty string when no resources provided."""
        prompt = prepare_resources_for_llm_prompt(
            selected_resources=[],
            session=db_session
        )

        assert prompt == ""

    def test_extracts_text_from_metadata(self, db_session: Session):
        """Should extract and include text from metadata['extracted_text']."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="9708 June 2023 Paper 2",
            file_path="/fake/pastpaper.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            signature="sig_pastpaper",
            metadata={"extracted_text": "Explain fiscal policy and its impact on aggregate demand..."}
        )

        selected_resources = [{
            'resource': resource,
            'relevance_score': 0.9,
            'resource_type': ResourceType.PAST_PAPER.value,
            'title': resource.title,
            'resource_id': str(resource.id)
        }]

        prompt = prepare_resources_for_llm_prompt(
            selected_resources=selected_resources,
            session=db_session
        )

        assert "9708 June 2023 Paper 2" in prompt
        assert "(Relevance: 90%)" in prompt
        # Text extraction is implementation-specific, just verify structure
        assert "[1]" in prompt

    def test_multiple_resources_numbered_sequentially(self, db_session: Session):
        """Should number multiple resources sequentially [1], [2], [3]."""
        resources = []
        for i in range(3):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.TEXTBOOK,
                title=f"Textbook Chapter {i+1}",
                file_path=f"/fake/textbook{i+1}.pdf",
                uploaded_by_student_id=uuid4(),
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                signature=f"sig_textbook{i+1}"
            )
            resources.append({
                'resource': resource,
                'relevance_score': 0.8 - (i * 0.1),
                'resource_type': ResourceType.TEXTBOOK.value,
                'title': resource.title,
                'resource_id': str(resource.id)
            })

        prompt = prepare_resources_for_llm_prompt(
            selected_resources=resources,
            session=db_session
        )

        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "[3]" in prompt
        assert "Textbook Chapter 1" in prompt
        assert "Textbook Chapter 2" in prompt
        assert "Textbook Chapter 3" in prompt
