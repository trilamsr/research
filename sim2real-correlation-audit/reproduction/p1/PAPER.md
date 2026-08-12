# What Does a Sim-to-Real Correlation Support?
## A Bounded 26-Paper Reporting Audit and Decision-Level Reanalysis

**Tri Lam - 6 August 2026**

## Abstract

Sim-to-real correlation is often used to support robot-policy evaluation, but
the practical question is whether acting on an evaluator selects an acceptable
real policy. A coefficient describes association among its entering points; it
does not specify the action, loss, or transport to new policies and tasks. We
audit 26 papers and find finite displayed panels in all 26; none defines a
target population or probability-sampling mechanism.

In this non-systematic set, top-1 decisions agree in 17 of 19 complete
matrices. Real2Sim's
checkpoint-selection aggregate has $r=.878$--$.947$ but selects a different
policy, with 12.5 percentage points of displayed real regret. Equal task
weighting for Cosmos-Surg gives $r=.883$, Spearman $\rho=.371$, a different
winner, and 10.0 points of regret. OSCAR's plotted values give $r=.855$ with a
1.1-point argmax difference, but its axes come from different evaluation pools
and its uncertainty cannot be reconstructed. Rank-aware companion metrics add
useful evidence but do not specify the downstream action, acceptable loss, or
real-test budget.

High correlation can coexist with task disagreement, reversed checkpoint
selection, and metric-implementation discrepancies. Correlation alone does not
determine winner agreement or regret.

## 1. Introduction

Real-robot evaluation is expensive, so simulation, learned world models, and
video evaluators are increasingly used to rank policies before deployment.
The consequential act is usually not reporting a coefficient; it is retaining,
testing, or deploying a policy because of that coefficient. Correlation between
simulated and real performance is relevant to that use, but three different
claims are often left entangled:

1. simulated and real scores are associated for the displayed points;
2. that association extends to new policies, tasks, sites, or sessions; and
3. selecting by simulation produces an acceptable real-world decision.

The first claim is descriptive. The second requires a target population and a
design or model linking the observed panel to that population. The third
requires a decision rule and loss. A high coefficient can coexist with a
ranking reversal near the top because Pearson correlation summarizes average
linear association rather than winner identity or decision regret.

Prior work has examined sim-to-real predictivity, repeated-observation
correlation, and reliable reinforcement-learning evaluation [1-5]. Recent
robotics systems have made simulation-based evaluation more capable and
reproducible [6-10]. Policy selection under uncertainty, top-k regret, and
downstream regret are also established ideas [33-35]. We apply them to ask:

> What does a reported sim-to-real coefficient support for a specified target,
> selection rule, and loss?

We contribute:

- a framework separating association, finite-panel action, population
  transport, and decision acceptability;
- an audit of 26 papers' correlation claims and a 19-case decision ledger;
- task-composition and measurement sensitivities;
- a reconstruction of six Real2Sim MMRV values; and
- a reporting checklist for future evaluations.

## 2. Association, population, and decision

Let $Y_i^R$ and $Y_i^S$ be real and simulated scores for displayed unit
$i$ in panel $\mathcal P$. The Pearson coefficient

$$
r_{\mathcal P} =
\frac{\sum_{i\in\mathcal P}(Y_i^R-\bar Y^R)(Y_i^S-\bar Y^S)}
{\sqrt{\sum_{i\in\mathcal P}(Y_i^R-\bar Y^R)^2}
\sqrt{\sum_{i\in\mathcal P}(Y_i^S-\bar Y^S)^2}}
$$

is a property of that displayed panel. The index $i$ may represent policies,
checkpoints, tasks, conditions, or a product of axes. A population correlation
requires a target distribution over the relevant units and a defensible link
from the observed panel to that distribution.

A policy-selection decision requires different quantities. For candidate set
$\mathcal A$, define the displayed real and simulated winner sets as

$$
R=\arg\max_{a\in\mathcal A}Y_a^R,\qquad
S=\arg\max_{a\in\mathcal A}Y_a^S.
$$

