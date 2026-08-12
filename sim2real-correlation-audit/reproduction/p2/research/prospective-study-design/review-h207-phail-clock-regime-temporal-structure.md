# Review: H207 PhAIL clock-regime temporal structure

Date: 2026-07-28

Status: independently challenged exploratory result; suitable for bounded
manuscript reliance within the limitations below.

## Candidate and scope

The challenged candidate is
`result-h207-phail-clock-regime-temporal-structure.json`, SHA-256
`31ef2b4162157769bf9f99ce47f50865076b99e114c7a67592319ce8df2b2252`.
Its protocol was fixed after H203 and H206 were known but before any achieved
first-state distance was computed within an H206 clock regime. The result is
therefore explicitly result-exposed exploratory, not confirmatory.

The producer uses only the hash-bound H202 first-state projection and H206
clock-regime projection/result/challenge. It opens no raw Parquet, later
state, action, command, media, success, reward, duration, termination,
performance, or other outcome field.

## Producer controls and result

Before material execution, the producer passed:

- exact input hashes and a 594-row one-to-one join;
- unique source-primary monotonic timestamps;
- exact regime sizes 250 and 344 and pair accounting 249 + 343 = 592;
- known transform and distance arithmetic;
- constant, alternating, drift, and IID synthetic controls;
- restricted-membership and deterministic-permutation controls; and
- a complete 999-repetition synthetic rehearsal at the production group
  sizes.

The fixed 49,999-permutation result is
`no_detectable_clock_regime_temporal_structure_at_fixed_resolution`.
The pooled observed/median ratio is 1.03060 with two-sided p=0.04984.
Regime 1 is 1.02690 with p=0.26804; regime 2 is 1.03346 with p=0.10196.
The pooled statistic misses the fixed p<=0.01 gate and remains well inside
the 0.90--1.10 material-effect interval. Neither fixed regime-specific test
approaches its Bonferroni p<=0.005 gate.

The result reproduces exactly under the producer, and 13 producer tests pass.

## Independent method

`challenge_h207_phail_clock_regime_temporal_structure.mjs` is a separate
Node.js implementation that does not import or execute the Python producer.
It:

- parses the two input projections independently and checks their hashes;
- reconstructs the complete join and monotonic ordering;
- recomputes all three observed statistics with separate loops;
- uses an independent SplitMix64/Fisher--Yates stream for 49,999
  within-regime restricted permutations; and
- applies the protocol classification independently.

The retained challenge is
`result-h207-phail-clock-regime-temporal-structure-independent-challenge.json`,
SHA-256
`39839285b7a84acf2fb3a5b74afe18a3fb32d51e2491358d6b42ad24b80032e2`.
Observed statistics agree within `7.1e-14`. The independent pooled p-value is
0.04736; regime-specific values are 0.25820 and 0.10256. Median differences
are at most 0.00442, and the independent classification is identical. The
validator rejects six mutations to the observed statistic, null summaries,
classification, group size, and scope.

## Challenge execution incident

The first challenge attempt self-rejected without writing an output because
its tiny known-answer control used the production pair-count denominators.
The material challenge loop had executed in memory, but no statistic was
displayed, retained, or used to change the protocol, producer, thresholds, or
claim. The repair made the statistic derive denominators from the supplied
groups and moved all challenge controls before the material loop. The repaired
path passed its controls before execution and now rebuilds byte-for-byte.
This was an independent-control implementation defect, not a scientific null
or a reason to exclude a result.

## Disposition

The independent evidence supports this bounded statement:

> H203's no-material-temporal-structure result survives the fixed H206
> clock-regime refinement: pooled and both regime-specific successive-distance
> tests miss their prespecified material gates.

It does not support independence, valid RNG operation, authenticated physical
execution order, carryover absence, machine or operator-session identity,
exchangeability clusters, valid uncertainty units, policy comparison, or a
performance claim. The pooled nominal p-value near 0.05 is retained but is
not evidence at the fixed 0.01 gate and accompanies only a 3.1% ratio
departure. No unresolved material concern remains for this narrow
exploratory reliance.

## Reproduction portability incident — 2026-08-05

The P2 manuscript gate later stopped because the producer's nominal exact
comparison included `platform.platform()`. The retained run recorded macOS
26.5.2 while the current machine reported macOS 26.6. A field-by-field rebuild
found this OS build label to be the only difference; every input binding,
observed statistic, permutation summary, p-value, classification, scope flag,
Python version, NumPy version, seed, and repetition count was exact.

The verifier now excludes only `run_identity.platform` from rebuild equality,
while validating both records and comparing every other field exactly. A
focused test confirms that an OS-label change passes and a numerical-result
change fails. The retained result and its independently challenged SHA-256 are
unchanged. This is a portability repair to a non-scientific environment label,
not a refreshed analysis or scientific-result change.
