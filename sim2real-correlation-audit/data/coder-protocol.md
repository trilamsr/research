# Independent-coder protocol (blind package)

Self-contained package for an independent coder — ideally a human, or at least a language model of a
different family from the one that produced the paper's codings — to re-code the §8.0 survey grid.
Purpose: inter-rater reliability (Cohen's κ) against the paper's codings, coded blind. A pilot
re-coding (2026-07-21, §8.1) used same-model-family agents and so measures consistency, not
independence; this package exists so anyone can run the real, human check.

## Blinding rules — read first

1. Do **not** read PAPER.md, README.md, `survey_table.py`, or anything else in this
   repository except this file. Do not search for the audit paper or its codings.
2. Code **only** from the version-pinned source papers listed below (arXiv), and their
   public code repositories where the paper text is insufficient.
3. **Figures and appendices count as part of the paper.** Two known coding traps: values
   printed *inside* figure images are invisible to HTML text extraction, and statistics
   are sometimes printed only in appendix body text. If a field seems absent from the
   main text, check the figures (as images) and appendices before coding "none".
4. Use the pinned version, not "latest": append the version suffix to the URL, e.g.
   `arxiv.org/abs/2607.01060v4`. The audit's claims are provenance-labeled to these
   versions (verified current as of 2026-07-21); coding a different version confounds
   coder judgment with version drift.

## Codebook

- **Rule 1 — unit.** A training checkpoint is not an independent unit; the training run
  is. Successive checkpoints of one run, per-task finetunes of one base, and
  perturbation conditions of one policy are one unit (one lineage). Sibling finetunes
  of a shared base: one lineage; if genuinely ambiguous, code your best reading and FLAG
  it with a one-line reason.
- **Rule 2 — uncertainty.** "Uncertainty on r" means uncertainty on the correlation
  itself (a p-value, CI, or bootstrap attached to r or ρ). Per-point error bars (CIs on
  individual success rates) do not count.
- **Rule 4 — selection rule.** "Rule stated" = the paper states which *checkpoint* of
  each policy enters the correlation (pre-specified step, explicit all-checkpoints,
  named selection criterion). Enumerating which *policies* were evaluated does not
  count.
  (Rule 3 governs inclusion and is not the coder's job: every paper below prints a
  sim-vs-real correlation coefficient for robot policy success.)

## Fields to code, per paper

1. `k` — independent training units behind the HEADLINE sim-vs-real correlation
   (integer; FLAG + reason if ambiguous)
2. `points` — scatter points behind that correlation (integer or `?`)
3. `uncertainty_on_r` — `none` | `p-value` | `CI` | `other`
4. `rule_stated` — `yes` | `no` (Rule 4)

Output format, one line per paper:

```
<arxiv-id> | k=<n>[FLAG: reason] | points=<n|?> | uncertainty=<code> | rule_stated=<yes|no>
```

## The 26 papers (version-pinned, verified current 2026-07-21)

| paper | pinned id |
|---|---|
| real2sim-eval | 2511.04665v2 |
| RoboWorld | 2607.01060v4 |
| Digital Cousins | 2604.15805v1 |
| SIMPLER | 2405.05941v1 |
| SimFoundry | 2606.28276v3 |
| WorldGym | 2506.00613v3 |
| RoboSnap | 2607.06699v1 |
| REALM | 2512.19562v1 |
| PolaRiS | 2512.16881v2 |
| SC3-Eval | 2606.18610v3 |
| WorldEval | 2505.19017v1 |
| A Practical Recipe | 2606.10366v1 |
| Cosmos-Surg-dVRK | 2510.16240v2 |
| Gemini/Veo | 2512.10675v2 |
| DreamDojo | 2602.06949v1 |
| dWorldEval | 2604.22152v1 |
| WEAVER | 2606.13672v2 |
| PlayWorld | 2603.09030v3 |
| EmbodiedSplat | 2509.17430v2 |
| MolmoSpaces | 2602.11337v2 |
| Mem-World | 2606.18960v2 |
| Colosseum V2 | 2605.27759v1 |
| VISER | 2605.06311v1 |
| OSCAR | 2606.04463v2 |
| Hi-WM | 2604.21741v2 |
| WM-PolicyEval | 2511.11520v3 |

## Afterward (for the analyst, not the coder)

Compare the returned grid to `survey_table.py` field-by-field; compute per-field percent
agreement and Cohen's κ; list every disagreement with both readings; resolve each by
returning to the pinned source, and record resolutions in §8.1. Report κ per field, not
pooled — the fields differ in difficulty, and a pooled number hides exactly the
construct problems this protocol exists to catch.

When you resolve a disagreement, the resolution is itself a claim about the source paper —
that it does or does not state uncertainty, does or does not name a checkpoint rule, has or
has not got independent units. Validate each resolution to the point of being undeniable
against the pinned source before recording it, in whichever direction it lands: a resolution
that vindicates the paper's coding must be as well-evidenced as one that overturns it.
Re-verify the version pins are still current before coding (the census tracks latest arXiv
versions; a bumped version is re-checked and re-pinned at submission, then diffed).
