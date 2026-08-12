# Review: H224 ArmnetBench v0.1 evaluation-design audit

Date: 2026-07-28

Status: independently challenged; adverse P2 contrast supported; H022 refusal
unchanged.

## Reviewed candidate

- protocol:
  `protocol-h224-armnetbench-paper-design-audit.md`;
- official paper: arXiv `2607.24481v1`, submitted
  `2026-07-27T14:16:43Z`;
- official PDF SHA-256:
  `c1d0edbd163f6db2597da67c4afe03e8b63deb3c2eefbfca613db3ff5319951e`;
- official source-package SHA-256:
  `21e4d8b117878e4d42d810da6e8e2a711c11e146dc389d1fd4ba7da97cf12bf1`;
- extracted `main.tex` SHA-256:
  `8ceaa0e443e561c90b376a22e5c4d541243685d5cb3d42b04d905118907f6e20`;
- producer result:
  `result-h224-armnetbench-paper-design-audit.json`, SHA-256
  `b29dc62a06f2174d2c9a6971dd678b774d728edc33431cee7a2e4976487f000a`;
- independent result:
  `result-h224-armnetbench-paper-design-independent-challenge.json`,
  SHA-256
  `f2ba898c42964f8a49bafb9b11bea2c5bdafbbbdd770af61765b12fdc8afe635`.

The PDF has 11 pages. Pages 3, 4, 5, 6, 8, and 9 were rendered and visually
checked for every relied-on design or limitation passage. They were legible
and consistent with the exact source. PDF metadata independently gives the
fixed title and all three authors. The source enables editing macros but
contains no use of the author-note or TODO commands.

## Unit dispositions

| fixed evidence unit | disposition | decisive boundary |
|---|---|---|
| paper-to-release identity | partial | named Hub collection, no immutable release identity in the paper |
| policy roster/checkpoints | partial | seven named policies and claimed checkpoint release, no evaluated revision/content hashes |
| standalone physical execution | supported | isolated policy container and separate task-policy rollouts |
| context definition/allocation timing | partial | common task/cell setup, no pre-policy allocation commitment |
| assignment/randomization/order | partial | object placement randomized, policy assignment and sequence unreported |
| reset/carryover/interventions | partial | manual resets and two exclusions; no acceptance trace, with wear/camera changes |
| episode/session/dependence identity | partial | episode and cell context, no session/operator/order dependence unit |
| rubric/horizon/missingness/evaluator | partial | three-way operator label and exclusions, but operator-dependent stopping |
| public trial/artifact/outcome linkage | supported | per-episode policy/media/outcome fields, reinforced by H029 |
| dependence-aware uncertainty | absent from fixed scope | no method tied to assignment, order, cell, or session |
| pre-execution evaluator | absent from fixed scope | operator scores after execution; world models are a downstream use |
| cost/capacity | supported | component, cell, supervision, and retrospective labor information |

The least-permissive tally is three `supported`, seven `partial`, two
`absent_from_fixed_scope`, and zero `not_assessed`.

## Independent challenge

The challenger is a separate Node standard-library implementation. It imports
no producer logic. It:

1. verifies the exact PDF, source archive, extracted TeX, H028, H029, H222,
   and producer-result hashes;
2. reconstructs design facts from separately defined exact phrases and
   absence tests;
3. derives the P2 and H022 decisions from those facts; and
4. compares all 12 least-permissive unit statuses with the producer.

It agrees on every unit. It independently returns
`adverse_mismatch_contrast` for P2 and `refused_unchanged` for H022. The saved
challenge validator rejects a positive P2 relabeling, any unit disagreement,
and any use of performance values.

## Adjudication

ArmnetBench is a useful contemporary contrast because it combines several
features that weaker negative cases may lack: seven policies, standalone
physical execution, a common task/cell setup, public trial artifacts, and
substantial operational detail. Those strengths do not supply the missing
identification bridge. The public paper does not establish context commitment
before policy assignment, a policy assignment or execution-order law,
measured reset acceptance, a session/dependence unit, or matching
uncertainty. It therefore qualifies as an adverse/mismatch P2 contrast, not a
positive design contrast and not evidence that the benchmark or rankings are
invalid.

This is a prospective temporal extension of the P2 public-source evidence:
the source was triggered after the earlier P2 synthesis and was selected from
title/identity metadata before performance inspection. It should be added
outside H178's fixed historical roster, with its source-layer status explicit.

The paper adds source-native rubric and artifact detail to the prior
ArmnetBench record but does not repair H022. In particular:

- the evaluated checkpoints remain unbound to immutable revisions;
- the rubric is three-way and the horizon is operator-dependent;
- the public record does not declare the required dependence unit; and
- the only evaluated scoring described here occurs after physical execution.

Corresponding-video evaluation remains post-execution and is not relabeled.

## Outcome-exposure disposition

The protocol was fixed before opening the abstract, PDF, source, or linked
artifacts. Three later exposures are retained:

1. the abstract displayed aggregate episode counts and label classes;
2. a source search incidentally displayed one performance sentence from the
   Results section; and
3. the required visual check of PDF page 8 displayed result tables immediately
   above the limitations section.

No performance value or ranking is copied into the canonical result, compared,
interpreted, or used in any unit coding or decision. The exposure cannot have
selected the source or changed the fixed decision rules. H224 is nevertheless
not an outcome-blinded reading of the full paper, and no later claim should
represent it as one.

## Remaining uncertainty and stop rule

The audit is bounded to the exact v1 public paper plus the already governed
H028/H029 records. It does not establish how the experiment was privately
scheduled, whether unlinked logs exist, whether the released containers and
checkpoints reproduce execution, or whether any design limitation affected a
policy result.

Do not open linked data, code, checkpoints, or media under H224. Revisit only
under a separately fixed question if a version-bound assignment/order ledger,
session/lifecycle record, fixed horizon, immutable checkpoint manifest, or
pre-execution evaluator becomes public.
