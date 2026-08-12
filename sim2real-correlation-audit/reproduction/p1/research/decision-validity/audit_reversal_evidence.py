#!/usr/bin/env python3
"""Recompute bounded model-selection outcomes from released numeric matrices."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "corpus-reporting-audit" / "sources"
OUT = ROOT / "result-reversal-evidence.json"


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


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = mean(x), mean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = math.sqrt(
        sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)
    )
    return numerator / denominator


def average_ranks(values: list[float]) -> list[float]:
    """Return one-based average ranks with exact ties sharing a rank."""
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(average_ranks(x), average_ranks(y))


def decision(points: dict[str, tuple[float, float]]) -> dict[str, object]:
    real_max = max(value[0] for value in points.values())
    sim_max = max(value[1] for value in points.values())
    real_winners = sorted(
        key for key, value in points.items() if value[0] == real_max
    )
    sim_winners = sorted(
        key for key, value in points.items() if value[1] == sim_max
    )
    regrets = [real_max - points[key][0] for key in sim_winners]
    ordered = sorted(points)
    return {
        "points": {
            key: {"real": points[key][0], "sim": points[key][1]}
            for key in ordered
        },
        "real_winners": real_winners,
        "sim_winners": sim_winners,
        "robustly_correct": set(sim_winners) <= set(real_winners),
        "possible_correct": bool(set(sim_winners) & set(real_winners)),
        "real_regret_min": min(regrets),
        "real_regret_max": max(regrets),
        "pearson_r": pearson(
            [points[key][0] for key in ordered],
            [points[key][1] for key in ordered],
        ),
    }


def mmrv(sim: list[float], real: list[float]) -> float:
    """SIMPLER Eq. 1: strict ordering XOR, weighted by the real-side gap."""
    maxima = []
    for i in range(len(sim)):
        violations = [
            abs(real[i] - real[j])
            for j in range(len(sim))
            if (sim[i] > sim[j]) != (real[i] > real[j])
        ]
        maxima.append(max(violations, default=0.0))
    return mean(maxima)


def aggregate(
    rows: list[dict[str, str]],
    label: str,
    real: str,
    sim: str,
    selector=lambda row: True,
) -> dict[str, tuple[float, float]]:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        if selector(row):
            grouped[row[label]].append((float(row[real]), float(row[sim])))
    return {
        key: (
            mean([pair[0] for pair in pairs]),
            mean([pair[1] for pair in pairs]),
        )
        for key, pairs in grouped.items()
    }


def stable_numbers(value):
    """Remove sub-ULP runtime differences from the released JSON artifact."""
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable_numbers(item) for item in value]
    return value


def build_results() -> dict[str, object]:
    """Recompute source-resolution results without serialization rounding."""
    results: dict[str, object] = {}

    simpler = read_csv("source-simpler-decisions.csv")
    results["SIMPLER"] = {}
    for embodiment in sorted({row["embodiment"] for row in simpler}):
        points = aggregate(
            simpler,
            "policy",
            "real_success",
            "sim_success",
            lambda row, embodiment=embodiment: row["embodiment"] == embodiment,
        )
        results["SIMPLER"][embodiment] = decision(points)
    results["SIMPLER"]["mmrv_argument_order_audit"] = {}
    for task in sorted({row["task"] for row in simpler}):
        task_rows = [row for row in simpler if row["task"] == task]
        sim_values = [float(row["sim_success"]) for row in task_rows]
        real_values = [float(row["real_success"]) for row in task_rows]
        results["SIMPLER"]["mmrv_argument_order_audit"][task] = {
            "paper_equation_and_executable_script": mmrv(
                sim_values, real_values
            ),
            "readme_and_calc_metrics_docstring_example": mmrv(
                real_values, sim_values
            ),
        }

    worldgym = read_csv("source-worldgym-decisions.csv")
    wg_points = aggregate(
        worldgym, "policy", "real_successes", "sim_successes"
    )
    results["WorldGym"] = {
        "aggregate_policy_decision": decision(wg_points),
        "pooled_cell_pearson_r": pearson(
            [float(row["real_successes"]) for row in worldgym],
            [float(row["sim_successes"]) for row in worldgym],
        ),
    }

    digital = read_csv("source-digital-cousins.csv")
    results["Digital Cousins"] = {
        "aggregate_policy_decision": decision(
            aggregate(digital, "policy", "x_real", "y_sim")
        ),
        "by_generalization_level": {},
    }
    for level in sorted({row["generalization_level"] for row in digital}):
        points = aggregate(
            digital,
            "policy",
            "x_real",
            "y_sim",
            lambda row, level=level: row["generalization_level"] == level,
        )
        results["Digital Cousins"]["by_generalization_level"][level] = decision(
            points
        )

    roboworld = read_csv("source-roboworld.csv")
    results["RoboWorld"] = {}
    for panel in sorted({row["panel"] for row in roboworld}):
        points = {
            row["series"]: (float(row["x_real"]), float(row["y_sim"]))
            for row in roboworld
            if row["panel"] == panel
        }
        results["RoboWorld"][panel] = decision(points)

    realm = read_csv("source-realm.csv")
    results["REALM"] = {}
    for panel in sorted({row["panel"] for row in realm}):
        points = aggregate(
            realm,
            "policy",
            "x_real",
            "y_sim",
            lambda row, panel=panel: row["panel"] == panel,
        )
        results["REALM"][panel] = decision(points)

    worldeval = read_csv("source-worldeval.csv")
    results["WorldEval"] = decision(
        aggregate(
            worldeval, "policy", "real_success", "generated_success"
        )
    )

    robosnap = read_csv("source-robosnap.csv")
    results["RoboSnap"] = {
        "figure": decision(
            {
                row["task"]: (
                    float(row["plotted_real_sr"]),
                    float(row["plotted_sim_sr"]),
                )
                for row in robosnap
            }
        ),
        "inline_table": decision(
            {
                row["task"]: (
                    float(row["table_real_sr"]),
                    float(row["table_sim_sr"]),
                )
                for row in robosnap
            }
        ),
    }

    wm = read_csv("source-wm-policyeval.csv")
    results["WM-PolicyEval"] = {}
    for model in sorted({row["world_model"] for row in wm}):
        points = aggregate(
            wm,
            "policy",
            "actual_success_rate",
            "predicted_success_rate",
            lambda row, model=model: row["world_model"] == model,
        )
        cell_rows = [row for row in wm if row["world_model"] == model]
        results["WM-PolicyEval"][model] = {
            "aggregate_policy_decision": decision(points),
            "pooled_cell_pearson_r": pearson(
                [float(row["actual_success_rate"]) for row in cell_rows],
                [float(row["predicted_success_rate"]) for row in cell_rows],
            ),
        }

    recipe = read_csv("source-recipe-rankings.csv")
    recipe_panels = []
    for row in recipe:
        recipe_panels.append(
            {
                "panel": f"{row['env']} / {row['dim']}",
                "sim_winner": row["sim_order"][0],
                "real_winner": row["real_order"][0],
                "correct": row["sim_order"][0] == row["real_order"][0],
                "printed_pearson_r": float(row["printed_r"]),
            }
        )
    results["A Practical Recipe"] = {
        "panels": recipe_panels,
        "disagreement_count": sum(
            not row["correct"] for row in recipe_panels
        ),
        "absolute_regret_recoverable": False,
    }

    cosmos = read_csv("source-cosmos-surg-dvrk.csv")
    results["Cosmos-Surg-dVRK"] = {}
    for panel in sorted({row["panel"] for row in cosmos}):
        panel_rows = [row for row in cosmos if row["panel"] == panel]
        points = aggregate(
            panel_rows,
            "policy",
            "x_real_descaled",
            "y_sim_descaled",
        )
        results["Cosmos-Surg-dVRK"][panel] = decision(points)
        if panel == "manual_human_vs_dvrk":
            run_points = aggregate(
                panel_rows,
                "unit",
                "x_real_descaled",
                "y_sim_descaled",
            )
            run_companion = decision(run_points)
            ordered_units = sorted(run_points)
            run_companion["spearman_rho"] = spearman(
                [run_points[key][0] for key in ordered_units],
                [run_points[key][1] for key in ordered_units],
            )
            run_companion["unit_definition"] = (
                "Three source-documented training-run lineages, each "
                "averaging two checkpoints across four displayed tasks."
            )
            results["Cosmos-Surg-dVRK"][panel][
                "training_run_companion"
            ] = run_companion

    embodied = read_csv("source-embodiedsplat.csv")
    results["EmbodiedSplat"] = {}
    for mesh in sorted({row["mesh"] for row in embodied}):
        points = {
            row["config"]: (
                float(row["real_success"]),
                float(row["sim_success"]),
            )
            for row in embodied
            if row["mesh"] == mesh
        }
        results["EmbodiedSplat"][mesh] = decision(points)

    gemini = read_csv("source-gemini-veo.csv")
    results["Gemini/Veo"] = decision(
        {
            row["variant"]: (
                float(row["real_success"]),
                float(row["veo_predicted_success"]),
            )
            for row in gemini
        }
    )

    hiwm = read_csv("source-hi-wm.csv")
    results["Hi-WM"] = decision(
        aggregate(
            hiwm,
            "policy",
            "real_success_rate",
            "generated_success_rate",
        )
    )

    molmo = read_csv("source-molmospaces.csv")
    results["MolmoSpaces"] = {}
    for task in sorted({row["task"] for row in molmo}):
        selected = [
            row
            for row in molmo
            if row["task"] == task
            and (
                task != "pick" or row["source_panel"] == "main_fig"
            )
        ]
        points = {
            row["policy"]: (
                float(row["real_success_pct"]),
                float(row["sim_success_pct"]),
            )
            for row in selected
        }
        results["MolmoSpaces"][task] = decision(points)

    oscar = read_csv("source-oscar.csv")
    results["OSCAR"] = decision(
        {
            row["policy"]: (
                float(row["real_sr_pct"]),
                float(row["wm_sr_pct"]),
            )
            for row in oscar
        }
    )

    weaver = read_csv("source-weaver.csv")
    results["WEAVER"] = {}
    for panel in sorted({row["panel"] for row in weaver}):
        points = aggregate(
            weaver,
            "policy",
            "real_sr",
            "wm_sr",
            lambda row, panel=panel: row["panel"] == panel,
        )
        results["WEAVER"][panel] = decision(points)

    mem = read_csv("source-mem-world.csv")
    results["Mem-World"] = decision(
        aggregate(mem, "policy", "real_success", "worldmodel_success")
    )

    return results


def main(out: Path = OUT) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(stable_numbers(build_results()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    main(args.out)
