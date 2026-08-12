# Corpus reporting audit

## Purpose

This family owns the bounded 26-paper corpus, recovered numeric source records,
coding protocol, independent codings, adjudicated estimand grid, and reporting
summaries. It is paper-complete for the included corpus but is not a systematic
review denominator or a coefficient-complete inventory of every secondary
result.

## Inputs and provenance

`sources/` is the preserved multi-file source collection. Each
`source-<paper>.csv` header records the pinned source version, extraction or
transcription method, validation gate, and caveats. The two blind coding CSVs
and their notes preserve each source-only recoding exactly as returned.
`protocol-corpus-coding.md` defines the fields,
`protocol-completeness-search.md` and `sources/log-arxiv-search.txt` document
the bounded search, and `review-estimand-adjudication.md` records adjudication.
`protocol-decision-case-eligibility.md` separately defines the finite-panel
decision-case gate and the source-claim alignment fields. Its generated
`result-decision-eligibility.csv` accounts for all 26 papers, including every
excluded decision case and its reason; it is completeness accounting within an
outcome-exposed bounded corpus, not a prevalence denominator.
`result-headline-claim-decision-alignment.csv` records the primary-source action
claim, every companion metric considered, and whether the exact displayed
top-policy rule is source-specified or audit-defined for each headline case.
`result-matrix-source-disposition.csv` accounts for every retained numeric
source file under the direct-cell matrix rule.
`result-complete-matrix-decisions.csv` reports all 19 eligible complete
direct-cell matrices. It is deliberately unbalanced by outcome (17 correct, 2
wrong), preventing the illustrative eight-case display from being mistaken for
a complete matrix ledger.
`result-inference-link-recoding.csv` is an exploratory broadened independent source review
that distinguishes fixed-benchmark and held-out predictive evidence from
formal population prediction. It supersedes any interpretation of the original
design-based `supported` field as an exhaustive inferential verdict, but its
category counts are judgment-bearing and not paper-prevalence estimates.
The blinded human replacement task is separately owned by the project-root
`SOURCE-ONLY-RECODING-INSTRUCTIONS.md`, `SOURCE-ONLY-PAPER-ROSTER.csv`, and
`SOURCE-ONLY-RECODING-FORM.csv`. It is intentionally paper-level and includes
both the frozen core constructs and the broadened inference-link constructs;
the older coefficient-level protocol remains the owner of the preserved
coefficient codings, not the human-fielding packet.

## Reproduction

From the project root:

```bash
.venv/bin/python research/corpus-reporting-audit/summarize_corpus.py
.venv/bin/python research/corpus-reporting-audit/audit_estimands.py
.venv/bin/python research/corpus-reporting-audit/compare_estimand_codings.py
.venv/bin/python research/corpus-reporting-audit/audit_decision_eligibility.py --check
.venv/bin/python research/corpus-reporting-audit/audit_claim_decision_alignment.py
.venv/bin/python research/corpus-reporting-audit/audit_complete_matrix_decisions.py --check
.venv/bin/python research/corpus-reporting-audit/audit_inference_links.py
.venv/bin/python research/corpus-reporting-audit/audit_source_only_recoding_packet.py
.venv/bin/python -m pytest research/corpus-reporting-audit -q
```

When a blinded human response is returned, validate it before opening prior
codings and optionally write a non-overwriting hash lock:

```bash
.venv/bin/python research/corpus-reporting-audit/validate_source_only_recoding_response.py \
  /path/to/locked-response.csv \
  --lock-out /path/to/locked-response.json
```

The coordinator-only selection, transmission, correction, locking, and
post-lock adjudication sequence is fixed in
`protocol-p1-source-only-human-recoding-fielding.md`. It is not part of the
source-only packet sent to the coder.

The source-native Real2Sim Figure 3 reconstruction additionally requires the
hash-locked arXiv `2511.04665v2` e-print archive and its extracted
`figures/exp-corr.pdf`, `figures/exp-curve.pdf`, and
`sections/04-experiments.tex` members:

