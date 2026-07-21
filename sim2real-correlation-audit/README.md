# Reproduction package — *What Does a Sim-to-Real Correlation Support? Five One-Line Checks and a Twenty-One-Paper Audit*

Everything a reader or reviewer needs to validate every number in the paper (`PAPER.md`).
Every quantitative claim traces to a script in this folder run on a CSV in `data/`; nothing is
hand-copied. The preregistration for the original checkpoint analysis is `PREREG-noise-floor.md`
(analyses beyond it are exploratory — paper §9).

## Quick start

```bash
make install    # one-time: venv with pinned numpy/scipy (+ pytest, matplotlib)
make verify     # full battery — ends with "ALL CHECKS PASSED"
```

`make verify` = `test` + `demo` + `survey` + `figures` + `results`. What success looks like:

**`make test`** — every headline number asserted, plus byte parity between the demo and paper §2.1:
```
18 passed in ~1s
```

**`make demo`** — paper §2.1, recomputed live:
```
RoboWorld, Fig. 9a (GPT-4o score)
  8 points over 8 independent units
  r = +0.9888   reported 0.989
  leverage        max drop-one |Δr| = 0.191  [0.798, 0.994]   ONE UNIT CARRIES THIS RESULT
  ...
```

**`make survey`** — §8's counts regenerated from the coded table:
```
surveyed: 21   excluded: 5   recovered: 11/21
P1 fewer than 10 independent units : 20/21
...
```

**`make figures`** — Figures 1–3 rebuilt, each printing its verification line:
```
VERIFY 9a: r_full=0.9888 (paper 0.989)  r_without_Binning=0.7980 (paper 0.798)
VERIFY survey: n=21  k=1: 4 (paper: 4)  k=2-3: 6 (paper: 6)
VERIFY DC: pooled r=0.9094 (paper 0.9094)  max drop-one |dr|=0.0130 (paper 0.013)
VERIFY comb: distinct multisets=35 (<=35)  distinct r atoms=35  draws below 2.5% quantile=4/256
```

**`make results`** — the preregistered analysis regenerated and diffed against the released output:
```
OK: results.json regenerates identically
```

Also: `make coverage` (§6.1 simulation, ~2 s), `make clean`. Raw per-command equivalents are in the
reproduction table at the bottom of this file.

## Layout

```
Makefile                make install / verify / test / demo / survey / figures / results / coverage
correlation_audit.py    the five checks (§2); --demo reproduces §2.1; --csv runs on your own data
survey_table.py         the 21-paper survey as data + every §8 count derived from it
measure_noise_floor.py  the preregistered checkpoint analysis → results.json (hash-locked; do not edit)
fz_coverage.py          Fisher-z coverage simulation (§6.1)
pixel_reextract.py      independent pixel-level re-extraction bounding extraction error (§3.1)
tests/                  known-answer tests; fix the tests never the audited code
figures/                make_figures.py + the three generated figures (PNG for the paper, PDF for LaTeX)
data/                   one CSV per source paper + its own README with per-file validation gates
```

## Methodology: how every number was produced

### 1. Data recovery from published figures (§3)

No surveyed paper publishes machine-readable results, so scatter coordinates were recovered from the
**vector drawing operators** of figures inside arXiv e-print tarballs (`arxiv.org/e-print/<id>`):
marker paths are parsed from the PDF content stream, mapped to data coordinates by least-squares
calibration against axis ticks/gridlines (calibration residuals ≤ 0.4 pt throughout), and legend
markers excluded geometrically. Every dataset passed a **validation gate** before use: the Pearson
*r* computed from the extracted points must reproduce a statistic printed by the source paper
(tolerances per file, ≤ 0.005 always, usually ≤ 0.001; each CSV header records its gate and result).
Extraction error was independently bounded by re-extracting RoboWorld Fig. 9a with a pixel-level
method (300 dpi render, color-blob detection, independent calibration): worst per-point deviation
0.61 x-units on one occluded marker, |Δr| = 0.0001 (`pixel_reextract.py`).

An *r*-based validation licenses *r*-based claims only (paper §3.1): reproducing *r* cannot certify a
metric whose definition had to be guessed (§7.2), and one figure (RoboSnap) deviates from its own
paper's numeric table (`data/robosnap-data/`, Appendix A).

### 2. The five checks (§2), with the math

For k independent units with paired (real, sim) values, Pearson r computed over the points:

- **Leverage (drop-one).** For each unit u, recompute r with u's points removed; report
  max_u |r − r_(−u)| and the range [min_u r_(−u), max_u r_(−u)]. Fires at max |Δr| > 0.10
  (any cutoff in [0.09, 0.12] selects the same firings on our 22 datasets). The design-level
  quantity is the hat (leverage) value h_u = 1/k + (x_u − x̄)² / Σ(x_j − x̄)², max 1.0, Σh = 2
  in simple regression.
- **Fisher-z.** z = atanh(r); interval tanh(z ± 1.96/√(k−3)). Where each unit contributes one
  point this is the textbook CI. Where points outnumber units we report either the
  aggregate-then-z interval (unit means, honest but wide) or the pooled-center bound
  (atanh(r_pooled) ± 1.96/√(k−3)) labeled as a **reference bound, not a calibrated CI** —
  `fz_coverage.py` measures its coverage at 97–100% (conservative) except under leverage
  geometry (87.5% worst case), while the naive pooled interval with n = all points covers as
  little as 4–20%.
- **Exact permutation.** The minimum attainable one-sided p over unit relabelings is **1/k!**
  (0.5 at k=2, 0.167 at k=3, 0.0417 at k=4); two-sided at most doubles it. Below k=4 no
  permutation test can reach p = 0.05.
