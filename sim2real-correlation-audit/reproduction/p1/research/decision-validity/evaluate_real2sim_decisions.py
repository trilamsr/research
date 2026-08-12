#!/usr/bin/env python3
# =============================================================================
# evaluate_real2sim_decisions.py  --  retained decision-validity prototype
# Former standalone-paper work, now absorbed into P1.
# =============================================================================
#
# WHAT THIS IS (read before citing any number it prints):
#   This is a RETAINED LEGACY PROTOTYPE / demonstration, NOT a canonical
#   paper-facing decision result. Its stable-order representative can silently
#   choose one checkpoint or policy from a tie. The tie-complete canonical
#   calculation is `research/claim-evidence-synthesis/result-paper-evidence.json`.
#   The input is an aggregate-derived, figure-EXTRACTED dataset: the
#   per-(task,policy,checkpoint) success rates were vector-recovered from
#   Figure 3 of real2sim-eval (arXiv:2511.04665v2) and integer episode counts
#   were back-inferred from the panel episode counts (20/27/16). These are
#   NOT per-trial ground truth and NOT independent replicates. The paper never
#   states how many training runs/seeds sit behind each checkpoint curve, so
#   checkpoints within a (task,policy) cell are PSEUDO-REPLICATED. The only
#   defensible independent unit is the POLICY (n=4 per task). Everything below
#   treats POLICY as the unit and, for the noise bootstrap, resamples
#   checkpoints WITHIN each policy (a clustered/policy-level resample), never
#   pooling checkpoints across policies.
#
#   Scope: real2sim-eval ONLY. Exploratory. No preregistration is locked for
#   this analysis. With n=4 policies per task, several of these metrics are
#   low-powered and prone to ties. Winner sets are exposed, but representative
#   scalar fields use the first stable-order maximizer and must not be cited as
#   tie-robust. Do NOT overclaim.
#
# THESIS UNDER TEST:
#   Rank correlation between a simulated evaluator and real outcomes can look
#   strong (high Pearson r / Spearman rho) while the DECISION the evaluator is
#   used for -- pick the top-1 policy, certify non-inferiority, detect a
#   regression -- is unreliable at the correct independent unit (the policy).
#
# METRICS (per task, policy = independent unit, n=4):
#   1. Top-1 selection agreement, under FOUR checkpoint-selection rules
#      (best-by-real, best-by-sim, last, mean). The rule is unstated in the
#      source; Paper 1 sec.5 already showed the rope correlation flips
#      +0.90 -> -0.31 under an equally defensible unstated rule, so we report
#      how the top-1 pick moves across rules rather than privileging one.
#   2. Regret = real_success(true best real policy) - real_success(sim's pick).
#   3. PCS (probability of correct selection) under binomial sampling noise,
#      with a CLUSTERED resample at the policy unit.
#   4. Correlation contrast: Pearson r and Spearman rho over the n=4
#      best-checkpoint points, printed alongside the decision outcome.
#
# Deterministic: fixed RNG seed. No time/date-based seeding.
# =============================================================================

import argparse
import csv
import json
import os
from collections import OrderedDict
from pathlib import Path

import numpy as np
from scipy import stats

# NOTE: intentionally NO pandas. The target venv
# (sim2real-correlation-audit/.venv) ships numpy + scipy only; this script
# uses the stdlib csv module so it runs against that venv unmodified.

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
SEED = 20260722          # fixed, deterministic; NOT time-derived
N_BOOT = 20000           # bootstrap draws for PCS
RNG = np.random.default_rng(SEED)

AUDIT_ROOT = Path(__file__).resolve().parents[2]
REPO = AUDIT_ROOT
FAMILY_ROOT = Path(__file__).resolve().parent
SOURCES = FAMILY_ROOT.parent / "corpus-reporting-audit" / "sources"
REAL2SIM_ROOT = FAMILY_ROOT.parent / "real2sim-noise-floor"
CKPT_CSV = SOURCES / "source-real2sim-eval-fig3-checkpoints.csv"
REF_CSV = REAL2SIM_ROOT / "input-fig3-digitized-reference.csv"

OUT_DIR = FAMILY_ROOT
OUT_JSON = OUT_DIR / "result-real2sim-decisions.json"

