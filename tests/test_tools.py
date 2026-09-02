from app.tools.filesystem import list_files, read_file
from app.tools.search import search_code, find_symbol
from app.tools.repository import map_repository
from app.tools.failure_discovery import discover_and_run_tests
from app.tools.evidence_validator import validate_evidence_chain
from app.tools.trace_exporter import export_trace_to_markdown, export_trace_to_json
from app.schemas.evidence import Evidence, EvidenceType
from app.schemas.trace import TraceEvent, TraceEventType, InvestigationTraceSummary

def test_list_files():
    files = list_files("fixtures/bug001_quantity_zero")
    assert len(files) >= 3
    paths = [f["path"] for f in files]
    assert any("cart.py" in p for p in paths)
    assert any("pricing.py" in p for p in paths)

def test_read_file_success():
    res = read_file("fixtures/bug001_quantity_zero/src/pricing.py", start_line=1, end_line=10)
    assert res["status"] == "success"
    assert "calculate_unit_price" in res["content"]
    assert res["total_lines"] >= 3

def test_read_file_not_found():
    res = read_file("fixtures/nonexistent_file.py")
    assert res["status"] == "error"
    assert "File not found" in res["error"]

def test_search_code():
    res = search_code("fixtures/bug001_quantity_zero", "calculate_unit_price")
    assert res["status"] == "success"
    assert len(res["matches"]) >= 1

def test_find_symbol():
    res = find_symbol("fixtures/bug001_quantity_zero", "ShoppingCart")
    assert res["status"] == "success"
    assert len(res["definitions"]) >= 1
    assert res["definitions"][0]["symbol"] == "ShoppingCart"
    assert res["definitions"][0]["type"] == "class"

def test_map_repository():
    res = map_repository("fixtures/bug001_quantity_zero")
    assert res["status"] == "success"
    assert res["total_files"] >= 3
    assert res["language"] == "Python"
    assert res["has_pytest"] is True

def test_failure_discovery():
    res = discover_and_run_tests("fixtures/bug001_quantity_zero")
    assert res["status"] == "success"
    assert res["total_failures"] >= 1
    assert res["selected_primary_failure"] is not None

def test_evidence_validator():
    ev = [
        Evidence(id="E1", type=EvidenceType.FILE, path="src/pricing.py", line_start=1, line_end=5, content_or_summary="pricing formula", source_tool="read_file")
    ]
    is_valid, details = validate_evidence_chain(ev, "fixtures/bug001_quantity_zero", [])
    assert is_valid is True
    assert len(details) == 1

def test_trace_exporters():
    event = TraceEvent(
        event_id="E-001",
        run_id="RUN-TEST",
        node="intake",
        event_type=TraceEventType.CASE_STARTED,
        output_summary="Started"
    )
    summary = InvestigationTraceSummary(
        case_id="BUG-001",
        run_id="RUN-TEST",
        tools_used_count=3,
        evidence_collected_count=4,
        hypotheses_count=3,
        experiments_count=1,
        supported_hypotheses_count=1,
        rejected_hypotheses_count=2,
        investigation_rounds=1,
        runtime_seconds=2.5,
        upstream_root_cause="src/cart.py:8-12"
    )
    md = export_trace_to_markdown("BUG-001", "RUN-TEST", [event], summary)
    js = export_trace_to_json("BUG-001", "RUN-TEST", [event], summary)
    assert "# 📜 RepoTrace" in md
    assert "BUG-001" in js
