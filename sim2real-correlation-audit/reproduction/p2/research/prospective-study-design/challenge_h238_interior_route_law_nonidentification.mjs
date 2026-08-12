#!/usr/bin/env node
// Method-distinct exact challenge for H238. Does not import or execute Python.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const protocol = path.join(here, "protocol-h238-interior-route-law-nonidentification.md");
const repairProtocol = path.join(here, "protocol-h238-challenge-repair-2026-07-31.md");
const producer = path.join(here, "interior_route_law_nonidentification.py");
const producerResult = path.join(
  here,
  "result-h238-interior-route-law-nonidentification.json",
);
const output = path.join(
  here,
  "result-h238-interior-route-law-nonidentification-independent-challenge.json",
);

function gcd(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y !== 0n) {
    [x, y] = [y, x % y];
  }
  return x;
}

function frac(n, d = 1n) {
  if (d === 0n) throw new Error("zero denominator");
  let nn = BigInt(n);
  let dd = BigInt(d);
  if (dd < 0n) {
    nn = -nn;
    dd = -dd;
  }
  const g = gcd(nn, dd);
  return [nn / g, dd / g];
}

function add(a, b) {
  return frac(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
}

function sub(a, b) {
  return frac(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
}

function mul(a, b) {
  return frac(a[0] * b[0], a[1] * b[1]);
}

function div(a, b) {
  return frac(a[0] * b[1], a[1] * b[0]);
}

function cmp(a, b) {
  const delta = a[0] * b[1] - b[0] * a[1];
  return delta < 0n ? -1 : delta > 0n ? 1 : 0;
}

function maxFrac(values) {
  return values.reduce((best, value) => (cmp(value, best) > 0 ? value : best));
}

function eq(a, b) {
  return cmp(a, b) === 0;
}

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function profiles(k, denominator) {
  const rows = [];
  function extend(prefix, lower) {
    if (prefix.length === k) {
      rows.push(prefix);
      return;
    }
    for (let value = lower; value <= denominator; value += 1) {
      extend([...prefix, value], value);
    }
  }
  extend([0], 0);
  return rows;
}

function lotteries(k) {
  const triangular = (k * (k + 1)) / 2;
  return [
    Array.from({ length: k }, () => frac(1n, BigInt(k))),
    [frac(1n), ...Array.from({ length: k - 1 }, () => frac(0n))],
    Array.from(
      { length: k },
      (_, index) => frac(BigInt(index + 1), BigInt(triangular)),
    ),
  ];
}

function canBeUniqueWinner(profile, winner, denominator) {
  const bestOther = Math.max(
    ...profile.filter((_, index) => index !== winner),
  );
  return profile[winner] + denominator > bestOther;
}

function formulaRegret(profile, denominator, lottery) {
  const a = profile.map((value) => frac(BigInt(value), BigInt(denominator)));
  let weighted = frac(0n);
  for (let index = 0; index < a.length; index += 1) {
    weighted = add(weighted, mul(lottery[index], a[index]));
  }
  const support = maxFrac(a.map((value, index) => sub(value, lottery[index])));
  return mul(frac(1n, 4n), add(sub(frac(1n), weighted), support));
}

function enumeratedRegret(profile, denominator, lottery) {
  const k = profile.length;
  const a = profile.map((value) => frac(BigInt(value), BigInt(denominator)));
  let worst = frac(0n);
  for (let mask = 0; mask < 2 ** k; mask += 1) {
    const values = a.map((value, index) =>
      add(value, frac((mask >> index) & 1)),
    );
    const best = maxFrac(values);
    let mixture = frac(0n);
    for (let index = 0; index < k; index += 1) {
      mixture = add(mixture, mul(lottery[index], values[index]));
    }
    const regret = mul(frac(1n, 4n), sub(best, mixture));
    if (cmp(regret, worst) > 0) worst = regret;
  }
  return worst;
}

function pairInterval(observed) {
  return [div(observed, frac(2n)), div(add(observed, frac(1n)), frac(2n))];
}

function mutationControls() {
  const rejected = [];
  const mutationProfile = [0, 1, 4];
  const mutationLottery = [frac(1n, 2n), frac(1n, 3n), frac(1n, 6n)];
  const correct = formulaRegret(mutationProfile, 5, mutationLottery);
  const a = mutationProfile.map((value) => frac(BigInt(value), 5n));
  const removedWeightedTerm = mul(
    frac(1n, 4n),
    add(frac(1n), maxFrac(a.map((value, index) => sub(value, mutationLottery[index])))),
  );
  if (eq(correct, removedWeightedTerm)) {
    throw new Error("removed-p-dot-a mutation was not rejected");
  }
  rejected.push("remove_p_dot_a_from_regret");

  const boundaryProfile = [0, 2, 5];
  const width = Math.max(...boundaryProfile) - Math.min(...boundaryProfile);
  if (width <= 5 && width < 5) {
    throw new Error("non-strict-interior mutation was not rejected");
  }
  rejected.push("replace_D_lt_1_with_D_le_1");

  const observed = frac(1n, 4n);
  const actualInterval = pairInterval(observed);
  const mutatedInterval = [
    actualInterval[0],
    add(actualInterval[0], frac(2n, 5n)),
  ];
  if (
    eq(actualInterval[0], mutatedInterval[0]) &&
    eq(actualInterval[1], mutatedInterval[1])
  ) {
    throw new Error("wrong-interval-width mutation was not rejected");
  }
  rejected.push("replace_interval_width_half_with_two_fifths");

  if (canBeUniqueWinner(boundaryProfile, 0, 5)) {
    throw new Error("boundary-minimum-winner mutation was not rejected");
  }
  rejected.push("claim_boundary_minimum_is_unique_winner");
  return rejected;
}

function build() {
  const denominator = 5;
  const rows = [];
  let totalProfiles = 0;
  let interiorProfiles = 0;
  let boundaryProfiles = 0;
  let interiorWinnerChecks = 0;
  let boundaryMinimumExclusions = 0;
  let regretChecks = 0;

  for (let k = 3; k <= 6; k += 1) {
    let kInterior = 0;
    let kBoundary = 0;
    const current = profiles(k, denominator);
    for (const profile of current) {
      totalProfiles += 1;
      const width = Math.max(...profile) - Math.min(...profile);
      if (width < denominator) {
        for (let winner = 0; winner < k; winner += 1) {
          if (!canBeUniqueWinner(profile, winner, denominator)) {
            throw new Error("interior winner witness failed");
          }
          interiorWinnerChecks += 1;
        }
        interiorProfiles += 1;
        kInterior += 1;
      } else {
        const minimum = Math.min(...profile);
        for (let winner = 0; winner < k; winner += 1) {
          if (profile[winner] === minimum) {
            if (canBeUniqueWinner(profile, winner, denominator)) {
              throw new Error("boundary minimum became unique");
            }
            boundaryMinimumExclusions += 1;
          }
        }
        boundaryProfiles += 1;
        kBoundary += 1;
      }

      for (const lottery of lotteries(k)) {
        if (
          !eq(
            formulaRegret(profile, denominator, lottery),
            enumeratedRegret(profile, denominator, lottery),
          )
        ) {
          throw new Error("regret formula mismatch");
        }
        regretChecks += 1;
      }
    }
    rows.push({
      k,
      profiles: current.length,
      interior_profiles: kInterior,
      boundary_profiles: kBoundary,
    });
  }

  const observedKnownAnswers = [
    frac(0n),
    frac(1n, 4n),
    frac(1n, 2n),
    frac(3n, 4n),
    frac(1n),
  ];
  for (const observed of observedKnownAnswers) {
    const [low, high] = pairInterval(observed);
    if (!eq(sub(high, low), frac(1n, 2n))) {
      throw new Error("pair interval width changed");
    }
    const straddles = cmp(low, frac(1n, 2n)) < 0 && cmp(high, frac(1n, 2n)) > 0;
    const interior = cmp(observed, frac(0n)) > 0 && cmp(observed, frac(1n)) < 0;
    if (straddles !== interior) throw new Error("pair interval boundary changed");
  }

  const rejectedMutations = mutationControls();

  return {
    schema: "h238-interior-route-law-independent-challenge-v1",
    status: "pass",
    classification: "relative_open_within_additive_shared_success_model",
    method: "exact Node BigInt rational census; no Python import or execution",
    denominator,
    rows,
    total_profiles: totalProfiles,
    interior_profiles: interiorProfiles,
    boundary_profiles: boundaryProfiles,
    interior_unique_winner_checks: interiorWinnerChecks,
    boundary_minimum_policy_exclusions: boundaryMinimumExclusions,
    regret_formula_vertex_checks: regretChecks,
    pair_interval_known_answers: observedKnownAnswers.length,
    mutation_controls_rejected: rejectedMutations.length,
    mutation_controls_rejected_names: rejectedMutations,
    runtime: {
      node: process.version,
      platform: process.platform,
      architecture: process.arch,
    },
    protocol_sha256: sha256(protocol),
    repair_protocol_sha256: sha256(repairProtocol),
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
    throw new Error("stored H238 independent challenge differs from recomputation");
  }
  process.stdout.write("OK: H238 independent Node challenge\n");
}
