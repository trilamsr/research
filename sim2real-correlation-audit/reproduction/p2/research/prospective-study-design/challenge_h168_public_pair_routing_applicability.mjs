#!/usr/bin/env node
// Independent outcome-free challenge of the H167 public applicability gate.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const files = {
  protocol: "protocol-h167-public-pair-routing-applicability.md",
  paper_protocol: "source-h122-roboarena-paper-protocol.json",
  ranking_semantics: "result-h106-roboarena-ranking-algorithm-and-exclusion.json",
  assignment_context: "result-h114-roboarena-authored-text-assignment-context.json",
  dataset_card_recall: "result-h116-roboarena-dataset-card-assignment-recall.json",
  release_challenge: "result-h122-release-sequence-independent-challenge.json",
  assignment_regimes: "result-roboarena-assignment-regimes.json",
  h165_target: "result-h165-pair-conditioned-operational-target.json",
  h166_challenge:
    "result-h166-pair-conditioned-operational-target-independent-challenge.json",
  h167_result: "result-h167-public-pair-routing-applicability.json",
};
const OUTPUT = path.join(
  FAMILY,
  "result-h168-public-pair-routing-applicability-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function full(name) {
  return path.join(FAMILY, files[name]);
}

function readJson(name) {
  return JSON.parse(fs.readFileSync(full(name), "utf8"));
}

function sha256(name) {
  return crypto
    .createHash("sha256")
    .update(fs.readFileSync(full(name)))
    .digest("hex");
}

function attack(id, rejected, reason) {
  requireCondition(rejected, `attack accepted: ${id}`);
  return { id, rejected: true, reason };
}

function build() {
  const paper = readJson("paper_protocol");
  const ranking = readJson("ranking_semantics");
  const assignment = readJson("assignment_context");
  const cards = readJson("dataset_card_recall");
  const release = readJson("release_challenge");
  const regimes = readJson("assignment_regimes");
  const h165 = readJson("h165_target");
  const h166 = readJson("h166_challenge");
  const producer = readJson("h167_result");

  requireCondition(ranking.outcome_values_accessed === false, "ranking outcomes used");
  requireCondition(assignment.outcome_values_accessed === false, "assignment outcomes used");
  requireCondition(
    cards.performance_values_retained_or_interpreted === false,
    "dataset-card performance used",
  );
  requireCondition(
    release.outcome_or_judgment_fields_referenced_or_used === false,
    "release outcomes used",
  );
  requireCondition(
    regimes.input.outcome_fields_referenced_or_used === false,
    "regime outcomes used",
  );
  requireCondition(h165.field_collection_authorized === false, "field use authorized");
  requireCondition(h166.disposition === "pass_with_scope", "H166 scope changed");

  const statusVector = [
    "absent",
    "available",
    "absent",
    "paper_described_only",
    "absent",
    "absent",
    "absent",
    "absent",
    "paper_described_only",
    "absent",
    "absent",
    "available",
    "partial",
    "contradicted_by_public_record",
    "partial",
  ];
  const required = [1, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15];
  const failed = required.filter((unitId) => statusVector[unitId - 1] !== "available");
  requireCondition(failed.length === 11, "failed conjunction changed");
  requireCondition(
    producer.units.map((row) => row.status).join("|") === statusVector.join("|"),
    "independent status vector disagrees with H167",
  );

  const paperStatesRandomPair = paper.source_findings[0].finding.includes(
    "describes that sampling as random",
  );
  const paperDisclaimsCurrent = paper.not_established_by_source.includes(
    "the current deployed server implementation or revision",
  );
  const publicRanks = ranking.algorithm_name === "Bradley-Terry Davidson";
  const serverLawAbsent =
    assignment.server_assignment_law_established === false
    && assignment.realized_assignment_probabilities_established === false;
  const cardsHaveNoCandidates = cards.candidate_window_count === 0;
  const cumulativeComplete = release.fixed_panel_support[1].supported_pair_count === 21;
  const newestIncomplete =
    release.fixed_panel_support[2].supported_pair_count === 15
    && release.fixed_panel_support[2].isolated_policies.length === 1;
  const bridgeRequired = regimes.decision_consequence.includes(
    "segment or explicitly bridge",
  );

  const attacks = [
    attack(
      "paper_random_sampling_identifies_current_deployed_law",
      paperStatesRandomPair && paperDisclaimsCurrent && serverLawAbsent,
      "paper protocol and current deployed implementation are distinct evidence units",
    ),
    attack(
      "global_leaderboard_is_within_pair_routing_action",
      publicRanks && h165.known_answer.unique_global_policy_identified === false,
      "the public ranking action differs from H165's within-pair action",
    ),
    attack(
      "paper_matched_conditions_identify_stable_future_Gab",
      paper.not_established_by_source.includes(
        "orientation probabilities, blocking, history, reset, or interference controls",
      ),
      "within-comparison matching does not identify a stable future context law",
    ),
    attack(
      "dataset_cards_supply_assignment_weights",
      cardsHaveNoCandidates && serverLawAbsent,
      "the three immutable cards provide no assignment-language candidate window",
    ),
    attack(
      "cumulative_complete_graph_proves_current_complete_support",
      cumulativeComplete && newestIncomplete,
      "the cumulative and newest-increment support states differ",
    ),
    attack(
      "roster_and_assignment_epochs_pool_without_bridge",
      bridgeRequired,
      "the prior outcome-free topology audit requires segmentation or a bridge",
    ),
    attack(
      "aggregate_session_counts_are_cluster_valid_assignment_export",
      release.session_identifiers_or_rows_retained === false,
      "aggregate structure is not a retained session-level assignment export",
    ),
  ];

  return {
    schema: "h168-public-pair-routing-applicability-independent-challenge-v1",
    challenge_runtime: process.version,
    producer_modules_imported: false,
    protocol_sha256: sha256("protocol"),
    source_hashes: Object.fromEntries(
      Object.keys(files)
        .filter((name) => !["protocol", "h167_result"].includes(name))
        .sort()
        .map((name) => [name, sha256(name)]),
    ),
    h167_result_sha256: sha256("h167_result"),
    outcome_fields_accessed_or_used: false,
    independently_reconstructed_status_vector: statusVector,
    required_unit_ids: required,
    failed_required_unit_ids: failed,
    failed_required_unit_count: failed.length,
    public_action_mismatch: statusVector[0] === "absent"
      && statusVector[1] === "available",
    semantic_attacks: attacks,
    attacks_rejected: attacks.length,
    decision: "not_qualified_for_public_pair_routing_application",
    disposition: "pass_with_scope",
    scope:
      "Independent outcome-free challenge of current public applicability only; "
      + "not benchmark invalidity, assignment intent, outcome dependence, "
      + "field authorization, or prospective impossibility.",
  };
}

function rendered(data) {
  return `${JSON.stringify(data, null, 2)}\n`;
}

const args = process.argv.slice(2);
requireCondition(
  args.length === 1 && (args[0] === "--write" || args[0] === "--check"),
  "use exactly one of --write or --check",
);
const result = build();
if (args[0] === "--write") {
  fs.writeFileSync(OUTPUT, rendered(result));
  console.log(JSON.stringify({
    disposition: result.disposition,
    decision: result.decision,
    attacks_rejected: result.attacks_rejected,
  }));
} else {
  requireCondition(fs.readFileSync(OUTPUT, "utf8") === rendered(result), "result is stale");
  console.log("OK: H168 independent public-applicability challenge regenerates exactly");
}
