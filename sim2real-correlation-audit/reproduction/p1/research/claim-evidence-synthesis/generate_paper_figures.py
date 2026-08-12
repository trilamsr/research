#!/usr/bin/env python3
"""Generate the paper figures for the clean-room rewrite.

Every annotation is checked against synthesize_paper_evidence.build_results(). The plotting
code may transform coordinates for display, but it does not own a second set of
paper values.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "corpus-reporting-audit" / "sources"
sys.path.insert(0, str(HERE))

import synthesize_paper_evidence as facts  # noqa: E402


BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
GREY = "#7A7A7A"
LIGHT = "#E8E8E8"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 180,
        "savefig.bbox": "tight",
    }
)


def source_rows(name: str) -> list[dict[str, str]]:
    with (SOURCES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def save(fig: plt.Figure, stem: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.pdf")
    fig.savefig(out_dir / f"{stem}.png")
    plt.close(fig)
    print(f"saved {stem}.pdf/.png")


def figure1_axes(result: dict[str, object], out_dir: Path) -> None:
    worldgym = next(
        row for row in result["pvalue_resolution"] if row["paper"] == "WorldGym"
    )
    assert worldgym["policy_blocks_k"] == 3
    assert worldgym["task_blocks_k"] == 17

    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for policy in range(3):
        for task in range(17):
            ax.add_patch(
                Rectangle(
                    (task, 2 - policy),
                    0.88,
                    0.72,
                    facecolor=(BLUE, ORANGE, GREEN)[policy],
                    edgecolor="white",
                    linewidth=0.7,
                    alpha=0.88,
                )
            )
    ax.set_xlim(-0.2, 18.0)
    ax.set_ylim(-1.15, 3.05)
    ax.set_xticks(np.arange(17) + 0.44, [str(i) for i in range(1, 18)], fontsize=7)
    ax.set_yticks([2.36, 1.36, 0.36], ["policy 1", "policy 2", "policy 3"])
    ax.set_xlabel("17 task blocks")

    ax.annotate(
        "",
        xy=(17.18, 0),
        xytext=(17.18, 2.72),
        arrowprops=dict(arrowstyle="<->", color=VERMILLION, linewidth=1.3),
    )
    ax.text(
        17.5,
        1.36,
        "policy-axis\nk = 3",
        ha="left",
        va="center",
        color=VERMILLION,
        fontsize=8,
    )
    ax.annotate(
        "",
        xy=(0, -0.38),
        xytext=(16.88, -0.38),
        arrowprops=dict(arrowstyle="<->", color=BLUE, linewidth=1.3),
    )
    ax.text(
        8.44,
        -0.68,
        "task-axis k = 17",
        ha="center",
        va="top",
        color=BLUE,
        fontsize=8,
    )
    ax.text(
        8.44,
        2.92,
        "51 displayed policy–task cells do not determine one exchangeability scheme",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    save(fig, "figure-worldgym-axis-validity", out_dir)


def figure2_decision_contrast(result: dict[str, object], out_dir: Path) -> None:
    google = result["decision_cases"]["simpler"]["google_robot"]
    google_points = google["aggregate_points"]
    google_fact = google["aggregate"]

    real2sim_rows = [
        row
        for row in source_rows("source-real2sim-eval-fig3-checkpoints.csv")
        if row["task"] == "T"
    ]
    policies = sorted({row["policy"] for row in real2sim_rows})
    t_points = {
        policy: (
            float(
                np.mean(
                    [
                        int(row["real_successes"]) / int(row["n_episodes"])
                        for row in real2sim_rows
                        if row["policy"] == policy
                    ]
                )
            ),
            float(
                np.mean(
                    [
                        int(row["sim_successes"]) / int(row["n_episodes"])
                        for row in real2sim_rows
                        if row["policy"] == policy
                    ]
                )
            ),
        )
        for policy in policies
    }
    t_fact = next(
        row
        for row in result["decision_cases"]["real2sim"]["rows"]
        if row["task"] == "T" and row["rule"] == "mean"
    )
    assert len(google_points) == google["n_policies"] == 6
    assert len(t_points) == 4

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.55))
    cases = [
        (
            axes[0],
            "SIMPLER Google",
            {
                key: (value["real"], value["sim"])
                for key, value in google_points.items()
            },
            google_fact["pearson_r"],
            google_fact["real_winners"],
            google_fact["sim_winners"],
            "winner agreement, regret = 0",
        ),
        (
            axes[1],
            "Real2Sim T-block",
            t_points,
            t_fact["pearson_r_min"],
            t_fact["outcomes"][0]["real_winners"],
            t_fact["outcomes"][0]["sim_winners"],
            f"winner disagreement, regret = {100 * t_fact['regret_fraction_min']:.2f} pp",
        ),
    ]
    palette = (BLUE, ORANGE, GREEN, PURPLE, VERMILLION, GREY)
    for ax, title, points, coefficient, real_winners, sim_winners, verdict in cases:
        for index, (policy, (real, sim)) in enumerate(sorted(points.items())):
            is_sim_winner = policy in sim_winners
            ax.scatter(
                100 * real,
                100 * sim,
                s=92 if is_sim_winner else 45,
                marker="*" if is_sim_winner else "o",
                color=palette[index],
                edgecolor="black" if is_sim_winner else "white",
                linewidth=0.7,
                zorder=3,
            )
            ax.annotate(
                policy,
                (100 * real, 100 * sim),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=6.8,
            )
        real_text = ", ".join(real_winners)
        sim_text = ", ".join(sim_winners)
        ax.set_title(f"{title}\nr = {coefficient:.3f}; {verdict}", fontweight="bold")
        ax.text(
            0.02,
            0.98,
            f"real winner: {real_text}\nsim winner: {sim_text}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7.4,
            bbox=dict(facecolor="white", edgecolor=LIGHT, alpha=0.92),
        )
        ax.set_xlabel("real success (%)")
        ax.set_ylabel("simulated success (%)")
        ax.grid(color=LIGHT, linewidth=0.7)
    fig.suptitle(
        "Similar finite-panel correlations, opposite top-1 decisions",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()
    save(fig, "figure-decision-contrast", out_dir)


def figure3_checkpoint_estimand(result: dict[str, object], out_dir: Path) -> None:
    fact = next(row for row in result["checkpoint_selection"] if row["task"] == "rope")
    selected = [
        row
        for row in source_rows("source-real2sim-eval-fig3-checkpoints.csv")
        if row["task"] == "rope"
    ]
    policies = sorted({row["policy"] for row in selected})
    assert len(selected) == fact["n_checkpoints"] == 20
    assert len(policies) == fact["n_policies"] == 4
    colors = dict(zip(policies, (BLUE, ORANGE, GREEN, PURPLE)))

    best_sim = []
    for policy in policies:
        policy_rows = [row for row in selected if row["policy"] == policy]
        maximum = max(float(row["sim_success"]) for row in policy_rows)
        choices = [row for row in policy_rows if float(row["sim_success"]) == maximum]
        assert len(choices) == 1
        best_sim.append(choices[0])

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.45), sharex=True, sharey=True)
    for policy in policies:
        policy_rows = [row for row in selected if row["policy"] == policy]
        real_values = [float(row["real_success"]) for row in policy_rows]
        sim_values = [float(row["sim_success"]) for row in policy_rows]
        assert all(0 <= value <= 100 for value in real_values + sim_values)
        axes[0].scatter(
            real_values,
            sim_values,
            s=38,
            color=colors[policy],
            label=policy,
            alpha=0.86,
        )
    coordinate_counts = Counter(
        (float(row["real_success"]), float(row["sim_success"])) for row in selected
    )
    assert sum(coordinate_counts.values()) == 20
    for (real_value, sim_value), count in coordinate_counts.items():
        if count > 1:
            axes[0].annotate(
                f"×{count}",
                (real_value, sim_value),
                xytext=(6, 5),
                textcoords="offset points",
                fontsize=7.5,
                fontweight="bold",
                color=GREY,
            )
    axes[0].set_title(f"all 20 checkpoints\nr = {fact['all_checkpoint_r']:.3f}")
    axes[0].set_xlabel("real success (%)")
    axes[0].set_ylabel("simulated success (%)")
    axes[0].legend(frameon=False, fontsize=7.5, title="policy", title_fontsize=7.5)

    offsets = {"act": (4, 4), "dp": (-24, 6), "pi0": (6, 6), "svla": (5, 5)}
    for row in best_sim:
        axes[1].scatter(
            float(row["real_success"]),
            float(row["sim_success"]),
            s=68,
            color=colors[row["policy"]],
            edgecolor="black",
            linewidth=0.5,
        )
        axes[1].annotate(
            row["policy"],
            (float(row["real_success"]), float(row["sim_success"])),
            xytext=offsets[row["policy"]],
            textcoords="offset points",
            fontsize=7,
        )
    axes[1].set_title(
        "best simulated-success checkpoint per policy\n"
        f"r = {fact['best_sim_r_min']:.3f}"
    )
    axes[1].set_xlabel("real success (%)")
    axes[1].text(
        0.5,
        -0.22,
        "best-real selection is also negative across all tied maxima: "
        f"{fact['best_real_r_min']:.3f} to {fact['best_real_r_max']:.3f}",
        transform=axes[1].transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color=VERMILLION,
    )
    for ax in axes:
        ax.grid(color=LIGHT, linewidth=0.7)
        ax.set_xlim(-2, 102)
        ax.set_ylim(-2, 102)
    save(fig, "figure-rope-estimand", out_dir)


def figure4_decision_atlas(result: dict[str, object], out_dir: Path) -> None:
    cases = result["decision_atlas"]["cases"]
    ordered = sorted(cases, key=lambda row: row["pearson_r"])
    fig, ax = plt.subplots(figsize=(7.4, 4.25))
    y = np.arange(len(ordered))
    for index, row in enumerate(ordered):
        color = GREEN if row["robustly_correct"] else VERMILLION
        marker = "o" if row["robustly_correct"] else "X"
        if row["pearson_r_range"] is not None:
            ax.hlines(
                index,
                row["pearson_r_range"][0],
                row["pearson_r_range"][1],
                color=color,
                linewidth=3.0,
                alpha=0.75,
                zorder=2,
            )
        ax.scatter(
            row["pearson_r"],
            index,
            s=90,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        if not row["robustly_correct"]:
            ax.annotate(
                f"{row['displayed_real_regret_pp']:.1f} pp regret",
                (row["pearson_r"], index),
                xytext=(7, 0),
                textcoords="offset points",
                va="center",
                fontsize=7.4,
                color=VERMILLION,
            )
    ax.set_yticks(y, [row["case"] for row in ordered])
    ax.set_xlim(0.45, 1.015)
    ax.set_xlabel("Pearson correlation for the declared policy decision")
    ax.set_title(
        "Correlation magnitude does not determine the displayed decision",
        fontweight="bold",
    )
    ax.grid(axis="x", color=LIGHT, linewidth=0.8)
    ax.axvspan(0.85, 1.0, color=LIGHT, alpha=0.35, zorder=0)
    ax.text(
        0.02,
        0.98,
        "circle = agreement    X = disagreement    line = tied-rule r range",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.5,
        color=GREY,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.82),
    )
    fig.tight_layout()
    save(fig, "figure-decision-atlas", out_dir)


def figure5_decision_robustness(result: dict[str, object], out_dir: Path) -> None:
    cases = result["decision_atlas"]["cases"]
    posterior_cases = [
        row
        for row in cases
        if row["posterior_probability_sim_winner_is_real_best"] is not None
    ]
    subset_cases = [row for row in cases if row["leave_one_task_out"] is not None]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.05))
    posterior_cases = sorted(
        posterior_cases,
        key=lambda row: row["posterior_probability_sim_winner_is_real_best"],
    )
    py = np.arange(len(posterior_cases))
    pvalues = [
        row["posterior_probability_sim_winner_is_real_best"]
        for row in posterior_cases
    ]
    pcolors = [
        GREEN if row["robustly_correct"] else VERMILLION
        for row in posterior_cases
    ]
    axes[0].barh(py, pvalues, color=pcolors, alpha=0.88)
    axes[0].set_yticks(py, [row["case"] for row in posterior_cases], fontsize=7.4)
    axes[0].set_xlim(0, 1)
    axes[0].set_xlabel("posterior probability")
    axes[0].set_title(
        "Displayed sim winner is real-best\n(independent-candidate model)",
        fontweight="bold",
        fontsize=9,
    )
    for index, value in enumerate(pvalues):
        axes[0].text(
            min(value + 0.02, 0.98),
            index,
            f"{value:.4f}",
            va="center",
            ha="right" if value > 0.9 else "left",
            fontsize=7.2,
        )

    subset_cases = sorted(
        subset_cases,
        key=lambda row: (
            row["leave_one_task_out"]["correct"]
            / row["leave_one_task_out"]["total"]
        ),
    )
    sy = np.arange(len(subset_cases))
    svalues = [
        row["leave_one_task_out"]["correct"]
        / row["leave_one_task_out"]["total"]
        for row in subset_cases
    ]
    scolors = [
        GREEN if row["robustly_correct"] else VERMILLION
        for row in subset_cases
    ]
    axes[1].barh(sy, svalues, color=scolors, alpha=0.88)
    axes[1].set_yticks(sy, [row["case"] for row in subset_cases], fontsize=7.4)
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel("fraction with winner agreement")
    axes[1].set_title(
        "Winner agreement after deleting one displayed task",
        fontweight="bold",
        fontsize=9,
    )
    for index, row in enumerate(subset_cases):
        loto = row["leave_one_task_out"]
        value = svalues[index]
        axes[1].text(
            min(value + 0.02, 0.98),
            index,
            f"{loto['correct']}/{loto['total']}",
            va="center",
            ha="right" if value > 0.9 else "left",
            fontsize=7.2,
        )

    for ax in axes:
        ax.grid(axis="x", color=LIGHT, linewidth=0.7)
    fig.suptitle(
        "Measurement-model and task-deletion sensitivities are distinct",
        fontsize=10.5,
        fontweight="bold",
    )
    fig.tight_layout()
    save(fig, "figure-decision-robustness", out_dir)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=HERE)
    args = parser.parse_args()
    result = facts.build_results()
    figure1_axes(result, args.out_dir)
    figure2_decision_contrast(result, args.out_dir)
    figure3_checkpoint_estimand(result, args.out_dir)
    figure4_decision_atlas(result, args.out_dir)
    figure5_decision_robustness(result, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
