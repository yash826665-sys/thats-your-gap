"""
That's Your Gap backend.

Single endpoint MVP: POST /api/analyze
Accepts two PDF uploads (LinkedIn export + resume) plus optional target
role / job description, and returns a validated CareerXRayResult JSON.

No documents are persisted. Uploaded bytes and extracted text live only
in memory for the duration of the request.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.analysis.engine import AnalysisError, run_career_xray_analysis
from app.analysis.llm_provider import get_llm_provider
from app.core.config import get_settings
from app.parser.build_profile import build_candidate_profile
from app.parser.pdf_extract import PDFExtractionError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("career_xray")

# Reminder for future contributors: never log raw document text or job
# descriptions (fields: raw_text, linkedin_raw_text, resume_raw_text,
# job_description). Log filenames, sizes, and outcome status only.

settings = get_settings()

app = FastAPI(title="That's Your Gap API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test-only hook: allows tests to inject a fake LLM provider without a real
# network call. Left as None in production, where get_llm_provider() is used.
app.state.llm_provider_override = None


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _validate_upload(file: UploadFile | None, *, label: str) -> None:
    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail=f"Please upload your {label}.")
    if file.content_type not in settings.allowed_upload_mime_types.split(","):
        raise HTTPException(
            status_code=400,
            detail=f"Your {label} must be a PDF file (got {file.content_type or 'unknown type'}).",
        )


async def _read_and_check_size(file: UploadFile, *, label: str) -> bytes:
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail=f"Your {label} appears to be empty.")
    if len(data) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Your {label} is too large "
                f"(max {settings.max_upload_size_mb}MB). Please upload a smaller file."
            ),
        )
    return data


@app.post("/api/analyze")
async def analyze(
    linkedin_pdf: UploadFile = File(...),
    resume_pdf: UploadFile = File(...),
    target_role: str | None = Form(default=None),
    job_description: str | None = Form(default=None),
) -> JSONResponse:
    _validate_upload(linkedin_pdf, label="LinkedIn PDF")
    _validate_upload(resume_pdf, label="resume PDF")

    linkedin_bytes = await _read_and_check_size(linkedin_pdf, label="LinkedIn PDF")
    resume_bytes = await _read_and_check_size(resume_pdf, label="resume PDF")

    try:
        profile = build_candidate_profile(
            linkedin_pdf_bytes=linkedin_bytes,
            resume_pdf_bytes=resume_bytes,
            target_role=target_role,
            job_description=job_description,
            settings=settings,
        )
    except PDFExtractionError as exc:
        logger.warning("PDF extraction failed: %s", exc.detail)
        raise HTTPException(status_code=422, detail=exc.user_message) from exc

    llm = app.state.llm_provider_override or get_llm_provider(settings)

    try:
        result = await run_career_xray_analysis(profile, llm=llm)
    except AnalysisError as exc:
        logger.error("Analysis failed: %s", exc.detail)
        raise HTTPException(status_code=502, detail=exc.user_message) from exc

    logger.info("Analysis completed successfully (career_signal=%s)", result.career_signal)
    return JSONResponse(content=result.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
    # Never leak stack traces or internal details to the client.
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )
