# P1 knowledge-gap register

Date: 2026-07-26

Purpose: author/auditor control for P1's bounded reporting audit and
decision-case evidence. This is not manuscript prose. External facts are
controlled by `../../../FINDINGS.md`; generated quantities are controlled by
`result-paper-evidence.json`.

## Resolution rule

The investigation asks what the present sources and computations establish.
It does not add hypothetical defenses or speculative mitigation analyses.

| ID | factual question | investigation and evidence | disposition | manuscript consequence |
|---|---|---|---|---|
| G01 | Is the corpus a field census or systematic review? | Search logs contain known misses; Searches 1–2 are incompletely logged. | Closed: no. It is a frozen 26-paper claim-based corpus. | All fractions are within-corpus reporting facts. Never state field prevalence. |
| G02 | Are the three codings independent coders of identical rows? | Two source-only codings used different coefficient-row granularities; the released grid is adjudicated. | Closed: no. Paper-level claims have three-way agreement; coefficient-level pooled reliability is unidentified. | Say “three codings,” not “three independent coders.” Do not report pooled kappa. |
| G03 | Is 26/26 finite-panel itself a substantive deficiency? | A correlation necessarily has entering observations; the coding establishes only that the displayed panel is describable. | Closed: weak alone. The defensible contrast is 0/26 defined target population or probability-sampling mechanism. The original support rule is design-based and not exhaustive of model/transport routes. | Do not headline 26/26 without the target-population contrast; suspend universal no-supported-inference wording. |
| G04 | Is coefficient inference truly absent in 20/26? | Version-specific figures/text were checked; WorldGym’s figure-only `p<.001` corrected the earlier count. | Closed for the observable reporting rule: 5 p-value papers, 1 interval paper, 20 neither. | Report p-values and coefficient intervals separately; a p-value is not interval uncertainty in coefficient magnitude. |
| G05 | What is the independent-unit count? | Policy lineage and permissive checkpoint/variant codings yield 25/26 and 23/26 below ten. Policy, task, and cell axes differ. | Closed only as two sensitivity codings. No universal effective \(n\). | Print the construct and range; never call all blocks independent runs. |
| G06 | Do printed p-values violate permutation-test resolution? | Four of five thresholds are below \(1/k!\) on the adopted policy-block axis. Source test schemes and exchangeability units are generally unspecified; task-axis resolutions differ. | Closed as a conditional resolution comparison, not an invalidity finding. | Keep in supplement or a tightly qualified inference section. |
| G07 | Are Fisher-\(z\) and permutation general small-\(k\) remedies? | Fisher-\(z\) is an approximation under iid bivariate-normal unit summaries. Permutation exactness requires the declared null and exchangeability scheme; discreteness remains. | Closed: no universal remedy. | Present assumption-labeled options, not “what still works.” Bootstrap-support counts are diagnostics, not coverage theorems. |
| G08 | Are the SIMPLER equal-task correlations source-reported? | Official `REAL_PERF`/`SIMPLER_PERF` arrays and `tools/calc_metrics.py` were checked. The source script operates task-by-task. | Closed: no. The equal-task means are newly declared audit estimands. | Label them as audit-defined. Do not attribute .974/.950 aggregate coefficients to SIMPLER. |
| G09 | Is the SIMPLER positive decision stable within its displayed task set? | Google: top-1 agrees, 3/5 task decisions agree, and all 5 leave-one-task-out aggregates agree. WidowX: 3/4 tasks and all 4 LOTO aggregates agree. | Closed descriptively. | Report aggregate, task heterogeneity, and LOTO together. No task-population inference or uncertainty claim. |
| G10 | Is Real2Sim’s high-correlation failure tie-complete? | All checkpoint-maximizer and policy-winner ties were enumerated for best-real, best-sim, and mean rules. | Closed: 7/9 necessarily wrong, 1/9 robustly correct, 1/9 tie-dependent. For T/best-sim, a non-winning SVLA checkpoint tie changes \(r=.878\)–\(.947\) but not the selected winner or 12.5-point regret. | The 9 cells share data and are not a frequency sample. Use T/best-sim as the source-aligned case and display its correlation range. |
| G11 | Is best-real a deployable rule? | It selects checkpoints with real outcomes. | Closed: no. It is an oracle/descriptive sensitivity rule. | Label best-real as diagnostic. Best-sim and mean are operationally interpretable but not uniquely mandated by the source. |
| G12 | Does the rope extraction have an unresolved duplicate? | Two same-colour DP markers coincide at \((0,0)\). Keeping both better reproduces the printed source \(r\). One-row deletion changes all-point and mean-rule \(r\), but no rope top-1 classification. | Closed as an extraction sensitivity; marker identity remains unresolved. | State both numerical readings in the supplement. Do not call either marker erroneous. |
| G13 | Does “7/9 wrong” estimate a failure rate? | Cells reuse the same three task data and multiple collapse rules. | Closed: no. | Use it only as a complete map of declared cases; do not attach binomial uncertainty or prevalence language. |
| G14 | Can A Practical Recipe support absolute decision loss? | Source rank strings identify top-1 and reproduce Spearman; absolute success rates are unavailable. | Closed: top-1 is recoverable, Pearson/MMRV/regret are not independently recomputable from ranks. | Report 3/11 source-printed rank disagreements and the printed association values; no regret or PCS. |
| G15 | Is A Practical Recipe a high-correlation negative arm? | Largest printed Pearson among its three disagreement panels is .672. | Closed: no. | Use it as source diversity and rank-disagreement breadth, not the headline counterexample. |
| G16 | What exactly does the SIMPLER/Real2Sim contrast establish? | Under declared finite-panel rules, SIMPLER Google has \(r=.973627\), correct top-1; Real2Sim T best-simulated-checkpoint has \(r=.877820\)–\(.947469\), wrong top-1 and 12.5 pp regret. | Closed: correlation magnitude alone is logically insufficient for these audit-declared decisions. | Do not imply causal simulator comparison, threshold calibration, source-specified top-1, or population failure probability. |
| G17 | Are the Real2Sim MMRV values and T count settled? | One of 60 conventions reproduces six values; Figure 3 geometry/lattice and source context establish 15 T points; 12 is replay. | Numerically closed. “Bug” attribution is conditional on unarchived author email. | Report the convention mismatch as reproducible. Either label the bug attribution personal communication or omit motive. |
| G18 | Can a reader rerun the original Real2Sim experiment? | Public artifacts expose checkpoint collections, example checkpoint paths, evaluation commands, and task-specific success scripts, but a 2026-07-28 recovery search found no exact Figure-3 point-to-checkpoint/run manifest, all paired rates, realized initial states, task-specific fit configs, or complete raw captures. | Externally blocked and nonfatal to the audit. | Claim recomputation from published displays, not source-experiment rerunning or twin refitting; see `review-p1-extraction-and-real2sim-provenance-recovery-2026-07-28.md`. |
| G19 | Are source-display inconsistencies diagnosed causally? | Published alternatives reproduce for RoboSnap, WorldEval, WM-PolicyEval, and others. A reply signed by RoboSnap coauthor Shujie confirms that its inline table is the numerical source of record and that the scatter markers were positioned manually in PowerPoint for presentation; the respondent's surname and raw email headers were not independently established. Other cases still lack authoritative raw matrices/code. | RoboSnap cause and source identity closed by author-confirmed personal communication; other causes remain unresolved. | Use RoboSnap's table values and label the plotting account as personal communication. Continue reporting other bounded mismatches without alleging intent or implementation cause. |
| G20 | Are the 28 leverage panels representative? | They are historically selected recovered panels with heterogeneous deletion units. | Closed: no. | Report continuous movements and full row list only; never use 10/28 as corpus prevalence. |
| G21 | Does MMRV’s greater relative deletion movement generalize? | 2.7–9.8× holds in four declared panels and depends on metric scale/convention. | Closed only for those panels. | Print absolute ranges and label the comparison illustrative. |
| G22 | Is the combined reader package sufficient and minimal? | Generated decision inputs, estimand grids, code, tests, provenance headers, and upstream-artifact audit are present. A cache-free copy installed only pinned requirements and passed 84 tests plus every declared target. | Closed for the declared P1 package. | Keep the three reproduction tiers visible; no claim of rerunning source robot experiments. |
| G23 | Is every main-table width appropriate? | The final 12-page PDF was rebuilt with TeX default fonts, all pages were visually inspected, and dense decision/artifact tables fit without overfull boxes. | Closed for the current PDF. | Reinspect affected pages after any later prose/table change. |
| G24 | Is Real2Sim the only independent high-correlation wrong-selection case? | Extended equal-task/policy decision recovery to every suitable released matrix. OSCAR has printed \(r=.852\) (recovered .855) with wrong top-1 and 1.1 pp regret. Cosmos-Surg manual has audit-defined policy-mean \(r=.883\), wrong top-1, and 10 pp regret. | Closed: no. | The logical result can be triangulated across three independent papers rather than resting on one extraction. |
| G25 | Does finite real-trial noise plausibly erase the three main negative cases? | A 500k-draw block-level Beta(1,1)-binomial posterior holds displayed simulator winners fixed and propagates documented real counts. Under independent candidate probabilities, support is .2566 for the separate Real2Sim T mean-rule sensitivity, .0875 for Cosmos manual, and .000168 for WM-PolicyEval IRASim. | Open across joint dependence: the point results reproduce, but published marginal counts do not identify cross-candidate coupling. | Label these as independent-model point estimates, not robust conclusions. Real2Sim mean-rule remeasurement is not evidence for the best-sim checkpoint case. |
| G26 | Are positive and negative decisions driven by one task? | Exact enumeration of all nonempty complete task subsets and every leave-one-task-out aggregate. Under the robust tie rule, WorldGym is 17/17 LOTO and 131068/131071 all-subset correct; Cosmos manual is 0/4 LOTO and 2/15 all-subset correct (3/15 possibly correct). | Closed descriptively for released complete matrices. | Use robust LOTO as the concise result; identify possible correctness separately when ties make it differ. |
| G27 | Are the positive controls genuinely stable under the same protocol? | Applied the identical task-subset calculation to WorldGym, Digital Cousins, Hi-WM, SIMPLER, WorldEval, WEAVER, and WM-PolicyEval/Cosmos. | Closed: WorldGym and Digital Cousins are exceptionally stable; some other nominal positives are composition-sensitive. | Present stable positives and robust negatives together; do not classify cases from full-panel top-1 alone. |
| G28 | Can OSCAR and Cosmos support two-sided measurement uncertainty? | OSCAR's 63 release IDs join to task instructions and 441 real binary outcomes in a pinned pre-paper RoboArena dump, but no GPT-5 judgments are released and printed WM rates imply 65 sessions. All media decode, and the outcome-independent 70-clip base packet has frame-equivalent generated-half crops and identity-blinded rater sheets. Cosmos officially documents 10 states × 3 seeds × 2 raters, confirming the 1/60 grid, but not individual label allocation. | Closed for a Cosmos aggregate sensitivity. OSCAR's real side, media, and base labeling packet are now closed; its published evaluator side and human label reliability remain externally blocked. | Report Cosmos two-sided stress over 10/30/60 effective label equivalents. For OSCAR, independently adjudicate controls and field the prepared pilot, or obtain the 65-session GPT-5 table and two-session reconciliation. |
| G29 | Can a correlation threshold be calibrated from the expanded decision atlas? | Correct and incorrect decisions coexist around \(r=.85-.98\), but panels differ in candidates, axes, aggregation, extraction grade, and sampling. | Closed negatively: no identified calibration sample or common loss. | Do not propose a universal cutoff. The evidence supports non-sufficiency, not threshold estimation. |
| G30 | Does the combined negative result survive source diversity? | Negative decisions now appear in Real2Sim (vector PDF), OSCAR (printed bar values), Cosmos-Surg (two vector figures), Recipe (printed ranks), and WM-PolicyEval (vector figure plus recovered appendix). | Closed for source-method triangulation. | Organize cases by evidentiary role rather than treating 7/9 or 3/11 as prevalence. |
| G31 | Is the displayed atlas eligibility-complete? | The first 13-row repair circularly inherited the prior subset-analysis set and omitted complete matrices. A source-file disposition audit now accounts for every retained numeric CSV and validates 19 direct-cell candidate x task/condition matrices: 17 correct and 2 wrong. | Closed for the declared inventory-derived direct-cell rule; the parent corpus and normalization choices remain outcome-exposed. | Link the full 19-row ledger before the illustrative atlas and never present the balanced display or 17/19 as a prevalence denominator. |
| G32 | Do the source papers rely on Pearson alone? | Primary-source claim mapping shows SIMPLER, Real2Sim, OSCAR, Cosmos-Surg, and WM-PolicyEval report rank-aware companion metrics. OSCAR’s \(\rho=.750\)/rank displacement and Cosmos manual’s audit \(\rho=.371\) already warn of rank disagreement. | Closed negatively. | Do not frame P1 as exposing author ignorance of ranking. The sharper gap is failure to connect metric bundles to a named action, loss, tolerance, tie rule, and budget. |
| G33 | Are the atlas top-1 rules the sources’ intended decisions? | Sources often claim ranking, checkpoint selection, screening, or replacement of real evaluation, but no headline source specifies the exact audit top-1 rule, task weights, tolerance, and budget. Real2Sim explicitly motivates checkpoint selection, making best-sim more aligned than the former mean rule. | Closed for wording; operational sufficiency remains open. | Use “audit-declared” or “source-aligned,” never “source-intended,” unless the exact action components are quoted. |
| G34 | Can a universal Pearson threshold below one guarantee correct top-1 selection? | Independently challenged three-candidate and fixed-regret constructions show \(r\to1\) with a wrong unique winner; two candidates are an explicit exception because positive \(r=1\) fixes order. | Closed negatively for exact finite panels with at least three candidates. This is elementary scope theory, not a new general theorem. | Do not calibrate or recommend a universal cutoff from the corpus or the construction. |
| G35 | Does Pearson imply any panel-specific regret statement? | Established squared-loss-to-decision-risk theory plus the OLS identity yields a retrospective finite-panel bound; a separately challenged simulator-margin refinement is often sharper. Source-resolution recomputation covers all 19 matrices: 19 positive-correlation certificates, 15 margin improvements, 12 zero-margin certificates, and 13 margin certificates equal to observed regret. | Closed as deterministic displayed-panel algebra. The generic inequality collides with prior theory and uses observed real dispersion; exact regret is already known when all real outcomes are known. | Treat as an explanatory diagnostic, not novel general theory, prediction, population transport, or causal validity. |
| G36 | Can the RoboWorld values be relied on under the v4 corpus pin? | Explicit official v3/v4 source archives have identical 33-file scientific manifests and byte-identical score/success figures. Independent v4 vector and repaired pixel re-extractions preserve every order, tie, winner, and coefficient to the declared residuals. The live rollout count is 4,186, not the 4,188 value in commented draft source. | Closed for retrospective fixed-panel use; the exact originally downloaded archive container remains unreconstructible but cannot change these identical scientific files. | Keep the numeric rows; cite the provenance review. Do not infer per-policy trial counts or independent panel replication. |
| G37 | What happens when an observed evaluator or scoring pipeline is substituted on the same fixed target? | A challenged census dispositions all 23 retained numeric sources and admits five absolute groups plus two rank-only groups. Cosmos manual and WM-PolicyEval/IRASim change the aggregate winner with 0.10 and 0.275 native success-proportion regret. WEAVER and both RoboWorld judge pairs retain the aggregate winner; WEAVER changes one of five block winners. Recipe changes winner in Vision and Layout but not Language or Behavior. EmbodiedSplat and WEAVER-FT are excluded by executable real-matrix mismatches. | Closed descriptively for available fixed contrasts: 2/5 absolute groups change aggregate winners, 2/10 outputs have nonzero regret, and 2/4 rank dimensions change winners. These dependent census counts are not rates. | Do not interpret as prevalence, causal evaluator effects, evaluator superiority, calibration, independent replication, or transport. |
| G38 | Can the complete forced-pair design support a materially sharper honest finite-cohort regret band than Stage 1 Hoeffding? | A frozen proof derives the sharp K=7 outcome-free block variance cap \(385/12\) and centered cap 30. Exhaustive K=3 equal/unequal-weight oracles, rigorous outward intervals, and independent causal, numerical, literature, and compute-integrity challenges validate a classical Bernstein baseline. | Closed positively for the binary, no-interference, independently permuted complete-block branch. Five-point sufficient width falls from 113,232 to 11,088 sessions, but remains a conservative width result. | Do not call this power, enrollment, field readiness, an exact randomization interval, or evidence that field assumptions hold. Prefixes and Stage 2B remain open. |
| G39 | Can the Stage 2A assignment law and access controls be verified against a live RoboArena/site export? | The dated public-access review finds zero eligible post-intake sessions and no available server/site assignment-export contract. A later source refresh found an official evaluator-onboarding contact form for volunteers with DROID access, but no deployed client, assignment/export contract, authorized site capacity, or native evidence. A hostilely reviewed synthetic harness recomputes context bindings, replays pair and orientation draws, separates stream identities/states, reconciles events and attempts, and refuses fake native, exact-randomness, execution, outcome, and field claims. | Open externally. A contact path exists; the structural/replay validator is qualified only on synthetic fixtures and no native verifier or deployed mechanism is available. | After the operational target is fixed, request immutable native bytes, signatures/witnesses, append-only events, access logs, deployed RNG/configuration, reset/sealing telemetry, post-block openings, and a shadow rehearsal. Re-review the new native verifier before any Stage A/B reliance. |
| G40 | If only the first execution in each pair is primary, what is identified and does balancing first counts solve the precision problem? | A frozen protocol and independently challenged exact implementation identify only a fixed-context uniform-partner paired-mixture target. All \(2^{18}\times48\) K=3 binary schedule-assignment cases, comparator universes, all-schedule invariances, analytic Hoeffding algebra, and the 512-schedule no-partner subclass reproduce. A K=7 counterexample gives variance \(1/20\) under uniform regular tournaments versus \(1/24\) under independent orientations. | Closed for outcome-free Stage 0/1 mathematics; open for design selection and field meaning. Fixed first counts do not uniformly dominate. Paired-only outcomes do not identify standalone success without additional identifying restrictions; pointwise no-partner equality is one strong sufficient bridge, not the only logically possible bridge. | Do not present first-only as a field solution. Resolve paired-mixture versus standalone target, sealing, reset/history, fresh-context availability, native assignment, completion/missingness, and cost telemetry before separately certifying any Stage 2 width or choosing paired versus solo. |
| G41 | Does current operational evidence select paired-mixture or standalone success as E2's primary target? | RoboArena's source protocol is natively paired and sequential, while top-1 specifies how many policies are chosen rather than their exposure. The public DROID reset homes the robot but does not establish scene restoration or washout. Paired-only outcomes do not identify standalone success without an independently justified bridge; the current recorded-action OSCAR evaluator is post-execution. | Open and branch-killing. Native pairing makes paired-mixture construct-aligned only if the actual use is the paired regime. Solo success is aligned if the chosen policy is deployed alone, but no owner-fixed record or live solo capacity exists. Stage 2 is NO-GO. | Obtain a signed/hashed outcome-blind owner decision record before using available infrastructure to test feasibility. Do not let paired access choose the estimand. A pre-execution selection or trial-savings claim also requires a pre-execution evaluator. |

