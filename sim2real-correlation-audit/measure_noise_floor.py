#!/usr/bin/env python3
"""A1a — noise-floor characterisation of the sim-real correlation (arXiv:2511.04665v2).

Implements PREREG-noise-floor.md v1.0 EXACTLY. Read that first; it states what this
analysis deliberately cannot do (no MDE, no calibrated CI, no p-value, no delta claim).

Three outputs, per PREREG §5:
  5.1  per-task Pearson r, with a HALT gate if it fails to reproduce Table I
  5.2  drop-one-cell fragility range          <- PRIMARY (no distributional assumption)
  5.3  specification curve across cluster units, explicitly NOT calibrated

Sim-side noise is NOT modelled (PREREG §6): the naive Bin(n, p_hat) redraw double-counts
noise and attenuates r (measured: toy -0.131, rope -0.044, T -0.124). Every interval here is
therefore a LOWER BOUND on uncertainty.

  python measure_noise_floor.py --data data/real2sim-eval-fig3-checkpoints.csv --out .
"""
import argparse, csv, json, sys
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr

# Preregistered BEFORE running (PREREG §5.3)
SEED = 0
N_REPLICATES = 8000
REPRO_TOL = 0.001                                   # §5.1 halt gate
TABLE_I = {"sloth": 0.944, "rope": 0.901, "T": 0.915}
EPISODES = {"sloth": 20, "rope": 27, "T": 16}
LABEL = {"sloth": "toy packing", "rope": "rope routing", "T": "T-block pushing"}


def load(path):
    rows = [r for r in csv.DictReader(l for l in open(path) if not l.startswith("#"))]
    by = {}
    for r in rows:
        by.setdefault(r["task"], []).append(r)
    return by


def arrays(recs, task):
    """Integer successes -> proportions. Uses the recovered integer counts, not the percentages."""
    n = EPISODES[task]
    rk = np.array([int(x["real_successes"]) for x in recs], float)
    sk = np.array([int(x["sim_successes"]) for x in recs], float)
    return rk / n, sk / n


# IMPLEMENTS R4
def drop_one_cell(recs, task):
    """PRIMARY (§5.2). Recompute r with each (task,policy) cell removed in turn.

    With 4 cells this yields exactly 4 numbers -- a RANGE, not a distribution. It supports no
    variance estimate and therefore no MDE or CI. That limitation is preregistered, not a
    shortcoming of this implementation."""
    cells = sorted({x["policy"] for x in recs})
    out = {}
    for c in cells:
        keep = [x for x in recs if x["policy"] != c]
        if len({x["policy"] for x in keep}) < 2:
            continue
        a, b = arrays(keep, task)
        out[c] = float(pearsonr(a, b)[0]) if a.std() and b.std() else float("nan")
    return out, cells


def cell_support_exact(recs, task):
    """EXACT enumeration of the cell-resampling distribution (added v1.1 after audit).

    Drawing k cells with replacement from k cells gives k**k ordered draws, and Pearson r
    depends only on the multiset -- so the distribution has a small, FINITE support (35 distinct
    values at k=4). The 8000-replicate Monte Carlo in spec_curve() was a stochastic approximation
    to a quantity computable exactly, and it reproduced this enumeration bit-for-bit.

    Reporting a '95% percentile interval' over 35 atoms overstates precision: the 2.5th percentile
    is not estimable when the smallest atom carries p=1/256 and the tail is 4-6 atoms wide. Worse,
    an atom can straddle the 0.025 cutoff -- sloth's lower bound alternates 0.798 <-> 0.821 on the
    SEED ALONE. This function returns the support so that fact is visible instead of hidden."""
    n = EPISODES[task]
    cells = {}
    for i, x in enumerate(recs):
        cells.setdefault(x["policy"], []).append(i)
    keys = sorted(cells)
    rk = np.array([int(x["real_successes"]) for x in recs])
    sk = np.array([int(x["sim_successes"]) for x in recs])
    from itertools import product
    vals = {}
    for draw in product(range(len(keys)), repeat=len(keys)):
        idx = np.concatenate([cells[keys[j]] for j in draw])
        a, b = rk[idx] / n, sk[idx] / n
        if a.std() == 0 or b.std() == 0:
            continue
        r = round(float(pearsonr(a, b)[0]), 12)
        vals[r] = vals.get(r, 0) + 1
    total = sum(vals.values())
    atoms = sorted(vals.items())
    # degenerate draws: all k picks the same cell -- not a plausible resample of a k-policy study
    degen = sum(1 for d in product(range(len(keys)), repeat=len(keys)) if len(set(d)) == 1)
    return {"n_atoms": len(atoms), "n_draws": total, "degenerate_draws": degen,
            "min": atoms[0][0], "max": atoms[-1][0],
            "support": [{"r": r, "p": c / total} for r, c in atoms]}


