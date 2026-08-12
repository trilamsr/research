# Review: H206 PhAIL monotonic/wall-clock bridge

Date: 2026-07-28

## Disposition

**Retain as result-exposed exploratory
`scale_separated_clock_offset_regimes`.**

Pinned `v0.2.1` source establishes the full chain: real inference uses
`TimeMode.CLOCK`; its default `SystemClock` returns `time.monotonic_ns()` for
the retained primary signal timestamp; episode creation uses `time.time_ns()`.
The difference between the two clocks therefore carries a source-qualified
clock-origin signal, shifted by the unobserved creation-to-first-sample delay
and potentially by wall-clock adjustment.

Across all 594 episodes, one adjacent offset gap is
1,556,979.985 seconds and the next largest is 0.509 seconds, a ratio of
3.06 million. Every threshold from one second through one day produces the
same two groups of 250 and 344 episodes. The groups are contiguous in
wall-clock order and span 5--20 March and 24 March--4 April 2026,
respectively.

Within both groups, wall-clock and first-state monotonic order have zero
discordant pairs (Kendall tau-a 1.0). Offset spans are 72.2 ms and 936.8 ms,
and maximum elapsed wall-versus-monotonic discrepancies from each group's
first episode are 41.6 ms and 904.1 ms. This source-qualifies a stable
within-regime chronology at the observed resolution.

## Independent challenge

A separate Node implementation uses BigInt arithmetic, an independent CSV
parser, direct source hashing, independent grouping/inversion logic, and
byte-exact reconstruction of all 594 projection rows. It exactly reproduces
the two memberships, policy/date composition, gap statistics, zero
discordances, and classification. Six source/result/scope attacks are
rejected.

Producer result SHA-256 is
`1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19`;
projection SHA-256 is
`7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529`;
challenge SHA-256 is
`6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268`.

## Consequence and scope

P2 may replace the broad statement that public chronology is wholly
unauthenticated with a narrower one: the release contains a source-qualified
within-regime ordering signal and two sharply separated clock-offset regimes.

The analysis was selected after H202 timestamp exposure and after the complete
offset-gap surface was inspected. It is explicitly exploratory and does not
identify a host, reboot, operator session, physical reset, carryover unit,
exchangeability cluster, or valid outcome uncertainty unit. Two regimes are
also insufficient for ordinary cluster-level inference. No later state,
performance, or outcome field was opened.
