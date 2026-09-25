"""
Turns raw extracted PDF text into a best-effort structured representation.

This is intentionally heuristic (regex / section-header based), not a
full NLP pipeline. It is a *starting point* for the structured profile:
the LLM analysis stage sees both this structured guess AND the raw text,
so mis-segmented sections don't cause facts to be lost — they just don't
get a clean bucket. We never invent content that isn't present in the
raw text.

LinkedIn "Save to PDF" exports and resumes both vary a lot in layout, so
section detection is deliberately forgiving (case-insensitive, tolerant
of extra whitespace) and always degrades gracefully to "leave it in
raw text" rather than throwing.
"""
from __future__ import annotations

import re

from app.schemas.profile import (
    CandidateFacts,
    CertificationEntry,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
)

# Section headers we look for, in the order LinkedIn/resumes typically use them.
SECTION_ALIASES: dict[str, list[str]] = {
    "summary": ["summary", "about"],
    "experience": ["experience", "work experience", "employment history"],
    "education": ["education"],
    "skills": ["skills", "top skills", "technical skills"],
    "projects": ["projects", "personal projects"],
    "certifications": ["licenses & certifications", "licenses and certifications", "certifications"],
    "achievements": ["honors & awards", "honors and awards", "achievements", "awards"],
}

URL_RE = re.compile(r"(https?://[^\s,)]+|(?:www\.)?linkedin\.com/[^\s,)]+|github\.com/[^\s,)]+)", re.I)
LINE_SPLIT_RE = re.compile(r"\r\n|\r|\n")