# IMPLEMENTS R5
def spec_curve(recs, task, rng):
    """§5.3. Percentile intervals under three resampling units.

    NOT CALIBRATED -- coverage at k=4 clusters could not be certified (PREREG §2).
    Reported as a range across specifications, never as a single selected interval.

    ⚠️ For unit='cell' this is SUPERSEDED by cell_support_exact(): the distribution has only 35
    atoms, so these percentiles are lattice points, not estimates. Retained to document what the
    preregistered procedure produced."""
    n = EPISODES[task]
    rk = np.array([int(x["real_successes"]) for x in recs])
    sk = np.array([int(x["sim_successes"]) for x in recs])
    cells = {}
    for i, x in enumerate(recs):
        cells.setdefault(x["policy"], []).append(i)
    keys = list(cells)

    res = {}
    for unit in ("none", "checkpoint", "cell"):
        draws = []
        for _ in range(N_REPLICATES):
            if unit == "none":
                idx = np.arange(len(recs))
                a = rng.binomial(n, rk[idx] / n) / n      # real axis only (§6)
                b = sk[idx] / n
            elif unit == "checkpoint":
                idx = rng.integers(0, len(recs), len(recs))
                a, b = rk[idx] / n, sk[idx] / n
            else:                                          # cell = (task x policy)
                pick = rng.choice(keys, len(keys), replace=True)
                idx = np.concatenate([cells[k] for k in pick])
                a, b = rk[idx] / n, sk[idx] / n
            if a.std() == 0 or b.std() == 0:
                continue                                   # degenerate replicate, dropped (§ Q2 open)
            draws.append(pearsonr(a, b)[0])
        d = np.array(draws)
        lo, hi = np.percentile(d, [2.5, 97.5])
        res[unit] = {"lo": float(lo), "hi": float(hi), "width": float(hi - lo),
                     "n_valid": int(len(d)), "n_dropped": int(N_REPLICATES - len(d))}
    return res


# IMPLEMENTS R1
def comparison_arm(root=Path(__file__).resolve().parents[1]):
    """PREREG §3 requirement 1 -- the eyeballed-data comparison arm.

    The eyeballed file has no sim column, so a correlation from it REQUIRES a stated pairing
    rule (recorded in that file's header): real_success from real_ground_truth.csv paired against
    paper_sim from fig3_digitized_reference.csv on (task, policy).

    Both arms are then restricted to best-checkpoint-per-policy so they are comparable -- which
    also isolates the finding: any divergence is a SELECTION-RULE effect, not a provenance one,
    because the extracted arm is computed from the same file as the primary analysis."""
    h = root / "harness"
    try:
        real = {(r["task"], r["policy"]): float(r["real_success"])
                for r in csv.DictReader(l for l in open(h / "real_ground_truth.csv")
                                        if not l.startswith("#"))}
        sim = {(r["task"], r["policy"]): float(r["paper_sim"])
               for r in csv.DictReader(l for l in open(h / "fig3_digitized_reference.csv")
                                       if not l.startswith("#"))}
        ext = [r for r in csv.DictReader(l for l in open(Path(__file__).parent /
                                                        "data/real2sim-eval-fig3-checkpoints.csv")
                                         if not l.startswith("#"))]
    except FileNotFoundError as e:
        return {"error": f"comparison arm inputs missing: {e}"}

    out = {}
    for task in ("sloth", "rope", "T"):
        keys = [k for k in real if k[0] == task and k in sim]
        eye = float(pearsonr([real[k] for k in keys], [sim[k] for k in keys])[0]) if len(keys) >= 3 else None
        # extracted arm, same best-checkpoint selection rule
        best = {}
        for x in (r for r in ext if r["task"] == task):
            p = x["policy"]; v = float(x["real_success"])
            if p not in best or v > best[p][0]:
                best[p] = (v, float(x["sim_success"]))
        ex = float(pearsonr([v[0] for v in best.values()], [v[1] for v in best.values()])[0]) \
            if len(best) >= 3 else None
        out[task] = {"eyeballed_best_ckpt_r": eye, "extracted_best_ckpt_r": ex,
                     "n_points": len(keys)}
    out["_pairing_rule"] = ("eyeballed: real_ground_truth.csv real_success x "
                            "fig3_digitized_reference.csv paper_sim, joined on (task, policy)")
    out["_interpretation"] = ("Both arms use best-checkpoint-per-policy (n=4). Divergence from the "
                              "all-checkpoint primary is therefore a SELECTION-RULE effect, not a "
                              "digitization/provenance effect.")
    return out


