import copy

import pytest

from app.analysis.engine import AnalysisError, run_career_xray_analysis
from app.analysis.llm_provider import LLMError, LLMProvider
from app.parser.normalize import merge_facts, normalize_document
from app.schemas.profile import CandidateProfile
from tests.fixtures import (
    SYNTHETIC_LINKEDIN_TEXT,
    SYNTHETIC_LLM_RESPONSE,
    SYNTHETIC_RESUME_TEXT,
)


class FakeLLMProvider(LLMProvider):
    """Returns a canned response instead of calling a real API."""

    def __init__(self, response: dict | None = None, raise_error: bool = False):
        self._response = response
        self._raise_error = raise_error

    async def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        if self._raise_error:
            raise LLMError("simulated provider failure")
        return copy.deepcopy(self._response)


def _synthetic_profile(target_role: str | None = None, job_description: str | None = None) -> CandidateProfile:
    linkedin_facts = normalize_document(SYNTHETIC_LINKEDIN_TEXT, source="linkedin")
    resume_facts = normalize_document(SYNTHETIC_RESUME_TEXT, source="resume")
    return CandidateProfile(
        facts=merge_facts(linkedin_facts, resume_facts),
        linkedin_raw_text=SYNTHETIC_LINKEDIN_TEXT,
        resume_raw_text=SYNTHETIC_RESUME_TEXT,
        target_role=target_role,
        job_description=job_description,
    )


@pytest.mark.asyncio
async def test_analysis_succeeds_with_valid_llm_output():
    profile = _synthetic_profile()
    llm = FakeLLMProvider(response=SYNTHETIC_LLM_RESPONSE)
    result = await run_career_xray_analysis(profile, llm=llm)
    assert result.career_signal == 74
    assert result.target_role_match is None


@pytest.mark.asyncio
async def test_analysis_raises_analysis_error_on_llm_failure():
    profile = _synthetic_profile()
    llm = FakeLLMProvider(raise_error=True)
    with pytest.raises(AnalysisError):
        await run_career_xray_analysis(profile, llm=llm)


@pytest.mark.asyncio
async def test_analysis_raises_on_malformed_llm_json():
    profile = _synthetic_profile()
    malformed = {"career_signal": 74}  # missing required fields
    llm = FakeLLMProvider(response=malformed)
    with pytest.raises(AnalysisError):
        await run_career_xray_analysis(profile, llm=llm)


@pytest.mark.asyncio
async def test_target_role_match_forced_null_when_not_requested():
    """Even if the model hallucinates a target_role_match, it's stripped
    when the user didn't provide a target role or job description."""
    profile = _synthetic_profile(target_role=None, job_description=None)
    response_with_match = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    response_with_match["target_role_match"] = {
        "matched_strengths": [],
        "missing_evidence": [],
        "potential_gaps": [],
        "recommended_changes": ["should not appear"],
    }
    llm = FakeLLMProvider(response=response_with_match)
    result = await run_career_xray_analysis(profile, llm=llm)
    assert result.target_role_match is None


@pytest.mark.asyncio
async def test_target_role_present_allows_match_section():
    profile = _synthetic_profile(target_role="Data Analyst", job_description="SQL and Power BI required.")
    response_with_match = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    response_with_match["target_role_match"] = {
        "matched_strengths": [{"insight": "Strong SQL evidence", "evidence": ["..."]}],
        "missing_evidence": [],
        "potential_gaps": [],
        "recommended_changes": ["Add a metric to the BI dashboard bullet."],
    }
    llm = FakeLLMProvider(response=response_with_match)
    result = await run_career_xray_analysis(profile, llm=llm)
    assert result.target_role_match is not None
    assert len(result.target_role_match.matched_strengths) == 1
