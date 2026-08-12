# H169 independent H164 `not_applicable` authorization challenge

Date: 2026-07-27

Disposition: `fail_repair_required`

## Failure

H164 permits a unit to use `not_applicable` only when the locked target
definition makes that unit logically unnecessary and supplies the reason. The
v1 dossier contains only `study_spec_hash`; it contains neither the target
specification nor a target-bound authorization list. The verifier checks that
some reason text is present but cannot verify that the target authorized the
exception.

A standalone Node.js reconstruction identified three fail-open dossiers.
Starting from the positive known answer, it changed one unit at a time to
`not_applicable` and supplied the arbitrary reason “claimed unnecessary
without target-bound authorization.” The current H164 implementation returned
`eligible_for_outcome_hidden_rehearsal` for:

1. `policy_observation_interface`;
2. `context_generation_and_assignment_order`; and
3. `reset_washout_and_carryover_control`.

The Python replay against the actual H164 classifier reproduces all three
decisions. Five independent control attacks—visible instrumentation,
dynamics-altering instrumentation, late preparation, an outcome field, and
measurement error equal to tolerance—remain rejected. The failure is local to
authorization of `not_applicable`, not evidence that every H164 control is
broken.

## Consequence

H164 v1 must not qualify any real-site rehearsal. Its synthetic known-answer
classification remains useful as development evidence, but its reliance gate
failed. The repair must bind a canonical target specification and an explicit
target-owned authorization map, verify the map against the target hash, and
fail closed for any absent, invented, stale, or forbidden authorization.

The repair should preserve the original four decisions and 14 attacks, add
authorization attacks, and receive a fresh independent challenge. H169 must
remain reproducible against the unchanged H164 v1 implementation rather than
being erased by an in-place fix.

## Scope

This is a synthetic interface failure. It does not show that a real site
misreported evidence, invalidate the public reset systems, analyze outcomes,
or authorize field activity.

## Trace

- H164 protocol SHA-256:
  `3a2f623b24219c23f4f4eec8547028325a5feab5e7385ac5088295ba1bb6e784`
- H164 v1 source SHA-256:
  `e66053790ffbefcdea1a267afbe2e5c9f488d39352840f926d3071b65f82c73b`
- H164 v1 result SHA-256:
  `f1be2b4b993f622fc2ae6292fbec5ca7b884db9b003ecb15266b881e8497d401`
- independent challenge source SHA-256:
  `1541de71bac2b97de30bf7112f6ebfdb14dd5c8bb96a95985400a4126aac3e26`
- producer replay validator SHA-256:
  `6bf33091fdf380f46584c6680bbe21edab0a73b2dbb603dc334c8c98af727d67`
- challenge result SHA-256:
  `056d7f38bab52299cd2974511381e02a7448d2b3fc4f30d5a8479af3afd2aa7b`
