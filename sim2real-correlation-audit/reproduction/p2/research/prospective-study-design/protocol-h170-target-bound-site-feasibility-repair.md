# Protocol: H170 target-bound site-feasibility repair

Date fixed: 2026-07-27

Status: fixed after H169 independently reproduced three H164 v1
`not_applicable` authorization bypasses and before implementing the repair.

## Failure being repaired

H164 v1 retains only a `study_spec_hash`. It neither retains the target
specification nor a target-owned authorization roster. Its verifier therefore
accepts arbitrary reason text as sufficient authorization for
`not_applicable`.

H169 showed that this can promote the policy-observation interface, context
generation/assignment order, or reset/washout/carryover unit to
`not_applicable` while still returning
`eligible_for_outcome_hidden_rehearsal`.

H164 v1 and H169 remain unchanged as the reproducible failure record. H170 is
a new reliance candidate.

## Fixed target specification

Use `input-h170-target-spec.json` as the exact target specification. It must:

1. identify `p2-pair-session-context-v1`, target version 1;
2. retain the native policy observation/action interfaces, native scene,
   context-before-pair law, and five-second capture/start limit;
3. enumerate all 16 H164 dossier units as required; and
4. contain an empty `not_applicable_authorizations` list.

The empty list is intentional: every unit is required for this target. H170
does not infer generic authorization rules for hypothetical future targets.
A future target that legitimately permits an exception requires a new
versioned target specification and validation challenge.

## Dossier v2

Every dossier must add:

- the complete `target_spec`;
- `study_spec_hash`, recomputed from the complete target specification; and
- `not_applicable_authorizations`, an exact copy of the target-owned
  authorization list.

The verifier must require exact equality to the canonical target
specification before inspecting unit status. It must reject:

- a missing, altered, stale, or merely rehashed target specification;
- any authorization not present in the canonical target;
- any `not_applicable` unit not exactly authorized by that target;
- duplicate, malformed, or stale authorization entries; and
- any authorization for a unit that the canonical target marks required.

For the current target, any `not_applicable` status must fail closed.

## Preserved H164 gates

H170 must preserve:

1. all four known-answer decisions;
2. all 64 dossier-unit rows and 64 content-verified artifacts;
3. all 14 H164 hostile-control rejections;
4. strict error-below-tolerance arithmetic;
5. target-change precedence for policy-visible/dynamics-changing
   instrumentation and excessive start delay; and
6. the outcome-hidden-only, no-real-site, no-field-collection boundary.

## Fixed H170 attacks

In addition to the 14 inherited attacks, reject:

1. arbitrary `not_applicable` on `policy_observation_interface`;
2. arbitrary `not_applicable` on
   `context_generation_and_assignment_order`;
3. arbitrary `not_applicable` on
   `reset_washout_and_carryover_control`;
4. a forged authorization absent from the canonical target;
5. a modified target specification with the old hash;
6. a modified target specification with a recomputed hash;
7. a replaced `study_spec_hash`;
8. a missing complete target specification; and
9. a malformed authorization container.

## Advancement

Advance to a fresh distinct-method challenge only if all preserved decisions
and controls pass, all nine new attacks fail closed, and the canonical result
regenerates byte-for-byte.

Even after a pass, H170 validates only synthetic interface logic. It does not
qualify a real site, establish physical truth or tolerance adequacy, resolve
safety/privacy/access, analyze outcomes, or authorize field collection.
