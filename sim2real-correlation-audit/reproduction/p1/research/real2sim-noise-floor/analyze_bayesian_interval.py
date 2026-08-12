#!/usr/bin/env python3
"""The Bayesian interval SS6.1 claims remains valid at k = 4 -- computed, not asserted.

Posterior for the unit-level correlation rho with a uniform prior on [-1, 1], using the
exact small-sample density of the Pearson r for a bivariate-normal sample (Fisher 1915;
hypergeometric form as in Hotelling 1953):

    p(r | rho, n) prop. (1-rho^2)^((n-1)/2) (1-r^2)^((n-4)/2) (1-rho*r)^(-(n-3/2))
                       * 2F1(1/2, 1/2; n-1/2; (1+rho*r)/2)

Aggregation matches SS6.1's recommended convention: checkpoints are averaged to their
per-run means, so n = k = 4 policies per task. Equal-tailed 95% credible interval from
numerical integration on a rho grid.

Usage: python analyze_bayesian_interval.py
"""
from __future__ import annotations
import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import hyp2f1
from scipy.stats import pearsonr

DATA = (
    Path(__file__).resolve().parents[1]
    / "corpus-reporting-audit"
    / "sources"
    / "source-real2sim-eval-fig3-checkpoints.csv"
)
GRID = np.linspace(-0.999999, 0.999999, 400001)


def r_density(r: float, rho: np.ndarray, n: int) -> np.ndarray:
    """Exact density of the sample correlation r given rho, up to a rho-free constant."""
    return ((1 - rho**2) ** ((n - 1) / 2)
            * (1 - rho * r) ** (-(n - 1.5))
            * hyp2f1(0.5, 0.5, n - 0.5, (1 + rho * r) / 2))


def posterior_interval(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if not math.isfinite(r) or not -1 <= r <= 1:
        raise ValueError("r must be finite and lie in [-1, 1]")
    if type(n) is not int or n < 3:
        raise ValueError("n must be an integer of at least 3")
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and lie strictly between 0 and 1")
    post = r_density(r, GRID, n)          # uniform prior: posterior prop. likelihood
    if not np.all(np.isfinite(post)):
        raise ValueError("posterior density is not finite")
    cdf = np.cumsum(post)
    if not math.isfinite(float(cdf[-1])) or cdf[-1] <= 0:
        raise ValueError("posterior density has no positive finite mass")
    cdf /= cdf[-1]
    lo = GRID[np.searchsorted(cdf, alpha / 2)]
    hi = GRID[np.searchsorted(cdf, 1 - alpha / 2)]
    return float(lo), float(hi)


def unit_level_r() -> dict[str, float]:
    rows = defaultdict(lambda: defaultdict(list))
    with open(DATA) as f:
        for row in csv.DictReader(l for l in f if not l.startswith("#")):
            rows[row["task"]][row["policy"]].append(
                (float(row["real_success"]), float(row["sim_success"])))
    out = {}
    for task, pols in rows.items():
        means = [(np.mean([p[0] for p in v]), np.mean([p[1] for p in v]))
                 for v in pols.values()]
        out[task] = float(pearsonr([m[0] for m in means], [m[1] for m in means])[0])
    return out


if __name__ == "__main__":
    print("Equal-tailed 95% posterior credible intervals for rho, uniform prior, n = k = 4")
    print("(unit-level r over per-run means, the aggregation SS6.1 recommends)\n")
    for task, r in sorted(unit_level_r().items()):
        lo, hi = posterior_interval(r, 4)
        print(f"  {task:6s}  r = {r:+.3f}   95% credible [{lo:+.3f}, {hi:+.3f}]")
