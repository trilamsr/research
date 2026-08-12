import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "analyze_cosmos_two_sided.py"
SPEC = importlib.util.spec_from_file_location("cosmos_two_sided", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_recovered_rates_are_integer_count_compatible():
    _, _, real, sim = MODULE.load_counts()
    assert np.all((real >= 0) & (real <= 10))
    assert np.all((sim >= 0) & (sim <= 60))
    assert real.shape == sim.shape == (6, 4)


def test_two_sided_stress_envelope_remains_below_half():
    result = MODULE.build_results()
    assert result["stress_envelope"]["all_scenarios_below_one_half"]


def test_committed_artifact_parity():
    expected = json.loads(
        (HERE / "result-cosmos-two-sided.json").read_text(encoding="utf-8")
    )
    assert MODULE.stable(MODULE.build_results()) == expected
