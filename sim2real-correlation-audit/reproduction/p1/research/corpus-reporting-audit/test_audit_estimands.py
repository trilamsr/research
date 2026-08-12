import sys
from math import factorial
from pathlib import Path

FAMILY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FAMILY_ROOT))

import compare_estimand_codings as compare
import audit_estimands as ea
from summarize_corpus import SURVEY


EXPECTED_PAPERS = {
    "real2sim-eval",
    "RoboWorld",
    "Digital Cousins",
    "SIMPLER",
    "SimFoundry",
    "WorldGym",
    "RoboSnap",
    "REALM",
    "PolaRiS",
    "SC3-Eval",
    "WorldEval",
    "A Practical Recipe",
    "Cosmos-Surg-dVRK",
    "Gemini/Veo",
    "DreamDojo",
    "dWorldEval",
    "WEAVER",
    "PlayWorld",
    "EmbodiedSplat",
    "MolmoSpaces",
    "Mem-World",
    "Colosseum V2",
    "VISER",
    "OSCAR",
    "Hi-WM",
    "WM-PolicyEval",
}


def test_full_corpus_grid_is_complete_and_valid():
    rows = ea.load_rows()
    assert len(rows) == 31
    assert {row["paper"] for row in rows} == EXPECTED_PAPERS
    assert len({(row["paper"], row["coefficient_id"]) for row in rows}) == len(rows)


def test_multiple_material_coefficient_structures_are_preserved():
    rows = ea.load_rows()
    counts = {
        paper: sum(row["paper"] == paper for row in rows)
        for paper in EXPECTED_PAPERS
    }
    assert counts["real2sim-eval"] == 3
    assert counts["EmbodiedSplat"] == 2
    assert counts["VISER"] == 2
    assert counts["WM-PolicyEval"] == 2


def test_summary_separates_description_from_inference():
    summary = ea.summarize(ea.load_rows())
    assert summary["papers"] == 26
    assert summary["coefficient_rows"] == 31
    assert summary["finite_panel_defined"] == 26
    assert summary["generalization_axis_named"] == 26
    assert summary["target_population_defined"] == 0
    assert summary["new_policy_supported"] == 0
    assert summary["new_task_supported"] == 0
    assert summary["crossed_supported"] == 0
    assert summary["printed_p_value"] == 5
    assert summary["correlation_interval"] == 1
    assert summary["any_correlation_uncertainty"] == 6
    assert summary["no_correlation_uncertainty"] == 20


def test_conditional_permutation_resolution_depends_on_axis():
    summary = ea.summarize(ea.load_rows())
    got = {row["paper"]: row for row in summary["conditional_permutation_floors"]}
    assert got["RoboWorld"]["policy_floor"] == 1 / factorial(8)
    assert got["WorldGym"]["policy_floor"] == 1 / factorial(3)
    assert got["WorldGym"]["task_floor"] == 1 / factorial(17)
    assert got["REALM"]["policy_floor"] == 1 / factorial(3)
    assert got["REALM"]["task_floor"] == 1 / factorial(7)
    assert got["Cosmos-Surg-dVRK"]["policy_floor"] == 1 / factorial(3)
    assert got["Cosmos-Surg-dVRK"]["task_floor"] == 1 / factorial(4)
    assert got["Mem-World"]["policy_floor"] == 1 / factorial(2)
    assert got["Mem-World"]["task_floor"] == 1 / factorial(5)


def test_legacy_k_counts_are_labeled_as_sensitivity_only():
    summary = ea.summarize(ea.load_rows())
    assert summary["legacy_universal_k_under_10"] == 25
    assert summary["legacy_universal_k_over_5"] == 3


def test_legacy_table_imports_observable_facts_from_estimand_grid():
    rows = ea.load_rows()
    by_paper = {}
    for row in rows:
        facts = by_paper.setdefault(
            row["paper"], {"uncertainty_on_r": set(), "selection_rule": set()}
        )
        facts["uncertainty_on_r"].add(row["uncertainty_on_r"])
        facts["selection_rule"].add(row["selection_rule"])

    for survey_row in SURVEY:
        paper = survey_row[0]
        assert {survey_row[5]} == by_paper[paper]["uncertainty_on_r"]
        assert {survey_row[6]} == by_paper[paper]["selection_rule"]


def test_worldgym_figure_only_p_value_is_preserved():
    row = next(row for row in ea.load_rows() if row["paper"] == "WorldGym")
    assert row["uncertainty_on_r"] == "p-value"
    assert "p<0.001" in row["interpretive_note"]


def test_selection_rule_categories_are_not_collapsed_to_boolean():
    counts = {}
    for row in SURVEY:
        counts[row[6]] = counts.get(row[6], 0) + 1
    assert counts == {"yes": 8, "no": 17, "not-applicable": 1}


def test_two_blind_codings_are_preserved_with_complete_corpus_coverage():
    result = compare.summarize()
    assert result["rows"] == {"released": 31, "blind-a": 72, "blind-b": 60}
    assert set(result["papers"]) == EXPECTED_PAPERS
    assert result["agreements"]["finite_panel_description"]["all_three"] == 26
    assert result["agreements"]["target_population_defined"]["all_three"] == 26


def test_worldgym_figure_only_p_value_is_present_in_both_blind_codings():
    for name in ("blind-a", "blind-b"):
        rows = compare.load(compare.CODINGS[name])
        worldgym = [row for row in rows if row["paper"] == "WorldGym"]
        assert worldgym
        assert any("p-value" in row["uncertainty_on_r"] for row in worldgym)
