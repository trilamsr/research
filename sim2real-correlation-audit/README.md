# What Does a Sim-to-Real Correlation Support?

**Five One-Line Checks and a Twenty-Two-Paper Audit** — paper (`PAPER.md`) and full reproduction
package. Every quantitative claim in the paper regenerates from a script in this folder run on a CSV
in `data/`; nothing is hand-copied.

## The paper in brief

Robot-learning papers increasingly justify evaluating policies in simulation by reporting a
correlation between simulated and real-world success. This paper asks what such a correlation can
actually support, given how few independent data points typically sit behind it. It contributes five
checks — each computable from a published scatter plot in one line — and applies them to every paper
we could find that reports a quantitative sim-to-real correlation for robot policies: twenty-two
papers, audited from data recovered out of their own published figures.

What the audit finds:

- **21 of 22** papers report their headline correlation over fewer than ten independent units
  (training runs), and five report it over a single unit, where a correlation across units does not
  exist as a quantity.
- **17 of 22** attach no uncertainty of any kind to the correlation.
- **6 of 22** report significance below the exact permutation floor — with $k$ units the smallest
  attainable one-sided $p$ is $1/k!$, so at $k=3$ no permutation test can reach $p=0.05$, yet
  $p<0.001$ appears in print.
- The good news: when the checks *can* run, they clear more often than they flag. The paper's
  recommendations require no new experiments — releasing the per-unit numbers behind one existing
  figure is enough.

The paper also documents an undocumented metric convention: the ranking metric MMRV is computed
differently across papers, no paper states its choice, and in one case the convention had to be
recovered by brute force against two figures at once (§7).

## The five checks

For $k$ independent units with paired (real, sim) values and Pearson $r$ over the points:

**1. Leverage (drop-one).** Recompute $r$ with each unit removed; report
$\max_u \lvert r - r_{(-u)} \rvert$ and the range of $r_{(-u)}$. Fires at $\max \lvert \Delta r
\rvert > 0.10$ (any cutoff in $[0.09, 0.12]$ selects the same firings on our 22 datasets). The
design-level quantity is the hat value

$$h_u = \frac{1}{k} + \frac{(x_u - \bar{x})^2}{\sum_j (x_j - \bar{x})^2}.$$

**2. Fisher-z interval.**

$$\tanh\left(\operatorname{atanh}(r) \pm \frac{1.96}{\sqrt{k-3}}\right)$$

With one point per unit this is the textbook CI. When points outnumber units, using $n$ = all points
covers as little as 4–20%; the paper's pooled-center variant is labeled a reference bound, not a
calibrated CI (coverage measured in `fz_coverage.py`: 97–100% conservative, 87.5% worst case under
leverage geometry).

**3. Exact permutation floor.** The minimum attainable one-sided $p$ over unit relabelings is

$$p_{\min} = \frac{1}{k!}$$

— 0.5 at $k=2$, 0.167 at $k=3$, 0.042 at $k=4$. Any smaller printed $p$ cannot come from a
permutation test at that $k$.

**4. Bootstrap support.** Resampling $k$ units with replacement yields at most

$$\binom{2k-1}{k}$$

distinct multisets (3, 10, 35, 126 for $k = 2 \ldots 5$), so a percentile CI at small $k$ rests on a
handful of atoms — verified exactly (35 distinct $r$ atoms at $k=4$).

**5. Granularity.** A success rate over $n$ episodes lies on the lattice $j/n$; MMRV over $N$ items
is a multiple of $1/(N \cdot n_{\text{ep}})$. A published 3-decimal value passes within rounding
slack with probability

$$\min(1,\; 0.001 \cdot N \cdot n_{\text{ep}})$$

— the check's own false-pass rate, reported alongside every verdict.

**MMRV** (Mean Maximum Rank Violation, SIMPLER Eq. 1):

$$\mathrm{MMRV} = \frac{1}{N} \sum_i \max_j \left[ \mathrm{viol}(i,j) \cdot \mathrm{gap}(i,j) \right]$$

