# H196 expansion-history exposure

Date: 2026-07-28

## What happened

H196 prospectively fixed 17 H195 path owners and allowed a directly imported
or invoked definition to be opened at the comparison endpoint when necessary
to resolve the semantic trace. The current endpoint required two such files:

- `positronic/policy/recording.py`, imported by
  `positronic/policy/remote.py`; and
- `positronic/offboard/server.py`, imported by every current fixed backend
  server file after `positronic/offboard/vendor_server.py` was deleted.

After opening those authorized endpoint files, targeted `git log -S` calls
were used to identify when `recording.rrd` and `uuid.uuid4().hex` entered the
repository. Those calls exposed commits
`91287959a41ee7ebb4b12212dd4dbe99c36efb99` and
`e370cbf1e6e31360fd17cc6d36a9ce74786abd94` before the two expansion paths
were formally added to H196's history enumeration.

No PhAIL dataset object, performance value, server recording, private service,
video, action, telemetry, note, or outcome was accessed.

## Why it matters

The initial protocol was sufficient for the endpoint comparison because it
prospectively authorized direct-definition expansion. It was not sufficient
for an exhaustive statement about the timing of changes in newly introduced
replacement files. Treating the two targeted commit discoveries as
prospective would overstate the history design.

## Disposition

- Preserve the endpoint comparison as prospective under the original direct
  expansion rule.
- Treat the timing and intervening-history claims involving the two expansion
  paths as result-exposed and exploratory.
- Amend the deterministic history enumeration to include exactly those two
  files and no new vocabulary.
- Preserve the initially exposed commit identities in the protocol and result.
- Do not use the exposure to add repositories, private storage, dataset
  fields, or performance content.

This is a scope-accounting correction, not a scientific outcome exclusion.

