#!/usr/bin/env python3
"""Independent stdlib-only reconstruction of the headline decision atlas.

This program intentionally does not import any project analysis module, NumPy,
SciPy, or a committed intermediate JSON. It starts from the source-traced CSVs,
implements its own aggregation, Pearson correlation, winner, regret, and task
subset logic, and writes a compact comparison target.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "corpus-reporting-audit" / "sources"


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return math.fsum(values) / len(values)


def pearson(real: list[float], simulated: list[float]) -> float:
    if len(real) != len(simulated) or len(real) < 2:
        raise ValueError("Pearson inputs must have equal length of at least two")
    real_mean = mean(real)
    sim_mean = mean(simulated)
    cross = math.fsum(
        (real_value - real_mean) * (sim_value - sim_mean)
        for real_value, sim_value in zip(real, simulated)
    )
    real_ss = math.fsum((value - real_mean) ** 2 for value in real)
    sim_ss = math.fsum((value - sim_mean) ** 2 for value in simulated)
    return cross / math.sqrt(real_ss * sim_ss)


def winner_set(values: dict[str, float], tolerance: float = 1e-12) -> list[str]:
    maximum = max(values.values())
    return sorted(
        candidate
        for candidate, value in values.items()
        if math.isclose(value, maximum, rel_tol=0.0, abs_tol=tolerance)
    )


def aggregate_rows(
    rows: list[dict[str, str]],
    *,
    candidate_key: str,
    block_key: str,
    real_key: str,
    sim_key: str,
    kept_blocks: set[str] | None = None,
) -> dict[str, object]:
    grouped: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"real": [], "sim": []}
    )
    seen_blocks: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        block = row[block_key]
        if kept_blocks is not None and block not in kept_blocks:
            continue
        candidate = row[candidate_key]
        grouped[candidate]["real"].append(float(row[real_key]))
        grouped[candidate]["sim"].append(float(row[sim_key]))
        seen_blocks[candidate].add(block)

    if not grouped:
        raise ValueError("aggregation selected no rows")
    block_counts = {len(value) for value in seen_blocks.values()}
    if len(block_counts) != 1:
        raise ValueError("candidate block coverage is incomplete")

    real = {
        candidate: mean(values["real"]) for candidate, values in grouped.items()
    }
    simulated = {
        candidate: mean(values["sim"]) for candidate, values in grouped.items()
    }
    candidates = sorted(grouped)
    real_winners = winner_set(real)
    sim_winners = winner_set(simulated)
    best_real = max(real.values())
    regrets = [best_real - real[candidate] for candidate in sim_winners]
    sim_order = sorted(candidates, key=lambda candidate: -simulated[candidate])
    minimum_top_k = min(
        index + 1
        for index, candidate in enumerate(sim_order)
        if candidate in real_winners
    )
    ordered_sim = sorted(simulated.values(), reverse=True)
    sim_margin = (
        ordered_sim[0] - ordered_sim[1]
        if len(ordered_sim) > 1
        else float("inf")
    )
    best_real_winner_sim_score = max(
        simulated[candidate] for candidate in real_winners
    )
    real_winner_sim_gap = max(simulated.values()) - best_real_winner_sim_score
    return {
        "pearson_r": pearson(
            [real[candidate] for candidate in candidates],
            [simulated[candidate] for candidate in candidates],
        ),
        "real_winners": real_winners,
        "sim_winners": sim_winners,
        "robustly_correct": set(sim_winners).issubset(real_winners),
        "real_regret_min": min(regrets),
        "real_regret_max": max(regrets),
        "minimum_sim_top_k_covering_a_real_winner": minimum_top_k,
        "real_scores": {candidate: real[candidate] for candidate in candidates},
        "sim_scores": {
            candidate: simulated[candidate] for candidate in candidates
        },
        "sim_top_to_runner_up_margin": sim_margin,
        "symmetric_per_score_perturbation_to_change_sim_winner": (
            sim_margin / 2.0
        ),
        "symmetric_per_score_perturbation_for_real_winner_to_tie_sim_top": (
            real_winner_sim_gap / 2.0
        ),
        "n_candidates": len(candidates),
        "n_blocks": block_counts.pop(),
    }


def subset_stability(
    rows: list[dict[str, str]],
    *,
    candidate_key: str,
    block_key: str,
    real_key: str,
    sim_key: str,
) -> dict[str, int]:
    blocks = sorted({row[block_key] for row in rows})
    correct = 0
    possibly_correct = 0
    total = 0
    loto_correct = 0
    loto_possibly_correct = 0
    for size in range(1, len(blocks) + 1):
        for combination in itertools.combinations(blocks, size):
            decision = aggregate_rows(
                rows,
                candidate_key=candidate_key,
                block_key=block_key,
                real_key=real_key,
                sim_key=sim_key,
                kept_blocks=set(combination),
            )
            total += 1
            correct += int(decision["robustly_correct"])
            possible = bool(
                set(decision["real_winners"]) & set(decision["sim_winners"])
            )
            possibly_correct += int(possible)
            if size == len(blocks) - 1:
                loto_correct += int(decision["robustly_correct"])
                loto_possibly_correct += int(possible)
    return {
        "all_nonempty_subsets_possibly_correct": possibly_correct,
        "all_nonempty_subsets_correct": correct,
        "all_nonempty_subsets_total": total,
        "leave_one_block_out_possibly_correct": loto_possibly_correct,
        "leave_one_block_out_correct": loto_correct,
        "leave_one_block_out_total": len(blocks),
    }


def case(
    rows: list[dict[str, str]],
    *,
    candidate_key: str,
    block_key: str,
    real_key: str,
    sim_key: str,
    regret_scale: float,
    include_subsets: bool,
) -> dict[str, object]:
    decision = aggregate_rows(
        rows,
        candidate_key=candidate_key,
        block_key=block_key,
        real_key=real_key,
        sim_key=sim_key,
    )
    output = {
        **decision,
        "displayed_real_regret_pp": decision["real_regret_max"] * regret_scale,
    }
    output["meets_displayed_real_regret_tolerance"] = {
        f"{threshold:g}_pp": output["displayed_real_regret_pp"] <= threshold
        for threshold in (1.0, 5.0, 10.0)
    }
    for key in (
        "sim_top_to_runner_up_margin",
        "symmetric_per_score_perturbation_to_change_sim_winner",
        "symmetric_per_score_perturbation_for_real_winner_to_tie_sim_top",
    ):
        output[f"{key}_pp"] = decision[key] * regret_scale
    if include_subsets:
        output["subset_stability"] = subset_stability(
            rows,
            candidate_key=candidate_key,
            block_key=block_key,
            real_key=real_key,
            sim_key=sim_key,
        )
    return output


def real2sim_best_sim_case(rows: list[dict[str, str]]) -> dict[str, object]:
    """Enumerate simulator-max checkpoint ties without using real outcomes."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["policy"]].append(row)
    tied_best = {}
    for policy, policy_rows in grouped.items():
        maximum = max(float(row["sim_success"]) for row in policy_rows)
        tied_best[policy] = [
            row
            for row in policy_rows
            if math.isclose(
                float(row["sim_success"]), maximum, rel_tol=0.0, abs_tol=1e-12
            )
        ]
    decisions = []
    policies = sorted(tied_best)
    for selection in itertools.product(*(tied_best[name] for name in policies)):
        decisions.append(
            case(
                list(selection),
                candidate_key="policy",
                block_key="policy",
                real_key="real_success",
                sim_key="sim_success",
                regret_scale=1.0,
                include_subsets=False,
            )
        )
    reference = max(decisions, key=lambda value: value["pearson_r"])
    for value in decisions:
        for key in (
            "real_winners",
            "sim_winners",
            "robustly_correct",
            "displayed_real_regret_pp",
        ):
            if value[key] != reference[key]:
                raise ValueError(f"Real2Sim T best-sim conclusion varies at {key}")
    return {
        **reference,
        "pearson_r_min": min(value["pearson_r"] for value in decisions),
        "pearson_r_max": max(value["pearson_r"] for value in decisions),
        "checkpoint_tie_combinations": len(decisions),
    }