# IMPLEMENTS R2
def toy_robustness(recs):
    """PREREG §3 requirement 2 -- toy 15/16/17 checkpoint robustness ("never silently pick one").

    The toy episode count disagrees three ways: appendix text 16, Table VIII 15, extracted 17.
    17 is primary because it reproduces the printed r=0.944 -- but that makes the reproduction
    gate circular for toy, so the alternatives must be reported, not assumed away.

    For k < 17 there is no principled rule for WHICH checkpoints to drop, so this reports the
    full range over all subsets of that size. A range is honest; a single number would not be."""
    if not recs:
        return {}
    n = EPISODES["sloth"]
    rk = np.array([int(x["real_successes"]) for x in recs])
    sk = np.array([int(x["sim_successes"]) for x in recs])
    out = {}
    for k in (15, 16, 17):
        if k > len(recs):
            continue
        rs = []
        for keep in combinations(range(len(recs)), k):
            a, b = rk[list(keep)] / n, sk[list(keep)] / n
            if a.std() and b.std():
                rs.append(float(pearsonr(a, b)[0]))
        passing = [r for r in rs if abs(r - TABLE_I["sloth"]) <= REPRO_TOL]
        out[str(k)] = {"n_subsets": len(rs), "r_min": min(rs), "r_max": max(rs),
                       "n_passing_repro_gate": len(passing),
                       "note": ("primary; the only subset is the full set" if k == 17 else
                                f"{len(passing)}/{len(rs)} subsets also clear the <=0.001 gate")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="report_a1a")
    ap.add_argument("--label", default="extracted")
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    by = load(args.data)
    result = {"source": args.data, "label": args.label, "seed": SEED,
              "replicates": N_REPLICATES, "sim_side_noise_modelled": False,
              "intervals_are_calibrated": False, "tasks": {}}

    print(f"=== Noise floor ({args.label}) per PREREG-noise-floor.md ===\n")
    halt = []
    for task in ("sloth", "rope", "T"):
        recs = by.get(task, [])
        if len(recs) < 3:
            print(f"[skip] {task}: {len(recs)} rows"); continue
        a, b = arrays(recs, task)
        r = float(pearsonr(a, b)[0])

        # §5.1 halt gate -- a stopping rule, NOT a tuning opportunity
        published = TABLE_I[task]
        delta = abs(r - published)
        gate = delta <= REPRO_TOL   # IMPLEMENTS R3
        if not gate:
            halt.append(f"{task}: r={r:.4f} vs published {published} (delta {delta:.4f} > {REPRO_TOL})")

        drops, cells = drop_one_cell(recs, task)
        vals = [v for v in drops.values() if not np.isnan(v)]
        spec = spec_curve(recs, task, rng)
        exact = cell_support_exact(recs, task)

        result["tasks"][task] = {
            "label": LABEL[task], "n_checkpoints": len(recs), "n_cells": len(cells),
            "episodes_per_checkpoint": EPISODES[task],
            "r": r, "published_r": published, "repro_delta": delta, "repro_gate_passed": bool(gate),
            "drop_one": {"per_cell": drops, "min": min(vals), "max": max(vals),
                         "swing": max(vals) - min(vals)},
            "specification_curve": spec,
            # v1.1: the cell branch's exact finite support. Supersedes spec["cell"].
            "cell_exact_support": exact,
        }
        print(f"{LABEL[task]:18s} r={r:.4f}  (Table I {published}, delta {delta:.4f}) "
              f"{'OK' if gate else 'GATE FAILED'}")
        print(f"  drop-one-cell : [{min(vals):.3f}, {max(vals):.3f}]  swing={max(vals)-min(vals):.3f}"
              f"   <- PRIMARY, {len(cells)} cells")
        for u in ("none", "checkpoint", "cell"):
            s = spec[u]
            note = "  <- SUPERSEDED, see exact support" if u == "cell" else ""
            print(f"  spec[{u:10s}]: [{s['lo']:.3f}, {s['hi']:.3f}]  width={s['width']:.3f}"
                  f"  (dropped {s['n_dropped']}){note}")
        print(f"  cell EXACT   : {exact['n_atoms']} atoms over {exact['n_draws']} draws, "
              f"support [{exact['min']:.3f}, {exact['max']:.3f}], "
              f"{exact['degenerate_draws']} degenerate (one cell x{len(cells)})")
        print()

    # PREREG §3 requirement 1: the eyeballed comparison arm. v1.0 skipped this SILENTLY while
    # reporting an empty halt list -- the prereg said "both are run" but the script was built
    # around integer count columns the eyeballed file does not have. Now implemented.
    result["comparison_arm"] = comparison_arm()

    # PREREG §3 requirement 2: toy 15/16 robustness rows ("never silently pick one").
    # v1.0 hardcoded 17 with no mechanism for the alternatives. Now implemented.
    result["toy_checkpoint_robustness"] = toy_robustness(by.get("sloth", []))

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    result["halt_triggered"] = bool(halt)
    result["halt_reasons"] = halt
    result["prereg_requirements_unmet"] = []   # both §3 requirements now implemented (v1.2)
    result["prereg_requirements_run"] = ["R1", "R2", "R3", "R4", "R5"]
    (outdir / "results.json").write_text(json.dumps(result, indent=2))

    if halt:
        print("!! PREREG ISSUES:")
        for h in halt:
            print("   -", h)
    print(f"\nWrote {outdir}/results.json")
    print("REMINDER: intervals are NOT calibrated and sim-side noise is NOT modelled (§2, §6).")
    print("Every uncertainty figure here is a LOWER BOUND.")


if __name__ == "__main__":
    main()
