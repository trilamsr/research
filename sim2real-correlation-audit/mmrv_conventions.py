#!/usr/bin/env python3
"""Brute-force MMRV convention grid: regenerates the PAPER.md section 7.2 results.

WHY THIS EXISTS. Section 7.2 claims three things that, until this script, had no
regenerating code in the package:

  (a) The subject paper's (real2sim-eval, arXiv:2511.04665v2) Table I MMRVs
      0.076 / 0.174 / 0.108 (toy packing / rope routing / T-block pushing)
      reproduce to print precision from our Figure-3 extraction
      (data/survey-real2sim-eval-fig3-checkpoints.csv) under EXACTLY ONE convention in
      the grid below: a violation whenever the <=-orderings of the pair disagree
      (tie-inclusive XOR), weighted by the SIMULATED-side gap |S_i - S_j|,
      normalized by N. That violation predicate is logically IDENTICAL to
      SIMPLER's (see below); the subject paper differs from SIMPLER in exactly
      one argument: it weights the SIMULATED-side gap where SIMPLER's defining
      equation weights the REAL side.
  (b) The same convention reproduces the 200-episode appendix figure
      (data/survey-real2sim-eval-fig9-200ep.csv) EXACTLY, as the rational lattice
      points 21/200, 307/2000, 209/3000 -- an exact-arithmetic match, not a
      tolerance match, computed here with fractions.Fraction.
  (c) REALM's (arXiv:2512.19562) V-VIEW panel prints MMRV = 0.253, and no
      convention in the grid comes within print precision of it on the 14
      points the panel actually draws (data/survey-realm.csv); SIMPLER's own
      convention gives 0.117, the value quoted as "ours" in section 7.2.
      (On these 14 points the tie-exclusive sign<0 reading gives the same
      0.117 to print precision.)

WHICH CONVENTION IS SIMPLER'S. SIMPLER's released code
(simpler_env/utils/metrics.py, mean_maximum_rank_violation) and its paper's
Eq. 1 (arXiv:2405.05941) agree with each other: the violation predicate is the
strict-inequality XOR  (S_i > S_j) != (R_i > R_j),  and the weight is the
REAL-side gap |R_i - R_j|.  Since (dR > 0) != (dS > 0) is logically identical
to (dR <= 0) != (dS <= 0) for every input, SIMPLER's convention IS the grid
variant leq-xor/real/N: a ONE-SIDED tie (tied on one axis, differing on the
other) counts as a violation.  Earlier drafts of section 7 mislabeled the
tie-exclusive sign<0/real/N variant as "SIMPLER's definition"; that variant is
kept in the grid (as TIE_EXCLUSIVE_CONVENTION) but the label was wrong.

THE METRIC. For N points (R_i, S_i) -- real and simulated success rates --

    MMRV = (1/norm) * aggregate_i  max_{j != i} [ viol(i,j) * gap(i,j) ]

and the convention grid is the cartesian product of:

  violation predicate viol(i,j), on dR = R_i - R_j, dS = S_i - S_j:
    sign<0            dR*dS < 0                (strict; ties never violate --
                                                NOT SIMPLER's definition,
                                                despite an earlier mislabel)
    leq-xor           (dR<=0) != (dS<=0)       (== (dR>0)!=(dS>0): SIMPLER's
                                                published definition; a tie on
                                                exactly one side violates)
    lt-xor            (dR<0)  != (dS<0)        (tie-inclusive, mirror reading)
    geq-xor           (dR>=0) != (dS>=0)       (pointwise identical to lt-xor,
                                                since not(dR>=0) == (dR<0) and
                                                XOR is complement-invariant;
                                                kept so the grid's advertised
                                                count stays 60 -- it can never
                                                produce a value lt-xor does not)
    sign<=0-any-tie   dR*dS <= 0 and not both zero  (most inclusive reading)

  gap side gap(i,j):
    real   |dR|        (SIMPLER's defining equation)
    sim    |dS|        (the subject paper's recovered convention)
    max    max(|dR|,|dS|)
    mean   (|dR|+|dS|)/2

  normalization:
    N      mean of per-item maxima over all N items (the published "M M" --
           max over pairs, mean over items)
    N-1    same sum divided by N-1
    pairs  mean of viol*gap over all C(N,2) unordered pairs (no max step)

5 x 4 x 3 = 60 variants, the "some fifty definitional variants" of section 7.2.

ARITHMETIC. Parts (a) and (b) run on exact rationals (success counts over
episode counts, via fractions.Fraction), so an "exact" verdict in (b) means
equality of rationals, and the (a) tolerance is applied to an exact value.
Part (c) runs on the float task-progression coordinates shipped in realm.csv.

USAGE.
  python mmrv_conventions.py            # full report + verdicts; exit 0 iff all
                                        # three published claims regenerate
  python mmrv_conventions.py --grid     # additionally dump all 60 variants for
                                        # every dataset

Data files are the shipped extractions only; nothing here touches the network
or the source PDFs.
"""
from __future__ import annotations

