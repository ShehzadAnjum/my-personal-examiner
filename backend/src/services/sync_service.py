"""
Cambridge Resource Sync Service.

Feature: 007-resource-bank-files (User Story 2)
Created: 2025-12-27

Functions for scraping Cambridge website, downloading past papers,
and linking mark schemes to question papers.

Daily sync workflow:
1. Scrape Cambridge website for Economics 9708 resources
2. Extract past paper URLs (last 10 years)
3. Download PDFs with signature-based change detection
4. Link mark schemes to corresponding question papers
5. Store in backend/resources/past_papers/9708/
6. Create database records
7. Queue S3 background uploads
"""

import hashlib
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from src.database import get_engine
from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.services.file_storage_service import (
    calculate_signature,
    get_file_path_for_resource,
    save_file_to_local,
)


def scrape_cambridge_website(subject_code: str = "9708") -> List[Dict[str, str]]:
    """
    Scrape Cambridge website for Economics 9708 past papers.

    Phase 1 Implementation:
    - Returns mock data structure for testing
    - Phase 2 will implement actual web scraping with selenium/BeautifulSoup

    Returns list of dictionaries with:
    - url: Download URL for PDF
    - filename: Filename (e.g., "2024_m_qp_12.pdf")
    - year: Exam year (e.g., "2024")
    - session: Exam session (m=May/June, s=Oct/Nov, w=Feb/March)
    - paper: Paper number (e.g., "12")
    - type: "question_paper" or "mark_scheme"
    - title: Human-readable title

    Args:
        subject_code: Cambridge subject code (default: 9708 for Economics)

    Returns:
        List of resource metadata dictionaries
    """
    # Phase 1: Mock implementation
    # Phase 2: Replace with actual Cambridge website scraping
    # Example URL: https://papers.gceguide.com/A%20Levels/Economics%20(9708)/

    resources = []

    # TODO Phase 2: Implement actual scraping
    # base_url = f"https://papers.gceguide.com/A%20Levels/Economics%20({subject_code})/"
    # response = requests.get(base_url, timeout=30)
    # soup = BeautifulSoup(response.content, 'html.parser')
    #
    # for link in soup.find_all('a', href=re.compile(r'\.pdf$')):
    #     filename = link['href'].split('/')[-1]
    #     metadata = parse_cambridge_filename(filename)
    #     if metadata:
    #         resources.append({
    #             'url': link['href'],
    #             'filename': filename,
    #             **metadata
    #         })

    return resources


def parse_cambridge_filename(filename: str) -> Optional[Dict[str, str]]:
    """
    Parse Cambridge filename to extract metadata.

    Cambridge naming convention:
    - Question papers: {subject}_{year}_{session}_{paper}.pdf (e.g., "9708_m24_qp_12.pdf")
    - Mark schemes: {subject}_{year}_{session}_{paper}_ms.pdf (e.g., "9708_m24_ms_12.pdf")

    Args:
        filename: Cambridge PDF filename

    Returns:
        Dictionary with year, session, paper, type fields, or None if invalid
    """
    # Pattern: 9708_s23_qp_12.pdf or 9708_s23_ms_12.pdf
    pattern = r'(\d{4})_(m|s|w)(\d{2})_(qp|ms)_(\d{1,2})\.pdf'
    match = re.match(pattern, filename.lower())

    if not match:
        return None

    subject, session_letter, year_suffix, paper_type, paper_num = match.groups()

    # Convert session letter to full name
    session_map = {
        'm': 'May/June',
        's': 'Oct/Nov',
        'w': 'Feb/March'
    }

    # Convert 2-digit year to 4-digit
    year = f"20{year_suffix}"

    # Determine resource type
    resource_type = "mark_scheme" if paper_type == "ms" else "question_paper"

    # Generate human-readable title
    title = f"Economics {subject} {session_map[session_letter]} {year} Paper {paper_num}"
    if resource_type == "mark_scheme":
        title += " (Mark Scheme)"

    return {
        'year': year,
        'session': session_letter,
        'paper': paper_num,
        'type': resource_type,
        'title': title
    }


