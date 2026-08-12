from __future__ import annotations

import ast
import copy
import shutil
from pathlib import Path

import pytest

import audit_h195_phail_session_identity_recording_trace as h195


def copied_source(tmp_path: Path) -> Path:
    destination = tmp_path / "positronic-v0.2.1"
    shutil.copytree(h195.SOURCE_ROOT, destination)
    return destination


def authorize_mutated_hash(
    monkeypatch: pytest.MonkeyPatch, source_root: Path, relative: str
) -> None:
    records = copy.deepcopy(h195.SOURCE_FILES)
    records[relative]["sha256"] = h195.sha256(source_root / relative)
    monkeypatch.setattr(h195, "SOURCE_FILES", records)


def mutate(
    source_root: Path, relative: str, old: str, new: str
) -> None:
    path = source_root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_canonical_trace_is_narrow_and_fail_closed():
    result = h195.build()
    h195.validate(result)
    assert (
        result["disposition"]
        == "session_recording_locator_created_but_not_exposed_to_writer"
    )
    assert result["trace"]["inference_session_assigned_fields"] == [
        "_metadata",
        "_websocket",
    ]
    assert result["trace"]["fixed_roster_explicit_identifier_observations"] == {
        "identifier_names": [],
        "identifier_generators": [],
    }
    assert result["trace"]["server_recording_locator_exposed_by_meta"] is False
    assert result["trace"]["public_release_rrd_path_count"] == 0
    assert any("opaque identifier names" in item for item in result["limitations"])
    assert any("server restarts" in item for item in result["limitations"])


def test_identifier_detector_finds_handshake_field_and_generator():
    tree = ast.parse(
        "import uuid\n"
        "def handshake(meta):\n"
        "    session_id = str(uuid.uuid4())\n"
        "    return {'session_id': session_id, **meta}\n"
    )
    assert h195.explicit_identifier_observations(tree) == {
        "identifier_names": ["session_id"],
        "identifier_generators": ["uuid.uuid4"],
    }


def test_validator_rejects_unexpected_top_level_field():
    result = h195.build()
    result["unexpected"] = True
    with pytest.raises(
        ValueError, match="result differs from exact source-derived schema"
    ):
        h195.validate(result)


def test_validator_rejects_nested_semantic_promotion():
    result = h195.build()
    result["trace"]["fixed_roster_explicit_identifier_observations"][
        "identifier_names"
    ] = ["session_id"]
    with pytest.raises(
        ValueError, match="result differs from exact source-derived schema"
    ):
        h195.validate(result)


def test_injected_handshake_identifier_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/offboard/client.py"
    mutate(
        source_root,
        relative,
        "return response['meta']",
        "return {**response['meta'], 'session_id': 'injected'}",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(
        ValueError, match="explicit identifier appeared in fixed PhAIL source roster"
    ):
        h195.build(source_root)


def test_reversed_reset_start_order_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/policy/harness.py"
    mutate(
        source_root,
        relative,
        "self.policy.reset(self.context)\n"
        "                self.ds_command.emit(DsWriterCommand.START(self._build_episode_meta(self.context)))",
        "self.ds_command.emit(DsWriterCommand.START(self._build_episode_meta(self.context)))\n"
        "                self.policy.reset(self.context)",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(
        ValueError, match="policy reset no longer precedes writer start"
    ):
        h195.build(source_root)


def test_missing_emitter_receiver_wiring_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/inference.py"
    mutate(
        source_root,
        relative,
        "world.connect(harness.ds_command, ds_agent.command, emitter_wrapper=wrapper)",
        "world.connect(harness.ds_command, harness.directive, emitter_wrapper=wrapper)",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(
        ValueError, match="harness-to-writer connection changed"
    ):
        h195.build(source_root)


def test_altered_static_serialization_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/dataset/local_dataset.py"
    mutate(
        source_root,
        relative,
        "self._path / 'static.json'",
        "self._path / 'other.json'",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(ValueError, match="static.json serialization changed"):
        h195.build(source_root)


def test_public_wrapper_metadata_injection_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/vendors/openpi/server.py"
    mutate(
        source_root,
        relative,
        "recording_dir: str | None,\n):",
        "recording_dir: str | None,\n    metadata: dict | None = None,\n):",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(
        ValueError, match="public PhAIL wrapper now accepts injected metadata"
    ):
        h195.build(source_root)


def test_recording_locator_metadata_exposure_changes_disposition_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source_root = copied_source(tmp_path)
    relative = "positronic/policy/codec.py"
    mutate(
        source_root,
        relative,
        "return self._inner.meta if self._inner else {}",
        "return {'recording_path': str(self._rec)}",
    )
    authorize_mutated_hash(monkeypatch, source_root, relative)
    with pytest.raises(ValueError, match="recording locator now enters metadata"):
        h195.build(source_root)
