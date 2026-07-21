"""Null calibration for the drop-one leverage check (PAPER.md par.4, par.4.2).

The leverage check computes max_u |r - r_(-u)| over unit deletions and flags at
> 0.10. This script quantifies how often a HEALTHY design -- no aberrant unit,
every unit exchangeable -- exceeds a given drop-one swing, so each observed
firing in the par.4.2 table can be reported as a percentile of its own null
rather than a binary flag.

Generative model (fz_coverage.py's cluster style): k units; unit-level latents
(a_u, b_u) ~ BVN(0, corr rho_unit, var w); each unit contributes m points =
latent + iid within-unit noise (independent in x and y) with var 1 - w, so the
"cluster share" w is the fraction of total variance that is between-unit.
w = 1.0 with m = 1 is the pure one-point-per-unit case. Pooled Pearson r is
over all k*m points; drop-one removes ALL m points of a unit; the statistic is
max_u |r_pooled - r_(-u)|.

For the main table rho_unit is CALIBRATED (bisection, common random numbers) so
the median pooled r across replicates matches the target printed r; when w < 1
attenuates the pooled correlation below the target even at rho_unit -> 1, the
boundary value is used and flagged "capped" -- the achieved median is reported
either way. GATE MODE (--gate-only also available) uses the exact reference
convention instead: m = 1, w = 1.0, FIXED rho (no calibration), checked against
independently computed 40,000-rep reference values before anything else runs.

Runnable end-to-end; numpy only; seed fixed (default_rng, per-cell seeds).
Defaults: 40,000 gate reps, 200,000 reps per table cell, 20,000-rep calibration.
--quick cuts these to 4,000 / 2,000 / 1,000 (faster, noisier; loosened gate
tolerances; paper numbers use the default).
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

BASE_SEED = 20260721
ROOT = Path(__file__).resolve().parent

NSIM = 200_000       # replicates per main-table cell (converged at the 3rd decimal)
GATE_NSIM = 40_000   # gate mode (matches the reference computation)
CAL_NSIM = 20_000    # replicates per calibration evaluation
CAL_ITERS = 30
RHO_MAX = 0.999999
FLAG = 0.10
CLUSTER_SHARES = (1.0, 0.8, 0.5)

# Gate references: independently computed, 40,000 reps, m=1, w=1.0, fixed rho.
#            name                        k   rho    obs     ref_P  ref_med
GATE_REFS = [("RoboWorld 9a",            8, 0.989, 0.191, 0.002, 0.007),
             ("Digital Cousins (k=4)",   4, 0.909, 0.013, 0.868, 0.097),
             ("Cosmos manual (k=3)",     3, 0.718, 0.124, 0.603, 1.036)]
GATE_TOL_P, GATE_TOL_MED = 0.010, 0.030            # full-rep tolerances
GATE_TOL_P_Q, GATE_TOL_MED_Q = 0.030, 0.100        # --quick tolerances


def _pearson_from_sums(sx, sy, sxx, syy, sxy, n):
    num = sxy - sx * sy / n
    var_x = sxx - sx**2 / n
    var_y = syy - sy**2 / n
    den = np.sqrt(np.maximum(var_x * var_y, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)
    return np.clip(r, -1.0, 1.0)


def simulate_max_dr(nsim, k, m, rho_unit, w, seed):
    """Simulate the healthy design; return (pooled r, max_u |delta r|), each (nsim,)."""
    rng = np.random.default_rng((BASE_SEED, seed))
    sd_u, sd_e = np.sqrt(w), np.sqrt(1.0 - w)
    z1 = rng.standard_normal((nsim, k))
    z2 = rng.standard_normal((nsim, k))
    a = z1 * sd_u
    b = (rho_unit * z1 + np.sqrt(1.0 - rho_unit**2) * z2) * sd_u
    x = a[:, :, None] + rng.standard_normal((nsim, k, m)) * sd_e
    y = b[:, :, None] + rng.standard_normal((nsim, k, m)) * sd_e

    n, n2 = k * m, (k - 1) * m
    ux, uy = x.sum(axis=2), y.sum(axis=2)                       # (nsim, k) unit sums
    uxx, uyy = (x * x).sum(axis=2), (y * y).sum(axis=2)
    uxy = (x * y).sum(axis=2)
    sx, sy = ux.sum(axis=1), uy.sum(axis=1)                     # (nsim,) totals
    sxx, syy, sxy = uxx.sum(axis=1), uyy.sum(axis=1), uxy.sum(axis=1)

    r_pool = _pearson_from_sums(sx, sy, sxx, syy, sxy, n)
    r_loo = _pearson_from_sums(sx[:, None] - ux, sy[:, None] - uy,
                               sxx[:, None] - uxx, syy[:, None] - uyy,
                               sxy[:, None] - uxy, n2)
    max_dr = np.abs(r_pool[:, None] - r_loo).max(axis=1)
    return r_pool, max_dr


def calibrate_rho_unit(target, k, m, w, nsim, seed):
    """Bisect rho_unit so median pooled r ~= target (common random numbers).

    Returns (rho_unit, capped): capped=True when w attenuates the pooled
    correlation below the target even at rho_unit -> 1.
    """
    def med(rho):
        r_pool, _ = simulate_max_dr(nsim, k, m, rho, w, seed)
        return float(np.median(r_pool))

    if med(RHO_MAX) <= target:
        return RHO_MAX, True
    lo, hi = 0.0, RHO_MAX
    for _ in range(CAL_ITERS):
        mid = 0.5 * (lo + hi)
        if med(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), False


def molmospaces_open():
    """(n_points, pearson r) of the MolmoSpaces open panel, from the released CSV."""
    xs, ys = [], []
    with open(ROOT / "data" / "molmospaces.csv") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            if row["task"] == "open":
                xs.append(float(row["sim_success_pct"]))
                ys.append(float(row["real_success_pct"]))
    return len(xs), float(np.corrcoef(xs, ys)[0, 1])


def build_cases():
    """(name, target printed r, k, m, observed max |delta r|)."""
    k_mo, r_mo = molmospaces_open()
    return [
        ("RoboWorld Fig 9a",        0.989, 8, 1,    0.191),
        ("Digital Cousins",         0.909, 4, 4,    0.013),
        ("Cosmos-Surg-dVRK manual", 0.718, 3, 8,    0.124),
        ("MolmoSpaces open",        r_mo,  k_mo, 1, 0.617),
        ("REALM Default",           0.88,  3, 7,    0.135),
        ("REALM V-VIEW",            0.89,  3, 5,    0.168),   # 14 pts / 3 policies -> m ~= 5
    ]


def run_gate(nsim, tol_p, tol_med):
    """Reference-convention check. Returns (rows, all_ok)."""
    rows, ok = [], True
    for i, (name, k, rho, obs, ref_p, ref_med) in enumerate(GATE_REFS):
        _, mx = simulate_max_dr(nsim, k, 1, rho, 1.0, seed=1000 + i)
        p = float(np.mean(mx >= obs))
        med = float(np.median(mx))
        good = abs(p - ref_p) <= tol_p and abs(med - ref_med) <= tol_med
        ok &= good
        rows.append((name, k, rho, obs, p, ref_p, med, ref_med, good))
    return rows, ok


def print_gate(rows, nsim):
    print(f"VALIDATION GATE  (m=1, w=1.0, fixed rho, {nsim:,} reps; "
          f"reference used 40,000)")
    hdr = (f"{'case':<22} {'k':>2} {'rho':>6} {'obs':>6} | "
           f"{'P(>=obs)':>8} {'ref_P':>6} | {'med':>6} {'ref':>6} | ok")
    print(hdr)
    print("-" * len(hdr))
    for name, k, rho, obs, p, ref_p, med, ref_med, good in rows:
        print(f"{name:<22} {k:>2} {rho:>6.3f} {obs:>6.3f} | "
              f"{p:>8.4f} {ref_p:>6.3f} | {med:>6.3f} {ref_med:>6.3f} | "
              f"{'PASS' if good else 'FAIL'}")
    print()


def run_cases(nsim, cal_nsim):
    out = []
    for ci, (name, target, k, m, obs) in enumerate(build_cases()):
        for wi, w in enumerate(CLUSTER_SHARES):
            rho, capped = calibrate_rho_unit(target, k, m, w, cal_nsim,
                                             seed=2000 + 10 * ci + wi)
            r_pool, mx = simulate_max_dr(nsim, k, m, rho, w,
                                         seed=3000 + 10 * ci + wi)
            out.append(dict(name=name, target=target, k=k, m=m, obs=obs, w=w,
                            rho=rho, capped=capped,
                            med_r=float(np.median(r_pool)),
                            med_mx=float(np.median(mx)),
                            p=float(np.mean(mx >= obs))))
    return out


def print_cases(rows, nsim):
    print(f"NULL CALIBRATION  ({nsim:,} reps/cell; P = fraction of healthy-design "
          f"replicates with max|dr| >= observed)")
    hdr = (f"{'case':<24} {'k':>2} {'m':>2} {'target':>6} {'w':>4} {'rho_u':>7} "
           f"{'med r':>6} {'med max|dr|':>11} {'obs':>6} {'P(null>=obs)':>12}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        cap = "*" if r["capped"] else " "
        print(f"{r['name']:<24} {r['k']:>2} {r['m']:>2} {r['target']:>6.3f} "
              f"{r['w']:>4.1f} {r['rho']:>6.4f}{cap} {r['med_r']:>6.3f} "
              f"{r['med_mx']:>11.3f} {r['obs']:>6.3f} {r['p']:>12.4f}")
    print("* rho_unit capped at boundary: target median r unreachable at this "
          "cluster share; achieved median reported.\n")


def run_general(nsim):
    out = []
    for i, k in enumerate((4, 6, 8, 12, 16)):
        for j, rho in enumerate((0.5, 0.9)):
            _, mx = simulate_max_dr(nsim, k, 1, rho, 1.0, seed=4000 + 10 * i + j)
            out.append((k, rho, float(np.mean(mx > FLAG))))
    return out


def print_general(rows, nsim):
    print(f"P(max|dr| > {FLAG})  for a healthy design, m=1, w=1.0, fixed rho "
          f"({nsim:,} reps) -- the flag partly measures smallness:")
    ks = sorted({k for k, _, _ in rows})
    rhos = sorted({rho for _, rho, _ in rows})
    print(f"{'k':>4} | " + " ".join(f"rho={rho:<4}" for rho in rhos))
    print("-" * (7 + 9 * len(rhos)))
    lut = {(k, rho): p for k, rho, p in rows}
    for k in ks:
        print(f"{k:>4} | " + " ".join(f"{lut[(k, rho)]:>8.4f}" for rho in rhos))
    print()


def main():
    global NSIM, GATE_NSIM, CAL_NSIM
    ap = argparse.ArgumentParser(
        description="Null calibration for the drop-one leverage check "
                    "(healthy-design percentiles for observed max |delta r|). "
                    "See module docstring.")
    ap.add_argument("--quick", action="store_true",
                    help="4,000 gate / 2,000 cell / 1,000 calibration reps "
                         "instead of 40,000 / 20,000 / 5,000 (faster, noisier; "
                         "paper numbers use the default)")
    ap.add_argument("--gate-only", action="store_true",
                    help="run only the validation gate and exit")
    args = ap.parse_args()
    if args.quick:
        NSIM, GATE_NSIM, CAL_NSIM = 2_000, 4_000, 1_000
        tol_p, tol_med = GATE_TOL_P_Q, GATE_TOL_MED_Q
    else:
        tol_p, tol_med = GATE_TOL_P, GATE_TOL_MED

    gate_rows, gate_ok = run_gate(GATE_NSIM, tol_p, tol_med)
    print_gate(gate_rows, GATE_NSIM)
    if not gate_ok:
        print("GATE FAILED: simulated null does not reproduce the reference "
              "values within tolerance. Stopping -- do not tune. See rows "
              "marked FAIL above.")
        sys.exit(1)
    if args.gate_only:
        return

    print_cases(run_cases(NSIM, CAL_NSIM), NSIM)
    print_general(run_general(NSIM), NSIM)


if __name__ == "__main__":
    main()
