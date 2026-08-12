import audit_h190_phail_session_artifact_paths as h190


def test_path_tokens_are_case_insensitive_and_fixed() -> None:
    assert h190.path_matches("A/Run_Metadata_1.yaml") == ["run_metadata"]
    assert h190.path_matches("episodes/reset/state.json") == ["reset"]
    assert h190.path_matches("ordinary/static.json") == []


def test_root_structured_candidate_boundary() -> None:
    prefix = h190.h187.PREFIX
    assert h190.root_structured_candidate(prefix + "index.json")
    assert not h190.root_structured_candidate(prefix + "rollouts/one/static.json")
    assert not h190.root_structured_candidate(prefix + "README.md")


def test_inventory_projection_retains_only_structural_metadata() -> None:
    rows = [
        {
            "key": h190.h187.PREFIX + "run_metadata.yaml",
            "size": 4,
            "etag": "x",
            "last_modified": "t",
        },
        {
            "key": h190.h187.PREFIX + "rollouts/one/static.json",
            "size": 5,
            "etag": "y",
            "last_modified": "u",
        },
    ]
    result = h190.project_inventory(rows)
    assert result["token_match_count"] == 1
    assert result["root_structured_candidate_count"] == 1
    assert set(result["token_matches"][0]) == {
        "key",
        "size",
        "etag",
        "last_modified",
        "matched_tokens",
        "target_scope",
    }


def test_source_path_classification() -> None:
    assert h190.classify_source_path("tests/test_session.py") == "test_or_example"
    assert h190.classify_source_path("docs/session.md") == "documentation"
    assert (
        h190.classify_source_path("positronic/session.py")
        == "implementation_or_configuration_lead"
    )


def test_dataset_scope_classification() -> None:
    assert h190.classify_dataset_path(
        h190.h187.ROLLOUT_PREFIX + "one/session.json"
    ) == "target_rollout_cohort"
    assert h190.classify_dataset_path(
        h190.h187.PREFIX + "teleoperation/one/reset.parquet"
    ) == "non_target_teleoperation_cohort"


def test_negative_disposition_is_recall_bounded() -> None:
    assert "fixed_token_target_rollout_or_root" in h190.NEGATIVE_DISPOSITION
    assert "source_recorded" not in h190.NEGATIVE_DISPOSITION
