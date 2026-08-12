# H168 independent public pair-routing applicability challenge

Date: 2026-07-27

Disposition: `pass_with_scope`

## Independence

The challenge uses a standalone Node.js implementation and reads the eight
outcome-free canonical inputs named by the H167 protocol. It does not import
the H167 Python producer or tests. It independently reconstructs the 15-unit
status vector and 11-unit failed conjunction before comparing with H167.

## Result

The challenge agrees with
`not_qualified_for_public_pair_routing_application`.

- The public program exposes a global ranking, not H165's within-presented-pair
  routing action.
- The paper-described random pair sampling does not establish the current
  deployed assignment law or weights.
- Paper-described within-comparison matching does not identify a stable future
  pair-specific context distribution.
- Complete cumulative support does not establish complete newest-increment
  support: the fixed records retain 21 versus 15 edges.
- The exposed roster/topology shift requires segmentation or an explicit
  bridge.
- Aggregate session counts are not a retained session-level assignment export.

## Semantic attacks

All seven attacks were rejected: promoting the paper protocol to current
deployment, relabeling the leaderboard as routing, promoting matched
conditions to a stable future context law, treating dataset cards as
assignment weights, promoting cumulative support to current support, pooling
across epochs without a bridge, and treating aggregate session counts as a
cluster-valid assignment export.

## Scope

This independently supports H167's current-public applicability decision only.
It does not invalidate RoboArena, establish assignment intent or outcome
dependence, analyze outcomes, authorize field activity, or show that a
prospective routing action is impossible.

## Trace

- H167 protocol SHA-256:
  `b891a7a88ae7c3b096df74f5b56d1cb826edf937951eedc245f258594c3e92c2`
- H167 result SHA-256:
  `09934aae0641d156ef7ab68d10c82319e2d6a52e42c149847db48f27ea8e4090`
- independent source SHA-256:
  `88b2cc3e4f3eb9a76c7004ffef210ff1173db94a8304934fb35cfc030de5b0a3`
- validator SHA-256:
  `e204c8f0abe6393460f7cb289e57db54158b71717f2eab428d76551c77b530aa`
- independent result SHA-256:
  `75df6d5ead9ed05402f6109c654bead06faacfd66e34084c4d06c0b3670d6aa5`

## Consequence

Close the current-public pair-routing application route negatively. P2 still
has two honest ways forward: obtain a prospectively declared within-pair
action with a fixed assignment/context law, or qualify a target-preserving
site for the common-context top-1 branch. H165 remains useful theory and
design guidance, not the current empirical application.
