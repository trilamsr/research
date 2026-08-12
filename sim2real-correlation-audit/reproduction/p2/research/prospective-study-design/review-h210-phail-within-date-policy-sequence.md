# Review: H210 PhAIL within-date policy sequence

Date: 2026-07-28

Status: independently challenged result-exposed exploratory result; suitable
for bounded manuscript reliance.

## Candidate and producer result

The candidate is
`result-h210-phail-within-date-policy-sequence.json`, SHA-256
`71bf7b49976b936c147cd021776dc3c5a32a401dff5824506a28b1ae5b77d112`.
H209's regime-level adjacency result was known, but the H210 protocol was
fixed before any policy adjacency was computed within UTC date.

The producer opens only the fixed H187 policy/date projection and H206
clock-regime projection. It does not open state vectors, raw Parquet, actions,
commands, media, later state, performance, or outcomes.

When policy multisets are preserved independently within all 13 dates, pooled
same-policy adjacency is 0.39243 versus a permutation median of 0.38038 and
an exact conditional-exchangeability expectation of 0.37984. The excess is
0.01205 with two-sided p=0.52872. For regime-1 dates, the corresponding excess
is 0.03704 (0.48560 versus 0.44856; p=0.23688); for regime-2 dates it is
-0.00296 (0.32544 versus 0.32840; p=0.90884). Neither the primary nor either
fixed secondary gate passes. The fixed classification is
`no_detectable_within_date_policy_sequence_structure_at_fixed_resolution`.

The producer passes 10 tests and exact deterministic rebuild.

## Independent method

`challenge_h210_phail_within_date_policy_sequence.mjs` independently parses
and joins the H187/H206 projections, reconstructs all 13 date groups, orders
labels by monotonic time, recomputes observed adjacencies and analytic
expectations, and uses a distinct SplitMix64/Fisher--Yates stream for 49,999
date-restricted multiset permutations. It does not import or execute the
Python producer.

The retained challenge is
`result-h210-phail-within-date-policy-sequence-independent-challenge.json`,
SHA-256
`021e6c84ddc53eb358d6d3ce51008fd61e4632a47d952e6136461733d3efc074`.
It agrees exactly on group sizes, observed statistics, analytic expectations,
permutation medians and quantiles, and classification. Its independent
two-sided p-values are 0.52280, 0.22740, and 0.89972. Six mutations to observed
values, expectations, null summaries, classification, group size, and scope
fail closed.

## Disposition and boundary

The independent evidence supports:

> H209's regime-1 policy-label adjacency signal does not persist after
> conditioning on UTC date at the fixed resolution. The residual within-date
> excess is small and non-significant under the fixed permutation reference.

The result narrows the scheduling concern to coarse calendar composition or
date boundaries at the resolution tested. It does not prove that date
composition caused H209, identify an assignment law, scheduler, physical
session, machine, reset, or dependence unit, validate exchangeability, or
authorize outcome access. No unresolved material concern remains for this
narrow classification.
