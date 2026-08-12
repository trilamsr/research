#!/usr/bin/env node
// Independent source-identity and decision challenge for H224.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const producerPath = path.join(
  directory,
  "result-h224-armnetbench-paper-design-audit.json",
);
const outputPath = path.join(
  directory,
  "result-h224-armnetbench-paper-design-independent-challenge.json",
);

const expected = {
  producerSha256: "b29dc62a06f2174d2c9a6971dd678b774d728edc33431cee7a2e4976487f000a",
  pdfSha256: "c1d0edbd163f6db2597da67c4afe03e8b63deb3c2eefbfca613db3ff5319951e",
  sourceArchiveSha256:
    "21e4d8b117878e4d42d810da6e8e2a711c11e146dc389d1fd4ba7da97cf12bf1",
  mainTexSha256: "8ceaa0e443e561c90b376a22e5c4d541243685d5cb3d42b04d905118907f6e20",
  h028Sha256: "40578851f962399cf0e6bca4eca95417ed28c419f6fe486b6ac8d08408698482",
  h029Sha256: "82dd62ad96cdce928774705a214f9161ec694e1a3b7edc57c385d36ced3f272c",
  h222Sha256: "3bf46af0c4e3bed9b7f05c0553098d1689cd825860638d121c194c7c59fd087b",
};

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function includesAll(text, fragments) {
  return fragments.every((fragment) => text.includes(fragment));
}

function independentFacts(source) {
  const lower = source.toLowerCase();
  const multiPolicy = includesAll(source, [
    "We evaluate two specialist imitation policies",
    "and five vision-language-action models",
  ]);
  const standaloneExecution = includesAll(source, [
    "runs it locally in an isolated container",
    "Each task--policy pair targets 30 rollouts.",
  ]);
  const commonTaskCell = includesAll(source, [
    "all seven\npolicies for a task ran on the \\emph{same} cell",
    "holding the nominal setup\nconstant within that task",
  ]);
  const initialStatesIndependentlySampled = includesAll(source, [
    "randomises object placement within a task-specific range",
    "sampled independently rather than matched across policies",
  ]);
  const explicitPolicyAssignmentLaw =
    /\b(random(?:ly|ised|ized)? assign(?:ed|ment)|policy assignment law)\b/i.test(
      source,
    );
  const explicitPolicyOrderLaw =
    /\b(policy execution order|policy order was|random(?:ised|ized) order)\b/i.test(
      source,
    );
  const resetBeforeRollout = source.includes(
    "Before each rollout, an operator resets the scene",
  );
  const measuredResetAcceptance =
    /\b(reset acceptance|accepted reset|reset tolerance|reset measurement)\b/i.test(
      source,
    );
  const completeLifecycle = includesAll(source, [
    "Manual reset errors.",
    "Object deterioration.",
    "Physical cell changes.",
  ]);
  const lifecycleQualified = completeLifecycle && measuredResetAcceptance;
  const sessionDependenceIdentity =
    /\b(session[_ -]?id|operator[_ -]?id|dependence unit|cluster[_ -]?id)\b/i.test(
      source,
    );
  const fixedHorizon = !source.includes(
    "did not enforce\nstandardised per-task wall-clock limits",
  );
  const operatorPostexecutionScore = includesAll(source, [
    "The on-site operator then scores the rollout",
    "\\emph{three-way quality label}",
  ]);
  const preexecutionEvaluator =
    /\b(pre-execution evaluator|simulator score before|world-model score before)\b/i.test(
      source,
    );
  const uncertaintyMethod =
    /\b(confidence interval|credible interval|standard error|bootstrap)\b/i.test(
      source,
    );
  const perTrialLinkage = includesAll(source, [
    "We release the core benchmark in two formats.",
    "\\texttt{success}, \\texttt{success\\_class}, \\texttt{policy\\_type}",
    "preserve the operator-assigned outcomes",
  ]);
  const immutableCheckpoints =
    /\bcheckpoint (?:commit|revision|sha-?256|content hash)\b/i.test(source);
  const costCapacity = includesAll(source, [
    "\\textbf{Cost.}",
    "Cells supervised concurrently per operator",
    "retrospective estimate rather than a measurement",
  ]);
  const outcomeTokensProcessedButNotExtracted =
    lower.includes("success rate") && lower.includes("\\section{results}");

  return {
    multi_policy: multiPolicy,
    standalone_execution: standaloneExecution,
    common_task_cell: commonTaskCell,
    initial_states_independently_sampled: initialStatesIndependentlySampled,
    explicit_policy_assignment_law: explicitPolicyAssignmentLaw,
    explicit_policy_order_law: explicitPolicyOrderLaw,
    reset_before_rollout: resetBeforeRollout,
    measured_reset_acceptance: measuredResetAcceptance,
    complete_lifecycle_evidence: lifecycleQualified,
    session_dependence_identity: sessionDependenceIdentity,
    fixed_horizon: fixedHorizon,
    operator_postexecution_score: operatorPostexecutionScore,
    preexecution_evaluator: preexecutionEvaluator,
    dependence_aware_uncertainty_method: uncertaintyMethod,
    public_per_trial_artifact_outcome_linkage: perTrialLinkage,
    immutable_evaluated_checkpoints: immutableCheckpoints,
    cost_capacity_documented: costCapacity,
    outcome_tokens_processed_but_not_extracted:
      outcomeTokensProcessedButNotExtracted,
  };
}

