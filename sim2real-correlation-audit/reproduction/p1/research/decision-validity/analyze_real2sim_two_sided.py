#!/usr/bin/env python3
"""Two-sided remeasurement of the Real2Sim T-block mean rule.

Figure 3 values quantize exactly to integer counts out of 16 episodes per
checkpoint. This analysis samples both real and simulator cell rates, then
recomputes equal-checkpoint policy means and winners. Evidence discounting
stresses unreleased episode pairing and repeat structure; it is not a fitted
dependence model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "corpus-reporting-audit" / "sources"
DEFAULT_OUT = ROOT / "result-real2sim-two-sided.json"
SEED = 20260724
N_DRAWS = 300_000
PRIORS = (0.5, 1.0, 2.0)
EVIDENCE_FRACTIONS = (0.25, 0.5, 1.0)


def load_cells() -> dict[str, list[tuple[float, float, float]]]:
    path = DATA / "source-real2sim-eval-fig3-checkpoints.csv"
    with path.open(encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(
                line
                for line in handle
                if line.strip() and not line.startswith("#")
            )
            if row["task"] == "T"
        ]
    cells: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for row in rows:
        cells[row["policy"]].append(
            (
                float(row["real_successes"]),
                float(row["sim_successes"]),
                float(row["n_episodes"]),
            )
        )
    return dict(cells)


def candidate_means(
    observations: list[tuple[float, float, float]],
    side: int,
    prior: float,
    evidence_fraction: float,
    rng: np.random.Generator,
) -> np.ndarray:
    successes = np.array([row[side] for row in observations])
    trials = np.array([row[2] for row in observations])
    draws = rng.beta(
        evidence_fraction * successes + prior,
        evidence_fraction * (trials - successes) + prior,
        size=(N_DRAWS, len(observations)),
    )
    return np.mean(draws, axis=1)


def evaluate(
    prior: float,
    evidence_fraction: float,
    rng: np.random.Generator,
) -> dict[str, object]:
    cells = load_cells()
    labels = sorted(cells)
    real = np.column_stack(
        [
            candidate_means(
                cells[label], 0, prior, evidence_fraction, rng
            )
            for label in labels
        ]
    )
    sim = np.column_stack(
        [
            candidate_means(
                cells[label], 1, prior, evidence_fraction, rng
            )
            for label in labels
        ]
    )
    real_best = np.argmax(real, axis=1)
    sim_best = np.argmax(sim, axis=1)
    rows = np.arange(N_DRAWS)
    regret = np.max(real, axis=1) - real[rows, sim_best]
    displayed_real = labels.index("dp")
    displayed_sim = labels.index("pi0")
    match = real_best == sim_best
    probability = float(np.mean(match))
    return {
        "prior_alpha_beta": prior,
        "nominal_evidence_fraction_both_sides": evidence_fraction,
        "effective_episode_equivalents_per_checkpoint": (
            16.0 * evidence_fraction
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
    cells = load_cells()
    rng = np.random.default_rng(SEED)
    scenarios = [
        evaluate(prior, fraction, rng)
        for prior in PRIORS
        for fraction in EVIDENCE_FRACTIONS
    ]
    probabilities = [
        row["probability_sampled_sim_winner_is_sampled_real_best"]
        for row in scenarios
    ]
    return {
        "scope": {
            "source": (
                "Vector-recovered Figure 3 T-block integer real/sim counts, "
                "16 episodes per checkpoint."
            ),
            "model": (
                "Independent binomial checkpoint likelihoods with Beta priors; equal "
                "checkpoint mean within policy; both sides sampled."
            ),
            "boundary": (
                "Episode pairing, checkpoint dependence, and training-run "
                "structure are unreleased. Evidence discounting is a stress "
                "device, not an estimated effective sample size."
            ),
        },
        "seed": SEED,
        "draws_per_scenario": N_DRAWS,
        "checkpoint_counts_by_policy": {
            label: len(observations)
            for label, observations in sorted(cells.items())
        },
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