import argparse
import csv
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).parent

# --------------------------------------------------------------------------- #
# The convention grid                                                         #
# --------------------------------------------------------------------------- #

VIOLATIONS = {
    "sign<0":          lambda dR, dS: dR * dS < 0,
    "leq-xor":         lambda dR, dS: (dR <= 0) != (dS <= 0),
    "lt-xor":          lambda dR, dS: (dR < 0) != (dS < 0),
    "geq-xor":         lambda dR, dS: (dR >= 0) != (dS >= 0),
    "sign<=0-any-tie": lambda dR, dS: dR * dS <= 0 and not (dR == 0 and dS == 0),
}

GAPS = {
    "real": lambda dR, dS: abs(dR),
    "sim":  lambda dR, dS: abs(dS),
    "max":  lambda dR, dS: max(abs(dR), abs(dS)),
    "mean": lambda dR, dS: (abs(dR) + abs(dS)) / 2,
}

NORMS = ("N", "N-1", "pairs")

CONVENTIONS = [(v, g, n) for v, g, n in product(VIOLATIONS, GAPS, NORMS)]

# The named conventions section 7.2 talks about.
# SIMPLER's actual convention (code + paper Eq. 1): strict-> XOR == leq-xor,
# real-side gap, mean-over-items of max-over-j.  One-sided ties violate.
SIMPLER_CONVENTION = ("leq-xor", "real", "N")
# Tie-exclusive variant an earlier draft mislabeled as "SIMPLER's definition";
# it is the convention the section 7 drop-one table was computed under.
TIE_EXCLUSIVE_CONVENTION = ("sign<0", "real", "N")
# Recovered for the subject paper: same violation predicate as SIMPLER,
# simulated-side gap instead of real-side.
SUBJECT_CONVENTION = ("leq-xor", "sim", "N")


def mmrv(points, violation: str, gap: str, norm: str):
    """MMRV of [(R_i, S_i), ...] under one (violation, gap, norm) convention.

    Exact when the coordinates are Fractions (mean of gaps stays rational;
    /2 in the 'mean' gap likewise).
    """
    viol, gapf = VIOLATIONS[violation], GAPS[gap]
    n = len(points)
    if n < 2:
        raise ValueError("MMRV needs at least 2 points")

    def d(i, j):
        return points[i][0] - points[j][0], points[i][1] - points[j][1]

    if norm == "pairs":
        total = sum(gapf(*d(i, j))
                    for i in range(n) for j in range(i + 1, n)
                    if viol(*d(i, j)))
        return total / Fraction(n * (n - 1), 2) if isinstance(total, Fraction) \
            else total / (n * (n - 1) / 2)

    total = sum(
        max((gapf(*d(i, j)) for j in range(n) if j != i and viol(*d(i, j))),
            default=0)
        for i in range(n))
    return total / (n if norm == "N" else n - 1)


# --------------------------------------------------------------------------- #
# Data loading (shipped CSVs only)                                            #
# --------------------------------------------------------------------------- #

def _rows(name: str):
    with open(HERE / "data" / name) as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load_fig3():
    """Per-task exact (real, sim) rates from the Figure-3 checkpoint extraction."""
    by_task: dict[str, list] = {}
    for r in _rows("survey-real2sim-eval-fig3-checkpoints.csv"):
        n = int(r["n_episodes"])
        by_task.setdefault(r["task"], []).append(
            (Fraction(int(r["real_successes"]), n),
             Fraction(int(r["sim_successes"]), n)))
    return by_task


def load_fig9():
    """Per-panel exact rates from the 200-episode appendix-figure extraction."""
    by_panel: dict[str, list] = {}
    for r in _rows("survey-real2sim-eval-fig9-200ep.csv"):
        by_panel.setdefault(r["panel"], []).append(
            (Fraction(int(r["k_real"]), int(r["n_real"])),
             Fraction(int(r["k_sim"]), int(r["n_sim"]))))
    return by_panel


def load_realm_panel(panel: str):
    """Float task-progression points of one REALM panel (as drawn: V-VIEW has 14)."""
    return [(float(r["x_real"]), float(r["y_sim"]))
            for r in _rows("survey-realm.csv") if r["panel"] == panel]


# --------------------------------------------------------------------------- #
# The three published claims                                                  #
# --------------------------------------------------------------------------- #