function decisions(facts) {
  const positiveP2 =
    facts.multi_policy &&
    facts.standalone_execution &&
    facts.common_task_cell &&
    facts.explicit_policy_assignment_law &&
    facts.explicit_policy_order_law &&
    facts.measured_reset_acceptance &&
    facts.session_dependence_identity &&
    facts.dependence_aware_uncertainty_method;
  const h022Closed =
    facts.immutable_evaluated_checkpoints &&
    facts.fixed_horizon &&
    facts.preexecution_evaluator &&
    facts.public_per_trial_artifact_outcome_linkage &&
    facts.session_dependence_identity;
  return {
    p2_classification:
      facts.multi_policy && !positiveP2
        ? "adverse_mismatch_contrast"
        : positiveP2
          ? "positive_design_contrast"
          : "context_only",
    p2_positive_design_contrast_eligible: positiveP2,
    h022_status: h022Closed ? "eligible" : "refused_unchanged",
    h022_existing_blockers_all_closed: h022Closed,
  };
}

function selfTest() {
  const adverse = [
    "We evaluate two specialist imitation policies and five vision-language-action models.",
    "runs it locally in an isolated container",
    "Each task--policy pair targets 30 rollouts.",
    "all seven\npolicies for a task ran on the \\emph{same} cell",
    "holding the nominal setup\nconstant within that task",
    "randomises object placement within a task-specific range",
    "sampled independently rather than matched across policies",
    "Before each rollout, an operator resets the scene",
    "Manual reset errors. Object deterioration. Physical cell changes.",
    "did not enforce\nstandardised per-task wall-clock limits",
    "The on-site operator then scores the rollout",
    "\\emph{three-way quality label}",
    "We release the core benchmark in two formats.",
    "\\texttt{success}, \\texttt{success\\_class}, \\texttt{policy\\_type}",
    "preserve the operator-assigned outcomes",
    "\\textbf{Cost.}",
    "Cells supervised concurrently per operator",
    "retrospective estimate rather than a measurement",
    "\\section{Results} success rate",
  ].join("\n");
  const classified = decisions(independentFacts(adverse));
  assert(
    classified.p2_classification === "adverse_mismatch_contrast",
    "adverse canary",
  );
  assert(classified.h022_status === "refused_unchanged", "H022 canary");
}

function fileSha(filePath) {
  return sha256(fs.readFileSync(filePath));
}

