import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import time
import glob
from app.schemas.case import BugCase
from app.graph import build_investigation_graph

def main():
    print("=" * 70)
    print("  RUNNING REPOTRACE BENCHMARK ACROSS EVALUATION CASES")
    print("=" * 70)

    case_files = sorted(glob.glob("evaluation/cases/BUG-*.json"))
    results = []

    os.makedirs("evaluation/results", exist_ok=True)
    graph = build_investigation_graph()

    for cpath in case_files:
        with open(cpath, "r", encoding="utf-8") as f:
            cdata = json.load(f)
        case = BugCase.model_validate(cdata)

        print(f"Investigating {case.case_id} with RepoTrace...")
        start_t = time.time()
        initial_state = {
            "case": case,
            "repo_path": case.repo_path,
            "commit_sha": case.commit_sha,
            "trajectory": []
        }
        res = graph.invoke(initial_state)
        runtime = round(time.time() - start_t, 2)

        rep = res.get("report")
        rep_dict = rep.model_dump() if rep else {}
        rep_dict["case_id"] = case.case_id
        rep_dict["runtime_seconds"] = runtime
        results.append(rep_dict)

        print(f"  Root Cause: {rep_dict.get('root_cause_file')}:{rep_dict.get('root_cause_lines')} | Runtime: {runtime}s")

    out_path = "evaluation/results/repotrace_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nRepoTrace benchmark complete. Results saved to {out_path}")

if __name__ == "__main__":
    main()
