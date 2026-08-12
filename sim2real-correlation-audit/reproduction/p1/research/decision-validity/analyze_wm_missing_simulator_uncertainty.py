#!/usr/bin/env python3
"""Two-sided WM-PolicyEval sensitivity to missing simulator evidence size."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "corpus-reporting-audit" / "sources"
INPUT = DATA / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-missing-simulator-evidence-sensitivity.md"
OUTPUT = HERE / "result-wm-missing-simulator-evidence-sensitivity.json"
BASE_SEED = 20260731
N_DRAWS = 300_000
STAGE_ZERO_DRAWS = 20_000
PRIORS = (0.5, 1.0, 2.0)
SIM_EVIDENCE_SIZES: tuple[float | None, ...] = (
    0.0,
    1.0,
    2.0,
    5.0,
    10.0,
    20.0,
    50.0,
    100.0,
    500.0,
    None,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8") as handle:
        return list(
            csv.DictReader(
                line
                for line in handle
                if line.strip() and not line.startswith("#")
            )
        )


def load_panels() -> dict[str, dict[str, object]]:
    rows = read_rows()
    models = sorted({row["world_model"] for row in rows})
    panels: dict[str, dict[str, object]] = {}
    for model in models:
        selected = [row for row in rows if row["world_model"] == model]
        candidates = sorted({row["policy"] for row in selected})
        tasks = sorted({row["task"] for row in selected})
        cells = {(row["policy"], row["task"]): row for row in selected}
        require(
            len(cells) == len(candidates) * len(tasks) == 12,
            f"{model}: incomplete 3x4 panel",
        )
        real_rates = np.array(
            [
                [
                    float(cells[(candidate, task)]["actual_success_rate"])
                    for task in tasks
                ]
                for candidate in candidates
            ],
            dtype=float,
        )
        sim_rates = np.array(
            [
                [
                    float(cells[(candidate, task)]["predicted_success_rate"])
                    for task in tasks
                ]
                for candidate in candidates
            ],
            dtype=float,
        )
        real_successes = 20.0 * real_rates
        require(
            np.allclose(real_successes, np.round(real_successes), atol=1e-12),
            f"{model}: real rates are not integer counts out of 20",
        )
        require(
            np.all((sim_rates >= 0) & (sim_rates <= 1)),
            f"{model}: simulator rate outside [0,1]",
        )
        panels[model] = {
            "candidates": candidates,
            "tasks": tasks,
            "real_successes": np.round(real_successes).astype(int),
            "sim_rates": sim_rates,
            "displayed_real_winner_index": int(
                np.argmax(real_rates.mean(axis=1))
            ),
            "displayed_sim_winner_index": int(
                np.argmax(sim_rates.mean(axis=1))
            ),
        }
    require(set(panels) == {"Cosmos", "IRASim"}, "unexpected panel roster")
    return panels


def scenario_seed(model_index: int, prior_index: int, evidence_index: int) -> int:
    return BASE_SEED + 10_000 * model_index + 100 * prior_index + evidence_index


def evaluate(
    panel: dict[str, object],
    prior: float,
    sim_evidence_size: float | None,
    draws: int,
    seed: int,
) -> dict[str, object]:
    require(math.isfinite(prior) and prior > 0, "prior must be positive finite")
    require(isinstance(draws, int) and draws > 0, "draws must be positive integer")
    if sim_evidence_size is not None:
        require(
            math.isfinite(sim_evidence_size) and sim_evidence_size >= 0,
            "simulator evidence must be nonnegative finite or infinity",
        )
    real_successes = np.asarray(panel["real_successes"], dtype=float)
    sim_rates = np.asarray(panel["sim_rates"], dtype=float)
    require(real_successes.shape == sim_rates.shape == (3, 4), "invalid panel shape")
    rng = np.random.default_rng(seed)
    real = rng.beta(
        real_successes + prior,
        20.0 - real_successes + prior,
        size=(draws,) + real_successes.shape,
    ).mean(axis=2)
    if sim_evidence_size is None:
        sim = np.broadcast_to(
            sim_rates.mean(axis=1),
            (draws, sim_rates.shape[0]),
        )
        evidence_label = "infinity_fixed_display"
    else:
        sim = rng.beta(
            sim_evidence_size * sim_rates + prior,
            sim_evidence_size * (1.0 - sim_rates) + prior,
            size=(draws,) + sim_rates.shape,
        ).mean(axis=2)
        evidence_label = f"{sim_evidence_size:g}"

    real_best = np.argmax(real, axis=1)
    sim_best = np.argmax(sim, axis=1)
    draw_index = np.arange(draws)
    regret = np.max(real, axis=1) - real[draw_index, sim_best]
    match = real_best == sim_best
    probability = float(np.mean(match))
    displayed_sim = int(panel["displayed_sim_winner_index"])
    displayed_real = int(panel["displayed_real_winner_index"])
    if sim_evidence_size is None:
        posterior_mean_sim = sim_rates
    else:
        posterior_mean_sim = (
            sim_evidence_size * sim_rates + prior
        ) / (sim_evidence_size + 2 * prior)
    posterior_mean_policy_scores = posterior_mean_sim.mean(axis=1)
    maximum_posterior_mean = float(np.max(posterior_mean_policy_scores))
    posterior_mean_winner_set = [
        panel["candidates"][index]
        for index, value in enumerate(posterior_mean_policy_scores)
        if abs(float(value) - maximum_posterior_mean) <= 1e-15
    ]
    return {
        "prior_alpha_beta": prior,
        "sim_effective_bernoulli_equivalents_per_policy_task": evidence_label,
        "draws": draws,
        "seed": seed,
        "probability_sampled_sim_winner_is_sampled_real_best": probability,
        "monte_carlo_se": math.sqrt(probability * (1.0 - probability) / draws),
        "probability_displayed_sim_winner_remains_sim_best": float(
            np.mean(sim_best == displayed_sim)
        ),
        "probability_displayed_real_winner_remains_real_best": float(
            np.mean(real_best == displayed_real)
        ),
        "probability_sampled_sim_selection_is_displayed_real_winner": float(
            np.mean(sim_best == displayed_real)
        ),
        "expected_real_regret_of_sampled_sim_winner": float(np.mean(regret)),
        "expected_real_regret_monte_carlo_se": float(
            np.std(regret, ddof=1) / math.sqrt(draws)
        ),
        "probability_positive_real_regret": float(np.mean(regret > 0)),
        "posterior_mean_sim_policy_scores": {
            candidate: float(posterior_mean_policy_scores[index])
            for index, candidate in enumerate(panel["candidates"])
        },
        "posterior_mean_sim_winner_set": posterior_mean_winner_set,
    }


def validate_stage_zero() -> dict[str, object]:
    panels = load_panels()
    rows = []
    zero_limit_checks = 0
    fixed_checks = 0
    for model_index, model in enumerate(sorted(panels)):
        panel = panels[model]
        candidates = panel["candidates"]
        displayed_real = candidates[int(panel["displayed_real_winner_index"])]
        displayed_sim = candidates[int(panel["displayed_sim_winner_index"])]
        require(displayed_real == "OpenVLA", f"{model}: real winner changed")
        expected_sim = "OpenVLA" if model == "Cosmos" else "Octo-Base"
        require(displayed_sim == expected_sim, f"{model}: simulator winner changed")
        for prior_index, prior in enumerate(PRIORS):
            row = evaluate(
                panel,
                prior,
                0.0,
                STAGE_ZERO_DRAWS,
                scenario_seed(model_index, prior_index, 0),
            )
            probability = row[
                "probability_sampled_sim_winner_is_sampled_real_best"
            ]
            se = math.sqrt((1 / 3) * (2 / 3) / STAGE_ZERO_DRAWS)
            require(
                abs(probability - 1 / 3) <= 6 * se,
                f"{model}: zero-evidence exchangeable limit failed",
            )
            zero_limit_checks += 1
        fixed = evaluate(
            panel,
            1.0,
            None,
            STAGE_ZERO_DRAWS,
            scenario_seed(model_index, 1, len(SIM_EVIDENCE_SIZES) - 1),
        )
        fixed_probability = fixed[
            "probability_sampled_sim_winner_is_sampled_real_best"
        ]
        if model == "Cosmos":
            require(fixed_probability > 0.85, "Cosmos fixed positive control changed")
        else:
            require(fixed_probability < 0.01, "IRASim fixed mismatch changed")
        fixed_checks += 1
        rows.append(
            {
                "model": model,
                "displayed_real_winner": displayed_real,
                "displayed_sim_winner": displayed_sim,
                "fixed_prior_1_probability": fixed_probability,
            }
        )
    return {
        "rows": rows,
        "zero_evidence_analytic_limit": 1 / 3,
        "zero_limit_checks": zero_limit_checks,
        "fixed_display_checks": fixed_checks,
        "draws_per_check": STAGE_ZERO_DRAWS,
    }


def panel_grid(
    model: str,
    model_index: int,
    panel: dict[str, object],
) -> dict[str, object]:
    scenarios = []
    for prior_index, prior in enumerate(PRIORS):
        for evidence_index, evidence in enumerate(SIM_EVIDENCE_SIZES):
            scenarios.append(
                evaluate(
                    panel,
                    prior,
                    evidence,
                    N_DRAWS,
                    scenario_seed(model_index, prior_index, evidence_index),
                )
            )
    probabilities = [
        row["probability_sampled_sim_winner_is_sampled_real_best"]
        for row in scenarios
    ]
    first_crossings: dict[str, str | None] = {}
    for prior in PRIORS:
        rows = [row for row in scenarios if row["prior_alpha_beta"] == prior]
        crossing = next(
            (
                row["sim_effective_bernoulli_equivalents_per_policy_task"]
                for row in rows
                if row["probability_sampled_sim_winner_is_sampled_real_best"]
                > 0.5
            ),
            None,
        )
        first_crossings[f"{prior:g}"] = crossing
    candidates = panel["candidates"]
    return {
        "model": model,
        "candidates": candidates,
        "tasks": panel["tasks"],
        "real_successes_of_20": np.asarray(
            panel["real_successes"], dtype=int
        ).tolist(),
        "sim_displayed_rates": np.asarray(
            panel["sim_rates"], dtype=float
        ).tolist(),
        "displayed_real_winner": candidates[
            int(panel["displayed_real_winner_index"])
        ],
        "displayed_sim_winner": candidates[
            int(panel["displayed_sim_winner_index"])
        ],
        "scenarios": scenarios,
        "stress_envelope": {
            "minimum_probability_sampled_winners_match": min(probabilities),
            "maximum_probability_sampled_winners_match": max(probabilities),
            "all_scenarios_below_one_half": all(value < 0.5 for value in probabilities),
            "all_scenarios_above_one_half": all(value > 0.5 for value in probabilities),
            "first_listed_evidence_size_above_one_half_by_prior": first_crossings,
        },
    }


def build() -> dict[str, object]:
    stage_zero = validate_stage_zero()
    panels = load_panels()
    results = {
        model: panel_grid(model, model_index, panels[model])
        for model_index, model in enumerate(sorted(panels))
    }
    return {
        "schema": "wm-missing-simulator-evidence-sensitivity-v1",
        "status": "pass",
        "classification": (
            "common_effective_evidence_changes_latent_winner_concordance"
        ),
        "outcome_status": "review_triggered_outcome_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "input_sha256": sha256(INPUT),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "draws_per_scenario": N_DRAWS,
        "priors": list(PRIORS),
        "sim_effective_evidence_grid": [
            "infinity_fixed_display" if value is None else value
            for value in SIM_EVIDENCE_SIZES
        ],
        "stage_zero": stage_zero,
        "panels": results,
        "scope": (
            "Finite retained WM-PolicyEval panels under independent Beta-binomial "
            "cell sensitivities with one common effective simulator evidence size "
            "for every policy-task cell. The estimand is posterior concordance "
            "between independently sampled latent simulator-best and real-best "
            "policies, not reliability of an observed-data operational action. "
            "With common positive evidence and a symmetric prior, the posterior-"
            "mean simulator action is unchanged because every displayed rate "
            "receives the same positive affine transform. Evidence sizes are not "
            "estimates of the missing simulator denominator and results do not "
            "transport."
        ),
    }


def stable(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def validate(data: dict[str, object]) -> None:
    require(data == stable(build()), "stored WM simulator sensitivity differs")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = stable(build())
    if args.write:
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE {args.out}")
    else:
        validate(json.loads(args.out.read_text(encoding="utf-8")))
        print("OK: WM missing-simulator-evidence sensitivity")


if __name__ == "__main__":
    main()
