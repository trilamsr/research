# H187 outcome-blind PhAIL context-support result

Date: 2026-07-27

Status: independently challenged bounded result; performance outcomes remain
sealed and the conditional outcome phase is not authorized.

## Result

The official PhAIL v1.0 594-rollout cohort is publicly enumerable at the
source-declared Nebius endpoint. Every episode has paired `meta.json` and
`static.json` sidecars. The retained manifest contains only episode identity,
model/variant, the four declared `BalancedSampler` context fields, creation
time, public source paths, and sidecar SHA-256 hashes. It contains no
performance field.

Across the complete release:

- policy exposure is ACT 151, GR00T 164, OpenPI 163, and SmolVLA 116;
- all 594 rows have task, object, tote-placement, and camera metadata;
- the four declared sampler fields form 19 observed full-window cells;
- 17 of those 19 cells contain all four policies;
- there are 126 observed
  `UTC date × task × object × tote × camera` cells;
- only 18 of those 126 cells contain all four policies;
- the 18-cell outcome-free common-support target retains 194 episodes
  (ACT 45, GR00T 62, OpenPI 39, SmolVLA 48) and excludes 400; and
- only 5 of 13 UTC dates contain all four policies even before conditioning
  on the other context fields.

The full-release common-support gate therefore fails. A much narrower
18-cell target can be identified and frozen with equal cell weights, but this
is a restricted target, not repair of the full release.

Chronology remains unresolved: 232 of 593 adjacent episodes repeat the same
policy, the longest same-policy run is 16, policy availability is batched
over calendar dates, and no source-recorded session identity is present.
Those diagnostics do not establish exchangeability or exclude carryover or
undocumented exclusions. Consequently `metadata_gate_pass` is false and no
performance field may be opened under H187.

## Candidate corrections and challenge

The first generated candidate incorrectly treated literal dotted JSON keys
such as `eval.object` as a nested `eval` object and fabricated missing
contexts. It was rejected before reliance. A corrected candidate then omitted
nonconstant `task` from support cells despite `task` being a declared sampler
grouping field and used overly broad gate language. Independent challenge
caught both defects. The final candidate:

- reads exact literal dotted keys;
- crosses all four declared sampler fields with UTC date;
- binds the sanitized CSV by SHA-256;
- recomputes every reported audit value from that CSV under `--check`;
- reports the restricted target rather than a general pass;
- keeps chronology explicitly unresolved; and
- leaves the outcome phase unauthorized.

Initial item count is separately recorded as H189 because the release places
it before policy assignment even though H187 prospectively prohibited
`eval.total_items`. H187 is not revised after seeing its result.

## Reproduction

From `research/prospective-study-design/`:

```text
python3 -m pytest -q test_audit_h187_phail_context_support.py
python3 audit_h187_phail_context_support.py --check
```

A fresh public-data rebuild uses:

```text
python3 audit_h187_phail_context_support.py --workers 24
```

The rebuild enumerates public inventory and downloads only 594 paired
`meta.json`/`static.json` sidecars. It does not download Parquet, video, or
telemetry. Canonical outputs are
`result-h187-phail-context-support.json` and
`result-h187-phail-context-support-sanitized.csv`.

## Scope

This is an exposure-support result for one fixture and one release. It does
not test which policy is best, establish randomized assignment, reconstruct
identical physical scenes, prove exchangeability, assess item-count support,
or make a population claim.
