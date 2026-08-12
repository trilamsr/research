---
title: "Supplement to: What Does a Sim-to-Real Correlation Support?"
author: "Tri Lam"
date: "2026-08-06"
---

## S1. Consensus and bounded-sample facts

| fact | result | interpretation |
|---|---:|---|
| Included papers | 26 | non-systematic claim-based corpus |
| Papers with recovered numeric results | 19 | recovery from published figures or tables |
| Finite displayed panel | 26/26 | all audited papers |
| Defined target population or probability-sampling mechanism | 0/26 | none reported |
| Coefficient p-value | 5/26 | null-test output, not interval uncertainty in magnitude |
| Coefficient interval | 1/26 | interval uncertainty for coefficient magnitude |
| Neither p-value nor coefficient interval | 20/26 | observable reporting fact; not evidence the coefficient is wrong |

## S2. Unit-count sensitivity

The two columns answer a policy/checkpoint sensitivity question; they do not treat tasks or conditions as automatically exchangeable units.

| paper | legacy policy/lineage blocks | permissive checkpoints/variants |
|---|---:|---:|
| real2sim-eval | 4 | 20 |
| RoboWorld | 8 | 8 |
| Digital Cousins | 4 | 4 |
| SIMPLER | 4 | 6 |
| SimFoundry | 5 | 8 |
| WorldGym | 3 | 3 |
| RoboSnap | 1 | 10 |
| REALM | 3 | 3 |
| PolaRiS | 4 | 4 |
| SC3-Eval | 1 | 7 |
| WorldEval | 4 | 4 |
| A Practical Recipe | 5 | 5 |
| Cosmos-Surg-dVRK | 3 | 6 |
| Gemini/Veo | 8 | 8 |
| DreamDojo | 1 | 6 |
| dWorldEval | 1 | 5 |
| WEAVER | 2 | 2 |
| PlayWorld | 18 | 18 |
| EmbodiedSplat | 2 | 4 |
| MolmoSpaces | 3 | 8 |
| Mem-World | 2 | 2 |
| Colosseum V2 | 1 | 1 |
| VISER | 1 | 2 |
| OSCAR | 2 | 7 |
| Hi-WM | 2 | 4 |
| WM-PolicyEval | 3 | 3 |

Across these two explicit codings, **23–25 of 26** papers have fewer than ten policy/checkpoint blocks.

## S3. Axis-specific best-case permutation resolution

These are combinatorial resolutions conditional on valid exchangeability, not exact test results. Tied statistics can make the attained minimum coarser.

| paper | printed p | policy k | 1/k! | task k | 1/k! |
|---|---:|---:|---:|---:|---:|
| RoboWorld | <0.001 | 8 | 0.000025 | — | — |
| WorldGym | <0.001 | 3 | 0.166667 | 17 | 0.000000 |
| REALM | <0.001 | 3 | 0.166667 | 7 | 0.000198 |
| Cosmos-Surg-dVRK | <0.001 | 3 | 0.166667 | 4 | 0.041667 |
| Mem-World | <0.001 | 2 | 0.500000 | 5 | 0.008333 |

## S4. Complete leave-one-unit/point table

The 0.10 column is retained only as a descriptive screen. The continuous movement and deletion unit are the reported quantities.

