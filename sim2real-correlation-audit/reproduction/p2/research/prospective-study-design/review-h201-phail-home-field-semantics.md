# Review: H201 PhAIL home-field semantics

Date: 2026-07-28

## Disposition

**Pass with scope as `generic_signal_schema_not_home_draw`.**

The complete exact-string census at Positronic `v0.2.1`
(`e406176bc526babb06844a48e3627a5c0409eb74`) yields 40
`joint_names`, 14 `joint_signal`, and 8 `pose_signals` source hits across ten
paths. The exact production trace resolves all three H200 candidates:

- `joint_names` is an array of revolute joint-name strings derived from the
  robot URDF and emitted as static robot-model metadata;
- `joint_signal` is the fixed signal-name string `robot_state.q`; and
- `pose_signals` is a fixed list of pose-signal names used as 3-D
  visualization roles.

The real-hardware inference path merges those constants and robot metadata
into the episode START payload, and the writer persists them to
`static.json`. The random reset target is computed in a separate `_reset`
path and is not added to robot metadata. None of the three candidates
source-defines the configured base home vector, realized perturbation/target,
seed, or RNG state.

## Independent challenge

A separate Node implementation imports no producer module. It repeats the
full-tree exact-string census, independently traces the producer-to-static
sink, confirms the 62-hit/ten-path inventory and all three semantic units, and
rejects nine attacks. In particular, joint names are not joint positions,
signal-name strings are not signal samples, visualization roles are not reset
evidence, and a random target elsewhere in the same driver is not serialized
metadata.

Producer result SHA-256 is
`fc76cdb9c2443b81953fd6c6a998b60ddfabaf615f210f3ba8366186c6a2fdc6`;
challenge result SHA-256 is
`a4837ba45e0fa229ae19147ab44d8c97d4b0e5db7b5ed667dcaee98939695433`.

## Consequence and scope

The public sidecar candidate lead closes without opening values. P2 may state
that the fixed public fields are schema descriptors and do not publicly
record the source-bound randomized home draw. H199's instrumentation request
therefore remains: serialize the realized target and RNG identity if the draw
is to be reproduced, conditioned on, or audited.

This does not establish historical execution fidelity, physical reset
success, harmful randomization, independence, exchangeability, or a
performance effect. No sidecar value, trajectory, action, observation,
recording, media, telemetry, performance field, outcome, or private service
was opened.

