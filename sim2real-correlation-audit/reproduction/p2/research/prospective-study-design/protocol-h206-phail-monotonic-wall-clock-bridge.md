# Protocol: H206 PhAIL monotonic/wall-clock bridge

Date fixed: 2026-07-28

Status: result-exposed exploratory analysis protocol. The H202 timestamp
range and complete offset-gap surface described in
`exploration-h206-phail-clock-offset-exposure.md` were known before this
protocol. Group membership, policy/date composition, within-group ordering,
and elapsed-time agreement were not. This is not a preregistration or a
confirmatory analysis.

## Question and decision value

Can the paired public episode-creation wall clock and first-state monotonic
clock recover a bounded machine-clock chronology for the complete 594-episode
PhAIL release?

A stable source-qualified clock regime could partially repair chronology
evidence without opening outcomes. It would not itself identify a host,
operator session, reset/carryover unit, exchangeability cluster, or valid
uncertainty unit.

## Fixed inputs and source boundary

- H187 sanitized cohort, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- H202 first-state projection, SHA-256
  `44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370`.
- H202 result, SHA-256
  `4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043`.
- Positronic tag `v0.2.1`, commit
  `e406176bc526babb06844a48e3627a5c0409eb74`, with exact SHA-256
  projections:
  - `pimm/world.py`:
    `cca1fbe28cd69adef15dac7c7c8a7b30386bcf9cf06d8c943b8c2d1736c5560f`;
  - `positronic/inference.py`:
    `f0d9565b501b70ea15421d86b0e742a8c57d5c22446f57f36f9bd7cf79d43080`;
  - `positronic/dataset/ds_writer_agent.py`:
    `40435c6a11cb8f75bb1dc79933da1ea8b47586cffa2988c3bf44756fb1fbe483`;
  - `positronic/dataset/local_dataset.py`:
    `e0308688d7daa43c4c27b00a5f199ed8ffc86caaf3b6b1b2cf9177adec82e493`;
  - `positronic/wire.py`:
    `586baf9bd736a623fc4b19027ea05158757f4e7e474a9f73081090a992329763`.

Require an exact one-to-one episode join, 594 unique IDs, finite positive
integer timestamps, and no missing policy or UTC-date field. Open no new
public object and no later state, action, command, camera, media, performance,
or outcome field.

## Fixed semantic trace

Require the pinned source to establish the complete chain:

1. real-hardware inference creates `pimm.World()` without a custom clock;
2. `World` defaults to `SystemClock`;
3. `SystemClock.now_ns()` returns `time.monotonic_ns()`;
4. real-hardware inference wires the dataset agent with `TimeMode.CLOCK`;
5. `DsWriterAgent` uses `clock.now_ns()` as the primary timestamp in that
   mode; and
6. `created_ts_ns` defaults to `time.time_ns()`.

If any link fails, stop at `clock_semantic_trace_incomplete`.

## Fixed descriptive analysis

For every episode \(i\), calculate

\[
o_i = c_i-m_i,
\]

where \(c_i\) is `created_ts_ns` and \(m_i\) is H202's first-state
`timestamp_ns`.

Report:

1. the complete count, uniqueness, minimum, maximum, and span of \(m_i\) and
   \(o_i\);
2. all sorted adjacent offset gaps through a canonical SHA-256 projection,
   plus the largest and second-largest gaps and their ratio;
3. numbers and sorted group sizes when a new group begins after an offset gap
   exceeding exactly 1 ms, 10 ms, 100 ms, 1 s, 10 s, 60 s, 600 s, 3,600 s,
   21,600 s, or 86,400 s;
4. a descriptive one-hour partition, selected after the gap surface was
   exposed, with group size, offset range/span, first/last wall timestamp,
   first/last monotonic timestamp, UTC-date counts, and policy counts;
5. within each one-hour group, Kendall's tau-a between wall-clock and
   monotonic order, the exact discordant-pair count, and the maximum absolute
   difference between elapsed wall time and elapsed monotonic time relative
   to the group's first wall-clock episode; and
6. whether each one-hour group is contiguous in wall-clock order and in
   episode-ID order.

Ties are ordered by episode ID for display only. Compute all integer
differences exactly before conversion to seconds. Do not select or discard a
group, policy, date, episode, or threshold after further exposure.

## Exploratory classification

Classify exactly one:

- `scale_separated_clock_offset_regimes` if the largest sorted offset gap is
  at least one day, is at least 1,000 times the second-largest gap, and the
  1-second through 6-hour partitions have identical memberships;
- `clock_offset_structure_without_scale_separation`;
- `no_clock_offset_structure_at_fixed_resolution`;
- `clock_semantic_trace_incomplete`; or
- `input_drift_or_integrity_failure`.

This outcome-responsive classification is an organizational description, not
a confirmatory test.

## Staged validation and challenge

Before material execution, verify source hashes, exact integer offset and gap
arithmetic, threshold boundary behavior, stable sorting, Kendall discordance,
elapsed-time discrepancy, and membership-contiguity logic on synthetic
known-answer examples. Before manuscript reliance, independently reconstruct
the source chain, exact offsets, one-hour memberships, and classification with
a distinct implementation.

## Scope

`time.time_ns() - time.monotonic_ns()` is compatible with a host's
wall-clock epoch at monotonic zero, shifted by the unobserved delay between
episode creation and the first retained state sample and potentially affected
by wall-clock adjustment. A regime is therefore a clock-offset regime, not
proof of a particular machine, reboot, operator session, physical reset,
carryover unit, or dependence cluster. Monotonic order is source-qualified
only within a regime whose clock origin is stable; it does not authenticate
all physical events or authorize performance inference.
