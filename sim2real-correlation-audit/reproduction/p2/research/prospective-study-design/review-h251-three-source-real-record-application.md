# H251 three-source real-record review

Date: 2026-08-11

Status: producer checks and a method-distinct Ruby reconstruction pass. The
result is exploratory because several example AnkIle outcomes were visible
during source selection. It is suitable for a bounded manuscript application,
not a population or deployment claim.

## Result

The three records answer different questions.

- **AnkIle:** routing, marker, and square each contain 150 submitted rollouts:
  three fixed policy artifacts on the same 50 manifest indices. Every
  policy-state cell is present and each task's three-edge route graph is
  complete. The exact released-panel winners lead the second policy by 3, 1,
  and 3 successes, respectively. All 50 rounds are marked submitted and
  within-round policy order is declared randomized. The files do not include
  achieved reset acceptance or a complete retry/attempt ledger. These are
  exact finite-panel descriptions, not uncertainty-adjusted population
  winners.
- **RoboArena:** the pinned release contains 3,883 sessions and 21 policy
  labels. It realizes 104 of 210 possible label pairs. The full graph has two
  components because one label is never paired; the 20 pair-eligible labels
  form one connected component. Twenty-seven observed edges occur in only one
  session and the median edge has 4.5 sessions. The exhaustive public schema
  lacks an exact initial-state/reset join, assignment probabilities or pool
  epochs, robot instance, and retry/attempt lineage. Policy-graph connectivity
  therefore cannot be promoted to a common-context global ranking.
- **TRI:** Dryad version 4 contains 20 CSVs, 648 rows, and 73 hardware rows.
  It provides outcome arrays and aggregate margins but no bundle, rollout,
  initial-condition, realized-order, reset, session/robot, retry, or immutable
  policy-version key. Three cells contain one extra terminal apostrophe; after
  the declared narrow parse repair, every array length and success count
  reconciles, but two released success-rate cells disagree with their own
  arrays and counts. TRI is retained only as a structural protocol/release
  contrast; no performance comparison or route reconstruction is used.

## Challenge and disposition

`challenge_h251_three_source_records.rb` independently traverses the graphs,
counts AnkIle outcomes and matched half-credit edges, and parses TRI arrays by
regular-expression/token arithmetic rather than the producer's Python/AST
path. All 22 comparisons pass. The challenge covers aggregate arithmetic and
topology only; it cannot validate the external data-generation process.

The evidence supports three concise manuscript claims:

1. a public real-robot release can identify an exact common-state finite-panel
   winner when every policy is run on every declared state;
2. even broad or connected policy-pair support does not identify a
   common-context target when the context law and lifecycle bridge are absent;
   and
3. a strong source-described matched-bundle protocol is not reconstructable
   when the public release drops its trial-level join.

Do not claim that the AnkIle winners generalize, that RoboArena's leaderboard
is wrong, or that TRI's experiment was not randomized. Missing fields concern
the fixed public releases, not private records or execution truth.

## AnkIle retention sensitivity and source-owner update

The released winners lead the runner-up by only 3, 1, and 3 successes. A
post-release worst-case sensitivity replaces a retained matched round by an
arbitrary three-policy binary outcome vector while keeping the declared
50-state panel fixed. The minimum number of round replacements needed to
reverse the released winner is two for routing, one for marker, and two for
square. Exact subset enumeration confirms each minimum. This is a fragility
calculation, not evidence that a replacement occurred or used outcome
information.

The released configuration enables incomplete-round reruns for routing and
marker and disables them for square. On 2026-08-12, the user supplied an email
reply signed by source owner Lars stating that all records were retained and
that the full data and provenance were planned for release in approximately
two weeks. The message establishes expected future availability, not the
number, reasons, or effects of any reruns. The scientific follow-up is to
compare the published retained panel with first-valid and all-valid-attempt
analyses once the records are released. The all-valid analysis must average
within policy-state cell before restoring equal weights across the 50 states,
so cells with more retries do not receive more influence.

## Reproduction

From the project root, with the pinned RoboArena metadata tree available:

```bash
.venv/bin/python -m pytest -q \
  research/prospective-study-design/test_analyze_h251_three_source_records.py
.venv/bin/python \
  research/prospective-study-design/analyze_h251_three_source_records.py \
  --roboarena-root <pinned-snapshot-root> --check
ruby research/prospective-study-design/challenge_h251_three_source_records.rb \
  --roboarena-root <pinned-snapshot-root> --check
```

Canonical outputs:

- `result-h251-three-source-real-record-application.json`
- `result-h251-three-source-real-record-challenge.json`