Conventions in the wild differ in the violation reading (sign-product, ties excluded, vs
$\leq$-XOR, tie-inclusive) and the gap side (real vs simulated), and no paper states its choice —
the subject paper's values reproduce to print precision only under $\leq$-XOR violations weighted by
the simulated-side gap (§7.2).

## Verify everything

```bash
make install    # one-time: venv with pinned dependencies
make verify     # tests + demo + survey + figures + results — ends "ALL CHECKS PASSED"
```

`make verify` asserts every headline number: 26 known-answer tests including byte-for-byte parity
between `correlation_audit.py --demo` and paper §2.1, every §8 survey count regenerated from the
coded table (`survey_table.py`), all three figures rebuilt with printed verification lines, and the
preregistered analysis (`measure_noise_floor.py`, hash-locked) regenerating `results.json`
identically.

## Where the data comes from

No surveyed paper publishes machine-readable results, so scatter coordinates were recovered from the
**vector drawing operators** of figures inside arXiv e-print tarballs: marker paths parsed from the
PDF content stream, mapped to data coordinates by least-squares calibration against axis ticks
(residuals ≤ 0.4 pt), legend markers excluded geometrically. Every dataset passed a validation gate
before use: the extracted points must reproduce a statistic the source paper printed (≤ 0.005
always, usually ≤ 0.001). Extraction error was independently bounded by a pixel-level re-extraction
of one figure: $\lvert \Delta r \rvert = 0.0001$ (`pixel_reextract.py`).

One CSV per source paper lives in `data/`, each with a provenance header (source figure, method,
calibration residuals, gate and result, caveats) — see `data/README.md` for the per-file table.

Every number in the paper passed at least two independent recomputations; absence claims (data not
released) were verified by genuinely attempting to obtain the data — project sites, git histories,
HuggingFace, high-zoom raster reads — before being asserted. This protocol overturned two of our own
draft claims before publication; the corrections are part of the paper's record (Appendices A–B).

## Reproducing headline paper numbers, one command each

| paper claim | command |
|---|---|
| §2.1 blocks (RoboWorld vs Digital Cousins) | `python correlation_audit.py --demo` |
| §8 counts (21/22, 17/22, 6/22 + 5/22, …) | `python survey_table.py` |
| §4/§4.2 leverage values, Fig. 1–3 numbers | `python figures/make_figures.py` |
| §5 flip, §7.1 granularity, robustness rows | `python measure_noise_floor.py --data data/real2sim-eval-fig3-checkpoints.csv --out .` |
| §6.1 coverage percentages | `python fz_coverage.py` |
| §7.2 convention grid (60 variants, unique Table I match, V-VIEW unreachable) | `python mmrv_conventions.py` |
| §4.2 leverage null calibration (RoboWorld P = 0.002; k = 3 firings typical) | `python leverage_null.py` |
| §3.1 extraction-error bound | `python pixel_reextract.py <RoboWorld-fig-9 PDF>` |
| everything above, asserted | `python -m pytest tests/` |

Run your own scatter through the five checks: `python correlation_audit.py --csv yourdata.csv`.
The preregistration is `PREREG-noise-floor.md` (hash-locked; linter in `harness/prereg_lint.py`);
analyses beyond it are marked exploratory in the paper (§9).

## License and citation

Code is MIT-licensed (repo-root `LICENSE`). The extracted datasets in `data/` are released
CC BY 4.0 — factual coordinates recovered from the cited papers' own published figures; the figures
remain their authors'. To cite (`CITATION.cff` carries the same metadata):

```bibtex
@misc{lam2026sim2real,
  author = {Lam, Tri},
  title  = {What Does a Sim-to-Real Correlation Support?
            Five One-Line Checks and a Twenty-Two-Paper Audit},
  year   = {2026},
  url    = {https://github.com/trilamsr/research/tree/main/sim2real-correlation-audit},
  note   = {Draft v1.1, 2026-07-21}
}
```