- **Bootstrap support.** Resampling k units with replacement yields at most **C(2k−1, k)**
  distinct multisets (3, 10, 35, 126 for k = 2..5), so a percentile CI at small k rests on a
  handful of atoms; we verified exactly 35 distinct r-atoms at k=4 on Digital Cousins, with 4 of
  256 resamples below the 2.5% cutoff.
- **Granularity.** A success rate over n episodes lies on the lattice j/n; MMRV over N items is a
  multiple of 1/(N·n_ep). A published 3-decimal value passes within rounding slack with
  probability min(1, 0.001·N·n_ep) for an arbitrary number — the check's own false-pass rate,
  reported alongside every verdict.

### 3. MMRV and its conventions (§7)

MMRV (Mean Maximum Rank Violation, SIMPLER Eq. 1) = (1/N) Σ_i max_j [violation(i,j) · gap(i,j)].
Conventions found in the wild differ in two places and **no paper states its choice**:

- violation: sign-product (S_i−S_j)(R_i−R_j) < 0 (ties excluded) vs order-XOR readings
  ((R_i≤R_j) ≠ (S_i≤S_j), tie-inclusive)
- gap: real-side |R_i−R_j| (SIMPLER's definition) vs simulated-side |S_i−S_j|

The subject paper's values reproduce to print precision only under **≤-XOR violations weighted by
the simulated-side gap** — identified by brute-forcing the convention grid against two figures at
once (Table I: 0.0765/0.1741/0.1083 vs published 0.076/0.174/0.108; its 200-episode appendix figure:
exactly 21/200, 307/2000, 209/3000). Our §7 stability tables use sign-product + real-side (stated in
the paper); conclusions are convention-robust (§7 footnote).

### 4. The survey (§8)

`survey_table.py` holds one row per paper: k (independent units behind the headline correlation,
under the paper's Rule 1 — a training run is a unit, a checkpoint is not, a task is not a policy),
uncertainty-on-r, rule-stated, recovered. Every cell was verified against the source paper's full
text at least twice, by independent passes, with quotes recorded in paper §8.0/§8.1. Running the
script prints every count used in §8; the paper's numbers are generated from it, never typed.
Sensitivity of all counts to the unit-coding rule is reported in §8.1.

### 5. Verification protocol

Every number passed through at least two independent recomputations (most through four): fresh-code
recomputation sweeps, source re-fetches for survey cells, obtainment attempts for every absence
claim (git history, project sites, HuggingFace listings, high-zoom raster reads), and adversarial
attacks on both irreproducibility claims. This protocol overturned two of our own draft claims
(paper §7.2 and Appendix A) before publication; the corrections are part of the paper's record.

## Data

One CSV per source paper. Every file carries a provenance header: source figure and e-print path,
extraction method, calibration residuals, validation gate and result, known caveats (coincident
markers, duplicates, unit rules).

| file | contents | validation |
|---|---|---|
| `real2sim-eval-fig3-checkpoints.csv` / `…-fig9-200ep.csv` | 52 (real, sim) checkpoint pairs, 3 tasks × 4 policies (subject paper Fig. 3); and 52 points from its 200-episode appendix eval, with per-point Clopper–Pearson whisker validation recovering episode counts (sim n=200, real n=20/27/16) | r ≤ 0.0004 / ≤ 0.00014; MMRV exact under §7.2's convention |
| `roboworld.csv` | 4 panels × 8 policies (Figs. 9–10) | all four printed r ≤ 0.0005; pixel re-extraction |Δr| = 0.0001 |
| `digital-cousins.csv` | 16 points, 4 architectures × 4 generalization levels | r = 0.9094 vs printed 0.91; exact match to the paper's numeric tables |
| `realm.csv` | 4 panels, 77 points, task/policy labels | panel r ≤ 0.0038; 3 of 4 printed MMRVs reproduce (V-VIEW's cannot — paper §7.2) |
| `cosmos-surg-dvrk.csv` | 2 panels × 24 points, run/checkpoint labels; header documents the divide-by-panel-max axis rendering | r Δ ≤ 0.00005 both panels |
| `dreamdojo.csv` | 6 checkpoint points, one training lineage | r Δ = 0.00035 |
| `molmospaces.csv` | pick (×2 sources), open, close panels, 24 rows | r Δ ≤ 0.0027, ρ exact; documents the text-vs-figure ρ discrepancy |
| `robosnap.csv` | 10 plotted points + the paper's own inline-table ground truth, per-point deltas | as-plotted r = 0.9089 and table r = 0.887 both reproduce exactly (Appendix A) |

Raster-only papers (EmbodiedSplat, Mem-World) and the excluded papers have no data folder;
in-figure values for them were verified by character-level zoom reads and are quoted, not extracted
(paper §8.0/§8.1).

## Reproducing headline paper numbers, one command each

| paper claim | command |
|---|---|
| §2.1 blocks (RoboWorld vs Digital Cousins) | `python correlation_audit.py --demo` |
| §8 counts (20/21, 16/21, 6/21 + 4/21, …) | `python survey_table.py` |
| §4/§4.2 leverage values, Fig. 1–3 numbers | `python figures/make_figures.py` |
| §5 flip, §7.1 granularity, robustness rows | `python measure_noise_floor.py --data data/real2sim-eval-fig3-checkpoints.csv --out .` then inspect `results.json` |
| §6.1 coverage percentages | `python fz_coverage.py` |
| §3.1 extraction-error bound | `python pixel_reextract.py <path-to-RoboWorld-fig-9-pdf>` (e-print: arxiv.org/e-print/2607.01060) |
| everything above, asserted | `python -m pytest tests/` |

The preregistration linter referenced in paper §9 lives at the repository root:
`harness/prereg_lint.py`.
