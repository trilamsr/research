import itertools
import json
from pathlib import Path

import pytest

import analyze_h251_three_source_records as h251


def test_components_handles_connected_and_disconnected_graphs() -> None:
    assert h251.components(["a", "b", "c"], [("a", "b"), ("b", "c")]) == [["a", "b", "c"]]
    assert h251.components(["a", "b", "c"], [("a", "b")]) == [["a", "b"], ["c"]]


def test_components_rejects_self_edge() -> None:
    with pytest.raises(ValueError, match="invalid graph edge"):
        h251.components(["a"], [("a", "a")])


def test_support_summary_known_answer() -> None:
    assert h251.support_summary([1, 2, 10, 50]) == {
        "minimum": 1,
        "median": 6.0,
        "maximum": 50,
        "edges_with_one_session": 1,
        "edges_with_at_least_10_sessions": 2,
        "edges_with_at_least_50_sessions": 1,
    }


def test_parse_array_rejects_nonlist() -> None:
    with pytest.raises(ValueError, match="not a list"):
        h251.parse_array("1")


def test_parse_array_repairs_only_declared_trailing_apostrophe_form() -> None:
    assert h251.parse_array_with_repair("[True,False]'") == ([True, False], True)
    assert h251.parse_array_with_repair("[True,False]") == ([True, False], False)


def test_retained_inputs_are_present_and_hashed() -> None:
    paths = h251.used_source_files()
    assert len(paths) == 38
    assert all(len(h251.sha256(path)) == 64 for path in paths)
    assert all(path.is_file() for path in paths)


def test_ankile_tasks_pass_fixed_integrity_gates() -> None:
    expected_reversal_rounds = {"routing": 2, "marker": 1, "square": 2}
    for task, spec in h251.ANKILE.items():
        result = h251.analyze_ankile_task(task, spec)
        assert result["released_finite_panel"]["complete_policy_state_rectangle"]
        assert result["route_graph"]["connected"]
        assert result["route_graph"]["edges"] == 3
        assert result["execution_record"]["all_rounds_submitted"]
        assert (
            result["released_finite_panel"]["retention_sensitivity"][
                "minimum_matched_round_replacements_to_reverse_winner"
            ]
            == expected_reversal_rounds[task]
        )


def test_ankile_replacement_minima_are_exact_by_subset_enumeration() -> None:
    for task, spec in h251.ANKILE.items():
        source = json.loads((h251.SOURCES / "ankile" / task / "results.json").read_text())
        values = {
            (row["policy_id"], row["manifest_idx"]): int(row["outcome"] == "success")
            for row in source["rollouts"]
        }
        states = sorted({state for _, state in values})
        policies = sorted({policy for policy, _ in values})
        successes = {policy: sum(values[(policy, state)] for state in states) for policy in policies}
        winner, runner_up = sorted(policies, key=successes.__getitem__, reverse=True)[:2]
        target = successes[winner] - successes[runner_up] + 1
        observed = h251.minimum_round_replacements(values, states, winner, runner_up, target)
        reductions = {state: values[(winner, state)] - values[(runner_up, state)] + 1 for state in states}
        assert not any(
            sum(reductions[state] for state in subset) >= target
            for size in range(observed)
            for subset in itertools.combinations(states, size)
        )
        assert any(
            sum(reductions[state] for state in subset) >= target
            for subset in itertools.combinations(states, observed)
        )


def test_tri_release_passes_fixed_reconciliation_gates() -> None:
    result = h251.analyze_tri(h251.SOURCES / "tri" / "files")
    assert result["release_structure"]["csv_files"] == 20
    assert result["integrity"]["binary_array_length_mismatches"] == 0
    assert result["integrity"]["binary_success_count_mismatches"] == 0
    assert result["integrity"]["binary_success_rate_mismatches"] == 2
    assert result["integrity"]["progress_array_length_mismatches"] == 0
    assert result["integrity"]["progress_bin_count_mismatches"] == 0
    assert result["integrity"]["progress_mean_mismatches"] == 0
    assert result["integrity"]["aggregate_only_rate_mismatches"] == 0
    assert result["matched_bundle_join"]["public_csv_join_reconstructable"] is False
    assert result["performance_analysis_authorized"] is False
