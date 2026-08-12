#!/usr/bin/env node
// Method-distinct deterministic challenge for the WM calibration audit.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const input = path.join(here, "..", "corpus-reporting-audit", "sources", "source-wm-policyeval.csv");
const protocol = path.join(here, "protocol-wm-probability-calibration-audit.md");
const producer = path.join(here, "audit_wm_probability_calibration.py");
const producerResult = path.join(here, "result-wm-probability-calibration-audit.json");
const output = path.join(here, "result-wm-probability-calibration-audit-independent-challenge.json");
const tolerance = 1e-10;

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function argmax(entries) {
  return entries.reduce((best, entry) => (entry[1] > best[1] ? entry : best))[0];
}

function parsePanels() {
  const lines = fs.readFileSync(input, "utf8").split(/\r?\n/).filter(
    (line) => line.trim() && !line.startsWith("#"),
  );
  const header = lines[0].split(",");
  const rows = lines.slice(1).map((line) => {
    const fields = line.split(",");
    const row = Object.fromEntries(header.map((name, index) => [name, fields[index]]));
    return {
      model: row.world_model,
      policy: row.policy,
      task: row.task,
      real: Number(row.actual_success_rate),
      predicted: Number(row.predicted_success_rate),
    };
  });
  return Object.fromEntries(
    ["Cosmos", "IRASim"].map((model) => [model, rows.filter((row) => row.model === model)]),
  );
}

function metrics(rows) {
  const real = rows.map((row) => row.real);
  const predicted = rows.map((row) => row.predicted);
  const realMean = mean(real);
  const predictedMean = mean(predicted);
  const centeredReal = real.map((value) => value - realMean);
  const centeredPredicted = predicted.map((value) => value - predictedMean);
  const covariance = centeredPredicted.reduce(
    (sum, value, index) => sum + value * centeredReal[index],
    0,
  );
  const predictedSumsq = centeredPredicted.reduce((sum, value) => sum + value * value, 0);
  const realSumsq = centeredReal.reduce((sum, value) => sum + value * value, 0);
  const slope = covariance / predictedSumsq;
  const intercept = realMean - slope * predictedMean;
  const rateMse = mean(rows.map((row) => (row.predicted - row.real) ** 2));
  const brier = mean(
    rows.map((row) => row.predicted ** 2 - 2 * row.predicted * row.real + row.real),
  );
  const variance = mean(rows.map((row) => row.real * (1 - row.real)));
  if (Math.abs(brier - rateMse - variance) > 1e-14) {
    throw new Error("Brier identity failed");
  }
  return {
    cell_rate_mse: rateMse,
    empirical_individual_outcome_brier: brier,
    empirical_outcome_variance_component: variance,
    calibration_in_the_large_predicted_minus_real: predictedMean - realMean,
    ols_intercept_real_on_predicted: intercept,
    ols_slope_real_on_predicted: slope,
    pearson_r: covariance / Math.sqrt(predictedSumsq * realSumsq),
  };
}

function selection(rows) {
  const policies = [...new Set(rows.map((row) => row.policy))].sort();
  const realMeans = Object.fromEntries(
    policies.map((policy) => [policy, mean(rows.filter((row) => row.policy === policy).map((row) => row.real))]),
  );
  const predictedMeans = Object.fromEntries(
    policies.map((policy) => [policy, mean(rows.filter((row) => row.policy === policy).map((row) => row.predicted))]),
  );
  return {
    real_winner: argmax(Object.entries(realMeans)),
    predicted_winner: argmax(Object.entries(predictedMeans)),
    real_means: realMeans,
    predicted_means: predictedMeans,
  };
}

function deletionRanges(rows) {
  const tasks = [...new Set(rows.map((row) => row.task))].sort();
  const deletionRows = tasks.map((task) => metrics(rows.filter((row) => row.task !== task)));
  const fields = [
    "cell_rate_mse",
    "empirical_individual_outcome_brier",
    "calibration_in_the_large_predicted_minus_real",
    "ols_intercept_real_on_predicted",
    "ols_slope_real_on_predicted",
  ];
  return Object.fromEntries(
    fields.map((field) => [
      field,
      {
        minimum: Math.min(...deletionRows.map((row) => row[field])),
        maximum: Math.max(...deletionRows.map((row) => row[field])),
      },
    ]),
  );
}

