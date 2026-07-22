"""Generate Figures 1-3 for PAPER.md. Okabe-Ito colorblind-safe palette, no chartjunk.
Outputs PDF+PNG to <paperdir>/figures/. Prints verification numbers that must match the paper.
"""
import csv
import itertools
import os
import sys
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Portable: works from a checkout (figures/make_figures.py) or a copy elsewhere.
_here = os.path.dirname(os.path.abspath(__file__))
PAPER = _here[:-len("/figures")] if _here.endswith("/figures") else os.getcwd()
FIGS = PAPER + "/figures"
os.makedirs(FIGS, exist_ok=True)
sys.path.insert(0, PAPER)
from survey_table import SURVEY  # noqa: E402

BLUE, ORANGE, VERM, GREY, SKY = "#0072B2", "#E69F00", "#D55E00", "#999999", "#56B4E9"

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight",
})


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(np.corrcoef(x, y)[0, 1])


def load_csv(name):
    """Read data/<name> as dict rows, skipping '#' comment lines."""
    with open(PAPER + "/data/" + name) as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def save(fig, name):
    fig.savefig(f"{FIGS}/{name}.pdf")
    fig.savefig(f"{FIGS}/{name}.png")
    plt.close(fig)
    print(f"saved {name}")


def make_fig1_roboworld_leverage():
    """Fig 1: RoboWorld Fig 9a scatter with and without PaliGemma Binning.

    Shows the leverage finding: r = 0.989 over all 8 policies falls to 0.798
    when the single high-leverage unit (hat value 0.978) is removed.
    """
    p9a = [r for r in load_csv("survey-roboworld.csv") if r["panel"].startswith("9a")]
    x = np.array([float(r["x_real"]) for r in p9a])
    y = np.array([float(r["y_sim"]) for r in p9a])
    names = [r["series"] for r in p9a]
    ib = names.index("PaliGemma Binning")
    mask = np.ones(len(x), bool); mask[ib] = False

    r_full = pearson(x, y)
    r_wo = pearson(x[mask], y[mask])
    print(f"VERIFY 9a: r_full={r_full:.4f} (paper 0.989)  r_without_Binning={r_wo:.4f} (paper 0.798)")

    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.scatter(x[mask], y[mask], s=38, color=BLUE, zorder=3, label="7 other policies")
    ax.scatter(x[ib], y[ib], s=70, color=VERM, marker="D", zorder=4, label="PaliGemma Binning")

    xs = np.linspace(x.min() - 40, x.max() + 40, 2)
    b1, a1 = np.polyfit(x, y, 1)
    b2, a2 = np.polyfit(x[mask], y[mask], 1)
    ax.plot(xs, b1 * xs + a1, color="black", lw=1.2, label=f"all 8 units:  r = {r_full:.3f}")
    ax.plot(xs, b2 * xs + a2, color=GREY, lw=1.2, ls="--", label=f"without Binning:  r = {r_wo:.3f}")

    ax.annotate("hat value 0.978\n(max possible 1.0)", xy=(x[ib], y[ib]),
                xytext=(x[ib] + 60, y[ib] + 0.28), fontsize=8, color=VERM,
                arrowprops=dict(arrowstyle="-", color=VERM, lw=0.8))
    ax.set_xlabel("RoboArena score (real)")
    ax.set_ylabel("RoboWorld GPT-4o score (sim)")
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    save(fig, "fig1_roboworld_9a_leverage")


