from app.schemas.case import BugCase
from baseline.baseline import run_baseline_v0

def test_baseline_execution():
    case = BugCase(
        case_id="BUG-001",
        repo_path="fixtures/bug001_quantity_zero",
        bug_description="Checkout fails when quantity is zero.",
        stack_trace="ZeroDivisionError at pricing.py:4"
    )
    res = run_baseline_v0(case)
    assert res["case_id"] == "BUG-001"
    assert "suspected_file" in res
    assert "diagnosis" in res
    assert res["runtime_seconds"] >= 0.0
