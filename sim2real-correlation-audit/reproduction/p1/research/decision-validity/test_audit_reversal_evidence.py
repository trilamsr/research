import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "audit_reversal_evidence", ROOT / "audit_reversal_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_reversal_evidence_known_answers():
    MODULE.main()
    result = json.loads(
        (ROOT / "result-reversal-evidence.json").read_text()
    )
    assert abs(result["WorldGym"]["pooled_cell_pearson_r"] - 0.7847863) < 1e-6
    assert result["WorldGym"]["aggregate_policy_decision"][
        "robustly_correct"
    ]
    irasim = result["WM-PolicyEval"]["IRASim"][
        "aggregate_policy_decision"
    ]
    assert irasim["sim_winners"] == ["Octo-Base"]
    assert irasim["real_winners"] == ["OpenVLA"]
    assert abs(irasim["real_regret_min"] - 0.275) < 1e-12
    assert result["A Practical Recipe"]["disagreement_count"] == 3
    cosmos = result["Cosmos-Surg-dVRK"]["manual_human_vs_dvrk"]
    assert cosmos["sim_winners"] == ["GR00T N1.5 50k"]
    assert cosmos["real_winners"] == ["GR00T N1 20k"]
    assert abs(cosmos["pearson_r"] - 0.883136559068) < 1e-12
    assert abs(cosmos["real_regret_min"] - 0.1) < 1e-12
    run_companion = cosmos["training_run_companion"]
    assert run_companion["sim_winners"] == ["groot-n1.5"]
    assert run_companion["real_winners"] == ["groot-n1"]
    assert abs(run_companion["pearson_r"] - 0.905397391522) < 1e-12
    assert abs(run_companion["spearman_rho"] - 0.5) < 1e-12
    assert abs(run_companion["real_regret_min"] - 0.0375) < 1e-12
    assert result["OSCAR"]["sim_winners"] == ["PG-FAST+"]
    assert result["OSCAR"]["real_winners"] == ["pi0-FAST"]


def test_simpler_documentation_call_order_is_not_equivalent():
    MODULE.main()
    rows = json.loads(
        (ROOT / "result-reversal-evidence.json").read_text()
    )["SIMPLER"]["mmrv_argument_order_audit"]
    move_near = rows["google_robot_move_near"]
    assert abs(
        move_near["paper_equation_and_executable_script"] - 0.111
    ) < 1e-12
    assert abs(
        move_near["readme_and_calc_metrics_docstring_example"]
        - 0.0026666666666666666
    ) < 1e-12
