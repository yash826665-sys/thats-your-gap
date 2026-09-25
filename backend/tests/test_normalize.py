from app.parser.normalize import merge_facts, normalize_document
from tests.fixtures import SYNTHETIC_LINKEDIN_TEXT, SYNTHETIC_RESUME_TEXT


def test_normalize_linkedin_extracts_name_and_headline():
    facts = normalize_document(SYNTHETIC_LINKEDIN_TEXT, source="linkedin")
    assert facts.name == "Alex Rivera"
    assert "Data Analyst" in facts.headline


def test_normalize_linkedin_extracts_skills():
    facts = normalize_document(SYNTHETIC_LINKEDIN_TEXT, source="linkedin")
    assert "SQL" in facts.skills
    assert "Power BI" in facts.skills


def test_normalize_handles_missing_sections_gracefully():
    sparse_text = "Jordan Lee\nSoftware Engineer\n\nSkills\nJava, C++\n"
    facts = normalize_document(sparse_text, source="linkedin")
    # Missing sections should degrade to empty lists/strings, never raise.
    assert facts.experience == []
    assert facts.education == []
    assert facts.certifications == []
    assert "Java" in facts.skills


def test_normalize_resume_experience_has_source_tag():
    facts = normalize_document(SYNTHETIC_RESUME_TEXT, source="resume")
    assert all(e.source == "resume" for e in facts.experience)


def test_merge_facts_combines_and_dedupes_skills():
    linkedin_facts = normalize_document(SYNTHETIC_LINKEDIN_TEXT, source="linkedin")
    resume_facts = normalize_document(SYNTHETIC_RESUME_TEXT, source="resume")
    merged = merge_facts(linkedin_facts, resume_facts)

    assert merged.name == "Alex Rivera"
    # SQL appears in both sources; should not be duplicated.
    sql_count = sum(1 for s in merged.skills if s.strip().lower() == "sql")
    assert sql_count == 1
    # Experience entries from both sources should all be present.
    sources = {e.source for e in merged.experience}
    assert sources == {"linkedin", "resume"}


def test_merge_facts_never_fabricates_missing_data():
    empty_linkedin = normalize_document("", source="linkedin")
    empty_resume = normalize_document("", source="resume")
    merged = merge_facts(empty_linkedin, empty_resume)
    assert merged.name == ""
    assert merged.skills == []
    assert merged.experience == []
