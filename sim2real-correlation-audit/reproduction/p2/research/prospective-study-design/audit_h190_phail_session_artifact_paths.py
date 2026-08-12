#!/usr/bin/env python3
"""Path-only H190 search for PhAIL session/reset identity artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

import audit_h187_phail_context_support as h187
import audit_h189_phail_initial_item_count_support as h189


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h190-phail-session-artifact-path-audit.md"
OUTPUT = FAMILY / "result-h190-phail-session-artifact-path-audit.json"
TOKENS = ("session", "run_metadata", "run-metadata", "reset", "sequence", "batch")
NEGATIVE_DISPOSITION = (
    "no_fixed_token_target_rollout_or_root_session_artifact_path_found"
)
POSITRONIC_TREE_URL = (
    "https://api.github.com/repos/Positronic-Robotics/positronic/"
    "git/trees/v0.2.1?recursive=1"
)
PHAIL_PAPER_TREE_URL = (
    "https://api.github.com/repos/Positronic-Robotics/phail-paper/"
    "git/trees/18ce72d5703dcbbbb10a980336aa5a1622601fb4?recursive=1"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_matches(path: str) -> list[str]:
    lowered = path.lower()
    return [token for token in TOKENS if token in lowered]


def root_structured_candidate(key: str) -> bool:
    relative = key.removeprefix(h187.PREFIX)
    suffix = PurePosixPath(relative).suffix.lower()
    return "/" not in relative.rstrip("/") and suffix in {".json", ".yaml", ".yml"}


def project_inventory(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    matches = []
    roots = []
    for row in inventory:
        key = str(row["key"])
        tokens = path_matches(key)
        projected = {
            "key": key,
            "size": int(row["size"]),
            "etag": str(row["etag"]),
            "last_modified": str(row["last_modified"]),
        }
        if tokens:
            matches.append(
                {
                    **projected,
                    "matched_tokens": tokens,
                    "target_scope": classify_dataset_path(key),
                }
            )
        if root_structured_candidate(key):
            roots.append(projected)
    return {
        "object_count": len(inventory),
        "manifest_sha256": h189.inventory_manifest_sha256(inventory),
        "token_match_count": len(matches),
        "token_matches": sorted(matches, key=lambda row: row["key"]),
        "root_structured_candidate_count": len(roots),
        "root_structured_candidates": sorted(roots, key=lambda row: row["key"]),
    }


def classify_dataset_path(key: str) -> str:
    if key.startswith(h187.ROLLOUT_PREFIX):
        return "target_rollout_cohort"
    if key.startswith(h187.PREFIX + "teleoperation/"):
        return "non_target_teleoperation_cohort"
    if key.startswith(h187.PREFIX + "human/"):
        return "non_target_human_cohort"
    return "release_root_or_unknown"


def project_tree(name: str, url: str, raw: bytes) -> dict[str, Any]:
    data = json.loads(raw)
    tree = data.get("tree")
    require(isinstance(tree, list), f"{name} tree missing")
    require(data.get("truncated") is False, f"{name} tree truncated")
    matches = []
    for row in tree:
        path = str(row.get("path", ""))
        tokens = path_matches(path)
        if tokens:
            matches.append(
                {
                    "path": path,
                    "type": row.get("type"),
                    "sha": row.get("sha"),
                    "size": row.get("size"),
                    "matched_tokens": tokens,
                    "classification": classify_source_path(path),
                }
            )
    return {
        "name": name,
        "url": url,
        "resolved_tree_sha": data.get("sha"),
        "tree_entry_count": len(tree),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "match_count": len(matches),
        "matches": sorted(matches, key=lambda row: row["path"]),
    }


def classify_source_path(path: str) -> str:
    lowered = path.lower()
    if any(part in lowered for part in ("test", "example", "fixture")):
        return "test_or_example"
    if PurePosixPath(path).suffix.lower() in {".md", ".rst", ".txt"}:
        return "documentation"
    return "implementation_or_configuration_lead"


def build() -> dict[str, Any]:
    inventory = h187.list_inventory()
    inventory_result = project_inventory(inventory)
    require(
        inventory_result["manifest_sha256"] == h189.EXPECTED_H187_INVENTORY,
        "public inventory drifted",
    )
    trees = []
    for name, url in (
        ("positronic-v0.2.1", POSITRONIC_TREE_URL),
        ("phail-paper-snapshot", PHAIL_PAPER_TREE_URL),
    ):
        trees.append(project_tree(name, url, h187.get_bytes(url)))
    # Generic root metadata and matches in non-target cohorts remain reported
    # for recall but cannot link the fixed 594-rollout cohort.
    dataset_lead = any(
        row["target_scope"] == "target_rollout_cohort"
        for row in inventory_result["token_matches"]
    )
    return {
        "schema": "h190-phail-session-artifact-path-audit-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "fixed_tokens": list(TOKENS),
        "dataset_inventory": inventory_result,
        "source_trees": trees,
        "dataset_content_opened": False,
        "performance_field_opened": False,
        "episode_linkable_data_artifact_lead": dataset_lead,
        "disposition": (
            "advance_candidate_to_separate_content_gate"
            if dataset_lead
            else NEGATIVE_DISPOSITION
        ),
        "scope": (
            "fixed-token path recall only; no inference about private or "
            "differently named records"
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result.get("schema") == "h190-phail-session-artifact-path-audit-v1",
        "schema",
    )
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(result.get("fixed_tokens") == list(TOKENS), "token drift")
    require(result.get("dataset_content_opened") is False, "dataset content")
    require(result.get("performance_field_opened") is False, "performance field")
    expected_disposition = (
        "advance_candidate_to_separate_content_gate"
        if result.get("episode_linkable_data_artifact_lead")
        else NEGATIVE_DISPOSITION
    )
    require(result.get("disposition") == expected_disposition, "disposition")
    require(
        result["dataset_inventory"]["manifest_sha256"]
        == h189.EXPECTED_H187_INVENTORY,
        "inventory hash",
    )
    require(
        all(tree["tree_entry_count"] > 0 for tree in result["source_trees"]),
        "empty tree",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate(json.loads(OUTPUT.read_text()))
        return
    result = build()
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