def _find_sections(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Return {section_key: (start_line_idx_after_header, end_line_idx_exclusive)}."""
    header_positions: list[tuple[int, str]] = []
    for i, raw_line in enumerate(lines):
        line = raw_line.strip().lower()
        if not line:
            continue
        for key, aliases in SECTION_ALIASES.items():
            if line in aliases or any(line == a for a in aliases):
                header_positions.append((i, key))
                break

    spans: dict[str, tuple[int, int]] = {}
    for idx, (line_no, key) in enumerate(header_positions):
        start = line_no + 1
        end = header_positions[idx + 1][0] if idx + 1 < len(header_positions) else len(lines)
        # Don't overwrite an earlier occurrence of the same key (keep first).
        if key not in spans:
            spans[key] = (start, end)
    return spans


def _lines_in(lines: list[str], span: tuple[int, int] | None) -> list[str]:
    if not span:
        return []
    start, end = span
    return [l.strip() for l in lines[start:end] if l.strip()]


def _guess_headline_and_name(lines: list[str]) -> tuple[str, str]:
    """
    LinkedIn PDF exports typically start with: Name, then a headline line,
    then location. We take the first non-empty line as name and the
    second as headline, defensively.
    """
    non_empty = [l.strip() for l in lines if l.strip()]
    name = non_empty[0] if len(non_empty) > 0 else ""
    headline = non_empty[1] if len(non_empty) > 1 else ""
    return name, headline


def _split_skills(skill_lines: list[str]) -> list[str]:
    skills: list[str] = []
    for line in skill_lines:
        # Skills sections are sometimes comma-separated, sometimes one per line,
        # sometimes bullet-separated.
        parts = re.split(r",|•|\u2022|\|", line)
        for p in parts:
            p = p.strip(" -\t")
            if p and len(p) < 60:
                skills.append(p)
    # De-duplicate while preserving order.
    seen = set()
    deduped = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped


def _parse_experience_blocks(exp_lines: list[str], source: str) -> list[ExperienceEntry]:
    """
    Group experience lines into entries. Heuristic: a new entry starts at a
    line that looks like a title (short, no trailing period) followed by a
    line containing a date range pattern within the next couple of lines.
    Falls back to one big block if structure can't be detected.
    """
    date_pattern = re.compile(
        r"(\b\d{4}\b.*(-|–|to).*(\b\d{4}\b|present)|"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4})",
        re.I,
    )

    entries: list[ExperienceEntry] = []
    i = 0
    n = len(exp_lines)
    if n == 0:
        return entries

    # Find candidate boundaries: lines followed within 2 lines by a date pattern.
    boundaries = []
    for idx in range(n):
        window = " ".join(exp_lines[idx: idx + 3])
        if date_pattern.search(window):
            boundaries.append(idx)

    if not boundaries:
        # Can't detect structure reliably; store as a single block so no text is lost.
        return [
            ExperienceEntry(
                title="",
                company="",
                dates="",
                description=" ".join(exp_lines)[:2000],
                source=source,
            )
        ]

    # Use boundaries as start of each entry block.
    boundaries = sorted(set(boundaries))
    for b_idx, start in enumerate(boundaries):
        end = boundaries[b_idx + 1] if b_idx + 1 < len(boundaries) else n
        block = exp_lines[start:end]
        if not block:
            continue
        title = block[0] if len(block) > 0 else ""
        company = block[1] if len(block) > 1 else ""
        dates_match = date_pattern.search(" ".join(block[:3]))
        dates = dates_match.group(0) if dates_match else ""
        description = " ".join(block[2:]) if len(block) > 2 else ""
        entries.append(
            ExperienceEntry(
                title=title[:200],
                company=company[:200],
                dates=dates[:100],
                description=description[:2000],
                source=source,
            )
        )
    return entries


def _parse_education_blocks(edu_lines: list[str], source: str) -> list[EducationEntry]:
    entries: list[EducationEntry] = []
    # Group by blank-ish heuristic: pairs of (school, degree) lines.
    i = 0
    while i < len(edu_lines):
        school = edu_lines[i]
        degree = edu_lines[i + 1] if i + 1 < len(edu_lines) else ""
        dates = ""
        date_match = re.search(r"\b(19|20)\d{2}\b(\s*-\s*(\b(19|20)\d{2}\b|present))?", degree, re.I)
        if date_match:
            dates = date_match.group(0)
        entries.append(EducationEntry(school=school[:200], degree=degree[:200], dates=dates, source=source))
        i += 2
    return entries


def _parse_projects(lines: list[str], source: str) -> list[ProjectEntry]:
    if not lines:
        return []
    projects = []
    current_name = None
    current_desc: list[str] = []
    for line in lines:
        # A short line with no verb-like ending is likely a project title.
        if len(line) < 80 and not line.endswith((".", ",")) and current_name is None:
            current_name = line
            continue
        if current_name is not None and len(line) < 80 and line[0:1].isupper() and len(current_desc) > 0:
            projects.append(ProjectEntry(name=current_name[:200], description=" ".join(current_desc)[:1500], source=source))
            current_name = line
            current_desc = []
            continue
        current_desc.append(line)
    if current_name is not None:
        projects.append(ProjectEntry(name=current_name[:200], description=" ".join(current_desc)[:1500], source=source))
    return projects


def _parse_certifications(lines: list[str], source: str) -> list[CertificationEntry]:
    certs = []
    i = 0
    while i < len(lines):
        name = lines[i]
        issuer = lines[i + 1] if i + 1 < len(lines) else ""
        certs.append(CertificationEntry(name=name[:200], issuer=issuer[:200], date="", source=source))
        i += 2
    return certs


def normalize_document(raw_text: str, *, source: str) -> CandidateFacts:
    """
    Convert raw extracted text from one document (LinkedIn or resume) into
    a best-effort CandidateFacts. Callers merge two of these (one per
    document) — see `merge_facts`.
    """
    lines = LINE_SPLIT_RE.split(raw_text)
    spans = _find_sections(lines)

    name, headline = ("", "")
    if source == "linkedin":
        name, headline = _guess_headline_and_name(lines)

    summary_lines = _lines_in(lines, spans.get("summary"))
    experience_lines = _lines_in(lines, spans.get("experience"))
    education_lines = _lines_in(lines, spans.get("education"))
    skills_lines = _lines_in(lines, spans.get("skills"))
    projects_lines = _lines_in(lines, spans.get("projects"))
    certifications_lines = _lines_in(lines, spans.get("certifications"))
    achievements_lines = _lines_in(lines, spans.get("achievements"))

    links = list(dict.fromkeys(URL_RE.findall(raw_text)))

    return CandidateFacts(
        name=name,
        headline=headline,
        summary=" ".join(summary_lines)[:2000],
        experience=_parse_experience_blocks(experience_lines, source),
        education=_parse_education_blocks(education_lines, source),
        skills=_split_skills(skills_lines),
        projects=_parse_projects(projects_lines, source),
        certifications=_parse_certifications(certifications_lines, source),
        achievements=achievements_lines[:20],
        links=links,
    )


def merge_facts(linkedin_facts: CandidateFacts, resume_facts: CandidateFacts) -> CandidateFacts:
    """
    Combine facts from both documents. Lists are concatenated (each entry
    already tags its `source`); scalar fields prefer LinkedIn for identity
    fields (name/headline) and fall back to resume when LinkedIn's is empty.
    """
    skills = list(dict.fromkeys([*linkedin_facts.skills, *resume_facts.skills]))
    links = list(dict.fromkeys([*linkedin_facts.links, *resume_facts.links]))

    return CandidateFacts(
        name=linkedin_facts.name or resume_facts.name,
        headline=linkedin_facts.headline or resume_facts.headline,
        summary=linkedin_facts.summary or resume_facts.summary,
        experience=[*linkedin_facts.experience, *resume_facts.experience],
        education=[*linkedin_facts.education, *resume_facts.education],
        skills=skills,
        projects=[*linkedin_facts.projects, *resume_facts.projects],
        certifications=[*linkedin_facts.certifications, *resume_facts.certifications],
        achievements=[*linkedin_facts.achievements, *resume_facts.achievements],
        links=links,
    )

