#!/usr/bin/env python3
"""Trace explicit Positronic session identity through the public PhAIL path."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parent.parent
REPOSITORY_SOURCE_ROOT = ROOT / "work" / "h194-positronic-v0.2.1"
VENDORED_SOURCE_ROOT = ROOT / "vendor" / "positronic-v0.2.1"
SOURCE_ROOT = (
    REPOSITORY_SOURCE_ROOT
    if REPOSITORY_SOURCE_ROOT.is_dir()
    else VENDORED_SOURCE_ROOT
)
PROTOCOL = FAMILY / "protocol-h195-phail-session-identity-recording-trace.md"
OUTPUT = FAMILY / "result-h195-phail-session-identity-recording-trace.json"
H190_PROJECTION = FAMILY / "projection-h190-phail-path-tree.json"
H190_PROJECTION_SHA256 = (
    "6350af0ce19ce1cea88c8f3c2613873c3e3624e47e0cfde5c02fbaa1506d98e1"
)
SOURCE_COMMIT = "e406176bc526babb06844a48e3627a5c0409eb74"

SOURCE_FILES = {
    "positronic/policy/remote.py": {
        "sha256": "787bff2df4b06a26441106ddc78ab73951d0bdd02fb34601f994b531d3809199",
        "lines": "41-45, 96-103",
        "supports": "policy reset creates a new base inference session and meta exposes handshake metadata",
    },
    "positronic/offboard/client.py": {
        "sha256": "bd3fcb45f5ef99b62c52b644e41931b943961235a8f4227e97ab63532d892140",
        "lines": "13-16, 18-32, 52-54, 86-101",
        "supports": "base session fields, ready handshake, and connection construction",
    },
    "positronic/offboard/vendor_server.py": {
        "sha256": "82d1d136f7e263b9e7b96f124ff5743ea2bafaacc1f79ae5c9d88a99055d0894",
        "lines": "123, 167-202",
        "supports": "ready metadata merges server, backend, and policy dictionaries",
    },
    "positronic/data_collection.py": {
        "sha256": "c621b874c30eb07887d4a85ad2f32b6de1a0dd82fa80f173525209972da7255f",
        "lines": "99-115, 135-147",
        "supports": "inspected alternate collection controller; not the PhAIL harness path",
    },
    "positronic/dataset/episode.py": {
        "sha256": "49bd9837a07b1d0d6a3034674cf78de27bc78b907ecf67e84f1c4df659b035bc",
        "lines": "127-152",
        "supports": "abstract per-episode static writer contract",
    },
    "positronic/dataset/ds_writer_agent.py": {
        "sha256": "40435c6a11cb8f75bb1dc79933da1ea8b47586cffa2988c3bf44756fb1fbe483",
        "lines": "38-56, 189-200, 276-296",
        "supports": "START payload is applied to the episode writer as static fields",
    },
    "positronic/policy/harness.py": {
        "sha256": "c01bd56bee3b406eefc41d01d9010464c1fed1490fdb18d3a0d2f838ae14c075",
        "lines": "64-87, 97-106",
        "supports": "policy reset precedes START and policy meta enters the START payload",
        "expansion_reason": "connect reset and policy metadata to DsWriterCommand.START",
    },
    "positronic/cfg/policy.py": {
        "sha256": "6d6fb174deb25c3a65c630bffb9e71553882786a395b157f2a8c3481aa56b90b",
        "lines": "62-95, 98-122, 136-147",
        "supports": "public phail_multiple composition of four selected RemotePolicy paths",
        "expansion_reason": "targeted re-review found the public policy composition missing",
    },
    "positronic/policy/base.py": {
        "sha256": "3119b6a01b223ca71df8e74b0cbd8619d556ab7818c9e5c38bc645687dc58cb6",
        "lines": "45-91",
        "supports": "SampledPolicy forwards reset and meta to the selected policy",
        "expansion_reason": "targeted re-review found selected-policy forwarding missing",
    },
    "positronic/policy/codec.py": {
        "sha256": "e164fec194d03d683dda14efe492f3720a12403b0e154568080c46d691da2ef6",
        "lines": "47-101, 264-287, 331-454, 460-486",
        "supports": "server recording wrapper creates per-reset RRD locator but omits it from meta",
        "expansion_reason": "targeted re-review found the server codec wrapper missing",
    },
    "positronic/inference.py": {
        "sha256": "f0d9565b501b70ea15421d86b0e742a8c57d5c22446f57f36f9bd7cf79d43080",
        "lines": "116-127, 130-159, 239-248",
        "supports": "public PhAIL entry point connects harness emitter to writer receiver",
        "expansion_reason": "independent challenge found the concrete emitter/receiver edge missing",
    },
    "positronic/wire.py": {
        "sha256": "586baf9bd736a623fc4b19027ea05158757f4e7e474a9f73081090a992329763",
        "lines": "8-17, 27-55",
        "supports": "constructs the DsWriterAgent returned to the inference entry point",
        "expansion_reason": "resolve the concrete writer-agent construction",
    },
    "positronic/dataset/local_dataset.py": {
        "sha256": "e0308688d7daa43c4c27b00a5f199ed8ffc86caaf3b6b1b2cf9177adec82e493",
        "lines": "97-133, 168-195, 228-260",
        "supports": "static items are serialized to static.json",
        "expansion_reason": "independent challenge found the concrete serializer missing",
    },
    "positronic/vendors/lerobot_0_3_3/server.py": {
        "sha256": "78d7956587d8a5db54a088015f59f41a42f6d0cd30d3a2eda76534dcd3815861",
        "lines": "25-77, 93-118",
        "supports": "ACT public PhAIL server metadata producer",
        "expansion_reason": "inspect every public PhAIL backend metadata producer",
    },
    "positronic/vendors/lerobot/server.py": {
        "sha256": "6fe568b46b314f5313b547ef33c93b62631d190ae225275b58a3b4464a70e6a9",
        "lines": "19-60, 76-85",
        "supports": "SmolVLA public PhAIL server metadata producer",
        "expansion_reason": "inspect every public PhAIL backend metadata producer",
    },
    "positronic/vendors/gr00t/server.py": {
        "sha256": "4599a131688471860e783d962ddb5a9dd76f9c28d8d8c553de1ba260e8598fbf",
        "lines": "258-341, 358-386",
        "supports": "GR00T public PhAIL server metadata producer",
        "expansion_reason": "inspect every public PhAIL backend metadata producer",
    },
    "positronic/vendors/openpi/server.py": {
        "sha256": "a4f2b5d383044ad6b7436d1d56a0473c2de43f93c5b39bb024c809fa7a83cd6b",
        "lines": "159-171, 179-248, 274-325",
        "supports": "OpenPI public PhAIL server metadata producer",
        "expansion_reason": "inspect every public PhAIL backend metadata producer",
    },
}

DREAMZERO_COUNTEREXAMPLE = {
    "path": "positronic/vendors/dreamzero/server.py",
    "sha256": "e4e230bad01345cf07cd6e45adea94328b77fc2cb9a5d0e7858e60a1f1f9b85e",
    "lines": "8, 176-189",
    "supports": "out-of-roster framework counterexample creates a UUID session_id",
}

BACKENDS = {
    "ACT": ("positronic/vendors/lerobot_0_3_3/server.py", "main"),
    "SmolVLA": ("positronic/vendors/lerobot/server.py", "main"),
    "GR00T": ("positronic/vendors/gr00t/server.py", "server"),
    "OpenPI": ("positronic/vendors/openpi/server.py", "server"),
}

IDENTIFIER_NAMES = {
    "session_id",
    "inference_session_id",
    "connection_id",
    "request_id",
    "execution_id",
    "trace_id",
    "run_id",
    "episode_uuid",
    "session_uuid",
    "request_uuid",
}
IDENTIFIER_GENERATORS = {
    "uuid.uuid1",
    "uuid.uuid4",
    "secrets.token_hex",
    "secrets.token_urlsafe",
}
LIMITATIONS = [
    "The audit is source-bounded to Positronic v0.2.1 and the fixed public PhAIL entry point and four backend server configurations.",
    "Backend-internal libraries, private configuration, externally injected metadata, and opaque identifier names were not exhaustively inspected.",
    "H193 is a fixed-vocabulary key projection and is not used as proof of general identifier absence.",
    "The RRD locator combines second-resolution wall time with a process-local counter; uniqueness across server restarts is not established.",
    "Zero RRD paths in the fixed public release inventory does not establish that configured server recording locations are unavailable or empty.",
    "A WebSocket object or network endpoint is not treated as a stable application-level identifier or dependence cluster.",
]
INTERPRETATION = (
    "Every fixed public PhAIL server configuration activates Positronic's "
    "RecordingCodec. Each server policy reset creates a session-specific RRD "
    "artifact locator from second-resolution wall time and a process-local "
    "counter, but the recording wrapper's meta path does not expose that "
    "locator to the ready handshake or episode static writer. The locator is "
    "not a globally unique identifier or a dependence cluster."
)
SCOPE = (
    "Positronic server-recording locator in the fixed public PhAIL path only; "
    "no claim about global uniqueness, public availability of server "
    "recordings, physical reset, operator session, exchangeability cluster, "
    "backend internals, private configuration, or opaque names"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted(node: ast.AST) -> str:
    parts: list[str] = []
    value = node
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def method(
    tree: ast.Module, class_name: str, method_name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (
                    isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
                    and child.name == method_name
                ):
                    return child
    raise ValueError(f"method missing: {class_name}.{method_name}")


def function(
    tree: ast.Module, function_name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and node.name == function_name
        ):
            return node
    raise ValueError(f"function missing: {function_name}")


def calls(node: ast.AST) -> list[tuple[str, int]]:
    return [
        (dotted(child.func), child.lineno)
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
    ]


def call_names(node: ast.AST) -> set[str]:
    return {name for name, _ in calls(node)}


def call_line(node: ast.AST, name: str) -> int:
    matches = [line for candidate, line in calls(node) if candidate == name]
    require(bool(matches), f"call missing: {name}")
    return min(matches)


def assigned_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            names.add(child.id)
        if isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Store):
            names.add(child.attr)
    return names


def string_dict_keys(node: ast.AST) -> set[str]:
    keys: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Dict):
            for key in child.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.add(key.value)
        if isinstance(child, ast.Call):
            keys.update(keyword.arg for keyword in child.keywords if keyword.arg)
    return keys


def string_literals(node: ast.AST) -> set[str]:
    return {
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }


def explicit_identifier_observations(node: ast.AST) -> dict[str, list[str]]:
    names = sorted(
        (assigned_names(node) | string_dict_keys(node)) & IDENTIFIER_NAMES
    )
    generators = sorted(call_names(node) & IDENTIFIER_GENERATORS)
    return {"identifier_names": names, "identifier_generators": generators}


def source_record(
    relative: str, expected: dict[str, str], source_root: Path
) -> dict[str, str]:
    source = source_root / relative
    require(source.is_file(), f"source missing: {relative}")
    require(sha256(source) == expected["sha256"], f"source drift: {relative}")
    return {"path": relative, **expected}


def verify_sources(source_root: Path = SOURCE_ROOT) -> list[dict[str, str]]:
    require(source_root.is_dir(), "pinned Positronic checkout missing")
    records = [
        source_record(relative, expected, source_root)
        for relative, expected in SOURCE_FILES.items()
    ]
    source_record(
        DREAMZERO_COUNTEREXAMPLE["path"],
        {key: value for key, value in DREAMZERO_COUNTEREXAMPLE.items() if key != "path"},
        source_root,
    )
    return records


def parse_sources(source_root: Path) -> dict[str, ast.Module]:
    return {
        relative: ast.parse(
            (source_root / relative).read_text(encoding="utf-8"),
            filename=relative,
        )
        for relative in SOURCE_FILES
    }


def build(source_root: Path = SOURCE_ROOT) -> dict[str, Any]:
    source_records = verify_sources(source_root)
    trees = parse_sources(source_root)

    client_init = method(
        trees["positronic/offboard/client.py"], "InferenceSession", "__init__"
    )
    client_handshake = method(
        trees["positronic/offboard/client.py"], "InferenceSession", "_handshake"
    )
    new_session = method(
        trees["positronic/offboard/client.py"], "InferenceClient", "new_session"
    )
    remote_reset = method(
        trees["positronic/policy/remote.py"], "RemotePolicy", "reset"
    )
    remote_meta = method(
        trees["positronic/policy/remote.py"], "RemotePolicy", "meta"
    )
    server_endpoint = method(
        trees["positronic/offboard/vendor_server.py"],
        "VendorServer",
        "websocket_endpoint",
    )
    server_init = method(
        trees["positronic/offboard/vendor_server.py"],
        "VendorServer",
        "__init__",
    )
    production = function(trees["positronic/cfg/policy.py"], "production")
    sampled_reset = method(
        trees["positronic/policy/base.py"], "SampledPolicy", "reset"
    )
    sampled_meta = method(
        trees["positronic/policy/base.py"], "SampledPolicy", "meta"
    )
    wrapped_reset = method(
        trees["positronic/policy/codec.py"], "_WrappedPolicy", "reset"
    )
    wrapped_meta = method(
        trees["positronic/policy/codec.py"], "_WrappedPolicy", "meta"
    )
    recording_new_session = method(
        trees["positronic/policy/codec.py"],
        "RecordingCodec",
        "_new_session",
    )
    recording_session_meta = method(
        trees["positronic/policy/codec.py"], "_RecordingSession", "meta"
    )
    recording_policy_reset = method(
        trees["positronic/policy/codec.py"], "_RecordingPolicy", "reset"
    )
    recording_policy_meta = method(
        trees["positronic/policy/codec.py"], "_RecordingPolicy", "meta"
    )
    harness_build = method(
        trees["positronic/policy/harness.py"], "Harness", "_build_episode_meta"
    )
    harness_directive = method(
        trees["positronic/policy/harness.py"], "Harness", "_handle_directive"
    )
    connect_writer = function(
        trees["positronic/inference.py"], "_connect_ds_command"
    )
    phail_entry = function(trees["positronic/inference.py"], "_internal_main")
    wire_writer = function(trees["positronic/wire.py"], "wire")
    writer_command = method(
        trees["positronic/dataset/ds_writer_agent.py"],
        "DsWriterAgent",
        "_handle_command",
    )
    disk_set_static = method(
        trees["positronic/dataset/local_dataset.py"],
        "DiskEpisodeWriter",
        "set_static",
    )
    disk_close = method(
        trees["positronic/dataset/local_dataset.py"],
        "DiskEpisodeWriter",
        "__exit__",
    )

    inference_fields = sorted(assigned_names(client_init))
    require(
        inference_fields == ["_metadata", "_websocket"],
        "InferenceSession fields changed",
    )
    require(
        "self._handshake" in call_names(client_init),
        "InferenceSession handshake changed",
    )
    require(
        {"self._websocket.recv", "deserialise"}.issubset(
            call_names(client_handshake)
        ),
        "client handshake receive path changed",
    )
    require(
        {"status", "ready", "meta"}.issubset(string_literals(client_handshake)),
        "ready metadata path changed",
    )
    require(
        "InferenceSession" in call_names(new_session),
        "new_session no longer constructs InferenceSession",
    )
    require(
        "self._client.new_session" in call_names(remote_reset),
        "RemotePolicy reset no longer creates a session",
    )
    require(
        {"flatten_dict"}.issubset(call_names(remote_meta))
        and {"type", "server"}.issubset(string_dict_keys(remote_meta)),
        "RemotePolicy metadata path changed",
    )
    require(
        {"self.resolve_model", "serialise"}.issubset(call_names(server_endpoint))
        and {"status", "meta"}.issubset(string_dict_keys(server_endpoint))
        and "ready" in string_literals(server_endpoint),
        "server ready metadata path changed",
    )
    require(
        "RecordingCodec" in call_names(server_init)
        and "recording_dir" in ast.unparse(server_init),
        "server recording wrapper construction changed",
    )
    require(
        "SampledPolicy" in call_names(production)
        and all(
            name in ast.unparse(production)
            for name in ("groot", "openpi", "act", "smolvla")
        ),
        "public four-policy composition changed",
    )
    require(
        "self._current_policy.reset" in call_names(sampled_reset)
        and "self._current_policy.meta" in ast.unparse(sampled_meta),
        "selected-policy reset/meta forwarding changed",
    )
    require(
        "self._policy.reset" in call_names(wrapped_reset)
        and "self._policy.meta | self._codec.meta" in ast.unparse(wrapped_meta),
        "codec reset/meta forwarding changed",
    )
    require(
        {
            "next",
            "datetime.now",
            "rr.RecordingStream",
            "rec.save",
            "_RecordingSession",
        }.issubset(call_names(recording_new_session))
        and "%y%m%d_%H%M%S" in string_literals(recording_new_session)
        and "positronic_inference" in string_literals(recording_new_session)
        and ".rrd" in ast.unparse(recording_new_session),
        "recording locator construction changed",
    )
    require(
        "self._codec._new_session" in call_names(recording_policy_reset)
        and "self._active.reset" in call_names(recording_policy_reset),
        "recording-policy reset path changed",
    )
    require(
        "_dir" not in ast.unparse(recording_session_meta)
        and "rec" not in ast.unparse(recording_session_meta)
        and "_dir" not in ast.unparse(recording_policy_meta)
        and "rec" not in ast.unparse(recording_policy_meta),
        "recording locator now enters metadata",
    )
    require(
        "flatten_dict" in call_names(harness_build)
        and "inference.policy." in ast.unparse(harness_build),
        "policy metadata flattening changed",
    )
    reset_line = call_line(harness_directive, "self.policy.reset")
    start_line = call_line(harness_directive, "DsWriterCommand.START")
    require(reset_line < start_line, "policy reset no longer precedes writer start")
    require(
        "world.connect(harness.ds_command, ds_agent.command" in ast.unparse(connect_writer),
        "harness-to-writer connection changed",
    )
    require(
        "'phail': droid_setup.override" in ast.unparse(phail_entry),
        "public PhAIL entry point changed",
    )
    require(
        "DsWriterAgent" in call_names(wire_writer),
        "writer-agent construction changed",
    )
    require(
        "cmd.static_data.items" in call_names(writer_command)
        and "ep_writer.set_static" in call_names(writer_command),
        "writer static-data application changed",
    )
    require(
        "self._static_items" in ast.unparse(disk_set_static),
        "disk static accumulator changed",
    )
    require(
        "json.dump" in call_names(disk_close)
        and "static.json" in ast.unparse(disk_close)
        and "self._static_items" in ast.unparse(disk_close),
        "static.json serialization changed",
    )

    backend_results = []
    for policy_name, (relative, wrapper_name) in BACKENDS.items():
        tree = trees[relative]
        wrapper = function(tree, wrapper_name)
        observations = explicit_identifier_observations(tree)
        wrapper_args = [
            argument.arg
            for argument in (
                wrapper.args.posonlyargs + wrapper.args.args + wrapper.args.kwonlyargs
            )
        ]
        require(
            "phail" in {
                target.id
                for child in tree.body
                if isinstance(child, ast.Assign)
                for target in child.targets
                if isinstance(target, ast.Name)
            },
            f"public PhAIL backend config missing: {policy_name}",
        )
        recording_dirs = sorted(
            value
            for value in string_literals(tree)
            if "phail_unified/server_recordings/" in value
        )
        require(
            len(recording_dirs) == 1,
            f"public PhAIL recording directory changed: {policy_name}",
        )
        backend_results.append(
            {
                "policy": policy_name,
                "source_path": relative,
                "public_wrapper": wrapper_name,
                "public_wrapper_accepts_metadata": "metadata" in wrapper_args,
                "phail_recording_directory": recording_dirs[0],
                **observations,
            }
        )

    roster_observations = explicit_identifier_observations(
        ast.Module(
            body=[
                node
                for relative, tree in trees.items()
                if relative not in {
                    "positronic/data_collection.py",
                    "positronic/dataset/episode.py",
                }
                for node in tree.body
            ],
            type_ignores=[],
        )
    )
    require(
        roster_observations
        == {"identifier_names": [], "identifier_generators": []},
        "explicit identifier appeared in fixed PhAIL source roster",
    )
    require(
        all(not row["public_wrapper_accepts_metadata"] for row in backend_results),
        "public PhAIL wrapper now accepts injected metadata",
    )

    require(
        sha256(H190_PROJECTION) == H190_PROJECTION_SHA256,
        "H190 safe projection drift",
    )
    h190_projection = json.loads(H190_PROJECTION.read_text(encoding="utf-8"))
    require(
        h190_projection["content_opened"] is False
        and h190_projection["performance_field_opened"] is False,
        "H190 projection boundary changed",
    )
    release_paths = [row["key"] for row in h190_projection["dataset_inventory"]]
    require(len(release_paths) == 14361, "H190 inventory count changed")
    public_rrd_paths = sorted(
        path for path in release_paths if path.lower().endswith(".rrd")
    )
    require(public_rrd_paths == [], "public release now contains RRD paths")

    dreamzero_path = source_root / DREAMZERO_COUNTEREXAMPLE["path"]
    dreamzero_tree = ast.parse(dreamzero_path.read_text(encoding="utf-8"))
    dreamzero_observations = explicit_identifier_observations(dreamzero_tree)
    require(
        "session_id" in dreamzero_observations["identifier_names"]
        and "uuid.uuid4" in dreamzero_observations["identifier_generators"],
        "DreamZero scope counterexample changed",
    )

    return {
        "schema": "h195-phail-session-identity-recording-trace-v3",
        "protocol_sha256": sha256(PROTOCOL),
        "source_commit": SOURCE_COMMIT,
        "source_records": source_records,
        "source_exposed": True,
        "result_exposed": True,
        "performance_field_opened": False,
        "dataset_content_opened": False,
        "trace": {
            "new_base_inference_session_per_policy_reset": True,
            "runtime_holder": "InferenceSession wrapping a WebSocket connection",
            "inference_session_assigned_fields": inference_fields,
            "ready_handshake_metadata_enters_policy_meta": True,
            "sampled_policy_forwards_selected_reset_and_meta": True,
            "server_recording_wrapper_enabled_for_all_four_backends": True,
            "server_recording_locator_pattern": (
                "{YYMMDD_HHMMSS}_{process_local_counter:04d}.rrd"
            ),
            "server_recording_locator_uniqueness": (
                "process-local counter plus second-resolution wall time; "
                "cross-restart uniqueness not established"
            ),
            "server_recording_locator_exposed_by_meta": False,
            "policy_reset_precedes_episode_start": True,
            "harness_emitter_connected_to_writer_receiver": True,
            "start_payload_applied_as_episode_static_fields": True,
            "episode_static_fields_serialized_to_static_json": True,
            "fixed_phail_backend_results": backend_results,
            "fixed_roster_explicit_identifier_observations": roster_observations,
            "public_release_inventory_object_count": len(release_paths),
            "public_release_rrd_path_count": len(public_rrd_paths),
            "h190_safe_projection_sha256": H190_PROJECTION_SHA256,
            "out_of_roster_dreamzero_counterexample": {
                "source_path": DREAMZERO_COUNTEREXAMPLE["path"],
                **dreamzero_observations,
            },
        },
        "disposition": (
            "session_recording_locator_created_but_not_exposed_to_writer"
        ),
        "interpretation": INTERPRETATION,
        "scope": SCOPE,
        "limitations": LIMITATIONS,
        "supersedes_unrelied_candidate_sha256": [
            "09baa38178bb78cd9ea57af9ba8d51a82e21119b7061422fa4cd23b22bc340c4",
            "1d92fefc04e1e6d99f690c2e29993d4a7b99317ff4174e8300ba51383fcbbf73",
        ],
    }


def validate(
    result: dict[str, Any], source_root: Path = SOURCE_ROOT
) -> None:
    expected = build(source_root)
    require(result == expected, "result differs from exact source-derived schema")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(
            OUTPUT.read_text(encoding="utf-8") == rendered,
            "stored result drift",
        )
        print("OK: H195 fixed-path identifier trace reproduces exactly")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print("OK: wrote repaired H195 fixed-path identifier trace")


if __name__ == "__main__":
    main()
