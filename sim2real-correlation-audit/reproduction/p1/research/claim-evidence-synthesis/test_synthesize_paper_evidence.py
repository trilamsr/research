import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "real2sim-noise-floor"))

import synthesize_paper_evidence as pr
from compare_json_numeric import compare


def result():
    return pr.build_results()


def test_consensus_facts_are_locked():
    assert result()["schema_version"] == 4
    survey = result()["survey"]
    assert survey["included_papers"] == 26
    assert survey["recovered_papers"] == 19
    assert survey["finite_panel_consensus"] == 26
    assert survey["target_population_consensus_no"] == 26
    assert survey["target_population_consensus_yes"] == 0
    assert survey["new_policy_supported_any_coding"] == 0
    assert survey["new_task_supported_any_coding"] == 0
    assert survey["crossed_supported_any_coding"] == 0
    assert survey["prints_any_correlation_uncertainty"] == 6
    assert survey["prints_no_correlation_uncertainty"] == 20


def test_cosmos_two_sided_remeasurement_is_fact_locked():
    result_block = result()["decision_atlas"][
        "cosmos_manual_two_sided_remeasurement"
    ]
    envelope = result_block["stress_envelope"]
    assert envelope["all_scenarios_below_one_half"]
    assert 0.20 < envelope[
        "minimum_probability_sampled_winners_match"
    ] < 0.23
    assert 0.20 < envelope[
        "maximum_probability_sampled_winners_match"
    ] < 0.23


def test_real2sim_two_sided_remeasurement_is_fact_locked():
    envelope = result()["decision_atlas"][
        "real2sim_t_two_sided_remeasurement"
    ]["stress_envelope"]
    assert envelope["all_scenarios_below_one_half"]
    assert 0.32 < envelope[
        "minimum_probability_sampled_winners_match"
    ] < 0.34
    assert 0.45 < envelope[
        "maximum_probability_sampled_winners_match"
    ] < 0.46


def test_oscar_public_join_is_fact_locked_from_canonical_dependency():
    oscar = result()["decision_atlas"]["oscar_public_join"]
    assert oscar["released_sessions"] == 63
    assert oscar["released_binary_outcomes"] == 441
    assert oscar["printed_wm_inferred_denominator_per_policy"] == 65
    assert "not an exact matched-session" in oscar["scope"]
    atlas = {row["case"]: row for row in result()["decision_atlas"]["cases"]}
    assert "63 released sessions (441 binary outcomes)" in atlas[
        "OSCAR Skeleton"
    ]["real_denominator"]
    assert "65 sessions" in atlas["OSCAR Skeleton"]["simulator_denominator"]


def test_consensus_helpers_detect_mutated_coding():
    details = {
        "paper-a": {
            "released": ("no",),
            "blind-a": ("no",),
            "blind-b": ("no",),
        },
        "paper-b": {
            "released": ("unsupported",),
            "blind-a": ("supported",),
            "blind-b": ("unsupported",),
        },
    }
    assert pr.count_all_coders_assign({"paper-a": details["paper-a"]}, "no") == 1
    assert pr.count_any_coder_assigns({"paper-b": details["paper-b"]}, "supported") == 1


def test_selection_split_is_not_mislabeled_as_three_way_consensus():
    survey = result()["survey"]
    assert survey["selection_final"] == {"yes": 8, "no": 17, "not-applicable": 1}
    assert survey["selection_all_three_exact_agreement"] == 12


def test_two_explicit_unit_codings_generate_23_to_25_range():
    sensitivity = result()["unit_count_sensitivity"]
    assert sensitivity["legacy_under_10"] == 25
    assert sensitivity["permissive_under_10"] == 23
    assert sensitivity["under_10_range"] == [23, 25]


def test_four_of_five_printed_p_values_are_below_policy_block_resolution():
    rows = result()["pvalue_resolution"]
    assert len(rows) == 5
    assert sum(row["printed_below_policy_resolution"] for row in rows) == 4
    assert next(row for row in rows if row["paper"] == "RoboWorld")[
        "best_case_policy_resolution"
    ] == 1 / 40320


