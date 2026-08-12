# Protocol: H202 PhAIL initial joint-state reconstruction

Date fixed: 2026-07-28

Status: prospective, outcome-free physical-state protocol fixed after H201 and
before inspecting any public trajectory value or schema. A source-driven
amendment was made before trajectory exposure: the v0.2.1 serializer drops
`RESETTING` but retains `ERROR` states in an exact companion
`robot_state.error` signal, so the error flag is required below.

## Question and decision value

Can the first retained Franka joint-state sample be reconstructed for the
exact 594 public PhAIL v1.0 episodes, and if so, how much does that achieved
initial joint state vary around the configured home vector?

H199 shows that the reset target is randomized but not serialized. H201 shows
that `static.joint_signal` is only the signal-name descriptor
`robot_state.q`. A complete first-state projection could partly repair the
reproducibility gap by recording achieved initial arm configuration, even
though it would not recover the target draw, RNG identity, scene state,
gripper state, acceptance decision, or operator session.

## Fixed population and source identity

- Exact H187 sanitized 594-episode cohort:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- Complete H190 safe inventory:
  `projection-h190-phail-path-tree.json`, SHA-256
  `6350af0ce19ce1cea88c8f3c2613873c3e3624e47e0cfde5c02fbaa1506d98e1`.
- H199 result SHA-256
  `2571b41e1796e5eb85ac96ac820c73aa0192c1703ffb9bb6abd85f454f0c41a8`.
- H201 result SHA-256
  `fc76cdb9c2443b81953fd6c6a998b60ddfabaf615f210f3ba8366186c6a2fdc6`.
- Public endpoint:
  `https://storage.eu-north1.nebius.cloud/positronic-public`.

Select exactly one inventory object per episode for each of the
source-defined Parquet basenames `robot_state.q.parquet` and
`robot_state.error.parquet`, only within that episode's fixed H187 rollout
directory. Reject duplicates, missing paths, paths outside the cohort
directory, and inventory or source drift. Do not add aliases after observing
coverage.

## Fixed source and recording semantics

Using only the already pinned Positronic `v0.2.1` writer, Franka-state
serializer, Harness, and local-dataset definitions, establish before
scientific interpretation:

1. the Parquet columns representing the seven joint positions and scalar
   error flag;
2. the timestamp column and units;
3. whether resetting/error states are retained or filtered;
4. the relation between episode START and the first retained joint sample; and
5. whether the first sample is an achieved observation rather than the
   commanded random target.

If these cannot be resolved inside that fixed source boundary, stop at
`semantic_trace_incomplete`.

## Fixed extraction

For every selected file:

1. download and record source path, advertised size/ETag when present, byte
   count, and SHA-256;
2. parse the schemas and require a finite numeric seven-vector, a scalar error
   flag in `{0, 1}`, and one timestamp for the first logical sample of each;
3. require the first `q` and error timestamps to be identical;
4. retain only episode ID, first timestamp, seven first-sample joint values,
   first error flag, both source paths, and both source hashes;
5. record row counts only as integrity fields; do not retain or summarize
   later values; and
6. reject rather than impute malformed, missing, duplicated, timestamp-
   misaligned, or nonfinite samples.

The downloaded signal file may physically contain the full joint-state trace.
Only the first logical sample and row count are authorized for decoding or
retention. Use a disposable content-addressed cache and do not place raw
Parquet in the reproduction package.

## Fixed estimands

Let the configured base vector be

```text
[0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
```

and H199's target-draw half-widths be

```text
[0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
```

Define a valid achieved-state sample as a schema-valid, timestamp-aligned pair
whose first error flag is zero. Report:

1. file-pair, schema-valid, timestamp-aligned, first-error, and valid-achieved-
   state coverage;
2. per-joint minimum, 5th percentile, median, mean, standard deviation, 95th
   percentile, and maximum of first-state deviation from the base vector;
3. per-joint fraction inside the configured target-draw support
   `[-a_j, +a_j]`, as description only;
4. minimum, median, mean, RMS, 95th percentile, and maximum Euclidean norm of
   the seven-joint deviation; and
5. observed per-joint standard deviation divided by the theoretical uniform
   target-draw standard deviation `a_j / sqrt(3)`, as a descriptive
   comparison only.

Use deterministic linear-interpolated empirical quantiles. Use population
standard deviations and RMS denominators over valid achieved-state episodes
only. Do not add
policy, date, task, context, chronology, adjacency, cluster, or outcome
comparisons after seeing the joint states.

## Classification and stop rules

Classify exactly one:

- `complete_initial_joint_state_reconstruction`:
  all 594 episodes have exactly one hash-bound file pair and one valid
  achieved-state first sample;
- `partial_initial_joint_state_reconstruction`:
  at least 90% but fewer than 594 episodes have a valid first sample;
- `insufficient_initial_joint_state_coverage`:
  fewer than 90% have a valid first sample;
- `semantic_trace_incomplete`; or
- `input_drift_or_integrity_failure`.

Preserve partial and null results. Do not relax the path, schema, vector,
coverage, or quantile rules after exposure.

## Staged validation and challenge

Before the material run:

1. verify the inventory selector on synthetic duplicate, missing, out-of-root,
   and wrong-signal cases;
2. verify paired first-row extraction on synthetic Parquet files with known
   values, later-row sentinel values, NaN/Inf, wrong dimensions, reordered
   columns, timestamp mismatch, error flags, and empty files;
3. verify arithmetic against hand-computed known answers;
4. run an outcome-independent transport/integrity rehearsal on the
   lexicographically smallest and largest H187 episode IDs (both `q` and
   error files) without printing joint values; and
5. require completeness/integrity checks before producing the canonical
   projection.

Before P2 reliance, independently reconstruct the selector, first-row
projection, and fixed summaries with a distinct implementation or method.

## Scope

The first retained nonerror joint state is not the commanded target, random draw,
scene state, gripper state, reset acceptance, proof that home was reached,
operator compliance, carryover absence, session identity, independence,
exchangeability, or a performance outcome. No action, command, camera, media,
success, reward, score, rank, duration, termination, annotation, or other
trajectory field may be opened. The exact `robot_state.error` companion is
authorized only to distinguish a retained driver error state from a nonerror
joint observation.
