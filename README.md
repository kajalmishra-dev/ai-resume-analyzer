# AI Resume Analyzer

A Streamlit application that analyzes resumes for ATS readiness, completeness, impact, skills, and job-description fit.

**Live demo:** https://ai-resume-analyzer-29.streamlit.app/

## Features

- Parse PDF, DOCX, and TXT resumes.
- Extract contact details, sections, skills, and resume signals.
- Calculate ATS-readiness, completeness, and impact scores.
- Compare a resume with a pasted job description.
- Generate a downloadable Markdown analysis report.
- Optionally use an OpenAI API key for resume coaching, summary rewriting, and resume Q&A.
- Run the core analysis locally without an API key.

## Project structure

```text
.
├── app.py                 # Streamlit entry point
├── src/
│   ├── analysis.py        # Scoring, skill extraction, and job matching
│   ├── llm.py             # Optional LLM-powered features
│   ├── parser.py          # Resume parsing and metadata extraction
│   └── skills.py          # Skill catalog and tokenization stopwords
├── tests/                 # Automated tests
├── .streamlit/            # Streamlit configuration
├── .devcontainer/         # Dev Container configuration
└── requirements*.txt      # Runtime and development dependencies
```

## Local development

### 1. Create an environment

```bash
python -m venv .venv
```

Activate it:

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows**
```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Then open `http://localhost:8501`.

### Optional AI features

The core analyzer does not require an API key. To enable coaching, summary rewriting, and Q&A, provide an OpenAI API key in the sidebar.

For local environment configuration, copy `.env.example` to `.env` if you use an environment loader in your own workflow. The application currently accepts the key through the Streamlit sidebar.

## Quality checks

Run the same checks used by CI:

```bash
ruff check .
pytest -v
```

## Supported resume formats

- PDF
- DOCX
- TXT

Uploads are limited to 8 MB.

## Notes

The scoring system is heuristic and intended to provide practical resume feedback rather than replace recruiter or hiring decisions.
