# Blind coder B notes

Coding was performed only from the coding protocol (now
`../protocol-corpus-coding.md`) and pinned primary-source files in an ephemeral
clean-room checkout. No repository paper, README, implementation, released
grid, tests, or prior audit notes were consulted. The checkout path was not a
retained dependency: stable source identities and extraction traces are
recorded in the corresponding `source-<paper>.csv` headers in this directory.

## Main ambiguities preserved

- **MolmoSpaces:** Figure 11 labels `R` and its caption calls it a coefficient of determination, while §5.2 calls the same 0.96 quantity a Pearson correlation coefficient. I preserved the reported values and flagged the nomenclature rather than silently converting or squaring them. The exact Open/Close policy counts are not enumerated in the text and remain `?`.
- **Cosmos-Surg-dVRK:** the pooled manual and automated headline correlations are clear, but the exact number of pooled policy/training-regime points is not stated. Three generated seeds are averaged within policy-task cells and were not recoded as training runs.
- **PlayWorld:** the headline figure says the panel crosses diverse policy architectures, training mixtures, and tasks, but the text does not enumerate the plotted cell count or lineage structure. Those counts remain `?`.
- **dWorldEval:** figure-only values were visually checked. LIBERO panels resolve to five checkpoints by three suites; RoboTwin and physical-real panels do not textually enumerate every plotted cell, so their displayed-point/task counts remain `?`.
- **Real2Sim:** the appendix explicitly gives 16/15/12 checkpoint counts for the three tasks. These are checkpoints, not evidence of 16/15/12 independent training runs. The main correlation has no correlation-level interval; Clopper–Pearson intervals discussed for success rates were not counted as uncertainty on `r`.
- **SIMPLER:** the Bridge value 0.890 is explicitly a mean of per-task correlations. The Google drawer aggregate in Table I differs structurally from separate Open/Close values in Table IV/Figure 6; the row identifies which aggregate it codes.
- **SimFoundry and PolaRiS:** headline averages are means of task/environment-specific policy correlations, not pooled cell-level coefficients.
- **A Practical Recipe:** proxy correlations average dimension-specific five-policy coefficients after task aggregation, whereas sensitivity correlation flattens policy-by-dimension sensitivity cells. These were coded as materially different estimands.
- **EmbodiedSplat:** the two four-point coefficients are printed inside Figure 1 and were visually inspected. The paper calls them SRCC, but the nearby passage does not fully specify the formula.
- **OSCAR:** 65 sessions were manually retained and then aggregated to seven per-policy means; the coefficient therefore has seven points, not 455 independent coefficient rows.
- **Colosseum V2:** the 0.916 statistic is an average of three task-specific Spearman correlations over perturbation conditions, not one pooled 18-point coefficient.
- **Target-population support:** no paper in this coding defined both a target superpopulation/sampling mechanism and axis-appropriate correlation uncertainty for new-policy, new-task, or crossed inference. All such population-inference fields are therefore conservatively coded `unsupported`, while finite displayed panels are coded `yes`.

## Counting conventions

- `policy_models` counts named displayed variants/checkpoints when those are the coefficient rows; `base_lineages` collapses clearly shared checkpoint families only when the primary source makes that relationship explicit.
- `training_runs` is `?` unless separately trained runs are explicitly documented for the coefficient. Evaluation seeds, generated-video seeds, sessions, episodes, and checkpoints were never substituted for training runs.
- For mean-of-correlations, `displayed_points` records the total underlying paired values across the component correlations, while `coefficient_axis` records `mean-of-correlations`.
- Repeated trials/sessions that are averaged before correlation are recorded under `conditions` when useful, but are not treated as coefficient points.
