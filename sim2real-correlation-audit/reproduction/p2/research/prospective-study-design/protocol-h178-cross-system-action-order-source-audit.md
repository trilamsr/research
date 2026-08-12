# Protocol: H178 cross-system action/order source audit

Date fixed: 2026-07-27

Status: fixed after H177 metadata screening and roster freeze, before opening
new candidate full text.

## Dependency and roster

Use exactly the seven H177 frozen identities in
`result-h177-cross-system-action-order-roster.json`, SHA-256
`77bcbc919ae96157ee81347aec6ce36ccd69d33204414e38e9d51a340757ae09`:

1. AutoEval (`2503.24278`);
2. RoboArena (`2506.18123`) as the positive control;
3. GE-Sim 2.0 (`2605.27491`);
4. *A Practical Recipe Towards Improving Sim-and-Real Correlation for VLA
   Evaluation* (`2606.10366`);
5. UMI-Bench 1.0 (`2606.10382`);
6. GigaWorld-1 / WMBench (`2607.02642`); and
7. RoboDojo (`2607.04434`).

The H177 disposition input has SHA-256
`c65fca374047f36deb8e00a9600903bdbc1ee0c6272175c5912e9e333f7e4ae9`.
Do not add or remove identities after source inspection.

## Source freeze

For the three newly discovered identities, retrieve the official arXiv
abstract page and PDF. Because the official web-search fallback returned
versionless links, record the exact latest version shown by the abstract page
at retrieval and bind the PDF by SHA-256. Do not silently update it later.

For the four known systems, reuse existing exact-version public sources and
their recorded hashes where sufficient:

- AutoEval `2503.24278v2`;
- UMI-Bench `2606.10382v1`;
- RoboDojo `2607.04434v3`; and
- the existing pinned RoboArena paper/protocol and official-source records.

An official project page or repository may be opened only when linked by the
paper or project page and needed to resolve a fixed coding unit. Record owner,
title, stable URL, revision when available, exact location, retrieval time,
content hash, and limitation. Stop once every unit is resolved or bounded by
the fixed sources.

## Coding units

For each system, code exactly:

1. `declared_operational_action` — the public decision the evaluation is
   intended to support;
2. `candidate_pair_or_roster_fixed_before_context`;
3. `context_fixed_before_candidate_assignment`;
4. `stable_assignment_law_public`;
5. `stable_context_law_public`;
6. `declared_target_support_complete_or_bounded`;
7. `reset_carryover_rule_public`;
8. `cluster_or_session_identity_public`;
9. `public_action_matches_identified_estimand`; and
10. `target_compatible_positive_contrast`.

Statuses are:

- `available`: directly specified with a stable source and sufficient
  operational detail;
- `partial`: relevant evidence exists but a necessary identity, quantity,
  ordering relation, scope, or linkage is missing;
- `paper_described_only`: prose asserts the unit without a reproducible public
  record or implementation;
- `absent_from_fixed_sources`: absent from the complete permitted scope; or
- `unresolved`: access or ambiguity prevents a disposition.

For `declared_operational_action`, store a bounded action label rather than one
of the five evidence statuses. Permitted labels are
`global_policy_ranking`, `fixed_task_policy_score_or_ranking`,
`simulator_or_world_model_evaluation`, `policy_development_or_improvement`,
and `unresolved_action`.

Every non-action row also stores a semantic value:

- `satisfied` when the named design/evidence condition holds at the stated
  scope;
- `not_satisfied` when the source affirmatively establishes the opposite or
  the condition is inapplicable to the declared target; or
- `unresolved` when public evidence is absent, partial, ambiguous, or only
  indirectly related.

Evidence status and semantic value are separate. For example, a paper may
directly establish that context was *not* fixed before candidate assignment:
that row is `available` with value `not_satisfied`. Conversely, silence is
`absent_from_fixed_sources` with value `unresolved`, not `not_satisfied`.

## Semantic rules

- A fixed task list is not a context distribution unless the target weights
  or full finite panel are declared.
- A policy queue is not a random assignment law.
- Running multiple policies is not complete support unless the target
  policy-by-context matrix or an honest missingness rule is public.
- An automated reset is not verified washout or carryover control.
- Episode totals are not cluster/session identity.
- A leaderboard is an action declaration, not proof that its score identifies
  a common target.
- A sim/real correlation study can be a finite-panel positive contrast only
  if the real policies, contexts, aggregation/action, support, reset, and
  cluster units are sufficiently public for that finite panel.
- A pair-first mechanism with freely chosen or pair-dependent context cannot
  identify a common-context global ranking without a bridge.
- Do not infer operational absence from missing public evidence.
- Do not extract or use performance direction, magnitude, significance, or
  leaderboard standing.

## Decisions

### Second mismatch

`second_mismatch_found` requires a non-RoboArena system with:

1. a declared global or common-target ranking/selection action;
2. candidate identity fixed before a pair- or candidate-dependent context is
   chosen or generated;
3. no public bridge to a common context target; and
4. source evidence sufficient to distinguish this from missing reporting.

### Positive contrast

`positive_contrast_found` requires a non-RoboArena system with:

1. a declared finite-panel or population action;
2. context fixed before candidate assignment, or a complete declared
   candidate-by-context finite panel;
3. a public assignment/execution rule;
4. complete or honestly bounded target support;
5. public reset/carryover handling; and
6. public cluster/session identity sufficient for the claimed uncertainty or
   finite-panel evidence.

For the bounded protocol-level decision, `available` or
`paper_described_only` may support a satisfied conjunction when the public
paper fixes the exact finite roster, context/episode list, execution rule, and
episode identity. Classify the contrast `source_described` unless public
artifacts independently reproduce those units. `partial`,
`absent_from_fixed_sources`, and `unresolved` cannot satisfy a conjunction.

If neither conjunction is met, return
`no_second_instantiation_in_bounded_frame`. Use `discovery_inconclusive` if
source retrieval or ambiguity prevents the bounded decision.

## Validation and challenge

- Emit all 70 system×unit rows.
- Bind every retained source and H177 dependency by exact hash.
- Test exact roster coverage, allowed statuses, action labels, conjunction
  logic, outcome-field exclusion, source locators, and byte-for-byte
  regeneration.
- Attack promotions based on fixed tasks alone, a queue alone, reset prose
  alone, episode totals, a leaderboard label, or sim/real correlation alone.
- Independently challenge any positive or mismatch decision before changing
  P2 manuscript status.

## Stop rule

Stop after the seven-system fixed source scope. A null is bounded to this
purposive frame and does not show field absence. Do not expand the roster to
obtain a second case, a positive contrast, or a paper.
