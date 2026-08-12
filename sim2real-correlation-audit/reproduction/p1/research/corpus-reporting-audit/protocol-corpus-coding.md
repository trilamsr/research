# Independent-coder protocol (blind, estimand-first)

Self-contained instructions for independently coding the source facts behind the §8.0 survey. The
coder records the axes that enter each coefficient before anyone decides which axis should be treated
as an inferential unit. This avoids building the audit's preferred "training lineage" interpretation
into the supposedly independent coding.

The purpose is twofold:

1. measure agreement on observable source facts; and
2. expose, rather than hide, disagreements about the population a coefficient is meant to
   generalize to.

A 2026-07-21 pilot used same-model-family agents and an earlier protocol that prescribed training
lineage as the unit. It measured consistency in applying that rule, not independent validation of the
rule. It must not be reported as inter-rater validation of the estimand.

## Blinding rules — read first

1. Do **not** read PAPER.md, README.md, `research/corpus-reporting-audit/summarize_corpus.py`, or anything else in this
   repository except this file. Do not search for the audit paper or its codings.
2. Code **only** from the version-pinned source papers listed below (arXiv), and their
   public code repositories where the paper text is insufficient.
3. **Figures and appendices count as part of the paper.** Two known coding traps: values
   printed *inside* figure images are invisible to HTML text extraction, and statistics
   are sometimes printed only in appendix body text. If a field seems absent from the
   main text, check the figures (as images) and appendices before coding "none".
4. Use the pinned version, not "latest": append the version suffix to the URL, e.g.
   `arxiv.org/abs/2607.01060v4`. The audit's claims are provenance-labeled to these
   versions (verified current as of 2026-07-23); coding a different version confounds
   coder judgment with version drift.

## Separation of source facts and interpretation

Do not assign one universal `k`.

A coefficient may describe a fixed set of cells while a reader or author wants to generalize over
new policies, tasks, training runs, environments, or more than one of these axes. Those are different
estimands. Dependence matters for an inferential interpretation; it does not make a descriptive
correlation over a fixed displayed panel undefined.

### Layer A — source facts

Record what the pinned source explicitly provides:

- `coefficient_scope`: the rows/cells entering the headline coefficient.
- `displayed_points`: number of paired values entering it.
- `policy_models`: number of named policy/model variants.
- `base_lineages`: number of distinguishable base model families, or `?`.
- `training_runs`: number of separately trained runs explicitly documented, or `?`.
- `checkpoints`: number of checkpoints entering the coefficient, or `0`/`?`.
- `tasks`: number of tasks entering the coefficient, or `0`/`?`.
- `conditions`: number of perturbations, criteria, scenes, or other repeated conditions.
- `coefficient_axis`: `policy`, `task`, `checkpoint`, `condition`, `crossed`, `mean-of-correlations`,
  or a pipe-separated combination.
- `uncertainty_on_r`: `none`, `p-value`, `CI`, `bootstrap`, or a pipe-separated combination.
- `selection_rule`: whether the source states how the checkpoint/model state entering each
  coefficient point was chosen. Code `yes` when the rule covers every entering point (for example,
  a pre-specified step, all checkpoints, or a named selection criterion); `no` when checkpoint/model
  state can vary and no rule is stated; `partial` when the rule covers only some entering points or
  the source leaves material doubt about its coverage; and `not-applicable` only when the source
  establishes that the coefficient entails no checkpoint/model-state choice. A disclosed rule is
  still `yes` if it selects on real outcomes; this field records disclosure, not validity. Policy
  roster, open-source availability, episode filtering, task selection, and session filtering are
  not checkpoint-selection rules and must instead be recorded in `fact_ambiguity`.
- `source_passage`: page, section, figure, or table supporting the coding.
- `fact_ambiguity`: what the source does not establish. Do not resolve an ambiguity by assumption.

Per-point error bars are not uncertainty on the correlation.

### Layer B — claim and estimand

Record separately:

- `finite_panel_description`: whether the printed coefficient is defined as a description of the
  displayed cells (`yes`, `no`, `unclear`).
- `generalization_axis_stated`: `policy`, `task`, `run`, `condition`, `crossed`, `no`, or a
  pipe-separated combination. This records what the prose names or clearly implies.
- `target_population_defined`: whether the paper defines the population or sampling mechanism to
  which the coefficient is intended to generalize (`yes` or `no`).
