from src.parser import parse_resume


SAMPLE = b"""Jane Doe
jane@example.com
+1 555-123-4567
linkedin.com/in/janedoe
github.com/janedoe

Summary
Software engineer with 3 years building web apps.

Skills
Python, SQL, React, Docker

Experience
- Built REST APIs that cut latency 30%
- Led a team of 4 on a Streamlit dashboard

Education
BSc Computer Science
"""


def test_parse_contact_and_sections():
    parsed = parse_resume("resume.txt", SAMPLE)
    assert parsed.email == "jane@example.com"
    assert parsed.phone is not None
    assert "janedoe" in (parsed.linkedin or "").lower()
    assert parsed.sections.get("skills")
    assert parsed.bullet_count >= 2
    assert parsed.quantified_bullets >= 1


def test_empty_file_raises():
    try:
        parse_resume("empty.txt", b"   ")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "extractable text" in str(exc).lower()