Selection is possibly correct when $R\cap S\neq\varnothing$, and robustly
correct when every simulated maximizer is a real maximizer,
$S\subseteq R$. Displayed real regret for selected policy $a$ is

$$
\max_{b\in\mathcal A}Y_b^R-Y_a^R.
$$

These definitions preserve ties and expose the decision consequence. They do
not convert a convenience panel into a policy population.

WorldGym illustrates why the axes cannot be collapsed into one effective
sample size. Its Figure 4a contains three policies repeated across 17 tasks,
giving 51 policy-task cells and reporting $r=.78,p<.001$ [10]. The policy
axis has three blocks and the task axis has 17; each supports a different
question and exchangeability argument.

\begin{center}
\begin{minipage}{.72\linewidth}
\centering
\includegraphics[width=\linewidth]{research/claim-evidence-synthesis/figure-worldgym-axis-validity.pdf}

\small Figure 1: The same 51 cells support distinct policy- and task-axis questions.
\end{minipage}
\end{center}

The evidence required depends on the claim being made:

\small
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.20\linewidth}
>{\raggedright\arraybackslash}p{0.29\linewidth}
>{\raggedright\arraybackslash}p{0.43\linewidth}@{}}
\hline
\textbf{claim} & \textbf{minimum object} & \textbf{what remains unresolved} \\
\hline
Displayed-panel association & Paired real and simulated values, metric
definition, and unit identity & Which policy an evaluator selects and the
real loss of that choice \\
Finite-panel decision & Candidate set, aggregation and selection rule, ties,
real winner set, and loss & Performance for new policies, tasks, sites, or
sessions \\
Population transport & Target population plus a sampling, assignment, or
predictive model linking it to the panel & Whether the resulting decision is
acceptable for the intended use \\
Decision acceptability & Named action, loss, tolerance, uncertainty, and
downstream real-test budget & Broader uses not covered by the declared target
and tolerance \\
\hline
\end{longtable}
\normalsize

Passing an earlier row does not pass a later one. Conversely, a useful
finite-panel result need not make a population claim if its action and boundary
are explicit.

## 3. Methods

### 3.1 Corpus and coding

We included 26 papers that evaluated robot policies, checkpoints, or variants
with aligned simulated and real outcomes and printed a named association
coefficient. The corpus is non-systematic. We coded each claim's units, target,
transport basis, checkpoint selection, and coefficient uncertainty.

### 3.2 Numeric data

We extracted numeric results for 19 papers from source data, tables, or figures
and checked figure-derived values against reported statistics where possible.
Matching a reported coefficient checks extraction, not the underlying
experiment. We label figure-derived values and do not infer missing trial
counts.

### 3.3 Decision atlas

For 19 complete matrices, we preserved source-defined rules where available;
otherwise we weighted displayed tasks equally, retained ties, and computed
displayed real regret. The resulting top-1 rule agrees in 17 cases and
disagrees in two.

### 3.4 Task composition and real-trial remeasurement

We test all displayed-task subsets and leave-one-task-out aggregates; these do
not represent future-task probabilities. Where real trial counts are known,
independent Beta(1,1) models estimate winner uncertainty. Missing simulator
counts and dependence are handled by sensitivity analysis.

\newpage

## 4. Reporting audit

\small
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.32\linewidth}
>{\raggedleft\arraybackslash}p{0.15\linewidth}
>{\raggedright\arraybackslash}p{0.45\linewidth}@{}}
\hline
\textbf{result} & \textbf{count} & \textbf{interpretation boundary} \\
\hline
Included papers & 26 & non-systematic corpus \\
Complete numeric matrices & 19/26 & source- and figure-derived \\
Finite displayed panel & 26/26 & all audited papers \\
Defined target population or sampling mechanism & 0/26 & none reported \\
Coefficient uncertainty & 5 p; 1 CI; 20 neither & p-values test a null rather than quantify magnitude uncertainty \\
Checkpoint or model state selection (yes/no/N/A) & 8 / 17 / 1 & disclosed in eight papers \\
Fewer than ten policy or checkpoint blocks & 23--25/26 & range reflects ambiguous reporting \\
\hline
\end{longtable}
\normalsize

