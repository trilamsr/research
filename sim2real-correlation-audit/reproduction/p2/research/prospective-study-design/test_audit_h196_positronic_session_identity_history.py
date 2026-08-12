import copy
import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).with_name("audit_h196_positronic_session_identity_history.py")
SPEC = importlib.util.spec_from_file_location("audit_h196", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


@pytest.fixture(scope="module")
def valid_result():
    result = AUDIT.build(AUDIT.DEFAULT_REPOSITORY)
    AUDIT.validate(result)
    return result


def rejected(result):
    with pytest.raises(ValueError):
        AUDIT.validate(result)


def test_valid_result_passes(valid_result):
    AUDIT.validate(copy.deepcopy(valid_result))


def test_wrong_endpoint_status_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["comparison_endpoint_prospective"] = False
    rejected(candidate)


def test_missing_history_exposure_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["expansion_history_result_exposed"] = False
    rejected(candidate)


def test_missing_fixed_path_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["fixed_paths"].pop()
    rejected(candidate)


def test_unrecorded_expansion_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["expansions"].pop()
    rejected(candidate)


def test_omitted_history_commit_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["history"]["commits"].pop()
    rejected(candidate)


def test_duplicate_history_commit_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["history"]["commits"].append(copy.deepcopy(candidate["history"]["commits"][0]))
    candidate["history"]["commit_count"] += 1
    rejected(candidate)


def test_wrong_uuid_construction_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["trace"]["episode_uid_construction"] = "timestamp"
    rejected(candidate)


def test_missing_rrd_join_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["trace"]["recording_locator_supplies_episode_to_rrd_join"] = False
    rejected(candidate)


def test_scope_overreach_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["trace"]["physical_reset_or_operator_session_established"] = True
    rejected(candidate)


def test_prohibited_access_flag_rejected(valid_result):
    candidate = copy.deepcopy(valid_result)
    candidate["server_recording_opened"] = True
    rejected(candidate)