```bash
.venv/bin/python research/corpus-reporting-audit/reextract_real2sim_figure3.py \
  --asset-root <extracted-2511.04665v2-with-archive> \
  --output-dir work/real2sim-figure3-source-reconstruction
REAL2SIM_ASSET_ROOT=<extracted-2511.04665v2-with-archive> \
  .venv/bin/python research/corpus-reporting-audit/check_reextract_real2sim_figure3.py
pdftocairo -svg \
  <extracted-2511.04665v2-with-archive>/figures/exp-corr.pdf \
  work/real2sim-figure3-poppler/exp-corr.svg
.venv/bin/python research/corpus-reporting-audit/challenge_real2sim_figure3_poppler.py \
  --svg work/real2sim-figure3-poppler/exp-corr.svg
.venv/bin/python research/corpus-reporting-audit/validate_real2sim_figure3_poppler_challenge.py
```

`review-real2sim-figure3-source-reconstruction-2026-07-29.md` records the
locked identities, producer result, method-distinct Poppler challenge,
dispositions, and the exact boundary between displayed-coordinate
reconstruction and unavailable experiment/run evidence.

Real2Sim Figure 9 uses the same locked archive plus
`figures/app-corr-200.pdf` and `figures/exp-curve.pdf`. The producer requires
PyMuPDF `1.24.14`; the independent path requires a Poppler SVG prepared from
the locked Figure 9 PDF:

```bash
.venv/bin/python research/corpus-reporting-audit/reextract_real2sim_figure9.py \
  --asset-root <extracted-2511.04665v2-with-archive> \
  --output-dir work/real2sim-figure9-source-reconstruction
.venv/bin/python research/corpus-reporting-audit/validate_real2sim_figure9_reconstruction.py \
  --input-dir work/real2sim-figure9-source-reconstruction
pdftocairo -svg \
  <extracted-2511.04665v2-with-archive>/figures/app-corr-200.pdf \
  work/real2sim-figure9-poppler/app-corr-200.svg
.venv/bin/python research/corpus-reporting-audit/challenge_real2sim_figure9_poppler.py \
  --svg work/real2sim-figure9-poppler/app-corr-200.svg \
  --pdf <extracted-2511.04665v2-with-archive>/figures/app-corr-200.pdf \
  --output-dir work/real2sim-figure9-poppler
.venv/bin/python research/corpus-reporting-audit/validate_real2sim_figure9_poppler_challenge.py \
  --input-dir work/real2sim-figure9-poppler
```

`review-real2sim-figure9-source-reconstruction-2026-07-29.md` records the
hidden-aware producer census, the visible-only challenge boundary, the
post-comparison signed-zero serialization correction, and the exact
source-experiment evidence that remains unavailable.

The other priority source-native reconstructions acquire exact public assets
from their pinned URLs and fail closed on their recorded hashes:

```bash
.venv/bin/python research/corpus-reporting-audit/reextract_cosmos_surg.py \
  --out work/result-cosmos-surg-source-reconstruction.json
.venv/bin/python research/corpus-reporting-audit/reextract_wm_policyeval.py \
  --out work/result-wm-policyeval-source-reconstruction.json
.venv/bin/python research/corpus-reporting-audit/reextract_oscar.py \
  --out work/result-oscar-source-reconstruction.json
cmp work/result-cosmos-surg-source-reconstruction.json \
  research/corpus-reporting-audit/result-cosmos-surg-source-reconstruction.json
cmp work/result-wm-policyeval-source-reconstruction.json \
  research/corpus-reporting-audit/result-wm-policyeval-source-reconstruction.json
cmp work/result-oscar-source-reconstruction.json \
  research/corpus-reporting-audit/result-oscar-source-reconstruction.json
```

These three commands require network access to arXiv and, for WM-PolicyEval,
the exact pinned appendix on GitHub. Their canonical result records retain the
source identities and missing-upstream-input boundaries.