- `new_policy_inference`: `supported`, `unsupported`, or `unidentified`.
- `new_task_inference`: `supported`, `unsupported`, or `unidentified`.
- `crossed_inference`: `supported`, `unsupported`, or `unidentified`.
- `interpretive_note`: one sentence explaining the distinction.

`Supported` requires more than having multiple entries on an axis. The source must define the target
population or sampling mechanism and use uncertainty appropriate to that axis. A high correlation
over a convenience panel is normally a finite-panel description, not automatically an estimate for a
superpopulation.

This original `supported` field is a design-based gate. It must not be treated
as exhaustive of non-sampling evidence. A broadened post-outcome recoding in
`result-inference-link-recoding.csv` separately records fixed-benchmark
validity, held-out predictive validation, transport assumptions, informal
operational generalization, and formally identified population prediction.
Several papers supply scientifically meaningful evidence in the first three
categories even though none defines a probability distribution or sampling
frame over future policies/tasks together with calibrated population-level
predictive uncertainty.

The broadened categories mean:

- `fixed_benchmark`: the claimed target is the named, exhaustively specified
  roster or suite; validity does not automatically extend beyond it;
- `operational_domain`: the prose intends reuse on similar future cases but
  does not define their probability distribution;
- `held_out_predictive_validation`: the evaluator is tested on a named policy,
  task, object, trajectory, or environment excluded from a relevant fitting or
  design stage; the source basis must state both what was held out and relative
  to which stage;
- `transport_assumption`: matched reconstruction, initial conditions, control,
  or another stated bridge is assumed to connect evaluator and real outcomes;
- `informal_representativeness`: diversity or coverage is asserted without a
  sampling frame or transport weights; and
- `formal_population_prediction`: a future-case distribution or sampling
  frame, link from the observed panel, and calibrated population-level
  predictive uncertainty are all present.

This broadened recoding is exploratory and judgment-bearing because it was
performed after outcome review in a model-assisted source recoding pass and
then spot-checked by the author on the strongest counterexamples. It is not
independent human source recoding or inter-rater validation. Its categorical
counts are not prevalence estimates. Paper-facing reliance is limited to the
construct correction and named primary-source examples. The roster-wide
absence of formal population prediction remains provisional pending
source-only human recoding; the raw `held_out` count is not a headline result.

Code an inference field `unsupported` only when the paper states or clearly implies generalization
along that field's axis but does not meet the support requirements above. Code it `unidentified`
when the paper neither states nor clearly implies an inference along that axis. In particular,
do not code every crossed-inference field `unsupported` merely because the displayed panel crosses
axes; the paper must make or clearly imply a crossed generalization claim.

### Layer C — optional sensitivity counts

Only after Layers A and B are frozen may the analyst derive interpretation-specific counts:

- `k_policy`: policy or lineage blocks, for a new-policy interpretation.
- `k_task`: task blocks, for a new-task interpretation.
- `k_run`: independently trained runs, when documented.
- `k_condition`: perturbation or condition blocks, where that is the target axis.

Every permutation resolution must name the chosen axis and scheme. For example:

> Under a one-sided full permutation of three exchangeable policy blocks,
> \(p_{\min}=1/3!=0.167\).

Do not shorten this to "the paper's minimum p is 0.167."

## Required output

Use one row per headline coefficient. If a paper averages several correlations or presents
materially different headline panels, use multiple rows.

The returned file must contain the Layer A and Layer B fields above plus:

- pinned arXiv version;
- coder identifier;
- coding date; and
- a flag for every field that required judgment.

Do not read `PAPER.md`, `README.md`, `research/corpus-reporting-audit/summarize_corpus.py`, `research/corpus-reporting-audit/audit_estimands.py`, or released coding grids
until the blind coding is complete.

## The 26 papers (version-pinned, verified current 2026-07-23)

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

1. Compare source-fact fields separately from interpretive fields.
2. Report raw agreement for every field.
3. Use Cohen's κ only for categorical fields where prevalence and category structure make it
   informative. Never pool fields.
4. List every disagreement with both readings and the exact primary-source passage.
5. Adjudicate source facts before discussing estimands.
6. Preserve defensible alternative estimands rather than forcing consensus.
7. Report corpus findings separately for fixed-panel description, new-policy inference,
   new-task inference, and crossed inference.
8. Re-verify the version pins immediately before final coding. If a version changed, diff and
   re-code it rather than silently updating the pin.
