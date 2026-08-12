# Protocol: H251 three-source real-record application

Date fixed: 2026-08-11

Status: exploratory. The three sources were selected for complementary design
and provenance before aggregate performance analysis. During source screening,
the Hugging Face viewer displayed a small number of AnkIle example outcome
rows. No aggregate AnkIle, RoboArena, or TRI performance result was calculated
before this protocol. All outcome-bearing results remain exploratory.

Post-exposure encoding clarification, 2026-08-11: the AnkIle files use three
terminal labels, `success`, `failure`, and `timeout`, while their own summaries
define success rate as `success` versus the other two labels. The row-level
analysis therefore maps `success` to 1 and both `failure` and `timeout` to 0.
This clarification was recorded after the labels and aggregates were visible;
it does not change the exploratory status.

Source-format amendment after the first fail-closed TRI parse, 2026-08-11:
three CSV cells (one outcome array repeated in `Fig2.csv` and twice in
`FigS32.csv`) append one unmatched apostrophe after the closing bracket. The
parser may remove exactly that terminal character only when the remaining
value is a valid list; the repaired array must then reproduce the source's
declared rollout count, success count, and rate. The raw files remain unchanged
and the canonical result reports the repair count.

## Question and intended use

Can three public real-robot records show, respectively, (1) a positive
common-context finite-panel comparison, (2) why a connected pairwise benchmark
graph does not supply a common-context target, and (3) why a strong published
matched-bundle protocol may remain unreconstructable from its public tables?

The intended use is a bounded empirical application of P2's identification
framework. The smallest useful result is one exact, version-bound statement
about what each release identifies. The analysis will not estimate deployment
performance or a population prevalence.

## Fixed sources

1. AnkIle `real01b` R5 routing, marker, and square evaluation repositories at
   revisions recorded in the retained source manifest. These were selected
   because each advertises three policies evaluated on the same 50 declared
   state identifiers.
2. RoboArena `DataDump_07-17-2026` at revision
   `7931db81f3f6a48a3245427f7213a4c461f92ccc`.
3. Toyota Research Institute's Dryad release, *A careful examination of large
   behavior models for multitask dexterous manipulation*, DOI
   `10.5061/dryad.xd2547dxc`, public version dated 2026-04-07.

Source files used in calculations must be retained when practical or bound by
URL, revision, size, and SHA-256. Large videos and action arrays are out of
scope because none of the fixed estimands requires them.

## Fixed analyses

### AnkIle positive case

- Include every parseable submitted rollout in each fixed repository. Fail
  closed on duplicate policy-state keys, missing policy or state identifiers,
  terminal labels outside `success`, `failure`, and `timeout`, incomplete
  policy-by-state rectangles, or disagreement between declared and observed
  counts.
- Unit: one policy rollout at one declared initial-state identifier.
- Target: the exact released 50-state finite panel for each task. This is not a
  probability sample or a deployment population.
- Report, by task: policy count, state count, completeness, exact success count
  and rate, half-credit pair scores on matched states, route-graph edges and
  connected components, and the exact finite-panel winner set. Tied winners
  remain tied.
- Do not attach population confidence intervals: the releases provide one
  rollout per policy-state cell and the Sobol panel does not by itself define a
  probability-sampling law for deployment.

### RoboArena pairwise case

- Include every parseable public session. Graph construction uses all sessions
  containing at least two distinct named policies and is independent of the
  recorded outcome.
- Unit: evaluation session. Report the policy roster, co-occurrence edge count,
  connected components, edge-support distribution, and the number of sessions
  contributing to each policy-set size. Do not disclose evaluator names,
  instructions, feedback, or session identifiers.
- Treat a location/instruction label only as an observed metadata proxy, never
  as an exact physical context or reset. Report whether the release contains
  exact initial-state, reset, assignment-probability, pool-epoch, robot,
  retry-parent, or exclusion-ledger fields.
- No global performance ranking will be estimated. Connectivity of the
  policy-only co-occurrence graph is a support description, not identification
  of P2's common-context target.

### TRI protocol/release contrast

- Include every released CSV and classify hardware versus simulation rows from
  the published panel field. Verify internal array-length/count/rate identities
  without changing or selecting rows based on performance.
- Unit in the release: a reported method-task-panel outcome array. Report file,
  row, method, task, hardware-row, and rollout counts only in aggregate.
- Audit whether public columns expose bundle, initial-condition, realized
  order, reset, session, robot, operator, retry, exclusion, or policy-version
  identifiers. Do not infer that array position is a shared bundle identifier
  unless the release explicitly declares that semantics.
- Do not reconstruct route edges or compare policy performance when the public
  files cannot establish the matched-bundle join described in the paper.

## Integrity gates and interpretation

All scripts must be deterministic, emit aggregate non-identifying results, and
bind this protocol plus each used source by SHA-256. Known-answer tests must
cover graph components, matched half-credit scores, ties, duplicate rejection,
incomplete rectangles, and TRI count/rate reconciliation. Canonical output is
written only after every source-specific gate passes.

Stop or narrow a source to structural description if its declared join cannot
be reconstructed, if counts disagree materially, or if a source revision
differs from the fixed identity. A positive finite-panel result does not
validate reset execution, retries, policy artifacts, stochastic performance,
or transport beyond the displayed states. Missing public fields mean only that
the fixed release cannot support the claim.