## Factual architecture selected

P1 has one primary empirical claim and a bounded decision
case set:

1. In the frozen corpus, all codings identify a displayed panel and none a
   target population or probability-sampling mechanism. Five papers report a
   coefficient p-value, one an interval, and twenty neither.
2. SIMPLER is a positive finite-panel case: a declared equal-task aggregate
   selects the real winner, while individual tasks expose heterogeneity.
3. Real2Sim is a tie-complete negative finite-panel case: a high correlation
   can select the wrong policy under a source-aligned checkpoint rule; a
   non-winning tie changes \(r\) but not the decision.
4. OSCAR and Cosmos-Surg provide separately sourced negative cases
   using different sources and policy rosters.
5. The inventory-derived direct-cell matrix ledger contains all 19 recovered
   matrices; WorldGym and Digital Cousins are post hoc stable agreement cases.
6. A Practical Recipe is an independent source-rank case: three printed panels
   disagree on top-1, but the available ranks do not identify absolute regret.

These cases do not estimate how often simulators make wrong choices. Together
they establish that a coefficient’s decision meaning must be named and checked
rather than inferred from its magnitude.

## Remaining external blockers

No remaining external gap blocks the bounded combined paper. The following
stronger results are unavailable from present evidence:

- field-wide prevalence from a systematic search;
- population-level selection error or calibrated correlation threshold;
- causal comparison of simulator families;
- exact rerunning of most source robot experiments;
- causal diagnoses for conflicting source displays;
- absolute regret for A Practical Recipe’s rank panels.

