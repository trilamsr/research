#!/usr/bin/env python3
"""Hash-bound design audit of the ArmnetBench v0.1 arXiv paper."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h224-armnetbench-paper-design-audit.md"
H028_RESULT = FAMILY / "result-armnetbench-target-metrology-intake.json"
H029_RESULT = FAMILY / "result-armnetbench-nonoutcome-manifest-linkage.json"
H222_RESULT = (
    FAMILY.parent
    / "decision-validity"
    / "result-h222-postbaseline-monitor-alert-screen.json"
)
OUTPUT = FAMILY / "result-h224-armnetbench-paper-design-audit.json"

ARXIV_ID = "2607.24481v1"
TITLE = (
    "ArmnetBench v0.1: Parallel Real-World Evaluation of Manipulation "
    "Policies on a Low-Cost Arm Farm"
)
AUTHORS = ["Praveen Selvaraj", "Lorenzo Uttini", "Ville Kuosmanen"]
SUBMITTED_UTC = "2026-07-27T14:16:43Z"
PDF_URL = "https://arxiv.org/pdf/2607.24481v1"
SOURCE_URL = "https://export.arxiv.org/src/2607.24481v1"
PDF_BYTES = 1_989_885
PDF_SHA256 = "c1d0edbd163f6db2597da67c4afe03e8b63deb3c2eefbfca613db3ff5319951e"
SOURCE_BYTES = 2_354_476
SOURCE_SHA256 = "21e4d8b117878e4d42d810da6e8e2a711c11e146dc389d1fd4ba7da97cf12bf1"
MAIN_TEX_SHA256 = "8ceaa0e443e561c90b376a22e5c4d541243685d5cb3d42b04d905118907f6e20"
PDF_PAGES = 11
H028_SHA256 = "40578851f962399cf0e6bca4eca95417ed28c419f6fe486b6ac8d08408698482"
H029_SHA256 = "82dd62ad96cdce928774705a214f9161ec694e1a3b7edc57c385d36ced3f272c"
H222_SHA256 = "3bf46af0c4e3bed9b7f05c0553098d1689cd825860638d121c194c7c59fd087b"

ALLOWED_STATUSES = {
    "supported",
    "partial",
    "absent_from_fixed_scope",
    "not_assessed",
}


def anchor(line: int, contains: str) -> dict[str, Any]:
    return {"line": line, "contains": contains}


EVIDENCE_UNITS: list[dict[str, Any]] = [
    {
        "unit_id": 1,
        "name": "immutable_paper_dataset_repository_identity",
        "status": "partial",
        "source_locations": ["main.tex:581-583", "PDF p.9"],
        "anchors": [
            anchor(581, "We release the core benchmark in LeRobot"),
            anchor(583, "huggingface.co/collections/armnet/armnetbench-v01"),
        ],
        "author_statement": (
            "The paper links a named Hub collection and names both release formats."
        ),
        "audit_inference": (
            "The paper/version is immutable, but the collection link supplies no "
            "dataset commit, tag, or content hash. H028 separately pins one dataset tag."
        ),
    },
    {
        "unit_id": 2,
        "name": "versioned_policy_roster_and_immutable_checkpoints",
        "status": "partial",
        "source_locations": ["main.tex:390-396", "PDF p.5"],
        "anchors": [
            anchor(391, "We evaluate two specialist imitation policies"),
            anchor(396, "We release every evaluated task--policy checkpoint."),
        ],
        "author_statement": (
            "Seven policy families are named and every task-policy checkpoint is "
            "said to be released."
        ),
        "audit_inference": (
            "No evaluated checkpoint revision or content hash is stated; H028 found "
            "public checkpoint links but no immutable revision binding."
        ),
    },
    {
        "unit_id": 3,
        "name": "standalone_per_policy_physical_execution",
        "status": "supported",
        "source_locations": ["main.tex:284-292", "main.tex:398-406", "PDF pp.4,6"],
        "anchors": [
            anchor(285, "A user submits a policy image, embodiment, and task."),
            anchor(286, "image and runs it locally in an isolated container"),
            anchor(400, "Each task--policy pair targets 30 rollouts."),
        ],
        "author_statement": (
            "A submitted policy runs in an isolated container and each task-policy "
            "pair receives its own physical rollouts."
        ),
        "audit_inference": (
            "This supports standalone policy execution, while physical carryover "
            "between successive rollouts remains a separate unresolved unit."
        ),
    },
    {
        "unit_id": 4,
        "name": "context_definition_and_allocation_timing",
        "status": "partial",
        "source_locations": ["main.tex:304-311", "main.tex:398-406", "PDF pp.4,6"],
        "anchors": [
            anchor(308, "We partitioned tasks across cells so that all seven"),
            anchor(309, "policies for a task ran on the \\emph{same} cell"),
            anchor(404, "sampled independently rather than matched across policies."),
        ],
        "author_statement": (
            "All policies for a task ran on one cell, with independently sampled "
            "initial states."
        ),
        "audit_inference": (
            "The task/cell context is described, but the source does not establish "
            "that the allocation rule was committed before policy choice or execution."
        ),
    },
    {
        "unit_id": 5,
        "name": "assignment_randomization_and_execution_order_law",
        "status": "partial",
        "source_locations": ["main.tex:219-220", "main.tex:400-406", "PDF pp.3,6"],
        "anchors": [
            anchor(219, "object positions are randomised"),
            anchor(403, "randomises object placement within a task-specific range."),
            anchor(404, "sampled independently rather than matched across policies."),
        ],
        "author_statement": (
            "Operators randomized object placement independently between rollouts."
        ),
        "audit_inference": (
            "No policy assignment mechanism, policy execution sequence, randomization "
            "draw, or order log is reported."
        ),
    },
    {
        "unit_id": 6,
        "name": "reset_restoration_acceptance_carryover_and_interventions",
        "status": "partial",
        "source_locations": [
            "main.tex:398-419",
            "main.tex:539-559",
            "PDF pp.6,8-9",
        ],
        "anchors": [
            anchor(401, "episode were removed due to incorrect manual resets"),
            anchor(402, "Before each rollout, an operator resets the scene"),
            anchor(551, "Object deterioration."),
            anchor(554, "Physical cell changes."),
        ],
        "author_statement": (
            "An operator resets before each rollout; two incorrect resets were "
            "removed, and object/camera changes are disclosed."
        ),
        "audit_inference": (
            "There is no measured reset-acceptance rule, restoration trace, complete "
            "intervention log, or adjustment for physical carryover."
        ),
    },
    {
        "unit_id": 7,
        "name": "episode_session_cluster_identity_and_dependence_unit",
        "status": "partial",
        "source_locations": ["main.tex:304-311", "main.tex:421-440", "PDF pp.4,6"],
        "anchors": [
            anchor(306, "We collected v0.1 on 3 cells co-located in a single room"),
            anchor(424, "Every episode has 3"),
            anchor(436, "and episode metadata"),
            anchor(438, "\\texttt{policy\\_repo\\_id})."),
        ],
        "author_statement": (
            "The paper identifies cells and episodes and describes per-episode metadata."
        ),
        "audit_inference": (
            "It does not publish a session/operator/order identity or declare the "
            "dependence unit needed for comparative uncertainty."
        ),
    },
    {
        "unit_id": 8,
        "name": "rubric_horizon_missingness_and_evaluator_identity",
        "status": "partial",
        "source_locations": ["main.tex:398-419", "PDF p.6"],
        "anchors": [
            anchor(405, "standardised per-task wall-clock limits"),
            anchor(406, "operator judgement."),
            anchor(407, "The on-site operator then scores the rollout"),
            anchor(408, "\\emph{three-way quality label}:"),
            anchor(419, "corrupted or unlabelled source episodes are excluded."),
        ],
        "author_statement": (
            "An on-site operator assigns a three-way label; the paper identifies "
            "excluded episodes and operator-dependent stopping."
        ),
        "audit_inference": (
            "Evaluator role and label classes are documented, but the horizon is not "
            "standardized and exclusion/missingness handling is not identification-complete."
        ),
    },
    {
        "unit_id": 9,
        "name": "public_per_trial_artifact_outcome_linkage",
        "status": "supported",
        "source_locations": ["main.tex:421-441", "main.tex:581-583", "PDF pp.6,9"],
        "anchors": [
            anchor(427, "episodes define the \\emph{core benchmark}"),
            anchor(434, "We release the core benchmark in two formats."),
            anchor(437, "\\texttt{success}, \\texttt{success\\_class}, \\texttt{policy\\_type}"),
            anchor(441, "preserve the operator-assigned outcomes"),
        ],
        "author_statement": (
            "The released episode formats carry per-episode policy identity, media, "
            "and operator-assigned outcome fields."
        ),
        "audit_inference": (
            "Together with H029's immutable non-outcome projection, this supports "
            "public per-trial linkage for the core dataset, not H022 timing."
        ),
    },
    {
        "unit_id": 10,
        "name": "uncertainty_matches_dependence_and_assignment",
        "status": "absent_from_fixed_scope",
        "source_locations": ["complete main.tex design/methods/discussion audit"],
        "anchors": [
            anchor(427, "all reported"),
            anchor(530, "Cross-cell physical reproducibility"),
        ],
        "author_statement": (
            "The audited source reports rollout counts and explicitly leaves "
            "cross-cell reproducibility unanswered."
        ),
        "audit_inference": (
            "No uncertainty method tied to assignment, order, cell, session, or "
            "another declared dependence unit is provided."
        ),
        "absent_terms": [
            "confidence interval",
            "credible interval",
            "standard error",
            "bootstrap",
        ],
    },
    {
        "unit_id": 11,
        "name": "preexecution_simulator_or_world_model_evaluator",
        "status": "absent_from_fixed_scope",
        "source_locations": ["main.tex:284-292", "main.tex:432-445", "PDF pp.4,6"],
        "anchors": [
            anchor(288, "Logs and video stream to the control panel"),
            anchor(407, "The on-site operator then scores the rollout"),
            anchor(444, "used to train or fine-tune action-conditioned world"),
        ],
        "author_statement": (
            "Operators score completed rollouts; world models are mentioned only as "
            "a downstream use of released trajectories."
        ),
        "audit_inference": (
            "The paper supplies no pre-execution evaluator capable of scoring every "
            "candidate without corresponding physical-execution media."
        ),
    },
    {
        "unit_id": 12,
        "name": "cost_and_capacity",
        "status": "supported",
        "source_locations": ["main.tex:256-280", "main.tex:313-332", "PDF pp.3-5"],
        "anchors": [
            anchor(256, "\\textbf{Cost.}"),
            anchor(314, "summarises deployment scale and operator workload."),
            anchor(317, "a retrospective estimate rather than a measurement"),
            anchor(331, "Cells supervised concurrently per operator"),
        ],
        "author_statement": (
            "The paper reports a component bill of materials, deployment scale, "
            "concurrent supervision, and an estimated active operator burden."
        ),
        "audit_inference": (
            "This is useful operational capacity evidence; the active-time figure is "
            "retrospective and not a measured trial-level cost record."
        ),
    },
]


DECISIONS = {
    "h022_status": "refused_unchanged",
    "h022_existing_blockers_all_closed": False,
    "h022_preexecution_evaluator_present": False,
    "h022_corresponding_video_scoring_reclassified": False,
    "p2_classification": "adverse_mismatch_contrast",
    "p2_positive_design_contrast_eligible": False,
    "p2_context_committed_before_policy_assignment": False,
    "p2_assignment_reset_order_dependence_sufficient": False,
    "p2_evidence_role": "prospective_temporal_out_of_sample_adverse_design_contrast",
    "paper_promotion_requires_independent_challenge": True,
    "linked_artifact_followup_authorized": False,
}

OUTCOME_EXPOSURE = {
    "source_selected_before_outcomes": True,
    "protocol_fixed_before_abstract_pdf_or_source_open": True,
    "abstract_aggregate_counts_and_label_schema_visible": True,
    "results_search_incidentally_displayed_one_performance_sentence": True,
    "required_page_8_visual_check_exposed_result_tables": True,
    "performance_values_incidentally_visible": True,
    "performance_values_extracted_or_used": False,
    "policy_rankings_compared_or_interpreted": False,
    "results_section_deliberately_audited": False,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_dependencies() -> None:
    bindings = [
        (H028_RESULT, H028_SHA256, "H028"),
        (H029_RESULT, H029_SHA256, "H029"),
        (H222_RESULT, H222_SHA256, "H222"),
    ]
    for path, expected, label in bindings:
        if sha256(path) != expected:
            raise ValueError(f"{label} dependency binding mismatch")


def validate_source_anchors(source: str) -> None:
    lines = source.splitlines()
    for unit in EVIDENCE_UNITS:
        for item in unit["anchors"]:
            line_number = item["line"]
            if line_number > len(lines) or item["contains"] not in lines[line_number - 1]:
                raise ValueError(
                    f"anchor mismatch for unit {unit['unit_id']} at line {line_number}"
                )
        for term in unit.get("absent_terms", []):
            if term.casefold() in source.casefold():
                raise ValueError(
                    f"fixed absence term unexpectedly present for unit "
                    f"{unit['unit_id']}: {term}"
                )


def pdf_page_count(path: Path) -> int:
    completed = subprocess.run(
        ["pdfinfo", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in completed.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError("pdfinfo did not report a page count")


def expected_result_record(observed_utc: str = "not_recorded") -> dict[str, Any]:
    validate_dependencies()
    statuses = {name: 0 for name in sorted(ALLOWED_STATUSES)}
    for unit in EVIDENCE_UNITS:
        statuses[unit["status"]] += 1
    return {
        "schema": "h224-armnetbench-paper-design-audit-v1",
        "observed_utc": observed_utc,
        "protocol_sha256": sha256(PROTOCOL),
        "dependencies": {
            "h028_result_sha256": H028_SHA256,
            "h029_result_sha256": H029_SHA256,
            "h222_result_sha256": H222_SHA256,
        },
        "source": {
            "arxiv_id": ARXIV_ID,
            "title": TITLE,
            "authors": AUTHORS,
            "submitted_utc": SUBMITTED_UTC,
            "pdf_url": PDF_URL,
            "pdf_bytes": PDF_BYTES,
            "pdf_sha256": PDF_SHA256,
            "pdf_pages": PDF_PAGES,
            "source_url": SOURCE_URL,
            "source_bytes": SOURCE_BYTES,
            "source_sha256": SOURCE_SHA256,
            "main_tex_sha256": MAIN_TEX_SHA256,
            "rendered_pdf_pages_visually_checked": [3, 4, 5, 6, 8, 9],
            "rendered_pages_legible_and_source_consistent": True,
        },
        "evidence_units": copy.deepcopy(EVIDENCE_UNITS),
        "status_counts": statuses,
        "decisions": copy.deepcopy(DECISIONS),
        "outcome_exposure": copy.deepcopy(OUTCOME_EXPOSURE),
        "interpretation": (
            "ArmnetBench supplies useful same-cell, standalone-execution, public "
            "per-trial, and capacity infrastructure. It is not a positive P2 design "
            "contrast because context commitment, policy assignment/order, reset "
            "acceptance, and dependence-aware uncertainty are not auditable. The new "
            "paper does not change H022's refusal."
        ),
        "scope_limits": {
            "linked_code_data_or_media_newly_opened": False,
            "policy_performance_used": False,
            "protected_p1_outcomes_accessed": False,
            "sealed_p3_frame_accessed": False,
            "author_contacted": False,
        },
    }


def validate_result_record(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result.get("observed_utc"), str):
        raise ValueError("observed_utc must be a string")
    expected = expected_result_record(result["observed_utc"])
    if result != expected:
        if result.get("decisions") != expected["decisions"]:
            raise ValueError("decision mismatch")
        raise ValueError("saved H224 result mismatch")
    return result


def acquire(source_tex: Path, pdf: Path, source_archive: Path) -> dict[str, Any]:
    validate_dependencies()
    if pdf.stat().st_size != PDF_BYTES or sha256(pdf) != PDF_SHA256:
        raise ValueError("official PDF identity mismatch")
    if (
        source_archive.stat().st_size != SOURCE_BYTES
        or sha256(source_archive) != SOURCE_SHA256
    ):
        raise ValueError("official source archive identity mismatch")
    source = source_tex.read_text(encoding="utf-8")
    if sha256_text(source) != MAIN_TEX_SHA256:
        raise ValueError("main.tex identity mismatch")
    if TITLE not in source.replace("\\textbf{\\LARGE ", "").replace("}", ""):
        raise ValueError("title mismatch")
    for author in AUTHORS:
        if author not in source:
            raise ValueError(f"author mismatch: {author}")
    if pdf_page_count(pdf) != PDF_PAGES:
        raise ValueError("PDF page-count mismatch")
    validate_source_anchors(source)
    result = expected_result_record(datetime.now(timezone.utc).isoformat())
    validate_result_record(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquire", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-tex", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--source-archive", type=Path)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.acquire == args.check:
        parser.error("choose exactly one of --acquire or --check")
    if args.check:
        validate_result_record(json.loads(args.out.read_text(encoding="utf-8")))
        print("OK: H224 ArmnetBench paper design audit validates")
        return
    if not all((args.source_tex, args.pdf, args.source_archive)):
        parser.error("--acquire requires --source-tex, --pdf, and --source-archive")
    result = acquire(args.source_tex, args.pdf, args.source_archive)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "h022": result["decisions"]["h022_status"],
                "p2": result["decisions"]["p2_classification"],
                "status_counts": result["status_counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
