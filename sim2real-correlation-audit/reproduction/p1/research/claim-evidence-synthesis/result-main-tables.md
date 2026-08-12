# Generated main-paper tables

Generated factual cells come from `research/claim-evidence-synthesis/result-paper-evidence.json`. Explanatory cells implement the locked rewrite specification.

## Table 1. Three layers of a correlation audit

| layer | question | evidence to report | boundary when absent |
|---|---|---|---|
| Identification | What finite panel does the coefficient describe? | displayed points, axes, aggregation | coefficient scope is ambiguous |
| Identification | What population or decision is the result meant to address? | target population or named finite-panel decision | population inference is unidentified |
| Identification | How did models, checkpoints, tasks, and conditions enter? | selection rule for every coefficient axis | selection sensitivity is unknown |
| Robustness | Does one relevant unit carry the coefficient? | continuous leave-unit-out values and deletion unit | finite-panel composition sensitivity is hidden |
| Robustness | Does an alternate decision-relevant estimand change the conclusion? | prespecified alternate aggregation or selection | one coefficient may answer the wrong decision |
| Reproduction | Can a reader recompute the coefficient and metric? | paired values, metric code, conventions, provenance | numerical agreement cannot be independently checked |

## Table 2. Results of the bounded 26-paper audit

| result | count | evidence class | interpretation boundary |
|---|---:|---|---|
| Included papers | 26 | adjudicated corpus ledger | 22-paper pre-Search-3 roster plus four fully logged Search-3 additions; not a census |
| Papers with recovered numeric results | 19 | per-paper recovery ledger | recovery modes and validation gates differ |
| Finite displayed panel | 26/26 | three model-assisted internal coding passes | provisional pending independent human source-only recoding; descriptive panel existence, not independence |
| Defined target population or sampling mechanism | 0/26 | three model-assisted internal coding passes | provisional pending independent human source-only recoding; absence does not show the simulator fails |
| Design-based support under the original coding rule | 0/26 | three applications of the same construct | model-based and transport routes were not separately coded |
| Coefficient p-value | 5/26 | adjudicated observable reporting fact | does not quantify uncertainty in coefficient magnitude |
| Coefficient interval | 1/26 | adjudicated observable reporting fact | only interval estimate for coefficient magnitude |
| Neither p-value nor coefficient interval | 20/26 | adjudicated observable reporting fact | does not imply the coefficient is numerically wrong |
| Fewer than ten policy/checkpoint blocks | 23–25/26 | two explicit sensitivity codings | not a unique effective sample size |

## Table 3. Inventory-derived complete direct-cell matrices

| panel | source metric bundle | Pearson r | Spearman ρ | top-1 | regret | LOTO |
|---|---|---:|---:|---|---:|---:|
| Cosmos-Surg-dVRK/automated_fig1b | Pearson and MMRV | 0.941 | 0.829 | correct | 0.00 pp | 1/4 |
| Cosmos-Surg-dVRK/manual_human_vs_dvrk | Pearson and MMRV | 0.883 | 0.371 | wrong | 10.00 pp | 0/4 |
| Digital Cousins | Pearson | 0.997 | 1.000 | correct | 0.00 pp | 4/4 |
| EmbodiedSplat/mesh-conditions | Pearson | 0.936 | 0.800 | correct | 0.00 pp | 2/2 |
| Hi-WM | Pearson | 0.964 | 1.000 | correct | 0.00 pp | 3/3 |
| Mem-World | Pearson and p-value | 1.000 | 1.000 | correct | 0.00 pp | 5/5 |
| MolmoSpaces/common-appendix-roster | Pearson and Spearman | 0.982 | 0.800 | correct | 0.00 pp | 3/3 |
| REALM/Default | Pearson and MMRV | 1.000 | 1.000 | correct | 0.00 pp | 7/7 |
| REALM/Overall | Pearson and MMRV | 1.000 | 1.000 | correct | 0.00 pp | 7/7 |
| REALM/VB-POSE | Pearson and MMRV | 1.000 | 1.000 | correct | 0.00 pp | 3/7 |
| SIMPLER/google_robot | Pearson and MMRV | 0.974 | 1.000 | correct | 0.00 pp | 5/5 |
| SIMPLER/widowx | Pearson and MMRV | 0.950 | 1.000 | correct | 0.00 pp | 4/4 |
| WEAVER/CtrlWorld | Pearson and Spearman | 1.000 | 1.000 | correct | 0.00 pp | 5/5 |
| WEAVER/WEAVER | Pearson and Spearman | 1.000 | 1.000 | correct | 0.00 pp | 5/5 |
| WEAVER/WEAVER-FT | Pearson and Spearman | 1.000 | 1.000 | correct | 0.00 pp | 5/5 |
| WM-PolicyEval/Cosmos | Pearson and MMRV | 0.975 | 1.000 | correct | 0.00 pp | 4/4 |
| WM-PolicyEval/IRASim | Pearson and MMRV | 0.507 | 0.500 | wrong | 27.50 pp | 1/4 |
| WorldEval | Pearson | 0.996 | 0.800 | correct | 0.00 pp | 5/5 |
| WorldGym | Pearson and ranking-preservation analysis | 0.992 | 1.000 | correct | 0.00 pp | 17/17 |

All 19 recovered complete direct-cell matrices are shown: 17 displayed agreements and 2 disagreements. These outcome-exposed rows are not a calibration sample or prevalence denominator; their exact aggregation rules and source limitations are recorded in the supplement.

## Table 4. Real2Sim reproduction

| task | Figure 3 N | episodes/checkpoint | recovered r | printed r | exact recovered MMRV | printed MMRV |
|---|---:|---:|---:|---:|---:|---:|
| toy packing | 17 | 20 | 0.9444 | 0.944 | 13/170 (0.076471) | 0.076 |
| rope routing | 20 | 27 | 0.9007 | 0.901 | 47/270 (0.174074) | 0.174 |
| T-block pushing | 15 | 16 | 0.9147 | 0.915 | 13/120 (0.108333) | 0.108 |

Recovered convention: ≤-XOR (equivalently strict-> XOR), simulated-side gap, divide by N. It is the only joint match among the 48 distinct formulas in the declared 60-entry grid.

## Table 5. Core reporting standard

| requirement | minimum disclosure |
|---|---|
| Target | Name the finite panel, target population if any, and deployment decision. |
| Axes | State whether points vary over policies, runs, checkpoints, tasks, or conditions. |
| Selection | State how every entering model/checkpoint and any tie was selected. |
| Dependence | Aggregate or model repeated observations at the unit relevant to the claim. |
| Robustness and uncertainty | Report continuous leave-unit-out sensitivity and assumption-labeled uncertainty. |
| Reproduction | Release paired unit-level values, metric implementation, conventions, and provenance. |
