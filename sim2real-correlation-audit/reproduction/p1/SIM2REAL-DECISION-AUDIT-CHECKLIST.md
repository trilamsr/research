# Sim-to-Real Decision Audit Checklist

Use this form when a simulated or learned evaluator is proposed to rank,
screen, retain, reject, test, or deploy robot policies. It can be completed
for a finite benchmark without claiming a population result.

For each row record **yes**, **no**, **partial**, **unknown**, or **N/A**, plus an evidence
link or exact source location. A “no” is not automatically a failure; its
importance depends on the declared claim and action.

## Audit record

| field | entry |
|---|---|
| project / evaluator | |
| candidate version or content hash | |
| claim and intended action | |
| reviewer and role | |
| review date | |
| evidence-access boundary | public / controlled reviewer access / other: |
| overall status | exploratory / evidence adequate for stated finite-panel audit conclusion / blocked |
| unresolved blocking items | |
| decision owner / operator | |
| operational or deployment context | |
| reversibility and required domain/safety approval | |

## Core fields for any decision claim

### 1. Intended action and acceptance

| question | status | evidence / explanation |
|---|---|---|
| Is the action named: top-1, top-k screening, thresholding, pair routing, or another rule? | | |
| Is the candidate policy/checkpoint set fixed and identified? | | |
| Are aggregation, weights, selection, and ties specified? | | |
| Is the real-world loss or consequence of error specified? | | |
| Was an acceptance criterion prespecified (for example loss tolerance, safety constraint, abstention rule, or multiobjective requirement)? | | |
| Is the downstream real-test budget stated where screening is claimed? | | |

### 1A. Rule provenance

Record the value and provenance of every decision component. Use
`source-stated`, `source-aligned`, `audit-defined`, or `not applicable`.

| component | value | provenance | evidence / explanation |
|---|---|---|---|
| candidate set | | | |
| checkpoint/model-state collapse | | | |
| task or condition weights | | | |
| aggregation | | | |
| tie rule | | | |
| action | | | |
| loss | | | |
| metric direction, scale, and unit | | | |
| task-specific hard constraints | | | |
| tolerance / acceptance criterion | | | |
| real-test budget | | | |

### 2. Entering evidence and provenance

| question | status | evidence / explanation |
|---|---|---|
| Are paired simulated and real values released or available under controlled reviewer access? | | |
| Does each point have a stable policy, checkpoint, task, condition, and source identity? | | |
| Are model/checkpoint selection and all aggregation weights stated? | | |
| Are missing, excluded, duplicated, failed, and fallback observations documented? | | |
| Are real and simulated denominators and cluster identities stated? | | |
| Are per-point simulator rollout or label counts and their effective sampling units stated? | | |
| Are independent training-run, seed, and session counts—and any checkpoint nesting—identified on both axes? | | |
| Are source versions, files, table/figure locations, retrieval identities, and transformations recorded? | | |
| Does released code reproduce printed values, or is any discrepancy explicitly bounded? | | |
| Are source facts, audit calculations, interpretations, and personal communications visibly separated? | | |

### 2A. Robot/evaluator execution contract

For every simulated and physical side, record the value and mark the
cross-side relationship `same`, `mapped`, or `not comparable`.

| field | simulated / evaluator side | physical side | relationship and evidence |
|---|---|---|---|
| observation interface and preprocessing | | | |
| action interface, controller, and control frequency | | | |
| horizon, timeout, and termination semantics | | | |
| task definition and success/failure rubric | | | |
| reset, recovery, retry, and carryover procedure | | | |
| robot instance, site, calibration, and safety intervention | | | |
| policy, checkpoint, software, and controller revision | | | |

### 2B. Learned, VLM, or human evaluator construct validity

Complete this block whenever either side uses learned or human judgment.

| question | status | evidence / explanation |
|---|---|---|
| Are the simulated/evaluator and physical outcome constructs explicitly defined and comparable? | | |
| Are judge identity, model/version, prompt, decoding, rubric, and thresholds fixed and recorded? | | |
| Are unit-level labels, label provenance, missing/fallback judgments, and blinding available? | | |
| Is human validation or agreement reported on a relevant outcome-blind sample? | | |
| Do positive controls show the evaluator detects known meaningful changes? | | |
| Do irrelevant-channel, substitution, or nuisance interventions test whether the score changes for the wrong reason? | | |
| Are evaluator drift, nondeterminism, and retry/aggregation behavior measured? | | |

