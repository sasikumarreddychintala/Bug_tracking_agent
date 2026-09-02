from app.schemas.case import BugCase
from app.graph import build_investigation_graph

def test_full_graph_investigation():
    case = BugCase(
        case_id="BUG-001",
        repo_path="fixtures/bug001_quantity_zero",
        bug_description="Checkout fails with ZeroDivisionError when quantity is zero.",
        stack_trace="""Traceback (most recent call last):
  File "src/cart.py", line 10, in add_item
    unit_price = calculate_unit_price(total_price, quantity)
  File "src/pricing.py", line 4, in calculate_unit_price
    return round(total_amount / quantity, 2)
ZeroDivisionError: division by zero""",
        reproduction_command="pytest tests/test_cart.py"
    )

    graph = build_investigation_graph()
    initial_state = {
        "mode": "MODE_A_KNOWN_FAILURE",
        "case": case,
        "repo_path": case.repo_path,
        "trace_events": [],
        "evidence": [],
        "hypotheses": [],
        "experiments": []
    }

    result = graph.invoke(initial_state)

    assert result.get("is_finished") is True
    report = result.get("report")
    assert report is not None
    assert "cart.py" in report.root_cause_file
    assert len(result.get("evidence", [])) >= 2
    assert len(result.get("hypotheses", [])) >= 2
    assert len(result.get("verifications", [])) >= 2
    assert len(result.get("trace_events", [])) >= 6
    assert result.get("evidence_validation_passed") is True
