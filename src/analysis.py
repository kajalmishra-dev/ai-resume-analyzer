from __future__ import annotations

import re
from dataclasses import dataclass

from src.parser import ParsedResume
from src.skills import KNOWN_SKILLS, STOPWORDS


@dataclass
class ScoreBreakdown:
    overall: int
    ats: int
    completeness: int
    impact: int
    notes: list[str]


def tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}", text.lower()) if w not in STOPWORDS}


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in KNOWN_SKILLS if skill in lowered]
    # keep unique, longer phrases first already listed
    seen: set[str] = set()
    ordered: list[str] = []
    for skill in found:
        if skill not in seen:
            seen.add(skill)
            ordered.append(skill)
    return ordered


def score_resume(parsed: ParsedResume) -> ScoreBreakdown:
    notes: list[str] = []

    contact_pts = 0
    if parsed.email:
        contact_pts += 25
    else:
        notes.append("Add a professional email address.")
    if parsed.phone:
        contact_pts += 20
    else:
        notes.append("Add a phone number so recruiters can reach you.")
    if parsed.linkedin:
        contact_pts += 15
    else:
        notes.append("Include a LinkedIn URL.")
    if parsed.github:
        contact_pts += 10
    if parsed.sections.get("summary"):
        contact_pts += 15
    else:
        notes.append("Add a 3–4 line professional summary.")
    if parsed.sections.get("skills") or extract_skills(parsed.raw_text):
        contact_pts += 15
    else:
        notes.append("Add a dedicated skills section.")
    completeness = min(100, contact_pts)

    ats = 55
    if parsed.page_count <= 2:
        ats += 15
    else:
        notes.append("Keep the resume to 1–2 pages for most roles.")
        ats -= 10
    if 350 <= parsed.word_count <= 900:
        ats += 15
    elif parsed.word_count < 250:
        notes.append("The resume is thin. Add concrete accomplishments.")
        ats -= 10
    elif parsed.word_count > 1200:
        notes.append("The resume is long. Cut older or unrelated content.")
        ats -= 5
    if parsed.sections.get("experience"):
        ats += 10
    if parsed.sections.get("education"):
        ats += 5
    ats = max(0, min(100, ats))

    impact = 40
    if parsed.bullet_count:
        impact += min(30, parsed.bullet_count * 3)
    else:
        notes.append("Use bullet points for experience instead of dense paragraphs.")
    if parsed.quantified_bullets:
        impact += min(20, parsed.quantified_bullets * 5)
    else:
        notes.append("Quantify results (%, $, time saved, users, revenue).")
    if parsed.action_verb_bullets:
        impact += min(10, parsed.action_verb_bullets * 2)
    else:
        notes.append("Start bullets with strong action verbs (Built, Led, Shipped).")
    impact = max(0, min(100, impact))

    overall = round(0.35 * ats + 0.35 * completeness + 0.30 * impact)
    if not notes:
        notes.append("Solid structure. Tailor keywords to each job description next.")
    return ScoreBreakdown(overall=overall, ats=ats, completeness=completeness, impact=impact, notes=notes)


def match_job(parsed: ParsedResume, job_description: str) -> dict:
    resume_skills = extract_skills(parsed.raw_text)
    jd_skills = extract_skills(job_description)
    jd_tokens = tokenize(job_description)
    resume_tokens = tokenize(parsed.raw_text)

    skill_matched = sorted(set(resume_skills) & set(jd_skills))
    skill_missing = sorted(set(jd_skills) - set(resume_skills))
    token_overlap = jd_tokens & resume_tokens

    skill_score = int(100 * len(skill_matched) / len(jd_skills)) if jd_skills else 0
    keyword_score = int(100 * len(token_overlap) / len(jd_tokens)) if jd_tokens else 0
    overall = round(0.7 * skill_score + 0.3 * keyword_score) if jd_skills else keyword_score

    return {
        "overall": min(100, overall),
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": skill_matched,
        "missing_skills": skill_missing,
        "shared_keywords": sorted(token_overlap)[:40],
    }
