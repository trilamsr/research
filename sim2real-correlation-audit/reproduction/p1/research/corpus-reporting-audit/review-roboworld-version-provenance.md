# Independent RoboWorld version and extraction review

Date: 2026-07-26

Status: provenance discrepancy resolved; fixed-panel numeric use approved.

## Trigger and independence

The retained `sources/source-roboworld.csv` header described an extraction from
arXiv v3, while the corpus protocol pins arXiv v4. A separate read-only source
provenance challenger investigated this discrepancy before the new
evaluator-substitution analysis could rely on the file. The challenger did not
edit the source record, extraction script, or this disposition.

## Version comparison

Explicit official arXiv v3 and v4 source archives were retrieved and extracted.
The 33 scientific source files are content-identical across versions.

- sorted content-manifest SHA-256:
  `f7fb9ef7093e6cc4045ed238e90aaac369635a91858c0c84ca02d9600d2e1a73`
- score-panel figure SHA-256:
  `3eae4367ac355e3d845cbc3d434cc0f4de6702570b0184a85b639f30f8dc92c8`
- success-rate-panel figure SHA-256:
  `0017d1ad19713e78ddfdb4aa498be77e86bf1e2386e2240cb4310f386439e9d1`

The raw archives and compiled PDFs have different hashes because of archive
metadata and the arXiv version/date stamp, not different scientific source
content. The repository's pinned v4 paper matches a fresh official v4
download:
`be2a6af575b63df53ff3a248414868c7db69c599af5beb167162aaace2e14c79`.

The original 2026-07-20 downloaded archive was not retained, and its URL was
unversioned. Its exact container version is therefore unreconstructible. This
does not alter the values because the explicit v3/v4 scientific files and both
load-bearing figures are identical.

## Independent v4 vector check

An independent direct vector re-extraction of all 32 v4 points found:

- maximum real-axis difference from retained values:
  `0.0070847` RoboArena leaderboard units (`0.00086%` of the axis range);
- maximum rubric-score-axis difference: `6.42e-8`;
- maximum success-rate-axis difference: `9.96e-5` percentage points; and
- maximum Pearson difference: `1.69e-6`.

Every pairwise order and exact tie was preserved. Every real and evaluator
winner set remained `Pi0.5`.

These residuals are compatible with the retained rounding and do not require a
numeric-row change.

## Rollout-count correction

The live v4 introduction and main figure state **4,186** rollouts. The number
4,188 appears only in commented-out draft source. The retained source header
incorrectly cited 4,188 as the paper's live value. It must be corrected to
4,186.

The scientific consequence is unchanged: 4,186 is not evenly divisible across
eight policies, and the paper does not identify a per-point trial count.

## Independent pixel-check repair

The committed `reextract_roboworld_pixels.py` failed under the repository
environment despite the README's reproduction claim. Two deterministic causes
were identified:

1. the left-panel frame selected the first and last detected spine inside a
   wide crop, inadvertently including the right panel's left spine; and
2. the grid mask excluded light-gray gridlines rendered at exactly RGB 235 by
   the current PyMuPDF build.

Using the first two detected spines and accepting `<=235` repaired the path.
A separately implemented pixel check reproduced panel 9a with:

- \(|\Delta r|=0.00010\);
- maximum x error `0.575` RoboArena units (`0.07%` of range); and
- maximum y error `0.0014` rubric-score units (`0.18%` of range).

The canonical script and README were updated. A separate post-fix execution
then reran the repaired canonical script on the pinned v4 score figure and recovered
all eight markers, the same \(|\Delta r|=0.00010\), maximum x error `0.575`,
maximum y error `0.0014`, and the retained drop-one correlation range. The
post-fix reproduction gate is closed.

## Reliance decision

The retained numeric rows may be used unchanged for retrospective
fixed-panel description and the bounded evaluator-substitution census.
RoboWorld supplies VLM-judge/scoring-pipeline substitutions, not a causal
simulator substitution.

This review does not support field prevalence, causal validity, independence
across the four shared-policy panels, per-trial uncertainty, or transport to
new policies and environments.
