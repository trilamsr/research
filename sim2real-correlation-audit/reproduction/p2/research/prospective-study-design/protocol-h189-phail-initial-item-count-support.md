# Protocol: H189 PhAIL initial-item-count support audit

Date fixed: 2026-07-28

Status: outcome-free protocol fixed before opening `eval.total_items`.
H189 is explicitly result-exposed to H187's metadata audit and does not revise
H187's estimand.

## Question and decision consequence

H187 identifies an 18-cell, 194-episode common-support target after crossing
UTC date with the four declared `BalancedSampler` fields. The PhAIL v1.0
release states that the operator loads \(N\) items before the system selects a
checkpoint and that this known count is recorded as episode metadata rather
than derived after the fact.

The question is:

> Does adding pre-assignment initial item count to the H187 context materially
> change positivity, the retained target, or the permitted scope of a future
> common-context comparison?

This can narrow or eliminate the H187 target. It cannot strengthen chronology,
exchangeability, or performance claims.

## Source and cohort

- Official release: `https://phail.ai/releases/v1.0`, retrieved 2026-07-28.
  The protocol places item loading before checkpoint selection and separately
  places successful-item recording after the episode.
- Cohort: the exact H187 official v1.0 594-rollout cohort at
  `phail/v1.0/dataset/rollouts/`.
- H187 inventory fingerprint:
  `8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982`.
- H187 sanitized-manifest fingerprint:
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.

Stop if the cohort, sidecar hashes, or 594 episode identities do not match
H187.

## Field boundary

Retain H187's exact output fields plus:

- `initial_item_count`, read only from literal top-level key
  `eval.total_items`.

Require a positive integer for all 594 episodes. Construct each output row
from an exact allowlist.

Never emit or analyze `eval.successful_items`, `eval.outcome`,
`eval.duration`, `eval.notes`, `eval.cap_per_item`, `meta.duration_ns`,
termination, safety, completion, HRT, rank, event-time, video, Parquet,
telemetry, or any other performance field.

## Analysis fixed before values

1. Report the item-count distribution overall and by policy.
2. Cross item count into:
   `task × object × tote × camera` over the full window.
3. Cross item count into:
   `UTC date × task × object × tote × camera`.
4. Report observed cells, policy counts, minimum policy exposure, and cells
   missing one or more policies.
5. Define the H189 restricted target as **every** date-context-item-count cell
   with positive exposure for all four policies, with equal weight across
   retained cells.
6. Compare the H189 target with H187's fixed 18 cells and 194 episodes using
   exact counts. Do not select a different time block, merge item counts, or
   use a performance field to regain support.

## Interpretation and stop rules

- Preserve a null change, narrowing, or complete loss of support.
- A support target is not an exchangeability certificate.
- No source-recorded session identity is available, and H187's chronology
  gate remains unresolved regardless of H189.
- H189 cannot authorize the performance-outcome phase.
- Do not revise H187 after observing H189.

## Validation

Before the full run:

- known-answer tests must show that the literal `eval.total_items` field is
  retained while synthetic successful-item, outcome, duration, and notes
  fields are excluded;
- invalid, missing, Boolean, zero, or nonintegral item counts must fail;
- output schema drift must fail; and
- result verification must recompute summaries from the hash-bound sanitized
  CSV.
