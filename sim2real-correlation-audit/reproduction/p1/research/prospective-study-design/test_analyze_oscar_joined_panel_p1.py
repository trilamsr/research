import json
from pathlib import Path

from analyze_oscar_joined_panel import analyze


FAMILY = Path(__file__).resolve().parent
PROJECT = FAMILY.parents[1]


def test_p1_joined_panel_decision_and_scope() -> None:
    result = analyze(
        FAMILY / "result-oscar-roboarena-join.json",
        PROJECT / "research/corpus-reporting-audit/sources/source-oscar.csv",
    )
    assert result["inputs"]["joined_real_denominator_per_policy"] == 63
    assert result["inputs"]["printed_wm_inferred_denominator_per_policy"] == 65
    assert result["decision"]["joined_release_real_winners"] == ["pi0-FAST"]
    assert result["decision"]["printed_real_winners"] == ["pi0-FAST"]
    assert result["decision"]["printed_wm_winners"] == ["PG-FAST+"]
    assert "not an exact matched-session" in result["scope"]


def test_p1_retained_join_is_complete_and_privacy_preserving() -> None:
    result = json.loads(
        (FAMILY / "result-oscar-roboarena-join.json").read_text()
    )
    assert result["release_structure"]["unique_sessions"] == 63
    assert result["release_structure"]["unique_session_policy_pairs"] == 441
    assert result["join_coverage"]["policy_records_with_valid_binary_success"] == 441
    assert result["source"]["oscar_resolved_revision"] == (
        "db5edfaef285c15d0a41d5115177a983c08b4f5f"
    )
    assert result["source"]["roboarena_resolved_revision"] == (
        "036d031087b892bd15d99d1d6406eedba4c902f7"
    )
    assert not any(result["privacy"].values())