def test_declared_illustrative_leverage_table_regenerates():
    leverage = result()["leverage"]
    assert leverage["n_rows"] == 28
    assert "not a corpus-prevalence denominator" in leverage["scope"]
    assert leverage["above_descriptive_0_10"] == 10
    assert abs(leverage["median_max_abs_delta_r"] - 0.060621865232775574) < 1e-15
    by_name = {row["dataset"]: row for row in leverage["rows"]}
    assert by_name["MolmoSpaces pick"]["n_points"] == 8
    assert abs(by_name["MolmoSpaces pick"]["max_abs_delta_r"] - 0.01995539035909777) < 1e-12
    assert abs(by_name["RoboWorld 9a"]["max_abs_delta_r"] - 0.19080750924747014) < 1e-12
    assert by_name["RoboWorld 9a"]["max_abs_delta_unit"] == "PaliGemma Binning"
    assert abs(by_name["RoboWorld 9a"]["r_after_max_delta_deletion"] - 0.7979679698937143) < 1e-12
    assert abs(by_name["WM-PolicyEval IRASim"]["max_abs_delta_r"] - 0.1764175907514185) < 1e-12


def test_checkpoint_selection_enumerates_ties():
    by_task = {row["task"]: row for row in result()["checkpoint_selection"]}
    rope = by_task["rope"]
    assert abs(rope["all_checkpoint_r"] - 0.9007080183704778) < 1e-15
    assert rope["best_real_n_tie_combinations"] == 4
    assert abs(rope["best_real_r_min"] - (-0.4714045207910319)) < 1e-15
    assert abs(rope["best_real_r_max"] - (-0.10307361440601553)) < 1e-15
    assert rope["best_sim_n_tie_combinations"] == 1
    assert abs(rope["best_sim_r_min"] - (-0.683130051063974)) < 1e-15


def test_simpler_decisions_regenerate_from_official_task_arrays():
    cases = result()["decision_cases"]["simpler"]
    google = cases["google_robot"]
    assert google["n_policies"] == 6
    assert google["n_tasks"] == 5
    assert abs(google["aggregate"]["pearson_r"] - 0.9736271622403364) < 1e-15
    assert google["aggregate"]["robustly_correct"]
    assert google["per_task"]["agreement_count"] == 3
    assert google["per_task"]["disagreement_count"] == 2
    assert google["leave_one_task_out"]["agreement_count"] == 5
    widowx = cases["widowx"]
    assert widowx["n_policies"] == 3
    assert widowx["n_tasks"] == 4
    assert abs(widowx["aggregate"]["pearson_r"] - 0.9498357332381226) < 1e-15
    assert widowx["aggregate"]["robustly_correct"]
    assert widowx["per_task"]["agreement_count"] == 3
    assert widowx["per_task"]["disagreement_count"] == 1
    assert widowx["leave_one_task_out"]["agreement_count"] == 4


def test_real2sim_decisions_are_tie_complete_and_extraction_sensitive():
    case = result()["decision_cases"]["real2sim"]
    assert case["summary"]["n_task_rule_cells"] == 9
    assert case["summary"]["necessarily_wrong"] == 7
    assert case["summary"]["robustly_correct"] == 1
    assert case["summary"]["tie_or_selection_dependent"] == 1
    t_mean = next(
        row
        for row in case["rows"]
        if row["task"] == "T" and row["rule"] == "mean"
    )
    assert t_mean["necessarily_wrong"]
    assert t_mean["checkpoint_tie_combinations"] == 1
    assert abs(t_mean["pearson_r_min"] - 0.9624768021107316) < 1e-15
    assert abs(t_mean["regret_fraction_min"] - 0.05729166666666663) < 1e-15
    sensitivity = case["coincident_rope_zero_sensitivity"]
    assert sensitivity["best_real_and_best_sim_unchanged"]
    assert abs(sensitivity["all_checkpoint_r_declared"] - 0.9007080168247251) < 1e-15
    assert abs(sensitivity["all_checkpoint_r_one_removed"] - 0.8806296515463028) < 1e-15
    assert sensitivity["mean_rule_declared"]["robustly_correct"]
    assert sensitivity["mean_rule_one_removed"]["robustly_correct"]


def test_practical_recipe_rank_panel_decisions_regenerate():
    case = result()["decision_cases"]["practical_recipe"]
    assert case["panel_count"] == 11
    assert case["agreement_count"] == 8
    assert case["disagreement_count"] == 3
    assert abs(case["max_printed_pearson_among_disagreements"] - 0.672) < 1e-15
    assert abs(case["max_printed_spearman_among_disagreements"] - 0.6) < 1e-15


