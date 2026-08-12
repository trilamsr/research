# Protocol: H187 PhAIL context-support audit

Date fixed: 2026-07-27

Status: outcome-free metadata protocol fixed after exploratory source discovery
and before episode-level outcome analysis. Phase 0 cohort resolution was fixed
before episode-field inspection.

## Research question

P2's pair-first counterexamples show that a global policy ranking need not
identify a common-context policy action when the evaluated pair determines the
context. PhAIL v1.0 is a materially different public real-robot system: the
operator creates an observable episode context before a sampler selects one of
four checkpoints, and the published action is a global scalar ranking.

The first question is deliberately outcome-free:

> Does the released PhAIL v1.0 exposure record give every evaluated policy
> adequate common support over the declared task, object, tote-placement,
> external-camera, and time/session contexts?

This is a design and support audit. It does not test which policy is best.

## Candidate and source identity

Primary candidate:

- PhAIL v1.0 release page, retrieved 2026-07-27:
  `https://phail.ai/releases/v1.0`;
- Positronic evaluation framework tag `v0.2.1`, tag object
  `e406176bc526babb06844a48e3627a5c0409eb74`;
- pinned sampler:
  `positronic/policy/sampler.py`;
- pinned configuration:
  `positronic/cfg/policy.py`;
- arXiv `2605.29710v1`; and
- analysis-repository discovery snapshot
  `18ce72d5703dcbbbb10a980336aa5a1622601fb4`.

The analysis repository is a discovery dependency, not yet a fixed release
dependency. The official page reports 594 evaluation runs at
`s3://positronic-public/phail/v1.0/dataset/`, while the discovery snapshot's
older data-audit documentation reports 524 inference episodes at
`s3://positronic-public/datasets/phail/v1.0/`. The official page reports 352
fine-tuning demonstrations; the same repository documentation reports 449.
Phase 0 must reconcile these identities before any result is relied upon.

### Phase 0 resolution fixed before episode-field inspection

Independent complete inventory enumeration established that the 524 episode
IDs are an exact subset of the 594 IDs: the latter adds episode IDs 524--593.
The 524 cohort is described by release tooling as production-variant filtered.
Both prefixes contain the same 449 training/teleoperation episode identities;
repository history changes the paper's count from 352 to 449, and no separate
352-episode selection manifest was found.

H187 therefore fixes the official release-page cohort of **594 rollouts** at
`phail/v1.0/dataset/rollouts/` as its primary target. This choice follows the
named v1.0 release and was made without episode outcomes or knowledge of the
published winner. The nested 524 production-filtered cohort may be reported
only as a prospectively named support sensitivity; it must not be merged with
the 594 cohort. UTC calendar date is the fixed time block. Missing context
values remain missing and cannot be recoded from outcome, note, event, video,
or telemetry fields.

### Pre-outcome protocol correction

Independent implementation challenge identified an internal inconsistency:
the protocol facts correctly listed `task` among the four `BalancedSampler`
grouping fields, but the research question and Phase 2 cell definition omitted
it. The support estimand was corrected to
`task × object × tote × camera × time` before any performance outcome was
opened and before reliance on the first generated support result. The rejected
candidate is not relied upon. This correction was driven by the pinned
assignment code and sanitized task metadata, not performance.

## Protocol facts fixed before metadata analysis

The release protocol states that, for each episode, the evaluator first
places the outbound tote and external camera and loads one object class. The
system then selects the checkpoint, and the operator is blind to model
identity. In framework tag `v0.2.1`, `BalancedSampler` conditions its counts on
the supplied context. The `phail_multiple` configuration supplies:

```text
task
eval.object
eval.tote_placement
eval.external_camera
```

This makes PhAIL a positive action-order contrast to the pair-first
counterexample in H151. It does not by itself prove realized balance,
positivity, exchangeability, or protection from time/session drift.

## Staged validation

### Phase 0 — release identity

1. Enumerate the exact public object inventory without opening outcome fields.
2. Record the storage prefix, object keys, sizes, modification metadata when
   supplied, and a stable content hash for every retained sidecar.
3. Reconcile the 594-versus-524 evaluation count and 352-versus-449 training
   count. If they are different releases or cohorts, name both and choose one
   prospectively for the audit.
4. Pin every code and data dependency to a revision or content manifest.

Stop before analysis if an exact evaluation cohort cannot be identified.

### Phase 1 — outcome-field exclusion

For each evaluation episode, a sanitizing loader may retain only:

- stable episode identity;
- policy/checkpoint identity;
- task and object;
- tote placement;
- external-camera placement;
- creation timestamp;
- session identity when recorded; and
- source path and content hash.

It must reject or discard before output every success, item-count, duration,
termination, safety, completion, HRT, rank, annotation, event-time, and other
performance field. Tests must fail when a prohibited field enters the
sanitized artifact.

### Phase 2 — support and order diagnostics

With all outcomes still sealed:

1. count policy exposure in every
   `task × object × tote × camera` cell;
2. report cells with zero policy support and the minimum policy count per
   cell;
3. quantify candidate-context imbalance using the full contingency table,
   without a performance interpretation;
4. audit policy adjacency, run length, and immediate repeats in chronological
   order;
5. repeat support summaries within declared session or fixed calendar-time
   blocks;
6. determine whether a common-cell target can include all four policies
   without extrapolation; and
7. freeze the exact target cells and standardization weights before any
   performance field is opened.

No null-hypothesis p-value is a design certificate. Report counts, maximum
absolute share deviations, support minima, and exact affected cells.

## Passing and adverse results

The design passes the narrow metadata gate only if:

- one exact released cohort is pinned;
- every policy has positive exposure in every retained target cell;
- no material time/session stratum used by the target has a missing policy;
- the chronological record does not reveal an undocumented candidate-specific
  exclusion or deterministic carryover rule; and
- one outcome-free target weighting can be fixed without using the published
  ranking.

Any failure is retained. A sparse supported target may be defined only from
outcome-free metadata and must be reported as a narrower target, not as repair
of the full release.

## Conditional outcome phase

Only after Phases 0--2 and their target weights are frozen may a separate
protocol open event-time outcomes. That phase would recompute the global
action under exact common-cell weighting and leave-one-session/configuration
perturbations, preserving agreement, tie, or reversal. H187 itself makes no
performance claim and does not authorize use of the mutable live leaderboard
as the outcome source of record.

## Scope and stop rules

- Do not call context-first order equivalent to randomized assignment.
- Do not infer within-cell scene replay; physical placements may still differ.
- Do not treat the four policies, one fixture, or four object classes as a
  population sample.
- Do not use the published winner to choose cells, weights, exclusions, or
  time blocks.
- Stop at a provisional source finding if release identity cannot be fixed.
- Do not download video or telemetry for this metadata gate.