# Selection rules that collapse a policy's checkpoints to one representative
# scalar (real, sim). "mean" averages counts; "last" takes the last-listed
# checkpoint (proxy for latest training stage -- CSV order is training order
# per the extraction notes). "best_real"/"best_sim" take the argmax checkpoint.
SELECTION_RULES = ["best_real", "best_sim", "last", "mean"]

# Absolute float tolerance for declaring a tie between two success rates.
TIE_TOL = 1e-9


# -----------------------------------------------------------------------------
# Load  (stdlib csv -> list-of-dict rows; no pandas)
# -----------------------------------------------------------------------------
def _read_csv_rows(path):
    """Read a CSV skipping lines whose first non-space char is '#'.
    Returns (header:list[str], rows:list[dict])."""
    with open(path, newline="") as f:
        data_lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(data_lines)
    header = [c.strip() for c in (reader.fieldnames or [])]
    rows = []
    for raw in reader:
        rows.append({(k.strip() if k else k): (v.strip() if isinstance(v, str) else v)
                     for k, v in raw.items()})
    return header, rows


def load_checkpoints(path):
    header, rows = _read_csv_rows(path)
    needed = {"task", "policy", "n_episodes", "real_successes",
              "sim_successes", "real_success", "sim_success"}
    missing = needed - set(header)
    if missing:
        raise ValueError(f"checkpoint CSV missing columns: {missing}")
    out = []
    for r in rows:
        out.append({
            "task": r["task"],
            "policy": r["policy"],
            "n_episodes": int(r["n_episodes"]),
            "real_successes": int(r["real_successes"]),
            "sim_successes": int(r["sim_successes"]),
            "real_success": float(r["real_success"]),
            "sim_success": float(r["sim_success"]),
        })
    return out


def load_reference(path):
    _, rows = _read_csv_rows(path)
    return rows


# --- small row helpers replacing pandas groupby/filtering -------------------
def unique_ordered(rows, key):
    """Distinct values of `key` in first-appearance order."""
    seen, out = set(), []
    for r in rows:
        v = r[key]
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def rows_where(rows, **kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]


# -----------------------------------------------------------------------------
# Selection: collapse checkpoints -> one (real, sim) scalar per policy
# -----------------------------------------------------------------------------
def collapse_policy(sub, rule):
    """sub = list of checkpoint rows for one (task, policy). Return (real, sim) %.

    Uses fractional success (successes / n_episodes) so 'mean' is a proper
    pooled-episode mean rather than a mean of rounded percentages. best_* use
    the same fractions for argmax (identical ordering to the % columns).
    Rows keep CSV order, so 'last' = last-listed checkpoint.
    """
    n_ep = np.array([r["n_episodes"] for r in sub], dtype=float)
    real_frac = np.array([r["real_successes"] for r in sub], dtype=float) / n_ep
    sim_frac = np.array([r["sim_successes"] for r in sub], dtype=float) / n_ep

    if rule == "best_real":
        i = int(np.argmax(real_frac))
        return 100.0 * real_frac[i], 100.0 * sim_frac[i]
    if rule == "best_sim":
        i = int(np.argmax(sim_frac))
        return 100.0 * real_frac[i], 100.0 * sim_frac[i]
    if rule == "last":
        return 100.0 * real_frac[-1], 100.0 * sim_frac[-1]
    if rule == "mean":
        return 100.0 * float(real_frac.mean()), 100.0 * float(sim_frac.mean())
    raise ValueError(f"unknown rule {rule}")


def policy_points(task_rows, rule):
    """Return OrderedDict policy -> (real%, sim%) under a selection rule.

    Policy order follows first appearance in the task's rows (stable).
    """
    out = OrderedDict()
    for pol in unique_ordered(task_rows, "policy"):
        sub = rows_where(task_rows, policy=pol)
        out[pol] = collapse_policy(sub, rule)
    return out


# -----------------------------------------------------------------------------
# Argmax with explicit tie handling
# -----------------------------------------------------------------------------
def argmax_with_ties(values, labels):
    """Return (winners_list, is_tie). winners_list = all labels within TIE_TOL
    of the max. is_tie True when >1 winner."""
    vmax = max(values)
    winners = [lab for lab, v in zip(labels, values) if abs(v - vmax) <= TIE_TOL]
    return winners, (len(winners) > 1)


