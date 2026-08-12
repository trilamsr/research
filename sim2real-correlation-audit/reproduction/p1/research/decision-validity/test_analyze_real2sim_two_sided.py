import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "analyze_real2sim_two_sided.py"
SPEC = importlib.util.spec_from_file_location("real2sim_two_sided", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_t_block_cell_structure():
    cells = MODULE.load_cells()
    assert set(cells) == {"act", "dp", "pi0", "svla"}
    assert sum(len(rows) for rows in cells.values()) == 15
    assert {row[2] for rows in cells.values() for row in rows} == {16.0}


def test_stress_envelope_remains_below_half():
    assert MODULE.build_results()["stress_envelope"][
        "all_scenarios_below_one_half"
    ]


def test_committed_artifact_parity():
    expected = json.loads(
        (HERE / "result-real2sim-two-sided.json").read_text(encoding="utf-8")
    )
    assert MODULE.stable(MODULE.build_results()) == expected
