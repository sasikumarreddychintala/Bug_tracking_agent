import pytest
from app.schemas.case import BugCase
from app.schemas.evidence import Evidence, EvidenceType
from app.agents.bug_understanding import run_bug_understanding
from app.agents.investigator import run_code_investigation
from app.agents.hypothesis import run_hypothesis_generation
from app.agents.verifier import run_verification
from app.agents.report import generate_report

@pytest.fixture
def sample_case():
    return BugCase(
        case_id="BUG-001",
        repo_path="fixtures/bug001_quantity_zero",
        bug_description="Checkout fails when quantity is zero.",
        stack_trace="""Traceback (most recent call last):
  File "src/cart.py", line 10, in add_item
    unit_price = calculate_unit_price(total_price, quantity)
  File "src/pricing.py", line 4, in calculate_unit_price
    return round(total_amount / quantity, 2)
ZeroDivisionError: division by zero""",
        reproduction_command="pytest tests/test_cart.py"
    )

def test_bug_understanding_agent(sample_case):
    res = run_bug_understanding(sample_case)
    assert len(res.symptoms) >= 1
    assert len(res.entry_points) >= 1
    assert len(res.investigation_questions) >= 1

def test_code_investigator_agent(sample_case):
    inv_res = run_code_investigation(
        case=sample_case,
        entry_points=["src/cart.py"],
        stacktrace_frames=[{"file": "src/pricing.py", "line": 4}],
        repo_path=sample_case.repo_path
    )
    assert len(inv_res["evidence"]) >= 1
    assert len(inv_res["observations"]) >= 1

def test_hypothesis_agent(sample_case):
    evidence = [
        Evidence(
            id="E1",
            type=EvidenceType.STACKTRACE,
            content_or_summary="Crash at pricing.py:4",
            source_tool="parse_stacktrace"
        ),
        Evidence(
            id="E2",
            type=EvidenceType.FILE,
            path="src/cart.py",
            line_start=8,
            line_end=12,
            content_or_summary="cart.py calls calculate_unit_price without checking quantity",
            source_tool="read_file"
        )
    ]
    hypotheses = run_hypothesis_generation(sample_case, evidence, ["cart.py inspect observation"])
    assert len(hypotheses) >= 2
    assert hypotheses[0].id == "H1"
    assert hypotheses[1].id == "H2"

def test_verifier_and_report_agent(sample_case):
    evidence = [
        Evidence(id="E1", type=EvidenceType.STACKTRACE, content_or_summary="Crash at pricing.py:4", source_tool="parse_stacktrace"),
        Evidence(id="E2", type=EvidenceType.FILE, path="src/cart.py", line_start=8, line_end=12, content_or_summary="cart.py missing validation", source_tool="read_file")
    ]
    hypotheses = run_hypothesis_generation(sample_case, evidence, ["cart.py inspect observation"])
    verifications = run_verification(hypotheses, evidence, [])
    assert len(verifications) >= 2

    report = generate_report(sample_case, evidence, hypotheses, verifications, [])
    assert report.case_id == "BUG-001"
    assert "cart.py" in report.root_cause_file
    assert report.confidence in ["HIGH", "MEDIUM"]
