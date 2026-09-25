import copy

import pytest
from pydantic import ValidationError

from app.schemas.analysis import CareerXRayResult
from tests.fixtures import SYNTHETIC_LLM_RESPONSE


def test_valid_response_parses_successfully():
    result = CareerXRayResult.model_validate(SYNTHETIC_LLM_RESPONSE)
    assert result.career_signal == 74
    assert result.dimensions.positioning == 78
    assert len(result.next_three_moves) == 3


def test_dimension_scores_are_clamped_to_0_100():
    bad = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    bad["dimensions"]["impact"] = 140
    bad["career_signal"] = -5
    result = CareerXRayResult.model_validate(bad)
    assert result.dimensions.impact == 100
    assert result.career_signal == 0


def test_missing_required_field_raises_validation_error():
    bad = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    del bad["strongest_signal"]
    with pytest.raises(ValidationError):
        CareerXRayResult.model_validate(bad)


def test_more_than_three_moves_gets_trimmed():
    bad = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    bad["next_three_moves"] = bad["next_three_moves"] * 3  # 9 items
    result = CareerXRayResult.model_validate(bad)
    assert len(result.next_three_moves) == 3


def test_target_role_match_can_be_null():
    ok = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    ok["target_role_match"] = None
    result = CareerXRayResult.model_validate(ok)
    assert result.target_role_match is None


def test_malformed_type_raises_validation_error():
    bad = copy.deepcopy(SYNTHETIC_LLM_RESPONSE)
    bad["career_signal"] = "not a number"
    with pytest.raises(ValidationError):
        CareerXRayResult.model_validate(bad)
