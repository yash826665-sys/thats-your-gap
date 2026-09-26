# That's Your Gap

> **See how the internet sees your career.**

That's Your Gap is an AI-powered career profile diagnostic tool built for job seekers.

Upload your LinkedIn profile PDF and resume PDF, optionally provide a target role and job description, and get an evidence-based analysis of how your professional profile currently comes across.

The product focuses on identifying your strongest signals, blind spots, evidence gaps, positioning issues, and actionable next steps.

---

## ✨ What It Does

That's Your Gap analyzes your LinkedIn profile and resume to generate:

- Career Signal
- Positioning Score
- Evidence Score
- Clarity Score
- Impact Score
- Role Alignment Score
- Strongest Career Signal
- Biggest Blind Spot
- Positioning Diagnosis
- Evidence Gaps
- Impact Analysis
- LinkedIn vs Resume Consistency Checks
- Target Role Match
- Three Actionable Next Moves

The analysis is designed to work from evidence present in the candidate's documents rather than inventing achievements or information.

---

## 🎯 Product Principles

That's Your Gap follows these core principles:

1. **Never fabricate information**
   - No invented achievements
   - No invented employers
   - No invented skills
   - No invented metrics
   - No invented experience

2. **No hiring predictions**
   - The product does not predict hiring probability.
   - It does not predict ATS pass probability.
   - Diagnostic scores are not employment predictions.

3. **Evidence-based analysis**
   - Insights should be supported by information found in the candidate's profile.

4. **Neutral discrepancy detection**
   - Differences between LinkedIn and resume are described neutrally.

5. **Actionable recommendations**
   - Recommendations focus on specific improvements rather than generic career advice.

---

## 🧠 How It Works

```text
User
 │
 │ LinkedIn PDF + Resume PDF
 │ Optional Target Role + Job Description
 ▼
Next.js Frontend
 │
 │ HTTP
 ▼
FastAPI Backend
 │
 ├── Upload validation
 ├── PDF text extraction
 │     ├── pdfplumber
 │     └── pypdf fallback
 ├── Candidate profile parsing
 │     └── CandidateFacts
 ├── Local AI analysis
 │     └── Ollama + Qwen 3.5 2B
 ├── Structured JSON validation
 │     └── Pydantic
 ▼
That's Your Gap Result
 │
 ▼
Results Dashboard
```

---

## 🛠️ Tech Stack

### Frontend

- Next.js 14
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide Icons

### Backend

- Python 3.13
- FastAPI
- Pydantic v2
- Uvicorn

### Document Processing

- pdfplumber
- pypdf
- Heuristic text normalization

### AI

- Ollama
- Qwen 3.5 2B
- Local AI inference

---

## 📁 Project Structure

```text
thats-your-gap/
│
├── backend/
│   ├── app/
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── llm_provider.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   │
│   │   ├── parser/
│   │   │   ├── __init__.py
│   │   │   ├── build_profile.py
│   │   │   ├── normalize.py
│   │   │   └── pdf_extract.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   └── profile.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── analyze/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   │
│   │   ├── components/
│   │   └── lib/
│   │       ├── api.ts
│   │       └── types.ts
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── .env.local.example
│
├── docs/
├── .gitignore
└── README.md
```

> Local `.env` and `.env.local` files are intentionally excluded from the repository.

---

# 🚀 Local Setup

## Prerequisites

Make sure you have:

- Python 3.13
- Node.js 18+
- Git
- Ollama

---

## 1. Install Ollama

Install Ollama on your machine.

Verify the installation:

```powershell
ollama --version
```

If Windows does not recognize the command, you can run Ollama directly from its installation path:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

---

## 2. Download Qwen 3.5 2B

That's Your Gap currently uses:

```text
qwen3.5:2b
```

Download the model:

```powershell
ollama pull qwen3.5:2b
```

Verify:

```powershell
ollama list
```

Ollama normally exposes its local API at:

```text
http://localhost:11434
```

---

## 3. Backend Setup

Navigate to the backend:

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
py -3.13 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

## 4. Backend Environment Variables

Create:

```text
backend/.env
```

Use the following configuration:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen3.5:2b

LLM_MAX_OUTPUT_TOKENS=4000
LLM_TIMEOUT_SECONDS=600
LLM_MAX_RETRIES=2

MAX_UPLOAD_SIZE_MB=10
ALLOWED_UPLOAD_MIME_TYPES=application/pdf

MAX_EXTRACTED_CHARS_PER_DOC=20000
MAX_JOB_DESCRIPTION_CHARS=8000