No paper defines a target population or probability-sampling mechanism,
although some make model-based transport arguments. Several papers report
held-out prediction, but none defines a future-policy or future-task
distribution with calibrated population-level uncertainty. Most reports also
do not define the test or exchangeability unit needed for a common inferential
interpretation.

## 5. Correlation and displayed decisions

Figure 2 compares illustrative agreement and disagreement cases at nearby,
often high correlations. It is not a prevalence sample; the complete 19-case
ledger appears in the supplement.

\begin{center}
\includegraphics[width=\linewidth]{research/claim-evidence-synthesis/figure-decision-atlas.pdf}

\small Figure 2: Illustrative cases: similar correlations can yield agreement
or disagreement. Labels show displayed real regret. Cases use different units
and aggregation rules and are not directly comparable.
\end{center}

\newpage

\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.21\linewidth}
>{\raggedleft\arraybackslash}p{0.10\linewidth}
>{\raggedright\arraybackslash}p{0.17\linewidth}
>{\raggedright\arraybackslash}p{0.18\linewidth}
>{\raggedleft\arraybackslash}p{0.11\linewidth}
>{\raggedleft\arraybackslash}p{0.08\linewidth}@{}}
\hline
\textbf{case} & \textbf{\(r\)} & \textbf{sim best} &
\textbf{real best} & \textbf{regret} & \textbf{LOTO} \\
\hline
WorldGym & .992 & OpenVLA & OpenVLA & 0 & 17/17 \\
Digital Cousins & .997 & \(\pi_0\) & \(\pi_0\) & 0 & 4/4 \\
SIMPLER Google & .974 & RT-1-converged & RT-1-converged & 0 & 5/5 \\
Real2Sim T (best-sim) & \(\mbox{.878--.947}\) & \(\pi_0\) & DP & 12.5 pp & -- \\
OSCAR Skeleton & .855 & PG-FAST+ & pi0-FAST & 1.1 pp & -- \\
Cosmos-Surg manual & .883 & GR00T N1.5 50k & GR00T N1 20k & 10.0 pp & 0/4 \\
WM-PolicyEval Cosmos & .975 & OpenVLA & OpenVLA & 0 & 4/4 \\
WM-PolicyEval IRASim & .507 & Octo-Base & OpenVLA & 27.5 pp & 1/4 \\
\hline
\end{longtable}

LOTO counts robustly correct leave-one-task-out aggregates. WorldGym reports a
pooled-cell $r=.78$; equal policy averaging gives $r=.992$. For Cosmos-Surg,
equal task weighting gives $r=.883$; averaging by training lineage gives
$r=.905$, $\rho=.500$, and 3.7 points of displayed regret. Real2Sim's tie
changes $r$ but not the selected winner or regret. Rank-aware metrics reveal
additional disagreement but do not define the action, loss, tie rule, or
evaluation budget.

Aggregate agreement can conceal task disagreement: SIMPLER Google has
$r=.974$ and an equal-task winner match, but only 3/5 task winners agree.
The evaluation rule can also reverse the result: Real2Sim rope moves from
$r=.901$ over all checkpoints to $r=-.683$ after best-simulated checkpoint
selection. Figure 2 shows that nearby coefficients can therefore support
different actions.

### 5.1 Agreement cases

WorldGym and Digital Cousins retain the correct winner under every single-task
deletion and nearly or fully all task subsets. SIMPLER Google also retains its
aggregate winner after every deletion, although only 3/5 task winners agree
[6,13]. These examples show stable agreement on their displayed tasks.

### 5.2 Disagreement cases

