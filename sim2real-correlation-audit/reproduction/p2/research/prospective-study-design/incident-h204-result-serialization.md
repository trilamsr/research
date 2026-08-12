# Incident: H204 result serialization boundary

Date: 2026-07-28

## What happened

The first material H204 execution completed its fixed model and permutation
computations, passed the result validator, and then failed before writing or
printing the candidate because NumPy integer rank fields were not
JSON-serializable.

No H204 classification, variance share, p-value, group mean, or diagnostic
was displayed or retained. The failure occurred only at the final
`json.dumps` boundary.

## Cause and repair

`numpy.linalg.matrix_rank` returns NumPy integer scalars. The result builder
placed those scalars directly into the rank fields, while the standard JSON
encoder accepts native Python integers only.

The repair explicitly converts nuisance rank, full rank, and factor degrees
of freedom to native `int` values. It does not change the fixed inputs,
transform, model, permutation stream, thresholds, classification, or scope.

## Retry rule

Rerun the unchanged material computation only after:

1. compilation succeeds;
2. a synthetic JSON serialization check covers the normalized rank fields;
   and
3. the staged controls still pass.

Retain the rerun result whether positive, null, or mixed.
