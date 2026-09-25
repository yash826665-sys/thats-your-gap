# That's Your Gap

> "See how the internet sees your career."

That's Your Gap is a diagnostic tool for job seekers. You upload your LinkedIn
profile PDF and your resume PDF, optionally add a target role and job
description, and get back an evidence-based read on how your profile
currently comes across: your strongest signal, your biggest blind spot,
where your positioning is inconsistent, and three specific, actionable
next moves.

This is **not** a hiring-probability predictor, an ATS score, or a
generic "resume grader." Every insight is traceable to something
actually present in your uploaded documents — nothing is invented.

## Status: first MVP

This repository implements the scope described below and nothing more.
No payments, no accounts, no job scraping, no persistence of uploaded
documents. Those are intentionally out of scope for this milestone.

---

## Product principles (enforced in code, not just copy)

1. Never fabricate achievements, skills, employers, or metrics.
2. Never claim a hiring probability, ATS pass probability, or any
   measure of employability — scores are labeled as diagnostic signals.
3. Facts (explicitly stated in the documents) are always kept separate
   from inference (the model's interpretation).
4. Every major insight carries an internal evidence trail back to the
   source text (see "Traceability" below).
5. LinkedIn vs. resume discrepancies are described neutrally
   ("Potential inconsistency detected...") — never as an accusation.
6. Recommendations are specific and reasoned, never generic
   ("rewrite your two strongest bullets to include a number," not
   "improve your skills").

---

## Architecture

```
Browser (Next.js)
   │  multipart/form-data: linkedin_pdf, resume_pdf, target_role?, job_description?
   ▼
FastAPI backend  ──────────────────────────────────────────────
   │
   ├─ 1. Upload validation (type, size, non-empty)
   ├─ 2. PDF text extraction (pdfplumber, pypdf fallback)
   │      → detects scanned/image-only PDFs and fails clearly
   ├─ 3. Heuristic section parsing → CandidateFacts
   │      (name, headline, summary, experience, education, skills,
   │       projects, certifications, achievements, links)
   ├─ 4. CandidateProfile assembled (facts + raw text + role/JD)
   ├─ 5. LLM analysis call (provider-abstracted, Anthropic by default)
   │      → strict system prompt encodes all product principles
   │      → structured JSON output
   ├─ 6. Pydantic schema validation of the LLM's output
   │      → malformed output is rejected, not silently passed through
   └─ 7. Validated CareerXRayResult returned as JSON
   │
   ▼
Browser renders the results report
```

No database is used in this MVP. Uploaded PDF bytes and extracted text
live only in memory for the duration of a single request and are
discarded afterward. The architecture is structured so Postgres could be
added later (e.g. to persist analysis history) without restructuring the
analysis pipeline — see "Future roadmap."

### Traceability

Every LLM-produced insight (`strongest_signal`, `biggest_blind_spot`,
`evidence_gaps`, etc.) carries an `evidence: string[]` field pointing back
to the specific facts or text that support it. The frontend doesn't
render this raw array today, but it's preserved end-to-end in the schema
and API response so a future version can show "why did you say this?"
on click without re-architecting anything.

---

## Tech stack

**Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer
Motion, Lucide icons.

**Backend:** Python 3.11+, FastAPI, Pydantic v2.

**Document processing:** pdfplumber (primary), pypdf (fallback),
heuristic section-based text normalization.

**AI:** Anthropic API via a small provider-abstraction layer
(`app/analysis/llm_provider.py`) — swapping providers means implementing
one interface, not touching analysis logic. API keys are read from
environment variables server-side only and are never sent to the
browser.

---

## Folder structure

```
career-xray/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, the /api/analyze endpoint
│   │   ├── core/
│   │   │   └── config.py           # env-var driven settings
│   │   ├── parser/                 # PDF extraction + structuring
│   │   │   ├── pdf_extract.py
│   │   │   ├── normalize.py
│   │   │   └── build_profile.py
│   │   ├── analysis/                # LLM orchestration
│   │   │   ├── llm_provider.py
│   │   │   ├── prompts.py
│   │   │   └── engine.py
│   │   └── schemas/                 # Pydantic models (profile + analysis result)
│   │       ├── profile.py
│   │       └── analysis.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                    # landing page (/) and /analyze
│   │   ├── components/
│   │   └── lib/                    # API client + shared TS types
│   ├── package.json
│   └── .env.local.example
├── docs/
├── .gitignore
└── README.md
```

`analysis/` and `parser/` live under `backend/app/` rather than at the
repo root, so imports stay clean Python packages (`app.parser.x`,
`app.analysis.y`) while keeping the same conceptual separation the spec
asked for.

---

## Local setup (Windows, macOS, Linux)

### Prerequisites

- Python 3.11+
- Node.js 18+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Edit `backend/.env` and set `ANTHROPIC_API_KEY`.

Run the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Check it's alive: open `http://localhost:8000/api/health` — should
return `{"status": "ok"}`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
copy .env.local.example .env.local   # Windows
# cp .env.local.example .env.local   # macOS/Linux
npm run dev
```

Open `http://localhost:3000`.

### 3. Try it

Export your LinkedIn profile as a PDF (LinkedIn: Profile → "Resources" →
"Save to PDF"), have a resume PDF ready, and upload both at
`http://localhost:3000/analyze`.

---

## Environment variables

### `backend/.env`

| Variable | Purpose | Default |
|---|---|---|
| `LLM_PROVIDER` | Which provider abstraction to use | `anthropic` |
| `ANTHROPIC_API_KEY` | Server-side only, never exposed to browser | — (required) |
| `LLM_MODEL` | Model name | `claude-sonnet-4-5` |
| `LLM_MAX_OUTPUT_TOKENS` | Cap on analysis response size | `4000` |
| `LLM_TIMEOUT_SECONDS` | Per-request timeout | `60` |
| `LLM_MAX_RETRIES` | Retries on malformed JSON / transient errors | `2` |
| `MAX_UPLOAD_SIZE_MB` | Max PDF size accepted | `10` |
| `ALLOWED_UPLOAD_MIME_TYPES` | Comma-separated allowed MIME types | `application/pdf` |
| `MAX_EXTRACTED_CHARS_PER_DOC` | Truncation guard per document | `20000` |
| `MAX_JOB_DESCRIPTION_CHARS` | Truncation guard for pasted JD | `8000` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `LOG_LEVEL` | Python logging level | `INFO` |

### `frontend/.env.local`

| Variable | Purpose | Default |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | URL of the backend API | `http://localhost:8000` |

---

## Running tests

```bash
cd backend
pip install -r requirements.txt   # if not already installed
pytest -v
```

Tests cover:

- PDF upload validation (missing file, wrong type, empty file, oversized file)
- PDF extraction (valid text PDF, corrupt/garbage bytes, scanned/no-text-layer PDF)
- Heuristic text normalization (section detection, missing-section
  graceful handling, merging LinkedIn + resume facts, skill de-duplication)
- Analysis schema validation (score clamping, missing required fields,
  malformed types, trimming excess `next_three_moves`, `target_role_match`
  correctly nullable)
- Analysis engine orchestration using a fake LLM provider (no real API
  calls in tests): success path, provider failure, malformed JSON,
  `target_role_match` forced to `null` when no role/JD was supplied
- Full API integration tests against `/api/analyze` (happy path, every
  validation error, LLM failure surfaced as a clean 502, never a raw
  stack trace)

A synthetic test profile (`backend/tests/fixtures.py`) is used throughout
testing — it describes a fictional "Alex Rivera" and is not derived from
any real person's data.

---

## Known limitations

- **Heuristic section parsing.** LinkedIn PDF exports and resumes vary a
  lot in layout. The structured `CandidateFacts` extraction is a
  best-effort regex/heading-based pass, not a full NLP pipeline. When it
  mis-segments something, the raw text of both documents is still passed
  to the LLM in full, so information isn't lost — it just may not land
  in a clean bucket for future structured features.
- **No persistence.** Refreshing the results page loses your analysis;
  there's no history, no accounts, no saved reports yet.
- **English-language documents.** Section-header detection and the
  analysis prompt currently assume English.
- **No PDF/A or password-protected PDF support.** Encrypted PDFs will
  fail extraction with a generic error rather than a specific "this PDF
  is password-protected" message.
- **Single LLM call per analysis**, with retries only on malformed JSON
  or transient errors — there's no fallback to a second provider yet.
- **The 0-100 diagnostic scores are not validated against any labeled
  dataset.** They're a structured way for the model to summarize its own
  qualitative read, not a psychometrically validated instrument. This is
  stated in the UI and should stay stated in any future UI.

---

## Future roadmap (not built yet)

- Accounts + saved analysis history (would introduce Postgres)
- Payments / subscriptions for repeat analyses
- "Why did you say this?" evidence drill-down in the UI (schema already
  supports it)
- GitHub / portfolio integration as a third evidence source
- Multi-language support
- Structured diffing view for LinkedIn vs. resume inconsistencies
- A second LLM provider as an automatic fallback on outage