# (a) Table I, print precision (3 decimals => tolerance 0.0005 on the exact value)
FIG3_PRINTED = {"sloth": Fraction(76, 1000),   # toy packing
                "rope":  Fraction(174, 1000),  # rope routing
                "T":     Fraction(108, 1000)}  # T-block pushing
FIG3_TOL = Fraction(5, 10000)
FIG3_LABEL = {"sloth": "toy packing ", "rope": "rope routing", "T": "T-block push"}

# (b) 200-episode appendix figure, exact rational targets
FIG9_TARGETS = {"toy_packing":     Fraction(21, 200),
                "rope_routing":    Fraction(307, 2000),
                "t_block_pushing": Fraction(209, 3000)}

# (c) REALM V-VIEW printed value; print precision again
REALM_PRINTED = 0.253
REALM_TOL = 0.0005


def conv_name(c):
    return "/".join(c)


def check_fig3(by_task):
    """Which conventions put all three Table I values within print precision?"""
    matches = []
    per_conv = {}
    for c in CONVENTIONS:
        vals = {t: mmrv(pts, *c) for t, pts in by_task.items()}
        per_conv[c] = vals
        if all(abs(vals[t] - FIG3_PRINTED[t]) <= FIG3_TOL for t in FIG3_PRINTED):
            matches.append(c)
    return matches, per_conv


def check_fig9(by_panel):
    """Which conventions hit all three appendix-figure fractions EXACTLY?"""
    matches = []
    per_conv = {}
    for c in CONVENTIONS:
        vals = {p: mmrv(pts, *c) for p, pts in by_panel.items()}
        per_conv[c] = vals
        if all(vals[p] == FIG9_TARGETS[p] for p in FIG9_TARGETS):
            matches.append(c)
    return matches, per_conv


def check_realm(points):
    """Full grid on the 14 drawn V-VIEW points; distance of each to 0.253."""
    vals = {c: mmrv(points, *c) for c in CONVENTIONS}
    reaching = [c for c, v in vals.items() if abs(v - REALM_PRINTED) <= REALM_TOL]
    return vals, reaching


