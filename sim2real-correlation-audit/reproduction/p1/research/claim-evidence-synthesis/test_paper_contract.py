"""Contract checks for the clean-room combined paper."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "PAPER.md"
QUANTITATIVE_SUPPLEMENT = ROOT / "research/claim-evidence-synthesis/result-quantitative-supplement.md"


def test_paper_uses_locked_decision_cases():
    text = PAPER.read_text(encoding="utf-8")
    assert "SIMPLER Google" in text
    assert "Real2Sim T (best-sim)" in text
    assert "A Practical Recipe" in text
    assert "OSCAR Skeleton" in text
    assert "Cosmos-Surg manual" in text
    assert "WM-PolicyEval IRASim" in text
    assert "figure-decision-atlas.pdf" in text
    assert "figure-decision-robustness.pdf" in text
    assert "12.5 percentage points" in text
    assert "23--25/26" in text
    assert "fewer than ten policy or checkpoint blocks" in text.lower()
    assert "5 p; 1 CI; 20 neither" in text
    normalized = " ".join(text.lower().split())
    assert "seven of nine" in normalized
    assert "one agrees" in normalized
    assert "one depends on tie handling" in normalized
    assert ".087" in text
    assert "omits simulator rollout counts" in normalized
    assert ".432" in text
    assert "sensitivity ranges" in normalized
    assert "isotonic" in normalized
    assert "changes irasim's winner to openvla" in normalized
    supplement = QUANTITATIVE_SUPPLEMENT.read_text(encoding="utf-8")
    assert "empirical individual-outcome Brier score" in supplement
    assert ".20417" in supplement
    for exact_fraction in (
        "13/170", "47/270", "13/120", "21/200", "307/2000", "209/3000"
    ):
        assert exact_fraction in supplement


def test_paper_excludes_quarantined_unqualified_claims():
    text = PAPER.read_text(encoding="utf-8")
    assert "MMRV is three to fifteen times less stable" not in text
    assert "Fisher-z | **works**" not in text
    assert "Exact permutation | **works**" not in text
    assert "systematic review of 26" not in text
    assert "cannot estimate field prevalence" in text
    assert "universal threshold" in text
    assert "no coding assigns supported" not in text.lower()
    assert "Only 6/26 report uncertainty" not in text
    assert "independent negative cases" not in text
    assert "task-stable loss" not in text
    assert "displayed decision it is meant to support" not in text
    assert "top-1 decisions agree in 17 of 19" in text.lower()
    assert "audit-defined" not in text


def test_paper_exposes_decision_framework_and_reusable_audit():
    text = PAPER.read_text(encoding="utf-8")
    normalized = " ".join(text.lower().split())
    assert "displayed-panel association" in normalized
    assert "finite-panel decision" in normalized
    assert "population transport" in normalized
    assert "decision acceptability" in normalized
    assert "the accompanying checklist covers the decision" in normalized
    assert "loss tolerance, and real-test budget" in normalized


def test_reusable_decision_audit_checklist_exists():
    checklist = ROOT / "SIM2REAL-DECISION-AUDIT-CHECKLIST.md"
    assert checklist.is_file()
    checklist_text = checklist.read_text(encoding="utf-8").lower()
    assert "intended action" in checklist_text
    assert "population or transport claim" in checklist_text
    assert "stop conditions" in checklist_text