The correct disposition is to omit those stronger claims, not add speculative
defenses.

## Evidence-first research decision after P1 closure

Date: 2026-07-26

This section records the next research questions without changing the
manuscript or treating their prospective value as evidence that their answers
will be favorable.

1. **Field prevalence remains unidentified.** G01 controls the present
   evidence: the 26-paper roster has neither a complete field denominator nor
   known inclusion probabilities. A defensible extension would be a separate
   bounded publication-frame study with a complete frame or positive sampling
   probability in every stratum, independent screening/coding, explicit
   missingness bounds, and design-based uncertainty. No reanalysis of the
   existing roster can repair this denominator.
2. **Causal simulator validity remains unidentified.** The present panels do
   not identify intervention-effect preservation, causal-surrogate validity,
   the effect of using a simulator-guided workflow, or the effect of improving
   a simulator component. The existing evidence can support only fixed-panel
   evaluator-substitution contrasts. A causal extension requires randomized
   matched interventions or a prospective shadow-decision design with sealed
   real outcomes.
3. **The universal-threshold theory question is closed negatively.** No
   distribution-free Pearson cutoff below one guarantees correct top-1
   selection once at least three candidates are allowed. Correlation can be
   translated into a retrospective panel-specific regret certificate using
   observed real dispersion and simulator margins, but the generic bound is a
   specialization of prior squared-loss-to-decision-risk theory. Proof,
   literature collision, source-resolution computation, and independent
   mathematical/implementation challenges are recorded under
   `../decision-validity/`.
