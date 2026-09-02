import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import glob
from app.schemas.case import BugCase
from baseline.baseline import run_baseline_v0

def main():
    print("=" * 70)
    print("  RUNNING BASELINE V0 BENCHMARK ACROSS EVALUATION CASES")
    print("=" * 70)

    case_files = sorted(glob.glob("evaluation/cases/BUG-*.json"))
    results = []

    os.makedirs("evaluation/results", exist_ok=True)

    for cpath in case_files:
        with open(cpath, "r", encoding="utf-8") as f:
            cdata = json.load(f)
        case = BugCase.model_validate(cdata)
        
        print(f"Running baseline on {case.case_id}...")
        res = run_baseline_v0(case, provider_type="mock")
        results.append(res)
        print(f"  Diagnosis: {res['diagnosis'][:60]}... | File: {res['suspected_file']}")

    out_path = "evaluation/results/baseline_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nBaseline benchmark complete. Results saved to {out_path}")

if __name__ == "__main__":
    main()