# -----------------------------------------------------------------------------
# Metrics 1 & 2: top-1 agreement + regret, per task per rule
# -----------------------------------------------------------------------------
def top1_and_regret(points):
    """points = {policy: (real, sim)}.
    Returns dict with real-best, sim-pick, agreement flag, regret, tie flags."""
    pols = list(points.keys())
    real = [points[p][0] for p in pols]
    sim = [points[p][1] for p in pols]

    real_winners, real_tie = argmax_with_ties(real, pols)
    sim_winners, sim_tie = argmax_with_ties(sim, pols)

    # Deterministic representative pick when a tie exists: first in stable
    # policy order. Reported alongside the full winner set so the tie is visible.
    real_best = real_winners[0]
    sim_pick = sim_winners[0]

    # Agreement: does sim's chosen top-1 sit in the set of real winners?
    # (Credits sim if it lands on any real-optimal policy under a real tie.)
    agree = sim_pick in real_winners

    real_best_val = points[real_best][0]
    sim_pick_realval = points[sim_pick][0]  # real success you'd actually get
    regret = real_best_val - sim_pick_realval

    return {
        "policies": pols,
        "real_pct": {p: round(points[p][0], 4) for p in pols},
        "sim_pct": {p: round(points[p][1], 4) for p in pols},
        "real_best_policy": real_best,
        "real_best_winners": real_winners,
        "real_tie": bool(real_tie),
        "sim_pick_policy": sim_pick,
        "sim_pick_winners": sim_winners,
        "sim_tie": bool(sim_tie),
        "agree": bool(agree),
        "real_best_real_success": round(real_best_val, 4),
        "sim_pick_real_success": round(sim_pick_realval, 4),
        "regret": round(regret, 4),
    }


# -----------------------------------------------------------------------------
# Metric 4: correlation contrast over n=4 best-real-checkpoint points
# -----------------------------------------------------------------------------
def correlation_contrast(points):
    """Pearson r and Spearman rho over the (real, sim) policy points."""
    pols = list(points.keys())
    real = np.array([points[p][0] for p in pols], dtype=float)
    sim = np.array([points[p][1] for p in pols], dtype=float)
    n = len(pols)

    res = {"n_policies": n}
    # Guard: correlation undefined if a variable is constant.
    if np.ptp(real) < TIE_TOL or np.ptp(sim) < TIE_TOL:
        res.update({"pearson_r": None, "pearson_p": None,
                    "spearman_rho": None, "spearman_p": None,
                    "note": "constant vector -> correlation undefined"})
        return res
    pr = stats.pearsonr(real, sim)
    sp = stats.spearmanr(real, sim)
    res.update({
        "pearson_r": round(float(pr.statistic), 4),
        "pearson_p": round(float(pr.pvalue), 4),
        "spearman_rho": round(float(sp.statistic), 4),
        "spearman_p": round(float(sp.pvalue), 4),
    })
    # Detect tied ranks in either variable (weakens Spearman with n=4).
    _, real_counts = np.unique(np.round(real, 6), return_counts=True)
    _, sim_counts = np.unique(np.round(sim, 6), return_counts=True)
    if (real_counts > 1).any() or (sim_counts > 1).any():
        res["rank_ties_present"] = True
    else:
        res["rank_ties_present"] = False
    return res


