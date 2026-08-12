# H187 source discovery and candidate disposition

Date: 2026-07-27

Status: provisional external-source finding retained because it changes P2's
next empirical target. No episode-level performance outcome was analyzed.

## Search boundary

An exploratory public-source search sought a second physical robot-policy
evaluation whose global ranking or selection action could be compared with
P2's action-order results. Eligibility required at least two policies, a
global comparative action, an assignment mechanism that could affect context
exposure, primary public documentation, and affirmative evidence sufficient
to classify action order. Missing documentation was not coded as safe order.

The strongest viable candidate is PhAIL v1.0. No second affirmative
H151-style mismatch was found. That null is retained rather than converted
into a broader narrative.

## Retained primary-source facts

The PhAIL v1.0 release page reports four evaluated VLA models, 594 evaluation
runs, public data and framework artifacts, and a blinded protocol. It states
that the operator first creates the tote, camera, item-count, and object
context; the system then selects a checkpoint with `BalancedSampler`; model
identity remains hidden from the operator.

At Positronic framework tag `v0.2.1`:

- `BalancedSampler.sample(keys, context)` groups counts by declared context
  fields and weights selection toward underrepresented policy keys; and
- `phail_multiple` supplies `task`, `eval.object`,
  `eval.tote_placement`, and `eval.external_camera` as grouping fields.

The arXiv v1 abstract identifies Human-Relative Throughput as a global scalar
with bootstrap intervals and separates it from pairwise KS testing. These
facts make PhAIL a positive context-first contrast with a real global action,
not a pair-first mismatch.

## Material source-identity correction

H132--H140 queried Amazon's public S3 endpoint and received `NoSuchBucket`.
The current source-declared analysis configuration instead uses the Nebius
endpoint `https://storage.eu-north1.nebius.cloud` with public profile access.
On 2026-07-27, unauthenticated path-style listing at that endpoint returned
HTTP 200 for both the named `phail/v1.0/dataset/` prefix and the older
`datasets/phail/v1.0/` prefix.

This directly falsifies treating the prior response as evidence that the
bucket itself was missing. The old raw trace remains valid evidence about the
Amazon endpoint, not about source-declared public availability.

A complete provisional `ListObjectsV2` enumeration at the Nebius endpoint
then found:

| public prefix | objects | bytes | episode `static.json` rows | cohort rows |
|---|---:|---:|---:|---|
| `phail/v1.0/dataset/` | 14,361 | 40,659,686,177 | 1,083 | 594 rollout, 449 teleoperation, 40 human |
| `datasets/phail/v1.0/` | 13,381 | 36,991,284,792 | 1,013 | 524 inference, 449 training, 40 human |

The sorted `(key, size, ETag, LastModified)` inventory hashes were,
respectively,
`8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982`
and
`58143d0cae031251b54978037f9435419d73d017ae176b184b730f5f07c18ae4`.
These are source-inventory fingerprints, not content hashes for multipart
objects.

An independent Node standard-library implementation subsequently reproduced
both complete inventories without opening any dataset object. It found the
524 episode IDs to be an exact subset of the 594 IDs; the old-only IDs are
524--593, with 14 objects per additional episode. Official release tooling
names the 524 export `phail_inference_prod`, and the data-audit documentation
describes it as production-variant filtered. This resolves the cohort
relationship without establishing byte identity.

Both prefixes contain the same 449 training/teleoperation episode identities.
Official repository history records commit
`afe06f2ceb0dbc1dd4160bdb5df7fb5a14430ed4`, which changed the paper's count
from 352 to 449 on 2026-05-12. The current paper and export source use 449,
while the live release page and Croissant metadata still state 352. No
separate 352-episode selection manifest was found. The defensible source
disposition is stale metadata, not a separately identified public cohort.

H187 fixes the official release-page 594-rollout cohort as its primary
outcome-free support target. The nested 524 production-filtered cohort is a
named sensitivity, not a merged sample. The official artifact list's
`v0.2.1` versus mutable `latest` image mismatch and the absence of a published
dataset content manifest remain release-dependency limitations.

## Disposition

Open H187 as the highest-information public empirical move:

1. construct an outcome-stripped episode manifest for the fixed 594 cohort;
2. audit common-context support and chronological balance;
3. freeze target cells and weights; and only then
4. consider a separately governed outcome analysis.

The endpoint and inventory portions of Phase 0 now pass independent
challenge. Listing fingerprints use explicit algorithms: the producer's
sorted `(key, size, ETag, LastModified)` SHA-256 is
`8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982`.
ETags remain inventory identifiers, not assumed content hashes.

TRI LBM 1.0 remains a strong source-described positive control without a
located structured public rollout table. STEP and RoboChallenge/Table30 V2
remain unresolved because the reviewed primary records do not establish the
needed candidate-to-context bridge. These are not negative findings.

## Source trace

- PhAIL v1.0 release and protocol:
  `https://phail.ai/releases/v1.0`
- PhAIL arXiv v1:
  `https://arxiv.org/abs/2605.29710v1`
- Positronic tag object:
  `e406176bc526babb06844a48e3627a5c0409eb74`
- Pinned sampler:
  `https://github.com/Positronic-Robotics/positronic/blob/v0.2.1/positronic/policy/sampler.py`
- Pinned configuration:
  `https://github.com/Positronic-Robotics/positronic/blob/v0.2.1/positronic/cfg/policy.py`
- Analysis discovery snapshot:
  `18ce72d5703dcbbbb10a980336aa5a1622601fb4`
- Retrieval date: 2026-07-27