Their method-distinct challenge requires Poppler conversions of the locked
native figures and the pinned OSCAR release metadata described in
`review-cosmos-wm-oscar-source-reconstruction-2026-07-29.md`:

```bash
.venv/bin/python research/corpus-reporting-audit/challenge_source_reconstructions_poppler.py \
  --work-dir <prepared-poppler-work> \
  --asset-dir <locked-challenge-assets> \
  --out-dir work/source-reconstruction-poppler-challenge/output
.venv/bin/python research/corpus-reporting-audit/validate_source_reconstructions_poppler.py \
  --out-dir work/source-reconstruction-poppler-challenge/output
.venv/bin/python research/corpus-reporting-audit/validate_source_reconstruction_public_boundaries.py \
  --asset-dir <locked-challenge-assets> \
  --out-dir work/source-reconstruction-poppler-challenge/output
```

The independent RoboWorld pixel check additionally requires the pinned v4
source figure identified in `sources/source-roboworld.csv`:

```bash
.venv/bin/python research/corpus-reporting-audit/reextract_roboworld_pixels.py \
  --pdf <extracted-v4>/appendix_figure/ranking_plot_compare_gpt_gemini_pearson_score.pdf
```

`review-roboworld-version-provenance.md` records the v3/v4 identity check, the
pixel-path repair, current acceptance tolerances, and the remaining access
requirement.

The canonical outputs are `result-estimand-grid.csv`,
`result-unit-count-sensitivity.csv`, `result-pvalue-resolution.csv`, and
`result-decision-eligibility.csv`, with
`result-headline-claim-decision-alignment.csv` as the source-to-action record
for paper-facing cases and `result-complete-matrix-decisions.csv` as the
outcome-complete matrix ledger. `result-inference-link-recoding.csv` owns the
broadened post-outcome inferential-link review.

## Dependencies and access

This family has no computational dependency on another project family. It
tracks the repository-wide external findings ledger at `../../../FINDINGS.md`.
Re-running the search requires network access; reproducing summaries from the
retained sources does not. Exact re-extraction additionally requires the
pinned source papers or assets identified in each source header.

## Recovered source records

`sources/source-simpler-decisions.csv` is a direct transcription of the official
SIMPLER repository's machine-readable `REAL_PERF` and `SIMPLER_PERF`
dictionaries. It supports the bounded decision case added to the combined
audit: equal-weight the displayed tasks within each embodiment, then compare
the finite-panel real and simulated top-policy sets. This aggregate is the
audit's declared decision, not a coefficient printed by SIMPLER.

`sources/source-worldgym-decisions.csv` is a direct transcription of
WorldGym's source-of-record 3-policy × 17-task appendix table.

Files are named `source-<paper>.csv` inside `sources/`, one per surveyed paper
whose data we recovered. Each was
extracted from a published figure (vector drawing operators where available, pixel reads otherwise)
or transcribed from a printed table, and validated by reproducing a statistic the source paper
printed. Each CSV's header comments record the exact source, extraction method, calibration
residuals, validation gate, and known caveats. Full methodology is in the
project `README.md` and paper.