Real2Sim motivates simulation for checkpoint selection [7]. Selecting each
policy's best displayed simulated checkpoint in the T block chooses $\pi_0$
instead of the real winner DP, with 12.5 points of displayed regret. An SVLA
checkpoint tie changes $r$ from .878 to .947 but not the decision. Across
three tasks and three tie-complete rules, seven of nine disagree, one agrees,
and one depends on tie handling.

OSCAR's plotted values give $r=.855$ [29]. PG-FAST+ wins on the world-model
axis and pi0-FAST on the real axis, a 1.1-point near-tie. The axes use different
evaluation pools (65 versus 63 sessions), preventing uncertainty
reconstruction. Its printed Spearman $\rho=.750$ and MMRV $=.571$ are not
jointly reproducible from the displayed bars under the published metric
definitions; the required per-policy rank inputs were not released.

Cosmos-Surg's equal-task aggregate selects GR00T N1.5 50k in simulation and
GR00T N1 20k in reality, with 10.0 points of regret [18]. Every single-task
deletion retains the mismatch. Real outcomes use ten trials per policy-task,
without released dependence information.

WM-PolicyEval changes the decision when only the evaluator changes [31].
Cosmos selects the real winner OpenVLA at $r=.975$; IRASim selects Octo-Base at
$r=.507$, producing 27.5 points of regret. The plotted points reproduce the
appendix values despite an inconsistent IRASim legend, and label-order
ambiguity does not change either decision. Simulator counts are unstated.

In *A Practical Recipe*, simulated and real top-1 disagree in 3/11 printed
rank panels; absolute regret cannot be recovered [9].

## 6. Robustness to measurement and task composition

\begin{center}
\includegraphics[width=\linewidth]{research/claim-evidence-synthesis/figure-decision-robustness.pdf}

\small Figure 3: Model and task-composition sensitivities, not calibrated
evaluator reliability.
\end{center}

Holding the simulator winner fixed, the Beta-binomial model gives Cosmos-Surg
.087 winner concordance and 11.6 points of expected regret. A two-sided
sensitivity gives .207--.220 concordance and 8.36--9.65 points of regret;
dependence is not identified.

Because WM-PolicyEval omits simulator rollout counts, sensitivity ranges are
.333--.9999 for Cosmos and .0001--.432 for IRASim. Policy-specific evidence can
reverse IRASim toward OpenVLA; the unknown counts and dependence prevent a
reliability estimate.

Both WM evaluators underpredict real success. Positive-slope affine
recalibration lowers error without changing rankings. An in-sample isotonic fit
changes IRASim's winner to OpenVLA but uses the same outcomes for fitting and
evaluation, so it is only a shape sensitivity.

Task-subset results answer a different robustness question. WorldGym and
Digital Cousins remain correct under every leave-one-task-out deletion.
Cosmos-Surg manual remains wrong after every deletion. WM-PolicyEval/IRASim is
composition-sensitive, becoming robustly correct in one of four
leave-one-task-out aggregates. A second deletion is only possibly correct:
the simulated winner set ties a real winner with a non-winner. Thus full-panel
top-1 alone does not distinguish stable agreement from a
composition-dependent result, and tie handling can matter.

## 7. Metric semantics and numerical provenance

Real2Sim's Figure 3 correlations reproduce within .0004. Treating one
coincident rope marker as one or two points changes $r$ but not any top-1
conclusion.

One tested convention reproduces all six Real2Sim MMRV values: ordering
disagreement weighted by the simulated-side gap and divided by $N$ [6].

## 8. Data and code availability

Data and code are provided with this article.
Project materials and checklist:
<https://github.com/trilamsr/research/tree/main/sim2real-correlation-audit>.

## 9. Reusable decision audit and reporting standard

The accompanying checklist covers the decision, data, sensitivities, target,
loss tolerance, and real-test budget.

## 10. Limitations

This non-systematic 26-paper corpus cannot estimate field prevalence and is
concentrated in recent manipulation and world-model evaluation. Figure-derived
values remain subject to raster resolution, overlapping marks, source
revisions, and unlabeled points despite matching reported coefficients.

