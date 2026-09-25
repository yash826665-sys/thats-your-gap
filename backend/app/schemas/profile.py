"""
Structured candidate profile.

Design principle: FACTS extracted verbatim from the documents are kept
separate from INFERENCES the analysis stage draws about them. Nothing in
this module is ever fabricated — every field is either populated from
extracted text or left empty/None.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ExperienceEntry(BaseModel):
    title: str = ""
    company: str = ""
    dates: str = ""
    description: str = ""
    source: str = Field(description="'linkedin' or 'resume'")


class EducationEntry(BaseModel):
    school: str = ""
    degree: str = ""
    dates: str = ""
    source: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""
    source: str = ""


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    source: str = ""


class CandidateFacts(BaseModel):
    """Explicitly-stated information pulled from the uploaded PDFs."""

    name: str = ""
    headline: str = ""
    summary: str = ""
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class ExtractedDocument(BaseModel):
    """Raw + lightly-normalized text extracted from a single PDF."""

    source: str  # 'linkedin' | 'resume'
    raw_text: str
    char_count: int
    page_count: int
    truncated: bool = False


class CandidateProfile(BaseModel):
    """
    The full structured representation passed into analysis.

    `facts` holds only explicitly-stated data. Raw text is kept alongside
    (not merged in) so the analysis stage can cite back to source text,
    and so nothing downstream can quietly promote raw text into a "fact"
    without going through extraction.
    """

    facts: CandidateFacts
    linkedin_raw_text: str = ""
    resume_raw_text: str = ""
    target_role: str | None = None
    job_description: str | None = None
