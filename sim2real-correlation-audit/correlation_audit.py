#!/usr/bin/env python3
"""What to report alongside a sim-vs-real correlation.

Five checks. Each exists because it caught something real in published work:

  1. LEVERAGE          Is one unit carrying the correlation?
                       RoboWorld reports r=0.989 with p<0.001 and a 500-resample bootstrap.
                       Removing one of its eight policies gives r=0.798. No conventional
                       check surfaces that; this one does in a line.

  2. FISHER-Z          What can this many independent units support?
                       At k=4 the interval spans most of [-1,1]. That is not a failure of
                       the method -- it is the honest answer, and it is worth printing.

  3. EXACT PERMUTATION Is a permutation test over units at alpha=0.05 even possible?
                       With k units there are k! labelings, so the smallest attainable
                       p-value is 1/k!. At k=3 that is 0.167: no result can reach 0.05.

  4. BOOTSTRAP SUPPORT Is a percentile CI meaningful here?
                       Resampling k units gives at most C(2k-1,k) distinct values -- 35 at
                       k=4. A "95% CI" over 35 atoms has an endpoint set by two or three
                       resamples, and it moves with the seed.

  5. GRANULARITY       Is your own reported value attainable at your stated design?
                       MMRV is a multiple of 1/(N*n_episodes). Only informative when that
                       lattice is coarse: at N*n_ep > ~300 an arbitrary value passes more
                       than a third of the time, so the check reports its own false-pass
                       rate and declares itself inconclusive rather than clearing a value.

WHAT THIS IS NOT. It does not decide whether a correlation is "good". It reports what the
design can support, so a reader can tell a robust result from a fragile one. Every check is
arithmetic on data you already have.

  from correlation_audit import audit
  audit(points, units)                       # points: [(real, sim), ...], units: labels
  audit(points, units, n_episodes=20, reported_mmrv=0.076)

  python correlation_audit.py --demo         # runs on the two datasets in this directory
"""
from __future__ import annotations
import argparse
import csv
import sys
from dataclasses import dataclass, field
from math import comb, factorial
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr

LEVERAGE_FLAG = 0.10      # a drop-one shift this large means one unit is load-bearing
ATOM_FLOOR = 50           # below this many attainable values, a percentile CI is not meaningful
ROUNDING_SLACK = 0.0005   # 3-decimal reporting


@dataclass
class Audit:
    n_points: int
    k_units: int
    r: float
    leverage: float
    drop_range: tuple[float, float]
    fisher_z: tuple[float, float] | None   # None when k <= 3: se = 1/sqrt(k-3) is undefined
    min_p: float
    atom_ceiling: int
    granularity: dict | None = field(default=None)
    # units whose removal left too few points to score -- reported, never silent
    skipped_units: list = field(default_factory=list)

    @property
    def leverage_computable(self) -> bool:
        return self.leverage == self.leverage      # False only for NaN

    @property
    def one_unit_carries(self) -> bool:
        return self.leverage_computable and self.leverage > LEVERAGE_FLAG

    @property
    def bootstrap_meaningful(self) -> bool:
        return self.atom_ceiling >= ATOM_FLOOR

    @property
    def test_possible(self) -> bool:
        return self.min_p <= 0.05

    def recommendation(self) -> str:
        """Every firing check, most serious first. An earlier version returned on the first
        match, so a dataset that both had one unit carrying the result AND could not reach
        alpha=0.05 reported only the leverage message."""
        out = []
        if not self.test_possible:
            out.append(f"With k={self.k_units}, no permutation test over units can reach alpha=0.05 "
                       f"(min p = 1/{self.k_units}! = {self.min_p:.3f}). A parametric p over pooled "
                       f"points answers a different question; do not report it as if it were a "
                       f"unit-level test.")
        if self.fisher_z is None:
            out.append(f"Fisher-z is undefined at k={self.k_units}; there is no interval to report. "
                       f"State k and the drop-one range instead.")
        if not self.leverage_computable:
            out.append(f"Leverage is not computable at k={self.k_units} with these unit sizes — "
                       f"the design cannot support a stability check at all.")
        if self.one_unit_carries:
            out.append(f"Report the drop-one range {self.drop_range[0]:.3f}–{self.drop_range[1]:.3f} "
                       f"alongside r; one unit moves it by {self.leverage:.3f}. Check the rank "
                       f"correlation too — leverage on Pearson need not affect ranking.")
        if not self.bootstrap_meaningful:
            out.append(f"Do not report a bootstrap CI: only {self.atom_ceiling} distinct values "
                       f"are attainable at k={self.k_units}.")
        if not out:
            return "r is stable to unit composition and k supports a resampling interval."
        return " ".join(out)


