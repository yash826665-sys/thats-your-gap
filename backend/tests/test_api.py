import io
import copy

import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app
from tests.fixtures import (
    SYNTHETIC_LINKEDIN_TEXT,
    SYNTHETIC_LLM_RESPONSE,
    SYNTHETIC_RESUME_TEXT,
)
from tests.test_analysis_engine import FakeLLMProvider

client = TestClient(app)


def _text_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612, 792))
    y = 750
    for line in text.split("\n"):
        c.drawString(72, y, line[:100])
        y -= 16
        if y < 72:
            c.showPage()
            y = 750
    c.save()
    return buf.getvalue()


LINKEDIN_PDF_BYTES = _text_pdf_bytes(SYNTHETIC_LINKEDIN_TEXT)
RESUME_PDF_BYTES = _text_pdf_bytes(SYNTHETIC_RESUME_TEXT)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_linkedin_pdf_returns_422():
    response = client.post(
        "/api/analyze",
        files={"resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf")},
    )
    assert response.status_code == 422  # FastAPI's own required-field validation


def test_non_pdf_file_rejected():
    response = client.post(
        "/api/analyze",
        files={
            "linkedin_pdf": ("linkedin.txt", b"not a pdf", "text/plain"),
            "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
        },
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_empty_file_rejected():
    response = client.post(
        "/api/analyze",
        files={
            "linkedin_pdf": ("linkedin.pdf", b"", "application/pdf"),
            "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
        },
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_oversized_file_rejected():
    huge = b"%PDF-1.4\n" + b"0" * (11 * 1024 * 1024)
    response = client.post(
        "/api/analyze",
        files={
            "linkedin_pdf": ("linkedin.pdf", huge, "application/pdf"),
            "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
        },
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_scanned_pdf_gives_clear_error_not_500():
    from pypdf import PdfWriter

    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(buf)
    blank_pdf = buf.getvalue()

    response = client.post(
        "/api/analyze",
        files={
            "linkedin_pdf": ("linkedin.pdf", blank_pdf, "application/pdf"),
            "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
        },
    )
    assert response.status_code == 422
    assert "scanned" in response.json()["detail"].lower() or "text" in response.json()["detail"].lower()


def test_full_happy_path_with_fake_llm():
    app.state.llm_provider_override = FakeLLMProvider(response=SYNTHETIC_LLM_RESPONSE)
    try:
        response = client.post(
            "/api/analyze",
            files={
                "linkedin_pdf": ("linkedin.pdf", LINKEDIN_PDF_BYTES, "application/pdf"),
                "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
            },
            data={"target_role": "", "job_description": ""},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["career_signal"] == 74
        assert len(body["next_three_moves"]) == 3
        assert body["target_role_match"] is None
    finally:
        app.state.llm_provider_override = None


def test_target_role_present_flows_through():
    app.state.llm_provider_override = FakeLLMProvider(response=SYNTHETIC_LLM_RESPONSE)
    try:
        response = client.post(
            "/api/analyze",
            files={
                "linkedin_pdf": ("linkedin.pdf", LINKEDIN_PDF_BYTES, "application/pdf"),
                "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
            },
            data={"target_role": "Data Analyst", "job_description": "SQL and Power BI required."},
        )
        assert response.status_code == 200
    finally:
        app.state.llm_provider_override = None


def test_llm_failure_returns_502_not_stack_trace():
    app.state.llm_provider_override = FakeLLMProvider(raise_error=True)
    try:
        response = client.post(
            "/api/analyze",
            files={
                "linkedin_pdf": ("linkedin.pdf", LINKEDIN_PDF_BYTES, "application/pdf"),
                "resume_pdf": ("resume.pdf", RESUME_PDF_BYTES, "application/pdf"),
            },
        )
        assert response.status_code == 502
        assert "Traceback" not in response.text
    finally:
        app.state.llm_provider_override = None