def build_results() -> dict[str, object]:
    worldgym = read_csv("source-worldgym-decisions.csv")
    digital_cousins = read_csv("source-digital-cousins.csv")
    simpler = [
        row
        for row in read_csv("source-simpler-decisions.csv")
        if row["embodiment"] == "google_robot"
    ]
    real2sim_t = [
        row
        for row in read_csv("source-real2sim-eval-fig3-checkpoints.csv")
        if row["task"] == "T"
    ]
    oscar = read_csv("source-oscar.csv")
    cosmos_manual = [
        row
        for row in read_csv("source-cosmos-surg-dvrk.csv")
        if row["panel"] == "manual_human_vs_dvrk"
    ]
    wm_rows = read_csv("source-wm-policyeval.csv")

    cases = {
        "WorldGym": case(
            worldgym,
            candidate_key="policy",
            block_key="task",
            real_key="real_successes",
            sim_key="sim_successes",
            regret_scale=10.0,
            include_subsets=True,
        ),
        "Digital Cousins": case(
            digital_cousins,
            candidate_key="policy",
            block_key="generalization_level",
            real_key="x_real",
            sim_key="y_sim",
            regret_scale=1.0,
            include_subsets=True,
        ),
        "SIMPLER Google": case(
            simpler,
            candidate_key="policy",
            block_key="task",
            real_key="real_success",
            sim_key="sim_success",
            regret_scale=100.0,
            include_subsets=True,
        ),
        "Real2Sim T best-sim checkpoint": real2sim_best_sim_case(real2sim_t),
        "OSCAR Skeleton": case(
            oscar,
            candidate_key="policy",
            block_key="policy",
            real_key="real_sr_pct",
            sim_key="wm_sr_pct",
            regret_scale=1.0,
            include_subsets=False,
        ),
        "Cosmos-Surg manual": case(
            cosmos_manual,
            candidate_key="policy",
            block_key="task",
            real_key="x_real_descaled",
            sim_key="y_sim_descaled",
            regret_scale=100.0,
            include_subsets=True,
        ),
        "WM-PolicyEval / Cosmos": case(
            [row for row in wm_rows if row["world_model"] == "Cosmos"],
            candidate_key="policy",
            block_key="task",
            real_key="actual_success_rate",
            sim_key="predicted_success_rate",
            regret_scale=100.0,
            include_subsets=True,
        ),
        "WM-PolicyEval / IRASim": case(
            [row for row in wm_rows if row["world_model"] == "IRASim"],
            candidate_key="policy",
            block_key="task",
            real_key="actual_success_rate",
            sim_key="predicted_success_rate",
            regret_scale=100.0,
            include_subsets=True,
        ),
    }
    return {
        "schema_version": 1,
        "method": (
            "Independent stdlib-only reconstruction from source-traced CSVs; "
            "no project analysis imports or committed intermediate JSON."
        ),
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=HERE / "result-independent-decision-audit.json",
    )
    args = parser.parse_args()
    result = build_results()
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
