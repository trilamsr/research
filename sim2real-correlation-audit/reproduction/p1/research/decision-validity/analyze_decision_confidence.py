#!/usr/bin/env python3
"""Finite-panel robustness and real-trial uncertainty for decision cases.

The subset analysis is deterministic: it enumerates every non-empty subset of
the displayed task/condition blocks and repeats the same equal-block policy
aggregation. The posterior analysis is explicitly model-conditional: each
real policy-block success probability receives an independent Beta(1,1) prior,
then policy performance is the equal-weight mean of its displayed blocks.
Simulation outcomes are held at their displayed values because several papers
do not release simulator trial counts.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "corpus-reporting-audit" / "sources"
DEFAULT_OUT = ROOT / "result-decision-confidence.json"
SEED = 20260723
N_DRAWS = 500_000


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(
            csv.DictReader(
                line
                for line in handle
                if line.strip() and not line.startswith("#")
            )
        )


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def winners(
    points: dict[str, tuple[float | Fraction, float | Fraction]]
) -> tuple[list[str], list[str]]:
    real_max = max(value[0] for value in points.values())
    sim_max = max(value[1] for value in points.values())
    return (
        sorted(key for key, value in points.items() if value[0] == real_max),
        sorted(key for key, value in points.items() if value[1] == sim_max),
    )


def complete_blocks(
    rows: list[dict[str, str]], block: str, candidate: str
) -> list[str]:
    candidates = {row[candidate] for row in rows}
    by_block: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        by_block[row[block]].add(row[candidate])
    return sorted(key for key, labels in by_block.items() if labels == candidates)


def subset_stability(
    rows: list[dict[str, str]],
    block: str,
    candidate: str,
    real: str,
    sim: str,
) -> dict[str, object]:
    blocks = complete_blocks(rows, block, candidate)
    candidates = sorted({row[candidate] for row in rows})
    outcomes = []
    for size in range(1, len(blocks) + 1):
        for subset in itertools.combinations(blocks, size):
            points = {}
            for label in candidates:
                selected = [
                    row
                    for row in rows
                    if row[block] in subset and row[candidate] == label
                ]
                points[label] = (
                    sum(Fraction(row[real]) for row in selected) / len(selected),
                    sum(Fraction(row[sim]) for row in selected) / len(selected),
                )
            real_winners, sim_winners = winners(points)
            possibly_correct = bool(set(real_winners) & set(sim_winners))
            robustly_correct = set(sim_winners).issubset(real_winners)
            outcomes.append(
                {
                    "size": size,
                    "possibly_correct": possibly_correct,
                    "robustly_correct": robustly_correct,
                    "real_winners": tuple(real_winners),
                    "sim_winners": tuple(sim_winners),
                }
            )

    full = next(row for row in outcomes if row["size"] == len(blocks))
    loto = [row for row in outcomes if row["size"] == len(blocks) - 1]
    mismatch_types = Counter(
        ("/".join(row["real_winners"]), "/".join(row["sim_winners"]))
        for row in outcomes
        if not row["possibly_correct"]
    )
    return {
        "n_complete_blocks": len(blocks),
        "n_candidates": len(candidates),
        "full_real_winners": list(full["real_winners"]),
        "full_sim_winners": list(full["sim_winners"]),
        "full_possibly_correct": full["possibly_correct"],
        "full_correct": full["robustly_correct"],
        "leave_one_block_out_possibly_correct": sum(
            row["possibly_correct"] for row in loto
        ),
        "leave_one_block_out_correct": sum(
            row["robustly_correct"] for row in loto
        ),
        "leave_one_block_out_total": len(loto),
        "all_nonempty_subsets_possibly_correct": sum(
            row["possibly_correct"] for row in outcomes
        ),
        "all_nonempty_subsets_correct": sum(
            row["robustly_correct"] for row in outcomes
        ),
        "all_nonempty_subsets_total": len(outcomes),
        "mismatch_types": {
            f"real={key[0]}|sim={key[1]}": value
            for key, value in sorted(mismatch_types.items())
        },
    }


def posterior_real_selection(
    cells: dict[str, list[tuple[float, float]]],
    displayed_sim_winners: list[str],
    rng: np.random.Generator,
) -> dict[str, object]:
    """Cells map candidate to [(successes, trials), ...]."""
    labels = sorted(cells)
    sampled_means = []
    for label in labels:
        draws = [
            rng.beta(successes + 1.0, trials - successes + 1.0, N_DRAWS)
            for successes, trials in cells[label]
        ]
        sampled_means.append(np.mean(np.stack(draws), axis=0))
    matrix = np.stack(sampled_means, axis=1)
    best = np.argmax(matrix, axis=1)
    selected_indices = [labels.index(label) for label in displayed_sim_winners]
    selected_best = np.isin(best, selected_indices)
    best_real = np.max(matrix, axis=1)
    selected_real = np.max(matrix[:, selected_indices], axis=1)
    probability = float(np.mean(selected_best))
    candidate_probabilities = {
        label: float(np.mean(best == index))
        for index, label in enumerate(labels)
    }
    return {
        "model": (
            "Independent Beta(1,1) policy-block success probabilities; "
            "equal displayed-block mean within candidate; displayed simulator "
            "winner held fixed."
        ),
        "seed": SEED,
        "draws": N_DRAWS,
        "displayed_sim_winners": displayed_sim_winners,
        "posterior_probability_sim_winner_is_real_best": probability,
        "monte_carlo_se": math.sqrt(
            probability * (1.0 - probability) / N_DRAWS
        ),
        "posterior_real_winner_probabilities": candidate_probabilities,
        "posterior_expected_real_regret": float(
            np.mean(best_real - selected_real)
        ),
        "posterior_probability_positive_real_regret": float(
            np.mean(best_real > selected_real)
        ),
    }


def real2sim_mean_posteriors(rng: np.random.Generator) -> dict[str, object]:
    rows = read_csv("source-real2sim-eval-fig3-checkpoints.csv")
    output = {}
    for task in sorted({row["task"] for row in rows}):
        selected = [row for row in rows if row["task"] == task]
        by_policy: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in selected:
            by_policy[row["policy"]].append(row)
        sim_means = {
            policy: mean(
                [
                    float(row["sim_successes"]) / float(row["n_episodes"])
                    for row in policy_rows
                ]
            )
            for policy, policy_rows in by_policy.items()
        }
        max_sim = max(sim_means.values())
        sim_winners = sorted(
            label for label, value in sim_means.items() if value == max_sim
        )
        cells = {
            policy: [
                (float(row["real_successes"]), float(row["n_episodes"]))
                for row in policy_rows
            ]
            for policy, policy_rows in by_policy.items()
        }
        output[task] = posterior_real_selection(cells, sim_winners, rng)
    return output


def wm_posteriors(rng: np.random.Generator) -> dict[str, object]:
    rows = read_csv("source-wm-policyeval.csv")
    output = {}
    for model in sorted({row["world_model"] for row in rows}):
        selected = [row for row in rows if row["world_model"] == model]
        sim_means: dict[str, list[float]] = defaultdict(list)
        cells: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for row in selected:
            sim_means[row["policy"]].append(
                float(row["predicted_success_rate"])
            )
            cells[row["policy"]].append(
                (20.0 * float(row["actual_success_rate"]), 20.0)
            )
        averaged = {key: mean(value) for key, value in sim_means.items()}
        maximum = max(averaged.values())
        sim_winners = sorted(
            key for key, value in averaged.items() if value == maximum
        )
        output[model] = posterior_real_selection(
            dict(cells), sim_winners, rng
        )
    return output


def cosmos_posteriors(rng: np.random.Generator) -> dict[str, object]:
    rows = read_csv("source-cosmos-surg-dvrk.csv")
    output = {}
    for panel in sorted({row["panel"] for row in rows}):
        selected = [row for row in rows if row["panel"] == panel]
        sim_means: dict[str, list[float]] = defaultdict(list)
        cells: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for row in selected:
            sim_means[row["policy"]].append(float(row["y_sim_descaled"]))
            cells[row["policy"]].append(
                (10.0 * float(row["x_real_descaled"]), 10.0)
            )
        averaged = {key: mean(value) for key, value in sim_means.items()}
        maximum = max(averaged.values())
        sim_winners = sorted(
            key for key, value in averaged.items() if value == maximum
        )
        output[panel] = posterior_real_selection(
            dict(cells), sim_winners, rng
        )
    return output


def subset_cases() -> dict[str, object]:
    cases = {}

    simpler = read_csv("source-simpler-decisions.csv")
    for embodiment in sorted({row["embodiment"] for row in simpler}):
        cases[f"SIMPLER/{embodiment}"] = subset_stability(
            [row for row in simpler if row["embodiment"] == embodiment],
            "task",
            "policy",
            "real_success",
            "sim_success",
        )

    cases["WorldGym"] = subset_stability(
        read_csv("source-worldgym-decisions.csv"),
        "task",
        "policy",
        "real_successes",
        "sim_successes",
    )
    cases["WorldEval"] = subset_stability(
        read_csv("source-worldeval.csv"),
        "task",
        "policy",
        "real_success",
        "generated_success",
    )
    cases["Digital Cousins"] = subset_stability(
        read_csv("source-digital-cousins.csv"),
        "generalization_level",
        "policy",
        "x_real",
        "y_sim",
    )
    cases["Hi-WM"] = subset_stability(
        read_csv("source-hi-wm.csv"),
        "task",
        "policy",
        "real_success_rate",
        "generated_success_rate",
    )

    wm = read_csv("source-wm-policyeval.csv")
    for model in sorted({row["world_model"] for row in wm}):
        cases[f"WM-PolicyEval/{model}"] = subset_stability(
            [row for row in wm if row["world_model"] == model],
            "task",
            "policy",
            "actual_success_rate",
            "predicted_success_rate",
        )

    cosmos = read_csv("source-cosmos-surg-dvrk.csv")
    for panel in sorted({row["panel"] for row in cosmos}):
        cases[f"Cosmos-Surg-dVRK/{panel}"] = subset_stability(
            [row for row in cosmos if row["panel"] == panel],
            "task",
            "policy",
            "x_real_descaled",
            "y_sim_descaled",
        )

    weaver = read_csv("source-weaver.csv")
    for panel in sorted({row["panel"] for row in weaver}):
        cases[f"WEAVER/{panel}"] = subset_stability(
            [row for row in weaver if row["panel"] == panel],
            "task",
            "policy",
            "real_sr",
            "wm_sr",
        )
    return cases


def stable_numbers(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable_numbers(item) for item in value]
    return value


def main(out: Path = DEFAULT_OUT) -> None:
    rng = np.random.default_rng(SEED)
    result = {
        "scope": {
            "subset_analysis": (
                "Exact sensitivity over every non-empty subset of complete "
                "displayed task/condition blocks; not a sampling probability."
            ),
            "posterior_analysis": (
                "Model-conditional real-trial measurement uncertainty for "
                "cases with documented real denominators; simulator values "
                "held fixed where simulator rollout counts are unavailable."
            ),
        },
        "subset_stability": subset_cases(),
        "real_trial_posterior": {
            "Real2Sim/mean_rule": real2sim_mean_posteriors(rng),
            "WM-PolicyEval": wm_posteriors(rng),
            "Cosmos-Surg-dVRK": cosmos_posteriors(rng),
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(stable_numbers(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    main(args.out)