| dataset | points | deletion units | unit | r | max abs change in r | max abs change in rho | >0.10 |
|---|---:|---:|---|---:|---:|---:|:---:|
| real2sim-eval toy | 17 | 4 | policy | 0.9444 | 0.006 | 0.054 | no |
| real2sim-eval rope | 20 | 4 | policy | 0.9007 | 0.029 | 0.073 | no |
| real2sim-eval T-block | 15 | 4 | policy | 0.9147 | 0.048 | 0.090 | no |
| RoboWorld 10a | 8 | 8 | policy | 0.9005 | 0.075 | 0.042 | no |
| RoboWorld 10b | 8 | 8 | policy | 0.8762 | 0.169 | 0.113 | yes |
| RoboWorld 9a | 8 | 8 | policy | 0.9888 | 0.191 | 0.021 | yes |
| RoboWorld 9b | 8 | 8 | policy | 0.9438 | 0.165 | 0.090 | yes |
| Digital Cousins (unit = policy) | 16 | 4 | policy | 0.9094 | 0.013 | 0.047 | no |
| Digital Cousins (unit = gen. level) | 16 | 4 | generalization level | 0.9094 | 0.037 | 0.063 | no |
| Cosmos-Surg-dVRK automated | 24 | 3 | policy run | 0.7561 | 0.073 | 0.086 | no |
| Cosmos-Surg-dVRK manual | 24 | 3 | policy run | 0.7180 | 0.123 | 0.131 | yes |
| DreamDojo | 6 | 6 | point | 0.9953 | 0.010 | 0.057 | no |
| MolmoSpaces pick | 8 | 8 | point | 0.9585 | 0.020 | 0.000 | no |
| MolmoSpaces open | 4 | 4 | point | 0.8523 | 0.617 | 0.900 | yes |
| MolmoSpaces close | 4 | 4 | point | 0.9727 | 0.040 | 0.000 | no |
| REALM Overall | 21 | 3 | policy | 0.9187 | 0.025 | 0.022 | no |
| REALM Default | 21 | 3 | policy | 0.8838 | 0.135 | 0.057 | yes |
| REALM VB-POSE | 21 | 3 | policy | 0.9335 | 0.080 | 0.187 | no |
| REALM V-VIEW | 14 | 3 | policy | 0.8902 | 0.168 | 0.080 | yes |
| subject paper toy, 200 episodes | 17 | 4 | policy | 0.8970 | 0.011 | 0.095 | no |
| subject paper rope, 200 episodes | 20 | 4 | policy | 0.9181 | 0.043 | 0.088 | no |
| subject paper T-block, 200 episodes | 15 | 4 | policy | 0.9501 | 0.037 | 0.071 | no |
| VISER Octo | 4 | 4 | point | 0.9988 | 0.000 | 0.028 | no |
| VISER OpenVLA | 5 | 5 | point | 0.8496 | 0.135 | 0.300 | yes |
| OSCAR | 7 | 7 | point | 0.8552 | 0.086 | 0.132 | no |
| Hi-WM | 12 | 12 | point | 0.9540 | 0.014 | 0.019 | no |
| WM-PolicyEval Cosmos | 12 | 12 | point | 0.7193 | 0.260 | 0.130 | yes |
| WM-PolicyEval IRASim | 12 | 12 | point | 0.2772 | 0.176 | 0.237 | yes |

Median maximum absolute change in r = 0.061; range 0.000–0.617. The descriptive 0.10 screen selects 10/28 illustrative rows; this is not a corpus-prevalence estimate.

## S5. Bounded decision cases

Each row concerns only the displayed policies and the stated aggregation rule. Top-1 agreement means that the simulator-selected winner belongs to the real-data winner set; regret is the displayed real-success gap to the best policy.

| case | declared rule | r | top-1 result | real regret | diagnostic |
|---|---|---:|---|---:|---|
| SIMPLER Google | equal-weight mean over 5 displayed tasks | 0.974 | agreement | 0 | 3/5 individual tasks agree; 5/5 leave-one-task-out aggregates agree |
| SIMPLER WidowX | equal-weight mean over 4 displayed tasks | 0.950 | agreement | 0 | 3/4 individual tasks agree; 4/4 leave-one-task-out aggregates agree |
| Real2Sim T-block | select each policy's best simulated checkpoint | 0.878–0.947 | disagreement | 12.50 pp | non-winning checkpoint tie changes r but not the selected or real winner |
| A Practical Recipe | printed top-ranked variant in each rank panel | varies | 3/11 panels disagree | — | largest printed Pearson r among disagreements = 0.672 |

Across Real2Sim's three tasks and three declared checkpoint-collapse rules, 7/9 cells necessarily disagree, 1/9 robustly agrees, and 1/9 is tie-dependent. These nine cells share data and are not independent repetitions.