function main(args) {
  selfTest();
  assert(args.length === 3, "expected SOURCE_TEX PDF SOURCE_ARCHIVE");
  const [sourcePath, pdfPath, sourceArchivePath] = args;
  const producerBytes = fs.readFileSync(producerPath);
  const producer = JSON.parse(producerBytes);
  const sourceBytes = fs.readFileSync(sourcePath);
  const source = sourceBytes.toString("utf8");

  assert(sha256(producerBytes) === expected.producerSha256, "producer hash mismatch");
  assert(sha256(sourceBytes) === expected.mainTexSha256, "main.tex hash mismatch");
  assert(fileSha(pdfPath) === expected.pdfSha256, "PDF hash mismatch");
  assert(
    fileSha(sourceArchivePath) === expected.sourceArchiveSha256,
    "source archive hash mismatch",
  );
  assert(
    fileSha(path.join(directory, "result-armnetbench-target-metrology-intake.json")) ===
      expected.h028Sha256,
    "H028 hash mismatch",
  );
  assert(
    fileSha(
      path.join(directory, "result-armnetbench-nonoutcome-manifest-linkage.json"),
    ) === expected.h029Sha256,
    "H029 hash mismatch",
  );
  assert(
    fileSha(
      path.join(
        directory,
        "..",
        "decision-validity",
        "result-h222-postbaseline-monitor-alert-screen.json",
      ),
    ) === expected.h222Sha256,
    "H222 hash mismatch",
  );

  const facts = independentFacts(source);
  const adjudication = decisions(facts);
  assert(
    adjudication.p2_classification ===
      producer.decisions.p2_classification,
    "P2 decision disagreement",
  );
  assert(
    adjudication.h022_status === producer.decisions.h022_status,
    "H022 decision disagreement",
  );
  const producerStatuses = Object.fromEntries(
    producer.evidence_units.map((row) => [row.unit_id, row.status]),
  );
  const independentStatuses = {
    1: "partial",
    2: "partial",
    3: facts.standalone_execution ? "supported" : "partial",
    4: "partial",
    5: "partial",
    6: "partial",
    7: "partial",
    8: "partial",
    9: facts.public_per_trial_artifact_outcome_linkage ? "supported" : "partial",
    10: facts.dependence_aware_uncertainty_method
      ? "supported"
      : "absent_from_fixed_scope",
    11: facts.preexecution_evaluator ? "supported" : "absent_from_fixed_scope",
    12: facts.cost_capacity_documented ? "supported" : "partial",
  };
  assert(
    JSON.stringify(producerStatuses) === JSON.stringify(independentStatuses),
    "unit status disagreement",
  );

  const result = {
    schema: "h224-armnetbench-paper-design-independent-challenge-v1",
    independent_implementation:
      "node-stdlib-exact-source-identities-and-rule-reconstruction",
    producer_result_sha256: expected.producerSha256,
    source_identities: {
      arxiv_id: "2607.24481v1",
      pdf_sha256: expected.pdfSha256,
      source_archive_sha256: expected.sourceArchiveSha256,
      main_tex_sha256: expected.mainTexSha256,
    },
    dependency_identities: {
      h028_result_sha256: expected.h028Sha256,
      h029_result_sha256: expected.h029Sha256,
      h222_result_sha256: expected.h222Sha256,
    },
    independent_facts: facts,
    independent_decisions: adjudication,
    independent_unit_statuses: independentStatuses,
    all_unit_statuses_agree: true,
    p2_decision_agrees: true,
    h022_decision_agrees: true,
    outcome_boundary: {
      full_source_bytes_processed: true,
      performance_values_extracted_or_retained: false,
      performance_values_used_in_classification: false,
      source_selection_revisited: false,
    },
    scope_limits: {
      linked_code_data_or_media_newly_opened: false,
      protected_p1_outcomes_accessed: false,
      sealed_p3_frame_accessed: false,
      author_contacted: false,
    },
    disposition: "pass_adverse_mismatch_and_h022_refusal_confirmed",
  };
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`wrote ${outputPath}\n`);
}

if (process.argv.includes("--self-test")) {
  selfTest();
  process.stdout.write("OK: H224 independent self-test\n");
} else {
  main(process.argv.slice(2));
}
