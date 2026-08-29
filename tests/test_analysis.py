from src.analysis import extract_skills, match_job, score_resume
from src.parser import parse_resume

SAMPLE = b"""Alex Dev
alex@test.com

Skills
Python, JavaScript, AWS

Experience
- Developed microservices serving 10k users

Education
BSc
"""

JOB = """
We need Python, React, and AWS experience. SQL is a plus.
"""


def test_extract_skills():
    parsed = parse_resume("r.txt", SAMPLE)
    skills = extract_skills(parsed.raw_text)
    assert "python" in skills
    assert "aws" in skills


def test_score_resume_in_range():
    parsed = parse_resume("r.txt", SAMPLE)
    scores = score_resume(parsed)
    assert 0 <= scores.overall <= 100
    assert scores.completeness > 0
    assert isinstance(scores.notes, list)


def test_job_match():
    parsed = parse_resume("r.txt", SAMPLE)
    result = match_job(parsed, JOB)
    assert "python" in result["matched_skills"]
    assert result["overall"] >= 0
    assert "react" in result["missing_skills"]
