# Review: H203 PhAIL achieved-first-state temporal structure

Date: 2026-07-28

## Disposition

**Pass as `no_detectable_temporal_structure_at_fixed_resolution`.**

The fixed global chronology statistic is 14.506 versus a permutation median
of 14.085, a ratio of 1.030 and two-sided p-value 0.0531. Within exact policy,
the ratio is 1.001 and p-value 0.965. Within UTC date, the ratio is 1.028 and
p-value 0.0701. None passes the fixed 0.01 threshold, and the primary global
ratio is far inside the material-effect boundaries of 0.90 and 1.10. The
seven primary adjacent-pair correlations range from -0.073 to -0.006, and
there are no exact duplicate first-state vectors.

The mild global and within-date tendency is toward greater successive
difference, not persistence. It remains visible as a continuous result, but
was not promoted by relaxing the fixed significance or effect thresholds.

## Independent challenge

A separate Node implementation imports no producer module. It independently
joins the two fixed CSVs, applies the source-configured transform, constructs
the complete squared-distance matrix, and runs 49,999 SplitMix64/Fisher-Yates
permutations under the same global, policy, and date scopes but a different
RNG stream. It exactly reproduces all three observed statistics and reaches
the same bounded-null classification. Its corresponding two-sided p-values
are 0.0528, 0.952, and 0.0731. Four scope/classification attacks are rejected.

Producer result SHA-256 is
`5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda`;
challenge result SHA-256 is
`c6db21d4657fd7ad30aac910976cd6cd2e27d5d1afe7b8853d25a13d813aae76`.

## Consequence and scope

P2 must not claim that the released first arm states demonstrate temporal
clustering, carryover, or nonexchangeability. The null is bounded to one
successive-distance statistic, 594 observations, release-record timestamps,
and three fixed permutation scopes. It does not authenticate physical order,
identify operator sessions, validate RNG independence, exclude subtler
dependence, establish valid outcome uncertainty units, or authorize opening
performance.

No new public object was opened. Only H202's first joint observations and the
fixed H187 policy/time fields were used; later state and every performance
field remained sealed.
