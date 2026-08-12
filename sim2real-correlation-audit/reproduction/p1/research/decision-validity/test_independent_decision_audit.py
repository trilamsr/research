import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "independent_decision_audit", HERE / "independent_decision_audit.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_independent_program_uses_no_project_analysis_or_scientific_stack():
    text = (HERE / "independent_decision_audit.py").read_text(encoding="utf-8")
    assert "import numpy" not in text
    assert "import scipy" not in text
    assert "synthesize_paper_evidence" not in text
    assert "audit_reversal_evidence" not in text
    assert "analyze_decision_confidence" not in text


def test_independent_results_match_paper_fact_lock():
    independent = MODULE.build_results()
    fact_lock = json.loads(
        (
            HERE.parent
            / "claim-evidence-synthesis"
            / "result-paper-evidence.json"
        ).read_text(encoding="utf-8")
    )
    expected = {row["case"]: row for row in fact_lock["decision_atlas"]["cases"]}
    assert set(independent["cases"]) == set(expected)

    for name, observed in independent["cases"].items():
        target = expected[name]
        assert abs(observed["pearson_r"] - target["pearson_r"]) < 1e-10
        assert observed["real_winners"] == target["real_winners"]
        assert observed["sim_winners"] == target["sim_winners"]
        assert observed["robustly_correct"] == target["robustly_correct"]
        assert (
            abs(
                observed["displayed_real_regret_pp"]
                - target["displayed_real_regret_pp"]
            )
            < 1e-10
        )
        if "subset_stability" in observed:
            subset = observed["subset_stability"]
            assert subset["leave_one_block_out_correct"] == (
                target["leave_one_task_out"]["correct"]
            )
            assert subset["leave_one_block_out_total"] == (
                target["leave_one_task_out"]["total"]
            )
            assert subset["all_nonempty_subsets_correct"] == (
                target["all_task_subsets"]["correct"]
            )
            assert subset["all_nonempty_subsets_total"] == (
                target["all_task_subsets"]["total"]
            )


def test_simulator_perturbation_thresholds_are_explicit():
    cases = MODULE.build_results()["cases"]
    for name in (
        "Real2Sim T best-sim checkpoint",
        "OSCAR Skeleton",
        "Cosmos-Surg manual",
        "WM-PolicyEval / IRASim",
    ):
        case = cases[name]
        assert case[
            "symmetric_per_score_perturbation_for_real_winner_to_tie_sim_top"
        ] > 0
        assert (
            case["symmetric_per_score_perturbation_to_change_sim_winner"] > 0
        )
    assert cases["Real2Sim T best-sim checkpoint"][
        "minimum_sim_top_k_covering_a_real_winner"
    ] == 2
    assert abs(
        cases["Real2Sim T best-sim checkpoint"]["pearson_r_min"]
        - 0.8778203471513463
    ) < 1e-12
    assert abs(
        cases["Real2Sim T best-sim checkpoint"]["pearson_r_max"]
        - 0.9474693713881575
    ) < 1e-12
    assert not cases["WM-PolicyEval / IRASim"][
        "meets_displayed_real_regret_tolerance"
    ]["10_pp"]


def test_committed_independent_result_matches_regeneration():
    committed = json.loads(
        (HERE / "result-independent-decision-audit.json").read_text(encoding="utf-8")
    )
    assert committed == MODULE.build_results()
