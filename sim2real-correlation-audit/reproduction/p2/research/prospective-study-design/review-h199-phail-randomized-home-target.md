# Review: H199 PhAIL randomized home target

Date: 2026-07-28

## Disposition

**Pass with scope as
`historical_and_current_unrecorded_randomized_home`.**

At both Positronic `v0.2.1`
(`e406176bc526babb06844a48e3627a5c0409eb74`) and pinned current
(`01b78e6f62ff5913490c360afdd2712eee070524`), the exact public `phail`
path binds the real DROID Franka reset and inherits the driver's nonzero
default `home_joints_variation`. Each reset draws an independent uniform
per-joint perturbation with half-widths
`[0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]` radians and adds it to the
configured base home target before a synchronous arm command.

The configuration-space support has maximum Euclidean joint perturbation
`0.2149418526020468` radians and RMS Euclidean perturbation
`0.12409673645990857` radians. These are joint-space summaries only.

Within the fixed source boundaries, neither endpoint serializes the realized
home target, perturbation, seed, or RNG state. The reset command is ordered
outside the retained episode. This supports a concrete instrumentation
request: retain the realized target and RNG identity as lifecycle context.

## Independent challenge

A separate Node implementation imports no producer module. It reconstructs
both command paths from Git objects, independently parses the default vector,
searches the complete fixed serialization boundary, recomputes the arithmetic,
and agrees on the classification. It rejects ten attacks, including:

- treating a driver default as sufficient without the PhAIL binding;
- conflating synchronous motion with persistent evidence;
- conflating the configured base pose with the realized draw;
- equating maximum and RMS joint norms;
- treating a joint norm as end-effector displacement;
- treating tagged source as historical execution fidelity; and
- inferring reset inadequacy, nonexchangeability, or a performance effect.

Producer result SHA-256 is
`2571b41e1796e5eb85ac96ac820c73aa0192c1703ffb9bb6abd85f454f0c41a8`;
challenge result SHA-256 is
`63909a9357cc49afa8d8f16b1373f05c4b5daad01e91007cf57f99a4490c3a7e`.

## Scope

The result is source-bound. It does not prove that the release executed this
code exactly, that the physical arm reached its target, that the randomization
was harmful, that scene state was reset, that episodes are dependent or
nonexchangeable, or that performance changed.

No dataset value, trajectory, action, observation, recording, media,
telemetry, performance field, outcome, or private service was opened.

