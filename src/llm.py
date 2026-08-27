from __future__ import annotations

from langchain_openai import ChatOpenAI

from src.parser import ParsedResume


def _client(api_key: str) -> ChatOpenAI:
    return ChatOpenAI(api_key=api_key, temperature=0.2, model="gpt-4o-mini")


def rewrite_summary(api_key: str, parsed: ParsedResume, job_description: str = "") -> str:
    llm = _client(api_key)
    prompt = (
        "Rewrite a concise professional resume summary (80–120 words) from this resume. "
        "Use first-person implied (no 'I'). Be specific and ATS-friendly.\n\n"
        f"RESUME:\n{parsed.raw_text[:8000]}\n"
    )
    if job_description:
        prompt += f"\nTARGET JOB:\n{job_description[:4000]}\n"
    return llm.invoke(prompt).content


def coaching_notes(api_key: str, parsed: ParsedResume, job_description: str = "") -> str:
    llm = _client(api_key)
    prompt = (
        "You are a senior recruiter. Give 6 prioritized, concrete resume improvements. "
        "Use a numbered list. Do not invent employers or metrics that are not in the resume.\n\n"
        f"RESUME:\n{parsed.raw_text[:8000]}\n"
    )
    if job_description:
        prompt += f"\nJOB DESCRIPTION:\n{job_description[:4000]}\n"
    return llm.invoke(prompt).content


def answer_resume_question(api_key: str, parsed: ParsedResume, question: str) -> str:
    llm = _client(api_key)
    prompt = (
        "Answer using only the resume. If unknown, say it is not on the resume.\n\n"
        f"RESUME:\n{parsed.raw_text[:8000]}\n\nQUESTION:\n{question}"
    )
    return llm.invoke(prompt).content
