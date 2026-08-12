# Source-discrepancy closure matrix

Date: 2026-07-24

Purpose: test whether each result-changing source discrepancy has a benign
published reconstruction. This consolidates existing source checks; it does
not infer causes.

| case | declared alternative grid | outcome | closure |
|---|---|---|---|
| Real2Sim MMRV | 60 combinations of tie inequality, XOR rule, real/simulator gap side, and normalization | Exactly one convention reproduces all six Table I/Figure 9 values: simulated-side gap, XOR ordering violation, divide by N. The v1→v2 source changes MMRVs while correlation figures remain unchanged. | Numerical semantics closed; “bug” motive remains conditional on unarchived author communication. |
| Real2Sim T count | 12 versus 15 points; vector marker count, coefficient/MMRV lattice, Figure 4 schedules, Figure 10 replay context | Figure 3/Table I requires 15; 12 is the separate replay subset. | Closed. |
| SIMPLER MMRV documentation | executable/paper `(sim, real)` versus README/docstring `(real, sim)` | The executable/paper reproduces official numbers; documentation order gives materially different asymmetric MMRV. | Closed as a documentation defect; source results unchanged. |
| WEAVER | Pearson versus Spearman over recovered displayed points | Recovered Pearson is .863; Spearman is .870, matching the advertised value. | Metric-label mismatch closed; no claim about implementation cause. |
| WorldEval headline | pooled 20-cell Pearson versus mean of task-level correlations | Pooled reconstruction is .926; printed .942 matches the mean-of-task estimand. | Estimand identity closed. Other task/figure inconsistencies remain source-blocked. |
| WM-PolicyEval real-world panels | printed legend coefficients versus recovered plotted cells and policy means | Neither straightforward pooled displayed-cell reconstruction nor policy-mean aggregation reproduces every printed legend value; winner calculations use the displayed coordinates and are labeled recovered. | Observation closed; authoritative raw matrix/plotting data still required for cause. |
| RoboSnap | vector figure versus inline table, plus source-owner clarification | The vector markers reproduce (r=.9089), while the inline table reproduces the reported (r=.887). A reply signed by RoboSnap coauthor Shujie confirms that the table contains the experimental values and was used for the reported coefficient; the markers were positioned manually in PowerPoint for presentation. | Closed: use the inline table as the numerical source of record. The independent figure extraction remains a presentation-geometry audit; top-1 is unchanged. |
| REALM V-VIEW | printed coefficient versus visible point geometry/alternative panel membership | Checked visible alternatives do not uniquely reproduce the label. | Source-blocked; excluded from any claim requiring exact numeric identity. |
| OSCAR denominator | printed bar lattice versus 63-session-per-policy released video tree | Printed WM rates lie on a 65-session lattice; the release contains 63 paired videos per policy and no canonical outcome table. | Discrepancy confirmed; two sessions and outcome rows remain externally blocked. |
| Cosmos manual denominator | 10 states, three generated seeds/state, two raters versus recovered 1/60 bar grid | Official protocol supports the 60-label structure. | Denominator closed at aggregate level; state/seed/rater dependence remains blocked. |

## Rule used

A discrepancy is:

- **closed** when one documented source convention reproduces all relevant
  values or an independent source passage resolves the identity;
- **nonfatal** when every visible alternative gives the same permitted
  decision but not the same number;
- **source-blocked** when no published alternative uniquely resolves the
  result and raw source-of-record rows are unavailable.

Source-blocked cases are omitted from headline numerical claims or labeled with
their recovery grade. This is stronger than choosing the most convenient
reconstruction and weaker than author-confirmed causal diagnosis.

## RoboSnap source-owner clarification

On 2026-08-12, the user supplied the body of an email reply signed by RoboSnap
coauthor Shujie. Shujie stated that the scatter plot was intended primarily as
a visual reference to the (y=x) line, that its markers were placed manually
in PowerPoint while adjusting the visual and colors, that the inline table
contains the experimental values, and that the reported (r=.887) was
computed from that table. The user subsequently reported replying to the
message.

This is a source-owner account of the plotting and calculation path. The
message body was supplied in the research task; the respondent's surname, raw
headers, and the original mailbox object were not independently established or
retained here. The causal
account is therefore author-confirmed personal communication, while the two
numerical coefficients remain independently reproduced from the pinned paper.
No finite-panel decision, corpus count, or headline conclusion changes.
