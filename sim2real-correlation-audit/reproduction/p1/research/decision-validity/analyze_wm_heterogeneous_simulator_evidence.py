#!/usr/bin/env python3
"""H239 extension: policy-heterogeneous simulator evidence sensitivity."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np

import analyze_wm_missing_simulator_uncertainty as h239


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-wm-heterogeneous-simulator-evidence-sensitivity.md"
OUTPUT = HERE / "result-wm-heterogeneous-simulator-evidence-sensitivity.json"
H239_RESULT = HERE / "result-wm-missing-simulator-evidence-sensitivity.json"
N_DRAWS = 500_000
BASE_SEED = 24_107_031
SCENARIOS = {
    "common_10": (10.0, 10.0, 10.0),
    "common_500": (500.0, 500.0, 500.0),
    "octo_base_10": (10.0, 500.0, 500.0),
    "octo_base_0": (0.0, 500.0, 500.0),
    "octo_small_10": (500.0, 10.0, 500.0),
    "octo_small_0": (500.0, 0.0, 500.0),
    "openvla_10": (500.0, 500.0, 10.0),
    "openvla_0": (500.0, 500.0, 0.0),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def winner_probabilities(best: np.ndarray, candidates: list[str]) -> dict[str, float]:
    return {
        candidate: float(np.mean(best == index))
        for index, candidate in enumerate(candidates)
    }


def evaluate(
    panel: dict[str, object],
    evidence: tuple[float, ...],
    draws: int,
    seed: int,
) -> dict[str, object]:
    require(len(evidence) == 3, "evidence vector must have three policies")
    require(draws > 0, "draw count must be positive")
    evidence_array = np.asarray(evidence, dtype=float)
    require(
        np.all(np.isfinite(evidence_array)) and np.all(evidence_array >= 0),
        "evidence values must be finite and nonnegative",
    )
    real_successes = np.asarray(panel["real_successes"], dtype=float)
    sim_rates = np.asarray(panel["sim_rates"], dtype=float)
    require(real_successes.shape == sim_rates.shape == (3, 4), "panel shape changed")
    rng = np.random.default_rng(seed)
    real = rng.beta(
        real_successes + 1,
        21 - real_successes,
        size=(draws, 3, 4),
    ).mean(axis=2)
    expanded = evidence_array[:, None]
    sim = rng.beta(
        1 + expanded * sim_rates,
        1 + expanded * (1 - sim_rates),
        size=(draws, 3, 4),
    ).mean(axis=2)
    real_best = np.argmax(real, axis=1)
    sim_best = np.argmax(sim, axis=1)
    matches = real_best == sim_best
    probability = float(np.mean(matches))

    posterior_mean_cells = (1 + expanded * sim_rates) / (2 + expanded)
    posterior_mean_scores = posterior_mean_cells.mean(axis=1)
    maximum = float(np.max(posterior_mean_scores))
    winner_set = [
        panel["candidates"][index]
        for index, value in enumerate(posterior_mean_scores)
        if abs(float(value) - maximum) <= 1e-15
    ]
    ordered = np.sort(posterior_mean_scores)[::-1]
    return {
        "evidence_by_policy": {
            candidate: float(evidence_array[index])
            for index, candidate in enumerate(panel["candidates"])
        },
        "draws": draws,
        "seed": seed,
        "latent_winner_concordance": probability,
        "monte_carlo_se": math.sqrt(probability * (1 - probability) / draws),
        "real_latent_winner_probabilities": winner_probabilities(
            real_best, panel["candidates"]
        ),
        "sim_latent_winner_probabilities": winner_probabilities(
            sim_best, panel["candidates"]
        ),
        "posterior_mean_sim_policy_scores": {
            candidate: float(posterior_mean_scores[index])
            for index, candidate in enumerate(panel["candidates"])
        },
        "posterior_mean_sim_winner_set": winner_set,
        "posterior_mean_sim_winner_margin": float(ordered[0] - ordered[1]),
    }


def h239_probability(model: str, evidence: str) -> tuple[float, float]:
    data = json.loads(H239_RESULT.read_text(encoding="utf-8"))
    row = next(
        item
        for item in data["panels"][model]["scenarios"]
        if item["prior_alpha_beta"] == 1
        and item["sim_effective_bernoulli_equivalents_per_policy_task"] == evidence
    )
    return (
        row["probability_sampled_sim_winner_is_sampled_real_best"],
        row["monte_carlo_se"],
    )


def stable(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def build() -> dict[str, object]:
    panels = h239.load_panels()
    results = {}
    common_checks = []
    for model_index, model in enumerate(sorted(panels)):
        scenarios = {
            name: evaluate(
                panels[model],
                evidence,
                N_DRAWS,
                BASE_SEED + 10_000 * model_index + index,
            )
            for index, (name, evidence) in enumerate(SCENARIOS.items())
        }
        for name, label in (("common_10", "10"), ("common_500", "500")):
            expected, expected_se = h239_probability(model, label)
            observed = scenarios[name]["latent_winner_concordance"]
            observed_se = scenarios[name]["monte_carlo_se"]
            tolerance = 4 * math.sqrt(expected_se**2 + observed_se**2)
            require(
                abs(observed - expected) <= tolerance,
                f"{model}/{name}: common-evidence H239 parity failed",
            )
            common_checks.append(
                {
                    "model": model,
                    "scenario": name,
                    "h239_probability": expected,
                    "current_probability": observed,
                    "four_combined_se_tolerance": tolerance,
                }
            )
        results[model] = {
            "candidates": panels[model]["candidates"],
            "scenarios": scenarios,
            "minimum_concordance": min(
                row["latent_winner_concordance"] for row in scenarios.values()
            ),
            "maximum_concordance": max(
                row["latent_winner_concordance"] for row in scenarios.values()
            ),
            "scenarios_above_one_half": [
                name
                for name, row in scenarios.items()
                if row["latent_winner_concordance"] > 0.5
            ],
        }
    require(
        results["IRASim"]["scenarios_above_one_half"],
        "IRASim did not cross one half under heterogeneous evidence",
    )
    return stable(
        {
            "schema": "wm-heterogeneous-simulator-evidence-sensitivity-v1",
            "status": "pass",
            "classification": (
                "common_evidence_direction_does_not_extend_to_heterogeneous_evidence"
            ),
            "outcome_status": "domain_review_triggered_outcome_exposed_exploratory",
            "protocol_sha256": sha256(PROTOCOL),
            "implementation_sha256": sha256(Path(__file__)),
            "input_sha256": sha256(h239.INPUT),
            "h239_result_sha256": sha256(H239_RESULT),
            "runtime": {
                "python": platform.python_version(),
                "numpy": np.__version__,
            },
            "draws_per_scenario": N_DRAWS,
            "prior_alpha_beta": 1,
            "common_evidence_parity_checks": common_checks,
            "panels": results,
            "scope": (
                "Posterior latent-rank concordance under independent Beta cells "
                "and policy-specific effective evidence shared across four tasks. "
                "Not operational selection reliability or an estimate of actual "
                "evidence/dependence."
            ),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build()
    if args.write:
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE {args.out}")
    else:
        require(
            json.loads(args.out.read_text(encoding="utf-8")) == result,
            "stored heterogeneous-evidence result differs",
        )
        print("OK: WM heterogeneous simulator-evidence sensitivity")


if __name__ == "__main__":
    main()