4. **The complete evaluator-substitution census is closed descriptively.**
   Every retained numeric source has a disposition. Five exact fixed-target
   absolute groups and two rank-only groups retain stable cases, reversals,
   block/rank sensitivity, and structural exclusions. The challenged result is
   exploratory finite-panel sensitivity, not prevalence, causality,
   calibration, or evaluator superiority.
5. **The planned prospective E2 action still requires operational
   confirmation, and its honest complete-block confidence baseline is now
   sharper but still expensive.** Three
   independent domain challenges found that pairwise preference/Borda and
   worst-retained-set regret may not match a top-1 task-success deployment
   action. Per-policy binary success requires marginal policy positivity under
   known randomized assignment; the current 21-pair-by-stratum saturation
   rule is an estimator-specific refusal, not a universal identification law.
   The pairwise common-grid activation is stopped. The independently
   challenged Stage 0 fork now verifies the exact estimator identities,
   construct reversal, nonuniform randomization checks, and support burden,
   but it does not choose the operational action or an enrollment. The
   independently reviewed Stage 1 now verifies exact HT covariance identities
   and a finite-sample Hoeffding--Bonferroni all-contrast band for the
   no-interference marginal-success branch. The band covers every enumerated
   K=3 binary table but is vacuous at small scale. Under seven policies, eight
   equal target strata, and complete forced-balanced blocks, its sufficient
   five-point-radius count is 113,232 sessions. The independently challenged
   Stage 2A uses sharp outcome-free forced-permutation variance and centered
   caps with a classical Bernstein inequality, reducing the corresponding
   sufficient count to 11,088 sessions. This is a conservative analytic-width
   result, not power or an enrollment recommendation. Further reduction
   requires a separately proved Stage 2B method, a narrower estimand/claim, or
   new design information; it cannot be obtained by substituting an
   unvalidated interval.
6. **Causal scope remains separated from predictive validity.** A randomized,
   outcome-sealed shadow study can estimate local fixed-roster policy-success
   contrasts and evaluator decision validity. It does not estimate the causal
   effect of adopting an evaluator or robot-trial savings. That requires a
   later equal-budget strategy-level randomized trial with a pre-execution
   evaluator; OSCAR's recorded-action replay cannot supply it.

Manuscript editing remains paused. Research artifacts and independent
challenges must stabilize before any paper-facing claim is reconsidered.
