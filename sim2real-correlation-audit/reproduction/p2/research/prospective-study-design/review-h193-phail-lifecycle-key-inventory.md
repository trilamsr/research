# H193 lifecycle-key inventory independent challenge

Date: 2026-07-28

Status: pass; no critical or material issue at key-only scope.

## Independent method

A distinct Node-based key-only projection traversed all 1,188
content-addressed cached sidecars without importing the producer
implementation. It verified every object against the H187 source hash,
reconciled the exact 594 unique episode IDs, projected only fixed lifecycle
keys and identity/time controls, and retained no primitive value or prohibited
key.

## Reproduced result

The independent projection reproduced all three canonical rows, node-type
counts, and episode-set hashes:

- `meta.created_ts_ns`: numeric control in 594 episodes;
- `static.inference.policy.server.host`: string infrastructure candidate in
  594 episodes; and
- `static.inference.policy.server.device`: string infrastructure candidate in
  267 episodes.

All 1,188 expected cache hashes were unique, present, and content-verified;
there were no extra cached JSON objects. The producer's five tests and
exact-rebuild `--check` also passed.

## Scope and exposure disposition

The server-qualified paths are infrastructure-key leads only. Key names do not
establish a session, reset boundary, assignment block, availability regime,
dependence cluster, or uncertainty unit.

After H193 was fixed and completed, a separate search accidentally printed the
nonperformance candidate values `host=0.0.0.0` and `device=cuda`. This does not
invalidate the prior key-only protocol, computation, or result. It does make
any H194 value/semantics follow-up result-exposed; those values cannot be
promoted to session findings or described as prospectively unseen.
