# Protocol: H167 public pair-routing applicability

Date fixed: 2026-07-27

Status: fixed after H165--H166 established the pair-conditioned target
semantics and before constructing the applicability matrix below.

## Question

Do the already audited outcome-free public RoboArena records establish the
action, assignment, context-mechanism, support, and lifecycle conditions
needed to apply H165's same-mechanism pair-routing target?

This is an applicability audit, not a new outcome analysis. It must not open
or use judgment, reward, success, or preference values.

## Fixed evidence

Hash-bind and read only these existing canonical records:

1. `source-h122-roboarena-paper-protocol.json`;
2. `result-h106-roboarena-ranking-algorithm-and-exclusion.json`;
3. `result-h114-roboarena-authored-text-assignment-context.json`;
4. `result-h116-roboarena-dataset-card-assignment-recall.json`;
5. `result-h122-release-sequence-independent-challenge.json`;
6. `result-roboarena-assignment-regimes.json`;
7. `result-h165-pair-conditioned-operational-target.json`; and
8. `result-h166-pair-conditioned-operational-target-independent-challenge.json`.

Do not inspect session rows, identifiers, outcomes, or additional source
files. Reuse the status and scope already recorded by the owning audits.

## Fixed 15-unit matrix

### Operational action

1. the public program declares within-presented-pair policy routing as a
   downstream action;
2. the public program instead declares a global policy leaderboard/ranking;
3. the H165 routing action and the public downstream action are aligned.

### Pair assignment

4. the paper describes random pair sampling before evaluator task/scene
   construction;
5. the currently deployed pair-assignment law is identified;
6. fixed, outcome-independent pair weights \(\pi\) are available;
7. the active policy pool and its effective intervals are available; and
8. a session-level assignment export is available.

### Context mechanism

9. matched conditions within each realized A/B comparison are
   paper-described;
10. a stable future pair-specific context law \(G_{ab}\) is identified; and
11. a bridge from the observed historical contexts to that future mechanism
    is identified.

### Support and lifecycle

12. the cumulative February public panel has all 21 fixed-policy edges;
13. the newest nonoverlapping increment has all 21 fixed-policy edges;
14. the roster/assignment epoch is stable enough to pool without a bridge;
    and
15. outcome-free session/lifecycle structure is available for future
    cluster-valid analysis.

Allowed statuses are `available`, `paper_described_only`, `partial`,
`absent`, and `contradicted_by_public_record`.

## Fixed decision rule

Return `qualified_for_public_pair_routing_application` only if:

- units 1, 3, 5--8, 10--11, and 13--15 are `available`; and
- no required unit is `contradicted_by_public_record`.

Otherwise return `not_qualified_for_public_pair_routing_application` and name
every failed conjunction member. Unit 2 is diagnostic: if available while
unit 1 is absent, report `public_action_mismatch`.

Do not infer that the benchmark is invalid, that pair-conditioned edges are
useless, that assignment was outcome-dependent, or that a prospective routing
target could not be adopted. The result addresses only current public
qualification for the declared H165 action.

## Required checks

1. Verify the exact upstream hashes and schemas.
2. Verify every source-side no-outcome flag that is present.
3. Emit all 15 units in fixed order with source trace.
4. Verify the paper-described/current-deployment distinction.
5. Verify the cumulative/newest-increment support distinction.
6. Reject promotion from a leaderboard target to within-pair routing.
7. Reject pooling over the exposed roster/assignment shift without a bridge.
8. Reproduce the result byte-for-byte.

## Advancement

Advance if the matrix makes the applicability decision and its exact blockers
auditable without reading outcomes. A negative result should redirect the
program toward either a prospectively declared routing action and assignment
law or the separately qualified common-context top-1 branch.