# --------------------------------------------------------------------------- #
# Report                                                                      #
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--grid", action="store_true",
                    help="dump every variant's value for every dataset")
    args = ap.parse_args()

    failures = []
    P = print

    P(f"MMRV convention grid: {len(CONVENTIONS)} variants "
      f"({len(VIOLATIONS)} violation predicates x {len(GAPS)} gap sides x "
      f"{len(NORMS)} normalizations)")
    P()

    # ---- (a) Figure 3 / Table I -------------------------------------------
    by_task = load_fig3()
    fig3_matches, fig3_vals = check_fig3(by_task)
    P("(a) real2sim-eval Table I vs Figure-3 checkpoint extraction")
    P(f"    printed: toy 0.076, rope 0.174, T-block 0.108; "
      f"match = all three within {float(FIG3_TOL)} (print precision)")
    if fig3_matches:
        for c in fig3_matches:
            vals = fig3_vals[c]
            P(f"    MATCH  {conv_name(c):<28}" +
              "  ".join(f"{FIG3_LABEL[t].strip()}={float(vals[t]):.6f} ({vals[t]})"
                        for t in ("sloth", "rope", "T")))
    else:
        P("    NO convention in the grid matches all three printed values.")
    if fig3_matches == [SUBJECT_CONVENTION]:
        P(f"    VERDICT: unique match, and it is the claimed convention "
          f"{conv_name(SUBJECT_CONVENTION)}  -- claim (a) REGENERATES")
    else:
        failures.append(
            f"(a) expected unique match {conv_name(SUBJECT_CONVENTION)}, "
            f"got {[conv_name(c) for c in fig3_matches]}")
        P(f"    VERDICT: DISCREPANCY -- {failures[-1]}")
    P()

    # ---- (b) Figure 9 (200-episode appendix figure) ------------------------
    by_panel = load_fig9()
    fig9_matches, fig9_vals = check_fig9(by_panel)
    P("(b) real2sim-eval 200-episode appendix figure (exact rational targets)")
    P("    targets: toy 21/200, rope 307/2000, T-block 209/3000")
    if fig9_matches:
        for c in fig9_matches:
            vals = fig9_vals[c]
            P(f"    EXACT  {conv_name(c):<28}" +
              "  ".join(f"{p}={vals[p]}" for p in FIG9_TARGETS))
    else:
        P("    NO convention reproduces all three fractions exactly.")
    if fig9_matches == [SUBJECT_CONVENTION]:
        P(f"    VERDICT: unique exact match, same convention as (a) "
          f"-- claim (b) REGENERATES")
    else:
        failures.append(
            f"(b) expected unique exact match {conv_name(SUBJECT_CONVENTION)}, "
            f"got {[conv_name(c) for c in fig9_matches]}")
        P(f"    VERDICT: DISCREPANCY -- {failures[-1]}")
    P()

    # ---- (c) REALM V-VIEW --------------------------------------------------
    vv = load_realm_panel("V-VIEW")
    realm_vals, reaching = check_realm(vv)
    ordered = sorted(realm_vals.items(), key=lambda kv: kv[1])
    lo_c, lo_v = ordered[0]
    hi_c, hi_v = ordered[-1]
    near_c, near_v = min(realm_vals.items(),
                         key=lambda kv: abs(kv[1] - REALM_PRINTED))
    simpler_v = realm_vals[SIMPLER_CONVENTION]
    tie_excl_v = realm_vals[TIE_EXCLUSIVE_CONVENTION]
    subject_v = realm_vals[SUBJECT_CONVENTION]
    P(f"(c) REALM V-VIEW panel: printed MMRV = {REALM_PRINTED}, "
      f"N = {len(vv)} drawn points (design implies 21)")
    P(f"    grid min     = {lo_v:.4f}  under {conv_name(lo_c)}")
    P(f"    grid max     = {hi_v:.4f}  under {conv_name(hi_c)}")
    P(f"    closest      = {near_v:.4f}  under {conv_name(near_c)} "
      f"(off by {abs(near_v - REALM_PRINTED):.4f})")
    P(f"    SIMPLER convention {conv_name(SIMPLER_CONVENTION)}: {simpler_v:.4f} "
      f"(section 7.2 quotes ours: 0.117)")
    P(f"    tie-exclusive variant {conv_name(TIE_EXCLUSIVE_CONVENTION)}: "
      f"{tie_excl_v:.4f} (same to print precision on these 14 points)")
    P(f"    subject-paper convention {conv_name(SUBJECT_CONVENTION)}: {subject_v:.4f}")
    if not reaching and abs(simpler_v - 0.117) <= 0.0005:
        P(f"    VERDICT: no variant of {len(CONVENTIONS)} comes within "
          f"{REALM_TOL} of 0.253 -- claim (c) REGENERATES")
    else:
        if reaching:
            failures.append(
                f"(c) variant(s) DO reach 0.253: {[conv_name(c) for c in reaching]}")
        if abs(simpler_v - 0.117) > 0.0005:
            failures.append(
                f"(c) SIMPLER-convention value {simpler_v:.4f} != quoted 0.117")
        for f in failures:
            if f.startswith("(c)"):
                P(f"    VERDICT: DISCREPANCY -- {f}")
    P()

    # ---- optional full dump ------------------------------------------------
    if args.grid:
        P("=" * 78)
        P("Full grid dump")
        hdr = (f"{'convention':<30}{'fig3 toy':>10}{'fig3 rope':>10}{'fig3 T':>10}"
               f"{'fig9 toy':>10}{'fig9 rope':>10}{'fig9 T':>10}{'V-VIEW':>9}")
        P(hdr)
        for c in CONVENTIONS:
            f3, f9 = fig3_vals[c], fig9_vals[c]
            P(f"{conv_name(c):<30}"
              f"{float(f3['sloth']):>10.4f}{float(f3['rope']):>10.4f}{float(f3['T']):>10.4f}"
              f"{float(f9['toy_packing']):>10.4f}{float(f9['rope_routing']):>10.4f}"
              f"{float(f9['t_block_pushing']):>10.4f}{realm_vals[c]:>9.4f}")
        P()

    # ---- verdict table -----------------------------------------------------
    P("=" * 78)
    P("VERDICT")
    P(f"  (a) Table I 0.076/0.174/0.108 via unique convention "
      f"{conv_name(SUBJECT_CONVENTION)}: "
      f"{'REGENERATED' if not any(f.startswith('(a)') for f in failures) else 'FAILED'}")
    P(f"  (b) appendix figure exact 21/200, 307/2000, 209/3000, same convention:  "
      f"{'REGENERATED' if not any(f.startswith('(b)') for f in failures) else 'FAILED'}")
    P(f"  (c) REALM V-VIEW 0.253 unreachable over {len(CONVENTIONS)} variants "
      f"(SIMPLER conv = 0.117): "
      f"{'REGENERATED' if not any(f.startswith('(c)') for f in failures) else 'FAILED'}")
    if failures:
        P()
        P("DISCREPANCIES (paper claims NOT regenerated -- do not quote section 7.2 "
          "without resolving):")
        for f in failures:
            P(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
