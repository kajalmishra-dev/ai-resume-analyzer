from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src.analysis import extract_skills, match_job, score_resume
from src.llm import answer_resume_question, coaching_notes, rewrite_summary
from src.parser import parse_resume

MAX_BYTES = 8 * 1024 * 1024
ALLOWED = {".pdf", ".docx", ".txt"}

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.4rem; max-width: 1200px; }
      [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 12px 16px;
      }
      .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0ea5e9 160%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
      }
      .hero h1 { margin: 0 0 6px 0; font-size: 1.7rem; }
      .hero p { margin: 0; color: #cbd5e1; }
    </style>
    """,
    unsafe_allow_html=True,
)


def build_report(parsed, scores, job_match=None) -> str:
    lines = [
        f"# Resume analysis — {parsed.filename}",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- Overall: {scores.overall}/100",
        f"- ATS readiness: {scores.ats}/100",
        f"- Completeness: {scores.completeness}/100",
        f"- Impact: {scores.impact}/100",
        "",
        "## Contact",
        f"- Email: {parsed.email or 'missing'}",
        f"- Phone: {parsed.phone or 'missing'}",
        f"- LinkedIn: {parsed.linkedin or 'missing'}",
        f"- GitHub: {parsed.github or 'missing'}",
        "",
        "## Detected skills",
        ", ".join(extract_skills(parsed.raw_text)) or "none",
        "",
        "## Recommendations",
        *[f"- {n}" for n in scores.notes],
    ]
    if job_match:
        lines += [
            "",
            "## Job match",
            f"- Overall: {job_match['overall']}%",
            f"- Matched: {', '.join(job_match['matched_skills']) or 'none'}",
            f"- Missing: {', '.join(job_match['missing_skills']) or 'none'}",
        ]
    return "\n".join(lines) + "\n"


with st.sidebar:
    st.header("Workspace")
    uploaded = st.file_uploader(
        "Resume file",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX, or TXT. Max 8 MB.",
    )
    api_key = st.text_input("OpenAI API key", type="password").strip()
    st.caption("Optional. Enables AI rewrite, coaching, and Q&A.")
    job_desc = st.text_area("Target job description", height=180, placeholder="Paste a JD to tailor analysis…")

st.markdown(
    """
    <div class="hero">
      <h1>Production Resume Analyzer</h1>
      <p>ATS scoring, skill extraction, job-fit, and recruiter-style coaching — from one upload.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not uploaded:
    c1, c2, c3 = st.columns(3)
    c1.info("1. Upload a resume in the sidebar")
    c2.info("2. Optionally paste a job description")
    c3.info("3. Review scores, gaps, and a downloadable report")
    st.stop()

suffix = "." + uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
if suffix not in ALLOWED:
    st.error("Unsupported file type.")
    st.stop()
data = uploaded.getvalue()
if len(data) > MAX_BYTES:
    st.error("File is larger than 8 MB.")
    st.stop()

file_id = f"{uploaded.name}-{len(data)}"
if st.session_state.get("file_id") != file_id:
    try:
        parsed = parse_resume(uploaded.name, data)
    except Exception as exc:
        st.error(str(exc))
        st.stop()
    st.session_state.file_id = file_id
    st.session_state.parsed = parsed

parsed = st.session_state.parsed
scores = score_resume(parsed)
job_match = match_job(parsed, job_desc) if job_desc.strip() else None

m1, m2, m3, m4 = st.columns(4)
m1.metric("Overall", f"{scores.overall}")
m2.metric("ATS ready", f"{scores.ats}")
m3.metric("Completeness", f"{scores.completeness}")
m4.metric("Impact", f"{scores.impact}")
if job_match:
    st.metric("Job match", f"{job_match['overall']}%")

overview, skills, match_tab, coach, qa, raw = st.tabs(
    ["Overview", "Skills", "Job match", "Coaching", "Q&A", "Raw text"]
)

with overview:
    left, right = st.columns((1.2, 1))
    with left:
        st.subheader("Profile signals")
        st.write(
            {
                "Email": parsed.email or "—",
                "Phone": parsed.phone or "—",
                "LinkedIn": parsed.linkedin or "—",
                "GitHub": parsed.github or "—",
                "Pages": parsed.page_count,
                "Words": parsed.word_count,
                "Bullets": parsed.bullet_count,
                "Quantified bullets": parsed.quantified_bullets,
            }
        )
    with right:
        st.subheader("Priority fixes")
        for note in scores.notes:
            st.write(f"• {note}")
        report = build_report(parsed, scores, job_match)
        st.download_button(
            "Download analysis report",
            data=report.encode("utf-8"),
            file_name="resume-analysis.md",
            mime="text/markdown",
        )

with skills:
    found = extract_skills(parsed.raw_text)
    st.subheader("Detected skills")
    if found:
        st.write(", ".join(s.title() if len(s) > 3 else s.upper() for s in found))
    else:
        st.warning("No catalog skills detected. Add a clear Skills section.")
    if parsed.sections.get("skills"):
        st.subheader("Skills section")
        st.write(parsed.sections["skills"])

with match_tab:
    if not job_desc.strip():
        st.info("Paste a job description in the sidebar to compute fit.")
    else:
        st.progress(job_match["overall"] / 100)
        a, b, c = st.columns(3)
        a.metric("Skill match", f"{job_match['skill_score']}%")
        b.metric("Keyword overlap", f"{job_match['keyword_score']}%")
        c.metric("JD skills found", len(job_match["jd_skills"]))
        st.subheader("Matched")
        st.success(", ".join(job_match["matched_skills"]) or "None yet")
        st.subheader("Missing on resume")
        st.error(", ".join(job_match["missing_skills"]) or "None")
        st.caption("Add missing skills only if you actually have them.")

with coach:
    st.subheader("Rule-based recommendations")
    for note in scores.notes:
        st.write(f"• {note}")
    if api_key:
        if st.button("Generate AI coaching"):
            try:
                st.session_state.coach = coaching_notes(api_key, parsed, job_desc)
            except Exception as exc:
                st.error(f"AI coaching failed: {exc}")
        if st.button("Rewrite summary"):
            try:
                st.session_state.summary = rewrite_summary(api_key, parsed, job_desc)
            except Exception as exc:
                st.error(f"Rewrite failed: {exc}")
        if st.session_state.get("coach"):
            st.markdown(st.session_state.coach)
        if st.session_state.get("summary"):
            st.subheader("Suggested summary")
            st.write(st.session_state.summary)
    else:
        st.caption("Add an OpenAI key for recruiter-style coaching and a rewritten summary.")

with qa:
    question = st.text_input("Ask about this resume")
    if question:
        if api_key:
            try:
                st.write(answer_resume_question(api_key, parsed, question))
            except Exception as exc:
                st.warning("AI Q&A failed. Showing matching resume excerpts.")
                st.caption(str(exc)[:240])
                st.write(parsed.raw_text[:2000])
        else:
            st.write(parsed.raw_text[:2500])

with raw:
    st.text_area("Extracted text", parsed.raw_text, height=360)
