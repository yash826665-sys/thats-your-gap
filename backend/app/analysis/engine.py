"""
Orchestrates a single analysis run: build prompt -> call LLM -> validate
against the strict CareerXRayResult schema -> return, or raise a clear
AnalysisError the API layer can turn into a safe HTTP response.
"""
from __future__ import annotations

import logging

from pydantic import ValidationError

from app.analysis.llm_provider import LLMError, LLMProvider
from app.analysis.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.analysis import CareerXRayResult
from app.schemas.profile import CandidateProfile

logger = logging.getLogger("career_xray.engine")


class AnalysisError(Exception):
    """User-safe message plus internal detail for logs."""

    def __init__(self, user_message: str, detail: str = ""):
        self.user_message = user_message
        self.detail = detail or user_message
        super().__init__(self.detail)


async def run_career_xray_analysis(
    profile: CandidateProfile, *, llm: LLMProvider
) -> CareerXRayResult:
    user_prompt = build_user_prompt(profile)

    try:
        raw_output = await llm.generate_json(
            system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt
        )
    except LLMError as exc:
        logger.error("LLM call failed: %s", exc)
        raise AnalysisError(
            "We couldn't complete your analysis right now. Please try again in a moment.",
            detail=str(exc),
        ) from exc

    # If no target role/JD was supplied, force target_role_match to null even if
    # the model produced something anyway — this section is opt-in by design.
    if not profile.target_role and not profile.job_description:
        raw_output["target_role_match"] = None

    try:
        result = CareerXRayResult.model_validate(raw_output)
    except ValidationError as exc:
        logger.error("LLM output failed schema validation: %s", exc)
        raise AnalysisError(
            "We had trouble structuring your That's Your Gap. Please try again.",
            detail=str(exc),
        ) from exc

    return result