### 3. Displayed-panel decision

| question | status | evidence / explanation |
|---|---|---|
| Are simulated and real winner sets computed under the declared rule? | | |
| Is agreement classified with set-valued ties (possible, robust, or disagreement)? | | |
| Is displayed real loss reported for the simulated choice? | | |
| Does the conclusion survive justified tie alternatives? | | |
| Are task composition, checkpoint choice, and plausible weights stressed where decision-relevant? | | |
| Are operational utilities, asymmetric costs, and task-specific hard constraints distinguished from an illustrative equal-weight mean? | | |

### 4. Execution integrity

| question | status | evidence / explanation |
|---|---|---|
| Were tasks, evaluators, rubrics, and acceptance rules fixed before viewing the corresponding real outcomes? | | |
| Is outcome leakage or tuning on the same real panel ruled out or disclosed? | | |
| Were reported panels, metrics, rules, and thresholds selected from a larger outcome-exposed set? If so, are multiplicity and exploratory status explicit? | | |
| Are randomization, execution order, resets, washout, and carryover controls stated? | | |
| Are operator interventions, fallback paths, hardware/software revisions, and drift recorded? | | |
| Are intended paired units actually paired in execution and analysis? | | |

## Conditional fields

Complete only the sections needed by the claim. Mark the others N/A.

### 5. Stochastic or uncertainty claim

| question | status | evidence / explanation |
|---|---|---|
| Are stochastic units and shared clusters/histories identified? | | |
| Is the sampling, assignment, likelihood, or exchangeability model stated? | | |
| Is finite-panel remeasurement separated from population uncertainty? | | |
| Is uncertainty propagated on both sides when denominators permit it? | | |
| Are model-dependent sensitivity results and Monte Carlo error labeled? | | |

### 6. Population or transport claim

| question | status | evidence / explanation |
|---|---|---|
| Is the target population of policies, tasks, sites, or sessions defined? | | |
| Are observed units sampled/assigned from that target, or is an explicit predictive/transport model supplied? | | |
| Is evidence that could falsify the bridge stated? | | |
| Are new-policy, new-task, new-site, and crossed-policy-task claims distinguished? | | |

### 7. Screening or adaptive claim

| question | status | evidence / explanation |
|---|---|---|
| Is the screened candidate set and adaptation history retained? | | |
| Are stopping, promotion, fallback, and abstention rules prespecified? | | |
| Does uncertainty account for selection and repeated looks where relevant? | | |
| Is the final real-test stage sufficient for the action actually taken? | | |

## Reportable conclusion

Complete these sentences:

> On the displayed panel, the evaluator supports ____________________________.

> It does not by itself support ____________________________________________.

> Under the declared action, the simulated choice has real loss ____________.

> The prespecified acceptance criterion is _________________________________.

> The main unresolved uncertainty or transport assumption is ______________.

## Worked example: Real2Sim T-block audit action

This example demonstrates form use; it does not assert that the source paper
used the audit-defined operational rule.

| field | example entry |
|---|---|
| candidate version | released Figure 3/Table I values pinned in the reproduction package |
| action | for each of four policies, choose its best displayed simulated point, then select the largest aggregate |
| source alignment | checkpoint selection is source-motivated; exact collapse, ties, and displayed regret are audit-defined; no substantive tolerance is specified |
| displayed result | simulated winner \(\pi_0\); displayed real winner DP |
| displayed loss | 12.5 percentage points |
| tie treatment | the non-winning SVLA checkpoint tie yields \(r=.878\)–.947 but does not change either winner |
| evidence boundary | recovered vector points reproduce printed correlations; raw experiment rerun and complete run pairing are unavailable |
| status | finite-panel disagreement under the declared audit action; no field-prevalence or population claim |

## Stop conditions

Do not promote a correlation to a decision claim when the action, candidate
set, aggregation, tie rule, loss, or acceptance criterion is unspecified. Do
not promote a finite-panel result to a population claim without a target and a
defensible sampling, assignment, predictive, or transport bridge. Do not treat
post-outcome tuning as prospective validation. A reporting audit cannot by
itself certify safety or operational suitability; consequential deployment
requires the applicable domain, safety, ethics, and organizational approvals.

This checklist operationalizes Section 9 of
`PAPER.md`. It is a reporting and review tool, not a
universal validity score.
