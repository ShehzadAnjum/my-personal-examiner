"""
Celery tasks for PDF text extraction and OCR processing.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Background tasks:
- extract_text_task: Extract text from uploaded PDF (background processing for large files)
- batch_ocr_scanned_pdfs: Batch process scanned PDFs detected during upload

Retry strategy:
- Max 2 retries (OCR is resource-intensive)
- 5-minute delay between retries
- Update resource.resource_metadata with extracted text
"""

import logging
from typing import Dict

from celery import Task
from sqlmodel import Session

from src.database import get_engine
from src.models.resource import Resource
from src.services.pdf_extraction_service import extract_pdf_text
from src.tasks.celery_app import app

logger = logging.getLogger(__name__)


class OCRTask(Task):
    """
    Custom Celery Task for OCR operations.

    Retry strategy:
    - Max 2 attempts (OCR is expensive, avoid excessive retries)
    - 5-minute delay between retries (300 seconds)
    - No jitter (predictable scheduling)
    """
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = 300  # 5 minutes
    retry_jitter = False


@app.task(bind=True, base=OCRTask, name='tasks.extract_text')
def extract_text_task(self, resource_id: str) -> Dict[str, any]:
    """
    Extract text from PDF resource in background.

    Called after resource upload completes. Extracts text using PyPDF2
    with OCR fallback for scanned PDFs, then stores in resource.resource_metadata.

    Args:
        resource_id: UUID of Resource record

    Returns:
        Dictionary with extraction results:
        - status: "success" | "failed"
        - method: "native" | "ocr"
        - char_count: Characters extracted
        - page_count: Number of pages
        - resource_id: Resource UUID
        - error: Error message (if failed)

    Side Effects:
        Updates resource.resource_metadata['extracted_text'] and metadata['extraction_method']
    """
    try:
        logger.info(f"Starting text extraction for resource {resource_id}")

        engine = get_engine()

        with Session(engine) as session:
            # Get resource
            resource = session.get(Resource, resource_id)

            if not resource:
                raise ValueError(f"Resource {resource_id} not found")

            # Extract text from PDF
            extraction_result = extract_pdf_text(resource.file_path, ocr_threshold=100)

            # Update resource metadata with extracted text
            if resource.resource_metadata is None:
                resource.resource_metadata = {}

            resource.resource_metadata['extracted_text'] = extraction_result['text']
            resource.resource_metadata['extraction_method'] = extraction_result['method']
            resource.resource_metadata['page_count'] = extraction_result['page_count']
            resource.resource_metadata['char_count'] = extraction_result['char_count']
            resource.resource_metadata['ocr_triggered'] = extraction_result['ocr_triggered']

            session.add(resource)
            session.commit()

            logger.info(
                f"Text extraction completed for {resource_id}: "
                f"{extraction_result['char_count']} chars via {extraction_result['method']}"
            )

            return {
                'status': 'success',
                'method': extraction_result['method'],
                'char_count': extraction_result['char_count'],
                'page_count': extraction_result['page_count'],
                'resource_id': resource_id
            }

    except Exception as exc:
        logger.error(f"Text extraction failed for {resource_id}: {str(exc)}")

        # Check if max retries reached
        if self.request.retries >= 1:  # 0-indexed, so 1 = 2nd attempt
            logger.critical(
                f"ALERT: Text extraction failed after 2 attempts for resource {resource_id}. "
                f"Error: {str(exc)}"
            )

            # Update resource metadata with error
            try:
                engine = get_engine()
                with Session(engine) as session:
                    resource = session.get(Resource, resource_id)
                    if resource:
                        if resource.resource_metadata is None:
                            resource.resource_metadata = {}

                        resource.resource_metadata['extraction_error'] = str(exc)
                        resource.resource_metadata['extraction_status'] = 'failed'

                        session.add(resource)
                        session.commit()
            except Exception as update_error:
                logger.error(f"Failed to update resource with error: {update_error}")

            return {
                'status': 'failed',
                'resource_id': resource_id,
                'error': str(exc),
                'retries_exhausted': True
            }

        # Retry
        raise self.retry(exc=exc)


@app.task(name='tasks.batch_ocr_scanned_pdfs')
def batch_ocr_scanned_pdfs() -> Dict[str, any]:
    """
    Batch process scanned PDFs that were uploaded but not yet OCR'd.

    Finds resources where:
    - metadata.extraction_status = 'pending_ocr'
    - metadata.ocr_triggered = True
    - metadata.extracted_text is empty or missing

    Queues them for OCR processing.

    Returns:
        Dictionary with batch processing statistics
    """
    try:
        from sqlmodel import select

        engine = get_engine()

        with Session(engine) as session:
            # Find resources pending OCR
            # (In Phase 1, we don't have a dedicated status field, so this is placeholder logic)
            # Phase 2: Add resource.ocr_status field to Resource model

            # For now, we'll just return a success message
            # Actual batch OCR will be implemented in Phase 2

            logger.info("Batch OCR task executed (Phase 1: placeholder)")

            return {
                'status': 'success',
                'processed_count': 0,
                'message': 'Batch OCR not yet implemented (Phase 1)'
            }

    except Exception as e:
        logger.error(f"Batch OCR task failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@app.task(name='tasks.extract_page_range')
def extract_page_range_task(resource_id: str, start_page: int, end_page: int) -> Dict[str, any]:
    """
    Extract text from specific page range (for textbook excerpts).

    Called when admin specifies page range during resource tagging.

    Args:
        resource_id: UUID of Resource record
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed, inclusive)

    Returns:
        Dictionary with extracted text and metadata
    """
    try:
        from src.services.pdf_extraction_service import extract_text_from_page_range

        logger.info(f"Extracting pages {start_page}-{end_page} from resource {resource_id}")

        engine = get_engine()

        with Session(engine) as session:
            resource = session.get(Resource, resource_id)

            if not resource:
                raise ValueError(f"Resource {resource_id} not found")

            # Extract text from page range
            excerpt_text = extract_text_from_page_range(
                resource.file_path,
                start_page,
                end_page
            )

            # Update metadata with excerpt
            if resource.resource_metadata is None:
                resource.resource_metadata = {}

            resource.resource_metadata['excerpt_text'] = excerpt_text
            resource.resource_metadata['excerpt_pages'] = f"{start_page}-{end_page}"

            session.add(resource)
            session.commit()

            logger.info(
                f"Page range extraction completed for {resource_id}: "
                f"pages {start_page}-{end_page}, {len(excerpt_text)} chars"
            )

            return {
                'status': 'success',
                'resource_id': resource_id,
                'page_range': f"{start_page}-{end_page}",
                'char_count': len(excerpt_text)
            }

    except Exception as e:
        logger.error(f"Page range extraction failed for {resource_id}: {str(e)}")
        return {
            'status': 'failed',
            'resource_id': resource_id,
            'error': str(e)
        }
