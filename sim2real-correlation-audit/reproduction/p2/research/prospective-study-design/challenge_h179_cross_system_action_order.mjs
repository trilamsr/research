#!/usr/bin/env node
// Independent Node reconstruction of the H178 fixed-source conjunctions.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(
  FAMILY,
  "protocol-h178-cross-system-action-order-source-audit.md",
);
const ROSTER = path.join(
  FAMILY,
  "result-h177-cross-system-action-order-roster.json",
);
const CODING = path.join(FAMILY, "input-h178-source-coding.json");
const PRODUCER = path.join(
  FAMILY,
  "result-h178-cross-system-action-order-source-audit.json",
);
const OUTPUT = path.join(
  FAMILY,
  "result-h179-cross-system-action-order-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

const evidence = new Set(["available", "paper_described_only"]);
const rankingActions = new Set([
  "global_policy_ranking",
  "fixed_task_policy_score_or_ranking",
]);
const positiveUnits = [
  "context_fixed_before_candidate_assignment",
  "stable_assignment_law_public",
  "stable_context_law_public",
  "declared_target_support_complete_or_bounded",
  "reset_carryover_rule_public",
  "cluster_or_session_identity_public",
  "public_action_matches_identified_estimand",
  "target_compatible_positive_contrast",
];

function byUnit(system) {
  return Object.fromEntries(system.units.map((row) => [row.unit, row]));
}

function isPositive(system) {
  const rows = byUnit(system);
  const action = rows.declared_operational_action;
  return (
    evidence.has(action.status) &&
    rankingActions.has(action.value) &&
    positiveUnits.every(
      (name) =>
        evidence.has(rows[name].status) && rows[name].value === "satisfied",
    )
  );
}

function isSecondMismatch(system) {
  const rows = byUnit(system);
  return (
    system.system !== "roboarena" &&
    rows.declared_operational_action.value === "global_policy_ranking" &&
    evidence.has(rows.candidate_pair_or_roster_fixed_before_context.status) &&
    rows.candidate_pair_or_roster_fixed_before_context.value === "satisfied" &&
    evidence.has(rows.context_fixed_before_candidate_assignment.status) &&
    rows.context_fixed_before_candidate_assignment.value === "not_satisfied" &&
    evidence.has(rows.stable_context_law_public.status) &&
    rows.stable_context_law_public.value === "not_satisfied" &&
    evidence.has(rows.public_action_matches_identified_estimand.status) &&
    rows.public_action_matches_identified_estimand.value === "not_satisfied"
  );
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function build() {
  const roster = JSON.parse(fs.readFileSync(ROSTER, "utf8"));
  const coding = JSON.parse(fs.readFileSync(CODING, "utf8"));
  const producer = JSON.parse(fs.readFileSync(PRODUCER, "utf8"));
  requireCondition(
    coding.fixed_roster_sha256 === sha256(ROSTER),
    "coding roster binding changed",
  );
  requireCondition(
    coding.systems.length === 7 &&
      coding.systems.every((system) => system.units.length === 10),
    "70-row frame changed",
  );
  requireCondition(
    roster.frozen_source_screening_roster
      .map((row) => row.arxiv_id)
      .join("|") === coding.systems.map((row) => row.arxiv_id).join("|"),
    "identity roster disagrees",
  );
  for (const source of coding.source_bindings) {
    requireCondition(
      sha256(path.join(FAMILY, source.path)) === source.sha256,
      `source hash changed: ${source.source_key}`,
    );
  }

  const positives = coding.systems
    .filter((system) => system.system !== "roboarena" && isPositive(system))
    .map((system) => system.system);
  const mismatches = coding.systems
    .filter(isSecondMismatch)
    .map((system) => system.system);
  requireCondition(
    positives.join("|") === "umi_bench|robodojo",
    "positive contrast reconstruction disagrees",
  );
  requireCondition(mismatches.length === 0, "unexpected second mismatch");
  requireCondition(
    positives.join("|") === producer.positive_contrast_systems.join("|") &&
      mismatches.join("|") === producer.second_mismatch_systems.join("|"),
    "producer decision disagrees",
  );

  const attacks = [];
  for (const systemName of positives) {
    const original = coding.systems.find((row) => row.system === systemName);
    for (const unitName of positiveUnits) {
      const attacked = clone(original);
      const row = attacked.units.find((item) => item.unit === unitName);
      row.status = "partial";
      row.value = "unresolved";
      attacks.push({
        attack: `${systemName}:${unitName}:remove_one_required_unit`,
        rejected: !isPositive(attacked),
      });
    }
  }
  const shortcutAttacks = [
    ["fixed_task_list_alone", "practical_recipe"],
    ["queue_alone", "autoeval"],
    ["reset_prose_alone", "autoeval"],
    ["episode_totals_alone", "gesim_2"],
    ["leaderboard_label_alone", "roboarena"],
    ["sim_real_correlation_alone", "practical_recipe"],
  ];
  for (const [attack, systemName] of shortcutAttacks) {
    const candidate = coding.systems.find((row) => row.system === systemName);
    attacks.push({ attack, rejected: !isPositive(candidate) });
  }
  requireCondition(attacks.every((row) => row.rejected), "semantic attack accepted");

  return {
    schema: "h179-cross-system-action-order-independent-challenge-v1",
    challenge_runtime: process.version,
    producer_modules_imported: false,
    protocol_sha256: sha256(PROTOCOL),
    upstream_hashes: {
      h177_roster_sha256: sha256(ROSTER),
      h178_source_coding_sha256: sha256(CODING),
      h178_result_sha256: sha256(PRODUCER),
    },
    independently_reconstructed_row_count: 70,
    independently_reconstructed_positive_contrasts: positives,
    independently_reconstructed_second_mismatches: mismatches,
    semantic_attacks: attacks,
    semantic_attacks_rejected: attacks.length,
    decision: "positive_contrast_found",
    positive_contrast_strength: "source_described",
    agrees_with_h178: true,
    outcome_fields_accessed_or_used: false,
    external_contact_performed: false,
    scope: [
      "The result is bounded to the fixed seven-system purposive roster.",
      "The two positive contrasts are supported by source descriptions rather than independently reproduced execution artifacts.",
      "The challenge does not assess performance outcomes or prevalence.",
    ],
    disposition: "pass_with_scope",
  };
}

const rendered = `${JSON.stringify(build(), null, 2)}\n`;
if (process.argv.includes("--check")) {
  requireCondition(fs.existsSync(OUTPUT), "challenge result is missing");
  requireCondition(fs.readFileSync(OUTPUT, "utf8") === rendered, "challenge result is stale");
  console.log("OK: H179 independent challenge is current");
} else {
  fs.writeFileSync(OUTPUT, rendered);
  console.log(`Wrote ${path.basename(OUTPUT)}: pass_with_scope`);
}
