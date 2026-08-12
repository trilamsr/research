import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "analyze_decision_confidence", ROOT / "analyze_decision_confidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_subset_stability_known_answers(tmp_path):
    out = tmp_path / "confidence.json"
    MODULE.main(out)
    result = json.loads(out.read_text())
    subset = result["subset_stability"]
    assert subset["WorldGym"]["leave_one_block_out_correct"] == 17
    assert subset["WorldGym"]["all_nonempty_subsets_correct"] == 131068
    assert subset["Digital Cousins"]["all_nonempty_subsets_correct"] == 15
    assert (
        subset["Cosmos-Surg-dVRK/automated_fig1b"][
            "all_nonempty_subsets_correct"
        ]
        == 5
    )
    assert (
        subset["Cosmos-Surg-dVRK/automated_fig1b"][
            "all_nonempty_subsets_possibly_correct"
        ]
        == 5
    )
    assert (
        subset["WM-PolicyEval/IRASim"][
            "all_nonempty_subsets_possibly_correct"
        ]
        == 7
    )
    assert (
        subset["WM-PolicyEval/IRASim"]["leave_one_block_out_correct"] == 1
    )
    assert (
        subset["WM-PolicyEval/IRASim"][
            "leave_one_block_out_possibly_correct"
        ]
        == 2
    )
    assert not subset["Cosmos-Surg-dVRK/manual_human_vs_dvrk"][
        "full_correct"
    ]
    assert subset["Cosmos-Surg-dVRK/manual_human_vs_dvrk"][
        "leave_one_block_out_correct"
    ] == 0


def test_real_trial_posterior_known_answers(tmp_path):
    out = tmp_path / "confidence.json"
    MODULE.main(out)
    result = json.loads(out.read_text())["real_trial_posterior"]
    t_block = result["Real2Sim/mean_rule"]["T"]
    assert 0.255 < t_block[
        "posterior_probability_sim_winner_is_real_best"
    ] < 0.258
    irasim = result["WM-PolicyEval"]["IRASim"]
    assert irasim["posterior_probability_sim_winner_is_real_best"] < 0.0003
    manual = result["Cosmos-Surg-dVRK"]["manual_human_vs_dvrk"]
    assert 0.086 < manual[
        "posterior_probability_sim_winner_is_real_best"
    ] < 0.089