def audit(points, units, n_episodes: int | None = None,
          reported_mmrv: float | None = None) -> Audit:
    """Audit a sim-vs-real correlation. Returns an Audit with all five checks.

    points   -- [(real_rate, sim_rate), ...]
    units    -- one label per point naming its INDEPENDENT unit. This is the choice that
                matters most: checkpoints of one training run are NOT independent units,
                and no paper in our survey states which it used.
    n_episodes, reported_mmrv -- optional; supply both to run the granularity check.

    The five checks, as computed here:

      leverage      For each unit u, recompute Pearson r with u's points removed
                    (drop-one at the UNIT level). leverage = max |r_drop - r|;
                    drop_range = (min, max) over the k recomputed r values.
      Fisher-z      95% CI at the unit level: z = arctanh(r), se = 1/sqrt(k-3),
                    interval tanh(z +/- 1.96*se). Undefined for k <= 3.
      permutation   min attainable p over the k! unit relabelings is 1/k!.
      bootstrap     resampling k units with replacement yields at most
                    C(2k-1, k) distinct statistic values (multiset count).
      granularity   MMRV must lie on the lattice of multiples of 1/(N*n_episodes);
                    false-pass rate = 2*ROUNDING_SLACK/(lattice spacing), i.e. the
                    chance an arbitrary value rounds onto the lattice anyway.
    """
    if len(points) != len(units):
        raise ValueError(f"{len(points)} points but {len(units)} unit labels")
    if len(points) < 3:
        raise ValueError("need at least 3 points")

    X = np.asarray([p[0] for p in points], float)
    Y = np.asarray([p[1] for p in points], float)
    if X.std() == 0 or Y.std() == 0:
        raise ValueError("no variance on one axis")

    r = float(pearsonr(X, Y)[0])
    labels = list(dict.fromkeys(units))          # stable order
    k = len(labels)

    drops, skipped = [], []
    for u in labels:
        keep = [i for i in range(len(points)) if units[i] != u]
        if len(keep) < 3:
            skipped.append(u); continue
        a, b = X[keep], Y[keep]
        if a.std() and b.std():
            drops.append(float(pearsonr(a, b)[0]))
        else:
            skipped.append(u)
    # At k=3 with one point per unit, every removal leaves 2 points and leverage is not
    # computable. That is not an error -- the other checks still apply, and 13 of the 18
    # papers we surveyed sit at df <= 2. Report what can be computed and say what cannot.
    if drops:
        leverage = max(abs(d - r) for d in drops)
        drop_rng = (min(drops), max(drops))
    else:
        leverage = float("nan")
        drop_rng = (float("nan"), float("nan"))
    # Fisher-z at the UNIT level: using n_points here would be the pseudo-replication
    # this tool exists to surface.
    # Fisher-z has se = 1/sqrt(k-3), which is undefined at k <= 3. Returning a [-1, 1]
    # interval there would look like a legitimate result; 13 of the 18 papers we surveyed
    # have df <= 2, so this path is the common case for the intended audience, not an edge.
    if k > 3:
        z = np.arctanh(np.clip(r, -0.999999, 0.999999))
        se = 1.0 / np.sqrt(k - 3)
        fz = (float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se)))
    else:
        fz = None

    gran = None
    if n_episodes and reported_mmrv is not None:
        # NOTE: len(points), not k. This is deliberate and is NOT the pseudo-replication
        # this tool exists to flag: MMRV is a mean over all N plotted items, so its
        # granularity is 1/(N*n_ep) regardless of how those items cluster into units.
        g = 1.0 / (len(points) * n_episodes)
        miss = abs(reported_mmrv / g - round(reported_mmrv / g)) * g
        # The test is only informative when the lattice is coarse relative to reporting
        # precision. Report its false-pass rate so a verdict is never quoted without its power.
        false_pass = min(1.0, 2 * ROUNDING_SLACK / g)
        gran = {"granularity": g, "miss": miss, "attainable": miss <= ROUNDING_SLACK,
                "false_pass_rate": false_pass, "informative": false_pass <= 0.35}

    return Audit(len(points), k, r, leverage, drop_rng, fz,
                 1.0 / factorial(k), comb(2 * k - 1, k), gran, skipped)


