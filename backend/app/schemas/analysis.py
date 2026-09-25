"""
Schema for the That's Your Gap analysis result.

Every insight-bearing object carries an `evidence` list of short strings
pointing back to what in the source material supports it. This is the
traceability layer referenced throughout the product spec: the frontend
doesn't have to render it, but it must exist so a later version can.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class EvidencedInsight(BaseModel):
    insight: str
    evidence: list[str] = Field(default_factory=list)


class Dimensions(BaseModel):
    """
    Five 0-100 diagnostic signals. These are NOT hiring-probability,
    ATS-pass-probability, or any kind of validated psychometric score.
    They are a product diagnostic only — this is enforced in copy at
    every layer (backend labels, API response, frontend display).
    """

    positioning: int
    evidence: int
    clarity: int
    impact: int
    role_alignment: int

    @field_validator("positioning", "evidence", "clarity", "impact", "role_alignment")
    @classmethod
    def clamp_0_100(cls, v: int) -> int:
        return max(0, min(100, int(v)))


class EvidenceGap(BaseModel):
    claim: str
    gap: str
    evidence: list[str] = Field(default_factory=list)


class ConsistencyCheck(BaseModel):
    topic: str
    linkedin_version: str = ""
    resume_version: str = ""
    note: str  # always neutral, non-accusatory phrasing


class TargetRoleMatch(BaseModel):
    matched_strengths: list[EvidencedInsight] = Field(default_factory=list)
    missing_evidence: list[EvidencedInsight] = Field(default_factory=list)
    potential_gaps: list[EvidencedInsight] = Field(default_factory=list)
    recommended_changes: list[str] = Field(default_factory=list)


class NextMove(BaseModel):
    recommendation: str
    reason: str


class CareerXRayResult(BaseModel):
    career_signal: int
    dimensions: Dimensions
    strongest_signal: EvidencedInsight
    biggest_blind_spot: EvidencedInsight
    positioning_diagnosis: EvidencedInsight
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list)
    impact_analysis: EvidencedInsight
    consistency_checks: list[ConsistencyCheck] = Field(default_factory=list)
    target_role_match: TargetRoleMatch | None = None
    next_three_moves: list[NextMove] = Field(default_factory=list, max_length=3)

    @field_validator("career_signal")
    @classmethod
    def clamp_signal(cls, v: int) -> int:
        return max(0, min(100, int(v)))

    @field_validator("next_three_moves")
    @classmethod
    def exactly_three_if_present(cls, v: list[NextMove]) -> list[NextMove]:
        # Enforced softly here; the prompt asks for exactly 3. If the model
        # returns more, trim; if fewer, allow (better than fabricating one).
        return v[:3]
