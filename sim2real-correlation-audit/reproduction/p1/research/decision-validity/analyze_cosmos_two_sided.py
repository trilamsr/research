#!/usr/bin/env python3
"""Two-sided finite-panel remeasurement for Cosmos-Surg manual evaluation.

The official project page identifies 10 initial states per policy-task, three
Cosmos seeds per state, and two raters per generated rollout. Published
aggregate rates therefore encode 60 binary labels per policy-task, but the
individual seed/rater/state allocation is unavailable. We stress effective
simulator evidence from 60 labels down to 10 initial-state equivalents.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "corpus-reporting-audit" / "sources"
DEFAULT_OUT = ROOT / "result-cosmos-two-sided.json"
SEED = 20260724
N_DRAWS = 300_000
PRIORS = (0.5, 1.0, 2.0)
SIM_EVIDENCE_FRACTIONS = (1.0 / 6.0, 0.5, 1.0)


def read_rows() -> list[dict[str, str]]:
    path = DATA / "source-cosmos-surg-dvrk.csv"
    with path.open(encoding="utf-8") as handle:
        return [
            row
            for row in csv.DictReader(
                line
                for line in handle
                if line.strip() and not line.startswith("#")
            )
            if row["panel"] == "manual_human_vs_dvrk"
        ]


def load_counts():
    rows = read_rows()
    candidates = sorted({row["policy"] for row in rows})
    tasks = sorted({row["task"] for row in rows})
    cells = {(row["policy"], row["task"]): row for row in rows}
    real_successes = np.array(
        [
            [
                round(10.0 * float(cells[(candidate, task)][
                    "x_real_descaled"
                ]))
                for task in tasks
            ]
            for candidate in candidates
        ],
        dtype=float,
    )
    sim_successes = np.array(
        [
            [
                round(60.0 * float(cells[(candidate, task)][
                    "y_sim_descaled"
                ]))
                for task in tasks
            ]
            for candidate in candidates
        ],
        dtype=float,
    )
    return candidates, tasks, real_successes, sim_successes


def evaluate(
    prior: float,
    sim_evidence_fraction: float,
    rng: np.random.Generator,
) -> dict[str, object]:
    candidates, _, real_successes, sim_successes = load_counts()
    real = rng.beta(
        real_successes + prior,
        10.0 - real_successes + prior,
        size=(N_DRAWS,) + real_successes.shape,
    ).mean(axis=2)
    sim = rng.beta(
        sim_evidence_fraction * sim_successes + prior,
        sim_evidence_fraction * (60.0 - sim_successes) + prior,
        size=(N_DRAWS,) + sim_successes.shape,
    ).mean(axis=2)
    real_best = np.argmax(real, axis=1)
    sim_best = np.argmax(sim, axis=1)
    rows = np.arange(N_DRAWS)
    regret = np.max(real, axis=1) - real[rows, sim_best]
    match = real_best == sim_best
    displayed_real = candidates.index("GR00T N1 20k")
    displayed_sim = candidates.index("GR00T N1.5 50k")
    probability = float(np.mean(match))
    return {
        "prior_alpha_beta": prior,
        "sim_nominal_label_evidence_fraction": sim_evidence_fraction,
        "sim_effective_binary_label_equivalents_per_policy_task": (
            60.0 * sim_evidence_fraction
        ),
        "probability_sampled_sim_winner_is_sampled_real_best": probability,
        "monte_carlo_se": math.sqrt(
            probability * (1.0 - probability) / N_DRAWS
        ),
        "probability_displayed_sim_winner_remains_sim_best": float(
            np.mean(sim_best == displayed_sim)
        ),
        "probability_displayed_real_winner_remains_real_best": float(
            np.mean(real_best == displayed_real)
        ),
        "probability_displayed_mismatch_pair": float(
            np.mean(
                (sim_best == displayed_sim) & (real_best == displayed_real)
            )
        ),
        "expected_real_regret_of_sampled_sim_winner": float(np.mean(regret)),
        "probability_positive_real_regret": float(np.mean(regret > 0)),
    }


def stable(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def build_results() -> dict[str, object]:
    candidates, tasks, real_successes, sim_successes = load_counts()
    rng = np.random.default_rng(SEED)
    scenarios = [
        evaluate(prior, fraction, rng)
        for prior in PRIORS
        for fraction in SIM_EVIDENCE_FRACTIONS
    ]
    probabilities = [
        row["probability_sampled_sim_winner_is_sampled_real_best"]
        for row in scenarios
    ]
    return {
        "scope": {
            "source_structure": (
                "10 real initial states per policy-task; three Cosmos seeds "
                "per initial state; two manual raters per generated rollout."
            ),
            "model": (
                "Independent binomial cell likelihoods with Beta priors and equal task "
                "weighting. Simulator evidence is discounted from 60 labels "
                "to 30 rollout or 10 initial-state equivalents."
            ),
            "boundary": (
                "Aggregate rates do not reveal the rater/seed/state allocation "
                "or dependence, so evidence fractions are sensitivity devices."
            ),
        },
        "seed": SEED,
        "draws_per_scenario": N_DRAWS,
        "candidates": candidates,
        "tasks": tasks,
        "real_successes_of_10": real_successes.astype(int).tolist(),
        "sim_success_labels_of_60": sim_successes.astype(int).tolist(),
        "scenarios": scenarios,
        "stress_envelope": {
            "minimum_probability_sampled_winners_match": min(probabilities),
            "maximum_probability_sampled_winners_match": max(probabilities),
            "all_scenarios_below_one_half": all(
                probability < 0.5 for probability in probabilities
            ),
        },
    }


def main(out: Path = DEFAULT_OUT) -> None:
    out.write_text(
        json.dumps(stable(build_results()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    arguments = parser.parse_args()
    main(arguments.out)
