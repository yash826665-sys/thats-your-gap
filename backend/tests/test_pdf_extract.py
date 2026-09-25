"""
Tests for PDF text extraction, including the scanned-PDF detection path.

We generate tiny real PDFs on the fly with reportlab-free raw PDF bytes
where possible; for the "scanned" case we simulate a PDF with a valid
structure but no extractable text layer.
"""
import io

import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from app.parser.pdf_extract import (
    PDFExtractionError,
    ScannedPDFError,
    extract_text_from_pdf,
)


def _blank_pdf_bytes(num_pages: int = 1) -> bytes:
    """A structurally valid PDF with blank pages and no text layer."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _text_pdf_bytes(lines: list[str]) -> bytes:
    """A real text-based PDF with the given lines of body text."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612, 792))
    y = 750
    for line in lines:
        c.drawString(72, y, line)
        y -= 18
        if y < 72:
            c.showPage()
            y = 750
    c.save()
    return buf.getvalue()


def test_real_text_pdf_extracts_successfully():
    lines = [f"This is line {i} of a realistic looking resume document." for i in range(40)]
    data = _text_pdf_bytes(lines)
    result = extract_text_from_pdf(data, label="resume PDF")
    assert "line 0" in result.text
    assert result.page_count >= 1


def test_empty_bytes_raises():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"", label="test doc")


def test_garbage_bytes_raises_clear_error():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"this is not a pdf at all", label="test doc")


def test_blank_pdf_detected_as_scanned():
    data = _blank_pdf_bytes(num_pages=1)
    with pytest.raises(ScannedPDFError):
        extract_text_from_pdf(data, label="LinkedIn PDF")


def test_error_messages_are_user_safe():
    try:
        extract_text_from_pdf(b"", label="resume PDF")
    except PDFExtractionError as exc:
        assert "resume PDF" in exc.user_message
        assert "Traceback" not in exc.user_message