def make_fig3_survey_k_dotplot():
    """Fig 3: dot plot of k (independent training units) across the 22 surveyed papers.

    Color-codes the permutation floor: k = 1 has no units to permute, k = 2-3
    cannot reach p = 0.05 (min p = 1/k!), k >= 4 can. Flags papers that print
    a p-value below their own permutation floor.
    """
    recs = []
    for p in SURVEY:
        name, k, flag, unc = p[0], p[2], p[3], p[5]
        recs.append((name + (" †" if flag else ""), k, unc))
    recs.sort(key=lambda t: (t[1], t[0].lower()))

    fig, ax = plt.subplots(figsize=(5.0, 4.6))
    ypos = np.arange(len(recs))
    for i, (label, k, unc) in enumerate(recs):
        if k == 1:
            c, m = GREY, "s"
        elif k <= 3:
            c, m = VERM, "o"
        else:
            c, m = BLUE, "o"
        ax.plot([0.6, k], [i, i], color="#DDDDDD", lw=0.8, zorder=1)
        ax.scatter([k], [i], s=42, color=c, marker=m, zorder=3)
        if unc is not None and unc.startswith("p") and k <= 3:  # p-value printed below its permutation floor
            ax.text(k + 0.35, i, "prints p < 0.001", va="center", fontsize=7, color=VERM)

    ax.axvline(3.5, color="black", lw=0.9, ls="--")
    ax.text(3.65, len(recs) - 0.4, "k ≥ 4 needed for any permutation\ntest to reach p ≤ 0.05  (min p = 1/k!)",
            fontsize=7.5, va="top")
    ax.set_yticks(ypos, [r[0] for r in recs], fontsize=7.5)
    ax.set_xlabel("independent training units behind the headline correlation (k)")
    ax.set_xlim(0.4, 19.5)
    ax.set_xticks([1, 2, 3, 4, 5, 8, 10, 18])
    handles = [
        Line2D([], [], color=GREY, marker="s", ls="", label="k = 1: single lineage — no units to permute"),
        Line2D([], [], color=VERM, marker="o", ls="", label="k = 2–3: p = 0.05 unreachable"),
        Line2D([], [], color=BLUE, marker="o", ls="", label="k ≥ 4: test possible"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=7.5, loc="lower right")
    save(fig, "fig3_survey_k_dotplot")
    n1 = sum(1 for _, k, _ in recs if k == 1); n23 = sum(1 for _, k, _ in recs if 2 <= k <= 3)
    print(f"VERIFY survey: n={len(recs)}  k=1: {n1} (paper: 6)  k=2-3: {n23} (paper: 9)")


def make_fig2_dc_bootstrap_comb():
    """Fig 2: the 35-atom cluster-bootstrap comb for Digital Cousins (k = 4).

    Enumerates all 4^4 = 256 cluster resamples, collapses them to their distinct
    r values (atoms), and overlays the smooth density a percentile CI presumes.
    Marks the 2.5% quantile to show how few resamples set the CI endpoint.
    """
    dc = load_csv("survey-digital-cousins.csv")
    pols = sorted(set(r["policy"] for r in dc))
    cl = {p: ([float(r["x_real"]) for r in dc if r["policy"] == p],
              [float(r["y_sim"]) for r in dc if r["policy"] == p]) for p in pols}
    r_dc = pearson([float(r["x_real"]) for r in dc], [float(r["y_sim"]) for r in dc])
    drops = [pearson(sum((cl[p][0] for p in pols if p != q), []), sum((cl[p][1] for p in pols if p != q), [])) for q in pols]
    print(f"VERIFY DC: pooled r={r_dc:.4f} (paper 0.9094)  max drop-one |dr|={max(abs(d - r_dc) for d in drops):.4f} (paper 0.013)")

    draws = []
    for tup in itertools.product(pols, repeat=4):
        xs_, ys_ = [], []
        for p in tup:
            xs_ += cl[p][0]; ys_ += cl[p][1]
        draws.append(pearson(xs_, ys_))
    draws = np.array(draws)
    atoms = Counter(np.round(draws, 10))
    n_multisets = len(set(tuple(sorted(t)) for t in itertools.product(range(4), repeat=4)))
    q025 = np.quantile(draws, 0.025)
    below = sum(m for v, m in atoms.items() if v < q025)
    print(f"VERIFY comb: distinct multisets={n_multisets} (<=35)  distinct r atoms={len(atoms)}  draws below 2.5% quantile={below}/256")

    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    vals = sorted(atoms)
    masses = np.array([atoms[v] / 256 for v in vals])
    ax.vlines(vals, 0, masses, color=BLUE, lw=1.6, label=f"attainable values ({len(atoms)} atoms)")

    # smooth density a reader would presume (KDE over the same draws), scaled to the plot
    kde_x = np.linspace(min(vals) - 0.05, 1.0, 400)
    bw = 0.02
    kde = np.exp(-0.5 * ((kde_x[:, None] - draws[None, :]) / bw) ** 2).sum(1)
    kde = kde / kde.max() * masses.max()
    ax.plot(kde_x, kde, color=GREY, ls="--", lw=1.1, label="the smooth density a percentile CI presumes")

    ax.axvline(q025, color=VERM, lw=0.9, ls=":")
    ax.text(q025, masses.max() * 1.02, f"2.5% cutoff:\n{below} of 256 resamples below", fontsize=7,
            color=VERM, ha="center", va="bottom")
    ax.set_xlabel("Pearson r of cluster-bootstrap resample  (Digital Cousins, k = 4 architectures)")
    ax.set_ylabel("probability mass")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    save(fig, "fig2_dc_bootstrap_comb")


if __name__ == "__main__":
    make_fig1_roboworld_leverage()
    make_fig3_survey_k_dotplot()
    make_fig2_dc_bootstrap_comb()
