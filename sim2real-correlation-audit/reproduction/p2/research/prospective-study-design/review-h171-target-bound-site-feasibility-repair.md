# H171 independent target-bound site-feasibility repair challenge

Date: 2026-07-27

Disposition: `pass_with_scope`

## Independence

The challenge is a standalone Node.js implementation. It does not import the
H164 or H170 Python producers or tests. It independently:

- canonicalizes and hashes the complete H170 target specification;
- verifies exact target identity in every dossier;
- reconstructs all four dossier decisions;
- decodes and hashes all 64 retained artifacts; and
- attacks the authorization layer directly.

## Result

The independent path reproduces:

- `target_preserving_complete`:
  `eligible_for_outcome_hidden_rehearsal`;
- `visible_fiducial_complete`: `target_altering_only`;
- `grid_scale_as_tolerance`: `not_evidenced`; and
- `unlinked_human_overlay`: `not_evidenced`.

It rejects all nine H170 authorization attacks, including the three H169
`not_applicable` bypasses, a forged authorization, changed target
specifications with old and recomputed hashes, a replaced target hash, a
missing target specification, and a malformed authorization container.

## Disposition

H170 passes the reliance gate for synthetic target-binding and decision logic.
It supersedes H164 v1 for any later reliance on the interface. H164 and H169
remain the permanent failure record.

The pass does not make a self-reported dossier true. Artifact hashes establish
internal content identity, not physical provenance or authenticity. A real
site still needs externally checkable sensor, calibration, tolerance,
workflow, safety/privacy/access, and lifecycle evidence.

## Scope

No real site is qualified and no field collection is authorized. The result
does not establish physical truth, tolerance adequacy, safety, outcome
validity, causal identification, or transport.

## Trace

- H170 protocol SHA-256:
  `ca8f25ee47a8ebd33b2604bdd9841d170ccbda6552d1e833238959a0e27ff65a`
- target specification file SHA-256:
  `4597cb6960fdc0b658cabdce7b33b1812dc4ea79da841ea584bbd41c3ada226a`
- H170 producer SHA-256:
  `bfa9c7e1ecb206c90df8033dfeb9d6296d1c049234253966c9df960de4870aad`
- H170 result SHA-256:
  `68d72630633ed682a9d91e934c97ebaa59643c7cb821dd6231b1d2bedb99b688`
- independent source SHA-256:
  `6386a0a7529ce9a68ee70ce008cb8fcebd38cda79522e26997e5fd1ae2b53700`
- validator SHA-256:
  `776bd8af6e7e97663746dc28634525455e8b9c6c784c9f67b5c38cef57c8e078`
- independent result SHA-256:
  `cef3b17be1956488b6bbaaa7388bc6aea4f8f2f0ee593e090fc11e078a3f371e`

## Consequence

Use H170--H171, not H164 v1, to prepare a public-data-only site evidence
request packet. The next gate should test whether a candidate site can supply
externally checkable evidence for every required unit without outcomes or
target-altering instrumentation. It must not infer feasibility from
self-attestation alone.