def download_past_paper(url: str, destination_path: str) -> bool:
    """
    Download past paper PDF from Cambridge website.

    Args:
        url: Download URL for PDF
        destination_path: Local file path to save PDF

    Returns:
        True if download successful, False otherwise

    Raises:
        requests.exceptions.RequestException: If download fails
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        # Create parent directories if needed
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Write file in chunks to handle large files
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    except requests.exceptions.RequestException as e:
        # Log error and return False
        print(f"ERROR: Failed to download {url}: {str(e)}")
        return False


def link_mark_scheme(
    question_paper_id: UUID,
    mark_scheme_id: UUID,
    session: Session
) -> None:
    """
    Link mark scheme to question paper in database.

    Uses metadata.mark_scheme_id JSONB field to create relationship.

    Args:
        question_paper_id: UUID of question paper resource
        mark_scheme_id: UUID of mark scheme resource
        session: SQLModel database session
    """
    question_paper = session.get(Resource, question_paper_id)

    if not question_paper:
        raise ValueError(f"Question paper {question_paper_id} not found")

    # Update metadata JSONB field
    if question_paper.metadata is None:
        question_paper.metadata = {}

    question_paper.metadata['mark_scheme_id'] = str(mark_scheme_id)

    session.add(question_paper)
    session.commit()


def check_resource_exists(signature: str, session: Session) -> Optional[Resource]:
    """
    Check if resource with given signature already exists.

    Signature-based change detection:
    - If signature exists, resource is unchanged (skip download)
    - If signature doesn't exist, resource is new (download)

    Args:
        signature: SHA-256 hash of file content
        session: SQLModel database session

    Returns:
        Existing Resource if found, None otherwise
    """
    statement = select(Resource).where(Resource.signature == signature)
    return session.exec(statement).first()


def sync_past_paper_from_url(
    url: str,
    metadata: Dict[str, str],
    session: Session,
    subject_code: str = "9708"
) -> Optional[Resource]:
    """
    Download and store single past paper from URL.

    Workflow:
    1. Download PDF to temporary location
    2. Calculate SHA-256 signature
    3. Check if already exists (skip if duplicate)
    4. Save to permanent storage
    5. Create database record
    6. Update last_checked timestamp
    7. Return created Resource

    Args:
        url: Download URL for PDF
        metadata: Parsed metadata (year, session, paper, type, title)
        session: SQLModel database session
        subject_code: Cambridge subject code (default: 9708)

    Returns:
        Created Resource record, or None if duplicate/failed
    """
    # Generate filename
    year = metadata['year']
    session_letter = metadata['session']
    paper = metadata['paper']
    paper_type = "ms" if metadata['type'] == "mark_scheme" else "qp"
    filename = f"{year}_{session_letter}_{paper_type}_{paper}.pdf"

    # Download to temporary location
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_path = temp_file.name

    try:
        # Download PDF
        if not download_past_paper(url, temp_path):
            return None

        # Calculate signature
        signature = calculate_signature(temp_path)

        # Check if duplicate
        existing = check_resource_exists(signature, session)
        if existing:
            # Update last_checked timestamp
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            print(f"INFO: Resource {filename} unchanged (signature match), skipped")
            os.remove(temp_path)
            return None

        # Determine final file path
        file_path = get_file_path_for_resource(
            resource_type=ResourceType.PAST_PAPER,
            filename=filename,
            subject_code=subject_code
        )

        # Save to permanent storage
        absolute_path = save_file_to_local(temp_path, file_path)

        # Create database record
        resource_type = (
            ResourceType.PAST_PAPER if metadata['type'] == "question_paper"
            else ResourceType.PAST_PAPER  # Mark schemes also use PAST_PAPER type
        )

        resource = Resource(
            id=uuid4(),
            resource_type=resource_type,
            title=metadata['title'],
            source_url=url,
            file_path=file_path,
            signature=signature,
            visibility=Visibility.PUBLIC,  # Past papers are public
            admin_approved=True,  # Auto-approve Cambridge official resources
            s3_sync_status=S3SyncStatus.PENDING,
            metadata={
                'year': metadata['year'],
                'session': metadata['session'],
                'paper': metadata['paper'],
                'resource_subtype': metadata['type']  # question_paper or mark_scheme
            }
        )

        session.add(resource)
        session.commit()
        session.refresh(resource)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        print(f"INFO: Created resource {filename} (ID: {resource.id})")
        return resource

    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"ERROR: Failed to sync {filename}: {str(e)}")
        return None


def sync_cambridge_resources(
    subject_code: str = "9708",
    years_back: int = 10
) -> Dict[str, any]:
    """
    Main sync function: Download all new past papers from Cambridge.

    Called by daily Celery Beat job at 2AM.

    Workflow:
    1. Scrape Cambridge website for Economics 9708
    2. Filter past papers from last {years_back} years
    3. Download each past paper (skip if signature match)
    4. Link mark schemes to question papers
    5. Return summary statistics

    Args:
        subject_code: Cambridge subject code (default: 9708)
        years_back: How many years of past papers to sync (default: 10)

    Returns:
        Dictionary with sync statistics:
        - total_found: Total resources on Cambridge website
        - new_downloaded: New resources downloaded
        - skipped_duplicates: Resources skipped (signature match)
        - failed: Resources that failed to download
        - mark_schemes_linked: Mark schemes successfully linked
    """
    engine = get_engine()

    with Session(engine) as session:
        # Scrape Cambridge website
        all_resources = scrape_cambridge_website(subject_code)

        # Filter by year (last {years_back} years)
        current_year = datetime.now().year
        cutoff_year = current_year - years_back

        resources = [
            r for r in all_resources
            if int(r.get('year', '0')) >= cutoff_year
        ]

        # Track statistics
        stats = {
            'total_found': len(resources),
            'new_downloaded': 0,
            'skipped_duplicates': 0,
            'failed': 0,
            'mark_schemes_linked': 0
        }

        # Store question paper IDs for linking
        question_papers = {}  # Key: (year, session, paper) -> Resource ID
        mark_schemes = []  # List of (year, session, paper, resource_id) tuples

        # Download each resource
        for resource_meta in resources:
            url = resource_meta.get('url')
            if not url:
                stats['failed'] += 1
                continue

            # Sync resource
            created_resource = sync_past_paper_from_url(url, resource_meta, session, subject_code)

            if created_resource:
                stats['new_downloaded'] += 1

                # Track for linking
                key = (
                    resource_meta['year'],
                    resource_meta['session'],
                    resource_meta['paper']
                )

                if resource_meta['type'] == 'question_paper':
                    question_papers[key] = created_resource.id
                else:  # mark_scheme
                    mark_schemes.append((*key, created_resource.id))
            else:
                stats['skipped_duplicates'] += 1

        # Link mark schemes to question papers
        for year, session, paper, ms_id in mark_schemes:
            key = (year, session, paper)
            if key in question_papers:
                try:
                    link_mark_scheme(question_papers[key], ms_id, session)
                    stats['mark_schemes_linked'] += 1
                except Exception as e:
                    print(f"ERROR: Failed to link mark scheme {ms_id}: {str(e)}")

        return stats
