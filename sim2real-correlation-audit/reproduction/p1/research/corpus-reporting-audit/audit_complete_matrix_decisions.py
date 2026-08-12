#!/usr/bin/env python3
"""Generate results for every eligible recovered direct-cell matrix.

Eligibility is derived from the retained source inventory, not inherited from
an earlier analysis result. A matrix needs at least two stable candidate
identities, at least two commensurable task/condition blocks, and exactly one
real/evaluator value per candidate-block cell after any declared
outcome-independent roster normalization.
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
DECISION = HERE.parent / "decision-validity"
REVERSAL = DECISION / "result-reversal-evidence.json"
CONFIDENCE = DECISION / "result-decision-confidence.json"
OUTPUT = HERE / "result-complete-matrix-decisions.csv"
SOURCES = HERE / "sources"
DISPOSITIONS = HERE / "result-matrix-source-disposition.csv"

FIELDS = [
    "panel_id",
    "paper",
    "condition",
    "rule_provenance",
    "aggregation_rule",
    "source_metric_bundle",
    "pearson_r",
    "audit_spearman_rho",
    "real_winners",
    "sim_winners",
    "top1_result",
    "displayed_real_regret_pp",
    "leave_one_task_out_correct",
    "leave_one_task_out_total",
    "all_nonempty_task_subsets_correct",
    "all_nonempty_task_subsets_total",
    "scope_note",
]

PANEL_META = {
    "Cosmos-Surg-dVRK/automated_fig1b": (
        "Cosmos-Surg-dVRK",
        "automated Fig. 1b",
        "source-matched aggregation/action; audit-defined ties/loss",
        "equal-task policy mean over four displayed tasks",
        "Pearson and MMRV",
    ),
    "Cosmos-Surg-dVRK/manual_human_vs_dvrk": (
        "Cosmos-Surg-dVRK",
        "manual human-vs-dVRK",
        "source-matched aggregation/action; audit-defined ties/loss",
        "equal-task policy mean over four displayed tasks",
        "Pearson and MMRV",
    ),
    "Digital Cousins": (
        "Digital Cousins",
        "four generalization levels",
        "audit-defined",
        "equal-level policy mean",
        "Pearson",
    ),
    "Hi-WM": (
        "Hi-WM",
        "three displayed tasks",
        "audit-defined",
        "equal-task policy mean",
        "Pearson",
    ),
    "SIMPLER/google_robot": (
        "SIMPLER",
        "Google Robot",
        "audit-defined",
        "equal-task policy mean over five displayed tasks",
        "Pearson and MMRV",
    ),
    "SIMPLER/widowx": (
        "SIMPLER",
        "WidowX",
        "audit-defined",
        "equal-task policy mean over four displayed tasks",
        "Pearson and MMRV",
    ),
    "WEAVER/CtrlWorld": (
        "WEAVER",
        "CtrlWorld",
        "audit-defined",
        "equal-task policy mean over five displayed tasks",
        "Pearson and Spearman",
    ),
    "WEAVER/WEAVER": (
        "WEAVER",
        "WEAVER",
        "audit-defined",
        "equal-task policy mean over five displayed tasks",
        "Pearson and Spearman",
    ),
    "WEAVER/WEAVER-FT": (
        "WEAVER",
        "WEAVER-FT",
        "audit-defined",
        "equal-task policy mean over five displayed tasks",
        "Pearson and Spearman",
    ),
    "WM-PolicyEval/Cosmos": (
        "WM-PolicyEval",
        "Cosmos",
        "audit-defined",
        "equal-task policy mean over four displayed tasks",
        "Pearson and MMRV",
    ),
    "WM-PolicyEval/IRASim": (
        "WM-PolicyEval",
        "IRASim",
        "audit-defined",
        "equal-task policy mean over four displayed tasks",
        "Pearson and MMRV",
    ),
    "WorldEval": (
        "WorldEval",
        "five displayed tasks",
        "audit-defined",
        "equal-task policy mean",
        "Pearson",
    ),
    "WorldGym": (
        "WorldGym",
        "17 displayed tasks",
        "audit-defined",
        "equal-task policy mean",
        "Pearson and ranking-preservation analysis",
    ),
    "REALM/Default": (
        "REALM",
        "Default",
        "audit-defined",
        "equal-task policy mean over seven displayed tasks",
        "Pearson and MMRV",
    ),
    "REALM/Overall": (
        "REALM",
        "Overall",
        "audit-defined",
        "equal-task policy mean over seven displayed tasks",
        "Pearson and MMRV",
    ),
    "REALM/VB-POSE": (
        "REALM",
        "VB-POSE",
        "audit-defined",
        "equal-task policy mean over seven displayed tasks",
        "Pearson and MMRV",
    ),
    "Mem-World": (
        "Mem-World",
        "five displayed tasks",
        "audit-defined",
        "equal-task policy mean",
        "Pearson and p-value",
    ),
    "MolmoSpaces/common-appendix-roster": (
        "MolmoSpaces",
        "appendix pick/open/close",
        "audit-defined",
        "equal-task mean over the four-policy intersection across three tasks",
        "Pearson and Spearman",
    ),
    "EmbodiedSplat/mesh-conditions": (
        "EmbodiedSplat",
        "Poly and DN mesh conditions",
        "audit-defined",
        "equal-mesh mean; candidate identity is base lineage x finetuning status",
        "Pearson",
    ),
}

NEW_PANELS = {
    "REALM/Default",
    "REALM/Overall",
    "REALM/VB-POSE",
    "Mem-World",
    "MolmoSpaces/common-appendix-roster",
    "EmbodiedSplat/mesh-conditions",
}


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def read_source(name: str) -> list[dict[str, str]]:
    with (SOURCES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def validate_source_dispositions() -> None:
    with DISPOSITIONS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    recorded = {row["source_file"] for row in rows}
    actual = {
        path.name
        for path in SOURCES.glob("source-*.csv")
        if not path.name.startswith("source-estimand-blind-")
    }
    if recorded != actual:
        raise ValueError("matrix source-disposition inventory is incomplete")
    eligible_ids = {
        panel_id
        for row in rows
        if row["status"] == "eligible"
        for panel_id in row["matrix_ids"].split("|")
        if panel_id
    }
    if eligible_ids != set(PANEL_META):
        raise ValueError("eligible source dispositions do not match matrix metadata")
    for row in rows:
        if not row["reason"].strip():
            raise ValueError(f"missing disposition reason for {row['source_file']}")


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and math.isclose(
            values[order[start]], values[order[end]], rel_tol=0.0, abs_tol=1e-12
        ):
            end += 1
        rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def pearson(x: list[float], y: list[float]) -> float:
    x_mean = math.fsum(x) / len(x)
    y_mean = math.fsum(y) / len(y)
    numerator = math.fsum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x, y)
    )
    denominator = math.sqrt(
        math.fsum((value - x_mean) ** 2 for value in x)
        * math.fsum((value - y_mean) ** 2 for value in y)
    )
    return numerator / denominator


def winner_set(values: dict[str, float]) -> list[str]:
    maximum = max(values.values())
    return sorted(
        name
        for name, value in values.items()
        if math.isclose(value, maximum, rel_tol=0.0, abs_tol=1e-12)
    )


def aggregate_matrix(
    rows: list[dict[str, str]],
    *,
    candidate,
    block_key: str,
    real_key: str,
    sim_key: str,
    kept_blocks: set[str] | None = None,
) -> dict[str, object]:
    cells: dict[tuple[str, str], tuple[float, float]] = {}
    candidates: set[str] = set()
    blocks: set[str] = set()
    for row in rows:
        block = row[block_key]
        if kept_blocks is not None and block not in kept_blocks:
            continue
        name = candidate(row)
        key = (name, block)
        if key in cells:
            raise ValueError(f"duplicate candidate-block cell {key}")
        cells[key] = (float(row[real_key]), float(row[sim_key]))
        candidates.add(name)
        blocks.add(block)
    if len(candidates) < 2 or len(blocks) < 1:
        raise ValueError("matrix needs at least two candidates and one retained block")
    expected = {(name, block) for name in candidates for block in blocks}
    if set(cells) != expected:
        raise ValueError("candidate x block matrix is incomplete")
    real = {
        name: math.fsum(cells[name, block][0] for block in blocks) / len(blocks)
        for name in candidates
    }
    simulated = {
        name: math.fsum(cells[name, block][1] for block in blocks) / len(blocks)
        for name in candidates
    }
    names = sorted(candidates)
    real_winners = winner_set(real)
    sim_winners = winner_set(simulated)
    best_real = max(real.values())
    regrets = [best_real - real[name] for name in sim_winners]
    return {
        "pearson_r": pearson(
            [real[name] for name in names], [simulated[name] for name in names]
        ),
        "points": {
            name: {"real": real[name], "sim": simulated[name]} for name in names
        },
        "real_winners": real_winners,
        "sim_winners": sim_winners,
        "robustly_correct": set(sim_winners).issubset(real_winners),
        "real_regret_max": max(regrets),
        "blocks": sorted(blocks),
    }


def matrix_stability(
    rows: list[dict[str, str]],
    *,
    candidate,
    block_key: str,
    real_key: str,
    sim_key: str,
) -> dict[str, int]:
    blocks = sorted({row[block_key] for row in rows})
    correct = 0
    total = 0
    loto = 0
    for size in range(1, len(blocks) + 1):
        for selected in itertools.combinations(blocks, size):
            decision = aggregate_matrix(
                rows,
                candidate=candidate,
                block_key=block_key,
                real_key=real_key,
                sim_key=sim_key,
                kept_blocks=set(selected),
            )
            total += 1
            correct += int(decision["robustly_correct"])
            if size == len(blocks) - 1:
                loto += int(decision["robustly_correct"])
    return {
        "all_nonempty_subsets_correct": correct,
        "all_nonempty_subsets_total": total,
        "leave_one_block_out_correct": loto,
        "leave_one_block_out_total": len(blocks),
    }


def source_matrix(panel_id: str) -> tuple[dict[str, object], dict[str, int], float]:
    if panel_id.startswith("REALM/"):
        panel = panel_id.split("/", 1)[1]
        rows = [
            row for row in read_source("source-realm.csv") if row["panel"] == panel
        ]
        keys = dict(
            candidate=lambda row: row["policy"],
            block_key="task",
            real_key="x_real",
            sim_key="y_sim",
        )
        scale = 100.0
    elif panel_id == "Mem-World":
        rows = read_source("source-mem-world.csv")
        keys = dict(
            candidate=lambda row: row["policy"],
            block_key="task",
            real_key="real_success",
            sim_key="worldmodel_success",
        )
        scale = 100.0
    elif panel_id == "MolmoSpaces/common-appendix-roster":
        appendix = [
            row
            for row in read_source("source-molmospaces.csv")
            if row["source_panel"] == "appendix_fig"
        ]
        by_task: dict[str, set[str]] = defaultdict(set)
        for row in appendix:
            by_task[row["task"]].add(row["policy"])
        common = set.intersection(*by_task.values())
        rows = [row for row in appendix if row["policy"] in common]
        keys = dict(
            candidate=lambda row: row["policy"],
            block_key="task",
            real_key="real_success_pct",
            sim_key="sim_success_pct",
        )
        scale = 1.0
    elif panel_id == "EmbodiedSplat/mesh-conditions":
        rows = read_source("source-embodiedsplat.csv")
        keys = dict(
            candidate=lambda row: f"{row['base_lineage']}-{row['ft_status']}",
            block_key="mesh",
            real_key="real_success",
            sim_key="sim_success",
        )
        scale = 100.0
    else:
        raise ValueError(f"unknown source-derived matrix {panel_id}")
    decision = aggregate_matrix(rows, **keys)
    if len(decision["blocks"]) < 2:
        raise ValueError(f"{panel_id} needs at least two complete blocks")
    stability = matrix_stability(rows, **keys)
    return decision, stability, scale


def decision_for(reversal: dict[str, object], panel_id: str) -> dict[str, object]:
    if panel_id.startswith("Cosmos-Surg-dVRK/"):
        return reversal["Cosmos-Surg-dVRK"][panel_id.split("/", 1)[1]]
    if panel_id.startswith("SIMPLER/"):
        return reversal["SIMPLER"][panel_id.split("/", 1)[1]]
    if panel_id.startswith("WEAVER/"):
        return reversal["WEAVER"][panel_id.split("/", 1)[1]]
    if panel_id.startswith("WM-PolicyEval/"):
        return reversal["WM-PolicyEval"][panel_id.split("/", 1)[1]][
            "aggregate_policy_decision"
        ]
    value = reversal[panel_id]
    if isinstance(value, dict) and "aggregate_policy_decision" in value:
        return value["aggregate_policy_decision"]
    return value


def build_rows() -> list[dict[str, object]]:
    validate_source_dispositions()
    reversal = load(REVERSAL)
    subset = load(CONFIDENCE)["subset_stability"]
    if set(subset) | NEW_PANELS != set(PANEL_META):
        raise ValueError("matrix inventory and metadata are inconsistent")

    rows = []
    for panel_id in sorted(PANEL_META):
        paper, condition, provenance, rule, metrics = PANEL_META[panel_id]
        if panel_id in NEW_PANELS:
            decision, stability, regret_scale = source_matrix(panel_id)
        else:
            decision = decision_for(reversal, panel_id)
            stability = subset[panel_id]
            regret_scale = 100.0
        candidates = sorted(decision["points"])
        real = [decision["points"][name]["real"] for name in candidates]
        simulated = [decision["points"][name]["sim"] for name in candidates]
        rows.append(
            {
                "panel_id": panel_id,
                "paper": paper,
                "condition": condition,
                "rule_provenance": provenance,
                "aggregation_rule": rule,
                "source_metric_bundle": metrics,
                "pearson_r": f"{decision['pearson_r']:.12f}",
                "audit_spearman_rho": f"{pearson(average_ranks(real), average_ranks(simulated)):.12f}",
                "real_winners": "|".join(decision["real_winners"]),
                "sim_winners": "|".join(decision["sim_winners"]),
                "top1_result": "correct" if decision["robustly_correct"] else "wrong",
                "displayed_real_regret_pp": f"{regret_scale * decision['real_regret_max']:.6f}",
                "leave_one_task_out_correct": stability["leave_one_block_out_correct"],
                "leave_one_task_out_total": stability["leave_one_block_out_total"],
                "all_nonempty_task_subsets_correct": stability[
                    "all_nonempty_subsets_correct"
                ],
                "all_nonempty_task_subsets_total": stability[
                    "all_nonempty_subsets_total"
                ],
                "scope_note": (
                    "Inventory-derived set of recovered complete direct-cell matrices; "
                    "outcome-exposed and not a prevalence denominator."
                ),
            }
        )
    return rows


def render(rows: list[dict[str, object]]) -> str:
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(build_rows())
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{OUTPUT} is stale")
        print("complete-matrix decision ledger valid: 19 panels")
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