def report(a: Audit, name: str = "", reported_r: float | None = None) -> str:
    """Render an Audit as the human-readable block printed by the CLI.

    One line per check, then the recommendation. reported_r, when given, is echoed
    beside the recomputed r so a reader can see whether they agree.
    """
    L = []
    L.append(f"{name}" if name else "correlation audit")
    L.append(f"  {a.n_points} points over {a.k_units} independent units")
    rr = f"   reported {reported_r}" if reported_r is not None else ""
    L.append(f"  r = {a.r:+.4f}{rr}")
    L.append("")
    if not a.leverage_computable:
        L.append(f"  leverage        NOT COMPUTABLE at k = {a.k_units} with these unit sizes "
                 f"(every removal leaves < 3 points)")
    else:
        flag = "ONE UNIT CARRIES THIS RESULT" if a.one_unit_carries else "no single unit dominates"
        L.append(f"  leverage        max drop-one |Δr| = {a.leverage:.3f}  "
                 f"[{a.drop_range[0]:.3f}, {a.drop_range[1]:.3f}]   {flag}")
    if a.fisher_z is None:
        L.append(f"  Fisher-z 95%    UNDEFINED at k = {a.k_units} (se = 1/√(k−3) needs k > 3)")
    else:
        L.append(f"  Fisher-z 95%    [{a.fisher_z[0]:+.3f}, {a.fisher_z[1]:+.3f}]   (df = k−3 = {a.k_units - 3})")
    L.append(f"  exact perm.     min attainable p = 1/{a.k_units}! = {a.min_p:.4f}   "
             f"{'test at .05 possible' if a.test_possible else 'NO test at .05 is possible'}")
    L.append(f"  bootstrap       ≤ C({2*a.k_units-1},{a.k_units}) = {a.atom_ceiling} distinct values   "
             f"{'usable' if a.bootstrap_meaningful else 'too coarse for a percentile CI'}")
    if a.skipped_units:
        L.append(f"  ⚠ leverage computed over {a.k_units - len(a.skipped_units)} of {a.k_units} units; "
                 f"dropping {', '.join(map(str, a.skipped_units))} left <3 points")
    if a.granularity:
        g = a.granularity
        verdict = 'ok' if g['attainable'] else 'NOT ATTAINABLE at this N'
        if not g['informative']:
            verdict = f"inconclusive — {g['false_pass_rate']:.0%} of arbitrary values pass this lattice"
        L.append(f"  granularity     multiple of {g['granularity']:.5f}; miss = {g['miss']:.5f}   {verdict}")
    L.append("")
    L.append(f"  → {a.recommendation()}")
    return "\n".join(L)


