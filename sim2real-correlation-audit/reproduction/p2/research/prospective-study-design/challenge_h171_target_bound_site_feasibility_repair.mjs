#!/usr/bin/env node
// Independent Node challenge of the H170 target-bound repair.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(
  FAMILY,
  "protocol-h170-target-bound-site-feasibility-repair.md",
);
const TARGET_SPEC_FILE = path.join(FAMILY, "input-h170-target-spec.json");
const H164_RESULT = path.join(
  FAMILY,
  "result-h164-outcome-free-site-feasibility-interface.json",
);
const H169_RESULT = path.join(
  FAMILY,
  "result-h169-h164-not-applicable-authorization-challenge.json",
);
const H170_RESULT = path.join(
  FAMILY,
  "result-h170-target-bound-site-feasibility-repair.json",
);
const OUTPUT = path.join(
  FAMILY,
  "result-h171-target-bound-site-feasibility-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256Bytes(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function sha256(file) {
  return sha256Bytes(fs.readFileSync(file));
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(",")}}`;
}

function canonicalHash(value) {
  return sha256Bytes(Buffer.from(stableStringify(value), "utf8"));
}

function deepEqual(a, b) {
  return stableStringify(a) === stableStringify(b);
}

const targetSpec = JSON.parse(fs.readFileSync(TARGET_SPEC_FILE, "utf8"));
const targetHash = canonicalHash(targetSpec);

function validateTargetBinding(dossier) {
  requireCondition(
    dossier.schema === "h170-site-feasibility-dossier-v2",
    "bad dossier schema",
  );
  requireCondition(
    dossier.target_spec && typeof dossier.target_spec === "object",
    "target_spec missing",
  );
  requireCondition(
    deepEqual(dossier.target_spec, targetSpec),
    "target_spec differs from canonical",
  );
  requireCondition(
    dossier.study_spec_hash === targetHash,
    "study_spec_hash differs from canonical",
  );
  requireCondition(
    canonicalHash(dossier.target_spec) === dossier.study_spec_hash,
    "target hash mismatch",
  );
  requireCondition(
    Array.isArray(dossier.not_applicable_authorizations),
    "authorization container malformed",
  );
  requireCondition(
    deepEqual(
      dossier.not_applicable_authorizations,
      targetSpec.not_applicable_authorizations,
    ),
    "authorization roster differs from canonical",
  );
  requireCondition(
    deepEqual(
      dossier.units.map((row) => row.unit),
      targetSpec.required_units,
    ),
    "unit roster differs from canonical",
  );
  const declared = dossier.units
    .filter((row) => row.status === "not_applicable")
    .map((row) => row.unit)
    .sort();
  const authorized = dossier.not_applicable_authorizations
    .map((row) => row.unit)
    .sort();
  requireCondition(
    deepEqual(declared, authorized),
    "not_applicable lacks exact authorization",
  );
}

function validateArtifacts(dossier) {
  const byId = new Map();
  for (const artifact of dossier.artifacts) {
    requireCondition(!byId.has(artifact.artifact_id), "duplicate artifact");
    const raw = Buffer.from(artifact.content_b64, "base64");
    requireCondition(raw.length === artifact.size_bytes, "artifact size mismatch");
    requireCondition(sha256Bytes(raw) === artifact.sha256, "artifact hash mismatch");
    byId.set(artifact.artifact_id, artifact);
  }
  for (const row of dossier.units) {
    requireCondition(row.artifact_ids.length > 0, "unit artifact missing");
    for (const artifactId of row.artifact_ids) {
      requireCondition(byId.has(artifactId), "referenced artifact missing");
    }
  }
}

function classify(dossier) {
  validateTargetBinding(dossier);
  validateArtifacts(dossier);
  const issues = [];
  const changes = [];
  if (dossier.prepared_before_outcomes !== true) issues.push("late");
  if (dossier.outcome_fields_present !== false) issues.push("outcomes");
  if (dossier.preexecution_comparison_recorded !== true) issues.push("comparison");
  if (dossier.acceptance_linked_to_controller_start !== true) issues.push("start_link");
  if (dossier.preexecution_capture_time_ns > dossier.controller_start_time_ns) {
    issues.push("capture_after_start");
  }
  if (
    dossier.controller_start_delay_ns
    !== dossier.controller_start_time_ns - dossier.preexecution_capture_time_ns
  ) {
    issues.push("delay_inconsistent");
  }
  if (dossier.human_override_used && !dossier.human_override_documented) {
    issues.push("override");
  }
  if (dossier.assigned_slots !== dossier.closed_slots) issues.push("slots");
  if (dossier.declared_retries !== dossier.observed_retries) issues.push("retries");
  if (dossier.capacity_safety_privacy_resolved !== true) issues.push("safety");
  if (dossier.tolerance_rationale_kind !== "site_owned_task_sensitivity_bound") {
    issues.push("tolerance_rationale");
  }
  for (const [feature, error] of Object.entries(
    dossier.measurement_error_by_feature,
  )) {
    if (error >= dossier.tolerance_by_feature[feature]) issues.push(`error:${feature}`);
  }
  for (const row of dossier.units) {
    if (["partial", "absent"].includes(row.status)) issues.push(`unit:${row.unit}`);
    if (row.status === "target_altering") changes.push(row.unit);
  }
  if (dossier.policy_visible_instrumentation) {
    changes.push("policy_observation_interface");
  }
  if (dossier.contact_or_dynamics_altering_instrumentation) {
    changes.push("scene_geometry_and_dynamics");
  }
  if (dossier.controller_start_delay_ns > dossier.max_allowed_start_delay_ns) {
    changes.push("controller_start_timing");
  }
  const complete = dossier.units.every((row) =>
    ["available", "not_applicable", "target_altering"].includes(row.status)
  );
  if (issues.length > 0) return "not_evidenced";
  if (changes.length > 0 && complete) return "target_altering_only";
  if (changes.length === 0 && complete) {
    return "eligible_for_outcome_hidden_rehearsal";
  }
  return "not_evidenced";
}

function attack(name, base, mutate) {
  const dossier = clone(base);
  mutate(dossier);
  let observed;
  try {
    observed = classify(dossier);
  } catch (error) {
    observed = `validation_error:${error.message}`;
  }
  const rejected = observed !== "eligible_for_outcome_hidden_rehearsal";
  requireCondition(rejected, `attack accepted: ${name}`);
  return { attack: name, observed, rejected };
}

function setNotApplicable(dossier, unitName) {
  const row = dossier.units.find((item) => item.unit === unitName);
  row.status = "not_applicable";
  row.missing_or_changed = "arbitrary reason";
}

function build() {
  const h164 = JSON.parse(fs.readFileSync(H164_RESULT, "utf8"));
  const h169 = JSON.parse(fs.readFileSync(H169_RESULT, "utf8"));
  const h170 = JSON.parse(fs.readFileSync(H170_RESULT, "utf8"));
  requireCondition(h169.disposition === "fail_repair_required", "H169 changed");
  requireCondition(targetSpec.not_applicable_authorizations.length === 0, "target changed");
  requireCondition(
    deepEqual(targetSpec.required_units, h164.unit_order),
    "required units disagree with H164",
  );
  requireCondition(
    h170.canonical_target_spec_hash === targetHash,
    "H170 target hash disagrees",
  );

  const decisions = {};
  let artifactCount = 0;
  for (const item of h170.dossiers) {
    const decision = classify(item.dossier);
    decisions[item.dossier.dossier_name] = decision;
    artifactCount += item.dossier.artifacts.length;
    requireCondition(
      decision === item.classification.decision,
      `decision disagrees: ${item.dossier.dossier_name}`,
    );
  }
  requireCondition(
    deepEqual(decisions, h170.known_answer_decisions),
    "known answers disagree",
  );
  requireCondition(artifactCount === 64, "artifact count changed");

  const base = h170.dossiers.find(
    (item) => item.dossier.dossier_name === "target_preserving_complete",
  ).dossier;
  const attacks = [
    attack("na_policy_observation", base, (dossier) =>
      setNotApplicable(dossier, "policy_observation_interface")),
    attack("na_context_order", base, (dossier) =>
      setNotApplicable(dossier, "context_generation_and_assignment_order")),
    attack("na_reset_carryover", base, (dossier) =>
      setNotApplicable(dossier, "reset_washout_and_carryover_control")),
    attack("forged_authorization", base, (dossier) => {
      setNotApplicable(dossier, "policy_observation_interface");
      dossier.not_applicable_authorizations.push({
        unit: "policy_observation_interface",
        rationale: "forged",
        target_spec_sha256: dossier.study_spec_hash,
      });
    }),
    attack("modified_target_old_hash", base, (dossier) => {
      dossier.target_spec.max_allowed_start_delay_ns += 1;
    }),
    attack("modified_target_rehashed", base, (dossier) => {
      dossier.target_spec.max_allowed_start_delay_ns += 1;
      dossier.study_spec_hash = canonicalHash(dossier.target_spec);
    }),
    attack("replaced_target_hash", base, (dossier) => {
      dossier.study_spec_hash = "0".repeat(64);
    }),
    attack("missing_target_spec", base, (dossier) => {
      delete dossier.target_spec;
    }),
    attack("malformed_authorization_container", base, (dossier) => {
      dossier.not_applicable_authorizations = {};
    }),
  ];

  return {
    schema: "h171-target-bound-site-feasibility-independent-challenge-v1",
    challenge_runtime: process.version,
    producer_modules_imported: false,
    protocol_sha256: sha256(PROTOCOL),
    target_spec_file_sha256: sha256(TARGET_SPEC_FILE),
    target_spec_canonical_hash: targetHash,
    upstream_hashes: {
      h164_result_sha256: sha256(H164_RESULT),
      h169_result_sha256: sha256(H169_RESULT),
      h170_result_sha256: sha256(H170_RESULT),
    },
    independently_reconstructed_decisions: decisions,
    independently_verified_artifact_count: artifactCount,
    authorization_attacks: attacks,
    authorization_attacks_rejected: attacks.length,
    h169_bypasses_rejected: true,
    disposition: "pass_with_scope",
    reliance_gate_passed_for_synthetic_interface_logic: true,
    real_site_qualified: false,
    field_collection_authorized: false,
    scope:
      "Independent target-binding and synthetic decision-logic challenge only; "
      + "not physical truth, evidence authenticity, tolerance adequacy, safety, "
      + "real-site qualification, outcomes, causality, or transport.",
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
    attacks_rejected: result.authorization_attacks_rejected,
    real_site_qualified: result.real_site_qualified,
  }));
} else {
  requireCondition(fs.readFileSync(OUTPUT, "utf8") === rendered(result), "result is stale");
  console.log("OK: H171 independent target-bound challenge regenerates exactly");
}
