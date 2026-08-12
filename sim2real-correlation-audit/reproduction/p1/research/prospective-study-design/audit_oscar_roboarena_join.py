#!/usr/bin/env python3
"""Join OSCAR release session IDs to RoboArena metadata without row disclosure.

The OSCAR release exposes paired videos under session/policy paths but no
outcome or task table.  This audit checks whether those opaque session IDs
resolve against a pinned RoboArena dump and writes only aggregate coverage and
policy-level binary-success summaries.  It never writes session IDs,
instructions, evaluator identifiers, feedback, or row-level outcomes.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from huggingface_hub import HfApi, hf_hub_download


OSCAR_REPO = "zywu2115/OSCAR_policy_rollout"
ROBOARENA_REPO = "RoboArena/DataDump_08-05-2025"
OSCAR_REVISION = "db5edfaef285c15d0a41d5115177a983c08b4f5f"
ROBOARENA_REVISION = "036d031087b892bd15d99d1d6406eedba4c902f7"
VIDEO_SUFFIX = "compare_overlay_vs_gt.mp4"

PRINTED_POLICY_NAMES = {
    "paligemma_binning_droid": "PG-Bin",
    "paligemma_diffusion_droid": "PG-flow",
    "paligemma_fast_droid": "PG-FAST",
    "paligemma_fast_specialist_droid": "PG-FAST+",
    "paligemma_vq_droid": "PG-FSQ",
    "pi0_droid": "pi0-flow",
    "pi0_fast_droid": "pi0-FAST",
}


def resolve_revision(api: HfApi, repo_id: str, requested: str) -> str:
    return api.dataset_info(repo_id, revision=requested).sha


def list_oscar_video_paths(
    api: HfApi, revision: str
) -> list[str]:
    tree = api.list_repo_tree(
        OSCAR_REPO,
        repo_type="dataset",
        revision=revision,
        recursive=True,
    )
    return sorted(
        entry.path
        for entry in tree
        if entry.path.endswith(f"/{VIDEO_SUFFIX}")
    )


def present(value: Any) -> bool:
    return value is not None and value != ""


def build(
    oscar_revision: str,
    roboarena_repo: str,
    roboarena_revision: str,
    retrieved: str,
) -> dict[str, Any]:
    api = HfApi()
    oscar_sha = resolve_revision(api, OSCAR_REPO, oscar_revision)
    roboarena_sha = resolve_revision(
        api, roboarena_repo, roboarena_revision
    )
    video_paths = list_oscar_video_paths(api, oscar_sha)

    parsed_paths = [path.split("/") for path in video_paths]
    malformed_video_paths = sum(
        len(parts) != 4 or parts[2] != "left" for parts in parsed_paths
    )
    session_ids = sorted(
        {
            parts[0]
            for parts in parsed_paths
            if len(parts) == 4 and parts[2] == "left"
        }
    )
    released_policies = sorted(
        {
            parts[1]
            for parts in parsed_paths
            if len(parts) == 4 and parts[2] == "left"
        }
    )
    pair_counts = Counter(
        (parts[0], parts[1])
        for parts in parsed_paths
        if len(parts) == 4 and parts[2] == "left"
    )

    joined_sessions = 0
    parse_failures = 0
    instruction_present = 0
    complete_policy_rosters = 0
    binary_success_present = 0
    binary_success_valid = 0
    successes = Counter()
    policy_records = Counter()
    missing_policy_records = Counter()
    extra_policy_records = Counter()

    for session_id in session_ids:
        filename = f"evaluation_sessions/{session_id}/metadata.yaml"
        try:
            local_path = hf_hub_download(
                repo_id=roboarena_repo,
                repo_type="dataset",
                revision=roboarena_sha,
                filename=filename,
            )
            with open(local_path, "r", encoding="utf-8") as handle:
                row = yaml.safe_load(handle)
            if not isinstance(row, dict):
                raise TypeError("metadata root is not a mapping")
        except Exception:  # Aggregate failed joins without disclosing identifiers.
            parse_failures += 1
            continue

        joined_sessions += 1
        instruction_present += present(row.get("language_instruction"))
        policies = row.get("policies")
        if not isinstance(policies, dict):
            missing_policy_records.update(released_policies)
            continue

        records_by_name = {}
        for record in policies.values():
            if not isinstance(record, dict):
                continue
            policy_name = str(record.get("policy_name") or "").strip()
            if policy_name:
                records_by_name[policy_name] = record

        observed = set(records_by_name)
        expected = set(released_policies)
        if observed == expected:
            complete_policy_rosters += 1
        missing_policy_records.update(expected - observed)
        extra_policy_records.update(observed - expected)

        for policy in released_policies:
            record = records_by_name.get(policy)
            if record is None:
                continue
            policy_records[policy] += 1
            if "binary_success" in record:
                binary_success_present += 1
            outcome = record.get("binary_success")
            if outcome in (0, 1, False, True):
                binary_success_valid += 1
                successes[policy] += int(outcome)

    policy_summary = {}
    for policy in released_policies:
        denominator = policy_records[policy]
        numerator = successes[policy]
        policy_summary[policy] = {
            "printed_name": PRINTED_POLICY_NAMES.get(policy),
            "real_binary_successes": numerator,
            "real_binary_trials": denominator,
            "real_binary_success_rate_pct": (
                100 * numerator / denominator if denominator else None
            ),
        }

    expected_pairs = len(session_ids) * len(released_policies)
    return {
        "source": {
            "oscar_repo_id": OSCAR_REPO,
            "oscar_requested_revision": oscar_revision,
            "oscar_resolved_revision": oscar_sha,
            "roboarena_repo_id": roboarena_repo,
            "roboarena_requested_revision": roboarena_revision,
            "roboarena_resolved_revision": roboarena_sha,
            "retrieved": retrieved,
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        },
        "privacy": {
            "row_level_data_written": False,
            "session_ids_written": False,
            "instructions_written": False,
            "evaluator_names_written": False,
            "feedback_written": False,
        },
        "release_structure": {
            "video_paths": len(video_paths),
            "malformed_video_paths": malformed_video_paths,
            "unique_sessions": len(session_ids),
            "unique_policies": len(released_policies),
            "expected_session_policy_pairs": expected_pairs,
            "unique_session_policy_pairs": len(pair_counts),
            "duplicate_session_policy_pairs": sum(
                count > 1 for count in pair_counts.values()
            ),
        },
        "join_coverage": {
            "joined_sessions": joined_sessions,
            "parse_or_download_failures": parse_failures,
            "sessions_with_task_instruction": instruction_present,
            "sessions_with_exact_seven_policy_roster": complete_policy_rosters,
            "joined_policy_records": sum(policy_records.values()),
            "policy_records_with_binary_success": binary_success_present,
            "policy_records_with_valid_binary_success": binary_success_valid,
            "missing_policy_records_by_policy": dict(
                sorted(missing_policy_records.items())
            ),
            "extra_policy_records_by_policy": dict(
                sorted(extra_policy_records.items())
            ),
        },
        "real_outcomes_for_released_sessions": policy_summary,
        "scope": (
            "Exact finite-release join. The public OSCAR video paths supply "
            "session IDs that resolve to task instructions and real binary "
            "outcomes in the pinned RoboArena dump. This does not recover "
            "OSCAR/GPT-5 judgments, explain the 63-versus-65 denominator, or "
            "establish a probability sample for future-session inference."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oscar-revision", default=OSCAR_REVISION)
    parser.add_argument("--roboarena-repo", default=ROBOARENA_REPO)
    parser.add_argument("--roboarena-revision", default=ROBOARENA_REVISION)
    parser.add_argument("--retrieved", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        oscar_revision=args.oscar_revision,
        roboarena_repo=args.roboarena_repo,
        roboarena_revision=args.roboarena_revision,
        retrieved=args.retrieved,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
