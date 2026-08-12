#!/usr/bin/env python3
"""Acquire the complete outcome-free path/tree projection used by H190."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import audit_h187_phail_context_support as h187
import audit_h190_phail_session_artifact_paths as h190


FAMILY = Path(__file__).resolve().parent
OUTPUT = FAMILY / "projection-h190-phail-path-tree.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def acquire_tree(name: str, url: str) -> dict[str, Any]:
    raw = h187.get_bytes(url)
    data = json.loads(raw)
    tree = data.get("tree")
    require(isinstance(tree, list), f"{name} tree missing")
    require(data.get("truncated") is False, f"{name} tree truncated")
    require(all(isinstance(row, dict) for row in tree), f"{name} tree row")
    projected = []
    for row in tree:
        require(isinstance(row.get("path"), str), f"{name} path missing")
        require(row.get("type") in {"blob", "tree"}, f"{name} type")
        require(isinstance(row.get("sha"), str), f"{name} sha")
        projected.append(
            {
                "path": row["path"],
                "type": row["type"],
                "sha": row["sha"],
                "size": row.get("size"),
            }
        )
    return {
        "name": name,
        "url": url,
        "resolved_tree_sha": data.get("sha"),
        "raw_response_sha256": sha256_bytes(raw),
        "tree": sorted(projected, key=lambda row: (row["path"], row["type"])),
    }


def build() -> dict[str, Any]:
    inventory = h187.list_inventory()
    require(
        h190.project_inventory(inventory)["manifest_sha256"]
        == "8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982",
        "dataset inventory identity changed",
    )
    trees = [
        acquire_tree("positronic-v0.2.1", h190.POSITRONIC_TREE_URL),
        acquire_tree("phail-paper-snapshot", h190.PHAIL_PAPER_TREE_URL),
    ]
    return {
        "schema": "h190-phail-safe-path-tree-projection-v1",
        "dataset_endpoint": h187.ENDPOINT,
        "dataset_prefix": h187.PREFIX,
        "dataset_inventory": inventory,
        "source_trees": trees,
        "content_opened": False,
        "performance_field_opened": False,
        "scope": (
            "complete object-key/structural-metadata and Git-tree projection; "
            "no dataset object or source blob content"
        ),
    }


def validate(projection: dict[str, Any]) -> None:
    require(
        projection.get("schema") == "h190-phail-safe-path-tree-projection-v1",
        "schema",
    )
    require(projection.get("dataset_endpoint") == h187.ENDPOINT, "endpoint")
    require(projection.get("dataset_prefix") == h187.PREFIX, "prefix")
    require(projection.get("content_opened") is False, "content opened")
    require(
        projection.get("performance_field_opened") is False,
        "performance field opened",
    )
    inventory = projection.get("dataset_inventory")
    require(isinstance(inventory, list) and len(inventory) == 14361, "inventory")
    require(
        all(
            set(row) == {"key", "size", "etag", "last_modified"}
            for row in inventory
        ),
        "inventory row schema",
    )
    require(
        h190.project_inventory(inventory)["manifest_sha256"]
        == "8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982",
        "inventory hash",
    )
    trees = projection.get("source_trees")
    require(
        isinstance(trees, list)
        and [tree["name"] for tree in trees]
        == ["positronic-v0.2.1", "phail-paper-snapshot"],
        "source trees",
    )
    for tree in trees:
        require(len(tree["raw_response_sha256"]) == 64, "raw response hash")
        require(bool(tree["resolved_tree_sha"]), "tree identity")
        require(bool(tree["tree"]), "empty tree")
        require(
            all(
                set(row) == {"path", "type", "sha", "size"}
                for row in tree["tree"]
            ),
            "tree row schema",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    rebuilt = build()
    validate(rebuilt)
    rendered = canonical_json(rebuilt)
    if args.check:
        require(args.output.read_text(encoding="utf-8") == rendered, "projection drift")
        print("OK: H190 safe path/tree projection reacquires exactly")
        return
    args.output.write_text(rendered, encoding="utf-8")
    print(f"OK: wrote {args.output}")


if __name__ == "__main__":
    main()
