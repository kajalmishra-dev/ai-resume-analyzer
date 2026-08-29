# Resume Analyzer

Upload a resume, get ATS-style scores, skill gaps, and job match — no API key needed for the basics.

**[Try it live →](https://ai-resume-analyzer-29.streamlit.app/)**

## What it does

- Parses PDF, DOCX, or TXT resumes
- Scores completeness, impact, and ATS readiness
- Matches your resume against a pasted job description
- Lets you download a short analysis report
- Optional OpenAI key for coaching, rewrite, and Q&A

## Quick start

```bash
git clone https://github.com/kajalmishra-dev/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Stack

Python · Streamlit · PyMuPDF · python-docx

## License

Portfolio / learning project. Use freely.
