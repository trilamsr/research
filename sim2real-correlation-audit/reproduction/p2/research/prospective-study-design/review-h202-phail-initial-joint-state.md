# Review: H202 PhAIL initial joint-state reconstruction

Date: 2026-07-28

## Disposition

**Pass as `complete_initial_joint_state_reconstruction`, with achieved-state
scope only.**

All 594 fixed H187 episodes have exactly one inventory-selected
`robot_state.q.parquet` and `robot_state.error.parquet` pair. Their first
samples are schema-valid and timestamp-aligned, and all 594 first error flags
are zero. The retained first joint observations therefore provide complete
achieved-state coverage for this public episode population.

Relative to the source-configured base home vector, the per-joint observed
standard deviations are 0.0170, 0.0294, 0.0475, 0.0460, 0.0586, 0.0574, and
0.0566 rad. These are 0.980--1.029 times the standard deviations implied by
the corresponding uniform target-draw intervals. Between 99.49% and 100% of
first observations fall inside the respective configured target supports.
The seven-joint deviation norm has median 0.1238 rad, RMS 0.1244 rad, 95th
percentile 0.1580 rad, and maximum 0.1875 rad.

## Independent challenge

A separate DuckDB implementation imports no producer module. After synthetic
first-row/sentinel, linear-quantile, and population-variance controls, it:

- reconstructs the exact selector from the fixed H187 cohort and safe H190
  inventory;
- verifies all 1,188 local source files against path, ETag, byte count, row
  count, and SHA-256 records;
- reads both first Parquet rows through DuckDB and exactly confirms every
  retained timestamp, error flag, and seven-vector; and
- recomputes the fixed summaries in DuckDB SQL.

The largest absolute difference between independently computed and producer
summary values is `4.440892098500626e-16`, below the fixed `1e-12` tolerance.
Producer result SHA-256 is
`4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043`;
challenge result SHA-256 is
`38fdc7d963fa19ba25c8142d4c984bbd00782609ca22c50482e6167fc4df3f19`.

## Consequence and scope

H202 partially repairs H199's public reproducibility gap: the achieved first
seven-joint arm state is reconstructable for every released episode and its
variation is quantitatively consistent in scale with the configured random
target support. It does not recover the commanded target or random draw, RNG
identity, reset acceptance criterion, scene or gripper state, operator
session, carryover, independence, exchangeability, or historical execution
fidelity. Small support exceedances also reinforce that the retained samples
must not be relabeled as the commanded draws.

Only the first `robot_state.q` and exact companion error sample were decoded.
No later state, action, command, camera, media, success, reward, score,
duration, termination, annotation, or other outcome field was opened,
retained, or summarized.
