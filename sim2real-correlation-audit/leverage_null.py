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

FIXED-X CONDITIONAL NULL (--fixed-x): the main table draws x from Gaussian
latents each replicate, so its percentiles mix "aberrant y-behavior" with
"unusual x-layout" -- RoboWorld 9a's isolated x-point (hat value 0.978) is
itself rare under a Gaussian x. The conditional mode holds the OBSERVED x
design fixed and resamples only y under a healthy linear relation fit to the
data: y*_i = a + b x_i + eps_i with (a, b) the OLS fit and eps either
parametric (iid N(0, sigma_hat^2), sigma_hat^2 = SS_res/(n-2)) or a residual
permutation (exchangeable observed residuals). Drop-one is over the same
independent units as the paper's table. P = fraction of replicates whose max
drop-one |delta r| >= the observed swing, computed from the released CSVs, not
hardcoded. This asks: GIVEN this x-layout, is the y-behavior surprising?

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
    with open(ROOT / "data" / "survey-molmospaces.csv") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            if row["task"] == "open":
                xs.append(float(row["sim_success_pct"]))
                ys.append(float(row["real_success_pct"]))
    return len(xs), float(np.corrcoef(xs, ys)[0, 1])


# --------------------------------------------------------------------------
# Fixed-x conditional null (--fixed-x): observed x design held fixed, y
# resampled under a healthy linear relation fit to the released data.
# (csv, filter column, filter value, x column, y column, unit column) per the
# unit choices of PAPER.md par.4.2 (RoboWorld/MolmoSpaces: unit = point;
# Cosmos: unit = training run; REALM: unit = policy).
FIXED_X_CASES = [
    ("RoboWorld 9a",        "survey-roboworld.csv", "panel", "9a_GPT-4o_score",
     "x_real", "y_sim", "series"),
    ("RoboWorld 9b",        "survey-roboworld.csv", "panel", "9b_Gemini-2.5-Flash_score",
     "x_real", "y_sim", "series"),
    ("RoboWorld 10b",       "survey-roboworld.csv", "panel", "10b_Gemini-2.5-Flash_success_rate",
     "x_real", "y_sim", "series"),
    ("Cosmos-Surg manual",  "survey-cosmos-surg-dvrk.csv", "panel", "manual_human_vs_dvrk",
     "x_real", "y_sim", "unit"),
    ("MolmoSpaces open",    "survey-molmospaces.csv", "task", "open",
     "sim_success_pct", "real_success_pct", "policy"),
    ("REALM Default",       "survey-realm.csv", "panel", "Default",
     "x_real", "y_sim", "policy"),
    ("REALM V-VIEW",        "survey-realm.csv", "panel", "V-VIEW",
     "x_real", "y_sim", "policy"),
    # 2026-07-21 Search-3 additions; unit column None = drop single points (rows).
    ("VISER OpenVLA",       "survey-viser.csv", "policy", "OpenVLA",
     "real_sr", "sim_ours_sr", None),
    ("WM-PolicyEval Cosmos", "survey-wm-policyeval.csv", "world_model", "Cosmos",
     "actual_success_rate", "predicted_success_rate", None),
    ("WM-PolicyEval IRASim", "survey-wm-policyeval.csv", "world_model", "IRASim",
     "actual_success_rate", "predicted_success_rate", None),
]


def load_fixed_x_case(fname, fcol, fval, xcol, ycol, ucol):
    """Return (x, y, unit index array, unit names) from a released CSV."""
    xs, ys, us = [], [], []
    with open(ROOT / "data" / fname) as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            if row[fcol] == fval:
                xs.append(float(row[xcol]))
                ys.append(float(row[ycol]))
                us.append(row[ucol] if ucol is not None else str(len(us)))
    names = sorted(set(us))
    idx = np.array([names.index(u) for u in us])
    return np.array(xs), np.array(ys), idx, names


def observed_max_dr(x, y, idx, n_units):
    """Observed pooled r, max drop-one |delta r| over units, worst unit index."""
    r = float(np.corrcoef(x, y)[0, 1])
    dr = np.array([abs(r - np.corrcoef(x[idx != u], y[idx != u])[0, 1])
                   for u in range(n_units)])
    return r, float(dr.max()), int(dr.argmax())


