#!/usr/bin/env python3
"""Regenerate the quantitative facts selected for the clean-room rewrite.

This is deliberately narrower than the legacy manuscript. It produces:

* consensus survey/estimand facts;
* the two explicit unit-count sensitivity codings;
* axis-specific permutation resolution for the five p-value papers;
* the declared 28-row illustrative leave-one-unit/point supplement table;
* checkpoint-selection sensitivity with ties enumerated;
* an inventory-derived complete direct-cell matrix ledger and an illustrative
  cross-source decision atlas;
* exact task-subset stability and model-conditional real-trial remeasurement;
* the four-row MMRV stability supplement table; and
* the Real2Sim MMRV convention reproduction.

The JSON is the machine-readable source of truth. The Markdown supplement is
rendered from the same in-memory results, so the two cannot silently diverge.
No source-paper experiment is rerun here; computations begin from the released
audit CSVs and their documented extraction gates.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from math import factorial
from pathlib import Path
from typing import Callable

FAMILY_ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = FAMILY_ROOT.parent
PROJECT_ROOT = FAMILY_ROOT.parents[1]
CORPUS_ROOT = RESEARCH_ROOT / "corpus-reporting-audit"
REAL2SIM_ROOT = RESEARCH_ROOT / "real2sim-noise-floor"
DECISION_ROOT = RESEARCH_ROOT / "decision-validity"
PROSPECT_ROOT = RESEARCH_ROOT / "prospective-study-design"
for module_root in (CORPUS_ROOT, REAL2SIM_ROOT):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

import numpy as np
from scipy.stats import spearmanr

import compare_estimand_codings as coding_compare
import analyze_bayesian_interval
import audit_estimands
import audit_mmrv_conventions
from summarize_corpus import EXCLUDED, SURVEY


ROOT = FAMILY_ROOT
DATA = CORPUS_ROOT / "sources"
SCHEMA_VERSION = 4


def rows(name: str) -> list[dict[str, str]]:
    return read_rows(DATA / name)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def pearson(x: list[float], y: list[float]) -> float:
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def correlation(points: list[tuple[float, float]], rank: bool = False) -> float:
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return float(spearmanr(x, y).statistic) if rank else pearson(x, y)


def drop_one(
    points: list[tuple[float, float]], units: list[str], rank: bool = False
) -> tuple[float, float, list[float]]:
    full = correlation(points, rank=rank)
    dropped = []
    for unit in dict.fromkeys(units):
        kept = [point for point, label in zip(points, units) if label != unit]
        if len(kept) < 2:
            raise ValueError(f"dropping {unit!r} leaves fewer than two points")
        dropped.append(correlation(kept, rank=rank))
    return full, max(abs(value - full) for value in dropped), dropped


@dataclass(frozen=True)
class LeverageSpec:
    label: str
    filename: str
    predicate: Callable[[dict[str, str]], bool]
    x: str
    y: str
    unit: str | None
    unit_label: str


def eq(column: str, value: str) -> Callable[[dict[str, str]], bool]:
    return lambda row: row[column] == value


LEVERAGE_SPECS = [
    LeverageSpec("real2sim-eval toy", "source-real2sim-eval-fig3-checkpoints.csv",
                 eq("task", "sloth"), "real_success", "sim_success", "policy", "policy"),
    LeverageSpec("real2sim-eval rope", "source-real2sim-eval-fig3-checkpoints.csv",
                 eq("task", "rope"), "real_success", "sim_success", "policy", "policy"),
    LeverageSpec("real2sim-eval T-block", "source-real2sim-eval-fig3-checkpoints.csv",
                 eq("task", "T"), "real_success", "sim_success", "policy", "policy"),
    LeverageSpec("RoboWorld 10a", "source-roboworld.csv",
                 eq("panel", "10a_GPT-4o_success_rate"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("RoboWorld 10b", "source-roboworld.csv",
                 eq("panel", "10b_Gemini-2.5-Flash_success_rate"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("RoboWorld 9a", "source-roboworld.csv",
                 eq("panel", "9a_GPT-4o_score"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("RoboWorld 9b", "source-roboworld.csv",
                 eq("panel", "9b_Gemini-2.5-Flash_score"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("Digital Cousins (unit = policy)", "source-digital-cousins.csv",
                 lambda row: True, "x_real", "y_sim", "policy", "policy"),
    LeverageSpec("Digital Cousins (unit = gen. level)", "source-digital-cousins.csv",
                 lambda row: True, "x_real", "y_sim", "generalization_level", "generalization level"),
    LeverageSpec("Cosmos-Surg-dVRK automated", "source-cosmos-surg-dvrk.csv",
                 eq("panel", "automated_fig1b"), "x_real", "y_sim", "unit", "policy run"),
    LeverageSpec("Cosmos-Surg-dVRK manual", "source-cosmos-surg-dvrk.csv",
                 eq("panel", "manual_human_vs_dvrk"), "x_real", "y_sim", "unit", "policy run"),
    LeverageSpec("DreamDojo", "source-dreamdojo.csv",
                 lambda row: True, "x_real", "y_sim", None, "point"),
    LeverageSpec("MolmoSpaces pick", "source-molmospaces.csv",
                 lambda row: row["task"] == "pick" and row["source_panel"] == "main_fig",
                 "sim_success_pct", "real_success_pct", None, "point"),
    LeverageSpec("MolmoSpaces open", "source-molmospaces.csv",
                 eq("task", "open"), "sim_success_pct", "real_success_pct", None, "point"),
    LeverageSpec("MolmoSpaces close", "source-molmospaces.csv",
                 eq("task", "close"), "sim_success_pct", "real_success_pct", None, "point"),
    LeverageSpec("REALM Overall", "source-realm.csv",
                 eq("panel", "Overall"), "x_real", "y_sim", "policy", "policy"),
    LeverageSpec("REALM Default", "source-realm.csv",
                 eq("panel", "Default"), "x_real", "y_sim", "policy", "policy"),
    LeverageSpec("REALM VB-POSE", "source-realm.csv",
                 eq("panel", "VB-POSE"), "x_real", "y_sim", "policy", "policy"),
    LeverageSpec("REALM V-VIEW", "source-realm.csv",
                 eq("panel", "V-VIEW"), "x_real", "y_sim", "policy", "policy"),
    LeverageSpec("subject paper toy, 200 episodes", "source-real2sim-eval-fig9-200ep.csv",
                 eq("panel", "toy_packing"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("subject paper rope, 200 episodes", "source-real2sim-eval-fig9-200ep.csv",
                 eq("panel", "rope_routing"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("subject paper T-block, 200 episodes", "source-real2sim-eval-fig9-200ep.csv",
                 eq("panel", "t_block_pushing"), "x_real", "y_sim", "series", "policy"),
    LeverageSpec("VISER Octo", "source-viser.csv",
                 eq("policy", "Octo"), "real_sr", "sim_ours_sr", None, "point"),
    LeverageSpec("VISER OpenVLA", "source-viser.csv",
                 eq("policy", "OpenVLA"), "real_sr", "sim_ours_sr", None, "point"),
    LeverageSpec("OSCAR", "source-oscar.csv",
                 lambda row: True, "real_sr_pct", "wm_sr_pct", None, "point"),
    LeverageSpec("Hi-WM", "source-hi-wm.csv",
                 lambda row: True, "real_success_rate", "generated_success_rate", None, "point"),
    LeverageSpec("WM-PolicyEval Cosmos", "source-wm-policyeval.csv",
                 eq("world_model", "Cosmos"), "actual_success_rate", "predicted_success_rate", None, "point"),
    LeverageSpec("WM-PolicyEval IRASim", "source-wm-policyeval.csv",
                 eq("world_model", "IRASim"), "actual_success_rate", "predicted_success_rate", None, "point"),
]


def leverage_table() -> list[dict[str, object]]:
    output = []
    for spec in LEVERAGE_SPECS:
        selected = [row for row in rows(spec.filename) if spec.predicate(row)]
        points = [(float(row[spec.x]), float(row[spec.y])) for row in selected]
        units = (
            [row[spec.unit] for row in selected]
            if spec.unit is not None
            else [str(index) for index in range(len(selected))]
        )
        r, max_dr, dropped = drop_one(points, units)
        rho, max_drho, _ = drop_one(points, units, rank=True)
        ordered_units = list(dict.fromkeys(units))
        worst_index = int(np.argmax([abs(value - r) for value in dropped]))
        output.append(
            {
                "dataset": spec.label,
                "n_points": len(points),
                "n_units": len(set(units)),
                "deletion_unit": spec.unit_label,
                "r": r,
                "max_abs_delta_r": max_dr,
                "drop_r_min": min(dropped),
                "drop_r_max": max(dropped),
                "max_abs_delta_unit": ordered_units[worst_index],
                "r_after_max_delta_deletion": dropped[worst_index],
                "spearman_rho": rho,
                "max_abs_delta_spearman": max_drho,
            }
        )
    return output


def mmrv(points: list[tuple[float, float]]) -> float:
    """SIMPLER convention: strict-> XOR, real-side gap, max then mean over N."""
    contributions = []
    for i, (real_i, sim_i) in enumerate(points):
        gaps = [
            abs(real_i - real_j)
            for j, (real_j, sim_j) in enumerate(points)
            if i != j and ((real_i > real_j) != (sim_i > sim_j))
        ]
        contributions.append(max(gaps, default=0.0))
    return sum(contributions) / len(contributions)


def metric_stability(
    label: str, points: list[tuple[float, float]], units: list[str]
) -> dict[str, object]:
    full_r = correlation(points)
    full_mmrv = mmrv(points)
    drop_r, drop_m = [], []
    for unit in dict.fromkeys(units):
        kept = [point for point, group in zip(points, units) if group != unit]
        drop_r.append(correlation(kept))
        drop_m.append(mmrv(kept))
    abs_r_swing = max(drop_r) - min(drop_r)
    abs_m_swing = max(drop_m) - min(drop_m)
    return {
        "dataset": label,
        "n_units": len(set(units)),
        "r": full_r,
        "mmrv": full_mmrv,
        "absolute_r_range": abs_r_swing,
        "absolute_mmrv_range": abs_m_swing,
        "relative_r_swing": abs_r_swing / abs(full_r),
        "relative_mmrv_swing": abs_m_swing / abs(full_mmrv),
        "relative_swing_ratio": (abs_m_swing / abs(full_mmrv)) / (abs_r_swing / abs(full_r)),
    }


def mmrv_stability_table() -> list[dict[str, object]]:
    dc = rows("source-digital-cousins.csv")
    dc_points = [(float(row["x_real"]) / 100, float(row["y_sim"]) / 100) for row in dc]
    output = [
        metric_stability("Digital Cousins, by policy", dc_points, [row["policy"] for row in dc]),
        metric_stability(
            "Digital Cousins, by generalization level",
            dc_points,
            [row["generalization_level"] for row in dc],
        ),
    ]
    rw = rows("source-roboworld.csv")
    for panel, label in (
        ("10a_GPT-4o_success_rate", "RoboWorld 10a"),
        ("10b_Gemini-2.5-Flash_success_rate", "RoboWorld 10b"),
    ):
        selected = [row for row in rw if row["panel"] == panel]
        real = np.asarray([float(row["x_real"]) for row in selected])
        real = (real - real.min()) / (real.max() - real.min())
        points = [(float(x), float(row["y_sim"])) for x, row in zip(real, selected)]
        output.append(metric_stability(label, points, [row["series"] for row in selected]))
    return output


def checkpoint_selection() -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows("source-real2sim-eval-fig3-checkpoints.csv"):
        grouped[row["task"]].append(row)

    output = []
    for task, task_rows in grouped.items():
        all_points = [
            (float(row["real_success"]), float(row["sim_success"])) for row in task_rows
        ]
        result: dict[str, object] = {
            "task": task,
            "n_checkpoints": len(task_rows),
            "n_policies": len({row["policy"] for row in task_rows}),
            "all_checkpoint_r": correlation(all_points),
        }
        for side, field in (("best_real", "real_success"), ("best_sim", "sim_success")):
            choices = []
            for policy in sorted({row["policy"] for row in task_rows}):
                candidates = [row for row in task_rows if row["policy"] == policy]
                maximum = max(float(row[field]) for row in candidates)
                choices.append([row for row in candidates if float(row[field]) == maximum])
            values = []
            for selected in itertools.product(*choices):
                points = [
                    (float(row["real_success"]), float(row["sim_success"]))
                    for row in selected
                ]
                values.append(correlation(points))
            result[f"{side}_r_min"] = min(values)
            result[f"{side}_r_max"] = max(values)
            result[f"{side}_n_tie_combinations"] = len(values)
        output.append(result)
    return sorted(output, key=lambda item: item["task"])


def winner_set(values: dict[str, float]) -> set[str]:
    maximum = max(values.values())
    return {
        label
        for label, value in values.items()
        if np.isclose(value, maximum, rtol=0.0, atol=1e-12)
    }


def decision_outcome(points: dict[str, tuple[float, float]]) -> dict[str, object]:
    real = {label: pair[0] for label, pair in points.items()}
    sim = {label: pair[1] for label, pair in points.items()}
    real_winners = winner_set(real)
    sim_winners = winner_set(sim)
    best_real = max(real.values())
    regrets = [best_real - real[label] for label in sim_winners]
    ordered = sorted(points)
    return {
        "real_winners": sorted(real_winners),
        "sim_winners": sorted(sim_winners),
        "possible_correct": bool(real_winners & sim_winners),
        "robustly_correct": sim_winners <= real_winners,
        "regret_fraction_min": min(regrets),
        "regret_fraction_max": max(regrets),
        "pearson_r": pearson(
            [points[label][0] for label in ordered],
            [points[label][1] for label in ordered],
        ),
    }


def simpler_decisions() -> dict[str, object]:
    source = rows("source-simpler-decisions.csv")
    output: dict[str, object] = {}
    for embodiment in sorted({row["embodiment"] for row in source}):
        selected = [row for row in source if row["embodiment"] == embodiment]
        tasks = sorted({row["task"] for row in selected})
        policies = sorted({row["policy"] for row in selected})

        def aggregate(kept_tasks: list[str]) -> dict[str, tuple[float, float]]:
            return {
                policy: (
                    float(
                        np.mean(
                            [
                                float(row["real_success"])
                                for row in selected
                                if row["task"] in kept_tasks
                                and row["policy"] == policy
                            ]
                        )
                    ),
                    float(
                        np.mean(
                            [
                                float(row["sim_success"])
                                for row in selected
                                if row["task"] in kept_tasks
                                and row["policy"] == policy
                            ]
                        )
                    ),
                )
                for policy in policies
            }

        aggregate_points = aggregate(tasks)
        task_rows = []
        for task in tasks:
            task_points = {
                row["policy"]: (
                    float(row["real_success"]),
                    float(row["sim_success"]),
                )
                for row in selected
                if row["task"] == task
            }
            task_rows.append({"task": task, **decision_outcome(task_points)})
        leave_one_task_out = []
        for omitted in tasks:
            kept = [task for task in tasks if task != omitted]
            leave_one_task_out.append(
                {"omitted_task": omitted, **decision_outcome(aggregate(kept))}
            )
        output[embodiment] = {
            "source_scope": (
                "Official REAL_PERF and SIMPLER_PERF values; equal-weight mean "
                "over the displayed tasks is newly declared by this audit."
            ),
            "n_policies": len(policies),
            "n_tasks": len(tasks),
            "aggregate": decision_outcome(aggregate_points),
            "aggregate_points": {
                policy: {"real": pair[0], "sim": pair[1]}
                for policy, pair in aggregate_points.items()
            },
            "per_task": {
                "rows": task_rows,
                "agreement_count": sum(
                    row["robustly_correct"] for row in task_rows
                ),
                "disagreement_count": sum(
                    not row["possible_correct"] for row in task_rows
                ),
            },
            "leave_one_task_out": {
                "rows": leave_one_task_out,
                "agreement_count": sum(
                    row["robustly_correct"] for row in leave_one_task_out
                ),
            },
        }
    return output


def real2sim_choice_rows(
    policy_rows: list[dict[str, str]], rule: str
) -> list[tuple[float, float]]:
    if rule == "mean":
        return [
            (
                float(
                    np.mean(
                        [
                            int(row["real_successes"]) / int(row["n_episodes"])
                            for row in policy_rows
                        ]
                    )
                ),
                float(
                    np.mean(
                        [
                            int(row["sim_successes"]) / int(row["n_episodes"])
                            for row in policy_rows
                        ]
                    )
                ),
            )
        ]
    field = "real_successes" if rule == "best_real" else "sim_successes"
    maximum = max(int(row[field]) for row in policy_rows)
    return [
        (
            int(row["real_successes"]) / int(row["n_episodes"]),
            int(row["sim_successes"]) / int(row["n_episodes"]),
        )
        for row in policy_rows
        if int(row[field]) == maximum
    ]


def real2sim_rule_decision(
    task_rows: list[dict[str, str]], rule: str
) -> dict[str, object]:
    policies = sorted({row["policy"] for row in task_rows})
    per_policy = {
        policy: real2sim_choice_rows(
            [row for row in task_rows if row["policy"] == policy], rule
        )
        for policy in policies
    }
    outcomes = [
        decision_outcome(dict(zip(policies, combination)))
        for combination in itertools.product(
            *(per_policy[policy] for policy in policies)
        )
    ]
    return {
        "task": task_rows[0]["task"],
        "rule": rule,
        "checkpoint_tie_combinations": len(outcomes),
        "necessarily_wrong": all(
            not row["possible_correct"] for row in outcomes
        ),
        "possibly_correct": any(row["possible_correct"] for row in outcomes),
        "robustly_correct": all(row["robustly_correct"] for row in outcomes),
        "regret_fraction_min": min(
            row["regret_fraction_min"] for row in outcomes
        ),
        "regret_fraction_max": max(
            row["regret_fraction_max"] for row in outcomes
        ),
        "pearson_r_min": min(row["pearson_r"] for row in outcomes),
        "pearson_r_max": max(row["pearson_r"] for row in outcomes),
        "outcomes": outcomes,
    }


def real2sim_decisions() -> dict[str, object]:
    source = rows("source-real2sim-eval-fig3-checkpoints.csv")
    decision_rows = []
    for task in sorted({row["task"] for row in source}):
        task_rows = [row for row in source if row["task"] == task]
        for rule in ("best_real", "best_sim", "mean"):
            decision_rows.append(real2sim_rule_decision(task_rows, rule))

    # The vector extraction contains two same-colour rope/DP markers at (0, 0).
    # Preserve a one-row deletion as an explicit extraction sensitivity.
    rope = [row for row in source if row["task"] == "rope"]
    zero_indices = [
        index
        for index, row in enumerate(rope)
        if row["policy"] == "dp"
        and int(row["real_successes"]) == 0
        and int(row["sim_successes"]) == 0
    ]
    if len(zero_indices) != 2:
        raise ValueError("expected exactly two coincident rope/DP zero rows")
    rope_minus_one = [
        row for index, row in enumerate(rope) if index != zero_indices[0]
    ]
    return {
        "scope": (
            "Four displayed policies; three identifiable checkpoint-collapse "
            "rules; all checkpoint and policy ties treated as sets. The nine "
            "task-rule cells reuse data and are descriptive, not independent."
        ),
        "rows": decision_rows,
        "summary": {
            "n_task_rule_cells": len(decision_rows),
            "necessarily_wrong": sum(
                row["necessarily_wrong"] for row in decision_rows
            ),
            "robustly_correct": sum(
                row["robustly_correct"] for row in decision_rows
            ),
            "tie_or_selection_dependent": sum(
                row["possibly_correct"] and not row["robustly_correct"]
                for row in decision_rows
            ),
            "some_tie_resolution_r_at_least_0_9_but_not_robustly_correct": sum(
                row["pearson_r_max"] >= 0.9 and not row["robustly_correct"]
                for row in decision_rows
            ),
            "all_tie_resolutions_r_at_least_0_9_but_not_robustly_correct": sum(
                row["pearson_r_min"] >= 0.9
                and not row["robustly_correct"]
                for row in decision_rows
            ),
        },
        "coincident_rope_zero_sensitivity": {
            "declared_rows": 20,
            "one_duplicate_removed_rows": 19,
            "all_checkpoint_r_declared": correlation(
                [
                    (
                        int(row["real_successes"]) / int(row["n_episodes"]),
                        int(row["sim_successes"]) / int(row["n_episodes"]),
                    )
                    for row in rope
                ]
            ),
            "all_checkpoint_r_one_removed": correlation(
                [
                    (
                        int(row["real_successes"]) / int(row["n_episodes"]),
                        int(row["sim_successes"]) / int(row["n_episodes"]),
                    )
                    for row in rope_minus_one
                ]
            ),
            "mean_rule_declared": real2sim_rule_decision(rope, "mean"),
            "mean_rule_one_removed": real2sim_rule_decision(
                rope_minus_one, "mean"
            ),
            "best_real_and_best_sim_unchanged": all(
                real2sim_rule_decision(rope, rule)
                == real2sim_rule_decision(rope_minus_one, rule)
                for rule in ("best_real", "best_sim")
            ),
        },
    }


def recipe_decisions() -> dict[str, object]:
    source = rows("source-recipe-rankings.csv")
    cases = []
    for row in source:
        sim_top = row["sim_order"][0]
        real_top = row["real_order"][0]
        cases.append(
            {
                "environment": row["env"],
                "simulator": row["simulator"],
                "dimension": row["dim"],
                "sim_top": sim_top,
                "real_top": real_top,
                "top1_agrees": sim_top == real_top,
                "printed_spearman": float(row["printed_rho"]),
                "printed_pearson": float(row["printed_r"]),
                "printed_mmrv": float(row["printed_mmrv"]),
            }
        )
    disagreements = [row for row in cases if not row["top1_agrees"]]
    return {
        "scope": (
            "Eleven printed rank panels in one paper; source rank strings "
            "identify top-1, but absolute success rates are unavailable."
        ),
        "panel_count": len(cases),
        "agreement_count": len(cases) - len(disagreements),
        "disagreement_count": len(disagreements),
        "max_printed_pearson_among_disagreements": max(
            row["printed_pearson"] for row in disagreements
        ),
        "max_printed_spearman_among_disagreements": max(
            row["printed_spearman"] for row in disagreements
        ),
        "disagreements": disagreements,
        "cases": cases,
    }


def decision_cases() -> dict[str, object]:
    return {
        "scope": (
            "Bounded decisions on displayed policies and declared task/checkpoint "
            "aggregation rules; no population error rates or population PCS."
        ),
        "simpler": simpler_decisions(),
        "real2sim": real2sim_decisions(),
        "practical_recipe": recipe_decisions(),
    }


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def decision_atlas() -> dict[str, object]:
    """Select paper-facing cases from the canonical decision-validity outputs.

    The upstream programs own winner aggregation, subset enumeration, and
    posterior simulation. This function validates and reshapes their committed
    results; it does not recompute those analyses.
    """
    reversal = load_json(DECISION_ROOT / "result-reversal-evidence.json")
    confidence = load_json(DECISION_ROOT / "result-decision-confidence.json")
    cosmos_two_sided = load_json(
        DECISION_ROOT / "result-cosmos-two-sided.json"
    )
    real2sim_two_sided = load_json(
        DECISION_ROOT / "result-real2sim-two-sided.json"
    )
    oscar_joined = load_json(PROSPECT_ROOT / "result-oscar-joined-panel.json")
    oscar_release = load_json(
        PROSPECT_ROOT / "result-oscar-roboarena-join.json"
    )
    oscar_release_sessions = oscar_release["release_structure"][
        "unique_sessions"
    ]
    oscar_release_outcomes = oscar_release["join_coverage"][
        "policy_records_with_valid_binary_success"
    ]
    oscar_wm_denominator = oscar_joined["inputs"][
        "printed_wm_inferred_denominator_per_policy"
    ]
    if (
        oscar_release_sessions
        != oscar_joined["inputs"]["joined_real_denominator_per_policy"]
    ):
        raise ValueError("OSCAR joined-panel denominator disagrees with release join")
    subsets = confidence["subset_stability"]
    posteriors = confidence["real_trial_posterior"]

    t_best_sim = next(
        row
        for row in real2sim_decisions()["rows"]
        if row["task"] == "T" and row["rule"] == "best_sim"
    )
    t_best_sim_outcome = t_best_sim["outcomes"][0]

    def record(
        *,
        case: str,
        source: str,
        rule: str,
        decision: dict[str, object],
        regret_scale: float,
        evidence_grade: str,
        real_denominator: str,
        simulator_denominator: str,
        subset_key: str | None = None,
        posterior: dict[str, object] | None = None,
        pearson_r_range: list[float] | None = None,
        coefficient_note: str,
    ) -> dict[str, object]:
        subset = subsets[subset_key] if subset_key else None
        return {
            "case": case,
            "source": source,
            "rule": rule,
            "pearson_r": decision["pearson_r"],
            "pearson_r_range": pearson_r_range,
            "coefficient_note": coefficient_note,
            "n_candidates": len(decision["points"]),
            "real_winners": decision["real_winners"],
            "sim_winners": decision["sim_winners"],
            "robustly_correct": decision["robustly_correct"],
            "displayed_real_regret_pp": decision["real_regret_max"] * regret_scale,
            "leave_one_task_out": (
                None
                if subset is None
                else {
                    "correct": subset["leave_one_block_out_correct"],
                    "total": subset["leave_one_block_out_total"],
                }
            ),
            "all_task_subsets": (
                None
                if subset is None
                else {
                    "correct": subset["all_nonempty_subsets_correct"],
                    "total": subset["all_nonempty_subsets_total"],
                }
            ),
            "posterior_probability_sim_winner_is_real_best": (
                None
                if posterior is None
                else posterior["posterior_probability_sim_winner_is_real_best"]
            ),
            "posterior_expected_real_regret_pp": (
                None
                if posterior is None
                else 100 * posterior["posterior_expected_real_regret"]
            ),
            "evidence_grade": evidence_grade,
            "real_denominator": real_denominator,
            "simulator_denominator": simulator_denominator,
        }

    cases = [
        record(
            case="WorldGym",
            source="WorldGym",
            rule="equal-task policy mean over 17 displayed tasks",
            decision=reversal["WorldGym"]["aggregate_policy_decision"],
            regret_scale=1.0,
            evidence_grade="exact published table",
            real_denominator="not used for this deterministic sensitivity",
            simulator_denominator="not used for this deterministic sensitivity",
            subset_key="WorldGym",
            coefficient_note="audit-defined policy aggregate; printed pooled-cell r=.78",
        ),
        record(
            case="Digital Cousins",
            source="Digital Cousins",
            rule="equal-level policy mean over four displayed generalization levels",
            decision=reversal["Digital Cousins"]["aggregate_policy_decision"],
            regret_scale=1.0,
            evidence_grade="table-validated recovered values",
            real_denominator="aggregate values only",
            simulator_denominator="aggregate values only",
            subset_key="Digital Cousins",
            coefficient_note="audit-defined policy aggregate",
        ),
        record(
            case="SIMPLER Google",
            source="SIMPLER",
            rule="equal-task policy mean over five displayed tasks",
            decision=reversal["SIMPLER"]["google_robot"],
            regret_scale=100.0,
            evidence_grade="official source arrays",
            real_denominator="aggregate values; original episode records unavailable",
            simulator_denominator="aggregate values; reconstructed binary arrays are not raw trials",
            subset_key="SIMPLER/google_robot",
            coefficient_note="audit-defined policy aggregate",
        ),
        record(
            case="Real2Sim T best-sim checkpoint",
            source="Real2Sim",
            rule="select each policy's best displayed simulated checkpoint",
                decision={
                    "pearson_r": t_best_sim["pearson_r_max"],
                    "points": {"act": {}, "dp": {}, "pi0": {}, "svla": {}},
                    "real_winners": t_best_sim_outcome["real_winners"],
                    "sim_winners": t_best_sim_outcome["sim_winners"],
                    "robustly_correct": not t_best_sim["necessarily_wrong"],
                    "real_regret_max": t_best_sim["regret_fraction_max"],
            },
            regret_scale=100.0,
            evidence_grade="vector-PDF recovery; printed coefficient reproduced",
            real_denominator="documented checkpoint-level counts",
            simulator_denominator="displayed rates; complete run structure unavailable",
            pearson_r_range=[
                t_best_sim["pearson_r_min"],
                t_best_sim["pearson_r_max"],
            ],
            coefficient_note=(
                "audit-declared source-aligned checkpoint-selection rule; "
                "the displayed r range reflects an unresolved non-winning checkpoint tie"
            ),
        ),
        record(
            case="OSCAR Skeleton",
            source="OSCAR",
            rule=(
                "audit-defined top-1 over seven displayed policies; "
                "source-provided values and metric bundle"
            ),
            decision=reversal["OSCAR"],
            regret_scale=1.0,
            evidence_grade="printed one-decimal bar labels; r reproduced to rounding",
            real_denominator=(
                "historical printed aggregation unstated; "
                f"{oscar_release_sessions} released sessions "
                f"({oscar_release_outcomes} binary outcomes) separately joined"
            ),
            simulator_denominator=(
                f"printed rates imply {oscar_wm_denominator} sessions; "
                "GPT-5 labels unavailable"
            ),
            coefficient_note="paper prints r=.852; recovered r shown",
        ),
        record(
            case="Cosmos-Surg manual",
            source="Cosmos-Surg-dVRK",
            rule="equal-task policy mean over four displayed tasks",
            decision=reversal["Cosmos-Surg-dVRK"]["manual_human_vs_dvrk"],
            regret_scale=100.0,
            evidence_grade="vector-PDF recovery; pooled coefficient reproduced",
            real_denominator="10 trials per policy-task",
            simulator_denominator=(
                "10 initial states x 3 generated seeds x 2 raters; "
                "aggregate allocation/dependence unreleased"
            ),
            subset_key="Cosmos-Surg-dVRK/manual_human_vs_dvrk",
            posterior=posteriors["Cosmos-Surg-dVRK"]["manual_human_vs_dvrk"],
            coefficient_note="audit-defined policy aggregate; paper prints pooled-cell r=.718",
        ),
        record(
            case="WM-PolicyEval / Cosmos",
            source="WM-PolicyEval",
            rule="equal-task policy mean over four displayed tasks",
            decision=reversal["WM-PolicyEval"]["Cosmos"]["aggregate_policy_decision"],
            regret_scale=100.0,
            evidence_grade="vector-PDF recovery plus exact appendix real values",
            real_denominator="20 trials per policy-task",
            simulator_denominator="unstated",
            subset_key="WM-PolicyEval/Cosmos",
            posterior=posteriors["WM-PolicyEval"]["Cosmos"],
            coefficient_note="audit-defined policy aggregate",
        ),
        record(
            case="WM-PolicyEval / IRASim",
            source="WM-PolicyEval",
            rule="equal-task policy mean over four displayed tasks",
            decision=reversal["WM-PolicyEval"]["IRASim"]["aggregate_policy_decision"],
            regret_scale=100.0,
            evidence_grade="vector-PDF recovery plus exact appendix real values",
            real_denominator="20 trials per policy-task",
            simulator_denominator="unstated",
            subset_key="WM-PolicyEval/IRASim",
            posterior=posteriors["WM-PolicyEval"]["IRASim"],
            coefficient_note="audit-defined policy aggregate",
        ),
    ]

    return {
        "scope": (
            "Heterogeneous finite-panel cases selected for evidentiary roles; "
            "not a calibration sample, prevalence denominator, or common population."
        ),
        "cases": cases,
        "real_trial_remeasurement_scope": (
            confidence["scope"]["posterior_analysis"]
            + " Candidate/block probabilities are independent in the fitted "
            "model; cross-candidate coupling is not identified by published "
            "marginal counts."
        ),
        "task_subset_scope": confidence["scope"]["subset_analysis"],
        "oscar_public_join": {
            "released_sessions": oscar_release_sessions,
            "released_binary_outcomes": oscar_release_outcomes,
            "printed_wm_inferred_denominator_per_policy": oscar_wm_denominator,
            "scope": oscar_joined["scope"],
        },
        "cosmos_manual_two_sided_remeasurement": {
            "scope": cosmos_two_sided["scope"],
            "draws_per_scenario": cosmos_two_sided["draws_per_scenario"],
            "stress_envelope": cosmos_two_sided["stress_envelope"],
            "scenarios": cosmos_two_sided["scenarios"],
        },
        "real2sim_t_two_sided_remeasurement": {
            "scope": real2sim_two_sided["scope"],
            "draws_per_scenario": real2sim_two_sided["draws_per_scenario"],
            "stress_envelope": real2sim_two_sided["stress_envelope"],
            "scenarios": real2sim_two_sided["scenarios"],
        },
    }


def integer_or_none(value: str) -> int | None:
    return int(value) if value.isdigit() else None


def unit_sensitivity() -> dict[str, object]:
    source = read_rows(CORPUS_ROOT / "result-unit-count-sensitivity.csv")
    if len(source) != 26:
        raise ValueError("unit-count sensitivity ledger must contain 26 papers")
    legacy = [int(row["legacy_policy_lineage_k"]) for row in source]
    permissive = [int(row["permissive_checkpoint_variant_k"]) for row in source]
    return {
        "rows": source,
        "legacy_under_10": sum(value < 10 for value in legacy),
        "permissive_under_10": sum(value < 10 for value in permissive),
        "under_10_range": [
            min(sum(value < 10 for value in legacy), sum(value < 10 for value in permissive)),
            max(sum(value < 10 for value in legacy), sum(value < 10 for value in permissive)),
        ],
    }


def complete_matrix_decisions() -> dict[str, object]:
    rows = read_rows(CORPUS_ROOT / "result-complete-matrix-decisions.csv")
    if len(rows) != 19:
        raise ValueError("complete-matrix ledger must contain 19 panels")
    typed = []
    for row in rows:
        typed.append(
            {
                **row,
                "pearson_r": float(row["pearson_r"]),
                "audit_spearman_rho": float(row["audit_spearman_rho"]),
                "displayed_real_regret_pp": float(
                    row["displayed_real_regret_pp"]
                ),
                "leave_one_task_out_correct": int(
                    row["leave_one_task_out_correct"]
                ),
                "leave_one_task_out_total": int(row["leave_one_task_out_total"]),
                "all_nonempty_task_subsets_correct": int(
                    row["all_nonempty_task_subsets_correct"]
                ),
                "all_nonempty_task_subsets_total": int(
                    row["all_nonempty_task_subsets_total"]
                ),
            }
        )
    return {
        "scope": (
            "All eligible direct-cell matrices derived from the retained source "
            "inventory under the declared candidate/block rules; outcome-exposed "
            "and not a prevalence denominator."
        ),
        "rows": typed,
        "n_panels": len(typed),
        "correct": sum(row["top1_result"] == "correct" for row in typed),
        "wrong": sum(row["top1_result"] == "wrong" for row in typed),
    }


def inference_link_recode() -> dict[str, object]:
    rows = read_rows(CORPUS_ROOT / "result-inference-link-recoding.csv")
    if len(rows) != 26 or len({row["paper"] for row in rows}) != 26:
        raise ValueError("inference-link recoding must contain 26 unique papers")
    return {
        "scope": (
            "Post-outcome broadened source review; categorical counts describe "
            "the frozen roster and are not literature prevalence estimates."
        ),
        "rows": rows,
        "held_out_predictive": sum(
            "held_out" in row["inferential_link"] for row in rows
        ),
        "fixed_benchmark_scope": sum(
            "fixed_benchmark" in row["target_scope"] for row in rows
        ),
        "formal_population_prediction": sum(
            row["formal_population_prediction"] == "yes" for row in rows
        ),
    }


def pvalue_resolution() -> list[dict[str, object]]:
    output = []
    for row in read_rows(CORPUS_ROOT / "result-pvalue-resolution.csv"):
        kp = int(row["policy_blocks_k"])
        kt = integer_or_none(row["task_blocks_k"])
        output.append(
            {
                **row,
                "policy_blocks_k": kp,
                "task_blocks_k": kt,
                "best_case_policy_resolution": 1 / factorial(kp),
                "best_case_task_resolution": 1 / factorial(kt) if kt else None,
                "printed_below_policy_resolution": (1 / factorial(kp)) > 0.001,
            }
        )
    return output


def count_all_coders_assign(
    details: dict[str, dict[str, tuple[str, ...]]], label: str
) -> int:
    return sum(
        all(values == (label,) for values in by_coder.values())
        for by_coder in details.values()
    )


def count_any_coder_assigns(
    details: dict[str, dict[str, tuple[str, ...]]], label: str
) -> int:
    return sum(
        any(label in values for values in by_coder.values())
        for by_coder in details.values()
    )


def survey_facts() -> dict[str, object]:
    adjudicated = audit_estimands.summarize(audit_estimands.load_rows())
    comparison = coding_compare.summarize()
    selection_agreement = comparison["agreements"]["selection_rule"]["all_three"]
    survey_by_name = {row[0]: row for row in SURVEY}
    recovered = sum(bool(row[7]) for row in SURVEY)

    return {
        "included_papers": len(SURVEY),
        "selected_near_miss_exclusions": len(EXCLUDED),
        "recovered_papers": recovered,
        "adjudicated_primary_coefficient_rows": adjudicated["coefficient_rows"],
        "finite_panel_consensus": count_all_coders_assign(
            comparison["details"]["finite_panel_description"], "yes"
        ),
        "target_population_consensus_yes": count_all_coders_assign(
            comparison["details"]["target_population_defined"], "yes"
        ),
        "target_population_consensus_no": count_all_coders_assign(
            comparison["details"]["target_population_defined"], "no"
        ),
        "new_policy_supported_any_coding": count_any_coder_assigns(
            comparison["details"]["new_policy_inference"], "supported"
        ),
        "new_task_supported_any_coding": count_any_coder_assigns(
            comparison["details"]["new_task_inference"], "supported"
        ),
        "crossed_supported_any_coding": count_any_coder_assigns(
            comparison["details"]["crossed_inference"], "supported"
        ),
        "prints_p_value": adjudicated["printed_p_value"],
        "prints_correlation_interval": adjudicated["correlation_interval"],
        "prints_any_correlation_uncertainty": adjudicated["any_correlation_uncertainty"],
        "prints_no_correlation_uncertainty": adjudicated["no_correlation_uncertainty"],
        "selection_final": {
            category: sum(row[6] == category for row in SURVEY)
            for category in ("yes", "no", "not-applicable")
        },
        "selection_all_three_exact_agreement": selection_agreement,
        "recovered_papers_list": sorted(name for name, row in survey_by_name.items() if row[7]),
    }


def real2sim_mmrv_reproduction() -> dict[str, object]:
    fig3 = audit_mmrv_conventions.load_fig3()
    fig9 = audit_mmrv_conventions.load_fig9()
    published = {
        row["task"]: row
        for row in read_rows(REAL2SIM_ROOT / "source-published-summary.csv")
    }
    matches3, values3 = audit_mmrv_conventions.check_fig3(fig3)
    matches9, values9 = audit_mmrv_conventions.check_fig9(fig9)
    convention = audit_mmrv_conventions.SUBJECT_CONVENTION
    return {
        "convention": {
            "violation": convention[0],
            "gap_side": convention[1],
            "normalization": convention[2],
        },
        "fig3_matching_conventions": [list(value) for value in matches3],
        "fig9_matching_conventions": [list(value) for value in matches9],
        "fig3_values": {
            task: {
                "exact_fraction": str(values3[convention][task]),
                "value": float(values3[convention][task]),
                "printed": float(published[task]["printed_mmrv"]),
                "recovered_r": correlation(
                    [(float(real), float(sim)) for real, sim in fig3[task]]
                ),
                "printed_r": float(published[task]["printed_r"]),
                "n_checkpoints": int(published[task]["figure3_checkpoints"]),
                "episodes_per_checkpoint": int(published[task]["episodes_per_checkpoint"]),
                "label": published[task]["label"],
            }
            for task in audit_mmrv_conventions.FIG3_PRINTED
        },
        "fig9_values": {
            panel: {
                "exact_fraction": str(values9[convention][panel]),
                "value": float(values9[convention][panel]),
            }
            for panel in audit_mmrv_conventions.FIG9_TARGETS
        },
        "t_block_checkpoint_counts": {
            "figure3_table1": 15,
            "figure10_replay_subset": 12,
            "evidence": (
                "15 Figure 3 markers reproduce Table I's r and MMRV; Figure 10 "
                "reports a separate 12-checkpoint replay subset"
            ),
        },
        "t_block_lattice": {
            "episodes_per_checkpoint": 16,
            "printed_mmrv": 0.108,
            "n_12": {
                "spacing": 1 / (12 * 16),
                "miss": abs(0.108 - round(0.108 * 12 * 16) / (12 * 16)),
            },
            "n_15": {
                "spacing": 1 / (15 * 16),
                "miss": abs(0.108 - round(0.108 * 15 * 16) / (15 * 16)),
            },
        },
    }


def bayesian_intervals() -> list[dict[str, object]]:
    output = []
    for task, r in sorted(analyze_bayesian_interval.unit_level_r().items()):
        lo, hi = analyze_bayesian_interval.posterior_interval(r, 4)
        output.append(
            {
                "task": task,
                # Twelve decimals is far beyond the precision supported by the
                # extracted source data and removes BLAS-level last-bit drift.
                "unit_level_r": round(r, 12),
                "n_unit_summaries": 4,
                "prior": "uniform on rho in [-1, 1]",
                "likelihood": "exact sample-r density under iid bivariate-normal unit summaries",
                "equal_tailed_95_interval": [lo, hi],
            }
        )
    return output


def build_results() -> dict[str, object]:
    leverage = leverage_table()
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": (
            "Bounded staged corpus: a 22-paper pre-Search-3 roster plus four fully "
            "logged Search-3 additions; not a census or systematic review. The earlier "
            "opportunistic base and Search 1-2 additions are only partially "
            "reconstructable. Six tracked exclusions are selected near-misses, not a "
            "screening denominator."
        ),
        "survey": survey_facts(),
        "unit_count_sensitivity": unit_sensitivity(),
        "complete_matrix_decisions": complete_matrix_decisions(),
        "inference_link_recode": inference_link_recode(),
        "pvalue_resolution": pvalue_resolution(),
        "leverage": {
            "scope": (
                "Historically selected illustrative panels from the recovered-data subset; "
                "not all eligible coefficients and not a corpus-prevalence denominator."
            ),
            "rows": leverage,
            "n_rows": len(leverage),
            "median_max_abs_delta_r": float(
                np.median([row["max_abs_delta_r"] for row in leverage])
            ),
            "min_max_abs_delta_r": min(row["max_abs_delta_r"] for row in leverage),
            "max_max_abs_delta_r": max(row["max_abs_delta_r"] for row in leverage),
            "above_descriptive_0_10": sum(
                row["max_abs_delta_r"] > 0.10 for row in leverage
            ),
        },
        "checkpoint_selection": checkpoint_selection(),
        "decision_cases": decision_cases(),
        "decision_atlas": decision_atlas(),
        "wm_missing_simulator_sensitivity": load_json(
            DECISION_ROOT
            / "result-wm-missing-simulator-evidence-sensitivity.json"
        ),
        "wm_probability_calibration": load_json(
            DECISION_ROOT / "result-wm-probability-calibration-audit.json"
        ),
        "wm_heterogeneous_simulator_evidence": load_json(
            DECISION_ROOT
            / "result-wm-heterogeneous-simulator-evidence-sensitivity.json"
        ),
        "wm_nonlinear_calibration": load_json(
            DECISION_ROOT
            / "result-wm-nonlinear-calibration-sensitivity.json"
        ),
        "bayesian_sensitivity": bayesian_intervals(),
        "mmrv_stability": mmrv_stability_table(),
        "real2sim_mmrv": real2sim_mmrv_reproduction(),
    }


def f(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def markdown(results: dict[str, object]) -> str:
    survey = results["survey"]
    lines = [
        "---",
        'title: "Supplement to: What Does a Sim-to-Real Correlation Support?"',
        'author: "Tri Lam"',
        'date: "2026-08-06"',
        "---",
        "",
        "## S1. Consensus and bounded-sample facts",
        "",
        "| fact | result | interpretation |",
        "|---|---:|---|",
        f"| Included papers | {survey['included_papers']} | non-systematic claim-based corpus |",
        f"| Papers with recovered numeric results | {survey['recovered_papers']} | recovery from published figures or tables |",
        f"| Finite displayed panel | {survey['finite_panel_consensus']}/26 | all audited papers |",
        f"| Defined target population or probability-sampling mechanism | 0/26 | none reported |",
        f"| Coefficient p-value | {survey['prints_p_value']}/26 | null-test output, not interval uncertainty in magnitude |",
        f"| Coefficient interval | {survey['prints_correlation_interval']}/26 | interval uncertainty for coefficient magnitude |",
        f"| Neither p-value nor coefficient interval | {survey['prints_no_correlation_uncertainty']}/26 | observable reporting fact; not evidence the coefficient is wrong |",
        "",
        "## S2. Unit-count sensitivity",
        "",
        "The two columns answer a policy/checkpoint sensitivity question; they do not treat "
        "tasks or conditions as automatically exchangeable units.",
        "",
        "| paper | legacy policy/lineage blocks | permissive checkpoints/variants |",
        "|---|---:|---:|",
    ]
    for row in results["unit_count_sensitivity"]["rows"]:
        lines.append(
            f"| {row['paper']} | {row['legacy_policy_lineage_k']} | "
            f"{row['permissive_checkpoint_variant_k']} |"
        )
    low, high = results["unit_count_sensitivity"]["under_10_range"]
    lines += [
        "",
        f"Across these two explicit codings, **{low}–{high} of 26** papers have fewer "
        "than ten policy/checkpoint blocks.",
        "",
        "## S3. Axis-specific best-case permutation resolution",
        "",
        "These are combinatorial resolutions conditional on valid exchangeability, not exact "
        "test results. Tied statistics can make the attained minimum coarser.",
        "",
        "| paper | printed p | policy k | 1/k! | task k | 1/k! |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in results["pvalue_resolution"]:
        task_k = "—" if row["task_blocks_k"] is None else str(row["task_blocks_k"])
        task_p = (
            "—"
            if row["best_case_task_resolution"] is None
            else f(row["best_case_task_resolution"], 6)
        )
        lines.append(
            f"| {row['paper']} | {row['printed_p']} | {row['policy_blocks_k']} | "
            f"{f(row['best_case_policy_resolution'], 6)} | {task_k} | {task_p} |"
        )
    lines += [
        "",
        "## S4. Complete leave-one-unit/point table",
        "",
        "The 0.10 column is retained only as a descriptive screen. The continuous movement "
        "and deletion unit are the reported quantities.",
        "",
        "| dataset | points | deletion units | unit | r | max abs change in r | max abs change in rho | >0.10 |",
        "|---|---:|---:|---|---:|---:|---:|:---:|",
    ]
    for row in results["leverage"]["rows"]:
        lines.append(
            f"| {row['dataset']} | {row['n_points']} | {row['n_units']} | "
            f"{row['deletion_unit']} | {f(row['r'], 4)} | "
            f"{f(row['max_abs_delta_r'], 3)} | "
            f"{f(row['max_abs_delta_spearman'], 3)} | "
            f"{'yes' if row['max_abs_delta_r'] > 0.10 else 'no'} |"
        )
    lines += [
        "",
        f"Median maximum absolute change in r = {f(results['leverage']['median_max_abs_delta_r'], 3)}; "
        f"range {f(results['leverage']['min_max_abs_delta_r'], 3)}–"
        f"{f(results['leverage']['max_max_abs_delta_r'], 3)}. "
        f"The descriptive 0.10 screen selects {results['leverage']['above_descriptive_0_10']}/28 "
        "illustrative rows; this is not a corpus-prevalence estimate.",
        "",
        "## S5. Bounded decision cases",
        "",
        "Each row concerns only the displayed policies and the stated aggregation rule. "
        "Top-1 agreement means that the simulator-selected winner belongs to the "
        "real-data winner set; regret is the displayed real-success gap to the best policy.",
        "",
        "| case | declared rule | r | top-1 result | real regret | diagnostic |",
        "|---|---|---:|---|---:|---|",
    ]
    for label, key in (("SIMPLER Google", "google_robot"), ("SIMPLER WidowX", "widowx")):
        case = results["decision_cases"]["simpler"][key]
        aggregate = case["aggregate"]
        lines.append(
            f"| {label} | equal-weight mean over {case['n_tasks']} displayed tasks | "
            f"{f(aggregate['pearson_r'], 3)} | agreement | 0 | "
            f"{case['per_task']['agreement_count']}/{case['n_tasks']} individual tasks agree; "
            f"{case['leave_one_task_out']['agreement_count']}/{case['n_tasks']} "
            "leave-one-task-out aggregates agree |"
        )
    t_best_sim = next(
        row
        for row in results["decision_cases"]["real2sim"]["rows"]
        if row["task"] == "T" and row["rule"] == "best_sim"
    )
    lines.append(
        f"| Real2Sim T-block | select each policy's best simulated checkpoint | "
        f"{f(t_best_sim['pearson_r_min'], 3)}–"
        f"{f(t_best_sim['pearson_r_max'], 3)} | disagreement | "
        f"{100 * t_best_sim['regret_fraction_min']:.2f} pp | "
        "non-winning checkpoint tie changes r but not the selected or real winner |"
    )
    recipe = results["decision_cases"]["practical_recipe"]
    lines.append(
        f"| A Practical Recipe | printed top-ranked variant in each rank panel | "
        "varies | "
        f"{recipe['disagreement_count']}/{recipe['panel_count']} panels disagree | — | "
        f"largest printed Pearson r among disagreements = "
        f"{f(recipe['max_printed_pearson_among_disagreements'], 3)} |"
    )
    real2sim_summary = results["decision_cases"]["real2sim"]["summary"]
    rope_sensitivity = results["decision_cases"]["real2sim"][
        "coincident_rope_zero_sensitivity"
    ]
    lines += [
        "",
        "Across Real2Sim's three tasks and three declared checkpoint-collapse rules, "
        f"{real2sim_summary['necessarily_wrong']}/9 cells necessarily disagree, "
        f"{real2sim_summary['robustly_correct']}/9 robustly agrees, and "
        f"{real2sim_summary['tie_or_selection_dependent']}/9 is tie-dependent. "
        "These nine cells share data and are not independent repetitions.",
        "",
        "The vector extraction contains two coincident rope/DP markers at (0,0). "
        f"Removing one changes all-checkpoint r from "
        f"{f(rope_sensitivity['all_checkpoint_r_declared'], 3)} to "
        f"{f(rope_sensitivity['all_checkpoint_r_one_removed'], 3)} and mean-rule r from "
        f"{f(rope_sensitivity['mean_rule_declared']['pearson_r_min'], 3)} to "
        f"{f(rope_sensitivity['mean_rule_one_removed']['pearson_r_min'], 3)}, "
        "but it does not change any of the three rope rule-level top-1 conclusions.",
        "",
        "## S6. Complete direct-cell matrices",
        "",
        results["complete_matrix_decisions"]["scope"],
        "",
        "| panel | source metric bundle | audit Pearson r | audit Spearman rho | top-1 | regret (pp) | LOTO |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for row in results["complete_matrix_decisions"]["rows"]:
        panel_label = row["panel_id"].replace("/", " — ").replace("_", " ")
        metric_label = row["source_metric_bundle"].replace(" and ", " + ")
        lines.append(
            f"| {panel_label} | {metric_label} | "
            f"{f(row['pearson_r'], 3)} | {f(row['audit_spearman_rho'], 3)} | "
            f"{row['top1_result']} | {f(row['displayed_real_regret_pp'], 2)} | "
            f"{row['leave_one_task_out_correct']}/"
            f"{row['leave_one_task_out_total']} |"
        )
    lines += [
        "",
        f"The complete-matrix set contains "
        f"{results['complete_matrix_decisions']['correct']}/"
        f"{results['complete_matrix_decisions']['n_panels']} displayed top-1 agreements and "
        f"{results['complete_matrix_decisions']['wrong']}/"
        f"{results['complete_matrix_decisions']['n_panels']} displayed top-1 disagreements. "
        "These counts describe this non-systematic recovered set only.",
        "",
        "## S7. Illustrative cross-source decision atlas",
        "",
        results["decision_atlas"]["scope"],
        "",
        "| case | r | simulated winner | displayed real winner | regret (pp) | LOTO | evidence |",
        "|---|---:|---|---|---:|---:|---|",
    ]
    for row in results["decision_atlas"]["cases"]:
        loto = row["leave_one_task_out"]
        loto_text = "—" if loto is None else f"{loto['correct']}/{loto['total']}"
        r_text = (
            f"{f(row['pearson_r_range'][0], 3)}–{f(row['pearson_r_range'][1], 3)}"
            if row["pearson_r_range"] is not None
            else f(row["pearson_r"], 3)
        )
        lines.append(
            f"| {row['case']} | {r_text} | "
            f"{', '.join(row['sim_winners'])} | {', '.join(row['real_winners'])} | "
            f"{f(row['displayed_real_regret_pp'], 2)} | {loto_text} | "
            f"{row['evidence_grade']} |"
        )
    lines += [
        "",
        "## S8. Finite-real-trial remeasurement",
        "",
        results["decision_atlas"]["real_trial_remeasurement_scope"],
        "",
        "| case | posterior P(sim winner is real-best) | posterior expected regret (pp) | real denominator | simulator denominator |",
        "|---|---:|---:|---|---|",
    ]
    for row in results["decision_atlas"]["cases"]:
        probability = row["posterior_probability_sim_winner_is_real_best"]
        if probability is None:
            continue
        lines.append(
            f"| {row['case']} | {f(probability, 6)} | "
            f"{f(row['posterior_expected_real_regret_pp'], 2)} | "
            f"{row['real_denominator']} | {row['simulator_denominator']} |"
        )
    wm_uncertainty = results["wm_missing_simulator_sensitivity"]["panels"]
    lines += [
        "",
        "### S8.1 Missing simulator-evidence sensitivity",
        "",
        "The effective simulator evidence grid is a sensitivity design, not an estimate "
        "of the unreleased rollout denominator.",
        "",
        "| evaluator | sampled-winner match range | expected real-regret range (pp) | all scenarios below one half? | first listed crossing by prior (.5/1/2) |",
        "|---|---:|---:|---|---|",
    ]
    for model in ("Cosmos", "IRASim"):
        panel = wm_uncertainty[model]
        probabilities = [
            row["probability_sampled_sim_winner_is_sampled_real_best"]
            for row in panel["scenarios"]
        ]
        regrets = [
            100 * row["expected_real_regret_of_sampled_sim_winner"]
            for row in panel["scenarios"]
        ]
        crossings = panel["stress_envelope"][
            "first_listed_evidence_size_above_one_half_by_prior"
        ]
        crossing_text = "/".join(
            "none" if crossings[key] is None else str(crossings[key])
            for key in ("0.5", "1", "2")
        )
        lines.append(
            f"| {model} | {f(min(probabilities), 4)}–{f(max(probabilities), 4)} | "
            f"{f(min(regrets), 1)}–{f(max(regrets), 1)} | "
            f"{str(panel['stress_envelope']['all_scenarios_below_one_half']).lower()} | "
            f"{crossing_text} |"
        )
    heterogeneous = results["wm_heterogeneous_simulator_evidence"]["panels"][
        "IRASim"
    ]["scenarios"]
    lines += [
        "",
        "### S8.2 Policy-heterogeneous simulator evidence",
        "",
        "The sampled-winner estimand measures latent-rank concordance under one "
        "common assumed evidence size, not observed-action reliability. The next "
        "rows vary assumed evidence by policy; actual evidence remains unknown.",
        "",
        "| IRASim scenario | evidence (Octo-Base/Octo-Small/OpenVLA) | latent-winner concordance | MCSE | posterior-mean simulator winner |",
        "|---|---|---:|---:|---|",
    ]
    for name in ("common_10", "openvla_10", "openvla_0"):
        row = heterogeneous[name]
        evidence = row["evidence_by_policy"]
        evidence_text = "/".join(
            f"{evidence[policy]:g}"
            for policy in ("Octo-Base", "Octo-Small", "OpenVLA")
        )
        lines.append(
            f"| {name} | {evidence_text} | "
            f"{f(row['latent_winner_concordance'], 4)} | "
            f"{f(row['monte_carlo_se'], 5)} | "
            f"{'/'.join(row['posterior_mean_sim_winner_set'])} |"
        )
    wm_calibration = results["wm_probability_calibration"]["panels"]
    lines += [
        "",
        "### S8.3 Probability-level affine calibration",
        "",
        "Cell-rate MSE and the empirical individual-outcome Brier score are different "
        "estimands. Their exact difference here is the empirical within-cell outcome "
        "variance. Positive affine calibration preserves the displayed aggregate winner.",
        "",
        "| evaluator | mean predicted-real | cell-rate MSE | empirical Brier | intercept | slope | task-held-out recalibrated MSE | winner preserved? |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for model in ("Cosmos", "IRASim"):
        panel = wm_calibration[model]
        calibration = panel["metrics"]
        heldout = panel["task_heldout_affine_recalibration"]
        lines.append(
            f"| {model} | "
            f"{f(calibration['calibration_in_the_large_predicted_minus_real'], 5)} | "
            f"{f(calibration['cell_rate_mse'], 5)} | "
            f"{f(calibration['empirical_individual_outcome_brier'], 5)} | "
            f"{f(calibration['ols_intercept_real_on_predicted'], 3)} | "
            f"{f(calibration['ols_slope_real_on_predicted'], 3)} | "
            f"{f(heldout['pooled_recalibrated_rate_mse'], 5)} | yes |"
        )
    nonlinear = results["wm_nonlinear_calibration"]["panels"]
    lines += [
        "",
        "### S8.4 Nonlinear calibration and Murphy decomposition",
        "",
        "The isotonic map is fitted and evaluated on the same 12 cells. It is an "
        "in-sample shape sensitivity, not prospective calibration or selection repair.",
        "",
        "| evaluator | raw winner | isotonic winner | raw rate MSE | isotonic in-sample MSE | Murphy reliability | resolution | Brier skill vs prevalence |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for model in ("Cosmos", "IRASim"):
        panel = nonlinear[model]
        murphy = panel["murphy_forecast_level_decomposition"]
        lines.append(
            f"| {model} | {panel['original_winner']} | "
            f"{panel['isotonic_winner']} | "
            f"{f(panel['raw_cell_rate_mse'], 5)} | "
            f"{f(panel['isotonic_in_sample_cell_rate_mse'], 5)} | "
            f"{f(murphy['reliability'], 5)} | "
            f"{f(murphy['resolution'], 5)} | "
            f"{f(murphy['brier_skill_vs_empirical_prevalence'], 3)} |"
        )
    lines += [
        "",
        "## S9. Exact displayed-task composition sensitivity",
        "",
        results["decision_atlas"]["task_subset_scope"],
        "",
        "| case | leave-one-task-out correct | all nonempty subsets correct |",
        "|---|---:|---:|",
    ]
    for row in results["decision_atlas"]["cases"]:
        loto = row["leave_one_task_out"]
        subsets = row["all_task_subsets"]
        if loto is None:
            continue
        lines.append(
            f"| {row['case']} | {loto['correct']}/{loto['total']} | "
            f"{subsets['correct']}/{subsets['total']} |"
        )
    lines += [
        "",
        "## S10. Checkpoint-selection sensitivity",
        "",
        "All tied maxima are enumerated. A range therefore reflects the selection rule itself, "
        "not arbitrary file order.",
        "",
        "| task | checkpoints | all-checkpoint r | best-real r range | tie combinations | best-sim r range | tie combinations |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results["checkpoint_selection"]:
        lines.append(
            f"| {row['task']} | {row['n_checkpoints']} | {f(row['all_checkpoint_r'], 3)} | "
            f"{f(row['best_real_r_min'], 3)} to {f(row['best_real_r_max'], 3)} | "
            f"{row['best_real_n_tie_combinations']} | "
            f"{f(row['best_sim_r_min'], 3)} to {f(row['best_sim_r_max'], 3)} | "
            f"{row['best_sim_n_tie_combinations']} |"
        )
    lines += [
        "",
        "## S11. MMRV versus correlation stability",
        "",
        "MMRV uses SIMPLER's strict-ordering XOR, real-side gap, and divide-by-N convention. "
        "RoboWorld's real-side leaderboard score is min-max scaled once on the full panel.",
        "",
        "| dataset | k | MMRV | absolute MMRV range | relative r swing | relative MMRV swing | ratio |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results["mmrv_stability"]:
        lines.append(
            f"| {row['dataset']} | {row['n_units']} | {f(row['mmrv'], 6)} | "
            f"{f(row['absolute_mmrv_range'], 6)} | "
            f"{100 * row['relative_r_swing']:.1f}% | "
            f"{100 * row['relative_mmrv_swing']:.1f}% | "
            f"{row['relative_swing_ratio']:.1f}× |"
        )
    mmrv_result = results["real2sim_mmrv"]
    lines += [
        "",
        "## S12. Real2Sim MMRV convention reproduction",
        "",
        "The declared grid has 60 named entries but 48 distinct formulas because one "
        "predicate pair is pointwise identical by construction. Exactly one distinct "
        "formula matches all three Table I values and all three Figure 9 values: less-than-or-equal XOR "
        "(equivalently strict-> XOR), simulated-side gap, divide by N.",
        "",
        "| panel | N | episodes | recovered r | printed r | exact recovered MMRV | printed MMRV |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for task, value in mmrv_result["fig3_values"].items():
        lines.append(
            f"| {value['label']} | {value['n_checkpoints']} | "
            f"{value['episodes_per_checkpoint']} | {f(value['recovered_r'], 4)} | "
            f"{f(value['printed_r'], 3)} | {value['exact_fraction']} "
            f"({f(value['value'], 6)}) | {f(value['printed'], 3)} |"
        )
    lines += [
        "",
        "The following appendix values use the same recovered convention:",
        "",
        "| panel | exact recovered MMRV | decimal |",
        "|---|---:|---:|",
    ]
    for panel, value in mmrv_result["fig9_values"].items():
        lines.append(
            f"| Figure 9 {panel} | {value['exact_fraction']} | {f(value['value'], 6)} |"
        )
    lines += [
        "",
        "We recover 15 T-block checkpoints from Figure 3; they reproduce Table I's "
        "$r=.915$ and MMRV $=.108$. Figure 10 reports a separate 12-checkpoint replay subset.",
        "",
        "## S13. Model-conditional correlation sensitivity",
        "",
        "These are equal-tailed posterior intervals under iid bivariate-normal unit summaries "
        "and a uniform prior on rho. They are not assumption-free intervals.",
        "",
        "| task | unit-level r | n | 95% posterior interval |",
        "|---|---:|---:|---:|",
    ]
    for row in results["bayesian_sensitivity"]:
        lo, hi = row["equal_tailed_95_interval"]
        lines.append(
            f"| {row['task']} | {f(row['unit_level_r'], 3)} | "
            f"{row['n_unit_summaries']} | [{f(lo, 3)}, {f(hi, 3)}] |"
        )
    lines.append("")
    return "\n".join(lines)


def main_tables_markdown(results: dict[str, object]) -> str:
    survey = results["survey"]
    low, high = results["unit_count_sensitivity"]["under_10_range"]
    lines = [
        "# Generated main-paper tables",
        "",
        "Generated factual cells come from "
        "`research/claim-evidence-synthesis/result-paper-evidence.json`. "
        "Explanatory cells implement "
        "the locked rewrite specification.",
        "",
        "## Table 1. Three layers of a correlation audit",
        "",
        "| layer | question | evidence to report | boundary when absent |",
        "|---|---|---|---|",
        "| Identification | What finite panel does the coefficient describe? | displayed points, axes, aggregation | coefficient scope is ambiguous |",
        "| Identification | What population or decision is the result meant to address? | target population or named finite-panel decision | population inference is unidentified |",
        "| Identification | How did models, checkpoints, tasks, and conditions enter? | selection rule for every coefficient axis | selection sensitivity is unknown |",
        "| Robustness | Does one relevant unit carry the coefficient? | continuous leave-unit-out values and deletion unit | finite-panel composition sensitivity is hidden |",
        "| Robustness | Does an alternate decision-relevant estimand change the conclusion? | prespecified alternate aggregation or selection | one coefficient may answer the wrong decision |",
        "| Reproduction | Can a reader recompute the coefficient and metric? | paired values, metric code, conventions, provenance | numerical agreement cannot be independently checked |",
        "",
        "## Table 2. Results of the bounded 26-paper audit",
        "",
        "| result | count | evidence class | interpretation boundary |",
        "|---|---:|---|---|",
        f"| Included papers | {survey['included_papers']} | adjudicated corpus ledger | 22-paper pre-Search-3 roster plus four fully logged Search-3 additions; not a census |",
        f"| Papers with recovered numeric results | {survey['recovered_papers']} | per-paper recovery ledger | recovery modes and validation gates differ |",
        f"| Finite displayed panel | {survey['finite_panel_consensus']}/26 | three model-assisted internal coding passes | provisional pending independent human source-only recoding; descriptive panel existence, not independence |",
        f"| Defined target population or sampling mechanism | 0/26 | three model-assisted internal coding passes | provisional pending independent human source-only recoding; absence does not show the simulator fails |",
        "| Design-based support under the original coding rule | 0/26 | three applications of the same construct | model-based and transport routes were not separately coded |",
        f"| Coefficient p-value | {survey['prints_p_value']}/26 | adjudicated observable reporting fact | does not quantify uncertainty in coefficient magnitude |",
        f"| Coefficient interval | {survey['prints_correlation_interval']}/26 | adjudicated observable reporting fact | only interval estimate for coefficient magnitude |",
        f"| Neither p-value nor coefficient interval | {survey['prints_no_correlation_uncertainty']}/26 | adjudicated observable reporting fact | does not imply the coefficient is numerically wrong |",
        f"| Fewer than ten policy/checkpoint blocks | {low}–{high}/26 | two explicit sensitivity codings | not a unique effective sample size |",
        "",
        "## Table 3. Inventory-derived complete direct-cell matrices",
        "",
        "| panel | source metric bundle | Pearson r | Spearman ρ | top-1 | regret | LOTO |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for row in results["complete_matrix_decisions"]["rows"]:
        lines.append(
            f"| {row['panel_id']} | {row['source_metric_bundle']} | "
            f"{f(row['pearson_r'], 3)} | {f(row['audit_spearman_rho'], 3)} | "
            f"{row['top1_result']} | "
            f"{f(row['displayed_real_regret_pp'], 2)} pp | "
            f"{row['leave_one_task_out_correct']}/"
            f"{row['leave_one_task_out_total']} |"
        )
    lines += [
        "",
        f"All {results['complete_matrix_decisions']['n_panels']} recovered complete "
        "direct-cell matrices are shown: "
        f"{results['complete_matrix_decisions']['correct']} displayed agreements and "
        f"{results['complete_matrix_decisions']['wrong']} disagreements. "
        "These outcome-exposed rows are not a calibration sample or prevalence denominator; "
        "their exact aggregation rules and source limitations are recorded in the supplement.",
        "",
        "## Table 4. Real2Sim reproduction",
        "",
        "| task | Figure 3 N | episodes/checkpoint | recovered r | printed r | exact recovered MMRV | printed MMRV |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    mmrv_result = results["real2sim_mmrv"]
    for value in mmrv_result["fig3_values"].values():
        lines.append(
            f"| {value['label']} | {value['n_checkpoints']} | "
            f"{value['episodes_per_checkpoint']} | {f(value['recovered_r'], 4)} | "
            f"{f(value['printed_r'], 3)} | {value['exact_fraction']} "
            f"({f(value['value'], 6)}) | {f(value['printed'], 3)} |"
        )
    lines += [
        "",
        "Recovered convention: ≤-XOR (equivalently strict-> XOR), simulated-side gap, "
        "divide by N. It is the only joint match among the 48 distinct formulas in the "
        "declared 60-entry grid.",
        "",
        "## Table 5. Core reporting standard",
        "",
        "| requirement | minimum disclosure |",
        "|---|---|",
        "| Target | Name the finite panel, target population if any, and deployment decision. |",
        "| Axes | State whether points vary over policies, runs, checkpoints, tasks, or conditions. |",
        "| Selection | State how every entering model/checkpoint and any tie was selected. |",
        "| Dependence | Aggregate or model repeated observations at the unit relevant to the claim. |",
        "| Robustness and uncertainty | Report continuous leave-unit-out sensitivity and assumption-labeled uncertainty. |",
        "| Reproduction | Release paired unit-level values, metric implementation, conventions, and provenance. |",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "result-paper-evidence.json")
    parser.add_argument("--supplement", type=Path, default=ROOT / "result-quantitative-supplement.md")
    parser.add_argument("--main-tables", type=Path, default=ROOT / "result-main-tables.md")
    args = parser.parse_args()
    result = build_results()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.supplement.write_text(markdown(result), encoding="utf-8")
    args.main_tables.write_text(main_tables_markdown(result), encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"wrote {args.supplement}")
    print(f"wrote {args.main_tables}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
