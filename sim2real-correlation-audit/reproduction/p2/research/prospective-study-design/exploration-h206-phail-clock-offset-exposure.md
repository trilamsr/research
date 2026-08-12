# H206 exposure record: PhAIL monotonic/wall-clock bridge

Date: 2026-07-28

Status: result-exposed exploratory branch. This is not a preregistration or
confirmatory analysis.

## Origin and exposure

H202 retained the first `robot_state.q` timestamp for every episode but used
it only for signal alignment. While selecting the next high-information
public-data question after H205, the author inspected those already retained
timestamps together with H187 `created_ts_ns` and the pinned `v0.2.1` source.

Before this record was written:

- source inspection revealed that `pimm.world.SystemClock.now_ns()` returns
  `time.monotonic_ns()`, while episode `created_ts_ns` defaults to
  `time.time_ns()`;
- the 594 first-state timestamps were found to be unique, to span about
  15.29 days of monotonic time, and to contain two decreases in episode-ID
  order; and
- the raw difference `created_ts_ns - first_timestamp_ns` was found to span
  approximately 18 days.

No clustering threshold, boot-group count, within-group chronology statistic,
policy comparison, performance value, later state, or additional trajectory
signal was examined before this record.

After this record and before the H206 analysis protocol was fixed, a complete
sorted-gap orientation pass found one offset gap of about 1,556,980 seconds,
while the second-largest gap was about 0.509 seconds. Thresholds from one
second through six hours therefore all produced two groups of 250 and 344
episodes. No group membership, relation to policy/date, within-group ordering,
elapsed-time agreement, or source-independent reconstruction was examined
before fixing the protocol.

## Scientific question

Can the paired wall-clock episode-creation timestamp and monotonic first-state
timestamp recover a bounded, source-qualified machine-boot chronology for
the complete public release?

For episode \(i\), the raw offset

\[
o_i = \mathrm{created\_ts\_ns}_i-\mathrm{first\_timestamp\_ns}_i
\]

equals the wall-clock epoch corresponding to monotonic zero minus the
unobserved delay from episode creation to the first retained state sample.
Near-equal offsets can therefore be consistent with a common machine boot,
but they are not by themselves operator sessions, physical reset groups, or
dependence clusters.

## Exploratory safeguards

- Use only the fixed H187 sanitized cohort, H202 first-state projection, and
  pinned `v0.2.1` source.
- Preserve the complete offset and sorted-gap surface rather than selecting
  one favorable grouping.
- Treat threshold-dependent groupings as sensitivity analyses.
- Open no later state, action, command, camera, media, performance, or outcome
  value.
- Do not infer host identity, operator session, reset/carryover absence,
  exchangeability, or valid outcome uncertainty units.
- Record any manuscript use as result-exposed descriptive evidence and obtain
  an independent source/method challenge first.
