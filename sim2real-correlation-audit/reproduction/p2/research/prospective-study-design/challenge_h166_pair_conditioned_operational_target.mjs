#!/usr/bin/env node
// Independent BigInt reconstruction and semantic challenge for H165.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(
  FAMILY,
  "protocol-h165-pair-conditioned-operational-target.md",
);
const H151 = path.join(
  FAMILY,
  "result-h151-pair-first-common-context-identification.json",
);
const H152 = path.join(
  FAMILY,
  "result-h152-pair-first-identification-independent-challenge.json",
);
const H165 = path.join(
  FAMILY,
  "result-h165-pair-conditioned-operational-target.json",
);
const OUTPUT = path.join(
  FAMILY,
  "result-h166-pair-conditioned-operational-target-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function gcd(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y !== 0n) [x, y] = [y, x % y];
  return x;
}

function q(numerator, denominator = 1n) {
  requireCondition(denominator !== 0n, "zero denominator");
  let n = BigInt(numerator);
  let d = BigInt(denominator);
  if (d < 0n) {
    n = -n;
    d = -d;
  }
  const divisor = gcd(n, d);
  return { n: n / divisor, d: d / divisor };
}

function add(a, b) {
  return q(a.n * b.d + b.n * a.d, a.d * b.d);
}

function sub(a, b) {
  return q(a.n * b.d - b.n * a.d, a.d * b.d);
}

function mul(a, b) {
  return q(a.n * b.n, a.d * b.d);
}

function div(a, b) {
  return q(a.n * b.d, a.d * b.n);
}

function equal(a, b) {
  return a.n === b.n && a.d === b.d;
}

function greater(a, b) {
  return a.n * b.d > b.n * a.d;
}

function text(a) {
  return `${a.n}/${a.d}`;
}

const ZERO = q(0n);
const ONE = q(1n);
const HALF = q(1n, 2n);
const THIRD = q(1n, 3n);
const PAIRS = ["01", "02", "12"];
const THETA = { "01": q(3n, 4n), "02": q(1n, 4n), "12": q(3n, 4n) };
const PI = { "01": THIRD, "02": THIRD, "12": THIRD };
const OPTIMAL = { "01": 0, "02": 2, "12": 1 };
const LOWER = { "01": 0, "02": 0, "12": 1 };

function members(pair) {
  requireCondition(PAIRS.includes(pair), `unsupported pair ${pair}`);
  return [Number(pair[0]), Number(pair[1])];
}

function routeValue(rule, theta = THETA, weights = PI) {
  let totalWeight = ZERO;
  let total = ZERO;
  for (const pair of Object.keys(weights)) {
    const weight = weights[pair];
    requireCondition(weight.n >= 0n, "negative weight");
    totalWeight = add(totalWeight, weight);
    requireCondition(pair in theta, `missing positive-weight edge ${pair}`);
    requireCondition(pair in rule, `missing routing action ${pair}`);
    const [lower, upper] = members(pair);
    requireCondition(
      rule[pair] === lower || rule[pair] === upper,
      `choice outside pair ${pair}`,
    );
    const edge = theta[pair];
    const chosen = rule[pair] === lower ? edge : sub(ONE, edge);
    total = add(total, mul(weight, chosen));
  }
  requireCondition(equal(totalWeight, ONE), "weights do not sum to one");
  return total;
}

function tournamentValues() {
  const q01 = THETA["01"];
  const q02 = THETA["02"];
  const q12 = THETA["12"];
  return [
    div(add(add(HALF, q01), q02), q(3n)),
    div(add(add(HALF, sub(ONE, q01)), q12), q(3n)),
    div(add(add(HALF, sub(ONE, q02)), sub(ONE, q12)), q(3n)),
  ];
}

function rejectedAttack(id, condition, reason) {
  requireCondition(condition, `semantic attack accepted: ${id}`);
  return { id, rejected: true, reason };
}

