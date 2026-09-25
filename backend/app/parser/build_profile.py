from __future__ import annotations

from app.core.config import Settings
from app.parser.normalize import merge_facts, normalize_document
from app.parser.pdf_extract import extract_text_from_pdf
from app.schemas.profile import CandidateProfile


def _truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def build_candidate_profile(
    *,
    linkedin_pdf_bytes: bytes,
    resume_pdf_bytes: bytes,
    target_role: str | None,
    job_description: str | None,
    settings: Settings,
) -> CandidateProfile:
    """
    Extract text from both PDFs, normalize each into structured facts,
    merge them, and assemble the CandidateProfile passed into analysis.

    Raises PDFExtractionError / ScannedPDFError (from pdf_extract) on
    unreadable input — callers should catch these and surface
    `.user_message` directly to the user.
    """
    linkedin_result = extract_text_from_pdf(linkedin_pdf_bytes, label="LinkedIn PDF")
    resume_result = extract_text_from_pdf(resume_pdf_bytes, label="resume PDF")

    linkedin_text, _ = _truncate(linkedin_result.text, settings.max_extracted_chars_per_doc)
    resume_text, _ = _truncate(resume_result.text, settings.max_extracted_chars_per_doc)

    linkedin_facts = normalize_document(linkedin_text, source="linkedin")
    resume_facts = normalize_document(resume_text, source="resume")
    merged_facts = merge_facts(linkedin_facts, resume_facts)

    clean_target_role = (target_role or "").strip()[:200] or None
    clean_job_description = (job_description or "").strip()[: settings.max_job_description_chars] or None

    return CandidateProfile(
        facts=merged_facts,
        linkedin_raw_text=linkedin_text,
        resume_raw_text=resume_text,
        target_role=clean_target_role,
        job_description=clean_job_description,
    )
