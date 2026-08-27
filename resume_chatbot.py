import os
import re
import pymupdf
import streamlit as st
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Smart Resume Chatbot", layout="wide")

st.sidebar.header("🔐 OpenAI API Key (optional)")
st.sidebar.caption(
    "A valid key enables AI answers. Without one, the app still extracts the PDF "
    "and scores job match with keyword overlap."
)
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password").strip()
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key


def extract_text_from_pdf(pdf_bytes):
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def words(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}", text.lower()))


def relevant_chunks(resume_text, question, k=4):
    parts = [p.strip() for p in re.split(r"\n\s*\n", resume_text) if p.strip()]
    if not parts:
        parts = [resume_text[i : i + 800] for i in range(0, len(resume_text), 700)]
    query = words(question)
    ranked = sorted(
        parts,
        key=lambda chunk: len(query & words(chunk)),
        reverse=True,
    )
    return ranked[:k] or parts[:k]


def keyword_job_match(resume_text, job_description):
    stop = {
        "and", "the", "for", "with", "that", "this", "from", "your", "you",
        "are", "will", "have", "has", "our", "job", "role", "team",
    }
    jd = words(job_description) - stop
    rs = words(resume_text) - stop
    matched = sorted(jd & rs)
    missing = sorted(jd - rs)
    percent = int(round(100 * len(matched) / len(jd))) if jd else 0
    return percent, matched, missing


def ask_with_openai(resume_text, question):
    llm = ChatOpenAI(api_key=openai_api_key, temperature=0)
    context = "\n\n".join(relevant_chunks(resume_text, question))
    prompt = (
        "You are a resume assistant. Answer using only this resume context.\n\n"
        f"{context}\n\nQuestion: {question}"
    )
    return llm.invoke(prompt).content


def score_with_openai(resume_text, job_description):
    llm = ChatOpenAI(api_key=openai_api_key, temperature=0)
    prompt = f"""
Compare the following resume and job description.

Resume:
{resume_text}

Job Description:
{job_description}

Give a match percentage (0–100%) and explain why, listing matching skills and any gaps.
Respond with:
- Match %: ...
- Matched Skills: ...
- Missing Skills: ...
- Summary: ...
"""
    return llm.invoke(prompt).content


st.title("🤖 Chat with Your Resume + Job Fit Analysis")

uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf")

if not uploaded_file:
    st.info("Upload a PDF resume to continue.")
    st.stop()

file_id = f"{uploaded_file.name}-{uploaded_file.size}"
if st.session_state.get("resume_file_id") != file_id:
    pdf_bytes = uploaded_file.getvalue()
    resume_text = extract_text_from_pdf(pdf_bytes)
    if not resume_text.strip():
        st.error("Could not read text from this PDF. Use a text-based PDF, not a scanned image.")
        st.stop()
    st.session_state.resume_file_id = file_id
    st.session_state.resume_text = resume_text

resume_text = st.session_state.resume_text
st.success("✅ Resume processed!")

tab1, tab2 = st.tabs(["💬 Chat with Resume", "📄 Job Match Dashboard"])

with tab1:
    user_question = st.text_input("Ask a question about your resume:")
    if user_question:
        if openai_api_key:
            try:
                response = ask_with_openai(resume_text, user_question)
            except Exception as exc:
                st.warning(
                    "OpenAI could not answer (invalid key or billing). Showing local excerpts instead."
                )
                st.caption(str(exc)[:300])
                response = "\n\n".join(relevant_chunks(resume_text, user_question))
        else:
            response = "\n\n".join(relevant_chunks(resume_text, user_question))
        st.markdown(f"**Answer:**\n\n{response}")

with tab2:
    st.subheader("🔎 Paste a Job Description Below")
    job_desc = st.text_area("Job Description", height=200)

    if job_desc:
        percent, matched, missing = keyword_job_match(resume_text, job_desc)
        summary = "Keyword overlap between the job description and resume."

        if openai_api_key:
            try:
                result = score_with_openai(resume_text, job_desc)
                match_pct = re.search(r"Match %:\s*(\d+)", result)
                if match_pct:
                    percent = int(match_pct.group(1))
                m = re.search(r"Matched Skills:\s*(.+)", result)
                miss = re.search(r"Missing Skills:\s*(.+)", result)
                summ = re.search(r"Summary:\s*(.+)", result)
                if m:
                    matched = [item.strip() for item in m.group(1).split(",") if item.strip()]
                if miss:
                    missing = [item.strip() for item in miss.group(1).split(",") if item.strip()]
                if summ:
                    summary = summ.group(1)
            except Exception as exc:
                st.warning("OpenAI job-match failed; showing keyword score instead.")
                st.caption(str(exc)[:300])

        st.subheader("📊 Match Score")
        st.progress(min(max(percent, 0), 100) / 100)
        st.metric("Match %", f"{percent}%")

        st.subheader("✅ Matched Skills")
        st.write(", ".join(matched[:40]) if matched else "Not found")

        st.subheader("❌ Missing Skills")
        st.write(", ".join(missing[:40]) if missing else "None")

        st.subheader("🧠 Summary")
        st.write(summary)