The vector extraction contains two coincident rope/DP markers at (0,0). Removing one changes all-checkpoint r from 0.901 to 0.881 and mean-rule r from 0.697 to 0.538, but it does not change any of the three rope rule-level top-1 conclusions.

## S6. Complete direct-cell matrices

All eligible direct-cell matrices derived from the retained source inventory under the declared candidate/block rules; outcome-exposed and not a prevalence denominator.

| panel | source metric bundle | audit Pearson r | audit Spearman rho | top-1 | regret (pp) | LOTO |
|---|---|---:|---:|---|---:|---:|
| Cosmos-Surg-dVRK — automated fig1b | Pearson + MMRV | 0.941 | 0.829 | correct | 0.00 | 1/4 |
| Cosmos-Surg-dVRK — manual human vs dvrk | Pearson + MMRV | 0.883 | 0.371 | wrong | 10.00 | 0/4 |
| Digital Cousins | Pearson | 0.997 | 1.000 | correct | 0.00 | 4/4 |
| EmbodiedSplat — mesh-conditions | Pearson | 0.936 | 0.800 | correct | 0.00 | 2/2 |
| Hi-WM | Pearson | 0.964 | 1.000 | correct | 0.00 | 3/3 |
| Mem-World | Pearson + p-value | 1.000 | 1.000 | correct | 0.00 | 5/5 |
| MolmoSpaces — common-appendix-roster | Pearson + Spearman | 0.982 | 0.800 | correct | 0.00 | 3/3 |
| REALM — Default | Pearson + MMRV | 1.000 | 1.000 | correct | 0.00 | 7/7 |
| REALM — Overall | Pearson + MMRV | 1.000 | 1.000 | correct | 0.00 | 7/7 |
| REALM — VB-POSE | Pearson + MMRV | 1.000 | 1.000 | correct | 0.00 | 3/7 |
| SIMPLER — google robot | Pearson + MMRV | 0.974 | 1.000 | correct | 0.00 | 5/5 |
| SIMPLER — widowx | Pearson + MMRV | 0.950 | 1.000 | correct | 0.00 | 4/4 |
| WEAVER — CtrlWorld | Pearson + Spearman | 1.000 | 1.000 | correct | 0.00 | 5/5 |
| WEAVER — WEAVER | Pearson + Spearman | 1.000 | 1.000 | correct | 0.00 | 5/5 |
| WEAVER — WEAVER-FT | Pearson + Spearman | 1.000 | 1.000 | correct | 0.00 | 5/5 |
| WM-PolicyEval — Cosmos | Pearson + MMRV | 0.975 | 1.000 | correct | 0.00 | 4/4 |
| WM-PolicyEval — IRASim | Pearson + MMRV | 0.507 | 0.500 | wrong | 27.50 | 1/4 |
| WorldEval | Pearson | 0.996 | 0.800 | correct | 0.00 | 5/5 |
| WorldGym | Pearson + ranking-preservation analysis | 0.992 | 1.000 | correct | 0.00 | 17/17 |

The complete-matrix set contains 17/19 displayed top-1 agreements and 2/19 displayed top-1 disagreements. These counts describe this non-systematic recovered set only.

## S7. Illustrative cross-source decision atlas

Heterogeneous finite-panel cases selected for evidentiary roles; not a calibration sample, prevalence denominator, or common population.

| case | r | simulated winner | displayed real winner | regret (pp) | LOTO | evidence |
|---|---:|---|---|---:|---:|---|
| WorldGym | 0.992 | OpenVLA | OpenVLA | 0.00 | 17/17 | exact published table |
| Digital Cousins | 0.997 | pi_0 | pi_0 | 0.00 | 4/4 | table-validated recovered values |
| SIMPLER Google | 0.974 | rt-1-converged | rt-1-converged | 0.00 | 5/5 | official source arrays |
| Real2Sim T best-sim checkpoint | 0.878–0.947 | pi0 | dp | 12.50 | — | vector-PDF recovery; printed coefficient reproduced |
| OSCAR Skeleton | 0.855 | PG-FAST+ | pi0-FAST | 1.10 | — | printed one-decimal bar labels; r reproduced to rounding |
| Cosmos-Surg manual | 0.883 | GR00T N1.5 50k | GR00T N1 20k | 10.00 | 0/4 | vector-PDF recovery; pooled coefficient reproduced |
| WM-PolicyEval / Cosmos | 0.975 | OpenVLA | OpenVLA | 0.00 | 4/4 | vector-PDF recovery plus exact appendix real values |
| WM-PolicyEval / IRASim | 0.507 | Octo-Base | OpenVLA | 27.50 | 1/4 | vector-PDF recovery plus exact appendix real values |

