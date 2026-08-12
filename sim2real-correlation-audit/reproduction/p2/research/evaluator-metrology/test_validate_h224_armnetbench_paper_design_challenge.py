from __future__ import annotations

import copy
import json

import pytest

import validate_h224_armnetbench_paper_design_challenge as validator


def saved() -> dict:
    return json.loads(validator.CHALLENGE.read_text(encoding="utf-8"))


def test_saved_challenge_validates() -> None:
    validator.validate(saved())


def test_positive_reclassification_is_rejected() -> None:
    altered = copy.deepcopy(saved())
    altered["independent_decisions"]["p2_classification"] = (
        "positive_design_contrast"
    )
    with pytest.raises(ValueError, match="decision mismatch"):
        validator.validate(altered)


def test_outcome_use_is_rejected() -> None:
    altered = copy.deepcopy(saved())
    altered["outcome_boundary"]["performance_values_used_in_classification"] = True
    with pytest.raises(ValueError, match="outcome boundary"):
        validator.validate(altered)
