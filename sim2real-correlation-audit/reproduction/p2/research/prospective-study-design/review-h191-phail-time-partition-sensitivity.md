# H191 PhAIL time-partition sensitivity independent challenge

Date: 2026-07-28

Status: pass after material verification-path correction. No performance field
was opened.

## Independent result

A separate implementation using integer timestamps reproduced:

- the exact H187 sanitized-input and H191 protocol hashes;
- 594 rows, the exact allowed header, and 594 empty session identities;
- zero disagreements between recorded UTC date and the creation timestamp;
- all 684 unique width/phase combinations and every canonical grid row;
- all eight width-level range summaries;
- the 19-cell, 17-supported-cell full-window result; and
- H187's 126-cell, 18-supported-cell, 194-episode UTC result.

The exact sensitivity ranges are:

| width | supported cells | retained episodes |
|---:|---:|---:|
| 12 h | 15--19 | 154--194 |
| 24 h | 15--19 | 154--194 |
| 48 h | 17--21 | 179--219 |
| 72 h | 15--21 | 169--226 |
| 96 h | 17--24 | 189--282 |
| 120 h | 18--22 | 205--287 |
| 144 h | 19--22 | 222--314 |
| 168 h | 18--23 | 226--328 |

At H187's fixed 24-hour UTC phase, 11 of 18 supported cells have minimum
per-policy count one and the other seven have minimum two. The subset is
therefore a thin positivity result, not evidence of adequate precision.

## Resolved material issue

The first verifier checked only the stored grid length and a few known
answers. It accepted a 684-row grid made of duplicates and an empty range
summary. The computation was correct, but stored-result verification was
fail-open.

The corrected verifier rebuilds the complete result from the hash-bound input
and requires exact equality with the stored JSON. Regression tests reject both
the duplicate-grid/missing-range attack and a one-cell mutation. Seven tests
and the canonical verification target pass.

## Scope

The result demonstrates dependence on deterministic calendar-bin width and
phase. It does not identify a session, select a scientifically preferred
partition, establish exchangeability or reset quality, define an actionable
performance target, or authorize outcomes.
