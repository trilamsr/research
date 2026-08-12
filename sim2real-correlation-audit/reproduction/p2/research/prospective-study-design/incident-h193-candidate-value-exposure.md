# H193 candidate-value exposure incident

Date: 2026-07-28

Status: diagnosed; H193 key-only result preserved, any H194 value analysis
must be result-exposed.

## What happened

After the H193 key-only result identified
`static.inference.policy.server.host` and
`static.inference.policy.server.device`, a search intended to locate their
semantics in source code also traversed the gitignored H193 sidecar cache. The
matching JSON lines printed the candidate configuration values
`host = 0.0.0.0` and `device = cuda` for multiple cached objects.

The search pattern was limited to the two candidate key names and related
server/source terms. It did not match, print, or inspect a success, outcome,
item-count, duration, safety, HRT, rank, note, video, telemetry, or other
performance field or value.

## Consequence

- H193's canonical producer and result remain key-only: they retain no
  primitive values and their exact candidate paths and episode counts were
  generated before this exposure.
- The candidate values are not experimental outcomes, but their exposure
  invalidates any claim that a later host/device value audit was fixed before
  seeing those values.
- Any follow-up must therefore be labeled result-exposed and must preserve a
  null or constant-value result. It may exhaustively summarize the two already
  selected fields under a fixed method but may not select a new field,
  threshold, grouping, or interpretation in response.
- PhAIL performance outcomes remain sealed.

## Cause and mitigation

The content-addressed cache correctly solved endpoint interruption and
integrity problems, but the subsequent source search did not exclude the
scratch cache path. Future source-semantics searches must target the pinned
source tree or explicit documentation paths and must not recursively include
`work/h193-sidecars/`.

No retry or deletion can restore the unexposed state. The scientific repair is
transparent result-exposed labeling, exhaustive fixed-field reporting, and
independent challenge of the H193 key result and any later value summary.
