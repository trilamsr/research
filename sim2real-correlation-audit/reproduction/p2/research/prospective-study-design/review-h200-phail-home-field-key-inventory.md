# Review: H200 PhAIL home-field key inventory

Date: 2026-07-28

## Disposition

**Pass as `candidate_home_field_key_found`, with semantics unresolved at this
stage.**

The fixed key-only vocabulary was applied to all 1,188 H187-hash-bound public
PhAIL v1.0 sidecars. Three keys occur in all 594 episodes:

- `static.joint_names`, array;
- `static.joint_signal`, string; and
- `static.pose_signals`, array.

The producer retained only episode identity, key path, category, and node
type. It did not retain or open primitive values. H193's already-fixed
`reset` and `seed` controls remain null and were not retroactively amended.

## Independent challenge

A separate Node traversal imports no producer module, revalidates all 1,188
sidecar hashes, independently tokenizes and excludes prohibited action,
observation, media, telemetry, and performance paths, and reproduces the
three candidate rows and episode-set hashes exactly. Eight attacks reject
key-name-to-value, all-episode-to-variation, source/history, and private-data
overreach.

Producer result SHA-256 is
`85e6f82975a6c9e3a6802cfd68d0dcdff954c90e262949c47f1ea7c31dee1010`;
challenge result SHA-256 is
`d9abcad04b5829bcc0961ada055a2e7436dabd5044ecac842365f77808ad3990`.

## Scope

This result establishes names and node types only. It does not establish that
any candidate is the configured or realized home target, RNG evidence,
per-reset information, or a dependence variable. H201 resolves the source
semantics before any candidate value is opened.

No primitive sidecar value, trajectory, action, observation, recording,
media, telemetry, performance field, outcome, or private service was opened.