# -----------------------------------------------------------------------------
# Metric 3: PCS under binomial noise, CLUSTERED resample at policy unit
# -----------------------------------------------------------------------------
def pcs_clustered(task_rows, rule, n_boot=N_BOOT, rng=RNG):
    """Estimate P(sim's top-1 pick == real-best policy) under sampling noise.

    Clustered / policy-level resample:
      - The TRUTH (real-best policy) is fixed from the observed best-real-
        checkpoint points (the target the evaluator is trying to hit).
      - Each draw: for every policy, resample its checkpoints WITH REPLACEMENT
        (cluster bootstrap over the pseudo-replicated checkpoints), then draw
        binomial episode counts for each resampled checkpoint using its own
        (p_hat = successes/n_episodes, n_episodes). Collapse to a scalar under
        `rule`. This injects BOTH the checkpoint-set uncertainty and the
        episode-level binomial noise, at the correct (policy) unit.
      - Record whether sim's resampled top-1 pick lands on the fixed real-best
        policy. PCS = fraction of draws where it does.

    Returns dict incl. pcs, whether the fixed truth has a tie, and the
    empirical distribution of which policy sim picks.
    """
    pols = unique_ordered(task_rows, "policy")

    # Pre-extract per-policy checkpoint arrays (counts + episodes) for both
    # real and sim, plus the observed collapsed points (for fixed truth).
    per_pol = {}
    obs_points = policy_points(task_rows, rule)
    for pol in pols:
        sub = rows_where(task_rows, policy=pol)
        per_pol[pol] = {
            "real_succ": np.array([r["real_successes"] for r in sub]),
            "sim_succ": np.array([r["sim_successes"] for r in sub]),
            "n_ep": np.array([r["n_episodes"] for r in sub]),
            "k": len(sub),
        }

    real_obs = [obs_points[p][0] for p in pols]
    real_winners, real_tie = argmax_with_ties(real_obs, pols)
    truth_set = set(real_winners)  # sim "correct" if it picks any real-optimal

    pick_counts = {p: 0 for p in pols}
    correct = 0

    for _ in range(n_boot):
        sim_scalar = {}
        for pol in pols:
            d = per_pol[pol]
            k = d["k"]
            # cluster resample: choose k checkpoint indices with replacement
            idx = rng.integers(0, k, size=k)
            n_ep = d["n_ep"][idx]
            # binomial redraw of real and sim successes at each resampled ckpt
            p_real = d["real_succ"][idx] / d["n_ep"][idx]
            p_sim = d["sim_succ"][idx] / d["n_ep"][idx]
            real_draw = rng.binomial(n_ep, p_real)
            sim_draw = rng.binomial(n_ep, p_sim)
            # collapse under the rule (fractions -> %)
            if rule == "best_real":
                j = int(np.argmax(real_draw / n_ep))
                sim_scalar[pol] = 100.0 * sim_draw[j] / n_ep[j]
            elif rule == "best_sim":
                j = int(np.argmax(sim_draw / n_ep))
                sim_scalar[pol] = 100.0 * sim_draw[j] / n_ep[j]
            elif rule == "last":
                sim_scalar[pol] = 100.0 * sim_draw[-1] / n_ep[-1]
            elif rule == "mean":
                sim_scalar[pol] = 100.0 * float((sim_draw / n_ep).mean())
            else:
                raise ValueError(rule)

        sim_vals = [sim_scalar[p] for p in pols]
        sim_winners, _ = argmax_with_ties(sim_vals, pols)
        # On a resampled tie, pick the first in stable order (deterministic).
        pick = sim_winners[0]
        pick_counts[pick] += 1
        if pick in truth_set:
            correct += 1

    return {
        "pcs": round(correct / n_boot, 4),
        "n_boot": n_boot,
        "fixed_real_best": real_winners,
        "fixed_real_tie": bool(real_tie),
        "sim_pick_distribution": {p: round(pick_counts[p] / n_boot, 4)
                                  for p in pols},
    }


# -----------------------------------------------------------------------------
# Driver
# -----------------------------------------------------------------------------
def analyze():
    rows = load_checkpoints(CKPT_CSV)
    ref = load_reference(REF_CSV)

    tasks = unique_ordered(rows, "task")

    results = {
        "meta": {
            "script": str(Path(__file__).resolve().relative_to(AUDIT_ROOT)),
            "prototype": True,
            "canonical_for_paper": False,
            "superseded_by": (
                "research/claim-evidence-synthesis/"
                "result-paper-evidence.json#checkpoint_selection"
            ),
            "representative_tie_warning": (
                "Scalar representative fields select the first stable-order maximizer; "
                "use the superseding tie-complete result for scientific reliance."
            ),
            "confirmatory": False,
            "preregistered": False,
            "data_source": "real2sim-eval arXiv:2511.04665v2 Fig.3, vector-extracted (NOT per-trial ground truth)",
            "scope": "real2sim-eval only",
            "independent_unit": "policy (n=4 per task)",
            "pcs_resample": "clustered at policy unit (checkpoints resampled within policy, not pooled)",
            "seed": SEED,
            "n_boot": N_BOOT,
            "selection_rules": SELECTION_RULES,
            "tie_tolerance": TIE_TOL,
            "checkpoint_csv": str(CKPT_CSV.relative_to(AUDIT_ROOT)),
            "reference_csv": str(REF_CSV.relative_to(AUDIT_ROOT)),
            "caveat": "Checkpoints are pseudo-replicated (unknown #seeds). n=4 per task -> low power, ties likely. Do not overclaim.",
        },
        "tasks": {},
    }

    for task in tasks:
        task_rows = rows_where(rows, task=task)
        task_pols = unique_ordered(task_rows, "policy")

        task_res = {
            "n_policies": len(task_pols),
            "checkpoints_per_policy": {
                p: len(rows_where(task_rows, policy=p)) for p in task_pols
            },
            "by_rule": {},
        }

        for rule in SELECTION_RULES:
            pts = policy_points(task_rows, rule)
            t1 = top1_and_regret(pts)
            corr = correlation_contrast(pts)
            pcs = pcs_clustered(task_rows, rule)
            task_res["by_rule"][rule] = {
                "top1_regret": t1,
                "correlation": corr,
                "pcs": pcs,
            }

        results["tasks"][task] = task_res

    return results, ref