| file | source paper (arXiv) | points | validated against |
|---|---|---|---|
| `source-real2sim-eval-fig3-checkpoints.csv` | real2sim-eval (2511.04665) | 52 — 3 tasks × 4 policies × 3–6 plotted operations | exact source-native reconstruction and method-distinct challenge; Table I r to ≤ 0.0004; MMRV exact under §7.2's convention |
| `source-real2sim-eval-fig9-200ep.csv` | real2sim-eval (2511.04665) | 52 — 200-episode appendix eval | exact source-native visible-row reconstruction and method-distinct challenge; printed r to ≤ 0.00014; vector whiskers validate as Clopper–Pearson bounds |
| `source-roboworld.csv` | RoboWorld (2607.01060v4; scientific source identical to v3) | 32 — 4 panels × 8 policies | all four printed r to ≤ 0.0005; independently challenged vector and pixel re-extractions |
| `source-digital-cousins.csv` | Digital Cousins (2604.15805) | 16 — 4 architectures × 4 levels | printed r = 0.91; exact match to its numeric tables |
| `source-realm.csv` | REALM (2512.19562) | 77 — 4 panels | panel r to ≤ 0.0038; 3 of 4 printed MMRVs |
| `source-cosmos-surg-dvrk.csv` | Cosmos-Surg-dVRK (2510.16240) | 48 — 2 panels × 24 | source-native reconstruction plus method-distinct challenge; both printed r to ≤ 0.00005 |
| `source-dreamdojo.csv` | DreamDojo (2602.06949) | 6 — one training lineage | printed r to 0.00035 |
| `source-molmospaces.csv` | MolmoSpaces (2602.11337) | 24 rows — pick ×2, open, close | printed r to ≤ 0.0027; Spearman exact |
| `source-robosnap.csv` | RoboSnap (2607.06699) | 10 + the paper's own inline table | as-plotted r = 0.9089 and table r = 0.887 both exact; coauthor confirms the table is the numerical source of record and the markers were positioned manually for presentation |
| `source-viser.csv` | VISER (2605.06311) | 9 — Table 5 transcription | all 4 printed r exact; real column traced to SIMPLER + OpenVLA (§8.1) |
| `source-oscar.csv` | OSCAR (2606.04463) | 7 policies — Fig. 1 bar labels | source-native reconstruction plus method-distinct challenge; Pearson +0.852 reproduces (0.8552); ρ/MMRV not jointly reproducible (§8.1) |
| `source-hi-wm.csv` | Hi-WM (2604.21741) | 12 — Fig. 6a raster extraction | printed r = 0.953, extracted 0.954 |
| `source-wm-policyeval.csv` | WM-PolicyEval (2511.11520) | 24 — Fig. 6b vector extraction | source-native reconstruction plus method-distinct challenge; points exact (drawn lines to 0.0006) but r = 0.719 ≠ printed 0.687 (§8.0) |
| `source-weaver.csv` | WEAVER (2606.13672) | 30 — 3 vector panels × 10 | all three panels' ρ and r to ≤ 0.002 |
| `source-worldeval.csv` | WorldEval (2505.19017) | 20 — 5 panels × 4 policies, raster | pooled r = 0.926 vs printed avg r = 0.942 |
| `source-gemini-veo.csv` | Gemini/Veo (2512.10675) | 8 — pixel-read | Pearson 0.888 = printed 0.88 |
| `source-embodiedsplat.csv` | EmbodiedSplat (2509.17430) | 8 — pixel-read | Poly Pearson 0.976 / DN 0.866 (the "SRCC" is Pearson, §8.1) |
| `source-colosseum-v2.csv` | Colosseum V2 (2605.27759) | per-condition arrays from LaTeX source | avg R² 0.798 and avg Spearman 0.916 reproduce exactly |
| `source-recipe-rankings.csv` | A Practical Recipe (2606.10366) | 11 rank tables | Spearman ρ reproduces exactly from ranks; Pearson not recoverable |
| `source-simpler-decisions.csv` | SIMPLER (2405.05941) | 42 task-policy rows | exact official `REAL_PERF`/`SIMPLER_PERF` source dictionaries; decision aggregate newly declared here |
| `source-worldgym-decisions.csv` | WorldGym (2506.00613v3) | 51 task-policy cells | pooled r = 0.784786 vs printed 0.78; source mean rates exact |

The coordinates are facts recovered from the papers' own published figures; the renderings in those
papers remain theirs. Five surveyed papers have no full recovered-data CSV: SC3-Eval and PlayWorld
(markers too heavily occluded to de-conflict), dWorldEval and Mem-World
(recoverable only in part), and PolaRiS (the point cloud recovers but its
per-environment estimator does not). Their source-fact codings and unresolved
ambiguities remain in `result-estimand-grid.csv`. See §3 of
`../../PAPER.md` for the recoverability accounting.