The cases differ in robots, tasks, candidates, aggregation, source quality, and
loss. They do not identify a universal threshold or population selection-error
rate. Real-trial estimates are model-conditional; missing simulator counts and
dependence limit their interpretation. Task-subset results describe displayed
tasks, not future-task probabilities.

Missing target or uncertainty information limits inference; it does not imply
evaluator failure.

## 11. Conclusion

A sim-to-real correlation is a property of a displayed panel. The audited
cases show that similar, often high coefficients can accompany different
winners and losses under named decision rules. Measurement and task-composition
sensitivities then answer distinct questions; neither creates a population
claim from a finite panel.

Correlation remains useful evidence of association. It becomes actionable only
with a defined target, decision rule, and loss tolerance; estimated outcomes
also require decision-relevant uncertainty.

## Author and declarations

Tri Lam conceived the audit, curated the records, implemented the analyses,
and wrote the manuscript. No conflicts of interest are declared. The paper is
a retrospective public-record audit and reports no new human- or animal-subject
experiment.

# References

\small

1. Kadian A, Truong J, Gokaslan A, et al. *Sim2Real Predictivity: Does
   Evaluation in Simulation Predict Real-World Performance?*
   arXiv:1912.06321, 2019.
2. Henderson P, Islam R, Bachman P, Pineau J, Precup D, Meger D. *Deep
   Reinforcement Learning that Matters.* arXiv:1709.06560, 2017.
3. Agarwal R, Schwarzer M, Castro PS, Courville AC, Bellemare MG. *Deep
   Reinforcement Learning at the Edge of the Statistical Precipice.*
   arXiv:2108.13264, 2021.
4. Bland JM, Altman DG. Calculating correlation coefficients with repeated
   observations: Part 2 - correlation between subjects. *BMJ*. 1995;310:633.
5. Kish L. *Survey Sampling.* Wiley; 1965.
6. Li X, Hsu K, Gu J, et al. *Evaluating Real-World Robot Manipulation
   Policies in Simulation.* arXiv:2405.05941, 2024.
7. Zhang K, Sha S, Jiang H, et al. *Real-to-Sim Robot Policy Evaluation with
   Gaussian Splatting Simulation of Soft-Body Interactions.*
   arXiv:2511.04665v2, 2025.
8. Jeon B, Ye S, Doo J, et al. *RoboWorld: Fast and Reliable Neural
   Simulators for Generalist Robot Policy Evaluation.*
   arXiv:2607.01060v4, 2026.
9. Wang S, Xu H, Hu Y, Lin F, Gao Y. *A Practical Recipe Towards Improving
   Sim-and-Real Correlation for VLA Evaluation.* arXiv:2606.10366v1, 2026.
10. Quevedo J, Sharma AK, Sun Y, et al. *WorldGym: World Model as An
    Environment for Policy Evaluation.* arXiv:2506.00613v3, 2025.
11. Good PI. Extensions of the concept of exchangeability and their
    applications. *Journal of Modern Applied Statistical Methods*. 2002;1(2).
12. Phipson B, Smyth GK. Permutation p-values should never be zero.
    *Statistical Applications in Genetics and Molecular Biology*. 2010;9(1).
13. Lu J, Shen Z, Wang Y, et al. *From Seeing to Simulating: Generative
    High-Fidelity Simulation with Digital Cousins for Generalizable Robot
    Learning and Evaluation.* arXiv:2604.15805, 2026.
14. Zhang S, Yi J, Zhong W, et al. *RoboSnap: One-Shot Real-to-Sim Scene
    Generation for Generalizable Robot Learning and Evaluation.*
    arXiv:2607.06699, 2026.
15. Jain A, Zhang M, Arora K, et al. *PolaRiS: Scalable Real-to-Sim
    Evaluations for Generalist Robot Policies.* arXiv:2512.16881, 2025.
