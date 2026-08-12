# Protocol: H191 PhAIL time-partition sensitivity

Date fixed: 2026-07-28

Status: post-challenge outcome-free robustness protocol. The grid was fixed
after an independent reviewer reported selected UTC-offset and bin-width
examples, so this is not represented as prospectively unseen.

## Question

How dependent is H187's 18-cell, 194-episode positivity subset on the arbitrary
UTC-calendar-date boundary?

## Fixed input and sealing

Use only H187's outcome-stripped 594-row artifact with SHA-256
`ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
Its allowed fields contain identity, policy/checkpoint, recorded context,
creation timestamp, empty session identity, and source hashes. No success,
duration, termination, safety, note, event, media, telemetry, or other
performance field may enter the analysis.

## Fixed diagnostic grid

For widths \(w\in\{12,24,48,72,96,120,144,168\}\) hours, enumerate every
integer-hour phase \(0,\ldots,w-1\) relative to the Unix epoch. For each
width-phase combination:

1. bin each creation timestamp using
   \(\lfloor(t+\mathrm{phase})/w\rfloor\);
2. cross the bin with exact task, object, tote placement, and external camera;
3. retain every cell with positive exposure for all four fixed policies; and
4. report total cells, supported cells, retained episodes, excluded episodes,
   policy counts, and the distribution of the minimum per-policy count.

Also reproduce the no-time full-window support summary and H187's exact
24-hour, phase-zero UTC result.

## Interpretation and stop rules

This is a deterministic sensitivity surface, not a search for a favorable
partition. Report the complete grid and width-level ranges. Do not select an
offset or width as a session surrogate, redefine H187's fixed result, propose
a performance estimand, or open outcomes. Variation demonstrates partition
dependence; invariance would demonstrate only robustness to this grid, not
session identity, reset, independence, or exchangeability.