ENVIRONMENT=development
CORS_ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

**Do not commit `backend/.env` to GitHub.**

---

## 5. Start the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The API will run at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/health
```

---

## 6. Frontend Setup

Open a second terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Create:

```text
frontend/.env.local
```

Add:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 7. Start the Frontend

Run:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# 📄 Using the Application

1. Open the application.
2. Upload your LinkedIn profile PDF.
3. Upload your resume PDF.
4. Optionally enter a target role.
5. Optionally paste a job description.
6. Start the analysis.
7. Review the generated career diagnostic.

---

# 🤖 AI Architecture

The current application uses a local AI provider through Ollama.

```text
FastAPI
   │
   ▼
LLM Provider
   │
   ▼
Ollama
   │
   ▼
Qwen 3.5 2B
```

The backend sends structured candidate information to the model and expects structured JSON in return.

The returned JSON is validated using Pydantic before it reaches the frontend.

Malformed AI responses are rejected instead of being silently passed through.

---

# 🔐 Privacy

The current MVP does not use a database.

Uploaded documents are processed during the analysis request and are not stored as persistent user records.

The current AI inference runs locally through Ollama during local development.

No Anthropic API key is required for the current implementation.

---

# 📊 Diagnostic Scores

That's Your Gap generates six diagnostic signals:

| Signal | Description |
|---|---|
| Career Signal | Overall diagnostic signal from the candidate profile |
| Positioning | How clearly the profile communicates a professional direction |
| Evidence | Strength and availability of supporting evidence |
| Clarity | How clearly the candidate's profile communicates its information |
| Impact | How well outcomes and measurable contributions are demonstrated |
| Role Alignment | Alignment between the profile and the selected target role |

Scores range from:

```text
0 – 100
```

These scores are **diagnostic signals only**.

They are not:

- Hiring probabilities
- ATS pass probabilities
- Employment probabilities
- Psychometric scores
- Guarantees of job outcomes

---

# 🧪 Testing

Run the backend tests:

```powershell
cd backend
pytest -v
```

The test suite covers:

- PDF upload validation
- PDF extraction
- Text normalization
- Candidate profile construction
- Analysis schema validation
- Analysis engine orchestration
- API validation
- LLM failure handling

The tests use synthetic candidate data and do not require a real AI API call.

---

# ⚠️ Known Limitations

### PDF Parsing

LinkedIn and resume PDFs can have different layouts.

The current parser uses heuristic section detection and works best with text-based PDFs.

Scanned or image-only PDFs may not produce usable text.

### Local AI Model

The current model is:

```text
Qwen 3.5 2B
```

It is intentionally lightweight and designed to run on consumer hardware.

Response quality and generation speed may differ from larger cloud-based models.

### Diagnostic Scores

The 0–100 diagnostic scores are not validated against a labeled dataset.

They should be treated as structured product diagnostics rather than scientific or psychometric measurements.

### No Persistent History

The current MVP does not store analysis history.

Refreshing or leaving the page can result in losing the current analysis.

### English Language

The current parsing and analysis pipeline is primarily designed for English-language resumes and LinkedIn exports.

---

# 🗺️ Roadmap

Future versions may include:

- User accounts
- Saved analysis history
- PostgreSQL database
- Payment and subscription system
- GitHub profile integration
- Portfolio analysis
- LinkedIn vs Resume visual comparison
- Evidence drill-down
- Multi-language support
- Larger AI model support
- Cloud AI provider fallback
- Improved job-description matching
- Personalized career action plans
- Job-market integrations

---

# 📌 Current MVP Status

**Status:** MVP

### Currently implemented

- [x] Landing page
- [x] LinkedIn PDF upload
- [x] Resume PDF upload
- [x] PDF extraction
- [x] Candidate profile parsing
- [x] Local AI analysis
- [x] Ollama integration
- [x] Qwen 3.5 2B integration
- [x] Structured JSON output
- [x] Pydantic validation
- [x] Career diagnostic scores
- [x] Evidence-based insights
- [x] Target role analysis
- [x] Job description analysis
- [x] Consistency checks
- [x] Actionable recommendations
- [x] Responsive frontend

---

# 👨‍💻 Project

**That's Your Gap**

An AI-powered career profile diagnostic tool designed to help candidates understand what their professional profile communicates — and identify what may be missing.

---

## Built With

**Next.js · TypeScript · Tailwind CSS · Framer Motion · FastAPI · Python · Pydantic · pdfplumber · pypdf · Ollama · Qwen**
