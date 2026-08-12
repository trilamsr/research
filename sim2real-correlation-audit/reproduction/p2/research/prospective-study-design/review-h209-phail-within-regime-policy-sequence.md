# Review: H209 PhAIL within-regime policy sequence

Date: 2026-07-28

Status: independently challenged result-exposed exploratory result; suitable
for bounded manuscript reliance.

## Candidate and producer result

The candidate is
`result-h209-phail-within-regime-policy-sequence.json`, SHA-256
`2879b1c4b0ade1e4d1fd47e5a0db5312fce2d401c5f1580f7e2af2c211da7794`.
The H206--H208 regime, date, and policy counts were known, but the protocol
was fixed before policy labels were ordered by monotonic timestamp or any
adjacency statistic was computed.

The producer opens only the fixed H187 policy/date projection and H206
clock-regime projection. It does not open state vectors, raw Parquet, actions,
commands, media, later state, performance, or outcomes.

The pooled same-policy adjacency fraction is 0.39189 versus a permutation
median 0.30574 and exact conditional-exchangeability expectation 0.30623.
Its two-sided p-value is 0.00004, but the 0.08615 absolute excess misses the
fixed 0.10 pooled material-effect gate.

Regime 1 has adjacency 0.48594 versus median 0.32129, an excess of 0.16466
with p=0.00004. Regime 2 has adjacency 0.32362 versus median 0.29446, an
excess of 0.02915 with p=0.23864. The fixed classification is therefore
`regime_specific_or_small_policy_sequence_structure`, not a material pooled
claim.

The producer passes 12 tests and exact deterministic rebuild.

## Independent method

`challenge_h209_phail_within_regime_policy_sequence.mjs` independently parses
and joins the H187/H206 projections, orders all labels, recomputes observed
adjacencies and analytic expectations, and uses a distinct SplitMix64/
Fisher--Yates stream for 49,999 within-regime multiset permutations. It does
not import or execute the Python producer.

The retained challenge is
`result-h209-phail-within-regime-policy-sequence-independent-challenge.json`,
SHA-256
`e6700b2ce631a7ca6e16669dad30cf00a4d922ff8444f3a2601a154e23ed767f`.
It agrees exactly on all observed statistics, analytic expectations,
permutation medians and quantiles, and classification. Its regime-2 p-value
is 0.23568 under the independent stream; the two structure signals remain at
the minimum Monte Carlo p=0.00004. Six mutations to observed values,
expectations, null summaries, classification, group size, and scope fail
closed.

The challenger's first attempt self-rejected before its material loop because
the tiny known-answer control used production pair denominators. The repair
derives denominators from each supplied group. Controls already preceded the
material loop; no failed-run scientific output was written or used to change
the protocol, producer, thresholds, or claim.

## Disposition and boundary

The independent evidence supports:

> Policy labels show regime-specific same-policy adjacency structure within
> H206's recovered chronology. The pooled excess is statistically extreme
> under the fixed permutation reference but falls below the fixed 10-point
> material-effect gate; regime 1 supplies the fixed secondary signal.

This result strengthens the request for explicit native assignment and block
metadata before later policy comparison. It does not establish that labels
were randomly assigned under the permutation reference, identify a scheduler
or physical session, prove outcome dependence, authorize outcome access, or
support a policy-performance effect. Regime 2 is a bounded null for this
statistic only. No unresolved material concern remains for the narrow
classification.