def test_expanded_decision_atlas_matches_canonical_outputs():
    atlas = {row["case"]: row for row in result()["decision_atlas"]["cases"]}
    assert set(atlas) == {
        "WorldGym",
        "Digital Cousins",
        "SIMPLER Google",
        "Real2Sim T best-sim checkpoint",
        "OSCAR Skeleton",
        "Cosmos-Surg manual",
        "WM-PolicyEval / Cosmos",
        "WM-PolicyEval / IRASim",
    }
    assert atlas["WorldGym"]["robustly_correct"]
    assert atlas["WorldGym"]["leave_one_task_out"] == {"correct": 17, "total": 17}
    assert atlas["Digital Cousins"]["all_task_subsets"] == {"correct": 15, "total": 15}
    assert abs(atlas["OSCAR Skeleton"]["pearson_r"] - 0.855166828631) < 1e-15
    assert atlas["OSCAR Skeleton"]["sim_winners"] == ["PG-FAST+"]
    assert atlas["OSCAR Skeleton"]["real_winners"] == ["pi0-FAST"]
    assert abs(atlas["OSCAR Skeleton"]["displayed_real_regret_pp"] - 1.1) < 1e-15
    assert abs(atlas["Cosmos-Surg manual"]["pearson_r"] - 0.883136559068) < 1e-15
    assert atlas["Cosmos-Surg manual"]["leave_one_task_out"] == {
        "correct": 0,
        "total": 4,
    }
    assert abs(
        atlas["WM-PolicyEval / IRASim"][
            "posterior_probability_sim_winner_is_real_best"
        ]
        - 0.000168
    ) < 1e-15


def test_complete_matrix_ledger_is_not_outcome_balanced():
    ledger = result()["complete_matrix_decisions"]
    assert ledger["n_panels"] == 19
    assert ledger["correct"] == 17
    assert ledger["wrong"] == 2
    assert {row["panel_id"] for row in ledger["rows"]} == {
        "Cosmos-Surg-dVRK/automated_fig1b",
        "Cosmos-Surg-dVRK/manual_human_vs_dvrk",
        "Digital Cousins",
        "Hi-WM",
        "SIMPLER/google_robot",
        "SIMPLER/widowx",
        "WEAVER/CtrlWorld",
        "WEAVER/WEAVER",
        "WEAVER/WEAVER-FT",
        "WM-PolicyEval/Cosmos",
        "WM-PolicyEval/IRASim",
        "WorldEval",
        "WorldGym",
        "REALM/Default",
        "REALM/Overall",
        "REALM/VB-POSE",
        "Mem-World",
        "MolmoSpaces/common-appendix-roster",
        "EmbodiedSplat/mesh-conditions",
    }


def test_broadened_inference_recode_preserves_non_sampling_evidence():
    recode = result()["inference_link_recode"]
    assert len(recode["rows"]) == 26
    assert recode["held_out_predictive"] >= 6
    assert recode["fixed_benchmark_scope"] >= 4
    assert recode["formal_population_prediction"] == 0


def test_remeasurement_results_are_explicitly_finite_panel_and_model_conditional():
    atlas = result()["decision_atlas"]
    assert "Model-conditional real-trial measurement uncertainty" in (
        atlas["real_trial_remeasurement_scope"]
    )
    assert "not a sampling probability" in atlas["task_subset_scope"]
    by_case = {row["case"]: row for row in atlas["cases"]}
    real2sim = by_case["Real2Sim T best-sim checkpoint"]
    assert real2sim["posterior_probability_sim_winner_is_real_best"] is None
    assert real2sim["pearson_r_range"] == [
        0.8778203471513463,
        0.9474693713881575,
    ]
    assert abs(real2sim["displayed_real_regret_pp"] - 12.5) < 1e-15
    assert abs(
        by_case["Cosmos-Surg manual"][
            "posterior_probability_sim_winner_is_real_best"
        ]
        - 0.087508
    ) < 1e-15
    assert abs(
        by_case["WM-PolicyEval / Cosmos"][
            "posterior_probability_sim_winner_is_real_best"
        ]
        - 0.999852
    ) < 1e-15


def test_mmrv_stability_table_regenerates():
    by_name = {row["dataset"]: row for row in result()["mmrv_stability"]}
    dc = by_name["Digital Cousins, by policy"]
    assert abs(dc["mmrv"] - 0.11145937500000003) < 1e-15
    assert abs(dc["absolute_mmrv_range"] - 0.0208308333333333) < 1e-15
    rw = by_name["RoboWorld 10b"]
    assert abs(rw["mmrv"] - 0.05506668074431946) < 1e-15
    assert abs(rw["relative_mmrv_swing"] - 0.8059818968909874) < 1e-15


