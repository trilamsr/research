#!/usr/bin/env node
// Independent BigInt/source reconstruction of H206.

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(FAMILY, "..", "..");
const COHORT = path.join(FAMILY, "result-h187-phail-context-support-sanitized.csv");
const H202 = path.join(FAMILY, "projection-h202-phail-initial-joint-state.csv");
const PRODUCER = path.join(FAMILY, "result-h206-phail-monotonic-wall-clock-bridge.json");
const PRODUCER_PROJECTION = path.join(FAMILY, "projection-h206-phail-clock-offset-regimes.csv");
const OUTPUT = path.join(
  FAMILY,
  "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json",
);
const DEFAULT_REPOSITORY = path.join(ROOT, "work", "h198-positronic-current");
const REVISION = "e406176bc526babb06844a48e3627a5c0409eb74";
const EXPECTED_EPISODES = 594;
const PRODUCER_SHA256 = "1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19";
const PROJECTION_SHA256 = "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529";
const SOURCE_SHA256 = {
  "pimm/world.py": "cca1fbe28cd69adef15dac7c7c8a7b30386bcf9cf06d8c943b8c2d1736c5560f",
  "positronic/inference.py": "f0d9565b501b70ea15421d86b0e742a8c57d5c22446f57f36f9bd7cf79d43080",
  "positronic/dataset/ds_writer_agent.py":
    "40435c6a11cb8f75bb1dc79933da1ea8b47586cffa2988c3bf44756fb1fbe483",
  "positronic/dataset/local_dataset.py":
    "e0308688d7daa43c4c27b00a5f199ed8ffc86caaf3b6b1b2cf9177adec82e493",
  "positronic/wire.py": "586baf9bd736a623fc4b19027ea05158757f4e7e474a9f73081090a992329763",
};
const THRESHOLDS = [
  1_000_000n,
  10_000_000n,
  100_000_000n,
  1_000_000_000n,
  10_000_000_000n,
  60_000_000_000n,
  600_000_000_000n,
  3_600_000_000_000n,
  21_600_000_000_000n,
  86_400_000_000_000n,
];

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256Bytes(raw) {
  return crypto.createHash("sha256").update(raw).digest("hex");
}

function sha256File(filename) {
  return sha256Bytes(fs.readFileSync(filename));
}

function parseCsv(text) {
  const records = [];
  let record = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        quoted = false;
      } else {
        field += character;
      }
    } else if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      record.push(field);
      field = "";
    } else if (character === "\n") {
      record.push(field.replace(/\r$/, ""));
      records.push(record);
      record = [];
      field = "";
    } else {
      field += character;
    }
  }
  requireCondition(!quoted, "unterminated CSV quote");
  if (field.length || record.length) {
    record.push(field);
    records.push(record);
  }
  const header = records.shift();
  requireCondition(header && new Set(header).size === header.length, "CSV header");
  return records
    .filter((row) => row.some((value) => value !== ""))
    .map((row) => {
      requireCondition(row.length === header.length, "CSV row width");
      return Object.fromEntries(header.map((name, index) => [name, row[index]]));
    });
}

function sourceTrace(repository) {
  const isGit = fs.existsSync(path.join(repository, ".git"));
  const files = {};
  if (isGit) {
    const revision = execFileSync("git", ["-C", repository, "rev-parse", REVISION], {
      encoding: "utf8",
    }).trim();
    requireCondition(revision === REVISION, "revision");
    for (const relative of Object.keys(SOURCE_SHA256)) {
      files[relative] = execFileSync(
        "git",
        ["-C", repository, "show", `${REVISION}:${relative}`],
        { encoding: null, maxBuffer: 20 * 1024 * 1024 },
      );
    }
  } else {
    for (const relative of Object.keys(SOURCE_SHA256)) {
      files[relative] = fs.readFileSync(path.join(repository, relative));
    }
  }
  const hashes = Object.fromEntries(
    Object.entries(files).map(([relative, raw]) => [relative, sha256Bytes(raw)]),
  );
  requireCondition(JSON.stringify(hashes) === JSON.stringify(SOURCE_SHA256), "source hashes");
  const texts = Object.fromEntries(
    Object.entries(files).map(([relative, raw]) => [relative, raw.toString("utf8")]),
  );
  const controls = {
    real_inference_uses_default_world: texts["positronic/inference.py"].includes(
      "with writer_cm as dataset_writer, pimm.World() as world:",
    ),
    world_defaults_to_system_clock: texts["pimm/world.py"].includes(
      "self._clock = clock or SystemClock()",
    ),
    system_clock_is_monotonic_ns:
      texts["pimm/world.py"].includes("class SystemClock(Clock):") &&
      texts["pimm/world.py"].includes("return time.monotonic_ns()"),
    real_inference_uses_clock_mode: texts["positronic/inference.py"].includes(
      "robot_arm, gripper, gui, TimeMode.CLOCK)",
    ),
    writer_primary_time_is_world_clock:
      texts["positronic/dataset/ds_writer_agent.py"].includes(
        "world_time_ns, message_time_ns = clock.now_ns(), msg.ts",
      ) &&
      texts["positronic/dataset/ds_writer_agent.py"].includes(
        "primary_ts = world_time_ns if self._time_mode == TimeMode.CLOCK else message_time_ns",
      ),
    episode_creation_is_wall_time_ns: texts[
      "positronic/dataset/local_dataset.py"
    ].includes("'created_ts_ns': created_ts_ns or time.time_ns()"),
    robot_state_signal_binding:
      texts["positronic/wire.py"].includes(
        "ds_agent.add_signal('robot_state', Serializers.robot_state)",
      ) &&
      texts["positronic/wire.py"].includes(
        "world.connect(robot_arm.state, ds_agent.inputs['robot_state'])",
      ),
  };
  requireCondition(Object.values(controls).every(Boolean), "source semantics");
  return {
    source_mode: "hash-bound v0.2.1 source projection",
    source_sha256: hashes,
    controls,
  };
}

