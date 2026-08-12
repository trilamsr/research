#!/usr/bin/env python3
"""Run H251's aggregate, privacy-preserving three-source P2 application."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import itertools
import json
import math
import re
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import yaml


FAMILY = Path(__file__).resolve().parent
PROJECT = FAMILY.parent.parent
PROTOCOL = FAMILY / "protocol-h251-three-source-real-record-application.md"
SOURCES = FAMILY / "sources" / "h251"
DEFAULT_OUTPUT = FAMILY / "result-h251-three-source-real-record-application.json"
ROBOARENA_REVISION = "7931db81f3f6a48a3245427f7213a4c461f92ccc"
ANKILE = {
    "routing": {
        "repo_id": "ankile/real01b-routing-d1-r5-threearm-checkpoint100000-iql-g0997-n16-heldout-sobol50",
        "revision": "15d419013006f1e3e8363abbf95650f212eb77f6",
    },
    "marker": {
        "repo_id": "ankile/real01b-marker-d2-r5-trio-baseline-dp-iql-cfinal-n16-heval-sobolseed2026070704",
        "revision": "cd5d0df42a622bcaad2b2a338396d4b6851cab9e",
    },
    "square": {
        "repo_id": "ankile/real01b-square-d2-r5-trio-baseline-dp-iql-s3fixfinal-n16-heval-sobolseed2026070901",
        "revision": "d2d109029967c27fad4e09637206cfe7614ff3de",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def components(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[list[str]]:
    graph = {node: set() for node in nodes}
    for left, right in edges:
        require(left in graph and right in graph and left != right, "invalid graph edge")
        graph[left].add(right)
        graph[right].add(left)
    seen: set[str] = set()
    result: list[list[str]] = []
    for start in sorted(graph):
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        group = []
        while queue:
            node = queue.popleft()
            group.append(node)
            for neighbor in sorted(graph[node]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        result.append(sorted(group))
    return sorted(result, key=lambda group: (-len(group), group))


def anonymized_policy_label(task: str, policy_id: int) -> str:
    return f"{task}-P{policy_id}"


def minimum_round_replacements(
    values: dict[tuple[int, int], int],
    states: list[int],
    winner: int,
    challenger: int,
    required_margin_reduction: int,
) -> int:
    """Fewest matched rounds whose arbitrary binary replacement can cut a margin."""
    require(required_margin_reduction > 0, "replacement target must be positive")
    reductions = sorted(
        (values[(winner, state)] - values[(challenger, state)] + 1 for state in states),
        reverse=True,
    )
    cumulative = 0
    for count, reduction in enumerate(reductions, start=1):
        cumulative += reduction
        if cumulative >= required_margin_reduction:
            return count
    raise ValueError("replacement target is unreachable")


def analyze_ankile_task(task: str, spec: dict[str, str]) -> dict[str, Any]:
    root = SOURCES / "ankile" / task
    result = json.loads((root / "results.json").read_text())
    manifest = json.loads((root / "meta" / "initial_states_manifest.json").read_text())
    lineage = json.loads((root / "meta" / "dataset_lineage.json").read_text())
    info = json.loads((root / "meta" / "info.json").read_text())

    require(result.get("args", {}).get("hf_repo_id") == spec["repo_id"], f"{task}: repo mismatch")
    require(lineage.get("repo_id") == spec["repo_id"], f"{task}: lineage repo mismatch")
    require(lineage.get("trainable") is False, f"{task}: evaluation lineage not marked nontrainable")
    require(info.get("total_episodes") == 150, f"{task}: unexpected episode total")

    states = manifest.get("states")
    require(isinstance(states, list) and len(states) == 50, f"{task}: expected 50 states")
    state_ids = [state.get("manifest_idx") for state in states]
    require(state_ids == list(range(50)), f"{task}: manifest indices are not 0..49")

    summary = result.get("summary")
    require(isinstance(summary, list) and len(summary) == 3, f"{task}: expected three policies")
    policy_ids = sorted(row.get("policy_id") for row in summary)
    require(policy_ids == [0, 1, 2], f"{task}: policy IDs are not 0,1,2")
    names = {row["policy_id"]: row["name"] for row in summary}
    artifacts = {row["policy_id"]: row["artifact"] for row in summary}
    require(len(set(artifacts.values())) == 3, f"{task}: policy artifacts are not distinct")

    rollouts = result.get("rollouts")
    require(isinstance(rollouts, list) and len(rollouts) == 150, f"{task}: expected 150 rollouts")
    values: dict[tuple[int, int], int] = {}
    label_counts = Counter()
    for row in rollouts:
        policy_id = row.get("policy_id")
        state_id = row.get("manifest_idx")
        outcome = row.get("outcome")
        require(policy_id in policy_ids and state_id in state_ids, f"{task}: invalid rollout key")
        require(outcome in {"success", "failure", "timeout"}, f"{task}: invalid outcome {outcome!r}")
        key = (policy_id, state_id)
        require(key not in values, f"{task}: duplicate policy-state key {key}")
        values[key] = int(outcome == "success")
        label_counts[outcome] += 1
    expected_keys = set(itertools.product(policy_ids, state_ids))
    require(set(values) == expected_keys, f"{task}: incomplete policy-state rectangle")

    round_plans = result.get("round_plans")
    require(isinstance(round_plans, list) and len(round_plans) == 50, f"{task}: expected 50 round plans")
    order_counts = Counter()
    round_to_state: dict[int, int] = {}
    for plan in round_plans:
        round_id = plan.get("round")
        state_id = plan.get("manifest_idx")
        require(round_id not in round_to_state and state_id in state_ids, f"{task}: invalid round plan")
        round_to_state[round_id] = state_id
        order = tuple(slot.get("policy_id") for slot in plan.get("policy_order", []))
        require(sorted(order) == policy_ids, f"{task}: incomplete policy order")
        order_counts[order] += 1
    for row in rollouts:
        require(round_to_state.get(row.get("round")) == row.get("manifest_idx"), f"{task}: rollout/round mismatch")

    policy_results = []
    success_counts: dict[int, int] = {}
    for policy_id in policy_ids:
        count = sum(values[(policy_id, state_id)] for state_id in state_ids)
        success_counts[policy_id] = count
        summary_row = next(row for row in summary if row["policy_id"] == policy_id)
        require(summary_row.get("successes") == count, f"{task}: summary success mismatch")
        require(summary_row.get("num_rounds") == 50, f"{task}: summary round mismatch")
        require(math.isclose(summary_row.get("success_rate"), count / 50, abs_tol=1e-12), f"{task}: rate mismatch")
        policy_results.append(
            {
                "policy": anonymized_policy_label(task, policy_id),
                "source_policy_name": names[policy_id],
                "source_artifact": artifacts[policy_id],
                "successes": count,
                "trials": 50,
                "success_rate": count / 50,
            }
        )

    edge_results = []
    graph_edges = []
    for left, right in itertools.combinations(policy_ids, 2):
        left_wins = ties = right_wins = 0
        for state_id in state_ids:
            a, b = values[(left, state_id)], values[(right, state_id)]
            if a > b:
                left_wins += 1
            elif a < b:
                right_wins += 1
            else:
                ties += 1
        score = (left_wins + 0.5 * ties) / len(state_ids)
        require(
            math.isclose(2 * score - 1, success_counts[left] / 50 - success_counts[right] / 50, abs_tol=1e-12),
            f"{task}: shared-success edge identity failed",
        )
        left_label = anonymized_policy_label(task, left)
        right_label = anonymized_policy_label(task, right)
        graph_edges.append((left_label, right_label))
        edge_results.append(
            {
                "left": left_label,
                "right": right_label,
                "left_wins": left_wins,
                "ties": ties,
                "right_wins": right_wins,
                "half_credit_score_left": score,
            }
        )

    maximum = max(success_counts.values())
    winner_set = [anonymized_policy_label(task, policy_id) for policy_id in policy_ids if success_counts[policy_id] == maximum]
    require(len(winner_set) == 1, f"{task}: replacement sensitivity requires a unique released winner")
    winner_id = next(policy_id for policy_id in policy_ids if success_counts[policy_id] == maximum)
    runner_up_id = max((policy_id for policy_id in policy_ids if policy_id != winner_id), key=success_counts.__getitem__)
    require(
        sum(success_counts[policy_id] == success_counts[runner_up_id] for policy_id in policy_ids) == 1,
        f"{task}: replacement sensitivity requires a unique runner-up",
    )
    margin = success_counts[winner_id] - success_counts[runner_up_id]
    remove_winner_rounds = minimum_round_replacements(values, state_ids, winner_id, runner_up_id, margin)
    reverse_winner_rounds = minimum_round_replacements(values, state_ids, winner_id, runner_up_id, margin + 1)
    labels = [anonymized_policy_label(task, policy_id) for policy_id in policy_ids]
    groups = components(labels, graph_edges)
    require(len(groups) == 1 and len(graph_edges) == 3, f"{task}: complete route graph not recovered")

    return {
        "source": {**spec, "license": "Apache-2.0"},
        "released_finite_panel": {
            "physical_task": manifest.get("task"),
            "states": 50,
            "policies": 3,
            "rollouts": 150,
            "complete_policy_state_rectangle": True,
            "terminal_label_counts": dict(sorted(label_counts.items())),
            "success_encoding": {"success": 1, "failure": 0, "timeout": 0},
            "policy_results": policy_results,
            "pair_results": edge_results,
            "winner_set": winner_set,
            "winner_margin_successes_over_second": margin,
            "retention_sensitivity": {
                "closest_challenger": anonymized_policy_label(task, runner_up_id),
                "minimum_matched_round_replacements_to_remove_unique_winner": remove_winner_rounds,
                "minimum_matched_round_replacements_to_reverse_winner": reverse_winner_rounds,
                "scope": "fixed 50-state panel; an affected retained round may be replaced by any three-policy binary outcome vector",
                "warning": "worst-case sensitivity only; it is not evidence that any released round was replaced or selected using outcomes",
            },
        },
        "route_graph": {
            "edges": len(graph_edges),
            "possible_edges": 3,
            "components": groups,
            "connected": True,
        },
        "execution_record": {
            "single_arena_session_id_present": bool(result.get("arena_session_id")),
            "all_rounds_submitted": sorted(result.get("arena_submitted_round_indices", [])) == list(range(50)),
            "round_policy_order_counts": {
                "-".join(str(value) for value in order): count for order, count in sorted(order_counts.items())
            },
            "randomized_order_declared": result.get("args", {}).get("random_arena_selection") == "uniform",
            "reset_retry_configuration_present": "reset_max_retries" in result.get("args", {}),
            "rerun_incomplete_rounds": result.get("args", {}).get("rerun_incomplete_rounds"),
            "attempt_or_retry_ledger_present": False,
            "achieved_reset_acceptance_record_present": False,
        },
        "interpretation": "exact released 50-state finite panel; no population or deployment inference",
    }


def normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def support_summary(values: list[int]) -> dict[str, Any]:
    require(values, "empty edge-support list")
    ordered = sorted(values)
    return {
        "minimum": ordered[0],
        "median": statistics.median(ordered),
        "maximum": ordered[-1],
        "edges_with_one_session": sum(value == 1 for value in ordered),
        "edges_with_at_least_10_sessions": sum(value >= 10 for value in ordered),
        "edges_with_at_least_50_sessions": sum(value >= 50 for value in ordered),
    }


def analyze_roboarena(root: Path) -> dict[str, Any]:
    paths = sorted(root.glob("evaluation_sessions/*/metadata.yaml"))
    require(len(paths) == 3883, f"RoboArena: expected 3883 metadata files, got {len(paths)}")
    nodes: set[str] = set()
    edge_counts: Counter[tuple[str, str]] = Counter()
    set_sizes = Counter()
    top_keys: set[str] = set()
    policy_keys: set[str] = set()
    preference_present = 0
    proxy_graphs: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    proxy_nodes: dict[tuple[str, str], set[str]] = defaultdict(set)

    for path in paths:
        row = yaml.safe_load(path.read_text())
        require(isinstance(row, dict), "RoboArena: metadata root is not a mapping")
        top_keys.update(row)
        policy_map = row.get("policies")
        require(isinstance(policy_map, dict), "RoboArena: policies is not a mapping")
        policies = []
        for policy_row in policy_map.values():
            require(isinstance(policy_row, dict), "RoboArena: invalid policy record")
            policy_keys.update(policy_row)
            name = str(policy_row.get("policy_name") or "").strip()
            require(name, "RoboArena: missing policy name")
            policies.append(name)
        require(len(policies) == len(set(policies)), "RoboArena: duplicate policy in session")
        unique = sorted(set(policies))
        set_sizes[len(unique)] += 1
        nodes.update(unique)
        session_edges = set(itertools.combinations(unique, 2))
        edge_counts.update(session_edges)
        if row.get("preference") in {"A", "B", "TIE"}:
            preference_present += 1

        proxy = (normalized_text(row.get("evaluation_location")), normalized_text(row.get("language_instruction")))
        proxy_nodes[proxy].update(unique)
        proxy_graphs[proxy].update(session_edges)

    groups = components(nodes, edge_counts)
    paired_nodes = {node for edge in edge_counts for node in edge}
    paired_groups = components(paired_nodes, edge_counts)
    possible_edges = len(nodes) * (len(nodes) - 1) // 2
    three_plus = connected_three_plus = 0
    for proxy, proxy_node_set in proxy_nodes.items():
        if len(proxy_node_set) < 3:
            continue
        three_plus += 1
        if len(components(proxy_node_set, proxy_graphs[proxy])) == 1:
            connected_three_plus += 1

    expected_top = {
        "evaluation_location",
        "evaluator_name",
        "language_instruction",
        "longform_feedback",
        "policies",
        "preference",
        "session_completion_timestamp",
        "session_creation_timestamp",
    }
    expected_policy = {"binary_success", "duration", "partial_success", "policy_name"}
    require(top_keys == expected_top, f"RoboArena: unexpected top-level schema {sorted(top_keys)}")
    require(policy_keys == expected_policy, f"RoboArena: unexpected policy schema {sorted(policy_keys)}")

    return {
        "source": {
            "repo_id": "RoboArena/DataDump_07-17-2026",
            "revision": ROBOARENA_REVISION,
            "license": "MIT",
        },
        "sessions": len(paths),
        "sessions_by_distinct_policy_count": {str(key): value for key, value in sorted(set_sizes.items())},
        "preference_records_with_declared_value": preference_present,
        "policy_cooccurrence_graph": {
            "policies": len(nodes),
            "observed_edges": len(edge_counts),
            "possible_edges": possible_edges,
            "unobserved_edges": possible_edges - len(edge_counts),
            "components": groups,
            "connected": len(groups) == 1,
            "pair_eligible_policies": len(paired_nodes),
            "pair_eligible_components": paired_groups,
            "pair_eligible_subgraph_connected": len(paired_groups) == 1,
            "policies_never_observed_with_another_policy": len(nodes - paired_nodes),
            "session_support": support_summary(list(edge_counts.values())),
        },
        "location_instruction_proxy": {
            "distinct_proxy_strata": len(proxy_nodes),
            "strata_with_at_least_three_policies": three_plus,
            "connected_strata_among_those": connected_three_plus,
            "warning": "location/instruction is not an exact physical context or reset",
        },
        "observed_schema": {
            "top_level_keys": sorted(top_keys),
            "policy_keys": sorted(policy_keys),
            "missing_for_common_context_or_lifecycle_join": [
                "assignment_probability_or_pool_epoch",
                "exact_initial_state_id",
                "reset_or_accepted_state_id",
                "robot_instance_id",
                "retry_parent_or_complete_attempt_ledger",
            ],
        },
        "interpretation": "policy-only graph support under pair-specific sessions; not a common-context route graph or global target ranking",
        "privacy": {
            "row_level_output": False,
            "evaluator_names_output": False,
            "instructions_output": False,
            "feedback_output": False,
            "session_ids_output": False,
        },
    }


def parse_array_with_repair(value: str) -> tuple[list[Any], bool]:
    repaired = value.startswith("[") and value.endswith("]'")
    cleaned = value[:-1] if repaired else value
    parsed = ast.literal_eval(cleaned)
    require(isinstance(parsed, list), "TRI: outcome field is not a list")
    return parsed, repaired


def parse_array(value: str) -> list[Any]:
    return parse_array_with_repair(value)[0]


def analyze_tri(root: Path) -> dict[str, Any]:
    csv_paths = sorted(root.glob("*.csv"))
    require(len(csv_paths) == 20, f"TRI: expected 20 CSVs, got {len(csv_paths)}")
    row_count = hardware_rows = 0
    listed_rollouts = hardware_listed_rollouts = 0
    raw_array_rows = aggregate_only_rows = 0
    binary_rows = progress_rows = 0
    binary_length_mismatches = binary_count_mismatches = binary_rate_mismatches = 0
    progress_length_mismatches = progress_bin_mismatches = progress_mean_mismatches = 0
    aggregate_rate_mismatches = 0
    trailing_apostrophe_repairs = 0
    all_columns: set[str] = set()
    schema_counts = Counter()
    files = {}

    for path in csv_paths:
        file_rows = file_hw = 0
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            require(reader.fieldnames is not None, f"TRI: {path.name} has no header")
            all_columns.update(reader.fieldnames)
            schema_counts["|".join(reader.fieldnames)] += 1
            for row in reader:
                row_count += 1
                file_rows += 1
                panel = row.get("Panel", "")
                is_hardware = "_HW_" in panel
                hardware_rows += int(is_hardware)
                file_hw += int(is_hardware)
                n = int(float(row["Num_Rollouts"]))
                require(n >= 0, "TRI: negative rollout count")
                listed_rollouts += n
                hardware_listed_rollouts += n if is_hardware else 0

                if row.get("Success/Failure", "").strip():
                    binary_rows += 1
                    raw_array_rows += 1
                    values, repaired = parse_array_with_repair(row["Success/Failure"])
                    trailing_apostrophe_repairs += int(repaired)
                    require(all(isinstance(value, bool) for value in values), "TRI: non-binary success array")
                    observed = sum(values)
                    binary_length_mismatches += int(len(values) != n)
                    binary_count_mismatches += int(observed != int(float(row["Num_Successes"])))
                    binary_rate_mismatches += int(
                        not math.isclose(observed / n if n else 0.0, float(row["Success_Rate"]), abs_tol=5e-10)
                    )
                elif row.get("Task_Progress_Results", "").strip():
                    progress_rows += 1
                    raw_array_rows += 1
                    raw_values, repaired_values = parse_array_with_repair(row["Task_Progress_Results"])
                    raw_bins, repaired_bins = parse_array_with_repair(row["Task_Progress_Bins"])
                    trailing_apostrophe_repairs += int(repaired_values) + int(repaired_bins)
                    values = [float(value) for value in raw_values]
                    bins = [float(value) for value in raw_bins]
                    observed_mean = statistics.fmean(values) if values else 0.0
                    progress_length_mismatches += int(len(values) != n)
                    progress_bin_mismatches += int(len(bins) != int(float(row["Num_Milestones"])) + 1)
                    progress_mean_mismatches += int(
                        not math.isclose(observed_mean, float(row["Avg_Task_Progress"]), abs_tol=5e-9)
                    )
                else:
                    aggregate_only_rows += 1
                    require("Num_Successes" in row and "Success_Rate" in row, "TRI: unknown aggregate schema")
                    successes = int(float(row["Num_Successes"]))
                    aggregate_rate_mismatches += int(
                        not math.isclose(successes / n if n else 0.0, float(row["Success_Rate"]), abs_tol=5e-10)
                    )
        files[path.name] = {"rows": file_rows, "hardware_rows": file_hw}

    require(trailing_apostrophe_repairs == 3, "TRI: unexpected source-format repair count")
    mismatch_total = sum(
        (
            binary_length_mismatches,
            binary_count_mismatches,
            binary_rate_mismatches,
            progress_length_mismatches,
            progress_bin_mismatches,
            progress_mean_mismatches,
            aggregate_rate_mismatches,
        )
    )
    missing_join_fields = [
        "bundle_id",
        "trial_or_rollout_id",
        "initial_condition_id",
        "realized_policy_order",
        "reset_id_or_acceptance",
        "session_or_robot_id",
        "operator_id",
        "retry_or_exclusion_lineage",
        "immutable_policy_version",
    ]
    require(not any(field in all_columns for field in missing_join_fields), "TRI: expected missing join field appeared")

    return {
        "source": {
            "doi": "10.5061/dryad.xd2547dxc",
            "dryad_version": 4,
            "dryad_version_id": 435338,
            "publication_date": "2026-04-07",
            "license": "CC0-1.0",
        },
        "release_structure": {
            "csv_files": len(csv_paths),
            "rows": row_count,
            "hardware_rows": hardware_rows,
            "raw_outcome_array_rows": raw_array_rows,
            "aggregate_only_rows": aggregate_only_rows,
            "binary_rows": binary_rows,
            "progress_rows": progress_rows,
            "sum_of_reported_row_rollout_counts": listed_rollouts,
            "sum_for_hardware_rows": hardware_listed_rollouts,
            "warning": "row rollout sums are not unique-rollout counts because figures and metrics can reuse evaluations",
            "files": files,
        },
        "integrity": {
            "binary_array_length_mismatches": binary_length_mismatches,
            "binary_success_count_mismatches": binary_count_mismatches,
            "binary_success_rate_mismatches": binary_rate_mismatches,
            "progress_array_length_mismatches": progress_length_mismatches,
            "progress_bin_count_mismatches": progress_bin_mismatches,
            "progress_mean_mismatches": progress_mean_mismatches,
            "aggregate_only_rate_mismatches": aggregate_rate_mismatches,
            "total_reconciliation_mismatches": mismatch_total,
            "trailing_apostrophe_cells_repaired": trailing_apostrophe_repairs,
            "schema_variants": len(schema_counts),
            "observed_columns": sorted(all_columns),
        },
        "matched_bundle_join": {
            "source_described_in_paper": True,
            "paper_url": "https://arxiv.org/html/2507.05331v1#S4.SS1.SSS1",
            "public_csv_join_reconstructable": False,
            "missing_fields": missing_join_fields,
        },
        "interpretation": "published outcome arrays with two rate inconsistencies and no public trial-level key for reconstructing matched bundles or route edges",
        "performance_analysis_authorized": False,
        "narrowing_reason": "structural contrast only: matched-bundle join is absent and two released success rates disagree with their arrays and counts",
    }


def used_source_files() -> list[Path]:
    paths = [SOURCES / "README.md", SOURCES / "tri" / "dryad-v4.zip", SOURCES / "tri" / "files" / "README.md"]
    paths.extend(sorted((SOURCES / "tri" / "files").glob("*.csv")))
    for task in ANKILE:
        root = SOURCES / "ankile" / task
        paths.extend(
            [
                root / "README.md",
                root / "results.json",
                root / "meta" / "info.json",
                root / "meta" / "dataset_lineage.json",
                root / "meta" / "initial_states_manifest.json",
            ]
        )
    require(all(path.is_file() for path in paths), "one or more retained source files are missing")
    return sorted(set(paths))


def build_result(roboarena_root: Path) -> dict[str, Any]:
    source_manifest = [
        {"path": str(path.relative_to(PROJECT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in used_source_files()
    ]
    return {
        "schema": "h251-three-source-real-record-application-v1",
        "status": "exploratory_outcome_exposed",
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__)),
        "source_manifest": source_manifest,
        "ankile": {task: analyze_ankile_task(task, spec) for task, spec in ANKILE.items()},
        "roboarena": analyze_roboarena(roboarena_root),
        "tri": analyze_tri(SOURCES / "tri" / "files"),
        "cross_source_conclusion": {
            "ankile": "positive exact finite-panel common-state comparison",
            "roboarena": "connected policy co-occurrence does not supply a common-context target law",
            "tri": "strong source-described matched protocol is not reconstructable from released outcome arrays",
            "deployment_or_population_claim": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--roboarena-root",
        required=True,
        type=Path,
        help="Pinned RoboArena snapshot root containing evaluation_sessions/.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result(args.roboarena_root)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(args.output.read_text() == rendered, "canonical H251 result differs from regeneration")
    else:
        args.output.write_text(rendered)
    print("OK: H251 three-source analysis passed")


if __name__ == "__main__":
    main()
