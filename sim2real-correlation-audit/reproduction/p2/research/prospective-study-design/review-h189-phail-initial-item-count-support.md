# H189 PhAIL initial-item-count support independent challenge

Date: 2026-07-28

Status: pass after material integrity correction; no remaining critical or
material issue. Performance outcomes remained sealed.

## Result

The official release order is explicit: the evaluator loads \(N\) items, the
system then selects a checkpoint, and successful-item count is recorded after
execution. The release separately describes the initial count as recorded
episode metadata rather than a derived result.

Across the fixed 594-rollout cohort:

- 80 episodes begin with 4 items and 514 with 8;
- by policy, 4/8 counts are ACT 34/117, GR00T 18/146, OpenPI 9/154, and
  SmolVLA 19/97;
- crossing item count into the full-window sampler context produces 27 cells,
  21 with all four policies;
- crossing item count into the fixed dated context produces 126 cells, 18
  with all four policies; and
- item count is deterministic within every H187 dated context cell.

H189 therefore retains exactly H187's same 18 cells, 194 episodes, equal
cell weights, and policy counts 45/62/39/48. This is a null change to the
restricted target, not evidence that the full release passes. Full-release
support still fails, chronology remains unresolved, and performance access
remains unauthorized.

## Independent checks

A separate Node implementation reproduced:

- 15 inventory pages, 14,361 unique objects, 40,659,686,177 bytes, and exact
  inventory SHA-256
  `8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982`;
- 594 unique paired rollout sidecars;
- zero missing or extra episode IDs;
- zero differences when every H189 row is projected onto H187's 14 fields,
  including both sidecar content hashes; and
- every reported item-count, cell, target, and policy total.

Exact-header inspection found no performance-field leakage. Thirteen focused
tests and result recomputation pass.

## Resolved material issue

The first challenged build checked the stored H187 inventory fingerprint but
did not compare it with the fresh public enumeration or require the rebuilt
H187-field projection to match H187 exactly. That latent drift path violated
the protocol stop rule even though the current source had not drifted.

The corrected candidate:

- recomputes and enforces exact fresh inventory-hash equality;
- requires exact ordered equality of all 594 projected H187 rows;
- adds known-answer and mismatch failure tests; and
- supports a recovery path that revalidates live inventory before rebuilding
  from the already content-hash-bound H189 CSV.

Independent re-review passes the correction.

## Scope

H189 establishes only that recorded initial item count does not further split
H187's dated target. It does not establish randomized assignment,
exchangeability, session independence, identical physical scenes, or a
performance result.
