# Protocol: H199 PhAIL randomized home target

Date fixed: 2026-07-28

Status at fixation: mixed-exposure, result-exposed current endpoint and
prospective baseline comparison. H198 exposed that pinned current Franka code
uses a nonzero `home_joints_variation`, draws a uniform perturbation inside
`Robot._reset`, and does not retain reset/carryover evidence on the exact
current PhAIL command path. The corresponding Positronic `v0.2.1` hardware
configuration and Franka driver files have not been opened for this question.

## Question and decision value

Does the source-bound PhAIL path at Positronic `v0.2.1`, as well as the pinned
current path, inherit a nonzero random Franka home-joint target on every arm
reset without persisting the realized target or random seed?

This is a concrete mechanism by which nominally “home” initial arm conditions
may vary across episodes. Randomization is not itself a flaw and may improve
coverage, but an unrecorded draw cannot be reproduced, conditioned on, or
checked as an exchangeability variable. A historical positive would sharpen
P2's lifecycle-evidence request for the released evaluation stack; a
current-only positive would remain an implementation recommendation.

## Fixed revisions and source boundary

Upstream: `https://github.com/Positronic-Robotics/positronic`

- `v0.2.1`: `e406176bc526babb06844a48e3627a5c0409eb74`;
- pinned current: `01b78e6f62ff5913490c360afdd2712eee070524`.

Compare exactly:

1. `positronic/inference.py`;
2. `positronic/cfg/embodiment.py`;
3. `positronic/cfg/hardware/roboarm/__init__.py`;
4. `positronic/drivers/roboarm/__init__.py`;
5. `positronic/drivers/roboarm/command.py`;
6. `positronic/drivers/roboarm/franka.py`;
7. `positronic/policy/harness.py`;
8. `positronic/dataset/ds_writer_agent.py`;
9. `positronic/dataset/serializers.py`;
10. `positronic/dataset/local_dataset.py`; and
11. `positronic/wire.py`.

If a path does not exist at one endpoint, record that absence. Follow a
directly imported definition only when required to resolve the exact
`phail` → DROID embodiment → Franka Reset → target draw → writer path; record
every expansion. Do not inspect Git history or add a path based on the result.

## Fixed source and quantitative units

At each endpoint, report:

1. whether `phail` binds the DROID embodiment;
2. whether DROID home binds arm `Reset()`;
3. the configured base home-joint vector;
4. the effective per-joint variation vector after configuration/default
   resolution;
5. the draw distribution and RNG interface;
6. whether arm target execution is blocking/synchronous;
7. whether the realized target is serialized in episode metadata/static data;
8. whether the seed or generator state is serialized;
9. whether the reset command itself is inside the retained episode window; and
10. whether the result is source-bound to the named PhAIL release rather than
    proven historical execution fidelity.

For a vector \(a\) of symmetric independent uniform half-widths, calculate
only:

- per-joint range in radians and degrees;
- maximum Euclidean joint-space perturbation
  \(\sqrt{\sum_j a_j^2}\); and
- root mean squared Euclidean perturbation
  \(\sqrt{\sum_j a_j^2/3}\).

These are configuration-space summaries, not end-effector displacement,
physical reset adequacy, or performance effects.

## Classification

Classify exactly one:

- `historical_and_current_unrecorded_randomized_home`;
- `current_only_unrecorded_randomized_home`;
- `randomized_home_draw_recorded`;
- `no_randomized_home_bound`;
- `trace_incomplete`.

The first two require an exact nonzero draw-to-arm-command path and absence of
realized-target/seed serialization within the fixed source boundary. A
source-bound `v0.2.1` result is not proof that every released episode executed
that code exactly.

## Verification, stop, and scope

Produce a deterministic result, exact source-hash binding, direct arithmetic
checks, and hostile tests for zero-vector substitution, default/config
misresolution, degrees/radians confusion, maximum/RMS confusion, command
versus recorded-evidence conflation, and historical-code versus historical-
execution overreach.

Do not inspect PhAIL sidecar values, outcomes, actions, telemetry, media,
recordings, scores, rewards, success, duration, or private services. If source
supports unrecorded randomized home, a separate protocol may inspect only
fixed release-sidecar key names for a corresponding field; H199 may not expand
into dataset content.