def test_real2sim_convention_and_exact_fractions_regenerate():
    mmrv = result()["real2sim_mmrv"]
    expected = [["leq-xor", "sim", "N"]]
    assert mmrv["fig3_matching_conventions"] == expected
    assert mmrv["fig9_matching_conventions"] == expected
    assert mmrv["fig3_values"]["T"]["exact_fraction"] == "13/120"
    assert mmrv["fig9_values"]["toy_packing"]["exact_fraction"] == "21/200"
    assert mmrv["fig9_values"]["rope_routing"]["exact_fraction"] == "307/2000"
    assert mmrv["fig9_values"]["t_block_pushing"]["exact_fraction"] == "209/3000"
    assert mmrv["t_block_checkpoint_counts"]["figure3_table1"] == 15
    assert mmrv["t_block_checkpoint_counts"]["figure10_replay_subset"] == 12
    assert abs(mmrv["t_block_lattice"]["n_12"]["miss"] - 0.001375) < 1e-15
    assert abs(mmrv["t_block_lattice"]["n_15"]["miss"] - (1 / 3000)) < 1e-15


def test_bayesian_sensitivity_is_model_labeled_and_regenerates():
    by_task = {row["task"]: row for row in result()["bayesian_sensitivity"]}
    assert set(by_task) == {"T", "rope", "sloth"}
    assert by_task["rope"]["prior"] == "uniform on rho in [-1, 1]"
    lo, hi = by_task["rope"]["equal_tailed_95_interval"]
    assert abs(lo - (-0.538394461605)) < 1e-12
    assert abs(hi - 0.90085909914) < 1e-12


def test_wm_missing_evidence_and_calibration_are_bound() -> None:
    generated = result()
    missing_result = generated["wm_missing_simulator_sensitivity"]
    assert "common_effective_evidence" in missing_result["classification"]
    assert "not reliability of an observed-data operational action" in missing_result[
        "scope"
    ]
    missing = missing_result["panels"]
    assert missing["IRASim"]["stress_envelope"][
        "all_scenarios_below_one_half"
    ]
    assert (
        missing["IRASim"]["stress_envelope"][
            "maximum_probability_sampled_winners_match"
        ]
        == 0.43204
    )
    assert not missing["Cosmos"]["stress_envelope"][
        "all_scenarios_above_one_half"
    ]
    assert all(
        row["expected_real_regret_monte_carlo_se"] > 0
        for panel in missing.values()
        for row in panel["scenarios"]
    )
    calibration = generated["wm_probability_calibration"]["panels"]
    assert calibration["Cosmos"]["metrics"]["cell_rate_mse"] == 0.023958333333
    assert (
        calibration["Cosmos"]["metrics"]["empirical_individual_outcome_brier"]
        == 0.204166666667
    )
    assert calibration["IRASim"]["full_panel_affine_selection_check"][
        "winner_preserved"
    ]
    for model in ("Cosmos", "IRASim"):
        heldout = calibration[model]["task_heldout_affine_recalibration"]
        assert heldout["heldout_tasks_improved"] == 2
        assert heldout["crossfitted_winner_margin"] > 0


def test_wm_review_triggered_heterogeneous_and_nonlinear_checks_are_bound() -> None:
    generated = result()
    heterogeneous = generated["wm_heterogeneous_simulator_evidence"][
        "panels"
    ]["IRASim"]["scenarios"]
    assert heterogeneous["common_10"]["latent_winner_concordance"] < 0.5
    assert heterogeneous["openvla_10"]["latent_winner_concordance"] > 0.5
    assert heterogeneous["openvla_0"]["latent_winner_concordance"] > 0.95

    nonlinear = generated["wm_nonlinear_calibration"]["panels"]["IRASim"]
    assert nonlinear["winner_changed"]
    assert nonlinear["isotonic_winner"] == "OpenVLA"
    assert (
        nonlinear["murphy_forecast_level_decomposition"][
            "brier_skill_vs_empirical_prevalence"
        ]
        < 0
    )


def test_committed_fact_artifacts_match_the_generator():
    generated = result()
    committed = json.loads((ROOT / "result-paper-evidence.json").read_text(encoding="utf-8"))
    compare(committed, generated, atol=1e-12)
    assert (ROOT / "result-quantitative-supplement.md").read_text(encoding="utf-8") == pr.markdown(generated)
    assert (ROOT / "result-main-tables.md").read_text(encoding="utf-8") == pr.main_tables_markdown(generated)