## S8. Finite-real-trial remeasurement

Model-conditional real-trial measurement uncertainty for cases with documented real denominators; simulator values held fixed where simulator rollout counts are unavailable. Candidate/block probabilities are independent in the fitted model; cross-candidate coupling is not identified by published marginal counts.

| case | posterior P(sim winner is real-best) | posterior expected regret (pp) | real denominator | simulator denominator |
|---|---:|---:|---|---|
| Cosmos-Surg manual | 0.087508 | 11.64 | 10 trials per policy-task | 10 initial states x 3 generated seeds x 2 raters; aggregate allocation/dependence unreleased |
| WM-PolicyEval / Cosmos | 0.999852 | 0.00 | 20 trials per policy-task | unstated |
| WM-PolicyEval / IRASim | 0.000168 | 24.99 | 20 trials per policy-task | unstated |

### S8.1 Missing simulator-evidence sensitivity

The effective simulator evidence grid is a sensitivity design, not an estimate of the unreleased rollout denominator.

| evaluator | sampled-winner match range | expected real-regret range (pp) | all scenarios below one half? | first listed crossing by prior (.5/1/2) |
|---|---:|---:|---|---|
| Cosmos | 0.3333–0.9999 | 0.0–18.6 | false | 2/2/5 |
| IRASim | 0.0001–0.4320 | 13.2–26.2 | true | none/none/none |

### S8.2 Policy-heterogeneous simulator evidence

The sampled-winner estimand measures latent-rank concordance under one common assumed evidence size, not observed-action reliability. The next rows vary assumed evidence by policy; actual evidence remains unknown.

| IRASim scenario | evidence (Octo-Base/Octo-Small/OpenVLA) | latent-winner concordance | MCSE | posterior-mean simulator winner |
|---|---|---:|---:|---|
| common_10 | 10/10/10 | 0.4302 | 0.00070 | Octo-Base |
| openvla_10 | 500/500/10 | 0.7339 | 0.00062 | OpenVLA |
| openvla_0 | 500/500/0 | 0.9821 | 0.00019 | OpenVLA |

### S8.3 Probability-level affine calibration

Cell-rate MSE and the empirical individual-outcome Brier score are different estimands. Their exact difference here is the empirical within-cell outcome variance. Positive affine calibration preserves the displayed aggregate winner.

| evaluator | mean predicted-real | cell-rate MSE | empirical Brier | intercept | slope | task-held-out recalibrated MSE | winner preserved? |
|---|---:|---:|---:|---:|---:|---:|---|
| Cosmos | -0.08750 | 0.02396 | 0.20417 | 0.133 | 0.791 | 0.02119 | yes |
| IRASim | -0.14583 | 0.05563 | 0.23583 | 0.240 | 0.402 | 0.03693 | yes |

### S8.4 Nonlinear calibration and Murphy decomposition

The isotonic map is fitted and evaluated on the same 12 cells. It is an in-sample shape sensitivity, not prospective calibration or selection repair.

| evaluator | raw winner | isotonic winner | raw rate MSE | isotonic in-sample MSE | Murphy reliability | resolution | Brier skill vs prevalence |
|---|---|---|---:|---:|---:|---:|---:|
| Cosmos | OpenVLA | OpenVLA | 0.02396 | 0.01149 | 0.01333 | 0.02082 | 0.035 |
| IRASim | Octo-Base | OpenVLA | 0.05563 | 0.02131 | 0.05219 | 0.02800 | -0.114 |

