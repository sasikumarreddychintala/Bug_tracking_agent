# ruff: noqa: E402
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import argparse
import time
from app.schemas.case import BugCase
from app.graph import build_investigation_graph

def run_investigation(case: BugCase, provider_type: str = "mock", mode: str = "MODE_A_KNOWN_FAILURE") -> dict:
    print("\n" + "=" * 70)
    print(f"  REPOTRACE: INVESTIGATING {case.case_id} (Mode: {mode})")
    print("=" * 70)
    print(f"Bug Description: {case.bug_description}")
    print(f"Repository:      {case.repo_path}")
    print(f"Reproduction:    {case.reproduction_command or 'pytest'}")
    print("-" * 70)

    start_time = time.time()
    graph = build_investigation_graph()

    initial_state = {
        "mode": mode,
        "case": case,
        "repo_path": case.repo_path,
        "commit_sha": case.commit_sha,
        "trace_events": [],
        "evidence": [],
        "hypotheses": [],
        "experiments": []
    }

    final_state = graph.invoke(initial_state)
    duration_s = round(time.time() - start_time, 2)

    report = final_state.get("report")
    summary = final_state.get("trace_summary")

    # Save output report
    os.makedirs("reports", exist_ok=True)
    report_file = os.path.join("reports", f"{case.case_id}_report.json")
    if report:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

    print("\n" + "-" * 70)
    print(f"  INVESTIGATION COMPLETE: {case.case_id}")
    print("-" * 70)
    if report:
        print(f"Executive Diagnosis:  {report.diagnosis}")
        print(f"Upstream Root Cause:  {report.root_cause_file}:{report.root_cause_lines}")
        print(f"Root Cause Summary:   {report.root_cause_summary}")
        print(f"Reproduction Status:  {report.reproduction_status}")
        print(f"Confidence Level:     {report.confidence}")
    print(f"Runtime:              {duration_s}s")
    if summary:
        print(f"Evidence Collected:   {summary.evidence_collected_count} items (Validation: {'PASSED' if final_state.get('evidence_validation_passed') else 'WARNING'})")
        print(f"Hypotheses Verified:  {summary.supported_hypotheses_count} Supported, {summary.rejected_hypotheses_count} Rejected")
    print(f"Trajectory Saved:     trajectories/{case.case_id}/trajectory.json")
    print(f"Markdown Audit Trail: trajectories/{case.case_id}/{final_state.get('run_id')}.md")
    print("=" * 70 + "\n")

    return final_state

def main():
    parser = argparse.ArgumentParser(description="RepoTrace - Autonomous Bug Root-Cause Investigation System")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo on BUG-001")
    parser.add_argument("--case", type=str, help="Case ID (e.g. BUG-001) or path to case JSON file")
    parser.add_argument("--discover", type=str, help="Mode B: Discover & investigate test failures in repository path")
    parser.add_argument("--provider", type=str, default="mock", choices=["mock", "openai", "ollama"], help="LLM Provider")

    args = parser.parse_args()

    if args.discover:
        # Mode B: Discover Test Failures
        print(f"Starting Mode B Failure Discovery on repository: {args.discover}")
        case_dummy = BugCase(
            case_id="DISCOVERY-RUN",
            repo_path=args.discover,
            bug_description="Automated failure discovery"
        )
        run_investigation(case_dummy, provider_type=args.provider, mode="MODE_B_DISCOVER_FAILURES")
        return

    if args.demo or not args.case:
        demo_case_file = "evaluation/cases/BUG-001.json"
        if os.path.exists(demo_case_file):
            with open(demo_case_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            case = BugCase.model_validate(cdata)
        else:
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
                reproduction_command="pytest fixtures/bug001_quantity_zero/tests/test_cart.py"
            )
        run_investigation(case, provider_type=args.provider, mode="MODE_A_KNOWN_FAILURE")
    else:
        if args.case.endswith(".json") and os.path.exists(args.case):
            with open(args.case, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            case = BugCase.model_validate(cdata)
        else:
            case_path = os.path.join("evaluation", "cases", f"{args.case}.json")
            if os.path.exists(case_path):
                with open(case_path, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                case = BugCase.model_validate(cdata)
            else:
                print(f"Error: Case file not found for {args.case}")
                return
        run_investigation(case, provider_type=args.provider, mode="MODE_A_KNOWN_FAILURE")

if __name__ == "__main__":
    main()