function labelsForThreshold(rows, threshold) {
  const labels = [0];
  for (let index = 1; index < rows.length; index += 1) {
    const gap = rows[index].offset - rows[index - 1].offset;
    labels.push(labels[index - 1] + (gap > threshold ? 1 : 0));
  }
  return labels;
}

function sortedSizes(labels) {
  const counts = new Map();
  for (const label of labels) counts.set(label, (counts.get(label) ?? 0) + 1);
  return [...counts.values()].sort((a, b) => a - b);
}

function contiguous(labels, group) {
  const positions = labels.flatMap((label, index) => (label === group ? [index] : []));
  return Math.max(...positions) - Math.min(...positions) + 1 === positions.length;
}

function counts(rows, key) {
  const output = {};
  for (const row of rows) output[row[key]] = (output[row[key]] ?? 0) + 1;
  return Object.fromEntries(Object.entries(output).sort(([a], [b]) => a.localeCompare(b)));
}

function build(repository) {
  requireCondition(sha256File(PRODUCER) === PRODUCER_SHA256, "producer hash");
  requireCondition(sha256File(PRODUCER_PROJECTION) === PROJECTION_SHA256, "projection hash");
  const producerText = fs.readFileSync(PRODUCER, "utf8");
  requireCondition(
    /"classification": "scale_separated_clock_offset_regimes"/.test(producerText),
    "producer classification",
  );
  const source = sourceTrace(repository);
  const cohort = parseCsv(fs.readFileSync(COHORT, "utf8"));
  const h202 = parseCsv(fs.readFileSync(H202, "utf8"));
  requireCondition(
    cohort.length === EXPECTED_EPISODES && h202.length === EXPECTED_EPISODES,
    "counts",
  );
  const firstById = new Map(h202.map((row) => [row.episode_id, row]));
  requireCondition(firstById.size === EXPECTED_EPISODES, "H202 identity");
  const rows = cohort.map((row) => {
    const first = firstById.get(row.episode_id);
    requireCondition(first, "join");
    const created = BigInt(row.created_ts_ns);
    const monotonic = BigInt(first.timestamp_ns);
    return {
      episode_id: row.episode_id,
      policy_model: row.policy_model,
      utc_date: row.utc_date,
      created,
      monotonic,
      offset: created - monotonic,
    };
  });
  requireCondition(new Set(rows.map((row) => row.episode_id)).size === EXPECTED_EPISODES, "cohort identity");
  const sorted = [...rows].sort((a, b) =>
    a.offset === b.offset
      ? a.episode_id.localeCompare(b.episode_id)
      : a.offset < b.offset
        ? -1
        : 1,
  );
  const gaps = sorted.slice(1).map((row, index) => row.offset - sorted[index].offset);
  const orderedGaps = [...gaps].sort((a, b) => (a < b ? 1 : a > b ? -1 : 0));
  const memberships = new Map(
    THRESHOLDS.map((threshold) => [threshold.toString(), labelsForThreshold(sorted, threshold)]),
  );
  const canonicalLabels = memberships.get("3600000000000");
  const stable = [
    1_000_000_000n,
    10_000_000_000n,
    60_000_000_000n,
    600_000_000_000n,
    3_600_000_000_000n,
    21_600_000_000_000n,
  ].every(
    (threshold) =>
      JSON.stringify(memberships.get(threshold.toString())) ===
      JSON.stringify(memberships.get("1000000000")),
  );
  const classification =
    orderedGaps[0] >= 86_400_000_000_000n &&
    orderedGaps[0] >= 1000n * orderedGaps[1] &&
    stable
      ? "scale_separated_clock_offset_regimes"
      : "challenge_classification_disagrees";
  const groupByEpisode = new Map(
    sorted.map((row, index) => [row.episode_id, canonicalLabels[index]]),
  );
  const wallOrdered = [...rows].sort((a, b) =>
    a.created === b.created
      ? a.episode_id.localeCompare(b.episode_id)
      : a.created < b.created
        ? -1
        : 1,
  );
  const idOrdered = [...rows].sort((a, b) => a.episode_id.localeCompare(b.episode_id));
  const summaries = [...new Set(canonicalLabels)].map((group) => {
    const members = rows.filter((row) => groupByEpisode.get(row.episode_id) === group);
    let discordant = 0;
    const ordered = [...members].sort((a, b) => (a.created < b.created ? -1 : 1));
    for (let first = 0; first < ordered.length; first += 1) {
      for (let second = first + 1; second < ordered.length; second += 1) {
        if (ordered[first].monotonic > ordered[second].monotonic) discordant += 1;
      }
    }
    const baseline = ordered[0];
    const discrepancies = members.map((row) => {
      const value =
        (row.created - baseline.created) - (row.monotonic - baseline.monotonic);
      return value < 0n ? -value : value;
    });
    const offsets = members.map((row) => row.offset);
    return {
      group_1h: group + 1,
      episode_count: members.length,
      offset_min_ns: offsets.reduce((a, b) => (a < b ? a : b)).toString(),
      offset_max_ns: offsets.reduce((a, b) => (a > b ? a : b)).toString(),
      maximum_elapsed_time_discrepancy_ns: discrepancies
        .reduce((a, b) => (a > b ? a : b))
        .toString(),
      wall_monotonic_discordant_pairs: discordant,
      policy_counts: counts(members, "policy_model"),
      utc_date_counts: counts(members, "utc_date"),
      contiguous_in_wall_clock_order: contiguous(
        wallOrdered.map((row) => groupByEpisode.get(row.episode_id)),
        group,
      ),
      contiguous_in_episode_id_order: contiguous(
        idOrdered.map((row) => groupByEpisode.get(row.episode_id)),
        group,
      ),
    };
  });

  const header = [
    "offset_rank",
    "episode_id",
    "policy_model",
    "utc_date",
    "created_ts_ns",
    "first_timestamp_ns",
    "offset_ns",
    "gap_from_previous_ns",
    "group_1h",
  ];
  const lines = [header.join(",")];
  sorted.forEach((row, index) => {
    lines.push(
      [
        index + 1,
        row.episode_id,
        row.policy_model,
        row.utc_date,
        row.created.toString(),
        row.monotonic.toString(),
        row.offset.toString(),
        index === 0 ? "" : gaps[index - 1].toString(),
        canonicalLabels[index] + 1,
      ].join(","),
    );
  });
  const projectionBytes = Buffer.from(`${lines.join("\n")}\n`);
  requireCondition(sha256Bytes(projectionBytes) === PROJECTION_SHA256, "exact projection reconstruction");
  requireCondition(projectionBytes.equals(fs.readFileSync(PRODUCER_PROJECTION)), "projection bytes");

  return {
    schema: "h206-node-bigint-independent-challenge-v1",
    method:
      "Node BigInt exact CSV/source reconstruction with independent grouping, inversion, and projection code",
    node_version: process.version,
    producer_result_sha256: sha256File(PRODUCER),
    producer_projection_sha256: sha256File(PRODUCER_PROJECTION),
    source_trace: source,
    episode_count: rows.length,
    largest_adjacent_gap_ns: orderedGaps[0].toString(),
    second_largest_adjacent_gap_ns: orderedGaps[1].toString(),
    threshold_group_sizes: Object.fromEntries(
      THRESHOLDS.map((threshold) => [
        threshold.toString(),
        sortedSizes(memberships.get(threshold.toString())),
      ]),
    ),
    one_hour_groups: summaries,
    independent_classification: classification,
    exact_projection_reconstruction: true,
    performance_or_later_state_opened: false,
    host_or_session_identity_established: false,
    dependence_cluster_established: false,
    result: "pass",
  };
}

const args = process.argv.slice(2);
const check = args.includes("--check");
const repositoryIndex = args.indexOf("--repository");
const repository =
  repositoryIndex >= 0 ? path.resolve(args[repositoryIndex + 1]) : DEFAULT_REPOSITORY;
const candidate = build(repository);
const serialized = `${JSON.stringify(candidate, null, 2)}\n`;
if (check) {
  requireCondition(fs.readFileSync(OUTPUT, "utf8") === serialized, "challenge exact rebuild");
  process.stdout.write("OK: H206 independent BigInt challenge reproduces\n");
} else {
  fs.writeFileSync(OUTPUT, serialized);
  process.stdout.write(serialized);
}