# -----------------------------------------------------------------------------
# Pretty print
# -----------------------------------------------------------------------------
def fmt_pts(d):
    return "  ".join(f"{k}={v:.1f}" for k, v in d.items())


def print_summary(results):
    m = results["meta"]
    print("=" * 78)
    print("DECISION-VALIDITY PROTOTYPE  --  Real2Sim")
    print("=" * 78)
    print(f"data      : {m['data_source']}")
    print(f"scope     : {m['scope']}   unit: {m['independent_unit']}")
    print(f"PCS resamp: {m['pcs_resample']}")
    print(f"seed={m['seed']}  n_boot={m['n_boot']}  rules={m['selection_rules']}")
    print(f"CAVEAT    : {m['caveat']}")
    print()

    for task, tr in results["tasks"].items():
        print("#" * 78)
        cpp = tr["checkpoints_per_policy"]
        print(f"TASK: {task}   (n_policies={tr['n_policies']}, "
              f"checkpoints/policy={cpp})")
        print("#" * 78)

        # header
        hdr = (f"{'rule':<10} {'real_best':<12} {'sim_pick':<12} "
               f"{'agree':<6} {'regret':<8} {'r':<7} {'rho':<7} "
               f"{'PCS':<6} ties")
        print(hdr)
        print("-" * len(hdr))

        for rule in SELECTION_RULES:
            block = tr["by_rule"][rule]
            t1 = block["top1_regret"]
            corr = block["correlation"]
            pcs = block["pcs"]

            r = corr.get("pearson_r")
            rho = corr.get("spearman_rho")
            r_s = f"{r:+.2f}" if r is not None else "n/a"
            rho_s = f"{rho:+.2f}" if rho is not None else "n/a"

            tie_flags = []
            if t1["real_tie"]:
                tie_flags.append("REAL-tie")
            if t1["sim_tie"]:
                tie_flags.append("SIM-tie")
            if corr.get("rank_ties_present"):
                tie_flags.append("rank-ties")
            tie_s = ",".join(tie_flags) if tie_flags else "-"

            agree_s = "YES" if t1["agree"] else "NO"
            real_best_s = f"{t1['real_best_policy']}({t1['real_best_real_success']:.0f})"
            sim_pick_s = f"{t1['sim_pick_policy']}({t1['sim_pick_real_success']:.0f})"

            flag = "  <-- MISMATCH" if not t1["agree"] else ""
            print(f"{rule:<10} {real_best_s:<12} {sim_pick_s:<12} "
                  f"{agree_s:<6} {t1['regret']:<8.1f} {r_s:<7} {rho_s:<7} "
                  f"{pcs['pcs']:<6.2f} {tie_s}{flag}")

        # per-rule policy points + sim-pick distribution detail
        print()
        for rule in SELECTION_RULES:
            block = tr["by_rule"][rule]
            t1 = block["top1_regret"]
            pcs = block["pcs"]
            print(f"  [{rule}] real%: {fmt_pts(t1['real_pct'])}")
            print(f"  {'':<{len(rule)+2}} sim% : {fmt_pts(t1['sim_pct'])}")
            print(f"  {'':<{len(rule)+2}} sim-pick dist over {pcs['n_boot']} draws: "
                  f"{pcs['sim_pick_distribution']}  (correct set={pcs['fixed_real_best']})")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_JSON,
        help="JSON output path (defaults to the canonical family result)",
    )
    args = parser.parse_args()
    os.makedirs(args.out.parent, exist_ok=True)
    results, ref = analyze()
    print_summary(results)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print("=" * 78)
    print(f"results written to: {args.out}")
    print("=" * 78)


if __name__ == "__main__":
    main()
