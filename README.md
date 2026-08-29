# Resume Analyzer

A small Streamlit app that reads your resume and tells you how it looks for ATS-style checks, skills, and a job description.

You can upload a PDF, DOCX, or TXT. It scores the resume, lists likely skills, shows what might be missing vs a JD, and lets you download a short report. OpenAI is optional. The basic analysis works without a key.

**Live demo:** _Add your Streamlit Cloud link here after deploy_

## What it does

- Pulls text and contact details from the file
- Scores completeness, impact, and ATS-style readiness
- Picks skills from a built-in list
- Compares the resume to a pasted job description
- Optional: AI coaching, a rewritten summary, and Q&A

## Screenshots

_Add images to `docs/` and uncomment below:_

<!--
![Overview](docs/overview.png)
![Job match](docs/job-match.png)
-->

## Run it

```bash
git clone https://github.com/kajalmishra-dev/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8503
```

Mac / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8503
```

Then open http://localhost:8503

## Tests

```powershell
pip install pytest
pytest tests/ -v
```

## Deploy (Streamlit Cloud)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. New app → repo `kajalmishra-dev/ai-resume-analyzer`, main file `app.py`.
3. Deploy. Optional: add `OPENAI_API_KEY` under **Secrets** for AI features.

## How to use it

1. Upload a resume (max 8 MB).
2. Paste a job description if you want a match score.
3. Check the tabs and download the report if you need it.
4. Add an OpenAI key in the sidebar only if you want the AI bits.

## Notes

Scoring is rule-based, not a trained model. Scanned PDFs often fail. Skills that are not in the list may be missed. Don’t commit API keys — `.env` is ignored.