def fixed_x_null(x, y, idx, nsim, seed, variant):
    """Max drop-one |delta r| under the conditional null, x held at observed.

    variant 'parametric':  eps ~ iid N(0, sigma_hat^2), sigma_hat^2 = SS_res/(n-2)
    variant 'permutation': eps = a fresh permutation of the observed residuals
    Returns max_dr, shape (nsim,).
    """
    n, k = len(x), idx.max() + 1
    xb, yb = x.mean(), y.mean()
    b = float(((x - xb) * (y - yb)).sum() / ((x - xb) ** 2).sum())
    a = yb - b * xb
    resid = y - (a + b * x)
    rng = np.random.default_rng((BASE_SEED, seed))
    if variant == "parametric":
        sigma = np.sqrt((resid ** 2).sum() / (n - 2))
        eps = rng.standard_normal((nsim, n)) * sigma
    else:
        eps = rng.permuted(np.broadcast_to(resid, (nsim, n)), axis=1)
    ystar = a + b * x + eps                                     # (nsim, n)

    memb = (idx[None, :] == np.arange(k)[:, None]).astype(float).T  # (n, k)
    sx, sxx = x.sum(), (x * x).sum()
    ux, uxx = x @ memb, (x * x) @ memb                          # (k,) fixed
    sy, syy = ystar.sum(axis=1), (ystar ** 2).sum(axis=1)       # (nsim,)
    sxy = ystar @ x
    uy, uyy = ystar @ memb, (ystar ** 2) @ memb                 # (nsim, k)
    uxy = ystar @ (x[:, None] * memb)
    n2 = n - memb.sum(axis=0)                                   # (k,)

    r_pool = _pearson_from_sums(sx, sy, sxx, syy, sxy, n)
    r_loo = _pearson_from_sums(sx - ux, sy[:, None] - uy, sxx - uxx,
                               syy[:, None] - uyy, sxy[:, None] - uxy, n2)
    return np.abs(r_pool[:, None] - r_loo).max(axis=1)


def run_fixed_x(nsim):
    out = []
    for ci, (name, fname, fcol, fval, xcol, ycol, ucol) in enumerate(FIXED_X_CASES):
        x, y, idx, names = load_fixed_x_case(fname, fcol, fval, xcol, ycol, ucol)
        r, obs, worst = observed_max_dr(x, y, idx, len(names))
        row = dict(name=name, n=len(x), k=len(names), r=r, obs=obs,
                   worst=names[worst])
        for vi, variant in enumerate(("parametric", "permutation")):
            mx = fixed_x_null(x, y, idx, nsim, seed=5000 + 10 * ci + vi, variant=variant)
            row["med_" + variant] = float(np.median(mx))
            row["p_" + variant] = float(np.mean(mx >= obs))
        out.append(row)
    return out


def print_fixed_x(rows, nsim):
    print(f"FIXED-X CONDITIONAL NULL  ({nsim:,} reps/cell; observed x design "
          f"held fixed, y resampled\nfrom the OLS fit; P = fraction of "
          f"replicates with max drop-one |dr| >= observed)")
    hdr = (f"{'case':<19} {'n':>3} {'k':>2} {'obs r':>6} {'obs max|dr|':>11} "
           f"{'worst unit':<18} | {'P param':>8} {'med':>6} | {'P perm':>8} {'med':>6}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['name']:<19} {r['n']:>3} {r['k']:>2} {r['r']:>6.3f} "
              f"{r['obs']:>11.3f} {r['worst']:<18} | "
              f"{r['p_parametric']:>8.4f} {r['med_parametric']:>6.3f} | "
              f"{r['p_permutation']:>8.4f} {r['med_permutation']:>6.3f}")
    print("Units per PAPER.md par.4.2 (RoboWorld/MolmoSpaces: point; Cosmos: "
          "training run; REALM: policy).\n")


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
        # 2026-07-21 Search-3 additions (drop-one over single points, m=1)
        ("VISER OpenVLA",           0.85,  5, 1,    0.135),
        ("WM-PolicyEval Cosmos",    0.719, 12, 1,   0.260),
        ("WM-PolicyEval IRASim",    0.277, 12, 1,   0.176),
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
    ap.add_argument("--fixed-x", action="store_true",
                    help="run only the fixed-x conditional null (observed x "
                         "design held fixed, y resampled from the OLS fit; "
                         "parametric and residual-permutation variants) for "
                         "the seven par.4.2 firings and exit")
    args = ap.parse_args()
    if args.quick:
        NSIM, GATE_NSIM, CAL_NSIM = 2_000, 4_000, 1_000
        tol_p, tol_med = GATE_TOL_P_Q, GATE_TOL_MED_Q
    else:
        tol_p, tol_med = GATE_TOL_P, GATE_TOL_MED

    if args.fixed_x:
        print_fixed_x(run_fixed_x(NSIM), NSIM)
        return

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
