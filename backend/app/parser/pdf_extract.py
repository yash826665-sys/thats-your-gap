"""
Robust PDF text extraction.

Handles normal text PDFs via pdfplumber (falls back to pypdf if
pdfplumber fails to open the file), and detects likely scanned/image-only
PDFs so we can show the user a clear message instead of silently
returning an empty profile.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import pdfplumber
from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Raised for any unrecoverable PDF problem. `user_message` is safe to show as-is."""

    def __init__(self, user_message: str, detail: str = ""):
        self.user_message = user_message
        self.detail = detail or user_message
        super().__init__(self.detail)


class ScannedPDFError(PDFExtractionError):
    pass


@dataclass
class ExtractionResult:
    text: str
    page_count: int


# A page is considered "likely scanned" if it has very little extractable
# text relative to typical page density. This is a heuristic, not a proof.
MIN_CHARS_PER_PAGE_TEXT_LAYER = 20


def _extract_with_pdfplumber(data: bytes) -> ExtractionResult:
    pages_text: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
    return ExtractionResult(text="\n\n".join(pages_text), page_count=page_count)


def _extract_with_pypdf(data: bytes) -> ExtractionResult:
    reader = PdfReader(io.BytesIO(data))
    pages_text = [(page.extract_text() or "") for page in reader.pages]
    return ExtractionResult(text="\n\n".join(pages_text), page_count=len(reader.pages))


def extract_text_from_pdf(data: bytes, *, label: str = "document") -> ExtractionResult:
    """
    Extract text from PDF bytes. Raises PDFExtractionError subclasses with
    user-safe messages on failure. Never raises a raw parser exception.
    """
    if not data:
        raise PDFExtractionError(f"Your {label} appears to be empty. Please upload a valid PDF.")

    try:
        result = _extract_with_pdfplumber(data)
    except Exception:
        try:
            result = _extract_with_pypdf(data)
        except Exception as exc:
            raise PDFExtractionError(
                f"We couldn't open your {label}. Please make sure it's a valid, uncorrupted PDF.",
                detail=str(exc),
            ) from exc

    if result.page_count == 0:
        raise PDFExtractionError(f"Your {label} has no pages we could read.")

    stripped = result.text.strip()

    if not stripped:
        raise ScannedPDFError(
            f"We couldn't find any selectable text in your {label}. "
            "This usually means it's a scanned image rather than a text PDF. "
            "Please export a text-based PDF (for LinkedIn: Profile → Resources → Save to PDF)."
        )

    avg_chars_per_page = len(stripped) / max(result.page_count, 1)
    if avg_chars_per_page < MIN_CHARS_PER_PAGE_TEXT_LAYER:
        raise ScannedPDFError(
            f"Your {label} doesn't seem to contain much readable text — it may be a scanned "
            "image rather than a text-based PDF. Please upload a text-based PDF export instead."
        )

    return ExtractionResult(text=stripped, page_count=result.page_count)