def _demo() -> int:
    """Run the audit on the two digitized datasets in data/ (PAPER.md section 2.1).

    Output is covered by a byte-for-byte parity test against the paper; do not
    change any printed text here without updating PAPER.md in the same commit.
    """
    here = Path(__file__).parent
    def rows(f):
        return [r for r in csv.DictReader(l for l in open(here / f) if not l.startswith("#"))]
    out = []
    try:
        rw = [r for r in rows("data/survey-roboworld.csv") if r["panel"].startswith("9a")]
        a = audit([(float(r["x_real"]), float(r["y_sim"])) for r in rw], [r["series"] for r in rw])
        out.append(report(a, "RoboWorld, Fig. 9a (GPT-4o score)", reported_r=0.989))
    except FileNotFoundError:
        out.append("data/survey-roboworld.csv not found")
    try:
        dc = rows("data/survey-digital-cousins.csv")
        a = audit([(float(r["x_real"]), float(r["y_sim"])) for r in dc], [r["policy"] for r in dc])
        out.append(report(a, "Digital Cousins (unit = architecture)", reported_r=0.91))
    except FileNotFoundError:
        out.append("data/survey-digital-cousins.csv not found")
    print(("\n\n" + "─" * 74 + "\n\n").join(out))
    print("\n" + "─" * 74)
    print("Same field, same kind of claim, opposite verdicts. RoboWorld has the larger k,")
    print("a p-value and a bootstrap — and one of its eight policies carries the result.")
    return 0


def main() -> int:
    """CLI entry point. Returns the process exit code (1 when a check fires, for CI)."""
    ap = argparse.ArgumentParser(
        description="Audit a sim-vs-real correlation: five checks (leverage, Fisher-z, "
                    "exact permutation, bootstrap support, granularity) on what the "
                    "experimental design can actually support. Input is a CSV with one "
                    "row per point and columns real, sim, unit (renameable below).",
        epilog="example:\n"
               "  python correlation_audit.py --csv results.csv\n"
               "  python correlation_audit.py --csv results.csv "
               "--n-episodes 20 --reported-mmrv 0.076 --json\n"
               "exit status: 1 if one unit carries the correlation, else 0.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="run on the datasets in this directory")
    ap.add_argument("--csv", help="CSV with columns: real, sim, unit")
    ap.add_argument("--real-col", default="real", help="column holding real-world rates")
    ap.add_argument("--sim-col", default="sim", help="column holding simulated rates")
    ap.add_argument("--unit-col", default="unit",
                    help="column naming the INDEPENDENT unit (e.g. policy, run_id) -- not the row")
    ap.add_argument("--json", action="store_true", help="machine-readable output for CI")
    ap.add_argument("--n-episodes", type=int)
    ap.add_argument("--reported-mmrv", type=float)
    args = ap.parse_args()
    if args.demo or not args.csv:
        return _demo()
    rs = [r for r in csv.DictReader(l for l in open(args.csv) if not l.startswith("#"))]
    if not rs:
        sys.exit(f"{args.csv}: no data rows")
    cols = {args.real_col, args.sim_col, args.unit_col}
    missing = cols - set(rs[0])
    if missing:
        sys.exit(f"{args.csv}: missing column(s) {sorted(missing)}.\n"
                 f"  found: {', '.join(rs[0])}\n"
                 f"  use --real-col/--sim-col/--unit-col to map them, e.g.\n"
                 f"    --real-col real_success --sim-col sim_success --unit-col policy")
    a = audit([(float(r[args.real_col]), float(r[args.sim_col])) for r in rs],
              [r[args.unit_col] for r in rs],
              n_episodes=args.n_episodes, reported_mmrv=args.reported_mmrv)
    if args.json:
        import json
        from dataclasses import asdict
        d = asdict(a)
        d["one_unit_carries"] = a.one_unit_carries
        d["bootstrap_meaningful"] = a.bootstrap_meaningful
        d["test_possible"] = a.test_possible
        d["recommendation"] = a.recommendation()
        print(json.dumps(d, indent=2))
    else:
        print(report(a, args.csv))
    # exit 1 when a check fires, so this can gate CI
    return 1 if a.one_unit_carries else 0


if __name__ == "__main__":
    sys.exit(main())
