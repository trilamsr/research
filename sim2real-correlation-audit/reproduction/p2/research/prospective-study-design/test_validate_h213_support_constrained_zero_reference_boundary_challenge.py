import copy
import json

import pytest

import validate_h213_support_constrained_zero_reference_boundary_challenge as validator


def retained() -> dict:
    return json.loads(validator.CHALLENGE.read_text())


def test_retained_challenge_validates() -> None:
    validator.validate(retained())


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("classification", "support_constraint_changes_optimizer_face_only"),
        ("imports_or_executes_producer", True),
        ("protocol_sha256", "0" * 64),
        ("producer_result_sha256", "0" * 64),
    ),
)
def test_top_level_tampering_fails(field: str, value: object) -> None:
    data = retained()
    data[field] = value
    with pytest.raises(ValueError):
        validator.validate(data)


def test_missing_attack_fails() -> None:
    data = retained()
    data["attacks"] = data["attacks"][:-1]
    with pytest.raises(ValueError):
        validator.validate(data)


def test_census_tampering_fails() -> None:
    data = copy.deepcopy(retained())
    data["exact_case_census"]["support_grid_lotteries_k_le_5_denominator_8"] -= 1
    with pytest.raises(ValueError):
        validator.validate(data)


def test_disagreement_fails() -> None:
    data = copy.deepcopy(retained())
    data["producer_agreement"]["classification"] = False
    with pytest.raises(ValueError):
        validator.validate(data)