function ols(rows) {
  const current = metrics(rows);
  return [
    current.ols_intercept_real_on_predicted,
    current.ols_slope_real_on_predicted,
  ];
}

function heldoutAffine(rows) {
  const tasks = [...new Set(rows.map((row) => row.task))].sort();
  const folds = [];
  const rawErrors = [];
  const calibratedErrors = [];
  const crossfitted = [];
  for (const heldoutTask of tasks) {
    const training = rows.filter((row) => row.task !== heldoutTask);
    const heldout = rows.filter((row) => row.task === heldoutTask);
    const [intercept, slope] = ols(training);
    const currentRaw = [];
    const currentCalibrated = [];
    for (const row of heldout) {
      const recalibrated = intercept + slope * row.predicted;
      const raw = (row.predicted - row.real) ** 2;
      const calibrated = (recalibrated - row.real) ** 2;
      rawErrors.push(raw);
      calibratedErrors.push(calibrated);
      currentRaw.push(raw);
      currentCalibrated.push(calibrated);
      crossfitted.push({ policy: row.policy, task: row.task, recalibrated });
    }
    folds.push({
      heldout_task: heldoutTask,
      training_intercept: intercept,
      training_slope: slope,
      heldout_uncalibrated_rate_mse: mean(currentRaw),
      heldout_recalibrated_rate_mse: mean(currentCalibrated),
    });
  }
  const policies = [...new Set(rows.map((row) => row.policy))].sort();
  const policyMeans = Object.fromEntries(
    policies.map((policy) => [
      policy,
      mean(crossfitted.filter((row) => row.policy === policy).map((row) => row.recalibrated)),
    ]),
  );
  const ordered = Object.entries(policyMeans).sort((left, right) => right[1] - left[1]);
  return {
    folds,
    pooled_uncalibrated_rate_mse: mean(rawErrors),
    pooled_recalibrated_rate_mse: mean(calibratedErrors),
    recalibration_reduces_pooled_rate_mse: mean(calibratedErrors) < mean(rawErrors),
    heldout_tasks_improved: folds.filter(
      (fold) => fold.heldout_recalibrated_rate_mse < fold.heldout_uncalibrated_rate_mse,
    ).length,
    crossfitted_policy_means: policyMeans,
    crossfitted_winner: ordered[0][0],
    crossfitted_winner_margin: ordered[0][1] - ordered[1][1],
  };
}

function close(actual, expected, label) {
  if (Math.abs(actual - expected) > tolerance) {
    throw new Error(`${label}: ${actual} vs ${expected}`);
  }
}