16. Tseng W-C, Hussein G, Dong Y, et al. *SC3-Eval: Evaluating Robot
    Foundation Models via Self-Consistent Video Generation.*
    arXiv:2606.18610, 2026.
17. Li Y, Zhu Y, Wen J, et al. *WorldEval: World Model as Real-World Robot
    Policies Evaluator.* arXiv:2505.19017, 2025.
18. Zbinden L, Nelson N, Chen J-T, et al. *Cosmos-Surg-dVRK: World
    Foundation Model-based Automated Online Evaluation of Surgical Robot
    Policy Learning.* arXiv:2510.16240, 2025.
19. Gemini Robotics Team, Choromanski K, Devin C, et al. *Evaluating Gemini
    Robotics Policies in a Veo World Simulator.* arXiv:2512.10675, 2025.
20. Gao S, Liang W, Zheng K, et al. *DreamDojo: A Generalist Robot World
    Model from Large-Scale Human Videos.* arXiv:2602.06949, 2026.
21. Li Y, Zhou Z, Chen Y, et al. *dWorldEval: Scalable Robotic Policy
    Evaluation via Discrete Diffusion World Model.* arXiv:2604.22152, 2026.
22. Jain AK, Wu Y, Farebrother J, et al. *WEAVER, Better, Faster, Longer: An
    Effective World Model for Robotic Manipulation.* arXiv:2606.13672, 2026.
23. Yin T, Mei Z, Zheng Z, et al. *PlayWorld: Learning Robot World Models
    from Autonomous Play.* arXiv:2603.09030, 2026.
24. Chhablani G, Ye X, Irshad MZ, Kira Z. *EmbodiedSplat: Personalized
    Real-to-Sim-to-Real Navigation with Gaussian Splats from a Mobile
    Device.* arXiv:2509.17430, 2025.
25. Kim Y, Pumacay W, Rayyan O, et al. *MolmoSpaces: A Large-Scale Open
    Ecosystem for Robot Navigation and Manipulation.* arXiv:2602.11337, 2026.
26. Zheng Z, Yu J, Peng X, et al. *Mem-World: Memory-Augmented
    Action-Conditioned World Models for Persistent Robot Manipulation.*
    arXiv:2606.18960, 2026.
27. Morgan J, Vijay P, Oh H, et al. *Colosseum V2: Benchmarking
    Generalization for Vision Language Action Models.* arXiv:2605.27759, 2026.
28. Zhu Y, Wang Z, Yang J, et al. *Toward Visually Realistic Simulation: A
    Benchmark for Evaluating Robot Manipulation in Simulation.*
    arXiv:2605.06311v1, 2026.
29. Wu Z, Gao J. *OSCAR: Omni-Embodiment Action-Conditioned World Model for
    Robotics.* arXiv:2606.04463v2, 2026.
30. Li Y, Zhou Z, Chen Y, et al. *Hi-WM: Human-in-the-World-Model for
    Scalable Robot Post-Training.* arXiv:2604.21741v2, 2026.
31. Tseng W-C, Gu J, Zhang Q, et al. *Scalable Policy Evaluation with Video
    World Models.* arXiv:2511.11520v3, 2025.
32. Ranawaka N, Wong J, Pai W-L, et al. *SimFoundry: Modular and Automated
    Scene Generation for Policy Learning and Evaluation.*
    arXiv:2606.28276, 2026.
33. Yang M, Dai B, Nachum O, Tucker G, Schuurmans D. *Offline Policy
    Selection under Uncertainty.* Proceedings of AISTATS, PMLR
    151:4376-4396, 2022.
34. Zhang Z, Chen R, Ye J, et al. *WHALE: Towards Generalizable and Scalable
    World Models for Embodied Decision-making.* arXiv:2411.05619v1, 2024.
35. Nakamura K, Tian T, Bajcsy A. *Not All Errors Are Made Equal: A Regret
    Metric for Detecting System-level Trajectory Prediction Failures.*
    Proceedings of CoRL, PMLR 270:4051-4065, 2025.