function build() {
  const optimalValue = routeValue(OPTIMAL);
  const lowerValue = routeValue(LOWER);
  const regret = sub(optimalValue, lowerValue);
  const scores = tournamentValues();
  requireCondition(equal(optimalValue, q(3n, 4n)), "optimal value changed");
  requireCondition(equal(lowerValue, q(7n, 12n)), "lower value changed");
  requireCondition(equal(regret, q(1n, 6n)), "regret changed");
  requireCondition(scores.every((score) => equal(score, HALF)), "scores do not tie");

  let missingRefused = false;
  try {
    routeValue(OPTIMAL, { "01": THETA["01"], "12": THETA["12"] });
  } catch (error) {
    missingRefused = String(error.message).includes("missing positive-weight edge 02");
  }
  let outsidePairRefused = false;
  try {
    routeValue({ "01": 2, "02": 2, "12": 1 });
  } catch (error) {
    outsidePairRefused = String(error.message).includes("choice outside pair 01");
  }

  const h151 = JSON.parse(fs.readFileSync(H151, "utf8"));
  const h152 = JSON.parse(fs.readFileSync(H152, "utf8"));
  const h165 = JSON.parse(fs.readFileSync(H165, "utf8"));
  requireCondition(
    h151.pair_conditioned_policy_tie === true
      && h151.world_low.unique_winner === 2
      && h151.world_high.unique_winner === 0
      && h151.endpoint_regret_census.every_singleton_floor.text === "1/3",
    "H151 boundary changed",
  );
  requireCondition(
    JSON.stringify(h152.pair_conditioned_policy_values)
        === JSON.stringify(["1/2", "1/2", "1/2"])
      && h152.low_world.unique_winner === 2
      && h152.high_world.unique_winner === 0
      && h152.disposition === "pass_with_scope",
    "H152 challenge changed",
  );
  requireCondition(
    h165.known_answer.edge_optimal_routing_value.text === text(optimalValue)
      && h165.known_answer.always_lower_index_value.text === text(lowerValue)
      && h165.known_answer.always_lower_index_regret.text === text(regret),
    "independent arithmetic disagrees with H165",
  );

  const attacks = [
    rejectedAttack(
      "tournament_tie_erases_pair_routing_advantage",
      scores.every((score) => equal(score, HALF))
        && greater(optimalValue, lowerValue),
      "a global score tie coexists with exact routing regret 1/6",
    ),
    rejectedAttack(
      "routing_optimum_identifies_unique_global_policy",
      scores.every((score) => equal(score, HALF)),
      "all global tournament scores tie",
    ),
    rejectedAttack(
      "comparative_edge_is_marginal_task_success",
      h165.support_and_refusal_matrix.some(
        (row) => row.target === "per_policy_task_success"
          && row.decision.startsWith("refused"),
      ),
      "comparative outcomes do not identify marginal success without a bridge",
    ),
    rejectedAttack(
      "future_context_mechanism_may_change_silently",
      h165.reporting_gate.future_pair_context_mechanism_fixed === true,
      "the operational target requires the same declared pair-specific mechanism",
    ),
    rejectedAttack(
      "outcome_adaptive_pair_weights_preserve_fixed_target",
      h165.reporting_gate.pair_weights_fixed_outcome_independently === true,
      "outcome-adaptive weights define a different analysis",
    ),
    rejectedAttack(
      "positive_weight_missing_edge_still_identifies_route_value",
      missingRefused,
      "a positive-weight missing edge is rejected",
    ),
    rejectedAttack(
      "router_may_choose_policy_outside_presented_pair",
      outsidePairRefused,
      "the routing action is restricted to a member of the presented pair",
    ),
    rejectedAttack(
      "pair_routing_estimates_evaluator_causal_effect",
      h165.support_and_refusal_matrix.some(
        (row) => row.target === "evaluator_or_simulator_causal_effect"
          && row.decision.startsWith("refused"),
      ),
      "no randomized evaluator intervention is supplied",
    ),
  ];
  requireCondition(attacks.length === 8, "attack roster changed");

  return {
    schema: "h166-pair-conditioned-operational-target-independent-challenge-v1",
    challenge_runtime: process.version,
    producer_modules_imported: false,
    protocol_sha256: sha256(PROTOCOL),
    upstream_hashes: {
      h151_result_sha256: sha256(H151),
      h152_result_sha256: sha256(H152),
      h165_result_sha256: sha256(H165),
    },
    independent_known_answer: {
      pair_weights: Object.fromEntries(PAIRS.map((pair) => [pair, text(PI[pair])])),
      pair_conditioned_edges: Object.fromEntries(
        PAIRS.map((pair) => [pair, text(THETA[pair])]),
      ),
      cyclic_preferences: ["0>1", "1>2", "2>0"],
      edge_optimal_route: OPTIMAL,
      edge_optimal_value: text(optimalValue),
      lower_index_route: LOWER,
      lower_index_value: text(lowerValue),
      lower_index_regret: text(regret),
      tournament_values: scores.map(text),
      unique_global_policy_identified: false,
    },
    upstream_common_context_boundary: {
      opposite_unique_winners: [2, 0],
      singleton_worst_regret_floor: "1/3",
      common_context_target_identified: false,
    },
    semantic_attacks: attacks,
    attacks_rejected: attacks.filter((attack) => attack.rejected).length,
    disposition: "pass_with_scope",
    scope:
      "Independent exact and semantic support for same-mechanism pair routing only; "
      + "not common-context selection, marginal success, causal effect, transport, "
      + "confidence, real-site qualification, field authorization, or novelty.",
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
    attacks_rejected: result.attacks_rejected,
    routing_value: result.independent_known_answer.edge_optimal_value,
  }));
} else {
  requireCondition(fs.readFileSync(OUTPUT, "utf8") === rendered(result), "result is stale");
  console.log("OK: H166 independent pair-conditioned challenge regenerates exactly");
}