## S9. Exact displayed-task composition sensitivity

Exact sensitivity over every non-empty subset of complete displayed task/condition blocks; not a sampling probability.

| case | leave-one-task-out correct | all nonempty subsets correct |
|---|---:|---:|
| WorldGym | 17/17 | 131068/131071 |
| Digital Cousins | 4/4 | 15/15 |
| SIMPLER Google | 5/5 | 24/31 |
| Cosmos-Surg manual | 0/4 | 2/15 |
| WM-PolicyEval / Cosmos | 4/4 | 12/15 |
| WM-PolicyEval / IRASim | 1/4 | 4/15 |

## S10. Checkpoint-selection sensitivity

All tied maxima are enumerated. A range therefore reflects the selection rule itself, not arbitrary file order.

| task | checkpoints | all-checkpoint r | best-real r range | tie combinations | best-sim r range | tie combinations |
|---|---:|---:|---:|---:|---:|---:|
| T | 15 | 0.915 | 0.878 to 0.944 | 2 | 0.878 to 0.947 | 2 |
| rope | 20 | 0.901 | -0.471 to -0.103 | 4 | -0.683 to -0.683 | 1 |
| sloth | 17 | 0.944 | 0.905 to 0.941 | 4 | 0.933 to 0.968 | 2 |

## S11. MMRV versus correlation stability

MMRV uses SIMPLER's strict-ordering XOR, real-side gap, and divide-by-N convention. RoboWorld's real-side leaderboard score is min-max scaled once on the full panel.

| dataset | k | MMRV | absolute MMRV range | relative r swing | relative MMRV swing | ratio |
|---|---:|---:|---:|---:|---:|---:|
| Digital Cousins, by policy | 4 | 0.111459 | 0.020831 | 1.9% | 18.7% | 9.8× |
| Digital Cousins, by generalization level | 4 | 0.111459 | 0.088890 | 8.1% | 79.8% | 9.8× |
| RoboWorld 10a | 8 | 0.005765 | 0.003467 | 15.4% | 60.2% | 3.9× |
| RoboWorld 10b | 8 | 0.055067 | 0.044383 | 30.0% | 80.6% | 2.7× |

## S12. Real2Sim MMRV convention reproduction

The declared grid has 60 named entries but 48 distinct formulas because one predicate pair is pointwise identical by construction. Exactly one distinct formula matches all three Table I values and all three Figure 9 values: less-than-or-equal XOR (equivalently strict-> XOR), simulated-side gap, divide by N.

| panel | N | episodes | recovered r | printed r | exact recovered MMRV | printed MMRV |
|---|---:|---:|---:|---:|---:|---:|
| toy packing | 17 | 20 | 0.9444 | 0.944 | 13/170 (0.076471) | 0.076 |
| rope routing | 20 | 27 | 0.9007 | 0.901 | 47/270 (0.174074) | 0.174 |
| T-block pushing | 15 | 16 | 0.9147 | 0.915 | 13/120 (0.108333) | 0.108 |

The following appendix values use the same recovered convention:

| panel | exact recovered MMRV | decimal |
|---|---:|---:|
| Figure 9 toy_packing | 21/200 | 0.105000 |
| Figure 9 rope_routing | 307/2000 | 0.153500 |
| Figure 9 t_block_pushing | 209/3000 | 0.069667 |

We recover 15 T-block checkpoints from Figure 3; they reproduce Table I's $r=.915$ and MMRV $=.108$. Figure 10 reports a separate 12-checkpoint replay subset.

## S13. Model-conditional correlation sensitivity

These are equal-tailed posterior intervals under iid bivariate-normal unit summaries and a uniform prior on rho. They are not assumption-free intervals.

| task | unit-level r | n | 95% posterior interval |
|---|---:|---:|---:|
| T | 0.962 | 4 | [-0.256, 0.978] |
| rope | 0.697 | 4 | [-0.538, 0.901] |
| sloth | 0.984 | 4 | [-0.163, 0.989] |