function build() {
  const panels = parsePanels();
  const expected = JSON.parse(fs.readFileSync(producerResult, "utf8"));
  const outputPanels = {};
  let numericComparisons = 0;
  for (const [model, rows] of Object.entries(panels)) {
    if (rows.length !== 12) throw new Error(`${model}: cell count changed`);
    const currentMetrics = metrics(rows);
    for (const [field, value] of Object.entries(currentMetrics)) {
      close(value, expected.panels[model].metrics[field], `${model}/${field}`);
      numericComparisons += 1;
    }
    const currentSelection = selection(rows);
    if (
      currentSelection.real_winner !== expected.panels[model].selection.real_winner ||
      currentSelection.predicted_winner !== expected.panels[model].selection.predicted_winner
    ) {
      throw new Error(`${model}: winner mismatch`);
    }
    const currentRanges = deletionRanges(rows);
    for (const [field, range] of Object.entries(currentRanges)) {
      close(
        range.minimum,
        expected.panels[model].task_deletion.ranges[field].minimum,
        `${model}/${field}/min`,
      );
      close(
        range.maximum,
        expected.panels[model].task_deletion.ranges[field].maximum,
        `${model}/${field}/max`,
      );
      numericComparisons += 2;
    }
    const currentHeldout = heldoutAffine(rows);
    const expectedHeldout = expected.panels[model].task_heldout_affine_recalibration;
    if (currentHeldout.folds.length !== expectedHeldout.folds.length) {
      throw new Error(`${model}: heldout fold count`);
    }
    for (let index = 0; index < currentHeldout.folds.length; index += 1) {
      const currentFold = currentHeldout.folds[index];
      const expectedFold = expectedHeldout.folds[index];
      if (currentFold.heldout_task !== expectedFold.heldout_task) {
        throw new Error(`${model}: heldout task order`);
      }
      for (const field of [
        "training_intercept",
        "training_slope",
        "heldout_uncalibrated_rate_mse",
        "heldout_recalibrated_rate_mse",
      ]) {
        close(currentFold[field], expectedFold[field], `${model}/${currentFold.heldout_task}/${field}`);
        numericComparisons += 1;
      }
    }
    for (const field of [
      "pooled_uncalibrated_rate_mse",
      "pooled_recalibrated_rate_mse",
      "crossfitted_winner_margin",
    ]) {
      close(currentHeldout[field], expectedHeldout[field], `${model}/heldout/${field}`);
      numericComparisons += 1;
    }
    for (const [policy, value] of Object.entries(currentHeldout.crossfitted_policy_means)) {
      close(value, expectedHeldout.crossfitted_policy_means[policy], `${model}/heldout/${policy}`);
      numericComparisons += 1;
    }
    if (
      currentHeldout.recalibration_reduces_pooled_rate_mse !==
        expectedHeldout.recalibration_reduces_pooled_rate_mse ||
      currentHeldout.heldout_tasks_improved !== expectedHeldout.heldout_tasks_improved ||
      currentHeldout.crossfitted_winner !== expectedHeldout.crossfitted_winner
    ) {
      throw new Error(`${model}: heldout disposition mismatch`);
    }
    if (!(currentMetrics.ols_slope_real_on_predicted > 0)) {
      throw new Error(`${model}: nonpositive affine slope`);
    }
    const transformedMeans = Object.fromEntries(
      Object.entries(currentSelection.predicted_means).map(([policy, value]) => [
        policy,
        currentMetrics.ols_intercept_real_on_predicted +
          currentMetrics.ols_slope_real_on_predicted * value,
      ]),
    );
    if (argmax(Object.entries(transformedMeans)) !== currentSelection.predicted_winner) {
      throw new Error(`${model}: positive affine map changed winner`);
    }
    if (Math.abs(currentMetrics.cell_rate_mse - currentMetrics.empirical_individual_outcome_brier) < tolerance) {
      throw new Error(`${model}: rate MSE was mislabeled Brier`);
    }
    outputPanels[model] = {
      metrics: currentMetrics,
      selection: currentSelection,
      deletion_ranges: currentRanges,
      task_heldout_affine_recalibration: currentHeldout,
      positive_affine_winner_preserved: true,
      rate_mse_is_brier: false,
    };
  }
  return {
    schema: "wm-probability-calibration-independent-challenge-v1",
    status: "pass",
    method: "Node direct CSV reconstruction with closed-form OLS and exact task deletions; no Python import or execution",
    tolerance,
    numeric_comparisons: numericComparisons,
    panels: outputPanels,
    protocol_sha256: sha256(protocol),
    input_sha256: sha256(input),
    producer_sha256: sha256(producer),
    producer_result_sha256: sha256(producerResult),
  };
}

const args = new Set(process.argv.slice(2));
if ((args.has("--write") ? 1 : 0) + (args.has("--check") ? 1 : 0) !== 1) {
  throw new Error("choose exactly one of --write or --check");
}
const result = build();
const serialized = `${JSON.stringify(result, null, 2)}\n`;
if (args.has("--write")) {
  fs.writeFileSync(output, serialized);
  process.stdout.write(`WROTE ${output}\n`);
} else {
  if (fs.readFileSync(output, "utf8") !== serialized) {
    throw new Error("stored calibration challenge differs from recomputation");
  }
  process.stdout.write("OK: WM calibration independent challenge\n");
}
